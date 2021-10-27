# Written by Roberto Franzosi

# Modified by Cynthia Dong and Elaine Dong (Oct 24 2019; Feb 6 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "Social Science Research",
										  ['os', 'tkinter', 'subprocess', 'csv']) == False:
	sys.exit(0)

import os
import tkinter as tk
from tkinter import filedialog
import subprocess
from subprocess import call
import tkinter.messagebox as mb
from sys import platform
import csv

import IO_files_util
import GUI_IO_util
import IO_user_interface_util
import lib_util
import Excel_util
import reminders_util
import file_summary_checker_util
import file_find_non_related_documents_util

# RUN section ______________________________________________________________________________________________________________________________________________________


def check_filename(output_dir_path):
	if IO_libraries_util.inputProgramFileCheck('file_checker_converter_cleaner_main.py') == False:
		return
	if platform == "win32":
		subprocess.call("python file_manager_main.py", shell=True)
	# linux # OS X
	elif platform == "linux" or platform == "linux2" or platform == "darwin":
		subprocess.call("sudo Python file_manager_main.py", shell=True)
	# files are opened in the file_filename_checker_main GUI


def character(output_dir_path):
	if IO_libraries_util.inputProgramFileCheck('WordNet_main.py') == False:
		return
	if platform == "win32":
		subprocess.call("python WordNet_main.py character", shell=True)
	# linux # OS X
	elif platform == "linux" or platform == "linux2" or platform == "darwin":
		subprocess.call("sudo Python WordNet_main.py character", shell=True)
	# files are opened in the WordNet GUI


def find_character_home(output_dir_path):
	if IO_libraries_util.inputProgramFileCheck('file_classifier_main.py') == False:
		return
	if platform == "win32":
		subprocess.call("python file_classifier_main.py character home", shell=True)
	# linux # OS X
	elif platform == "linux" or platform == "linux2" or platform == "darwin":
		subprocess.call("sudo Python file_classifier_main.py character home", shell=True)
	# files are opened in the file_classifier_main.py GUI

def missing_character(CoreNLPdir, input_main_dir_path, input_secondary_dir_path, output_dir_path, openOutputFiles, createExcelCharts, checkNER):
	if IO_libraries_util.inputProgramFileCheck('file_summary_checker_util.py') == False:
		return
	Excel_outputFile=file_summary_checker_util.main(CoreNLPdir, input_main_dir_path,input_secondary_dir_path,output_dir_path,openOutputFiles, createExcelCharts, checkNER)
	if Excel_outputFile!="":
		filesToOpen.extend(Excel_outputFile)

def intruder(CoreNLPdir,input_main_dir_path, output_dir_path, openOutputFiles, createExcelCharts, similarityIndex_Intruder_var):
	if IO_libraries_util.inputProgramFileCheck('file_find_non_related_documents_util.py') == False:
		return
	startTime=IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running INTRUDER at', True,
									   'You can follow INTRUDER in command line.')
	# Windows...
	outputFiles=file_find_non_related_documents_util.main(CoreNLPdir, input_main_dir_path, output_dir_path, openOutputFiles, createExcelCharts, similarityIndex_Intruder_var)

	if outputFiles!='':
		filesToOpen.extend(outputFiles)
	# Nothing to plot; only one line in the output csv file
	IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running INTRUDER at', True, '', True, startTime)


def ancestor(input_main_dir_path, output_dir_path):
	if IO_libraries_util.inputProgramFileCheck('WordNet_main.py') == False:
		return
	if platform == "win32":
		subprocess.call("python WordNet.py ancestor", shell=True)
	# linux # OS X
	elif platform == "linux" or platform == "linux2" or platform == "darwin":
		subprocess.call("sudo Python WordNet_main.py ancestor", shell=True)
	# files are opened in the WordNet GUI


"""
This function read in Lucene_document_classes_freq.csv and group articles from the same newspaper together.
The result csv file showcase for every newspaper, the distribution of plagiarism score.

Key: The way we compute distribution of plagiarism score for newspaper is by adding up all scores for the same 
newspaper and take the average
"""


