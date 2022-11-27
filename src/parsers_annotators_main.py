# Written by Roberto Franzosi

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "parsers_annotators_main", ['tkinter', 'subprocess']) == False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_files_util
import config_util
import reminders_util
import Stanford_CoreNLP_util
import Stanford_CoreNLP_coreference_util
import Stanza_util
import spaCy_util

# RUN section ______________________________________________________________________________________________________________________________________________________

# https://stackoverflow.com/questions/45886128/unable-to-set-up-my-own-stanford-corenlp-server-with-error-could-not-delete-shu
# for the Error [Thread-0] INFO CoreNLP - CoreNLP Server is shutting down
# sometimes the error appears but processing actually continues; but rebooting should do the trick if processing does not continue

# dateInclude indicates whether there is date embedded in the file name.
# 1: included 0: not included

def run(inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage,
        manual_Coref, open_GUI,
        parser_var,
        parser_menu_var,
        single_quote,
        CoNLL_table_analyzer_var, annotators_var, annotators_menu_var):

    filesToOpen = []
    outputCoNLLfilePath = ''

    if '--------------' in annotators_menu_var:
        mb.showwarning(title='Only a label',message='Your annotator selection is invalid. It is only a label to make readability of menu options easier.\n\nPlease, select a different option and try again.')
        return

    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = \
        config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]
    if package_display_area_value == '':
        mb.showwarning(title='No setup for NLP package and language',
                       message="The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again.")
        return

    # get the date options from filename
    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        temp_config_filename = 'NLP_default_IO_config.csv'
    else:
        temp_config_filename = scriptName.replace('main.py', 'config.csv')
    extract_date_from_filename_var, date_format_var, date_separator_var, date_position_var = \
        config_util.get_date_options(temp_config_filename, config_input_output_numeric_options)
    extract_date_from_text_var = 0

    if parser_var == 0 and CoNLL_table_analyzer_var == 1:
        mb.showinfo("Warning", "You have selected to open the CoNLL table analyser GUI. This option expects to run the parser first.\n\nPlease, tick the CoreNLP parser checkbox and try again.")
        return

    if annotators_var and annotators_menu_var == '':
        mb.showinfo("Warning", "You have selected to run a CoreNLP annotator but no annotator has been selected.\n\nPlease, select an annotator and try try again.")
        return

    if annotators_menu_var == 'Word embeddings (Word2Vec)':
        mb.showinfo("Warning", "The 'Word embeddings (Word2Vec)' annotator is not available yet for either BERT or spaCy. Sorry!\n\nPlease, select an annotator and try try again.")
        return

