# Written by Roberto Franzosi November 2019, updated March 2020 

# config_array

# input_output_options[0] Directory of software used: 0 NO SOFTWARE 1 CoreNLP 2 WordNet 3 Mallet
# input_output_options[1] 0 No input file 1 CoNLL file 2 TXT file 3 csv file 4 any single txt, pdf, docx, csv, conll file
# input_output_options[2] 0 NO input dir
# input_output_options[3] 0 NO input secondary dir
# input_output_options[4] 0 NO output file
# input_output_options[5] 0 NO output dir

# every IO widget, files or directories, have a line in the config file
# config lines can be blank, if NOT required by the specific NLP script
# config lines with missing values for a required IO widget will be exported as "EMPTY LINE"  

import sys
import GUI_util
# import IO_libraries_util
#
# if not IO_libraries_util .install_all_packages(GUI_util.window,"config_util",['os','tkinter','ntpath']):
#     sys.exit(0)

import os

import ntpath  # to split the path from filename
import tkinter as tk
import tkinter.messagebox as mb

import IO_user_interface_util
import GUI_IO_util

defaultConfigFilename = 'default-config.txt'
emptyConfigString = "EMPTY LINEEMPTY LINEEMPTY LINEEMPTY LINE"


# used in GIS_GUI and GIS_geocode_GUI

# Google_config: 'Google-geocode_API-config.txt' or 'Google-Maps_API-config.txt'
def Google_API_Config_Save(Google_config,Google_API_key):
    # save the API key is not blank and not already there
    if Google_API_key != '':
        GoogleConfigFilename = os.path.join(GUI_IO_util.configPath, Google_config)
        # if not os.path.isfile(GoogleConfigFilename):
        with open(GoogleConfigFilename, "w+", newline='', encoding='utf-8', errors='ignore') as file1:
            file1.write(Google_API_key)
            if 'Maps' in Google_config:
                msg='Maps'
            else:
                msg = 'geocoder'
            mb.showwarning(title='Warning',
                           message='The Google API key\n\n' + Google_API_key + '\n\nhas been saved to ' + GoogleConfigFilename + '."\n\nIt will read in automatically every time you select the Google ' + msg)
        file1.close()

# fileName with path
def checkConfigFileExists(configFile, fileName, IO):
    error=False
    # check that the config file exists first
    if not os.path.isfile(os.path.join(GUI_IO_util.configPath,configFile)):
        error = True
        mb.showwarning(title='File error',
                       message='The "' + configFile + '" config file does not exist. It must have been never created, deleted, or moved.\n\nYou must re-create the file by selecting the appropriate I/O options, save them, and try again!')
        fileName = ''
    else:
        if fileName != '' and fileName != 'EMPTY LINE':
            if not os.path.isfile(fileName):
                # must pass the right config filename in case there is only the default config
                if (not os.path.isfile(configFile) and
                        os.path.isfile(os.path.join(GUI_IO_util.configPath, defaultConfigFilename))):
                    configFile = defaultConfigFilename
                mb.showwarning(title='File error',
                               message="The " + IO + " file saved in " + configFile + "\n\n" + fileName + "\n\nno longer exists. It must have been deleted or moved.\n\nPlease, select a new " + IO + " file and try again!")
                fileName = ''
    return error, fileName


# fileName with path
def checkConfigDirExists(configFile, dirName, IO):
    # the error variable is used to avoid checking repeatedly, with repeated error messages, when checking the config file
    error=False
    # check that the config file exists first; add path to file
    # configFile = os.path.isfile(os.path.join(GUI_IO_util.configPath,configFile))
    if not os.path.isfile(os.path.join(GUI_IO_util.configPath,configFile)):
        error = True
        mb.showwarning(title='File error',
                       message='The "' + configFile + '" config file does not exist. It must have been never created, deleted, or moved.\n\nYou must re-create the file by selecting the appropriate I/O options, save them, and try again!')

        dirName = ''
    else:
        if dirName != '' and dirName != 'EMPTY LINE':
            if not os.path.isdir(dirName):
                # must pass the right config filename in case there is only the default config
                if (not os.path.isfile(configFile) and
                        os.path.isfile(os.path.join(GUI_IO_util.configPath, defaultConfigFilename))):
                    configFile = defaultConfigFilename
                mb.showwarning(title='Directory error',
                               message="The " + IO + " directory saved in " + configFile + "\n\n" + dirName + "\n\nno longer exists. It must have been deleted or moved.\n\nPlease, select a new " + IO + " directory and try again!")
                dirName = ''
    return error, dirName

