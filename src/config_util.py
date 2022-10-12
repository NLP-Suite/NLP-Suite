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
import pandas as pd

import IO_user_interface_util
import GUI_IO_util
import csv

defaultConfigFilename = 'NLP_default_IO_config.csv'

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


# config_input_output_numeric_options is a list
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

def save_IO_config(window, config_filename, config_input_output_numeric_options, current_config_input_output_alphabetic_options):
    # saved_config_input_output_alphabetic_options, config_input_output_full_options, missingIO = read_config_file(
    #     config_filename, config_input_output_numeric_options)
    # if saved_config_input_output_alphabetic_options != current_config_input_output_alphabetic_options:
    #     # TODO Roby check that only 4 items are checked ['', '', '', '']
    #     # both input filename and dir are empty
    #     if current_config_input_output_alphabetic_options[0] == ['', '', '', ''] or \
    #             current_config_input_output_alphabetic_options[1] == ['', '', '', '']:
    #         print("IN save_IO_config current_config_input_output_alphabetic_options[0] SAVE FALSE",
    #               current_config_input_output_alphabetic_options[0])
    #         print("IN save_IO_config current_config_input_output_alphabetic_options[1] SAVE FALSE",
    #               current_config_input_output_alphabetic_options[1])
    #         saveGUIconfig = False
    #     else:
    #         # TODO Roby check that only 4 items are checked ['', '', '', '']
    #         print("IN save_IO_config saved_config_input_output_alphabetic_options [0] SAVE TRUE",
    #               saved_config_input_output_alphabetic_options[0])
    #         print("IN save_IO_config saved_config_input_output_alphabetic_options [1] SAVE TRUE",
    #               saved_config_input_output_alphabetic_options[1])
    #         if saved_config_input_output_alphabetic_options[0] == ['', '', '', ''] or \
    #                 saved_config_input_output_alphabetic_options[1] == ['', '', '', '']:
    #             saveGUIconfig = True
    #     if 'default' in config_filename:
    #         saveGUIconfig = mb.askyesno("Save I/O values to 'Default I/O configuration': " + config_filename,
    #                                     'The selected Input/Output options are different from the I/O values previously saved in\n\n' + config_filename + '\n\nand listed below in succinct form for readability:\n\n' + str(
    #                                         config_input_output_full_options) + '\n\nDo you want to replace the previously saved I/O values with the current ones?')
    #     else:
    #         saveGUIconfig = mb.askyesno(
    #             "Save I/O values to 'GUI-specific I/O configuration': " + config_filename,
    #             'The selected Input/Output options are different from the I/O values previously saved in\n\n' + config_filename + ' and listed below in succinct form for readability:\n\n' + str(
    #                 config_input_output_full_options) + '\n\nDo you want to replace the previously saved I/O values with the current ones?')
    #     if saveGUIconfig == True:
    write_IO_config_file(window, config_filename, config_input_output_numeric_options,
                                  current_config_input_output_alphabetic_options)
def write_external_software_config_file(window, config_filename, currently_selected_options, currently_selected_parsers):
    # check that the config directory exists inside the NLP main directory
    if os.path.isdir(GUI_IO_util.configPath) is False:
        try:
            os.mkdir(GUI_IO_util.configPath)
        except:
            mb.showwarning(title='Permission error?',
                           message="The command failed to create the Config directory.\n\nIf you look at your command line and you see a \'Permission error\', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on \'Properties\'. Make sure that the \'Attributes\' setting, the last one on the display window, is NOT set to \'Read only\'. If so, click on the checkbox until the Read only is cleared, click on \'Apply\' and then \'OK\', exit the NLP Suite and try again.")
            return

    config_filename_path=os.path.join(GUI_IO_util.configPath, config_filename)
    try:
        # TODO any change in the labels MAIN NLP PACKAGE, LEMMATIZER PACKAGE, and LANGUAGE(S) must be carried out
        #   several times in this scripts (search for instance for MAIN NLP PACKAGE and change
        #   they also need to be changed in one line in NLP_setup_package_language_main.py
        csv_file = pd.DataFrame()
        csv_file.at[0, 'Software'] = currently_selected_options['MAIN NLP PACKAGE']
        csv_file.at[0, 'Path'] = {currently_selected_parsers}
        csv_file.at[0, 'Download_link)'] = currently_selected_options['LEMMATIZER PACKAGE']

        csv_file.to_csv(config_filename_path, encoding='utf-8', index=False)
        csv_file.to_csv(config_filename_path, encoding='utf-8', index=False)

        IO_user_interface_util.timed_alert(window, 2000, 'Warning',
                                           'NLP external software options have been saved to\n\n  ' + config_filename_path,
                                           False)
    except:
        mb.showwarning(title='Permission error?',
                       message="The command failed to save the config file\n\n" + config_filename + "\n\nIf you look at your command line and you see a \'Permission error\', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on \'Properties\'. Make sure that the \'Attributes\' setting, the last one on the display window, is NOT set to \'Read only\'. If so, click on the checkbox until the Read only is cleared, click on \'Apply\' and then \'OK\', exit the NLP Suite and try again.")

