# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 18:08:26 2020

@author: gmichael
"""

import numpy as np

def where(e):
    if type(e) is np.ndarray:
        res=np.where(e)
        return list(res[0])


# def where(a,f):
#     #replace IDL where() for lists
#     #a - list
#     #f should be a lambda fun for one element of a
#
#     return [i for i,e in enumerate(a) if f(e)]
#
#
# # a=[4,5,7,9,12]
# # print(where(a,lambda x:x>6))
#
#
#
# def index(a,q):
#     return [a[i] for i in q]