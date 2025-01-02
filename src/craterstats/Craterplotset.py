#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.figure as mfig

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
            'subtitle':'',
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
            'show_subtitle':1, 
            },*args,kwargs)

        self.sz_ratio= self.pt_size / 9.
        self.marker_def = [e[2].copy() for e in cst.MARKERS]
        for e in self.marker_def:
            e['markersize'] *= self.sz_ratio
            e['markeredgewidth'] = .5 * self.sz_ratio
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
                    'show_subtitle',
                    'sig_figs',
                     ):
                v = int(v)
            setattr(self, k, v)
        
            
    def CreatePlotSpace(self):
        """
        Set up plot dimensions, font and scaled font size, titles, tick marks, and tick labels
        Create layout
        Set up plot coordinate transformations

        """

        if self.fig: del self.fig
            
#set up plot dimensions
            
        self.time_plot=self.presentation in ['chronology','rate']
            
        def f(x): return np.clip(gm.mag(x), 1, None)
        self.decades=f(self.xrange),f(self.yrange)

        self.data_aspect=(
            2                                 if self.presentation=='differential' else
            self.decades[1]/self.decades[0]   if self.presentation=='Hartmann' or self.time_plot else
            1
            )            
            
        plot_dims=[float(e) for e in self.print_dimensions.split('x')]
        
        self.print_scale=(                                                      #in cm/decade
            np.clip(plot_dims[0],1,None) if len(plot_dims)==1 else
            plot_dims[0]/self.decades[0] if self.presentation=='Hartmann' else
            min(np.clip(plot_dims*np.array([1,self.data_aspect]),1,None)/self.decades)
            )
                
        randomness_plot=int(self.randomness and not self.time_plot) #boolean as 0,1
        margin=self.pt_size*.2  #plot margin in cm
        xsize=self.decades[0]*self.print_scale+2*margin #in cm

        ysize=(
            xsize+self.print_scale*randomness_plot  if self.presentation=='Hartmann' else
            xsize                                   if self.time_plot else
            (randomness_plot+self.decades[1]/self.data_aspect)*self.print_scale+2*margin
            )
              
        self.position=margin*np.array([1,1,xsize/margin-2,ysize/margin-2-randomness_plot]) #cm
        position_randomness=margin*np.array([1,ysize/margin-.8-randomness_plot,xsize/margin-2,ysize/margin-2]) #cm - not yet used
        normalised_position=self.position/np.array([xsize,ysize,xsize,ysize])  #pos, width for matplotlib axes

# set up font and scaled font size

        plt.style.use(('default', 'dark_background')[self.invert])

        desired_font=['Myriad Pro','Verdana','DejaVu Sans','Tahoma'] # in order of preference
        available_font= gm.mpl_check_font(desired_font)
        scale_factor = {'Myriad Pro':1.,
                        'Verdana':.83,
                        'DejaVu Sans':.83,
                        'Tahoma':.93,
                        }[available_font]
        self.scaled_pt_size=self.pt_size*scale_factor

        plt.rc('font', family=available_font, size = self.scaled_pt_size)
        plt.rc('mathtext', fontset ='custom', rm=available_font, bf=available_font+':bold', cal=available_font+':italic')

# set up titles, tick marks, and tick labels

        nonroot2=False in [cp.binning=='root-2' for cp in self.craterplot]

        xtitle="Age, Ga" if self.time_plot else 'Diameter'
        ytitle={
            'cumulative':   'Cumulative crater density, km$^{-2}$',           
            'differential': 'Differential crater density, km$^{-3}$',
            'R-plot': 'Relative crater density (R)',
            'Hartmann':     'Craters per √2-bin'+(' (equivalent)' if nonroot2 else '')+', km$^{-2}$',
            'chronology':   'Cumulative crater density N(>'+format(self.ref_diameter,'.0f')+' km), km$^{-2}$',
            'rate':         'Crater formation rate N(>'+format(self.ref_diameter,'.0f')+' km), km$^{-2}$ Ga$^{-1}$',
            }[self.presentation]
        
        title=(self.title if self.show_title else '') + ('\n'+self.subtitle if self.show_subtitle else '')

        xminor=xmajor=xtickv=None
        add_xminorlogticks=False
        xtick_labelsize='medium'
 
        if self.time_plot:
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
                xtick_labelsize=self.scaled_pt_size*.75
                
            elif self.style=='natural':                
                v=np.arange(np.ceil(self.xrange[0]),np.floor(self.xrange[1])+1).tolist()
                xtickname=[format(10**e,'0g')+'$\,$km' if e>=0 else format(10**(e+3),'0g')+'$\,$m' for e in v]
                xtickv=v
                add_xminorlogticks=True

