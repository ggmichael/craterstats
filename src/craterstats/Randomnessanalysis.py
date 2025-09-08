#  Copyright (c) 2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import math
import os
import re

import astropy_healpix as hpx
import astropy.units as u
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import spherely as sph
from progressbar import ProgressBar
import pyproj as prj

import craterstats as cst
import craterstats.gm as gm


class Randomnessanalysis(cst.Spatialcount):
    '''Applies randomness tests to Spatialcount'''

    def __init__(self,trials,measure,filename=None,area_file=None):
        super().__init__(filename,area_file)
        self.init_Cratercount()
        self.trials=trials
        self.measure=measure
        self.max_threads = os.cpu_count()-1

    def init_Cratercount(self):
        self.cc = cst.Cratercount()
        self.cc.diam = self.diam
        self.cc.lon = self.lon
        self.cc.lat = self.lat
        self.cc.fraction = self.fraction
        self.cc.prebinned = 0

    def establish_hpx(self,n):
        """
        establish HEALpix grid for 2d binning
        """
        area_globe = 4 * math.pi * self.planetary_radius**2
        desired_nbins = n/10
        desired_bin_area = self.area / desired_nbins
        desired_n_hpx = area_globe / desired_bin_area
        nside = 2**round(np.log2(math.sqrt(desired_n_hpx/12)))
        self.hp = hpx.HEALPix(nside=nside, order='nested')

    def self_pp(self):
        """
        tuple of vars for parallel processing
        """
        return self_pp_tuple(**{key: getattr(self, key) for key in attrs_pp})

    def oplot_neighbours(self,cps,craters,neighbours,ax=None):
        """
        Overplot neighbours
        """
        if not ax:
            ax=cps.ax
        sz_ratio = ax.get_position().width/cps.ax.get_position().width
        for lon,lat,nb in zip(craters.lon,craters.lat,neighbours):
            x0, y0 = self.ortho_proj(lon, lat)
            x1, y1 = self.ortho_proj(sph.get_x(nb), sph.get_y(nb))
            ax.plot((x0,x1),(y0,y1), color='black', linewidth=0.5*cps.sz_ratio*sz_ratio)

    def get_bin_craters(self,bin,Craterlist=False):
        # from real config
        bin_keys = [f"{e:.3g}" for e in np.log2(self.cc.binned['d_min'])]
        if Craterlist:
            xydf = [(x, y, d, f) for x, y, d, f, i in zip(self.lon, self.lat, self.diam, self. fraction, self.cc.reverse_indices)
                    if bin_keys[i - 1] == bin]
            craters = cst.Spatialcount.Craterlist(lon=[x for x, _, _, _ in xydf],
                                 lat=[y for _, y, _, _ in xydf],
                                 diam=[d for _, _, d, _ in xydf],
                                 fraction=[f for _, _, _, f in xydf])
            return craters
        else:
            xy = [(e, f) for e, f, i in zip(self.lon, self.lat, self.cc.reverse_indices) if bin_keys[i - 1] == bin]
            pts, ids = zip(*[(sph.create_point(longitude=x, latitude=y), self.hp.lonlat_to_healpix(x * u.deg, y * u.deg)) for x, y in xy])
            hpd = {}
            for pt, id in zip(pts, ids):
                if id not in hpd:
                    hpd[id] = [pt]
                else:
                    hpd[id].append(pt)
            return pts,ids,hpd

    def montecarlo_split(self,staggered=False):
        """
        Prepare separate runs across bin range
        """
        binning='root-2'
        self.cc.apply_binning(binning, offset=0.)
        match self.measure:
            case 'sdaa': min_count = 3
            case 'm2cnd': min_count = 3

        self_pp = self.self_pp()
        self.results = {}
        bin_result = namedtuple('bin_result',['m0','p2','m','mn','sd','n_sigma'])

        for b,n in zip(self.cc.binned['d_min'],self.cc.binned['n_event']):
            if n >= min_count:
                bin = f"{np.log2(b):.3g}"
                print(f"Bin: {bin} d_min:{b:0.3g} number:{n}")

                pts, ids, hpd = self.get_bin_craters(bin)
                m0,p2 = evaluate_randomness(self_pp,pts, ids, hpd)
                print(f"Actual value of measure: {m0:0.3g}")

                # do monte carlo for random configs
                m = montecarlo_pp(self_pp,b,n)

                mn,sd = (np.mean(m),np.std(m))
                n_sigma = (m0-mn)/sd

                self.results[bin] = bin_result(m0=m0, p2=p2, m=m,mn=mn,sd=sd,n_sigma=n_sigma)
                if b> .15: break


    def plot_histogram(self,cps,bin,ax0=None,sz_ratio=1): # mark median and 1 sd band
        if ax0:
            ax=ax0
        else:
            cps.create_map_plotspace()
            ax = cps.ax

        res = self.results[bin]
        m0,m=(res.m0,res.m)

        nbins = round(math.sqrt(self.trials) + 5)

        h,be = np.histogram(m, bins=nbins)
        bar_width = np.diff(be)
        xr = [min(list(be)+[m0])-bar_width[0],max(list(be)+[m0])+bar_width[0]]
        if not ax0:
            xr[0] -= .6*gm.mag(xr)
        yr = [0,max(h)*(1.1 if ax0 else 1.5)]

        ax.bar(be[:-1], h, width=bar_width, color = cps.grey[3], edgecolor=None, linewidth=0.5,align='edge')

        h = list(h)
        x0,y0 = zip(*[(e,f[i]) for e,f in zip(be,zip([0]+h,h+[0])) for i in [0,1]])
        ax.plot(x0, y0, color='black', linewidth=.7 * sz_ratio)

        ax.plot([m0]*2, yr, color=cps.palette[0],alpha = 0.4, lw = 2 * cps.sz_ratio * sz_ratio)
        ax.text(m0, yr[0]+1*gm.mag(yr), f"{m0:0.3g} ", size=.7*cps.scaled_pt_size * math.sqrt(sz_ratio), rotation=0,
                                 horizontalalignment='center', verticalalignment='bottom')

        # shade sd
        sdr = [res.mn-res.sd,res.mn+res.sd]
        x1,y1 = zip(*[(e,f) for e,f in zip(x0,y0) if sdr[0]<e<sdr[1]])
        x1 = [sdr[0]]*2+list(x1)+[sdr[1]]*2
        y1 = [0,y1[0]]+list(y1)+[y1[-1],0]
        ax.fill_between(x1, y1, color=cps.grey[1], lw=.5 * cps.sz_ratio * sz_ratio)

        # plot mean
        ax.plot([res.mn] * 2, [0,np.interp(res.mn, x1, y1)], color=cps.palette[0], alpha=0.4, lw=1 * cps.sz_ratio * sz_ratio)

        ax.set_xlim(xr[0], xr[1])
        ax.set_ylim(yr[0], yr[1])

        xtickv = [e for e in gm.ticks(xr, 5) if xr[0] < e < xr[1]]
        xt_label = [f'{e:g}' for e in xtickv]
        xt_label[-1] = "  "*len(xt_label[-1])+xt_label[-1]+" km"
        ax.set_xticks(xtickv)
        ax.tick_params(axis='x', which='both', width=.5*sz_ratio, length=cps.pt_size * .2, pad=cps.pt_size * .1)
        ax.tick_params(axis='x', which='minor', length=cps.pt_size * .1)
        ax.set_xticklabels(xt_label,fontsize=.7*cps.scaled_pt_size * math.sqrt(sz_ratio), color=cps.palette[0])

        ax.patch.set_facecolor('none')

        if ax0:
            ax.spines['left'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.set_yticks([])
        else:
            ax.set_ylabel('Frequency')

        cps.fig.savefig(r"D:\mydocs\tmp\ra_plot_histogram.png", dpi=500)

    def plot_map_and_histogram(self, cps, bin, ax=None,sz_ratio=1):
        if not ax:
            ax=cps.ax
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.set_facecolor('none')

        mf = 1.
        hf = .3
        offset = (0,35)
        pos = ax.get_position()
        dx,dy = ( (1-hf) * pos.width * offset[0]/100, pos.height * (1- hf*.5) * offset[1]/100 )
        ax1 = cps.fig.add_axes([pos.x0, pos.y0 + (1-mf) * pos.height, pos.width * mf, pos.height * mf])
        ax2 = cps.fig.add_axes([pos.x0 + (1-hf) * pos.width - dx, pos.y0 +dy, pos.width * hf - dx, pos.height * hf *.5])

        craters = self.get_bin_craters(bin, Craterlist=True)
        self.plot(cps, craters=craters, ax=ax1)
        self.oplot_neighbours(cps,craters,self.results[bin].p2,ax=ax1)
        self.plot_histogram(cps, bin, ax0=ax2,sz_ratio=sz_ratio)

        d_min = 2**float(bin)
        ax.text(1, .9, gm.diameter_range([d_min,d_min*math.sqrt(2)],2), size=.7 * cps.scaled_pt_size * math.sqrt(sz_ratio),
                 transform=ax.transAxes, ha="right")

        cps.fig.savefig(r"D:\mydocs\tmp\m_and_h.png", dpi=500)


    def plot_montecarlo_split(self,cps): # multiplot?
        dim = math.ceil(math.sqrt(len(self.results)+1))
        cps.create_map_plotspace()
        pos = cps.ax.get_position()
        cps.ax.set_visible(False)
        cps.ax.set_axis_off()
        def make_ax(i):
            x,y = (i%dim,dim - 1 - i//dim)
            axi = cps.fig.add_axes([
                pos.x0 + x * (pos.width / dim),
                pos.y0 + y * (pos.height / dim),  # pos.y0 + (n - 1 - i) * (pos.height / n),
                pos.width / dim,
                pos.height / dim
            ])
            return axi

        for i,bin in enumerate(self.results):
            self.plot_map_and_histogram(cps,bin ,ax=make_ax(i),sz_ratio=1/dim)

        self.plot_n_sigma(cps,ax0=make_ax(i+1))

        cps.fig.savefig(r"D:\mydocs\tmp\ra_hist_nxn.png", dpi=500)

    def plot_n_sigma(self,cps,ax0=None):
        if not ax0:
            ax0=cps.ax
        ax0.set_visible(False)
        pos = ax0.get_position()
        sz_ratio = pos.width / cps.ax.get_position().width
        if ax0:
            ax = cps.fig.add_axes([pos.x0+.15*pos.width,pos.y0 + pos.height / 3,pos.width*.85,pos.height/3])
        else:
            ax = cps.fig.add_axes([pos.x0, pos.y0 + pos.height / 3, pos.width, pos.height / 3])

        xr=[-2,2]
        yr=[e * math.sqrt(12) for e in [-1,1]]
        ytick = [-10,-5,-3,-2,-1,0,1,2,3,5,10]
        ytickv = np.sqrt(np.abs(ytick))*np.sign(ytick)
        yticklabels = [f"{e}" for e in ytick]

        xtickv, xticklabels, xminor = cst.Hartmann_bins(xr)
        plt.rcParams.update({'xtick.labelsize': 1. *cps.scaled_pt_size})
        ax.set_xticks(xtickv)
        ax.set_xticklabels(xticklabels)
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(xminor))

        ax.set_yticks(ytickv)
        ax.set_yticklabels(yticklabels)
        ax.tick_params(axis='y', direction='in',labelsize=0.4*cps.scaled_pt_size*math.sqrt(sz_ratio), width=.5*sz_ratio, length=cps.pt_size * .2, pad=cps.pt_size * .1)
        ax.tick_params(axis='x', which='both', direction='in', labelsize=0.5*cps.scaled_pt_size*math.sqrt(sz_ratio),
                       width=.5*sz_ratio, length=cps.pt_size * .2, pad=cps.pt_size * .2)
        ax.tick_params(axis='x', which='minor', length=cps.pt_size * .1)
        ax.set_ylim(yr[0], yr[1])
        ax.set_xlim(xr[0], xr[1])
        ax.set_ylabel(r"$n_\sigma$",fontsize=1.*cps.scaled_pt_size*(sz_ratio), labelpad=.001*cps.pt_size*sz_ratio,fontstyle='italic')
        ax.set_xlabel("Diameter",fontsize=1.*cps.scaled_pt_size*(sz_ratio))
        for spine in ax.spines.values(): spine.set_linewidth(.3*sz_ratio)

        ax.text(.5, .13, "clustered", color=cps.grey[0], size=.7 * cps.scaled_pt_size * math.sqrt(sz_ratio), transform=ax.transAxes, va = 'center', ha = 'center')
        ax.text(.5, .87, "separated", color=cps.grey[0], size=.7 * cps.scaled_pt_size * math.sqrt(sz_ratio), transform=ax.transAxes, va = 'center', ha = 'center')
        #ax.text(.5, .5, "mean random", color=cps.grey[4], size=.7 * cps.scaled_pt_size * math.sqrt(sz_ratio),
        #        transform=ax.transAxes, va='center', ha='center')


        ax.fill_between(xr,[ytickv[2]]*2, y2 = [ytickv[8]]*2, color=cps.grey[2])
        ax.fill_between(xr, [ytickv[3]]*2, y2 = [ytickv[7]]*2, color=cps.grey[3])
        ax.fill_between(xr, [ytickv[4]]*2, y2 = [ytickv[6]]*2, color=cps.grey[1])

        x = [np.log10(2**float(r)) for r in self.results]
        y0 = [(self.results[r].m0 - self.results[r].mn)/self.results[r].sd for r in self.results]
        y = [np.sqrt(abs(e))*np.sign(e) for e in y0] # apply axis scaling
        marker = cps.marker_def[10].copy()
        marker['markersize'] *= cps.sz_ratio*sz_ratio
        ax.plot(x,y,linestyle='-',**marker,color=cps.palette[0],linewidth=.75*sz_ratio)

        cps.fig.savefig(r"D:\mydocs\tmp\ra_nsigma.png", dpi=500)

    def write(self,filename):
        results_table = [f"{bin:<12}\t{self.results[bin].n_sigma:9.4g}" for bin in self.results]
        trials_table = ["\t".join([f"{t:<12}"] + [f"{self.results[bin].m[t]:<12.7g}" for bin in self.results])
                        for t in range(self.trials) ]
        s = (['# Randomness analysis',
              f'version = {cst.__version__}',
              '#',
              f'source = {gm.filename(self.filename,'ne')}',
              f'trials = {self.trials}',
              f'measure = {self.measure}',
              'results={bin, n_sigma']
             + results_table +
             ['}',
              'table = {trial, '+", ".join([f"b{i}" for i,_ in enumerate(self.results)])]
             + trials_table +
             ['}'])
        gm.write_textfile(filename,s)

    def read(self,filename,on_match=False):
        c = gm.read_textstructure(filename)
        # need to test for combinations of trials/measure: on_match

        self.trials = int(c["trials"])
        self.measure = c["measure"]
        res = c["results"]
        t = c["table"]

        pass




#######################################################
# standalone functions required for parallel processing
# note that 'self' in routines below is not class instance, but analogous self_pp namedtuple
#######################################################

attrs_pp = ['hp', 'planetary_radius', 'area', 'enclosing_area','polygon','xr','yr','trials','max_threads','measure']
self_pp_tuple = namedtuple('self_pp_tuple', attrs_pp)

def evaluate_randomness(self_pp, pts, ids, hpd):
    """
    Evaluate randomness measure
    """
    match self_pp.measure:
        case 'm2cnd':
            measure, p2 = kth_nearest_neighbour_pp(self_pp, pts, ids, hpd, k=2)  # p2 are neighbours (for plotting real config)
    return measure, p2

def run_trial(self_pp, b, n, trial_index):
    pts, ids, hpd = sprinkle_discs_pp(self_pp, n, b)  # Generate points and ids
    m, _ = evaluate_randomness(self_pp, pts, ids, hpd)
    return m

def run_trial_wrapper(args):
    return run_trial(*args)

def montecarlo_pp(self_pp, b, n):
    """
    Single Monte Carlo run. - parallel
    """
    with ProcessPoolExecutor(max_workers=self_pp.max_threads) as executor:
        trial_indices = range(self_pp.trials)
        args = [(self_pp, b, n, trial_index) for trial_index in trial_indices]
        #measures = list(executor.map(run_trial_wrapper, args))

        # Create a progress bar
        pbar = ProgressBar(max_value=self_pp.trials)

        # Submit tasks to the executor and keep track of futures
        future_to_index = {executor.submit(run_trial_wrapper, arg): trial_index for arg, trial_index in zip(args, trial_indices)}

        measures = []
        for future in as_completed(future_to_index):
            result = future.result()  # Get the result of the completed trial
            measures.append(result)  # Store the result
            pbar.update(future_to_index[future])  # Update progress bar

        pbar.finish()  # Finish the progress bar

    return measures

def random_points_pp(self ,n):
    # consider integral of cos(lat): sin(lat) - range varies from -1 to 1 for -180 to 180
    y0 = np.sin(np.radians(self.yr[0])) # move to init?
    y1 = np.sin(np.radians(self.yr[1]))
    y = np.degrees(np.asin(np.random.uniform(y0, y1, n)))
    x = np.random.uniform(self.xr[0], self.xr[1], n)
    return zip(x ,y)

def sprinkle_discs_pp(self ,n ,diam):
    """
    generate z random points in enclosing area
    find those in actual area
    find non-overlapping (could optimise with 2d spatial bin search)
    take first n good points
    """
    expected_hit_rate = self.area /self.enclosing_area
    angular_radius = diam / self.planetary_radius
    hpd = {}
    count = 0

    while count < n:
        shortfall = n - count
        z = int(1.2 * shortfall / expected_hit_rate) + 10  # guess at required number of points
        p0 = random_points_pp(self,z)
        for lon,lat in p0:
            pt = sph.create_point(longitude=lon, latitude=lat)
            if sph.within(pt, self.polygon):

                # erase existing craters closer than diam/2
                hpx_neighbours = self.hp.cone_search_lonlat(lon*u.deg, lat*u.deg, angular_radius*u.rad)
                for id in hpx_neighbours:
                    if id in hpd:
                        len0 = len(hpd[id])
                        hpd[id] = [e for e in hpd[id] if sph.distance(pt, e, radius = self.planetary_radius) > diam/2]
                        count += len(hpd[id]) - len0

                # add new point
                id0 = self.hp.lonlat_to_healpix(lon*u.deg, lat*u.deg)
                if id0 not in hpd:
                    hpd[id0] = [pt]
                else:
                    hpd[id0].append(pt)
                count += 1
                if count >= n: # should never exceed
                    break

    pts,ids = zip(*[(e, key) for key, id_list in hpd.items() for e in id_list])
    return pts,ids,hpd

def kth_nearest_neighbour_pp(self, pts,ids,hpd, k=1):
    """
    find k_th nearest neighbour list
    """
    def get_kth(pt,zone):
        dist_pt = [(sph.distance(pt, e, radius=self.planetary_radius),e)
                   for id in zone if id in hpd
                   for e in hpd[id]]
        sorted_dist_pt = sorted(dist_pt, key=lambda x: x[0])
        return sorted_dist_pt[k]

    neighbours = []
    distances = []

    if len(pts) < k+1:
        print("no solution")
        return

    for id,pt in zip(ids,pts):
        locality = set()
        outer = {id}
        while True:
            locality |= outer # union
            n = sum(len(hpd[e]) for e in locality if e in hpd)
            if n >= k+1:
                break
            hpx_neighbours = set(self.hp.neighbours(tuple(outer)).flatten())
            outer = hpx_neighbours - locality

        d0,pt0 = get_kth(pt,locality)

        # redefine neighbourhood based on known kth closest: if pt near edge, could be over hpx cell boundary
        hpx_neighbours = self.hp.cone_search_lonlat(sph.get_x(pt) * u.deg, sph.get_y(pt) * u.deg, d0/self.planetary_radius * u.rad)
        d1, pt1 = get_kth(pt, hpx_neighbours)
        neighbours += [pt1]
        distances += [d1]

    mean_distance = np.mean(distances)
    return mean_distance,neighbours
