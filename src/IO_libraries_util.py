import csv
import sys
from sys import platform
import os
import tkinter as tk
import tkinter.messagebox as mb
import subprocess
from psutil import virtual_memory
from typing import List
import requests
import webbrowser
from subprocess import call

import GUI_util
import GUI_IO_util
import reminders_util
import TIPS_util
import IO_internet_util
import IO_user_interface_util
import csv
import sys
from sys import platform
import os
import tkinter as tk
import tkinter.messagebox as mb
import subprocess
from psutil import virtual_memory
from typing import List
import requests
import webbrowser

import GUI_util
import GUI_IO_util
import reminders_util
import TIPS_util
import IO_internet_util
import IO_user_interface_util

# import pip not used
# def install(software_name):
#     pip.main(['install', software_name])

# tkcolorpicker requires tkinter and pillow to be installed (https://libraries.io/pypi/tkcolorpicker)
# tkcolorpicker is both the software_name and module name
# pillow is the Python 3 version of PIL which was an older Python 2 version
# PIL being the commmon module for both software_names, you need to check for PIL and trap PIL to tell the user to install pillow

def which_shell():
    """
    Checks for the default shell, and returns the shell variant for Windows, macOS, and major Linux operating systems.
    :rtype: str - The type of shell. (e.g., "bash", "zsh", etc.)
    """
    shell = os.path.split(os.environ['SHELL'])[-1]
    if shell != 'zsh':
        error_msg = 'You are running shell ' + str(
            shell) + '\n\nSince the release of macOS 10.15 (Catalina) on October 7, 2019, the default macOS shell has been switched from bash to zsh. The NLP Suite has been optimized for zsh not bash. The algorithm will exit.\n\nPlease, read carefully the TIPS_NLP_Anaconda NLP environment pip.pdf on how to change shell to zsh.'
        answer = tk.messagebox.askyesno("MacOS shell error",
                                        error_msg + "\n\nDo you want to open the TIPS file now?")
        if answer:
            TIPS_util.open_TIPS('TIPS_NLP_Anaconda NLP environment pip.pdf')
    return shell

# return false if missing modules
def install_all_Python_packages(window, calling_script, modules_to_try):
    errorFound = False
    missingModules = []
    for module in modules_to_try:
        # import module
        try:
            i = __import__(module, fromlist=[''])
            # __import__(module)
        except ImportError as e:
            print(e)
            # passing pdfminer.six to this function, would ALWAYS fail the import
            # so we need to pass only pdfminer but then tell the user which pdfminer to install
            if 'pdfminer' in module:
                module = 'pdfminer.six'  # we need this specific version of pdfminer
            if 'docx' in module:
                module = 'python-docx'  # python-docx would always break the code; must pass docx
            if 'vlc' in module:
                module = 'python-vlc'
            missingModules.append(module)
            if 'spellchecker' in missingModules:
                # rename the module to the software_name to be installed
                missingModules = ['pyspellchecker' if x == 'spellchecker' else x for x in missingModules]
            if 'PIL' in missingModules:
                # rename the module to the software_name to be installed
                missingModules = ['pillow' if x == 'PIL' else x for x in missingModules]
    if missingModules:
        errorFound = True
        if platform == 'darwin':
            shell = which_shell()
            if shell != 'zsh':
                return False
        # root = tk.Tk()
        # root.withdraw()
        window.withdraw()
        if len(missingModules) == 0:
            msg=''
        elif len(missingModules) == 1:
            msg = missingModules[0]
        elif len(missingModules) > 1:
            msg = 'each of the listed modules'

        message = "FATAL ERROR. Please, read carefully. The NLP Suite will exit.\n\nThe script '" + \
                  calling_script + "' needs to import the following modules:\n\n" + ', '.join(missingModules) + \
                  "\n\nPlease, in command prompt/terminal, type\n\nNLP\n\nif you have run STEP3-NLP environment. Otherwise type" + \
                  "\n\nconda activate NLP\n\nEither command will activate the right NLP environment (NLP case sensitive) where to install the module. In the right NLP environment, type" + \
                  "\n\npip install " + str(msg) + "\n\nto install the module, close the NLP Suite, and try again."

        if 'pygit2' in str(missingModules):
            message = message + "\n\nWithout pygit2 the NLP Suite will not be automatically updated.\n\nThis, however, may be a sign that either you have not run STEP2 or you have not run it to completion (STEP2 installs all software_names used by the NLP Suite and takes quite some time). To install all software_names, run STEP2 again or, in command line/prompt, type\n\npip install -r requirements.txt"

        answer = tk.messagebox.askyesno("Module import error",
                                        message + "\n\nDo you want to open the TIPS file 'TIPS_NLP_Anaconda NLP environment pip.pdf' to learn about Anaconda environments and the installation of python modules via pip?")
        if answer:
            TIPS_util.open_TIPS('TIPS_NLP_Anaconda NLP environment pip.pdf')

        if 'stanfordnlp' or 'stanza' in missingModules:
            # sys.version_info is the Python version
            if (sys.version_info[0] < 3) or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
                if 'stanza' in missingModules:
                    mb.showwarning(title='Python version error',
                                   message="The module 'stanza' requires a Python version 3.6 or higher. You are currently running version " +
                                           sys.version_info[0] + "." + sys.version_info[
                                               0] + ".\n\nTo install Python with Anaconda, in command prompt/terminal type 'Conda install Python=3.7'.")
            # https://stackoverflow.com/questions/56239310/could-not-find-a-version-that-satisfies-the-requirement-torch-1-0-0
            # for more recent torch and torchvision, see https://pytorch.org/get-started/previous-versions/
            # for most recent torch and torchvision, see https://pytorch.org/get-started/locally/
            # if 'stanfordnlp' in missingModules:
            #     mb.showwarning(title='Warning',
            #                     message = "To install 'stanfordnlp' you will need to FIRST install 'torch' and 'torchvision' by typing:\n\nconda install pytorch torchvision cudatoolkit -c pytorch\n\nAFTER the successful installation of 'torch' and 'torchvision', you will need to install 'stanfordnlp' and 'stanford.download('en')'. At your command prompt/terminal, type:\n\npython\n\nThen at the >>> type:\n\nimport stanfordnlp\n\nWhen done type:\n\nstanfordnlp.download('en')\n\nWhen done type:\n\nexit().\n\nYOU MUST BE CONNECTED TO THE INTERNET TO INSTALL MODULES!\n\nYOU MUST ALSO BE IN THE NLP ENVIRONMENT!")
            # pip install torch===1.7.1 torchvision===0.8.2 -f https://download.pytorch.org/whl/torch_stable.html
            if 'stanza' in missingModules:
                mb.showwarning(title='Warning',
                               message="To install 'stanza' you will need to FIRST install 'torch' and 'torchvision' by typing:\n\nconda install pytorch torchvision cudatoolkit -c pytorch\n\nMAKE SURE TO INCLUDE THE HTTPS COMPONENT AFTER -f OR YOU WILL GET THE ERROR: -f option requires 1 argument.\n\nAFTER the successful installation of 'torch' and 'torchvision', you will need to install 'stanza' and 'stanza.download('en')'. At your command prompt/terminal or terminal, type:\n\npython\n\nThen at the >>> type:\n\nimport stanza\n\nWhen done type:\n\nstanza.download('en')\n\nWhen done type:\n\nexit().\n\nYOU MUST BE CONNECTED TO THE INTERNET TO INSTALL MODULES!\n\nYOU MUST ALSO BE IN THE NLP ENVIRONMENT!")
        # install(e.name)
    return not errorFound