def save_external_software_config(window, currently_selected_options, currently_selected_parsers):
    config_filename = GUI_IO_util.configPath + os.sep + 'NLP_setup_external_software_config.csv'
    # package, parsers, package_basics, language = read_NLP_package_language_config()
    error, package, parsers, package_basics, language, package_display_area_value = read_NLP_package_language_config()
    if error or len(parsers)==0:
        saved_NLP_package_language_options = ''
        save_config = True
    else:
        # TODO any change in the labels MAIN NLP PACKAGE, LEMMATIZER PACKAGE, and LANGUAGE(S) must be carried out
        #   several times in this scripts (search for instance for MAIN NLP PACKAGE and change
        #   they also need to be changed in one line in NLP_setup_package_language_main.py
        saved_NLP_package_language_options= {'MAIN NLP PACKAGE': package, 'LEMMATIZER PACKAGE': package_basics, 'LANGUAGE(S)': language}
        save_config=False
    if saved_NLP_package_language_options!='' and currently_selected_options!=saved_NLP_package_language_options:
        save_config = mb.askyesno("Save external software options",
                                  'The selected external software options are different from the values previously saved in\n\n' + config_filename + '\n\nDo you want to replace the previously saved values with the current ones?')
    if save_config:
        write_NLP_package_language_config_file(window, config_filename, currently_selected_options, currently_selected_parsers)

def read_NLP_package_language_config():
    package = ''
    parsers = []
    basics_package = ''
    language = ''
    config_filename = GUI_IO_util.configPath + os.sep + 'NLP_default_package_language_config.csv'
    # dataset = pd.read_csv(config_filename, sep='\t')
    error = False
    try:
        dataset = pd.read_csv(config_filename)
        package = dataset.iat[0, 0]
        parsers = dataset.iat[0, 1].split(',')
        basics_package = dataset.iat[0, 2]
        language = dataset.iat[0, 3]
        # TODO any change in the labels MAIN NLP PACKAGE, LEMMATIZER PACKAGE, and LANGUAGE(S) must be carried out
        #   several times in this scripts (search for instance for MAIN NLP PACKAGE and change
        #   they also need to be changed in one line in NLP_setup_package_language_main.py
        package_display_area_value = f"MAIN NLP PACKAGE: {package}, LEMMATIZER PACKAGE: {basics_package}, LANGUAGE(S): {language}"
    except:
        error = True
        # error must be set to true to display the next message after the entire GUI has been displayed
        # mb.showwarning(title='Warning',
        #                message="The config file 'NLP_default_package_language_config.csv' could not be found in the sub-directory 'config' of your main NLP Suite folder.\n\nPlease, setup the default NLP package and language options using the Setup button.")
        package_display_area_value = ''
    return error, package, parsers, basics_package, language, package_display_area_value

