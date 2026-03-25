#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import importlib.resources as importlib_resources

import numpy as np
import matplotlib.path as mpath
import craterstats.gm as gm
import craterstats as cst

PRESENTATIONS = ('cumulative', 'differential', 'R-plot', 'Hartmann', 'chronology', 'rate', 'sequence', 'uncertainty')
OPLOT_TYPES = ('data', 'differential-fit', 'cumulative-fit', 'poisson', 'buffered-poisson')
OPLOT_TYPES_SHORT = ('data', 'd-fit', 'c-fit', 'poisson', 'b-poisson')
CRATERPLOT_KEYS = ('source', 'name', 'range', 'snap', 'type', 'error_bars', 'hide', 'colour', 'psym', 'binning', 'age_left', 'show_age',
                   'resurf', 'resurf_showall', 'isochron', 'offset_age')

CARRY_OVER_PROPERTIES = ('source','psym','snap','isochron','error_bars','colour','binning') # not 'type' - only if 'source' too

DEFAULT_XRANGE0 = ((-3, 2), (-3, 2), (-2, 3), (-3.15, 2.56), (4.5, 0), (4.5, 0), (4.2, 1e-2), (4.2, 1e-5))
DEFAULT_YRANGE0 = ((-4, 1), (-5, 5), (-4, 1), (-8, 5), (-6, 2), (-6, 3), (0, 0), (-2, 8))
DEFAULT_XRANGE = dict(zip(PRESENTATIONS, DEFAULT_XRANGE0))
DEFAULT_YRANGE = dict(zip(PRESENTATIONS, DEFAULT_YRANGE0))

PLANETS = ('Moon', 'Mars', 'Mercury')
SURFACE_AREAS = (3.79e7, 1.44e8, 7.48e7)

LINESTYLES = {'m2cnd':'--','sdaa':':'}

# Constants for settings and plotting
DEFAULTS = {
    'set': {
        'chronology_system': 'Moon, Neukum (1983)',
        'epochs': None,
        'equilibrium': None,
        'invert': 0,
        'tight': 0,
        'transparent': 0,
        'text_halo': None,  # conditional default set in construct_cps_dict()
        'isochrons': '',
        'legend': 'fnacr',
        'mu': 1,
        'presentation': 'differential',
        'print_dimensions': '7.5x7.5',
        'pt_size': '9.0',
        'font': 'Open Sans',
        'randomness': 0,
        'ref_diam': 1,
        'sig_figs': 3,
        'style': 'natural',
        'title': '',
        'out': None,
        'format': {'png', 'csv'},
        'min_diameter': 0.15,
        'global_area': 1e12,  # default larger than all terrestrial planets
        'n_samples': 200,
        'trials': 30,
        'measures': {'m2cnd','sdaa'},
        'ra_offset': 0.,
        'bins': 0,
    },
    'plot': {
        'source': 'None',
        'name': '',
        'range': ['0', 'inf'],
        'snap': 1,
        'type': 'data',  # should be conditional default set in construct_cps_dict()
        'error_bars': 1,
        'hide': 0,
        'colour': 0,
        'psym': 1,
        'binning': 'pseudo-log',
        'age_left': 0,
        'show_age': 1,
        'resurf': 0,
        'resurf_showall': 0,
        'isochron': 0,
        'offset_age': ['0', '0'],
    }
}


GREYS = (['#aaaaaa', '#e0e0e0', '#ededed', '#f8f8f8', '#ffffff'],  # standard/inverted grey values
         ['#787878', '#464646', '#373737', '#282828', '#000000'])

PALETTE = (  # 1st column for white background; 2nd for inverted
    ('#000000', '#ffffff', 'Black'),
    ('#a00000', '#ff0000', 'Red'),
    ('#008200', '#00ff00', 'Green'),
    ('#0050c8', '#5ab4ff', 'Blue'),
    ('#e1af00', '#ffdc00', 'Yellow'),
    ('#8748bd', '#b464ff', 'Violet'),
    ('#aaaaaa', '#787878', 'Grey'),
    ('#19426b', '#19426b', 'blue1'),
    ('#476788', '#476788', 'blue2'),
    ('#7a91a9', '#7a91a9', 'blue3'),
    ('#a0ccd3', '#a0ccd3', 'blue4'),
    ('#533714', '#533714', 'brown1'),
    ('#6b4719', '#6b4719', 'brown2'),
    ('#7b5c33', '#7b5c33', 'brown3'),
    ('#af9c83', '#af9c83', 'brown4'),
    ('#336b19', '#336b19', 'green1'),
    ('#5d8a49', '#5d8a49', 'green2'),
    ('#91af83', '#91af83', 'green3'),
    ('#b58000', '#b58000', 'orange'),
    ('#6b1946', '#6b1946', 'pink1'),
    ('#975e7d', '#975e7d', 'pink2'),
    ('#ba93a8', '#ba93a8', 'pink3'),
    ('#4c265d', '#4c265d', 'purple1'),
    ('#876e93', '#876e93', 'purple2'),
    ('#6b1920', '#6b1920', 'red1'),
    ('#7c393f', '#7c393f', 'red2'),
    ('#8d595e', '#8d595e', 'red3'),
    ('#196b64', '#196b64', 'teal1'),
    ('#6ba09b', '#6ba09b', 'teal2'),
    ('#b5a200', '#b5a200', 'yellow1'),
    ('#ded68e', '#ded68e', 'yellow2'),
    ('#a8b100', '#a8b100', 'yellow-green'),
)

