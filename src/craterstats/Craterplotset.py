#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.
import copy
import sys
import os

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.figure as mfig
from matplotlib import patheffects
from matplotlib.patches import Polygon
import matplotlib.colors as colors
import matplotlib.patches as patches
import matplotlib.font_manager as fm

import numpy as np
from palettable.colorbrewer.diverging import Spectral_9
from progressbar import progressbar

import craterstats as cst
import craterstats.gm as gm

class Craterplotset:
    """
    Base object for set of Craterplots. Holds properties common to all of set.
    Creates plot layout and calls overplot methods of Craterplot instances.
    Aggregates legend annotations.

    """
    
    def __init__(self,*args,**kwargs):   
            
        # matplotlib objects
        self.fig=None
        self.ax=None
        
        self.craterplot=[]  #craterplot layers   
        self.cf=None        #chronology fn
        self.pf=None        #production fn
        self.ef=None        #equilibrium fn
        self.ep=None        #epoch system

        self.cm2inch=1/2.54

        self.UpdateSettings({
            'title':None,
            'presentation':'differential',
            'xrange':[-3,2],
            'yrange':[-5,5],
            'style':'natural',
            'isochrons':None,
            'print_dimensions':'7.5x7.5',
            'pt_size':9.,
            'ref_diameter':1.,
            'sig_figs':3,
            'randomness':0,
            'mu':1,
            'invert':0,
            'text_halo':1,
            'bins':False,
            },*args,kwargs)

        self.sz_ratio= self.pt_size / 9.
        self.grey = cst.GREYS[self.invert]
        self.palette = [e[self.invert] for e in cst.PALETTE]
        self.marker_def = [e[2].copy() for e in cst.MARKERS]
        self.max_y = None

        
    def UpdateSettings(self,*args,**kwargs): #pass either dictionary or keywords
        a = {k: v for d in args for k, v in d.items()}
        a.update(**kwargs)
        for k, v in a.items():
            #if k == 'source': self.cratercount = cst.Cratercount(v)
            if k in ('xrange','yrange'): v=[float(e) for e in v]
            if k in ('pt_size','ref_diameter'): v = float(v)
            if k in (
                    'randomness',
                    'mu',
                    'invert',
                    'text_halo',
                    'sig_figs',
                     ):
                v = int(v)
            setattr(self, k, v)


    def EstablishFontandScaling(self):

        plt.style.use(('default', 'dark_background')[self.invert])

        # Path to your local font directory
        font_dir = os.path.join(os.path.dirname(__file__), 'fonts')

        # Register each font manually
        for fname in os.listdir(font_dir):
            if fname.endswith(".ttf"):
                path = os.path.join(font_dir, fname)
                fm.fontManager.addfont(path)

        available_font = 'Open Sans'

        # Set mathtext font set and fallback
        plt.rc('mathtext', fontset='custom',
               rm=available_font,
               bf=available_font,
               it=available_font,
               cal=available_font)

        plt.rcParams['mathtext.fallback'] = 'stix' #'stixsans'

        scale_factor = {'Open Sans':.89,
                        'Noto Sans':.89,
                        'Myriad Pro': 1.,
                        'Verdana': .83,
                        'DejaVu Sans': .83,
                        'Tahoma': .93,
                        }[available_font]
        self.scaled_pt_size = self.pt_size * scale_factor
        plt.rc('font', family=available_font, size=self.scaled_pt_size)

        #plt.rcParams['svg.fonttype'] = 'none' # makes text editable, but then not portable
        plt.rcParams['image.composite_image'] = False # prevent optimisation of svg raster

        tw = .4 * self.sz_ratio
        plt.rcParams.update({
            'legend.fontsize': 'x-small',
            'legend.title_fontsize': 'small',
            'axes.labelsize': self.scaled_pt_size * .9,
            'axes.titlesize': 'small',
            'xtick.labelsize': 'medium',
            'ytick.labelsize': 'medium',
            'axes.titlepad': self.scaled_pt_size * 1.,
            'axes.linewidth': tw,
            'xtick.major.width': tw,
            'xtick.minor.width': tw,
            'ytick.major.width': tw,
            'ytick.minor.width': tw,
        })

    def CreatePlotSpace(self):
        """
        Set up plot dimensions, font and scaled font size, titles, tick marks, and tick labels
        Create layout
        Set up plot coordinate transformations

        """

        if self.fig: del self.fig
        self.EstablishFontandScaling()
            
#set up plot dimensions

        def f(x): return np.clip(gm.mag(x), 1, None)
        self.decades=f(self.xrange),f(self.yrange)

        self.data_aspect=(
            2                                 if self.presentation=='differential' else
            self.decades[1]/self.decades[0]   if self.presentation in ['Hartmann','chronology', 'rate'] else
            1
            )            
            
        plot_dims=[float(e) for e in self.print_dimensions.split('x')]
        
        self.print_scale=(                                                      #in cm/decade
            np.clip(plot_dims[0],1,None) if len(plot_dims)==1 else
            plot_dims[0]/self.decades[0] if self.presentation=='Hartmann' else
            min(np.clip(plot_dims*np.array([1,self.data_aspect]),1,None)/self.decades)
            )

        randomness_plot=int(self.randomness and not self.presentation in ['chronology', 'rate']) #boolean as 0,1
        margin=self.pt_size*.2  #plot margin in cm
        xsize=self.decades[0]*self.print_scale+2*margin #in cm

        ysize=(
            xsize+self.print_scale*randomness_plot  if self.presentation=='Hartmann' else
            xsize                                   if self.presentation in ['chronology', 'rate'] else
            (randomness_plot+self.decades[1]/self.data_aspect)*self.print_scale+2*margin
            )
              
        self.position=margin*np.array([1,1,xsize/margin-2,ysize/margin-2-randomness_plot]) #cm
        position_randomness=margin*np.array([1,ysize/margin-.8-randomness_plot,xsize/margin-2,ysize/margin-2]) #cm - not yet used
        normalised_position=self.position/np.array([xsize,ysize,xsize,ysize])  #pos, width for matplotlib axes

