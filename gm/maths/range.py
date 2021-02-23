# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 12:26:50 2020

@author: gmichael
"""

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
    