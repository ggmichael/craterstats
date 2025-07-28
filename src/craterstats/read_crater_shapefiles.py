#  Copyright (c) 2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import math
import re
import shapefile # pyshp
import spherely as sph

import craterstats as cst
import craterstats.gm as gm

def read_crater_shapefiles(crater_file,area_file=None):
    """
    read crater and area shapefiles, extracting diameters, area, perimeter
    if area_file not specified, try to get from crater_file name
    """

    def read_shp(shp):
        prj = gm.filename(shp, 'pn1', '.prj')
        wkt = gm.read_textfile(prj)[0]
        if not wkt.startswith("GEOGCS"):
            raise ValueError("Shapefile is not using Geographic Coordinate System (GCS)")
        pattern = r'SPHEROID\["[^\"]*",\s*(\d+\.?\d*)\s*,\s*\d+\.?\d*\]'
        match = re.search(pattern, wkt)
        planetary_radius = float(match.group(1))/1e3

        sf = shapefile.Reader(shp)
        shapes = sf.shapes()
        return shapes,planetary_radius

    if not area_file:
        f = re.sub(r'CRATER', 'AREA', gm.filename(crater_file,'n'), flags=re.IGNORECASE)
        area_file = gm.filename(crater_file,'p1e',f)

    sc, rc = read_shp(crater_file)
    sa, ra = read_shp(area_file)

    if rc != ra:
        raise ValueError("Crater/Area shapefile coordinate systems disagree")

    print(f"Planetary radius: {rc:0g} km")

    multipolygon=[]
    for shape in sa:
        parts = shape.parts
        points = shape.points
        n_rings = len(parts)-1
        if n_rings==0:
            p = sph.create_polygon(shell=points)
        else:
            ext = points[:parts[1]]
            int=[]
            for i in range(1, len(parts)):
                start_idx = parts[i]
                end_idx = parts[i + 1] if i + 1 < len(parts) else len(points)
                int += [points[start_idx:end_idx]]
            p = sph.create_polygon(shell=ext,holes=int)
        print(f"Polygon has {n_rings} hole(s). Sub-area: {sph.area(p, radius=ra):.5g} km2")
        multipolygon += [p]
    p = sph.create_multipolygon(multipolygon)
    area = sph.area(p, radius=ra)
    perimeter = sph.perimeter(p, radius=ra)
    print(f"Total area {area:.5g} km2; perimeter: {perimeter:.5g} km\nDiameter, km")

    d=[]
    frac=[]
    transform = cst.Fractional_crater_fn()
    for shape in sc:
        c = sph.create_polygon(shell=shape.points)
        c_area = sph.area(c,radius = rc)
        diam = math.sqrt(4*c_area/math.pi)
        print(f"{diam:.5g}")
        d += [diam]
        if sph.covered_by(c,p):
            f = 1
        else:
            area_intersection = sph.area(sph.intersection(c,p),radius = rc)
            area_frac = area_intersection/c_area
            f = transform.af2lf(area_frac)
        frac += [f]

    return d,frac,area,perimeter

