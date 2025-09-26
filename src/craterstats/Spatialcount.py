#  Copyright (c) 2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

from collections import namedtuple
from datetime import datetime
import math
import os
import re
import shutil

import numpy as np
import matplotlib.pyplot as plt
import shapefile  # pyshp
import shapely as shp
import spherely as sph
import pyproj as prj

import craterstats as cst
import craterstats.gm as gm

class Spatialcount:
    '''Reads spatial crater count data'''

    Craterlist = namedtuple('Craterlist', ['lon','lat','diam','fraction'])

    def __init__(self,filename=None,area_file=None):
        self.filename=filename
        filetype = gm.filename(filename, 'e') if filename else None
        self.name = gm.filename(filename, "n")

        if filetype == '.scc':
            self.readSCCfile()
        elif filetype == '.shp':
            if not area_file:  # if area_file not specified, try to get from crater_file name
                f = re.sub(r'CRATER', 'AREA', gm.filename(filename, 'n'))
                area_file = gm.filename(filename, 'p1e', f)
            self.crater_file = filename
            self.area_file = area_file
            self.name = re.sub(r'_?CRATER_?', '', gm.filename(filename, "n"))
            self.readSHPfiles()

    def summary(self):
        print(f"\nPlanetary radius: {self.planetary_radius:0g} km")
        print(f"Total area {self.area:.7g} km2\nperimeter: {self.perimeter:.5g} km")
        print("\nDiameter, km  fraction      lon                  lat")
        for d, f, x, y in zip(self.diam, self.fraction, self.lon, self.lat):
            print(f"{d:<12.7g} {f:9.3g} {x:20.12f} {y:20.12f}")

    def llr2xyz(self,lon,lat,r = None):
        if not r: r = self.planetary_radius
        lat_rad = np.radians(lat)
        lon_rad = np.radians(lon)
        x = r * np.cos(lat_rad) * np.cos(lon_rad)
        y = r * np.cos(lat_rad) * np.sin(lon_rad)
        z = r * np.sin(lat_rad)
        return x,y,z

    def readSCCfile(self):

        s = gm.read_textfile(self.filename,ignore_hash=True,strip=';', as_string=True)
        s = re.sub(r"a-axis radius", "oct_a_axis_radius", s) # fix OpenCraterTool misformatting
        c = gm.read_textstructure(s,from_string=True)

        crater=c['crater']
        diam=[float(e) for e in crater['diam']]
        frac=[float(e) for e in crater['fraction']] if 'fraction' in c else [1. for e in diam]
        lon=[float(e) for e in crater['lon']]
        lat = [float(e) for e in crater['lat']]
        q=[i for i,e in sorted(enumerate(diam),key=lambda x:x[1])]     #get sorted indices
        self.diam=[diam[e] for e in q]
        self.fraction=[frac[e] for e in q]
        self.lon = [lon[e] for e in q]
        self.lat = [lat[e] for e in q]

        radius_key = next((k for k in ("a_axis_radius", "oct_a_axis_radius") if k in c), None) # remove later
        self.planetary_radius = float(c[radius_key].split(' ')[0])

        b = c['unit_boundary']
        z = sorted(set([(int(a), b == 'int') for a, b in zip(b['sub_area'], b['tag'])]))

        d={}
        for i, _ in z:
            pts = [(float(x),float(y)) for x,y, sub_area in zip(c['unit_boundary']['lon'],c['unit_boundary']['lat'], c['unit_boundary']['sub_area']) if int(sub_area) == i]
            p = sph.create_polygon(shell=pts)
            d[i] = (pts, p) #, xyz(pts)) # xyz needs to be moved out
            xr1 = gm.range([x for x,y in pts])
            yr1 = gm.range([y for x, y in pts])
            if i == 1:
                xr=xr1
                yr=yr1
            else:
                xr = (min(xr1[0], xr[0]), max(xr1[1], xr[1]))
                yr = (min(yr1[0], yr[0]), max(yr1[1], yr[1]))

        p=[]
        for i, internal in z:
            if not internal:
                holes=[]
                for j, internal1 in z[i:]:
                    if sph.within(d[j][1],d[i][1]):
                        holes += [d[j][0]]
                p += [sph.create_polygon(shell=d[i][0], holes=holes)]

        p = sph.create_multipolygon(p) #merge if multiple

        self.area=sph.area(p, radius=self.planetary_radius)
        self.perimeter=sph.perimeter(p, radius=self.planetary_radius)
        self.polygon=p

        n_pole = sph.create_point(longitude=0, latitude=90)
        s_pole = sph.create_point(longitude=0, latitude=-90)
        if sph.covers(p, n_pole):
            yr = (yr[0], 90)
            xr = (-180,180)
        if sph.covers(p, s_pole):
            yr = (-90, yr[1])
            xr = (-180, 180)
        self.xr=xr
        self.yr=yr
        enclosing_polygon = sph.create_polygon(shell=[(xr[0],yr[0]),(xr[0],yr[1]),(xr[1],yr[1]),(xr[1],yr[0])])
        self.enclosing_area = sph.area(enclosing_polygon, radius=self.planetary_radius)

        print(f"Range: {xr[0]:.2f}:{xr[1]:.2f} {yr[0]:.2f}:{yr[1]:.2f}, area: {self.area:.2f} km2, perimeter: {self.perimeter:.2f} km (planetary radius: {self.planetary_radius:0g} km)")



    def readSHPfiles(self):
        """
        read crater and area shapefiles, extracting diameters, area, perimeter

        """
        def read_shp(shp):
            mtime = os.path.getmtime(shp)
            prj_file = gm.filename(shp, 'pn1', '.prj')
            wkt = gm.read_textfile(prj_file)[0]
            crs = prj.CRS.from_wkt(wkt)
            planetary_radius = crs.ellipsoid.semi_major_metre / 1e3
            sf = shapefile.Reader(shp)
            shapes = sf.shapes()

            if not crs.is_geographic:
                transformer = prj.Transformer.from_crs(crs, crs.geodetic_crs, always_xy=True)
                for shape in shapes:
                    xy = list(zip(*shape.points))
                    lons, lats = transformer.transform(xy[0], xy[1])
                    shape.points = [(lon, lat) for lon, lat in zip(lons, lats)]

            return shapes, planetary_radius, mtime

        sc, rc, tc = read_shp(self.crater_file)
        sa, ra, ta = read_shp(self.area_file)
        if rc != ra:
            raise ValueError("Crater/Area shapefile planetary radii disagree")
        self.planetary_radius = rc
        self.tc, self.ta = tc, ta
        self.sa = sa

        multipolygon = []
        for shape in sa:
            parts = shape.parts
            points = shape.points
            n_rings = len(parts) - 1
            if n_rings == 0:
                p = sph.create_polygon(shell=points)
            else:
                ext = points[:parts[1]]
                int = []
                for i in range(1, len(parts)):
                    start_idx = parts[i]
                    end_idx = parts[i + 1] if i + 1 < len(parts) else len(points)
                    int += [points[start_idx:end_idx]]
                p = sph.create_polygon(shell=ext, holes=int)
            # print(f"Polygon has {n_rings} hole(s). Sub-area: {sph.area(p, radius=ra):.5g} km2")
            multipolygon += [p]
        p = sph.create_multipolygon(multipolygon)
        self.polygon = p
        self.area = sph.area(p, radius=ra)
        self.perimeter = sph.perimeter(p, radius=ra)

        diam = []
        frac = []
        lon = []
        lat = []
        transform = cst.fractional_crater_transform()
        for shape in sc:
            c = sph.create_polygon(shell=shape.points)
            c_area = sph.area(c, radius=rc)
            # diam1 = math.sqrt(4*c_area/math.pi)  # flat diameter from area: better behaviour if noisy vertex positions
            # diam2 = sph.perimeter(c,radius = rc)/math.pi # flat diameter from perimeter: greater error if noisy vertex positions
            diam3 = 2 * rc * math.acos(1 - c_area / (2 * math.pi * rc ** 2))  # spherical diameter from area

            pt = sph.centroid(c)
            x, y = (sph.get_x(pt), sph.get_y(pt))
            # print(f"{len(shape.points)} {(diam2-diam1)/diam1:12.3g} {diam1:12.7g} {diam2:12.7g} {diam3:12.9g} {x:20.12f} {y:20.12f} ")
            diam += [diam3]
            lon += [x]
            lat += [y]
            if sph.covered_by(c, p):
                f = 1
            else:
                area_intersection = sph.area(sph.intersection(c, p), radius=rc)
                area_frac = area_intersection / c_area
                f = transform.af2lf(area_frac)
            frac += [f]

        self.diam = diam
        self.fraction = frac
        self.lon = lon
        self.lat = lat
        return


    def writeSCCfile(self, filename=None):
        sub_area, tag, pts = [],[],[]
        i = 1
        for shape in self.sa: # might be better to use technique from write_SHP, i.e. dismantle self.polygon
            parts = list(shape.parts) + [len(shape.points)]
            pts += shape.points
            for j in range(len(shape.parts)):
                n = parts[j + 1] - parts[j]
                tag += ['ext' if j==0 else 'int'] * n
                sub_area += [i] * n
                i += 1
        boundary_table = [f"{i:<5}\t{a:<5}\t{b:<4}\t{c[0]:23.15f}\t{c[1]:23.15f}"
                          for i, (a, b, c) in enumerate(zip(sub_area, tag, pts), start=1)]

        crater_table = [f"{d:<12.7g}\t{f:9.3g}\t{x:23.15f}\t{y:23.15f}\t{1}"
                        for d, f, x, y in zip(self.diam, self.fraction, self.lon, self.lat)]

        # include so that can import into OpenCratertool (also requires topo_scale_factor for craters - prefer without when n/a)
        s2 = (['#', '# Extra lines for OpenCraterTool compatibility:',
               f"a-axis radius = {self.planetary_radius:0g} <km>", ]
              + [f"# Area_name {i} = NULL" for i in range(1, sub_area[-1] + 1)]
              + ['#'])

        s = (['# Spatial crater count',
              'craterstats_version = '+ cst.__version__,'#',
              '# Derived from:',
              '# ' + datetime.fromtimestamp(self.tc).strftime("%Y-%m-%d %H:%M ") + gm.filename(self.crater_file, 'ne'),
              '# ' + datetime.fromtimestamp(self.ta).strftime("%Y-%m-%d %H:%M ") + gm.filename(self.area_file, 'ne'),
              '#',
              f"a_axis_radius = {self.planetary_radius:0g} <km>",
              f"Total_area = {self.area:0g} <km2>",
              f"Total_perimeter = {self.perimeter:0g} <km>",
              '#',] + s2 + [
              'unit_boundary = {vertex, sub_area, tag, lon, lat']
             + boundary_table +
             ['}',
              'crater = {diam, fraction, lon, lat, topo_scale_factor']
              + crater_table +
              ['}'])

        if filename:
            gm.write_textfile(filename,s)
        else:
            print('\n'.join(s))


    def writeSHPfiles(self, filename):
        """
        Write shapefile pair
        """
        # do crater file
        fc = gm.filename(filename,'pn1e',"_CRATER")
        c = shapefile.Writer(fc)
        c.field('Diam_km', 'F', 12,6)
        c.field('x_coord', 'F', 20,15)
        c.field('y_coord', 'F', 20, 15)
        c.field('tag', 'C', 20)
        rims,wkt = self.find_rims()
        for d, x, y, r in zip(self.diam, self.lon, self.lat, rims):
            c.record(Diam_km=d, x_coord=x, y_coord=y, tag='standard')
            c.poly([list(zip(*r))])
        c.close()
        gm.write_textfile(gm.filename(fc,'pn1','.prj'),wkt)
        shutil.copy(cst.PATH + 'config/_CRATER.qml', gm.filename(fc,'pn1','.qml'))

        # do area file
        fa = gm.filename(filename, 'pn1e', "_AREA")
        a = shapefile.Writer(fa)
        a.field('area', 'F', 12,6)
        a.field('area_name', 'C', 30)
        decomposed = self.polygon_to_pts()
        for i, p in enumerate(decomposed):
            a.poly(p)
            a.record(None, f'Area_{i + 1}')
        a.close()
        gm.write_textfile(gm.filename(fa, 'pn1', '.prj'), wkt)
        shutil.copy(cst.PATH + 'config/_AREA.qml', gm.filename(fa, 'pn1', '.qml'))

    def find_rims(self,craters=None,ns=100):
        """
        Calculate crater rim lon lat points given centres and diameters
        """
        lon,lat,diam = (craters.lon,craters.lat,craters.diam) if craters else (self.lon,self.lat,self.diam)

        theta = [2 * math.pi * i / ns for i in range(ns + 1)]
        cx, cy = np.array([(math.cos(e), math.sin(e)) for e in theta]).T
        rs = f'{self.planetary_radius * 1e3:0.0f}'
        wkt = f'GEOGCS["Spherical_GCS_{rs}", DATUM["Sphere_{rs}", SPHEROID["Sphere_{rs}", {rs}, 0]], PRIMEM["Greenwich", 0], UNIT["Degree", 0.0174532925199433]]'
        geod = prj.CRS(wkt)
        rims = []
        # make projection centre transformers at this spacing for speed (Distance distortion: 0.061% at 2 deg)
        # nb: max offset from projection centre is grid/2
        grid = 5
        t_dict = {}
        for d, x, y in zip(diam, lon, lat):
            origin = (round(x/grid)*grid,round(y/grid)*grid)
            if not origin in t_dict:
                proj4 = f"+proj=laea +lat_ts=0 +lat_0={origin[1]} +lon_0={origin[0]} +R={self.planetary_radius * 1e3:0.0f} +units=m +no_defs"
                laea = prj.CRS(proj4)
                t_dict[origin] = prj.Transformer.from_crs(laea, geod, always_xy=True)  # laea.geodetic_crs
                t_dict[(origin,'inverse')] = prj.Transformer.from_crs(geod, laea, always_xy=True)
            dx,dy = t_dict[(origin,'inverse')].transform(x,y)
            r = d * 1e3 / 2
            ll_pts = t_dict[origin].transform(dx+ cx * r, dy + cy * r)
            rims += [ll_pts]
        return rims,wkt

    def polygon_to_pts(self,p0=None):
        """
        Decompose polygon/multipolygon into list of lists of rings/holes
        """
        if not p0:
            p0=self.polygon
        decomposed=[]
        for p in p0 if isinstance(p0, list) else [p0]:
            z = sph.to_wkb(p)
            y = shp.from_wkb(z)
            x = shp.get_exterior_ring(y)
            rings = [list(x.coords)]
            for j in range(shp.get_num_interior_rings(y)):
                x = shp.get_interior_ring(y,j)
                rings.append(list(x.coords))  # Append holes
            decomposed += [rings]
        return decomposed


    def plot(self,cps,craters=None,grid=False,ax=None):
        """
        Plot Spatialcount

        """
        if not ax:
            ax=cps.ax
        sz_ratio = ax.get_position().width / cps.ax.get_position().width

        cen = sph.centroid(self.polygon)
        cenlon, cenlat = (sph.get_x(cen),sph.get_y(cen))
        xr0 = yr0 = None
        ortho_proj = prj.Proj(proj='ortho', lat_0=cenlat, lon_0=cenlon, R=self.planetary_radius)
        self.ortho_proj = ortho_proj

        # do area
        z = sph.to_wkb(self.polygon)
        multipolygon = shp.from_wkb(z)

        if not isinstance(multipolygon, shp.MultiPolygon):
            multipolygon = shp.MultiPolygon([multipolygon])

        for poly in multipolygon.geoms:
            exterior_x, exterior_y = poly.exterior.xy
            interior_coords = [interior.xy for interior in poly.interiors]
            x_exterior, y_exterior = ortho_proj(exterior_x, exterior_y)
            x_interior = []
            y_interior = []
            for interior_x, interior_y in interior_coords:
                x_interior_tmp, y_interior_tmp = ortho_proj(interior_x, interior_y)
                x_interior.append(x_interior_tmp)
                y_interior.append(y_interior_tmp)

            # Reassemble the projected polygon
            projected_polygon = shp.Polygon(zip(x_exterior, y_exterior),
                holes=[list(zip(xi, yi)) for xi, yi in zip(x_interior, y_interior)] if x_interior else None)
            gm.shp_plot_polygon(ax, projected_polygon, facecolor=cps.grey[2], edgecolor=cps.grey[1], linewidth=0.5*sz_ratio)

            xr0 = gm.range(list(x_exterior) + list(xr0) if xr0 else x_exterior)
            yr0 = gm.range(list(y_exterior) + list(yr0) if yr0 else y_exterior)

        # do craters
        rims,wkt = self.find_rims(craters=craters,ns=30)
        for r in rims:
            x, y = ortho_proj(r[0],r[1])
            ax.plot(x, y, color=cps.palette[0], linewidth=0.3*cps.sz_ratio,zorder=2)

            xr0 = gm.range(list(x) + list(xr0) )
            yr0 = gm.range(list(y) + list(yr0) )

        xr = np.array(gm.range(xr0)) + np.array([-1, 1]) * gm.mag(xr0) * (.1 if ax is cps.ax else .02)
        yr = np.array(gm.range(yr0)) + np.array([-1, 1]) * gm.mag(yr0) * (.1 if ax is cps.ax else .02)

        # do gridlines - this probably needs improving for poles
        if grid:
            lonr, latr = ortho_proj(xr0, yr0, inverse=True)

            xtickv = gm.ticks(lonr, 6)
            ytickv = gm.ticks(latr, 6)

            ns=50
            dlat = ytickv[1]-ytickv[0]
            dlon = xtickv[1]-xtickv[0]
            offset = (ax.transData.transform_point((0, dlat))[1] - ax.transData.transform_point((0, 0))[1])/2e4*cps.scaled_pt_size
            # Plot parallels (latitude lines) and meridians (longitude lines)
            for lat in ytickv[1:-1]:
                x_par, y_par = ortho_proj(np.linspace(xtickv[0]-dlat, xtickv[-1]+dlat, ns), np.repeat(lat,ns))  # plot meridians
                ax.plot(x_par, y_par, color=cps.grey[0], linewidth=0.3*cps.sz_ratio)
                ax.text(np.clip(x_par[-1],xr[0],xr[1]),np.clip(y_par[-1],yr[0],yr[1])-offset,f'{lat:.7g}°',
                        ha='right',va='top',color=cps.grey[0],fontsize=cps.scaled_pt_size*.5)
            for lon in xtickv[1:-1]:
                x_mer, y_mer = ortho_proj( np.repeat(lon,ns), np.linspace(ytickv[0]-dlon, ytickv[-1]+dlon, ns))  # plot parallels
                ax.plot(x_mer, y_mer, color=cps.grey[0], linewidth=0.3*cps.sz_ratio)
                ax.text(np.clip(x_mer[0],xr[0],xr[1]),np.clip(y_mer[0],yr[0],yr[1]),f' {lon:.7g}°',
                        ha='left',va='bottom',color=cps.grey[0],fontsize=cps.scaled_pt_size*.5)

        ax.set_xlim(xr[0],xr[1])
        ax.set_ylim(yr[0],yr[1])
        ax.set_axis_off()
        ax.set_aspect('equal', adjustable='box')


