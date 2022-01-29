import csv
import sys
from sys import platform
import os
import tkinter as tk
import tkinter.messagebox as mb
import subprocess
import psutil
from psutil import virtual_memory
from typing import List
import webbrowser

import GUI_IO_util
import reminders_util
import TIPS_util
import IO_internet_util

# import pip not used
# def install(package):
#     pip.main(['install', package])

# tkcolorpicker requires tkinter and pillow to be installed (https://libraries.io/pypi/tkcolorpicker)
# tkcolorpicker is both the package and module name
# pillow is the Python 3 version of PIL which was an older Python 2 version
# PIL being the commmon module for both packages, you need to check for PIL and trap PIL to tell the user to install pillow

def install_all_packages(window, calling_script, modules_to_try):
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
        # root = tk.Tk()
        # root.withdraw()
        window.withdraw()
        if len(missingModules) == 1:
            msg = missingModules[0]
        elif len(missingModules) > 1:
            msg = 'each of the listed modules'
        mb.showwarning(title='Module import error',
                       message="FATAL ERROR. Please, read carefully. The NLP Suite will exit.\n\nThe script '" + calling_script + "' needs to import the following modules:\n\n" + ', '.join(
                           missingModules) + "\n\nPlease, in command prompt/terminal, type\nconda activate NLP\nto activate the right NLP environment (NLP case sensitive) where to install the package, then use the command\npip install " + str(
                           msg) + "\nand try again.\n\nTo install a specific version of a package use: pip install SomePackage==1.0.4 where SomePackage can be Spacy, wordcloud or whatever package you are trying to install and 1.0.4 will be the specific version you want to install.\n\nTo find the package version currently installed on your machine, type: conda list to list the version of all the packages, or conda list SomePackage for a a specific package.\n\nYOU MUST BE CONNECTED TO THE INTERNET TO INSTALL MODULES!\n\nThe installation of some modules (e.g., pdfminer.six) may give you a permission error. In that case, add --user to the pip command, for instance, pip install pdfminer.six --user.")
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
                return False
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
        return False
        # install(e.name)
    return True


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
    import IO_user_interface_util
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

# return errorFound, error_code, system_output
def check_java_installation(script):
    errorFound = False
    java_output = subprocess.run(['java', '-version'], capture_output=True)
    error_code = java_output.returncode  # Should be 0 if java installed
    system_output = java_output.stderr.decode(
        'utf-8')  # This is what you see when you run "java -version" in your command line

    if not system_output:
        # Java issues do not seem to be a problem with Mac
        if platform == "win32" and 'CoreNLP' in script:
            title_options = ['Java JDK version']
            message = 'You are running ' + system_output.split("\r\n""", 1)[
                0] + '.\n\nStanford CoreNLP works best with Java version JDK 8 on Windows machines.\n\nIf you run into problems with Stanford CoreNLP, you may wish to uninstall the Java version you are currently running and install Java JDK 8. Please, read the installation instructions on the NLP Suite GitHub wiki pages at\nhttps://github.com/NLP-Suite/NLP-Suite/wiki/Install-External-Software#JAVA-JDK.'
            reminders_util.checkReminder('Stanford-CoreNLP_config.csv', title_options,
                                         message, True)

    if system_output:
        if platform == "win32" and 'CoreNLP' in script:
            for info in system_output.split(" "):
                if "-Bit" in info:  # find the information about bit
                    if info[:2] != "64":  # check if it's 64 bit
                        answer = tk.messagebox.askyesno("Java version Error",
                                                        "You are not using JAVA 64-Bit version.\n\nThis will cause an error running Stanford CoreNLP: Could not create the Java Virtual Machine.\n\nPlease, configure your machine to use JAVA 64-Bit.\n\nPlease, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.\n\nDo you want to open the TIPS file now?")
                        if answer:
                            TIPS_util.open_TIPS('TIPS_NLP_Stanford CoreNLP memory issues.pdf')
                        errorFound = True

    if error_code != 0 and "not recognized" in system_output:
        mb.showwarning(title='Java installation error',
                       message='A test for Java returned a non-zero error code ' + str(
                           error_code) + ' and Java not recognized (You can check this in command line by typing Java -version). Java is not installed.\n\n' + script + ' is a Java script that requires Java installed on your machine (you need the JDK version, Java Development Kit; install Java JDK 8, which seems to work best for Stanford CoreNLP).\n\nPlease, read the Java installation TIPS, install Java and try again. Program will exit.')
        errorFound = True
    elif error_code != 0:
        mb.showwarning(title='Java error',
                       message='A test for Java returned a non-zero error code ' + str(
                           error_code) + ' with the following system error: ' + system_output + '.\n\nJava may not be properly installed.\n\n' + script + ' is a Java script that requires Java installed on your machine (you need the JDK version, Java Development Kit; install Java JDK 8, which seems to work best for Stanford CoreNLP).\n\nPlease, read the Java installation TIPS, check your Java installation, install Java properly and try again (go to command line and type Java -version). Program will exit.')
        errorFound = True

    return errorFound, error_code, system_output


