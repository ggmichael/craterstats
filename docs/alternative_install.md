
## 1. Simple conda environment and pip (Windows, MacOS, Linux)

Recommended if you plan to use other Python software in addition to Craterstats-III:

1. Install the conda environment manager using the [miniforge installer](https://github.com/conda-forge/miniforge#install) for your OS. 
1. Launch the Miniforge prompt (Windows) or any command prompt (MacOS, Linux) and enter the following to create a virtual environment for craterstats:
    ```
    conda create -n craterstats python=3.12
    ```
1. Activate the virtual environment:
   ```
   conda activate craterstats
   ```
1. Install the craterstats package with its dependencies:
   ```
   pip install craterstats
   ```
1. If on Windows, create a desktop shortcut for future start-up:
   ```
   craterstats --create_desktop_icon
   ```
   Modify properties for preferred start-up folder if desired.

### Normal start-up

1. Double-click the desktop icon if present. Otherwise, launch the Miniforge prompt (Windows) or any command prompt (MacOS, Linux) and activate the virtual environment:
   ```
   conda activate craterstats
   ```   
1. Begin entering `craterstats` commands.

### Upgrade 

If you later need to upgrade to a newer version, use:

    pip install --upgrade craterstats

In case of failure, it is always safe to delete the craterstats environment directory from `<userhome>/miniforge3/envs`, and reinstall fresh.

## 2. Pipx (Windows)

If Craterstats will be the only Python software you use, this is a straightforward set-up. 
Pipx can also be used on Linux/MacOS, but steps may differ slightly.

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

3. Install craterstats
 - Open fresh command prompt and enter 
```
pipx install craterstats
```
The `craterstats` command is subsequently available in every command prompt window.

### Upgrade

If you later need to upgrade your version of Craterstats-III, enter 
```
pipx upgrade craterstats
```

## 3. From github

This method of installation may allow you to test features in development that have not yet been included in a versioned release.
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

### Updating

You can update to the latest version on github using the command `git pull` from within the 
`craterstats-github` directory. If a new version reports missing packages, repeat the command:
   ```
   pip install -U -r craterstats/requirements.txt
   ```