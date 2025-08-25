#  Copyright (c) 2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
import math
import re
import shapefile  # pyshp
import shapely as shp
import spherely as sph
import pyproj as prj
import os
import shutil
from datetime import datetime

import craterstats as cst
import craterstats.gm as gm


class Spatialcount:
    '''Reads spatial crater count data'''

    def __init__(self,filename=None,area_file=None):
        self.filename=filename
        filetype = gm.filename(filename, 'e') if filename else None

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

    # may be useful later again, but not used now:
    # def llr2xyz(lon,lat,r):
    #     lat_rad = math.radians(lat)
    #     lon_rad = math.radians(lon)
    #     x = r * math.cos(lat_rad) * math.cos(lon_rad)
    #     y = r * math.cos(lat_rad) * math.sin(lon_rad)
    #     z = r * math.sin(lat_rad)
    #     return x,y,z
    # def xyz(pts):
    #     return [llr2xyz(lon,lat,self.planetary_radius) for lon,lat in pts]

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

        print(f"Planetary radius: {self.planetary_radius:0g} km")
        print(f"Area: {self.area:.2f} km2, perimeter: {self.perimeter:.2f} km")

        n_pole = sph.create_point(longitude=0, latitude=90)
        s_pole = sph.create_point(longitude=0, latitude=-90)
        if sph.covers(p, n_pole):
            yr = (yr[0], 90)
            xr = (-180,180)
        if sph.covers(p, s_pole):
            yr = (-90, yr[1])
            xr = (-180, 180)

        print(f"Range: {xr[0]:2f}:{xr[1]:2f} {yr[0]:2f}:{yr[1]:2f}")
        self.xr=xr
        self.yr=yr
        enclosing_polygon = sph.create_polygon(shell=[(xr[0],yr[0]),(xr[0],yr[1]),(xr[1],yr[1]),(xr[1],yr[0])])
        self.enclosing_area = sph.area(enclosing_polygon, radius=self.planetary_radius)
        print(f"Enclosing area: {self.enclosing_area:.2f} km2")


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
        transform = cst.Fractional_crater_fn()
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
        # do crater file
        fc = gm.filename(filename,'pn1e',"_CRATER")
        c = shapefile.Writer(fc)
        c.field('Diam_km', 'F', 12,6)
        c.field('x_coord', 'F', 20,15)
        c.field('y_coord', 'F', 20, 15)
        c.field('tag', 'C', 20)

        ns = 100
        theta = [2 * math.pi * i / ns for i in range(ns + 1)]
        cx,cy = np.array([(math.cos(e), math.sin(e)) for e in theta]).T

        rs = f'{self.planetary_radius * 1e3:0.0f}'
        wkt = f'GEOGCS["Spherical_GCS_{rs}", DATUM["Sphere_{rs}", SPHEROID["Sphere_{rs}", {rs}, 0]], PRIMEM["Greenwich", 0], UNIT["Degree", 0.0174532925199433]]'
        geod = prj.CRS(wkt)

        for d,x,y in zip(self.diam,self.lon,self.lat):
            proj4 = f"+proj=laea +lat_ts=0 +lat_0={y} +lon_0={x} +R={self.planetary_radius * 1e3:0.0f} +units=m +no_defs"
            laea=prj.CRS(proj4)
            transformer = prj.Transformer.from_crs(laea, geod, always_xy=True) #laea.geodetic_crs
            r = d * 1e3 / 2
            ll_pts = transformer.transform(cx * r, cy * r)
            c.record(Diam_km=d, x_coord=x, y_coord=y, tag='standard')
            c.poly([list(zip(*ll_pts))])
        c.close()
        gm.write_textfile(gm.filename(fc,'pn1','.prj'),wkt)
        shutil.copy(cst.PATH + 'config/_CRATER.qml', gm.filename(fc,'pn1','.qml'))

        # do area file
        fa = gm.filename(filename, 'pn1e', "_AREA")
        a = shapefile.Writer(fa)
        a.field('area', 'F', 12,6)
        a.field('area_name', 'C', 30)

        for i,p in enumerate(self.polygon if isinstance(self.polygon, list) else [self.polygon]):
            z = sph.to_wkb(p)
            y = shp.from_wkb(z)
            x = shp.get_exterior_ring(y)
            rings = [list(x.coords)]
            for j in range(shp.get_num_interior_rings(y)):
                x = shp.get_interior_ring(y,j)
                rings.append(list(x.coords))  # Append holes
            a.poly(rings)
            a.record(None, f'Area_{i + 1}')
        a.close()
        gm.write_textfile(gm.filename(fa, 'pn1', '.prj'), wkt)
        shutil.copy(cst.PATH + 'config/_AREA.qml', gm.filename(fa, 'pn1', '.qml'))








