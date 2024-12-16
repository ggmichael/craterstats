
# Craterstats

This is a reimplementation in Python 3.8 of the CraterstatsII software, a tool to analyse and plot crater count data for planetary surface dating.

# Installation

The `craterstats` package is available through the Python Package Index (PyPi).
The following procedure for installation on Windows, MacOS or Linux is recommended:

1. Install `conda` using the [miniforge installer](https://github.com/conda-forge/miniforge#miniforge3) for your OS. 
1. Launch the Miniforge prompt (Windows) or any command prompt (MacOS, Linux) and enter the following to create a virtual environment for craterstats:
  
    ```
    conda create -n craterstats python=3.8
    ```
1. Activate the virtual environment:

   ```
   conda activate craterstats
   ```
1. Install the craterstats package with its dependencies:

   ```
   pip install craterstats
   ```

 
# Quick demonstration

After installation, the following command will produce a series of example output plots and data, demonstrating the main features of the software. Plot image files are placed into the subfolder `demo/` of the current folder, while text output – including the full command lines as they could be typed to generate the output – goes to the terminal window.
    
    craterstats -demo

# Normal start

Launch the miniforge prompt and activate the virtual environment:
   ```
   conda activate craterstats
   ```
On Windows, you can alternatively create a desktop shortcut with this target: 

```
%windir%\system32\cmd.exe "/K" %homedrive%%homepath%\miniforge3\Scripts\activate.bat craterstats
```

# Upgrade 

If you later need to upgrade to a newer version, use:
   ```
   pip install --upgrade craterstats
   ```


# Usage

The program operates through the command line to produce output in the form of publication or presentation ready graphics, or tabulated analysis results for further processing.

There are two parts to creating a Craterstats plot:

1. Specify the type of plot and any characteristics which apply to the analysis as a whole, e.g. whether differential, cumulative or other data presentation; the chronology system, displayed axis ranges

2. Specify the data to be overplotted, and which chronology model evaluations should be applied to it

In the following example, the first items define characteristics for the whole plot: `-cs neukumivanov` specifies the chronology system, *Mars, Neukum-Ivanov (2001)* 
(any unambiguous abbreviation is acceptable), and the `-title Example plot` adds the chosen title.

The `-p` indicates the start of an overplot definition, which should come after the part 1 settings. Following this, the path to the data source is given (note that %sample% is a path abbreviation to a craterstats installation directory): this will produce a simple data plot with the default binning, colour and plot symbol. After the second `-p`, an additional overplot is specified: this time, a poisson age evaluation for the diameter range 0.2–0.7 km. Note that parameters within an overplot definition are separated by a `,`.  

    craterstats -cs neukumivanov -title Example plot -p source=%sample%/Pickering.scc -p type=poisson,range=[.2,.7]

A plot image file is created in the current folder with the same name `Pickering.png`. The output path or name can be changed with the `-o` option.  Different file types can be produced by giving the appropriate extension or with the `-f` option. 
Supported types are: png, jpg, tif, pdf, svg, txt, stat (multiple types can be specified, e.g. `-f png txt`)

An additional text file is created with the name `Pickering.cs` which contains the command line parameters used to create the plot. Sometimes it may be convenient 
to edit this file to modify the plot, which can then be regenerated with the shorter command:

    craterstats -i Pickering.cs

Tables of chronology systems, equilibrium functions and epoch systems – which can be used with the `-cs`, `-ef` and `-ep` options – may be listed with the following command:

    craterstats -lcs

These items may specifed by their index number, e.g. `-cs 4`, or using any unambiguous abbreviated form, e.g. `-cs ida`. Similarly, `-ef standard` or `-ef trask` is equivalent to `-ef 1` 

Numbered tables of plot symbols and colours – which can be used with the `psym=` and `colour=` options – may be listed with the following command:

    craterstats -lpc

and can likewise be specified by index or abbreviation, e.g. `psym=1`, `psym=circle` or `psym=o` all select a circle; `colour=2`, `colour=green` or `colour=gr` select green.  

Differential plots are produced by default. To switch to a different kind, e.g. cumulative, add `-pr 1` or `-pr cumulative` to the part 1 settings. Other possibilities are: 3 - relative (R), 4 - Hartmann, 5 - chronology, 6 - rate.

The complete set of options can be seen with:

    craterstats --help

To simplify the construction of the command line, certain plot properties are persistent. If, for example, you specify `source=C:\tmp\area1.scc` in the first overplot, this becomes the default for subsequent overplots. Only when you wish to introduce a different source file do you need to specify it again. This also applies to other properties where it is useful, including `binning=`, `colour=` and `psym=`.


# Examples

Differential plot with Poisson age evaluations, equilibrium function, and epoch system

    craterstats -cs neukumivanov -ep mars -ef standard -p source=%sample%/Pickering.scc -p type=poisson,range=[2,5],offset_age=[2,-2] -p range=[.2,.7]

Differential plot with two differential fit age evaluations

    craterstats -cs NI2001 -p source=%sample%/Pickering.scc,psym=o -p type=d-fit,range=[.2,.7],isochron=1 -p range=[2,5],colour=red

Differential age fits with 10/decade binning

    craterstats -cs neukumivanov -p source=%sample%/Pickering.scc,psym=o,binning=10/decade -p type=d-fit,range=[.2,.7],isochron=1 -p range=[2,5],colour=red

Cumulative fit with resurfacing correction

    craterstats -pr cumul -cs neukumivanov -p source=%sample%/Pickering.scc,psym=sq -p type=c-fit,range=[.2,.7],resurf=1,psym=fsq


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

Full references for specific chronology or other functions are listed with the function definitions in `config/functions.txt`.

A set of introductory slides to the methods and an earlier version of the software is [here](https://github.com/ggmichael/craterstats/tree/main/docs),
as well an update on this python version. Note that some command syntax has changed since the slides were produced.





