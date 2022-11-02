# Written by Roberto Franzosi, May 2021

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "IO_setup_main",
                                          ['os', 'tkinter', 'argparse']) == False:
    sys.exit(0)

# IO config are saved in config_util.save_IO_config after checking values in NLP_setup_update.exit_window

import argparse
import tkinter.messagebox as mb
import tkinter as tk

import GUI_IO_util
import config_util
import reminders_util
import IO_files_util

if __name__ == '__main__':
    # get arguments from command line
    parser = argparse.ArgumentParser(description='Setup Input/Output Options')
    parser.add_argument('--config_option', type=str, dest='config_option', default='',
                        help='a string to hold the I/O configuration for the GUI, e.g., [1,0,0,1]')
    parser.add_argument('--config_filename', type=str, dest='config_filename', default='',
                        help='a string to hold the config filename containing the selected I/O options, e.g., NLP_default_IO_config.csv')
    args = parser.parse_args()

    config_input_output_numeric_options = args.config_option
    config_filename = args.config_filename
    if len(config_input_output_numeric_options)==0:
        mb.showwarning(title='Warning',
                       message='You are running the IO_setup_main as a standalone. Although all _main scripts can be run independently as standalone GUIs, this particularly script cannot. It can only be opened via another GUI script. Sorry!\n\nThe GUI will close after clicking OK.')
        sys.exit(0)
    # convert config_option string to list
    # config_option is the I/O configuration for the specific GUI, e.g. [0,1,0,1]
    config_input_output_numeric_options = config_input_output_numeric_options.split(', ')
    config_input_output_numeric_options = list(map(int, config_input_output_numeric_options))

# RUN section ______________________________________________________________________________________________________________________________________________________

# There are no commands in the IO_setup GUI

# GUI section ______________________________________________________________________________________________________________________________________________________

if config_filename == 'NLP_menu_config.csv':
    config_filename = 'NLP_default_IO_config.csv'
config_file_label=config_filename
if 'default' in config_file_label:
    config_file_label='Default I/O configuration, to be saved to: ' + config_file_label
else:
    config_file_label='GUI-specific I/O configuration, to be saved to: ' + config_file_label

GUI_label = 'Graphical User Interface (GUI) for Setting Up Input/Output, I/O, Options (' + config_file_label + ")"
# The 4 values of config_option refer to:
#   input file
        # 1 for CoNLL file
        # 2 for TXT file
        # 3 for csv file
        # 4 for any type of file
        # 5 for txt or html
        # 6 for txt or csv
#   input dir
#   input secondary dir
#   output dir

# each GUI comes with the config_option specified  for the script,
# 	e.g., [2,1,0,1] when both an input file of type txt or an input dir are valid options
# 		  [0,1,0,1] in this case ONLY an inout Dir is a valid option

# define variables
y_multiplier_integer = 0
# GUI_size is reset many times in the script
GUI_width=str(GUI_IO_util.get_GUI_width(2))
GUI_size = GUI_width + 'x290'

extract_date_from_filename_var = tk.IntVar()
date_format_var = tk.StringVar()
date_separator_var = tk.StringVar()
date_position_var = tk.IntVar()

# either input file or dir (for corpus) and no secondary dir
if ((config_input_output_numeric_options[0] == 0 and config_input_output_numeric_options[1] != 0)
    or (config_input_output_numeric_options[0] != 0 and config_input_output_numeric_options[1] == 0)) \
        and config_input_output_numeric_options[2] == 0:
    GUI_size = GUI_width + 'x340'

# either input file or dir (for corpus) and secondary dir
if ((config_input_output_numeric_options[0] == 0 and config_input_output_numeric_options[1] != 0)
    or (config_input_output_numeric_options[0] != 0 and config_input_output_numeric_options[1] == 0)) \
        and config_input_output_numeric_options[2] != 0:
    GUI_size = GUI_width + 'x380'

# both input file and dir (for corpus) and no secondary dir
if config_input_output_numeric_options[0] != 0 and config_input_output_numeric_options[1] != 0 and config_input_output_numeric_options[2] == 0:
    GUI_size = GUI_width + 'x380'

