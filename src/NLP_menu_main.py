# written by Roberto Franzosi October 2019,
# edited Spring 2020, July 2020

#input: 1. file name
#input: 1. directory name
#output: directory name

import sys
import multiprocessing
multiprocessing.freeze_support()

import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"NLP",['os','tkinter'])==False:
    sys.exit(0)

import os
from sys import platform
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
from subprocess import call
import webbrowser

import GUI_IO_util
import IO_files_util
import reminders_util
import constants_util
import config_util
import run_script_util
import language_tools_advisor_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run():
    # widget values read here at RUN time (was: run_script_command lambda + run() params)
    inputFilename = GUI_util.inputFilename.get()
    input_main_dir_path = GUI_util.input_main_dir_path.get()
    output_dir_path = GUI_util.output_dir_path.get()
    openOutputFiles = GUI_util.open_csv_output_checkbox.get()
    chartPackage = GUI_util.charts_package_options_widget.get()
    dataTransformation = GUI_util.data_transformation_options_widget.get()
    script_to_run = globals()['script_to_run']
    IO_values = globals()['IO_values']

    if script_to_run=='':
        mb.showwarning('No option selection','No option has been selected.\n\nPlease, using the dropdown menus, select one of the many General tools and/or Linguistic analysis tools, then click on RUN again.')
        return
    IO_files_util.runScript_fromMenu_option(script_to_run,IO_values,inputFilename,input_main_dir_path, output_dir_path, openOutputFiles,chartPackage, dataTransformation)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
GUI_util.run_button.configure(command=run)

# Show welcome screen for the first 3 launches, then go straight to the menu.
# --from-welcome flag is passed by NLP_welcome_main to avoid a redirect loop.
import json as _json

if '--from-welcome' not in sys.argv:
    _launch_count_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'launch_count.json')
    try:
        with open(_launch_count_file, 'r') as _f:
            _launch_data = _json.load(_f)
        _launch_count = _launch_data.get('count', 0)
    except (FileNotFoundError, ValueError):
        _launch_count = 0

    _launch_count += 1
    try:
        os.makedirs(os.path.dirname(_launch_count_file), exist_ok=True)
        with open(_launch_count_file, 'w') as _f:
            _json.dump({'count': _launch_count}, _f)
    except Exception:
        pass

    if _launch_count <= 3:
        import run_script_util as _rsu
        _rsu.run_script("NLP_welcome_main.py")
        sys.exit(0)

# GUI section ______________________________________________________________________________________________________________________________________________________

IO_setup_display_brief=False

GUI_width=GUI_IO_util.get_GUI_width(2)
GUI_height=630 # height of GUI with full I/O display

GUI_size = str(GUI_width) + 'x' + str(GUI_height)

