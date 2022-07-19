# Written by Roberto Franzosi

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "Stanza_main.py", ['tkinter', 'subprocess']) == False:
    sys.exit(0)

import os
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_files_util
import IO_user_interface_util
import config_util
import reminders_util
import IO_internet_util
import Stanza_util
import constants_util
# import Stanford_CoreNLP_annotator_util
import Stanford_CoreNLP_coreference_util
# import CoNLL_util
# import file_checker_util
# import file_cleaner_util
# import sentence_analysis_util

# RUN section ______________________________________________________________________________________________________________________________________________________

# https://stackoverflow.com/questions/45886128/unable-to-set-up-my-own-stanford-corenlp-server-with-error-could-not-delete-shu
# for the Error [Thread-0] INFO CoreNLP - CoreNLP Server is shutting down
# sometimes the error appears but processing actually continues; but rebooting should do the trick if processing does not continue

# dateInclude indicates whether there is date embedded in the file name.
# 1: included 0: not included
# def run(inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage, memory_var, date_extractor, split_files, quote_extractor, Stanza_gender_annotator, CoReference, manual_Coref, parser, parser_menu_var, dateInclude, sep, date_field_position, dateFormat, compute_sentence, CoNLL_table_analyzer_var):


def run(inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage,
        memory_var, language_var,
        parser, parser_menu_var,
        dateInclude, sep, date_field_position, dateFormat,
        CoNLL_table_analyzer_var,
        Stanza_annotators_var, Stanza_annotators_menu_var,
        CoreNLP_var):

    filesToOpen = []
    outputCoNLLfilePath = ''

    # # check internet connection
    # if not IO_internet_util.check_internet_availability_warning("Stanford CoreNLP"):
    #     return
    #

    if parser == 0 and CoNLL_table_analyzer_var == 0 and Stanza_annotators_var == 0 and CoreNLP_var == 0:
        mb.showinfo("Warning", "No options have been selected.\n\nPlease, select an option and try again.")
        return

    if CoNLL_table_analyzer_var == 1:
        mb.showwarning('Warning',
                       'The option of opening the CoNLL table analyser GUI for Stanza is not available yet. Sorry!\n\nPlease, select a different option and try again.')
        return
        # mb.showinfo("Warning", "You have selected to open the CoNLL table analyser GUI. This option expects to run the parser first.\n\nPlease, tick the CoreNLP parser checkbox and try again.")
        # return

    if parser:
        if parser_menu_var == 'Constituency parser':
            # TODO MINO
            #   connect to Stanza annotator
            mb.showwarning('Warning',
                           'The selected option is not available yet. Sorry!\n\nPlease, select a different option and try again.')
            return
        annotator='depparse'

    if Stanza_annotators_var:
        if Stanza_annotators_menu_var == '':
            mb.showwarning('Warning',
                           'The option of running a Stanza annotator has been selected but no annotaor has been selected.\n\nPlease, select an annotator option and try again.')
            return
        if 'Sentence splitter (with sentence length)' in Stanza_annotators_menu_var:
            annotator = 'Sentence'
        elif 'Lemma annotator' in Stanza_annotators_menu_var:
            annotator = 'Lemma'
        elif 'POS annotator' in Stanza_annotators_menu_var:
            annotator = 'All POS'
        elif 'NER annotator' in Stanza_annotators_menu_var:  # NER annotator
            annotator = 'NER'
        elif 'Sentiment analysis' in Stanza_annotators_menu_var:
            annotator = 'sentiment'
        else:
            return

        document_length_var = 1
        limit_sentence_length_var = 1000
        tempOutputFiles = Stanza_util.Stanza_annotate(config_filename, inputFilename, inputDir,
                                                                       outputDir,
                                                                       openOutputFiles,
                                                                       createCharts, chartPackage,
                                                                       annotator, False,
                                                                       language_list,
                                                                       memory_var, document_length_var, limit_sentence_length_var,
                                                                       extract_date_from_filename_var=dateInclude,
                                                                       date_format=dateFormat,
                                                                       date_separator_var=sep,
                                                                       date_position_var=date_field_position)
            # ,
            #                                                            language=language_var)
            #                                                         #    language = language_var)

        if tempOutputFiles == None:
            return

        if len(tempOutputFiles)>0:
            filesToOpen.extend(tempOutputFiles)
            if 'parser' in annotator:
                reminders_util.checkReminder(config_filename,
                                             reminders_util.title_options_CoreNLP_NER_tags,
                                             reminders_util.message_CoreNLP_NER_tags,
                                             True)
                if CoNLL_table_analyzer_var:
                        if IO_libraries_util.check_inputPythonJavaProgramFile('CoNLL_table_analyzer_main.py') == False:
                            return
                        # open the analyzer having saved the new parser output in config so that it opens the right input file
                        config_filename_temp = 'conll_table_analyzer_config.csv'
                        config_input_output_numeric_options = [1, 0, 0, 1]
                        config_input_output_alphabetic_options = [str(tempOutputFiles[0]), '', '', outputDir]
                        config_util.write_config_file(GUI_util.window, config_filename_temp,
                                                      config_input_output_numeric_options,
                                                      config_input_output_alphabetic_options, True)

                        reminders_util.checkReminder(config_filename,
                                                     reminders_util.title_options_CoNLL_analyzer,
                                                     reminders_util.message_CoNLL_analyzer,
                                                     True)

                        call("python CoNLL_table_analyzer_main.py", shell=True)

        if openOutputFiles:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

    if CoreNLP_var:
        call("python Stanford_CoreNLP_main.py", shell=True)

# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                 GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.create_chart_output_checkbox.get(),
                                 GUI_util.charts_dropdown_field.get(),
                                 memory_var.get(),
                                 language_var.get(),
                                 parser_var.get(),
                                 parser_menu_var.get(),
                                 fileName_embeds_date.get(),
                                 date_separator_var.get(),
                                 date_position_var.get(),
                                 date_format.get(),
                                 CoNLL_table_analyzer_var.get(),
                                 Stanza_annotators_var.get(),
                                 Stanza_annotators_menu_var.get(),
                                 CoreNLP_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=560, # height at brief display
                             GUI_height_full=640, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display


GUI_label = 'Graphical User Interface (GUI) for Stanza (Stanford NLP Group)'
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
config_input_output_numeric_options=[2,1,0,1]
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = scriptName.replace('main.py', 'config.csv')

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window = GUI_util.window

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path

def clear(e):
    reset_language_list()
    language_var.set("English")
    language_menu.configure(state='normal')
    parser_var.set(1)
    parser_menu_var.set("Dependency parser")
    Stanza_annotators_var.set(0)
    Stanza_annotators_menu_var.set('')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

language_var = tk.StringVar()
language_list = []
memory_var = tk.IntVar()
date_extractor_var = tk.IntVar()
split_files_var = tk.IntVar()
parser_var = tk.IntVar()
parser_menu_var = tk.StringVar()
fileName_embeds_date = tk.IntVar()

date_format = tk.StringVar()
date_separator_var = tk.StringVar()
date_position_var = tk.IntVar()

CoNLL_table_analyzer_var = tk.IntVar()

Stanza_annotators_var = tk.IntVar()
Stanza_annotators_menu_var = tk.StringVar()

CoreNLP_var = tk.IntVar()

def open_GUI():
    call("python file_checker_converter_cleaner_main.py", shell=True)

pre_processing_button = tk.Button(window, text='Pre-processing tools (file checking & cleaning GUI)',command=open_GUI)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               pre_processing_button)

# memory options

memory_var_lb = tk.Label(window, text='Memory ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               memory_var_lb, True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(8)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+100, y_multiplier_integer,
                                               memory_var)

date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy', 'yyyy-mm-dd', 'yyyy-dd-mm', 'yyyy-mm',
                                 'yyyy')

fileName_embeds_date_msg = tk.Label()
date_position_menu_lb = tk.Label()
date_position_menu = tk.OptionMenu(window, date_position_var, 1, 2, 3, 4, 5)
date_format_lb = tk.Label()
date_separator = tk.Entry(window, textvariable=date_separator_var)
date_separator_lb = tk.Label()

