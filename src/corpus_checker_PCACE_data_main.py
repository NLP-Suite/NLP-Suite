# Written by Roberto Franzosi

# Modified by Cynthia Dong and Elaine Dong (Oct 24 2019; Feb 6 2020)
# Modified by Claude Code, July 2026

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "Corpus Checker (PC-ACE data)",
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
import charts_util
import reminders_util
import file_summary_checker_util
import file_find_non_related_documents_util
import run_script_util
import plagiarist_util
import config_aware_parser_util

# RUN section ______________________________________________________________________________________________________________________________________________________


def check_filename(outputDir):
    if IO_libraries_util.check_inputPythonJavaProgramFile('file_checker_converter_cleaner_main.py') == False:
        return
    if platform == "win32":
        run_script_util.run_script("file_manager_main.py")
    # linux # OS X
    elif platform == "linux" or platform == "linux2" or platform == "darwin":
        subprocess.call("sudo Python file_manager_main.py", shell=True)
    # files are opened in the file_filename_checker_main GUI


def character(outputDir):
    if IO_libraries_util.check_inputPythonJavaProgramFile('semantic_aggregation_main.py') == False:
        return
    if platform == "win32":
        run_script_util.run_script("semantic_aggregation_main.py", "character")
    # linux # OS X
    elif platform == "linux" or platform == "linux2" or platform == "darwin":
        subprocess.call("sudo Python semantic_aggregation_main.py character", shell=True)
    # files are opened in the WordNet GUI

def find_character_home(outputDir):
    if IO_libraries_util.check_inputPythonJavaProgramFile('file_classifier_main.py') == False:
        return
    if platform == "win32":
        run_script_util.run_script("file_classifier_main.py", "character", "home")
    # linux # OS X
    elif platform == "linux" or platform == "linux2" or platform == "darwin":
        subprocess.call("sudo Python file_classifier_main.py character home", shell=True)
    # files are opened in the file_classifier_main.py GUI

def missing_character(CoreNLPdir, inputDir, input_secondary_dir_path, outputDir, openOutputFiles, chartPackage, dataTransformation, checkNER):
    if IO_libraries_util.check_inputPythonJavaProgramFile('file_summary_checker_util.py') == False:
        return
    Excel_outputFile=file_summary_checker_util.main(CoreNLPdir, inputDir,input_secondary_dir_path,outputDir,openOutputFiles, chartPackage, dataTransformation, checkNER)
    if Excel_outputFile!="":
        filesToOpen.append(Excel_outputFile)

def intruder(CoreNLPdir,inputDir, outputDir, openOutputFiles, chartPackage, dataTransformation, similarityIndex_Intruder_var):
    if IO_libraries_util.check_inputPythonJavaProgramFile('file_find_non_related_documents_util.py') == False:
        return
    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running INTRUDER at',
                                                 True, '', True, '', True)
    # Windows...
    outputFiles=file_find_non_related_documents_util.main(CoreNLPdir, inputDir, outputDir, openOutputFiles, chartPackage, dataTransformation, similarityIndex_Intruder_var)

    if outputFiles!='':
        filesToOpen.append(outputFiles)
    # Nothing to plot; only one line in the output csv file
    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running INTRUDER at', True, '', True, startTime, True)


def ancestor(inputDir, outputDir):
    if IO_libraries_util.check_inputPythonJavaProgramFile('semantic_aggregation_main.py') == False:
        return
    if platform == "win32":
        run_script_util.run_script("WordNet.py", "ancestor")
    # linux # OS X
    elif platform == "linux" or platform == "linux2" or platform == "darwin":
        subprocess.call("sudo Python semantic_aggregation_main.py ancestor", shell=True)
    # files are opened in the WordNet GUI


"""
This function read in document_similarity_document_classes_freq.csv and group articles from the same newspaper together.
The result csv file showcase for every newspaper, the distribution of plagiarism score.

Key: The way we compute distribution of plagiarism score for newspaper is by adding up all scores for the same 
newspaper and take the average
"""


def group_newspaper(document_class_csv, outputFilename):
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
    with open(outputFilename, "w", newline='', encoding='utf-8', errors='ignore') as f:
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


