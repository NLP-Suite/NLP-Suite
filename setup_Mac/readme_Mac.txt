							Installation Instructions for Mac

Table of Contents

Getting started
Moving or Renaming your NLP-Suite folder
Installing the NLP Suite in three easy steps
Installing Git
Running the NLP Suite
Updating the NLP Suite
Mac running bash/zsh
Useful conda & pip commands (prompt)
	conda commands
	pip commands
	prompt commands

You can find detailed installation instructions at the NLP Suitte GitHub pages https://github.com/NLP-Suite/NLP-Suite/wiki/Install-the-NLP-Suite.

Getting started

	1. Unzip the downloaded file. The folder should be called NLP-Suite.

	2.	Enter the NLP-Suite folder and the setup_Mac subfolder.

Moving or Renaming your NLP-Suite folder
 
Installing the NLP Suite in three easy steps
 
	1. STEP1
		Run STEP1-install_anaconda.command by double-clicking on it to install Anaconda and Python. Click "install" if prompted.
		Running STEP1 will not affect Anaconda if you already have it installed on your machine.
		Do not turn off your machine or start running STEP2 until STEP1 is complete. When installation is complete you will see the message "The Anaconda3 installation is complete." in command line/prompt.			

		If something goes fundamentally wrong while running STEP1 and you get errors in both STEP1 and STEP2, you may need to delete Anaconda and reinstall it. To do that, in command line/prompt type:
		
		rm -rf ~/anaconda
		
		Press enter to run the command.
		Run STEP1 again.

	2. STEP2

		Run STEP2-install_NLP-Suite.command by double-clicking on it to install all Python components via requirements.txt and Java files and may take quite a while. STEP2 will also install torch and torchvision, nltk, and spaCy en language pack. Please, be patient. Installatin of all files may take an hour or more.

		If something goes fundamentally wrong while running STEP1 and you get errors in both STEP1 and STEP2, you may need to delete Anaconda and reinstall it (see above in STEP1).

		STEP2 relies on Git.

Installing Git

	STEP2 relies on Git. Please download Git at this link https://git-scm.com/download/mac  (select Install Xcode if you do not have disk space problems; otherwise download the Binary installer. Run the downloaded exe file.

	3. STEP3
		
	Once STEP2 is finished, run STEP3-NLP-environment.command by double-clicking on it.

	STEP3 will add a shortcut that will allow you to type NLP (CAPS) after opening a command line/prompt and automatically be placed into your NLP Anaconda environment as well as in your NLP Suite Directory. You need to run the command only once (but no harm if you accidentally do that repeatedly).
	
	THIS COMMAND IS VERY HELPFUL IF YOU NEED TO USE pip TO INSTALL PYTHON PACKAGES; THESE PYTHON PACKAGES MUST BE INSTALLED IN THE NLP ENVIRONMENT, RATHER THAN base, FOR THE NLP SUITE TO WORK. You can remove the NLP alias this script creates by running the NLP_environment_shortcut_remove.command.

Running the NLP Suite

The Mac installation script does not create a desktop NLP Suite icon. You need to click on the run_NLP-Suite.command file in setup_Mac to run the NLP Suite.

Updating the NLP Suite

The NLP Suite updates the scripts automatically to the lastest release available on GitHub every time you exit the NLP Suite. The update features rely on Git.

	The NLP Suite updates automatically to the lastest release available on GitHub every time you exit the NLP Suite. The update features rely on Git.

2. Mac running bash/zsh

	if you are a Mac user, you run a pip command (e.g., pip command spacy) and the NLP Suite after installation still warns you that stacy is not installed, most likely you are running macOS bash instead of zsh.

	Since the release of macOS 10.15 (Catalina) on October 7, 2019, the default macOS shell has been switched from bash to zsh. The NLP Suite has been optimized for zsh not bash. If you encounter errors with the installation of some Python packages (e.g., Stacy), most likely you are running bash. To ensure that you are running zhs open a command line/terminal and type 

	chsh -s /bin/zsh

	"terminal.integrated.shell.osx": "/bin/zsh",

	conda init zsh

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

			conda env remove --name NLP Suite

			  will delete an environment (i.e., NLP Suite) wrongly created or no longer necessary. 

		4. List all environments

			conda info --envs
			conda env list

			either command will give you a list of the environments on your machine; you will see at least two environments, base and NLP.

		5. List all Python packages

			conda list

			will give you a list of all Python packages installed in a specific environment; make sure to be in the right environment by using conda activate.

			If you run the command conda list from the anaconda prompt, rather than from a specific environment, you will list all installed packages in all environments.

	pip commands

		The pip command: What is pip?  

		pip is a package-management system written in Python used to install and manage software packages. Thus, if you open a command line/prompt and type

		1. install a Python packages

			pip install pandas

			will install the pandas package

		2. uninstall a Python packages
		
			pip uninstall pandas

			will uninstall a package (e.g., pandas)

		3. install a Python package version  

			Python scripts are VERY sensitive to the package version used to create the script. To ensure that the package will work on your computer, use the following command to install the required package version. 

			To install a specific version of a package run the command

			pip install pandas~=1.2.1

			will install a specific version of a package (e.g., pandas 1.2.1)

		4. Permission error with pip install

			The installation of some packages (e.g., pdfminer.six) may give you a permission error. In that case, add --user to the pip command, for instance, 

			pip install pdfminer.six --user

		5. More errors with pip command

			If, after installing a package via pip install, the NLP Suite warns you that the package you have just installed is not installed, you have probably installed the package in the wrong environment (e.g., base) and not in NLP.

			All Python packages are installed in specific Anaconda environments. The NLP Suite is setup in the NLP environment. If you open a command line/terminal most likely it will open the base environment.

			If base appears in command line/terminal, you are in the wrong environment.

			If you installed pandas in the base environment, it will not be recognized by the NLP Suite. You need to uninstall it from the base environment and install it in the NLP environment after activating the NLP environmant via conda activate NLP.

		6. Show the version of Python package

			pip show pandas

			will give you the version of any package (e.g., pandas) installed in the selected environment

	prompt commands
										
		1. where

			where Python
			
		will give the list of all the locations where Python is installed