# Stanford CoreNLP ---------------------------------------------------------------------------
    if package=='Stanford CoreNLP':
        if parser_var or (annotators_var and annotators_menu_var != ''):
            annotator = []
            if IO_libraries_util.check_inputPythonJavaProgramFile('Stanford_CoreNLP_util.py') == False:
                return

            if parser_var:
                if 'PCFG' in parser_menu_var:
                    annotator='parser (pcfg)'
                elif parser_menu_var == 'Neural Network':
                    annotator='parser (nn)'
            else:
                if annotators_var and annotators_menu_var != '':
                    if 'NER (Open GUI)' in annotators_menu_var: # NER annotator
                        if IO_libraries_util.check_inputPythonJavaProgramFile('NER_main.py') == False:
                            return
                        call("python NER_main.py", shell=True)
                    elif 'Sentence splitter (with sentence length)' in annotators_menu_var:
                        annotator = 'Sentence'
                    elif 'Lemma annotator' in annotators_menu_var:
                        annotator = 'Lemma'
                    elif 'POS annotator' in annotators_menu_var:
                        annotator = 'All POS'
                    elif 'Gender' in annotators_menu_var:
                        annotator = 'gender'
                    elif 'Quote' in annotators_menu_var:
                        annotator = 'quote'
                    elif 'Normalized' in annotators_menu_var:
                        annotator = 'normalized-date'
                    elif '*' in annotators_menu_var:
                        annotator = ['gender','normalized-date','quote']
                    elif 'Sentiment analysis' in annotators_menu_var:
                        annotator = ['sentiment']
                    elif 'SVO' in annotators_menu_var:
                        annotator = ['SVO']
                    elif 'OpenIE' in annotators_menu_var:
                        annotator = ['OpenIE']
                    elif 'Coreference PRONOMINAL resolution' in annotators_menu_var:
                        annotator = []
                        if IO_libraries_util.check_inputPythonJavaProgramFile(
                                "Stanford_CoreNLP_coReference_util.py") == False:
                            return
                        file_open, error_indicator = Stanford_CoreNLP_coreference_util.run(config_filename, inputFilename,
                                                                                           inputDir,
                                                                                           outputDir, openOutputFiles,
                                                                                           createCharts, chartPackage,
                                                                                           language, memory_var,
                                                                                           export_json_var,
                                                                                           manual_Coref)

                        if error_indicator != 0:
                            mb.showinfo("Coreference Resolution Error",
                                        "Since Stanford CoreNLP Co-Reference Resolution throws error, " +
                                        "and you either didn't choose manual Co-Reference Resolution or manual Co-Referenece Resolution fails as well, the process ends now.")
                        filesToOpen.append(file_open)
                    else:
                        return

            if len(annotator)>0:
                tempOutputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                               outputDir,
                                                                               openOutputFiles, createCharts, chartPackage,
                                                                               annotator, False, #'All POS',
                                                                               language, export_json_var, memory_var, document_length_var, limit_sentence_length_var,
                                                                               extract_date_from_filename_var=extract_date_from_filename_var,
                                                                               date_format=date_format_var,
                                                                               date_separator_var=date_separator_var,
                                                                               date_position_var=date_position_var,
                                                                               single_quote_var = single_quote)

                if len(tempOutputFiles)>0:
                    filesToOpen.append(tempOutputFiles)
                    if 'parser' in annotator:
                        reminders_util.checkReminder(config_filename,
                                                     reminders_util.title_options_CoreNLP_NER_tags,
                                                     reminders_util.message_CoreNLP_NER_tags,
                                                     True)

# spaCy ---------------------------------------------------------------------------
    if package == 'spaCy':
        if parser_var or (annotators_var and annotators_menu_var != ''):
            if IO_libraries_util.check_inputPythonJavaProgramFile(
                    'spaCy_util.py') == False:
                return

        if parser_var:
            # if parser_menu_var == 'Dependency parser':
            #     mb.showwarning('Warning',
            #                    'The selected option is not available yet. Sorry!\n\nPlease, select a different option and try again.')
            #     return
            annotator = 'depparse'

        if annotators_var:
            if annotators_menu_var == '':
                mb.showwarning('Warning',
                               'The option of running a spaCy annotator has been selected but no annotaor has been selected.\n\nPlease, select an annotator option and try again.')
                return
            if 'Sentence splitter (with sentence length)' in annotators_menu_var:
                annotator = 'Sentence'
            elif 'Lemma annotator' in annotators_menu_var:
                annotator = 'Lemma'
            elif 'POS annotator' in annotators_menu_var:
                annotator = 'All POS'
            elif 'NER annotator' in annotators_menu_var:  # NER annotator
                annotator = 'NER'
            elif 'Sentiment analysis' in annotators_menu_var:
                annotator = 'sentiment'
            elif 'SVO extraction' in annotators_menu_var:
                annotator = 'SVO'
            elif 'Gender' in annotators_menu_var or 'Quote' in annotators_menu_var or 'Normalized NER' in annotators_menu_var or 'Gender' in annotators_menu_var or 'OpenIE' in annotators_menu_var:
                mb.showwarning(title='Option not available in spaCy',
                               message='The ' + annotators_menu_var + ' is not available in spaCy.\n\nThe annotator is available in Stanford CoreNLP. If you wish to run the annotator, please, using the Setup dropdown menu at the bottom of this GUI, select the Setup NLP package and corpus language option and select Stanford CoreNLP as your default package and try again.')
                return
            else:
                mb.showwarning('Warning',
                               'The selected option ' + annotators_menu_var + ' is not available in spaCy (yet).\n\nPlease, select another annotator and try again.')
                return

        document_length_var = 1
        limit_sentence_length_var = 1000
        tempOutputFiles = spaCy_util.spaCy_annotate(config_filename, inputFilename, inputDir,
                                                    outputDir,
                                                    openOutputFiles,
                                                    createCharts, chartPackage,
                                                    annotator, False,
                                                    language,
                                                    memory_var, document_length_var, limit_sentence_length_var,
                                                    extract_date_from_filename_var=extract_date_from_filename_var,
                                                    date_format=date_format_var,
                                                    date_separator_var=date_separator_var,
                                                    date_position_var=date_position_var)

        if tempOutputFiles == None:
            return

        if len(tempOutputFiles) > 0:
            filesToOpen.append(tempOutputFiles)
            if 'parser' in annotator:
                reminders_util.checkReminder(config_filename,
                                             reminders_util.title_options_CoreNLP_NER_tags,
                                             reminders_util.message_CoreNLP_NER_tags,
                                             True)

