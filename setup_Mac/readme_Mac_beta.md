# Installation Instructions for Mac

## Table of Contents

1. **Getting Started**
2. **Moving or Renaming your NLP-Suite Folder**
3. **Installing the NLP Suite in Three Easy Steps**
4. **Installing Git**
5. **Running the NLP Suite**
6. **Updating the NLP Suite**
7. **Mac Running Bash/Zsh**
8. **Useful Conda & Pip Commands**

Detailed installation instructions are available on the [NLP Suite GitHub pages](https://github.com/NLP-Suite/NLP-Suite/wiki/Install-the-NLP-Suite).

### Getting Started

1. Unzip the downloaded file. The folder should be called `NLP-Suite`.
2. Enter the `NLP-Suite` folder and the `setup_Mac` subfolder.

### Installing the NLP Suite in Three Easy Steps
1. **Preparation**
   - In the NEW Mac Systems, you must first navigate to the `Terminal` app on app. You can find it in `Launchpad` -> `Other` -> `Terminal`. Alternatively, you may find it by simply searching for this program on your software using Spotlight (What is Spotlight, the icon on top of the bar: https://support.apple.com/guide/terminal/aside/glos33eb8abd/2.14/mac/14.0). 
   - You should get familiar with the following commands using a terminal. This used not to be the case for an older version of Apple products, as Apple has released some updates to its security guidelines, making our current solution a bit more complicated than the prior releases. These commands helpful for this course are:
   1) cd [Some file / directory ]to direct yourself to another folder
   2) chmod +x [Some scripts, like .command] to get access
   3) sudo [Some scripts, like .command, .sh] to get admin access
   4) ./[Some scripts.command] to run scripts
   5) The action of dragging. This is a convenient way for you to let the Terminal identify the location of a folder, or a file.
   Since these write-ups may be unclear, you should visit this video for a demo on how to use Terminal for Mac users: https://youtu.be/st4cMWKt5FM
   You should read more at: https://developer.apple.com/library/archive/documentation/OpenSource/Conceptual/ShellScripting/shell_scripts/shell_scripts.html#//apple_ref/doc/uid/TP40004268-CH237-SW3
   - You should use `chmod +x [.command]` command for each of the .command files inside the setup-Mac folder that you have just visited and as shown in the demo video. You should do exactly as the video has shown. Once all three .command files are given access through the `chmod +x [.command]` way, you are then able to proceed with the following STEP1 - 3 instructions on installation. 
   - Note: if double click fails, please use the ./[.command] way as indicated in the video shown.

2. **STEP1**
   - Run `STEP1-install_anaconda.command` by double-clicking on it to install Anaconda and Python.
   - If you already have Anaconda, running STEP1 will not affect it.
   - Do not turn off your machine or start STEP2 until STEP1 is complete.

