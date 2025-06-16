#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
import craterstats.gm as gm

def diameter_range(d,sf=2):
    """
    Convert numerical diameters in km into string diameter range with units

    :param d: two element numerical sequence of diameters in km
    :param sf: no of significant figures
    :return: string diameter range
    """

    # \u2013 en-dash \u2009 short space
    if np.isinf(d[1]):
        return 'unconstrained'

    if d[1] >=1:
        s = gm.sigfigs(d, sf)
        return f"{s[0]}\u2013{s[1]} km"
    else:
        s = gm.sigfigs(np.array(d)*1000, sf)
        return f"{s[0]}\u2013{s[1]} m"


if __name__ == '__main__':
    print(diameter_range(np.array([.65, 1.2])))
    print(diameter_range([.65, 1.2]))
    print(diameter_range([.65, .95]))