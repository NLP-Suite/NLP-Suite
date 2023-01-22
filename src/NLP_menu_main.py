# written by Roberto Franzosi October 2019,
# edited Spring 2020, July 2020

#input: 1. file name
#input: 1. directory name
#output: directory name

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"NLP",['os','tkinter'])==False:
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

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,input_main_dir_path, output_dir_path,
    openOutputFiles,
    createCharts,
    chartPackage,
    script_to_run,
    IO_values):

    if script_to_run=='':
        mb.showwarning('No option selection','No option has been selected.\n\nPlease, using the dropdown menus, select one of the many General tools and/or Linguistic analysis tools, then click on RUN again.')
        return
    IO_files_util.runScript_fromMenu_option(script_to_run,IO_values,inputFilename,input_main_dir_path, output_dir_path, openOutputFiles,createCharts,chartPackage)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_chart_output_checkbox.get(),
                            GUI_util.charts_package_options_widget.get(),
                            script_to_run,
                            IO_values)

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

IO_setup_display_brief=False

GUI_width=GUI_IO_util.get_GUI_width(2)
GUI_height=670 # height of GUI with full I/O display

GUI_size = str(GUI_width) + 'x' + str(GUI_height)

# GUI_size='1150x670'
GUI_label='Graphical User Interface (GUI) for a suite of tools of Natural Language Processing (NLP) & Data Visualization'
# there is currently NO way to setup a specific I/O config for the NLP_menu_main; it can only have the default setup
# config_filename='NLP_config.csv'
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = scriptName.replace('main.py', 'config.csv')
# overwrite the standard way of setting up config_filename, since NLP_menu_main saves to default_config
config_filename = 'NLP_default_IO_config.csv'

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
handle_setup_options_OK_checkbox_var = tk.IntVar()
setup_software_OK_checkbox_var = tk.IntVar()

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
pydict["Parsers & annotators (BERT, CoreNLP, spaCy, Stanza)"] = ["parsers_annotators_main.py", 1]
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
pydict["Statistics (txt files)"] = ["style_analysis_main.py", 1]
pydict["Co-Reference PRONOMINAL resolution (via Stanford CoreNLP)"] = ["parsers_annotators_main.py", 1]
pydict["Co-Occurrences viewer"] = ["NGrams_CoOccurrences_Viewer_main.py", 1]
pydict["Data manipulation (ALL options GUI)"] = ["data_manipulation_main.py", 1]
pydict["File checker (file content)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File checker (file content utf-8 encoding)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File checker (file name)"] = ["file_manager_main.py", 1]
pydict["File cleaner (Change to ASCII non-ASCII apostrophes & quotes and % to percent)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File cleaner (Find & Replace string)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File cleaner (Remove blank lines from txt file(s))"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File cleaner (Add full stop . at the end of paragraphs without end-of-paragraph punctuation)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File cleaner (Pronominal resolution via CoreNLP)"] = ["coreference_main.py", 1]
pydict["File classifier (dumb classifier via embedded date) (file name)"] = ["file_classifier_main.py", 1]
pydict["File finder (file name)"] = ["file_manager_main.py", 1]
pydict["File search (file content for words/collocations)"] = ["file_search_byWord_main.py", 1]
pydict["File search (file content for n-grams & co-occurrences; N-grams viewer)"] = ["NGrams_CoOccurrences_Viewer_main.py", 1]
pydict["File-type converter (csv, docx, pdf, rtf --> txt)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File matcher (file name)"] = ["file_matcher_main.py", 1]
pydict["File merger (file content)"] = ["file_merger_main.py", 1]
pydict["File splitter (file content)"] = ["file_splitter_main.py", 1]
pydict["File splitter (file name)"] = ["file_splitter_main.py", 1]
pydict["File manager (List, Rename, Copy, Move, Delete, Count, Split)"] = ["file_manager_main.py", 1]
pydict["Find non-related documents"] = ["social_science_research_main.py", 1]
pydict["Excel charts"] = ["charts_Excel_main.py", 1]
pydict["Animated time-dependent bar plot (Plotly) (Open GUI)"] = ["data_visualization_main.py", 1]
pydict["Network graphs (Gephi) (Open GUI)"] = ["data_visualization_main.py", 1]
pydict["Sankey flowchart (Plotly) (Open GUI)"] = ["data_visualization_main.py", 1]
pydict["Sunburst pie chart (Plotly) (Open GUI)"] = ["data_visualization_main.py", 1]
pydict["Treemap (Plotly) (Open GUI)"] = ["data_visualization_main.py", 1]
pydict["Geographic maps: Geocoding & maps"] = ["GIS_main.py", 1]
pydict["Geographic maps: Google Earth Pro"] = ["GIS_Google_Earth_main.py", 1]
pydict["Geographic maps: From texts to maps"] = ["GIS_main.py", 1]
pydict["Geographic distances between locations"] = ["GIS_distance_main.py", 1]  # GIS_distance_main.py
pydict["Gender guesser"] = ["Gender guesser", 0, 0, '']
pydict["Language detection"] = ["style_analysis_main.py", 1]
pydict["NER (Named Entity Recognition) annotator"] = ["NER_main.py", 1]
pydict["Newspaper article/Document titles"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["N-grams (word & character)"] = ["style_analysis_main.py", 1]
pydict["N-grams viewer"] = ["NGrams_CoOccurrences_Viewer_main.py", 1]
pydict["Nominalization"] = ["nominalization_main.py", 1]
pydict["Sample corpus (ALL options GUI)"] = ["sample_corpus_main.py", 1]
pydict["File handler (ALL options GUI)"] = ["file_handler_ALL_main.py", 1]
pydict["Search (ALL options GUI)"] = ["file_search_ALL_main.py", 1]
pydict["Search CoNLL table"] = ["CoNLL_table_analyzer_main.py", 1]
pydict["Search text file(s) for n-grams & co-occurrences (N-grams viewer)"] = ["NGrams_CoOccurrences_Viewer_main.py", 1]
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
pydict["Similarities between documents (via Java Lucene)"] = ["social_science_research_main.py", 1]
pydict["Similarities between documents (via Python difflib)"] = ["", 0]  # not available
pydict["Similarities between words (Levenshtein distance)"] = ["file_spell_checker_main.py", 1]
pydict["Spelling checkers"] = ["file_spell_checker_main.py", 1]
pydict["Spelling checker cleaner (Find & Replace string)"] = ["file_checker_converter_cleaner_main.py",1]
# pydict["Spelling checker/Unusual words (via NLTK)"] = ["file_spell_checker_main.py", 1]
# pydict["Spelling checker (via autocorrect)"] = ["file_spell_checker_main.py", 1]
# pydict["Spelling checker (via pyspellchecker)"] = ["file_spell_checker_main.py", 1]
# pydict["Spelling checker (via textblob)"] = ["file_spell_checker_main.py", 1]
pydict["PC-ACE database (via Pandas)"] = ["DB_PCACE_data_analyzer_main.py", 1]
pydict["SQL database (via SQLite)"] = ["DB_SQL_main.py", 1]
pydict["Stanford CoreNLP"] = ["parsers_annotators_main.py", 1]
pydict["Semantic analysis (via TensorFlow)"] = ["", 0]
pydict["SRL Semantic Role Labeling"] = ["", 0]
pydict["Dictionary items by sentence index"] = ["sentence_analysis_util.dictionary_items_bySentenceID", 0, 3, 'txt']
pydict["Topic modeling (via MALLET & Gensim)"] = ["topic_modeling_main.py", 1]
pydict["utf-8 compliance"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["Style analysis (ALL options GUI)"] = ["style_analysis_main.py", 1]
pydict["Narrative analysis (ALL options GUI)"] = ["narrative_analysis_ALL_main.py", 1]
pydict["WHAT\'S IN YOUR CORPUS/DOCUMENT(S)? A SWEEPING VIEW"] = ["whats_in_your_corpus_main.py", 1]
pydict["Corpus/document(s) statistics (Sentences, words, lines)"] = ["style_analysis_main.py", 1]
pydict["Wordclouds (ALL options GUI)"] = ["wordclouds_main.py", 1]
pydict["WordNet"] = ["knowledge_graphs_WordNet_main.py", 1]
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
    GUI_util.setup_IO_configuration_options(False,scriptName,True)
    setup_IO_checkbox()

def setup_IO_checkbox():
    state = str(GUI_util.run_button['state'])
    if state != 'disabled':
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

handle_setup_options_OK_checkbox = tk.Checkbutton(window, state='disabled',
                                      variable=handle_setup_options_OK_checkbox_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                             handle_setup_options_OK_checkbox,
                                             True, False, True, False,
                                             90, GUI_IO_util.labels_x_coordinate,
                                             "The checkbox, always disabled, is ticked ON when the parser/annotator and corpus language options have been setup.\nIf the checkbox is OFF, click on the 'SETUP default NLP parser...' button to set up.")

NLP_package_language_config = GUI_IO_util.configPath+os.sep+'NLP_default_package_language_config.csv'
def handle_setup_options_checkbox(NLP_package_language_config):
    if os.path.isfile(NLP_package_language_config):
        handle_setup_options_OK_checkbox_var.set(1)
    else:
        handle_setup_options_OK_checkbox_var.set(0)
handle_setup_options_OK_checkbox_var.trace('w', lambda x, y, z: handle_setup_options_checkbox(NLP_package_language_config))

handle_setup_options_checkbox(NLP_package_language_config)

NLP_package_language_setup_button = tk.Button(window, text='SETUP default NLP parsers & annotators package and default corpus language', width=95, font=("Courier", 10, "bold"), command=lambda: call("python NLP_setup_package_language_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate+30,
                                               y_multiplier_integer,
                                               NLP_package_language_setup_button, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate+30,
                                               "The NLP Suite relies on a handful of external software to carry out specialized tasks (e.g., Stanford CoreNLP, Gephi).\nClick on the Setup button to select your preferred parser software (e.g., Stanford CoreNLP) and the laguage of your corpus (e.g., English)\nYour selected options will be used as default in all GUIs; but you can change your preferences at any time.")

open_default_NLP_package_language_config_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, NLP_package_language_config))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+GUI_IO_util.open_NLP_package_language_config_button, y_multiplier_integer,
                                               open_default_NLP_package_language_config_button, False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate, "Open the NLP_default_package_language_config.csv file containing the default NLP parser and annotators and corpus language options")

setup_software_checkbox = tk.Checkbutton(window, state='disabled',
                                         variable=setup_software_OK_checkbox_var, onvalue=1, offvalue=0, command=lambda: setup_external_programs_checkbox('',False))
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                             setup_software_checkbox,
                                             True, False, True, False,
                                             90, GUI_IO_util.labels_x_coordinate,
                                             "The checkbox, always disabled, is ticked ON when all external software have been installed.\nIf the checkbox is OFF, click on the 'SETUP external software' button to set up.")