# GUI_size='1150x670'
GUI_label='Graphical User Interface (GUI) for a suite of tools of Natural Language Processing (NLP) & Data Visualization'
# there is currently NO way to setup a specific I/O config for the NLP_menu_main; it can only have the default setup
# config_filename='NLP_config.csv'
# overwrite the standard way of setting up config_filename, since NLP_menu_main saves to default_config
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
config_input_output_numeric_options=[2,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

# # GUI CHANGES add following lines to every special GUI
# # +2 is the number of lines starting at 1 of IO widgets
y_multiplier_integer = GUI_util.y_multiplier_integer + 0
window = GUI_util.window
# config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
# config_filename = GUI_util.config_filename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

setup_IO_OK_checkbox_var = tk.IntVar()
setup_parsers_annotators_OK_checkbox_var = tk.IntVar()
setup_external_software_OK_checkbox_var = tk.IntVar()

script_to_run=''
IO_values=''

software = ''
missing_external_software = ''

def clear(e):

    software_setup_var.set('')
    data_file_handling_tools_var.set('')
    pre_processing_tools_var.set('')
    statistical_tools_var.set('')
    visualization_tools_var.set('')
    corpus_tools_var.set('')
    corpus_document_tools_var.set('')
    sentence_tools_var.set('')
    GUI_util.clear("Escape")

window.bind("<Escape>", clear)

# IO fields do not need to be checked for scripts that open their own GUI
# TODO we should move this function to the GUI?
# IO_values 1 required file; 2 required dir; 3 either file or dir
def checkIO_Filename_InputDir(script, IO_values_local=0, fileExtension=''):
    if IO_values_local == 0:  # the case of a script with its own GUI; should never be here
        return True
    inputFilename = GUI_util.inputFilename.get()
    input_dir_path = GUI_util.input_main_dir_path.get()
    if IO_values_local == 1 or IO_values_local == 3:  # filename required
        # there MUST be a filename; check filename
        if IO_values_local == 1 and inputFilename == '':
            mb.showwarning(title='Fatal error',
                           message='The script ' + script + ' requires a valid INPUT filename. The filename is currrently blank.\n\nPlease, select a valid INPUT filename and try again.')
            return False
        if IO_values_local == 3 and inputFilename == '' and input_dir_path == '':
            mb.showwarning(title='Fatal error',
                           message='The script ' + script + ' requires a valid INPUT filename and/or directory. Both filename and directory are currrently blank.\n\nPlease, select a valid INPUT filename or directory and try again.')
        # RF return False
        # check file extension
        if inputFilename != '':
            fExtension = inputFilename.split(".")[-1]
            if fExtension not in fileExtension:
                mb.showwarning(title='Fatal error',
                               message='The script ' + script + ' requires a valid INPUT file with extension ' + str(
                                   fileExtension) + '.' + '\n\nPlease, select a valid INPUT file and try again.')
                return False

    if IO_values_local == 2:  # input_dir required
        # there MUST be a directory; check directory
        if input_dir_path == '':
            mb.showwarning(title='Fatal error',
                           message='The script ' + script + ' requires a valid INPUT directory. The directory is currrently blank.\n\nPlease, select a valid INPUT directory and try again.')
            return False

    if IO_values_local == 3:  # either filename or input_dir required
        # already checked above
        if inputFilename == '' and input_dir_path == '':
            mb.showwarning(title='Fatal error',
                           message='The script ' + script + ' requires a valid INPUT filename and/or directory. Both filename and directory are currrently blank.\n\nPlease, select a valid INPUT filename or directory and try again.')
            return False

    return True


# if you want to get the value, just call val=pydict[input] where the input is the
# input from the table
# val[0] will be the py file you want and val[1] will be the availability with 1 to be available and 0 to be unexisting
# There are FIVE values in the dictionary:
#	1. the label displayed in any of the menus (the key to be used)
#	2. the name of the python script (to be passed to NLP.py) LEAVE BLANK IF OPTION NOT AVAILABLE
#	3. 0 False 1 True whether the script has a GUI that will check IO items or we need to check IO items here
#	4. 1, 2, 3 (to be chcked when the script has no GUI )
#		1 requires input Dir
#		2 requires input file
#		3 requires either Dir or file
#	5. file extension
# FOR CONVENIENCE, THE DIC ENTRIES ARE IN KEY ALPHABETICAL ORDER

# set all values to null when using a web-based program, as in:
#	pydict["Gender guesser"] = ["Gender guesser", 0, 0,'']

# set 2 values to null when option is not available:
#	pydict["Male & female names"] = ["", 0] not available

# all pydict values are grouped together in constants_util.py
pydict = {}
pydict[""] = ["", 0]  # not available
# https://stanfordnlp.github.io/CoreNLP/quote.html
pydict["Parsers & annotators (CoreNLP, spaCy, Stanza)"] = ["parsers_annotators_main.py", 1]
pydict["CoreNLP annotator - date (normalized NER date)"] = ["parsers_annotators_main.py", 1]
pydict["CoreNLP annotator - gender (male & female names; via CoreNLP and dictionaries)"] = ["html_annotator_gender_main.py", 1]
pydict["CoreNLP annotator - quote"] = ["parsers_annotators_main.py", 1]
pydict["CoreNLP annotator - coreference (pronominal)"] = ["coreference_main.py", 1]
pydict["SVO (Subject-Verb-Object) extractor & visualization"] = ["SVO_main.py", 1]
pydict["Knowledge graphs: DBpedia & YAGO"] = ["knowledge_graphs_DBpedia_YAGO_main.py", 1]
pydict["HTML annotator - dictionary, gender, DBpedia, YAGO, WordNet - (All options GUI)"] = ["html_annotator_main.py", 1]
pydict["HTML annotator extractor"] = ["html_annotator_main.py", 1]
pydict["Annotator - hedge/uncertainty"] = ["", 0]
pydict["CoNLL table analyzer - Search the CoNLL table"] = ["CoNLL_table_analyzer_main.py", 1]
pydict["CoNLL table analyzer - Clause, noun, verb, function words frequencies"] = ["CoNLL_table_analyzer_main.py", 1]
pydict["Statistics (csv files)"] = ["statistics_csv_main.py", 1]
pydict["Statistics (txt files): Number of documents, words, syllables"] = ["statistics_txt_main.py", 1] # ["style_analysis_main.py", 1]
pydict["Statistics (txt files): Number of nouns, verbs, adjectives, pronouns, ..."] = ["statistics_txt_main.py", 1] # ["style_analysis_main.py", 1]
pydict["Co-Reference PRONOMINAL resolution (via Stanford CoreNLP)"] = ["parsers_annotators_main.py", 1]
pydict["Co-Occurrences VIEWER"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["N-grams VIEWER"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["Co-Occurrences"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["N-grams"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["N-grams search"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["N-grams/Co-Occurrences VIEWER"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["Data manipulation (ALL options GUI)"] = ["data_manipulation_main.py", 1]
pydict["File checker (A pre-processing pipeline of data quality control)"] = ["file_checker_pre_processing_pipeline_main.py", 1]
pydict["File checker (file content)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File checker (file content utf-8 encoding)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File checker (file name)"] = ["file_manager_main.py", 1]
pydict["File cleaner (file content) (Change to ASCII non-ASCII apostrophes & quotes and % to percent)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File cleaner (file content) (Find & Replace string)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File cleaner (file content) (Remove blank lines from txt file(s))"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File cleaner (file content) (Add full stop . at the end of paragraphs without end-of-paragraph punctuation)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File cleaner (file content) (Pronominal resolution via CoreNLP)"] = ["coreference_main.py", 1]
pydict["File classifier (dumb classifier via embedded date) (file name)"] = ["file_classifier_main.py", 1]
pydict["File finder (file name)"] = ["file_manager_main.py", 1]
pydict["File search (file content for words/collocations)"] = ["file_search_byWord_main.py", 1]
pydict["File search (file content for n-grams & co-occurrences)"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["File-type converter (csv, docx, pdf, rtf --> txt)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File matcher (file name)"] = ["file_matcher_main.py", 1]
pydict["File merger (file content)"] = ["file_merger_main.py", 1]
pydict["File splitter (file content)"] = ["file_splitter_main.py", 1]
pydict["File splitter (file name)"] = ["file_splitter_main.py", 1]
pydict["File manager (file name) (List, Rename, Copy, Move, Delete, Count, Split)"] = ["file_manager_main.py", 1]
pydict["Find non-related documents"] = ["corpus_checker_main.py", 1]
pydict["Excel charts"] = ["charts_Excel_main.py", 1]
pydict["Animated time-dependent bar plot (Plotly)"] = ["data_visualization_main.py", 1]
pydict["Boxplot"] = ["data_visualization_main.py", 1]
pydict["Colormap chart"] = ["data_visualization_main.py", 1]
pydict["Multiple bar charts"] = ["data_visualization_main.py", 1]
pydict["Network graphs (Gephi)"] = ["data_visualization_main.py", 1]
pydict["Sankey flowchart (Plotly)"] = ["data_visualization_main.py", 1]
pydict["Sunburst pie chart (Plotly)"] = ["data_visualization_main.py", 1]
pydict["Treemap (Plotly)"] = ["data_visualization_main.py", 1]
pydict["Geographic maps: From texts to maps via Google Earth Pro and Google Maps"] = ["GIS_main.py", 1]
pydict["Geographic maps: From csv file to maps via Google Earth Pro and Google Maps"] = ["GIS_Google_Earth_main.py", 1]
pydict["Geographic distances between locations"] = ["GIS_distance_main.py", 1]  # GIS_distance_main.py
pydict["Symbolic space: characters in NON-geocodable space (house, field, forest, threshold)"] = ["GIS_symbolic_main.py", 1]
pydict["Language detection"] = ["style_analysis_main.py", 1]
pydict["NER (Named Entity Recognition) annotator"] = ["NER_main.py", 1]
pydict["Newspaper article/Document titles"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["N-grams & Co-occurrences"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["Nominalization"] = ["nominalization_main.py", 1]
pydict["Sample corpus (ALL options GUI)"] = ["sample_corpus_main.py", 1]
pydict["File handler (ALL options GUI)"] = ["file_handler_ALL_main.py", 1]
pydict["Search (ALL options GUI)"] = ["file_search_ALL_main.py", 1]
pydict["Search CoNLL table"] = ["CoNLL_table_analyzer_main.py", 1]
pydict["Search text file(s) for n-grams & co-occurrences"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["Search text file(s) for words/collocations"] = ["file_search_byWord_main.py", 1]
pydict["Sentence analysis (ALL options GUI)"] = ["sentence_analysis_main.py", 1]
pydict["Sentence complexity"] = ["sentence_analysis_main.py", 1]
pydict["Sentence/text readability (via textstat)"] = ["sentence_analysis_main.py", 1]
pydict["Sentence visualization: Dependency tree viewer (png graphs)"] = ["sentence_analysis_main.py", 1]
pydict["Sentence visualization: Dynamic sentence network viewer (Gephi graphs)"] = ["", 0]  # not available
pydict["Sentiment analysis"] = ["sentiment_analysis_main.py", 1]
pydict['Sentiment analysis (dictionary options: ANEW, hedonometer, SentiWordNet, VADER)'] = ["sentiment_analysis_main.py", 1]
pydict['Sentiment analysis (neural network/tensor options: BERT, spaCy, Stanford CoreNLP, Stanza)'] = ["sentiment_analysis_main.py", 1]
pydict["Sentiments/emotions (ALL options GUI)"] = ["sentiments_emotions_ALL_main.py", 1]
pydict["Shape of stories"] = ["shape_of_stories_main.py", 1]
pydict["Similarities between documents (via TF-IDF)"] = ["corpus_checker_main.py", 1]
pydict["Similarities between documents (via Python difflib)"] = ["", 0]  # not available
pydict["Similarities between words (Levenshtein distance)"] = ["file_spell_checker_main.py", 1]
pydict["Spelling checkers"] = ["file_spell_checker_main.py", 1]
pydict["Spelling checker cleaner (Find & Replace string)"] = ["file_checker_converter_cleaner_main.py",1]
# pydict["Spelling checker/Unusual words (via NLTK)"] = ["file_spell_checker_main.py", 1]
# pydict["Spelling checker (via autocorrect)"] = ["file_spell_checker_main.py", 1]
# pydict["Spelling checker (via pyspellchecker)"] = ["file_spell_checker_main.py", 1]
# pydict["Spelling checker (via textblob)"] = ["file_spell_checker_main.py", 1]
pydict["PC-ACE database (via Pandas)"] = ["DB_PCACE_data_analysis_main.py", 1]
pydict["SQL database (via SQLite)"] = ["DB_SQL_main.py", 1]
pydict["Stanford CoreNLP"] = ["parsers_annotators_main.py", 1]
pydict["Semantic analysis"] = ["semantic_analysis_main.py", 1]
pydict["Syntactic analysis (ALL)"] = ["syntactic_analysis_ALL_main.py", 1]
pydict["SRL Semantic Role Labeling"] = ["", 0]
pydict["Dictionary items by sentence index"] = ["sentence_analysis_util.dictionary_items_bySentenceID", 0, 3, 'txt']
pydict["Topic modeling (via MALLET & Gensim)"] = ["topic_modeling_main.py", 1]
pydict["utf-8 compliance"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["Style analysis (ALL options GUI)"] = ["style_analysis_main.py", 1]
pydict["Narrative analysis (ALL options GUI)"] = ["narrative_analysis_ALL_main.py", 1]
pydict["CORPUS PROFILER. WHAT'S IN YOUR CORPUS? A SWEEPING VIEW."] = ["corpus_profiler_main.py", 1]
pydict["Corpus/document(s) statistics (Sentences, words, lines)"] = ["statistics_txt_main.py", 1]
pydict['Corpus/document(s) statistics (Nouns, verbs, adjectives, pronouns, ...)'] = ["statistics_txt_main.py", 1]
pydict['N-grams & Co-Occurrences'] = ["NGrams_CoOccurrences_main.py", 1]
pydict["Who wrote the text? Man or woman? (via Gender guesser)"] = ["Gender guesser", 0, 0, '']
pydict["Wordclouds (ALL options GUI)"] = ["wordclouds_main.py", 1]
pydict["Semantic aggregation (WordNet, VerbNet, FrameNet)"] = ["semantic_aggregation_main.py", 1]
pydict["Word embeddings (Word2Vec) (via BERT & Gensim)"] = ["word2vec_main.py", 1]
# pydict["Word embeddings (Word2Vec) (via spaCy)"] = ["", 0]
pydict["------------------"] = ["", 2]
# the following labels are found in constants_util
#   'Fundamental NLP tools ---------------------------------------------------------------------------'
#   'Specialized tools --------------------------------------------------------------------------------'
#   'Style analysis tools -----------------------------------------------------------------------------------'
# all pydict values are grouped together in constants_util.py

# NLP Suite team & How to cite are in GUI_util

IO_setup_var = tk.IntVar()
software_setup_var = tk.StringVar()
data_file_handling_tools_var = tk.StringVar()
pre_processing_tools_var = tk.StringVar()
statistical_tools_var = tk.StringVar()
visualization_tools_var = tk.StringVar()
corpus_tools_var = tk.StringVar()
corpus_document_tools_var = tk.StringVar()
sentence_tools_var = tk.StringVar()

setup_IO_OK_checkbox = tk.Checkbutton(window, state='disabled',
                                      variable=setup_IO_OK_checkbox_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                             setup_IO_OK_checkbox,
                                             True, False, True, False,
                                             90, GUI_IO_util.labels_x_coordinate,
                                             "The checkbox, always disabled, is ticked ON when the I/O options have been setup.\nIf the checkbox is OFF, click on the 'SETUP default I/O options...' button to set up.")

def setup_IO():
    GUI_util.setup_IO_configuration_options(False,scriptName, silent=True, open_setup_IO_GUI=True)
    setup_IO_checkbox()

def setup_IO_checkbox():
    # RUN is always normal for NLP_mnenu_main so this test would fail
    # state = str(GUI_util.run_button['state'])
    # if state != 'disabled':

    config_input_output_alphabetic_options, missing_IO, config_file_exists = config_util.read_config_file(config_filename, config_input_output_numeric_options)

    if missing_IO=='':
        setup_IO_OK_checkbox_var.set(1)
    else:
        setup_IO_OK_checkbox_var.set(0)

IO_setup_button = tk.Button(window, text='SETUP default I/O options: INPUT file/directory (corpus) and OUTPUT files directory', width=95, font=("Courier", 10, "bold"), command=lambda: setup_IO())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate+30,
                                               y_multiplier_integer,
                                               IO_setup_button, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate+30,
                                               "You will probably use the same document(s) (i.e., corpus), written in the same language, for different analyses using different NLP tools, and exporting results to the same directory.\n Click on the SETUP button to setup Input/Output (I/O) options.\nYour selected options will be used as default in all GUIs; but you can change your preferences at any time; and every GUI also allows you to setup GUI-specific I/O options.")

open_default_IO_config_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, GUI_IO_util.configPath+os.sep+'NLP_default_IO_config.csv'))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+GUI_IO_util.open_IO_config_button, y_multiplier_integer,
                                               open_default_IO_config_button, False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate, "Open the NLP_default_IO_config.csv file containing the default Input/Output options")

setup_parsers_annotators_OK_checkbox = tk.Checkbutton(window, state='disabled',
                                      variable=setup_parsers_annotators_OK_checkbox_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                             setup_parsers_annotators_OK_checkbox,
                                             True, False, True, False,
                                             90, GUI_IO_util.labels_x_coordinate,
                                             "The checkbox, always disabled, is ticked ON when the parser/annotator and corpus language options have been setup.\nIf the checkbox is OFF, click on the 'SETUP default NLP parser...' button to set up.")

NLP_package_language_config = GUI_IO_util.configPath+os.sep+'NLP_default_package_language_config.csv'
def setup_parsers_annotators_checkbox(NLP_package_language_config):
    if os.path.isfile(NLP_package_language_config):
        setup_parsers_annotators_OK_checkbox_var.set(1)
    else:
        setup_parsers_annotators_OK_checkbox_var.set(0)
setup_parsers_annotators_OK_checkbox_var.trace('w', lambda x, y, z: setup_parsers_annotators_checkbox(NLP_package_language_config))

setup_parsers_annotators_checkbox(NLP_package_language_config)

def _setup_parsers_and_recheck():
    run_script_util.run_script("NLP_setup_package_language_main.py")
    setup_parsers_annotators_checkbox(NLP_package_language_config)

NLP_package_language_setup_button = tk.Button(window, text='SETUP default NLP parsers & annotators package and default corpus language', width=95, font=("Courier", 10, "bold"), command=_setup_parsers_and_recheck)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate+30,
                                               y_multiplier_integer,
                                               NLP_package_language_setup_button, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate+30,
                                               "The NLP Suite relies on a handful of external software to carry out specialized tasks (e.g., Stanford CoreNLP, Gephi).\nClick on the Setup button to select your preferred parser software (e.g., Stanford CoreNLP) and the laguage of your corpus (e.g., English)\nYour selected options will be used as default in all GUIs; but you can change your preferences at any time.")

open_default_NLP_package_language_config_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, NLP_package_language_config))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+GUI_IO_util.open_NLP_package_language_config_button, y_multiplier_integer,
                                               open_default_NLP_package_language_config_button, False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate, "Open the NLP_default_package_language_config.csv file containing the default NLP parser and annotators and corpus language options")

setup_external_software_checkbox = tk.Checkbutton(window, state='disabled',
                                         variable=setup_external_software_OK_checkbox_var, onvalue=1, offvalue=0, command=lambda: setup_external_programs_checkbox())
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                             setup_external_software_checkbox,
                                             True, False, True, False,
                                             90, GUI_IO_util.labels_x_coordinate,
                                             "The checkbox, always disabled, is ticked ON when all external software have been installed.\nIf the checkbox is OFF, click on the 'SETUP external software' button to set up.")

software_dir = ''

def setup_external_programs_checkbox():
    # If the config file doesn't exist, external software is not set up
    ext_config = GUI_IO_util.configPath + os.sep + 'NLP_setup_external_software_config.csv'
    if not os.path.isfile(ext_config):
        setup_external_software_OK_checkbox_var.set(0)
        return ''
    # get the software_dir and software_url for the selected software_name from the config file
    software_dir, software_url, missing_software, error_found = IO_libraries_util.get_external_software_dir('NLP_menu_main', '',
                                                        silent=True, only_check_missing=True, install_download='download')
    if missing_software!='':
        setup_external_software_OK_checkbox_var.set(0)
    else:
        setup_external_software_OK_checkbox_var.set(1)
    return missing_external_software


def callback(software: str):
    # print('IN CALLBACK')
    software_setup_var.set(software)
    setup_external_programs_checkbox()

def setup_external_software_warning():
    global software
    mb.showwarning('External software option', 'Please, select next the external software that you would like to download/install using the dropdown menu.')
    software = GUI_IO_util.dropdown_menu_widget(window, "Please, select the external software to setup using the dropdown menu on the left, then click OK to accept your selection", ['Stanford CoreNLP', 'Gephi', 'Google Earth Pro', 'MALLET', 'WordNet'],'Stanford CoreNLP',callback)
    if software != None:
        setup_external_programs_checkbox()

def setup_external_software():
    run_script_util.run_script("NLP_setup_external_software_main.py")
    setup_external_programs_checkbox()

# software_setup_button = tk.Button(window, text='Setup external software', width=95, font=("Courier", 10, "bold"), command=lambda: setup_external_software_warning())
software_setup_button = tk.Button(window, text='SETUP external software', width=95, font=("Courier", 10, "bold"), command=lambda: setup_external_software())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate+30,
                                               y_multiplier_integer,
                                               software_setup_button, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate+30,
                                               "The NLP Suite relies on a handful of external software to carry out specialized tasks (e.g., Stanford CoreNLP, Gephi)\nClick on the Setup button to download and install these freeware software packages\nYou only have to do this once")

open_setup_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, GUI_IO_util.configPath+os.sep+'NLP_setup_external_software_config.csv'))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+GUI_IO_util.open_setup_external_software_button, y_multiplier_integer,
                                               open_setup_button, False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate, "Open the NLP_setup_external_software_config.csv file containing all external software installation paths")

