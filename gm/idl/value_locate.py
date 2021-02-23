
import numpy as np

def value_locate(x,v): #drop-in replacement for IDL function
    res=np.searchsorted(x,v)-1
    return res