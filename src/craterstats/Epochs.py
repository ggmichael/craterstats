#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
import re

import craterstats as cst
import craterstats.gm as gm


class Epochs:
    """
    Decode Epoch definitions, calculate derived values, and provide overplot routines

    """

    def __init__(self, source,identifier,pf,cf):

        if type(source) is dict:
            src = source
        else:
            if '\n' in source: # multiline string is definition
                txt = source + '\nepochs={\n name="null"\n}' # add null entry to force implied array
            else: # single line string is filename
                txt = gm.read_textfile(source, as_string=True, ignore_hash=True)
            src = gm.read_textstructure(txt, from_string=True)

        definition = next((e for e in src['epochs'] if e['name'] == identifier), None)
        if definition is None:
            raise ValueError('Epoch system not found: ' + identifier)

        self.name = definition['name']
        self.epoch = definition['epoch']
        self.formatting = definition['formatting']
        self.ref_diameter = [int(e) for e in definition['ref_diameter']] if 'ref_diameter' in definition else None
        self.density = [float(e) for e in definition['density']] if 'density' in definition else None
        self.time = [float(e) for e in definition['time']] if 'time' in definition else None
        self.reference = definition['reference']
        self.pf=pf
        self.cf=cf

        if self.time is None:
            a0=[pf.fit({'presentation':'cumulative','d':d,'y':ncum/1e6,'err':0})[0] for d,ncum in zip(self.ref_diameter,self.density)]
            self.time=[0.]+list(cf.t(a0=np.array(a0)))

    def __str__(self):
        return self.name

    def decode_formatting(self):
        """
        Decode epoch definition

        """
        label_slant=int(self.formatting[0])
        colour = [int(re.search(r'\d?', e)[0]) for e in self.formatting[1:]]
        offset = ['r' in e for e in self.formatting[1:]]
        boundary = ['b' in e for e in self.formatting[1:]]
        return label_slant,colour,offset,boundary

    def chronology_oplot(self,cps,phi=False):
        """
        Overplot epoch system on chronology/rate plot

        :param cps: Craterplotset instance
        :param phi: rate function?
        :return: none
        """
        p_t,p_y=self.cf.getplotdata(phi=phi,linear=True)
        label_slant, colour, offset, boundary = self.decode_formatting()

        for i,(t0,t1) in enumerate(zip(self.time[1:],self.time[2:])):  # fill epoch regions
            t=np.linspace(t0,t1,100)
            y=np.interp(t,p_t,p_y)
            cps.ax.fill_between(t,y,y*1e-11, color=cps.grey[3-colour[i+1]], edgecolor=None, lw=0)

        for i, t in enumerate(self.time[1:]):  # add dividing lines
            y = np.interp(t, p_t, p_y)
            cps.ax.plot([t,t], [y, y * 1e-11], color=cps.grey[0] ,lw=.4 if boundary[i] else .3 ,
                        alpha=1 if boundary[i] else .3)

        t0 = list(self.time) + [cps.xrange[0]]
        for i,e in enumerate(self.epoch): # write epoch names
            t=(t0[i]+t0[i+1])/2
            y = self.cf.phi(t) if phi else self.cf.N1(t)
            cps.ax.text(t-.03, y*1.5, e,
                        size=cps.pt_size * .6, rotation=label_slant,
                        rotation_mode='anchor', verticalalignment='center', horizontalalignment='left',
                        bbox=dict(facecolor='none', edgecolor='none', pad=50))

        y = self.cf.phi(self.time[1])*.7 if phi else self.cf.N1(self.time[1])/2.5
        for i,t in enumerate(self.time): # write epoch times
            if t!=0:
                cps.ax.annotate(f' {t:0.3g} ',xy=(t, y),
                            xytext=(cps.pt_size * .04, 0), textcoords="offset points",
                            size=cps.pt_size * .6, rotation=90,
                            verticalalignment='bottom' if offset[i] else 'top',
                            horizontalalignment='center',
                            bbox=dict(facecolor='none', edgecolor='none', pad=50))


    def sequence_oplot(self,cps):
        """
        Overplot epoch system on a sequence plot

        :param cps: Craterplotset instance
        :return: none
        """

        label_slant, colour, offset, boundary = self.decode_formatting()

        for j in [0, 1] if cps.crossover else [0]:

            for i,(t0,t1) in enumerate(zip(self.time[1:],self.time[2:])):  # fill epoch regions
                cps.ax2[j].fill_between([t0,t1],[0,0],[1,1], color=cps.grey[3-colour[i+1]], edgecolor=None, lw=0)

            for i, t in enumerate(self.time[1:]):  # add dividing lines
                cps.ax2[j].plot([t,t], [0,1], color=gm.mix_colours(cps.grey[0], 'black' if cps.invert else 'white' ,1 if boundary[i] else .3),
                                lw=.4 if boundary[i] else .3)

            t0 = sorted(self.time + [cps.t_min,cps.t_max])[1:] #lower limit substitutes correct place in seq

            for i,e in enumerate(self.epoch): # write epoch names
                lbl=[a[0] for a in re.split(' |-',e)]
                lbl=lbl[0].lower()+lbl[1] if len(lbl)==2 else lbl[0]
                if j==0:
                    t = (t0[i] + t0[i + 1]) / 2
                else:
                    t = np.sqrt(t0[i] * t0[i + 1])
                cps.ax2[j].text(t, .01, lbl, horizontalalignment='center',
                                size=cps.scaled_pt_size * .55, clip_on=True)



    def oplot(self,cps):
        """
        Overplot epoch system on crater count plot

        :param cps: Craterplotset instance
        :return: none
        """
        a0=[self.cf.a0(t) for t in self.time[1:]]
        iso = [self.pf.getisochron(cps.presentation,e,cps.ef) for e in a0]
        _, colour, _, boundary = self.decode_formatting()

        for i,(a,b) in enumerate(zip(iso,iso[1:])):
            x=np.concatenate((a['d'], b['d'][::-1]))
            y = np.concatenate((a['y'], b['y'][::-1]))
            cps.ax.fill(np.log10(x),y, color=cps.grey[3 - colour[i + 1]], edgecolor=None, lw=0)

            if boundary[i]:
                cps.ax.plot(np.log10(a['d']),a['y'], color=cps.grey[0], lw=.3)


