# both input file and dir (for corpus) and secondary dir
if config_input_output_numeric_options[0] != 0 and config_input_output_numeric_options[1] != 0 and config_input_output_numeric_options[2] != 0:
    GUI_size = GUI_width + 'x420'

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window = GUI_util.window

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, False,'')

# check the GUI specific IO options against the default options in NLP_default_IO_config.csv
#	warning the user for any discrepancy

# the selection of files and directories is done in GUI_util, which in turn calls
#   selectFile or selectDirectory in IO_files_util
# initial folders are setup in IO_files_util

# config_input_output_alphabetic_options, config_input_output_full_options, missingIO = config_util.read_config_file(config_filename, config_input_output_numeric_options)
config_input_output_alphabetic_options, missingIO = config_util.read_config_file(config_filename, config_input_output_numeric_options)
# set existing GUI options

# TODO Must relay the widget here to display hover-over information, although the widget has been laid in GUI_util
# the index for config_input_output_numeric_options start at 0

# FILE INPUT
if config_input_output_numeric_options[0]!=0: # input filename
    label = ''
    if config_input_output_alphabetic_options[0][2]!='' and not 'Date: ' in config_input_output_alphabetic_options[0][1]:
        label = '  (Date: ' + str(config_input_output_alphabetic_options[0][2]) + \
                ', ' + str(config_input_output_alphabetic_options[0][3]) + \
                ', ' + str(config_input_output_alphabetic_options[0][4]) + ')'

    GUI_util.inputFilename.set(config_input_output_alphabetic_options[0][1] + label)
    inputFile_lb = tk.Label(window, textvariable=GUI_util.inputFilename)

    date_hover_over_label = ''
    if '  (Date: ' in label:
        date_hover_over_label = 'The input file has a date embedded in the filename with the following options for date format, date character(s) separator, and date position in filename.\n(Date: ' + GUI_util.inputFilename.get().split(' (Date:')[1]
    else:
        date_hover_over_label = 'The input file has no date embedded in the filename'
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window,
                                                   GUI_IO_util.entry_box_x_coordinate,
                                                   y_multiplier_integer,
                                                   inputFile_lb,
                                                   False, False, False, False, 90,
                                                   GUI_IO_util.IO_configuration_menu,
                                                   date_hover_over_label)

# TODO Must relay the widget here to display hover-over information, although the widget has been laid in GUI_util
# DIR INPUT
if config_input_output_numeric_options[1]!=0: # input dir
    label = ''
    date_hover_over_label = ''
    if config_input_output_alphabetic_options[1][2]!='' and not 'Date: ' in config_input_output_alphabetic_options[1][1]: # there is date format
        label = '  (Date: ' + str(config_input_output_alphabetic_options[1][2]) + \
                ', ' + str(config_input_output_alphabetic_options[1][3]) + \
                ', ' + str(config_input_output_alphabetic_options[1][4]) + ')'
        date_hover_over_label = 'The input file has a date embedded in the filename with the following values:\n' \
                                'Date format: ' + str(config_input_output_alphabetic_options[0][2]) + \
                                ' Date character(s) separator: ' + str(config_input_output_alphabetic_options[0][3]) + \
                                ' Date position: ' + str(config_input_output_alphabetic_options[0][4])

    GUI_util.input_main_dir_path.set(config_input_output_alphabetic_options[1][1] + label)
    inputMainDir_lb = tk.Label(window, textvariable=GUI_util.input_main_dir_path)
    date_hover_over_label = ''
    if '  (Date: ' in label:
        date_hover_over_label = 'The txt files in the input directory contain a date embedded in the filename with the following values:\n' + \
                                'Date format: ' + str(config_input_output_alphabetic_options[1][2]) + \
                                ' Date character(s) separator: ' + str(config_input_output_alphabetic_options[1][3]) + \
                                ' Date position: ' + str(config_input_output_alphabetic_options[1][4])
    else:
        date_hover_over_label = 'The txt files in the selected input directory have no date embedded in the filename'

    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window,
                                                   GUI_IO_util.entry_box_x_coordinate,
                                                   y_multiplier_integer,
                                                   inputMainDir_lb,
                                                   False, False, False, False, 90,
                                                   GUI_IO_util.IO_configuration_menu,
                                                   date_hover_over_label)