def group_newspaper(document_class_csv, output_filename):
	newspaper_frequency_classes = {}  # accumulate frequency for different classes for each newspaper
	newspaper_frequency = {}  # count the # of times this newspaper occurs
	newspaper_names = []  # list of unique newspaper names
	with open(document_class_csv) as csv_file:
		csv_lines = csv.reader(csv_file)
		next(csv_lines)  # skip header
		for row in csv_lines:
			# process article name
			if ("_" in row[0]):
				newspaper = row[0].split("_")[0]
			else:
				newspaper = row[0]
			# count newspaper frequency and accumulates count for each newspaper based on classes
			if newspaper in newspaper_frequency_classes:
				newspaper_frequency[newspaper] += 1
				for i in range(1, 11):
					newspaper_frequency_classes[newspaper][i - 1] += int(row[i])
			else:
				newspaper_frequency[newspaper] = 1
				newspaper_names.append(newspaper)
				newspaper_frequency_classes[newspaper] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # initialize as 10 zeros
				for i in range(1, 11):
					newspaper_frequency_classes[newspaper][i - 1] += int(row[i])
	newspaper_names.sort()  # sort by newspaper name
	# write to output csv file
	with open(output_filename, "w", newline='', encoding='utf-8', errors='ignore') as f:
		writer = csv.writer(f)
		# write header
		header = ["Newspaper Name", "0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50-60%", "60-70%", "70-80%",
				  "80-90%", "90-100%"]
		writer.writerow(header)
		for newspaper_name in newspaper_names:
			to_write = [newspaper_name]
			frequency_count = newspaper_frequency_classes[newspaper_name]
			for i in range(0, 10):
				to_write.append(int(frequency_count[i] / newspaper_frequency[newspaper_name]))
			writer.writerow(to_write)


def plagiarist(input_main_dir_path, output_dir_path, open_csv_output_checkbox, createExcelCharts,
			   similarityIndex_Plagiarist_var, fileName_embeds_date, DateFormat, DatePosition, DateCharacterSeparator):
	if similarityIndex_Plagiarist_var < .8:
		mb.showwarning(title='Similarity Index warning', message="The level of similarity was set at " + str(
			similarityIndex_Plagiarist_var) + ".\n\nCAVEAT! The default threshold for similarity is normally set at 80%.\n\nBe aware that lowering the default level may result in too many documents wrongly classified as similar; conversely, raising the level may exclude too many documents.")

	if IO_libraries_util.inputProgramFileCheck('Lucene.jar') == False:
		return
	if len(DateCharacterSeparator) == 0:
		tk.messagebox.showinfo("Plagiarist", "DateCharacterSeparator")
		return
	lib_stopwords = lib_util.check_lib_stopwords()

	if len(lib_stopwords) != 0:
		startTime=IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running PLAGIARIST at',
										   True)
		errorFound, error_code, system_output = IO_libraries_util.check_java_installation('Lucene')
		if errorFound:
			return
		subprocess.call(['java', '-jar', 'Lucene.jar', '-inputDir', input_main_dir_path + os.sep, '-outputDir',
						 output_dir_path + os.sep
							, '-stopword', lib_stopwords, '-embedsDate', str(fileName_embeds_date), '-dateFormat',
						 DateFormat
							, '-datePos', str(DatePosition), '-itemsDelim', DateCharacterSeparator, '-similarityIndex',
						 str(similarityIndex_Plagiarist_var)])
		filesToOpen.append(output_dir_path + os.sep + "document_duplicates.txt")

		outputFilenameCSV_1 = output_dir_path + os.sep + "Lucene_classes_freq.csv"
		filesToOpen.append(outputFilenameCSV_1)

		if fileName_embeds_date:
			outputFilenameCSV_2 = output_dir_path + os.sep + "Lucene_classes_time_freq.csv"
			filesToOpen.append(outputFilenameCSV_2)

		outputFilenameCSV_3 = output_dir_path + os.sep + "Lucene_document_instance_classes_freq.csv"
		filesToOpen.append(outputFilenameCSV_3)

		outputFilenameCSV_4 = output_dir_path + os.sep + "Lucene_Document_classes_freq.csv"
		group_newspaper(outputFilenameCSV_3, outputFilenameCSV_4)
		filesToOpen.append(outputFilenameCSV_4)

	if createExcelCharts:
		# Lucene_classes_freq.csv; outputFilenameCSV_1
		outputDir=output_dir_path
		inputFilename = outputFilenameCSV_1
		columns_to_be_plotted = [[0, 1]]
		hover_label = ['List of Documents in Category']
		Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
												  outputFileLabel='SSR_plagiar',
												  chart_type_list=["bar"],
												  chart_title='Frequency of Plagiarism by Classes of % Duplication',
												  column_xAxis_label_var='Classes of percentage duplication',
												  hover_info_column_list=hover_label)
		if Excel_outputFilename != "":
			filesToOpen.append(Excel_outputFilename)

		# Plot Lucene_classes_time_freq.csv line plot (temporal plot); outputFilenameCSV_2
		if fileName_embeds_date:
			# columns_to_be_plotted = [[0,1], [0,2], [0,3], [0,4], [0,5], [0,6],[0,7], [0,8], [0,9],[0,10]]
			# hover_label=['','','','','','','','','','']
			inputFilename = outputFilenameCSV_2
			columns_to_be_plotted = [[0, 1], [0, 2], [0, 3]]
			hover_label = ['', '', '']
			Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
													  outputFileLabel='SSR_plagiar',
													  chart_type_list=["line"],
													  chart_title='Frequency of Plagiarism by Year',
													  column_xAxis_label_var='Year',
													  hover_info_column_list=hover_label)
			if Excel_outputFilename != "":
				filesToOpen.append(Excel_outputFilename)

		# No plot for Lucene_document_classes_freq.csv
		#   because it could potentially have thousands of documents
		# 	inputFilename = outputFilenameCSV_3


		# Lucene_Document_classes_freq.csv; outputFilenameCSV_4
		columns_to_be_plotted = [[0, 1],[0, 2],[0, 3]]
		hover_label = ['']
		inputFilename = outputFilenameCSV_4
		Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
												  outputFileLabel='SSR_plagiar',
												  chart_type_list=["bar"],
												  chart_title='Frequency of Plagiarism by Document Name & Classes',
												  column_xAxis_label_var='',
												  hover_info_column_list=hover_label)
		if Excel_outputFilename != "":
			filesToOpen.append(Excel_outputFilename)

	IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running PLAGIARIST at', True, '', True, startTime)

