# Written by Roberto Franzosi November 2019, updated December 2021
# input_output_options[0] 0 No input file 1 CoNLL file 2 TXT file 3 csv file 4 any single txt, pdf, docx, csv, conll file
# input_output_options[1] 0 NO input dir
# input_output_options[2] 0 NO input secondary dir
# input_output_options[3] 0 NO output dir
# every IO widget, files or directories, has a line in the config file
# config lines can be blank if NOT required by the specific NLP script
import csv
import logging
import os
from subprocess import call

import GUI_IO_util
import IO_user_interface_util
import pandas as pd

logger = logging.getLogger(__name__)

defaultConfigFilename = "NLP_default_IO_config.csv"


# fileName with path, the value saved in config_filename
def checkConfigFileExists(config_filename, fileName, IO):
    error = False
    # check that the config file exists first, after adding path to file
    if not os.path.isfile(os.path.join(GUI_IO_util.configPath, config_filename)):
        error = True
        logger.info(
            "File error %s",
            'The "'
            + config_filename
            + '" config file does not exist. It must have been never created, deleted, or moved.\n\nYou must re-create the file by selecting the appropriate I/O options, save them, and try again!',
        )
        fileName = ""
    else:
        if fileName != "":
            if not os.path.isfile(fileName):
                # must pass the right config filename in case there is only the default config
                if not os.path.isfile(config_filename) and os.path.isfile(
                    os.path.join(GUI_IO_util.configPath, defaultConfigFilename)
                ):
                    config_filename = defaultConfigFilename
                logger.info(
                    "File error %s",
                    "The "
                    + IO
                    + " file saved in "
                    + config_filename
                    + "\n\n"
                    + fileName
                    + "\n\nno longer exists. It must have been deleted or moved.\n\nPlease, select a new "
                    + IO
                    + " file and try again!",
                )
                fileName = ""
    return error, fileName


# dirName, the value saved in config_filename
def checkConfigDirExists(config_filename, dirName, IO):
    # the error variable is used to avoid checking repeatedly, with repeated error messages, when checking the config file
    error = False
    # check that the config file exists first, after adding path to file
    if not os.path.isfile(os.path.join(GUI_IO_util.configPath, config_filename)):
        error = True
        logger.info(
            "File error %s",
            'The "'
            + config_filename
            + '" config file does not exist. It must have been never created, deleted, or moved.\n\nYou must re-create the file by selecting the appropriate I/O options, save them, and try again!',
        )

        dirName = ""
    else:
        if dirName != "":
            if not os.path.isdir(dirName):
                # must pass the right config filename in case there is only the default config
                if not os.path.isfile(config_filename) and os.path.isfile(
                    os.path.join(GUI_IO_util.configPath, defaultConfigFilename)
                ):
                    config_filename = defaultConfigFilename
                logger.info(
                    "Directory error %s",
                    "The "
                    + IO
                    + " directory saved in "
                    + config_filename
                    + "\n\n"
                    + dirName
                    + "\n\nno longer exists. It must have been deleted or moved.\n\nPlease, select a new "
                    + IO
                    + " directory and try again!",
                )
                dirName = ""
    return error, dirName


# config_input_output_numeric_options is a list
def getFiletype(config_input_output_numeric_options):
    if config_input_output_numeric_options[0] == 1:
        fileType = "Input csv CoNLL filename with path"
    elif config_input_output_numeric_options[0] == 2:
        fileType = "Input txt filename with path"
    elif config_input_output_numeric_options[0] == 3:
        fileType = "Input csv filename with path"
    elif config_input_output_numeric_options[0] == 4:
        fileType = "Input txt/pdf/docx/csv filename with path"
    else:
        fileType = "Input filename with path"
    return fileType


