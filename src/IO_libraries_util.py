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
# def install(package):
#     pip.main(['install', package])

# tkcolorpicker requires tkinter and pillow to be installed (https://libraries.io/pypi/tkcolorpicker)
# tkcolorpicker is both the package and module name
# pillow is the Python 3 version of PIL which was an older Python 2 version
# PIL being the commmon module for both packages, you need to check for PIL and trap PIL to tell the user to install pillow

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
def install_all_packages(window, calling_script, modules_to_try):
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
            missingModules.append(module)
            if 'spellchecker' in missingModules:
                # rename the module to the package to be installed
                missingModules = ['pyspellchecker' if x == 'spellchecker' else x for x in missingModules]
            if 'PIL' in missingModules:
                # rename the module to the package to be installed
                missingModules = ['pillow' if x == 'PIL' else x for x in missingModules]
    if missingModules:
        errorFound = True
        error_msg = "\n\nPlease, read the TIPS_NLP_Anaconda NLP environment pip.pdf"
        if platform == 'darwin':
            shell = which_shell()
            if shell != 'zsh':
                return False
        # root = tk.Tk()
        # root.withdraw()
        window.withdraw()
        if len(missingModules) == 1:
            msg = missingModules[0]
        elif len(missingModules) > 1:
            msg = 'each of the listed modules'

        message = "FATAL ERROR. Please, read carefully. The NLP Suite will exit.\n\nThe script '" + \
                  calling_script + "' needs to import the following modules:\n\n" + ', '.join(missingModules) + \
                  "\n\nPlease, in command prompt/terminal, type\n\nNLP\n\nif you have run STEP3-NLP environment. Otherwise type" + \
                  "\n\nconda activate NLP\n\nEither command will activate the right NLP environment (NLP case sensitive) where to install the package. In the right NLP environment, type" + \
                  "\n\npip install " + str(msg) + "\n\nto install the module and try again."

        if 'pygit2' in str(missingModules):
            message = message + "\n\nWithout pygit2 the NLP Suite will not be automatically updated.\n\nThis, however, may be a sign that either you have not run STEP2 or you have not run it to completion (STEP2 installs all packages used by the NLP Suite and takes quite some time). To install all packages, run STEP2 again or, in command line/prompt, type\n\npip install -r requirements.txt"
        answer = tk.messagebox.askyesno("Module import error",
                                        message + "\n\nDo you want to open the TIPS file now?")
        if answer:
            TIPS_util.open_TIPS('TIPS_NLP_Anaconda NLP environment pip.pdf')

        if 'stanfordnlp' or 'stanza' in missingModules:
            # sys.version_info is the Python version
            if (sys.version_info[0] < 3) or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
                # if 'stanfordnlp' in missingModules:
                #     mb.showwarning(title='Python version error',
                #                    message="The module 'stanfordnlp' requires a Python version 3.6 or higher. You are currently running version " +
                #                            sys.version_info[0] + "." + sys.version_info[
                #                                0] + ".\n\nTo install Python with Anaconda, in command prompt/terminal type 'Conda install Python=3.7'.")
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
    errorFound = False
    config_filename = ''
    reminder_title = ''
    reminder_message = ''
    message = ''
    error_code = 1 # should be 0 if Java is installed
    system_output = '' # This is what you see when you run "java -version" in your command line

    # unnecessary
    # if platform == 'win32':
    #     errorFound = check_windows_64_bits()
    #     if errorFound:
    #         return errorFound, error_code, system_output

    try:
        # if you are testing new Java install/uninstall ...
        #   YOU MUST CLOSE PyCharm to run correctly the next command
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
        errorFound = True

    if errorFound:
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
                        errorFound = True
    return errorFound, error_code, system_output, java_version


# the function checks that a called Java or Python file is available in the src subdirectory
def check_inputPythonJavaProgramFile(programName, subdirectory='src'):
    # filePath=NLPPath+os.sep+subdirectory+os.sep+programName
    if not os.path.isfile(GUI_IO_util.NLPPath + os.sep + subdirectory + os.sep + programName):
        mb.showerror("Input file error",
                     "The required file " + programName + " was not found. The file is expected to be in the subdirectory " + subdirectory + " of the main NLP directory.\n\nPlease, make sure to copy " + programName + " to the " + subdirectory + " subdirectory and try again.")
        return False
    return True

