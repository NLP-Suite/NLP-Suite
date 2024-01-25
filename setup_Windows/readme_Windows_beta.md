# Installation Instructions for Windows

## Table of Contents

1. **Getting started**
2. **Moving or Renaming your NLP-Suite folder**
3. **Installing the NLP Suite in three easy steps**
4. **Installing Git**
5. **Running the NLP Suite**
6. **Updating the NLP Suite**
7. **Useful conda & pip commands (prompt)**
   - conda commands
   - pip commands
   - prompt commands

Detailed installation instructions are available at the [NLP Suite GitHub pages](https://github.com/NLP-Suite/NLP-Suite/wiki/Install-the-NLP-Suite).

### Getting started

1. Unzip the file downloaded from [GitHub](https://github.com/NLP-Suite/NLP-Suite/releases). The folder should be named `NLP-Suite`.
2. Enter the `NLP-Suite` folder and the `setup_Windows` subfolder.
3. Be careful! Windows new updates may affect the performance in NLP Suite due to its automatic introduction of the Onedrive saving concept. If you have a Onedrive subscription of your computer, you MUST NOT download the software in the Onedrive folder. Please see what you could do at: https://www.youtube.com/watch?v=1ML4jYseA3A to avoid such problem. Note: it might not be absolutely necessary to stop downloading everything to your onedrive, however, you must be careful not to cause a problem of installing NLP Suite on Onedrive folder. If you see a "Desktop" folder but it is located where the left-hand bar says "OneDrive", that will be INCORRECT and you must correct the problem. 

### Moving or Renaming your NLP-Suite folder

- If you rename your NLP Suite folder or move it to a different location (e.g., from Desktop to Documents) and are using the Desktop icon to run the NLP Suite, you will need to change the target path of the icon. Right-click on the icon, click on Properties, and edit the Target value.

### Installing the NLP Suite in the following steps

Note: All instructions are written consequentially and in a linear way. Non of the steps (i.e. STEP1, Pre STEP2, ...) could be concurrently executed. Attempts to do so may result in more complicated, and in extreme cases, costly-to-recover issues. However, once a "STEP" is successful as indicated in this manual, it is unlikely to be reverted by future operations, therefore a re-doing of an existing step may not be necessary unless in extenuating circumstances. In all steps from STEP1 through STEP2, including intermediates, internet connection is absolutely necessary. 

1. **STEP1**
   - Run `STEP1-install_anaconda.bat` by double-clicking on it to install Anaconda and Python.
   - Running STEP1 will not affect Anaconda if you already have it installed on your machine.
   - Installation may take a while. Do not turn off your machine or start running STEP2 until STEP1 is complete. When installation is complete you will see the message "The Anaconda3 installation is complete." in command line/prompt.
   - If something goes fundamentally wrong while running STEP1 and you get errors in both STEP1 and STEP2, you may need to uninstall Anaconda and reinstall it. To do that, you will need to run the PowerShell command with these three steps:
     1. Right-click the Windows button on the lower left corner.
     2. Select "Windows PowerShell (Admin)".
     3. Run `rm -rf ~/anaconda`.
     4. Run STEP1 again.

2. **POST-STEP1 CHECKS. Recommended for Windows 10 or higher. Not absolutely necessary for Windows 9 or lower. **
   - Python on Windows newest releases (Win 11, etc.) are known to be distorted by Microsoft's set-ups. 
   - Test A: Before you proceed to Pre-STEP2 and further, it is important you test that python is working correctly to avoid failure of subsequent steps.
   - Step i. To test, first go to the home and find `Command Prompt` (CMD). If you don't know how to open it, you should actively google search, such as: https://www.howtogeek.com/235101/10-ways-to-open-the-command-prompt-in-windows-10/.
   - Step ii. Once you open CMD, you should proceed with typing a `python` and press enter; or type `python3` and press enter. 
   - Step iii: If an error like shown in the video occurs in this paragraph occurs, you must proceed with the video's instruction to proceed with eliminating the auto-Microsoft Store pop-up. Please look at it: https://www.youtube.com/watch?v=umyc4Yo87Qc for more information.
   - Test A Outcome: When you type `python` and something like `Type "help", "copyright", "credits" or "license" for more information. >>>` occurs, that suggest a successful elimination. Please proceed to Test B.
   - Test A failure: Seeing anything else, including things like `python is not recognized as an internal or external command` suggests strongly something wrong with STEP1, and further proceeding is discouraged. Please restart STEP1 and if failure persists after you have done research on Google and youtube videos, contact the develop team. 
   - Test B : Initiate a new cmd window and test for anaconda installation. You should type `conda` in the command line prompt window, and see if an appropriate log was output.
   - Test B Outcome: You should read something like:
`usage: conda [-h] [-V] command ...`
`conda is a tool for managing and deploying applications, environments and packages.`
`Options:.......`
   - Test B Failure: Anything other than shown is likely indication of failure. Please restart STEP1 and if failure persists and if failure persists after you have done research on Google and youtube videos, contact the develop team. 
   - Motives and Purpose: Why all the trouble? NLP Suite is known to be running from a lower-level than most "Applications" - that are well-packaged such that frequent development could be initiated through Git rather than releasing downloadable executables. Further, student users could contribute easily as backend python code is more directly exposed to the users, so any fundamental errors could be easily identified by code inspection. Therefore, a development environment is recommended for all users. 

3. **Pre-STEP2: Installing Git**
   - Download Git from [here](https://git-scm.com/downloads). The website will detect if your machine is 32-bit or 64-bit. Run the downloaded exe file.

4. **STEP2**
   - STEP2 relies on Git. If you have not run "Pre-STEP2: Installing Git", it will not be successful.
   - STEP2 also relies on STEP1's Python installation. If you do not have STEP1 complete, it will not be successful. If STEP1 is not fully complete, STEP2 will not be successful either.  
   - After completing STEP1, run `STEP2-install_NLP-Suite.ps1` using right-click -> run using Powershell.
   - If this method above invokes a red message, please follow this youtube tutorials: https://www.youtube.com/watch?v=s3sWPUBLxmc if an Execution Policy error is thrown. 
   - If you don't understand how to even open Powershell, please visit: https://www.youtube.com/watch?v=bs8qfwNFQ24 for information on using Powershells.
   - This step installs Python components via `requirements.txt`, Java files, and other necessary components. 

5. **STEP3**
   - After finishing STEP2, run `STEP3-NLP-environment.bat` by double-clicking on it.
   - This step adds a shortcut to quickly access the NLP Anaconda environment and NLP Suite Directory in the command line/prompt.
   - To remove the NLP alias, run `NLP_environment_shortcut_remove.bat`.

### Running the NLP Suite

- The Windows installation script creates a desktop NLP Suite icon. Double-click the `NLP_Suite` icon on your desktop or click on the `run_NLP-Suite.bat` file in `setup_Windows`. You can also click on the `run_NLP-Suite.bat` file in setup_Windows to run the NLP Suite.
- Note for developers. In the likelihood that efficiency may be desired, you should navigate to the `src` folder, go to the terminal and use either `python3 NLP_welcome_main.py` (or any other main.py with progression of the course), or `python NLP_welcome_main.py` (or any other main.py with progression of the course, e.g. NLP_menu_main.py). 

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
   - If you installed pandas in the `base` environment, it will not be recognized by the NLP Suite. You need to uninstall it from the base environment and install it in the NLP environment after activating the NLP environmant via the command

conda activate NLP

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
