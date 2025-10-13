#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import os
import sys
import argparse
import re
import platform
import subprocess
import shlex

import craterstats as cst
import craterstats.gm as gm


class AppendPlotDict(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        s=' '.join(values)
        d = {}
        for kv in re.split(r',(?=\w+=)',s): # only split on commas directly preceding keys
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
        try:
            with open(values) as f:
                # parse arguments in the file and store them in the target namespace
                a=f.read()
                a=('\n').join([e for e in a.split('\n') if e.strip() and not e.strip().startswith('#')] ) #remove '#' commented lines
                parser.parse_args(shlex.split(a), namespace)
                namespace.input_filename = f.name
                setattr(namespace, self.dest, True)
        except FileNotFoundError:
            raise argparse.ArgumentError(self, f"File not found: {values}")
        except PermissionError:
            raise argparse.ArgumentError(self, f"Permission denied: {values}")
        except Exception as e:
            raise argparse.ArgumentError(self, e)

def get_parser():
    parser = argparse.ArgumentParser(description='Craterstats: a tool to analyse and plot crater count data for planetary surface dating.')

    parser.add_argument('-i','--input', help="input args from file", metavar='filename.cs', action=LoadFromFile)
    parser.add_argument('-inc', '--include', help="include settings from external file", metavar='filename.txt', action=LoadFromFile)

    parser.add_argument("-lcs", help="list chronology systems", action='store_true')
    parser.add_argument("-lpc", help="list plot symbols and colours", action='store_true')
    parser.add_argument("-about", help="show program details", action='store_true')
    parser.add_argument("-v","--version", help="show program version", action='store_true')
    parser.add_argument("-demo", help="run sequence of demonstration commands: output in ./demo", action='store_true')
    parser.add_argument("-b","--bins", help="show bin boundaries", action='store_true')
    parser.add_argument("--convert", help="desired format [stat|scc|shp], source file", nargs=2, type=str)

    parser.add_argument("-o","--out", help="output filename (omit extension for default) or directory", nargs='+', action=SpacedString)
    parser.add_argument("--functions_user", help="path to file containing user defined chronology systems", nargs='+', action=SpacedString)
    parser.add_argument("--create_desktop_icon", help="create desktop icon for activated window", action='store_true')
    parser.add_argument("-m", "--merge", help="merge crater count files", nargs='+', action=SpacedString)

    parser.add_argument("-f", "--format", help="output formats",  nargs='+', choices=['png','tif','pdf','svg','csv'])

    parser.add_argument("-cs", "--chronology_system", help="chronology system index")
    parser.add_argument("-ef", "--equilibrium", help="equilibrium function index")
    parser.add_argument("-ep", "--epochs", help="epoch system index")

    parser.add_argument("-title", help="plot title", nargs='+', action=SpacedString)
    parser.add_argument("-pr", "--presentation", help="data presentation: " + (', ').join(cst.PRESENTATIONS))
    parser.add_argument("-xrange", help="x-axis range, log(min) log(max)", nargs=2)
    parser.add_argument("-yrange", help="y-axis range, log(min) log(max)", nargs=2)
    parser.add_argument("-isochrons", help="comma-separated isochron list in Ga, e.g. 1,3,3.7a,4a (optional combined suffix to modify label: n - suppress; a - above; s - small)")
    parser.add_argument("-legend", help="0 - suppress; or any combination of: n - name, a - area, p - perimeter, c - number of craters, r - range, N - N(d_ref) value")
    parser.add_argument("-mu", nargs='?', choices=[0,1], type=int, const=1, help="1 - show; 0 - suppress")
    parser.add_argument("-style", choices=['natural', 'root-2'], help="diameter axis style")

    parser.add_argument("-invert",  nargs='?', choices=[0,1], type=int, const=1, help="1 - invert to black background; 0 - white background")
    parser.add_argument("-text_halo", nargs='?', choices=[0,1], type=int, const=1, help="1 - on [default]; 0 - off")
    parser.add_argument("-transparent", nargs='?', choices=[0,1], type=int, const=1, help="set transparent background")
    #combine invert/transparent into one? maybe not, but invert could be same syntax - get rid of 0,1
    parser.add_argument("-tight", help="tight layout", action='store_true')

    parser.add_argument("-pd", "--print_dimensions", help="print dimensions: either single value (cm/decade) or enclosing box in cm (AxB), e.g. 2 or 8x8")
    parser.add_argument("-pt_size", type=float, help="point size for figure text")
    parser.add_argument("-ref_diameter", type=float, help="reference diameter for displayed N(d_ref) values")
    parser.add_argument("-sf","--sig_figs", type=int, choices=[2,3], help="number of significant figures for displayed ages")

    parser.add_argument("-st","--sequence_table", help="generate sequence probability table", action='store_true')

    parser.add_argument("-d_min","--min_diameter", type=float, help="minimum diameter for uncertainty plot")
    parser.add_argument("-ns", "--n_samples", type=int, help="number of samples for uncertainty plot")

    parser.add_argument("-p", "--plot", nargs='+', action=AppendPlotDict, metavar="KEY=VAL,",
                        help="Specify overplot.\nAllowed keys:   \n"
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
                             "show_age={1,0},"
                             "resurf={1,0}, apply resurfacing correction,"
                             "resurf_showall={1,0}, show all data with resurfacing correction,"
                             "isochron={1,0}, show whole fitted isochron,"
                             "offset_age=[x,y], in 1/20ths of decade")

    parser.add_argument("-ra", "--randomness_analysis", help="source fil for randomness analysis", nargs='+', action=SpacedString)
    parser.add_argument("-trials", type=int, help="number of Monte Carlo trials for randomness analysis")
    parser.add_argument("-measure", help="comma-separated list of measures for randomness analysis (from m2cnd,sdaa)")
    parser.add_argument("-ra_offset", type=int, help="vertical offset for randomness analysis sub-plot in 1/20ths of decade")

    return parser

def defaults():
    set = {
        'chronology_system': 'Moon, Neukum (1983)',
        'cite_functions': 1,
        'epochs': None,
        'equilibrium': None,
        'invert': 0,
        'transparent':0,
        'text_halo':1,
        'isochrons': None,
        'legend': 'fnacr',
        'mu': 1,
        'presentation': 'differential',
        'print_dimensions': '7.5x7.5',
        'pt_size': 9.0,
        'randomness': 0,
        'ref_diam': 1,
        'sig_figs': 3,
        'style': 'natural',
        'title': None,
        'format': {'png', 'csv'},
        'min_diameter':0.15,
        'global_area':1e12, # default larger than all terrestrial planets
        'n_samples':200,
        'ra_offset':0,
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
        'show_age': 1,
        'resurf': 0,
        'resurf_showall': 0,
        'isochron': 0,
        'offset_age': [0, 0]
    }
    return {'set':set,'plot':plot}


def decode_abbreviation(s,v,one_based=False,allow_ambiguous=False,allow_invalid=False):
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
        if allow_invalid:
            return -1
        else:
            sys.exit('Invalid abbreviation: ' + v)
    elif len(res) > 1 and not allow_ambiguous:
        sys.exit('Ambiguous abbreviation: ' + v)
    return res[0][0]


def construct_cps_dict(args,c,f,default_filename):
    if 'presentation' in vars(args):
        if args.presentation is not None:
            c['presentation'] = cst.PRESENTATIONS[decode_abbreviation(cst.PRESENTATIONS, args.presentation,one_based=True)]
    if c['presentation'] in ['chronology', 'rate', 'sequence','uncertainty']: #possible to overwrite with user-choice
        c['xrange'] = cst.DEFAULT_XRANGE[c['presentation']]
        c['yrange'] = cst.DEFAULT_YRANGE[c['presentation']]
    if c['presentation']=='sequence':
        c['legend']='A'

    for k,v in vars(args).items():
        if v is None:
            if k == 'out': c[k] = default_filename # don't set as default in parse_args: need to detect None in source_cmds
        else:
            if k in ('title',
                     'isochrons',
                     'legend',
                     'print_dimensions',
                     'pt_size',
                     'ref_diameter',
                     'sig_figs',
                     'randomness',
                     'mu',
                     'invert',
                     'transparent',
                     'text_halo',
                     'style',
                     'xrange', 'yrange',
                     'min_diameter','n_samples',
                     'bins',
                     'ra_offset',
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
    i=decode_abbreviation(cst.PLANETS,cs['body'],allow_invalid=True)
    if i!=-1:
        c['global_area']=cst.SURFACE_AREAS[i]

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
                    'show_age',
                    'resurf',
                    'resurf_showall',
                    'isochron',
                    ):
                p[k]=v
            elif k in ('range','offset_age'):
                p[k] = v.strip('[]').split(',')
            elif k == 'source':
                p['source']=cs_source(v).strip('"')
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

def convert_format(args, cps, cs_content):
    def outfile(name, out, ext):
        if out:
            if os.path.isdir(out):
                outfile = out + name + ext
            else:
                outfile = gm.filename(out, 'pn') + ext
        else:
            outfile = name + ext
        return outfile

    fmt, src = args.convert
    scc = cst.Spatialcount(src.replace('%sample%/', cst.PATH + 'sample/'))
    fmt1 = fmt.lstrip(".")
    fmt0 = gm.filename(src,'e').lstrip(".")
    out = outfile(gm.filename(src, 'n'), args.out, '.'+fmt1)
    match fmt1:
        case 'stat' if fmt0 in ['diam','scc','shp']:
            cc = cst.Cratercount(src)
            out = gm.filename(out, 'p1e', cc.name)
            cc.WriteStatFile(out)
        case 'scc':
            if fmt0 == 'shp':
                scc = cst.Spatialcount(src)
                out = gm.filename(out, 'p1e', scc.name)
                scc.writeSCCfile(out)
        case 'shp':
            if fmt0 == 'scc':
                scc = cst.Spatialcount(src)
                scc.writeSHPfiles(out)
                out = gm.filename(out,'pn1e', '[_CRATER,_AREA]')
        case 'png'|'svg'|'pdf':
            if fmt0 in ['shp','scc']:
                out = re.sub(r'_?CRATER_?', '', out)
                out = gm.filename(out, 'pn1e','_map')
                cps.create_map_plotspace()
                scc.plot(cps,grid=True)
                cps.fig.savefig(out, dpi=500, transparent=cps.transparent, bbox_inches='tight' if args.tight else None, pad_inches=.02 if args.tight else None)
                gm.write_textfile(gm.filename(out,'pn1','.cs'), cs_content)
        case _:
            print(f"{fmt0} to {fmt1} conversion not supported")
            return
    print(f"Conversion written to: {out}")
    return

def source_cmds(src):
    cmd=gm.read_textfile(src, ignore_blank=True, ignore_hash=True)
    parser=get_parser()
    for i,c in enumerate(cmd):
        a = c.split()
        args = parser.parse_args(a)
        if args.out is None:
            f=f'{i:02d}-out'
            a+=['-o',f]
            c+=' -o '+f
        print(f'\nCommand: {i}\ncraterstats ' + c)
        main(a)
    print('\nProcessing complete.')

def demo(d=None,src=None):
    if not src: src = cst.PATH+'config/demo_commands.txt'
    cmd = gm.read_textfile(src, ignore_blank=True, ignore_hash=True)
    out='demo/'
    os.makedirs(out,exist_ok=True)
    if d is None:
        d=range(0,len(cmd))
    for i in d:
        c=cmd[i]
        print(f'\nDemo {i}\ncraterstats '+c)
        a = shlex.split(f'-o {out}{i:02d}-demo {c}')
        main(a)
    print('\nDemo output written to: '+out)
    return d

def do_functions_user(args):
    if os.environ.get('CONDA_PREFIX'): # conda environment
        config = os.environ.get('CONDA_PREFIX')+'/etc/config_functions_user.txt'
    elif getattr(sys, 'frozen', False): # pyinstaller environment
        config = os.path.dirname(sys.executable) + '/_internal/craterstats/config_functions_user.txt'
    else:
        return None #actions environment is not conda
    if args.functions_user:
        s=['#path to functions_user.txt',args.functions_user]
        gm.write_textfile(config,s)
        print(': '.join(s)[1:])
    return gm.read_textfile(config,ignore_hash=True)[0] if gm.file_exists(config) else None

def create_desktop_icon():
    system = platform.system()
    match system:
        case 'Windows':
            subprocess.run([
                "powershell", "-NoProfile", "-Command", '''
                $s = New-Object -ComObject WScript.Shell
                $sc = $s.CreateShortcut("$env:USERPROFILE\\Desktop\\craterstats-III.lnk")
                $sc.TargetPath = "$env:windir\\system32\\cmd.exe"
                $sc.Arguments = '/K "%USERPROFILE%\\miniforge3\\Scripts\\activate.bat craterstats"'
                $sc.WorkingDirectory = "$env:USERPROFILE"
                $sc.Save()
                '''
            ], check=True)
            print('Desktop shortcut created.')

        case _:
            print(f"Desktop shortcut creation is not yet implemented for: {system}.")

def cs_source(v):
    return v.replace('%sample%/', cst.PATH + 'sample/')

def randomness_analysis(args,cps):
    out = '' if cps.out=='out' else gm.filename(cps.out,'pn')
    ra = cst.Randomnessanalysis(cs_source(args.randomness_analysis), out=out)
    cps.out = gm.filename(ra.ra_file,'pn')
    trials = args.trials if args.trials else 300
    cps.measures = args.measure.split(',') if args.measure else ['m2cnd','sdaa']
    diff = set(cps.measures) - {'m2cnd','sdaa'}
    if diff:
        sys.exit(f"Invalid measure: {diff}")
    for measure in cps.measures:
        ra.run_montecarlo(trials, measure)
        # do each loop so as to retain data if interrupted
        ra.calculate_stats()
        ra.write()
    return ra

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
            print("Unable to read user functions file: "+functions_user+" - ignoring.")
    functions = gm.read_textstructure(s,from_string=True)

    if args.create_desktop_icon:
        create_desktop_icon()
        return

    if args.lcs:
        print(gm.bright("\nChronology systems:"))
        print('\n'.join([f'{e['name']}' for e in functions['chronology_system']]))
        print(gm.bright("\nEquilibrium functions:"))
        print('\n'.join([f'{e['name']}' for e in functions['equilibrium']]))
        print(gm.bright("\nEpoch systems:"))
        print('\n'.join([f'{e['name']}' for e in functions['epochs']]))
        return

    if args.lpc:
        print(gm.bright("\nPlot symbols:"))
        print(', '.join([f'{e[1]} ({e[0]})' for e in cst.MARKERS]))
        print(gm.bright("\nColours:"))
        print(', '.join([f'{e[2]}' for e in cst.PALETTE]))
        return

    if args.about:
        print('\n'.join(cst.ABOUT))
        return

    if args.version:
        print('\n'.join(cst.ABOUT[0:5]))
        return

    if args.merge:
        cst.merge_cratercounts(args)
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
        default_filename = re.sub(r'_?CRATER_?', '', default_filename) # remove if present from shp file
    cps_dict = construct_cps_dict(args, dflt['set'], functions, default_filename)
    if gm.filename(cps_dict['out'],'n')=='out' and cps_dict['presentation'] in ('chronology', 'rate', 'uncertainty'):
        cps_dict['out']=gm.filename(cps_dict['out'],'p')+cps_dict['presentation']

    if 'a' in cps_dict['legend'] and 'b-poisson' in [d['type'] for d in cp_dicts]:
        cps_dict['legend']+='p' #force to show perimeter with area if using b-poisson

    cps=cst.Craterplotset(cps_dict) #,craterplot=cpl)
    for d in cp_dicts:
        if isinstance(d['colour'], int):d['colour']=cps.palette[d['colour']]
    cpl = [cst.Craterplot(d) for d in cp_dicts]
    cps.craterplot=cpl

    cs_content = ''.join(['\n'+e if e[0]=='-' and not (e+' ')[1].isdigit() else ' '+shlex.quote(e) for e in args0])[1:]

    if args.convert:
        convert_format(args, cps, cs_content)
        return

    if cpl and cps.presentation not in ('sequence','uncertainty'):
        cps.autoscale(cps_dict['xrange'] if 'xrange' in cps_dict else None,
                      cps_dict['yrange'] if 'yrange' in cps_dict else None)


    def savefig(tag=''):
        cps.fig.savefig(cps.out + tag +'.' + f, dpi=500, transparent=cps.transparent,
                        bbox_inches='tight' if args.tight else None, pad_inches=.02 if args.tight else None)

    drawn=False
    for f in cps.format:
        if f in {'png','pdf','svg','tif'}:
            if args.randomness_analysis:
                ra = randomness_analysis(args,cps)
                for measure in cps.measures:
                    ra.plot_montecarlo_split(cps, measure)
                    savefig('-'+measure)
                # cps.create_map_plotspace()
                # ra.plot(cps,grid=True)
                # savefig('-map')
            elif cps.presentation == 'uncertainty':
                for plt in ('k','err','age'):
                    cps.draw()
                    cps.age_area_plot(plt)
                    savefig('_'+plt)
            else:
                if not drawn:
                    cps.draw()
                    drawn = True
                savefig()

        if f in {'csv'}:
            cps.create_summary_table(f_out=cps.out+'.'+f)

    if not args.input:
        gm.write_textfile(cps.out + '.cs', cs_content)

if __name__ == '__main__': 
    main()