# Stanza ---------------------------------------------------------------------------

    if package == 'Stanza':
        if parser_var or (annotators_var and annotators_menu_var != ''):

            if IO_libraries_util.check_inputPythonJavaProgramFile(
                    'Stanza_util.py') == False:
                return
        if parser_var:
            if parser_menu_var == 'Constituency parser':
                mb.showwarning('Warning',
                               'The selected option "' + parser_menu_var + '" is not available yet in the NLP Suite implementation of ' + package +'. Sorry!\n\nPlease, select a different option and try again.')
                return
            annotator = 'depparse'

        if annotators_var:
            if annotators_menu_var == '':
                mb.showwarning('Warning',
                               'The option of running a Stanza annotator has been selected but no annotaor has been selected.\n\nPlease, select an annotator option and try again.')
                return
            if 'Sentence splitter (with sentence length)' in annotators_menu_var:
                annotator = 'Sentence'
            elif 'Lemma annotator' in annotators_menu_var:
                annotator = 'Lemma'
            elif 'POS annotator' in annotators_menu_var:
                annotator = 'All POS'
            elif 'NER annotator' in annotators_menu_var:  # NER annotator
                annotator = 'NER'
            elif 'Sentiment analysis' in annotators_menu_var:
                annotator = 'sentiment'
            elif 'SVO extraction' in annotators_menu_var:
                annotator = 'SVO'
            elif 'Gender' in annotators_menu_var or 'Quote' in annotators_menu_var or 'Normalized NER' in annotators_menu_var or 'Gender' in annotators_menu_var or 'OpenIE' in annotators_menu_var:
                mb.showwarning(title='Option not available in Stanza',
                               message='The ' + annotators_menu_var + ' is not available in Stanza.\n\nThe annotator is available in Stanford CoreNLP. If you wish to run the annotator, please, using the Setup dropdown menu at the bottom of this GUI, select the Setup NLP package and corpus language option and select Stanford CoreNLP as your default package and try again.')
                return
            else:
                mb.showwarning('Warning',
                               'The selected option ' + annotators_menu_var + ' is not available in Stanza (yet).\n\nPlease, select another annotator and try again.')
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
                                                      extract_date_from_filename_var=extract_date_from_filename_var,
                                                      date_format=date_format_var,
                                                      date_separator_var=date_separator_var,
                                                      date_position_var=date_position_var)

        if tempOutputFiles == None:
            return

        if len(tempOutputFiles) > 0:
            filesToOpen.append(tempOutputFiles)
            if 'parser' in annotator:
                reminders_util.checkReminder(config_filename,
                                             reminders_util.title_options_CoreNLP_NER_tags,
                                             reminders_util.message_CoreNLP_NER_tags,
                                             True)

    # CoNLL table analyzer
    if CoNLL_table_analyzer_var:
        if IO_libraries_util.check_inputPythonJavaProgramFile('CoNLL_table_analyzer_main.py') == False:
            return
        # open the analyzer having saved the new parser output in config so that it opens the right input file
        config_filename_temp = 'conll_table_analyzer_config.csv'
        config_input_output_numeric_options_temp=[1, 0, 0, 1]
        # TODO Roby must pass the correct config_input_output_alphabetic_options
        config_input_output_alphabetic_options = [str(tempOutputFiles[0]), '','',outputDir,date_format_var,date_separator_var,date_position_var]
        config_util.write_IO_config_file(GUI_util.window, config_filename_temp, config_input_output_numeric_options_temp, config_input_output_alphabetic_options, True)

        reminders_util.checkReminder(config_filename,
                                     reminders_util.title_options_CoNLL_analyzer,
                                     reminders_util.message_CoNLL_analyzer,
                                     True)

        call("python CoNLL_table_analyzer_main.py", shell=True)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated

run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                 GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.create_chart_output_checkbox.get(),
                                 GUI_util.charts_package_options_widget.get(),
                                 manual_Coref_var.get(),
                                 open_GUI_var.get(),
                                 parser_var.get(),
                                 parser_menu_var.get(),
                                 quote_var.get(),
                                 CoNLL_table_analyzer_var.get(),
                                 annotators_var.get(),
                                 annotators_menu_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=440, # height at brief display
                             GUI_height_full=520, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label = 'Graphical User Interface (GUI) for NLP parsers & annotators'
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

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path


def clear(e):
    # package.set('Stanford CoreNLP')
    # language.set("English")
    parser_var.set(1)
    parser_menu_var.set("Probabilistic Context Free Grammar (PCFG)")
    annotators_var.set(0)
    annotators_menu_var.set('')
    manual_Coref_checkbox.place_forget()  # invisible
    open_GUI_checkbox.place_forget()  # invisible
    quote_checkbox.place_forget()  # invisible
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

package = tk.StringVar()
language = tk.StringVar()
language_list = []
CoreNLP_gender_annotator_var = tk.IntVar()
split_files_var = tk.IntVar()
quote_extractor_var = tk.IntVar()
manual_Coref_var = tk.IntVar()
open_GUI_var = tk.IntVar()
parser_var = tk.IntVar()
parser_menu_var = tk.StringVar()


CoNLL_table_analyzer_var = tk.IntVar()

annotators_var = tk.IntVar()
annotators_menu_var = tk.StringVar()

quote_var = tk.IntVar()
y_multiplier_integer_SV=0 # used to set the parser widget on the proper GUI line
y_multiplier_integer_SV1=0 # used to set the quote_var widget and coref widget on the proper GUI line

def open_GUI(param):
    if 'preprocess' in param:
        call('python file_checker_converter_cleaner_main.py',shell=True)
    else:
        call('python coreference_main.py',shell=True)

pre_processing_button = tk.Button(window, width=GUI_IO_util.widget_width_short, text='Pre-processing tools: file checking & cleaning (Open GUI)',command=lambda: open_GUI('preprocess'))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   pre_processing_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")
coreference_button = tk.Button(window, width=GUI_IO_util.widget_width_short, text='Coreference resolution (Open GUI)',command=lambda: open_GUI('coref'))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   coreference_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

y_multiplier_integer_SV=y_multiplier_integer

parser_checkbox = tk.Checkbutton(window, variable=parser_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer_SV,
                                               parser_checkbox, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "If you wish to change the NLP package used (spaCy, Stanford CoreNLP, Stanza) and their available parsers, use the Setup dropdown menu at the bottom of this GUI")

available_parsers=''

parser_var.set(1)

parsers=[]

if len(parsers) == 0:
    parser_menu = tk.OptionMenu(window, parser_menu_var, parsers)
    # parser_menu.configure(width=50)
else:
    parser_menu = tk.OptionMenu(window, parser_menu_var, *parsers)
    # parser_menu.configure(width=50)
#     # place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.parsers_annotators_parser_menu_pos,
                                               y_multiplier_integer,
                                               parser_menu, False, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "If you wish to change the NLP package used (spaCy, Stanford CoreNLP, Stanza) and their available parsers, use the Setup dropdown menu at the bottom of this GUI")

def activate_SentenceTable(*args):
    global parser_menu
    if parser_var.get() == 0:
        parser_menu_var.set('')
        # parser_menu.configure(width=50, state='disabled')
        parser_menu.configure(state='disabled')
        # compute_sentence_var.set(0)
        CoNLL_table_analyzer_var.set(0)
    else:
        parser_menu_var.set('Probabilistic Context Free Grammar (PCFG)')
        # parser_menu.configure(width=50, state='normal')
        parser_menu.configure(state='normal')
        # compute_sentence_var.set(1)
        CoNLL_table_analyzer_var.set(1)

CoNLL_table_analyzer_var.set(0)
CoNLL_table_analyzer_checkbox = tk.Checkbutton(window, text='CoNLL table analyzer', variable=CoNLL_table_analyzer_var,
                                               onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               CoNLL_table_analyzer_checkbox, True)
CoNLL_table_analyzer_checkbox_msg = tk.Label()
CoNLL_table_analyzer_checkbox_msg.config(text="Open the CoNLL table analyzer GUI")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.parsers_annotators_parser_open_CoNLL_pos, y_multiplier_integer,
                                               CoNLL_table_analyzer_checkbox_msg)