def write_external_software_config_file(config_filename, currently_selected_options, currently_selected_parsers):
    # check that the config directory exists inside the NLP main directory
    if os.path.isdir(GUI_IO_util.configPath) is False:
        try:
            os.mkdir(GUI_IO_util.configPath)
        except Exception:
            logger.info(
                "Permission error? The command failed to create the Config directory.\n\nIf you look at your command line and you see a 'Permission error', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on 'Properties'. Make sure that the 'Attributes' setting, the last one on the display window, is NOT set to 'Read only'. If so, click on the checkbox until the Read only is cleared, click on 'Apply' and then 'OK', exit the NLP Suite and try again."
            )
            return

    config_filename_path = os.path.join(GUI_IO_util.configPath, config_filename)
    try:
        # TODO any change in the labels MAIN NLP PACKAGE, LEMMATIZER PACKAGE, and LANGUAGE(S) must be carried out
        #   several times in this scripts (search for instance for MAIN NLP PACKAGE and change
        #   they also need to be changed in one line in NLP_setup_package_language_main.py
        csv_file = pd.DataFrame()
        csv_file.at[0, "Software"] = currently_selected_options["MAIN NLP PACKAGE"]
        csv_file.at[0, "Path"] = {currently_selected_parsers}
        csv_file.at[0, "Download_link)"] = currently_selected_options["LEMMATIZER PACKAGE"]

        csv_file.to_csv(config_filename_path, encoding="utf-8", index=False)

        IO_user_interface_util.timed_alert(
            2000,
            "Warning",
            "NLP external software options have been saved to\n\n  " + config_filename_path,
            False,
        )
    except Exception:
        logger.info(
            "Permission error? %s",
            "The command failed to save the config file\n\n"
            + config_filename
            + "\n\nIf you look at your command line and you see a 'Permission error', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on 'Properties'. Make sure that the 'Attributes' setting, the last one on the display window, is NOT set to 'Read only'. If so, click on the checkbox until the Read only is cleared, click on 'Apply' and then 'OK', exit the NLP Suite and try again.",
        )


def read_NLP_package_language_config():
    package = ""
    parsers = []
    basics_package = ""
    language = ""
    encoding_var = "utf-8"
    export_json_var = 0
    memory_var = 4
    limit_document_length_var = 90000
    limit_sentence_length_var = 100
    config_filename = GUI_IO_util.configPath + os.sep + "NLP_default_package_language_config.csv"
    error = False
    if not os.path.exists(config_filename):
        logger.info(
            "Warning The config file 'NLP_default_package_language_config.csv' could not be found in the sub-directory 'config' of your main NLP Suite folder.\n\nPlease, setup the default NLP package and language options using the Setup button."
        )
        error = True
    else:
        try:
            dataset = pd.read_csv(config_filename, encoding="utf-8", on_bad_lines="skip")
            package = dataset.iat[0, 0]
            parsers = dataset.iat[0, 1].split(",")
            basics_package = dataset.iat[0, 2]
            language = dataset.iat[0, 3]
            encoding_var = dataset.iat[0, 4]
            export_json_var = int(dataset.iat[0, 5])
            memory_var = int(dataset.iat[0, 6])
            limit_document_length_var = int(dataset.iat[0, 7])
            limit_sentence_length_var = int(dataset.iat[0, 8])
            # TODO any change in the labels MAIN NLP PACKAGE, LEMMATIZER PACKAGE, and LANGUAGE(S) must be carried out
            #   several times in this scripts (search for instance for MAIN NLP PACKAGE and change
            #   they also need to be changed in one line in NLP_setup_package_language_main.py
        except Exception:
            # setup default values if config is not available for first tme users
            package = "Stanford CoreNLP"
            parsers = ["Neural Network", "Probabilistic Context Free Grammar (PCFG)"]
            basics_package = "Stanza"
            language = ""
            encoding_var = "utf-8"
            export_json_var = 0
            memory_var = 4
            limit_document_length_var = 90000
            limit_sentence_length_var = 100
            error = True
            # error must be set to true to display the next message after the entire GUI has been displayed
            # mb.showwarning(title='Warning',
            #                message="The config file 'NLP_default_package_language_config.csv' could not be found in the sub-directory 'config' of your main NLP Suite folder.\n\nPlease, setup the default NLP package and language options using the Setup button.")
    package_display_area_value = (
        f"MAIN NLP PACKAGE: {package}, LEMMATIZER PACKAGE: {basics_package}, LANGUAGE(S): {language}"
    )
    return (
        error,
        package,
        parsers,
        basics_package,
        language,
        package_display_area_value,
        encoding_var,
        export_json_var,
        memory_var,
        limit_document_length_var,
        limit_sentence_length_var,
    )


