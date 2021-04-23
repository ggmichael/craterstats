#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np

from . import sigfigs

def scientific_notation(n,sf=3,force=False):
    '''
    Convert number to latex-style scientific notation string

    values >0.01 and <10000 are shown without multiplier unless force=True

    :param n: number to convert
    :param sf: number of significant figures
    :param force: force notation even for low-value exponents
    :return: latex-style formatted string
    '''

    if -2 < np.log10(abs(n)) < 4 and not force:
            return sigfigs(n, sf)

    s0 = ("{:." + str(sf-1) + "e}").format(n)
    s = s0.split('e')
    return s[0]+'×10^{'+str(int(s[1]))+'}'



