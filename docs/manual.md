
# Command options

usage: craterstats.py [-h] [-i INPUT] [-inc INCLUDE] [-lcs] [-lpc] [-about] [-demo] [-b] [-o OUT [OUT ...]] [--functions_user FUNCTIONS_USER [FUNCTIONS_USER ...]] [--merge MERGE [MERGE ...]]
                      [-f {png,tif,pdf,svg,csv,stat} [{png,tif,pdf,svg,csv,stat} ...]] [-cs CHRONOLOGY_SYSTEM] [-ef EQUILIBRIUM] [-ep EPOCHS] [-title TITLE [TITLE ...]] [-pr PRESENTATION] [-xrange XRANGE XRANGE] [-yrange YRANGE YRANGE]
                      [-isochrons ISOCHRONS] [-legend LEGEND] [-mu {0,1}] [-style {natural,root-2}] [-invert {0,1}] [-transparent] [-tight] [-pd PRINT_DIMENSIONS] [-pt_size PT_SIZE] [-ref_diameter REF_DIAMETER] [-sf {2,3}] [-st]
                      [-d_min MIN_DIAMETER] [-ns N_SAMPLES] [-p KEY=VAL, [KEY=VAL, ...]]

-h, --help            show help message

-i, --input [filename.cs]   input command line arguments from file

-inc, --include [filename.txt]  include commands from external file (same format as .cs file) e.g., to share layout settings between a set of plots: 

```
-cs neukum01
-pr cml
-ef trask
-xrange -2 1
-yrange -2 1
-sf 3
-pt_size 11
-tight
```

-lcs                  list chronology systems

- Chronology systems:
  - Moon, Neukum (1983)
  - Moon, Neukum et al. (2001)
  - Moon, Hartmann 2010 iteration
  - Moon, Yue et al. (2022)
  - Mars, Neukum-Ivanov (2001)
  - Mars, Ivanov (2001)
  - Mars, Hartmann 2004 iteration
  - Mars, Hartmann & Daubar (2016)
  - Mercury, Strom & Neukum (1988)
  - Mercury, Neukum et al. (2001)
  - Mercury, Le Feuvre and Wieczorek 2011 non-porous
  - Mercury, Le Feuvre and Wieczorek 2011 porous
  - Vesta, Rev4, Schmedemann et al (2014)
  - Vesta, Rev3, Schmedemann et al (2014)
  - Vesta, Marchi & O'Brien (2014)
  - Ceres, Hiesinger et al. (2016)
  - Ida, Schmedemann et al (2014)
  - Gaspra, Schmedemann et al (2014)
  - Lutetia, Schmedemann et al (2014)
  - Phobos, Case A - SOM, Schmedemann et al (2014)
  - Phobos, Case B - MBA, Schmedemann et al (2014)
  

- Equilibrium functions: 
  - Lunar equilibrium (Trask, 1966)
  - Hartmann (1984)
  

- Epoch systems:
  - Moon, Wilhelms (1987)
  - Moon, Guo et al (2024)
  - Mars, Michael (2013)


-lpc                  list plot symbols and colours

- Plot symbols:
square (s), circle (o), star4 (\*4), triangle (^), star5 (\*), diagonal cross (x), cross (+), point (.), inverted triangle (v), filled square (fs), filled circle (fo), filled star4 (f*4), filled triangle (ft), filled star5 (f\*), filled inverted triangle
 (fv)


- Colours:
Black, Red, Green, Blue, Yellow, Violet, Grey, blue1, blue2, blue3, blue4, brown1, brown2, brown3, brown4, green1, green2, green3, orange, pink1, pink2, pink3, purple1, purple2, red1, red2, red3, teal1, teal2, yellow1, yellow2, yellow-green


-about                show program details

-demo                 run sequence of demonstration commands: output in ./demo

-b, --bins            show bin overlay (to aid diamater selection - normally remove before publication)

-o, --out [filename]   output filename (omit extension for default) or directory

-f, --format [{png,tif,pdf,svg,csv,stat}] 
                output formats

--functions_user [filepath] set path to user-defined chronology system file.

- Chronology system definitions should be modelled on those in `src/craterstats/config/functions.txt`
- Filepath will be persistent across conda sessions
- Check new systems are recognised with `craterstats -lcs`

--create_desktop_icon   

- On Windows, generate desktop shortcut to start up Craterstats-III 

-m, --merge             merge two or more crater count files into single file

