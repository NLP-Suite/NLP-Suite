# written by Roberto Franzosi October 2019, edited Spring 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_merger_main.py",['os','tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk

import GUI_IO_util
import IO_user_interface_util
import file_merger_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(input_main_dir_path, output_dir_path,
    openOutputFiles,
    createCharts,
    merge_processSubdir,
    merge_saveFilenameInOutput,
    merge_embed_filenames_inStringSeparators,
    merge_separator_entry_begin,
    merge_separator_entry_end,
    merge_embed_subdir_name,
    merge_character_separator):

    if IO_libraries_util.check_inputPythonJavaProgramFile('file_merger_util.py')==False:
        return

    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', "Started running 'File Merger' at",
												 True, '', True,'',True)

    file_merger_util.file_merger(GUI_util.window,
                                input_main_dir_path,
                                output_dir_path,
                                openOutputFiles,
                                merge_processSubdir,
                                merge_saveFilenameInOutput,
                                merge_embed_filenames_inStringSeparators,
                                merge_separator_entry_begin,
                                merge_separator_entry_end,
                                merge_embed_subdir_name,
                                merge_character_separator)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, "Analysis end", "Finished running 'File Merger' at", True, '', True, startTime, True)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
							GUI_util.create_chart_output_checkbox.get(),
							GUI_util.charts_dropdown_field.get(),
                            merge_subdir_var.get(),
                            merge_save_fileName_var.get(),
                            merge_embed_filenames_inStringSeparators_var.get(),
                            merge_separator_entry_begin_var.get(),
                            merge_separator_entry_end_var.get(),
                            merge_embed_subdir_name_var.get(),
                            merge_character_separator_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_width=GUI_IO_util.get_GUI_width(3)
GUI_height=360 # height of GUI with full I/O display

if IO_setup_display_brief:
    GUI_height = GUI_height - 40
    y_multiplier_integer = GUI_util.y_multiplier_integer  # IO BRIEF display
    increment=0 # used in the display of HELP messages
else: # full display
    # GUI CHANGES add following lines to every special GUI
    # +3 is the number of lines starting at 1 of IO widgets
    # y_multiplier_integer=GUI_util.y_multiplier_integer+2
    y_multiplier_integer = GUI_util.y_multiplier_integer + 1  # IO FULL display
    increment=1

GUI_size = str(GUI_width) + 'x' + str(GUI_height)

GUI_label='Graphical User Interface (GUI) for File Merger'
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = scriptName.replace('main.py', 'config.csv')

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
config_input_output_numeric_options=[0,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
input_main_dir_path =GUI_util.input_main_dir_path
output_dir_path =GUI_util.output_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

merge_subdir_var=tk.IntVar()
merge_embed_subdir_name_var=tk.IntVar()
merge_character_separator_var=tk.StringVar()
merge_save_fileName_var=tk.IntVar()
merge_embed_filenames_inStringSeparators_var=tk.IntVar()
merge_separator_entry_begin_var=tk.StringVar()
merge_separator_entry_end_var=tk.StringVar()

def clear(e):
	GUI_util.clear("Escape")
window.bind("<Escape>", clear)


#setup GUI widgets

# MERGE ________________________________________________________

# merge_files_lb = tk.Label(window, text='Merge files',font=("Courier", 12, "bold"))
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,merge_files_lb)

merge_save_fileName_var.set(0)
merge_save_fileName_checkbox = tk.Checkbutton(window, text='Save filename in output', variable=merge_save_fileName_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,merge_save_fileName_checkbox,True)

merge_embed_filenames_inStringSeparators_var.set(0)
merge_embed_filenames_inStringSeparators_checkbox = tk.Checkbutton(window, text='Embed filename in separators', variable=merge_embed_filenames_inStringSeparators_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+220,y_multiplier_integer,merge_embed_filenames_inStringSeparators_checkbox,True)

merge_separator_entry_begin = tk.Entry(window,width=10,textvariable=merge_separator_entry_begin_var)
merge_separator_entry_end = tk.Entry(window,width=10,textvariable=merge_separator_entry_end_var)

def display_merge_separator(y_multiplier_integer):
	merge_separator_entry_begin_var.set("<@#")
	merge_separator_entry_begin.configure(state="disabled")
	y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+440,y_multiplier_integer,merge_separator_entry_begin,True)

	merge_separator_entry_end_var.set("#@>")
	merge_separator_entry_end.configure(state="disabled")
	y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+520,y_multiplier_integer,merge_separator_entry_end,True)
