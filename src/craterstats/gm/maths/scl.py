#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np


def scl(x,in_range=None,out_range=None,tname=None,double=False):

# function gm_scl,x,in_range=in_range,out_range=out_range,byte=byte,int=int,uint=uint,double=double
#   ;more powerful bytscl function - type taken from out_range if present, otherwise x
#   ;in_range - range of input data to be stretched
#   ;out_range - output range
#   ;double - if set, do calculation in doubles (for mosaic metre values)

    if tname==None:
        tname=type(x[0]) if out_range==None else type(out_range[0])
    
    mn=min(x)
    mx=max(x)
    if in_range != None:
        mn=in_range[0]
        mx=in_range[1]
    
    if out_range == None:
      eps=1e-9 
      if tname is np.uint16: out_range=[0,65536-eps]
      elif tname is np.int16: out_range=[-32768,32768-eps]
      elif tname is np.ubyte: out_range=[0,256-eps]  
      else:out_range=[0,100-eps]

    if double:
          y=(np.float64(x)-mn)/(mx-mn)
    else:          
          y=(np.float32(x)-mn)/(mx-mn)
    
    y.clip(min=0., max=1.,out=y)
    out=out_range[0]+y*(out_range[1]-out_range[0])
     
    return np.array(out,dtype=tname)



if __name__ == '__main__':
    a=scl(np.linspace(2,7,9),out_range=[10,20])
    print(a)