# the function either reads available IO_options saved in the config file or
#   takes the numeric list of I/O values (e.g. [0,1,0,0,1,0]) and converts it to a string list of items 'EMPTY LINE'
def get_IO_options(config_filename,config_input_output_options):
    if config_input_output_options!=[0,0,0,0,0,0]:
        # use default config at first
        IO_options=readConfig(config_filename,config_input_output_options)
    else:
        IO_options=None

    # the following check and lines are necessary
    #   to avoid code break in
    #   if IO_options[] in later tests
    #   when there is no config folder
    if IO_options==None or IO_options==[]:
        IO_options=[]
        for i in range(len(config_input_output_options)):
            lineValue = "EMPTY LINE"
            IO_options.append(lineValue)
    return IO_options


# configFile includes path
# changes made here must reflect changes in GUI_util.preload_configData_set_input_output_options(window,configFile)
##configPath is defined in IO_util

# every IO widget, files or directories, have a line in the config file
# config lines can be blank, if NOT required by the specific NLP script
# config lines with missing values for a required IO widget will be exported as "EMPTY LINE"  

# called by GUI_util as first step
# GUI_util calls setup_IO_configArray as second step
#   config_array is config_input_output_options
#   for examples, for NLP.py config_array=[0,4,1,0,0,1]
# returns a list input_output_options
def readConfig(configFile, config_array):
    # configFile_basename is the filename w/o the full path
    input_output_options = []
    error = False
    configFile_basename = ntpath.basename(configFile)
    configFilePath = os.path.join(GUI_IO_util.configPath, configFile)
    configFile = ''
    # when BOTH the default-config.txt file and
    #   specific GUI config file are present
    #   the specific GUI config file will take precedence
    # otherwise the default-config.txt will always be used for all tools

    # must pass the right config filename in case there is only the default config
    if os.path.isfile(configFilePath):
        configFile = configFilePath
    # else:
    #     if os.path.isfile(os.path.join(GUI_IO_util.configPath, defaultConfigFilename)):
    #         configFile = os.path.join(GUI_IO_util.configPath, defaultConfigFilename)
    if configFile != '':
        f_config = open(configFile, 'r', encoding='utf-8', errors='ignore')
        configList = f_config.readlines()
        configList = [i.strip() for i in configList]
        length = len(configList)
        if length < len(config_array):
            # Not necessary to display the error
            # mb.showwarning(title='File error', message="The Input/Output config file\n\n" + configFile + "\n\ncontains only " + str(length) + " lines. IT IS AN OLD CONFIG FILE.\n\nThe new release of the NLP suite requires 6 lines. You will need to re-select your Input/Output options and save them when you press QUIT.")
            error = True
        for i in range(len(config_array)):
            if error:
                input_output_options.append('')
            else:
                input_output_options.append(configList[i])
    # else:
    #     mb.showwarning(title='File error', message="There is no Input/Output configuration file\n\n" + configFile + "\n\nPlease, click on the Setup INPUT/OUTPUT button to set it up.")
    return input_output_options

# the function is sed to obtain the list of six numeric values of IO options for a specific config file (e.g., [0, 1, 0, 1, 0, 1])

