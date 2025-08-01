#  Copyright (c) 2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import math
import re
import shapefile  # pyshp
import spherely as sph
import pyproj as prj
import os
from datetime import datetime

import craterstats as cst
import craterstats.gm as gm


class Cratershapefile:
    '''Read shapefile pair created by CraterTools, OpenCraterTool, or ArcPro'''

    def __init__(self, crater_file=None, area_file=None):
        if not area_file:  # if area_file not specified, try to get from crater_file name
            f = re.sub(r'CRATER', 'AREA', gm.filename(crater_file, 'n'))
            area_file = gm.filename(crater_file, 'p1e', f)
        self.crater_file = crater_file
        self.area_file = area_file
        self.name = re.sub(r'_?CRATER_?', '', gm.filename(crater_file, "n"))

    def read(self):
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

    def print(self):
        print(f"\nPlanetary radius: {self.planetary_radius:0g} km")
        print(f"Total area {self.area:.7g} km2\nperimeter: {self.perimeter:.5g} km")
        print("\nDiameter, km  fraction      lon                  lat")
        for d, f, x, y in zip(self.diam, self.fraction, self.lon, self.lat):
            print(f"{d:<12.7g} {f:9.3g} {x:20.12f} {y:20.12f}")

    def write_scc(self,filename=None):
        sub_area, tag, pts = [],[],[]
        i = 1
        for shape in self.sa:
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

        # include so that can import into OpenCratertool (also requires col 5 for craters)
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
