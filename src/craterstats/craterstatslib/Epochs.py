#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
import re

import gm
import craterstatslib as cst


class Epochs:

    def __init__(self, source,identifier,pf,cf):

        if type(source) is dict:
            src = source
        else:
            if type(source) is list:
                txt = '\n'.join([gm.read_textfile(e, as_string=True) for e in source])
            elif type(source) is str:
                txt= gm.read_textfile(source, as_string=True, ignore_hash=True)
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
        label_slant=int(self.formatting[0])
        colour = [int(re.search('\d?', e)[0]) for e in self.formatting[1:]]
        offset = ['r' in e for e in self.formatting[1:]]
        boundary = ['b' in e for e in self.formatting[1:]]
        return label_slant,colour,offset,boundary

    def chronology_oplot(self,cps,phi=False):
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
                        size=cps.pt_size * .7, rotation=label_slant,
                        rotation_mode='anchor', verticalalignment='center', horizontalalignment='left',
                        bbox=dict(facecolor='none', edgecolor='none', pad=50))

        y = self.cf.phi(self.time[1])*.7 if phi else self.cf.N1(self.time[1])/2.5
        for i,t in enumerate(self.time): # write epoch times
            if t!=0:
                cps.ax.annotate(' {:0.3g} '.format(t),xy=(t, y),
                            xytext=(cps.pt_size * .04, 0), textcoords="offset points",
                            size=cps.pt_size * .7, rotation=90,
                            verticalalignment='bottom' if offset[i] else 'top',
                            horizontalalignment='center',
                            bbox=dict(facecolor='none', edgecolor='none', pad=50))


    def oplot(self,cps):
        a0=[self.cf.a0(t) for t in self.time[1:]]
        iso = [self.pf.getisochron(cps.presentation,e,cps.ef) for e in a0]
        _, colour, _, boundary = self.decode_formatting()

        for i,(a,b) in enumerate(zip(iso,iso[1:])):
            x=np.concatenate((a['d'], b['d'][::-1]))
            y = np.concatenate((a['y'], b['y'][::-1]))
            cps.ax.fill(np.log10(x),y, color=cps.grey[3 - colour[i + 1]], edgecolor=None, lw=0)

            if boundary[i]:
                cps.ax.plot(np.log10(a['d']),a['y'], color=cps.grey[0], lw=.3)



if __name__ == '__main__':
    f="config/functions.txt"
    cf = cst.Chronologyfn(f, 'Moon, Neukum (1983)')
    pf = cst.Productionfn(f, 'Moon, Neukum (1983)')
    ep=Epochs(f,'Moon, Wilhelms (1987)',pf,cf)
















