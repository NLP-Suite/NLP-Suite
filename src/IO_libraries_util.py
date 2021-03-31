import csv
import sys
import os
import tkinter as tk
import tkinter.messagebox as mb
import subprocess
from typing import List

import IO_user_interface_util
import IO_files_util
import GUI_IO_util


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
                           missingModules) + "\n\nPlease, in command prompt/terminal, and in the NLP ENVIRONMENT, use the command\npip install " + str(
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
    try:
        import nltk.data
        nltk.data.find(resource_path)
    except LookupError:
        IO_user_interface_util.timed_alert(window, 2000, 'Downloading nltk resource',
                                           'Downloading nltk ' + resource + '...\n\nPlease, be patient...', False)
        nltk.download(resource)


def check_java_installation(script):
    errorFound = False
    if sys.platform == 'darwin':  # Mac
        java_output = subprocess.run(['java', '-version'], capture_output=True)
    else:
        java_output = subprocess.run(['java', '-version'], capture_output=True)
    error_code = java_output.returncode  # Should be 0 if java installed
    system_output = java_output.stderr.decode(
        'utf-8')  # This is what you see when you run "java -version" in your command line
    if error_code != 0 and "not recognized" in system_output:
        mb.showwarning(title='Java installation error',
                       message='A test for Java returned a non-zero error code ' + str(
                           error_code) + ' and Java not recognized (You can check this in command line). Java is not installed.\n\n' + script + ' is a Java script that requires Java installed on your machine (you need the JDK version, Java Development Kit).\n\nPlease, read the Java installation TIPS, install Java and try again. Program will exit.')
        errorFound = True
    elif error_code != 0:
        mb.showwarning(title='Java error',
                       message='A test for Java returned a non-zero error code ' + str(
                           error_code) + ' with the following system error: ' + system_output + '.\n\nJava may not be properly installed.\n\n' + script + ' is a Java script that requires Java installed on your machine (you need the JDK version, Java Development Kit).\n\nPlease, read the Java installation TIPS, check your Java installation, install Java properly and try again. Program will exit.')
        errorFound = True

    return errorFound, error_code, system_output


def inputProgramFileCheck(programName, subdirectory='src'):
    # filePath=NLPPath+os.sep+subdirectory+os.sep+programName
    if not os.path.isfile(GUI_IO_util.NLPPath + os.sep + subdirectory + os.sep + programName):
        mb.showerror("Input file error",
                     "The required file " + programName + " was not found. The file is expected to be in the subdirectory " + subdirectory + " of the main NLP directory.\n\nPlease, make sure to copy " + programName + " to the " + subdirectory + " subdirectory and try again.")
        return False
    return True


def inputExternalProgramFileCheck(software_dir, programName):
    fileList = []
    for file in os.listdir(software_dir):
        # if file.endswith(".txt"):
        # print(os.path.join(software_dir, file))
        fileList.append(file)
    if programName == 'Stanford CoreNLP':
        for item in fileList:
            if 'stanford-corenlp' in str(item):
                return True
        mb.showwarning(title='Software error',
                       message="The selected software directory\n  " + software_dir + "'\nis NOT the expected CoreNLP directory. The directory should contain, among other things, many files with \'stanford-corenlp\' in the filename. DO MAKE SURE THAT WHEN YOU UNZIP THE STANFORD CORENLP ARCHIVE YOU DO NOT END UP WITH A STANFORD CORENLP DIRECTORY INSIDE A STANFORD CORENLP DIRECTORY.\n\nPlease, select the appropriate CoreNLP directory and try again!\n\nYou can download Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\nPlease, read the TIPS_NLP_Stanford CoreNLP download install run.pdf and the NLP_TIPS_Java JDK download install run.pdf.")
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
                           message="The selected software directory\n  " + software_dir + "'\nis NOT the expected Mallet directory. The directory should contain, among other things, the directories \'bin\' and \'class\'. DO MAKE SURE THAT WHEN YOU UNZIP THE MALLET ARCHIVE YOU DO NOT END UP WITH A MALLET DIRECTORY INSIDE A MALLET DIRECTORY.\n\nPlease, select the appropriate Mallet directory and try again!\n\nYou can download Mallet at http://mallet.cs.umass.edu/download.php.\n\nPlease, read the TIPS_NLP_Topic modeling Mallet installation.pdf and the NLP_TIPS_Java JDK download install run.pdf.")
            return False
    if programName == 'SENNA':
        if 'senna-osx' in fileList and 'senna-win32.exe' in fileList:
            return True
        else:
            mb.showwarning(title='Software error',
                           message="The selected software directory\n  " + software_dir + "'\nis NOT the expected SENNA directory. The directory should contain, among other things, the files \'senna-osx\' and \'senna-win32.exe\'. DO MAKE SURE THAT WHEN YOU UNZIP THE SENNA ARCHIVE YOU DO NOT END UP WITH A SENNA DIRECTORY INSIDE A SENNA DIRECTORY.\n\nPlease, select the appropriate SENNA directory and try again!\n\nYou can download SENNA at https://ronan.collobert.com/senna/download.html.")
            return False
    if programName == 'WordNet':
        if 'dict' in fileList and 'src' in fileList:
            return True
        else:
            mb.showwarning(title='Software error',
                           message="The selected software directory\n  " + software_dir + "'\nis NOT the expected WordNet directory. The directory should contain, among other things, the directories \'dict\' and \'src\'. DO MAKE SURE THAT WHEN YOU UNZIP THE WORDNET ARCHIVE YOU DO NOT END UP WITH A WORDNET DIRECTORY INSIDE A WORDENET DIRECTORY.\n\nPlease, select the appropriate WordNet directory and try again!\n\nYou can download WordNet at https://wordnet.princeton.edu/download/current-version.\n\nPlease, read the TIPS_NLP_WordNet.pdf.")
            return False