def write_NLP_package_language_config_file(window, config_filename, currently_selected_options, currently_selected_parsers):
    # check that the config directory exists inside the NLP main directory
    if os.path.isdir(GUI_IO_util.configPath) is False:
        try:
            os.mkdir(GUI_IO_util.configPath)
        except:
            mb.showwarning(title='Permission error?',
                           message="The command failed to create the Config directory.\n\nIf you look at your command line and you see a \'Permission error\', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on \'Properties\'. Make sure that the \'Attributes\' setting, the last one on the display window, is NOT set to \'Read only\'. If so, click on the checkbox until the Read only is cleared, click on \'Apply\' and then \'OK\', exit the NLP Suite and try again.")
            return

    config_filename_path=os.path.join(GUI_IO_util.configPath, config_filename)
    try:
        # TODO any change in the labels MAIN NLP PACKAGE, LEMMATIZER PACKAGE, and LANGUAGE(S) must be carried out
        #   several times in this scripts (search for instance for MAIN NLP PACKAGE and change
        #   they also need to be changed in one line in NLP_setup_package_language_main.py
        csv_file = pd.DataFrame()
        csv_file.at[0, 'Parser & annotators'] = currently_selected_options['MAIN NLP PACKAGE']
        csv_file.at[0, 'Parsers'] = {currently_selected_parsers}
        csv_file.at[0, 'Basic functions (tokenizer/lemmatizer)'] = currently_selected_options['LEMMATIZER PACKAGE']
        csv_file.at[0, 'Corpus language'] = currently_selected_options['LANGUAGE(S)']

        csv_file.to_csv(config_filename_path, encoding='utf-8', index=False)

        IO_user_interface_util.timed_alert(window, 2000, 'Warning',
                                           'NLP package and language options have been saved to\n\n  ' + config_filename_path,
                                           False)
    except:
        mb.showwarning(title='Permission error?',
                       message="The command failed to save the config file\n\n" + config_filename + "\n\nIf you look at your command line and you see a \'Permission error\', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on \'Properties\'. Make sure that the \'Attributes\' setting, the last one on the display window, is NOT set to \'Read only\'. If so, click on the checkbox until the Read only is cleared, click on \'Apply\' and then \'OK\', exit the NLP Suite and try again.")


def save_NLP_package_language_config(window, currently_selected_options, currently_selected_parsers, memory, document_length, limit_sentence_length):
    config_filename = GUI_IO_util.configPath + os.sep + 'NLP_default_package_language_config.csv'
    # package, parsers, package_basics, language = read_NLP_package_language_config()
    error, package, parsers, package_basics, language, package_display_area_value = read_NLP_package_language_config()
    if error or len(parsers)==0:
        saved_NLP_package_language_options = ''
        save_config = True
    else:
        # TODO any change in the labels MAIN NLP PACKAGE, LEMMATIZER PACKAGE, and LANGUAGE(S) must be carried out
        #   several times in this scripts (search for instance for MAIN NLP PACKAGE and change
        #   they also need to be changed in one line in NLP_setup_package_language_main.py
        saved_NLP_package_language_options= {'MAIN NLP PACKAGE': package, 'LEMMATIZER PACKAGE': package_basics, "LANGUAGE(S)": language}
        save_config=False
    if saved_NLP_package_language_options!='' and currently_selected_options!=saved_NLP_package_language_options:
        save_config = mb.askyesno("Save NLP package and language options",
                                  'The selected NLP package and language options are different from the values previously saved in\n\n' + config_filename + '\n\nDo you want to replace the previously saved values with the current ones?')
    if save_config:
        write_NLP_package_language_config_file(window, config_filename, currently_selected_options, currently_selected_parsers)

# config_input_output_alphabetic_options is a double list with no headers,
#   with one sublist for each of the four types of IO confiigurations: filename, input main dir, input secondary dir, output dir
# each sublist has four items: path, date format, date separator, date position
# e.g., [['C:/Users/rfranzo/Desktop/NLP-Suite/lib/sampleData/The Three Little Pigs.txt', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['C:\\Program Files (x86)\\NLP_backup\\Output', '', '', '']]
def get_template_config_csv_file(config_input_output_numeric_options, config_input_output_alphabetic_options):
    IO_configuration =[]
    fileType=getFiletype(config_input_output_numeric_options) # different types of input files
    IO_configuration_label = \
                  [fileType,
                  'Input files directory',
                  'Input files secondary directory',
                  'Output files directory']

    # header = ['I/O configuration label', 'Path', 'Date format', 'Date separator character(s)', 'Date position']
    # # loop through the 4 rows of input file, input primary dir, input secondary dir, output dir
    print("config_input_output_alphabetic_options",config_input_output_alphabetic_options)
    # column header is the set of values in IO_configuration_label defined above
    for (index, column_header) in enumerate(IO_configuration_label): # row is the sublist
        print("index",index,"   column_header",column_header)
        date_options = ''
        if len(config_input_output_alphabetic_options[index]) > 0:
            sublist=config_input_output_alphabetic_options[index]
            print("len sublist", len(sublist),'sublist',sublist)
            # date options saved: date format, date characters separator, date position in filename
            # =4 when date options are available, otherwise =1
            if len(sublist)==4:
                IO_configuration.append([column_header, sublist[0], sublist[1], sublist[2], sublist[3]])
            else:
                IO_configuration.append([column_header, sublist[0]])
            # if ", , " in date_options:
            #     IO_configuration.append([IO_configuration_label[index]])
            # else:
            # print("after appending ",IO_configuration[index])
            # print("after appending row ", row)
        else:
            print("index before bombing",index, "date options",date_options,"IO_configuration_label[index]",IO_configuration_label[index])
            # IO_configuration.append([column_header,'','','','']) # path + 3 date items
            IO_configuration.append([IO_configuration_label[index], date_options])  # path + 3 date items
    print("IN get_template_config_csv_file AT THE END IO_configuration_label",IO_configuration)
    return IO_configuration