# modules_to_try has the following format: ['re','glob',...]
# https://stackoverflow.com/questions/48097428/how-to-check-and-install-missing-modules-in-python-at-time-of-execution
# we only check rather than install because the next function install would break if pip is not the expected version

# def import_nltk_data(window):
#     try:
#         import nltk.data
#     except LookupError:
#         mb.showwarning(title='No nltk data available',
#                        message='The script needs the nltk data. These cannot be downloaded from requirements.\n\n\To download the data, in command line type\npython -m nltk.downloader all\n\nWARNING! On some laptops, the nltk.downloader may run into SSL certificate errors. If so, please type the following line in command line\n/Applications/Python 3.7/Install Certificates.command\n\nand start again. Please, change 3.7 to whatever Python version you have installed on your machine; to check your Python version type\nPython\nin command line.')


# check for missing nltk resource and download if missing
# resource paths &  resource
#   'taggers/averaged_perceptron_tagger','averaged_perceptron_tagger'
#   'tokenizers/punkt','punkt'
#   'corpora/WordNet','WordNet'
#   'corpora/stopwords','stopwords'

def import_nltk_resource(window, resource_path, resource):
    try:
        import nltk.data
        nltk.data.find(resource_path)
    except LookupError:
        IO_user_interface_util.timed_alert(window, 2000, 'Downloading nltk resource',
                                           'Downloading nltk ' + resource + '...\n\nIf downloading fails, in command line please type python -m nltk.downloader all\n\n Please, be patient...', False)
        print('Downloading nltk ' + resource + '   If downloading fails, in command line please type: python -m nltk.downloader all')
        nltk.download(resource)

def check_avaialable_memory(software):
    mem = virtual_memory()
    mem.total  # total physical memory available
    mem_GB=int(mem.total/1000000000)
    if mem_GB<10:
        reminders_util.checkReminder('Stanford-CoreNLP_config.csv', reminders_util.title_options_memory,
                                     reminders_util.message_memory, True)
    return mem_GB

# originally written to check for Java jdk version
# could be used for something else
# def check_environment_variables_path():
    # if platform == "win32" and 'CoreNLP' in script:
    #     for x in os.environ:
    #         if x == 'PATH':
    #             if 'Java' in os.getenv(x):
    #                 if not 'Java' in os.getenv(x):
    #                     answer = tk.messagebox.askyesno(title='Java error',
    #                                    message='A test for Java in the Environment Variables PATH failed.' +
    #                                            # '\n\nJava is not installed in your machine.\n\n' + script + ' is a Java script that requires Java installed on your machine (you need the JDK version, Java Development Kit; install Java JDK 8, which seems to work best for Stanford CoreNLP).\n\nPlease, read the Java installation TIPS, check your Java installation, install Java properly and try again (go to command line and type Java -version). Program will exit.')
    #                                             '\n\nJava is not installed in your machine.\n\n' + script + ' is a Java script that requires Java installed on your machine (you can check by going to command line and typing Java -version).\n\nInstall Java properly and try again. Program will exit.\n\n\n\nDo you want to open the Java website now and install it?')
    #                     print('Java is not installed in Environment variables')
    #                     errorFound = True
    #                     if answer:
    #                         status_code = requests.get(url).status_code
    #                         if status_code != 200:
    #                             mb.showwarning(title='Warning',
    #                                            message='Oops! The Java website could not be opened. Please, try again later.')
    #                             return
    #                         webbrowser.open_new_tab(url)
    #                     else:
    #                         return
    #                     return errorFound, error_code, system_output
    #                 else:
    #                     if not 'Java\jdk' in os.getenv(x):
    #                         # Java\jdk or java\jre
    #                         mb.showwarning(title='Java JDK error',
    #                                        message='A test for Java JDK in the Environment Variables PATH failed.' +
    #                                                '\n\nJava is installed in your machine but not the JDK version.\n\n' + script + ' is a Java script that requires Java JDK installed on your machine (you need the JDK version, Java Development Kit; install Java JDK 8, which seems to work best for Stanford CoreNLP).\n\nPlease, read the Java installation TIPS, check your Java installation, install Java JDK properly and try again (go to command line and type Java -version). Program will exit.')
    #                         print('Java is installed in Environment variables but ot the jdk version required by Stanford CoreNLP.')
    #                         errorFound = True
    #                         return errorFound, error_code, system_output


# for now the java_version as a single version number, e.g., 8 or 17, is not used
def get_java_version(system_output):
    java_version = system_output.split('\r\n')[0]
    java_version = java_version.split(' ')[2]
    # java_version = java_version.split('.')[0]
    # java_version = java_version.replace("\"","")
    return java_version

def check_windows_64_bits():
    errorFound = False
    if 'PROCESSOR_ARCHITEW6432' in os.environ:
        mb.showwraning(title='Fatal error',message='You are not running a Windows 64-bits machine as required by Stanford CoreNLP.\n\nThis will cause an error running Stanford CoreNLP: Could not create the Java Virtual Machine.')
        errorFound = True
    if not os.environ['PROCESSOR_ARCHITECTURE'].endswith('64'):
        errorFound = True
    return errorFound

# return errorFound, error_code, system_output
def check_java_installation(script):
    java_version=0
    Java_errorFound = False
    config_filename = ''
    reminder_title = ''
    reminder_message = ''
    message = ''
    error_code = 1 # should be 0 if Java is installed
    system_output = '' # This is what you see when you run "java -version" in your command line

    # unnecessary
    # if platform == 'win32':
    #     Java_errorFound = check_windows_64_bits()
    #     if Java_errorFound:
    #         return Java_errorFound, error_code, system_output

    try:
        # if you are testing new Java install/uninstall ...
        #   YOU MUST CLOSE PyCharm to run correctly the next command subprocess.run
        java_output = subprocess.run(['java', '-version'], capture_output=True)
        error_code = java_output.returncode  # Should be 0 if java installed
        system_output = java_output.stderr.decode('utf-8')  # This is what you see when you run "java -version" in your command line
        java_version = get_java_version(system_output)
    except:
        error_code = 1

    url = 'https://www.oracle.com/java/technologies/downloads/archive/'
    title = 'Java error'

    if error_code != 0:
        if ("not recognized" in system_output) or (system_output == ''):
            message = 'A test for Java returned a non-zero error code ' + str(
                    error_code) + ' and Java not recognized (You can check this in command line by typing Java -version).'

        if system_output != '':
            message = message + ' with the following system error: ' + system_output + '\n\n'
            message = message + \
                '\n\nJAVA MAY NOT BE CORRECTLY INSTALLED IN YOUR MACHINE.\n\n'
        else:
            message = message + \
                '\n\nJAVA IS NOT INSTALLED IN YOUR MACHINE.\n\n'
        message = message + script + ' is a Java script that requires the freeware Java (by Oracle) installed on our machine.\n\n' \
                'THE PROGRAM WILL EXIT.' \
                '\n\nTo download Java from the Oracle website, you will need to sign in in your Oracle account (you must create a FREE Oracle account if you do not have one).'\
                '\n\nSelect the most current Java SE version then download the JDK suited for your machine (Mac/Windows) and finally run the downloaded executable.' \
                '\n\nDO YOU WANT TO OPEN THE JAVA DOWNLOAD WEBSITE AND INSTALL JAVA NOW? (You must be connected to the internet)'
        Java_errorFound = True

    if Java_errorFound:
        # open website
        open_url(title, url, ask_to_open=True, message_title=title, message=message, reminder_title=reminder_title, reminder_message=reminder_message)

    if system_output != '':
        # checking for 64 bits windows machines
        if platform == "win32" and 'CoreNLP' in script:
            for info in system_output.split(" "):
                if "-Bit" in info:  # find the information about bit
                    if info[:2] != "64":  # check if it's 64 bit
                        message = 'You are not using JAVA 64-Bit version.\n\nThis will cause an error running Stanford CoreNLP: Could not create the Java Virtual Machine.\n\nPlease, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.\n\nAfter checking the Java version installed in your machine, if 32-Bit you will need to uninstall it and download and install the Java 64-Bit version,\n\nTHE PROGRAM WILL EXIT.\n\nDo you want to open the TIPS file now?'
                        answer = tk.messagebox.askyesno("Java version Error",
                                                        "You are not using JAVA 64-Bit version.\n\nThis will cause an error running Stanford CoreNLP: Could not create the Java Virtual Machine.\n\nPlease, configure your machine to use JAVA 64-Bit.\n\nPlease, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.\n\nDo you want to open the TIPS file now?")
                        if answer:
                            TIPS_util.open_TIPS('TIPS_NLP_Stanford CoreNLP memory issues.pdf')
                        Java_errorFound = True
    return Java_errorFound, error_code, system_output, java_version