# CORPUS LANGUAGE & NLP options available in the Suite
corpus_language_button = tk.Button(window,
                                   text="Which NLP tools in the Suite can I use with my corpus language?",
                                   width=95, font=("Courier", 11, "bold"), fg='red',
                                   command=lambda: language_tools_advisor_util.run(
                                       outputDir=GUI_util.output_dir_path.get()))
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 30,
                                               y_multiplier_integer,
                                               corpus_language_button, False, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 30,
                                               "Create an HTML file with a list of NLP tools available in the Suite for analysis of a corpus in a specific language.")

# CORPUS PROFILER -- flagship one-click tool: a prominent bold red button, given a role of its own at the
# top of the tool list. Placement/wording easy to tweak.
corpus_profiler_button = tk.Button(window,
                                   text="CORPUS PROFILER  —  what's in your corpus? one click → an HTML report and a paper-style summary",
                                   width=95, font=("Courier", 11, "bold"), fg='red',
                                   command=lambda: run_script_util.run_script("corpus_profiler_main.py"))
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 30,
                                               y_multiplier_integer,
                                               corpus_profiler_button, False, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 30,
                                               "CORPUS PROFILER — run a battery of NLP analyses on your corpus with sensible DEFAULTS and get a paper-style summary plus a single navigable HTML report (NLP_corpus_profile.html) that links every result.")

