#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
import types
import craterstats.gm as gm


def import_code(code):
    module = types.ModuleType('cf')
    exec(code, module.__dict__)
    return module


class Chronologyfn:
    
    def __init__(self,source,identifier):
        
        t_steps=1000
        self.lambda_n1=None
        self.lambda_phi=None

        self.name=identifier
        
        if type(source) is dict:
            src=source
        else:
            if '\n' in source: # multiline string is definition
                txt = source + '\nchronology={\n name="null"\n}' # add null entry to force implied array
            else: # single line string is filename
                txt = gm.read_textfile(source, as_string=True, ignore_hash=True)
            src = gm.read_textstructure(txt, from_string=True)
        
        self.definition=next((e for e in src['chronology'] if e['name']==identifier),None)
        if self.definition is None:
            raise ValueError('Chronology function not found: '+identifier)
              
        if 'coefficients' in self.definition:            
            p=[float(e) for e in self.definition['coefficients']]
            self.lambda_n1 = lambda t: p[0]*(np.exp(p[1]*t)-1.)+p[3]*t
            self.lambda_phi = lambda t: p[1]*p[0]*np.exp(p[1]*t)+p[3]  
      
        if 'n1_code' in self.definition:
            # '*' allows unforseen fns to be used in user code without np prefix (or user-awareness of python)
            code='from numpy import *\n' \
                'def n1(t):\n' \
                +'\n'.join(['  '+e.strip() for e in self.definition['n1_code'].splitlines()]) \
                +'\n  return n1'
            m=import_code(code)
            self.lambda_n1=m.n1
            
        self.ts=np.linspace(0.,5.,t_steps)
        self.n1s=self.N1(self.ts)     
        
    def __str__(self):
        return self.name
    
    def N1(self,t):  #t in Ga
        return self.lambda_n1(t)

    def a0(self,t):
        return np.log10(self.N1(t))
        
    def phi(self,t): #phi = dN1/dt - the impact rate [/Ga]
        if self.lambda_phi is None:
            dt=t/1e4
            return (self.N1(t+dt)-self.N1(t-dt))/(2.*dt)
        else:
            return self.lambda_phi(t)
        
    def t(self,a0=None,n1=None):
        if not a0 is None:
            n1=10**a0
        
        t=np.interp(n1,self.n1s,self.ts)
        return t
             
    def getplotdata(self,phi=False,linear=False):
        ns=1000
        t=np.linspace(0.,5.,ns) if linear else 10**np.linspace(-9,np.log10(5),ns) #maybe could reuse self.t (switch to log there?)
        y=self.phi(t) if phi else self.N1(t)
        return t,y