# the function checks that a called Java or Python file is available in the src subdirectory
def check_inputPythonJavaProgramFile(programName, subdirectory='src'):
    # filePath=NLPPath+os.sep+subdirectory+os.sep+programName
    if not os.path.isfile(GUI_IO_util.NLPPath + os.sep + subdirectory + os.sep + programName):
        mb.showerror("Input file error",
                     "The required file " + programName + " was not found. The file is expected to be in the subdirectory " + subdirectory + " of the main NLP directory.\n\nPlease, make sure to copy " + programName + " to the " + subdirectory + " subdirectory and try again.")
        return False
    return True


CoreNLP_download = "https://stanfordnlp.github.io/CoreNLP/download.html" # zip file for both Mac and Windows
Gephi_download = "https://gephi.org/users/download/" # dmg Mac dmg file; Windows exe file
Google_Earth_download = "https://www.google.com/earth/download/gep/agree.html?hl=en-GB" # Mac dmg file; Windows exe file
Java_download = "https://www.oracle.com/java/technologies/downloads/archive/"
MALLET_download = "http://mallet.cs.umass.edu/download.php" # Mac tar-gz file; Windows zip file
# SENNA removed from SVO way too slow
# SENNA_download = "https://ronan.collobert.com/senna/download.html"
WordNet_download = "https://wordnet.princeton.edu/download/current-version" # Mac tar-gz file; Windows exe file

# the function checks that if Stanford CoreNLP version matches with the latest downloadable version
def check_CoreNLPVersion(CoreNLPdir,calling_script='',silent=False):
    # get latest downloadable version
    try:
        response = requests.get("https://api.github.com/repos/stanfordnlp/CoreNLP/releases/latest")
    except:
        # no internet
        return
    github_version = response.json()["name"][1:]
    # get local stanford corenlp version
    onlyfiles = [f for f in os.listdir(CoreNLPdir) if os.path.isfile(os.path.join(CoreNLPdir, f))]
    for f in onlyfiles:
        if f.startswith("stanford-corenlp-"):
            local_version = f[:-4].split("-")[2]
            if github_version != local_version:
                if not silent:
                    IO_user_interface_util.timed_alert(GUI_util.window, 6000, 'Stanford CoreNLP version',
                                   "Oops! Your local Stanford CoreNLP version is " + local_version +
                                   ".\n\nIt is behind the latest Stanford CoreNLP version available on GitHub (" + github_version + ").\n\nYour current version of Stanford CoreNLP will run anyway, but you should update to the latest release.",
                                                       False,'',True)
                break
    return

# the function checks that a specific external program (e.g., Gephi, StanfordCoreNLP) have been properly installed
#   it either reads a config csv file or it comes from having selected a specific program directory
# returns False when there is an error; true otherwise

def check_inputExternalProgramFile(calling_script, software_dir, programName, readingConfig=True, silent=False):

    message=''
    fileList = []
    if not 'Java' in programName: #!='Java (JDK)' Java (JDK)'
        unarchive_msg = ''
        head, tail = os.path.split(software_dir)
        # 9/1
        if software_dir=='':
            installation_message = programName.upper() + ' has not been installed on your machine (the Path cell is blank in the config file NLP_setup_external_software_config.csv).\n\nIf you have not downloaded the software yet, cancel installation when prompted and use the dropdown menu "Software DOWNLOAD" instead.\n\n' # \
                                   # + software_location_message

        if readingConfig:
            wrong_dir_msg = 'The software directory\n\n  ' + software_dir + '\n\nstored in the config file\n\nNLP_setup_external_software_config.csv\n\nis NOT the expected ' + programName.upper() + ' directory.'
        else:
            wrong_dir_msg = 'The selected software directory\n\n  ' + software_dir + '\n\nis NOT the expected ' + programName.upper() + ' directory.'
        if os.path.isdir(os.path.join(software_dir, tail)):
            unarchive_msg = '\n\nIt looks like your ' + programName + ' directory ' + software_dir + ' contains a ' + tail + ' directory inside. DO MAKE SURE THAT WHEN YOU UNARCHIVE THE ' + programName.upper() + ' ARCHIVE YOU DO NOT END UP WITH A ' + programName.upper() + ' DIRECTORY INSIDE A ' + programName.upper() + ' DIRECTORY.'
        select_directory_msg = '\n\nPlease, select the appropriate ' + programName.upper() + ' directory.'
        directory_content = ''  # initialize variable
        Mac_msg = '\n\nOnce you have downloaded ' + programName.upper() + ' double click on the downloaded .dmg file and drag the ' + programName.upper() + ' application in your Mac Applications directory.'


        message = ''

        if software_dir=='':
            if not silent:
                mb.showinfo(title='Warning', message=installation_message)
                return False
        if not os.path.isdir(software_dir):
            if 'setup_external_software' in calling_script:
                reinstall_string = '\n\nPlease, reinstall ' + programName + ' by selecting the folder where the software is stored on your machine' #using the dropdown menu "Software INSTALL" and select the location where the software is stored on your machine'
            else:
                reinstall_string = '\n\nPlease, reinstall ' + programName
            wrong_software_dir = 'The installation directory\n\n' + software_dir + '\n\nfor the external software ' + \
                                programName + \
                                ' stored in the config file NLP_setup_external_software_config.csv DOES NOT EXIST.' \
                                '\n\nIt may have been moved or renamed.' + reinstall_string + '.'
            if not silent:
                mb.showinfo(title='Warning',message=wrong_software_dir)
                return False
        else:
            for file in os.listdir(software_dir):
                # create a list of files inside the program directory so that they can be checked for validity
                if os.listdir(software_dir):
                    fileList.append(file)

