
# Craterstats

This is a reimplementation in Python 3.8 of the CraterstatsII software, a tool to analyse and plot crater count data for planetary surface dating.

# Installation

The `craterstats` package is available on pypi.
There are 2 recommended way to receive the required dependencies for the package.

1. If you are installing it specifically to only run `craterstats``, the following is suggested:

- (recommended, but not required:) install conda via the [miniforge or mambaforge installer](https://github.com/conda-forge/miniforge)
- create a virtual environment for craterstats, with conda, e.g.: `conda create -n craterstats python=3.8`
- activate the virtual environment, with conda, e.g.: `conda activate craterstats`
- then execute the pip install: `pip install craterstats`

This will get all dependencies from the pypi server.

2. Alternatively, if you intend to add the `craterstats` package to other libraries and packages you are managing within a virtual environment, we recommend to use conda like so:

- create craterstats conda environment: `conda create -n craterstats python=3.8`
- activate the env: `conda activate craterstats`
- use the requirements file of this package to install the dependencies: `mamba install --file ./requirements.txt`
- finish by getting `craterstats` from pypi: `pip install craterstats`

The advantage of this is, that conda/mamba will take care that your dependencies fit to the rest of your other libraries/packages that you install later on.

Note, that conda runs equally well on on major OS platforms, hence it is our recommendation for virtual envs (but there are other frameworks that do this as well.)

 
# Quick demonstration

After installation, the following command will produce a series of example output plots and data, demonstrating the main features of the software. Plot image files are placed into the subfolder `demo/`, while text output – including the full command lines as they could be typed to generate the output – goes to the terminal window.
    
    craterstats -demo

# Normal start

Open a command prompt/terminal window and run the activate script:
   
Windows:

    c:\craterstats\Scripts\activate

Alternatively, copy windows_shortcut/craterstats.lnk to the Windows desktop to create a startup icon. 
    
Linux:

    source ~/.craterstats/bin/activate

# Usage

The program operates through the command line to produce output in the form of publication or presentation ready graphics, or tabulated analysis results for further processing.

There are two parts to creating a Craterstats plot:

1. Specify the type of plot and any characteristics which apply to the analysis as a whole, e.g. whether differential, cumulative of other data presentation; the chronology system, displayed axis ranges

2. Specify the data to be overplotted, and which chronology model evaluations should be applied to it

In the following example, the first items define characteristics for the whole plot: `-cs neukumivanov` specifies chronology system 4, *Mars, Neukum-Ivanov (2001)* , and the `-title Example plot` adds the chosen title.

The `-p` indicates the start of an overplot definition, which should come after the part 1 settings. Following this, the path to the data source is given: this will produce a simple data plot with the default binning, colour and plot symbol. After the second `-p`, an additional overplot is specified: this time, a poisson age evaluation for the diameter range 0.2–0.7 km. Note that parameters within an overplot definition are separated by a `,`.  

    craterstats -cs neukumivanov -title Example plot -p source=craterstats/sample/Pickering.scc -p type=poisson,range=[.2,.7]

By default, an output file is created in the current folder with the name `out.png`. The output path or name can be set with the `-o` option.  Different file types can be produced by giving the appropriate extension or with the `-f` option. Supported types are: png, jpg, tif, pdf, svg, txt.

Tables of chronology systems, equilibrium functions and epoch systems – which can be used with the `-cs`, `-ef` and `-ep` options – may be listed with the following command:

    craterstats -lcs

These items may specifed by their index number, e.g. `-cs 4`, or using any unambiguous abbreviated form, e.g. `-cs ida`. Similarly, `-ef standard` or `-ef trask` is equivalent to `-ef 1` 

Numbered tables of plot symbols and colours – which can be used with the `psym=` and `colour=` options – may be listed with the following command:

    craterstats -lpc

and can likewise be specified by index or abbreviation, e.g. `psym=1`, `psym=circle` or `psym=o` all select a circle; `colour=2`, `colour=green` or `colour=gr` select green.  

Differential plots are produced by default. To switch to a different kind, e.g. cumulative, add `-pr 1` or `-pr cum` to the part 1 settings. Other possibilities are: 3 - relative (R), 4 - Hartmann, 5 - chronology, 6 - rate.

The complete set of options can be seen with:

    craterstats --help

# Examples

Differential plot with Poisson age evaluations, equilibrium function, and epoch system

    craterstats -cs neukumivanov -ep mars -ef standard -p source=src/craterstats/sample/Pickering.scc -p type=poisson,range=[2,5],offset_age=[2,-2] -p range=[.2,.7]

Differential plot with two differential fit age evaluations

    craterstats -cs neukumivanov -p source=src/craterstats/sample/Pickering.scc,psym=o -p type=d-fit,range=[.2,.7],isochron=1 -p range=[2,5],colour=red

Differential age fits with 10/decade binning

    craterstats -cs neukumivanov -p source=src/craterstats/sample/Pickering.scc,psym=o,binning=10/decade -p type=d-fit,range=[.2,.7],isochron=1 -p range=[2,5],colour=red

Cumulative fit with resurfacing correction

    craterstats -pr cumul -cs neukumivanov -p source=src/craterstats/sample/Pickering.scc,psym=sq -p type=c-fit,range=[.2,.7],resurf=1,psym=fsq


# Additional information

The useable chronology systems, equilibrium functions and epoch systems are defined in the text file `config/functions.txt`. User functions may be added here, following the same format.

There is a text file `config/default.plt` which contains all the default plot settings. This may be modified to suit the choices you use most often.

To simplify the construction of the command line, certain plot properties are 'sticky'. If, for example, you specify `source=craterstats/sample/Pickering.scc` in the first overplot, this becomes the default for subsequent overplots. Only if you wish to introduce a different source file do you need to specify it again. This applies to other properties where it is useful, including `binning=`, `colour=` and `psym=`.

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

A set of introductory slides from a previous workshop is available here: [https://pdsimage2.wr.usgs.gov/pub/pigpen/tutorials/FreieUni_Workshop2012/](https://pdsimage2.wr.usgs.gov/pub/pigpen/tutorials/FreieUni_Workshop2012/)