# def initialize_calculated():
#     """
#     these definitions must be contained in function for proper multiprocessing initialisation
#     """

with importlib_resources.path("craterstats.config", "demo_commands.txt") as path:
    cst.PATH = gm.filename(str(path),'u')

star4 = mpath.Path(
    np.array(([-1, -.25, 0, .25, 1, .25, 0, -.25, -1], [0, .25, 1, .25, 0, -.25, -1, -.25, 0])).transpose())

cst.MARKERS = (('s', 'square', {'marker': 's', 'fillstyle': 'none', 'markersize': 3.}),
           ('o', 'circle', {'marker': 'o', 'fillstyle': 'none', 'markersize': 3.}),
           ('*4', 'star4', {'marker': star4, 'fillstyle': 'none', 'markersize': 4.3}),
           ('^', 'triangle', {'marker': '^', 'fillstyle': 'none', 'markersize': 3.5}),
           ('*', 'star5', {'marker': '*', 'fillstyle': 'none', 'markersize': 4.5}),
           ('x', 'diagonal cross', {'marker': 'x', 'markersize': 3.}),
           ('+', 'cross', {'marker': '+', 'markersize': 3.5}),
           ('.', 'point', {'marker': '.', 'markersize': 3.}),
           ('v', 'inverted triangle', {'marker': 'v', 'fillstyle': 'none', 'markersize': 3.5}),
           ('fs', 'filled square', {'marker': 's', 'markersize': 2.5}),
           ('fo', 'filled circle', {'marker': 'o', 'markersize': 2.5}),
           ('f*4', 'filled star4', {'marker': star4, 'markersize': 3.8}),
           ('f^', 'filled triangle', {'marker': '^', 'markersize': 2.5}),
           ('f*', 'filled star5', {'marker': '*', 'markersize': 3.5}),
           ('fv', 'filled inverted triangle', {'marker': 'v', 'markersize': 2.5}),
           )

cst.ABOUT=["Craterstats-III",
       "Copyright (c) 2021-2025, Greg Michael",
       "Licensed under BSD 3-Clause License. See LICENSE.txt for details.",
       "Version: "+cst.__version__,
       "",
       "Explanations of concepts and calculations used in the software are given in:",
       "",
       "Standardisation of crater count data presentation",
       "Arvidson R.E., Boyce J., Chapman C., Cintala M., Fulchignoni M., Moore H., Neukum G., Schultz P., Soderblom L., Strom R., Woronow A., Young R. "
       "Standard techniques for presentation and analysis of crater size–frequency data. Icarus 37, 1979.",
       "",
       "Formulation of a planetary surface chronology model",
       "Neukum G., Meteorite bombardment and dating of planetary surfaces (English translation, 1984). Meteoritenbombardement und Datierung planetarer Oberflächen (German original, 1983).",
       "",
       "Resurfacing correction for cumulative fits; production function differential forms",
       "Michael G.G., Neukum G., Planetary surface dating from crater size-frequency distribution measurements: Partial resurfacing events and statistical age uncertainty. EPSL 294, 2010.",
       "",
       "Differential fitting; binning bias correction; revised Mars epoch boundaries",
       "Michael G.G., Planetary surface dating from crater size-frequency distribution measurements: Multiple resurfacing episodes and differential isochron fitting. Icarus, 2013.",
       "",
       "Poisson timing analysis; mu-notation",
       "Michael G.G., Kneissl T., Neesemann A., Planetary surface dating from crater size-frequency distribution measurements: Poisson timing analysis. Icarus, 2016.",
       "",
       "Poisson calculation for buffered crater count",
       "Michael G.G., Yue Z., Gou S., Di K., Dating individual several-km lunar impact craters from the rim annulus in "
       "region of planned Chang’E-5 landing Poisson age-likelihood calculation for a buffered crater counting area. EPSL 568, 2021.",
       "",
       "Small-area and low number counts: age-area-uncertainty plots",
       "Michael G., Liu J., Planetary surface dating from crater size–frequency distribution measurements: interpretation of small-area and low number counts. Icarus 431, 2025.",
       "",
       "Sequence probability and simultaneous formation",
       "Michael G., Zhang L., Wu C., Liu J., Planetary surface dating from crater size–frequency distribution measurements: Sequence probability and simultaneous formation. Did the close Chang’E-6 mare units form simultaneously? Icarus 438, 2025.",
       "",
       "Full references for specific chronology or other functions are listed with the function definitions in `config/functions.txt`.",
       "",
       ]

