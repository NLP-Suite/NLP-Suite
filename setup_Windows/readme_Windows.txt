Installation Instructions for Windows

You can find detailed installation instructions at the NLP Suitte GitHub pages https://github.com/NLP-Suite/NLP-Suite/wiki/Install-the-NLP-Suite.

1. Unzip the downloaded file. The folder should be called NLP-Suite.

2.	Enter the NLP-Suite folder and the setup_Windows subfolder.
 
3. Run STEP1-install_anaconda by double-clicking on it to install Anaconda and Python.
	Running STEP1 will not affect Anaconda if you already have it installed on your machine.
	Installation may take a while. Do not turn off your machine or start running STEP2 until STEP1 is complete. When installation is complete you will see the message "The Anaconda3 installation is complete." in command line/prompt.

	If something goes fundamentally wrong while running STEP1 and you get errors in both STEP1 and STEP2, you may need to delete Anaconda and reinstall it. To do that, in command line/prompt type:
	rd -r "$Home\anaconda"
	Press enter to run the command and then run STEP1 again.

4. Once STEP1 is finished, run STEP2-install_components through right-click -> run using Powershell 
	STEP2 will install all Python components via requirements.txt and Java files and may take quite a while. STEP2 will also install torch and torchvision, nltk, and spaCy en language pack. Please, be patient.

	If something goes fundamentally wrong while running STEP1 and you get errors in both STEP1 and STEP2, you may need to delete Anaconda and reinstall it. To do that, in command line/prompt type:
	rm -rf ~/anaconda
	Press enter to run the command and then run STEP1 again.

NLP Suite updates & Git instructions

The NLP Suite updates the scripts automatically to the lastest release available on GitHub every time you exit the NLP Suite. The update features rely on Git. Please download Git at this link https://git-scm.com/downloads (select the Windows link; it will automatically detect whether your machine is 32-bit or 64-bit on the top line Click here to download the latest...). Run the downloaded exe file.

Run Instructions

The Windows installation script creates a desktop NLP Suite icon. Double click the NLP_Suite icon on your desktop to run the NLP Suite.
You can also click on the run_NLP-Suite.bat file directly to run the NLP Suite.

NLP environment shortcuts for Windows

Run the NLP-environment_shortcut_add.bat file by double clicking it. This will add a shortcut to your command prompt that will allow you to type NLP and automatically be placed into your NLP Anaconda environment as well as in your NLP Suite Directory. You can remove the alias this script creates by running the NLP_environmen_shortcut_remove.bat.