def write_NLP_package_language_config_file(
    config_filename,
    currently_selected_options,
    currently_selected_parsers,
    encoding_var,
    export_json_var,
    memory,
    limit_document_length,
    limit_sentence_length,
):
    # check that the config directory exists inside the NLP main directory
    if os.path.isdir(GUI_IO_util.configPath) is False:
        try:
            os.mkdir(GUI_IO_util.configPath)
        except Exception:
            logger.info(
                "Permission error? The command failed to create the Config directory.\n\nIf you look at your command line and you see a 'Permission error', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on 'Properties'. Make sure that the 'Attributes' setting, the last one on the display window, is NOT set to 'Read only'. If so, click on the checkbox until the Read only is cleared, click on 'Apply' and then 'OK', exit the NLP Suite and try again."
            )
            return

    config_filename_path = os.path.join(GUI_IO_util.configPath, config_filename)
    try:
        # TODO any change in the labels MAIN NLP PACKAGE, LEMMATIZER PACKAGE, and LANGUAGE(S) must be carried out
        #   several times in this scripts (search for instance for MAIN NLP PACKAGE and change
        #   they also need to be changed in one line in NLP_setup_package_language_main.py
        csv_file = pd.DataFrame()
        csv_file.at[0, "Parser & annotators"] = currently_selected_options["MAIN NLP PACKAGE"]
        csv_file.at[0, "Parsers"] = {currently_selected_parsers}
        csv_file.at[0, "Basic functions (tokenizer/lemmatizer)"] = currently_selected_options["LEMMATIZER PACKAGE"]
        csv_file.at[0, "Corpus language"] = currently_selected_options["LANGUAGE(S)"]
        csv_file.at[0, "Language encoding"] = encoding_var
        csv_file.at[0, "Export Json"] = export_json_var
        csv_file.at[0, "CoreNLP memory"] = int(memory)
        csv_file.at[0, "CoreNLP document length"] = int(limit_document_length)
        csv_file.at[0, "CoreNLP sentence-length limit"] = int(limit_sentence_length)

        csv_file.to_csv(config_filename_path, encoding="utf-8", index=False)

        IO_user_interface_util.timed_alert(
            2000,
            "Warning",
            "NLP package and language options have been saved to\n\n  " + config_filename_path,
            False,
        )
    except Exception:
        logger.info(
            "Permission error? %s",
            "The command failed to save the config file\n\n"
            + config_filename
            + "\n\nIf you look at your command line and you see a 'Permission error', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on 'Properties'. Make sure that the 'Attributes' setting, the last one on the display window, is NOT set to 'Read only'. If so, click on the checkbox until the Read only is cleared, click on 'Apply' and then 'OK', exit the NLP Suite and try again.",
        )


def save_NLP_package_language_config(
    currently_selected_options,
    package,
    basics_package,
    language,
    parsers,
    encoding,
    export_json,
    memory,
    limit_document_length,
    limit_sentence_length,
):
    config_filename = GUI_IO_util.configPath + os.sep + "NLP_default_package_language_config.csv"
    # TODO any change in the labels MAIN NLP PACKAGE, LEMMATIZER PACKAGE, and LANGUAGE(S) must be carried out
    #   several times in this scripts (search for instance for MAIN NLP PACKAGE and change
    #   they also need to be changed in one line in NLP_setup_package_language_main.py
    write_NLP_package_language_config_file(
        config_filename,
        currently_selected_options,
        parsers,
        encoding,
        export_json,
        memory,
        limit_document_length,
        limit_sentence_length,
    )


# config_input_output_alphabetic_options is a double list with no headers,
#   with one sublist for each of the four types of IO confiigurations: filename, input main dir, input secondary dir, output dir
# each sublist has four items: path, date format, date separator, date position
# e.g., [['C:/Users/rfranzo/Desktop/NLP-Suite/lib/sampleData/The Three Little Pigs.txt', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['C:\\Program Files (x86)\\NLP_backup\\Output', '', '', '']]
# 5 fields: label/path + sort order + 3 date items (Item separator character(s), Date format, Date position)