CoreNLP_download = "https://stanfordnlp.github.io/CoreNLP/download.html"
# 'https://nlp.stanford.edu/software/stanford-corenlp-latest.zip'
MALLET_download = "http://mallet.cs.umass.edu/download.php"
SENNA_download = "https://ronan.collobert.com/senna/download.html"
WordNet_download = "https://wordnet.princeton.edu/download/current-version"
Gephi_download = "https://gephi.org/users/download/"
Google_Earth_download = "https://www.google.com/earth/download/gep/agree.html?hl=en-GB"

def inputProgramFileCheck(programName, subdirectory='src'):
    # filePath=NLPPath+os.sep+subdirectory+os.sep+programName
    if not os.path.isfile(GUI_IO_util.NLPPath + os.sep + subdirectory + os.sep + programName):
        mb.showerror("Input file error",
                     "The required file " + programName + " was not found. The file is expected to be in the subdirectory " + subdirectory + " of the main NLP directory.\n\nPlease, make sure to copy " + programName + " to the " + subdirectory + " subdirectory and try again.")
        return False
    return True


def inputExternalProgramFileCheck(software_dir, programName):

    fileList = []
    if platform == 'darwin':
        for file in os.listdir('/Applications'):
            if 'Gephi' in file:
                fileList.append('gephi')
            if 'Google Earth Pro' in file:
                fileList.append('google earth pro')
    for file in os.listdir(software_dir):
        # if file.endswith(".txt"):
        # print(os.path.join(software_dir, file))
        fileList.append(file)
    if programName == 'Stanford CoreNLP':
        for item in fileList:
            if 'stanford-corenlp' in str(item):
                return True
        mb.showwarning(title='Software error',
                       message="The selected software directory\n  " + software_dir + "'\nis NOT the expected CoreNLP directory. The directory should contain, among other things, many files with \'stanford-corenlp\' in the filename. DO MAKE SURE THAT WHEN YOU UNZIP THE STANFORD CORENLP ARCHIVE YOU DO NOT END UP WITH A STANFORD CORENLP DIRECTORY INSIDE A STANFORD CORENLP DIRECTORY.\n\nPlease, select the appropriate CoreNLP directory and try again!\n\nYou can download Stanford CoreNLP at " + CoreNLP_download + ".\n\nPlease, read the TIPS_NLP_Stanford CoreNLP download install run.pdf and the NLP_TIPS_Java JDK download install run.pdf.")
        return False
    if programName == 'Mallet':
        # check that Mallet has no spaces in path
        if ' ' in software_dir:
            mb.showerror(title='Mallet directory error',
                         message='The selected Mallet directory \n   ' + software_dir + '\ncontains a blank (space) in the path. The Mallet code cannot handle paths that contain a space and will break.\n\nPlease, place place Mallet in a directory with a path containing no spaces and try again.')
            return False
        if 'bin' in fileList and 'class' in fileList:
            return True
        else:
            mb.showwarning(title='Software error',
                           message="The selected software directory\n  " + software_dir + "'\nis NOT the expected Mallet directory. The directory should contain, among other things, the directories \'bin\' and \'class\'. DO MAKE SURE THAT WHEN YOU UNZIP THE MALLET ARCHIVE YOU DO NOT END UP WITH A MALLET DIRECTORY INSIDE A MALLET DIRECTORY.\n\nPlease, select the appropriate Mallet directory and try again!\n\nYou can download Mallet at " + MALLET_download + ".\n\nPlease, read the TIPS_NLP_Topic modeling Mallet installation.pdf and the NLP_TIPS_Java JDK download install run.pdf.")

            return False
    if programName == 'SENNA':
        if 'senna-osx' in fileList and 'senna-win32.exe' in fileList:
            return True
        else:
            mb.showwarning(title='Software error',
                           message="The selected software directory\n  " + software_dir + "'\nis NOT the expected SENNA directory. The directory should contain, among other things, the files \'senna-osx\' and \'senna-win32.exe\'. DO MAKE SURE THAT WHEN YOU UNZIP THE SENNA ARCHIVE YOU DO NOT END UP WITH A SENNA DIRECTORY INSIDE A SENNA DIRECTORY.\n\nPlease, select the appropriate SENNA directory and try again!\n\nYou can download SENNA at " + SENNA_download + ".")
            return False
    if programName == 'WordNet':
        if 'dict' in fileList and 'src' in fileList:
            return True
        else:
            mb.showwarning(title='Software error',
                    message="The selected software directory\n  " + software_dir + "'\nis NOT the expected WordNet directory. The directory should contain, among other things, the directories \'dict\' and \'src\'. DO MAKE SURE THAT WHEN YOU UNZIP THE WORDNET ARCHIVE YOU DO NOT END UP WITH A WORDNET DIRECTORY INSIDE A WORDENET DIRECTORY.\n\nPlease, select the appropriate WordNet directory and try again!\n\nYou can download WordNet at " + WordNet_download + ".\n\nPlease, read the TIPS_NLP_WordNet.pdf.")
            return False
    if programName == 'Gephi':
        if platform == 'win32':
            if 'gephi' in fileList and 'gephi' in fileList and 'platform' in fileList:
                return True
            else:
                mb.showwarning(title='Software error',
                               message="The selected software directory\n  " + software_dir + "'\nis NOT the expected Gephi directory. The directory should contain, among other things, the directories \'gephi\' and \'platform\'.\n\nPlease, select the appropriate Gephi directory and try again!\n\nYou can download Gephi at " + Gephi_download + ". Make sure you have a recent Java installed on your system. Gephi is compatible with Java 7 and 8 versions. After the Gephi download completes, run the installer and follow the steps.\n\nPlease, read the TIPS_NLP_Gephi.pdf.")
                return False
        if platform == 'darwin':
            if 'gephi' in fileList:
                return True
            else:
                mb.showwarning(title='Software error',
                               message="Gephi was not found among Mac applications.\n\nYou can download Gephi at " + Gephi_download + ".\n\nAfter the download completes, click on the downloaded .dmg file and drag the Gephi application in your Mac Applications folder.\n\nPlease, read the TIPS_NLP_Gephi.pdf.")
                return False

    if programName == 'Google Earth Pro':
        if platform == 'win32':
            if 'client' in fileList:
                return True
            else:
                expected_GEP_files = "The directory should contain the subdirectory \'client'\n\nMOST LIKELY THE EXECUTABLE FILE WILL AUTOMATICALLY INSTALL GOOGLE EARTH PRO UNDER A FOLDER GOOGLE IN C:\Program Files."
        if platform == 'darwin':
            if 'google earth pro' in fileList:
                return True
            mb.showwarning(title='Software error',
                           message = "Google Earth Pro was not found among Mac applications.\n\nYou can download Google Earth Pro at " + Google_Earth_download + ".\n\nPlease, read the TIPS_NLP_Google Earth Pro.pdf.")
            return False

