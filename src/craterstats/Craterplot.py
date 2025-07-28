#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
from matplotlib.textpath import TextPath
import re

import craterstats as cst
import craterstats.gm as gm


class Craterplot:
    """
    Specify and draw a single overplot: either a crater data series, or an age estimate of one
    """

    def __init__(self,*args,**kwargs):
        self.UpdateSettings({
            'cratercount':None, # if not provided, will create from 'source'
            'source':'',
            'name':'',
            'range':['0','inf'],   #unconstrained
            'snap':1,
            'type':'data',
            'error_bars':1,
            'hide':0,
            'colour':0,
            'psym':0,
            'binning':'pseudo-log',
            'age_left':0,
            'show_age':1,
            'resurf':0,
            'resurf_showall':0,
            'isochron':0,
            'offset_age':[0.,0.],
            },*args,kwargs)

        self.range = self.cratercount.decode_range(self.range,self.binning,self.snap)

    def UpdateSettings(self,*args,**kwargs): #pass either dictionary or keywords
        a = {k: v for d in args for k, v in d.items()}
        a.update(**kwargs)
        for k, v in a.items():
            if k in ('offset_age'):
                v = [float(e) for e in v]
            if k == 'range':
                pass #do nothing
            if k in ('error_bars',
                     'snap',
                     'hide',
                     'age_left',
                     'show_age',
                     'resurf',
                     'resurf_showall',
                     'isochron',
                     'psym',
                     ):
                v = int(v)
            setattr(self, k, v)
        if not self.cratercount and self.source:
            self.cratercount = cst.Cratercount(self.source)
        if not self.source and self.cratercount:
            self.source = self.cratercount.filename
        if not self.name and self.source:
            self.name = re.sub(r'_?CRATER_?', '', gm.filename(self.source,"n"))  # remove if present from shp file


    def calculate_age(self,cps):
        """
        Calculate age

        :param cps: Craterplotset instance
        """
        if self.type in ['poisson','b-poisson']:
            pf_range=cps.pf.range
            r0=np.clip(self.range,pf_range[0],pf_range[1])
            self.pdf=cst.Craterpdf(cps.pf, cps.cf, self.cratercount, r0, bcc=self.type == 'b-poisson')
            self.t = self.pdf.median1sigma()  # median/1-sigma gaussian-equivalent percentiles
            self.a0=cps.cf.a0(self.t)
            self.n=self.pdf.k
            self.n_event=self.n

        else:
            if self.type=='c-fit':
                p0=self.cratercount.getplotdata("cumulative",self.binning, range=self.range,
                    resurfacing=self.resurf_showall if self.resurf and self.type == 'c-fit' else None,
                    pf=cps.pf)
            elif self.type=='d-fit':
                p0=self.cratercount.getplotdata("differential",self.binning,range=self.range,pf=cps.pf)

            self.n=p0['n']    #override with number used in fit (range may be a bit different because of d_min)
            self.n_event=p0['n_event']
            self.a0=cps.pf.fit(p0)
            self.t = [cps.cf.t(a0=e) for e in self.a0]
            self.bin_range=p0['bin_range']

        self.n_d = cps.pf.evaluate("cumulative", cps.ref_diameter, self.a0[0])



    def overplot(self,cps):
        """
        Add overplot elements into figure

        :param cps: Craterplotset instance
        :return: none
        """
        if not self.cratercount or self.hide: return

        if cps.presentation=='sequence':
            self.overplot_sequence_element(cps)
            return

        p = self.cratercount.getplotdata(cps.presentation, self.binning, range=self.range,
            resurfacing=self.resurf_showall if self.resurf and self.type == 'c-fit' else None,
            pf=cps.pf)

        self.n=p['n']
        self.n_event=p['n_event']

        if self.error_bars:
            cps.ax.errorbar(np.log10(p['d']),p['y'],yerr=p['err'],fmt='none',linewidth=.5*cps.sz_ratio,ecolor=cps.grey[0])

        if self.type in ['c-fit','d-fit','poisson','b-poisson']:
            self.calculate_age(cps)

            if self.isochron:
                iso=cps.pf.getisochron(cps.presentation,self.a0[0],cps.ef)
                cps.ax.plot(np.log10(iso['d']), iso['y'], label=None,color=cps.grey[0], lw=.4*cps.sz_ratio, zorder=.9)

            expansion=np.array([.99,1.01])
            fit=cps.pf.getplotdata(cps.presentation,self.a0[0],range=self.range*expansion)
            cps.ax.plot(np.log10(fit['d']), fit['y'], label='fit', color=self.colour, lw=.7*cps.sz_ratio)

            if self.show_age:
                st=cst.str_age(self.t[0], self.t[2] - self.t[0], self.t[0] - self.t[1], cps.sig_figs, mu=cps.mu)
                xy = cps.data_to_axis((np.log10(fit['d'][0]),fit['y'][0]))
                x,y = xy + 0.02*np.ones(2)*(-1 if self.age_left else 1) +np.array(self.offset_age)/(cps.decades[0]*20) #(cps.decades[0]*10).
                cps.ax.text(x,y,st,transform=cps.ax.transAxes,
                            color=self.colour,size=cps.scaled_pt_size*1.2,
                            horizontalalignment='right' if self.age_left else 'left',)

                if self.type in ['poisson','b-poisson']:
                    text_extent = TextPath((0, 0), st, size=cps.scaled_pt_size*1.2).get_extents()
                    h,w=text_extent.height,text_extent.width
                    f = 1 / (cps.cm2inch * (cps.position[2] - cps.position[0]) * 100) #conversion for axes coord
                    offset = self.pdf.offset(self.age_left)          # normalised units of mini-plot width in +x direction
                    box = np.array([.12, .05])*cps.sz_ratio          # dimensions of plot box

                    if self.age_left:  # offset from string write position
                        dx = -(f * w + .03) + (-1 + offset) * box[0]
                    else:
                        dx = f * w + .03 + offset * box[0]
                    dy = f * h / 2

                    pos = np.array([x+dx, y-dy, x+dx + box[0], y-dy + box[1]])
                    pos2=cps.axis_to_fig(pos)
                    pos3=np.concatenate([pos2[0:2],pos2[2:4]-pos2[0:2]])
                    ax = cps.fig.add_axes(pos3)
                    self.pdf.plot(ax,pt_size=cps.scaled_pt_size,color=self.colour,logscale=False)

        legend_label=self.make_legend_label(cps)
        cps.ax.plot(np.log10(p['d']),p['y'],label=', '.join(legend_label) if legend_label else None,
                    **cps.marker_def[self.psym],ls='',color=self.colour)



    def make_legend_label(self,cps):
        legend_label = []

        if self.type in ['c-fit', 'd-fit', 'poisson', 'b-poisson']:
            if 'c' in cps.legend:
                if self.cratercount.buffered:
                    legend_label += [f'{self.n_event:.1f}']
                else:
                    if np.abs(self.n_event - self.n) < .001:
                        legend_label += [f'{self.n:0g}']
                    else:
                        legend_label += [f'{self.n:.1f} (of {self.n_event:d})']
                legend_label[-1] += " craters"
            if 'r' in cps.legend:
                if not self.cratercount.prebinned and self.type in ['poisson','b-poisson']:
                    r=self.range
                else:
                    r=gm.range(self.cratercount.generate_bins(self.binning,self.range,expand=False))
                legend_label += [gm.diameter_range(r)]
            if 'N' in cps.legend:
                legend_label += [f'N({cps.ref_diameter:0g})' +'=' + gm.scientific_notation(10**self.a0[0],10**self.a0[2],10**self.a0[1], unit='km-2')]
            if cps.presentation == 'sequence':
                if 'a' in cps.legend:
                    legend_label+=[gm.scientific_notation(self.cratercount.area, sf=3, unit='km2')]
                if 'A' in cps.legend:
                    legend_label+=[(cst.str_age(self.t[0], self.t[2] - self.t[0], self.t[0] - self.t[1], cps.sig_figs,
                                            mu=cps.mu, no_error=False))]

        if self.type=='data':
            if 'n' in cps.legend:
                legend_label+=[self.name if self.name!='' else gm.filename(self.source, "n")]
            if 'a' in cps.legend:
                legend_label+=[gm.scientific_notation(self.cratercount.area, sf=3, unit='km2')]
            if 'p' in cps.legend:
                if self.cratercount.perimeter:
                    legend_label += [gm.scientific_notation(self.cratercount.perimeter, sf=3) + ' km']

        return legend_label


    def get_data_range(self,cps):
        """
        Return data range of Craterplot

        :param cps: Craterplotset instance
        :return: (d_min,d_max,y_min,y_max)
        """
        p = self.cratercount.getplotdata(cps.presentation, self.binning, range=self.range,
             resurfacing=self.resurf_showall if self.resurf and self.type == 'c-fit' else None,
             pf=cps.pf)
        return gm.range(p['d']) + gm.range(p['y'])




    def overplot_sequence_element(self,cps):
        """
        Add overplot sequence elements into figure

        :param cps: Craterplotset instance
        :return: none
        """

        p = self.cratercount.getplotdata('differential', self.binning, range=self.range,
            resurfacing=None, pf=cps.pf)

        self.n=p['n']
        self.n_event=p['n_event']

        if self.type in ['c-fit','d-fit','poisson','b-poisson']:

            self.calculate_age(cps)

            seq=[e for e in cps.craterplot if e.type != 'data' and not e.hide]
            n=len(seq)
            i=[i for i,e in enumerate(seq) if e is self][0]
            dy = (n - i) / (n+1)
            w0 = 0.5/(n+1)
            w = 0.3 * w0

            lw = cps.scaled_pt_size / 16.

            for j in [0, 1] if cps.crossover else [0]:

                if self.type in ['poisson','b-poisson']:
                    self.pdf.violin_plot(cps.ax2[j],dy,w0,pt_size=cps.scaled_pt_size,color=self.colour,invert=cps.invert)

                if self.type in ['d-fit','c-fit']:
                    cps.ax2[j].fill_between([self.t[1], self.t[2]], [dy + w, dy + w], [dy - w, dy - w],
                                            color=gm.mix_colours(self.colour,'black' if cps.invert else 'white',0.35),
                                            edgecolor=self.colour,lw=lw,zorder=4)

                    cps.ax2[j].plot([self.t[0], self.t[0]],
                                    [dy + w, dy - w], color=self.colour, alpha=0.5, lw=lw*.7,zorder=4)

            text = '\n'.join(gm.strip_quotes(self.name).split(r'\n')) #clear quotes and substitute real linebreaks
            cps.ax.text(-.007, dy, text, fontsize=cps.scaled_pt_size * .75, ha='right', va='center')

            lbl = self.make_legend_label(cps)
            if lbl: cps.ax.text(1.007, dy, '\n'.join(lbl), fontsize=cps.scaled_pt_size * .75, ha='left', va='center')














