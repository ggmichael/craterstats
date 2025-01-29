#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.
import copy

import numpy as np
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.figure as mfig
from matplotlib import patheffects

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
            'title':'',
            'presentation':'differential',
            'xrange':[-3,2],
            'yrange':[-5,5],
            'style':'natural',
            'isochrons':'',
            'show_isochrons':0,
            'legend_data':'a', # a show counting area
            'legend_fit':'r', # n - show N(d_ref); r - show diam range
            'print_dimensions':'7.5x7.5',
            'pt_size':9.,
            'ref_diameter':1.,
            'cite_functions':1,
            'sig_figs':3,
            'randomness':0,
            'mu':1,
            'invert':0,
            'show_title':1,
            },*args,kwargs)

        self.sz_ratio= self.pt_size / 9.
        self.grey = cst.GREYS[self.invert]
        self.palette = [e[self.invert] for e in cst.PALETTE]

        
    def UpdateSettings(self,*args,**kwargs): #pass either dictionary or keywords
        a = {k: v for d in args for k, v in d.items()}
        a.update(**kwargs)
        for k, v in a.items():
            #if k == 'source': self.cratercount = cst.Cratercount(v)
            if k in ('xrange','yrange'): v=[float(e) for e in v]
            if k in ('pt_size','ref_diameter'): v = float(v)
            if k in ('show_isochrons',
                    'cite_functions',
                    'randomness',
                    'mu',
                    'invert',
                    'show_title',
                    'sig_figs',
                     ):
                v = int(v)
            setattr(self, k, v)


    def EstablishFontandScaling(self):
        # set up font and scaled font size

        plt.style.use(('default', 'dark_background')[self.invert])

        desired_font = ['Myriad Pro', 'Verdana', 'DejaVu Sans', 'Tahoma']  # in order of preference
        available_font = gm.mpl_check_font(desired_font)
        scale_factor = {'Myriad Pro': 1.,
                       'Verdana': .83,
                       'DejaVu Sans': .83,
                       'Tahoma': .93,
                       }[available_font]
        self.scaled_pt_size = self.pt_size * scale_factor

        plt.rc('font', family=available_font, size=self.scaled_pt_size)
        plt.rc('mathtext', fontset='custom', rm=available_font, bf=available_font + ':bold',
              cal=available_font + ':italic')

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
        self.marker_def = [e[2].copy() for e in cst.MARKERS]
        f = self.decades[0]*self.print_scale/7.5
        for e in self.marker_def:
            e['markersize'] *= 0.8 * f # * self.print_scale/1.875
            e['markeredgewidth'] = .5 * f # * self.print_scale/1.875

# set up titles, tick marks, and tick labels

        nonroot2=False in [cp.binning=='root-2' for cp in self.craterplot]

        xtitle="Age, Ga" if self.presentation in ['chronology', 'rate'] else 'Diameter'
        ytitle={
            'cumulative':   'Cumulative crater density, km$^{-2}$',           
            'differential': 'Differential crater density, km$^{-3}$',
            'R-plot': 'Relative crater density (R)',
            'Hartmann':     'Craters per √2-bin'+(' (equivalent)' if nonroot2 else '')+', km$^{-2}$',
            'chronology':   'Cumulative crater density N(>'+format(self.ref_diameter,'.0f')+' km), km$^{-2}$',
            'rate':         'Crater formation rate N(>'+format(self.ref_diameter,'.0f')+' km), km$^{-2}$ Ga$^{-1}$',
            }[self.presentation]
        
        title = ('\n'.join(self.title.split('|')) if self.show_title else None)

        xminor=xmajor=xtickv=None
        add_xminorlogticks=False

 
        if self.presentation in ['chronology', 'rate']:
            xminor, xmajor = .5, 1
        else:
            if self.style=='root-2' or self.presentation=='Hartmann':                
                v=[np.log10(2.**e) for e in range(-10,11)] #set up root-2/hartmann axis labels
                labels=[str(e) for e in
                        (1, 2, 4, 8, 16, 31, 63, 125, 250, 500, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)]
                labels[10]='  '+labels[10]+"km"
                xtickv,xtickname = map(list,zip(*[(val,txt) for val,txt in zip(v,labels) if val>=self.xrange[0] and val<=self.xrange[1]]))
                if xtickv[0]<0: xtickname[0]+='m'
                xminor=(xtickv[1]-xtickv[0])/2
                plt.rcParams.update({'xtick.labelsize':self.scaled_pt_size*.75})
                
            elif self.style=='natural':                
                v=np.arange(np.ceil(self.xrange[0]),np.floor(self.xrange[1])+1).tolist()
                xtickname=[format(10**e,'0g')+'$\,$km' if e>=0 else format(10**(e+3),'0g')+'$\,$m' for e in v]
                xtickv=v
                add_xminorlogticks=True