#  Stanford CoreNLP
    if programName == 'Stanford CoreNLP':
        for item in fileList:
            if 'ejml' in str(item) or 'javax' in str(item):
                return True
        directory_content = wrong_dir_msg + '\n\nThe ' + programName.upper() + ' directory should contain, among other things, many files with \'ejml\' and \'javax\' in the filename.'
        message = directory_content + unarchive_msg + select_directory_msg

# Gephi
    if programName == 'Gephi':
        if platform == 'win32':
            if 'gephi' in fileList and 'gephi' in fileList and 'platform' in fileList:
                return True
            directory_content = wrong_dir_msg + '\n\nThe ' + programName.upper() + ' directory should contain, among other things, the subdirectories \'gephi\' and \'platform\''
            message = directory_content + unarchive_msg + select_directory_msg
        if platform == 'darwin':
            if 'Gephi.app' in fileList:
                return True
            directory_content ='\n\nThe ' + programName.upper() + ' was not found among Mac applications.'
            message = directory_content + Mac_msg

# Google Earth Pro
    if programName == 'Google Earth Pro':
        if platform == 'win32':
            if 'client' in fileList:
                return True
            directory_content = wrong_dir_msg + '\n\nThe ' + programName.upper() + ' directory should contain the subdirectory \'client\n\nMOST LIKELY THE EXECUTABLE FILE WILL AUTOMATICALLY INSTALL GOOGLE EARTH PRO UNDER A directory GOOGLE IN C:\Program Files.'
            message = directory_content + unarchive_msg + select_directory_msg

        if platform == 'darwin':
            if 'Google Earth Pro.app' in fileList:
                return True
            directory_content = '\n\nThe ' + programName.upper() + ' was not found among Mac applications.'
            message = directory_content + Mac_msg

# Java (JDK)
    if 'Java' in programName:
        Java_errorFound, error_code, system_output, java_version = check_java_installation(programName)
        # url = 'https://www.oracle.com/java/technologies/downloads/archive/'
        # Java_errorFound=True # for testing
        if not Java_errorFound:
            if "Java version " + str(java_version) + " installed" != software_dir:
                # need to update the config file Path (i.e., software_dir) for the current Java version
                # overwrite the csv file with updated csv_fields
                existing_software_config = get_existing_software_config()
                existing_software_config = update_software_config("Java version " + str(java_version) + " installed", programName, existing_software_config)
                save_software_config(existing_software_config, '', silent=True)
            return True
        if Java_errorFound and not silent:
            mb.showwarning(title=programName + ' installation.',
                           message=programName + ' is not installed on your machine.')
            return False
        else:
            if software_dir=='' and not silent:
                mb.showwarning(title=programName + ' installation.',
                               message=programName + ' is installed on your machine (Java version ' + str(java_version) + ') but the Java version is not saved in NLP_setup_external_software_config.csv' \
                                       '\n\nPlease, use the droopdown meny for "Software INSTALL on your machine and select "Java (JDK)" to save the Java version in the config file.')
                return True

    # MALLET
    if programName == 'MALLET':
        # check that MALLET has no spaces in path
        if ('bin' in fileList and 'class' in fileList) and not ' ' in software_dir:
            return True
        # check that MALLET has no spaces in path
        if ' ' in software_dir:
            mb.showerror(title='MALLET directory error',
                         message='The selected ' + programName.upper() + ' directory \n   ' + software_dir + '\ncontains a blank (space) in the path.\n\nThe ' + programName.upper() + ' code cannot handle paths that contain a space and will break.\n\nPlease, move ' + programName.upper() + ' in a directory with a path containing no spaces and try again.')

        directory_content = wrong_dir_msg + '\n\nThe ' + programName.upper() + ' directory should contain, among other things, the subdirectories \'bin\' and \'class\''
        message = directory_content + unarchive_msg + select_directory_msg

# WordNet
    if programName == 'WordNet':
        if 'dict' in fileList and 'src' in fileList:
            return True
        directory_content = wrong_dir_msg + '\n\nThe ' + programName.upper() + ' directory should contain, among other things, the subdirectories \'dict\' and \'src\''
        message = directory_content + unarchive_msg + select_directory_msg

    # display error messages ----------------------------------------------------------------
    # it gets here only if there ws an error and with a specific message return True for all software options
    # if the user has tinkered with the config file adding an extra line, for whatever reason,
    #   it would not be marked with an error message; if message is '' we do not want to display the warning; all is OK
    if message!='' and not silent:
        mb.showwarning(title=programName.upper() + ' installation error',
                message=message)
    # False is returned when there is an error
    return False

def open_url(website_name, url, ask_to_open = False, message_title='', message='', config_filename='', reminder_title='', reminder_message='', scriptName=''):
    # check internet connection
    if not IO_internet_util.check_internet_availability_warning("Check on GitHub the NLP Suite newest release version"):
        return False
    # check if a reminder needs to be displayed
    if reminder_title != '':
        reminders_util.checkReminder(scriptName, reminder_title,
                                     reminder_message, True)
    # check if the question to open the website is asked
    if ask_to_open:
        answer = tk.messagebox.askyesno(message_title,
                                        message)
        if answer == False:
            return False

    status_code = requests.get(url).status_code
    if status_code != 200:
        mb.showwarning(title='Warning',
                       message='Oops! The ' + website_name + ' website could not be opened.\n\nPlease, check the url or try again later.')
        return False
    webbrowser.open_new_tab(url)
    return True

def initialize_software_config_fields(existing_software_config: list) -> list:
    """
    @param existing_software_config: current csv file in list format, similar to sample_csv below
    @return: the new csv files, with software fields up to date.
    """
    sample_csv = [['Software', 'Installation_path', 'Download_link'],
                  ['Stanford CoreNLP', '', CoreNLP_download],
                  ['Gephi', '', Gephi_download],
                  ['Google Earth Pro', '', Google_Earth_download],
                  ['Java (JDK)', '', Java_download],
                  ['MALLET', '', MALLET_download],
                  ['WordNet', '', WordNet_download]]
    fields = [x[0].lower() for x in existing_software_config]
    for (index, row) in enumerate(sample_csv):
        if row[0].lower() not in fields:
            existing_software_config.append(sample_csv[index])
    return existing_software_config

def delete_software_config(existing_software_config, software):
    for (index, row) in enumerate(existing_software_config):
        if row[0] == software:
            (existing_software_config[index])[1]=''
            break
    return existing_software_config

def get_existing_software_config(external_software_config_file=''):
    if external_software_config_file=='':
        external_software_config_file='NLP_setup_external_software_config.csv'
    software_config = GUI_IO_util.configPath + os.sep + external_software_config_file
    # FIXED: must insert the new software_name into software-config.csv when the software_name is missing in the user csv file
    try:
        csv_file = open(software_config, 'r', newline='')
        existing_software_config = list(csv.reader(csv_file, delimiter=','))
    except:
        existing_software_config = list()
        existing_software_config = initialize_software_config_fields(existing_software_config)
    return existing_software_config