def check_CoNLL_table(*args):
    if CoNLL_table_analyzer_var.get() == 1:
        CoNLL_table_analyzer_checkbox_msg.config(text="Open CoNLL table analyzer GUI")
    else:
        CoNLL_table_analyzer_checkbox_msg.config(text="Do NOT open CoNLL table analyzer GUI")
CoNLL_table_analyzer_var.trace('w', check_CoNLL_table)

check_CoNLL_table()

Annotators_checkbox = tk.Checkbutton(window, text='Annotators', variable=annotators_var,
                                             onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               Annotators_checkbox, True)

annotators_menu_var.set("")
annotators_menu_var.set("")
annotators_menu = tk.OptionMenu(window, annotators_menu_var,
        'Fundamental NLP tools (via BERT, CoreNLP, spaCy, Stanza) -------------------------------------',
        '   Sentence splitter (with sentence length)',
        '   Lemma annotator',
        '   POS annotator',
        '   NER (Open GUI)',
        'Special annotators (via BERT, CoreNLP, spaCy, Stanza) -----------------------------------------',
        '   Coreference PRONOMINAL resolution (via BERT, CoreNLP, spaCy Neural Network)',
        '   Sentiment analysis (Neural Network)',
        '   OpenIE - Relation triples extractor (via CoreNLP Neural Network)',
        '   SVO extraction (via CoreNLP, spaCy, Stanza)',
        '   Word embeddings (Word2Vec) (via BERT, Gensim, spaCy)',
        'More special annotators (CoreNLP only) --------------------------------------------------------',
        '   Gender annotator (via CoreNLP Neural Network)',
        '   Normalized NER date annotator (via CoreNLP)',
        '   Quote/dialogue annotator (via CoreNLP Neural Network)')

y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.parsers_annotators_parser_annotator_pos, y_multiplier_integer,
                                               annotators_menu)

y_multiplier_integer_SV1=y_multiplier_integer

manual_Coref_checkbox = tk.Checkbutton(window, text='Manual edit',
                                       variable=manual_Coref_var,
                                       onvalue=1, offvalue=0)

open_GUI_checkbox = tk.Checkbutton(window, text='Open coreference GUI',
                                       variable=open_GUI_var,
                                       onvalue=1, offvalue=0)

quote_checkbox = tk.Checkbutton(window, text='Include single quotes',
                                       variable=quote_var,
                                       onvalue=1, offvalue=0)

def activate_annotators_menu(*args):
    global y_multiplier_integer, y_multiplier_integer_SV1
    if parser_var.get()==True and (annotators_var.get()==True and annotators_menu_var.get()!=''):
        mb.showinfo("Warning", "You have selected to run BOTH the CoreNLP parser AND the annotator '" + annotators_menu_var.get().lstrip() + "'.\n\nPlease, select one or the other and try again.")
        return
    if annotators_var.get() == True:
            # if 'POS' in annotators_menu_var.get():
            #     mb.showinfo("Warning", "You have selected to run the CoreNLP parser AND the lemma/POS annotator. The parser already computes lemmas and POS tags.\n\nPlease, tick either the parser or the annotator checkbox.")
            #     annotators_var.set(0)
            #     annotators_menu_var.set('')
            #     return
        annotators_menu.configure(state='normal')
        if y_multiplier_integer_SV1 == 0:
            y_multiplier_integer_SV1 = y_multiplier_integer
        if '*' in annotators_menu_var.get() or 'dialogue' in annotators_menu_var.get():
            y_multiplier_integer=y_multiplier_integer_SV1-1
            quote_var.set(0)
            y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.parsers_annotators_parser_col2_pos,
                                                           y_multiplier_integer,
                                                           quote_checkbox,True)
            quote_checkbox.configure(state='normal')
        else:
            quote_checkbox.place_forget()  # invisible

        if 'Coreference' in annotators_menu_var.get():
            y_multiplier_integer=y_multiplier_integer_SV1-1
            manual_Coref_var.set(0)
            y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.parsers_annotators_parser_manual_coref_edit_pos,
                                                           y_multiplier_integer,
                                                           manual_Coref_checkbox,True)

            open_GUI_var.set(0)
            y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.parsers_annotators_parser_openGUI_pos,
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
        annotators_menu_var.set('')
        annotators_menu.configure(state='disabled')
