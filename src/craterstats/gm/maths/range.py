#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np

def range(x,magnitude=False,outer=False):
    if len(x)==0:
        return np.nan if magnitude else np.nan,np.nan

    mn=np.min(x)
    mx=np.max(x)
    
    if outer:  # return integer range containing range
        mn=np.floor(mn)
        mx=np.ceil(mx)    
    
    if magnitude:
        return mx-mn  
    
    return mn,mx


def mag(x,outer=False):
    return range(x,magnitude=True,outer=outer)
    