# gets a string of either missing or wrongly installed external software listed in config file:
#   CoreNLP, Gephi, Google Earth Pro, MALLET, WordNet
# warn user only if the specific software_name required to run a script is missing
def get_missing_external_software_list(calling_script, external_software_config_file, software_name, silent=False):
    if external_software_config_file=='':
        external_software_config_file=get_existing_software_config(external_software_config_file)
    index = 0
    missing_index = 0
    missing_software=''
    # external_software_config_file=external_software_config_file[1:]  # skip header line
    for row in external_software_config_file[1:]:  # skip header line
        software_name = row[0]
        software_dir = row[1]
        index = index + 1
        ExternalProgramFile_result = check_inputExternalProgramFile(calling_script, software_dir, software_name, True, silent)
        if external_software_config_file[index][1]=='' or os.path.isdir(software_dir) == False or \
                ExternalProgramFile_result == False:
            missing_index = missing_index +1
            # missing_software = missing_software + '  ' + str(missing_index) + '. ' + str(software_name).upper() + '\n\n'
            if missing_software=='':
                missing_software = str(software_name).upper() + '\n\n'
            else:
                missing_software = missing_software + str(software_name).upper() + '\n\n'
                # missing_software = missing_software + ',  ' + str(software_name).upper() + '\n\n'
        # if calling_script!='NLP_setup_external_software_main.py' and missing_software!='':
        #     call("python NLP_setup_external_software_main.py", shell=True)

    return missing_software

