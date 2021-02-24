#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np

def str_diameter_range(d):

    # \u2013 en-dash \u2009 short space
    if d[1] >=1:
        return '{0[0]:0g}\u2013{0[1]:0g} km'.format(d)
    else:
        return '{0[0]:0g}\u2013{0[1]:0g} m'.format(np.array(d)*1000)


if __name__ == '__main__':
    print(str_diameter_range(np.array([.65, 1.2])))
    print(str_diameter_range([.65, 1.2]))
    print(str_diameter_range([.65, .95]))