#create layout

        tw=.4*self.sz_ratio
        plt.rcParams.update({
            'legend.fontsize':      'x-small',
            'legend.title_fontsize':'small',
            'axes.labelsize':       self.scaled_pt_size*.9,
            'axes.titlesize':       'small',
            'xtick.labelsize':      xtick_labelsize,
            'ytick.labelsize':      'medium',
            'axes.titlepad':        self.scaled_pt_size*1.,
            'axes.linewidth':tw,
            'xtick.major.width':tw,
            'xtick.minor.width':tw,
            'ytick.major.width':tw,
            'ytick.minor.width':tw,
        })


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
        
        if title not in ('','\n'):ax.set_title(title) #change when subtitle removed
        if ytitle != '':ax.set_xlabel(xtitle)
        if ytitle != '':ax.set_ylabel(ytitle)

        self.fig=fig
        self.ax=ax

# set up coordinate transformations
        a2d=ax.transAxes + ax.transData.inverted()
        self.axis_to_data = a2d.transform
        self.data_to_axis = a2d.inverted().transform
        self.axis_to_fig = (ax.transAxes + fig.transFigure.inverted()).transform
     


    def draw(self):
        """
        Draw plot, adding all specified items

        """

        self.CreatePlotSpace()

        N=self.pf.evaluate("cumulative",[self.ref_diameter,1.]) if self.pf else [1,1]
        ref_diam_ratio=N[0]/N[1]

        if self.cite_functions:
            txt=''
            if self.ep: txt += "Epochs: " + self.ep.name + '\n'
            if self.ef: txt += "EF: " + self.ef.name + '\n'
            if not (self.time_plot and self.ref_diameter==1) or self.ep: txt += "PF: " + self.pf.name + '\n'
            txt += "CF: " + self.cf.name
            #offset would be better specified in pts (1.5 * fontsize) [for many-decade plots]:
            self.ax.text(.05, .05, txt, transform=self.ax.transAxes, fontsize=self.scaled_pt_size * .7, linespacing=1.5)

        if self.time_plot:
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

        else:
            if self.ep: #overplot epochs
                self.ep.oplot(self)
            if self.ef:
                e = self.ef.getplotdata(self.presentation)
                self.ax.plot(np.log10(e['d']), e['y'], color=self.grey[0], lw=.7)

            if self.show_isochrons and self.isochrons:
                self.plot_isochrons()
            
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

        self.ax.legend(h1,b1,frameon=False, loc='upper right', borderaxespad=1,handletextpad=0.5,labelspacing=.4,handlelength=1.5)


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
        my = .7 * (2 if self.presentation=='differential' else 1) # minimum empty margin
        xr = np.array([np.floor(np.log10(min(x0))-mx[0]), np.ceil(np.log10(max(x1))+mx[1])])
        yr = np.array([np.floor(np.log10(min(y0))-my), np.ceil(np.log10(max(y1))+my)])

        #set to square
        dx,dy= gm.mag(xr), gm.mag(yr)
        if self.presentation == 'differential':
            if dy/2.-np.floor(dy/2.) > .01: yr+=[0,1]
            dy= gm.mag(yr)
            d=dy/2-dx
            d0=abs(d)
            d2a=int(d0/2)
            d2b=d0-d2a
            if d<0: yr+=np.array([-d2b,d2a])*2
            if d>0: xr+=np.array([-d2a,d2b])
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

        # w now obsolete in this table (width)
        table = (('name', '24', '', None),
                 ('area', '8', '.5g', None),
                 ('binning', '>10', '', None),
                 ('bin_range' if d['type'] in ('c-fit','d-fit') else 'range', '5', '.2g', ('d_min', 'd_max')),
                 ('type', '>9', '', ('method',)),
                 ('resurf', '6', '', None),
                 ('n', '7', '', None),
                 ('n_event', '9', '', None),
                 ('t', '7', '.3g', ('age','age-','age+')),
                 ('a0', '6', '.4g', ('a0','a0-','a0+')),
                 ('n_d', '8', '.2e', ('N({:0g})'.format(self.ref_diameter),)),
                 ('source', '', '', None),
                 ('Latex', '', '', None),
                 ('MathML', '', '', ["MathML [copy-paste into Word using 'paste as text' or CTRL-SHIFT-V]"]))

        ln = []
        for k, w, f, t in table:
            if t is not None:
                ln += list(t)
            else:
                ln += [k]
        st = ','.join(ln)

        for d in s:
            ln=[]
            for k,w,f,_ in table:
                if k=='name' and d[k]=='':
                    d[k]= gm.filename(d['source'], 'n')
                if k in ('range','bin_range','t','a0'):
                    v=','.join([('{:'+f+'}').format(e) for e in d[k]])
                elif k in ('Latex','MathML'):
                    a = d['t']
                    v = cst.str_age(a[0], a[0] - a[1], a[2] - a[0], mu=self.mu, MathML = k=='MathML')
                else:
                    v=('{:'+f+'}').format(d[k])
                ln+=[v]
            st += '\n'+','.join(ln)

        if f_out:
            try:
                gm.write_textfile(f_out, st)
            except:
                sys.exit(gm.bright("Unable to write file: ") + f_out)

        return st #for test routine