CoreNLP_download = "https://stanfordnlp.github.io/CoreNLP/download.html"
# 'https://nlp.stanford.edu/software/stanford-corenlp-latest.archive'
Gephi_download = "https://gephi.org/users/download/"
Google_Earth_download = "https://www.google.com/earth/download/gep/agree.html?hl=en-GB"
Java_download = "https://www.oracle.com/java/technologies/downloads/archive/"
MALLET_download = "http://mallet.cs.umass.edu/download.php"
# SENNA removed from SVO way too slow
# SENNA_download = "https://ronan.collobert.com/senna/download.html"
WordNet_download = "https://wordnet.princeton.edu/download/current-version"

# the function checks that if Stanford CoreNLP version matches with the latest downloadable version
def check_CoreNLPVersion(CoreNLPdir,calling_script=''):
    # get latest downloadable version
    try:
        response = requests.get("https://api.github.com/repos/stanfordnlp/CoreNLP/releases/latest")
    except:
        # no internet
        return False
    github_version = response.json()["name"][1:]
    # get local stanford corenlp version
    onlyfiles = [f for f in os.listdir(CoreNLPdir) if os.path.isfile(os.path.join(CoreNLPdir, f))]
    for f in onlyfiles:
        if f.startswith("stanford-corenlp-"):
            local_version = f[:-4].split("-")[2]
            if github_version != local_version:
                IO_user_interface_util.timed_alert(GUI_util.window, 6000, 'Stanford CoreNLP version',
                               "Oops! Your local Stanford CoreNLP version is " + local_version +
                               ".\n\nIt is behind the latest Stanford CoreNLP version available on GitHub (" + github_version + ").\n\nYour current version of Stanford CoreNLP will run anyway, but you should update to the latest release.",
                                                   False,'',True)
                # mb.showwarning("Warning", "Oops! Your local Stanford CoreNLP version is " + local_version +
                #                ".\n\nIt is behind the latest Stanford CoreNLP version available on GitHub (" + github_version + ").\n\nYour current version of Stanford CoreNLP will run anyway, but you should update to the latest release.")
                if calling_script != 'NLP_menu_main':
                    get_external_software_dir('calling_script', 'Stanford CoreNLP', silent=False, only_check_missing=False)
                return False
    return True

# the function checks that external programs (e.g., Gephi, StanfordCoreNLP) have been properly installed
#   it either reads a config csv file or it comes from having selected a program directory
def check_inputExternalProgramFile(calling_script, software_dir, programName, readingConfig=True, silent=False):
    unarchive_msg = ''
    head, tail = os.path.split(software_dir)
    if readingConfig:
        wrong_dir_msg = 'The software directory\n\n  ' + software_dir + '\n\nstored in the config file\n\nNLP_setup_external_software_config.csv\n\nis NOT the expected ' + programName.upper() + ' directory.'
    else:
        wrong_dir_msg = 'The selected software directory\n\n  ' + software_dir + '\n\nis NOT the expected ' + programName.upper() + ' directory.'
    if os.path.isdir(os.path.join(software_dir,tail)):
        unarchive_msg = '\n\nIt looks like your ' + programName + ' directory ' + software_dir + ' contains a ' + tail + ' directory inside. DO MAKE SURE THAT WHEN YOU UNARCHIVE THE ' + programName.upper() + ' ARCHIVE YOU DO NOT END UP WITH A ' + programName.upper() + ' DIRECTORY INSIDE A ' + programName.upper() + ' DIRECTORY.'
    select_directory_msg = '\n\nPlease, select the appropriate ' + programName.upper() + ' directory.'
    directory_content = '' # initialize variable
    Mac_msg = '\n\nOnce you have downloaded ' + programName.upper() + ' click on the downloaded .dmg file and drag the ' + programName.upper() + ' application in your Mac Applications folder.'
    message=''

    fileList = []
    if programName!='Java (JDK)':
        for file in os.listdir(software_dir):
            # create a list of files inside the program directory so that they can be checked for validity
            if os.listdir(software_dir):
                # if file.endswith(".txt"):
                # print(os.path.join(software_dir, file))
                fileList.append(file)