# called by get_missing_IO_values in GUI_util and readConfig below
# returns a double list of csv IO labels and values saved in a csv config file
# returns config_input_output_alphabetic_options, a list with 5 items
# config_option_csv contains 5 columns for each of four rows of input filename, directory, secondary directory, output directory
#   Oct 2022 added 3 more columns for date options of either fileName or Input Dir: date format, character separator, date position
# config_option_csv = list(csv.reader(csv_file, delimiter=','))

def read_config_file(config_filename, config_input_output_numeric_options):
    print("config_filename, config_input_output_numeric_options",config_filename, config_input_output_numeric_options)
    config_input_output_alphabetic_options = []
    configFilePath = os.path.join(GUI_IO_util.configPath, config_filename)
    # check that the config file exists
    if os.path.isfile(configFilePath) == True:
        csv_file = open(configFilePath, 'r', newline='')
        config_input_output_alphabetic_options = list(csv.reader(csv_file, delimiter=','))
        config_input_output_alphabetic_options.pop(0) # skip header
        print("IN AFTER csv read configFilePath 3",config_input_output_alphabetic_options)
    else:
        config_input_output_alphabetic_options = list()
        config_input_output_alphabetic_options=get_template_config_csv_file(config_input_output_numeric_options,config_input_output_alphabetic_options)
        # remove headers row to uniform output to the pd option above that does not read header
    missingIO=get_missing_IO_values(config_input_output_numeric_options, config_input_output_alphabetic_options)
    print("IN read AT END config_input_output_alphabetic_options",config_input_output_alphabetic_options)
    # return config_input_output_alphabetic_options, config_input_output_full_options, missingIO
    return config_input_output_alphabetic_options, missingIO

# called by read_config_file above
def get_missing_IO_values(config_input_output_numeric_options, config_input_output_alphabetic_options):
    print("in get missing IO config_input_output_alphabetic_options", config_input_output_alphabetic_options)
    missing_IO=''
    # loop through the 4 input/output options: input filename, input man dir, input secondary dir, output dir
    index = 0
    # index ranges 0-3: Input filename, input main dir, input secondary dir, output dir
    while index <= len(config_input_output_alphabetic_options):
        if index == 0: # filename;
            # if the filename is an option (config_input_output_numeric_options[index-1])
            #   and its path value is config_option_csv[index-1][1] is blank check directory
            if config_input_output_numeric_options[index]>0 and config_input_output_alphabetic_options[index][1] == '':
                # in [1][1] the first [1] refers to row number (input dir) the second to column number (the path)
                if config_input_output_alphabetic_options[1][1] == '': # check input dir
                    # add filename as missing if dir not there either; dir will be added in next check
                    config_label = str(config_input_output_alphabetic_options[index][0])
                    missing_IO = missing_IO + config_label + '\n'
        elif index == 1:  # Input files dir
            if config_input_output_numeric_options[index] > 0 and config_input_output_alphabetic_options[1][1] == '':
                # in [0][1] the first [0] refers to row number (input filename) the second to column number (the path)
                if config_input_output_alphabetic_options[0][1] == '': # check input filename
                    config_label = str(config_input_output_alphabetic_options[index][0])
                    missing_IO = missing_IO + config_label + '\n'
        elif index == 2: # Input files secondary dir
            if config_input_output_numeric_options[index] > 0 and config_input_output_alphabetic_options[index][1] == '':
                config_label = str(config_input_output_alphabetic_options[index][0])
                missing_IO = missing_IO + config_label + '\n'
        elif index == 3: # outputDir
            if config_input_output_numeric_options[index] > 0 and config_input_output_alphabetic_options[index][1] == '':
                config_label = str(config_input_output_alphabetic_options[index][0])
                missing_IO = missing_IO + config_label + '\n'
        index = index + 1
    return missing_IO