def Levenshtein():
	if IO_libraries_util.inputProgramFileCheck('file_spell_checker_main.py') == False:
		return
	if platform == "win32":
		subprocess.call("python file_spell_checker_main.py", shell=True)
	# linux # OS X
	elif platform == "linux" or platform == "linux2" or platform == "darwin":
		subprocess.call("sudo Python file_spell_checker_main.py", shell=True)
	# files are opened in the spell_checker_main


def run(input_main_dir_path, input_secondary_dir_path, output_dir_path, openOutputFiles, createExcelCharts,
		fileName_embeds_date, DateFormat, DatePosition, DateCharacterSeparator,
		check_filename_var, character_var, character_home_var, missing_character_var, NER_var, intruder_var,
		similarityIndex_Intruder_var, ancestor_var, nouns_verbs,
		plagiarist_var, similarityIndex_Plagiarist_var, Levenshtein_var):
	global filesToOpen
	filesToOpen = []
	# check that the CoreNLPdir as been setup
	CoreNLPdir, missing_external_software = IO_libraries_util.get_external_software_dir('social_science_research', 'Stanford CoreNLP')
	if CoreNLPdir==None:
		return filesToOpen

	if (check_filename_var == False and character_var == False and character_home_var == False and missing_character_var == False and intruder_var == False and Levenshtein_var==False and ancestor_var == False and plagiarist_var == False):
		mb.showwarning(title='No options selected',
					   message='No options have been selected.\n\nPlease, select an option and try again.')
		return

	if check_filename_var == True:
		check_filename(output_dir_path)
	elif character_var == True:
		character(output_dir_path)
	elif character_home_var == True:
		find_character_home(output_dir_path)
	elif missing_character_var == True:
		missing_character(CoreNLPdir, input_main_dir_path, input_secondary_dir_path, output_dir_path, openOutputFiles, createExcelCharts, NER_var)
	elif intruder_var == True:
		intruder(CoreNLPdir, input_main_dir_path, output_dir_path, openOutputFiles, createExcelCharts, similarityIndex_Intruder_var)
	elif ancestor_var == True:
		ancestor(input_main_dir_path, output_dir_path)
	elif plagiarist_var == True:
		plagiarist(input_main_dir_path, output_dir_path, openOutputFiles, createExcelCharts,
				   similarityIndex_Plagiarist_var, fileName_embeds_date, DateFormat, DatePosition,
				   DateCharacterSeparator)
	elif Levenshtein_var == True:
		Levenshtein()
	if openOutputFiles == True:
		IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)


# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command = lambda: run(GUI_util.input_main_dir_path.get(),
								 GUI_util.input_secondary_dir_path.get(),
								 GUI_util.output_dir_path.get(),
								 GUI_util.open_csv_output_checkbox.get(),
								 GUI_util.create_Excel_chart_output_checkbox.get(),
								 fileName_embeds_date.get(),
								 date_format.get(),
								 date_position_var.get(),
								 date_separator_var.get(),
								 check_filename_var.get(),
								 character_var.get(),
								 character_home_var.get(),
								 missing_character_var.get(),
								 NER_var.get(),
								 intruder_var.get(),
								 similarityIndex_Intruder_var.get(),
								 ancestor_var.get(),
								 ancestor_menu_var.get(),
								 plagiarist_var.get(),
								 similarityIndex_Plagiarist_var.get(),
								 Levenshtein_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=False
GUI_width=1100
GUI_height=640 # height of GUI with full I/O display

if IO_setup_display_brief:
    GUI_height = GUI_height - 80
    y_multiplier_integer = GUI_util.y_multiplier_integer  # IO BRIEF display
    increment=0 # used in the display of HELP messages
