
# Craterstats-III command options quick reference

    craterstats [-h] [-i INPUT] [-inc INCLUDE] [-lcs] [-lpc]
                          [-about] [-v] [-demo] [-b] [-o OUT [OUT ...]]
                          [--functions_user FUNCTIONS_USER [FUNCTIONS_USER ...]]
                          [--create_desktop_icon] [-m MERGE [MERGE ...]]
                          [-f {png,tif,pdf,svg,csv,stat} [{png,tif,pdf,svg,csv,stat} ...]]
                          [-cs CHRONOLOGY_SYSTEM] [-ef EQUILIBRIUM]
                          [-ep EPOCHS] [-title TITLE [TITLE ...]]
                          [-pr PRESENTATION] [-xrange XRANGE XRANGE]
                          [-yrange YRANGE YRANGE] [-isochrons ISOCHRONS]
                          [-legend LEGEND] [-mu {0,1}]
                          [-style {natural,root-2}] [-invert {0,1}]
                          [-text_halo {0,1}] [-transparent] [-tight]
                          [-pd PRINT_DIMENSIONS] [-pt_size PT_SIZE]
                          [-ref_diameter REF_DIAMETER] [-sf {2,3}] [-st]
                          [-d_min MIN_DIAMETER] [-ns N_SAMPLES]
                          [-p KEY=VAL,[KEY=VAL,...]]


## Options

`-h, --help`
  Show this help message and exit.

`-i, --input FILE`
  Input command line arguments from a file.

`-inc, --include FILE`
  Include commands from an external .txt file, typically to share layout settings:

```txt
-cs neukum01
-pr cml
-ef trask
-xrange -2 1
-yrange -2 1
-sf 3
-pt_size 11
-tight
```

`-lcs`
  List available chronology systems.

`-lpc`
  List plot symbols and colours.

`-about`
  Show program details.

`-v, --version`
  show program version

`-demo`
  Run demonstration commands; outputs saved in `./demo`.

`-b, --bins`
  Show bin overlay to aid diameter selection.

`-o, --out FILE_OR_DIR`
  Output filename (omit extension for default) or directory.

`-f, --format [png|tif|pdf|svg|csv|stat]`
  Output format(s).

`--functions_user FILE`
  Set path to user-defined chronology system file.
- Chronology system definitions should be modelled on those in `src/craterstats/config/functions.txt`
- Filepath will be persistent across conda sessions

`--create_desktop_icon`
  On Windows, generate a desktop shortcut for Craterstats-III.

`-m, --merge FILES`
  Merge multiple crater count files.

`-cs, --chronology_system NAME`
  Set chronology system (run `-lcs` for list). e.g. Mars, Hartmann & Daubar (2016) or abbreviated as HD16

`-ef, --equilibrium NAME`
  Set equilibrium function (run `-lcs` for list).

`-ep, --epochs NAME`
  Set epoch system (run `-lcs` for list).

`-title TITLE`
  Plot title. Use `|` for multiline; wrap in quotes if needed.

`-pr, --presentation TYPE`
  Data presentation style. Valid values:
  * `cumulative`
  * `differential`
  * `R-plot`
  * `Hartmann`
  * `chronology`
  * `rate`
  * `sequence` (copy or create `-p` entries for age measurements)
  * `uncertainty` (also specify `-d_min` value)

`-xrange MIN MAX`
  X-axis range (log scale).

`-yrange MIN MAX`
  Y-axis range (log scale).

`-isochrons LIST`
  Comma-separated isochrons (e.g. `1,3,3.7a,4a`). Suffix options:

  * `n` — suppress label
  * `a` — place label above instead of below
  * `s` — small font size

`-legend CODES`
  Legend elements. Codes can be combined in any order, e.g. `-legend fnacr`:

  * `f` — functions
  * `n` — name
  * `a` — area
  * `p` — perimeter
  * `c` — number of craters
  * `r` — range
  * `N` — N(d_ref) value
  * `A` — age (sequence plot)
  * `0` — suppress legend completely

`-mu [{0,1}]`
  Legend visibility: `1` = show (default); `0` = suppress.

`-style {natural,root-2}`
  Diameter axis style.

`-invert [{0,1}]`
  Background color: `0` = white (default), `1` or no parameter = black.

`-text_halo [{0,1}]`
  Text halo for better legend readability: `0` = no, `1` = yes (default). Note: enabling makes text in SVG/PDF non-editable.

`-transparent [{0,1}]`
  Use transparent background (`1` or no parameter = yes).

`-tight`
  Use tight layout.

`-pd, --print_dimensions VALUE_OR_DIMENSIONS`
  Print dimensions in cm per decade or bounding box (e.g. `1.5` or `8x8`).

`-pt_size VALUE`
  Font point size for figure text.

`-ref_diameter VALUE`
  Alternative reference diameter for N(d_ref) values.

`-sf, --sig_figs {2,3}`
  Number of significant figures for displayed ages.

`-st, --sequence_table`
  Generate sequence probability table (`_sequence.csv` output).

`-d_min, --min_diameter VALUE`
  Minimum crater diameter for dating (for uncertainty plots).

`-ns, --n_samples VALUE`
  Number of samples for uncertainty plot.

`-p, --plot KEY=VAL[,KEY=VAL...]`
  Specify overplot options. Keys and values can be abbreviated (e.g. `source` to `src` or  `differential-fit` to `d-fit`). 
  Multiple key-value pairs should be separated by commas. Available options:

  * `source=filename`
    Data source filename.

  * `name=label`
    Label for legend (filename used by default).

  * `range=[min,max]` or `range=[b7,b9]`
    Diameter or bin range to plot. Examples:

    * `range=[0.2,0.7]` (km range, expanded to nearest bin boundaries)
    * `range=[b7,b9]` (bins 7 to 9)
    * `range=[b7,b-2]` (7th to 2nd-last bin)

  * `snap={1,0}`
    Snap diameter range to bin boundaries (`1` = yes, default).

  * `type={data,cumulative-fit,differential-fit,poisson,b-poisson}`
    Plot data only or choose age-estimate method.

  * `error_bars={1,0}`
    Show error bars (`1` = yes, default).

  * `hide={1,0}`
    Hide this overplot (`1` = yes).

  * `colour={black,red,green,blue,yellow,violet,grey,blue1,blue2,blue3,blue4,brown1,brown2,brown3,brown4,green1,green2,green3,orange,pink1,pink2,pink3,purple1,purple2,red1,red2,red3,teal1,teal2,yellow1,yellow2,yellow-green}`
    Colour for overplot. 

  * `psym={square (s), circle (o), star4 (*4), triangle (^), star5 (*), diagonal cross (x), cross (+), point (.), inverted triangle (v), filled square (fs), filled circle (fo), filled star4 (f*4), filled triangle (ft),filled star5 (f*), filled inverted triangle (fv)}`
    Plot symbol.  

  * `binning={pseudo-log,20/decade,10/decade,x2,root-2,4th root-2,none}`
    Binning divisions.

  * `age_left={1,0}`
    Move age label to left side (`0` default).

  * `show_age={1,0}`
    Display age label (`1` default).

  * `resurf={1,0}`
    Apply resurfacing correction (`0` default).

  * `resurf_showall={1,0}`
    Show all data with resurfacing correction.

  * `isochron={1,0}`
    Extend isochron beyond selected range (`0` default).

  * `offset_age=[x,y]`
    Offset position of age label (in units of 1/20th of decade).