parser_var.trace('w', activate_annotators_menu)
annotators_var.trace('w', activate_annotators_menu)
annotators_menu_var.trace('w', activate_annotators_menu)

activate_annotators_menu()

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
TIPS_options = 'utf-8 encoding', 'Excel - Enabling Macros', 'Excel smoothing data series', 'csv files - Problems & solutions', 'Statistical measures', 'English Language Benchmarks', 'Things to do with words: Overall view', 'Stanford CoreNLP supported languages', 'Stanford CoreNLP performance & accuracy', 'Stanford CoreNLP download', 'Stanford CoreNLP parser', 'Stanford CoreNLP memory issues', 'Stanford CoreNLP date extractor (NER normalized date)', 'Stanford CoreNLP coreference resolution', 'Stanford CoreNLP OpenIE', 'CoNLL Table', 'POSTAG (Part of Speech Tags)', 'DEPREL (Stanford Dependency Relations)', 'NER (Named Entity Recognition)','Gender annotator','Quote annotator','Normalized NER date annotator','Sentiment analysis','Things to do with words: Overall view' #, 'Java download install run'

# add all the lines to the end to every special GUI
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
                                  "Please, click on the 'Coreference resolution' button to open the GUI where you will be able to perform coreference resolution of your input document(s).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to use the CoreNLP parser to obtain a CoNLL table (CoNLL U format).\n\nThe CoNLL table is the basis of many of the NLP analyses: noun & verb analysis, function words, clause analysis, query CoNLL.\n\nYou have a choice between two types of papers:\n   1. the recommended default Probabilistic Context Free Grammar (PCFG) parser;\n   2. a Neural-network dependency parser.\n\nThe neural network approach is more accurate but much slower.\n\nIn output the scripts produce a CoNLL table with the following 9 fields: ID, FORM, LEMMA, POSTAG, NER (23 classes), HEAD, DEPREL, DEPS, CLAUSAL TAGS (the neural-network parser does not produce clausal tags).\n\nThe following fields will be automatically added to the standard 9 fields of a CoNLL table (CoNLL U format): RECORD NUMBER, DOCUMENT ID, SENTENCE ID, DOCUMENT (INPUT filename), DATE (if the filename embeds a date).\n\nIf you suspect that CoreNLP may have given faulty results for some sentences, you can test those sentences directly on the Stanford CoreNLP website at https://corenlp.run")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick/untick the checkbox if you want to open (or not) the CoNLL table analyzer GUI to analyze the CoreNLP parser results contained in the CoNLL table.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select one of the many other annotators available through Stanford CoreNLP: Coreference pronominal resolution, DepRel, POS, NER (Named Entity Recognition), NER normalized date. gender, quote, and sentiment analysis.\n\nANNOTATORS MARKED AS NEURAL NETWORK ARE MORE ACCURATE, BUT SLOW AND REQUIRE A GREAT DEAL OF MEMORY.\n\n1.  PRONOMINAL co-reference resolution refers to such cases as 'John said that he would...'; 'he' would be substituted by 'John'. CoreNLP can resolve other cases but the algorithm here is restricted to pronominal resolution.\n\nThe co-reference resolution checkbox is disabled when selected an entire directory in input. The co-reference resolution algorithm is a memory hog. You may not have enough memory on your machine.\n\nTick the checkbox Manually edit coreferenced document if you wish to resolve manually cases of unresolved or wrongly resolved coreferences. MANUAL EDITING REQUIRES A LOT OF MEMORY SINCE BOTH ORIGINAL AND CO-REFERENCED FILE ARE BROUGHT IN MEMORY. DEPENDING UPON FILE SIZES, YOU MAY NOT HAVE ENOUGH MEMORY FOR THIS STEP.\n\nTick the Open GUI checkbox to open the specialized GUI for pronominal coreference resolution.\n\n2.  The CoreNLP NER annotator recognizes the following NER values:\n  named (PERSON, LOCATION, ORGANIZATION, MISC);\n  numerical (MONEY, NUMBER, ORDINAL, PERCENT);\n  temporal (DATE, TIME, DURATION, SET).\n  In addition, via regexner, the following entity classes are tagged: EMAIL, URL, CITY, STATE_OR_PROVINCE, COUNTRY, NATIONALITY, RELIGION, (job) TITLE, IDEOLOGY, CRIMINAL_CHARGE, CAUSE_OF_DEATH.\n\n3.  The NER NORMALIZED DATE annotator extracts standard dates from text in the yyyy-mm-dd format (e.g., 'the day before Christmas' extracted as 'xxxx-12-24').\n\n4.  The CoreNLP coref GENDER annotator extracts the gender of both first names and personal pronouns (he, him, his, she, her, hers) using a neural network approach. This annotator requires a great deal of memory. So, please, adjust the memory allowing as much memory as you can afford.\n\n5.  The CoreNLP QUOTE annotator extracts quotes from text and attributes the quote to the speaker. The default CoreNLP parameter is DOUBLE quotes. If you want to process both DOUBLE and SINGLE quotes, plase tick the checkbox 'Include single quotes.'\n\n6.  The SENTIMENT ANALYSIS annotator computes the sentiment values (negative, neutral, positive) of each sentence in a text.\n\n6.  The OpenIE (Open Information Extraction) annotator extracts  open-domain relation triples, representing a subject, a relation, and the object of the relation.\n\n\n\nIn INPUT the algorithms expect a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithms will produce a number of csv files  and Excel charts. The Gender annotator will also produce an html file with male tags displayed in blue and female tags displayed in red. The Coreference annotator will produce txt-format copies of the same input txt files but co-referenced.\n\Select * to run Gender annotator (Neural Network), Normalized NER date, and Quote/dialogue annotator (Neural Network).")
    # y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
    #                               "Please, tick the checkbox if you want to open the GUI to run other parsers and annotatators available in the NLP Suite: spaCy & Stanza. Use the dropdown menu to select the GUI you wish to open.\n\nBoth spaCy and Stanza use neural networks for all their parsers and annotators. spcaCy is also lighting fast.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

