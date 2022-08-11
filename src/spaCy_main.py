# Written by Roberto Franzosi

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "spaCy.py", ['tkinter', 'subprocess']) == False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_files_util
import IO_user_interface_util
import config_util
import reminders_util
import IO_internet_util
import Stanford_CoreNLP_annotator_util
import Stanford_CoreNLP_coreference_util
import CoNLL_util
import file_checker_util
import file_cleaner_util
import sentence_analysis_util

# RUN section ______________________________________________________________________________________________________________________________________________________

# https://stackoverflow.com/questions/45886128/unable-to-set-up-my-own-stanford-corenlp-server-with-error-could-not-delete-shu
# for the Error [Thread-0] INFO CoreNLP - CoreNLP Server is shutting down
# sometimes the error appears but processing actually continues; but rebooting should do the trick if processing does not continue

# dateInclude indicates whether there is date embedded in the file name.
# 1: included 0: not included
# def run(inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage, memory_var, date_extractor, split_files, quote_extractor, spaCy_gender_annotator, CoReference, manual_Coref, parser, parser_menu_var, dateInclude, sep, date_field_position, dateFormat, compute_sentence, CoNLL_table_analyzer_var):

def run(inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage,
        memory_var,
        manual_Coref, open_GUI, language_var, parser, parser_menu_var, dateInclude, sep, date_field_position, dateFormat,
        CoNLL_table_analyzer_var, spaCy_annotators_var, spaCy_annotators_menu_var,
        other_parsers_annotators_var, other_parsers_annotators_menu_var):

    filesToOpen = []
    outputCoNLLfilePath = ''

    # check internet connection
    if not IO_internet_util.check_internet_availability_warning("Stanford CoreNLP"):
        return

    if parser == 0 and CoNLL_table_analyzer_var == 0 and spaCy_annotators_var == 0 and other_parsers_annotators_var==0:
        mb.showinfo("Warning", "No options have been selected.\n\nPlease, select an option and try again.")
        return

    if parser == 0 and CoNLL_table_analyzer_var == 1:
        mb.showinfo("Warning", "You have selected to open the CoNLL table analyser GUI. This option expects to run the parser first.\n\nPlease, tick the CoreNLP parser checkbox and try again.")
        return

    if parser:
        if parser_menu_var == 'Constituency parser':
            # TODO MINO
            #   connect to Stanza annotator
            mb.showwarning('Warning',
                           'The selected option is not available yet. Sorry!\n\nPlease, select a different option and try again.')
            return
        annotator = 'depparse'

    if spaCy_annotators_var and spaCy_annotators_menu_var != '':
        if 'Sentence splitter (with sentence length)' in spaCy_annotators_menu_var:
            annotator = 'Sentence'
        elif 'Lemma annotator' in spaCy_annotators_menu_var:
            annotator = 'Lemma'
        elif 'POS annotator' in spaCy_annotators_menu_var:
            annotator = 'All POS'
        elif 'NER annotator' in spaCy_annotators_menu_var:  # NER annotator
            annotator = 'NER'
        elif 'Coreference' in spaCy_annotators_menu_var:
            # TODO MINO
            #   connect to spaCy annotator
            annotator = 'coref'
            mb.showwarning('Warning',
                           'The selected option is not available yet. Sorry!\n\nPlease, select a different option and try again.')
            return
        elif 'Sentiment analysis' in spaCy_annotators_menu_var:
            # TODO MINO
            #   connect to spaCy annotator
            annotator = 'sentiment'
            mb.showwarning('Warning',
                           'The selected option is not available yet. Sorry!\n\nPlease, select a different option and try again.')
            return
        elif 'Gender' in spaCy_annotators_menu_var or 'Normalized NER' in spaCy_annotators_menu_var or 'Gender' in spaCy_annotators_menu_var:
            mb.showwarning(title='Option not available n Stanza',
                           message='The ' + spaCy_annotators_menu_var + ' is not available in spaCy.\n\nTh annotator is available in Stanford CoreNLP. If you wish to run the annotator, please, open the Stanford CoreNLP GUI and run the annotator.')
        else:
            return

        tempOutputFiles = spaCy_annotator_util.spaCy_annotate(config_filename, inputFilename, inputDir,
                                                                       outputDir,
                                                                       openOutputFiles, createCharts, chartPackage,
                                                                       annotator, False, #'All POS',
                                                                       memory_var, document_length_var, limit_sentence_length_var,
                                                                       extract_date_from_filename_var=dateInclude,
                                                                       date_format=dateFormat,
                                                                       date_separator_var=sep,
                                                                       date_position_var=date_field_position,
                                                                       single_quote_var = single_quote,
                                                                       language = language_var)

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

    if other_parsers_annotators_var:
        if other_parsers_annotators_menu_var=="Stanford CoreNLP":
            call("python Stanford_CoreNLP_main.py", shell=True)
        elif other_parsers_annotators_menu_var=="Stanza":
                call("python Stanza_main.py", shell=True)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)


# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                 GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.create_chart_output_checkbox.get(),
                                 GUI_util.charts_dropdown_field.get(),
                                 memory_var.get(),
                                 manual_Coref_var.get(),
                                 open_GUI_var.get(),
                                 language_var.get(),
                                 parser_var.get(),
                                 parser_menu_var.get(),
                                 fileName_embeds_date.get(),
                                 date_separator_var.get(),
                                 date_position_var.get(),
                                 date_format.get(),
                                 CoNLL_table_analyzer_var.get(),
                                 spaCy_annotators_var.get(),
                                 spaCy_annotators_menu_var.get(),
                                 other_parsers_annotators_var.get(),
                                 other_parsers_annotators_menu_var.get())

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


GUI_label = 'Graphical User Interface (GUI) for spaCy'
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
    parser_var.set(1)
    parser_menu_var.set("Dependency parse")
    spaCy_annotators_var.set(0)
    spaCy_annotators_menu_var.set('')
    manual_Coref_checkbox.place_forget()  # invisible
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

language_var = tk.StringVar()
memory_var = tk.IntVar()
date_extractor_var = tk.IntVar()
split_files_var = tk.IntVar()
quote_extractor_var = tk.IntVar()
manual_Coref_var = tk.IntVar()
open_GUI_var = tk.IntVar()
parser_var = tk.IntVar()
parser_menu_var = tk.StringVar()
fileName_embeds_date = tk.IntVar()

date_format = tk.StringVar()
date_separator_var = tk.StringVar()
date_position_var = tk.IntVar()

CoNLL_table_analyzer_var = tk.IntVar()

spaCy_annotators_var = tk.IntVar()
spaCy_annotators_menu_var = tk.StringVar()

other_parsers_annotators_var = tk.IntVar()
other_parsers_annotators_menu_var = tk.StringVar()

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
memory_var.set(4)
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

language_var.set('English')
language_menu = tk.OptionMenu(window, language_var, 'Catalan', 'Chinese', 'Danish', 'Dutch', 'English', 'Finnish', 'French', 'German', 'Greek', 'Italian', 'Japanese', 'Korean', 'Lithuanian', 'Macedonian', 'Multi-language', 'Norwegian Bokmål', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Spanish', 'Swedish')
# language_menu.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+100,
                                               y_multiplier_integer, language_menu)

parser_var.set(1)
parser_checkbox = tk.Checkbutton(window, text='spaCy parser', variable=parser_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               parser_checkbox, True)

parser_menu_var.set("Dependency parse")
parser_menu = tk.OptionMenu(window, parser_menu_var, 'Dependency parse')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               parser_menu)

def activate_SentenceTable(*args):
    if parser_var.get() == 0:
        parser_menu_var.set('')
        parser_menu.configure(state='disabled')
        # compute_sentence_var.set(0)
        CoNLL_table_analyzer_var.set(0)
    else:
        parser_menu_var.set('Dependency parse')
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

spaCy_annotators_checkbox = tk.Checkbutton(window, text='spaCy annotators', variable=spaCy_annotators_var,
                                             onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               spaCy_annotators_checkbox, True)

spaCy_annotators_menu_var.set("")
spaCy_annotators_menu = tk.OptionMenu(window, spaCy_annotators_menu_var,
        'Sentence splitter (with sentence length)',
        'Lemma annotator',
        'POS annotator',
        'NER',
        'Coreference PRONOMINAL resolution',
        'Sentiment analysis',
        'Word2Vec',
       'SVO extraction (Subject-Verb-Object',
       '',
       'Gender annotator',
       'Normalized NER date annotator',
       'Quote/dialogue annotator')

y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               spaCy_annotators_menu)

manual_Coref_checkbox = tk.Checkbutton(window, text='Manual edit',
                                       variable=manual_Coref_var,
                                       onvalue=1, offvalue=0)

open_GUI_checkbox = tk.Checkbutton(window, text='Open coreference GUI',
                                       variable=open_GUI_var,
                                       onvalue=1, offvalue=0)

