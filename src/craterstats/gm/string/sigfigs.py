#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
import re

def sigfigs(n, digits):

    if isinstance(n, (list, tuple, np.ndarray)):
        return [sigfigs(e,digits) for e in n]

    s=f"{n:.{digits - 1}e}"
    m=re.search(r"(?P<sign>-?)(?P<num>[\d\.]*)e(?P<exp>.*)",s)
    sf=m['num'].replace('.','')    
    e=int(m['exp'])

    #construct output for 4 different cases   
    if e<0:                             #insert leading zeros
        res='0.'+'0'*(abs(e)-1)+sf  
    elif e<digits-1:                    #insert intermediate decimal point
        res=sf[:e+1]+'.'+sf[e+1:]
    elif e<digits-1:                    #no decimal required
        res=sf
    else:                               #add trailing zeros
        res=sf+'0'*(e-digits+1)
        
    res=m['sign']+res
    
    return res

if __name__ == '__main__':
    print(sigfigs(3.14159,3))
    print(sigfigs(3.14159,2))
    print(sigfigs(112.14159,2)) # should be '110'
    print(sigfigs(-.0314159,3))
    print(sigfigs(314759,3))
    print(sigfigs(31.4759,1))
    print(sigfigs([243.3,0.3422],2))