# the function does NOT check for the various options in software dir and input file type
# input_output_options[0] Directory of software used: 0 NO SOFTWARE 1 CoreNLP 2 WordNet 3 Mallet
# input_output_options[1] 0 No input file 1 CoNLL file 2 TXT file 3 csv file 4 any single txt, pdf, docx, csv, conll file
# input_output_options[2] 0 NO input dir
# input_output_options[3] 0 NO input secondary dir
# input_output_options[4] 0 NO output file
# input_output_options[5] 0 NO output dir
def get_config_array_from_configFile(configFile):
    # configFile_basename is the filename w/o the full path
    config_array = []
    error = False
    configFile_basename = ntpath.basename(configFile)
    configFilePath = os.path.join(GUI_IO_util.configPath, configFile)
    configFile = ''
    if os.path.isfile(configFilePath):
        configFile = configFilePath
    else:
        if os.path.isfile(os.path.join(GUI_IO_util.configPath, defaultConfigFilename)):
            configFile = os.path.join(GUI_IO_util.configPath, defaultConfigFilename)
    if configFile != '':
        f_config = open(configFile, 'r', encoding='utf-8', errors='ignore')
        configList = f_config.readlines()
        configList = [i.strip() for i in configList]
        length = len(configList)
        for i in range(len(configList)):
            if (i == 1):
                if (configList[i] != ""):
                    config_array.append(1)
                else: # check Dir option
                    config_array.append(0)
            elif (i == 2):
                if (configList[i] != ""):
                    config_array.append(1)
                else: # check Dir option
                    config_array.append(0)
            else:
                if configList[i]!="EMPTY LINE" and configList[i]!="":
                    config_array.append(1)
                else:
                    config_array.append(0)
    return config_array


def writeConfigFile(configFilename, configArray):
    # when writing a csv file newline='' prevents writing an extra blank line after every record
    try:
        with open(os.path.join(GUI_IO_util.configPath, configFilename), "w+", newline='', encoding='utf-8',
                  errors='ignore') as f:
            for i in range(0, len(configArray)):
                # all empty items are set to EMPTY LINE
                if configArray[i]=='':
                    configArray[i]='EMPTY LINE'
                f.write(configArray[i])
                f.write('\n')
        f.close()
    except:
        mb.showwarning(title='Permission error?',
                       message="The command failed to save the config file\n\n" + configFilename + "\n\nIf you look at your command line and you see a \'Permission error\', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on \'Properties\'. Make sure that the \'Attributes\' setting, the last one on the display window, is NOT set to \'Read only\'. If so, click on the checkbox until the Read only is cleared, click on \'Apply\' and then \'OK\', exit the NLP Suite and try again.")
        return False
    return True


# returns True if the IO values are all blank
#   or are the same as the saved ones in either
#   GUI config or default config
# When True, i.e., saved config and current config are the same, there will be need to ask the question to save
def checkSavedConfig(configFilename, configArray):
    currentStringArray = ''
    savedStringArray = ''
    IO_setup_display_string=''
    for i in range(0, len(configArray)):
        if configArray[i]=='':
            configArray[i] = 'EMPTY LINE'
        currentStringArray = currentStringArray + configArray[i]
    # get config saved values; savedConfigArray is a list []
    savedConfigArray = readConfig(configFilename, configArray)
    for i in range(0, len(savedConfigArray)):
        if savedConfigArray[i]=='':
            savedConfigArray[i] = 'EMPTY LINE'
        savedStringArray = savedStringArray + savedConfigArray[i]
        # compute the IO_setup_display_string for display brief
        # head is path, tail is filename
        if i == 1:
            if savedConfigArray[i]!='' and savedConfigArray[i]!='EMPTY LINE':
                head, tail = os.path.split(savedConfigArray[i])
                IO_setup_display_string = "INPUT FILE: " + str(tail)
        if i == 2:
            if savedConfigArray[i]!='' and savedConfigArray[i]!='EMPTY LINE':
                head, tail = os.path.split(savedConfigArray[i])
                IO_setup_display_string = "INPUT DIR: " + str(tail)
        if i == 5:
            if savedConfigArray[i] != '' and savedConfigArray[i] != 'EMPTY LINE':
                head, tail = os.path.split(savedConfigArray[i])
                IO_setup_display_string = IO_setup_display_string+"\nOUTPUT DIR: " + str(tail)
    if (currentStringArray != emptyConfigString and currentStringArray != savedStringArray):
        return False, IO_setup_display_string
    else:
        return True, IO_setup_display_string

