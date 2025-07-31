#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
import craterstats as cst
import craterstats.gm as gm
import spherely as sph
import random
import math
import re


class Spatialcount:
    '''Reads spatial crater count data'''

    def __init__(self,filename=None):
        self.filename=filename
        filetype = gm.filename(filename, 'e', max_ext_length=6) if filename else None

        if filetype == '.scc':
            self.readSCCfile()

    def readSCCfile(self):
        def llr2xyz(lon,lat,r):
            lat_rad = math.radians(lat)
            lon_rad = math.radians(lon)
            x = r * math.cos(lat_rad) * math.cos(lon_rad)
            y = r * math.cos(lat_rad) * math.sin(lon_rad)
            z = r * math.sin(lat_rad)
            return x,y,z
        def xyz(pts):
            return [llr2xyz(lon,lat,self.planetary_radius) for lon,lat in pts]


        self.cratercount = cst.Cratercount(self.filename)

        s = gm.read_textfile(self.filename,ignore_hash=True,strip=';', as_string=True)
        s = re.sub(r"a-axis radius", "a_axis_radius", s) # fix OpenCraterTool misformatting
        c = gm.read_textstructure(s,from_string=True)
        self.planetary_radius = float(c['a_axis_radius'].split(' ')[0])

        b = c['unit_boundary']
        z = sorted(set([(int(a), b == 'int') for a, b in zip(b['sub_area'], b['tag'])]))

        d={}
        for i, _ in z:
            pts = [(float(x),float(y)) for x,y, sub_area in zip(c['unit_boundary']['lon'],c['unit_boundary']['lat'], c['unit_boundary']['sub_area']) if int(sub_area) == i]
            p = sph.create_polygon(shell=pts)
            d[i] = (pts, p, xyz(pts))
            xr1 = gm.range([x for x,y in pts])
            yr1 = gm.range([y for x, y in pts])
            if i == 1:
                xr=xr1
                yr=yr1
            else:
                xr = (min(xr1[0], xr[0]), max(xr1[1], xr[1]))
                yr = (min(yr1[0], yr[0]), max(yr1[1], yr[1]))

        import shapely as shp
        q=[]
        p=[]
        for i, internal in z:
            if not internal:
                holes=[]
                qholes = []
                for j, internal1 in z[i:]:
                    if sph.within(d[j][1],d[i][1]):
                        holes += [d[j][0]]
                        #qholes += [d[j][2]]
                p += [sph.create_polygon(shell=d[i][0], holes=holes)]
                q += [shp.Polygon(shell=d[i][2], holes=qholes)]

        p = sph.create_multipolygon(p) #merge if multiple

        self.area=sph.area(p, radius=self.planetary_radius)
        self.perimeter=sph.perimeter(p, radius=self.planetary_radius)
        self.polygon=p
        self.shape=shp.MultiPolygon(q)
        self.q=d[1][0]

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

    def random_points(self,n):
        # consider integral of cos(lat): sin(lat) - range varies from -1 to 1 for -180 to 180
        y0 = np.sin(np.radians(self.yr[0])) # move to init?
        y1 = np.sin(np.radians(self.yr[1]))
        y = np.degrees(np.asin(np.random.uniform(y0, y1, n)))
        x = np.random.uniform(self.xr[0], self.xr[1], n)
        return zip(x,y)

    def sprinkle_discs(self,n,diam):
        """
        generate z random points in enclosing area
        find those in actual area
        find non-overlapping (could optimise with 2d spatial bin search)
        take first n good points
        """
        expected_hit_rate = self.area/self.enclosing_area
        shortfall = n
        p = []
        overlapped = []

        while True:
            z = int(1.2 * shortfall / expected_hit_rate)  # guess at required number of points
            p0 = self.random_points(z)
            for e in p0:
                pt = sph.create_point(longitude=e[0], latitude=e[1])
                if sph.within(pt, self.polygon):
                    if all(sph.distance(pt, e, radius=self.planetary_radius)>diam/2 for e in p):
                        p += [pt]
                    else:
                        overlapped += [pt]
            shortfall = n - len(p)
            if shortfall <=0:
                break

        return p[:n]

    def plain_plot(self,p):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        # plot the unit sphere for reference (optional)
        # u = np.linspace(0, 2 * np.pi, 100)
        # v = np.linspace(0, np.pi, 100)
        # x = np.outer(np.cos(u), np.sin(v))
        # y = np.outer(np.sin(u), np.sin(v))
        # z = np.outer(np.ones(np.size(u)), np.cos(v))
        # ax.plot_surface(x, y, z, color='y', alpha=0.1)


        lam = np.radians(sph.get_x(p))
        phi = np.radians(sph.get_y(p))
        x = np.cos(phi) * np.cos(lam)
        y = np.cos(phi) * np.sin(lam)
        z = np.sin(phi)

        ax.scatter(x,y,z, c='b')

        plt.show()

        print()





