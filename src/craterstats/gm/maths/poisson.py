#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
from scipy.special import factorial

from . import normal


def poisson(k,lam,cumulative=False,threshold=23):
    '''
    poisson mass function
    vectorised in lambda, but not k

    :param k:
    :param lam:
    :param cumulative: return cmf instead of pmf
    :param threshold: use normal approximation above threshold value of k
    :return: pmf
    '''

    if k<threshold:       # poisson
        if cumulative:
            res = 0.
            for i in range(k+1):
                res += (lam**i) / factorial(i)
            return np.exp(-lam) * res
        else:
            return lam**k * np.exp(-lam) / factorial(k)

    else:                 # normal
        if cumulative:
            return normal(lam, np.sqrt(lam), k, cumulative=True)
        else:
            return normal(lam, np.sqrt(lam), k)




