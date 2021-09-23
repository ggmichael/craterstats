#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import os
import sys
import argparse
import numpy as np
import re
import pathlib

try:
    import importlib.resources as importlib_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources


import craterstats as cst
import craterstats.gm as gm


class AppendPlotDict(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        s=' '.join(values)
        d = {}
        for kv in re.split(',(?=\w+=)',s): # only split on commas directly preceding keys
            k, v = kv.split("=")
            if k in ('range','offset_age'):
                v= gm.read_textstructure(kv, from_string=True)[k]
            d[k] = v
        list_of_d = getattr(namespace, self.dest)
        list_of_d=[d] if list_of_d is None else list_of_d+[d]
        setattr(namespace, self.dest, list_of_d)

class SpacedString(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, ' '.join(values))


def get_parser():
    parser = argparse.ArgumentParser(description='Craterstats: a tool to analyse and plot crater count data for planetary surface dating.')

    parser.add_argument("-lcs", help="list chronology systems", action='store_true')
    parser.add_argument("-lpc", help="list plot symbols and colours", action='store_true')
    parser.add_argument("-about", help="show program details", action='store_true')
    parser.add_argument("-demo", help="run sequence of demonstration commands: output in ./demo", action='store_true')
    parser.add_argument("-src", help="take command line parameters from text file", nargs='+', action=SpacedString)

    parser.add_argument("-t", "--template", help="plot template", nargs='+', action=SpacedString)
    parser.add_argument("-o","--out", help="output filename (omit extension for default)", nargs='+', action=SpacedString)
    parser.add_argument("-as","--autoscale", help="rescale plot axes", action='store_true')
    parser.add_argument("-f", "--format", help="output formats",  nargs='+', choices=['png','jpg','tif','pdf','svg','txt'])
    parser.add_argument("--transparent", help="set transparent background", action='store_true')

    parser.add_argument("-cs", "--chronology_system", help="chronology system index")
    parser.add_argument("-ef", "--equilibrium", help="equilibrium function index")
    parser.add_argument("-ep", "--epochs", help="epoch system index")

    parser.add_argument("-title", help="plot title", nargs='+', action=SpacedString)
    parser.add_argument("-subtitle", help="plot subtitle", nargs='+', action=SpacedString)
    # parser.add_argument("-pi","--presentation", choices=range(1,7), metavar="[1-6]", default=2, type=int, dest='presentation_index',
    #     help="data presentation index: "+(', ').join([str(i+1)+'-'+e for i,e in enumerate(cst.PRESENTATIONS)]))
    parser.add_argument("-pr", "--presentation", help="data presentation: "
                        + (', ').join([str(i + 1) + '-' + e for i, e in enumerate(cst.PRESENTATIONS)]))
    parser.add_argument("-xrange", help="x-axis range, log(min) log(max)", nargs=2)
    parser.add_argument("-yrange", help="y-axis range, log(min) log(max)", nargs=2)
    parser.add_argument("-isochrons", help="comma-separated isochron list in Ga, e.g. 1,3,3.7a,4a (optional combined suffix to modify label: n - suppress; a - above; s - small)")
    parser.add_argument("-show_isochrons", choices=['0', '1'], help="1 - show; 0 - suppress")
    parser.add_argument("-legend", help="any combination of: n - name; a - area; # - number of craters; r - range; N - N(d_ref) value")
    parser.add_argument("-cite_functions", choices=['0','1'], help="1 - show; 0 - suppress")
    parser.add_argument("-mu", choices=['0','1'], help="1 - show; 0 - suppress")
    parser.add_argument("-style", choices=['natural', 'root-2'], help="diameter axis style")
    parser.add_argument("-invert", choices=['0','1'], help="1 - invert to black background; 0 - white background")

    parser.add_argument("-print_dim", help="print dimensions: either single value (cm/decade) or enclosing box (AxB), e.g. 2 or 8x8", nargs=1)
    parser.add_argument("-pt_size", type=float, help="point size for figure text")
    parser.add_argument("-ref_diameter", type=float, help="reference diameter for displayed N(d_ref) values")
    parser.add_argument("-sf","--sig_figs", type=int, choices=[2,3], help="number of significant figures for displayed ages")

    parser.add_argument("-p", "--plot", nargs='+', action=AppendPlotDict, metavar="KEY=VAL,",
                        help="specify overplot. Allowed keys:   \n"
                             "source=txt,"
                             "name=txt,"
                             "range=[min,max],"
                             "type={data,poisson,c-fit,d-fit},"
                             "error_bars={1,0},"
                             "hide={1,0},"
                             "colour={0-31},"
                             "psym={0-14},"
                             "binning={" +','.join(cst.Cratercount.BINNINGS) + "},"
                             "age_left={1,0},"
                             "display_age={1,0},"
                             "resurf={1,0}, apply resurfacing correction,"
                             "resurf_showall={1,0}, show all data with resurfacing correction,"
                             "isochron={1,0}, show whole fitted isochron,"
                             "offset_age=[x,y], in 1/20ths of decade")
    return parser

def decode_abbreviation(s,v,one_based=False,allow_ambiguous=False):
    """
    decode abitrary abbreviation of list member into index

    :param s: full string list
    :param v: abbreviation or index
    :param one_based: menu indexing of s starts at 1?
    :param allow_ambiguous: if allowed, return first match
    :return: index (zero-based)
    """

    try:  # if v contains index
        return np.clip(int(v) - int(one_based), 0, len(s))
    except: # otherwise abbreviation...
        regex = '(?i)' + '.*'.join(v)
        res = [i for i,e in enumerate(s) if re.search(regex, e) is not None]
        if len(res) == 0:
            sys.exit('Invalid abbreviation: ' + v)
        elif len(res) > 1 and not allow_ambiguous:
            sys.exit('Ambiguous abbreviation: ' + v)
        return res[0]


def construct_cps_dict(args,c,f):
    cpset=c['set']
    if 'presentation' in vars(args):
        if args.presentation is not None:
            cpset['presentation'] = cst.PRESENTATIONS[decode_abbreviation(cst.PRESENTATIONS, args.presentation,one_based=True)]
    if cpset['presentation'] in ['chronology', 'rate']: #possible to overwrite with user-choice
        cpset['xrange'] = cst.DEFAULT_XRANGE[cpset['presentation']]
        cpset['yrange'] = cst.DEFAULT_YRANGE[cpset['presentation']]
    cpset['format'] = set(cpset['format']) if 'format' in cpset else {}

    for k,v in vars(args).items():
        if v is None:
            if k == 'out': cpset[k] = 'out' # don't set as default in parse_args: need to detect None in source_cmds
        else:
            if k in ('title',
                     'subtitle',
                     'isochrons',
                     'show_isochrons',
                     'legend',
                     'print_dimensions',
                     'pt_size',
                     'ref_diameter',
                     'cite_functions',
                     'sig_figs',
                     'randomness',
                     'mu',
                     'invert',
                     'show_title',
                     'show_subtitle',
                     'style',
                     'xrange', 'yrange',
                     ):
                cpset[k]=v
            elif k in ('chronology_system','equilibrium','epochs'):
                names = [e['name'] for e in f[k]]
                cpset[k]=f[k][decode_abbreviation(names, v, one_based=True)]['name']

            elif k == 'out':
                cpset[k] = gm.filename(v, 'pn')
                ext= gm.filename(v, 'e').lstrip('.')
                if ext: cpset['format'].add(ext)
            elif k == 'format':
                cpset[k]=set(v)


    cs=next((e for e in f['chronology_system'] if e['name'] == cpset['chronology_system']), None)
    if cs is None: sys.exit('Chronology system not found:' + cpset['chronology_system'])

    cpset['cf'] = cst.Chronologyfn(f, cs['cf'])
    cpset['pf'] = cst.Productionfn(f, cs['pf'])

    if 'equilibrium' in cpset and cpset['equilibrium'] not in (None,''):
        cpset['ef'] = cst.Productionfn(f, cpset['equilibrium'], equilibrium=True)
    if 'epochs' in cpset and cpset['epochs'] not in (None,''):
        cpset['ep'] = cst.Epochs(f, cpset['epochs'],cpset['pf'],cpset['cf'])

    if cpset['presentation'] == 'Hartmann':
        if hasattr(cpset['pf'],'xrange'): #not possible to overwrite with user choice
            cpset['xrange'] = cpset['pf'].xrange
            cpset['yrange'] = cpset['pf'].yrange
        else:
            cpset['xrange'] = cst.DEFAULT_XRANGE['Hartmann']
            cpset['yrange'] = cst.DEFAULT_YRANGE['Hartmann']

    return cpset


def construct_plot_dicts(args, c):
    plot = c['plot']
    if type(plot) is list: plot=plot[0] #take only first plot entry as template
    cpl = []
    if args.plot is None: return []
    for d in args.plot:
        p=plot.copy()
        if cpl: # for these items: if not given, carry over from previous
            for k in ['source','psym','type','isochron','error_bars','colour','binning']:
                p[k] = cpl[-1][k]
        else:
            if not 'source' in d: sys.exit('Source not specified')

        for k,v in d.items():
            if k in (
                    'source',
                    'name',
                    'range',
                    'type',
                    'error_bars',
                    'hide',
                    'binning',
                    'age_left',
                    'display_age',
                    'resurf',
                    'resurf_showall',
                    'isochron',
                    'offset_age',
                    ):
                p[k]=v
            elif k == 'colour':
                names=[n for c1,c2,n in cst.PALETTE]
                p[k]=decode_abbreviation(names, v, allow_ambiguous=True)
            elif k == 'psym':
                j=[i for i,e in enumerate(cst.MARKERS) if e[0]==v]
                if len(j)==1: # found standard abbreviation
                    p[k]=j[0]
                else: # look for abitrary abbreviation or index
                    names = [e[1] for e in cst.MARKERS]
                    p[k]=decode_abbreviation(names, v, allow_ambiguous=True)

        p['cratercount'] = cst.Cratercount(p['source'])
        cpl += [p]
    return cpl


def source_cmds(src):
    cmd=gm.read_textfile(src, ignore_blank=True, ignore_hash=True)
    parser=get_parser()
    for i,c in enumerate(cmd):
        print(f'\nCommand: {i}\npython craterstats.py '+c)
        a = c.split()
        args = parser.parse_args(a)
        if args.out is None: a+=['-o','{:02d}-out'.format(i)]
        main(a)
    print('\nProcessing complete.')

def demo(d=None,src=None):
    if src is None:
        demo_cmds_ref=importlib_resources.files("craterstats.config") / 'demo_commands.txt'
        with importlib_resources.as_file(demo_cmds_ref) as src:
            cmd = gm.read_textfile(src, ignore_blank=True, ignore_hash=True)
    else:
        cmd = gm.read_textfile(src, ignore_blank=True, ignore_hash=True)
    out='demo/'
    os.makedirs(out,exist_ok=True)
    f = '-o '+out+'{:02d}-demo '
    if d is None:
        d=range(0,len(cmd))
    for i in d:
        c=cmd[i]
        print(f'\nDemo {i}\npython craterstats.py '+c)
        a = (f.format(i) + c).split()
        main(a)
    print('\n\nDemo output written to: '+out)


def main(args0=None):
    args = get_parser().parse_args(args0)

    template_ref=importlib_resources.files("craterstats.config") / 'default.plt'
    functions_ref=importlib_resources.files("craterstats.config") / 'functions.txt'

    with importlib_resources.as_file(template_ref) as template:
        c = gm.read_textstructure(template if args.template is None else args.template)
    with importlib_resources.as_file(functions_ref) as functions:
        f = gm.read_textstructure(functions)

    if args.lcs:
        print(gm.bright("\nChronology systems:"))
        print('\n'.join(['{0} {1}'.format(i + 1, e['name']) for i, e in enumerate(f['chronology_system'])]))
        print(gm.bright("\nEquilibrium functions:"))
        print('\n'.join(['{0} {1}'.format(i + 1, e['name']) for i, e in enumerate(f['equilibrium'])]))
        print(gm.bright("\nEpoch systems:"))
        print('\n'.join(['{0} {1}'.format(i + 1, e['name']) for i, e in enumerate(f['epochs'])]))
        return

    if args.lpc:
        print(gm.bright("\nPlot symbols:"))
        print('\n'.join(['{0} {1} ({2})'.format(i, e[1], e[0]) for i, e in enumerate(cst.MARKERS)]))
        print(gm.bright("\nColours:"))
        print('\n'.join(['{0} {1}'.format(i, e[2]) for i, e in enumerate(cst.PALETTE)]))
        return

    if args.about:
        print('\n'.join(cst.ABOUT))
        return

    if args.src:
        source_cmds(args.src)
        return

    if args.demo:
        demo()
        return

    cps_dict = construct_cps_dict(args, c, f)
    cp_dicts = construct_plot_dicts(args, c)
    cpl = [cst.Craterplot(d) for d in cp_dicts]

    cps=cst.Craterplotset(cps_dict,craterplot=cpl)
    if cpl:
        if args.autoscale or not ('xrange' in cps_dict and 'yrange' in cps_dict):
            cps.autoscale()

    drawn=False
    for f in cps.format:
        if f in {'png','jpg','pdf','svg','tif'}:
            if not drawn:
                cps.draw()
                drawn=True
            cps.fig.savefig(cps_dict['out']+'.'+f, dpi=500, transparent=args.transparent)
        if f in {'txt'}:
            cps.create_summary_table()

if __name__ == '__main__': 
    main()