# ── Notebook: the seven tool dropdowns grouped into TWO tabs (General Utility / Linguistic) ──
# Replaces the seven stacked dropdown rows (the layout designed in NLP_menu_notebook_skeleton).
# Each Combobox keeps the SAME textvariable as before, so the existing traces (getScript),
# the RUN dispatch, and the Esc-clear all keep working UNCHANGED. Mirrors the placed-notebook
# pattern already used in data_visualization_main.py.
nb_style = ttk.Style()
try:
    nb_style.theme_use('clam')
except Exception:
    pass
nb_style.configure('NLP.TNotebook.Tab', font=("Courier", 11, "bold"), foreground='red', padding=[16, 5])
nb_style.map('NLP.TNotebook.Tab',
             background=[('selected', '#d0e0f0'), ('!selected', '#e8e8e8')],
             foreground=[('selected', 'red'), ('!selected', '#999999')])

notebook_y = GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step * y_multiplier_integer
nb_width = GUI_width - GUI_IO_util.labels_x_coordinate - 20
nb_height = 210
tools_notebook = ttk.Notebook(window, style='NLP.TNotebook')
tools_notebook.place(x=GUI_IO_util.labels_x_coordinate, y=notebook_y, width=nb_width, height=nb_height)

tab_linguistic = ttk.Frame(tools_notebook)
tab_utility = ttk.Frame(tools_notebook)
# Linguistic tools are the suite's raison d'être -> make them the FIRST tab, so they are the
# default selected tab on every launch; General Utility tools follow as the supporting cast.
tools_notebook.add(tab_linguistic, text='   Linguistic Analysis Tools   ')
tools_notebook.add(tab_utility, text='   General Utility Tools   ')
tools_notebook.select(tab_linguistic)

