# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 19:56:56 2020

@author: gmichael
"""

def bin_bias_correction(beta,k):
    #b=beta - bin boundary factor, e.g. sqrt(2)
    #k=log-log slope (incl. minus sign, e.g. -2)
    #ref: Michael (2013), Eq. 2
    
    g=beta**.5-beta**(-.5)
    Fbin2F_ratio=(beta**(k/2.)-beta**(-k/2.)) / (g*k)
    
    return Fbin2F_ratio