software_dir = ''

def setup_external_programs_checkbox(software, only_check_missing=False):
    global software_dir
    silent = False
    if setup_software_OK_checkbox_var.get()==0 or software != '':
        if software_dir == None and software == '':
            return
        # missing_external_software = IO_libraries_util.get_missing_external_software_list('NLP_menu', '', '',True)
        software_dir, software_url, missing_external_software = IO_libraries_util.get_external_software_dir('NLP_menu', software, silent, only_check_missing)
        if missing_external_software!='':

            setup_software_OK_checkbox_var.set(0)
        else:
            setup_software_OK_checkbox_var.set(1)
    return missing_external_software
# setup_software_OK_checkbox_var.trace('w', lambda x, y, z: setup_external_programs_checkbox(''))

def callback(software: str):
    print('IN CALLBACK')
    software_setup_var.set(software)
    setup_external_programs_checkbox(software,False)

def setup_software_warning():
    global software
    mb.showwarning('External software option', 'Please, select next the external software that you would like to download/install using the dropdown menu.')
    software = GUI_IO_util.dropdown_menu_widget(window, "Please, select the external software to setup using the dropdown menu on the left, then click OK to accept your selection", ['Stanford CoreNLP', 'Gephi', 'Google Earth Pro', 'MALLET', 'WordNet'],'Stanford CoreNLP',callback)
    if software != None:
        setup_external_programs_checkbox(software,True)