else: # full display
    # GUI CHANGES add following lines to every special GUI
    # +3 is the number of lines starting at 1 of IO widgets
    # y_multiplier_integer=GUI_util.y_multiplier_integer+2
    y_multiplier_integer = GUI_util.y_multiplier_integer + 2  # IO FULL display
    increment=2

GUI_size = str(GUI_width) + 'x' + str(GUI_height)

GUI_label = 'Graphical User Interface (GUI) for Various Tools for Social Science Research'
config_filename = 'social-science-research-config.txt'
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
config_option = [0, 0, 1, 1, 0, 1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

window = GUI_util.window
config_input_output_options = GUI_util.config_input_output_options
config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_options, config_filename,IO_setup_display_brief)

check_filename_var = tk.IntVar()
character_var = tk.IntVar()
missing_character_var = tk.IntVar()
character_home_var = tk.IntVar()
NER_var = tk.IntVar()
intruder_var = tk.IntVar()
similarityIndex_Intruder_var = tk.DoubleVar()
plagiarist_var = tk.IntVar()
similarityIndex_Plagiarist_var = tk.DoubleVar()
Levenshtein_var = tk.IntVar()

fileName_embeds_date = tk.IntVar()

date_format = tk.StringVar()
date_separator_var = tk.StringVar()
date_position_var = tk.IntVar()

keyWord_var = tk.StringVar()
keyWord_entry_var = tk.StringVar()
ancestor_var = tk.IntVar()
ancestor_menu_var = tk.StringVar()
selectedFile_var = tk.StringVar()  # the noun/verb file to be used for ancestor

fileName_embeds_date_checkbox = tk.Checkbutton(window, text='Filename embeds date', state="disabled",
											   variable=fileName_embeds_date, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
											   fileName_embeds_date_checkbox, True)

date_format_lb = tk.Label(window, text='Date format ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
											   date_format_lb, True)
date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy', 'yyyy-mm-dd', 'yyyy-dd-mm', 'yyyy-mm',
								 'yyyy')
date_format_menu.configure(width=10, state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 90, y_multiplier_integer,
											   date_format_menu, True)

date_separator_var_lb = tk.Label(window, text='Date character separator ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 210, y_multiplier_integer,
											   date_separator_var_lb, True)
date_separator_var_menu = tk.Entry(window, textvariable=date_separator_var)
date_separator_var_menu.configure(width=2, state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 360, y_multiplier_integer,
											   date_separator_var_menu, True)

date_position_var_menu_lb = tk.Label(window, text='Date position ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 390, y_multiplier_integer,
											   date_position_var_menu_lb, True)
date_position_var_menu = tk.OptionMenu(window, date_position_var, 1, 2, 3, 4, 5)
date_position_var_menu.configure(width=4, state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 490, y_multiplier_integer,
											   date_position_var_menu)

check_filename_var.set(0)
check_filename_checkbox = tk.Checkbutton(window, text='Check the filenames well-formedness',
										 variable=check_filename_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
											   check_filename_checkbox)

character_var.set(0)
character_checkbox = tk.Checkbutton(window, text='Find the character & the ancestor (via WordNet)',
									variable=character_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
											   character_checkbox)

missing_character_var.set(0)
missing_character_checkbox = tk.Checkbutton(window, text='Find the missing character', variable=missing_character_var,
											onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
											   missing_character_checkbox, True)

NER_var.set(0)
NER_checkbox = tk.Checkbutton(window, text='NER (Named Entity Recognition) ', state="disabled", variable=NER_var,
							  onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
											   NER_checkbox)

Levenshtein_var.set(0)
Levenshtein_checkbox = tk.Checkbutton(window, text="Check the character's name tag", variable=Levenshtein_var,
									  onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
											   Levenshtein_checkbox)

character_home_var.set(0)
character_home_checkbox = tk.Checkbutton(window, text="Find the character's home", variable=character_home_var,
										 onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
											   character_home_checkbox)

intruder_var.set(0)
intruder_checkbox = tk.Checkbutton(window, text='Find the intruder', variable=intruder_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
											   intruder_checkbox, True)

similarityIndex_Intruder_var.set(0.2)
similarityIndex_Intruder_menu_lb = tk.Label(window, text='Relativity index threshold')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
											   similarityIndex_Intruder_menu_lb, True)
similarityIndex_Intruder_menu = tk.OptionMenu(window, similarityIndex_Intruder_var, .1, .15, .2, .25, .3, .35, .4, .45,
											  .5, .45, .5, .55, .6, .65, .7, .75, .8, .85, .9)
similarityIndex_Intruder_menu.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 170, y_multiplier_integer,
											   similarityIndex_Intruder_menu)

plagiarist_var.set(0)
plagiarist_checkbox = tk.Checkbutton(window, text='Find the plagiarist', variable=plagiarist_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
											   plagiarist_checkbox, True)