def update_csv_fields(existing_csv: list) -> list:
    """

    @param existing_csv: current csv file in list format, similar to sample_csv below
    @return: the new csv files, with software fields up to date.
    """
    sample_csv = [['Software', 'Path', 'Download_link'],
                  ['Stanford CoreNLP', '', CoreNLP_download],
                  ['Mallet', '', MALLET_download],
                  ['SENNA', '', SENNA_download],
                  ['WordNet', '', WordNet_download],
                  ['Gephi', '', Gephi_download],
                  ['Google Earth Pro', '', Google_Earth_download]]
    fields = [x[0].lower() for x in existing_csv]
    for (index, row) in enumerate(sample_csv):
        if row[0].lower() not in fields:
            existing_csv.append(sample_csv[index])
    return existing_csv

def get_existing_software_config():
    software_config = GUI_IO_util.configPath + os.sep + 'software_config.csv'
    # FIXED: must insert the new package into software-config.csv when the package is missing in the user csv file
    try:
        csv_file = open(software_config, 'r', newline='')
        existing_csv = list(csv.reader(csv_file, delimiter=','))
    except:
        existing_csv = list()
    update_csv_fields(existing_csv)
    return existing_csv

# gets a list of the external software: CoreNLP, SENNA, WordNet, MALLET, Google Earth Pro, Gephi
def get_missing_external_software_list(existing_csv):
    if existing_csv=='':
        existing_csv=get_existing_software_config()
    index = 0
    missing_software=''
    for row in existing_csv[1:]:  # skip header line
        software_name = row[0]
        download_software = row[2]
        index = index + 1
        if existing_csv[index][1]=='':
            missing_software = missing_software + str(software_name).upper() + ' download at ' + str(download_software + '\n\n')
    return missing_software