def plagiarist(inputDir, outputDir, open_csv_output_checkbox, chartPackage, dataTransformation,
               similarityIndex_Plagiarist_var, fileName_embeds_date, DateFormat, DatePosition, DateCharacterSeparator):
    if similarityIndex_Plagiarist_var < .8:
        mb.showwarning(title='Similarity Index warning', message="The level of similarity was set at " + str(
            similarityIndex_Plagiarist_var) + ".\n\nCAVEAT! The default threshold for similarity is normally set at 80%.\n\nBe aware that lowering the default level may result in too many documents wrongly classified as similar; conversely, raising the level may exclude too many documents.")

    lib_stopwords = lib_util.check_lib_stopwords()

    if fileName_embeds_date and len(DateCharacterSeparator) == 0:
        tk.messagebox.showinfo("Plagiarist",
            "The filenames are marked as embedding a date, but no date character "
            "separator was entered.\n\nPlease enter the separator and try again.")
        return

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                   'Started running PLAGIARIST at', True, '', True, '', True)

    # scikit-learn TF-IDF + cosine similarity; writes the document-similarity output
    # files consumed by the charting below.
    result = plagiarist_util.run(inputDir, outputDir, lib_stopwords,
                                 similarityIndex_Plagiarist_var,
                                 fileName_embeds_date, DateFormat, DatePosition,
                                 DateCharacterSeparator)
    if result is None:
        return

    filesToOpen.append(outputDir + os.sep + "document_duplicates.txt")

    outputFilenameCSV_1 = outputDir + os.sep + "document_similarity_classes_freq.csv"
    filesToOpen.append(outputFilenameCSV_1)

    outputFilenameCSV_2 = outputDir + os.sep + "document_similarity_classes_time_freq.csv"
    if fileName_embeds_date and os.path.isfile(outputFilenameCSV_2):
        filesToOpen.append(outputFilenameCSV_2)

    outputFilenameCSV_3 = outputDir + os.sep + "document_similarity_document_instance_classes_freq.csv"
    filesToOpen.append(outputFilenameCSV_3)

    outputFilenameCSV_4 = outputDir + os.sep + "document_similarity_Document_classes_freq.csv"
    group_newspaper(outputFilenameCSV_3, outputFilenameCSV_4)
    filesToOpen.append(outputFilenameCSV_4)

    if chartPackage!='No charts':
        # document_similarity_classes_freq.csv; outputFilenameCSV_1
        outputDir=outputDir
        inputFilename = outputFilenameCSV_1
        columns_to_be_plotted_xAxis=[]
        columns_to_be_plotted_yAxis=[[0, 1]]
        hover_label = ['List of Documents in Category']
        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, inputFilename, outputDir,
                                                  outputFileLabel='SSR_plagiar',
                                                  chartPackage=chartPackage,
                                                  dataTransformation=dataTransformation,
                                                  chart_type_list=["bar"],
                                                  chart_title='Frequency of Plagiarism by Classes of % Duplication',
                                                  column_xAxis_label_var='Classes of percentage duplication',
                                                  hover_info_column_list=hover_label)
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        # Plot document_similarity_classes_time_freq.csv line plot (temporal plot); outputFilenameCSV_2
        if fileName_embeds_date and os.path.isfile(outputFilenameCSV_2):
            # columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=[[0,1], [0,2], [0,3], [0,4], [0,5], [0,6],[0,7], [0,8], [0,9],[0,10]]
            # hover_label=['','','','','','','','','','']
            inputFilename = outputFilenameCSV_2
            columns_to_be_plotted_xAxis=[]
            columns_to_be_plotted_yAxis=[[0, 1], [0, 2], [0, 3]]
            hover_label = ['', '', '']
            outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, inputFilename, outputDir,
                                                      outputFileLabel='SSR_plagiar',
                                                      chartPackage=chartPackage,
                                                      dataTransformation=dataTransformation,
                                                      chart_type_list=["line"],
                                                      chart_title='Frequency of Plagiarism by Year',
                                                      column_xAxis_label_var='Year',
                                                      hover_info_column_list=hover_label)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        # No plot for document_similarity_document_classes_freq.csv
        #   because it could potentially have thousands of documents
        # 	inputFilename = outputFilenameCSV_3


        # document_similarity_Document_classes_freq.csv; outputFilenameCSV_4
        columns_to_be_plotted_xAxis=[]
        columns_to_be_plotted_yAxis=[[0, 1],[0, 2],[0, 3]]
        hover_label = ['']
        inputFilename = outputFilenameCSV_4
        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, inputFilename, outputDir,
                                                  outputFileLabel='SSR_plagiar',
                                                  chartPackage=chartPackage,
                                                  dataTransformation=dataTransformation,
                                                  chart_type_list=["bar"],
                                                  chart_title='Frequency of Plagiarism by Document Name & Classes',
                                                  column_xAxis_label_var='',
                                                  hover_info_column_list=hover_label)
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running PLAGIARIST at', True, '', True, startTime)