def get_software_config(softwareDir, software_name, existing_software_config):
    software_config = GUI_IO_util.configPath + os.sep + 'NLP_setup_external_software_config.csv'
    if not os.path.isfile(software_config):
        csv_fields = get_existing_software_config(software_config)
        with open(software_config, 'w+', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(csv_fields)

    # read the existing values of csv
    csv_fields = get_existing_software_config()
    for i, row in enumerate(csv_fields):
        if row[0] == software_name:
            csv_fields[i][1] = softwareDir  # update path of csv_fields
        else:
            csv_fields[i][1] = csv_fields[i][1] # copy current value
    return existing_software_config

# returns a double list [[]] of updated external software in NLP_setup_external_software_config.csv
def update_software_config(softwareDir, software_name, existing_software_config):
    for i, row in enumerate(existing_software_config):
        if row[0] == software_name:
            existing_software_config[i][1] = softwareDir  # update path of csv_fields
            break
        else:
            existing_software_config[i][1] = existing_software_config[i][1] # copy current value
    return existing_software_config

def save_software_config(existing_software_config, missing_software_string, silent=False):
    software_config = GUI_IO_util.configPath + os.sep + 'NLP_setup_external_software_config.csv'
    # overwrite the csv file with updated csv_fields
    with open(software_config, 'w+', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(existing_software_config)
        message="The config file 'NLP_setup_external_software_config.csv' was successfully saved to\n\n" + software_config
        # convert comma-separated string to list []
        missing_software_list = missing_software_string.split(",")
        if len(missing_software_list)>0:
            missing_software_string=", ".join(missing_software_list)
            message = message + "\n\nDon\'t forget that you have " + str(len(missing_software_list)) + " other remaining missing software to download and/or install: " + missing_software_string
        if not silent:
            mb.showwarning(title='Config installation file saved',
                       message=message)

# software_name is != '' when ...
#   1. the function is called from a specific script that uses the software_name (e.g., parsers_annotators_main)
#   2. the function is called from NLP_menu_main when clicking on the button Setup external software
# return software_dir, software_url, missing_software, errorFound

def get_external_software_dir(calling_script, software_name_checked, silent, only_check_missing, install_download='', errorFound = False):
    software_dir = ''
    software_url = ''
    index = 0

    missing_software=''

    # get a list of software in software-config.csv
    existing_software_config = get_existing_software_config()
    # loop through all software in NLP_setup_external_software_config.csv file
    for row in existing_software_config[1:]:  # skip header line
        answer = False
        index = index + 1
        software_name = row[0]
        software_dir = row[1]
        software_url = row[2]

        # when checking a specific software, skip all other software in the loop
        if software_name_checked.lower() != '' and \
                (software_name_checked.lower() != software_name.lower()):
            continue

        if software_name_checked.lower() != '' and \
                ((software_name_checked.lower() == software_name.lower()) or
                 ('Java' in software_name_checked and 'Java' in software_name)):
            if software_dir == '':
                errorFound=True

# software_dir does NOT exist (the path cell is blank in the config file NLP_setup_external_software_config.csv)
#         if software_dir == None or software_dir == '':
#             if missing_software=='':
#                 missing_software = str(software_name).upper() + '\n\n'
#                 errorFound = True
#             else:
#                 missing_software = missing_software + str(software_name).upper() + '\n\n'
#
# # software_dir exists (the path cell contains a software path in the config file NLP_setup_external_software_config.csv)
#         else:
        # the software directory is stored in config file but...
        #   check that the software directory still exists and the software_name has not been moved
        # False is returned when there is an error
        # check_inputExternalProgramFile checks a specific software software_name stored in NLP_setup_external_software_config.csv
        errorFound = not check_inputExternalProgramFile(calling_script, software_dir, software_name, True, silent)
        if errorFound:
            # RF 7/28
            software_dir = ''
            # software_dir = existing_software_config[index][1]
            software_url = existing_software_config[index][2]
            existing_software_config[index][1] = '' #software_dir
            if software_name not in missing_software:
                missing_software = missing_software + str(software_name).upper() + '\n\n'

        # if you are checking for a specific software_name and the directory is NOT found
        #   return None; no point continuing in the for loop
        if (software_name_checked.lower()!='') and (software_name_checked.lower() in software_name.lower()):
            # errorFound = False
            break

    if software_dir == '':
        software_dir = None # specific calling scripts (e.g. Stanford CoreNL) check for None
    else:
        if software_name_checked=='':
            software_dir = None
            software_url = ''

    return software_dir, software_url, missing_software, errorFound
    # end of get_external_software_dir
def ask_download_installation_questions(download_install, software_name, software_dir, message, silent=False):
    cancel_download_install = False
    if software_dir != None and software_dir != '':  # and software_name.lower() in software_name.lower():
        if software_name != '':
            answer = False
            if download_install == 'install':
                if not silent:
                    answer = tk.messagebox.askyesno(software_name + " installation", message)
            else:
                if not silent:
                    answer = tk.messagebox.askyesno(software_name + " download", message)
            if not answer:
                cancel_download_install = True
    return cancel_download_install


# Gephi.app, Google Earth Pro.app

def check_program_Mac_Applications(programName):
    if (programName + '.app') in os.listdir("/Applications"):
        return True
    return False

# called by external_software_download
# called by external_software_install
def display_download_installation_messages(download_install, software_name, software_dir, software_url,
                                         calling_script, missing_software, silent, error_found=False):
    title='Warning'
    download_install_message = ''
    download_message = ''
    installation_message = ''
    re_installation_directory_message=''
    archive_message=''
    archive_warning=''
    opening_message = ''
    already_downloaded_message=''
    already_installed_message=''
    after_website_opens_message = ''
    executing_unzipping_label=''
    software_extension = ''

    # Stanford CoreNLP zip file for both Mac and Windows
    # Gephi Mac dmg file; Windows exe file
    # Google Earth Pro Mac dmg file; Windows exe file
    # MALLET Mac tar-gz file; Windows zip file
    # WordNet Mac tar-gz file; Windows exe file

# setup general variables -----------------------------------------------------------------------------

    # platform = 'darwin'

# Mac setup general variables --------------------------------------------------------------------------------------
    if platform == 'darwin':
        Mac_Applications_label = ' directory (NOT Mac Applications!) '
        if software_name=='Gephi':
            software_extension = '.dmg' # Mac executable file
            file_name = 'the file. The default Gephi download file is for MacOs with an Intel chip; if you have an M1 or M2 chip download the Mac OS (Silicon) file'
            Mac_Applications_label = ' Mac Applications directory '
        elif software_name=='Google Earth Pro':
            software_extension = '.dmg' # Mac executable file
            file_name = 'the latest available Google Earth Pro file found at the bottom of the download website'
            Mac_Applications_label = ' Mac Applications directory '
        elif 'Java' in software_name:
            software_extension = '.dmg'
            file_name = 'Arm 64 DMG Installer'
        elif software_name == 'MALLET':
            software_extension = '.tar-gz'
            file_name = 'mallet-2.0.8.tar-gz'
        elif software_name == 'Stanford CoreNLP':
            software_extension = '.zip' # both Mac & Windows
            file_name = 'the latest available zip file (e.g., Download CoreNLP 4.5.2)'
        elif software_name == 'WordNet':
            software_extension = '.tar.gz'
            file_name = 'WordNet-3.0.tar.gz'
        else:
            software_extension = '.tar-gz' # Mac zip file
            file_name ='.tar-gz file'
# Windows setup general variables --------------------------------------------------------------------------------------
    else:
        Mac_Applications_label = ' directory '
        if software_name=='Gephi':
            software_extension = '.exe' # Windows executable file
            file_name = 'the latest available Gephi for Windows'
        elif 'Java' in software_name:
            software_extension = '.exe'
            file_name = 'Windows x64 Installer'
        elif software_name == 'MALLET':
            software_extension = '.zip'
            file_name = 'mallet-2.0.8.zip'
        elif software_name=='Stanford CoreNLP':
            software_extension = '.zip' # both Mac & Windows
            file_name = 'the latest available zip file (e.g., Download CoreNLP 4.5.2)'
        elif software_name == 'WordNet':
            software_extension = '.exe'
            file_name = 'WordNet-2.1.exe'
        else:
            software_extension = '.exe'
            file_name = '.exe file'

    if software_extension=='.tar-gz' or software_extension=='.zip':
        executing_unzipping_label = 'unzip'
    elif software_extension=='.dmg' or software_extension=='.exe':
        executing_unzipping_label = 'extract'

    if 'download' in download_install:
        software_location_label='MOVE'
    else:
        software_location_label = 'INSTALL'

    if software_name == 'WordNet':
        WordNet_Chrome_message = '\n\nIf you use Chrome as a browser and after clicking on the download link nothing happens, most likely Chrome has blocked the download operation. ' \
                  'You have two options. Click on the download executable and ...' \
                  '\n   1. Select "Open link in new window." and refresh or hit return to start downloading.' \
                  '\n   2. Select "Copy link address", start a new tab, paste the copied address and refresh or hit return to start downloading.'
    else:
        WordNet_Chrome_message = ''

    if software_name == 'MALLET':
        MALLET_message = '\n\nA MALLET DIRECTORY CANNOT CONTAIN BLANKS (SPACES) IN THE PATH. THE MALLET CODE CANNOT HANDLE PATHS THAT CONTAIN A SPACE AND WILL BREAK.'
    else:
        MALLET_message = ''

    if (platform == 'win32') or (platform == 'darwin' and software_name != 'Gephi' and software_name != 'Google Earth Pro'):
        software_location_message = 'DO NOT ' + software_location_label + ' THE SOFTWARE DIRECTORY INSIDE THE NLP SUITE DIRECTORY OR IT MAY BE OVERWRITTEN IN CASE YOU NEED TO RE-INSTALL THE SUITE.' + \
                                MALLET_message + WordNet_Chrome_message
    else:
        software_location_message = ''


    # both download-install messages ------------------------------------------------------------------------------------------------------------------------------------------

    if software_name == '':
        title = 'NLP Suite external software download and/or install'
        opening_message = 'The NLP Suite relies on several external programs that need to be downloaded and installed.\n\n' \
                'LIST OF PROGRAMS TO BE DOWNLOADED/INSTALLED:\n\n' + missing_software + \
                '\n\nPlease, use the "Software DOWNLOAD" dropdown menu to download and install the software in the list or some functionality will be lost for some of the scripts ' \
                                '(e.g., you cannot do any textual analysis of any kind without Stanford CoreNLP or produce any geographic maps without Google Earth Pro). ' \
                                'The algorithms that use any of these programs will remind you that you need to install them if you want to run the algorithm. ' \
                                '\n\nIf you have already downloaded the software, but not installed it, click on the "Software install" button to select the directory where you saved it on your machine in order to install it; ' \
                                'you will only have to do this once (the selected installation directory will be saved in NLP_setup_external_software_config.csv).'
    else:
        # NL_menu__main
        if (software_dir=='' or  software_dir==None) and (not 'NLP_menu' in calling_script and not 'NLP_setup_external_software' in calling_script):
                opening_message = 'The script ' + calling_script.upper() + ' requires the external software ' + software_name.upper() + ' to run. The software needs to downloaded/installed.' \
                    '\n\nFor your convenience, the download function can automatically open the NLP_setup_external_software_main.py GUI ' \
                    'where you can download and install this and any other required external software.' \
                    '\n\nDO YOU WANT TO OPEN THE GUI?'
                if not silent:
                    answer = tk.messagebox.askyesno(software_name + " installation", opening_message)
                    if answer:
                        download_message = ''
                        call("python NLP_setup_external_software_main.py", shell=False)
                        # must get software_dir in case it was changed in the NLP_setup_external_software_main GUI
                        software_dir, software_url, missing_software, error_found = get_external_software_dir(calling_script,
                                                                                                 software_name,
                                                                                                 silent=True,
                                                                                                 only_check_missing=True,
                                                                                                 install_download='install')

                    else:
                        # download_message, installation_message are set to '' when no new download or installation is desired
                        download_message = ''
                    return software_dir, title, opening_message, download_message, installation_message

# DOWNLOAD  messages ------------------------------------------------------------------------------

    if 'download' in download_install:
        # Windows zip file; double click or right click to unzip
        # Mac dmg file; double-click to execute
        # Mac tar-gz file; double_click to unzip it

# DOWNLOAD check software_dir ------------------------------------------------------------------------------

        # software not yet downloaded and installed (i.e., Path field is blank in NLP_setup_external_software_config.csv)
        if software_dir == None or software_dir == '':

# DOWNLOAD check software_name --------------------------------------------------------------------------------
#   setting up messages
            if software_name!='':

                title = software_name.upper() + ' software download and/or install'
                after_website_opens_message = 'Once the ' + software_name.upper() + ' download website opens up, download ' + \
                   file_name + '.'

                after_download_message = '\n\nAfter download is completed, double click on the ' + software_extension + ' file to ' + executing_unzipping_label + \
                  ' all the software files, and move the entire new directory to a location of your choice (e.g., desktop).\n\n' + \
                  software_location_message

                after_download_installation_message = '\n\nAfter downloading and ' + executing_unzipping_label + 'ing, and perhaps moving the ' + software_name.upper() + \
                  ' software directory, you will be asked whether you also want to install ' + software_name.upper() + \
                  ' by selecting its saved directory location. You will only have to do this once; the selected installation directory will be saved in NLP_setup_external_software_config.csv).'

# GEPHI & GOOGLE EARTH PRO DOWNLOAD
#   setting up messages
                if platform == 'darwin':
                    if check_program_Mac_Applications(software_name):
                        # GEPHI & GOOGLE EARTH PRO DOWNLOAD
                        software_dir='/Applications'

                    if software_name == 'Gephi':
                        software_dir = "/Applications"
                        after_download_message = '\n\nAfter download is completed, double click on the ' + software_extension + ' file to ' + executing_unzipping_label + \
                                                 ' all the software files. Gephi will be placed next to the Applications directory and you must manually move it to Applications.'

                    if software_name == 'Google Earth Pro':
                        software_dir = "/Applications"
                        after_download_message = '\n\nAfter download is completed, double click on the ' + software_extension + ' file to install Google Earth Pro. The installation process will automatically place Google Earth Pro in the Applications directory.'

# Java download
#   setting up messages

                if 'Java' in software_name:
                    # since Stanford CoreNLP, Gephi, and MALLET need Java, check for Java installation
                    Java_errorFound, error_code, system_output, java_version = check_java_installation(
                        software_name)
                    if not Java_errorFound:
                        software_dir = "Java version " + str(java_version) + " installed"
                        mb.showwarning(title=software_name + ' installation.',
                                       message=software_name + ' is already installed on your machine:\n\n' + software_dir + ' as saved in NLP_setup_external_software_config.csv.'
                                                '\n\nIf you want to install a new version, you need to uninstall the current version, since Java is in your environment variables, and then download and/or install a different version.')
                        # download_message='' is used to detect a cancellation
                        download_message = ""
                        return software_dir, title, opening_message, download_message, installation_message
                    else:
                        download_message = 'To download Java from the Oracle website, you will need to sign in your Oracle account (you must create a FREE Oracle account if you do not have one).\n\n' \
                                           'Select the most current Java SE version then download the JDK suited for your machine (Mac/Windows) and finally run the downloaded executable.'
                else:
                    download_message = after_website_opens_message + after_download_message

            already_downloaded_message = ''

# DOWNLOAD check software_dir ------------------------------------------------------------------------------

        else: # already downloaded (i.e., Path field has a value in NLP_setup_external_software_config.csv)

# DOWNLOAD check software_name --------------------------------------------------------------------------------

# Java download
            if software_name != '':
                if 'Java' in software_name:
                    # since Stanford CoreNLP, Gephi, and MALLET need Java, check for Java installation
                    Java_errorFound, error_code, system_output, java_version = check_java_installation(software_name)
                    if not Java_errorFound:
                        software_dir = "Java version " + str(java_version) + " installed"
                    mb.showwarning(title=software_name + ' installation.',
                                   message=software_name + ' is already installed on your machine:\n\n' + software_dir + ' as saved in NLP_setup_external_software_config.csv.'
                                                        '\n\nIf you want to install a new version, you need to uninstall the current version, since Java is in your environment variables, and then download and/or install a different version.')
                    # download_message, installation_message are set to '' when no new download or installation is desired
                    download_message = ''
                    return software_dir, title, opening_message, download_message, installation_message

            already_downloaded_message = software_name.upper() + " has already been downloaded and installed on your machine.\n\n" \
                                        "Do you want to access the software_name url\n\n  " + software_url + "\n\nand download it again (maybe a different release)?\n\n" \
                                        '\n\nIf, instead, you have moved the software directory to a location different from the one saved in the config file, use the dropdown menu "Software install" to select the new location.'
            cancel_download_install = ask_download_installation_questions(download_install, software_name,
                                      software_dir, already_downloaded_message,
                                      silent=False)
            if cancel_download_install:
                # download_message, installation_message are set to '' when no new download or installation is desired
                download_message=''
                return software_dir, title, opening_message, download_message, installation_message

# WordNet download

            if software_name == 'WordNet':
                download_message = 'Once the WORDNET website opens up, you need to download the executable file WordNet-2.1.exe. After downloading, run the executable file by double-clicking on it and move the WordNet directory ' \
                                                                'to a location of your choice (e.g., desktop).\n\n' + software_location_message + WordNet_Chrome_message  # installation_message
            else:
                download_message = after_website_opens_message + download_install_message

# DOWNLOAD ask questions ---------------------------------------------------------------

        if download_message !='':
            mb.showwarning(title='download ' + software_name.upper(), message=download_message)

# INSTALL messages -------------------------------------------------------------------------

    elif download_install == 'install':

        # INSTALL check software_dir ------------------------------------------------------------------------------

        if (software_dir == None or software_dir == ''):

# INSTALL check software_name --------------------------------------------------------------------------------

# Java
            if 'Java' in software_name:
                # since Stanford CoreNLP, Gephi, and MALLET need Java, check for Java installation
                Java_errorFound, error_code, system_output, java_version = check_java_installation(software_name)
                # RF 8/30
                # if not Java_errorFound:
                if Java_errorFound:
                    software_dir = "Java version " + str(java_version) + " installed"
                    # @@@
                    mb.showwarning(title=software_name + ' installation.',
                                   message=software_name + ' is already installed on your machine (but the Java version is not saved in NLP_setup_external_software_config.csv; '
                                                           'when you CLOSE this GUI make sure to save the changes).'
                                                           '\n\nIf you want to install a new version, you need to uninstall the current version, '
                                                           'since Java is in your environment variables, and then use the "Software DOWNLOAD" dropdown menu to download and install a different version.')

                # download_message, installation_message are set to '' when no new download or installation is desired
                download_message = '###'
                return software_dir, title, opening_message, download_message, installation_message

# Gephi and Google Earth Pro

            if platform == 'darwin' and (software_name=='Gephi' or software_name=='Google Earth Pro'):
                    if not check_program_Mac_Applications(software_name):
                        installation_message = software_name.upper() + ' IS NOT INSTALLED ON YOUR MACHINE (the Path cell is blank in the config file NLP_setup_external_software_config.csv).' \
                                                '\n\nIf you have already downloaded the software, and just not installed it, double click on the downloaded ' + software_extension + ' file.'
                        if software_name=='Gephi':
                            installation_message = installation_message + '\n\nGephi will be placed next to the Applications directory and you must manually move it to Applications.'
                        if software_name == 'Google Earth Pro':
                                installation_message = installation_message + '\n\nThe installation process will automatically place Google Earth Pro in the Applications directory.'
                    else:
                        installation_message = software_name.upper() + ' IS ALREADY INSTALLED ON YOUR MACHINE.\n\nIf you want to install a different version, please go to the Applications directory, delete ' + \
                                               software_name + ', and use the dropdown menu "Software DOWNLOAD" to select ' + software_name + ' and download and install a different release.'

                    mb.showwarning(title='Install ' + software_name.upper(), message=installation_message)
                    software_dir='/Applications'
                    # download_message, installation_message are set to '' when no new download or installation is desired
                    download_message = installation_message
                    return software_dir, title, opening_message, download_message, installation_message

            installation_message = software_name.upper() + ' has not been installed on your machine (the Path cell is blank in the config file NLP_setup_external_software_config.csv).\n\nIf you have not downloaded the software yet, cancel installation when prompted and use the dropdown menu "Software DOWNLOAD" instead.\n\n' \
                                   + software_location_message
            # @@@ 9/1
            if not error_found:
                mb.showwarning(title='Install ' + software_name.upper(), message=installation_message)

# INSTALL check software_dir ------------------------------------------------------------------------------

        else: # already installed

# any software

            if 'NLP_menu' in calling_script or 'NLP_setup_external_software' in calling_script:
                installation_message = software_name.upper() + " has already been installed on your machine.\n\nDo you want to install it again, " \
                    "selecting a different directory location from the current location?\n\n" + software_dir
            else:
                installation_message=''

# Java

            if 'Java' in software_name:
                # since Stanford CoreNLP, Gephi, and MALLET need Java, check for Java installation
                Java_errorFound, error_code, system_output, java_version = check_java_installation(software_name)
                if not Java_errorFound:
                    software_dir = "Java version " + str(java_version) + " installed"
                    mb.showwarning(title=software_name + ' installation.',
                               message=software_name + ' is already installed on your machine:\n\n' + software_dir + ' as saved in NLP_setup_external_software_config.csv.\n\nIf you want to install a new version, '
                                    'you need to uninstall the current version, since Java is in your environment variables, and then use the "Software DOWNLOAD" dropdown menu to download and install a different version.')
                # download_message, installation_message are set to '' when no new download or installation is desired
                download_message = ''
                return software_dir, title, opening_message, download_message, installation_message

# Stanford CoreNLP

            # check that Stanford CoreNLP is the latest release
            if software_name == 'Stanford CoreNLP':
                check_CoreNLPVersion(software_dir, calling_script, silent)
                # software_dir = ''
                # missing_software = software_name


            # when called from a specific GUI that requires an external software (e.g., Stanford_CoreNLP_util)
            #  if the software is installed, you do not want to ask any questions
            if installation_message=='':
                return software_dir, title, opening_message, download_message, installation_message

            cancel_download_install = ask_download_installation_questions(download_install, software_name,
                                                                          software_dir, installation_message,
                                                                          silent=False)
            if cancel_download_install:
                # download_message, installation_message are set to '' when no new download or installation is desired
                download_message = ''
                return software_dir, title, opening_message, download_message, installation_message

        installation_directory_message = "You will be asked next to select the" + Mac_Applications_label + \
                                            "where \n\n" + software_name.upper() + \
                                            "\n\nis saved on your machine. " \
                                            "\n\nPress Esc or Cancel to exit when the dialogue box opens if you do not want to install " + software_name.upper() + '.\n\n' \
                                            + software_location_message

        mb.showwarning(title='Install ' + software_name.upper(), message=installation_directory_message)

        temp_software_dir = tk.filedialog.askdirectory(initialdir=software_dir,
                                                       title='Select a directory for ' + software_name + '. Press Esc or Cancel to exit.')
        if temp_software_dir != '':
            if not check_inputExternalProgramFile(calling_script, temp_software_dir, software_name,
                                                  False, False):
                download_message = ''
                software_dir = None
            else:
                # since download_message='' is used to detect a cancellation it must be set to the value of installation_message
                download_message = installation_message
                software_dir = temp_software_dir

    return software_dir, title, opening_message, download_message, installation_message


# DOWNLOADING -------------------------------------------------------------------------------
# if 'CoreNLP' in software_download_var.get():
#     software_website_url="https://stanfordnlp.github.io/CoreNLP/download.html"
# if 'Gephi' in software_download_var.get():
#     software_website_url="https://gephi.org/users/download/"
# if 'Java' in software_download_var.get():
#     software_website_url="https://www.oracle.com/java/technologies/downloads/archive/"
# if 'MALLET' in software_download_var.get():
#     software_website_url="http://mallet.cs.umass.edu/download.php"
# # 'SENNA' was removed from SVO options; way too slow
# # if 'SENNA' in software_download_var.get(): NO LONGER USED
# #     software_website_url= "https://ronan.collobert.com/senna/download.html"
# if 'WordNet' in software_download_var.get():
#     software_website_url="https://wordnet.princeton.edu/download/current-version"
def external_software_download(calling_script, software_name, existing_software_config, silent=False):

    # get the software_dir and software_url for the selected software_name
    software_dir, software_url, missing_software, error_found = get_external_software_dir(calling_script, software_name,
                                                        silent=True, only_check_missing=True, install_download='download')
    download_message=''
    if missing_software=='':
        return software_dir, software_url, download_message

    software_dir, title, opening_message, download_message, installation_message = \
        display_download_installation_messages('download', software_name, software_dir, software_url, calling_script, '', silent, error_found)

    # download_message is set to ''' when the software has already been downloaded and the user opts NOT to re-download
    if download_message=='':
        return software_dir, software_url, download_message

# DOWNLOAD open software download website

    open_url(software_name, software_url)

# DOWNLOAD JAVA for CoreNLP, Gephi, MALLET

    ### should go in def display...
    if software_name == 'Stanford CoreNLP' or software_name == 'Gephi' or software_name == 'MALLET':
        # since Stanford CoreNLP, Gephi, and MALLET need Java, check for Java installation
        Java_errorFound, error_code, system_output, java_version = check_java_installation(software_name)
        # url = 'https://www.oracle.com/java/technologies/downloads/archive/'
        # Java_errorFound=True # for testing
        if Java_errorFound:
            Java_required = software_name + ' requires the freeware Java (by Oracle) installed on our machine.\n\nDon\'t forget to download and install Java JDK.'
            mb.showwarning(title='Warning',message=Java_required)
            # open_url('Java', url, ask_to_open = True, message_title = 'Java', message = Java_required)
    # software_dir, existing_software_config = external_software_install(calling_script, software_name, existing_software_config, silent)
    return software_dir, software_url, download_message


# INSTALLING -------------------------------------------------------------------------------
# updates the array existing_software_config with the value of software_dir
# returns the software_dir and the double list existing_software_config = [[]]
def external_software_install(calling_script, software_name, existing_software_config, silent, errorFound):
    # get installation directory and website
    # if not error_found:
    software_dir, software_url, missing_software, error_found = get_external_software_dir(calling_script, software_name,
                                                            silent=True, only_check_missing=True, install_download='install', errorFound=errorFound)
    #@@@
    # if missing_software=='':
    #     return software_dir, existing_software_config
    software_dir, title, opening_message, download_message, installation_message = \
        display_download_installation_messages('install', software_name, software_dir, software_url, calling_script, missing_software, silent, errorFound)
    # download_message, installation_message are set to '' when no new download or installation is desired
    if download_message=='':
        return software_dir, existing_software_config, error_found

    ###
    # existing_software_config = get_existing_software_config()

    if not error_found and software_dir != None and software_dir != '':
        # check that it is the correct software directory
        if 'corenlp' in software_name.lower():
            software_name = 'Stanford CoreNLP'
        elif 'gephi' in software_name.lower():
            software_name = 'Gephi'
        elif 'google earth pro' in software_name.lower():
            software_name = 'Google Earth Pro'
        elif 'java' in software_name.lower():
            software_name = 'Java (JDK)'
        elif 'mallet' in software_name.lower():
            software_name = 'MALLET'
        elif 'wordnet' in software_name.lower():
            software_name = 'WordNet'
        if not 'Java' in software_name:
            # check that the selected directory for the external program is correct; if so save
            if not check_inputExternalProgramFile(calling_script, software_dir, software_name, False):
                software_dir = None

    # update the array existing_software_config with the value of software_dir
    # values will be saved when pressing CLOSE
    if software_dir != None and software_dir != '':
        existing_software_config = update_software_config(software_dir, software_name, existing_software_config)

    return software_dir, existing_software_config, error_found
