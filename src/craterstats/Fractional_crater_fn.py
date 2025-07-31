#  Copyright (c) 2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
import craterstats.gm as gm
import matplotlib.pyplot as plt

class Fractional_crater_fn:
    '''
    Transform function between area fraction and linear fraction over boundary.
    Easy to measure the polygon area overlap, but require fractional linear overlap for
    statistics. (Originally suggested by Misha Kreslavsky)

    After initialisation, able to call inverse function af2lf()
    '''

    def __init__(self):
        self.lf = np.array(gm.scl(range(100), out_range=[0., 1]))
        self.af = self.area_fraction(self.lf)

    def area_fraction(self,lf):
        d = 1 - 2 * lf
        theta = 2 * np.arccos(d)
        return (1 / (2 * np.pi)) * (theta - np.sin(theta))

    def af2lf(self,af):
        lf = np.interp(af, self.af, self.lf)
        return lf

    def plot(self):
        plt.plot(self.lf, self.af)
        plt.plot([0,1],[0,1],color='r')
        plt.gca().set_aspect('equal', adjustable='box')
        plt.xlabel('linear frac')
        plt.ylabel('area frac')
        plt.show()

