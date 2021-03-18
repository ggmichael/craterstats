#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np

def where(e):
    if type(e) is np.ndarray:
        res=np.where(e)
        return list(res[0])