fileName_embeds_date_checkbox = tk.Checkbutton(window, text='Filename embeds date', variable=fileName_embeds_date,
                                               onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               fileName_embeds_date_checkbox, True)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               fileName_embeds_date_msg, True)

date_format.set('mm-dd-yyyy')
date_format_lb = tk.Label(window, text='Date format ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               date_format_lb, True)
date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy', 'yyyy-mm-dd', 'yyyy-dd-mm', 'yyyy-mm',
                                 'yyyy')
date_format_menu.configure()
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 90, y_multiplier_integer,
                                               date_format_menu, True)

date_separator_lb = tk.Label(window, text='Date character separator ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 230, y_multiplier_integer,
                                               date_separator_lb, True)

date_separator_var.set('_')
date_separator = tk.Entry(window, textvariable=date_separator_var)
date_separator.configure(width=2)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 390, y_multiplier_integer,
                                               date_separator, True)

date_position_var.set(2)
date_position_menu_lb = tk.Label(window, text='Date position ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 440, y_multiplier_integer,
                                               date_position_menu_lb, True)
date_position_menu = tk.OptionMenu(window, date_position_var, 1, 2, 3, 4, 5)
date_position_menu.configure(width=2)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 530, y_multiplier_integer,
                                               date_position_menu)


def check_CoreNLP_dateFields(*args):
    if fileName_embeds_date.get() == 1:
        # fileName_embeds_date_msg.config(text="Date option ON")
        date_format_menu.config(state="normal")
        date_separator.config(state='normal')
        date_position_menu.config(state='normal')
    else:
        # fileName_embeds_date_msg.config(text="Date option OFF")
        date_format_menu.config(state="disabled")
        date_separator.config(state='disabled')
        date_position_menu.config(state="disabled")

fileName_embeds_date.trace('w', check_CoreNLP_dateFields)

language_lb = tk.Label(window,text='Language')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),
                                               y_multiplier_integer, language_lb, True)

# TODO MINO we need to get the list of Stanza supported languages from this script
#   https://github.com/stanfordnlp/stanza/issues/511
# def list_all_languages(model_dir=DEFAULT_MODEL_DIR):
#     with open(os.path.join(model_dir, 'resources.json')) as fin:
#         resources = json.load(fin)
#     languages = [lang for lang in resources if 'alias' not in resources[lang]]
#     languages = sorted(languages)
#     return languages
import json
import stanza.resources.common
DEFAULT_MODEL_DIR = stanza.resources.common.DEFAULT_MODEL_DIR
from tkinter import *
lang_dict  = dict(constants_util.languages)

def print_it(event):
    print(language_var.get())

language_var.set('English')
language_list.append('English')
def list_all_languages(model_dir=DEFAULT_MODEL_DIR):
    with open(os.path.join(model_dir, 'resources.json')) as fin:
        resources = json.load(fin)
    languages = [lang for lang in resources if 'alias' not in resources[lang]]
    languages = sorted(languages)
    return languages

langs = list_all_languages()
langs_full = sorted([lang_dict[x] for x in langs])
language_menu = ttk.Combobox(window, width = 70, textvariable = language_var)
language_menu['values'] = langs_full
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+100,
                                               y_multiplier_integer, language_menu,True)
def check_language(*args):
    if language_var.get() in language_list:
        mb.showwarning(title='Warning',
                       message='The selected language "' + language_var.get() + '" is already in your selection list: ' + str(
                           language_list) + '.\n\nPlease, select another language.')
        window.focus_force()
        return
    else:
        if language_var.get() == '':
            language_menu.configure(state='normal')
        else:
            language_list.append(language_var.get())
            language_menu.configure(state='disabled')
        add_language_button.configure(state='normal')
        reset_language_button.configure(state='normal')
        show_language_button.configure(state='normal')
language_var.trace('w', check_language)

add_language_button = tk.Button(window, text='+', width=2,height=1,state='normal',command=lambda: activate_language_var())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 410,y_multiplier_integer,add_language_button, True)

