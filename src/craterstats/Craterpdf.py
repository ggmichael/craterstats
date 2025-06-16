#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import sys

import numpy as np
import math
from scipy.integrate import simpson

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import craterstats as cst
import craterstats.gm as gm


class Craterpdf:
    """
    Create and plot age uncertainty distribution function

    """

    def __init__(self, pf,cf,cc,d_range,k=None,lam=None,bcc=False,n_samples=5000):
        """
        :param pf: Productionfn object
        :param cf: Chronologyfn object
        :param cc: Cratercount object
        :param d_range: diameter range (km)
        :param k: number of craters in range (normally not required - calculated from cc)
        :param lam: lambda for 1 Ga (if wish to force value, e.g. for probability calculation)
        :param bcc: buffered crater count?
        :param n_samples: number of samples for likelihood curve
        """

        x=np.linspace(-10, 5, n_samples) #additive change to a0 (equidistant in fitting space)
        a0=cf.a0(1.)
        self.ts = cf.t(a0=a0+x)
        self.dt = self.ts - np.roll(self.ts, 1)
        self.dt[0] = self.dt[1]

        if k is not None:
            self.k=k
        elif cc.diam:
            d = [e for e in cc.diam if d_range[0] <= e < d_range[1]]
            self.k = len(d)
        else:   # we have a binned-only count
            b = cc['binned']
            q = np.where(b['d_min'] >= d_range[0] and b['d_max'] <= d_range[1])
            self.k = np.sum(b['.n_event'][q])

        if not lam:
            if bcc: #buffered count
                if cc.perimeter is None:
                    sys.exit('Error: buffered-poisson calculation requires polygon perimeter in source file')
                ns=500 #samples of PF for integration
                d=np.linspace(d_range[0], d_range[1], ns)
                F=pf.F(d,a0)
                y=(cc.area+d*cc.perimeter/2.+np.pi*d**2/8.)*F
                I1=simpson(y,d)
                lam=I1
            else: #standard count
                Ncum=pf.evaluate("cumulative",d_range,a0)
                Ninc=(Ncum[0]-Ncum[1])*cc.area # no expected on area with phi(1 Ga)
                lam=Ninc

        pdf0 = gm.poisson(self.k, lam * 10 ** x)
        pdf0 = pdf0.astype(float)
        if np.sum(pdf0)<1e-30: #force line peak if under-resolved
            pdf0[np.searchsorted(lam * 10 ** x,self.k)]=1.
        self.lam = lam
        self.pdf = pdf0/np.sum(pdf0*self.dt)
        self.cdf = np.cumsum(self.pdf*self.dt)


    def t(self,cum_fraction):
        """
        Return time for interpolated percentiles

        :param cum_fraction: percentile as fraction
        :return: times
        """
        return np.interp(cum_fraction,self.cdf,self.ts)

    def cumulative_fraction(self,t):
        """
        Return interpolated percentile for time

        :param t: time, Ga
        :return: cum_fraction
        """
        return np.interp(t,self.ts,self.cdf)

    def relative_probability(self,t):
        """
        Return relative_probability for time

        :param t: time, Ga
        :return: relative_probability
        """
        return np.interp(t,self.ts,self.pdf)

    def gaussian_percentiles(self,n=1):
        """
        Return ordered Gaussian n-sigma percentiles

        :param n: max n-sigma
        :return: ordered percentiles (as fractions)
        """
        g= [.5]
        for i in range(1,n+1):
            f = (1-math.erf(i/np.sqrt(2.)))/2
            g = [f]+g+[1-f]
        return g

    def median1sigma(self):
        """
        Return times for median and 1-sigma percentiles

        :return: times
        """
        g=self.gaussian_percentiles()
        return self.t([g[i] for i in [1,0,2]])


    def plot(self,ax=None,pt_size=9,color='0',t_range=None,logscale=False, max_ticks=3):
        """
        Set up uncertainty distribution plot

        :param ax: matplotlib axes object
        :param pt_size: character point size
        :param color: colour
        :param t_range: preset axis range
        :return: none
        """
        if not ax:
            ax = plt.subplot(1,1,1)

        linewidth=.5 * pt_size / 9
        t=self.t([.003]+self.gaussian_percentiles()+[.997])
        p=np.searchsorted(self.ts,t)-1

        if logscale:
            if t_range:
                xt0= ([np.log10(t_range[0])]
                    +list(range(np.floor(np.log10(t_range[0])).astype(int)+1,np.ceil(np.log10(t_range[1])).astype(int)))
                    +[np.log10(t_range[1])])  # log tick values (potentially including non-integer limits)
            else:
                t_range=gm.range(t)
                xt0=list(range(np.floor(np.log10(t_range[0])).astype(int),np.ceil(np.log10(t_range[1])).astype(int)+1))

            xt = [10 ** e if e<1 else 4.5 for e in xt0]
            xt_label = [cst.str_age(e, simple=True) for e in xt]
            if xt0[-1]>0:  # pad label if less than decade away
                xt_label[-1] = "      " + xt_label[-1]
            ax.set_xscale('log')
            ax.set_xlim(xt[0], xt[-1], auto=False)
            ax.xaxis.set_minor_formatter(ticker.NullFormatter())

        else:  # linear
            if t_range:
                max_t = t_range[1]
            else:
                max_t = np.max(t)
            xt = gm.ticks(np.array([0.,max_t]), max_ticks)
            max_i=-1

            max_text = cst.str_age(xt[max_i], simple=True)
            a = max_text.split(' ')
            xt_units = float(a[0]) / xt[max_i] * xt
            xt_label = [f'{e:g}' for e in xt_units]
            xt_label[max_i] = "      " + xt_label[max_i] + " " + a[1]  # add unit to last label, e.g. "Ga"
            ax.set_xlim(xt[0], max_t, auto=False)
            ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())


        ax.plot(self.ts, self.pdf, lw=linewidth * 1.5, color=color)
        ax.set_ylim(bottom=0) # eliminates tiny gap between axis and fill area
        ax.fill_between(self.ts[p[1]:p[3]], self.pdf[p[1]:p[3]], 0, color=color, alpha=0.35,
                        edgecolor=None, lw=None)
        ax.fill_between(self.ts[p[2]:p[2] + 1], self.pdf[p[2]:p[2] + 1], edgecolor=color, lw=linewidth, alpha=.5)

        ax.patch.set_facecolor('none') # make region transparent over background graphics
        ax.get_yaxis().set_visible(False)
        for e in ['right','left','top']: ax.spines[e].set_visible(False)
        ax.spines['bottom'].set_linewidth(linewidth)
        ax.spines['bottom'].set_color(color)

        ax.set_xticks(xt)

        ax.tick_params(axis='x', which='both', width=linewidth, length=pt_size * .2, pad=pt_size * .1, color=color)
        ax.tick_params(axis='x', which='minor', length=pt_size * .1)
        ax.set_xticklabels(xt_label,fontsize=pt_size*.6, color=color)#,horizontalalignment='left')

    def offset(self,left):
        """
        Calculate offset for correct spacing of age text from mini-plot peak, in +ve x-direction

        :param left: left-aligned plot?
        :return: offset as fraction of mini-plot width
        """
        t=self.t(.997)
        max_ticks=3
        xt= gm.ticks(np.append(0, t), max_ticks)
        q=np.where(self.pdf > np.max(self.pdf)/2)
        edges=self.ts[[q[0][0],q[0][-1]]]
        norm=edges/np.max(xt)
        offset=(1-norm[1])-.1 if left else -norm[0]+.1
        return offset

    def violin_plot(self,ax,y,w0,pt_size=9,color='0',invert=False):
        """
        Set up uncertainty distribution plot

        :param ax: matplotlib axes object
        :param pt_size: character point size
        :param color: colour
        :return: none
        """
        linewidth=.4 * pt_size / 9
        t=self.t([.0001,.16,.5,.84,.9999])
        p=np.searchsorted(self.ts,t)-1

        w = .9*w0/max(self.pdf)

        ax.fill_between(self.ts[p[0]:p[4]], y + w * self.pdf[p[0]:p[4]], y - w * self.pdf[p[0]:p[4]],
                        color='black' if invert else 'white',
                        edgecolor=color, lw=linewidth * 1.5, zorder=4)

        ax.fill_between(self.ts[p[1]:p[3]], y + w * self.pdf[p[1]:p[3]], y - w * self.pdf[p[1]:p[3]],
                        color=gm.mix_colours(color,'black' if invert else 'white',0.35),
                        edgecolor=color,lw=linewidth, zorder=4)

        ax.fill_between(self.ts[p[2]:p[2] + 1], y + w * self.pdf[p[2]:p[2] + 1], y - w * self.pdf[p[2]:p[2] + 1],
                        edgecolor=color, lw=linewidth, alpha=.5, zorder=4)


    def calculate_sequence_probability(self,pdf2):
        """
        Calculate sequence probability with another Craterpdf object
        
        :param pdf2: another Craterpdf object
        :return: probability that self older than pdf
        """
        # Discretisation of cdf biases result, since calculated for one edge, especially for narrow pdfs.
        # Finding midpoint to fix:
        cdf2=(pdf2.cdf+np.roll(pdf2.cdf, 1))/2.
        P = np.sum(self.dt * self.pdf * cdf2)
        return P

    def calculate_instantaneous_probability_ratio(self, t):
        """
        Calculate probability ratio between pdf median and another time, t

        :param t: other time, t
        :return: probability ratio pr(t)/pr(median) [usually <1. if median close to max]
        """
        v = np.interp([self.t(0.5),t], self.ts, self.pdf)
        r = v[1]/v[0]
        return r

    # def calculate_mean_relative_likelihood(self, t):
    #     """
    #     experimental
    #     want mean relative likelihood over pdf if given median t (area stays same, n now unknown)
    #
    #
    #     :return: probability that self older than pdf
    #     """
    #     #have to create new pdf, since lambda changed...
    #
    #     mrl = np.sum(pdf2**2/median_pdf2*pdf2.dt)
    #
    #     return mrl