# advance past the notebook so the RUN bar (GUI_bottom) lands below it
y_multiplier_integer = y_multiplier_integer + 6

_tab_help_x = nb_width - 95
_ROW_STEP = 42

def _tab_row(parent, row_y, label_text, combobox, help_message):
    tk.Label(parent, text=label_text).place(x=10, y=row_y + 3)
    combobox.place(x=250, y=row_y)
    tk.Button(parent, text='? HELP',
              command=lambda m=help_message: mb.showinfo("NLP Suite Help", m)).place(x=_tab_help_x, y=row_y)

# --- General Utility tab -------------------------------------------------------
data_file_handling_tools_var.set('')
data_file_handling_tools_menu = ttk.Combobox(tab_utility, width=80, textvariable=data_file_handling_tools_var)
data_file_handling_tools_menu['values'] = constants_util.NLP_Suite_data_file_handling_tools_menu
_tab_row(tab_utility, 12, 'Data & Files Handling Tools', data_file_handling_tools_menu,
         "Please, using the dropdown menu, select one of the many options available for data and file handling." + GUI_IO_util.msg_Esc)

pre_processing_tools_var.set('')
pre_processing_tools_menu = ttk.Combobox(tab_utility, width=80, textvariable=pre_processing_tools_var)
pre_processing_tools_menu['values'] = constants_util.NLP_Suite_pre_processing_tools_menu
_tab_row(tab_utility, 12 + _ROW_STEP, 'Pre-Processing Tools', pre_processing_tools_menu,
         "Please, using the dropdown menu, select one of the many options available for pre-processing text." + GUI_IO_util.msg_Esc)

statistical_tools_var.set('')
statistical_tools_menu = ttk.Combobox(tab_utility, width=80, textvariable=statistical_tools_var)
statistical_tools_menu['values'] = ['Statistics (csv files)','Corpus/document(s) statistics (Sentences, words, lines)','Corpus/document(s) statistics (Nouns, verbs, adjectives, pronouns, ...)','N-grams & Co-occurrences']
_tab_row(tab_utility, 12 + 2 * _ROW_STEP, 'Statistical Tools', statistical_tools_menu,
         "Please, using the dropdown menu, select the option available for statistical analyses." + GUI_IO_util.msg_Esc)

visualization_tools_var.set('')
visualization_menu = ttk.Combobox(tab_utility, width=80, textvariable=visualization_tools_var)
visualization_menu['values'] = constants_util.NLP_Suite_visualization_tools_menu
_tab_row(tab_utility, 12 + 3 * _ROW_STEP, 'Visualization Tools', visualization_menu,
         "Please, using the dropdown menu, select one of the many options available for visualizing data.\n\nNearly all linguistic tools, however, automatically visualize results, typically in Excel charts, but also in more specialized graphical tools, such as network graphs in Gephi or GIS maps in Google Earth Pro or in Google Maps." + GUI_IO_util.msg_Esc)