# set up marker size
        f = self.decades[0] * self.print_scale / 7.5
        for e in self.marker_def:
            e['markersize'] *= 0.8 * f  # * self.print_scale/1.875
            e['markeredgewidth'] = .5 * f  # * self.print_scale/1.875

# set up titles, tick marks, and tick labels

        nonroot2=False in [cp.binning=='root-2' for cp in self.craterplot]

        xtitle="Age, Ga" if self.presentation in ['chronology', 'rate'] else 'Diameter'
        ytitle={
            'cumulative':   'Cumulative crater density, km$^{-2}$',           
            'differential': 'Differential crater density, km$^{-3}$',
            'R-plot': 'Relative crater density (R)',
            'Hartmann':     'Craters per $√$2-bin'+(' (equivalent)' if nonroot2 else '')+', km$^{-2}$',
            'chronology':   'Cumulative crater density N(>'+format(self.ref_diameter,'.0f')+' km), km$^{-2}$',
            'rate':         'Crater formation rate N(>'+format(self.ref_diameter,'.0f')+' km), km$^{-2}$ Ga$^{-1}$',
            }[self.presentation]
        
        title = ('\n'.join(self.title.split('|')) if self.title else None)

        xminor=xmajor=xtickv=None
        add_xminorlogticks=False

 
        if self.presentation in ['chronology', 'rate']:
            xminor, xmajor = .5, 1
        else:
            if self.style=='root-2' or self.presentation=='Hartmann':
                xtickv, xtickname, xminor, _ = cst.Hartmann_bins(self.xrange)
                plt.rcParams.update({'xtick.labelsize':self.scaled_pt_size*.65})
                if self.presentation == 'Hartmann':
                    plt.rcParams.update({'ytick.labelsize': self.scaled_pt_size *.8})
            elif self.style=='natural':                
                v=np.arange(np.ceil(self.xrange[0]),np.floor(self.xrange[1])+1).tolist()
                xtickname=[format(10**e,'0g')+r'$\,$km' if e>=0 else format(10**(e+3),'0g')+r'$\,$m' for e in v]
                xtickv=v
                add_xminorlogticks=True

#create layout

        fig = mfig.Figure(figsize=[xsize*self.cm2inch,ysize*self.cm2inch],dpi=200)

        ax=fig.add_axes(normalised_position)
        ax.set_axisbelow(False) # draw axis on top of other elements

        # Add solid background rectangle for -transparent option (only axis labels transparent)
        bg = patches.Rectangle((0, 0), 1, 1,
            transform=ax.transAxes, zorder=-10,  color= 'black' if self.invert else 'white', linewidth=0)
        ax.add_patch(bg)

        if add_xminorlogticks:                      #draw minor xlog ticks using different axes, since main x axis is linear
            ax2=fig.add_axes(normalised_position,frameon=False)
            ax2.set_axisbelow(False)
            ax2.set_xscale('log')      
            ax2.set_xbound(lower=10**self.xrange[0], upper=10**self.xrange[1])  
            ax2.tick_params(axis='x',which='minor',direction="in",length=self.pt_size*.15, top=True)
            ax2.tick_params(axis='x',which='major', bottom=False,labelbottom=False)
            ax2.get_yaxis().set_visible(False)            
                    
        ax.set_yscale('log')                                             #don't use xlog scale - awful to set up ticks for Hartmann binning
        ax.set_ylim(bottom=10**self.yrange[0], top=10**self.yrange[1])   #nb craterstats2 used linear for both axes
        ax.set_xlim(left=self.xrange[0], right=self.xrange[1])
        
        ax.tick_params(axis='both',which='major',direction="in",length=self.pt_size*.3,right=True,top=True)
        ax.tick_params(axis='both',which='minor',direction="in",length=self.pt_size*.15,right=True,top=True)
 
        if xminor is not None: ax.xaxis.set_minor_locator(ticker.MultipleLocator(xminor))            
        if xmajor is not None: ax.xaxis.set_major_locator(ticker.MultipleLocator(xmajor))

        ax.yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=self.decades[1]+2))
        ax.yaxis.set_minor_locator(ticker.LogLocator(base=10., subs=(.1,.2,.3,.4,.5,.6,.7,.8,.9), numticks=self.decades[1]+2))
        ax.yaxis.set_minor_formatter(ticker.NullFormatter())
                    
        if xtickv is not None:
            ax.set_xticks(xtickv)
            ax.set_xticklabels(xtickname)                
        
        if title:ax.set_title(title)
        if xtitle != '':ax.set_xlabel(xtitle)
        if ytitle != '':ax.set_ylabel(ytitle)

