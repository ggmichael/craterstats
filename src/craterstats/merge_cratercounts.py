#  Copyright (c) 2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import sys

import craterstats as cst
import craterstats.gm as gm

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



