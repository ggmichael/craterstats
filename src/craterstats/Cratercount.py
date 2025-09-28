#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
import itertools as it
import re
import sys

import craterstats as cst
import craterstats.gm as gm

class Cratercount:
    '''Reads crater count data; provides onward in various styles and binnings'''

    BINNINGS = ['pseudo-log', '20/decade', '10/decade', 'x2', 'root-2', '4th root-2', 'none'] #allowed binnings

    def __init__(self,filename=None,filename2=None):
        self.filename=filename
        filetype = gm.filename(filename, 'e', max_ext_length=6) if filename else None

        self.filename2 = filename2 # shp allows 2 files
        self.binning=None
        self.binned={}
        self.perimeter=None
        self.buffered=False
        self.prebinned=False
        if filetype:
            self.name = gm.filename(filename, 'n')
            self.n_sigma, self.n_trials = self.read_ra_file()

        bad_filetype = False
        try:
            if filetype == '.stat': self.ReadStatFile()
            elif filetype == '.diam': self.ReadDiamFile()
            # '.binned' disallowed for now
            # requires dedicated code to interact with 'range' specification beyond given bins
            # needs further consideration (e.g. for poisson range), but better not to use data in this format anyway
            #elif filetype=='.binned': self.ReadBinnedFile()
            elif filetype == '.scc': self.ReadSCCfile()
            elif filetype == '.shp': self.ReadSHPfile()
            elif filetype == None: pass #just create empty object
            else: bad_filetype = True
        except SystemExit:
            sys.exit()
        except:
            sys.exit("Unable to read file: "+filename)
        if bad_filetype: sys.exit("Unrecognised crater count file type: " + filename)


    def __str__(self):
        return self.filename

    def read_ra_file(self):
        possible_locations = (self.name + '_ra.txt',gm.filename(self.filename,'p')+self.name+'_ra.txt')
        f = next((loc for loc in possible_locations if gm.file_exists(loc)), None)
        if f:
            c = gm.read_textstructure(f)
            measures = sorted(set(c['n_sigma'].keys()) - {'bin'})
            trials = [c[m]['n_trials'] for m in measures]
            return c['n_sigma'],trials
        else:
            return None, None

# ;****************************************************
# ;             Generate missing details
# ;****************************************************

    def MakeBinGeometricMean(self):
        d_min=self.binned['d_min']
        d_max=np.append(d_min[1:],d_min[-1]*( (d_min[-1]/d_min[-2])))

        self.binned.update({'d_mean':np.sqrt(d_min*d_max),
                            'bin_width':d_max-d_min,
                            'd_max':d_max})

    def MakeBinMin(self):
        d_mean=self.binned['d_mean']
        d_min0=[np.sqrt(a*b) for a,b in zip(d_mean,d_mean[1:])]
        d_min=[d_min0[0]*d_mean[0]/d_mean[1]]+d_min0    #assume first bin in same ratio
        self.binned.update(d_min=d_min)

        width0=[b-a for a,b in zip(d_mean,d_mean[1:])]
        width=width0+[width0[-1]*d_mean[-1]/d_mean[-2]] #assume last bin in same ratio
        self.binned.update(bin_width=width)

    def MakeBinNcum(self):
        self.binned.update(ncum=np.array(list(it.accumulate(reversed(self.binned['n'])))))
        self.binned.update(ncum_event=np.array(list(it.accumulate(reversed(self.binned['n_event'])))))


