

usage: `craterstats.py [-h] [-i INPUT] [-lcs] [-lpc] [-about] [-demo] [-o OUT] [-as] [-f {png,tif,pdf,svg,csv,stat} [{png,tif,pdf,svg,csv,stat} ...]] [-cs CHRONOLOGY_SYSTEM] [-ef EQUILIBRIUM] [-ep EPOCHS] [-title TITLE]
                      [-subtitle SUBTITLE] [-pr PRESENTATION] [-xrange XRANGE XRANGE] [-yrange YRANGE YRANGE] [-isochrons ISOCHRONS] [-show_isochrons {0,1}] [-legend LEGEND] [-cite_functions {0,1}] [-mu {0,1}] [-style {natural,root-2}] [-invert {0,1}] [-transparent] [-tight]
                      [-pd PRINT_DIMENSIONS] [-pt_size PT_SIZE] [-ref_diameter REF_DIAMETER] [-sf {2,3}] [-st] [-p KEY=VAL, [KEY=VAL, ...]]`

Craterstats: a tool to analyse and plot crater count data for planetary surface dating.

optional arguments:

  -h, --help            show help message

  -i, --input [filename]   input args from file

  -lcs                  list chronology systems

  -lpc                  list plot symbols and colours

  -about                show program details

  -demo                 run sequence of demonstration commands: output in ./demo

  -o, --out [filename]   output filename (omit extension for default) or directory

  -as, --autoscale      rescale plot axes

  -f, --format [{png,tif,pdf,svg,csv,stat}] 
                        output formats

  -cs, --chronology_system [abbreviated chronology system name]
                        chronology system, abbreviated

  -ef, --equilibrium 
                        equilibrium function, abbreviated

  -ep, --epochs
                        epoch system, abbreviated

  -title [title]        plot title

  -subtitle [subtitle]  plot subtitle

  -pr, --presentation   data presentation, abbreviated: 
  
- cumulative
- differential
- R-plot
- Hartmann
- chronology
- rate
- sequence
- uncertainty


  -xrange 
                        x-axis range, log(min) log(max)

  -yrange
                        y-axis range, log(min) log(max)

  -isochrons comma-separated isochron list in Ga, e.g. `-isochrons 1,3,3.7a,4a`.
                        Each with optional suffix to modify label: 
  - n - suppress label
  - a - place above instead of below
  - s - small font size

  -show_isochrons {0,1}
                        1 - show; 0 - suppress

  -legend [codes]       any combination of: 
  
- n - name
- a - area 
- p - perimeter 
- c - number of craters
- r - range
- N - N(d_ref) value
- 0 - suppress legend completely

    e.g. `-legend nacr`


  -cite_functions {0,1}
                        1 - show; 0 - suppress

  -mu {0,1}             1 - show; 0 - suppress

  -style {natural,root-2}
                        diameter axis style

  -invert {0,1}         1 - invert to black background; 0 - white background

  -transparent          set transparent background

  -tight                tight layout

  -pd, --print_dimensions 
                        either single value (cm/decade) or enclosing box for axes in cm (AxB), e.g. `-pd 1.5` or `-pd 8x8`

  -pt_size              point size for figure text

  -ref_diameter 
                        reference diameter for displayed N(d_ref) values

  -sf, --sig_figs {2,3}
                        number of significant figures for displayed ages, e.g. `-sf 3`

  -st, --sequence_table
                        generate sequence probability table (with extension `_sequence.csv`)

  -p, --plot [KEY=VAL, ...]
                        specify overplot. Allowed keys: 
                        
- source=filename
- name=txt
- range=[min,max]
- type={data,poisson,b-poisson,c-fit,d-fit}
- error_bars={1,0}
- hide={1,0}
- colour={black, red, blue, green...} Enter `craterstats -lpc` for full list
- psym={circle, square, star, filled circle...} Enter `craterstats -lpc` for full list
- binning={pseudo-log,20/decade,10/decade,x2,root-2,4th root-2,none}
- age_left={1,0}
- display_age={1,0}
- resurf={1,0}, apply resurfacing correction
- resurf_showall={1,0}, show all data with resurfacing correction
- isochron={1,0}, extend isochron beyond selected range
- offset_age=[x,y], offset position of age label (in units of 1/20th of decade)