def Levenshtein():
    if IO_libraries_util.check_inputPythonJavaProgramFile('file_spell_checker_main.py') == False:
        return
    if platform == "win32":
        run_script_util.run_script("file_spell_checker_main.py")
    # linux # OS X
    elif platform == "linux" or platform == "linux2" or platform == "darwin":
        subprocess.call("sudo Python file_spell_checker_main.py", shell=True)
    # files are opened in the spell_checker_main


def run():
    # widget values read here at RUN time (was: run_script_command lambda + run() params)
    inputDir = GUI_util.input_main_dir_path.get()
    input_secondary_dir_path = GUI_util.input_secondary_dir_path.get()
    outputDir = GUI_util.output_dir_path.get()
    openOutputFiles = GUI_util.open_csv_output_checkbox.get()
    chartPackage = GUI_util.charts_package_options_widget.get()
    dataTransformation = GUI_util.data_transformation_options_widget.get()
    fileName_embeds_date = globals()['fileName_embeds_date'].get()
    DateFormat = date_format.get()
    DatePosition = date_position_var.get()
    DateCharacterSeparator = items_separator_var.get()
    check_filename_var = globals()['check_filename_var'].get()
    character_var = globals()['character_var'].get()
    character_home_var = globals()['character_home_var'].get()
    missing_character_var = globals()['missing_character_var'].get()
    NER_var = globals()['NER_var'].get()
    intruder_var = globals()['intruder_var'].get()
    similarityIndex_Intruder_var = globals()['similarityIndex_Intruder_var'].get()
    ancestor_var = globals()['ancestor_var'].get()
    nouns_verbs = ancestor_menu_var.get()
    plagiarist_var = globals()['plagiarist_var'].get()
    similarityIndex_Plagiarist_var = globals()['similarityIndex_Plagiarist_var'].get()
    Levenshtein_var = globals()['Levenshtein_var'].get()

    config_filename = GUI_util.config_filename_selected_config.get()

    global filesToOpen
    filesToOpen = []
    # Both parsing tools in this GUI ('Find the missing character' and 'Find the intruder') are now
    # config-aware (Stanford CoreNLP / Stanza / spaCy); every other option either opens another GUI or is
    # pure Python (the plagiarist uses scikit-learn TF-IDF). So the Stanford CoreNLP directory is required
    # ONLY when CoreNLP is the package selected in the NLP Suite setup -- Stanza/spaCy users are no longer
    # forced to install CoreNLP to use this GUI.
    CoreNLPdir = ''
    if config_aware_parser_util.requires_CoreNLP():
        # check that the CoreNLPdir has been setup
        CoreNLPdir, existing_software_config, errorFound = IO_libraries_util.external_software_install('corpus_checker_PCACE_data_main',
                                                                                             'Stanford CoreNLP',
                                                                                             '',
                                                                                             silent=False, errorFound=False)
        if CoreNLPdir==None or CoreNLPdir=='':
            return filesToOpen

    if (check_filename_var == False and character_var == False and character_home_var == False and missing_character_var == False and intruder_var == False and Levenshtein_var==False and ancestor_var == False and plagiarist_var == False):
        mb.showwarning(title='No options selected',
                       message='No options have been selected.\n\nPlease, select an option and try again.')
        return

    if check_filename_var == True:
        check_filename(outputDir)
    elif character_var == True:
        character(outputDir)
    elif character_home_var == True:
        find_character_home(outputDir)
    elif missing_character_var == True:
        missing_character(CoreNLPdir, inputDir, input_secondary_dir_path, outputDir, openOutputFiles, chartPackage, dataTransformation, NER_var)
    elif intruder_var == True:
        intruder(CoreNLPdir, inputDir, outputDir, openOutputFiles, chartPackage, dataTransformation, similarityIndex_Intruder_var)
    elif ancestor_var == True:
        ancestor(inputDir, outputDir)
    elif plagiarist_var == True:
        plagiarist(inputDir, outputDir, openOutputFiles, chartPackage, dataTransformation,
                   similarityIndex_Plagiarist_var, fileName_embeds_date, DateFormat, DatePosition,
                   DateCharacterSeparator)
    elif Levenshtein_var == True:
        Levenshtein()
    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)


# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
GUI_util.run_button.configure(command=run)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=False
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=600, # height at brief display
                             GUI_height_full=680, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label = 'Graphical User Interface (GUI) for the Corpus checker (PC-ACE data)'
config_filename = 'NLP_default_IO_config.csv'
head, scriptName = os.path.split(os.path.basename(__file__))

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
config_input_output_numeric_options=[0,1,1,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window = GUI_util.window
# config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
# config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

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
items_separator_var = tk.StringVar()
date_position_var = tk.IntVar()

keyWord_var = tk.StringVar()
keyWord_entry_var = tk.StringVar()
ancestor_var = tk.IntVar()
ancestor_menu_var = tk.StringVar()
selectedFile_var = tk.StringVar()  # the noun/verb file to be used for ancestor

extra_GUIs_var = tk.IntVar()
extra_GUIs_menu_var = tk.StringVar()

#setup GUI widgets

def activate_extra_GUIs():
    # the dropdown is clickable only while the checkbox is ticked. Without this command the checkbox would be
    # inert: the menu would stay enabled, a user could pick a GUI before ticking, open_GUI would grey the menu
    # out and return, and nothing could switch it back on -- a disabled OptionMenu cannot be clicked.
    extra_GUIs_menu.configure(state='normal' if extra_GUIs_var.get() else 'disabled')

extra_GUIs_var.set(0)
extra_GUIs_checkbox = tk.Checkbutton(window, text='GUIs available for more analyses ', variable=extra_GUIs_var, onvalue=1, offvalue=0, command=lambda: activate_extra_GUIs())
# extra_GUIs_checkbox.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,extra_GUIs_checkbox,True)

extra_GUIs_menu_var.set('')
extra_GUIs_menu = tk.OptionMenu(window,extra_GUIs_menu_var,'PC-ACE data analysis (Open GUI)','PC-ACE data validation (Open GUI)')
extra_GUIs_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   extra_GUIs_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select other related types of analysis you wish to perform" \
                                    "\nThe selected GUI will open without having to press RUN")

def open_GUI(*args):
    if not extra_GUIs_var.get():
        return
    if 'validation' in extra_GUIs_menu_var.get():
        run_script_util.run_script("DB_PCACE_data_validation_main.py")
    elif 'analysis' in extra_GUIs_menu_var.get():
        run_script_util.run_script("DB_PCACE_data_analysis_main.py")
extra_GUIs_menu_var.trace('w',open_GUI)

fileName_embeds_date_checkbox = tk.Checkbutton(window, text='Filename embeds date', state="disabled",
                                               variable=fileName_embeds_date, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               fileName_embeds_date_checkbox, True)

date_format_lb = tk.Label(window, text='Date format ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                                               date_format_lb, True)
date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy', 'yyyy-mm-dd', 'yyyy-dd-mm', 'yyyy-mm',
                                 'yyyy')
date_format_menu.configure(width=10, state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate + 90, y_multiplier_integer,
                                               date_format_menu, True)

items_separator_var_lb = tk.Label(window, text='Date character separator ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate + 210, y_multiplier_integer,
                                               items_separator_var_lb, True)
items_separator_var_menu = tk.Entry(window, textvariable=items_separator_var)
items_separator_var_menu.configure(width=2, state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate + 360, y_multiplier_integer,
                                               items_separator_var_menu, True)

date_position_var_menu_lb = tk.Label(window, text='Date position ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate + 390, y_multiplier_integer,
                                               date_position_var_menu_lb, True)
date_position_var_menu = tk.OptionMenu(window, date_position_var, 1, 2, 3, 4, 5)
date_position_var_menu.configure(width=4, state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate + 490, y_multiplier_integer,
                                               date_position_var_menu)

check_filename_var.set(0)
check_filename_checkbox = tk.Checkbutton(window, text='Check the filenames well-formedness',
                                         variable=check_filename_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               check_filename_checkbox)

character_var.set(0)
character_checkbox = tk.Checkbutton(window, text='Find the character & the ancestor (via WordNet, VerbNet, FrameNet)',
                                    variable=character_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               character_checkbox)

missing_character_var.set(0)
missing_character_checkbox = tk.Checkbutton(window, text='Find the missing character', variable=missing_character_var,
                                            onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               missing_character_checkbox, True)

NER_var.set(0)
NER_checkbox = tk.Checkbutton(window, text='NER (Named Entity Recognition) ', state="disabled", variable=NER_var,
                              onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                                               NER_checkbox)

Levenshtein_var.set(0)
Levenshtein_checkbox = tk.Checkbutton(window, text="Check the character's name tag", variable=Levenshtein_var,
                                      onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               Levenshtein_checkbox)

character_home_var.set(0)
character_home_checkbox = tk.Checkbutton(window, text="Find the character's home", variable=character_home_var,
                                         onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               character_home_checkbox)

intruder_var.set(0)
intruder_checkbox = tk.Checkbutton(window, text='Find the intruder', variable=intruder_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               intruder_checkbox, True)

similarityIndex_Intruder_var.set(0.2)
similarityIndex_Intruder_menu_lb = tk.Label(window, text='Relativity index threshold')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                                               similarityIndex_Intruder_menu_lb, True)
similarityIndex_Intruder_menu = tk.OptionMenu(window, similarityIndex_Intruder_var, .1, .15, .2, .25, .3, .35, .4, .45,
                                              .5, .55, .6, .65, .7, .75, .8, .85, .9)
