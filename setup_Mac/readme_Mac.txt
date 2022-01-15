Installation Instructions for Mac

You can find detailed installation instructions at the NLP Suitte GitHub pages https://github.com/NLP-Suite/NLP-Suite/wiki/Install-the-NLP-Suite.

1. Unzip the downloaded file. The folder should be called NLP-Suite.

2.	Enter the NLP-Suite folder and the setup_Mac subfolder.
 
3. Run STEP1-install_anaconda by double-clicking on it to install Anaconda and Python. Click "install" if prompted.
	Running STEP1 will not affect Anaconda if you already have it installed on your machine.

4. Once STEP1 is finished, run STEP2-install_components through right-click -> run using Powershell 
	STEP2 will install all Python components via requirements.txt and Java files and may take quite a while. STEP2 will also install torch and torchvision, nltk, and spaCy en language pack. Please, be patient. Installatin of all files may take an hour or more.

NLP Suite updates & Git instructions

The NLP Suite updates the scripts automatically to the lastest release available on GitHub every time you exit the NLP Suite. The update features rely on Git. Please download Git at this link https://git-scm.com/downloads, if it hasn’t been installed already.

Run Instructions

The Mac installation script creates a desktop NLP Suite icon. Double click the NLP_Suite icon on your desktop to run the NLP Suite.
You can also click on the run_NLP-Suite.command file directly to run the NLP Suite.

NLP environment shortcuts for Mac

Run the NLP-environment_shortcut_add.command file by double clicking it. This will add a shortcut to your command prompt that will allow you to type NLP and automatically be placed into your NLP Anaconda environment as well as in your NLP Suite Directory. You can remove the alias this script creates by running the NLP_environmen_shortcut_remove.command.