reset_language_button = tk.Button(window, text='Reset', width=5,height=1,state='normal',command=lambda: reset_language_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 450,y_multiplier_integer,reset_language_button,True)

show_language_button = tk.Button(window, text='Show', width=5,height=1,state='normal',command=lambda: show_language_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 510,y_multiplier_integer,show_language_button)

def reset_language_list():
    language_list.clear()
    language_menu.configure(state='normal')
    language_var.set('')

def show_language_list():
    if len(language_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected language options.')
    else:
        mb.showwarning(title='Warning', message='The currently selected language options are:\n\n  ' + '\n  '.join(language_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

def activate_language_var():
    # Disable the + after clicking on it and enable the class menu
    add_language_button.configure(state='disabled')
    language_menu.configure(state='normal')

parser_var.set(1)
parser_checkbox = tk.Checkbutton(window, text='Stanza parser', variable=parser_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               parser_checkbox, True)

parser_menu_var.set("Dependency parser")
parser_menu = tk.OptionMenu(window, parser_menu_var, 'Constituency parser','Dependency parser')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               parser_menu)

def activate_SentenceTable(*args):
    if parser_var.get() == 0:
        parser_menu_var.set('')
        parser_menu.configure(state='disabled')
        # compute_sentence_var.set(0)
        CoNLL_table_analyzer_var.set(0)
    else:
        parser_menu_var.set('Dependency parser')
        parser_menu.configure(state='normal')
        # compute_sentence_var.set(1)
        CoNLL_table_analyzer_var.set(1)

CoNLL_table_analyzer_var.set(0)
CoNLL_table_analyzer_checkbox = tk.Checkbutton(window, text='CoNLL table analyzer', variable=CoNLL_table_analyzer_var,
                                               onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               CoNLL_table_analyzer_checkbox, True)
CoNLL_table_analyzer_checkbox_msg = tk.Label()
CoNLL_table_analyzer_checkbox_msg.config(text="Open the CoNLL table analyzer GUI")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               CoNLL_table_analyzer_checkbox_msg)

def check_CoNLL_table(*args):
    if CoNLL_table_analyzer_var.get() == 1:
        CoNLL_table_analyzer_checkbox_msg.config(text="Open CoNLL table analyzer GUI")
    else:
        CoNLL_table_analyzer_checkbox_msg.config(text="Do NOT open CoNLL table analyzer GUI")


CoNLL_table_analyzer_var.trace('w', check_CoNLL_table)

Stanza_annotators_checkbox = tk.Checkbutton(window, text='Stanza annotators', variable=Stanza_annotators_var,
                                             onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               Stanza_annotators_checkbox, True)

Stanza_annotators_menu_var.set("")
Stanza_annotators_menu = tk.OptionMenu(window, Stanza_annotators_menu_var,
        'Sentence splitter (with sentence length)',
        'Lemma annotator',
        'POS annotator',
        'NER annotator',
        'Sentiment analysis')

y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               Stanza_annotators_menu)


def activate_Stanza_annotators_menu(*args):
    if Stanza_annotators_var.get() == True:
        if parser_var.get():
            if 'POS' in Stanza_annotators_menu_var.get():
                mb.showinfo("Warning", "You have selected to run the CoreNLP parser AND the lemma/POS annotator. The parser already computes lemmas and POS tags.\n\nPlease, tick either the parser or the annotator checkbox.")
                Stanza_annotators_var.set(0)
                Stanza_annotators_menu_var.set('')
                return
        Stanza_annotators_menu.configure(state='normal')
        if '*' in Stanza_annotators_menu_var.get():
            y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 400,
                                                           y_multiplier_integer,True)
    else:
        Stanza_annotators_menu_var.set('')
        Stanza_annotators_menu.configure(state='disabled')

Stanza_annotators_var.trace('w', activate_Stanza_annotators_menu)
Stanza_annotators_menu_var.trace('w', activate_Stanza_annotators_menu)

activate_Stanza_annotators_menu()

