#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import os
import sys
import argparse
import numpy as np
import re
import pathlib

import importlib.resources as importlib_resources

import craterstats as cst
import craterstats.gm as gm


class AppendPlotDict(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        s=' '.join(values)
        d = {}
        for kv in re.split(',(?=\w+=)',s): # only split on commas directly preceding keys
            try:
                k, v = kv.split("=")
            except:
                sys.exit("Missing '=' in expression: " + option_string+' '+kv)
            d[k] = v
        list_of_d = getattr(namespace, self.dest)
        list_of_d=[d] if list_of_d is None else list_of_d+[d]
        setattr(namespace, self.dest, list_of_d)

class SpacedString(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, ' '.join(values))

class LoadFromFile(argparse.Action):
    def __call__ (self, parser, namespace, values, option_string = None):
        with values as f:
            # parse arguments in the file and store them in the target namespace
            a=f.read()
            a=('\n').join([e for e in a.split('\n') if e.strip() and (e+' ')[0]!='#'] ) #remove '#' commented lines
            parser.parse_args(a.split(), namespace)
            namespace.input_filename = f.name
            setattr(namespace, self.dest, True)

def get_parser():
    parser = argparse.ArgumentParser(description='Craterstats: a tool to analyse and plot crater count data for planetary surface dating.')

    parser.add_argument('-i','--input', help="input args from file", type=open, action=LoadFromFile)
    parser.add_argument("-src", help="take command line parameters from text file", nargs='+', action=SpacedString)
    #latter is used for demo. Maybe switch demo to use .cs files, too?

    parser.add_argument("-lcs", help="list chronology systems", action='store_true')
    parser.add_argument("-lpc", help="list plot symbols and colours", action='store_true')
    parser.add_argument("-about", help="show program details", action='store_true')
    parser.add_argument("-demo", help="run sequence of demonstration commands: output in ./demo", action='store_true')

    parser.add_argument("-o","--out", help="output filename (omit extension for default) or directory", nargs='+', action=SpacedString)
    parser.add_argument("--functions_user", help="path to file containing user defined chronology systems", nargs='+', action=SpacedString)

    parser.add_argument("-f", "--format", help="output formats",  nargs='+', choices=['png','tif','pdf','svg','csv','stat'])

    parser.add_argument("-cs", "--chronology_system", help="chronology system index")
    parser.add_argument("-ef", "--equilibrium", help="equilibrium function index")
    parser.add_argument("-ep", "--epochs", help="epoch system index")

    parser.add_argument("-title", help="plot title", nargs='+', action=SpacedString)
    parser.add_argument("-pr", "--presentation", help="data presentation: " + (', ').join(cst.PRESENTATIONS))
    parser.add_argument("-xrange", help="x-axis range, log(min) log(max)", nargs=2)
    parser.add_argument("-yrange", help="y-axis range, log(min) log(max)", nargs=2)
    parser.add_argument("-isochrons", help="comma-separated isochron list in Ga, e.g. 1,3,3.7a,4a (optional combined suffix to modify label: n - suppress; a - above; s - small)")
    parser.add_argument("-show_isochrons", choices=['0', '1'], help="1 - show; 0 - suppress")
    parser.add_argument("-legend", help="0 - suppress; or any combination of: n - name, a - area, p - perimeter, c - number of craters, r - range, N - N(d_ref) value")
    parser.add_argument("-cite_functions", choices=['0','1'], help="1 - show; 0 - suppress")
    parser.add_argument("-mu", choices=['0','1'], help="1 - show; 0 - suppress")
    parser.add_argument("-style", choices=['natural', 'root-2'], help="diameter axis style")

    parser.add_argument("-invert", choices=['0','1'], help="1 - invert to black background; 0 - white background")
    parser.add_argument("-transparent", help="set transparent background", action='store_true')
    #combine invert/transparent into one? maybe not, but invert could be same syntax - get rid of 0,1
    parser.add_argument("-tight", help="tight layout", action='store_true')

    parser.add_argument("-pd", "--print_dimensions", help="print dimensions: either single value (cm/decade) or enclosing box in cm (AxB), e.g. 2 or 8x8")
    parser.add_argument("-pt_size", type=float, help="point size for figure text")
    parser.add_argument("-ref_diameter", type=float, help="reference diameter for displayed N(d_ref) values")
    parser.add_argument("-sf","--sig_figs", type=int, choices=[2,3], help="number of significant figures for displayed ages")

    parser.add_argument("-st","--sequence_table", help="generate sequence probability table", action='store_true')

    parser.add_argument("-p", "--plot", nargs='+', action=AppendPlotDict, metavar="KEY=VAL,",
                        help="specify overplot. Allowed keys:   \n"
                             "source=txt,"
                             "name=txt,"
                             "range=[min,max],"
                             "snap={1,0},"
                             "type={data,poisson,b-poisson,c-fit,d-fit},"
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

def defaults():
    set = {
        'chronology_system': 'Moon, Neukum (1983)',
        'cite_functions': 1,
        'epochs': '',
        'equilibrium': '',
        'invert': 0,
        'isochrons': '',
        'legend': 'nacr',
        'mu': 1,
        'presentation': 'differential',
        'print_dimensions': '7.5x7.5',
        'pt_size': 8.0,
        'randomness': 0,
        'ref_diam': 1,
        'sig_figs': 3,
        'show_isochrons': 1,
        'show_legend_area': 1,
        'show_title': 1,
        'style': 'natural',
        'title': '',
        'format': {'png', 'csv'}
        }
    plot = {
        'source': '',
        'name': '',
        'range': ['0', 'inf'],
        'snap': 1,
        'type': 'data',
        'error_bars': 1,
        'hide': 0,
        'colour': 0,
        'psym': 1,
        'binning': 'pseudo-log',
        'age_left': 0,
        'display_age': 1,
        'resurf': 0,
        'resurf_showall': 0,
        'isochron': 0,
        'offset_age': [0, 0]
    }
    return {'set':set,'plot':plot}


def decode_abbreviation(s,v,one_based=False,allow_ambiguous=False):
    """
    decode arbitrary abbreviation of list member into index

    :param s: full string list
    :param v: abbreviation or index
    :param one_based: menu indexing of s starts at 1?
    :param allow_ambiguous: if allowed, return first match
    :return: index (zero-based)
    """

    #perhaps add back index selection requiring # prefix?

    regex = '(?i)' + '.*'.join(v)
    res = [(i,e) for i,e in enumerate(s) if re.search(regex, e) is not None]
    res.sort(key=lambda x: len(x[1]))
    if len(res) == 0:
        sys.exit('Invalid abbreviation: ' + v)
    elif len(res) > 1 and not allow_ambiguous:
        sys.exit('Ambiguous abbreviation: ' + v)
    return res[0][0]


def construct_cps_dict(args,c,f,default_filename):
    if 'presentation' in vars(args):
        if args.presentation is not None:
            c['presentation'] = cst.PRESENTATIONS[decode_abbreviation(cst.PRESENTATIONS, args.presentation,one_based=True)]
    if c['presentation'] in ['chronology', 'rate', 'sequence']: #possible to overwrite with user-choice
        c['xrange'] = cst.DEFAULT_XRANGE[c['presentation']]
        c['yrange'] = cst.DEFAULT_YRANGE[c['presentation']]
    if c['presentation']=='sequence':
        c['legend']='A'
    #c['format'] = set(c['format']) if 'format' in c else {}

    for k,v in vars(args).items():
        if v is None:
            if k == 'out': c[k] = default_filename # don't set as default in parse_args: need to detect None in source_cmds
        else:
            if k in ('title',
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
                     'style',
                     'xrange', 'yrange',
                     ):
                c[k]=v
            elif k in ('chronology_system','equilibrium','epochs'):
                names = [e['name'] for e in f[k]]
                c[k]=f[k][decode_abbreviation(names, v, one_based=True, allow_ambiguous=True)]['name']

            elif k == 'out':
                if os.path.isdir(v):
                    c[k] = os.path.normpath(v+'/'+default_filename)
                else:
                    c[k] = gm.filename(v, 'pn')
                    ext = gm.filename(v, 'e').lstrip('.')
                    if ext: c['format'].add(ext)
            elif k == 'format':
                c[k]=set(v)


    cs=next((e for e in f['chronology_system'] if e['name'] == c['chronology_system']), None)
    if cs is None: sys.exit('Chronology system not found:' + c['chronology_system'])

    c['cf'] = cst.Chronologyfn(f, cs['cf'])
    c['pf'] = cst.Productionfn(f, cs['pf'])

    if 'equilibrium' in c and c['equilibrium'] not in (None,''):
        c['ef'] = cst.Productionfn(f, c['equilibrium'], equilibrium=True)
    if 'epochs' in c and c['epochs'] not in (None,''):
        c['ep'] = cst.Epochs(f, c['epochs'],c['pf'],c['cf'])

    if c['presentation'] == 'Hartmann':
        if hasattr(c['pf'],'xrange'): #not possible to overwrite with user choice
            c['xrange'] = c['pf'].xrange
            c['yrange'] = c['pf'].yrange
        else:
            c['xrange'] = cst.DEFAULT_XRANGE['Hartmann']
            c['yrange'] = cst.DEFAULT_YRANGE['Hartmann']

    return c


def construct_plot_dicts(args,plot):
    #if type(plot) is list: plot=plot[0] #take only first plot entry as template
    cpl = []
    specified_source = False
    if args.plot is None: return []
    for d in args.plot:
        p=plot.copy()
        if cpl: # for these items: if not given, carry over from previous
            for k in ['source','psym','snap','isochron','error_bars','colour','binning']:
                p[k] = cpl[-1][k]
            if p['source'] == cpl[-1]['source']: #only carry type if source unchanged
                p['type'] = cpl[-1]['type']

        for k0,v in d.items():
            k=cst.CRATERPLOT_KEYS[decode_abbreviation(cst.CRATERPLOT_KEYS, k0, allow_ambiguous=True)]
            if k in (
                    'name',
                    'snap',
                    'error_bars',
                    'hide',
                    'age_left',
                    'display_age',
                    'resurf',
                    'resurf_showall',
                    'isochron',
                    ):
                p[k]=v
            elif k in ('range','offset_age'):
                p[k] = v.strip('[]').split(',')
            elif k == 'source':
                v = v.replace('%sample%/', cst.PATH+'sample/')
                p['source']=v.strip('"')
                specified_source = True
            elif k == 'type':
                p[k]=cst.OPLOT_TYPES_SHORT[decode_abbreviation(cst.OPLOT_TYPES, v, allow_ambiguous=True)]
            elif k == 'binning':
                p[k] = cst.Cratercount.BINNINGS[decode_abbreviation(cst.Cratercount.BINNINGS, v, allow_ambiguous=True)]
                cst.Cratercount.BINNINGS
            elif k == 'colour':
                if v[0]=='#':
                    if bool(re.match(r'^#([0-9A-Fa-f]{6})$', v)):
                        p[k]=v
                    else:
                        sys.exit('Invalid colour:'+v)
                else:
                    names=[n for c1,c2,n in cst.PALETTE]
                    p[k]=decode_abbreviation(names, v, allow_ambiguous=True)
            elif k == 'psym':
                j=[i for i,e in enumerate(cst.MARKERS) if e[0]==v]
                if len(j)==1: # found standard abbreviation
                    p[k]=j[0]
                else: # look for arbitrary abbreviation or index
                    names = [e[1] for e in cst.MARKERS]
                    p[k]=decode_abbreviation(names, v, allow_ambiguous=True)

        if not specified_source: sys.exit('Source not specified')
        if os.path.isabs(p['source']):
            src = p['source']
        else:
            src = (gm.filename(args.input_filename,'p') if args.input else '')+p['source']
        p['cratercount'] = cst.Cratercount(src)
        cpl += [p]
    return cpl


def source_cmds(src):
    cmd=gm.read_textfile(src, ignore_blank=True, ignore_hash=True)
    parser=get_parser()
    for i,c in enumerate(cmd):
        a = c.split()
        args = parser.parse_args(a)
        if args.out is None:
            f='{:02d}-out'.format(i)
            a+=['-o',f]
            c+=' -o '+f
        print(f'\nCommand: {i}\ncraterstats ' + c)
        main(a)
    print('\nProcessing complete.')

def demo(d=None,src=cst.PATH+'config/demo_commands.txt'):
    cmd = gm.read_textfile(src, ignore_blank=True, ignore_hash=True)
    out='demo/'
    os.makedirs(out,exist_ok=True)
    f = '-o '+out+'{:02d}-demo '
    if d is None:
        d=range(0,len(cmd))
    for i in d:
        c=cmd[i]
        print(f'\nDemo {i}\ncraterstats '+c)
        a = (f.format(i) + c).split()
        main(a)
    print('\nDemo output written to: '+out)

def do_functions_user(args):
    if os.environ.get('CONDA_PREFIX'):
        config = os.environ.get('CONDA_PREFIX')+'/etc/config_functions_user.txt'
    else:
        return None #actions environment is not conda
    if args.functions_user:
        s=['#path to functions_user.txt',args.functions_user]
        gm.write_textfile(config,s)
    return gm.read_textfile(config,ignore_hash=True)[0] if gm.file_exists(config) else None

def main(args0=None):
    args = get_parser().parse_args(args0)
    if not args0: args0=sys.argv[1:]

    functions=cst.PATH+'config/functions.txt'
    s = gm.read_textfile(functions, ignore_hash=True, strip=';', as_string=True)  # read and remove comments
    functions_user = do_functions_user(args)
    if functions_user:
        try:
            s = s + gm.read_textfile(functions_user, ignore_hash=True, strip=';', as_string=True)
        except:
            print("Unable to read "+functions_user+" - ignoring.")
    functions = gm.read_textstructure(s,from_string=True)

    if args.lcs:
        print(gm.bright("\nChronology systems:"))
        print('\n'.join(['{0}'.format(e['name']) for e in functions['chronology_system']]))
        print(gm.bright("\nEquilibrium functions:"))
        print('\n'.join(['{0}'.format(e['name']) for e in functions['equilibrium']]))
        print(gm.bright("\nEpoch systems:"))
        print('\n'.join(['{0}'.format(e['name']) for e in functions['epochs']]))
        return

    if args.lpc:
        print(gm.bright("\nPlot symbols:"))
        print(', '.join(['{0} ({1})'.format(e[1], e[0]) for e in cst.MARKERS]))
        print(gm.bright("\nColours:"))
        print(', '.join(['{0}'.format(e[2]) for e in cst.PALETTE]))
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

    dflt = defaults()
    cp_dicts = construct_plot_dicts(args,dflt['plot'])
    if args.input:
        default_filename = gm.filename(args.input_filename,'pn')
    else:
        default_filename = '_'.join(sorted(set([gm.filename(d['source'], 'n') for d in cp_dicts]))) if cp_dicts else 'out'
    cps_dict = construct_cps_dict(args, dflt['set'], functions, default_filename)

    if 'a' in cps_dict['legend'] and 'b-poisson' in [d['type'] for d in cp_dicts]:
        cps_dict['legend']+='p' #force to show perimeter with area if using b-poisson


    cps=cst.Craterplotset(cps_dict) #,craterplot=cpl)
    for d in cp_dicts:
        if isinstance(d['colour'], int):d['colour']=cps.palette[d['colour']]
    cpl = [cst.Craterplot(d) for d in cp_dicts]
    cps.craterplot=cpl

    if cpl and cps.presentation not in ('sequence'):
        cps.autoscale(cps_dict['xrange'] if 'xrange' in cps_dict else None,
                      cps_dict['yrange'] if 'yrange' in cps_dict else None)

    if not args.input:
        gm.write_textfile(cps_dict['out']+'.cs',''.join(['\n'+e if e[0]=='-' and not (e+' ')[1].isdigit() else ' '+e for e in args0])[1:])

    drawn=False
    for functions in cps.format:
        if functions in {'png','pdf','svg','tif'}:
            if not drawn:
                cps.draw()
                drawn=True
            cps.fig.savefig(cps_dict['out']+'.'+functions, dpi=500, transparent=args.transparent,
                            bbox_inches='tight' if args.tight else None,pad_inches=.02 if args.tight else None)
        if functions in {'csv'}:
            cps.create_summary_table(f_out=cps_dict['out']+'.'+functions)
        if functions in {'stat'}:
            stat_files=set([(e.source,e.binning) for e in cpl])
            for stat in stat_files:
                cc=cst.Cratercount(stat[0])
                cc.WriteStatFile(gm.filename(stat[0],"n12", '_'+stat[1],".stat"),stat[1])


if __name__ == '__main__': 
    main()