def get_template_config_csv_file(config_input_output_numeric_options, config_input_output_alphabetic_options):
    IO_configuration = []
    fileType = getFiletype(config_input_output_numeric_options)  # different types of input files
    IO_configuration_label = [
        fileType,
        "Input files directory",
        "Input files secondary directory",
        "Output files directory",
    ]

    # loop through the 4 rows of input file, input primary dir, input secondary dir, output dir
    # configuration_column_label is the set of values in IO_configuration_label defined above
    for index, configuration_column_label in enumerate(IO_configuration_label):  # row is the sublist
        if len(config_input_output_alphabetic_options) > 0:
            if len(config_input_output_alphabetic_options[index]) > 0:
                sublist = config_input_output_alphabetic_options[index]
                # 5 fields: label/path + sort order + 3 date items
                # date options saved: date format, date characters separator, date position in filename
                # =5 when date options are available (path + sort order + 3 date options), otherwise =1
                # [configuration_column_label, sublist[0], sublist[1], sublist[2], sublist[3]])
                IO_configuration.append(
                    [
                        configuration_column_label,
                        sublist[0],
                        sublist[1],
                        sublist[4],
                        sublist[3],
                        sublist[4],
                    ]
                )
                if len(sublist) == 5:
                    IO_configuration.append(
                        [
                            configuration_column_label,
                            sublist[0],
                            sublist[1],
                            sublist[2],
                            sublist[3],
                            sublist[4],
                        ]
                    )
                else:
                    IO_configuration.append([configuration_column_label, sublist[0]])
                config_input_output_alphabetic_options = IO_configuration
        else:
            # 5 fields: label/path + sort order + 3 date items (Item separator character(s), Date format, Date position)
            IO_configuration.append([IO_configuration_label[index], "", "", "", 0])
    return IO_configuration


# called by get_missing_IO_values in GUI_util and readConfig below
# returns config_input_output_alphabetic_options, a double list of csv IO labels and values
#   each sublist containing 5 items
# config_option_csv contains 5 columns for each of four rows of input filename, directory, secondary directory, output directory
#   Oct 2022 added 3 more columns for date options of either fileName or Input Dir: date format, character separator, date position
#   Jan 2023 added sort order
# 5 fields: label/path + sort order + 3 date items


def read_config_file(config_filename, config_input_output_numeric_options):
    config_input_output_alphabetic_options = []
    configFilePath = os.path.join(GUI_IO_util.configPath, config_filename)
    # check that the config file exists
    if os.path.isfile(configFilePath):
        config_file_exists = True
        csv_file = open(configFilePath, newline="")
        config_input_output_alphabetic_options = list(csv.reader(csv_file, delimiter=","))
        config_input_output_alphabetic_options.pop(0)  # skip header
        # if not 'Date format' in config_input_output_alphabetic_options[0]: # len(config_input_output_alphabetic_options[0])==2:
        if len(config_input_output_alphabetic_options[0]) == 2:
            logger.info(
                "Obsolete csv config file structure %s",
                "The "
                + configFilePath
                + " has an obsolete config file structure.\n\nIt will be automatically deleted.\n\nPlease, enter next the Input/output configuration options that will be saved with the new file structure.",
            )
            csv_file.close()
            os.remove(configFilePath)
            # repeat until the user has entered the appropriate information in NLP_setup_IO_main.py
            while not os.path.isfile(configFilePath):
                call(
                    "python NLP_setup_IO_main.py --config_option "
                    + str(config_input_output_numeric_options).replace("[", '"').replace("]", '"')
                    + " --config_filename "
                    + config_filename,
                    shell=True,
                )
                if not os.path.isfile(configFilePath):
                    logger.info(
                        "Missing IO configuration data  You must enter the appropriate Input/output configuration options in NLP_setup_IO_main.py and SAVE them to exit this loop."
                    )
            # read the newly saved options
            csv_file = open(configFilePath, newline="")
            config_input_output_alphabetic_options = list(csv.reader(csv_file, delimiter=","))
            config_input_output_alphabetic_options.pop(0)  # skip header
            # cannot use read_config_file again or it returns the old config_input_output_numeric_options
            #   and the program bombs in GUI_util
        csv_file.close()
    else:
        config_file_exists = False
        config_input_output_alphabetic_options = list()
        # setup an empty double list config_input_output_alphabetic_options, WITHOUT header
        # @@@RF also added sort order
        config_input_output_alphabetic_options = get_template_config_csv_file(
            config_input_output_numeric_options, config_input_output_alphabetic_options
        )
    missing_IO = get_missing_IO_values(config_input_output_numeric_options, config_input_output_alphabetic_options)
    return config_input_output_alphabetic_options, missing_IO, config_file_exists


