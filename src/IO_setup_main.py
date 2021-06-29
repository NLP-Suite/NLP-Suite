# Written by Roberto Franzosi, May 2021

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "IO_setup_main",
										  ['os', 'tkinter', 'argparse']) == False:
	sys.exit(0)

import tkinter as tk
import argparse

import GUI_IO_util

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
	# convert config_option string to list
	config_option = config_option.split(', ')
	config_option = list(map(int, config_option))

	print("config_filename",config_filename)

# RUN section ______________________________________________________________________________________________________________________________________________________


# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
# run_script_command = lambda: run(GUI_util.inputFilename.get(),
# 								 GUI_util.input_main_dir_path.get(),
# 								 GUI_util.input_secondary_dir_path.get(),
# 								 GUI_util.output_dir_path.get())
# GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

GUI_label = 'Graphical User Interface (GUI) for Setting Up Input/Output, IO, Options (' +config_filename + ")"
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

# if __name__ == '__main__':
# 	# get arguments from command line
# 	parser = argparse.ArgumentParser(description='Setup Input/Output Options')
# 	parser.add_argument('--config_option', type=str, dest='config_option', default='',
# 						help='a string to hold the I/O configuration for the GUI, e.g., [0, 1, 1, 0, 0, 1]')
# 	parser.add_argument('--config_filename', type=str, dest='config_filename', default='',
# 						help='a string to hold the config filename containing the selected I/O options, e.g., default-config.txt')
# 	args = parser.parse_args()
#
# 	config_option = args.config_option
# 	config_filename = args.config_filename
# 	# convert config_option string to list
# 	config_option = config_option.split(', ')
# 	config_option = list(map(int, config_option))

y_multiplier_integer = GUI_util.y_multiplier_integer

if config_option[3] != 0: # secondary INPUT directory
	GUI_size = '1100x320'
	increment = 2
	help_increment = 3
	y_multiplier_integer = y_multiplier_integer + 1
else:
	GUI_size = '1100x280'
	increment = 1
	help_increment=2

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

# GUI CHANGES add following lines to every special GUI
# +3 is the number of lines starting at 1 of IO widgets
y_multiplier_integer = GUI_util.y_multiplier_integer + increment

window = GUI_util.window
config_input_output_options = GUI_util.config_input_output_options
# config_filename = GUI_util.config_filename
# inputFilename = GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_options, config_filename, False)

TIPS_lookup = {'No TIPS available':''}
TIPS_options='No TIPS available'

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
		GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step, "Help",
									  "Please, select the main INPUT directory of the TXT files to be analyzed." + GUI_IO_util.msg_openExplorer)

	# INPUT secondary directory
	if config_option[3]!=0:
		GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 2, "Help",
									  "Please, select the secondary INPUT directory of the TXT files to be analyzed." + GUI_IO_util.msg_openExplorer)

	# OUTPUT  directory
	GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * help_increment, "Help",
								  GUI_IO_util.msg_outputDirectory)

help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), GUI_IO_util.get_basic_y_coordinate(),
			 GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message = "This Python 3 script provides a front-end GUI (Graphical User Interface) for setting up the Input/Output information necessary to run the NLP-Suite scripts, namely the INPUT files to be used - a single file or a set of files in a directory - and the OUTPUT directory where the files produced by the NLP Suite scripts will be saved - txt, csv, html, kml, jpg.\n\nThe selected I/O configuration will be saved in config files in the config subdirectory. The default-config.txt file will be used for all NLP Suite scripts unless a different configuraton is selected for a specific script by selecting the 'Alternative I/O configuation'. When opening the GUI with the option 'Alternative I/O configuation' a configuration file will be saved under the config subdirectory with the specif name of the calling script (e.g., Stanford-CoreNLP-config.txt).\n\nWhen clicking the CLOSE button, the script will give the option to save the currently selected configuration IF different from the previously saved configuration."
readMe_command = lambda: GUI_IO_util.readme_button(window, GUI_IO_util.get_help_button_x_coordinate(),
												   GUI_IO_util.get_basic_y_coordinate(), "Help", readMe_message)
GUI_util.GUI_bottom(config_input_output_options, y_multiplier_integer, readMe_command, TIPS_lookup, TIPS_options,False)

GUI_util.window.mainloop()