if config_input_output_numeric_options[2]!=0: # input secondary dir
    GUI_util.input_secondary_dir_path.set(config_input_output_alphabetic_options[2][1])
    y_multiplier_integer = y_multiplier_integer + 1

if config_input_output_numeric_options[3] != 0: # output dir
    GUI_util.output_dir_path.set(config_input_output_alphabetic_options[3][1])
    y_multiplier_integer = y_multiplier_integer +1

extract_date_checkbox = tk.Checkbutton(window, text='Extract date from filename (for dynamic GIS)', variable=extract_date_from_filename_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,
                                               GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer,
                                               extract_date_checkbox,
                                               True, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               'Tick the checkbox if the filename(s) used as your corpus embed a date (e.g, The New York Times_12-19-1899). Then select the appropriate information (please, read the ?HELP for more information).\n' \
                                                'The NLP Suite will use the information to build dynamic network graphs and dynamic GIS maps.')


date_format_lb = tk.Label(window,text='Format ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate,
                                               y_multiplier_integer, date_format_lb, True)
date_format_var.set('mm-dd-yyyy')
date_format_menu = tk.OptionMenu(window, date_format_var, 'mm-dd-yyyy', 'dd-mm-yyyy','yyyy-mm-dd','yyyy-dd-mm','yyyy-mm','yyyy')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.date_format_coordinate,
                                               y_multiplier_integer, date_format_menu, True)
date_separator_var.set('_')
date_separator_lb = tk.Label(window, text='Character separator ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.date_char_sep_lb_coordinate,
                                               y_multiplier_integer, date_separator_lb, True)

date_separator = tk.Entry(window, textvariable=date_separator_var, width=3)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.date_char_sep_coordinate,
                                               y_multiplier_integer, date_separator, True)

date_position_menu_lb = tk.Label(window, text='Position ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.date_position_lb_coordinate,
                                               y_multiplier_integer, date_position_menu_lb, True)
date_position_var.set(2)
date_position_menu = tk.OptionMenu(window,date_position_var,1,2,3,4,5)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.date_position_coordinate,
                                               y_multiplier_integer, date_position_menu)

def check_dateFields(*args):
    if extract_date_from_filename_var.get() == 1:
        date_format_menu.config(state="normal")
        date_separator.config(state='normal')
        date_position_menu.config(state='normal')
    else:
        date_format_menu.config(state="disabled")
        date_separator.config(state='disabled')
        date_position_menu.config(state="disabled")
extract_date_from_filename_var.trace('w',check_dateFields)