# called by read_config_file above
# returns the IO labels that are missing: Filename, Dir, output Dir
def get_missing_IO_values(config_input_output_numeric_options, config_input_output_alphabetic_options):
    missing_IO = ""
    # loop through the 4 input/output options: input filename, input man dir, input secondary dir, output dir
    index = 0
    # index ranges 0-3: Input filename, input main dir, input secondary dir, output dir
    while index < len(config_input_output_alphabetic_options):
        if index == 0:  # filename;
            # if the filename is an option (config_input_output_numeric_options[index-1])
            #   and its path value is config_option_csv[index-1][1] is blank check directory
            if (
                config_input_output_numeric_options[index] > 0
                and config_input_output_alphabetic_options[index][1] == ""
            ):
                # in [1][1] the first [1] refers to row number (input dir) the second to column number (the path)
                if config_input_output_alphabetic_options[1][1] == "":  # check input dir
                    # add filename as missing if dir not there either; dir will be added in next check
                    config_label = str(config_input_output_alphabetic_options[index][0])
                    missing_IO = missing_IO + config_label + "\n"
        elif index == 1:  # Input files dir
            if config_input_output_numeric_options[index] > 0 and config_input_output_alphabetic_options[1][1] == "":
                # in [0][1] the first [0] refers to row number (input filename) the second to column number (the path)
                if config_input_output_alphabetic_options[0][1] == "":  # check input filename
                    config_label = str(config_input_output_alphabetic_options[index][0])
                    missing_IO = missing_IO + config_label + "\n"
        elif index == 2:  # Input files secondary dir
            if (
                config_input_output_numeric_options[index] > 0
                and config_input_output_alphabetic_options[index][1] == ""
            ):
                config_label = str(config_input_output_alphabetic_options[index][0])
                missing_IO = missing_IO + config_label + "\n"
        elif index == 3:  # outputDir
            if (
                config_input_output_numeric_options[index] > 0
                and config_input_output_alphabetic_options[index][1] == ""
            ):
                config_label = str(config_input_output_alphabetic_options[index][0])
                missing_IO = missing_IO + config_label + "\n"
        index = index + 1
    return missing_IO


# check_missing_IO is called from GUI_util
# the function checks for missing IO values, displays messages and sets the RUN button to normal or disabled
def check_missing_IO(config_filename, scriptName, IO_setup_display_brief, missing_IO, silent=False):
    if config_filename == "NLP_config.csv" or "NLP_menu_main" in scriptName:
        config_filename = "NLP_default_IO_config.csv"
    Run_Button_Off = False
    if Run_Button_Off:
        run_button_state = "disabled"
    else:
        run_button_state = "normal"
    return run_button_state, False


# every IO widget, files or directories, have a line in the config file
# config lines are blank, if NOT required by the specific NLP script


