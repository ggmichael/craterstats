
# Craterstats

This is a reimplementation in Python 3.8 of the CraterstatsII software, a tool to analyse and plot crater count data for planetary surface dating.
 
# Quick start

After installation, the following command will produce a series of example output plots and data, demonstrating the main features of the software. Plot image files are placed into the subfolder `demo/`, while text output – including the full command lines as they could be typed to generate the output – goes to the terminal window.

    python craterstats.py -demo


# Usage

The program operates through the command line to produce output in the form of publication or presentation ready graphics, or tabulated analysis results for further processing.

There are two parts to creating a Craterstats plot:

1. Specify the type of plot and any characteristics which apply to the analysis as a whole, e.g. whether differential, cumulative of other data presentation; the chronology system, displayed axis ranges

2. Specify the data to be overplotted, and which chronology model evaluations should be applied to it

In the following example, the first items define characteristics for the whole plot: `-cs 3` specifies chronology system 3, *Mars, Neukum-Ivanov (2001)*, and the `-title Example plot` adds the chosen title.

The `-p` indicates the start of an overplot definition (this should come after the part 1 settings). Following this, the path to the data source is given: this will produce a simple data plot with the default binning, colour and plot symbol. After the second `-p`, an additional overplot is specified: this time, a poisson age evaluation for the diameter range 0.2–0.7 km. Note that parameters within an overplot definition are separated by a `,`.  

    python craterstats.py -cs 3 -title Example plot -p source=sample/Pickering.scc -p type=poisson,range=[.2,.7]

By default, an output file is created in the current folder with the name `out.png`. The output path or name can be set with the `-o` option.  Different file types can be produced by giving the appropriate extension or with the `-f` option. Supported types are: png, jpg, tif, pdf, svg, txt.

Also, by default, a differential plot was produced. To switch to a cumulative plot, add `-pi 1` to the part 1 settings. Other possibilities are: 3 - relative (R), 4 - Hartmann, 5 - chronology, 6 - rate.

Numbered tables of recognised chronology systems, equilibrium functions and epoch systems – which can be used with the `-cs`, `-ef` and `-ep` options – may be listed with the following command:

    python craterstats.py -lcs

Numbered tables of plot symbols and colours – which can be used with the `psym=` and `colour=` options – may be listed with the following command:

    python craterstats.py -lpc

The complete set of options can be seen with:

    python craterstats.py --help

# Additional information

The useable chronology systems, equilibrium functions and epoch systems are defined in the text file `config/functions.txt`. User functions may be added here, following the same format.

There is a text file `config/default.plt` which contains all the default plot settings. This may be modified to suit the choices you use most often.

To simplify the construction of the command line, certain plot properties are 'sticky'. If, for example, you specify `source=sample/Pickering.scc` in the first overplot, this becomes the default for subsequent overplots. Only if you wish to introduce a different source file do you need to specify it again. This applies to other properties where it is useful, including `binning=`, `colour=` and `psym=`.

