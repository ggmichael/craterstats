#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
import craterstats.gm as gm


def scientific_notation(n,sf=3,force=False):

    if -2 < np.log10(n) < 4 and not force:
            return gm.sigfigs(n, sf)

    s0 = ("{:." + str(sf-1) + "e}").format(n)
    s = s0.split('e')
    return s[0]+'×10^{'+str(int(s[1]))+'}'


if __name__ == '__main__':
    for j in [2,3,4]:
        for i in range(-5,5):
            print(scientific_notation(10**i*np.pi,j))
        print()