# Takes in the name of the config file (including .txt extension), the number of paths to save (nSaves)
# and an array that should contain all the input-output files & dir
# called from GUI_IO_util.exit_window 
# configFilename with no path;
# configArray contains all the IO files and paths
#   configArray is computed by setup_IO_configArray in config_util 
# configPath is defined in IO_util

# every IO widget, files or directories, have a line in the config file
# config lines can be blank, if NOT required by the specific NLP script
# config lines with missing values for a required IO widget will be exported as "EMPTY LINE"  

# EMPTY LINE refer to the following IO widgets
# input_output_options[0] Directory of software used: 0 NO SOFTWARE 1 CoreNLP 2 WordNet 3 Mallet
# input_output_options[1] 0 No input file 1 CoNLL file 2 TXT file 3 csv file 4 any single txt, pdf, docx, csv, conll file
# input_output_options[2] 0 NO input dir
# input_output_options[3] 0 NO input secondary dir
# input_output_options[4] 0 NO output file
# input_output_options[5] 0 NO output dir
# MUTUALLY EXCLUSIVE OPTIONS (i.e., IInput file and input dir) ARE SAVED WITH A BLANK VALUE WHEN NOT PRESENT
def saveConfig(window, configFilename, configArray, silent=False):
    # for GUIs with no I/O widgets configArray 
    #   is empty lines
    if (configArray[0] == 'EMPTY LINE' or configArray[0] == '') and \
        (configArray[1] == 'EMPTY LINE' or configArray[1] == '') and \
        (configArray[2] == 'EMPTY LINE' or configArray[2] == '') and \
        (configArray[3] == 'EMPTY LINE' or configArray[3] == '') and \
        (configArray[4] == 'EMPTY LINE' or configArray[4] == '') and \
        (configArray[5] == 'EMPTY LINE' or configArray[5] == ''):
        return
    currentStringArray = ''
    configFileWritten = False
    if os.path.isdir(GUI_IO_util.configPath) == False:
        try:
            os.mkdir(GUI_IO_util.configPath)
        except:
            mb.showwarning(title='Permission error?',
                           message="The command failed to create the Config directory.\n\nIf you look at your command line and you see a \'Permission error\', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on \'Properties\'. Make sure that the \'Attributes\' setting, the last one on the display window, is NOT set to \'Read only\'. If so, click on the checkbox until the Read only is cleared, click on \'Apply\' and then \'OK\', exit the NLP Suite and try again.")
            return

    for i in range(0, len(configArray)):
        currentStringArray = currentStringArray + configArray[i]
    if currentStringArray == emptyConfigString:
        return
    # There IS GUI config or default config
    #   and current IO values = saved IO values 
    #   exit without asking save question    
    if os.path.isfile(os.path.join(GUI_IO_util.configPath, configFilename)) == True:
        # check config file content against current values; if the same, i.e., True, exit with no question
        sameValues, IO_setup_display_string=checkSavedConfig(configFilename, configArray)
        if sameValues==True:
            return
        else:
            if silent == True:
                saveGUIconfig = True
            else:
                if 'default' in configFilename:
                    saveGUIconfig = mb.askyesno("Save I/O values to 'Default I/O configuration': " + configFilename,
                                                'The selected Input/Output options are different from the I/O values previously saved in "' + configFilename + '"' + ' listed below in succinct form for readability:\n\n' + IO_setup_display_string + '\n\nDo you want to replace the previously saved I/O values with the current ones?')
                else:
                    saveGUIconfig = mb.askyesno("Save I/O values to 'Alternative I/O configuration': " + configFilename,
                                                'The selected Input/Output options are different from the I/O values previously saved in "' + configFilename + '"' + ' listed below in succinct form for readability:\n\n' + IO_setup_display_string + '\n\nDo you want to replace the previously saved I/O values with the current ones?')
            if saveGUIconfig == True:
                configFileWritten = writeConfigFile(configFilename, configArray)
    else:  # no GUI config available
            configFileWritten = writeConfigFile(configFilename, configArray)

    if configFilename != 'license-config.txt':
        if configFileWritten:
            IO_user_interface_util.timed_alert(window, 3000, 'Warning',
                                               'INPUT and OUTPUT paths configuration have been saved to\n\n' + configFilename,
                                               False)