# ;****************************************************
# ;                    File readers
# ;****************************************************

    def ReadStatFile(self):
        # Valid stat file has either 7 or 11 columns:
        col = ['diam', 'n', 'n_density', 'n_density_err', 'ncum', 'ncum_density', 'ncum_density_err',
               'd_mean', 'n_diff', 'n_diff_err', 'n_event']

        s=gm.read_textfile(self.filename,ignore_blank=True,ignore_hash=True)

        nc = len(s[0].split()) # Number of columns
        t=[e.split() for e in s]

        diam = np.array([float(e[0]) for e in t])  # 'diam' is in the first column
        n = np.array([float(e[1]) for e in t])  # 'n' is in the second column
        ncum = np.array([float(e[4]) for e in t])  # 'ncum' is in the 5th column
        ncum_density = np.array([float(e[5]) for e in t])  # 'ncum_density' is in the 6th column

        self.area = ncum[0] / ncum_density[0]
        self.binned = {
            'd_min': diam,
            'n': n,
            'n_event': n if nc == 7 else np.array([float(e[10]) for e in t]), # 'n_event' is in the 11th column (index 10) if nc == 11
            'ncum': ncum,
            'ncum_event': ncum
        }
        self.prebinned = True
        self.binning = 'pseudo-log'
        self.MakeBinGeometricMean()

    def ReadDiamFile(self):
        s= gm.read_textstructure(self.filename)

        c=s['crater']
        diam=[float(e) for e in c['diameter']]

        if 'reference_area' in c:                           #buffered case
            area=1. #nominal area
            self.buffered=True
            frac=[area/float(e) for e in c['reference_area']]
        else:                                               #normal case
            area=float(s['area'])
            frac=[float(e) for e in c['fraction']] if 'fraction' in c else [1.]*len(diam)

        if (min(frac)<0 or max(frac)>1) and self.buffered==0:
            self.errormsg="Crater list in "+self.filename+" has invalid crater fractions."
        if area==0:
            self.errormsg="Crater list in "+self.filename+" has undefined area."


        diam,frac=zip(*sorted(zip(diam,frac),reverse=True))

        self.area=area
        self.diam=diam
        self.fraction=frac
        self.prebinned=0

    def ReadBinnedFile(self):
        s= gm.read_textstructure(self.filename)
        t=s['table']
        diam=[float(e) for e in t['diameter']]

        q=[i for i,e in sorted(enumerate(diam),key=lambda x:x[1])]     #get sorted indices

        self.area=float(s['area'])

        d_min=[diam[e] for e in q]
        n=[float(t['frequency'][e]) for e in q]
        n_event=[float(t['event_frequency'][e]) for e in q] if 'event_frequency' in t else n
        self.binned={'d_min':np.array(d_min),'n':np.array(n),'n_event':np.array(n_event)}

        self.prebinned=1
        self.MakeBinGeometricMean()
        self.MakeBinNcum()


    def ReadSCCfile(self):
        s = gm.read_textstructure(self.filename)
        c=s['crater']
        diam=[float(e) for e in c['diam']]
        frac=[float(e) for e in c['fraction']] if 'fraction' in c else [1. for e in diam]

        q=[i for i,e in sorted(enumerate(diam),key=lambda x:x[1])]     #get sorted indices

        self.area=float(re.findall(r'\s*[\d\.]*',s['Total_area'])[0])
        if 'Perimeter' in s.keys():
            self.perimeter = float(s['Perimeter'].split()[0])
        if 'Total_perimeter' in s.keys(): #for Thomas Heyer's OpenCraterTool
            self.perimeter = float(re.findall(r'\s*[\d\.]*',s['Total_perimeter'])[0])
        self.diam=[diam[e] for e in q]
        self.fraction=[frac[e] for e in q]
        self.prebinned=0

    def ReadSHPfile(self):
        shp = cst.Spatialcount(self.filename,self.filename2)
        self.diam, self.fraction  = shp.diam, shp.fraction
        self.area, self.perimeter = shp.area, shp.perimeter
        self.prebinned=0
        self.name = shp.name

# ;****************************************************
# ;                 File writers
# ;****************************************************

    def WriteStatFile(self,filename,binning='pseudo-log'):

        if not self.prebinned:
            if self.binning != binning:
                self.apply_binning(binning)

        out=['# Craterstats3 exported stat file',
             '#--------------------------------',
             '#','# Source: '+self.filename,'# Binning: '+self.binning,
             '#','# Total area = '+format(self.area,'0g'),'#',
             '#  D_min       F(D)       N_inc       Error        C(D)       N_cum       Error      D_mean      N_diff       Error     N_event','#',
             '#------------------------------------------------------------------------------------------------------------------------------']

        a=self.area
        b=self.binned

        for i in range(len(b['d_min'])):
            if b['n'][i]>0:
                s=(format(b['d_min'][i],'<7.5g')+
                   format(b['n'][i],'>11.5g')+
                   format(b['n'][i]/a,'>13.3E')+
                   format(b['n'][i]/a/np.sqrt(b['n'][i]),'>12.3E')+
                   format(b['ncum'][i],'>11.5g')+
                   format(b['ncum'][i]/a,'>13.3E')+
                   format(b['ncum'][i]/a/np.sqrt(b['ncum'][i]),'>12.3E')+
                   format(b['d_mean'][i],'>12.4g')+
                   format(b['n'][i]/b['bin_width'][i]/a,'>12.3E')+
                   format(b['n'][i]/b['bin_width'][i]/a/np.sqrt(b['n_event'][i]),'>12.3E')+
                   format(b['n_event'][i],'>12.5g'))
                out+=[s]

        out+=['#------------------------------------------------------------------------------------------------------------------------------']
        gm.write_textfile(filename, out)