# set up n_sigma axis
        if self.max_y:
            y_ra_normalised = (self.max_y + gm.mag(self.yrange)/16 + self.ra_offset/20 - self.yrange[0]) / gm.mag(self.yrange)
            ax_ra = fig.add_axes([normalised_position[0],normalised_position[1]+y_ra_normalised*normalised_position[3],normalised_position[2],normalised_position[3]/16])
            ax_ra.set_xlim(left=self.xrange[0], right=self.xrange[1])
            ax_ra.set_ylim(-np.sqrt(3),np.sqrt(3))
            ax_ra.set_facecolor('none')
            ax_ra.yaxis.tick_right()
            ytick = [-3,-2,-1,0,1,2,3]
            ytickv = cst.n_sigma_scaling(ytick)
            yticklabels = [f"{e}" for e in ytick]
            ax_ra.set_yticks(ytickv)
            ax_ra.set_yticklabels(yticklabels)
            ax_ra.tick_params(axis='y', direction='in',labelsize=0.5*self.scaled_pt_size, width=.5, length=self.pt_size * .2, pad=self.pt_size * .1)
            for s in ['left','right','top','bottom']: ax_ra.spines[s].set_visible(False)
            ax_ra.set_yticks([])
            ax_ra.set_xticks([])
            self.ra_legend_drawn = False
            self.ax_ra = ax_ra

        self.fig=fig
        self.ax=ax

# add bin labels
        if self.bins:
            cpb = next((cp for cp in self.craterplot if cp.type=='data'), None)
            bins = cpb.cratercount.generate_bins(cpb.binning, 10**self.xrange)
            for i,b in enumerate(bins):
                c = [self.palette[0],'red','dodgerblue'][i%3]
                if b < 10 ** self.xrange[1]:
                    if i%3!=0:
                        ax.fill_between(np.log10([b,bins[i+1]]), 10**self.yrange[0], 10**self.yrange[1], color=c, ec=None, alpha=0.1,zorder=3)
                    if b > 10 ** self.xrange[0]:
                        for y in [.16,.5,.84]:
                            ax.text(np.log10(b), y, f" {b:.1e}"[0:4], ha='center', va='bottom' if (i%2)==0 else 'top',
                                    color=c, fontsize=self.scaled_pt_size * .4, rotation=90, transform = ax.get_xaxis_transform())