# software_setup_button = tk.Button(window, text='Setup external software', width=95, font=("Courier", 10, "bold"), command=lambda: setup_software_warning())
software_setup_button = tk.Button(window, text='SETUP external software', width=95, font=("Courier", 10, "bold"), command=lambda: call("python NLP_setup_external_software_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate+30,
                                               y_multiplier_integer,
                                               software_setup_button, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate+30,
                                               "The NLP Suite relies on a handful of external software to carry out specialized tasks (e.g., Stanford CoreNLP, Gephi)\nClick on the Setup button to download and install these freeware software packages\nYou only have to do this once")

open_setup_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, GUI_IO_util.configPath+os.sep+'NLP_setup_external_software_config.csv'))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+GUI_IO_util.open_setup_software_button, y_multiplier_integer,
                                               open_setup_button, False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate, "Open the NLP_setup_external_software_config.csv file containing all external software installation paths")

general_tools_lb = tk.Label(window, text='General Utility Tools', foreground="red",font=("Courier", 12, "bold"))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               general_tools_lb)

# setup GUI widgets
data_file_handling_tools_var.set('')
file_handling_lb = tk.Label(window, text='Data & Files Handling Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               file_handling_lb, True)
data_file_handling_tools_menu = ttk.Combobox(window, width = 90, textvariable = data_file_handling_tools_var)
data_file_handling_tools_menu['values'] = constants_util.NLP_Suite_data_file_handling_tools_menu
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer, data_file_handling_tools_menu,
                                             False, False, True, False,
                                             90, GUI_IO_util.entry_box_x_coordinate,
                                             "Using the dropdown menu, select one of the available options and then click on RUN. Press Esc to clear selections.")