CoreNLP_var.set(0)
CoreNLP_checkbox = tk.Checkbutton(window, text='Stanford CoreNLP - parsers and annotators (Open GUI)', variable=CoreNLP_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,CoreNLP_checkbox)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Stanford CoreNLP download': 'TIPS_NLP_Stanford CoreNLP download install run.pdf',
               'Stanford CoreNLP performance & accuracy':'TIPS_NLP_Stanford CoreNLP performance and accuracy.pdf',
               'Stanford CoreNLP parser': 'TIPS_NLP_Stanford CoreNLP parser.pdf',
               'Stanford CoreNLP memory issues': 'TIPS_NLP_Stanford CoreNLP memory issues.pdf',
               'NER (Named Entity Recognition)': 'TIPS_NLP_NER (Named Entity Recognition).pdf',
               'Stanford CoreNLP date extractor (NER normalized date)': 'TIPS_NLP_Stanford CoreNLP date extractor.pdf',
               'Stanford CoreNLP coreference resolution': 'TIPS_NLP_Stanford CoreNLP coreference resolution.pdf',
               'Excel - Enabling Macros': 'TIPS_NLP_Excel Enabling macros.pdf',
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
               'utf-8 encoding': 'TIPS_NLP_Text encoding.pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf',
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',
               'Things to do with words: Overall view': 'TIPS_NLP_Things to do with words Overall view.pdf',
               'Stanford CoreNLP supported languages':'TIPS_NLP_Stanford CoreNLP supported languages.pdf',
               'CoNLL Table': 'TIPS_NLP_Stanford CoreNLP CoNLL table.pdf',
               'POSTAG (Part of Speech Tags)': "TIPS_NLP_POSTAG (Part of Speech Tags) Stanford CoreNLP.pdf",
               'Gender annotator':'TIPS_NLP_Gender annotator.pdf',
               'Sentiment analysis':'TIPS_NLP_Sentiment analysis.pdf',
               'Noun Analysis': "IPS_NLP_Noun Analysis.pdf",
               'Verb Analysis': "TIPS_NLP_Verb Analysis.pdf",
               'Function Words Analysis': 'TIPS_NLP_Function Words Analysis.pdf',
               'Clause Analysis': 'TIPS_NLP_Clause analysis.pdf'}
               # 'Java download install run': 'TIPS_NLP_Java download install run.pdf',
# TIPS_options = 'utf-8 encoding', 'Excel - Enabling Macros', 'Excel smoothing data series', 'csv files - Problems & solutions', 'Stanford CoreNLP supported languages', 'Stanford CoreNLP performance & accuracy', 'Stanford CoreNLP download', 'Stanford CoreNLP parser', 'Stanford CoreNLP memory issues', 'Stanford CoreNLP date extractor (NER normalized date)', 'Stanford CoreNLP coreference resolution', 'Stanford CoreNLP OpenIE', 'CoNLL Table', 'POSTAG (Part of Speech Tags)', 'DEPREL (Stanford Dependency Relations)', 'NER (Named Entity Recognition)', 'Clause Analysis', 'Noun Analysis', 'Verb Analysis', 'Function Words Analysis', 'English Language Benchmarks' #, 'Java download install run'
TIPS_options = 'utf-8 encoding', 'Excel - Enabling Macros', 'Excel smoothing data series', 'csv files - Problems & solutions', 'Statistical measures', 'Stanford CoreNLP supported languages', 'Stanford CoreNLP performance & accuracy', 'Stanford CoreNLP download', 'Stanford CoreNLP parser', 'Stanford CoreNLP memory issues', 'Stanford CoreNLP date extractor (NER normalized date)', 'Stanford CoreNLP coreference resolution', 'CoNLL Table', 'POSTAG (Part of Speech Tags)', 'DEPREL (Stanford Dependency Relations)', 'NER (Named Entity Recognition)','Gender annotator','Sentiment analysis','Things to do with words: Overall view' #, 'Java download install run'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.

