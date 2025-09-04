#  Copyright (c) 2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
import math
import matplotlib.pyplot as plt
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

class Randomnessanalysis(cst.Spatialcount):
    '''Applies randomness tests to Spatialcount'''

    def __init__(self,filename=None,area_file=None):
        super().__init__(filename,area_file)
    def random_points(self ,n):
        # consider integral of cos(lat): sin(lat) - range varies from -1 to 1 for -180 to 180
        y0 = np.sin(np.radians(self.yr[0])) # move to init?
        y1 = np.sin(np.radians(self.yr[1]))
        y = np.degrees(np.asin(np.random.uniform(y0, y1, n)))
        x = np.random.uniform(self.xr[0], self.xr[1], n)
        return zip(x ,y)

    def sprinkle_discs(self ,n ,diam):
        """
        generate z random points in enclosing area
        find those in actual area
        find non-overlapping (could optimise with 2d spatial bin search)
        take first n good points
        """
        expected_hit_rate = self.area /self.enclosing_area
        shortfall = n
        p = []
        overlapped = []

        area_globe = 4 * math.pi * self.planetary_radius**2
        fraction_globe = self.enclosing_area/area_globe
        threshold = 0.1 # not sure where optimal yet

        if fraction_globe < threshold: # make points on laea
            pass
        else: # make points with fibonnacci
            pass






        # while True:
        #     z = int(1.2 * shortfall / expected_hit_rate)  # guess at required number of points
        #     p0 = self.random_points(z)
        #     for e in p0:
        #         pt = sph.create_point(longitude=e[0], latitude=e[1])
        #         if sph.within(pt, self.polygon):
        #             if all(sph.distance(pt, e, radius=self.planetary_radius ) >dia m /2 for e in p):
        #                 p += [pt]
        #             else:
        #                 overlapped += [pt]
        #     shortfall = n - len(p)
        #     if shortfall < =0:
        #         break

        return p[:n]

