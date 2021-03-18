#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
from scipy.integrate import simps

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import gm
import craterstatslib as cst


class Craterpdf:

    def __init__(self, pf,cf,cc,d_range,bcc=None,n_samples=3000):

        x=np.linspace(-10, 3, n_samples) #additive change to a0 (equidistant in fitting space)
        a0=cf.a0(1.)
        self.ts = cf.t(a0=a0+x)
        self.dt = self.ts - np.roll(self.ts, 1)
        self.dt[0] = self.dt[1]

        if cc.diam:
            d = [e for e in cc.diam if d_range[0] < e < d_range[1]]  # I'd prefer ge and lt, but this comes out consistent with binning
            self.k = len(d)
        else:   # means we have a binned-only count
            b = cc['binned']
            q = np.where(b['d_min'] >= d_range[0] and b['d_max'] <= d_range[1])
            self.k = np.sum(b['.n_event'][q])

        if bcc: #buffered count
            ns=300 #samples of PF for integration
            d=np.linspace(d_range[0], d_range[1], ns)
            F=pf.F(d,a0)
            y=(cc.area+d*cc.perimeter/2.+np.pi*d**2/8.)*F
            I1=simps(y,d)
            lam=I1
        else: #standard count
            Ncum=pf.evaluate("cumulative",d_range,a0)
            Ninc=(Ncum[0]-Ncum[1])*cc.area #no expected on area in bin in 1 Ga... this is assuming constant impact rate; lambda=Ninc
            lam=Ninc

        pdf0= gm.poisson(self.k, lam * 10 ** x)
        self.pdf=pdf0/np.sum(pdf0*self.dt)
        self.cdf=np.cumsum(self.pdf*self.dt)


    def t(self,cum_fraction): #interpolate percentiles
        return np.interp(cum_fraction,self.cdf,self.ts)


    def plot(self,ax=None,pt_size=9,color='0'):
        if not ax:
            ax = plt.subplot(1,1,1)

        linewidth=.5 * pt_size / 9
        t=self.t([.003,.16,.5,.84,.997])
        p=np.searchsorted(self.ts,t)-1

        max_ticks=3
        xt= gm.ticks(np.append(0, t), max_ticks)
        max_t=np.max(xt)
        max_text=cst.str_age(max_t, simple=True)
        a=max_text.split(' ')
        xt_units=float(a[0])/max_t*xt
        xt_label=['{:g}'.format(e) for e in xt_units]
        xt_label[-1]="      "+xt_label[-1]+" "+a[1]   # add unit to last label, e.g. "Ga"

        ax.plot(self.ts,self.pdf,lw=linewidth*1.5,color=color)
        ax.patch.set_facecolor('none') # make region transparent over background graphics
        ax.fill_between(self.ts[p[1]:p[3]], self.pdf[p[1]:p[3]], 0,  color=color, alpha=0.35,  edgecolor=color, lw=linewidth) #'.7'
        ax.fill_between(self.ts[p[2]:p[2]+1], self.pdf[p[2]:p[2]+1], edgecolor=color, lw=linewidth, alpha=.5)

        ax.get_yaxis().set_visible(False)
        for e in ['right','left','top']: ax.spines[e].set_visible(False)
        ax.spines['bottom'].set_linewidth(linewidth)
        ax.spines['bottom'].set_color(color)

        ax.set_xbound(lower=0, upper=xt[1])
        ax.set_xticks(xt)
        ax.tick_params(axis='x', which='both', width=linewidth, length=pt_size * .2, pad=pt_size * .1, color=color)
        ax.tick_params(axis='x', which='minor', length=pt_size * .1)
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
        ax.set_xticklabels(xt_label,fontsize=pt_size*.7, color=color)#,horizontalalignment='left')

    def offset(self,left): # for correct spacing of age text from mini-plot peak, in +ve x-direction
        t=self.t(.997)
        max_ticks=3
        xt= gm.ticks(np.append(0, t), max_ticks)
        q=np.where(self.pdf > np.max(self.pdf)/2)
        edges=self.ts[[q[0][0],q[0][-1]]]
        norm=edges/np.max(xt)
        offset=(1-norm[1])-.1 if left else -norm[0]+.1
        return offset