pre_processing_tools_var.set('')
pre_processing_lb = tk.Label(window, text='Pre-Processing Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               pre_processing_lb, True)

pre_processing_tools_menu = ttk.Combobox(window, width = 90, textvariable = pre_processing_tools_var)
pre_processing_tools_menu['values'] = constants_util.NLP_Suite_pre_processing_tools_menu
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer, pre_processing_tools_menu, False, False, True, False, 90, GUI_IO_util.entry_box_x_coordinate, "Using the dropdown menu, select one of the available options and then click on RUN. Press Esc to clear selections.")

statistical_tools_var.set('')
statistical_tools_lb = tk.Label(window, text='Statistical Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               statistical_tools_lb, True)
statistical_tools_menu = ttk.Combobox(window, width = 90, textvariable = statistical_tools_var)
statistical_tools_menu['values'] = ['Statistics (csv files)','Statistics (txt files)']
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer, statistical_tools_menu, False, False, True, False, 90, GUI_IO_util.entry_box_x_coordinate, "Using the dropdown menu, select one of the available options and then click on RUN. Press Esc to clear selections.")

visualization_lb = tk.Label(window, text='Visualization Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               visualization_lb, True)
visualization_menu = ttk.Combobox(window, width = 90, textvariable = visualization_tools_var)
visualization_menu['values'] = constants_util.NLP_Suite_visualization_tools_menu
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer, visualization_menu, False, False, True, False, 90, GUI_IO_util.entry_box_x_coordinate, "Using the dropdown menu, select one of the available options and then click on RUN. Press Esc to clear selections.")

# (startX, startY, endX, endY) where endX is the width of window
# https://stackoverflow.com/questions/40390746/how-to-correctly-use-tkinter-create-line-coordinates
# window.create_line(0,y_multiplier_integer,1000,y_multiplier_integer)

# leave a blank line to separate the linguistic analyses

linguistic_tools_lb = tk.Label(window, text='Linguistic Analysis Tools', foreground="red",font=("Courier", 12, "bold"))
# text.configure(font=("Times New Roman", 12, "bold"))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               linguistic_tools_lb)

corpus_tools_lb = tk.Label(window, text='CORPUS Analysis Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               corpus_tools_lb, True)
# tools that apply exclusively to a corpus
corpus_menu = ttk.Combobox(window, width = 90, textvariable = corpus_tools_var)
corpus_menu['values'] = constants_util.NLP_Suite_corpus_tools_menu
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer, corpus_menu, False, False, True, False, 90, GUI_IO_util.entry_box_x_coordinate, "Using the dropdown menu, select one of the available options and then click on RUN. Press Esc to clear selections.")

# 'KWIC (Key Word In Context)')

# corpus_document_tools_var.set('')
corpus_document_tools_lb = tk.Label(window, text='CORPUS/DOCUMENT Analysis Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               corpus_document_tools_lb, True)
#tools that can be applied to either corpus or single document
corpus_documents_menu = ttk.Combobox(window, width = 90, textvariable = corpus_document_tools_var)
corpus_documents_menu['values'] = constants_util.NLP_Suite_corpus_document_tools_menu
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer, corpus_documents_menu, False, False, True, False, 90, GUI_IO_util.entry_box_x_coordinate, "Using the dropdown menu, select one of the available options and then click on RUN. Press Esc to clear selections.")

sentence_tools_var.set('')
sentence_tools_lb = tk.Label(window, text='SENTENCE Analysis Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               sentence_tools_lb, True)
sentence_tools_menu = ttk.Combobox(window, width = 90, textvariable = sentence_tools_var)
sentence_tools_menu['values'] = ['Sentence analysis (ALL options GUI)']
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer, sentence_tools_menu, False, False, True, False, 90, GUI_IO_util.entry_box_x_coordinate, "Using the dropdown menu, select one of the available options and then click on RUN. Press Esc to clear selections.")