# in some circumstances, some buttons are disabled in the GUI
#   (e.g., in WordNet the input csv file is disabled)
#   In these case, you do not want to disable the RUN button
def add2Missing(missingIO, configName, button_state):
    if button_state == 'disabled':
        return missingIO
    if len(missingIO) > 0:
        missingIO = missingIO + ", " + configName
    else:
        missingIO = configName
    return missingIO


# called by GUI_util
# every IO widget, files or directories, have a line in the config file
# config lines can be blank, if NOT required by the specific NLP script
# config lines with missing values for a required IO widget will be exported as "EMPTY LINE"
# config_input_output_options is the list of IO values set in the main scrip of a script with GUI 
#   for examples, for NLP.py config_array=[0, 4, 1, 0, 0, 1]
#   where config_array is config_input_output_options

# called by GUI_util as second step
# GUI_util calls readConfig as first step
# configArray contains all the IO files and paths
#   configArray is computed by setup_IO_configArray in config_util
def setup_IO_configArray(window, config_input_output_options, select_softwareDir_button, softwareDir,
                         select_file_button, inputFilename, select_input_main_dir_button, input_main_dir_path,
                         select_input_secondary_dir_button, input_secondary_dir_path, select_output_file_button,
                         outputFilename, select_output_dir_button, output_dir_path):
    button_state = []
    configArray = []
    configNames = []
    missingIO = ""

    button_state.append(select_softwareDir_button['state'])
    button_state.append(select_file_button['state'])
    button_state.append(select_input_main_dir_button['state'])
    button_state.append(select_input_secondary_dir_button['state'])
    button_state.append(select_output_file_button['state'])
    button_state.append(select_output_dir_button['state'])

    configArray.append(softwareDir.get())
    configArray.append(inputFilename.get())
    configArray.append(input_main_dir_path.get())
    configArray.append(input_secondary_dir_path.get())
    configArray.append(outputFilename.get())
    configArray.append(output_dir_path.get())

    configNames.append("Software directory")
    configNames.append("Input file")
    configNames.append("Input files directory")
    configNames.append("Input files secondary directory")
    configNames.append("Output file")
    configNames.append("Output files directory")

    for i in range(0, len(config_input_output_options)):
        if config_input_output_options[i] > 0:
            # we no longer disable the IO buttons when mutually exclusive (input file vs dir)
            # users did not know what to do although it is in the help
            # if button_state[i]=='normal':
            # some IO buttons, however, are still disabled when NOT needed
            #   (e.g., in WordNet)
            if configArray[i] == '':
                if configNames[i] == "Input file" or configNames[i] == "Input files directory":
                    # for Input you can only have either a single file or dir
                    if configNames[i] == "Input file":
                        # dir input option is available 
                        if config_input_output_options[i + 1] > 0:
                            if configArray[i + 1] == '':
                                # add both file and dir to missingIO
                                missingIO = add2Missing(missingIO, configNames[i], button_state[i])
                                missingIO = add2Missing(missingIO, configNames[i + 1], button_state[i])
                        else:
                            # add file to missingIO when no dir option is available
                            # if button_state[i]=='normal':
                            missingIO = add2Missing(missingIO, configNames[i], button_state[i])
                    elif configNames[i] == "Input files directory":
                        # add dir to missingIO when no file option is available
                        if config_input_output_options[i - 1] == 0:
                            # if button_state[i]=='normal':
                            missingIO = add2Missing(missingIO, configNames[i], button_state[i])
                else:
                    # if button_state[i] == 'normal':
                    missingIO = add2Missing(missingIO, configNames[i], button_state[i])
        else:
            # when the IO widget option is not available
            #   (e.g., software dir when no software is required)
            configArray[i] = 'EMPTY LINE'
    return configArray, missingIO