def save_software_config(new_csv,package):
    software_config = GUI_IO_util.configPath + os.sep + 'software_config.csv'
    with open(software_config, 'w+', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(new_csv)

    mb.showwarning(title=package.upper() + ' installation path saved',
                               message="The installation path of " + package.upper() + " was successfully saved to " + software_config)

# when coming from NLP_menu_main only_check_missing is set to True to set te checkbox to 0/1 if there is/isn't missing software
def get_external_software_dir(calling_script, package, silent=False, only_check_missing=False):
    # get a list of software in software-config.csv
    existing_csv = get_existing_software_config()
    download_software = ''
    missing_software = ''
    software_dir = None
    # software_dir = ''
    software_name = ''
    index = 0
    errorFound = False
    # get any existing software_config csv file
    for row in existing_csv[1:]:  # skip header line
        index = index + 1
        software_name = row[0]
        software_dir = row[1]
        download_software = row[2]
        if software_dir == '':  # check path field; software_dir == '' the software has not been downloaded and installed yet
            print("MISSING SOFTWARE", str(software_name).upper() + ' download at ' + str(download_software))
            errorFound=True
        else:
            errorFound=False
            # the software directory is stored in config file but...
            #   check that the software directory still exists and the package has not been moved
            if platform == 'darwin' and software_dir == '/Applications':
                if (package.lower()!='') and (package.lower() in software_name.lower()) and (calling_script!='NLP_menu'):
                    return software_dir, missing_software
            if os.path.isdir(software_dir) == False or inputExternalProgramFileCheck(software_dir, software_name) == False:
                mb.showwarning(title='Directory error',
                               message='The directory\n  ' + software_dir + '\nstored in the software config file\n  ' + GUI_IO_util.configPath + os.sep + 'software_config.csv' + '\nno longer exists. It may have been renamed, deleted, or moved.\n\nYou must re-select the ' +
                                       software_name.upper() + ' directory.')
                errorFound=True
                silent = False
            else:
                # if you are checking for a specific package and that is found return the appropriate directory
                # unless called from NLP_menu_main
                if (package.lower()!='') and (package.lower() in software_name.lower()) and (calling_script!='NLP_menu'):
                    return software_dir, missing_software

        if errorFound:
            software_dir = ''
            existing_csv[index][1] = software_dir
            missing_software = missing_software + str(software_name).upper() + ' download at ' + str(download_software + '\n\n')
            # if you are checking for a specific package and the directory is NOT found
            #   return None; no point continuing
            if (package.lower()!='') and (package.lower() in software_name.lower()):
                errorFound = False
                break
        if (package.lower()!='') and (package.lower() not in software_name.lower()):
            continue

        if (not errorFound) and (package!='') and (calling_script=='NLP_menu'):

            mb.showwarning(title=package,
                           message='The external software ' + package + ' is up-to-date and correctly installed at ' + software_dir)
            # if you are checking for a specific package and that is found return the appropriate directory
            if (package!=''):
                return software_dir, missing_software

    # check for missing external software
    if len(missing_software) > 0:
        if only_check_missing==True:
            return None, missing_software
        if 'NLP_menu' in calling_script:  # called from NLP_main GUI. We just need to warn the user to download and install options
            title = 'NLP Suite external software ' + str(package.upper())
            if package=='':
                message = 'The NLP Suite relies on several external programs that need to be installed.\n\nLIST OF PROGRAMS TO BE INSTALLED:\n\n' + missing_software + 'Please, download and install the software in the list or some functionality will be lost for some of the scripts (e.g., you cannot do any textual analysis of any kind without Stanford CoreNLP or produce any geographic maps without Google Earth Pro). The algorithms that use any of these programs will remind you that you need to install them if you want to run the algorithm. If you have already downloaded the software, you need to select the directory where you installed it; you will only have to do this once.\n\nDO YOU WANT TO DOWNLOAD/INSTALL THE SOFTWARE IN THE LIST NOW?\n\nY = Download & install;\nN = Install;\nCANCEL to exit and download/install later?'
            else:
                message = 'Please, download/install the selected software ' + package.upper() + ' or some functionality will be lost for some of the scripts (e.g., you cannot do any textual analysis of any kind without Stanford CoreNLP or produce any geographic maps without Google Earth Pro). The algorithms that use any of these programs will remind you that you need to install them if you want to run the algorithm. If you have already downloaded the software, you need to select the directory where you installed it; you will only have to do this once.\n\nDO YOU WANT TO DOWNLOAD/INSTALL ' + package.upper() + ' NOW?\n\nY = Download & install;\nN = Install;\nCANCEL to exit and download/install later?'
        else:
            title = package.upper() + ' software'
            message = 'WARNING!\n\nThe script ' + calling_script.upper() + ' requires the external software ' + package.upper() + \
                      ' to run.\n\nIf you have not downloaded and installed ' + package.upper() + ' yet, you can do that at ' + download_software + '\n\nIf you have already downloaded ' + package.upper() + ', you meed to select the directory where you installed it; you will only have to do this once.\n\nDO NOT INSTALL EXTERNAL SOFTWARE INSIDE THE NLP SUITE FOLDER OR THEY BE OVERWRITTEN WHEN YOU UPGRADE THE SUITE.\n\nDo you want to download/install this software now?\n\nY = Download & install;\nN = Install;\nCANCEL to exit'
        # already downloaded the software, you meed to select the directory where you installed it; ESC or CANCEL to exit if you haven\'t installed it yet.

        if not silent:
            answer = tk.messagebox.askyesnocancel(title, message)
            # Y answer = TRUE download & install
            # N answer = FALSE install
            # CANCEL answer = None

            exit_for_loop = False
            # mb.showwarning(title=title, message=message)
            if answer == None:
                software_dir = None
            else:
                for (index, row) in enumerate(existing_csv[1:]): # skip header row
                    if exit_for_loop:
                        break
                    index = index + 1
                    software_name = row[0]
                    software_dir = row[1]
                    software_download = row[2]

                    if package!='' and package!=software_name:
                        continue

# Setup user messages for the various types f external software and platforms

                    if platform == 'darwin':
                        message2 = "You will be asked next to select the Mac Applications directory where the software " + software_name.upper() + " was installed after downloading; you can press CANCEL or ESC if you have not downloaded the software yet."
                    if platform == 'win32':
                        message2 = "You will be asked next to select the directory where the software " + software_name.upper() + " was installed after downloading; you can press CANCEL or ESC if you have not downloaded the software yet."
                    if platform == 'darwin' and (software_name == 'Google Earth Pro' or software_name == 'Gephi'):
                        message1 = "\n\nYou will then be asked to select the Mac Applications directory where the software " + software_name.upper() + " was installed after downloading; you can press CANCEL or ESC if you have not downloaded the software yet."
                        message3 = "Please, select the Mac Applications directory where the software " + software_name.upper() + " was installed after downloading; you can press CANCEL or ESC if you have not downloaded the software yet."
                    else:
                        message1 = "\n\nYou will then be asked to select the directory where the software " + software_name.upper() + " was installed after downloading; you can press CANCEL or ESC if you have not downloaded the software yet."
                        message3 = ". Please, select the directory where the software was installed after downloading; you can press CANCEL or ESC if you have not downloaded the software yet."

                    # DOWNLOADING answer is True for downloading
                    if answer == True and software_dir == '':  # Yes Download if software not installed
                        # Stanford CoreNLP, MALLET, SENNA download zip files which must be treated differently from straight executable files
                        zip_message = ''
                        title=software_name.upper() +' download'

# Messages for MALLET

                        if software_name == 'MALLET':
                            MALLET_msg = '\n\nA MALLET DIRECTORY CANNOT CONTAIN BLANKS (SPACES) IN THE PATH. THE MALLET CODE CANNOT HANDLE PATHS THAT CONTAIN A SPACE AND WILL BREAK.'
                        else:
                            MALLET_msg = ''

# Messages for Stanford CoreNLP, SENNA, MALLET, WordNet in Mac

                        if software_name=='Stanford CoreNLP' or software_name == 'SENNA' or software_name == 'MALLET' or (platform == 'darwin' and software_name == 'WordNet'):
                            zip_message=', UNARCHIVE the downloaded archived file, and move the entire unarchived folder '
                            zip_warning='\n\nDO MAKE SURE THAT WHEN YOU UNARCHIVE ' + software_name + ' YOU DO NOT END UP WITH A ' + software_name + ' DIRECTORY INSIDE A ' + software_name + ' DIRECTORY.'

# Messages for Gephi, Google Earth Pro, and WordNet in Windows

                        if software_name == 'Gephi' or software_name == 'Google Earth Pro' or (platform == 'win32' and software_name == 'WordNet'):
                            message = 'After downloading ' + software_name.upper() + ' run the executable file.'
                            message = message + message1
                            if platform == 'darwin':
                                message = message + ' The software will be installed among the Mac applications.'
                        else:
                            zip_message = ', move the downloaded and unarchived software '
                            zip_warning = ''
                            message='After downloading ' + software_name.upper() + zip_message + 'to a directory of your choice and select that directory for installation, so that the NLP Suite algorithms will know where to find ' + software_name + ' on your hard drive.' + '\n\nDO NOT INSTALL EXTERNAL SOFTWARE INSIDE THE NLP SUITE FOLDER OR THEY MAY BE OVERWRITTEN WHEN YOU UPGRADE THE SUITE.' + zip_warning + MALLET_msg

                        if software_name == 'WordNet':
                            if platform == 'darwin':
                                message = 'Once the WORDNET website opens up, you need to download the executable file WordNet-3.0.tar.gz. Right-click on the file to unpack the archive and install it.' + message1
                            # only the Windows version is an exe file
                            # the Mac version is a compressed tar.gz file
                            if platform == 'win32':
                                message= 'Once the WORDNET website opens up, you need to download the executable file WordNet-2.1.exe. After downloading, run the executable file.' + message1

                        mb.showwarning(title=title,
                                       message=message)
                        # check internet connection
                        if not IO_internet_util.check_internet_availability_warning('NLP_menu_main'):
                            return

# DOWNLOAD WordNet
                        if software_name == 'WordNet':
                            mb.showwarning(title=software_name.upper()+ ' with Chrome',
                                           message='If you use Chrome as a browser and after clicking on the download link nothing happens, most likely Chrome has blocked the download operation. You have two options. Right click on the download executable and ...\n   1. Select "Open link in new window." and refresh or hit return to start downloading.\n   2. Select "Copy link address", start a new tab, paste the copied address and refresh or hit return to start downloading.')

                        # open software download website
                        webbrowser.open_new(software_download)

# DOWNLOAD JAVA for CoreNLP or Gephi

                        if software_name == 'Stanford CoreNLP' or software_name == 'Gephi':
                            # since Stanford CoreNLP and Gephi need Java, check for Java installation
                            errorFound, error_code, system_output = check_java_installation(software_name)
                            if platform == 'win32':
                                java_download = 'https://www.oracle.com/java/technologies/downloads/#java8-windows'
                            else:
                                java_download = 'https://www.oracle.com/java/technologies/downloads/#java8-mac'
                            # errorFound=True # for testing
                            if errorFound:
                                Java_required=software_name + ' requires the freeware Java (by Oracle) installed on our machine.\n\nTo dowanload Java from the Oracle website, you will need to sign in in your Oracle account (you must create a free Oracle account if you do not have one).\n\nThe NLP Suite will now open the Java website on JDK8... JDK8 seems to work best with Stanford CoreNP on some machines. But on most machines higher Java releases also work.\n\nWhichever Java version you install, you need the JDK version, Java Development Kit.\n\nDownload Java JDK and run the executable.'
                                mb.showwarning(title='Java',
                                                message=Java_required)
                                webbrowser.open_new(java_download)

# DOWNLOAD Microsoft Visual Studio C++ for SENNA

                        if software_name == 'SENNA':
                            # Microsoft Visual Studio C++ must be downloaded for Windows machines;
                            #   on Mac it is built into the OS
                            if platform=='win32':
                                title='Microsoft Visual Studio C++'
                                message='SENNA (and Python WordCloud) require the freeware Visual Studio C++ (Community edition) installed on our Windows machine. If you haven\'t already installed it, please do so now.\n\nThe downloaded file is an executable file that opens an installer.\n\nDo you want to install Visual Studio C++?'
                                answer = tk.messagebox.askyesnocancel(title, message)
                                if answer:
                                    download_studio='https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019'

                                    webbrowser.open_new(download_studio)

# INSTALLING
                    if software_dir == '' and package.lower() in software_name.lower():
                        # get software directory
                        software_dir = None
                        while software_dir == None:
                            # should not start from NLP/src since users are strongly advised NT to install external softare inside the NLP Suite folder
                            # initialFolder = os.path.dirname(os.path.abspath(__file__))
                            initialFolder = ''
                            if not answer: # answer = True downloading and installing; you have already warned the user
                                title = software_name.upper() + ' software installation'
                                mb.showwarning(title=title,
                                               message=message2)
                            software_dir = tk.filedialog.askdirectory(initialdir=initialFolder,
                                                                      title=title + message3)
                            # GEPHI INSTALLATION
                            if platform == 'darwin':
                                if software_name == 'Gephi':
                                    if not os.path.isdir("/Applications/Gephi.app/Contents/MacOS"):
                                        mb.showwarning(title=title,
                                                       message="GEPHI has not been installed.")
                                        software_dir = ''
                                    else:
                                        software_dir = "/Applications/Gephi.app/Contents/MacOS"
                                # GOOGLE EARTH PRO INSTALLATION
                                if software_name == 'Google Earth Pro':
                                    if not os.path.isdir("/Applications/Google Earth Pro.app/Contents/MacOS"):
                                        mb.showwarning(title=title,
                                                       message="GOOGLE EARTH PRO has not been installed.")
                                        software_dir = ''
                                    else:
                                        software_dir = "/Applications/Google Earth Pro.app/Contents/MacOS"
                            # INSTALLATION
                            if software_dir != '':
                                # check that it is the correct software directory
                                if 'corenlp' in software_name.lower():
                                    software_name = 'Stanford CoreNLP'
                                elif 'mallet' in software_name.lower():
                                    software_name = 'Mallet'
                                elif 'senna' in software_name.lower():
                                    software_name = 'SENNA'
                                elif 'wordnet' in software_name.lower():
                                    software_name = 'WordNet'
                                elif 'gephi' in software_name.lower():
                                    software_name = 'Gephi'
                                elif 'google earth pro' in software_name.lower():
                                    software_name = 'Google Earth Pro'
                                # check that the selected folder for the external program is correct; if so save
                                if not inputExternalProgramFileCheck(software_dir, software_name):
                                    software_dir = ''

                            # update the array existing_csv with the value of software_dir
                            if software_dir != '':
                                existing_csv[index][1] = software_dir
                                save_software_config(existing_csv, software_name)
                            # exit when you are considering a specific software (package)
                            if package.lower()!='':
                                if package.lower() in software_name.lower():
                                    if answer:  # downloading and installing; you have already warned the user
                                        exit_for_loop = True #  break # exit top download for loop as well
                                    # exit loop: while software_dir == None
                                    break
            if software_dir == '':
                software_dir = None
    return software_dir, missing_software
