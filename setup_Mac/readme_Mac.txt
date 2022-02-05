Installation Instructions for Mac

You can find detailed installation instructions at the NLP Suitte GitHub pages https://github.com/NLP-Suite/NLP-Suite/wiki/Install-the-NLP-Suite.

1. Unzip the downloaded file. The folder should be called NLP-Suite.

2.	Enter the NLP-Suite folder and the setup_Mac subfolder.
 
3. Run STEP1-install_anaconda by double-clicking on it to install Anaconda and Python. Click "install" if prompted.
	Running STEP1 will not affect Anaconda if you already have it installed on your machine.
	Do not turn off your machine or start running STEP2 until STEP1 is complete. When installation is complete you will see the message "The Anaconda3 installation is complete." in command line/prompt.			

	If something goes fundamentally wrong while running STEP1 and you get errors in both STEP1 and STEP2, you may need to delete Anaconda and reinstall it. To do that, in command line/prompt type:
	rm -rf ~/anaconda
	Press enter to run the command and then run STEP1 again.

4. Once STEP1 is finished, run STEP2-install_components through right-click -> run using Powershell 

	STEP2 relies on Git. Please download Git at this link https://git-scm.com/download/mac  (install Xcode if you do not have disk space problems; otherwise download the Binary installer).

	STEP2 will install all Python components via requirements.txt and Java files and may take quite a while. STEP2 will also install torch and torchvision, nltk, and spaCy en language pack. Please, be patient. Installatin of all files may take an hour or more.

5. Once STEP2 is finished, run STEP3-NLP-environment.command by double-clicking on it.

	STEP3 will add a shortcut that will allow you to type NLP (CAPS) after opening a command line/ prompt and automatically be placed  and automatically be placed into your NLP Anaconda environment as well as in your NLP Suite Directory. You need to run the command only once (but no harm if you accidentally do that repeatedly). THIS COMMAND IS VERY HELPFUL IF YOU NEED TO USE pip TO INSTALL PYTHON PACKAGES; THESE PYTHON PACKAGES MUST BE INSTALLED IN THE NLP ENVIRONMENT, RATHER THAN base, FOR THE NLP SUITE TO WORK. You can remove the NLP alias this script creates by running the NLP_environment_shortcut_remove.command.

NLP Suite updates & Git instructions

The NLP Suite updates the scripts automatically to the lastest release available on GitHub every time you exit the NLP Suite. The update features rely on Git.

Run Instructions

The Mac installation script does not create a desktop NLP Suite icon. You need to click on the run_NLP-Suite.command file in setup_Mac to run the NLP Suite.
