#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
from scipy.special import erf

def normal(m,s,x,cumulative=False):
    '''
    evaluate normal pdf at point(s) x

    :param m: mean
    :param s: sd
    :param x: point(s) to evaluate
    :param cumulative: return cdf instead of pdf
    :return: pdf
    '''

    if cumulative:
        return 0.5 * (1 + erf((x - m) / (s * np.sqrt(2.))))
    else:
        return np.exp(-((x-m)**2)/(2*s**2))/(s*np.sqrt(2*np.pi))