-cs, --chronology_system 
                    chronology system, abbreviated (Enter `craterstats -lcs` for full list)

-ef, --equilibrium 
                    equilibrium function, abbreviated (Enter `craterstats -lcs` for full list)

-ep, --epochs
                    epoch system, abbreviated (Enter `craterstats -lcs` for full list)

-title [title]        plot title

- use `|` as separator for multi-line title

-pr, --presentation   data presentation, abbreviated: 
  
  - cumulative
  - differential
  - R-plot
  - Hartmann
  - chronology
  - rate
  - sequence - copy or create -p entries as for normal age measurements (Poisson or fit types) 
  - uncertainty - note: also specify d_min value (-d_min XXX)


-xrange 
                    x-axis range, log(min) log(max)

-yrange
                    y-axis range, log(min) log(max)

-isochrons comma-separated isochron list in Ga, e.g. `-isochrons 1,3,3.7a,4a`.
                    Each with optional suffix to modify label: 
  - n - suppress label
  - a - place above instead of below
  - s - small font size

-legend [codes]       any combination of: 
  
  - f - functions
  - n - name
  - a - area 
  - p - perimeter 
  - c - number of craters
  - r - range
  - N - N(d_ref) value
  - A - age (sequence plot)
  - 0 - suppress legend completely

      e.g. `-legend fnacr`


-mu {0,1}             1 - show; 0 - suppress

-style {natural,root-2}
                    diameter axis style

-invert {0,1}         1 - invert to black background; 0 - white background

-transparent          set transparent background

-tight                use tight layout

-pd, --print_dimensions 
                    either single value (cm/decade) or enclosing box for axes in cm (AxB), e.g. `-pd 1.5` or `-pd 8x8`

-pt_size              point size for figure text

-ref_diameter 
                    alternative reference diameter for displayed N(d_ref) values

-sf, --sig_figs {2,3}
                    number of significant figures for displayed ages, e.g. `-sf 3`

-st, --sequence_table
                    generate sequence probability table (with extension `_sequence.csv`)

-d_min, --min_diameter
    specify minimum observable crater diameter for complete count (uncertainty plot) 

-ns, --n_samples
    specify number of samples for uncertainty plot

-p, --plot [KEY=VAL, ...]
                    specify overplot. All keys and string values can be abbreviated, e.g. `source` to `src` or  `differential-fit` to `d-fit` 
                        
  - source=filename
  - name=txt, label for legend (filename is default)
  - range=[min,max]
    - either diameter range in km, e.g. `range=[0.2,0.7]` (will be expanded to closest bin boundaries)
    - or bin range, e.g. `range=[b7,b9]` include bin 7 to bin 9 (only bins with data) or `range=[b7,b-2]` (counting from 7th to 2nd-last point)
  - snap={1,0}, snap diameter range to bin boundaries (default is 1 - yes)
  - type={data,cumulative-fit,differential-fit,poisson,b-poisson,sequence}
  - error_bars={1,0}, show error bars (default is 1 - yes)
  - hide={1,0}, hide overplot (default is 0 - no)
  - colour={black, red, blue, green...} Enter `craterstats -lpc` for full list
    - black, red, green, blue, yellow, violet, grey, blue1, blue2, blue3, blue4, brown1, brown2, brown3, brown4, green1, green2, green3, orange, pink1, pink2, pink3, purple1, purple2, red1, red2, red3, teal1, teal2, yellow1, yellow2, yellow-green
  - psym={circle, square, star5, filled circle...} Enter `craterstats -lpc` for full list
    - square (s), circle (o), star4 (\*4), triangle (^), star5 (\*), diagonal cross (x), cross (+), point (.), inverted triangle (v), filled square (fs), filled circle (fo), filled star4 (f\*4), filled triangle (f^), filled star5 (f\*), filled inverted triangle (fv)
  - binning={pseudo-log,20/decade,10/decade,x2,root-2,4th root-2,none}
  - age_left={1,0}, move age label to left side (default is 0 - no)
  - show_age={1,0}, display age label (default is 1 - yes)
  - resurf={1,0}, apply resurfacing correction to cumulative fit (default is 0 - no)
  - resurf_showall={1,0}, show all data with resurfacing correction
  - isochron={1,0}, extend isochron beyond selected range (default is 0 - no)
  - offset_age=[x,y], offset position of age label (in units of 1/20th of decade)
