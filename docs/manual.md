

usage: `craterstats.py [-h] [-i INPUT] [-src SRC [SRC ...]] [-lcs] [-lpc] [-about] [-demo] [-t TEMPLATE [TEMPLATE ...]] [-o OUT [OUT ...]] [-as] [-f {png,tif,pdf,svg,csv,stat} [{png,tif,pdf,svg,csv,stat} ...]] [-cs CHRONOLOGY_SYSTEM] [-ef EQUILIBRIUM] [-ep EPOCHS] [-title TITLE [TITLE ...]]
                      [-subtitle SUBTITLE [SUBTITLE ...]] [-pr PRESENTATION] [-xrange XRANGE XRANGE] [-yrange YRANGE YRANGE] [-isochrons ISOCHRONS] [-show_isochrons {0,1}] [-legend LEGEND] [-cite_functions {0,1}] [-mu {0,1}] [-style {natural,root-2}] [-invert {0,1}] [-transparent] [-tight]
                      [-pd PRINT_DIMENSIONS] [-pt_size PT_SIZE] [-ref_diameter REF_DIAMETER] [-sf {2,3}] [-st] [-p KEY=VAL, [KEY=VAL, ...]]`

Craterstats: a tool to analyse and plot crater count data for planetary surface dating.

optional arguments:

  -h, --help            show this help message and exit

  -i INPUT, --input INPUT
                        input args from file

  -src SRC [SRC ...]    take command line parameters from text file

  -lcs                  list chronology systems

  -lpc                  list plot symbols and colours

  -about                show program details

  -demo                 run sequence of demonstration commands: output in ./demo

  -o OUT [OUT ...], --out OUT [OUT ...]
                        output filename (omit extension for default) or directory

  -as, --autoscale      rescale plot axes

  -f {png,tif,pdf,svg,csv,stat} [{png,tif,pdf,svg,csv,stat} ...], --format {png,tif,pdf,svg,csv,stat} [{png,tif,pdf,svg,csv,stat} ...]
                        output formats

  -cs CHRONOLOGY_SYSTEM, --chronology_system CHRONOLOGY_SYSTEM
                        chronology system index

  -ef EQUILIBRIUM, --equilibrium EQUILIBRIUM
                        equilibrium function index

  -ep EPOCHS, --epochs EPOCHS
                        epoch system index

  -title TITLE [TITLE ...]
                        plot title

  -subtitle SUBTITLE [SUBTITLE ...]
                        plot subtitle

  -pr PRESENTATION, --presentation PRESENTATION
                        data presentation: 1-cumulative, 2-differential, 3-R-plot, 4-Hartmann, 5-chronology, 6-rate, 7-sequence, 8-uncertainty

  -xrange XRANGE XRANGE
                        x-axis range, log(min) log(max)

  -yrange YRANGE YRANGE
                        y-axis range, log(min) log(max)

  -isochrons ISOCHRONS  comma-separated isochron list in Ga, e.g. 1,3,3.7a,4a (optional combined suffix to modify label: n - suppress; a - above; s - small)

  -show_isochrons {0,1}
                        1 - show; 0 - suppress

  -legend LEGEND        0 - suppress; or any combination of: n - name, a - area, p - perimeter, c - number of craters, r - range, N - N(d_ref) value

  -cite_functions {0,1}
                        1 - show; 0 - suppress

  -mu {0,1}             1 - show; 0 - suppress

  -style {natural,root-2}
                        diameter axis style

  -invert {0,1}         1 - invert to black background; 0 - white background

  -transparent          set transparent background

  -tight                tight layout

  -pd PRINT_DIMENSIONS, --print_dimensions PRINT_DIMENSIONS
                        print dimensions: either single value (cm/decade) or enclosing box in cm (AxB), e.g. 2 or 8x8

  -pt_size PT_SIZE      point size for figure text

  -ref_diameter REF_DIAMETER
                        reference diameter for displayed N(d_ref) values

  -sf {2,3}, --sig_figs {2,3}
                        number of significant figures for displayed ages

  -st, --sequence_table
                        generate sequence probability table

  -p KEY=VAL, [KEY=VAL, ...], --plot KEY=VAL, [KEY=VAL, ...]
                        specify overplot. Allowed keys: source=txt,name=txt,range=[min,max],type={data,poisson,b-poisson,c-fit,d-fit},error_bars={1,0},hide={1,0},colour={0-31},psym={0-14},binning={pseudo-log,20/decade,10/decade,x2,root-2,4th
                        root-2,none},age_left={1,0},display_age={1,0},resurf={1,0}, apply resurfacing correction,resurf_showall={1,0}, show all data with resurfacing correction,isochron={1,0}, show whole fitted isochron,offset_age=[x,y], in 1/20ths of decade
