#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np

def value_locate(x,v):
    '''
    safe replacement for IDL value_locate function

    :param x:
    :param v:
    :return:
    '''
    return np.searchsorted(x,v)-1