def update_csv_fields(existing_csv: list) -> list:
    """

    @param existing_csv: current csv file in list format, similar to sample_csv below
    @return: the new csv files, with software fields up to date.
    """
    sample_csv = [['Software', 'Path', 'Download_link'],
                  ['Stanford CoreNLP', '', 'https://nlp.stanford.edu/software/stanford-corenlp-latest.zip'],
                  ['Mallet', '', 'http://mallet.cs.umass.edu/download.php'],
                  ['SENNA', '', 'https://ronan.collobert.com/senna/download.html'],
                  ['WordNet', '', 'https://wordnet.princeton.edu/download/current-version']]
    fields = [x[0] for x in existing_csv]
    for (index, row) in enumerate(sample_csv):
        if row[0] not in fields:
            existing_csv.append(sample_csv[index])
    return existing_csv


def get_existing_software_config(package):
    software_config = GUI_IO_util.configPath + os.sep + 'software_config.csv'
    # FIXED: must insert the new package into software-config.csv when the package is missing in the user csv file
    try:
        csv_file = open(software_config, 'r', newline='')
        existing_csv = list(csv.reader(csv_file, delimiter=','))
    except:
        existing_csv = list()
    update_csv_fields(existing_csv)
    return existing_csv


def save_software_config(new_csv):
    software_config = GUI_IO_util.configPath + os.sep + 'software_config.csv'
    with open(software_config, 'w+', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(new_csv)


def get_external_software_dir(calling_script, package, warning=True):
    # get a list of software in software-config.csv
    existing_csv = get_existing_software_config(package)
    download_software = ''
    missing_software = ''
    software_dir = None
    software_name = ''
    silent = False
    index = 0
    errorFound = False
    # get any existing software_config csv file
    for row in existing_csv[1:]:  # skip header line
        index = index + 1
        software_name = row[0]
        software_dir = row[1]
        download_software = row[2]
        # software_dir == '' the software has not been downloaded and installed yet
        #   it is MISSING
        if software_dir == '':  # check path field
            print("MISSING SOFTWARE", str(software_name).upper() + ' download at ' + str(download_software))
            # missing_software = missing_software + str(software_name).upper() + ' download at ' + str(
            #     download_software + '\n\n')
            errorFound=True
        else:
            # the software directory is stored in config file but...
            #   check that the software directory still exists and the package has not been moved
            if os.path.isdir(software_dir) == False or inputExternalProgramFileCheck(software_dir, software_name) == False:
                mb.showwarning(title='Directory error',
                               message='The directory\n  ' + software_dir + '\nstored in the software config file\n  ' + GUI_IO_util.configPath + os.sep + 'software_config.csv' + '\nno longer exists. It may have been renamed, deleted, or moved.\n\nYou must re-select the ' +
                                       software_name.upper() + ' directory.')
                errorFound=True
                silent = True
            else:
                # if you are checking for a specific package and that is found return the appropriate directory
                if (package.lower()!='') and (package.lower() in software_name.lower()):
                    return software_dir

        if errorFound:
            software_dir = ''
            existing_csv[index][1] = software_dir
            missing_software = missing_software + str(software_name).upper() + ' download at ' + str(
                download_software + '\n\n')
            # if you are checking for a specific package and the directory is NOT found
            #   return None; no point continuing
            if (package.lower()!='') and (package.lower() in software_name.lower()):
                return None
            errorFound = False

    # check for missing software
    if len(missing_software) > 0:
        if calling_script == 'NLP_menu':  # called from NLP_main GUI. We just need to warn the user to download and install options
            title = 'NLP Suite external software'
            message = 'The NLP Suite relies on several external programs.\n\nPlease, download and install the following software or some functionality will be lost for some of the scripts.\n\n' + missing_software + 'If you have already downloaded the software, please, select next the directory where you installed it; ESC or CANCEL to exit, if you haven\'t installed it yet.'
        else:
            title = package.upper() + ' software'
            message = 'WARNING!\n\nThe script ' + calling_script.upper() + ' requires the external software ' + package.upper() + \
                      ' to run.\n\nIf you have not downloaded and installed ' + package + ' yet, you can do that at ' + download_software + '\n\nIf you have already downloaded ' + package + ', please, select next the directory where you installed it; ESC or CANCEL to exit, if you haven\'t installed it yet.'
        if not silent:
            mb.showwarning(title=title, message=message)
        for (index, row) in enumerate(existing_csv[1:]): # skip header row
            software_name = row[0]
            software_dir = row[1]
            # if software_dir == '' and package.lower() in software_name.lower():
            if software_dir == '':
                # get software directory
                title = software_name.upper() + ' software'
                software_dir = None
                while software_dir == None:
                    initialFolder = os.path.dirname(os.path.abspath(__file__))
                    software_dir = tk.filedialog.askdirectory(initialdir=initialFolder,
                                                              title=title + '. Please, select the directory where the software was installed; or press CANCEL or ESC if you have not downloaded the software yet.')
                    # software_name=''
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
                        # check that the selected folder for the external program is correct
                        if not inputExternalProgramFileCheck(software_dir, software_name):
                            software_dir = ''
                    # update the array existing_csv with the value of software_dir
                    existing_csv[index][1] = software_dir
                    # exit when you are considering a specific software (package)
                    # exit loop: while software_dir == None
                    if package.lower()!='':
                        if package.lower() in software_name.lower():
                            break
                # exit loop: for (index, row) in enumerate(existing_csv)
                if package.lower() != '':
                    if package.lower() in software_name.lower():
                        break
        save_software_config(existing_csv)
    if software_dir == '':
        software_dir = None
    return software_dir
