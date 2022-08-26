						Installation Instructions for Windows

Table of Contents

Getting started
Moving or Renaming your NLP-Suite folder
Installing the NLP Suite in three easy steps
Installing Git
Running the NLP Suite
Updating the NLP Suite
Useful conda & pip commands (prompt)
	conda commands
	pip commands
	prompt commands
	
You can find detailed installation instructions at the NLP Suitte GitHub pages https://github.com/NLP-Suite/NLP-Suite/wiki/Install-the-NLP-Suite.

Getting started

	1. Unzip the file downloaded from GitHub (https://github.com/NLP-Suite/NLP-Suite/releases). The folder should be called NLP-Suite.

	2. Enter the NLP-Suite folder and the setup_Windows subfolder.

Moving or Renaming your NLP-Suite folder
	
		If you rename your NLP Suite folder or move it to a different location (e.g., from Desktop to Documents) and you are using the Desktop icon too run the NLP Suite, you will need to change the target path of the icon. How? Right click on the icon, click on Properties, edit the Target value.

Installing the NLP Suite in three easy steps
 
	1. STEP1
	
		Run STEP1-install_anaconda by double-clicking on it to install Anaconda and Python.
		Running STEP1 will not affect Anaconda if you already have it installed on your machine.
		Installation may take a while. Do not turn off your machine or start running STEP2 until STEP1 is complete. When installation is complete you will see the message "The Anaconda3 installation is complete." in command line/prompt.

		If something goes fundamentally wrong while running STEP1 and you get errors in both STEP1 and STEP2, you may need to uninstall Anaconda and reinstall it. To do that, you will need to run the PowerShell command with these three steps:
			1.	Right click the windows button on the lower left corner;
			2.	Select "Windows PowerShell (Admin)"
			3.	Run the rd – r "$Home\Anaconda3"
		Run STEP1 again.

	2. STEP2
	
		Once STEP1 is finished, run STEP2-install_components through right-click -> run using Powershell 

		STEP2 will install all Python components via requirements.txt and Java files and may take quite a while. STEP2 will also install torch and torchvision, nltk, and spaCy en language pack. Please, be patient.

		If something goes fundamentally wrong while running STEP1 and you get errors in both STEP1 and STEP2, you may need to delete Anaconda and reinstall it. To do that, in command line/prompt type:
		rm -rf ~/anaconda
		Press enter to run the command and then run STEP1 again.
		
		STEP2 relies on Git.

Installing Git

	The Git website will automatically detect whether your machine is 32-bit or 64-bit on the top line Click here to download the latest...

	STEP2 relies on Git. Please download Git at this link https://git-scm.com/downloads/win (the Git website will automatically detect whether your machine is 32-bit or 64-bit; on the top line Click here to download the latest...). Run the downloaded exe file.

	3. STEP3
	
		Once STEP2 is finished, run STEP3-NLP-environment.bat by double-clicking on it. STEP3 will add a shortcut that will allow you to type NLP (CAPS) after opening a command line/ prompt and automatically be placed into your NLP Anaconda environment as well as in your NLP Suite Directory. You need to run the command only once (but no harm if you accidentally do that repeatedly).
		
		THIS COMMAND IS VERY HELPFUL IF YOU NEED TO USE pip TO INSTALL PYTHON PACKAGES; THESE PYTHON PACKAGES MUST BE INSTALLED IN THE NLP ENVIRONMENT, RATHER THAN base, FOR THE NLP SUITE TO WORK. You can remove the NLP alias this script creates by running the NLP_environment_shortcut_remove.bat.

Running the NLP Suite

	The Windows installation script creates a desktop NLP Suite icon. Double click the NLP_Suite icon on your desktop to run the NLP Suite.
	You can also click on the run_NLP-Suite.bat file in setup_Windows to run the NLP Suite.

Updating the NLP Suite

	The NLP Suite updates automatically to the lastest release available on GitHub every time you exit the NLP Suite. The update features rely on Git.

Useful Anaconda & pip commands

	Commands listed here - conda and pip - all work from command line/prommpt

	1. conda commands
	2. pip commands
	3. prompt commands

	conda commands

		1. Change/activate environment

			conda activate NLP 

			will place you in a specific environment (e.g., NLP)

		2. Create a new environment

			conda create -n NLP -y

			will re-create the NLP environment that you may have accidentally deleted. You will then need to run conda activate NLP and CD to the NLP folder then python -m pip install -r requirements.txt or python3 -m pip install -r requirements.txt to reinstall all packages and be back to where you were before deleting the NLP environment.  

		3. Delete an environment

			conda deactive
			conda env remove --name NLP

			  will delete an environment (i.e., NLP Suite) wrongly created or no longer necessary. 

		4. List all environments

			conda info --envs
			conda env list

			either command will give you a list of the environments on your machine; you will see at least two environments, base and NLP.

		5. List all Python packages

			conda list

			will give you a list of all Python packages installed in a specific environment; make sure to be in the right environment by using conda activate.

			If you run the command conda list from the anaconda prompt, rather than from a specific environment, you will list all installed packages in all environments.

		6. Uninstall Python

			conda uninstall Python

	pip commands

		The pip command: What is pip?  

		pip is a package-management system written in Python used to install and manage software packages. Thus, if you open a command line/prompt and type


		1. upgrade pip to latest version
		
			python -m pip install --upgrade pip
		
		2. install a Python packages

			pip install pandas

			will install the pandas package

			To force a re-installment of a package with all its dependencies, use the command
			
			pip install --upgrade --force-reinstall pandas

		3. uninstall a Python packages
		
			pip uninstall pandas

			will uninstall a package (e.g., pandas)

		4. install a Python package version  

			Python scripts are VERY sensitive to the package version used to create the script. To ensure that the package will work on your computer, use the following command to install the required package version. 

			To install a specific version of a package run the command

			pip install pandas~=1.2.1

			will install a specific version of a package (e.g., pandas 1.2.1)

		5. Permission error with pip install

			The installation of some packages (e.g., pdfminer.six) may give you a permission error. In that case, add --user to the pip command, for instance, 

			pip install pdfminer.six --user

		6. More errors with pip command

			If, after installing a package via pip install, the NLP Suite warns you that the package you have just installed is not installed, you have probably installed the package in the wrong environment (e.g., base) and not in NLP.

			All Python packages are installed in specific Anaconda environments. The NLP Suite is setup in the NLP environment. If you open a command line/terminal most likely it will open the base environment.

			If base appears in command line/terminal, you are in the wrong environment.

			If you installed pandas in the base environment, it will not be recognized by the NLP Suite. You need to uninstall it from the base environment and install it in the NLP environment after activating the NLP environmant via conda activate NLP.

		7. Show the version of Python package

			pip show pandas

			will give you the version of any package (e.g., pandas) installed in the selected environment

	prompt commands
										
		1. where

			where Python
			
			will give the list of all the locations where Python is installed

		2. Python version
		
			python --version
			
			will tell you which Python version you are running

		3. Java version
		
			java -version
			
			will tell you which Java version you are running