# --- Linguistic Analysis tab ---------------------------------------------------
corpus_tools_var.set('')
corpus_menu = ttk.Combobox(tab_linguistic, width=80, textvariable=corpus_tools_var)
corpus_menu['values'] = constants_util.NLP_Suite_corpus_tools_menu
_tab_row(tab_linguistic, 12, 'CORPUS Analysis Tools', corpus_menu,
         "Please, using the dropdown menu, select one of the many options available for analyzing your corpus.\n\nCORPUS TOOLS APPLY TO MULTIPLE DOCUMENTS ONLY, RATHER THAN TO A SINGLE DOCUMENT.\n\nIn INPUT the tools expect multiple documents stored in a directory (the 'corpus')." + GUI_IO_util.msg_Esc)

corpus_document_tools_var.set('')
corpus_documents_menu = ttk.Combobox(tab_linguistic, width=80, textvariable=corpus_document_tools_var)
corpus_documents_menu['values'] = constants_util.NLP_Suite_corpus_document_tools_menu
_tab_row(tab_linguistic, 12 + _ROW_STEP, 'CORPUS/DOCUMENT Analysis Tools', corpus_documents_menu,
         "Please, using the dropdown menu, select one of the many options available for analyzing your corpus and/or a single document.\n\nTHE TOOLS IN THIS CATEGORY APPLY TO EITHER MULTIPLE DOCUMENTS (THE 'CORPUS') OR TO A SINGLE DOCUMENT." + GUI_IO_util.msg_Esc)

sentence_tools_var.set('')
sentence_tools_menu = ttk.Combobox(tab_linguistic, width=80, textvariable=sentence_tools_var)
sentence_tools_menu['values'] = ['Sentence analysis (ALL options GUI)']
_tab_row(tab_linguistic, 12 + 2 * _ROW_STEP, 'SENTENCE Analysis Tools', sentence_tools_menu,
         "Please, using the dropdown menu, select one of the many options available for analyzing your corpus/document by sentence index." + GUI_IO_util.msg_Esc)

def clear_selected_options(tool_selected):
    if tool_selected=='data_file_handling_tools' and data_file_handling_tools_var.get()!='':
        pre_processing_tools_var.set('')
        statistical_tools_var.set('')
        visualization_tools_var.set('')
        corpus_tools_var.set('')
        corpus_document_tools_var.set('')
        sentence_tools_var.set('')
    if tool_selected=='pre_processing_tools' and pre_processing_tools_var.get()!='':
        data_file_handling_tools_var.set('')
        statistical_tools_var.set('')
        visualization_tools_var.set('')
        corpus_tools_var.set('')
        corpus_document_tools_var.set('')
        sentence_tools_var.set('')
    if tool_selected=='statistical_tools' and statistical_tools_var.get()!='':
        data_file_handling_tools_var.set('')
        pre_processing_tools_var.set('')
        visualization_tools_var.set('')
        corpus_tools_var.set('')
        corpus_document_tools_var.set('')
        sentence_tools_var.set('')
    if tool_selected=='visualization_tools' and visualization_tools_var.get()!='':
        data_file_handling_tools_var.set('')
        pre_processing_tools_var.set('')
        statistical_tools_var.set('')
        corpus_tools_var.set('')
        corpus_document_tools_var.set('')
        sentence_tools_var.set('')
    if tool_selected=='corpus_tools' and corpus_tools_var.get()!='':
        data_file_handling_tools_var.set('')
        pre_processing_tools_var.set('')
        statistical_tools_var.set('')
        visualization_tools_var.set('')
        corpus_document_tools_var.set('')
        sentence_tools_var.set('')
    if tool_selected=='corpus_document_tools' and corpus_document_tools_var.get()!='':
        data_file_handling_tools_var.set('')
        pre_processing_tools_var.set('')
        statistical_tools_var.set('')
        visualization_tools_var.set('')
        corpus_tools_var.set('')
        sentence_tools_var.set('')
    if tool_selected=='sentence_tools' and sentence_tools_var.get()!='':
        data_file_handling_tools_var.set('')
        pre_processing_tools_var.set('')
        statistical_tools_var.set('')
        visualization_tools_var.set('')
        corpus_tools_var.set('')
        corpus_document_tools_var.set('')

def getScript(tool_selected, script):
    global script_to_run, IO_values
    if script != '':
        script_to_run, IO_values = IO_files_util.getScript(pydict, script)
    clear_selected_options(tool_selected)

data_file_handling_tools_var.trace('w', lambda x, y, z: getScript('data_file_handling_tools',data_file_handling_tools_var.get()))
pre_processing_tools_var.trace('w', lambda x, y, z: getScript('pre_processing_tools', pre_processing_tools_var.get()))
statistical_tools_var.trace('w', lambda x, y, z: getScript('statistical_tools',statistical_tools_var.get()))
visualization_tools_var.trace('w', lambda x, y, z: getScript('visualization_tools',visualization_tools_var.get()))
corpus_tools_var.trace('w', lambda x, y, z: getScript('corpus_tools',corpus_tools_var.get()))
corpus_document_tools_var.trace('w', lambda x, y, z: getScript('corpus_document_tools',corpus_document_tools_var.get()))
sentence_tools_var.trace('w', lambda x, y, z: getScript('sentence_tools',sentence_tools_var.get()))

def openYouTube(video_url):
    if video_url!='':
        webbrowser.open_new_tab(video_url)
    else:
        mb.showwarning(title='Warning',
                   message='The YouTube video ' + video_url + ' could not be found in the NLP Suite YouTube channel.\n\nPlease, warn the NLP Suite developers.')

videos_lookup = {'Setup the NLP Suite':'https://www.youtube.com/watch?v=W56SU9oAbpc'}
videos_options = 'Setup the NLP Suite'