similarityIndex_Intruder_menu.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate + 170, y_multiplier_integer,
                                               similarityIndex_Intruder_menu,
                                               False, False, False, False, 90,
                                               GUI_IO_util.entry_box_x_coordinate + 170,
                                               "Select the threshold BELOW which a document is flagged as an intruder, i.e., as not belonging to the folder (event) it is filed in.\n\nThe index is a cosine similarity computed between the social actors and named entities of a document and those of all the other documents filed in the same folder.\n\nThe default value is 0.2. Raising the threshold flags more documents: set it above .6 and nearly every document becomes an intruder. The recommended range is below .4.")

plagiarist_var.set(0)
plagiarist_checkbox = tk.Checkbutton(window, text='Find the plagiarist', variable=plagiarist_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               plagiarist_checkbox, True)

similarityIndex_Plagiarist_var.set(.8)
similarityIndex_Plagiarist_menu_lb = tk.Label(window, text='Similarity index ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                                               similarityIndex_Plagiarist_menu_lb, True)
similarityIndex_Plagiarist_menu = tk.OptionMenu(window, similarityIndex_Plagiarist_var, .4, .45, .5, .55, .6,
                                                .65, .7, .75, .8, .85, .9)
similarityIndex_Plagiarist_menu.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate + 170, y_multiplier_integer,
                                               similarityIndex_Plagiarist_menu,
                                               False, False, False, False, 90,
                                               GUI_IO_util.entry_box_x_coordinate + 170,
                                               "Select the threshold AT OR ABOVE which two documents are considered duplicates of one another (how much the sources copied from each other).\n\nSimilarity is computed as a TF-IDF cosine similarity between the two documents.\n\nThe default value is 0.8, i.e., 80%. Lowering it gives too many false positives, with documents wrongly classified as similar; raising it may exclude genuine duplicates. Because earlier releases scored similarity differently, it is worth re-checking this threshold on your own corpus.")