display_merge_separator(y_multiplier_integer)

merge_embed_subdir_name_var.set(0)
merge_embed_subdir_name_checkbox = tk.Checkbutton(window, state='disabled', text='Embed subdirname', variable=merge_embed_subdir_name_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+610,y_multiplier_integer,merge_embed_subdir_name_checkbox,True)

character_separator_lb = tk.Label(window, text='Character separator')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+770,y_multiplier_integer,character_separator_lb,True)

merge_character_separator_var.set("__")
merge_character_separator = tk.Entry(window,width=5,state='disabled',textvariable=merge_character_separator_var)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+900,y_multiplier_integer,merge_character_separator)

merge_subdir_var.set(0)
merge_subdir_checkbox = tk.Checkbutton(window, text='Process subdirectories', variable=merge_subdir_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,merge_subdir_checkbox)

def activate_allOptions(*args):
	merge_save_fileName_checkbox.configure(state='normal')
	merge_subdir_checkbox.configure(state="normal")
	merge_embed_filenames_inStringSeparators_checkbox.configure(state="disabled")
	merge_separator_entry_begin.configure(state="disabled")
	merge_separator_entry_end.configure(state="disabled")
	merge_embed_subdir_name_checkbox.configure(state='disabled')
	merge_character_separator.configure(state='disabled')
	if merge_save_fileName_var.get()==True:
		merge_embed_filenames_inStringSeparators_checkbox.configure(state="normal")
		if merge_embed_filenames_inStringSeparators_var.get()==True:
			merge_separator_entry_begin.configure(state="normal")
			merge_separator_entry_end.configure(state="normal")
		if merge_subdir_var.get()==True:
			merge_embed_subdir_name_checkbox.configure(state='normal')
		if merge_embed_subdir_name_var.get()==True:
			merge_character_separator.configure(state='normal')
	else:
		merge_embed_filenames_inStringSeparators_var.set(0)


merge_embed_filenames_inStringSeparators_var.trace('w',activate_allOptions)
merge_embed_filenames_inStringSeparators_var.trace('w',activate_allOptions)
merge_embed_subdir_name_var.trace('w',activate_allOptions)
merge_save_fileName_var.trace('w',activate_allOptions)
merge_embed_subdir_name_var.trace('w',activate_allOptions)
merge_subdir_var.trace('w',activate_allOptions)

activate_allOptions()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'File manager':'TIPS_NLP_File manager.pdf','File handling in NLP Suite': "TIPS_NLP_File handling in NLP Suite.pdf",'Filename checker':'TIPS_NLP_Filename checker.pdf','Filename matcher':'TIPS_NLP_Filename matcher.pdf','File classifier (By date)':'TIPS_NLP_File classifier (By date).pdf','File classifier (By NER)':'TIPS_NLP_File classifier (By NER).pdf','File content checker & converter':'TIPS_NLP_File checker & converter.pdf','Text encoding (utf-8)':'TIPS_NLP_Text encoding (utf-8).pdf','Spelling checker':'TIPS_NLP_Spelling checker.pdf','File merger':'TIPS_NLP_File merger.pdf','File splitter':'TIPS_NLP_File splitter.pdf'}
TIPS_options= 'File merger','File splitter','File handling in NLP Suite','File manager', 'Filename checker','Filename matcher', 'File classifier (By date)','File classifier (By NER)','File content checker & converter','Text encoding (utf-8)','Spelling checker'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
	clearOptions="\n\nTo clear a previously selected option for any of the tools, click on the appropriate dropdown menu and press ESCape twice."
	if not IO_setup_display_brief:
		y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,GUI_IO_util.msg_anyData)
		y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,GUI_IO_util.msg_outputDirectory)
	else:
		y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
									  GUI_IO_util.msg_IO_setup)

	y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox to save the filenames in the merged output file.\n\nTo make it easy to find files in the merged output, embed the filenames in unique start/end strings. Filenames will be saved with their path. WHEN SELECTING THE OPTION OF EMBEDDING THE SUBDIRECTORY NAME IN THE FILENAME, THE FILENAME WILL BE SAVED WITHOUT PATH.\n\nThe option of saving the subdirectory name when saving the file is only available when processing subdirectories.")
	y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox to process files in subdirectories.\n\nWhen processing subdirectories, if the filename is saved in the merged output, the filename will be saved without a path. You will, however, have the option to save the filename with the suffix of the subdirectory name.")
	y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
	return y_multiplier_integer - 1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="This Python 3 script merges txt files into a single txt file with a number of processing options."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()