3. **Pre-STEP2**
   - STEP2 relies on Git. Download Git from [here](https://git-scm.com/download/mac).

4. **STEP2**
   - Run `STEP2-install_NLP-Suite.command` to install all Python components via `requirements.txt`, Java files, torch, torchvision, nltk, and spaCy en language pack.

5. **STEP3**
   - Once STEP2 is finished, run `STEP3-NLP-environment.command`.
   - STEP3 adds a shortcut for easy access to the NLP Anaconda environment.


### Running the NLP Suite

- To run the NLP Suite, click on the `run_NLP-Suite.command` file in `setup_Mac`.
- In the likelihood that it is unsuccessful, you must use `Terminal` again to complete the running as Apple has placed new restrictions. For more information, check this video: https://youtu.be/-FN9pCFG6DU

### Updating the NLP Suite

- The NLP Suite updates automatically to the latest release available on GitHub every time you exit the NLP Suite. This feature relies on Git.
- Note: if you click on the "CLOSE" button on the right lower corner, it will be successful - and is the only way. Invoking Task manager to force shut down, or directly using the "X" button on the top right might not be successful in updating.
- Check frequently if your NLP Suite is up-to-date by visiting the current github page for release history. If you notify an incorrect release history, in addition to correcting git, the easiest solution is simply to download the entire package from GitHub all over again.  

### Useful Anaconda & pip commands

Commands listed here - conda and pip - all work from the command line/prompt.

#### conda commands

1. **Change/activate environment**
   - `conda activate NLP`: Activates a specific environment (e.g., NLP).

2. **Create a new environment**
   - `conda create -n NLP -y`: Recreates the NLP environment if deleted.
   - will re-create the NLP environment that you may have accidentally deleted. You will then need to run 
         conda activate NLP 
         and CD to the NLP current stable src folder (e.g., cd C:\Users\rfranzo\Desktop\NLP-Suite\src)
         then 
         python -m pip install -r requirements.txt or python3 -m pip install -r requirements.txt to reinstall all packages and be back to where you were before deleting the NLP environment.  

3. **Delete an environment**
   - `conda deactive`
   - `conda env remove --name NLP`: Deletes an environment (e.g., NLP) wrongly created or no longer necessary. Avoid this operation unless you are convinced of such error. 

4. **List all environments**
   - `conda info --envs` or `conda env list`: Lists all environments on your machine. either command will give you a list of the environments on your machine; you will see at least two environments, base and NLP.

5. **List all Python packages**
   - `conda list`: Lists all Python packages in the current environment. will give you a list of all Python packages installed in a specific environment; make sure to be in the right environment by using conda activate. If you run the command conda list from the anaconda prompt, rather than from a specific environment, you will list all installed packages in all environments.

6. **Uninstall Python**
   - `conda uninstall Python` Please avoid this dangerous operation if possible. Advanced developers could use this command at discretion. 

#### pip commands

- **What is pip?**: A package(see below)-management system used to install and manage software packages in Python. Thus, if you open a command line/prompt and type.
- **What is a package**?
A package is a pre-written set of files that could be invoked (used) frequently, stored usually inside your system. Package is usually written with the intent of allowing a developer of a code to quickly execute a common operation, such as but not limited to: statistics on a table, operations on the files in system, network connection from command lines, sometimes using only 1 line or less to achieve the goal. A typical package is, however, several hundred lines or even more. The use of package makes code more succint and robust (less error-prone). Packages were usually the result of collaboration, and therefore, is subject to version change. Just as the common commercial software changes over time - new logo, new interface - packages also change versions frequently. This result in errors known as dependecy conflict, or other issues - some code were just so well-written (or poorly written on the flip side) - that it could only depend on features (or perhaps, bugs) in some particular packages. That is why at times you might encounter failure for NLP Suite to properly execute - the packages might not work in alignment, but we have tried our best in the newest release to avoid such errors, but exeptions may still pop up. In the likelihood you or developer identify that package is a root cause, please consider these following instructions: 
- **What is an environment**?
1. We need environment in this software! If you are a developer, or simply wants an organized computer, an environment is absolutely critical. An environment is like the Matrix movie, some virtual world of a sort. If you install packages in environment `A`, package will not auto-propagate to environment `B` automatically - though the environment manager, here known as `Anaconda`, could easily identify copies of such packages and move things quickly. 
2. In a given Anaconda interface, there are two environments: `base` and `NLP`. The base is default when you don't develop in an environment, the NLP, as constructed in STEP1 code, is tailored to NLP Suite. Environment host different packages, and switching environemnt may be a good way for you to track which packages are there. 

1. **Upgrade pip to the latest version**
   - `python -m pip install --upgrade pip`

2. **Install a Python package**
   - `pip install pandas`: Installs the pandas package.
   - To force reinstall with dependencies: `pip install --upgrade --force-reinstall pandas`

3. **Uninstall a Python package**
   - `pip uninstall pandas`: Uninstalls a package (e.g., pandas).

4. **Install a specific version of a Python package**
   - Python scripts are VERY sensitive to the package version used to create the script. To ensure that the package will work on your computer, use the following command to install the required package version.
   - E.g. `pip install pandas~=1.5.2`: Installs a specific version (e.g., pandas 1.5.2). Pandas is exclusely specific in this Software. It must be 1.5.2.

5. **Permission error with pip install**
   - The installation of some packages (e.g., pdfminer.six) may give you a permission error. In that case, add --user to the pip command, for instance, Add `--user` to the command, e.g., `pip install pdfminer.six --user`.

6. **Errors with pip command**
   - If, after installing a package via pip install, the NLP Suite warns you that the package you have just installed is not installed, you have probably installed the package in the wrong environment (e.g., base) and not in NLP.
   - All Python packages are installed in specific Anaconda environments. The NLP Suite is setup in the NLP environment. If you open a command line/terminal most likely it will open the base environment.
   - If base appears in command line/terminal, you are in the wrong environment.
   - If you installed pandas in the `base` environment, it will not be recognized by the NLP Suite. You need to uninstall it from the base environment and install it in the NLP environment after activating the NLP environmant via conda activate NLP.

7. **Show the version of a Python package**
   - `pip show pandas`: Shows the version of an installed package.
8. **Show all Python packages**
   - `pip freeze`: you should see a list of packages after this command. 

#### prompt commands

1. **where**
   - `where Python`: Lists all locations where Python is installed. In some version, you should write `where Python3`

2. **Python version**
   - `python --version`: Shows the current Python version.

3. **Java version**
   - `java -version`: Shows the current Java version. You must have Java installed to have this open. 

4. **Delete/remove Anaconda**
   - `rm -rf ~/anaconda`: Removes Anaconda from your system.
