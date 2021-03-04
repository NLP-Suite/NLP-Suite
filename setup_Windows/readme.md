# Setup Instructions for Windows

1. Download the NLP Suite through [this link](https://github.com/NLP-Suite/NLP-Suite/releases).

2. Unzip the zip file to a location

3. Go to the extracted folder

4. Run "STEP1-install_anaconda" by double-clicking on it.
    - SKIP THIS STEP IF YOU ALREADY HAVE ANACONDA INSTALLED ON YOUR MACHINE
    - If you'd like to skip this step, make sure you have Anaconda in $PATH. One way to check is to type conda in a command-line window, press enter, and see if there is an error.

5. Run "STEP2-install_components" through right-click -> run using Powershell

6. Double click to run setup_auto_update.bat
    - The auto update feature replies on Git. Please download Git through [this link](https://git-scm.com/downloads).

If you encounter any problems, feel free to [start a new issue](https://github.com/NLP-Suite/NLP-Suite/issues/new/choose). For a list of current issues with the NLP Suite, [click here](https://github.com/NLP-Suite/NLP-Suite/issues).

# Update Instructions

There are two ways of updating to the newest NLP Suite version.
1. Double click `update.bat` on your local machine every time you want to get the newest files from GitHub.
2. Double click on `setup_auto_update.bat` and the NLP Suite will be automatomatically updated every time on exit. You only need to click on setup_auto_update.bat once.

## Shortcuts

Run the `add_shortcut.bat` file by double clicking it. This will add a shortcut to your command prompt that will allow you to type `nlp` and automatically be placed into your NLP Anaconda environment as well as in your NLP Suite Directory. You can remove the alias this script creates by running the `remove_shortcut.bat`.
