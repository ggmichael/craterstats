
# Craterstats-III

This is a Python reimplementation and extension of the Craterstats-II software, a tool to analyse and plot crater count data for planetary surface dating.

[Gallery](https://github.com/ggmichael/craterstats/blob/main/docs/gallery.md)

[Quick reference](https://github.com/ggmichael/craterstats/blob/main/docs/manual.md)

# Recent additions

- Support for filename_CRATER.shp, filename_AREA.shp shapefile sets. These can be produced in, e.g. ArcPRO, 
using three-point circle and polygon tools, as well as OpenCraterTools
- Spatial randomness analysis (see Michael et al., 2012)

Both features use spherical geometry for calculations 

# Installation

Craterstats can be installed as a standalone executable for Windows. 
Download the latest version [here](https://github.com/ggmichael/craterstats/releases), 
unzip to wherever you prefer, and double-click `create_desktop_shortcut.bat` to create a start-up icon.

Executables have recently been added for MacOS and successful operation was reported for the arm64 version. 
[Download](https://github.com/ggmichael/craterstats/releases), unzip where you prefer, add the new directory to the shell path, and run Craterstats command from 
within a Terminal window. Feedback on the usability of these MacOS versions is especially welcome.   

Other installation methods (for Windows, MacOS and Linux) [here](https://github.com/ggmichael/craterstats/blob/main/docs/alternative_install.md).

# Quick demonstration and try-out

After installation, the following command will produce a series of example output plots as in the gallery, 
demonstrating the main features of the software. Plot image files are placed into the subfolder `demo/` of the 
current folder.
    
    craterstats -demo

Alternatively, visit the [Gallery](https://github.com/ggmichael/craterstats/blob/main/docs/gallery.md) and copy some of the commands there to recreate the example plots.


# Usage

The program operates through the command line to produce output in the form of publication or presentation ready graphics, or tabulated analysis results for further processing.

There are two parts to creating a Craterstats plot:

1. Specify the type of plot and any characteristics which apply to the analysis as a whole, e.g. whether differential, cumulative or other data presentation; the chronology system, displayed axis ranges

2. Specify the data to be overplotted, and which chronology model evaluations should be applied to it

In the following example, the first items define characteristics for the whole plot: `-cs neukumivanov` specifies the chronology system, *Mars, Neukum-Ivanov (2001)* 
(any unambiguous abbreviation is acceptable, e.g. ni2001 or marsNI), and the `-title Example plot` adds the chosen title.

The `-p` indicates the start of an overplot definition. Following this, the path to the data source is given: this will produce a simple data plot with the default binning, colour and plot symbol
(note that %sample% is a special path abbreviation to a craterstats installation directory - it's not needed for your own data). After the second `-p`, 
an additional overplot is specified: this time, a poisson age evaluation for the diameter range 0.2–0.7 km. Parameters within an overplot definition are separated by a `,`.  

    craterstats -cs neukumivanov -p source=%sample%/Pickering.scc -p type=poisson,range=[.2,.7]

Sometimes it is useful to be able to specify the diameter range in terms of the plotted data points. Here we plot from the 8th to the 5th-from-last bins:

    craterstats -cs neukumivanov -p source=%sample%/Pickering.scc -p type=poisson,range=[b8,b-5]

Or it may be easier to use a temporary bin overlay by adding the option `--bins`

    craterstats -cs neukumivanov -p source=%sample%/Pickering.scc -p type=poisson,range=[b8,b-5] --bins

A plot image file is created in the current folder with the same name `Pickering.png`. The output path or name can be changed with the `-o` option.  Different file types can be produced by giving the appropriate extension or with the `-f` option. 
Supported types are: png, tif, pdf, svg, csv, (multiple types can be specified, e.g. `-f png csv`)

An additional text file is created with the name `Pickering.cs` which contains the command line parameters used to create the plot. Often it is convenient 
to edit this file to modify the plot, which can then be regenerated with the shorter command:

    craterstats -i Pickering.cs

Another  file, `Pickering.csv`, gives dating results in tabular form for further analysis or transfer to a manuscript. 
Preformatted ages and N(1) values, e.g. $\mu630^{+37}_{-35}$ Ma, are provided in latex and in MathML (copy and paste into Word with CTRL-SHIFT-V to get formatted expression). 
   
Tables of chronology systems, equilibrium functions and epoch systems – which can be used with the `-cs`, `-ef` and `-ep` options – may be listed with the following command:

    craterstats -lcs

These items may specifed using any unambiguous abbreviated form, e.g. `-cs ida`. Thus, `-ef lunar` or `-ef trask` will obtain the `Lunar equilibrium (Trask, 1966)` equilibrium function. 

Tables of plot symbols and colours – which can be used with the `psym=` and `colour=` options – may be listed with the following command:

    craterstats -lpc

and can likewise be specified by name or abbreviation, e.g. `psym=circle` or `psym=o` select a circle; `colour=green` or `col=gr` select green. 

Differential plots are the default data presentation. To switch to a different kind, e.g. cumulative, add `-pr cumulative` or `-pr cml`. 
Other possibilities are: relative (R), Hartmann, chronology, rate, sequential or uncertainty.

The complete set of options can be seen with:

    craterstats --help

To simplify the construction of the command line, certain plot properties are persistent. If, for example, you specify `source=C:\tmp\area1.scc` in the first overplot, this becomes the default for subsequent overplots until you specify a different source file. This also applies to other properties where it is useful, including `binning=`, `colour=` and `psym=`.

Uncertainty plots for the evaluation of small-area, low-number counts, assuming a complete count of craters larger than d_min can be generated 
(plots for k, measured error and measured/actual age - see Michael & Liu, 2025):

    craterstats -pr uncertainty -cs n83 -d_min 0.15

as well as plots for comparing a sequence of events (Michael, Zhang et al., 2025):

    craterstats -pr seq -ep Wilhelms -xrange 4.2 1 -legend fAca -p src=%sample%/e1.diam,range=[0.24,1.5],type=poisson -p src=%sample%/e2.diam,rng=[0.25,1.5] -p src=%sample%/e3.diam,rng=[0.24,1.5] -p src=%sample%/w1.diam,rng=[0.21,1.2],colour=red 

You can run the spatial randomness analysis code for a particular .scc file or crater/area shapefile set as follows:

    craterstats -ra "%sample%/CE-6 8-km vicinity.scc" -trials 3000


# References

Explanations of concepts and calculations used in the software are given in publications below.

#### Standardisation of crater count data presentation

>Arvidson, R.E., Boyce, J., Chapman, C., Cintala, M., Fulchignoni, M., Moore, H., Neukum,
G., Schultz, P., Soderblom, L., Strom, R., Woronow, A., Young, R. [<i>Standard
techniques for presentation and analysis of crater size–frequency data.</i>](https://doi.org/10.1016/0019-1035%2879%2990009-5) Icarus 37, 1979.

#### Formulation of a planetary surface chronology model

>Neukum G., [<i>Meteorite bombardment and dating of planetary surfaces</i>](http://ntrs.nasa.gov/search.jsp?R=19840027189) (English translation, 1984). [<i>Meteoritenbombardement und Datierung planetarer Oberflächen</i>](http://www.planet.geo.fu-berlin.de/public/Neukum-Thesis%201983.pdf) (German original) Habilitation Thesis, Univ. of Munich, 186pp, 1983.

#### Resurfacing correction for cumulative fits; production function differential forms

>Michael G.G., Neukum G., [<i>Planetary surface dating from crater size-frequency distribution measurements: Partial resurfacing events and statistical age uncertainty.</i>](http://doi.org/10.1016/j.epsl.2009.12.041) Earth and Planetary Science Letters 294, 2010.

#### Differential fitting; binning bias correction; revised Mars epoch boundaries

>Michael G.G., [<i>Planetary surface dating from crater size-frequency distribution measurements: Multiple resurfacing episodes and differential isochron fitting.</i>](http://doi.org/10.1016/j.icarus.2013.07.004) Icarus 2013.

#### Poisson timing analysis; <i>μ</i>-notation

>Michael G.G., Kneissl T., Neesemann A., [<i>Planetary surface dating from crater size-frequency distribution measurements: Poisson timing analysis.</i>](https://doi.org/10.1016/j.icarus.2016.05.019) Icarus, 2016.

#### Poisson calculation for buffered crater count
       
>Michael G.G., Yue Z., Gou S., Di K., [<i>Dating individual several-km lunar impact craters from the rim annulus in region of planned Chang’E-5 landing Poisson age-likelihood calculation.</i>](https://doi.org/10.1016/j.epsl.2021.117031) EPSL 568, 2021.

#### Small-area and low number counts: age-area-uncertainty plots
>Michael G., Liu J., [<i>Planetary surface dating from crater size–frequency distribution measurements: interpretation of small-area and low number counts.</i>](https://doi.org/10.1016/j.icarus.2025.116489) Icarus 431, 2025.

#### Sequence probability and simultaneous formation
>Michael G., Zhang L., Wu C., Liu J. [<i>Planetary surface dating from crater size–frequency distribution measurements: Sequence probability and simultaneous formation. Did the close Chang’E-6 mare units form simultaneously?](https://doi.org/10.1016/j.icarus.2025.116644) Icarus 438, 2025.

Full references for specific chronology or other functions are listed with the function definitions in `config/functions.txt`.

A set of introductory slides to the methods and an earlier version of the software is [here](https://github.com/ggmichael/craterstats/tree/main/docs),
as well an update on this python version. Note that some command syntax has changed since the slides were produced.





