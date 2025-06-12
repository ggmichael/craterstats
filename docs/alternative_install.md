
# Alternative installation method for Windows

This method uses `pipx` instead of `conda` to isolate the Python environment. If Craterstats will be the only Python
software you use, this is a simpler set-up. 

1. Install Python
- Download Python 3.12 from https://www.python.org/downloads/
- Select _Add python.exe to PATH_ (but not _Use admin privileges_); choose _Install Now_

2. Install pipx

 - Open command prompt and enter
```
python -m pip install --user pipx
python -m pipx ensurepath
```
- Close command prompt

4. Install craterstats
 - Open fresh command prompt and enter 
```
pipx install craterstats
```
The `craterstats` command is subsequently available in every command prompt window.

(Pipx can be used on Linux/MacOS, but requires additional steps to ensure no conflict with the system Python)

# Installation from github

This method of installation may allow you to test features in development that have not yet been included in the versioned PyPi release.
Since development features may be fragile, this is probably only advisable if you are in contact with the author about a specific issue.

1. Install `conda` using the [miniforge installer](https://github.com/conda-forge/miniforge#miniforge3) for your OS, if not present.
1. Install `git` for your OS, if not present ([installing Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)).
1. Launch the Miniforge prompt (Windows) or any command prompt (MacOS, Linux) and enter the following to create a virtual environment for craterstats from github that is separate from the one for the PyPi version:

    ```
    conda create -n craterstats-github python=3.12
    ```
1. Activate the virtual environment:

   ```
   conda activate craterstats-github
   ```
1. Make a directory to hold the code (wherever you prefer, but probably in the user's home):

   ```
   mkdir craterstats-github
   cd craterstats-github   
   ```
1. Clone the code from github:

   ```
   git clone https://github.com/ggmichael/craterstats.git
   ```
1. Install the package requirements:
   ```
   pip install -r craterstats/requirements.txt
   ```
1. Create access to program using single-word `craterstats` command:

   Windows:
   ```
   echo python %cd%\craterstats\src\craterstats.py %*>%CONDA_PREFIX%\craterstats.bat
   ```
   Linux/MacOS [untested]:
   ```
   echo "python $PWD/craterstats/src/craterstats.py $@" > $CONDA_PREFIX/craterstats.sh
   ```
1. Check for successful installation with, e.g.:
   ```
   craterstats -about
   ```

## Updating

You can update to the latest version on github using the command `git pull` from within the 
`craterstats-github` directory. If a new version reports missing packages, repeat the command:
   ```
   pip install -U -r craterstats/requirements.txt
   ```