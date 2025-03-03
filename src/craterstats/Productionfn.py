#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import sys
import numpy as np
import scipy.optimize as sc

import craterstats as cst
import craterstats.gm as gm


class Productionfn:
    
    def __init__(self,source,identifier,equilibrium=False):
        
        self.name=identifier
        pf_type='equilibrium' if equilibrium else 'production'
        
        if type(source) is dict:
            src=source
        else:
            if '\n' in source: # multiline string is definition
                txt = source + '\n'+pf_type+'={\n name="null"\n}' # add null entry to force implied array
            else: # single line string is filename
                txt = gm.read_textfile(source, as_string=True, ignore_hash=True)
            src = gm.read_textstructure(txt, from_string=True)
        
        self.definition=next((e for e in src[pf_type] if e['name']==identifier), None)
        if self.definition is None:
            raise ValueError(pf_type.title()+' function not found: '+identifier)
        
        self.type=self.definition['type'] if 'type' in self.definition else 'polynomial'

        if 'range' in self.definition:
            self.range=np.float32(np.array(self.definition['range']))
        else:
            self.range = np.array([1e-4, 2e3])  # default max range

        if 'yrange' in self.definition: #for fixed Hartmann plots
            self.yrange=np.float32(np.array(self.definition['yrange']))

        if self.type=='polynomial':
            self.a=[float(e) for e in self.definition['coefficients']]
            self.C = self.polynomial_C
            self.C10 = self.polynomial_C10
            self.F = self.polynomial_F
            self.F10 = self.polynomial_F10
            self.R = self.polynomial_R
            self.H = self.polynomial_H
            
        elif self.type=='tabular incremental root-2':
            h=[float(e) for e in self.definition['H']]
            index_1km=int(self.definition['index_1km'])
            hC10=np.log10(list(reversed(np.cumsum(list(reversed(h))))))
            self.hC10=hC10-hC10[index_1km]

            d_min=np.array([2**((i-index_1km)/2) for i,e in enumerate(h)])
            d_mean=d_min*2**.25
            self.d_min10=np.log10(d_min)
            self.d_mean10=np.log10(d_mean)
            self.range=d_mean[[0,-1]]
            self.xrange = np.log10([d_min[0],d_min[-1]*2**.5]) # plot axis range

            self.C = self.hartmann_C
            self.C10 = self.hartmann_C10
            self.F = self.hartmann_F
            self.F10 = self.hartmann_F10
            self.R = self.hartmann_R
            self.H = self.hartmann_H

    def __str__(self):
        return self.name

    def evaluate(self,presentation,d,a0=None):
        '''
        Evaluate PF according to presentation string

        :param presentation: presentation string
        :param d: series of crater diameters (km)
        :param a0: a0
        :return: y-values
        '''
        if not a0:
            a0 = self.a[0] if hasattr(self,'a') else 0.
        if presentation=='cumulative':
            return self.C(d,a0)
        elif presentation=='differential':
            return self.F(d,a0)
        elif presentation=='R-plot':
            return self.R(d,a0)
        elif presentation=='Hartmann':
            return self.H(d,a0)
        
           
#polynomial pf

    def polynomial_C10(self, d10, a0):
        a = [a0] + self.a[1:]
        C10 = gm.poly(a, d10)
        return C10

    def polynomial_C(self,d,a0): #cumulative fn
        x=np.log10(d)
        C=10**self.polynomial_C10(x,a0)
        return C

    def polynomial_F10(self, d10, a0):
        F10 = np.log10(self.polynomial_F(10**d10,a0))
        return F10
    
    def polynomial_F(self,d,a0): #differential form
        x=np.log10(d)
        a=[a0]+self.a[1:]
        p= gm.poly(a, x)
        dCdp=np.log(10.)*10.**p
        a_dash=[(i+1)*e for i,e in enumerate(a[1:])]
        dpdx= gm.poly(a_dash, x)
        dxdD=1./(d*np.log(10.))    
        F=-dCdp*dpdx*dxdD  #(Michael & Neukum 2010, Eq 1)
        return F
    
    def polynomial_R(self,d,a0): #relative (R) (Arvidson et al, 1979)
        F=self.polynomial_F(d,a0)  
        R=F/(d**(-3.))          
        return R
    
    def polynomial_H(self,d,a0): #Hartmann diagram 
        F=self.polynomial_F(d,a0)
        H=F*d*(2**.25-2**(-.25)) #adjust to bin minimum (Michael 2013, Eq. 1)
        return H

