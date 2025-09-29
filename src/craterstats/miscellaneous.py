#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import sys

import numpy as np
import matplotlib.pyplot as plt

import craterstats as cst
import craterstats.gm as gm


"""
This file contains miscellaneous code for Craterstats
"""

def bin_bias_correction(beta,k):
    '''
    Correction for binning bias of log-log histogram of known slope (see Michael (2013), Eq. 2)

    :param beta: ratio between adjacent bin boundaries, e.g. sqrt(2)
    :param k: log-log slope (including minus sign, e.g. -2)
    :return: correction ratio
    '''

    g=beta**.5-beta**(-.5)
    with np.errstate(invalid='ignore'): # both vectors of conditional are evaluated:
        Fbin2F_ratio = np.where(abs(k) < 1e-5,1., (beta ** (k / 2.) - beta ** (-k / 2.)) / (g * k) )

    return Fbin2F_ratio


class fractional_crater_transform:
    '''
    Transform function between area fraction and linear penetration across boundary.
    Easy to measure the polygon area overlap, but require fractional linear overlap for
    statistics. (Originally suggested by Misha Kreslavsky)

    After initialisation, able to call inverse function af2lf()
    '''

    def __init__(self):
        self.lf = np.array(gm.scl(range(100), out_range=[0., 1]))
        self.af = self.area_fraction(self.lf)

    def area_fraction(self,lf):
        d = 1 - 2 * lf
        theta = 2 * np.arccos(d)
        return (1 / (2 * np.pi)) * (theta - np.sin(theta))

    def af2lf(self,af):
        lf = np.interp(af, self.af, self.lf)
        return lf

    def plot(self):
        plt.plot(self.lf, self.af)
        plt.plot([0,1],[0,1],color='r')
        plt.gca().set_aspect('equal', adjustable='box')
        plt.xlabel('linear frac')
        plt.ylabel('area frac')
        plt.show()


def merge_cratercounts(args,equal_weight=False):
    '''
    Merge two or more cratercounts into a single file

    :param args: cmd line params
    :param: equal_weight [not yet implemented/verified]
    '''
    fs=gm.quoted_split(args.merge)
    if len(fs)<2:
        sys.exit("Specify at least two crater count files.")

    out=args.out
    if not out:
        out='_'.join(sorted(gm.filename(fs, 'n')))
    out = gm.filename(out, 'pn1', '.diam')

    d=[]
    frac=[]
    a=0.
    p=0.

    for f in fs:
        cc=cst.Cratercount(f)
        if cc.prebinned:
            sys.exit("Not a valid crater diameter file: "+f)

        #fraction1 = n_elements(fraction) eq 1?replicate(fraction, n_elements(diam)): fraction
        area=cc.area

        if equal_weight:
            fraction = [e/area for e in cc.fraction]  # weight by area
            area = 1.
        else:
            fraction = cc.fraction

        d += cc.diam
        frac += fraction
        a += area
        p += cc.perimeter

    s = (['# Merged crater diameter file', '#----------------------------', '#']
           + ['# ' + gm.filename(f, "ne") for f in fs]
           + ['#']
           + [f"area = {a}"]
           + [f"perimeter = {p}"]
           + ['#',"crater = {diameter, fraction"]
           + [f"{a:<12g}  {b:g}" for a,b in zip(d,frac)]
           + ['}']
         )

    gm.write_textfile(out,s)
    print('Merged file: '+out)




def str_age(age,e1=0,e2=0,sf=3,unit=None,simple=False,no_error=False,mu=False,MathML=False):
    '''
    Convert numerical age in Ga to latex-style string, optionally with sub/superscript errors and mu uncertainty function

    :param age:
    :param e1: plus error
    :param e2: minus error
    :param sf: no of sig figs
    :param unit: force specified unit
    :param simple: don't show zero decimals (for isochrons), nor use latex-style
    :param no_error: don't show errors
    :param mu: show mu uncertainty function
    :param MathML - use MathML instead of latex. Can paste into MS Word
    :return: age string
    '''

    f = [1, 1e-3, 1e-6, 1e-9]
    unit0 = ['Ga', 'Ma', 'ka', 'a']

    if unit is not None:
        a = next((e, u) for e, u in zip(f, unit0) if unit == u)
    else:
        a = next((e, u) for e, u in zip(f, unit0) if age >= e or u =='a')

    v=age/a[0]

    if simple:
        st=f'{v:g}'
    else:
        st= gm.sigfigs(v, sf)

    if e1>0 and not no_error :
        e1s = gm.sigfigs(e1 / a[0], sf - 1)
        e2s = gm.sigfigs(e2 / a[0], sf - 1)
        if MathML:
            st = '<msubsup><mtext>'+st+'</mtext><mtext>&#x2212;'+e2s+'</mtext><mtext>+'+e1s+'</mtext></msubsup>'
        else:
            st += '^{+' + e1s + '}_{-' + e2s + '}'

    if simple:
        st += ' ' + a[1]
    elif MathML:
        st = ('<math xmlns="http://www.w3.org/1998/Math/MathML">'
              +('<mi>&#956;</mi>' if mu else '')+st+'<mtext>&#8239;'+a[1]+'</mtext></math>')
    else:
        st = '$' + (r'𝜇' if mu else '') + st + '$ ' + a[1]

    return st


def Hartmann_bins(d_range):
    """
    Generate tick values and tick labels with units for Hartmann scale
    """
    v = [np.log10(2. ** e) for e in range(-10, 11)]  # set up root-2/hartmann axis labels
    labels = [str(e) for e in
              (1, 2, 4, 8, 16, 31, 63, 125, 250, 500, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)]
    labels[10] = '  ' + labels[10] + "km"
    xtickv, xtickname = map(list, zip(*[(val, txt) for val, txt in zip(v, labels) if d_range[0] <= val <= d_range[1]]))
    if xtickv[0] < 0: xtickname[0] += 'm'
    xminor = (xtickv[1] - xtickv[0]) / 2
    xminorv = [e+xminor for e in [xtickv[0]-2*xminor]+xtickv if d_range[0] <= e+xminor <= d_range[1]]
    return xtickv,xtickname,xminor,xminorv

def n_sigma_scaling(v):
    """
    scaling for n_sigma plot: enlarge central zone
    """
    return np.power(np.abs(v),.6)*np.sign(v)