similarityIndex_Plagiarist_var.set(.8)
similarityIndex_Plagiarist_menu_lb = tk.Label(window, text='Similarity index ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
											   similarityIndex_Plagiarist_menu_lb, True)
similarityIndex_Plagiarist_menu = tk.OptionMenu(window, similarityIndex_Plagiarist_var, .4, .45, .5, .45, .5, .55, .6,
												.65, .7, .75, .8, .85, .9)
similarityIndex_Plagiarist_menu.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 170, y_multiplier_integer,
											   similarityIndex_Plagiarist_menu)


def clear(e):
	similarityIndex_Intruder_var.set(0.2)
	similarityIndex_Plagiarist_var.set(0.2)
	GUI_util.clear("Escape")


window.bind("<Escape>", clear)


def activate_dateOptions(*args):
	if fileName_embeds_date.get() == False:
		date_format_menu.configure(width=10, state="disabled")
		date_separator_var_menu.configure(width=2, state="disabled")
		date_position_var_menu.configure(width=4, state="disabled")
	else:
		date_format_menu.configure(width=10, state="normal")
		date_separator_var_menu.configure(width=2, state="normal")
		date_position_var_menu.configure(width=4, state="normal")


fileName_embeds_date.trace('w', activate_dateOptions)


def activate_fileName_wellFormedness(*args):
	if check_filename_var.get() == False:
		fileName_embeds_date_checkbox.configure(state="disabled")
		NER_checkbox.configure(state="disabled")
		NER_var.set(0)
		similarityIndex_Intruder_menu.configure(state="disabled")
		character_home_checkbox.configure(state="normal")
		missing_character_checkbox.configure(state="normal")
		Levenshtein_checkbox.configure(state='normal')
		character_checkbox.configure(state="normal")
		# character_home_checkbox.configure(state="normal")
		intruder_checkbox.configure(state="normal")
		plagiarist_checkbox.configure(state="normal")
	else:
		reminders_util.checkReminder(config_filename, ["Filename checker"], '', True)
		fileName_embeds_date_checkbox.configure(state="normal")
		NER_checkbox.configure(state="disabled")
		NER_var.set(0)
		similarityIndex_Intruder_menu.configure(state="disabled")
		character_home_checkbox.configure(state="disabled")
		missing_character_checkbox.configure(state="disabled")
		Levenshtein_checkbox.configure(state='disabled')
		character_checkbox.configure(state="disabled")
		# character_home_checkbox.configure(state="disabled")
		intruder_checkbox.configure(state="disabled")
		plagiarist_checkbox.configure(state="disabled")


check_filename_var.trace('w', activate_fileName_wellFormedness)


def activate_characterHomeOptions(*args):
	if character_home_var.get() == False:
		similarityIndex_Intruder_menu.configure(state="disabled")
		check_filename_checkbox.configure(state='normal')
		missing_character_checkbox.configure(state="normal")
		Levenshtein_checkbox.configure(state='normal')
		character_checkbox.configure(state="normal")
		# character_home_checkbox.configure(state="normal")
		intruder_checkbox.configure(state="normal")
		plagiarist_checkbox.configure(state="normal")
		NER_checkbox.configure(state="disabled")
		NER_var.set(0)
	else:
		similarityIndex_Intruder_menu.configure(state="disabled")
		check_filename_checkbox.configure(state='disabled')
		missing_character_checkbox.configure(state="disabled")
		Levenshtein_checkbox.configure(state='disabled')
		character_checkbox.configure(state="disabled")
		# character_home_checkbox.configure(state="disabled")
		intruder_checkbox.configure(state="disabled")
		plagiarist_checkbox.configure(state="disabled")
		NER_checkbox.configure(state="disabled")
		NER_var.set(0)


character_home_var.trace('w', activate_characterHomeOptions)


def activate_CharacterOptions(*args):
	if character_var.get() == False:
		check_filename_checkbox.configure(state='normal')
		missing_character_checkbox.configure(state="normal")
		Levenshtein_checkbox.configure(state='normal')
		character_home_checkbox.configure(state="normal")
		intruder_checkbox.configure(state="normal")
		plagiarist_checkbox.configure(state="normal")
		NER_checkbox.configure(state="disabled")
		NER_var.set(0)
		similarityIndex_Intruder_menu.configure(state="disabled")
	else:
		check_filename_checkbox.configure(state='disabled')
		missing_character_checkbox.configure(state="disabled")
		Levenshtein_checkbox.configure(state='disabled')
		character_home_checkbox.configure(state="disabled")
		intruder_checkbox.configure(state="disabled")
		plagiarist_checkbox.configure(state="disabled")
		NER_checkbox.configure(state="disabled")
		NER_var.set(0)
		similarityIndex_Intruder_menu.configure(state="disabled")