TIPS_lookup = {'NLP Suite: Package description': 'TIPS_NLP_NLP Suite Package description.pdf',
               'pip install & Anaconda environments': 'TIPS_NLP_Anaconda NLP environment pip.pdf',
               'Things to do with words: NLP approach': 'TIPS_NLP_Things to do with words NLP approach.pdf',
               'Setup Input/Output configuration for your corpus': 'TIPS_NLP_Setup INPUT-OUTPUT options.pdf',
               'Setup external software (e.g., MALLET)': 'TIPS_NLP_Setup external software.pdf',
               'NLP Suite: General tools': 'TIPS_NLP_NLP Suite General tools.pdf',
               'NLP Suite: Tools of linguistic analysis': 'TIPS_NLP_NLP Suite Tools of linguistic analysis.pdf',
               'NLP basic language': 'TIPS_NLP_NLP Basic language.pdf',
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',               'Things to do with words: Overall view': 'TIPS_NLP_Things to do with words Overall view.pdf',
               'Things to do with words: Content analysis': 'TIPS_NLP_Things to do with words Content analysis.pdf',
               'Things to do with words: Frame analysis': 'TIPS_NLP_Things to do with words Frame analysis.pdf',
               'Things to do with words: Narrative analysis': 'TIPS_NLP_Things to do with words Narrative analysis.pdf',
               'Things to do with words: Rhetoric (Arguments)': 'TIPS_NLP_Things to do with words Rhetorical analysis Arguments.pdf',
               'Things to do with words: Rhetoric (Tropes & Figures)': 'TIPS_NLP_Things to do with words Rhetorical analysis Tropes and Figures.pdf',
               'Style analysis': 'TIPS_NLP_Style analysis.pdf',
               'Text encoding (utf-8)': 'TIPS_NLP_Text encoding (utf-8).pdf',
               'Excel - Enabling Macros': 'TIPS_NLP_Excel Enabling macros.pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures':'TIPS_NLP_Statistical measures.pdf',}
TIPS_options = 'NLP Suite: Package description', 'pip install & Anaconda environments', 'Text encoding (utf-8)','Excel - Enabling Macros','csv files - Problems & solutions', 'Statistical measures', 'Setup Input/Output configuration for your corpus', 'Setup external software (e.g., MALLET)', 'Things to do with words: NLP approach', 'English Language Benchmarks',  'NLP Suite: General tools', 'NLP Suite: Tools of linguistic analysis', 'NLP basic language', 'Things to do with words: Overall view', 'Things to do with words: Content analysis', 'Things to do with words: Frame analysis', 'Things to do with words: Narrative analysis', 'Things to do with words: Rhetoric (Arguments)', 'Things to do with words: Rhetoric (Tropes & Figures)', 'Style analysis'


# reminders content for specific GUIs are set in the csv file reminders

# 'KWIC',
# 'KWIC':'TIPS_NLP_KWIC (Key Words In Context).pdf'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate,y_multiplier_integer):
    # y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,GUI_IO_util.msg_anyFile)
    # y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,GUI_IO_util.msg_anyData)
    # y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    # leave a blank line to separate general tools
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer+1,"NLP Suite Help",
                                  "Please, click on the button to the right to open the GUI that will allow you to setup default I/O options:\n   INPUT file and or directory of files (your corpus) and\n   OUTPUT directory where all files (csv, txt, html, kml, jpg) produced by the NLP-Suite tools will be saved.\n\nThese default I/O options will be used for all GUIs.\n\nThe checkbox at the beginning of the line is set to OK if all INPUT/OUTPUT options have been successfully selected and saved in the NLP_default_IO_config.csv file under the subdirecory config.\n\nYou can open the NLP_default_IO_config.csv file by clicking on the button at the end of the line." + GUI_IO_util.msg_IO_config)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, click on the button to the right to open the GUI that will allow you to setup default NLP package to be used for parsers and annotators (spaCy, Stanford CoreNLP, Stanza) and the language of your corpus.\n\nThe checkbox at the beginning of the line is set to OK if all INPUT/OUTPUT options have been successfully selected and saved in the NLP_default_IO_config.csv file under the subdirecory config.\n\nYou can open the NLP_default_IO_config.csv file by clicking on the button at the end of the line." + GUI_IO_util.msg_IO_config)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "The NLP-Suite relies for some of its operations on external software that needs to be downloaded and installed (Stanford CoreNLP, WordNet, MALLET, SENNA, Gephi, Google Earth Pro). When using any of these software, the NLP-Suite needs to know where they have been installed on your computer (e.g., C:\\Program Files (x86)\\WordNet).\n\nPlease, click on the 'Select external software' button to select the software option that you want to link to its installation directory. YOUR SELECTION WILL BE SAVED IN THE NLP_setup_external_software_config.csv FILE UNDER THE SUBDIRECTORY config.\n\nThe checkbox at the beginning of the line is set to OK if all external software packages have been successfully installed.\n\nYou can open the NLP_setup_external_software_config.csv file by clicking on the button at the end of the line.\n\n"
                                  "The NLP_setup_external_software_config.csv file has three columns (with headers Software, Path, Download_link) and 6 rows, one for each of the external software and with the followining expected labels: Stanford CoreNLP, MALLET, SENNA, WordNet, Gephi, Google Earth Pro and where "
                                  "Path refers to the installation path of the software on your machine. "\
                                  "As an example, the three fields for the Stanford CoreNLP software would look like this: "
                                  "Stanford CoreNLP   C:/Program Files (x86)/stanford-corenlp-4.3.1   https://stanfordnlp.github.io/CoreNLP/download.html. "
                                  "Needless to say C:/Program Files (x86)/stanford-corenlp-4.3.1 will change, depending upon where you install CoreNLP locally.")
    # The seven tool-dropdown ?HELP buttons now live INSIDE the two notebook tabs (see _tab_row),
    # so only the three SETUP-row help buttons are placed down the left margin here.
    return y_multiplier_integer
# Place the three SETUP help buttons (side effect). Do NOT overwrite y_multiplier_integer: keep the
# post-notebook value computed above so the RUN bar (GUI_bottom) lands BELOW the notebook.
help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

# change the value of the readMe_message
readMe_message = "This Python 3 script is the front end for a wide collection of Java and Python Natural Language Processing (NLP) tools.\n\nThe set of tools are divided into GENERAL UTILITY TOOLS (data and file handling, pre-processing, statistical, visualization) and LINGUISTIC ANALYSIS TOOLS.\n\nLINGUISTIC ANALYSIS TOOLS are divided into tools that expect in input CORPUS DATA (i.e., multiple documents stored in a directory), CORPUS and/or SINGLE DOCUMENT, and SENTENCE.\n\nWhile some linguistic tools are specific for one of these three categories (e.g., topic modeling cannot be performed on a single document), MANY TOOLS OVERLAP. Tools that can work on a single file or a corpus are all classified under CORPUS/DOCUMENT tools. SENTENCE TOOLS still require either a corpus or a single document in input; but they also provide in output sentence-level information for more ingrained linguistic analyses.\n\nAll tools are open source freeware software released under the GNU LGPLv2.1 license (http://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html).\n\nYou can cite the NLP Suite as:\n\nFranzosi, Roberto. 2020. NLP Suite: A collection of natural language processing and visualization tools GitHub: https://github.com/NLP-Suite/NLP-Suite/wiki."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