def activate_spaCy_annotators_menu(*args):
    global y_multiplier_integer, y_multiplier_integer_SV
    if spaCy_annotators_var.get() == True:
        if parser_var.get():
            if 'POS' in spaCy_annotators_menu_var.get():
                mb.showinfo("Warning", "You have selected to run the CoreNLP parser AND the lemma/POS annotator. The parser already computes lemmas and POS tags.\n\nPlease, tick either the parser or the annotator checkbox.")
                spaCy_annotators_var.set(0)
                spaCy_annotators_menu_var.set('')
                return
        spaCy_annotators_menu.configure(state='normal')

        if 'Coreference' in spaCy_annotators_menu_var.get():
            y_multiplier_integer=y_multiplier_integer-1
            manual_Coref_var.set(0)
            y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 400,
                                                           y_multiplier_integer,
                                                           manual_Coref_checkbox,True)

            open_GUI_var.set(0)
            y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 550,
                                                           y_multiplier_integer,
                                                           open_GUI_checkbox)
            open_GUI_checkbox.configure(state='normal')
            if input_main_dir_path.get()!='':
                manual_Coref_checkbox.configure(state='disabled')
            else:
                manual_Coref_checkbox.configure(state='normal')
        else:
            manual_Coref_checkbox.place_forget()  # invisible
            open_GUI_checkbox.place_forget()  # invisible
    else:
        manual_Coref_checkbox.place_forget()  # invisible
        open_GUI_checkbox.place_forget()  # invisible
        spaCy_annotators_menu_var.set('')
        spaCy_annotators_menu.configure(state='disabled')

spaCy_annotators_var.trace('w', activate_spaCy_annotators_menu)
spaCy_annotators_menu_var.trace('w', activate_spaCy_annotators_menu)

activate_spaCy_annotators_menu()

other_parsers_annotators_var.set(0)
other_parsers_annotators_checkbox = tk.Checkbutton(window, text='Other parsers and annotators (Open GUI)', variable=other_parsers_annotators_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,other_parsers_annotators_checkbox,True)

other_parsers_annotators_menu_var.set("Stanford CoreNLP")
other_parsers_annotators_menu = tk.OptionMenu(window, other_parsers_annotators_menu_var, 'Stanford CoreNLP', 'Stanza')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate()+50, y_multiplier_integer,
                                               other_parsers_annotators_menu)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Stanford CoreNLP download': 'TIPS_NLP_Stanford CoreNLP download install run.pdf',
               'Stanford CoreNLP performance & accuracy':'TIPS_NLP_Stanford CoreNLP performance and accuracy.pdf',
               'Stanford CoreNLP parser': 'TIPS_NLP_Stanford CoreNLP parser.pdf',
               'Stanford CoreNLP memory issues': 'TIPS_NLP_Stanford CoreNLP memory issues.pdf',
               'NER (Named Entity Recognition)': 'TIPS_NLP_NER (Named Entity Recognition).pdf',
               'Stanford CoreNLP date extractor (NER normalized date)': 'TIPS_NLP_Stanford CoreNLP date extractor.pdf',
               'Stanford CoreNLP OpenIE': 'TIPS_NLP_Stanford CoreNLP OpenIE.pdf',
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
               'Quote annotator':'',
               'Normalized NER date annotator':'TIPS_NLP_Stanford CoreNLP date extractor.pdf',
               'Sentiment analysis':'TIPS_NLP_Sentiment analysis.pdf',
               'Noun Analysis': "IPS_NLP_Noun Analysis.pdf",
               'Verb Analysis': "TIPS_NLP_Verb Analysis.pdf",
               'Function Words Analysis': 'TIPS_NLP_Function Words Analysis.pdf',
               'Clause Analysis': 'TIPS_NLP_Clause analysis.pdf'}
               # 'Java download install run': 'TIPS_NLP_Java download install run.pdf',