character_var.trace('w', activate_CharacterOptions)


def activate_missingCharacterOptions(*args):
	if missing_character_var.get() == False:
		check_filename_checkbox.configure(state='normal')
		character_checkbox.configure(state="normal")
		character_home_checkbox.configure(state="normal")
		Levenshtein_checkbox.configure(state='normal')
		intruder_checkbox.configure(state="normal")
		plagiarist_checkbox.configure(state="normal")
		NER_checkbox.configure(state="disabled")
		NER_var.set(0)
		similarityIndex_Intruder_menu.configure(state="disabled")
	else:
		similarityIndex_Intruder_menu.configure(state="normal")
		NER_checkbox.configure(state="normal")
		check_filename_checkbox.configure(state='disabled')
		character_checkbox.configure(state="disabled")
		character_home_checkbox.configure(state="disabled")
		Levenshtein_checkbox.configure(state='disabled')
		intruder_checkbox.configure(state="disabled")
		plagiarist_checkbox.configure(state="disabled")


missing_character_var.trace('w', activate_missingCharacterOptions)


def activate_LevenshteinOptions(*args):
	if Levenshtein_var.get() == False:
		check_filename_checkbox.configure(state='normal')
		similarityIndex_Intruder_menu.configure(state="disabled")
		character_home_checkbox.configure(state="normal")
		missing_character_checkbox.configure(state="normal")
		character_checkbox.configure(state="normal")
		# character_home_checkbox.configure(state="normal")
		intruder_checkbox.configure(state="normal")
		plagiarist_checkbox.configure(state="normal")
		NER_checkbox.configure(state="disabled")
		NER_var.set(0)
	else:
		check_filename_checkbox.configure(state='disabled')
		NER_checkbox.configure(state="disabled")
		NER_var.set(0)
		similarityIndex_Intruder_menu.configure(state="disabled")
		character_home_checkbox.configure(state="disabled")
		missing_character_checkbox.configure(state="disabled")
		character_checkbox.configure(state="disabled")
		# character_home_checkbox.configure(state="disabled")
		intruder_checkbox.configure(state="disabled")
		plagiarist_checkbox.configure(state="disabled")


Levenshtein_var.trace('w', activate_LevenshteinOptions)


def activate_intruderOptions(*args):
	if intruder_var.get() == False:
		similarityIndex_Intruder_menu.configure(state="disabled")
		check_filename_checkbox.configure(state='normal')
		missing_character_checkbox.configure(state="normal")
		Levenshtein_checkbox.configure(state='normal')
		character_checkbox.configure(state="normal")
		character_home_checkbox.configure(state="normal")
		plagiarist_checkbox.configure(state="normal")
		NER_checkbox.configure(state="disabled")
		NER_var.set(0)
	else:
		similarityIndex_Intruder_menu.configure(state="normal")
		check_filename_checkbox.configure(state='disabled')
		missing_character_checkbox.configure(state="disabled")
		Levenshtein_checkbox.configure(state='disabled')
		character_checkbox.configure(state="disabled")
		character_home_checkbox.configure(state="disabled")
		plagiarist_checkbox.configure(state="disabled")
		NER_checkbox.configure(state="disabled")
		NER_var.set(0)


intruder_var.trace('w', activate_intruderOptions)


def activate_filenameEmbedsDate(*args):
	if plagiarist_var.get() == False:
		similarityIndex_Plagiarist_menu.configure(state="disabled")
		similarityIndex_Plagiarist_menu.configure(state="disabled")
		check_filename_checkbox.configure(state='normal')
		character_checkbox.configure(state="normal")
		character_home_checkbox.configure(state="normal")
		missing_character_checkbox.configure(state="normal")
		Levenshtein_checkbox.configure(state='normal')
		intruder_checkbox.configure(state="normal")
		fileName_embeds_date_checkbox.configure(state="disabled")
		fileName_embeds_date.set(0)
	else:
		reminders_util.checkReminder(config_filename, ["Plagiarist"], '', True)
		similarityIndex_Plagiarist_menu.configure(state="normal")
		check_filename_checkbox.configure(state='disabled')
		character_checkbox.configure(state="disabled")
		character_home_checkbox.configure(state="disabled")
		Levenshtein_checkbox.configure(state='disabled')
		missing_character_checkbox.configure(state="disabled")
		intruder_checkbox.configure(state="disabled")
		fileName_embeds_date_checkbox.configure(state="normal")


plagiarist_var.trace('w', activate_filenameEmbedsDate)


# populates date field based on tkinter vars defined in the specific gui (dateVar, formatVar, and positionVar)
# returns the separator and the position
def plagiaristOptions(dateFormatField, dateSeparatorField, datePositionField):
	dateFormatField.set('mm-dd-yyyy')
	dateSeparatorField.set('_')
	datePositionField.set(2)