msg = ""
if config_filename == 'NLP_default_IO_config.csv':
    if (config_input_output_alphabetic_options[0][0]!='') or config_input_output_alphabetic_options[1][0]!='':
        # check the input filename
        if (config_input_output_alphabetic_options[0][0]!='') and config_input_output_numeric_options[0]==0:
            msg = "The Default I/O configuration used by all scripts in the NLP Suite is currently set up with a FILE in INPUT.\n\n" \
                "But the current script expects a DIRECTORY in INPUT.\n\n"
        # check the input directory
        if (config_input_output_alphabetic_options[1][0]!='') and config_input_output_numeric_options[1]==0:
            msg = "The Default I/O configuration used by all scripts in the NLP Suite is currently set up with a DIRECTORY in INPUT.\n\n" \
                "But the current script expects a FILE in INPUT.\n\n"
        if msg!="":
            msg=msg + \
                "If you change the Default I/O configuration, the new I/O configuration will be used by all scripts in the NLP Suite.\n\n" \
                "If this is not what you wish to do, you should CLOSE the I/O Setup GUI w/o saving any changes and use the GUI-specific I/O configuration for this specific script."

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Setup INPUT-OUTPUT options':'TIPS_NLP_Setup INPUT-OUTPUT options.pdf'}
TIPS_options='Setup INPUT-OUTPUT options'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    # 1 for CoNLL file
    # 2 for TXT file
    # 3 for csv file
    # 4 for any type of file
    # 5 for txt or html
    # 6 for txt or csv

    # HELP buttons
    if config_input_output_numeric_options[0]==1:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_CoNLL)
    elif config_input_output_numeric_options[0]==2:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_txtFile)
    elif config_input_output_numeric_options[0]==3:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_csvFile)
    elif config_input_output_numeric_options[0] == 4:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_anyFile)
    elif config_input_output_numeric_options[0]==5:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_txt_htmlFile)
    elif config_input_output_numeric_options[0]==6:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_csv_txtFile)

    # INPUT primary directory
    if config_input_output_numeric_options[1]!=0:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, select the main INPUT directory of the TXT files to be analyzed." + GUI_IO_util.msg_openExplorer)

    # INPUT secondary directory
    if config_input_output_numeric_options[2]!=0:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, select the secondary INPUT directory of the TXT files to be analyzed." + GUI_IO_util.msg_openExplorer)

    # OUTPUT  directory
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_outputDirectory)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         'Some of the algorithms in the NLP Suite (e.g., GIS models and network models) can build dynamic models (i.e., models that vary with tiime) when time/date is known. If the filenames in youur corpus embed a date (e.g., The New York Times_12-19-1899), the NLP Suite can use that metadata information to build dynamic models. If that is the case, using the dropdown menu, select the date format of the date embedded in the filename (default mm-dd-yyyy).\n\nPlease, enter the character used to separate the date field embedded in the filenames from the other fields (e.g., _ in the filename The New York Times_12-23-1992) (default _).\n\nPlease, using the dropdown menu, select the position of the date field in the filename (e.g., 2 in the filename The New York Times_12-23-1992; 4 in the filename The New York Times_1_3_12-23-1992 where perhaps fields 2 and 3 refer respectively to the page and column numbers) (default 2).')

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, hit the SAVE button to save any changes made.")

    return y_multiplier_integer -1

y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

def save_config(config_input_output_alphabetic_options):
    # config_input_output_alphabetic_options is a double list, each sublist of 4 items
    #   (path + 3 date items [[],[],...])
    # e.g., [['', '', '', ''], ['C:/Users/rfranzo/Desktop/NLP-Suite/lib/sampleData/newspaperArticles', 'mm/dd/yyyy', '_', '4'], ['', '', '', ''], ['C:/Program Files (x86)/NLP_backup/Output', '', '', '']]

    # build current options config_input_output_alphabetic_options, a list of 4 items: path + 3 date items


    # config_util.get_template_config_csv_file(config_input_output_numeric_options, config_input_output_alphabetic_options)

    fileType=config_util.getFiletype(config_input_output_numeric_options) # different types of input files

    input_item_date=[]

    # extract_date_from_filename_var, date_format_var, date_separator_var, date_position_var
    #   are all local to this GUI rather than on GUI_util
    if extract_date_from_filename_var.get():
        input_item_date.append(date_format_var.get())
        input_item_date.append(date_separator_var.get())
        input_item_date.append(date_position_var.get())
        date_label = ' (Date: ' + str(date_format_var.get()) + ' ' + \
                          str(date_separator_var.get()) + ' ' + \
                          str(int(date_position_var.get())) + ')'
    else:
        date_label = ''
        input_item_date=['','',0]

    inputFilename_list = []
    inputFilename_list.append(fileType)

    if not extract_date_from_filename_var.get():
        fileName_no_date=IO_files_util.open_file_removing_date_from_filename(window,GUI_util.inputFilename.get(),False)
        GUI_util.inputFilename.set(fileName_no_date)
    else:
        if GUI_util.inputFilename.get() != '':
            if '(Date: ' in GUI_util.inputFilename.get():
                GUI_util.inputFilename.set(GUI_util.inputFilename.get())
            else:
                GUI_util.inputFilename.set(GUI_util.inputFilename.get() + date_label)
        else:
            GUI_util.inputFilename.set('')
    inputFilename_list.append(GUI_util.inputFilename.get())
    if GUI_util.inputFilename.get() != '':
        inputFilename_list.extend(input_item_date)
    else:
        inputFilename_list.extend(['', '', 0])