# TIPS_options = 'utf-8 encoding', 'Excel - Enabling Macros', 'Excel smoothing data series', 'csv files - Problems & solutions', 'Stanford CoreNLP supported languages', 'Stanford CoreNLP performance & accuracy', 'Stanford CoreNLP download', 'Stanford CoreNLP parser', 'Stanford CoreNLP memory issues', 'Stanford CoreNLP date extractor (NER normalized date)', 'Stanford CoreNLP coreference resolution', 'Stanford CoreNLP OpenIE', 'CoNLL Table', 'POSTAG (Part of Speech Tags)', 'DEPREL (Stanford Dependency Relations)', 'NER (Named Entity Recognition)', 'Clause Analysis', 'Noun Analysis', 'Verb Analysis', 'Function Words Analysis', 'English Language Benchmarks' #, 'Java download install run'
TIPS_options = 'utf-8 encoding', 'Excel - Enabling Macros', 'Excel smoothing data series', 'csv files - Problems & solutions', 'Statistical measures', 'Stanford CoreNLP supported languages', 'Stanford CoreNLP performance & accuracy', 'Stanford CoreNLP download', 'Stanford CoreNLP parser', 'Stanford CoreNLP memory issues', 'Stanford CoreNLP date extractor (NER normalized date)', 'Stanford CoreNLP coreference resolution', 'Stanford CoreNLP OpenIE', 'CoNLL Table', 'POSTAG (Part of Speech Tags)', 'DEPREL (Stanford Dependency Relations)', 'NER (Named Entity Recognition)','Gender annotator','Quote annotator','Normalized NER date annotator','Sentiment analysis','Things to do with words: Overall view' #, 'Java download install run'

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
                                  "Please, select the memory size spaCy will use. Default = 8. Lower this value if spaCy runs out of resources.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if your filenames embed a date (e.g., The New York Times_12-23-1992).\n\nWhen the date option is ticked, the script will add a date field to the CoNLL table. The date field will be used by other NLP scripts (e.g., Ngrams).\n\nOnce you have ticked the 'Filename embeds date' option, you will need to provide the follwing information:\n   1. the date format of the date embedded in the filename (default mm-dd-yyyy); please, select.\n   2. the character used to separate the date field embedded in the filenames from the other fields (e.g., _ in the filename The New York Times_12-23-1992) (default _); please, enter.\n   3. the position of the date field in the filename (e.g., 2 in the filename The New York Times_12-23-1992; 4 in the filename The New York Times_1_3_12-23-1992 where perhaps fields 2 and 3 refer respectively to the page and column numbers); please, select.\n\nIF THE FILENAME EMBEDS A DATE AND THE DATE IS THE ONLY FIELD AVAILABLE IN THE FILENAME (e.g., 2000.txt), enter . in the 'Date character separator' field and enter 1 in the 'Date position' field.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Stanza provides pretrained NLP models for a total 22 human languages. Please, using the dropdown menu, select the language to be used."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to use the spaCY neural network dependency parser to obtain a CoNLL table (CoNLL U format).\n\nThe CoNLL table is the basis of many of the NLP analyses: noun & verb analysis, function words, clause analysis, query CoNLL.\n\nIn output the scripts produce a CoNLL table with the following 9 fields: ID, FORM, LEMMA, POSTAG, NER (23 classes), HEAD, DEPREL, DEPS, CLAUSAL TAGS (the neural-network parser does not produce clausal tags).\n\nThe following fields will be automatically added to the standard 9 fields of a CoNLL table (CoNLL U format): RECORD NUMBER, DOCUMENT ID, SENTENCE ID, DOCUMENT (INPUT filename), DATE (if the filename embeds a date).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick/untick the checkbox if you want to open (or not) the CoNLL table analyzer GUI to analyze the CoreNLP parser results contained in the CoNLL table.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select one of the many other annotators available through spaCy: Coreference pronominal resolution, DepRel, POS, NER (Named Entity Recognition), and sentiment analysis.\n\nALL ANNOTATORS ARE BASED ON NEURAL NETWORKS.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you want to open the GUI to run other parsers and annotatators available in the NLP Suite: Stanford CoreNLP Java-based parsers and annotators & the Python-based Stanza. Use the dropdown menu to select the GUI you wish to open.\n\nCoreNLP does not use neural networks for all its parsers and annotators, contrary to spaCy and Stanza.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), 0)

# change the value of the readMe_message
readMe_message = "These Python 3 scripts will perform different types of textual operations using spaCy. ALL ALGORITHMS ARE BASED ON NEURAL NETWORK. The main operation is text parsing to produce the CoNLL table (CoNLL U format).\n\nIn INPUT the algorithms expect a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithms will produce different file types: txt-format copies of the same input txt files for co-reference, csv for annotators."
readMe_command = lambda: GUI_IO_util.display_button_info("NLP Suite Help", readMe_message)

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

mb.showwarning(title='Option not available yet!',message='The spaCy GUI and algorithms are currently under development. None of the options will work. Sorry!')
GUI_util.window.mainloop()
