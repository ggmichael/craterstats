#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
import craterstats.gm as gm

def str_diameter_range(d,sf=2):
    """
    Convert numerical diameters in km into string diameter range with units

    :param d: two element numerical sequence of diameters in km
    :param sf: no of significant figures
    :return: string diameter range
    """

    # \u2013 en-dash \u2009 short space
    if d[1] >=1:
        s = gm.sigfigs(d, sf)
        return '{0[0]}\u2013{0[1]} km'.format(s)
    else:
        s = gm.sigfigs(np.array(d)*1000, sf)
        return '{0[0]}\u2013{0[1]} m'.format(s)


if __name__ == '__main__':
    print(str_diameter_range(np.array([.65, 1.2])))
    print(str_diameter_range([.65, 1.2]))
    print(str_diameter_range([.65, .95]))