# ;****************************************************

    def generate_bins(self,binning,d,offset=0.,expand=True):
        '''
        Generate bin boundaries to cover range of d

        :param binning: binning style string
        :param d: diameter values
        :param offset: fractional offset (set 0.5 to offset by half bin)
        :param expand: create one boundary beyond data (default True)
        :return: bin boundaries
        '''
        r10=np.log10(gm.range(d)) if len(d)>0 else np.array([0.,0.])
        eps=.001 # small vs smallest possible bin factor
        if expand:
            r10[1] += eps
        else:
            r10[0] += eps
            r10[1] -= eps

        if binning == 'none': return d
        if binning == 'pseudo-log':
            a=[1.,1.1,1.2,1.3,1.4,1.5,1.7,2.,2.5,3.,3.5,4.,4.5,5.,6.,7.,8.,9.]
            b=[10**e for e in range(int(np.floor(r10[0])),int(np.ceil(r10[1]+.1)))] # if above .9 make sure get next decade
            bins=np.outer(b,a).flatten()
        else:
            bins_per_decade = {'x2': 1. / np.log10(2.),
                               'root-2': 2./np.log10(2.),
                               '4th root-2': 4./np.log10(2.),
                               '10/decade': 10.,
                               '20/decade': 20.,
                            }[binning]

            br = np.array(gm.range(r10*bins_per_decade + offset, outer=True)) - offset
            b0 = np.arange(br[0],br[1]+1)
            bins = 10 ** (b0 / bins_per_decade)

        q=np.searchsorted(bins,10**r10)
        needed_bins = bins[np.clip(q[0]-1,0,None):q[1]+1]
        return needed_bins


    def apply_binning(self,binning,offset=0.):
        '''
        Create binned version of cratercount (internally, into self.binned structure)

        :param binning: name of binning style
        :param offset: fractional offset (set 0.5 to offset by half bin)
        :return: none
        '''
        if not binning in self.BINNINGS: raise Exception("Invalid binning")

        d=self.diam

        if binning=='none':
            bins,h = zip(*sorted(zip(d, self.fraction)))
            bins, h = np.array(bins), np.array(h)
            bin_centres = bins
            h_event=np.ones(len(h))
            width = np.zeros(len(d))

        else:
            bins=self.generate_bins(binning,d,offset=offset)
            h_event, _ = np.histogram(d, bins=bins)
            self.reverse_indices = np.digitize(d, bins) # needed for randomness analysis
            h,_ = np.histogram(d,weights=self.fraction,bins=bins)

            width=bins[1:]-bins[:-1]
            bin_centres=np.sqrt(bins[1:]*bins[:-1])



        self.binned={'d_min':bins[:-1] if binning!='none' else bins,
                     'd_max':bins[1:] if binning!='none' else bins,
                     'bin_width':width,
                     'd_mean':bin_centres,
                     'n':h,
                     'n_event':h_event,
                     'ncum':np.flip(np.cumsum(np.flip(h))),
                     'ncum_event':np.flip(np.cumsum(np.flip(h_event)))
                     }
        self.binning=binning


    def decode_range(self,range,binning,snap):
        if not self.prebinned:
            if self.binning != binning:
                self.apply_binning(binning)

        r1 = [0.,0.]
        snap1 = [snap,snap]
        q = np.where(self.binned['n'] > 0)
        for i,r in enumerate(range):
            try:
                if isinstance(r, float):
                    r1[i]=r
                elif r[0]=='b':
                    v=int(r[1:])
                    v=np.clip(v,-len(q[0]),len(q[0]))
                    if v>0:
                        v-=1
                    r1[i]=self.binned['d_mean'][q[0][v]]
                    snap1[i]=1
                else:
                    r1[i]=float(r)
            except:
                sys.exit('Range limit error: ' + r)

        if r1[1] < r1[0]: r1[1]=r1[0]

        if self.binning != 'none':
            if snap1[0] and r1[0]>0:
                r1[0] = self.binned['d_min'][np.searchsorted(self.binned['d_min'],r1[0]*(1.0000001))-1]
            if snap1[1] and r1[1] <= self.binned['d_max'][-1]-1e-7:
                r1[1] = self.binned['d_max'][np.searchsorted(self.binned['d_max'],r1[1]*(0.999999))]

        return r1


