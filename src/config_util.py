# Written by Roberto Franzosi November 2019, updated December 2021

# input_output_options[0] 0 No input file 1 CoNLL file 2 TXT file 3 csv file 4 any single txt, pdf, docx, csv, conll file
# input_output_options[1] 0 NO input dir
# input_output_options[2] 0 NO input secondary dir
# input_output_options[3] 0 NO output dir

# every IO widget, files or directories, has a line in the config file
# config lines can be blank if NOT required by the specific NLP script

# import sys
# import GUI_util
# import IO_libraries_util
#
# if not IO_libraries_util .install_all_packages(GUI_util.window,"config_util",['os','tkinter']):
#     sys.exit(0)

import os
import tkinter.messagebox as mb

import IO_user_interface_util
import GUI_IO_util
import csv

defaultConfigFilename = 'default_config.csv'

# fileName with path, the value saved in config_filename
def checkConfigFileExists(config_filename, fileName, IO):
    error=False
    # check that the config file exists first, after adding path to file
    if not os.path.isfile(os.path.join(GUI_IO_util.configPath,config_filename)):
        error = True
        mb.showwarning(title='File error',
                       message='The "' + config_filename + '" config file does not exist. It must have been never created, deleted, or moved.\n\nYou must re-create the file by selecting the appropriate I/O options, save them, and try again!')
        fileName = ''
    else:
        if fileName != '':
            if not os.path.isfile(fileName):
                # must pass the right config filename in case there is only the default config
                if (not os.path.isfile(config_filename) and
                        os.path.isfile(os.path.join(GUI_IO_util.configPath, defaultConfigFilename))):
                    config_filename = defaultConfigFilename
                mb.showwarning(title='File error',
                               message="The " + IO + " file saved in " + config_filename + "\n\n" + fileName + "\n\nno longer exists. It must have been deleted or moved.\n\nPlease, select a new " + IO + " file and try again!")
                fileName = ''
    return error, fileName

# dirName, the value saved in config_filename
def checkConfigDirExists(config_filename, dirName, IO):
    # the error variable is used to avoid checking repeatedly, with repeated error messages, when checking the config file
    error=False
    # check that the config file exists first, after adding path to file
    if not os.path.isfile(os.path.join(GUI_IO_util.configPath,config_filename)):
        error = True
        mb.showwarning(title='File error',
                       message='The "' + config_filename + '" config file does not exist. It must have been never created, deleted, or moved.\n\nYou must re-create the file by selecting the appropriate I/O options, save them, and try again!')

        dirName = ''
    else:
        if dirName != '':
            if not os.path.isdir(dirName):
                # must pass the right config filename in case there is only the default config
                if (not os.path.isfile(config_filename) and
                        os.path.isfile(os.path.join(GUI_IO_util.configPath, defaultConfigFilename))):
                    config_filename = defaultConfigFilename
                mb.showwarning(title='Directory error',
                               message="The " + IO + " directory saved in " + config_filename + "\n\n" + dirName + "\n\nno longer exists. It must have been deleted or moved.\n\nPlease, select a new " + IO + " directory and try again!")
                dirName = ''
    return error, dirName


def getFiletype(config_input_output_numeric_options):
    if config_input_output_numeric_options[0]==1:
        fileType='Input csv CoNLL filename with path'
    elif config_input_output_numeric_options[0] == 2:
        fileType = 'Input txt filename with path'
    elif config_input_output_numeric_options[0] == 3:
        fileType = 'Input csv filename with path'
    elif config_input_output_numeric_options[0] == 4:
        fileType = 'Input txt/pdf/docx/csv filename with path'
    else:
        fileType = 'Input filename with path'
    return fileType

def get_standard_config_csv(config_input_output_numeric_options, config_input_output_alphabetic_options):

    header=['I/O configuration label', 'Path']
    fileType=getFiletype(config_input_output_numeric_options)
    standard_config_csv = \
                  [[fileType],
                  ['Input files directory'],
                  ['Input files secondary directory'],
                  ['Output files directory']]

    for (index, row) in enumerate(standard_config_csv):
        if len(config_input_output_alphabetic_options) > 0:
            standard_config_csv[index].append(config_input_output_alphabetic_options[index])
        else:
            standard_config_csv[index].append('')
    standard_config_csv.insert(0,header)
    return standard_config_csv