#create layout

        fig = mfig.Figure(figsize=[xsize*self.cm2inch,ysize*self.cm2inch],dpi=200) # bypass pyplot figure manager (causes issues, and not needed for non-interactive)

        ax=fig.add_axes(normalised_position)
        ax.set_axisbelow(False) # draw axis on top of other elements
        
        if add_xminorlogticks:                      #draw minor xlog ticks using different axes, since main x axis is linear
            ax2=fig.add_axes(normalised_position,frameon=False)
            ax2.set_axisbelow(False)
            ax2.set_xscale('log')      
            ax2.set_xbound(lower=10**self.xrange[0], upper=10**self.xrange[1])  
            ax2.tick_params(axis='x',which='minor',direction="in",length=self.pt_size*.25, top=True)
            ax2.tick_params(axis='x',which='major', bottom=False,labelbottom=False)
            ax2.get_yaxis().set_visible(False)            
                    
        ax.set_yscale('log')                                             #don't use xlog scale - awful to set up ticks for Hartmann binning
        ax.set_ylim(bottom=10**self.yrange[0], top=10**self.yrange[1])   #nb craterstats2 used linear for both axes
  
        ax.set_xlim(left=self.xrange[0], right=self.xrange[1])
        
        ax.tick_params(axis='both',which='major',direction="in",length=self.pt_size*.5,right=True,top=True)
        ax.tick_params(axis='both',which='minor',direction="in",length=self.pt_size*.25,right=True,top=True)
 
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

        self.fig=fig
        self.ax=ax

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
        xsize, ysize = [float(e)+2*margin for e in self.print_dimensions.split('x')]


        #self.position = margin * np.array([1, 1, xsize / margin - 2, ysize / margin - 2])  # cm

        def f(x): return np.clip(gm.mag(x), 1, None)
        self.decades=f(self.xrange),f(self.yrange)

        self.t_max = np.clip(max(self.xrange), 1e-8, 4.5)
        self.t_min = np.clip(min(self.xrange), 0., 3.5)

        if self.t_min<1 and self.t_min !=0:
            self.t_min=10**np.floor(np.log10(self.t_min))
            self.crossover = True
        else:
            self.crossover = False


        if self.crossover:
            t_crossover = 3.
            log_t_min = np.log10(self.t_min)

            dec2lin = 0.7
            lin_units = max(self.t_max - t_crossover, 0) / dec2lin
            log_units = np.log10(t_crossover) - log_t_min

            xtickv = [3., 3.5, 4.]

        else:
            t_crossover = self.t_min
            lin_units = 1
            log_units = 0
            xtickv = [e/2. for e in range(0,10) if self.t_min <= e/2. <= self.t_max]

        xticklabels = [str(e) for e in xtickv]
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

        if self.presentation == 'uncertainty':
            offset_cbar = [.3, .3]  # offset_x,w from main plot
            pos_cbar = [xsize - margin + offset_cbar[0], margin, offset_cbar[1], ysize - margin*2]
            ax_cbar = fig.add_axes(pos_cbar / np.array([xsize, ysize, xsize, ysize]))

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

            ax_log.plot(t_crossover,0,marker='x',clip_on=False,markeredgewidth=.3, markersize=self.pt_size*.3,color='black')
        else:
            ax_log.set_axis_off()


        #ax_lin
        ax_lin.set_xlim(left=self.t_max, right=t_crossover)
        ax_lin.set_ylim(bottom=0, top=1)


        ax_lin.set_xticks(xtickv, labels=xticklabels)
        ax_lin.tick_params(length=2, pad=1.5)
        ax_lin.tick_params(which='minor',length=1)
        ax_lin.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))

        ax_lin.get_yaxis().set_visible(False)
        ax_lin.spines[['left', 'right', 'top']].set_visible(False)

        #ax_all
        ax.set_xlim(left=0, right=1)
        ax.get_xaxis().set_visible(False)
        if self.presentation == 'sequence':
            ax.set_ylim(bottom=0, top=1)
            ax.get_yaxis().set_visible(False)
            ax.spines[['left', 'right', 'top', 'bottom']].set_visible(False)
        elif self.presentation == 'uncertainty':
            ax.set_yscale('log')
            ax.set_ylim(bottom=10 ** self.yrange[0], top=10 ** self.yrange[1])
            ax.set_ylabel('Area, km$^2$')

        ax.patch.set_facecolor('none')
        title = '\n'.join(self.title.split('|')) if self.show_title else None
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

        if self.cite_functions:
            txt=''
            if self.ep: txt += "Epochs: " + self.ep.name + '\n'
            if self.ef and self.presentation not in ['sequence']: txt += "EF: " + self.ef.name + '\n'
            if not (self.presentation in ['chronology', 'rate'] and self.ref_diameter==1) or self.ep: txt += "PF: " + self.pf.name + '\n'
            txt += "CF: " + self.cf.name
            #offset would be better specified in pts (1.5 * fontsize) [for many-decade plots]:
            text=self.ax.text(.05, .05, txt, transform=self.ax.transAxes, fontsize=self.scaled_pt_size * .7, linespacing=1.5)
            text.set_path_effects([patheffects.withStroke(linewidth=self.sz_ratio, foreground='black' if self.invert else 'white',alpha=0.7)])  # White shadow beneath text

        if self.presentation in ['chronology', 'rate']:
            phi=self.presentation=='rate'
            if self.ep:
                self.ep.chronology_oplot(self,phi=phi)
            t,y=self.cf.getplotdata(linear=True,phi=phi)

            if self.ref_diameter != 1.:  # only show legend if not N(1)
                self.ax.plot(t, y * ref_diam_ratio, label='N(>{:g} km)'.format(self.ref_diameter),
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

            if self.show_isochrons and self.isochrons:
                self.plot_isochrons()

        if self.presentation == 'sequence' and self.ep: self.ep.sequence_oplot(self)

        if self.presentation == 'uncertainty':
            pass

        if self.presentation in ['cumulative', 'differential', 'R-plot', 'Hartmann', 'sequence']:
            for cp in self.craterplot:
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

        legend=self.ax.legend(h1,b1,frameon=False, loc='upper right', borderaxespad=1,handletextpad=0.5,labelspacing=.4,handlelength=1.5)
        for item in legend.get_texts(): #inverted shadow for improved contrast
            item.set_path_effects(
                [patheffects.withStroke(linewidth=self.sz_ratio, foreground='black' if self.invert else 'white', alpha=0.7)])

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

            q = gm.where(np.abs(np.log10(iso['y']) - (self.yrange[1] - .1)) < .1)
            if not q or (d10[q[0]] < self.xrange[0]):  # (d10[q[0][0]] < self.xrange[0]):
                q= gm.where(abs(d10 - np.max([self.xrange[0] + .15, d10[0]])) < .1)

            if q and not hide:
                sx = np.mean(d10[q])
                sy = np.log10(self.pf.evaluate(self.presentation, 10**sx, a0))-.05
                y_factor = self.data_aspect
                th = np.rad2deg(np.arctan2(np.log10(self.pf.evaluate(self.presentation, 10**(sx + .3), a0))-sy, .3 * y_factor))

                self.ax.text(sx, 10 ** sy, cst.str_age(t, simple=True),
                             color=self.grey[0], size=self.scaled_pt_size*(.5 if small else .7),
                             rotation=th, rotation_mode='anchor',
                             verticalalignment='bottom' if above else 'top',
                             horizontalalignment='left',
                             bbox=dict(facecolor='none', edgecolor='none', boxstyle='square,pad=0.5'))

    def autoscale(self,xrange=None,yrange=None):
        """
        Calculate union of data ranges from all Craterplots
        Use to set default axis ranges

        xrange: optional forced range
        yrange: optional forced range

        :return: none
        """
        x0,x1,y0,y1=zip(*[cp.get_data_range(self) for cp in self.craterplot])
        mx = (.5, .9) # minimum empty margin
        my = [e * (2 if self.presentation=='differential' else 1) for e in [.3,.7]] # minimum empty margin
        xr = np.array([np.floor(np.log10(min(x0))-mx[0]), np.ceil(np.log10(max(x1))+mx[1])])
        yr = np.array([np.floor(np.log10(min(y0))-my[0]), np.ceil(np.log10(max(y1))+my[1])])

        #set to square (better to add padding on side with least space)
        #optimal padding should consider margins mx, my as well
        dx,dy= gm.mag(xr), gm.mag(yr)
        if self.presentation == 'differential':
            if dy/2.-np.floor(dy/2.) > .01: yr+=[-1,0]
            dy= gm.mag(yr)
            d=dy/2-dx
            d0=abs(d)
            d2a=int(d0/2)
            d2b=d0-d2a
            if d<0: yr+=np.array([-d2b,d2a])*2
            if d>0: xr+=np.array([-d2b,d2a])
        else:
            d=dy-dx
            d0=abs(d)
            d2a=int(d0/2)
            d2b=d0-d2a
            if d < 0: yr += [-d2a,d2b]
            if d > 0: xr += [-d2a,d2b]

        self.xrange = xr if xrange is None else np.array(xrange,dtype=float)
        self.yrange = yr if yrange is None else np.array(yrange,dtype=float)

    def create_summary_table(self,f_out=None):
        """
        Output table of Craterplot age calculations to stdout

        :return: none
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

        n_d_lbl='N({:0g})'.format(self.ref_diameter)
        # w now obsolete in this table (width)
        table = (('name', '24', '', None),
                 ('area', '8', '.5g', None),
                 ('binning', '>10', '', None),
                 ('bin_range' if d['type'] in ('c-fit','d-fit') else 'range', '5', '.2g', ('d_min', 'd_max')),
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
                    v=','.join([('{:'+f+'}').format(e) for e in d[k]])
                    if k in ('range','bin_range'):
                        txt_range=gm.diameter_range(d[k])
                elif k=='n_d':
                    v = ','.join([('{:' + f + '}').format(10**e) for e in d['a0']])
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
                    v=('{:'+f+'}').format(d[k])
                ln+=[v]
            st += '\n'+','.join(ln)+'," "'

        st = (',,,,,,,,,,,,,,,,,,,,Formatted values [paste MathML into Word using CTRL-SHIFT-V]\n'
              ',,,,,,,,,,,,,,,,,,,,,MathML,,Latex,\n'
              )+st

        if f_out:
            try:
                gm.write_textfile(f_out, st)
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

        st += '\nt_median:,'+','.join(['{0:.3g}'.format(tt) for tt in t])
        st += '\nmean(t_median):,'+'{0:.4g}'.format(t_mean)

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
               +'{0:g}'.format(prob_worse) )

        try:
            gm.write_textfile(f_csv,st)
        except:
            sys.exit(gm.bright("Unable to write file: ")+f_csv)

    def age_area_plot(self):
        #,pf,cf,out,min_diameters,min_areas,sample_plot_index=-1,max_area=3.8e7,cs_label=False,dark=False):

        log_t_min=-5
        t_crossover=3.
        t_max=4.2
        xfrac_linear = 0.3
        ns = 300  # samples for plotting
        area_decades=6 #6

        t_sample = 0.1
        n_samples=6
        sample_plot_labels='ghijklmn'

        cm2inch=1/2.54
        xsize=18
        ysize=10
        nsy=ns*ysize//xsize

        p={}
        pack=['log_t_min','t_crossover','t_max','xfrac_linear','cm2inch','xsize','ysize','dark']
        for e in pack:
            p[e]=eval(e)


        ns_lin = round(ns*xfrac_linear)
        ns_log = ns - ns_lin

        log_age_range = [log_t_min, np.log10(t_crossover)]

        log_age = np.concatenate((
            np.linspace(log_age_range[0], log_age_range[1], ns_log),
            np.log10(np.linspace(t_crossover, t_max, ns_lin+1)[1:])
            ))


        x_sample=(ns-1)-np.interp(np.log10(t_sample),log_age,range(ns))
        y_sample = np.linspace(0, nsy, n_samples+2, dtype='int32')[1:n_samples+1]


        for di, dmin in enumerate(min_diameters):  # ,0,1

            log_area_range = [min_areas[di], min_areas[di] + area_decades]
            log_area = np.linspace(log_area_range[0], log_area_range[1], nsy)
            p['log_area_range']=log_area_range

            d_range = [10 ** dmin, 1000.]
            cc = cst.Cratercount()
            mid_d = np.sqrt(d_range[0] * d_range[1])
            cc.diam = [mid_d]  # shouldn't be empty

            zz = np.zeros((ns,nsy))
            kk = np.zeros((ns,nsy))
            ee = np.zeros((ns, nsy))
            lm = np.zeros((ns, nsy))

            a0 = cf.a0(10 ** log_age)
            C = np.ndarray(ns)

            for i,a in enumerate(a0):
                r=pf.evaluate("cumulative",d_range,a0=a)
                C[i]=r[0]-r[1]

            if dark: plt.style.use("dark_background")
            fig,axs = plt.subplots(1,n_samples,  figsize=[xsize * 2 * cm2inch, ysize/3. * cm2inch], layout='constrained')
            axs = [e for e in axs.flat]

            for i,xx in enumerate(log_age):
                for j,yy in enumerate(log_area):
                    area=10**yy
                    lam=C[i]*area
                    k=round(lam)
                    k=np.random.poisson(lam) if lam < 1e5 else lam #prevent too large lam
                    cc.area=area
                    pdf = cst.Craterpdf(pf, cf, cc, d_range, k=k, bcc=False,n_samples=2000)
                    t = pdf.median1sigma()
                    #err=(t[2]-t[1])/t[0]/2.
                    err = np.sqrt(t[2]/t[1]) - 1.
                    ratio=t[0]/(10**xx)

                    zz[i,j]=0 if np.isnan(err) else err #clear underflow errors
                    kk[i,j]=k
                    ee[i,j]=1 if np.isnan(ratio) else ratio
                    lm[i,j]=lam

            if di == sample_plot_index:
                for jm in range(n_samples):
                    area = 10 ** log_area[y_sample[jm]]
                    a0 = cf.a0(t_sample)
                    r = pf.evaluate("cumulative", d_range, a0=a0)
                    C_sample = r[0] - r[1]
                    lam=C_sample * area
                    #k = round(lam)
                    k = round(np.median(np.random.poisson(lam,5))) if lam < 1e5 else round(lam) #show typical plots for explanation
                    cc.area = area
                    pdf = cst.Craterpdf(pf, cf, cc, d_range, k=k, bcc=False, n_samples=6000)
                    pdf.plot(axs[jm], logscale=True, t_range=[1e-3, 4.5],pt_size=12.,color='1' if dark else '0')
                    t = pdf.median1sigma()
                    t_txt = cst.str_age(t[0],t[2]-t[0],t[0]-t[1],unit="Ma")
                    axs[jm].text(0.03, .25, f'$k={k:0g}$\n{t_txt}',transform=axs[jm].transAxes, size=10.)
                    axs[jm].text(0,.75,sample_plot_labels[jm],transform=axs[jm].transAxes,size=16.)



            id=f'{di:02d} {10.**dmin:0g}km '
            if di == sample_plot_index:
                fig.savefig(out+'4'+id + ' multi.png', dpi=500)

            #saturation calculation
            log_b = np.tile(log_area, (ns, 1))
            log_a = np.log10(lm*np.pi/4)+2*dmin
            alpha = np.where(np.isnan(log_a), 1., 1. - (log_a > log_b)*.2 - (log_a > (log_b - 1))*.4)
            alpha = np.where(log_b > np.log10(max_area), 0.4, alpha)
            alpha_s = np.flip(np.transpose(alpha), 1)
            q1 = np.where(log_a[:, 0] > (log_b[:, 0] - 1))
            q2 = np.where(log_a[:, 0] > (log_b[:, 0]))
            q3 = np.where(np.log10(max_area) < log_b[0,:])
            def add_saturation_text():
                if q1[0].size > 0 and (q1[0][0]/ns < .98):
                    ax.text(1 - q1[0][0]/ns , .87, '10% saturation', size=9., rotation=90,
                            transform=ax.transAxes, horizontalalignment='right', verticalalignment='top')
                if q2[0].size > 0 and (q2[0][0]/ns < .98):
                    ax.text(1 - q2[0][0]/ns , .87, '100% saturation', size=9., rotation=90,
                            transform=ax.transAxes, horizontalalignment='right', verticalalignment='top')
                if q3[0].size > 0 and (q3[0][0]/nsy < .98):
                    ax.text(.82, q3[0][0]/nsy , 'whole globe', size=9., rotation=0,
                            transform=ax.transAxes, horizontalalignment='right', verticalalignment='bottom')

            def add_diameter_text():
                fig.text(0.03, .96, '$d > ' + (f'{10. ** dmin:0g}$ km' if dmin >= 0 else f'{10. ** (dmin + 3):0g}$ m'),
                         size=10., transform=ax.transAxes, horizontalalignment='left', verticalalignment='top')

            def add_cs_text():
                fig.text(0.97, .04, 'PF: '+pf.name+'\nCF: '+cf.name, size=9., transform = ax.transAxes,
                         horizontalalignment='right', verticalalignment='bottom')

            def add_sample_markers(invert=None):
                if di == sample_plot_index:
                    for i in range(n_samples):
                        if dark and invert is not None:
                            if invert[i]==1: plt.style.use("default")

                        ax.text(x_sample, y_sample[i], r"$" + sample_plot_labels[i] + "$", size=12, #c='black',
                                horizontalalignment='center', verticalalignment='center')

                        if dark: plt.style.use("dark_background")

            def add_subfig_label(n):
                fig.text(0.02, .89, 'abcdefghijklmno'[di*3+n], size=18.)



            fig,ax,cax = establish_linlog_fig(p)
            im = np.flip(np.transpose(np.clip(kk, 0, 8)), 1)
            im = ax.imshow(im, cmap_k, origin="lower", interpolation='none', alpha=alpha_s, aspect='auto')
            cbar = fig.colorbar(im,cax,ticks=[0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5])
            cbar.ax.set_yticklabels(['0','1','2','3','4','5','6','7+'])
            cbar.set_label('$k$', rotation=90)
            if di == sample_plot_index: add_sample_markers()
            add_saturation_text()
            add_diameter_text()
            if cs_label: add_cs_text()
            add_subfig_label(0)
            fig.savefig(out+'1'+id+ ' k.png', dpi=500)

            fig,ax,cax = establish_linlog_fig(p)
            im = ax.imshow(np.flip(np.transpose(zz),1) * 100, cmap_err, origin="lower", interpolation='none',alpha=0.8*alpha_s,
                             extent=[0,ns-1,0,nsy-1],aspect='auto', vmin=0) #, vmax=115)#, 'plasma_r'
            cbar = fig.colorbar(im,cax)
            cbar.set_label('Measured uncertainty $\sigma$, %', rotation=90)
            if di == sample_plot_index: add_sample_markers()
            add_saturation_text()
            add_diameter_text()
            if cs_label: add_cs_text()
            add_subfig_label(1)
            fig.savefig(out+'2'+id + ' err.png', dpi=500)


            fig,ax,cax = establish_linlog_fig(p)
            im = np.flip(np.transpose(np.log10(ee)),1)
            vmin=np.log10(1./5)
            vmax=np.log10(5.)
            alpha=np.where((im > vmin) & (im < vmax),1.,0.)
            im = ax.imshow(im,
                           cmap_ratio, origin="lower", interpolation='none',  #'Spectral'
                           extent=[0,ns-1,0,nsy-1],aspect='auto', vmin=vmin,vmax=vmax,alpha=alpha*alpha_s)#, 'plasma_r'
            cbar = fig.colorbar(im,cax,ticks=[np.log10(e) for e in [.1,.2,1/3.,.5,1./1.4,1.,1.4,2.,3.,5.,10.]])
            cbar.ax.set_yticklabels(['0.1', '.2', '.33', '.5','.7', '1', '1.4', '2', '3', '5','10'])
            cbar.set_label('Measured/actual age', rotation=90)
            if di == sample_plot_index: add_sample_markers(invert=[0,1,1,1,1,1])
            add_saturation_text()
            add_diameter_text()
            if cs_label: add_cs_text()
            add_subfig_label(2)
            fig.savefig(out+'3'+id +' ratio.png', dpi=500)