# check_missingIO is called from GUI_util
# the function checks for missing IO values, displays messages and sets the RUN button to normal or disabled
def check_missingIO(window,missingIO,config_filename, scriptName, IO_setup_display_brief, silent=False):
    # if 'NLP_menu_main' in scriptName:
    #     silent = True
    if config_filename=='NLP_config.csv' or 'NLP_menu_main' in scriptName:
        config_filename = 'NLP_default_IO_config.csv'
    # the IO_button_name error message changes depending upon the call
    button = "button"
    # there is no RUN button when setting up IO information so the call to check_missingIO should be silent
    # setup all potential error messages
    run_button_disabled_msg = "The RUN button is disabled until the required information for the selected Input/Output fields is entered.\n\n"
    if "IO_setup_main" in scriptName:
        run_button_disabled_msg = ""
        enter_required_IO='Press OK to enter the required I/O information using the \'Select INPUT and Select OUTPUT\' buttons at the top of the GUI.\nPress CANCEL to exit without entering I/O information then press CLOSE.'
    elif 'NLP_menu_main' in scriptName:
        enter_required_IO="Please, click on the top button 'Setup default I/O options: INPUT corpus file(s) and OUTPUT files directory' to enter the required I/O information."
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
    if config_filename == "social-science-research_config.csv":
        # RUN button always active since several options are available and IO gets checked in the respective scripts
        Run_Button_Off=False
        missingIO=''
    mutually_exclusive_msg=''
    if "Input txt filename with path" in missingIO and "Input files directory" in missingIO:
        mutually_exclusive_msg='The two I/O options - "Input txt filename with path" and "Input files directory" - are MUTUALLY EXCLUSIVE. YOU CAN ONLY HAVE ONE OR THE OTHER BUT NOT BOTH. In other words, you can choose to work with a sigle file in input or with many files stored in a directory.\n\n'
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
    try:
        window.focus_force()
    except:
        pass
    return run_button_state, answer

# every IO widget, files or directories, have a line in the config file
# config lines are blank, if NOT required by the specific NLP script

# input_output_options[0] 0 No input file 1 CoNLL file 2 TXT file 3 csv file 4 any single txt, pdf, docx, csv, conll file
# input_output_options[1] 0 NO input dir
# input_output_options[2] 0 NO input secondary dir
# input_output_options[3] 0 NO output dir
def write_IO_config_file(window, config_filename, config_input_output_numeric_options, config_input_output_alphabetic_options, silent=False):
    # print('IN  write_IO_config_file','\n  ', config_input_output_numeric_options, '\n  ', config_input_output_alphabetic_options)
    # check that the config directory exists inside the NLP main directory
    if os.path.isdir(GUI_IO_util.configPath) == False:
        try:
            os.mkdir(GUI_IO_util.configPath)
        except:
            mb.showwarning(title='Permission error?',
                           message="The command failed to create the Config directory.\n\nIf you look at your command line and you see a \'Permission error\', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on \'Properties\'. Make sure that the \'Attributes\' setting, the last one on the display window, is NOT set to \'Read only\'. If so, click on the checkbox until the Read only is cleared, click on \'Apply\' and then \'OK\', exit the NLP Suite and try again.")
            return

    config_filename_path=os.path.join(GUI_IO_util.configPath, config_filename)
    # temp = get_template_config_csv_file(config_input_output_numeric_options,config_input_output_alphabetic_options)
    # print("IN WRITE temp",temp)
    try:
        with open(config_filename_path, 'w+', newline='') as csv_file:
            writer = csv.writer(csv_file)
            # writer.writerows(temp)
            header = ['I/O configuration label', 'Path', 'Date format', 'Date separator character(s)', 'Date position']
            config_input_output_alphabetic_options.insert(0, header)
            writer.writerows(config_input_output_alphabetic_options)
        csv_file.close()
    except:
        mb.showwarning(title='Permission error?',
                       message="The command failed to save the config file\n\n" + config_filename + "\n\nIf you look at your command line and you see a \'Permission error\', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on \'Properties\'. Make sure that the \'Attributes\' setting, the last one on the display window, is NOT set to \'Read only\'. If so, click on the checkbox until the Read only is cleared, click on \'Apply\' and then \'OK\', exit the NLP Suite and try again.")

    if config_filename != 'license_config.csv':
        IO_user_interface_util.timed_alert(window, 1000, 'Warning',
                                           'INPUT and OUTPUT paths configuration have been saved to\n\n' + config_filename_path,
                                           False)

# used in GIS_GUI and GIS_geocode_GUI
# Google_config: 'Google-geocode-API_config.csv' or 'Google-Maps-API_config.csv'
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