# set up coordinate transformations
        a2d=ax.transAxes + ax.transData.inverted()
        self.axis_to_data = a2d.transform
        self.data_to_axis = a2d.inverted().transform
        self.axis_to_fig = (ax.transAxes + fig.transFigure.inverted()).transform
     

    def create_time_axis_plotspace(self):
        """
        Set up plotspace with normal/split time axis for sequence, uncertainty plot
        """
        if self.fig: del self.fig
        self.EstablishFontandScaling()

        # set up plot dimensions
        margin = self.pt_size * .2  # plot margin in cm
        plot_dims = [float(e) for e in self.print_dimensions.split('x')]
        if len(plot_dims) == 1:
            xsize = ysize = 5 * plot_dims[0] + 2 * margin
            self.aspect_ratio=1
        else:
            xsize, ysize = (e + 2 * margin for e in plot_dims)
            self.aspect_ratio = plot_dims[1]/plot_dims[0]

        def f(x): return np.clip(gm.mag(x), 1, None)
        self.decades=f(self.xrange),f(self.yrange)

        self.t_max = np.clip(max(self.xrange), 3., 4.5)
        self.t_min = np.clip(min(self.xrange), 0., 3.5)

        if self.t_min<1 and self.t_min !=0:
            self.t_min=10**np.floor(np.log10(self.t_min))
            self.crossover = True
        else:
            self.crossover = False

        if self.crossover:
            t_crossover = 3.
            dec2lin = 0.7
            xtickv = [e for e in [3., 3.5, 4.] if e<=self.t_max]
            log_t_min = np.log10(self.t_min)
            lin_units = max(self.t_max - t_crossover, 0) / dec2lin
            log_units = np.log10(t_crossover) - log_t_min
        else:
            t_crossover = self.t_min
            lin_units = 1
            log_units = 0
            xtickv = [e/2. for e in range(0,10) if self.t_min <= e/2. <= self.t_max]

        xticklabels = [f"{e:.2g}" for e in xtickv]
        xticklabels[-1] += ' Ga'

        xfrac_linear = lin_units / (lin_units + log_units)
        width_linear = xfrac_linear * (xsize - margin * 2)
        pos_linear = [margin, margin, width_linear, ysize - 2*margin]
        pos_log = [margin + width_linear, margin, (1 - xfrac_linear) * (xsize - margin * 2), pos_linear[3]]
        pos_all = [margin, margin, xsize - margin * 2, ysize - margin * 2]

        fig = mfig.Figure(figsize=[xsize * self.cm2inch, ysize * self.cm2inch], dpi=500)

        ax_lin = fig.add_axes(pos_linear / np.array([xsize, ysize, xsize, ysize]))
        ax_log = fig.add_axes(pos_log / np.array([xsize, ysize, xsize, ysize]))
        ax = fig.add_axes(pos_all / np.array([xsize, ysize, xsize, ysize]))

        # Add solid background rectangle for -transparent option (only axis labels transparent)
        bg_ax = fig.add_axes(pos_all / np.array([xsize, ysize, xsize, ysize]), zorder=-1)
        bg = patches.Rectangle((0, 0), 1, 1,
            transform=bg_ax.transAxes, zorder=-10,  color= 'black' if self.invert else 'white', linewidth=0)
        bg_ax.add_patch(bg)
        bg_ax.set_xticks([])
        bg_ax.set_yticks([])
        bg_ax.set_frame_on(False)

        if self.presentation == 'uncertainty':
            offset_cbar = [.2, .2]  # offset_x,w from main plot
            pos_cbar = [xsize - margin + offset_cbar[0], margin, offset_cbar[1], ysize - margin*2]
            ax_cbar = fig.add_axes(pos_cbar / np.array([xsize, ysize, xsize, ysize]))
            ax_cbar.tick_params(length=2, pad=1.5)

        #ax_log
        if self.crossover:
            ax_log.set_xscale('log')
            ax_log.set_xlim(left=t_crossover, right=10 ** log_t_min)
            def xlogFuncFormatter(x, pos):
                return cst.str_age(x, simple=True)
            ax_log.xaxis.set_major_formatter(ticker.FuncFormatter(xlogFuncFormatter))
            ax_log.xaxis.set_major_locator(ticker.LogLocator(numticks=999))
            ax_log.xaxis.set_minor_locator(ticker.LogLocator(numticks=999, subs="auto"))
            ax_log.tick_params(length=2, pad=1.5)
            ax_log.tick_params(which='minor',length=1)
            ax_log.get_yaxis().set_visible(False)
            ax_log.spines[['left', 'right', 'top']].set_visible(False)
            ax_log.set_ylim(bottom=0, top=1)
        else:
            ax_log.set_axis_off()

        #ax_lin
        ax_lin.set_xlim(left=self.t_max if self.t_max>t_crossover else t_crossover+.1, right=t_crossover)
        ax_lin.set_xticks(xtickv, labels=xticklabels)
        ax_lin.tick_params(length=2, pad=1.5)
        ax_lin.tick_params(which='minor',length=1)
        ax_lin.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))

        if self.presentation == 'sequence':
            ax_lin.set_ylim(bottom=0, top=1)
            ax_lin.get_yaxis().set_visible(False)
            ax_lin.spines[['left', 'right']].set_visible(False)
        elif self.presentation == 'uncertainty':
            ax_lin.set_yscale('log')
            ax_lin.yaxis.set_major_locator(ticker.LogLocator(numticks=999))
            ax_lin.yaxis.set_minor_locator(ticker.LogLocator(numticks=999, subs="auto"))
            ax_lin.set_ylim(bottom=10 ** self.yrange[0], top=10 ** self.yrange[1])
            ax_lin.set_ylabel('Area, km$^2$')
            ax_lin.spines[['right', 'top']].set_visible(False)

        #ax_all
        ax.set_xlim(left=0, right=1)
        ax.xaxis.set_ticks_position('none') #not hiding xaxis because want to show xlabel
        ax.set_xticks([])
        ax.set_ylim(bottom=0, top=1)
        ax.get_yaxis().set_visible(False)
        if self.presentation == 'sequence':
            ax.spines[['left', 'right', 'top', 'bottom']].set_visible(False)
            ax.set_xlabel('Age', labelpad=2 * self.scaled_pt_size)
        elif self.presentation == 'uncertainty':
            #ax.spines[['left', 'bottom']].set_visible(False)
            ax.set_xlabel('Actual age', labelpad=2*self.scaled_pt_size)

        if self.t_max>3.:
            ax.plot(xfrac_linear, 0, marker='x', clip_on=False, markeredgewidth=.3, color=self.palette[0],
                             markersize=self.pt_size * .4, zorder=2)
        ax.patch.set_facecolor('none')

        title = '\n'.join(self.title.split('|')) if self.title else None
        if title: ax.set_title(title)

        # create layout
        self.fig = fig
        self.ax = ax
        self.ax2 = (ax_lin,ax_log)
        if self.presentation == 'uncertainty':
            self.ax_cbar=ax_cbar

        # set up coordinate transformations
        a2d = ax.transAxes + ax.transData.inverted()
        self.axis_to_data = a2d.transform
        self.data_to_axis = a2d.inverted().transform
        self.axis_to_fig = (ax.transAxes + fig.transFigure.inverted()).transform

        # pass on values
        self.t_crossover = t_crossover
        self.xfrac_linear = xfrac_linear

    def draw(self):
        """
        Draw plot, adding all specified items

        """

        if self.presentation in ('sequence','uncertainty'):
            self.create_time_axis_plotspace()
        else:
            self.CreatePlotSpace()

        N=self.pf.evaluate("cumulative",[self.ref_diameter,1.]) if self.pf else [1,1]
        ref_diam_ratio=N[0]/N[1]

        if 'f' in self.legend:
            txt=''
            if self.ep: txt += "Epochs: " + self.ep.name + '\n'
            if self.ef and self.presentation not in ['sequence']: txt += "EF: " + self.ef.name + '\n'
            if not (self.presentation in ['chronology', 'rate'] and self.ref_diameter==1) or self.ep: txt += "PF: " + self.pf.name + '\n'
            txt += "CF: " + self.cf.name
            #offset would be better specified in pts (1.5 * fontsize) [for many-decade plots]:
            if self.presentation in ('uncertainty'):
                text = self.ax.text(.95, .05, txt, transform=self.ax.transAxes, fontsize=self.scaled_pt_size * .7,
                                    ha='right',linespacing=1.5)
            else:
                text=self.ax.text(.05, .05, txt, transform=self.ax.transAxes, fontsize=self.scaled_pt_size * .7, linespacing=1.5)
            if self.text_halo and self.presentation not in ('sequence', 'uncertainty'):
                text.set_path_effects([patheffects.withStroke(linewidth=self.sz_ratio, foreground='black' if self.invert else 'white',alpha=0.7)])  # White shadow beneath text

        if self.presentation in ['chronology', 'rate']:
            phi=self.presentation=='rate'
            if self.ep:
                self.ep.chronology_oplot(self,phi=phi)
            t,y=self.cf.getplotdata(linear=True,phi=phi)

            if self.ref_diameter != 1.:  # only show legend if not N(1)
                self.ax.plot(t, y * ref_diam_ratio, label=f'N(>{self.ref_diameter:g} km)',
                             lw=1, color=self.palette[0], marker=None)
                self.ax.plot(t, y, label='N(>1 km)', color=self.grey[0], lw=1, marker=None)
            else:
                self.ax.plot(t, y, color=self.palette[0], lw=1, marker=None)

        if self.presentation in ['cumulative', 'differential', 'R-plot', 'Hartmann']:
            if self.ep: #overplot epochs
                self.ep.oplot(self)
            if self.ef:
                e = self.ef.getplotdata(self.presentation)
                self.ax.plot(np.log10(e['d']), e['y'], color=self.grey[0], lw=.7)

            if self.isochrons:
                self.plot_isochrons()

        if self.presentation == 'sequence' and self.ep: self.ep.sequence_oplot(self)

        # if self.presentation == 'uncertainty':
        #     self.age_area_plot()

        if self.presentation in ['cumulative', 'differential', 'R-plot', 'Hartmann', 'sequence']:
            for cp in reversed(self.craterplot):
                cp.overplot(self)

        # aggregate legend entries
        h, b = self.ax.get_legend_handles_labels()
        h1, b1 =[], []
        skip=False
        for i,e in enumerate(b):
            if skip:
                skip=False
                continue
            if e=='fit':
                skip = True
                if set(self.legend) & set('crN') != set():
                    h1.append((h[i],h[i+1]))
                    b1.append(b[i+1])
            else:
                h1.append(h[i])
                b1.append(e)

        h1.reverse()
        b1.reverse()
        legend=self.ax.legend(h1,b1,frameon=False, loc='upper right', borderaxespad=1,handletextpad=0.5,labelspacing=.4,handlelength=1.5)
        if self.text_halo:
            for item in legend.get_texts(): #inverted shadow for improved contrast
                item.set_path_effects([patheffects.withStroke(linewidth=self.sz_ratio, foreground='black' if self.invert else 'white', alpha=0.7)])

    def plot_isochrons(self):
        """
        Overplot predefined isochrons with annotations

        :return: none
        """

        isochrons = [(abs(float(e.rstrip('ash'))),'h' in e,'a' in e, 's' in e) for e in self.isochrons.split(',')]

        for t,hide,above,small in isochrons:
            a0 = self.cf.a0(t)
            iso = self.pf.getisochron(self.presentation, a0, self.ef)
            d10 = np.log10(iso['d'])
            self.ax.plot(d10, iso['y'], color=self.grey[0], lw=.5*self.sz_ratio)
            y_factor = self.data_aspect

            q = gm.where(np.abs(np.log10(iso['y']) - (self.yrange[1] - .1 * y_factor)) < .1)
            if not q or (d10[q[0]] < self.xrange[0]):  # (d10[q[0][0]] < self.xrange[0]):
                q= gm.where(abs(d10 - np.max([self.xrange[0] + .15, d10[0]])) < .1)

            if q and not hide:
                sx = np.mean(d10[q])
                sy = np.log10(self.pf.evaluate(self.presentation, 10**sx, a0))-.05

                th = np.rad2deg(np.arctan2(np.log10(self.pf.evaluate(self.presentation, 10**(sx + .3), a0))-sy, .3 * y_factor))

                self.ax.text(sx, 10 ** sy, cst.str_age(t, simple=True),
                             color=self.grey[0], size=self.scaled_pt_size*(.5 if small else .7),
                             rotation=th, rotation_mode='anchor',
                             verticalalignment='bottom' if above else 'top',
                             horizontalalignment='left',
                             #bbox=dict(facecolor='none', edgecolor='black', boxstyle='square,pad=0.6')
                             )

    def autoscale(self,xrange=None,yrange=None):
        """
        Calculate union of data ranges from all Craterplots
        Use to set default axis ranges

        xrange: optional forced range
        yrange: optional forced range

        :return: none
        """
        x0,x1,y0,y1=zip(*[cp.get_data_range(self) for cp in self.craterplot])
        mx = (.3, .8) # minimum empty margin
        my = [e * (2 if self.presentation=='differential' else 1) for e in [.3,.3]] # minimum empty margin
        min_x, max_x = np.log10(min(x0)), np.log10(max(x1))
        min_y, max_y = np.log10(min(y0)), np.log10(max(y1))
        xr = np.array([np.floor(min_x-mx[0]), np.ceil(max_x+mx[1])])
        yr = np.array([np.floor(np.log10(min(y0))-my[0]), np.ceil(np.log10(max(y1))+my[1])])

        if any([cp.cratercount.n_sigma and cp.type == 'data' for y, cp in zip(y1, self.craterplot)]): # plot n_sigma?
            yr[1] = max(yr[1], np.ceil(max_y + gm.mag(yr)*3/16))
            mg = gm.mag(yr)
            #self.ra_y_position = (max_y - yr[0] + mg*1.5/16) / mg
            self.max_y = max_y
            max_y += mg/8
            self.n_sigma_range = gm.range([float(e) for cp in self.craterplot if cp.cratercount.n_sigma and cp.type == 'data' for e in cp.cratercount.n_sigma['bin']])
            self.measures = sorted({e for cp in self.craterplot if cp.cratercount.n_sigma and cp.type == 'data' for e in cp.cratercount.n_sigma.keys()} - {'bin'})

        big_left = min_x - xr[0] + mx[0] > xr[1] - max_x + mx[1] #still want biassed to left
        big_bottom = min_y - yr[0] > yr[1] - max_y

        #optimal padding should consider margins mx, my as well
        dx,dy= gm.mag(xr), gm.mag(yr)
        if np.isnan(dx): #only empty crater files
            xr=yr=np.array([-2.,0.])
        elif self.presentation == 'differential':
            if dy/2.-np.floor(dy/2.) > .01: yr+=[-1,0]
            dy= gm.mag(yr)
            d=dy/2-dx
            d0=abs(d)
            d2a=int(d0/2)
            d2b=d0-d2a
            if d<0: yr+=np.array([-d2a,d2b])*2 if big_bottom else np.array([-d2b,d2a])*2
            if d>0: xr+=np.array([-d2a,d2b]) if big_left else np.array([-d2b,d2a])
        else:
            d=dy-dx
            d0=abs(d)
            d2a=int(d0/2)
            d2b=d0-d2a
            if d < 0: yr += [-d2a,d2b] if big_bottom else [-d2b,d2a]
            if d > 0: xr += [-d2a,d2b] if big_left else [-d2b,d2a]

        self.xrange = xr if xrange is None else np.array(xrange,dtype=float)
        self.yrange = yr if yrange is None else np.array(yrange,dtype=float)

    def create_summary_table(self,f_out=None):
        """
        :return: Output ascii table of Craterplot age calculations

        """
        s=[]
        for cp in self.craterplot:
            if cp.type in ['c-fit', 'd-fit', 'poisson', 'b-poisson']:
                cp.calculate_age(self)
                d = {k: getattr(cp, k, None) for k in
                      {'name', 'binning', 'range', 'bin_range', 'resurf', 'type', 'source', 'n', 'n_event', 't','a0','n_d'}}
                d.update({k: getattr(cp.cratercount, k, None) for k in {'area'} })
                s+=[d]

        if not s: return

        n_d_lbl=f'N({self.ref_diameter:0g})'
        # w now obsolete in this table (width)
        table = (('name', '24', '', None),
                 ('area', '8', '.5g', None),
                 ('binning', '>10', '', None),
                 ('bin_range' if d['type'] in ('c-fit','d-fit') and d['resurf'] != 1 else 'range', '5', '.2g', ('d_min', 'd_max')),
                 ('type', '>9', '', ('Method',)),
                 ('resurf', '6', '', None),
                 ('n', '7', '', None),
                 ('n_event', '9', '', None),
                 ('t', '7', '.3g', ('Age','Age-','Age+')),
                 ('a0', '6', '.4g', ('a0','a0-','a0+')),
                 ('n_d', '8', '.2e', (n_d_lbl,n_d_lbl+'-',n_d_lbl+'+')),
                 ('source', '', '', None),
                 (' ', '', '', None),
                 ('Range', '', '', None),
                 ('MathML', '', '', ('Age', n_d_lbl)),
                 ('Latex', '', '', ('Age',n_d_lbl)),
                 )

        ln = []
        for k, w, f, t in table:
            if t is not None:
                ln += list(t)
            else:
                ln += [k[:1].upper() + k[1:]]
        st = ','.join(ln)

        for d in s:
            ln=[]
            for k,w,f,_ in table:
                if k=='name' and d[k]=='':
                    d[k]= gm.filename(d['source'], 'n')
                if k in ('range','bin_range','t','a0'):
                    v = ','.join([f"{e:{f}}" for e in d[k]])
                    if k in ('range','bin_range'):
                        txt_range=gm.diameter_range(d[k])
                elif k=='n_d':
                    v = ','.join([f"{10**e:{f}}" for e in d['a0']])
                elif k in ('Latex','MathML'):
                    t = d['t']
                    v0 = cst.str_age(t[0], t[2] - t[0], t[0] - t[1], mu=self.mu, MathML = k=='MathML')
                    a0 = d['a0']
                    v1 = gm.scientific_notation(10**a0[0],10**a0[2],10**a0[1], unit='km-2', MathML = k=='MathML')
                    v=v0+','+v1
                elif k==' ':v=' '
                elif k == 'Range':
                    v=txt_range
                else:
                    v = f"{d[k]:{f}}"
                ln+=[v]
            st += '\n'+','.join(ln)+'," "'

        st = (',,,,,,,,,,,,,,,,,,,,Formatted values [paste MathML into Word using CTRL-SHIFT-V]\n'
              ',,,,,,,,,,,,,,,,,,,,,MathML,,Latex,\n'
              )+st

        if f_out:
            try:
                gm.write_textfile(f_out, st, BOM=True)  # excel misreads long dash if no BOM
            except:
                sys.exit(gm.bright("Unable to write file: ") + f_out)

        return st #for test routine

    def create_sequence_table(self,f_csv):
        """
        Output table of sequence probabilities from sequence plot

        :f_csv: filepath for csv output
        :return: sequence table
        """

        # calculate sequence table
        show_self_comparison = False
        cpl = [e for e in self.craterplot if e.type in ['poisson','buffered-poisson'] and not e.hide]
        n = len(cpl)
        if n<2: return
        s=[['' for i in range(n+1)] for j in range(n+1)]

        for i in range(n):
            cpl[i].calculate_age(self)
            s[i][0]=cpl[i].name

        for i in range(n):
            for j in range(i if show_self_comparison else i+1,n):
                P = cpl[i].pdf.calculate_sequence_probability(cpl[j].pdf)
                s[i][j+1] = gm.sigfigs(1.-P,2)
                s[j][i+1] = gm.sigfigs(P,2)

        st='Table of probability that t(x)>t(y)\n'+'\n'.join([','+','.join([cpl[i].name for i in range(n)])]+[','.join(e) for e in s])

        # calculate probability of simultaneous formation vs median time formation

        t = [cp.pdf.t(0.5) for cp in cpl]
        t_mean= sum(t)/float(n)

        st += '\nt_median:,'+','.join([f'{tt:.3g}' for tt in t])
        st += '\nmean(t_median):,'+f'{t_mean:.4g}'

        # second calculation of same

        lam_ratio = [self.cf.N1(tt)/self.cf.N1(t_mean) for tt,cp in zip(t,cpl)]
        pdf2 = [cst.Craterpdf(self.pf,self.cf,cp.cratercount,cp.range,k=cp.pdf.k,lam=cp.pdf.lam*lr) for lr,cp in zip(lam_ratio,cpl)]

        # combined pdf

        pdf3 = copy.deepcopy(pdf2[0])
        pdf3.pdf = np.product([e.pdf for e in pdf2],0)

        rel_probs =  [e.relative_probability(t0) for e,t0 in zip(pdf2,t)]
        compound_prob = np.product(rel_probs)

        worse = np.where(pdf3.pdf < compound_prob, pdf3.dt * pdf3.pdf, 0)
        prob_worse = sum(worse)/sum(pdf3.dt * pdf3.pdf)

        st += ('\n\nProbability of more distant time configuration than observed if all surfaces formed at t_mean:\n,'
               +f'{prob_worse:g}' )

        try:
            gm.write_textfile(f_csv,st)
        except:
            sys.exit(gm.bright("Unable to write file: ")+f_csv)

    def age_area_plot(self,plt):
        # import warnings
        # warnings.filterwarnings('error', category=RuntimeWarning)

        cmap_k = 'Set2_r'
        cmap_err = Spectral_9.mpl_colormap
        cmap_ratio = colors.ListedColormap(Spectral_9.mpl_colors)

        # new initialisation
        dmin = self.min_diameter
        max_area=self.global_area

        if self.aspect_ratio>1:
            nsx = self.n_samples  # samples for plotting
            nsy = int(nsx*self.aspect_ratio)
        else:
            nsy = self.n_samples
            nsx = int(nsy/self.aspect_ratio)

        ns_lin = round(nsx*self.xfrac_linear)
        ns_log = nsx - ns_lin

        log_age_range = [np.log10(self.t_min), np.log10(self.t_crossover)]
        log_age = np.concatenate((
            np.linspace(log_age_range[0], log_age_range[1], ns_log),
            np.log10(np.linspace(self.t_crossover, self.t_max, ns_lin+1)[1:])
            ))

        log_area_range = self.yrange
        log_area = np.linspace(log_area_range[0], log_area_range[1], nsy)

        d_range = [dmin, 1000.]
        cc = cst.Cratercount()
        mid_d = np.sqrt(d_range[0] * d_range[1])
        cc.diam = [mid_d]  # shouldn't be empty

        if not hasattr(self, 'age_area'): #store values first time, else retrieve
            zz = np.zeros((nsx,nsy))
            kk = np.zeros((nsx,nsy))
            ee = np.zeros((nsx, nsy))
            lm = np.zeros((nsx, nsy))

            a0 = self.cf.a0(10 ** log_age)
            C = np.ndarray(nsx)

            for i,a in enumerate(a0):
                r=self.pf.evaluate("cumulative",d_range,a0=a)
                C[i]=r[0]-r[1]

            for i,xx in progressbar(enumerate(log_age),max_value=nsx):
                for j,yy in enumerate(log_area):
                    area=10**yy
                    lam=C[i]*area
                    k=np.random.poisson(lam) if lam < 1e5 else int(lam)  # prevent too large lam
                    cc.area=area
                    pdf = cst.Craterpdf(self.pf, self.cf, cc, d_range, k=k, bcc=False,n_samples=2000)
                    t = pdf.median1sigma()
                    err = np.sqrt(t[2]/t[1]) - 1.
                    ratio=t[0]/(10**xx)

                    zz[i,j]=0 if np.isnan(err) else err  # clear underflow errors
                    kk[i,j]=k
                    ee[i,j]=1 if np.isnan(ratio) else ratio
                    lm[i,j]=lam

            self.age_area=(zz,kk,ee,lm)
        else:
            zz, kk, ee, lm = self.age_area

        x_exceed = y_exceed = None

        if np.searchsorted(log_area_range,np.log10(max_area)) == 1:
            y_exceed = (np.log10(max_area) - log_area_range[0])/gm.mag(log_area_range)
            p = [[0, y_exceed], [1, y_exceed], [1, 1], [0, 1]]

        if self.ef:
            C_ef_dmin = self.ef.evaluate("cumulative",dmin)
            C = self.pf.evaluate("cumulative",[dmin,1.])
            T_eq = self.cf.t(n1=C_ef_dmin * C[1]/C[0])

            match np.searchsorted([self.t_min,self.t_crossover,self.t_max],T_eq):
                case 1:
                    x_exceed = (self.xfrac_linear + (1 - self.xfrac_linear) *
                                (np.log10(self.t_crossover) - np.log10(T_eq)) /
                                (np.log10(self.t_crossover) - np.log10(self.t_min)))
                case 2:
                    x_exceed = (self.xfrac_linear *
                                (self.t_max - T_eq) / (self.t_max - self.t_crossover))
                case _:
                    pass

            if x_exceed:
                p = [[0,0],[x_exceed, 0], [x_exceed, 1], [0, 1]]

        if x_exceed and y_exceed:
            p = [[0,0],[x_exceed,0],[x_exceed,y_exceed],[1,y_exceed],[1,1],[0,1]]
        if x_exceed or y_exceed:
            poly = Polygon(p, closed=True, facecolor='white', edgecolor=None, alpha=0.6)

        # print(f'T_eq {T_eq}, t_max {self.t_max}, t_cross {self.t_crossover}, t_min {self.t_min}\n'
        #       f'xfraclin {self.xfrac_linear}, x_exceed {x_exceed}')

        if plt=='k':
            im = np.flip(np.transpose(np.clip(kk, 0, 8)), 1)
            imo = self.ax.imshow(im, cmap_k, origin="lower", interpolation='none', alpha=None, aspect='auto',extent=[0,1,0,1])
            cbar = self.fig.colorbar(imo,self.ax_cbar,ticks=[0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5])
            cbar.ax.set_yticklabels(['0','1','2','3','4','5','6','7+'])
            cbar.set_label('$k$', rotation=90)

        elif plt=='err':
            imo = self.ax.imshow(np.flip(np.transpose(zz),1) * 100, cmap_err, origin="lower", interpolation='none',alpha=None,
                             aspect='auto', vmin=0,extent=[0,1,0,1]) #, vmax=115)#, 'plasma_r' extent=[0,ns-1,0,nsy-1]
            cbar = self.fig.colorbar(imo,self.ax_cbar)
            cbar.set_label(r'Measured uncertainty $\sigma$, %', rotation=90)

        elif plt == 'age':
            im = np.flip(np.transpose(np.log10(ee)),1)
            vmin=np.log10(1./5)
            vmax=np.log10(5.)
            # svg output does not respect alpha; both png and svg respect np.nan
            im=np.where((im > vmin) & (im < vmax),im,np.nan)
            imo = self.ax.imshow(im,
                           cmap_ratio, origin="lower", interpolation='none', #zorder=0,
                           extent=[0,1,0,1],aspect='auto', vmin=vmin,vmax=vmax)
            cbar = self.fig.colorbar(imo,self.ax_cbar,ticks=[np.log10(e) for e in [.1,.2,1/3.,.5,1./1.4,1.,1.4,2.,3.,5.,10.]])
            cbar.ax.set_yticklabels(['0.1', '.2', '.33', '.5','.7', '1', '1.4', '2', '3', '5','10'])
            cbar.set_label('Measured/actual age', rotation=90)
            poly.set_alpha(0.7)

        def add_saturation_text():
            if y_exceed and (y_exceed < .98):
                self.ax.text(.82, y_exceed , 'whole globe', size=self.scaled_pt_size * .7, rotation=0,
                        transform=self.ax.transAxes, horizontalalignment='right', verticalalignment='bottom')
            if self.ef:
                if x_exceed and (x_exceed > .02):
                    self.ax.text(x_exceed, .87, 'saturation', size=self.scaled_pt_size * .7, rotation=90,
                                 horizontalalignment='right', verticalalignment='top')

        def add_diameter_text():
            self.fig.text(0.03, .96, '$d > ' + (f'{dmin:0.3g}$ km' if dmin >= 1 else f'{dmin*1000:0.3g}$ m'),
                     size=self.scaled_pt_size * .8, transform=self.ax.transAxes, horizontalalignment='left', verticalalignment='top')

        if x_exceed or y_exceed:
            self.ax.add_patch(poly)
        add_saturation_text()
        add_diameter_text()


    def create_map_plotspace(self):
        """
        Set up plotspace for Spatialcount map
        """
        if self.fig: del self.fig
        self.EstablishFontandScaling()

        # set up plot dimensions
        margin = self.pt_size * .2  # plot margin in cm
        plot_dims = [float(e) for e in self.print_dimensions.split('x')]
        if len(plot_dims) == 1:
            xsize = ysize = 5 * plot_dims[0] + 2 * margin
            self.aspect_ratio=1
        else:
            xsize, ysize = (e + 2 * margin for e in plot_dims)
            self.aspect_ratio = plot_dims[1]/plot_dims[0]

        self.position = margin * np.array([1, 1, xsize / margin - 2, ysize / margin - 2])  # cm
        normalised_position = self.position / np.array([xsize, ysize, xsize, ysize])

        self.fig = mfig.Figure(figsize=[xsize * self.cm2inch, ysize * self.cm2inch], dpi=500)
        self.ax = self.fig.add_axes(normalised_position)

        if self.title:
            self.ax.set_title('\n'.join(self.title.split('|')) )