# config_input_output_alphabetic_options is a double list with no headers,
#   with one sublist for each of the four types of IO configurations: filename, input main dir, input secondary dir, output dir
# each sublist has four items: path, date format, date separator, date position
# e.g., [['C:/Users/rfranzo/Desktop/NLP-Suite/lib/sampleData/The Three Little Pigs.txt', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['C:\\Program Files (x86)\\NLP_backup\\Output', '', '', '']]
def write_IO_config_file(
    config_filename,
    config_input_output_numeric_options,
    config_input_output_alphabetic_options,
    silent=False,
):
    # check that the config directory exists inside the NLP main directory
    if not os.path.isdir(GUI_IO_util.configPath):
        try:
            os.mkdir(GUI_IO_util.configPath)
        except Exception:
            logger.info(
                "Permission error? The command failed to create the Config directory.\n\nIf you look at your command line and you see a 'Permission error', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on 'Properties'. Make sure that the 'Attributes' setting, the last one on the display window, is NOT set to 'Read only'. If so, click on the checkbox until the Read only is cleared, click on 'Apply' and then 'OK', exit the NLP Suite and try again."
            )
            return

    config_filename_path = os.path.join(GUI_IO_util.configPath, config_filename)
    try:
        with open(config_filename_path, "w+", newline="") as csv_file:
            writer = csv.writer(csv_file)
            # in the NLP_setup_IO_config there are 6 columns and 4 rows (each row for input file, input dir1, input dir2, output dir)
            header = [
                "I/O configuration label",
                "Path",
                "Sort order",
                "Item separator character(s)",
                "Date format",
                "Date position",
            ]
            config_input_output_alphabetic_options.insert(0, header)
            writer.writerows(config_input_output_alphabetic_options)
        csv_file.close()
    except Exception:
        logger.info(
            "Permission error? %s",
            "The command failed to save the config file\n\n"
            + config_filename
            + "\n\nIf you look at your command line and you see a 'Permission error', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on 'Properties'. Make sure that the 'Attributes' setting, the last one on the display window, is NOT set to 'Read only'. If so, click on the checkbox until the Read only is cleared, click on 'Apply' and then 'OK', exit the NLP Suite and try again.",
        )

    if config_filename != "license_config.csv":
        IO_user_interface_util.timed_alert(
            2000,
            "Warning",
            "INPUT and OUTPUT paths configuration have been saved to\n\n" + config_filename_path,
            False,
        )


def get_date_options(config_filename, config_input_output_numeric_options):

    # in the NLP_setup_IO_config there are 6 columns and 4 rows (each row for input file, input dir1, input dir2, output dir):
    # 5 fields: label/path + sort order + 3 date items (Item separator character(s), Date format, Date position)
    config_input_output_alphabetic_options, missing_IO, config_file_exists = read_config_file(
        config_filename, config_input_output_numeric_options
    )
    if len(config_input_output_alphabetic_options) > 0:
        index = 0
        # define variable with default values
        filename_embeds_date_var = 0
        date_format_var = "mm/dd/yyyy"  # default
        items_separator_var = "_"  # default
        date_position_var = 2  # default
        while index < 2:  # check date options for input file and input dir
            # date options saved: date format, date characters separator, date position in filename
            # =4 when date options are available (path + sort order + 3 date options), otherwise =1
            # @@@RF
            # rows from a missing config file are 5-element templates with no date fields
            row = config_input_output_alphabetic_options[index]
            if len(row) > 5 and row[4] != "":  # check date format field
                filename_embeds_date_var = 1
                date_format_var = row[4]
                items_separator_var = row[3]
                date_position_var = int(row[5])
            index = index + 1
    return (
        filename_embeds_date_var,
        date_format_var,
        items_separator_var,
        date_position_var,
        config_file_exists,
    )


# used in GIS_GUI and GIS_geocode_GUI
def Google_API_Config_Save(Google_config, Google_API_key):
    # save the API key is not blank and not already there
    if Google_API_key != "":
        GoogleConfigFilename = os.path.join(GUI_IO_util.configPath, Google_config)
        # if not os.path.isfile(GoogleConfigFilename):
        with open(GoogleConfigFilename, "w+", newline="", encoding="utf-8", errors="ignore") as file1:
            file1.write(Google_API_key)
            if "Maps" in Google_config:
                msg = "Maps"
            else:
                msg = "geocoder"
            IO_user_interface_util.timed_alert(
                2000,
                "Warning",
                "The Google API key\n\n"
                + Google_API_key
                + "\n\nhas been saved to "
                + GoogleConfigFilename
                + '."\n\nIt will read in automatically every time you select the Google '
                + msg,
            )
        file1.close()
