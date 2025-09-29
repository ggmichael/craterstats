#  Copyright (c) 2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import math
import os

import astropy_healpix as hpx
import astropy.units as u
import numpy as np
import matplotlib.ticker as ticker
from scipy.spatial import SphericalVoronoi
import shapely as shp
import shapely.affinity as shp_aff
import spherely as sph
from progressbar import ProgressBar
import pyproj as prj

import craterstats as cst
import craterstats.gm as gm


class Randomnessanalysis(cst.Spatialcount):
    '''Applies randomness tests to Spatialcount'''

    MEASURES = ['m2cnd','sdaa']
    def __init__(self,filename=None,area_file=None,out=None):
        super().__init__(filename,area_file)
        self.init_Cratercount()
        self.montecarlo = {}
        self.max_threads = os.cpu_count()-1
        self.ra_file = (out if out else self.name) + "_ra.txt"
        self.read()
        binning='root-2'
        self.cc.apply_binning(binning, offset=0.)
        self.plot_reduction_factor = None

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
            ax.plot((x0,x1),(y0,y1), color=cps.grey[0], linewidth=0.5*cps.sz_ratio*sz_ratio, zorder=1)

    def oplot_voronoi(self,cps,craters,p2,ax=None):
        """
        Overplot voronoi polygons
        """
        if not ax:
            ax=cps.ax
        sz_ratio = ax.get_position().width/cps.ax.get_position().width

        # start from sph_polygons output (p2) from sdaa calc.
        shp_polygons0 = [shp.from_wkb(sph.to_wkb(p)) for p in p2]
        # flatten any multipolygons (disjoint areas or holes should also be outlined)
        shp_polygons = [polygon for shape in shp_polygons0 for polygon in (shape.geoms if isinstance(shape, shp.MultiPolygon) else [shape])]

        ns = 20
        frac = np.linspace(0, 1-1/ns, ns)
        geod = prj.Geod(a=1,f=0)

        # need to interpolate between vertices here to get proper curvature in distorted map (only for display)
        # could make ns fn of distance if needed
        interp_threshold = result = 2 * math.pi / 1800
        for p in shp_polygons:
            x0, y0 = p.exterior.xy
            x1,y1 = [],[]
            for i in range(len(x0)):
                i1 = (i + 1) % len(x0)
                azimuth, _, distance = geod.inv(x0[i], y0[i], x0[i1], y0[i1])
                if distance > interp_threshold:
                    x1i, y1i, _ = geod.fwd(np.full(ns, x0[i]), np.full(ns, y0[i]), np.full(ns, azimuth), distance * frac)
                    x1.extend(x1i)
                    y1.extend(y1i)
                else:
                    x1.append(x0[i])
                    y1.append(y0[i])

            x2, y2  = self.ortho_proj(x1, y1)
            projected_polygon = shp.Polygon(zip(x2, y2)) # Reassemble projected polygon
            gm.shp_plot_polygon(ax, projected_polygon, facecolor='none', edgecolor=cps.grey[0], linewidth=0.5 * sz_ratio)


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


    def montecarlo_split(self, measure, self_pp, staggered=False):
        """
        Prepare separate runs across bin range
        """
        match measure:
            case 'sdaa': min_count = 3
            case 'm2cnd': min_count = 3

        self.montecarlo[measure]['trials'] = {}

        for b,n in zip(self.cc.binned['d_min'],self.cc.binned['n_event']):
            if n >= min_count:
                bin = f"{np.log2(b):.3g}"
                print(f"{measure}, bin {bin}: {gm.diameter_range([b,b*math.sqrt(2)],2)}, {n} craters")

                # do parallel monte carlo for random configs
                m = montecarlo_pp(self_pp,b,n)
                self.montecarlo[measure]['trials'][bin] = m


    def run_montecarlo(self, trials, measure):

        self.establish_hpx(trials)
        self_pp = self.self_pp(trials, measure)

        if not measure in self.montecarlo or not self.montecarlo[measure]['n_trials'] == trials: # skip montecarlo if already have data
            self.montecarlo[measure] = {'n_trials':trials}
            self.montecarlo_split(measure, self_pp)

    def calculate_stats(self):
        for measure in self.montecarlo.keys():
            self_pp = self.self_pp(self.montecarlo[measure]['n_trials'], measure)
            self.montecarlo[measure]['stats'] = {}
            stats = namedtuple('stats', ['m0', 'p2', 'mn', 'sd', 'n_sigma','percentile'])
            for bin in self.montecarlo[measure]['trials'].keys():

                pts, ids, hpd = self.get_bin_craters(bin)
                m0,p2 = evaluate_randomness(self_pp,pts, ids, hpd)
                #print(f"Bin: {bin} d_min:{2**float(bin):0.3g} number:{len(pts)} Actual value of measure: {m0:0.3g}")

                m = self.montecarlo[measure]['trials'][bin]
                mn,sd = (np.mean(m),np.std(m))
                n_sigma = (m0-mn)/sd
                percentile = np.searchsorted(np.sort(m), m0) / len(m) * 100
                self.montecarlo[measure]['stats'][bin] = stats(m0=m0, p2=p2, mn=mn, sd=sd, n_sigma=n_sigma,percentile = percentile)

    def plot_histogram(self,cps,measure,bin,ax0=None,sz_ratio=1.): # mark median and 1 sd band
        if ax0:
            ax=ax0
        else:
            cps.create_map_plotspace()
            ax = cps.ax

        res = self.montecarlo[measure]['stats'][bin]
        m = self.montecarlo[measure]['trials'][bin]
        m0 = res.m0

        nbins = round(math.sqrt(self.montecarlo[measure]['n_trials']) + 5)

        h,be = np.histogram(m, bins=nbins)
        bar_width = np.diff(be)
        xr = [min(list(be)+[m0])-bar_width[0],max(list(be)+[m0])+bar_width[0]]
        if not ax0:
            xr[0] -= .6*gm.mag(xr)
        yr = [0,max(h)*(1.1 if ax0 else 1.5)]

        ax.bar(be[:-1], h, width=bar_width, color = cps.grey[3], edgecolor=None, linewidth=0.5,align='edge')

        h = list(h)
        x0,y0 = zip(*[(e,f[i]) for e,f in zip(be,zip([0]+h,h+[0])) for i in [0,1]])
        ax.plot(x0, y0, color=cps.palette[0], linewidth=.7 * sz_ratio)

        ax.plot([m0]*2, yr, color=cps.palette[0],alpha = 0.4, lw = 2 * cps.sz_ratio * sz_ratio)

        ax.text(m0, yr[0]+1*gm.mag(yr), f"{m0:0.3g}\n{gm.percentile_sigfigs(res.percentile)}%", size=.7*cps.scaled_pt_size * math.sqrt(sz_ratio), rotation=0,
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
        xt_label[-1] = "  "*len(xt_label[-1])+xt_label[-1]+(" km" if measure=='m2cnd' else " km²")
        ax.set_xticks(xtickv)
        ax.tick_params(axis='x', which='both', width=.5*sz_ratio, length=cps.pt_size * .3 *sz_ratio, pad=cps.pt_size * .1)
        ax.tick_params(axis='x', which='minor', length=cps.pt_size * .15 * sz_ratio)
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
        ax.set_xticklabels(xt_label,fontsize=.7*cps.scaled_pt_size * math.sqrt(sz_ratio), color=cps.palette[0])

        ax.patch.set_facecolor('none')

        if ax0:
            for s in ['left', 'right', 'top']: ax.spines[s].set_visible(False)
            ax.set_yticks([])
        else:
            ax.set_ylabel('Frequency')

    def get_plot_reduction_factor(self,hf):
        """
        Find reduction factor so that map doesn't overlap histogram
        hf : histogram fractional width of plot
        return: amount to reduce normalised map plot
        """
        if not self.plot_reduction_factor:
            # this could be moved to init....
            cen = sph.centroid(self.polygon)
            cenlon, cenlat = (sph.get_x(cen),sph.get_y(cen))
            ortho_proj = prj.Proj(proj='ortho', lat_0=cenlat, lon_0=cenlon, R=self.planetary_radius)
            self.ortho_proj = ortho_proj

            # do area
            z = sph.to_wkb(self.polygon)
            multipolygon = shp.from_wkb(z)
            p = []

            if not isinstance(multipolygon, shp.MultiPolygon):
                multipolygon = shp.MultiPolygon([multipolygon])

            for poly in multipolygon.geoms:
                exterior_x, exterior_y = poly.exterior.xy
                x_exterior, y_exterior = ortho_proj(exterior_x, exterior_y)
                # Reassemble the projected polygon
                projected_polygon = shp.Polygon(zip(x_exterior, y_exterior))
                p.append(projected_polygon)

            mp = shp.MultiPolygon(p)
            x_mn,y_mn,x_mx,y_mx = shp.bounds(mp)
            x_mg,y_mg = (x_mx-x_mn,y_mx-y_mn)
            mg = max(x_mg,y_mg)
            mp_scaled = shp_aff.scale(mp,xfact=1/mg,yfact=1/mg)
            mp_normalised = shp_aff.translate(mp_scaled,xoff=-mp_scaled.bounds[0], yoff=-mp_scaled.bounds[1])
            hf = .3
            hist_box = shp.Polygon([(1,0),(1,hf*.5),(1-hf,hf*.5),(1-hf,0),(1,0)])
            f = 1.
            while shp_aff.scale(mp_normalised,xfact=f,yfact=f).overlaps(hist_box):
                f *= .98
            self.plot_reduction_factor = f
        return self.plot_reduction_factor

    def plot_map_and_histogram(self, cps, measure, bin, ax=None,sz_ratio=1.):
        if not ax:
            ax=cps.ax
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.set_facecolor('none')

        hf = .3
        mf = self.get_plot_reduction_factor(hf)
        offset = (0, .15)
        pos = ax.get_position()
        dx,dy = ( (1-hf) * pos.width * offset[0], pos.height * (1- hf*.5) * offset[1] )
        ax1 = cps.fig.add_axes([pos.x0, pos.y0 + (1-mf) * pos.height, pos.width * mf, pos.height * mf])
        ax2 = cps.fig.add_axes([pos.x0 + (1-hf) * pos.width - dx, pos.y0 +dy, pos.width * hf - dx, pos.height * hf *.5])

        craters = self.get_bin_craters(bin, Craterlist=True)
        self.plot(cps, craters=craters, ax=ax1)
        match measure:
            case 'm2cnd': self.oplot_neighbours(cps,craters,self.montecarlo[measure]['stats'][bin].p2,ax=ax1)
            case 'sdaa': self.oplot_voronoi(cps, craters, self.montecarlo[measure]['stats'][bin].p2, ax=ax1)
        self.plot_histogram(cps, measure, bin, ax0=ax2,sz_ratio=sz_ratio)

        d_min = 2**float(bin)
        ax.text(1., .95, gm.diameter_range([d_min,d_min*2**.499],2)+f'\nn = {len(craters.diam)}', size=.7 * cps.scaled_pt_size * math.sqrt(sz_ratio),
                 transform=ax.transAxes, ha="right",va='top')


    def plot_montecarlo_split(self,cps,measure): # multiplot?
        dim = math.ceil(math.sqrt(len(self.montecarlo[measure]['stats'])+1))
        cps.create_map_plotspace()
        pos = cps.ax.get_position()
        #cps.ax.set_visible(False)
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

        for i,bin in enumerate(self.montecarlo[measure]['stats']):
            self.plot_map_and_histogram(cps,measure,bin ,ax=make_ax(i),sz_ratio=1/dim)

        self.plot_n_sigma(cps, measure, ax0=make_ax(dim ** 2 - 1))


    def plot_n_sigma(self, cps, measure, ax0=None):
        if not ax0:
            ax0=cps.ax
        ax0.set_visible(False)
        pos = ax0.get_position()
        sz_ratio = pos.width / cps.ax.get_position().width

        if ax0:
            ax = cps.fig.add_axes([pos.x0+.15*pos.width,pos.y0 + pos.height*.3,pos.width*.95,pos.height*.4])
        else:
            ax = cps.fig.add_axes([pos.x0, pos.y0 + pos.height / 3, pos.width, pos.height / 2])

        x = [np.log10(2**(float(r)+.25)) for r in self.montecarlo[measure]['stats']]
        y0 = [(e.m0 - e.mn)/e.sd for e in self.montecarlo[measure]['stats'].values()]
        y1 = [cst.n_sigma_scaling(e) for e in y0] # apply axis scaling
        y = [-e if measure=='sdaa' else e for e in y1] # flip for sdaa
        xr = min(x)-np.log10(2**.251),max(x)+np.log10(2**.251) # control end-labels
        mg = gm.mag(cps.xrange)

        for spine in set(ax.spines.values())-{'bottom'}: spine.set_visible(False)
        #ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        ax.set_ylim(cst.n_sigma_scaling(-6), cst.n_sigma_scaling(6))
        ax.set_xlim(xr[0], xr[1])

        ax.fill_between(xr, [cst.n_sigma_scaling(-3)]*2, y2 = [cst.n_sigma_scaling(3)]*2, color=cps.grey[2], edgecolor='none')
        ax.fill_between(xr, [cst.n_sigma_scaling(-2)]*2, y2 = [cst.n_sigma_scaling(2)]*2, color=cps.grey[3], edgecolor='none')
        ax.fill_between(xr, [cst.n_sigma_scaling(-1)]*2, y2 = [cst.n_sigma_scaling(1)]*2, color=cps.grey[1], edgecolor='none')

        marker = cps.marker_def[10].copy()
        marker['markersize'] *= sz_ratio

        ax.plot(x, y, color=cps.palette[0], lw=1. * cps.sz_ratio*sz_ratio, **marker, linestyle=cst.LINESTYLES[measure], clip_on=False)

        dy=-.08
        ax.text(np.mean(xr), cst.n_sigma_scaling(-5), "clustered", color=cps.grey[0], size=.4 * cps.scaled_pt_size, va='center', ha='center', clip_on=False)
        ax.text(np.mean(xr), cst.n_sigma_scaling(7), "separated", color=cps.grey[0], size=.4 * cps.scaled_pt_size, va='center', ha='center', clip_on=False)
        ax.text(xr[1], dy, r"    $n_\sigma$", color=cps.grey[0], size=.4 * cps.scaled_pt_size, va='center', ha='left')
        for y in [-3,-1,0,1,3]:
            ax.text(xr[1], cst.n_sigma_scaling(y)+dy, f"{abs(y):>2}", color=cps.grey[0], size=.3 * cps.scaled_pt_size, va='center', ha='left')

        ax.text(xr[0] - mg*.005, 0, measure + f"\n{self.montecarlo[measure]['n_trials']} trials", color=cps.grey[0], size=.4 * cps.scaled_pt_size,  va='center', ha='right')

        xtickv,xtickname,_,xminorv = cst.Hartmann_bins(xr)
        ax.spines['top'].set_position(('data', cst.n_sigma_scaling(3)))
        ax.xaxis.set_ticks_position('top')
        ax.tick_params(axis='x', which='both', direction="out", color=cps.grey[1], labelcolor=cps.grey[0], width=.5*sz_ratio,
                       length=cps.pt_size*sz_ratio * .2, pad=cps.pt_size*sz_ratio * .2, labelsize=cps.scaled_pt_size*sz_ratio)
        ax.tick_params(axis='x', which='minor', length=cps.pt_size*sz_ratio * .15)
        ax.set_xticks(xtickv)
        ax.set_xticks(xminorv, minor=True)
        ax.set_xticklabels(xtickname)



    def write(self):
        s = ['# Randomness analysis',
              f'version = {cst.__version__}',
              f'source = "{self.filename}"',
              ]

        table = []
        for bin in self.montecarlo[next(iter(self.montecarlo))]['stats'].keys():
            row = f"{bin:<12}"
            for measure in self.montecarlo:
                row += f"\t{self.montecarlo[measure]['stats'][bin].n_sigma:9.4g}"
            table.append(row)
        n_sigma = (['#','n_sigma = {bin' + ''.join([f', {measure}' for measure in self.montecarlo])]
                   + table + ['}'])
        s += n_sigma

        for measure in self.montecarlo:
            trials = (
                ['trials  = {index, ' + ", ".join([b for b in self.montecarlo[measure]['trials']])]
                + ["\t".join([f"{t:<12}"] + [f"{v[t]:<12.7g}" for bin,v in self.montecarlo[measure]['trials'].items()])
                            for t in range(self.montecarlo[measure]['n_trials']) ]
                + ['}'])
            s1 = (
                ['#',f'{measure} = {{',
                f'n_trials = {self.montecarlo[measure]['n_trials']}']
                + trials
                + ['}'])
            s += s1
        gm.write_textfile(self.ra_file,s)

    def read(self):
        # allow read from source file location, but write will still be to current dir or -o
        possible_locations = (self.ra_file, gm.filename(self.filename, 'pn1','_ra.txt'))
        f = next((loc for loc in possible_locations if gm.file_exists(loc)), None)
        if f:
            c = gm.read_textstructure(f)
            for name in self.MEASURES:
                if name in c:
                    self.montecarlo[name] = {
                        'n_trials':int(c[name]['n_trials']),
                        }
                    self.montecarlo[name]['trials'] = {}
                    for b in list(c[name]['trials'].keys())[1:]:
                        self.montecarlo[name]['trials'][b] = [float(e) for e in c[name]['trials'][b]]

    def self_pp(self,trials, measure):
        """
        tuple of vars for parallel processing
        """
        return self_pp_tuple(trials=trials,measure=measure,**{key: getattr(self, key) for key in attrs_pp[:-2]})

#######################################################
# standalone functions required for parallel processing
# note that 'self' in routines below is not class instance, but analogous self_pp namedtuple
#######################################################

attrs_pp = ['hp', 'planetary_radius', 'area', 'enclosing_area', 'polygon', 'xr', 'yr', 'max_threads', 'trials','measure']
self_pp_tuple = namedtuple('self_pp_tuple', attrs_pp)

def evaluate_randomness(self_pp, pts, ids, hpd):
    """
    Evaluate randomness measure
    """
    match self_pp.measure:
        case 'm2cnd':
            measure, p2 = kth_nearest_neighbour_pp(self_pp, pts, ids, hpd, k=2)  # p2 are neighbours (for plotting real config)
        case 'sdaa':
            measure, p2 = sdaa(self_pp, pts, ids, hpd)
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
        pbar = ProgressBar(max_value=self_pp.trials)

        # Submit tasks to executor and track futures
        future_to_index = {executor.submit(run_trial_wrapper, arg): trial_index for arg, trial_index in zip(args, trial_indices)}

        measures = []
        for future in as_completed(future_to_index):
            result = future.result()  # Get result of completed trial
            measures.append(result)
            pbar.update(future_to_index[future])  # Update progress bar
        pbar.finish()
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


def sdaa(self, pts, ids, hpd):
    """
    find standard deviation of adjacent area (spherical)
    """

    ll_radians = [(math.radians(sph.get_x(p)), math.radians(sph.get_y(p))) for p in pts]
    xyz = np.array([(math.cos(y) * math.cos(x), math.cos(y) * math.sin(x), math.sin(y)) for x, y in ll_radians])

    center = np.array([0, 0, 0])
    radius = 1.0
    sv = SphericalVoronoi(xyz, radius, center, threshold=1e-09)
    sv.sort_vertices_of_regions()

    xyz_polygons = [[sv.vertices[id] for id in region] for region in sv.regions]
    ll_polygons = [[(math.degrees(math.atan2(y, x)), math.degrees(math.asin(z))) for x, y, z in p] for p in xyz_polygons]
    sph_polygons0 = [sph.create_polygon([(lon, lat) for lon, lat in p]) for p in ll_polygons]
    sph_polygons = [sph.intersection(self.polygon, p) for p in sph_polygons0]

    areas = [sph.area(p,radius=self.planetary_radius) for p in sph_polygons]
    sdaa = np.std(areas)

    return sdaa, sph_polygons


