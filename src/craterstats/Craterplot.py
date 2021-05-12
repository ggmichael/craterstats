#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
from matplotlib.textpath import TextPath

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
            'range':np.array([0.,np.inf]),   #unconstrained
            'type':'data',
            'error_bars':1,
            'hide':0,
            'colour':0,
            'psym':0,
            'binning':'pseudo-log',
            'age_left':0,
            'display_age':1,
            'resurf':0,
            'resurf_showall':0,
            'isochron':0,
            'offset_age':[0.,0.],
            },*args,kwargs)

    def UpdateSettings(self,*args,**kwargs): #pass either dictionary or keywords
        a = {k: v for d in args for k, v in d.items()}
        a.update(**kwargs)
        for k, v in a.items():
            if k in ('range', 'offset_age'): v = [float(e) for e in v]
            if k in ('error_bars',
                     'hide',
                     'age_left',
                     'display_age',
                     'resurf',
                     'resurf_showall',
                     'isochron',
                     'colour',
                     'psym',
                     ):
                v = int(v)
            setattr(self, k, v)
        if not self.cratercount and self.source:
            self.cratercount = cst.Cratercount(self.source)
        if not self.source and self.cratercount:
            self.source = self.cratercount.filename


    def calculate_age(self,cps):
        """
        Calculate age

        :param cps: Craterplotset instance
        """
        if self.type=='poisson':
            pf_range=cps.pf.range
            r0=np.clip(self.range,pf_range[0],pf_range[1])

            self.pdf=cst.Craterpdf(cps.pf, cps.cf, self.cratercount, r0)
            self.t=self.pdf.t([.50,.16,.84]) #median/1-sigma gaussian-equivalent percentiles
            self.a0=cps.cf.a0(self.t)
            self.n=self.pdf.k
            self.n_event=self.n

        elif self.type=='b-poisson': # implement after publication
            pf_range=cps.pf.range()
            r0=np.clip(self.range,pf_range[0],pf_range[1])

            # cpdf=obj_new("craterpdf",cps.pf,cps.cf,self.cratercount,r0,/buffer)
            # if ~obj_valid(cpdf) then return

            # self.t=cpdf->t([.50,.16,.84]) ;1-sigma intervals/median
            # self.a0=cps.cf->a0(self.t)

            # self.n=cpdf->k()
            # self.n_event=self.n

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

        p = self.cratercount.getplotdata(cps.presentation, self.binning, range=self.range,
             resurfacing=self.resurf_showall if self.resurf and self.type == 'c-fit' else None,
             pf=cps.pf)

        self.n=p['n']
        self.n_event=p['n_event']
        legend_label = []

        if self.error_bars:
            cps.ax.errorbar(np.log10(p['d']),p['y'],yerr=p['err'],fmt='none',linewidth=.7,ecolor=cps.grey[0])

        if self.type in ['c-fit','d-fit','poisson','b-poisson']:
            self.calculate_age(cps)

            if self.isochron:
                iso=cps.pf.getisochron(cps.presentation,self.a0[0],cps.ef)
                cps.ax.plot(np.log10(iso['d']), iso['y'], label=None,color=cps.grey[0], lw=.4, zorder=.9)

            expansion=np.array([.99,1.01])
            fit=cps.pf.getplotdata(cps.presentation,self.a0[0],range=self.range*expansion)
            cps.ax.plot(np.log10(fit['d']), fit['y'], label='fit', color=cps.palette[self.colour], lw=.7)

            if self.display_age:
                st=cst.str_age(self.t[0], self.t[2] - self.t[0], self.t[0] - self.t[1], cps.sig_figs, mu=cps.mu)
                xy = cps.data_to_axis((np.log10(fit['d'][0]),fit['y'][0]))
                x,y = xy + 0.02*np.ones(2)*(-1 if self.age_left else 1) +np.array(self.offset_age)/(cps.decades[0]*20) #(cps.decades[0]*10).
                cps.ax.text(x,y,st,transform=cps.ax.transAxes,
                            color=cps.palette[self.colour],size=cps.scaled_pt_size*1.2,
                            horizontalalignment='right' if self.age_left else 'left',)

                if self.type in ['poisson','b-poisson']:
                    text_extent = TextPath((0, 0), st, size=cps.scaled_pt_size*1.2).get_extents()
                    h,w=text_extent.height,text_extent.width
                    f = 1 / (cps.cm2inch * (cps.position[2] - cps.position[0]) * 100) #conversion for axes coord
                    offset = self.pdf.offset(self.age_left)          # normalised units of mini-plot width in +x direction
                    box = np.array([.12, .05])*cps.pt_size/9.        # dimensions of plot box

                    if self.age_left:  # offset from string write position
                        dx = -(f * w + .03) + (-1 + offset) * box[0]
                    else:
                        dx = f * w + .03 + offset * box[0]
                    dy = f * h / 2

                    pos = np.array([x+dx, y-dy, x+dx + box[0], y-dy + box[1]])
                    pos2=cps.axis_to_fig(pos)
                    pos3=np.concatenate([pos2[0:2],pos2[2:4]-pos2[0:2]])
                    ax = cps.fig.add_axes(pos3)
                    self.pdf.plot(ax,pt_size=cps.scaled_pt_size,color=cps.palette[self.colour])

            if '#' in cps.legend:
                if self.cratercount.buffered:
                    legend_label += ['{:.1f}'.format(self.n_event)]
                else:
                    if np.abs(self.n_event - self.n) < .001:
                        legend_label += ['{:0g}'.format(self.n)]
                    else:
                        legend_label += ['{0:.1f} (of {1:d})'.format(self.n,self.n_event)]
                legend_label[-1] += " craters"
            if 'r' in cps.legend:
                legend_label += [cst.str_diameter_range(self.cratercount.generate_bins(self.binning,self.range,expand=False))]
            if 'N' in cps.legend:
                legend_label += ['N({0:0g})'.format(cps.ref_diameter) +'$=' + gm.scientific_notation(self.n_d, sf=3) + '$ km$^{-2}$']


        if self.type=='data':
            if 'n' in cps.legend:
                legend_label+=[self.name if self.name!='' else gm.filename(self.source, "n")]
            if 'a' in cps.legend:
                legend_label+=['$' + gm.scientific_notation(self.cratercount.area, sf=3) + '$ km$^{2}$']

        cps.ax.plot(np.log10(p['d']),p['y'],label=', '.join(legend_label) if legend_label else None,
                    **cps.marker_def[self.psym],ls='',color=cps.palette[self.colour],markeredgewidth=.5)



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
