# ;****************************************************
# ;                    plot output
# ;****************************************************

    def resurf_adj(self,pf,range):
        p0=self.getplotdata("cumulative",self.binning,range=range)
        p=p0.copy()
        n=len(p['d'])
        count=0
        ncum_adj=0.
        if n > 1:
            while True:
                ncum_adj0=ncum_adj
                p['y']=p0['y']+ncum_adj
                a0=pf.fit(p)
                ncum_adj=pf.evaluate("cumulative",p['d'][n-1],a0[0])-p0['y'][n-1]
                count+=1
                if abs(ncum_adj0-ncum_adj) < .0001 or count > 20:
                    break
        return ncum_adj


    def getplotdata(self,presentation,binning,
                    range=None,
                    resurfacing=0,
                    showall=0,
                    pf=None):
        '''
        Return cratercount data in one of several presentation forms suitable for plotting

        :param presentation: data presentation name
        :param binning: binning name
        :param range: diameter range (km)
        :param resurfacing: None|0|1  - no correction|show only range of correction|show all corrected points
        :param pf: production function (for binning bias or resurfacing corrections)
        :return: dictionary of plottable values
        '''

        if not self.prebinned:
            if self.binning != binning:
                self.apply_binning(binning)

        adj = 0 if resurfacing==0 else self.resurf_adj(pf,range)

        q=np.where(self.binned['n']>0)

        if presentation=='cumulative':
            d=self.binned['d_min'][q]
            y=self.binned['ncum'][q]/self.area+adj
            err=y/np.sqrt(self.binned['ncum_event'][q])

        elif presentation=='incremental':
            d=self.binned['d_mean'][q]
            y=self.binned['n'][q]/self.area
            err=y/np.sqrt(self.binned['n_event'][q])

        elif presentation=='Hartmann':
            d=self.binned['d_mean'][q]
            y=self.binned['n'][q]/self.binned['bin_width'][q]/self.area*d*(np.sqrt(2.)-1.)
            err=y/np.sqrt(self.binned['n_event'][q])

        elif presentation=='differential':
            d=self.binned['d_mean'][q]
            y=self.binned['n'][q]/self.binned['bin_width'][q]/self.area
            err=y/np.sqrt(self.binned['n_event'][q])

            #correct for exponential binning bias (Michael, 2013 - Section 5)
            beta=(self.binned['d_mean'][q]/self.binned['d_min'][q])**2  #bin ratio
            if pf:
                k=np.log10(pf.evaluate("cumulative",d*np.sqrt(beta))/pf.evaluate("cumulative",d/np.sqrt(beta)))/np.log10(beta)
            else:
                k=-3. #if exact slope unknown, taking -3 (cumulative) is much better than nothing
            f=cst.bin_bias_correction(beta, k)
            y/=f

        elif presentation=='R-plot':
            d=self.binned['d_mean'][q]
            y=d**3*self.binned['n'][q]/self.binned['bin_width'][q]/self.area
            err=y/np.sqrt(self.binned['n_event'][q])

        if range:
            d_mean_q=self.binned['d_mean'][q]
            q1=np.where(((0 if showall == 1 else range[0]) < d_mean_q)  & (d_mean_q < range[1]))
            d=d[q1]
            y=y[q1]
            err=err[q1]
            q=q[0][q1]  #[0] takes first dim of tuple

            r1=range.copy()
            if resurfacing == 1:
                r1[0]=0 # show all corrected points
            if r1[0] == 0: r1[0]=self.binned['d_min'][0]
            if r1[1] == np.inf: r1[1] = self.binned['d_max'][-1]
            bin_range = tuple(np.array(self.generate_bins(self.binning,r1,expand=False))[[0,-1]])  # extend selection to bin boundaries
        else:
            bin_range = self.binned['d_min'][q[0][0]], self.binned['d_max'][q[0][-1]] # data range


        n=np.sum(self.binned['n'][q])             #no of craters in range
        n_event=np.sum(self.binned['n_event'][q])

        return {'presentation':presentation,'d':d,'y':y,'err':err,'n':n,'n_event':n_event,'bin_range':bin_range}