def clear(e):
    extra_GUIs_var.set(0)
    extra_GUIs_menu_var.set('')
    activate_extra_GUIs()  # untick must also grey the dropdown out, or checkbox and menu disagree
    similarityIndex_Intruder_var.set(0.2)
    similarityIndex_Plagiarist_var.set(0.8)
    GUI_util.clear("Escape")

window.bind("<Escape>", clear)


def activate_dateOptions(*args):
    if fileName_embeds_date.get() == False:
        date_format_menu.configure(width=10, state="disabled")
        items_separator_var_menu.configure(width=2, state="disabled")
        date_position_var_menu.configure(width=4, state="disabled")
    else:
        date_format_menu.configure(width=10, state="normal")
        items_separator_var_menu.configure(width=2, state="normal")
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
        reminders_util.checkReminder(scriptName, ["Filename checker"], '', True)
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
        reminders_util.checkReminder(scriptName, ["Plagiarist"], '', True)
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
plagiaristOptions(date_format, items_separator_var, date_position_var)

# y_multiplier_integer = y_multiplier_integer+1

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Corpus checker (PC-ACE data) - the whole pipeline': 'TIPS_NLP_Corpus checker (PC-ACE data).pdf',
               'Check the character\'s name tag': 'TIPS_NLP_Word similarity (Levenshtein edit distance).pdf',
               'Filename well-formedness': 'TIPS_NLP_Filename checker.pdf',
               'WordNet': 'TIPS_NLP_WordNet.pdf',
               'Lexical databases (WordNet, VerbNet, FrameNet)': 'TIPS_NLP_Lexical databases (WordNet, VerbNet, FrameNet).pdf',
               'Find the character\'s home (By date)': 'TIPS_NLP_File classifier (By date).pdf',
               'Find the character\'s home (By NER)': 'TIPS_NLP_File classifier (By NER).pdf',
               'NER (Named Entity Recognition)': 'TIPS_NLP_NER (Named Entity Recognition).pdf',
               'Find the missing character': 'TIPS_NLP_Find the missing character.pdf',
               'Find the intruder': 'TIPS_NLP_Find the intruder.pdf',
               'Find the plagiarist': 'TIPS_NLP_Find the plagiarist.pdf',
               'CoNLL Table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",
               'POSTAG (Part of Speech Tags)': "TIPS_NLP_POSTAG (Part of Speech Tags) Stanford CoreNLP.pdf"}
               # 'Java download install run': 'TIPS_NLP_Java download install run.pdf'}
TIPS_options = 'Corpus checker (PC-ACE data) - the whole pipeline', 'Filename well-formedness', 'WordNet', 'Lexical databases (WordNet, VerbNet, FrameNet)', 'Find the character\'s home (By date)', 'Find the character\'s home (By NER)', 'NER (Named Entity Recognition)', 'Find the missing character', 'Check the character\'s name tag', 'Find the intruder', 'Find the plagiarist', 'CoNLL Table', 'POSTAG (Part of Speech Tags)' #, 'Java download install run'


# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      "Please, select the main INPUT directory of the TXT files to be analyzed." + GUI_IO_util.msg_openExplorer)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      "Please, select the secondary INPUT directory of the TXT files to be analyzed." + GUI_IO_util.msg_openExplorer)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         'Please, tick the \'GUIs available\' checkbox if you wish to see and select the range of other available tools suitable for sentiment analysis.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if the filenames processed by the scripts 'Check the filenames well-formedness' and 'Find the plagiarist' embed a date (e.g., The New York Times_12-23-1992).\n\nOnce you have ticked the 'Filename embeds date' option, you will need to provide the following information:\n   1. the date format of the date embedded in the filename (default mm-dd-yyyy);\n   2. the character used to separate the date field embedded in the filenames from the other fields (e.g., _ in the filename The New York Times_12-23-1992) (default _);\n   3. the position of the date field in the filename (e.g., 2 in the filename The New York Times_12-23-1992; 4 in the filename The New York Times_1_3_12-23-1992 where perhaps fields 2 and 3 refer respectively to the page and column numbers).\n\nIF THE FILENAME EMBEDS A DATE AND THE DATE IS THE ONLY FIELD AVAILABLE IN THE FILENAME (e.g., 2000.txt), enter . in the 'Date character separator' field and enter 1 in the 'Date position' field.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to check the well-formedness of filenames (for filenames that embed different items of information, e.g., The New York Times_4-22-1918_4_2, i.e., newspaper name, date, page number, column number, separated by _.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to open the WordNet GUI and run the Python 3 scripts 'Find the character' and 'Find the ancestor'.\n\n'Find the character' uses the WordNet lexicon database to provide a list of words as social actors (i.e., human characters, groups, or organizations) or other characters (e.g., animals, for folktales).\n\n'Find the ancestor' aggregates the nouns and verbs of a csv list into higher-level categories (e.g., run, flee, walk, ... aggregated as verbs of movement). In the Semantic aggregation GUI you can choose the knowledge base used for the aggregation: WordNet (synsets), VerbNet (verb classes), or FrameNet (semantic frames). WordNet organizes NOUNS into an is-a hierarchy and is what produces the list of social actors; VerbNet and FrameNet come into their own for VERBS and for the frames (and frame roles) in which actors appear.\n\nPlease, note that whichever knowledge base you explore here, the checks 'Find the missing character' and 'Find the intruder' compare your documents against the social actor list stored as social-actor-list.csv in the lib/wordLists folder, which is built from WordNet.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to run the Python 3 script 'Find the missing character'. The script checks an event summary (whether human- or machine-generated) against a set of documents (e.g., all describing the same event) that provided the basis for the summary. The script will generate a list of social actors missing in the event summary.\n\nPlease, check the NER (Named Entity Recognition) tick box to run the script with the added NER filter. The NER option relies on the NER tagger of the NLP package you selected in the NLP Suite setup (Stanford CoreNLP, Stanza, or spaCy) to increase the probability of identifying missing information in document summaries against the original documents. Summaries will be checked against the originals not just on the basis of missing social actors (by their improper name, e.g., girl), but by proper names (e.g., Mary), and also dates, locations, organizations, as computed by the NER tagger. Named-entity results differ somewhat between packages, since each uses a different model.\n\nIn INPUT the script expects 3 paths:\n  path to a directory containing several folders, each folder containing a set of related documents (e.g., all describing the same event);\n  path to the directory containing the set of event summaries;\n  output path directory.\n\nIn OUTPUT the script will create two csv files: a csv file that contains the missing social actors and the location of the error; a csv file that calculates the frequency of having a missing social actor problem.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to run the Python 3 script \'Check the character\'s name tag\' (i.e., the Levenshtein\'s word distance, also known as edit distance, between any 2 words selected by their NER, Named Entity Recognition, values: CITY, COUNTRY, LOCATION, ORGANIZATION, PERSON).\n\nIn INPUT, the script expects a main directory with several subdirectories with varying sets of txt files. This set of files will be checked for word difference.\n\nThe edit distance is the number of single-character insertions, deletions, or substitutions needed to turn one word into another (Fleming/Flemming is 1 edit; Coolidge/Cooledge is 2), scaled to a 0-100 similarity score. The comparison ignores case and word order, so COBB and Cobb, and Jim Cobb and Cobb, Jim, are recognized as the same name.\n\nBe aware that a single similarity threshold behaves differently on short and long words: on short surnames one edit already costs a large share of the score (Lee/Loe scores only 67), so genuine typos may fall below the threshold, while distinct short names may sit above it (Macon/Bacon scores 80). Inspect the suggestions rather than accepting them wholesale.\n\nIn OUTPUT, the script will produce a csv file listing each word flagged as a possible variant, the closest matching word found elsewhere in the directory, and that word's frequency, so that you can judge which spelling is the correct one.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to run the Python 3 script 'Find the character\'s home'. The script uses the date embedded in the filename of files in a directory to check against the dates of files grouped in the same subdirectory (e.g., because they talk about the same event).\n\nIt is presumed that files with dates that are very close to each other, as user specified, will belong to the same event.\n\nIn INPUT the script expects 3 paths:\n  path to a directory containing a list of files;\n  a directory containing several folders, each folder containing a set of related documents (e.g., all describing the same event);\n  output path directory.\n\nIn OUTPUT the script will create a csv file listing, for each loose document, the subdirectory (event) whose documents are closest to it in date, so that you can decide where the document belongs.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to run the Python 3 script 'Find the intruder'. The script checks the documents grouped together in a directory, as perhaps all describing a specific event, to see whether any of them do not belong to the group. The script uses NER values for 'Location','Date','Organization', and 'Person' as criteria for checking files.\n\nPlease, using the dropdown menu, select a value for the similarity index. The similarity index, based on cosine similarity, is used to compute the degree of similarity between documents. The default value is set as 0.2. If you set a high value >.6, then every document may be an intruder; so, the recommended value should be <.4.\n\nIn INPUT the script expects the path to a directory containing several folders, each folder containing a set of related documents (e.g., all describing the same event).\n\nIn OUTPUT, the script creates two csv files: One includes a list of irrelevant files, and the folder they are in; The other csv file contains the frequency of having intruders in the input folders.\n\nNo Excel charts are produced since the csv output lists only one record of frequencies and percentages.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to run the 'Find the plagiarist' tool. It uses TF-IDF with cosine similarity to compute the percentage of similarity between any two documents.\n\nIn INPUT the tool expects:\n   1. the file stopwords.txt stored in the lib subdirectory;\n   2. a directory that contains all the files to be compared.\n\nIn OUTPUT, the tool produces four output files: \n   1. document_duplicates.txt that shows the summary of duplicated files;\n   2. document_similarity_classes_freq.csv that shows how many documents fall into each class of frequency (e.g., 100 documents have 10%-20% similarity with other files);\n   3. document_similarity_classes_time_freq.csv that shows, for each year, how many documents fall into each class of frequency (e.g., in 1897, 100 documents have 10%-20% similarity with other files);\n  4. document_similarity_document_classes_freq.csv that shows for each document, how many documents fall into each class of frequency (e.g., for the document “The Oglethorpe Echo_09-19-1919_1_1.txt”, 10 other documents have 10%-20% frequency of similarity with it).\n\nThe default threshold for similarity is set at 80%. Documents that get a score over this value are considered duplicates of the candidate document. Because the similarity is computed with TF-IDF cosine similarity, and earlier releases used a different scoring, you may wish to re-check this threshold on your corpus. Lowering the level would give too many false positives (too many documents wrongly classified as similar); raising the level may exclude too many documents.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

