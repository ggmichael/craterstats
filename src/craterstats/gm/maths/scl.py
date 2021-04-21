#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np


def scl(x,in_range=None,out_range=None,tname=None,double=False):
    '''
    scale to integer range - output type taken from out_range if present, otherwise from x

    :param x: source array
    :param in_range: range of input data to be stretched (optional)
    :param out_range: desired output range (optional)
    :param tname: desired output type, 'byte','int16','uint16' (optional)
    :param double: if set, do calculation in doubles
    :return: rescaled data
    '''

    if tname==None:
        dtype=type(x[0]) if out_range==None else type(out_range[0])
    
    mn=min(x)
    mx=max(x)
    if in_range != None:
        mn=in_range[0]
        mx=in_range[1]
    
    if out_range == None:
      eps16 = 1e-2
      eps8 = 1e-5
      if tname == 'uint16':
          dtype=np.uint16
          out_range=[0.,65536-eps16]
      elif tname == 'int16':
          dtype = np.int16
          out_range=[-32768.,32768-eps16]
      elif tname == 'byte':
          dtype=np.ubyte
          out_range=[0.,256-eps8]
      else:
          out_range=[0.,100-eps8]

    if double:
          y=(np.float64(x)-mn)/(mx-mn)
    else:          
          y=(np.float32(x)-mn)/(mx-mn)
    
    y.clip(min=0., max=1.,out=y)
    out=out_range[0]+y*(out_range[1]-out_range[0])
     
    return np.array(out,dtype=dtype)



if __name__ == '__main__':
    a=np.linspace(2,7,4)
    print(scl(a, tname='byte'))
    print(scl(a, tname='int16'))
    print(scl(a, tname='uint16'))

    print(scl(a,out_range=[10,20]))