# main_dir_path
    inputDir_list=[]
    # if GUI_util.input_main_dir_path.get()!='':
    inputDir_list.append('Input files directory')
    if not extract_date_from_filename_var.get():
        directory_no_date=IO_files_util.open_directory_removing_date_from_directory(window,GUI_util.input_main_dir_path.get(),False)
        GUI_util.input_main_dir_path.set(directory_no_date)
    else:
        if GUI_util.input_main_dir_path.get() != '':
            if '(Date: ' in GUI_util.input_main_dir_path.get():
                GUI_util.input_main_dir_path.set(GUI_util.input_main_dir_path.get())
            else:
                GUI_util.input_main_dir_path.set(GUI_util.input_main_dir_path.get() + date_label)
    inputDir_list.append(GUI_util.input_main_dir_path.get())
    if GUI_util.input_main_dir_path.get()!='':
        inputDir_list.extend(input_item_date)
    else:
        inputDir_list.extend(['', '', 0])

    input_item_date = ['', '', 0] # secondary dir and output dir do not have dates

    inputDir2_list = []
    # inputDir2_list.extend([GUI_util.input_secondary_dir_path.get(), '','',''])
    # if GUI_util.input_secondary_dir_path.get()!='':
    inputDir2_list.append('Input files secondary directory')
    inputDir2_list.append(GUI_util.input_secondary_dir_path.get())
    inputDir2_list.extend(input_item_date)

    outputDir_list = []
    # outputDir_list.extend([GUI_util.output_dir_path.get(), '','',''])
    # if GUI_util.output_dir_path.get()!='':
    outputDir_list.append('Output files directory')
    outputDir_list.append(GUI_util.output_dir_path.get())
    outputDir_list.extend(input_item_date)

    # combine all four Input/output options in a list
    current_config_input_output_alphabetic_options=[]
    current_config_input_output_alphabetic_options.append(inputFilename_list)
    current_config_input_output_alphabetic_options.append(inputDir_list)
    current_config_input_output_alphabetic_options.append(inputDir2_list)
    current_config_input_output_alphabetic_options.append(outputDir_list)

    config_util.write_IO_config_file(window, config_filename, config_input_output_numeric_options,
                                     current_config_input_output_alphabetic_options, silent=False)

save_button = tk.Button(window, text='SAVE', width=10, height=2, command=lambda: save_config(config_input_output_alphabetic_options))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.close_button_x_coordinate,
                                               y_multiplier_integer, save_button)

y_multiplier_integer = y_multiplier_integer +.5

# change the value of the readMe_message
readMe_message = "This Python 3 script provides a front-end GUI (Graphical User Interface) for setting up the Input/Output information necessary to run the NLP-Suite scripts, namely the INPUT files to be used - a single file or a set of files in a directory - and the OUTPUT directory where the files produced by the NLP Suite scripts will be saved - txt, csv, html, kml, jpg.\n\nThe selected I/O configuration will be saved in config files in the config subdirectory. The NLP_default_IO_config.csv file will be used for all NLP Suite scripts unless a different configuraton is selected for a specific script by selecting the 'Alternative I/O configuation'. When opening the GUI with the option 'Alternative I/O configuation' a configuration file will be saved under the config subdirectory with the specif name of the calling script (e.g., Stanford-CoreNLP_config.csv).\n\nWhen clicking the CLOSE button, the script will give the option to save the currently selected configuration IF different from the previously saved configuration."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, False, 'NLP_setup_IO_main')

if msg!="":
    mb.showwarning(title='Warning', message=msg)

result = reminders_util.checkReminder(config_filename,
                              reminders_util.title_options_IO_setup,
                              reminders_util.message_IO_setup)
if result!=None:
    routine_options = reminders_util.getReminders_list(config_filename)

result = reminders_util.checkReminder(config_filename,
                              reminders_util.title_options_IO_setup_date_options,
                              reminders_util.message_IO_setup_date_options)

GUI_util.window.mainloop()
