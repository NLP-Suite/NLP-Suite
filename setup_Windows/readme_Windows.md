# Windows
## Installation Instructions

1. Unzip the downloaded file and enter the extracted folder

![NLP Suite Folder](https://github.com/NLP-Suite/NLP-Suite/blob/current-stable/images/image001.png?raw=true)

- The folder should be called NLP-Suite. The extracted content should be like this:

![NLP Suite Folder](https://github.com/NLP-Suite/NLP-Suite/blob/current-stable/images/image002.png?raw=true)
 
2.	Enter the setup_Windows folder. Run "STEP1-install_anaconda" by double-clicking on it.
- SKIP THIS STEP IF YOU ALREADY HAVE ANACONDA INSTALLED ON YOUR MACHINE 
- If you would like to skip this step, make sure you have Anaconda in $PATH. One way to check if you do is to type conda in a command-line window, press enter, and see if there is an error.

![NLP Suite Folder](https://github.com/NLP-Suite/NLP-Suite/blob/current-stable/images/image003.png?raw=true)
Example of properly installed Anaconda in PATH
 
![NLP Suite Folder](https://github.com/NLP-Suite/NLP-Suite/blob/current-stable/images/image004.png?raw=true)
Example of missing Anaconda in PATH
 
3.	Run "STEP2-install_components" through right-click -> run using Powershell 
 
![NLP Suite Folder](https://github.com/NLP-Suite/NLP-Suite/blob/current-stable/images/image005.png?raw=true)

4. Double click to run setup_auto_update.bat

- The auto update feature relies on Git. Please download Git through [this link](https://git-scm.com/downloads) if it hasn’t been installed.

## Update Instructions

There are two ways of updating to the newest NLP Suite version.

1. Double click update_NLP-Suite.bat on your local machine every time you want to get new/changed files from GitHub.
2. Double click on update_NLP-Suite_auto.bat and, from then on, when exiting the NLP Suite new/changed files will be automatically pulled from GitHub. You only need to run update_NLP-Suite_auto.bat once.

## Run Instructions
The Windows installation script creates an NLP Suite desktop icon. Double click the NLP_Suite icon on your desktop to run the Suite. You can also click on the run_NLP-Suite.bat directly.
 
## NLP environment shortcuts for Windows
Run the NLP-environment_shortcut_add.bat file by double clicking it. This will add a shortcut to your command prompt that will allow you to type nlp and automatically be placed into your NLP Anaconda environment as well as in your NLP Suite Directory. You can remove the alias this script creates by running the NLP_environmen_shortcut_remove.bat.

![NLP Suite Folder](https://github.com/NLP-Suite/NLP-Suite/blob/current-stable/images/image006.png?raw=true)