def getScript(script):
    global script_to_run, IO_values
    script_to_run, IO_values = IO_files_util.getScript(pydict, script)

data_file_handling_tools_var.trace('w', lambda x, y, z: getScript(data_file_handling_tools_var.get()))
pre_processing_tools_var.trace('w', lambda x, y, z: getScript(pre_processing_tools_var.get()))
statistical_tools_var.trace('w', lambda x, y, z: getScript(statistical_tools_var.get()))
visualization_tools_var.trace('w', lambda x, y, z: getScript(visualization_tools_var.get()))
corpus_tools_var.trace('w', lambda x, y, z: getScript(corpus_tools_var.get()))
corpus_document_tools_var.trace('w', lambda x, y, z: getScript(corpus_document_tools_var.get()))
sentence_tools_var.trace('w', lambda x, y, z: getScript(sentence_tools_var.get()))

def openYouTube(video_url):
    if video_url!='':
        webbrowser.open_new_tab(video_url)
    else:
        mb.showwarning(title='Warning',
                   message='The YouTube video ' + video_url + ' could not be found in the NLP Suite YouTube channel.\n\nPlease, warn the NLP Suite developers.')

videos_lookup = {'Setup the NLP Suite':'https://www.youtube.com/watch?v=W56SU9oAbpc&list=PL95lLs07jOtqArcIYzO-FX14T7lkauuab&index=2'}
videos_options = 'Setup the NLP Suite'

TIPS_lookup = {'NLP Suite: Package description': 'TIPS_NLP_NLP Suite Package description.pdf',
               'pip install & Anaconda environments': 'TIPS_NLP_Anaconda NLP environment pip.pdf',
               'Things to do with words: NLP approach': 'TIPS_NLP_Things to do with words NLP approach.pdf',
               'Setup Input/Output configuration for your corpus': 'TIPS_NLP_Setup INPUT-OUTPUT options.pdf',
               'Setup external software (e.g., MALLET)': 'TIPS_NLP_Setup external software.pdf',
               'NLP Suite: General tools': 'TIPS_NLP_NLP Suite general tools.pdf',
               'NLP Suite: Tools of linguistic analysis': 'TIPS_NLP_NLP Suite Tools of linguistic analysis.pdf',
               'NLP basic language': 'TIPS_NLP_NLP Basic Language.pdf',
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
                                  "The NLP-Suite relies for some of its operations on external software that needs to be downloaded and installed (Stanford CoreNLP, WordNet, MALLET, SENNA, Gephi, Google Earth Pro). When using any of these software, the NLP-Suite needs to know where they have been installed on your computer (e.g., C:\Program Files (x86)\WordNet).\n\nPlease, click on the 'Select external software' button to select the software option that you want to link to its installation directory. YOUR SELECTION WILL BE SAVED IN THE NLP_setup_external_software_config.csv FILE UNDER THE SUBDIRECTORY config.\n\nThe checkbox at the beginning of the line is set to OK if all external software packages have been successfully installed.\n\nYou can open the NLP_setup_external_software_config.csv file by clicking on the button at the end of the line.\n\n"
                                  "The NLP_setup_external_software_config.csv file has three columns (with headers Software, Path, Download_link) and 6 rows, one for each of the external software and with the followining expected labels: Stanford CoreNLP, MALLET, SENNA, WordNet, Gephi, Google Earth Pro and where "
                                  "Path refers to the installation path of the software on your machine. "\
                                  "As an example, the three fields for the Stanford CoreNLP software would look like this: "
                                  "Stanford CoreNLP   C:/Program Files (x86)/stanford-corenlp-4.3.1   https://stanfordnlp.github.io/CoreNLP/download.html. "
                                  "Needless to say C:/Program Files (x86)/stanford-corenlp-4.3.1 will change, depending upon where you install CoreNLP locally.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer+1,"NLP Suite Help",
                                  "Please, using the dropdown menu, select one of the many options available for data and file handling." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, using the dropdown menu, select one of the many options available for pre-processing text." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, using the dropdown menu, select the option available for statistical analyses." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, using the dropdown menu, select one of the many options available for visualizing data.\n\nNearly all linguistic tools, however, automatically visualize results, typically in Excel charts, but also in more specialized graphical tools, such as network graphs in Gephi or GIS (Geographic Information System) maps in Google Earth Pro or in Google Maps." + GUI_IO_util.msg_Esc)
    # leave a blank line to separate the linguistic analyses
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer+1,"NLP Suite Help",
                                  "Please, using the dropdown menu, select one of the many options available for analyzing your corpus.\n\nCORPUS TOOLS APPLY TO MULTIPLE DOCUMENTS ONLY, RATHER THAN TO A SINGLE DOCUMENT.\n\nIn INPUT the tools expect multiple documents stored in a directory (the 'corpus')." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, using the dropdown menu, select one of the many options available for analyzing your corpus and/or a single document.\n\nTHE TOOLS IN THIS CATEGORY, APPLY TO EITHER MULTIPLE DOCUMENTS (THE 'CORPUS') OR TO A SINGLE DOCUMENT.\n\nIn INPUT the tools expect either multiple documents stored in a directory (the 'corpus') or a single document." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, using the dropdown menu, select one of the many options available for analyzing your corpus/document by sentence index.\n\nTHE TOOLS IN THIS CATEGORY, APPLY TO EITHER MULTIPLE DOCUMENTS (THE 'CORPUS') OR TO A SINGLE DOCUMENT; BUT THEY ALSO PROVIDE SENTENCE-BASED INFORMATION FOR MORE IN-GRAINED ANALYSES.\n\nIn INPUT the tools expect either multiple documents stored in a directory (the 'corpus') or a single document." + GUI_IO_util.msg_Esc)

    return y_multiplier_integer