# return dateFormat, dateSeparator, datePosition
plagiaristOptions(date_format, date_separator_var, date_position_var)

# y_multiplier_integer = y_multiplier_integer+1

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Check the character\'s name tag': 'TIPS_NLP_Word similarity (Levenshtein distance).pdf',
			   'Filename well-formedness': 'TIPS_NLP_Filename well-formedness.pdf',
			   'WordNet': 'TIPS_NLP_WordNet.pdf',
			   'Find the character\'s home (By date)': 'TIPS_NLP_File classifier (By date).pdf',
			   'Find the character\'s home (By NER)': 'TIPS_NLP_File classifier (By NER).pdf',
			   'NER (Named Entity Recognition)': 'TIPS_NLP_NER (Named Entity Recognition) Stanford CoreNLP.pdf',
			   'Find the missing character': 'TIPS_NLP_Find the missing character.pdf',
			   'Check the character\'s name tag': 'TIPS_NLP_TIPS_NLP_Word similarity (Levenshtein word distance).pdf',
			   'Find the intruder': 'TIPS_NLP_Find the intruder.pdf',
			   'Find the plagiarist': 'TIPS_NLP_Find the plagiarist (via Lucene).pdf',
			   'CoNLL Table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",
			   'POSTAG (Part of Speech Tags)': "TIPS_NLP_POSTAG (Part of Speech Tags) Stanford CoreNLP.pdf",
			   'Java download install run': 'TIPS_NLP_Java download install run.pdf'}
TIPS_options = 'Filename well-formedness', 'WordNet', 'Find the character\'s home (By date)', 'Find the character\'s home (By NER)', 'NER (Named Entity Recognition)', 'Find the missing character', 'Check the character\'s name tag', 'Find the intruder', 'Find the plagiarist', 'CoNLL Table', 'POSTAG (Part of Speech Tags)', 'Java download install run'


# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, basic_y_coordinate, y_step):
	if not IO_setup_display_brief:
		GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
									  "Please, select the main INPUT directory of the TXT files to be analyzed." + GUI_IO_util.msg_openExplorer)
		GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step, "Help",
									  "Please, select the secondary INPUT directory of the TXT files to be analyzed." + GUI_IO_util.msg_openExplorer)
		GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 2, "Help",
									  GUI_IO_util.msg_outputDirectory)
	else:
		GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
									  GUI_IO_util.msg_IO_setup)

	GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 1), "Help",
								  "Please, tick the checkbox if the filenames processed by the scripts 'Check the filenames well-formedness' and 'Find the plagiarist' embed a date (e.g., The New York Times_12-23-1992).\n\nOnce you have ticked the 'Filename embeds date' option, you will need to provide the following information:\n   1. the date format of the date embedded in the filename (default mm-dd-yyyy);\n   2. the character used to separate the date field embedded in the filenames from the other fields (e.g., _ in the filename The New York Times_12-23-1992) (default _);\n   3. the position of the date field in the filename (e.g., 2 in the filename The New York Times_12-23-1992; 4 in the filename The New York Times_1_3_12-23-1992 where perhaps fields 2 and 3 refer respectively to the page and column numbers).\n\nIF THE FILENAME EMBEDS A DATE AND THE DATE IS THE ONLY FIELD AVAILABLE IN THE FILENAME (e.g., 2000.txt), enter . in the 'Date character separator' field and enter 1 in the 'Date position' field.")
	GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 2), "Help",
								  "Please, tick the checkbox if you wish to check the well-formedness of filenames (for filenames that embed different items of information, e.g., The New York Times_4-22-1918_4_2, i.e., newspaper name, date, page number, column number, separated by _.")
	GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 3), "Help",
								  "Please, tick the checkbox if you wish to open the WordNet GUI and run the Python 3 scripts 'Find the character' and 'Find the ancestor'.\n\n'Find the character' uses the WordNet lexicon database to provide a list of words as social actors (i.e., human characters, groups, or organizations) or other characters (e.g., animals, for folktales).\n\n'Find the ancestor' uses the WordNet lexicon database to aggregate nouns and verbs of a csv list (e.g., run, flee, walk, ... aggregated as verbs of movement).")
	GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 4), "Help",
								  "Please, tick the checkbox if you wish to run the Python 3 script 'Find the missing character'. The script checks an event summary (whether human- or machine-generated) against a set of documents (e.g., all describing the same event) that provided the basis for the summary. The script will generate a list of social actors missing in the event summary.\n\nPlease, check the NER (Named Entity Recognition) tick box to run the script with the added NER filter. The NER option relies on the Stanford NER tagger to increase the probability of identifying missing information in document summaries against the original documents. Summaries will be checked against the originals not just on the basis of missing social actors (by their improper name, e.g., girl), but by proper names (e.g., Mary), and also dates, locations, organizations, as computed by the Stanford NER tagger.\n\nIn INPUT the script expects 3 paths:\n  path to a directory containing several folders, each folder containing a set of related documents (e.g., all describing the same event);\n  path to the directory containing the set of event summaries;\n  output path directory.\n\nIn OUTPUT the script will create two csv files: a csv file that contains the missing social actors and the location of the error; a csv file that calculates the frequency of having a missing social actor problem.")
	GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 5), "Help",
								  "Please, tick the checkbox if you wish to run the Python 3 script \'Check the character\'s name tag\' (i.e., the Levenshtein\'s word distance, also known as edit distance, between any 2 words selected by their NER, Named Entity Recognition, values: CITY, COUNTRY, LOCATION, ORGANIZATION, PERSON).\n\nIn INPUT, the script expects a main directory with several subdirectories with varying sets of txt files. This set of files will be checked for word difference.\n\nIn OUTPUT, the script will produce a csv files with a list suggested ")
	GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 6), "Help",
								  "Please, tick the checkbox if you wish to run the Python 3 script 'Find the character\'s home. The script uses the date embedded in the filename of files in a directory to check against the dates of files grouped in the same subdirectory (e.g., because they talk about the same event).\n\nIt is presumed that files with dates that are very close to each other, as user specified, will belong to the same event.\n\nIn INPUT the script expects 3 paths:\n  path to a directory containing a list of files;\n  a directory containing several folders, each folder containing a set of related documents (e.g., all describing the same event);\n  output path directory.\n\nIn OUTPUT the script will create two csv files: a csv file that contains the missing social actors and the location of the error; a csv file that calculates the frequency of having a missing social actor problem.")
	GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 7), "Help",
								  "Please, tick the checkbox if you wish to run the Python 3 script 'Find the intruder'. The script checks the documents grouped together in a directory, as perhaps all describing a specific event, to see whether any of them do not belong to the group. The script uses NER values for 'Location','Date','Organization', and 'Person' as criteria for checking files.\n\nPlease, using the dropdown menu, select a value for the similarity index. The similarity index, based on cosine similarity, is used to compute the degree of similarity between documents. The default value is set as 0.2. If you set a high value >.6, then every document may be an intruder; so, the recommended value should be <.4.\n\nIn INPUT the script expects the path to a directory containing several folders, each folder containing a set of related documents (e.g., all describing the same event).\n\nIn OUTPUT, the script creates two csv files: One includes a list of irrelevant files, and the folder they are in; The other csv file contains the frequency of having intruders in the input folders.\n\nNo Excel charts are produced since the csv output lists only one record of frequencies and percentages.")
	GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 8), "Help",
								  "Please, tick the checkbox if you wish to run the Java script 'Find the plagiarist'. The script, based on Lucene, checks a set of documents to compute the percentage of similarity between any two of them.\n\nIn INPUT the script expects:\n   1. the file stopwords.txt stored in the lib subdirectory;\n   2. a directory that contains all the files to be compared.\n\nIn OUTPUT, the script produces four output files: \n   1. document_duplicates.txt that shows the summary of duplicated files;\n   2. Lucene_class_freq.csv that shows how many documents fall into each class of frequency (e.g., 100 documents have 10%-20% similarity with other files);\n   3. Lucene_classes_time_freq.csv that shows, for each year, how many documents fall into each class of frequency (e.g., in 1897, 100 documents have 10%-20% similarity with other files);\n  4. Lucene_document_classes_freq.csv that shows for each document, how many documents fall into each class of frequency (e.g., for the document “The Oglethorpe Echo_09-19-1919_1_1.txt”, 10 other documents have 10%-20% frequency of similarity with it).\n\nThe default threshold for similarity is set at 80%. Documents that get a score over this value are considered duplicates of the candidate document. This level was arrived at by running several different threshold levels on different corpora. Lowering the level would give too many false positives (too many documents wrongly classified as similar); raising the level may exclude too many documents.")
	GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 9), "Help",
								  GUI_IO_util.msg_openOutputFiles)

help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), GUI_IO_util.get_basic_y_coordinate(),
			 GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message = "This Python 3 script provides a front-end GUI (Graphical User Interface) for a set of NLP tools, written in Java and Python 3, that can be of use in a variety of social science research projects based on documents.\n\nIn INPUT the scripts expect a main drectory where txt files to be analyzed are stored and, depending upon the type of tools run, a secondary directory where further txt files are stored.\n\nIn OUTPUT, the scripts will save the csv files and Excel charts written by the various scripts."
readMe_command = lambda: GUI_IO_util.readme_button(window, GUI_IO_util.get_help_button_x_coordinate(),
												   GUI_IO_util.get_basic_y_coordinate(), "Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief)

GUI_util.window.mainloop()