#Hartmann tabular incremental root-2

    def hartmann_C10(self,d10,a0): #cumulative fn
        return self.hartmann_calc(d10,a0,'C10',log10=True)

    def hartmann_C(self,d,a0): #cumulative fn
        return self.hartmann_calc(d,a0,'C')
        
    def hartmann_H(self,d,a0): #Hartmann diagram 
        return self.hartmann_calc(d,a0,'H')
    
    def hartmann_F10(self,d10,a0): #differential form
        return self.hartmann_calc(d10,a0,'F10',log10=True)

    def hartmann_F(self,d,a0): #differential form
        return self.hartmann_calc(d,a0,'F')

    def hartmann_R(self,d,a0): #relative (R) (Arvidson et al, 1979)  
        return self.hartmann_calc(d,a0,'R')
    
    def hartmann_calc(self,x,a0,mode,log10=False):
        #C,H,F,R - lower case represent continuous functions; upper case - evaluations for given d
        d10=x if log10 else np.log10(x)
        c=10**(self.hC10+a0)
        
        if mode in ('C','C10'):
            C10 = np.interp(d10, self.d_min10, np.log10(c))
            return 10**C10 if mode=='C' else C10

        h=c-np.concatenate((c[1:],[0]))
        
        if mode=='H':
            H=10**np.interp(d10,self.d_mean10,np.log10(h))
            return H
        
        beta=np.sqrt(2)
        bin_width0=2**.25-2**-.25
        f_bin=h/(10**self.d_mean10)/bin_width0

        k = (self.hC10 - np.roll(self.hC10,-1)) / np.log10(beta)
        k[-1]=k[-2] #fix slope at end to be continuous
        bc=cst.bin_bias_correction(beta, k) #remove binning bias
        f=f_bin/bc       
        
        if mode in ('F','F10'):
            F10=np.interp(d10,self.d_mean10,np.log10(f))
            return 10**F10 if mode=='F' else F10
        
        r=f/(10**self.d_mean10)**-3
        
        if mode=='R': 
            R=10**np.interp(d10,self.d_mean10,np.log10(r))
            return R


    def fit(self,p):
        '''
        Make fit to points supplied in dict, according to presentation (cumulative or differential)

        :param p: dict containing presentation, y, d and err fields
        :return: a0 tuple: (fit, lower, upper)
        '''
        y, d, err = p['y'], p['d'], p['err']

        if type(y) is np.ndarray:
            if y.size == 0:
                sys.exit('Cannot fit to empty range')
            if y.size==1:
                y,d,err=y[0],d[0],err[0] # must convert to float so that next line works for float or ndarray
        if isinstance(y, (np.floating, float)): #allow to call with single values for conversion
            y,d,err=np.array([y,y]),np.array([d,d]),np.array([err,err])

        with np.errstate(divide='ignore'):
            if p['presentation'] == 'cumulative':
                func, sigma = self.C10, 1 / np.sqrt(y)
            elif p['presentation'] == 'differential':
                func, sigma = self.F10, 1 / np.sqrt(err)

        popt, pcov = sc.curve_fit(func, np.log10(d), np.log10(y),sigma=sigma)
        a0=popt[0]-[0,np.log10(y[0])-np.log10(y[0]-.98*err[0]),np.log10(y[0])-np.log10(y[0]+.98*err[0])]
        return a0


    def getplotdata(self,presentation,a0=None,range=None):
        '''
        Return dict of values for plotting PF

        :param presentation: presentation string
        :param a0: a0
        :param range: diameter range
        :return: dict with series of values for plotting
        '''
        ns=400
        if a0 is None: a0 = self.a[0]
        if range is None: range=self.range
        range=np.clip(range,self.range[0],self.range[1])
        log_d=np.linspace(np.log10(range[0]),np.log10(range[1]),ns)
        d=10.**log_d
        y=self.evaluate(presentation,d,a0)
        return {'presentation':presentation,'d':d,'y':y}


    def getisochron(self,presentation,a0,ef):
        '''
        Return series of values for plotting isochron, optionally truncated by equilibrium function curve

        :param presentation: presentation string
        :param a0: a0
        :param ef: equilibrium function instance (optional)
        :return: dict with series of values for plotting
        '''

        iso=self.getplotdata(presentation,a0)
        if ef:
            e=ef.getplotdata(presentation)
            j= gm.value_locate(e['d'], iso['d'])
            q= gm.where(iso['y'] < e['y'][j] * .8)
            iso={'presentation':presentation,'d':iso['d'][q],'y':iso['y'][q]}

        return iso