def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, click on the 'Pre-processing tools' button to open the GUI where you will be able to perform a variety of\n   file checking options (e.g., utf-8 encoding compliance of your corpus or sentence length);\n   file cleaning options (e.g., convert non-ASCII apostrophes & quotes and % to percent).\n\nNon utf-8 compliant texts are likely to lead to code breakdown in various algorithms.\n\nASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n\n% signs will lead to code breakdon of Stanford CoreNLP.\n\nSentences without an end-of-sentence marker (. ! ?) in Stanford CoreNLP will be processed together with the next sentence, potentially leading to very long sentences.\n\nSentences longer than 70 or 100 words may pose problems to Stanford CoreNLP (the average sentence length of modern English is 20 words). Please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "The Stanford CoreNLP performance is affected by various issues: memory size of your computer, document size, sentence length\n\nPlease, select the memory size Stanza will use. Default = 8. Lower this value if Stanza runs out of resources.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if your filenames embed a date (e.g., The New York Times_12-23-1992).\n\nWhen the date option is ticked, the script will add a date field to the CoNLL table. The date field will be used by other NLP scripts (e.g., Ngrams).\n\nOnce you have ticked the 'Filename embeds date' option, you will need to provide the follwing information:\n   1. the date format of the date embedded in the filename (default mm-dd-yyyy); please, select.\n   2. the character used to separate the date field embedded in the filenames from the other fields (e.g., _ in the filename The New York Times_12-23-1992) (default _); please, enter.\n   3. the position of the date field in the filename (e.g., 2 in the filename The New York Times_12-23-1992; 4 in the filename The New York Times_1_3_12-23-1992 where perhaps fields 2 and 3 refer respectively to the page and column numbers); please, select.\n\nIF THE FILENAME EMBEDS A DATE AND THE DATE IS THE ONLY FIELD AVAILABLE IN THE FILENAME (e.g., 2000.txt), enter . in the 'Date character separator' field and enter 1 in the 'Date position' field.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Stanza provides pretrained NLP models for a total 66 human languages. Please, using the dropdown menu, select the language to be used.\n\nIf your documents contain different languages, you have two options to ensure that the selected annotator will process your documents with the correct language model:\n\n   1. use the multilingual option at the end of the list of languages and let Stanza pick the right language model for the various parts of your document;\n   2. if you know the languages used in your documents, a better alternative that produces better results is for you to select the languages using the + widget."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to use the Stanza dependency parser to obtain a CoNLL table (CoNLL U format).\n\nThe CoNLL table is the basis of many of the NLP analyses: noun & verb analysis, function words, clause analysis, query CoNLL.\n\nIn output the scripts produce a CoNLL table with the following 9 fields: ID, FORM, LEMMA, POSTAG, NER (23 classes), HEAD, DEPREL, DEPS, CLAUSAL TAGS (the neural-network parser does not produce clausal tags).\n\nThe following fields will be automatically added to the standard 9 fields of a CoNLL table (CoNLL U format): RECORD NUMBER, DOCUMENT ID, SENTENCE ID, DOCUMENT (INPUT filename), DATE (if the filename embeds a date).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick/untick the checkbox if you want to open (or not) the CoNLL table analyzer GUI to analyze the CoreNLP parser results contained in the CoNLL table.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select one of the many other annotators available through Stanza: sentencce splitter, lemmatizer, POS, NER (Named Entity Recognition), and sentiment analysis.\n\nALL Stanza ANNOTATORS ARE BASED ON NEURAL NETWORK.\n\n\n\nIn INPUT the algorithms expect a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithms will produce a number of csv files and charts.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you want to open the GUI to run Stanford CoreNLP Java-based parsers and annotators.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), 0)

# change the value of the readMe_message
readMe_message = "These Python 3 scripts will perform different types of textual operations using Stanza. ALL ALGORITHMS ARE BASED ON NEURAL NETWORK. The main operation is text parsing to produce the CoNLL table (CoNLL U format).\n\nIn INPUT the algorithms expect a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithms will produce different file types: txt-format copies of the same input txt files for co-reference, csv for annotators."
readMe_command = lambda: GUI_IO_util.display_button_info("NLP Suite Help", readMe_message)

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
