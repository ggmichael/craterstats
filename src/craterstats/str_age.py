#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import craterstats.gm as gm

def str_age(age,e1=0,e2=0,sf=3,ga=False,simple=False,no_error=False,mu=False,dict=False):
    #ga - force Ga unit
    #simple - don't show unnecessary decimals (for isochrons), nor use '$' for craterpdf
    #no_error - don't show errors
    #sf - sig figs (3 or 2?)

    if ga: 
        a=(1,'Ga')
    else:
        f=[1,1e-3,1e-6,1e-9]
        unit=['Ga','Ma','ka','a']        
        a=next((e,u) for e,u in zip(f,unit) if age>=e)

    v=age/a[0]

    if simple:
        st='{:g}'.format(v)
    else:
        st= gm.sigfigs(v, sf)

    if e1>0 and not no_error :
        e1s = gm.sigfigs(e1 / a[0], sf - 1)
        e2s = gm.sigfigs(e2 / a[0], sf - 1)
        st=st+'^{+'+e1s+'}_{-'+e2s+'}'

    if mu:
        st='\mu'+st
      
    if not simple:
        st='$'+st+'$'

    st += ' '+a[1]
    
    return st

if __name__ == '__main__':
    print(str_age(.314,.11,.14))
    print(str_age(.314, .11, .14,ga=True,mu=True))
    print(str_age(.314, simple=True))