# called by get_missing_IO_values and readConfig below
# returns a double list of csv IO labels and values saved in a csv config file
def read_config_file(config_filename, config_input_output_numeric_options):
    config_input_output_alphabetic_options = []
    config_input_output_full_options = ''
    configFilePath = os.path.join(GUI_IO_util.configPath, config_filename)
    # check that the config file exists
    if os.path.isfile(configFilePath) == True:
        csv_file = open(configFilePath, 'r', newline='')
        config_option_csv = list(csv.reader(csv_file, delimiter=','))
    else:
        config_option_csv = list()
        config_option_csv=get_standard_config_csv(config_input_output_numeric_options,config_option_csv)
    missingIO=get_missing_IO_values(config_input_output_numeric_options, config_option_csv)
    index = 1
    for row in config_option_csv[1:]:  # skip header line
        if row[1]!='':
            if config_input_output_full_options=='':
                config_input_output_full_options=str(row[0]) + ': ' + str(row[1])
            else:
                config_input_output_full_options = config_input_output_full_options + '\n\n' + str(row[0]) + ': ' + str(row[1]) + '\n'
        config_input_output_alphabetic_options.append(row[1])
        index = index + 1
    return config_input_output_alphabetic_options, config_input_output_full_options, missingIO

# called by read_config_file above
def get_missing_IO_values(config_input_output_numeric_options, config_option_csv):
    index = 1 # skip header line
    # the index for config_input_output_numeric_options starts at index -1 since it has no header
    missing_IO=''
    while index < len(config_option_csv):
        if index == 1: # filename;
            if config_input_output_numeric_options[index-1]>0 and config_option_csv[index][1] == '':
                if config_option_csv[2][1] == '': # check input dir
                    config_label = str(config_option_csv[index][0])
                    missing_IO = missing_IO + config_label + '\n'
        elif index == 2:  # Input files dir
            if config_input_output_numeric_options[index-1] > 0 and config_option_csv[index][1] == '':
                if config_option_csv[1][1] == '': # check input filename
                    config_label = str(config_option_csv[index][0])
                    missing_IO = missing_IO + config_label + '\n'
        elif index == 3: # Input files secondary dir
            if config_input_output_numeric_options[index-1] > 0 and config_option_csv[index][1] == '':
                config_label = str(config_option_csv[index][0])
                missing_IO = missing_IO + config_label + '\n'
        elif index == 4: # outputDir
            if config_input_output_numeric_options[index-1] > 0 and config_option_csv[index][1] == '':
                config_label = str(config_option_csv[index][0])
                missing_IO = missing_IO + config_label + '\n'
        index = index + 1
    return missing_IO

