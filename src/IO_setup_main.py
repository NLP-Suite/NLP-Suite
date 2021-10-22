# Written by Roberto Franzosi, May 2021

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "IO_setup_main",
                                          ['os', 'tkinter', 'argparse']) == False:
    sys.exit(0)

import argparse
import tkinter.messagebox as mb

import GUI_IO_util
import config_util
import reminders_util

if __name__ == '__main__':
    # get arguments from command line
    parser = argparse.ArgumentParser(description='Setup Input/Output Options')
    parser.add_argument('--config_option', type=str, dest='config_option', default='',
                        help='a string to hold the I/O configuration for the GUI, e.g., [0, 1, 1, 0, 0, 1]')
    parser.add_argument('--config_filename', type=str, dest='config_filename', default='',
                        help='a string to hold the config filename containing the selected I/O options, e.g., default-config.txt')
    args = parser.parse_args()

    config_option = args.config_option
    config_filename = args.config_filename
    if len(config_option)==0:
        mb.showwarning(title='Warning',
                       message='You are running the IO_setup_main as a standalone. Although all _main scripts can be run independently as standalone GUIs, this particularly script cannot. It can only be opened via another GUI script. Sorry!\n\nThe GUI will close after clicking OK.')
        sys.exit(0)
    # convert config_option string to list
    # config_option is the I/O configuration for the specific GUI, e.g. [0, 0, 1, 0, 0, 1]
    config_option = config_option.split(', ')
    config_option = list(map(int, config_option))

# RUN section ______________________________________________________________________________________________________________________________________________________

# There are no commands in the IO_setup GUI

# GUI section ______________________________________________________________________________________________________________________________________________________

config_file_label=config_filename
if 'default' in config_file_label:
    config_file_label='Default I/O configuration, to be saved to: ' + config_file_label
else:
    config_file_label='Alternative I/O configuration, to be saved to : ' + config_file_label

GUI_label = 'Graphical User Interface (GUI) for Setting Up Input/Output, I/O, Options (' + config_file_label + ")"
# The 6 values of config_option refer to:
#   software directory
#   input file
# 1 for CoNLL file
# 2 for TXT file
# 3 for csv file
# 4 for any type of file
# 5 for txt or html
# 6 for txt or csv
#   input dir
#   input secondary dir
#   output file
#   output dir

# each GUI comes with the config_option specified  for the script,
# 	e.g., [0, 2, 1, 0, 0, 1] when both an input file of type txt or an input dir are valid options
# 		  [0,0,1,0,0,1] in this case ONLY an inout Dir is a valid option

help_increment = 0
GUI_size = '1100x280'
if config_option[1] != 0: # no input file; only dir (for corpus)
    GUI_size = '1100x240'
    help_increment = 0
if config_option[2] != 0:  # both input file and input dir are valid options
    if config_option[1] == 0:
        GUI_size = '1100x240'
        help_increment = 0
    else:
        GUI_size = '1100x280'
        help_increment = 1
# the secondary INPUT directory is currently not used in IO_setup
if config_option[3] != 0:  # secondary INPUT directory
    GUI_size = '1100x320'
    help_increment = 2

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

y_multiplier_integer = GUI_util.y_multiplier_integer

window = GUI_util.window
config_input_output_options = GUI_util.config_input_output_options

GUI_util.GUI_top(config_input_output_options, config_filename, False)

# check the GUI specific IO options against the default options in default-config.txt
#	warning the user for any discrepancy

# the selection of files and directories is done in GUI_util, which in turn calls
#   selectFile or selectDirectory in IO_files_util
# initial folders are setup in IO_files_util