# Check Stanford CoreNLP
    if programName == 'Stanford CoreNLP':
        for item in fileList:
            if 'ejml' in str(item) or 'javax' in str(item):
                return True
        directory_content = wrong_dir_msg + '\n\nThe ' + programName.upper() + ' directory should contain, among other things, many files with \'ejml\' and \'javax\' in the filename.'
        message = directory_content + unarchive_msg + select_directory_msg

    # Check Gephi
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

# Check Google Earth Pro
    if programName == 'Google Earth Pro':
        if platform == 'win32':
            if 'client' in fileList:
                return True
            directory_content = wrong_dir_msg + '\n\nThe ' + programName.upper() + ' directory should contain the subdirectory \'client\n\nMOST LIKELY THE EXECUTABLE FILE WILL AUTOMATICALLY INSTALL GOOGLE EARTH PRO UNDER A FOLDER GOOGLE IN C:\Program Files.'
            message = directory_content + unarchive_msg + select_directory_msg

        if platform == 'darwin':
            if 'Google Earth Pro.app' in fileList:
                return True
            directory_content = '\n\nThe ' + programName.upper() + ' was not found among Mac applications.'
            message = directory_content + Mac_msg

# Check Java (JDK)
    if programName == 'Java (JDK)':
        if platform == 'win32':
            if 'java' in fileList and 'platform' in fileList:
                return True
            directory_content = wrong_dir_msg + '\n\nThe ' + programName.upper() + ' directory should contain, among other things, the subdirectories \'gephi\' and \'platform\''
            message = directory_content + unarchive_msg + select_directory_msg

# Check MALLET
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

# Check WordNet
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
    return False

