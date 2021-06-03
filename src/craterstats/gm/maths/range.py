#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np

def range(x,magnitude=False,outer=False):
    """
    Find min, max of vector x

    :param x: vector
    :param magnitude: return magnitude of range instead?
    :param outer: return integer range containing range?
    :return: (min,max)
    """
    if len(x)==0:
        return np.nan if magnitude else np.nan,np.nan

    mn=np.min(x)
    mx=np.max(x)
    
    if outer:
        mn=np.floor(mn)
        mx=np.ceil(mx)    
    
    if magnitude:
        return mx-mn  
    
    return mn,mx


def mag(x,outer=False):
    return range(x,magnitude=True,outer=outer)