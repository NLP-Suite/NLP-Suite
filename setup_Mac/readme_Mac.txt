Installation Instructions for Mac

You can find detailed installation instructions at the NLP Suitte GitHub pages https://github.com/NLP-Suite/NLP-Suite/wiki/Install-the-NLP-Suite.

1. Unzip the downloaded file. The folder should be called NLP-Suite.

2.	Enter the NLP-Suite folder and the setup_Mac subfolder.
 
3. Run STEP1-install_anaconda by double-clicking on it to install Anaconda and Python. Click "install" if prompted.
	Running STEP1 will not affect Anaconda if you already have it installed on your machine.

4. Once STEP1 is finished, run STEP2-install_components through right-click -> run using Powershell 
	STEP2 will install all Python components via requirements.txt and Java files and may take quite a while. STEP2 will also install torch and torchvision, nltk, and spaCy en language pack. Please, be patient.

Update Instructions

There are two ways of updating to the newest NLP Suite version.

1. Double click update_NLP-Suite.command on your local machine every time you want to get new/changed files from GitHub.
2. Double click on update_NLP-Suite_auto.command and, from then on, when exiting the NLP Suite new/changed files will be automatically pulled from GitHub. You only need to run update_NLP-Suite_auto.command once.
The update_NLP-Suite_auto.command ONLY WORKS IF YOU OPEN THE NLP SUITE FROM THE run_NLP-Suite.command. IT DOES NOT WORK IF YOU RUN IN COMMAND/PROMPT python NLP_welcome_main.py or python NLP_menu_main.py 

The update features rely on Git. Please download Git at this link https://git-scm.com/downloads, if it hasn’t been installed already.

Run Instructions

The Mac installation script creates a desktop NLP Suite icon. Double click the NLP_Suite icon on your desktop to run the NLP Suite.
You can also click on the run_NLP-Suite.command file directly to run the NLP Suite.

NLP environment shortcuts for Mac

Run the NLP-environment_shortcut_add.command file by double clicking it. This will add a shortcut to your command prompt that will allow you to type NLP and automatically be placed into your NLP Anaconda environment as well as in your NLP Suite Directory. You can remove the alias this script creates by running the NLP_environmen_shortcut_remove.command.