# change the value of the readMe_message
readMe_message = "This Python 3 script will perform different types of textual operations using a selected NLP package (e.g., spaCy, Stanford CoreNLP, Stanza). The main operation is text parsing to produce the CoNLL table (CoNLL U format).\n\nYOU MUST BE CONNETED TO THE INTERNET TO RUN THE SCRIPTS.\n\nIn INPUT the algorithms expect a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithms will produce different file types: txt-format copies of the same input txt files for co-reference, csv for annotators (HTML for gender annotator)."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName, False)

def activate_NLP_options(*args):
    global error, parsers, available_parsers, parser_lb, package, package_display_area_value, language, language_list, y_multiplier_integer
    error, package, parsers, package_basics, language, package_display_area_value, package_display_area_value_new, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = GUI_util.handle_setup_options(y_multiplier_integer, scriptName)
    if package != '':
        available_parsers = 'Parsers for ' + package # + '                          '
    else:
        available_parsers = 'Parsers'
    if package_display_area_value_new != package_display_area_value:
        language_list = [language]
        parser_menu_var.set(parsers[0])
        m = parser_menu["menu"]
        m.delete(0, "end")
        for s in parsers:
            s=s.lstrip() # remove leading blanks since parsers are separated by ,blank
            m.add_command(label=s, command=lambda value=s: parser_menu_var.set(value))
    parser_lb = tk.Label(window, text=available_parsers)
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.parsers_annotators_parser_lb_pos,
                                                   y_multiplier_integer_SV,
                                                   parser_lb, True, False, False, False, 90,
                                                   GUI_IO_util.labels_x_coordinate,
                                                   "If you wish to change the NLP package used (spaCy, Stanford CoreNLP, Stanza) and their available parsers, use the Setup dropdown menu at the bottom of this GUI")
    # parser_lb.config(text=available_parsers)
    # print("available parsers",available_parsers)
GUI_util.setup_menu.trace('w', activate_NLP_options)
activate_NLP_options()

if error:
    mb.showwarning(title='Warning',
               message="The config file 'NLP_default_package_language_config.csv' could not be found in the sub-directory 'config' of your main NLP Suite folder.\n\nPlease, setup next the default NLP package and language options.")
    call("python NLP_setup_package_language_main.py", shell=True)
    # this will display the correct hover-over info after the python call, in case options were changed
    error, package, parsers, package_basics, language, package_display_area_value_new, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()

GUI_util.window.mainloop()