# change the value of the readMe_message
readMe_message = "This Python 3 script provides a front-end GUI (Graphical User Interface) for a pipeline of eight computer-automated checks on the RELIABILITY of a collection of documents. Rather than analyzing content, these tools ask a different question: is my corpus correctly built? Are the filenames well formed? Is every document filed under the right event? Are the same people and places spelled consistently? Did my hand-written summaries leave out actors who appear in the sources? Are some documents simply copies of others?\n\nThe checks expect data organized as in PC-ACE: one subdirectory per cluster (in the lynching project, an event), each holding that cluster's documents, with metadata embedded in the filenames and separated by an underscore (e.g., The Atlanta Constitution_01-22-1892_4_2, i.e., newspaper name, date, page number, column number). A cluster may equally be a topic, an informant, or a recipient; what matters is that documents are grouped in subdirectories.\n\nIn INPUT the scripts expect a main directory where txt files to be analyzed are stored and, depending upon the type of tools run, a secondary directory where further txt files are stored (e.g., the event summaries used by 'Find the missing character').\n\nIn OUTPUT, the scripts will save the csv files and Excel charts written by the various scripts.\n\nThe checks that parse text use the NLP package you selected in the NLP Suite setup (Stanford CoreNLP, Stanza, or spaCy). You are asked for the Stanford CoreNLP directory ONLY when CoreNLP is the package you selected.\n\nThese tools are described in Franzosi, R., Dong, W., & Dong, Y. (2021), 'Qualitative and quantitative research in the humanities and social sciences: how natural language processing (NLP) can help', Quality & Quantity."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
