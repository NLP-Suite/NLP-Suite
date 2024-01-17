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

- The NLP Suite updates automatically every time you exit, using Git.

### Mac Running Bash/Zsh

- For macOS 10.15 (Catalina) and later, use `zsh` instead of `bash` for compatibility.
- Switch to zsh using `chsh -s /bin/zsh` and `conda init zsh`.

### Useful Anaconda & Pip Commands

#### Conda Commands

1. Activate environment: `conda activate NLP`
2. Create new environment: `conda create -n NLP -y`
3. Delete an environment: `conda env remove --name NLP`
4. List all environments: `conda info --envs` or `conda env list`
5. List all Python packages: `conda list`
6. Uninstall Python: `conda uninstall Python`

#### Pip Commands

1. Upgrade pip: `python -m pip install --upgrade pip`
2. Install Python packages: `pip install [package_name]`
3. Uninstall Python packages: `pip uninstall [package_name]`
4. Install specific package version: `pip install [package_name]~=[version]`
5. Permission error solution: Add `--user` to the pip command
6. More on pip errors: Ensure the package is installed in the correct environment
7. Show package version: `pip show [package_name]`

#### Prompt Commands

1. Locate Python: `where Python`
2. Show Java JDK version: `java -version` or `java --version`
3. Show Python version: `python --version`
4. Remove Anaconda: `rm -rf ~/anaconda`

---