if platform == 'darwin':
    window.update()

# temp_config_filename = config_filename # 'NLP_menu_config.csv'
routine_options = reminders_util.getReminders_list(scriptName)

reminders_util.checkReminder(scriptName,
                             reminders_util.title_options_NLP_Suite_architecture,
                             reminders_util.message_NLP_Suite_architecture,
                             True)
routine_options = reminders_util.getReminders_list(scriptName)

if sys.platform == 'darwin':
    reminders_util.checkReminder(scriptName,
                                 reminders_util.title_options_TensorFlow,
                                 reminders_util.message_TensorFlow,
                                 True)
    routine_options = reminders_util.getReminders_list(scriptName)

# Auto-generate default config files on first run so the user can test immediately
def ensure_default_configs():
    import csv as _csv
    config_dir = GUI_IO_util.configPath
    if not os.path.isdir(config_dir):
        try:
            os.mkdir(config_dir)
        except Exception:
            return False

    created = []

    io_config = os.path.join(config_dir, 'NLP_default_IO_config.csv')
    if not os.path.isfile(io_config):
        sample_dir = os.path.join(GUI_IO_util.NLPPath, 'lib', 'sampleData', 'newspaperArticles')
        output_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'NLP_output')
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception:
                output_dir = ''
        sample_dir_path = sample_dir.replace('\\', '/')
        output_dir_path = output_dir.replace('\\', '/')
        with open(io_config, 'w', newline='', encoding='utf-8') as f:
            w = _csv.writer(f)
            w.writerow(['I/O configuration label', 'Path', 'Sort order', 'Item separator character(s)', 'Date format', 'Date position'])
            w.writerow(['Input txt filename with path', '', '', '', '', ''])
            w.writerow(['Input files directory', sample_dir_path, '0', '_', 'mm-dd-yyyy', '4'])
            w.writerow(['Input files secondary directory', '', '', '', '', ''])
            w.writerow(['Output files directory', output_dir_path, '', '', '', ''])
        created.append('I/O configuration (input: lib/sampleData/newspaperArticles, output: ~/Documents/NLP_output)')

    pkg_config = os.path.join(config_dir, 'NLP_default_package_language_config.csv')
    if not os.path.isfile(pkg_config):
        with open(pkg_config, 'w', newline='', encoding='utf-8') as f:
            w = _csv.writer(f)
            w.writerow(['Parser & annotators', 'Parsers', 'Basic functions (tokenizer/lemmatizer)',
                         'Corpus language', 'Language encoding', 'Export Json',
                         'CoreNLP memory', 'CoreNLP document length', 'CoreNLP sentence-length limit'])
            w.writerow(['Stanza', "Dependency parser, Constituency parser", 'Stanza',
                         'English', 'utf-8', '0.0', '0.0', '0.0', '0.0'])
        created.append('NLP package & language (Stanza, English)')

    if created:
        msg = ('The NLP Suite has automatically created default configuration files '
               'so you can start testing right away:\n\n')
        for item in created:
            msg += '  • ' + item + '\n'
        msg += ('\nYou can change these options at any time using the SETUP buttons above.')
        mb.showinfo('Default configuration created', msg)
        return True
    return False

configs_created = ensure_default_configs()

# check for missing I/O configuration options
setup_IO_checkbox()
setup_parsers_annotators_checkbox(NLP_package_language_config)

# check for missing external software
missing_external_software = setup_external_programs_checkbox()

if missing_external_software!='':
    reminders_util.checkReminder(scriptName,
                                 reminders_util.title_options_missing_external_software_NLP_main_GUI,
                                 reminders_util.message_missing_external_software_NLP_main_GUI,
                                 True)
    routine_options = reminders_util.getReminders_list(scriptName)

if not setup_IO_OK_checkbox_var.get() or not setup_parsers_annotators_OK_checkbox_var.get() or not setup_external_software_OK_checkbox_var.get():
    answer = tk.messagebox.askyesno("Warning", 'Some (or all) of the required three setup options:\n'
                                               '\n\nSetup default I/O options...\nSetup default NLP parsers and annotators...\nSetup external software'
                                               '\n\ndisplayed in the three buttons at the top of this GUI are not completed (the checkbox to the left of the incomplete setup button is not ticked off).'
                                               '\n\nYou should click on the appropriate Setup button and complete the required setup.'
                                               '\n\nDo you want to watch the video on how to setup the NLP Suite options?')
    if answer:
        GUI_util.videos_dropdown_field.set('Setup the NLP Suite')
        # GUI_util.watch_video(videos_lookup, scriptName)

if sys.platform == 'darwin':
    import platform
    if platform.machine() != 'x86_64':
        # When running as a PyInstaller frozen app, sys.executable is the bundle
        # binary, not a Python interpreter, so pip cannot be invoked. The bundled
        # python-env already includes TensorFlow with Apple Silicon support, so
        # no check is needed. Only warn when running from source (development mode).
        if not getattr(sys, 'frozen', False):
            import subprocess
            try:
                output = subprocess.check_output(
                    [sys.executable, "-m", "pip", "freeze"], stderr=subprocess.DEVNULL
                ).decode("utf-8")
            except Exception:
                output = ""
            has_tensorflow = any(pkg in output for pkg in ("tensorflow-metal", "tensorflow-macos", "tensorflow==", "tensorflow "))
            if not has_tensorflow:
                mb.showwarning(
                    title='Warning',
                    message='Your Mac uses an Apple Silicon chip (M1/M2/M3).\n\n'
                            'Some algorithms that rely on TensorFlow (e.g. BERT) may not work correctly '
                            'without a TensorFlow build that supports Apple Silicon.\n\n'
                            'If you plan to use those algorithms, install TensorFlow for Apple Silicon:\n\n'
                            '    pip install tensorflow tensorflow-metal\n\n'
                            'You do NOT need to reinstall Anaconda — the bundled python-env already '
                            'supports Apple Silicon.'
                )

GUI_util.window.mainloop()