y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

# change the value of the readMe_message
readMe_message = "This Python 3 script is the front end for a wide collection of Java and Python Natural Language Processing (NLP) tools.\n\nThe set of tools are divided into GENERAL UTILITY TOOLS (data and file handling, pre-processing, statistical, visualization) and LINGUISTIC ANALYSIS TOOLS.\n\nLINGUISTIC ANALYSIS TOOLS are divided into tools that expect in input CORPUS DATA (i.e., multiple documents stored in a directory), CORPUS and/or SINGLE DOCUMENT, and SENTENCE.\n\nWhile some linguistic tools are specific for one of these three categories (e.g., topic modeling cannot be performed on a single document), MANY TOOLS OVERLAP. Tools that can work on a single file or a corpus are all classified under CORPUS/DOCUMENT tools. SENTENCE TOOLS still require either a corpus or a single document in input; but they also provide in output sentence-level information for more ingrained linguistic analyses.\n\nAll tools are open source freeware software released under the GNU LGPLv2.1 license (http://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html).\n\nYou can cite the NLP Suite as:\n\nFranzosi, Roberto. 2020. NLP Suite: A collection of natural language processing and visualization tools GitHub: https://github.com/NLP-Suite/NLP-Suite/wiki."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

if platform == 'darwin':
    window.update()

temp_config_filename = config_filename # 'NLP_menu_config.csv'
routine_options = reminders_util.getReminders_list(temp_config_filename)

reminders_util.checkReminder(temp_config_filename,
                             reminders_util.title_options_NLP_Suite_architecture,
                             reminders_util.message_NLP_Suite_architecture,
                             True)
routine_options = reminders_util.getReminders_list(temp_config_filename)

if sys.platform == 'darwin':
    reminders_util.checkReminder(temp_config_filename,
                                 reminders_util.title_options_TensorFlow,
                                 reminders_util.message_TensorFlow,
                                 True)
    routine_options = reminders_util.getReminders_list(temp_config_filename)

# check for missing I/O configuration options
setup_IO_checkbox()

# check for missing external software
missing_external_software = setup_external_programs_checkbox('', True)

if missing_external_software!='':
    reminders_util.checkReminder(temp_config_filename,
                                 reminders_util.title_options_missing_external_software_NLP_main_GUI,
                                 reminders_util.message_missing_external_software_NLP_main_GUI,
                                 True)
    routine_options = reminders_util.getReminders_list(temp_config_filename)

if not setup_IO_OK_checkbox_var.get() or not handle_setup_options_OK_checkbox_var.get() or not setup_software_OK_checkbox_var.get():
    answer = tk.messagebox.askyesno("Warning", 'Some (or all) of the required three NLP Suite setup options (I/O configuration, NLP package and language, external software displayed in the three buttons at the top of this GUI) are not completed.\n\nDo you want to watch the video on how to setup the NLP Suite options?')
    if answer:
        GUI_util.videos_dropdown_field.set('Setup the NLP Suite')
        # GUI_util.watch_video(videos_lookup, scriptName)
GUI_util.window.mainloop()