# check_missingIO is called from GUI_util
# the function checks for missing IO values, displays messages and sets the RUN button to normal or disabled
def check_missingIO(window,missingIO,config_filename, scriptName, IO_setup_display_brief, silent=False):
    if 'NLP_menu_main' in scriptName:
        silent = True
    if config_filename=='NLP_config.csv':
        config_filename = 'default_config.csv'
    # the IO_button_name error message changes depending upon the call
    button = "button"
    # there is no RUN button when setting up IO information so the call to check_missingIO should be silent
    run_button_disabled_msg = "The RUN button is disabled until the required information for the selected Input/Output fields is entered.\n\n"
    if "IO_setup_main" in scriptName:
        run_button_disabled_msg = ""
        enter_required_IO='Press OK to enter the required I/O information using the \'Select INPUT and Select OUTPUT\' buttons at the top of the GUI.\nPress CANCEL to exit without entering I/O information then press CLOSE.'
    else:
        if not IO_setup_display_brief:
            enter_required_IO='' #'Press OK to enter the required I/O information using the \'Select INPUT and Select OUTPUT\' buttons at the top of the GUI.\nPress CANCEL to exit without entering I/O information.'
        else:
            enter_required_IO='Press OK to enter the required I/O information when the I/O setup GUI opens next.\nPress CANCEL to exit without entering I/O information.'
    if IO_setup_display_brief==True:
        IO_button_name = "Setup INPUT/OUTPUT configuration" # when displaying brief
    if IO_setup_display_brief==False:
        if 'NLP_menu_main' in scriptName:
            IO_button_name = "Setup default I/O options"  # when displaying from NLP_menu_main
        else:
            IO_button_name = "Select INPUT & Select OUTPUT" # when displaying full
            button="buttons"
    Run_Button_Off=False
    #do not check IO requirements for NLP.py; too many IO options available depending upon the script run
    # if config_filename=="NLP_config.csv" or config_filename=="social-science-research_config.csv":
    if config_filename == "social_science_research_config.csv":
        # RUN button always active since several options are available and IO gets checked in the respective scripts
        Run_Button_Off=False
        missingIO=''
    mutually_exclusive_msg=''
    if "Input filename with path" in missingIO and "Input files directory" in missingIO:
        mutually_exclusive_msg='The two I/O options - "Input filename with path" and "Input files directory" - are MUTUALLY EXCLUSIVE. YOU CAN ONLY HAVE ONE OR THE OTHER BUT NOT BOTH. In other words, you can choose to work with a sigle file in input or with many files stored in a directory.\n\n'
    answer=True # = cancel in mb.askokcancel
    if missingIO!='':
        Run_Button_Off = True
        if not silent:
            if (not IO_setup_display_brief) and (not "IO_setup_main" in scriptName):
                mb.showwarning(title='Warning', message='The following required INPUT/OUTPUT information is missing in config file ' + config_filename + ':\n\n' + missingIO + '\n' + mutually_exclusive_msg + run_button_disabled_msg + enter_required_IO)
                answer=False
            else:
                answer=mb.askokcancel(title='Warning', message='The following required INPUT/OUTPUT information is missing in config file ' + config_filename + ':\n\n' + missingIO + '\n' + mutually_exclusive_msg + run_button_disabled_msg + enter_required_IO)
    if Run_Button_Off==True:
        run_button_state="disabled"
    else:
        run_button_state="normal"
    window.focus_force()
    return run_button_state, answer

# every IO widget, files or directories, have a line in the config file
# config lines are blank, if NOT required by the specific NLP script

# input_output_options[0] 0 No input file 1 CoNLL file 2 TXT file 3 csv file 4 any single txt, pdf, docx, csv, conll file
# input_output_options[1] 0 NO input dir
# input_output_options[2] 0 NO input secondary dir
# input_output_options[3] 0 NO output dir
def write_config_file(window, config_filename, config_input_output_numeric_options, config_input_output_alphabetic_options, silent=False):
    print('IN def write_config_file')
    # check that the config directory exists inside the NLP main directory
    if os.path.isdir(GUI_IO_util.configPath) == False:
        try:
            os.mkdir(GUI_IO_util.configPath)
        except:
            mb.showwarning(title='Permission error?',
                           message="The command failed to create the Config directory.\n\nIf you look at your command line and you see a \'Permission error\', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on \'Properties\'. Make sure that the \'Attributes\' setting, the last one on the display window, is NOT set to \'Read only\'. If so, click on the checkbox until the Read only is cleared, click on \'Apply\' and then \'OK\', exit the NLP Suite and try again.")
            return

    config_filename_path=os.path.join(GUI_IO_util.configPath, config_filename)
    temp = get_standard_config_csv(config_input_output_numeric_options,config_input_output_alphabetic_options)
    try:
        with open(config_filename_path, 'w+', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(temp)
        csv_file.close()
    except:
        mb.showwarning(title='Permission error?',
                       message="The command failed to save the config file\n\n" + config_filename + "\n\nIf you look at your command line and you see a \'Permission error\', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on \'Properties\'. Make sure that the \'Attributes\' setting, the last one on the display window, is NOT set to \'Read only\'. If so, click on the checkbox until the Read only is cleared, click on \'Apply\' and then \'OK\', exit the NLP Suite and try again.")

    if config_filename != 'license_config.csv':
        IO_user_interface_util.timed_alert(window, 3000, 'Warning',
                                           'INPUT and OUTPUT paths configuration have been saved to\n\n' + config_filename_path,
                                           False)

# used in GIS_GUI and GIS_geocode_GUI
# Google_config: 'Google-geocode_API_config.csv' or 'Google-Maps_API_config.csv'
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