msg = ""
default_IO_options = config_util.get_IO_options(config_filename, config_input_output_options)
if config_filename == 'default-config.txt':
    if (default_IO_options[1]!='' and default_IO_options[1]!='EMPTY LINE') or default_IO_options[2]!='':
        # if (default_IO_options[1] != '' and default_IO_options[1] != 'EMPTY LINE') or default_IO_options[2] != '':
        # check the input filename
        if (default_IO_options[1]!='' and default_IO_options[1]!='EMPTY LINE') and config_input_output_options[1]==0:
            msg = "The Default I/O configuration used by all scripts in the NLP Suite is currently set up with a FILE in INPUT.\n\n" \
                "But the current script expects a DIRECTORY in INPUT.\n\n"
        # check the input directory
        if (default_IO_options[2]!='' and default_IO_options[2]!='EMPTY LINE') and config_input_output_options[2]==0:
            msg = "The Default I/O configuration used by all scripts in the NLP Suite is currently set up with a DIRECTORY in INPUT.\n\n" \
                "But the current script expects a FILE in INPUT.\n\n"
        if msg!="":
            msg=msg + \
                "If you change the Default I/O configuration, the new I/O configuration will be used by all scripts in the NLP Suite.\n\n" \
                "If this is not what you wish to do, you should CLOSE the I/O Setup GUI w/o saving any changes and use the Alternative I/O configuration for this specific script."

TIPS_lookup = {'Setup INPUT-OUTPUT options':'TIPS_NLP_Setup INPUT-OUTPUT options.pdf'}
TIPS_options='Setup INPUT-OUTPUT options'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, basic_y_coordinate, y_step):
    # 1 for CoNLL file
    # 2 for TXT file
    # 3 for csv file
    # 4 for any type of file
    # 5 for txt or html
    # 6 for txt or csv

    # INPUT file by type
    if config_option[1]==1:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_CoNLL)
    elif config_option[1]==2:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_txtFile)
    elif config_option[1]==3:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_csvFile)
    elif config_option[1] == 4:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_anyFile)
    elif config_option[1]==5:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_txt_htmlFile)
    elif config_option[1]==6:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_csv_txtFile)
    # INPUT primary directory
    if config_option[2]!=0:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + (y_step * help_increment), "Help",
                                      "Please, select the main INPUT directory of the TXT files to be analyzed." + GUI_IO_util.msg_openExplorer)

    # NOT currently used in setup
    # INPUT secondary directory
    if config_option[3]!=0:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + (y_step * help_increment), "Help",
                                      "Please, select the secondary INPUT directory of the TXT files to be analyzed." + GUI_IO_util.msg_openExplorer)

    # OUTPUT  directory
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + (y_step * (help_increment+1)), "Help",
                                  GUI_IO_util.msg_outputDirectory)

help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), GUI_IO_util.get_basic_y_coordinate(),
             GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message = "This Python 3 script provides a front-end GUI (Graphical User Interface) for setting up the Input/Output information necessary to run the NLP-Suite scripts, namely the INPUT files to be used - a single file or a set of files in a directory - and the OUTPUT directory where the files produced by the NLP Suite scripts will be saved - txt, csv, html, kml, jpg.\n\nThe selected I/O configuration will be saved in config files in the config subdirectory. The default-config.txt file will be used for all NLP Suite scripts unless a different configuraton is selected for a specific script by selecting the 'Alternative I/O configuation'. When opening the GUI with the option 'Alternative I/O configuation' a configuration file will be saved under the config subdirectory with the specif name of the calling script (e.g., Stanford-CoreNLP-config.txt).\n\nWhen clicking the CLOSE button, the script will give the option to save the currently selected configuration IF different from the previously saved configuration."
readMe_command = lambda: GUI_IO_util.readme_button(window, GUI_IO_util.get_help_button_x_coordinate(),
                                                   GUI_IO_util.get_basic_y_coordinate(), "Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_options, y_multiplier_integer, readMe_command, TIPS_lookup, TIPS_options,False,'IO_setup_main')

if msg!="":
    mb.showwarning(title='Warning', message=msg)

# routine_options = reminders_util.getReminders_list(config_filename)
result = reminders_util.checkReminder(config_filename,
                              reminders_util.title_options_IO_setup,
                              reminders_util.message_IO_setup)
if result!=None:
    routine_options = reminders_util.getReminders_list(config_filename)

GUI_util.window.mainloop()