def open_url(website_name, url, ask_to_open = False, message_title='', message='', config_filename='', reminder_title='', reminder_message=''):
    # check internet connection
    if not IO_internet_util.check_internet_availability_warning("Check on GitHub the NLP Suite newest release version"):
        return False
    # check if a reminder needs to be displayed
    if reminder_title != '':
        reminders_util.checkReminder(config_filename, reminder_title,
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
    sample_csv = [['Software', 'Path', 'Download_link'],
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
    # FIXED: must insert the new package into software-config.csv when the package is missing in the user csv file
    try:
        csv_file = open(software_config, 'r', newline='')
        existing_software_config = list(csv.reader(csv_file, delimiter=','))
    except:
        existing_software_config = list()
        existing_software_config = initialize_software_config_fields(existing_software_config)
    return existing_software_config

# gets a string of either missing or wrongly installed external software listed in config file:
#   CoreNLP, Gephi, Google Earth Pro, MALLET, WordNet
# warn user only if the specific package required to run a script is missing
def get_missing_external_software_list(calling_script, external_software_config_file, package, silent=False):
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

def get_software_config(softwareDir, package, existing_software_config):
    software_config = GUI_IO_util.configPath + os.sep + 'NLP_setup_external_software_config.csv'
    if not os.path.isfile(software_config):
        csv_fields = get_existing_software_config(software_config)
        with open(software_config, 'w+', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(csv_fields)

    # read the existing values of csv
    csv_fields = get_existing_software_config()
    for i, row in enumerate(csv_fields):
        if row[0] == package:
            csv_fields[i][1] = softwareDir  # update path of csv_fields
        else:
            csv_fields[i][1] = csv_fields[i][1] # copy current value
    return existing_software_config

# returns a double list [[]] of updated external software in NLP_setup_external_software_config.csv
def update_software_config(softwareDir, package, existing_software_config):
    for i, row in enumerate(existing_software_config):
        if row[0] == package:
            existing_software_config[i][1] = softwareDir  # update path of csv_fields
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
            message = message + "\n\nDon\'t forget that you have " + str(len(missing_software_list)) + " other remaining missing software to download/install: " + missing_software_string
        if not silent:
            mb.showwarning(title='Config installation file saved',
                       message=message)

# package is != '' when ...
#   1. the function is called from a specific script that uses the package (e.g., parsers_annotators_main)
#   2. the function is called from NLP_menu_main when clicking on the button Setup external software
# return software_dir, missing_software
def get_external_software_dir(calling_script, package, silent, only_check_missing):
    # get a list of software in software-config.csv
    existing_software_config = get_existing_software_config()
    software_dir = ''
    software_url = ''
    software_name = ''
    index = 0
    errorFound = False
    Cancel = False
    missing_software=''

    if package == '':
        title = 'NLP Suite external software download/install'
        download_website_msg = 'You can select whether to download and/or install required external software in the list (or exit setup).\n\nFor your convenience, if you select to download & install, the download function automatically opens the appropriate software download website. YOU NEED TO BE CONNECTED TO THE INTERNET!'
        download_install_list_msg = download_website_msg + '\n\nPlease, download and/or install the software in the list or some functionality will be lost for some of the scripts (e.g., you cannot do any textual analysis of any kind without spaCy, Stanford CoreNLP, or Stanza or produce any geographic maps without Google Earth Pro). The algorithms that use any of these programs will remind you that you need to install them if you want to run the algorithm. If you have already downloaded the software, you need to select the directory where you installed it; you will only have to do this once.\n\nDO YOU WANT TO DOWNLOAD/INSTALL THE SOFTWARE IN THE LIST NOW? THE ALGORITHM WILL LOOP THROUGH ALL THE PROGRAMS IN THE LIST (unless you press CANCEL).\n\nY = Download & install;\nN = Install;\nCANCEL to exit and download/install later'
        message = 'The NLP Suite relies on several external programs that need to be downloaded and installed.\n\nLIST OF PROGRAMS TO BE DOWNLOADED/INSTALLED:\n\n' + missing_software + download_install_list_msg
    else:
        title = package.upper() + ' software download/install'
        download_website_msg = 'You can select whether to download and/or install ' + package.upper() + ' (or exit setup).\n\nFor your convenience, the download function automatically opens the ' + package.upper() + ' download website. YOU NEED TO BE CONNECTED TO THE INTERNET!'
        if calling_script != 'NLP_menu':
            if platform == 'darwin' and (package == 'Gephi' or package == 'Google Earth Pro'):
                download_install_package_msg = download_website_msg + '\n\nDO YOU WANT TO DOWNLOAD/INSTALL ' + package.upper() + ' NOW?\n\nY = Download & install;\nN = Install;\nCANCEL to exit and download/install later'
            else:
                download_install_package_msg = download_website_msg + '\n\nDO YOU WANT TO DOWNLOAD/INSTALL ' + package.upper() + ' NOW?\n\nY = Download & install;\nN = Install;\nCANCEL to exit and download/install later'
                if 'NLP_setup_external_software_main' in calling_script:
                    message = download_install_package_msg
                else:
                    message = 'The script ' + calling_script.upper() + ' requires the external software ' + package.upper() + ' to run. The software has not been installed in the NLP Suite and you need to do so.\n\n' + download_install_package_msg
        else:
            if platform == 'darwin' and (package == 'Gephi' or package == 'Google Earth Pro'):
                download_install_package_msg = download_website_msg + '\n\nPlease, download/install ' + package.upper() + ' or some functionality will be lost for some of the scripts. You will only have to do this once.\n\nDO YOU WANT TO DOWNLOAD/INSTALL ' + package.upper() + ' NOW?\n\nY = Download & install;\nN = Install;\nCANCEL to exit and download/install later'
            else:
                download_install_package_msg = download_website_msg + '\n\nPlease, download/install ' + package.upper() + ' or some functionality will be lost for some of the scripts. If you have already downloaded the software, you need to select the directory where you installed it; you will only have to do this once.\n\nDO YOU WANT TO DOWNLOAD/INSTALL ' + package.upper() + ' NOW?\n\nY = Download & install;\nN = Install;\nCANCEL to exit and download/install later'
            message = download_install_package_msg

    # loop through all software in NLP_setup_external_software_config.csv file
    java_found = False
    for row in existing_software_config[1:]:  # skip header line
        answer = False
        index = index + 1
        software_name = row[0]
        # in releases prior to 3.8.5 Java (JDK) was not part of the config NLP_setup_external_software_config.csv
        if 'Java' in software_name:
            java_found=True
        software_dir = row[1]
        software_url = row[2]
        # if checking a specific external software (i.e., package)
        #   you do not want a list of missing external software
        if package!='' and package != software_name:
            continue
        # platform = 'darwin' # forcing darwin for testing in a Windows machine
        if software_dir == '':
            if missing_software=='':
                missing_software = str(software_name).upper() + '\n\n'
                errorFound = True
            else:
                if not 'Java version' in software_dir:
                    if 'Java' in software_name:
                        errorFound, error_code, system_output, java_version = check_java_installation('Java (JDK)')
                        if not errorFound:
                            software_dir="Java version "+java_version+" installed"
                    if (not 'Java' in software_name) or errorFound:
                        missing_software = missing_software + str(software_name).upper() + '\n\n'
                        errorFound=True
        else:
            errorFound=False
            # the software directory is stored in config file but...
            #   check that the software directory still exists and the package has not been moved
            ExternalProgramFile_result = check_inputExternalProgramFile(calling_script, software_dir, software_name, True, True )
            if not 'Java version' in software_dir:
                if os.path.isdir(software_dir) == False or ExternalProgramFile_result == False:
                    if missing_software == '':
                        missing_software = str(software_name).upper() + '\n\n'
                    else:
                        missing_software = missing_software + str(software_name).upper() + '\n\n'
                        # missing_software = missing_software + ',  ' + str(software_name).upper() + '\n\n'
                    errorFound=True
                else:
                    # if you are checking for a specific package and that is found return the appropriate directory
                    # unless called from NLP_menu_main
                    if (package.lower()!='') and (package.lower() in software_name.lower()) and (calling_script!='NLP_menu'):
                        return software_dir, software_url, missing_software

        if errorFound:
            software_dir = ''
            existing_software_config[index][1] = software_dir
            # if you are checking for a specific package and the directory is NOT found
            #   return None; no point continuing
            if (package.lower()!='') and (package.lower() in software_name.lower()):
                errorFound = False
                break
        if (package.lower()!='') and (package.lower() not in software_name.lower()):
            continue

        if (not errorFound) and (package!='') and ((calling_script=='NLP_menu') or (calling_script=='NLP_setup_external_software_main.py')):
            if package == 'Stanford CoreNLP':
                check_CoreNLPVersion(GUI_util.window,software_dir, calling_script)
                # software_dir = ''
                # missing_software = package
            answer = tk.messagebox.askyesno(title=package, message='The external software ' + package + ' is already installed at ' + software_dir + '\n\nDo you want to re-install the software, in case you moved it to a different location?')
            if answer == True:
                # initialize_software_config_fields(existing_software_config, package)
                delete_software_config(existing_software_config, package)
                missing_software = package
                software_dir = ''
            else:
                # if you are checking for a specific package and that is found return the appropriate directory
                if (package!=''):
                    return software_dir, software_url, missing_software


    # check for missing external software
    # check that Java is installed otherwise add to missing
    errorFound, error_code, system_output, java_version = check_java_installation('Java (JDK)')
    # in releases prior to 3.8.5 Java (JDK) was not part of the config NLP_setup_external_software_config.csv
    if not java_found:
        existing_software_config.insert(4,['Java (JDK)', "Java version "+java_version+" installed", Java_download])
        save_software_config(existing_software_config, missing_software, silent=True)
    # errorFound = True # for testing
    if errorFound:
        if missing_software=='':
            missing_software = str('Java (JDK)').upper() + '\n\n'
        else:
            missing_software = missing_software + str('Java (JDK)').upper() + '\n\n'

    if missing_software!='':
        if only_check_missing==True:
            return None, software_url, missing_software
        else:
            if calling_script != 'NLP_setup_external_software_main.py':
                call("python NLP_setup_external_software_main.py", shell=True)

        if software_dir == '':
            software_dir = None # specific calling scripts (e.g. Stanford CoreNL) check for None
        # after installation, check again for missing software
        # missing_software = get_missing_external_software_list(calling_script, existing_software_config, package)

    return software_dir, software_url, missing_software


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
def external_software_download(calling_script, software_name, existing_software_config):
    software_dir, software_url, missing_software = get_external_software_dir(calling_script, software_name,
                                                                             silent=False, only_check_missing=False)
    if 'Java' in software_name:
        # since Stanford CoreNLP, Gephi, and MALLET need Java, check for Java installation
        errorFound, error_code, system_output, java_version = check_java_installation(software_name)
        software_dir="Java version "+java_version+" installed"
    else:
        if software_dir == None:
            software_dir = ''

    archive_location_warning = '\n\nDO NOT MOVE THE EXTERNAL SOFTWARE FOLDER INSIDE THE NLP SUITE FOLDER OR IT MAY BE OVERWRITTEN IN CASE YOU NEED TO RE-INSTALL THE SUITE.'
    # Setup user messages for the various types of external software and platforms
        # in Mac, Gephi and Google Earth Pro are installed in Applications
    if platform == 'darwin' and (software_name != 'Google Earth Pro' and software_name != 'Gephi' and software_name != 'Java (JDK)'):
        message2 = "You will be asked next to select the directory (NOT Mac Applications!) where the software\n\n" + software_name.upper() + "\n\nwas installed after downloading; you can press CANCEL or ESC if you have not downloaded the software yet."
    if platform == 'darwin' and (software_name == 'Google Earth Pro' or software_name == 'Gephi'):
        message2 = "You will be asked next to select the Mac Applications directory where the software\n\n" + software_name.upper() + "\n\nwas installed after downloading; you can press CANCEL or ESC if you have not downloaded the software yet."
    if platform == 'win32' and software_name != 'Java (JDK)':
        message2 = "You will be asked next to select the directory where the software\n\n" + software_name.upper() + "\n\nwas installed after downloading; you can press CANCEL or ESC if you have not downloaded the software yet."
    if platform != 'darwin' and (software_name != 'Google Earth Pro' and software_name != 'Gephi' and software_name != 'Java (JDK)'):
        message1 = "\n\nYou will then be asked to select the directory where the software\n\n" + software_name.upper() + "\n\nwas installed after downloading; you can press CANCEL or ESC if you have not downloaded the software yet."
        message3 = ". Please, select the directory where the software was installed after downloading; you can press CANCEL or ESC if you have not downloaded the software yet."
    else:
        message1 = ""
        message3 = ""

    if software_dir != '':  # and package.lower() in software_name.lower():
        answer = tk.messagebox.askyesno(software_name + " download",
                                        software_name + " has already been downloaded and installed. Do you want to access the package url\n\n  " + software_url + "\n\nand download it again?")
        if not answer:
            return software_dir, software_url

    # Stanford CoreNLP, MALLET download zip files which must be treated differently from straight executable files
    archive_message = ''
    title=software_name.upper() +' download'

# MALLET DOWNLOAD Messages for MALLET

    if software_name == 'MALLET':
        MALLET_msg = '\n\nA MALLET DIRECTORY CANNOT CONTAIN BLANKS (SPACES) IN THE PATH. THE MALLET CODE CANNOT HANDLE PATHS THAT CONTAIN A SPACE AND WILL BREAK.'
    else:
        MALLET_msg = ''

# CoreNLP, MALLET, WordNet in Mac are archived files
# DOWNLOAD Messages for Stanford CoreNLP, SENNA, MALLET, WordNet in Mac

    if software_name=='Stanford CoreNLP' or \
            software_name == 'MALLET' or \
            (platform == 'darwin' and software_name == 'WordNet'):
        archive_message=', double click on the downloaded file to unarchive it, move the entire software folder to a location of your choice (e.g., desktop), '
        archive_warning='\n\nDO MAKE SURE THAT WHEN YOU UNARCHIVE ' + software_name + ' YOU DO NOT END UP WITH A ' + software_name + ' DIRECTORY INSIDE A ' + software_name + ' DIRECTORY.' + archive_location_warning

# Gephi and Google Earth Pro in Mac are automatically installed in Applications
# GEPHI & GOOGLE EARTH DOWNLOAD Messages for Gephi, Google Earth Pro

    if software_name == 'Gephi' or software_name == 'Google Earth Pro':
        if platform == 'win32':
            message = 'After downloading ' + software_name.upper() + ' run the executable file and move the ' + software_name.upper() + ' folder to a location of your choice (e.g., desktop).' + archive_location_warning
            message = message + message1
        if platform == 'darwin':
            message = message + '\n\nAfter the download completes, click on the downloaded .dmg file and drag the ' + software_name.upper() + ' application in your Mac Applications folder.'
    else:
        #
        archive_message = ', double click on the downloaded file to unarchive it, move the entire software folder '
        archive_warning = ''
        message='After downloading ' + software_name.upper() + archive_message + 'to a directory of your choice (e.g., desktop), and select that directory when prompted for installation so that the NLP Suite algorithms will know where to find ' + software_name.upper() + ' on your hard drive.' + archive_location_warning + archive_warning + MALLET_msg

# JAVA DOWNLOAD Messages for Java
    if 'Java' in software_name:
        message='To download Java from the Oracle website, you will need to sign in in your Oracle account (you must create a FREE Oracle account if you do not have one).\n\nSelect the most current Java SE version then download the JDK suited for your machine (Mac/Windows) and finally run the downloaded executable.'

# WORDNET DOWNLOAD Messages for WordNet (executable in Windows, archive tar.gz in Mac)
    if software_name == 'WordNet':
        mb.showwarning(title=software_name.upper() + ' with Chrome',
                       message='If you use Chrome as a browser and after clicking on the download link nothing happens, most likely Chrome has blocked the download operation. You have two options. Right click on the download executable and ...\n   1. Select "Open link in new window." and refresh or hit return to start downloading.\n   2. Select "Copy link address", start a new tab, paste the copied address and refresh or hit return to start downloading.')
        if platform == 'darwin':
            message = 'Once the WORDNET website opens up, you need to download the executable file WordNet-3.0.tar.gz. double click on the file to unpack the archive and move the WordNet folder to a location of your choice (e.g., desktop).' + message1
        # only the Windows version is an exe file
        # the Mac version is a compressed tar.gz file
        if platform == 'win32':
            message = 'Once the WORDNET website opens up, you need to download the executable file WordNet-2.1.exe. After downloading, run the executable file and move the WordNet folder to a location of your choice (e.g., desktop).' + archive_location_warning + message1

    mb.showwarning(title=title,
                   message=message)

# DOWNLOAD open software download website

    open_url(software_name, software_url)

# DOWNLOAD JAVA for CoreNLP, Gephi, MALLET

    if software_name == 'Stanford CoreNLP' or software_name == 'Gephi' or software_name == 'MALLET':
        # since Stanford CoreNLP, Gephi, and MALLET need Java, check for Java installation
        errorFound, error_code, system_output, java_version = check_java_installation(software_name)
        # url = 'https://www.oracle.com/java/technologies/downloads/archive/'
        # errorFound=True # for testing
        if errorFound:
            Java_required = software_name + ' requires the freeware Java (by Oracle) installed on our machine.\n\nDon\'t forget to download and install Java JDK.'
            mb.showwarning(title='Warning',message=Java_required)
            # open_url('Java', url, ask_to_open = True, message_title = 'Java', message = Java_required)
    software_dir, existing_software_config = external_software_install(calling_script, software_name, existing_software_config)
    return software_dir, software_url

# INSTALLING -------------------------------------------------------------------------------
# updates the array existing_software_config with the value of software_dir
# returns the software_dir and the double list existing_software_config = [[]]
def external_software_install(calling_script, software_name, existing_software_config):
    software_dir, software_url, missing_software = get_external_software_dir(calling_script, software_name,
                                                                             silent=False, only_check_missing=False)
    if 'Java' in software_name:
        # since Stanford CoreNLP, Gephi, and MALLET need Java, check for Java installation
        errorFound, error_code, system_output, java_version = check_java_installation(software_name)
        software_dir="Java version "+java_version+" installed"
    else:
        if software_dir == None:
            software_dir = ''

    if software_dir == '': #  and package.lower() in software_name.lower():
        if platform == 'darwin' and (software_name != 'Google Earth Pro' and software_name != 'Gephi'):
            message2 = "You will be asked next to select the directory (NOT Mac Applications!) where the software\n\n" + software_name.upper() + "\n\nwas downloaded, so that it can be installed on your machine.\n\nYou can press CANCEL or ESC if you have not downloaded the software yet or you do not want to install the software now."
        if platform == 'darwin' and (software_name == 'Google Earth Pro' or software_name == 'Gephi'):
            message2 = "You will be asked next to select the Mac Applications directory where the software\n\n" + software_name.upper() + "\n\nwas downloaded, so that it can be installed on your machine.\n\nYou can press CANCEL or ESC if you have not downloaded the software yet or you do not want to install the software now."
        if platform == 'win32':
            message2 = "You will be asked next to select the directory where the software\n\n" + software_name.upper() + "\n\nwas downloaded, so that it can be installed on your machine.\n\nYou can press CANCEL or ESC if you have not downloaded the software yet or you do not want to install the software now."
        if platform != 'darwin' and (software_name != 'Google Earth Pro' and software_name != 'Gephi'):
            message1 = "\n\nYou will then be asked to select the directory where the software\n\n" + software_name.upper() + "\n\nwas downloaded, so that it can be installed on your machine.\n\nYou can press CANCEL or ESC if you have not downloaded the software yet or you do not want to install the software now."
            message3 = ". Please, select the directory where the software was downloaded, so that it can be installed on your machine.\n\nYou can press CANCEL or ESC if you have not downloaded the software yet or you do not want to install the software now."
        else:
            message1 = ""
            message3 = ""

    if software_dir != '':  # and package.lower() in software_name.lower():
        mb.showwarning(title=software_name+' installation.',message=software_name+' is already installed. If you want to change the installation directory, select next a new directory, otherwise press Esc or Cancel when the dialogue box opens.')
        temp_software_dir = tk.filedialog.askdirectory(initialdir=software_dir,
                                                  title='Select a new directory for ' + software_name + '. Press Esc or Cancel to exit.')
        if temp_software_dir !='':
            if not check_inputExternalProgramFile(calling_script, temp_software_dir, software_name, False, False):
                software_dir = None
            else:
                software_dir = temp_software_dir
    else:
        existing_software_config = get_existing_software_config()

        # get software directory
        while software_dir == '':

            # on Mac Gephi and Google Earth Pro are installed in Applications
            if platform == 'darwin':
                # GEPHI INSTALLATION
                if software_name == 'Gephi':
                    software_dir = "/Applications"
                # GOOGLE EARTH PRO INSTALLATION
                if software_name == 'Google Earth Pro':
                    software_dir = "/Applications"
            if platform == 'darwin' or platform == 'win32':
                # should not start from NLP/src since users are strongly advised NT to install external softare inside the NLP Suite folder
                # initialFolder = os.path.dirname(os.path.abspath(__file__))
                initialFolder = ''
                title = software_name.upper() + ' software installation'
                mb.showwarning(title=title,
                               message=message2)

                software_dir = tk.filedialog.askdirectory(initialdir=initialFolder,
                                                  title=title + message3)
                if software_dir == '': # hit CANCEL in file dialog
                    Cancel = True
                    software_dir = None # to exit while loop
            # INSTALLATION
            if software_dir != '' and software_dir != None:
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
                # check that the selected folder for the external program is correct; if so save
                if not check_inputExternalProgramFile(calling_script, software_dir, software_name, False):
                    software_dir = None

    # update the array existing_software_config with the value of software_dir
    if software_dir != '' and software_dir != None:
        existing_software_config = update_software_config(software_dir, software_name, existing_software_config)
    return software_dir, existing_software_config
