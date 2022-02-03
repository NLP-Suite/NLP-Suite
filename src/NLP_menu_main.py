# written by Roberto Franzosi October 2019, 
# edited Spring 2020, July 2020

#input: 1. file name
#input: 1. directory name
#output: directory name

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"NLP",['os','tkinter','atexit'])==False:
    sys.exit(0)

import os
from sys import platform
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
import atexit

import GUI_IO_util
import IO_files_util
import reminders_util
import constants_util
from update_util import update_self


def exit_handler():
    update_self()

atexit.register(exit_handler)


# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,input_main_dir_path, output_dir_path,
    openOutputFiles,
    createExcelCharts,
    script_to_run,
    IO_values):
    if script_to_run=='':
        mb.showwarning('No option selection','No option has been selected.\n\nPlease, using the dropdown menus, select one of the many General tools and/or Linguistic analysis tools, then click on RUN again.')
        return
    IO_files_util.runScript_fromMenu_option(script_to_run,IO_values,inputFilename,input_main_dir_path, output_dir_path, openOutputFiles,createExcelCharts)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_Excel_chart_output_checkbox.get(),
                            script_to_run,
                            IO_values)

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

IO_setup_display_brief=False

GUI_width=GUI_IO_util.get_GUI_width(1)
GUI_height=670 # height of GUI with full I/O display

GUI_size = str(GUI_width) + 'x' + str(GUI_height)

# GUI_size='1150x670'
GUI_label='Graphical User Interface (GUI) for a suite of tools of Natural Language Processing (NLP) & Data Visualization'
# there is currently NO way to setup a specific I/O config for the NLP_menu_main; it can only have the default setup
# config_filename='NLP_config.csv'
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = scriptName.replace('main.py', 'config.csv')
# overwrite the standard way of setting up config_filename, since NLP_menu_main saves to default_config
config_filename = 'default_config.csv'

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
pydict["Stanford CoreNLP"] = ["knowledge_graphs_main.py", 1]
pydict["CoreNLP annotator - date (NER normalized date)"] = ["Stanford_CoreNLP_main.py", 1]
pydict["CoreNLP annotator - gender (male & female names; via CoreNLP and dictionaries)"] = ["html_annotator_gender_main.py", 1]
pydict["CoreNLP annotator - quote"] = ["Stanford_CoreNLP_main.py", 1]
pydict["CoreNLP annotator - coreference (pronominal)"] = ["Stanford_CoreNLP_coreference_main.py", 1]
pydict["Knowledge graphs: DBpedia & YAGO"] = ["knowledge_graphs_DBpedia_YAGO_main.py", 1]
pydict["HTML annotator"] = ["html_annotator_main.py", 1]
pydict["HTML annotator extractor"] = ["html_annotator_main.py", 1]
pydict["Annotator - hedge/uncertainty"] = ["", 0]
pydict["CoNLL table analyzer - Search the CoNLL table"] = ["CoNLL_table_analyzer_main.py", 1]
pydict["CoNLL table analyzer - Clause, noun, verb, function words frequencies"] = ["CoNLL_table_analyzer_main.py", 1]
pydict["Statistics (csv & txt files)"] = ["statistics_NLP_main.py", 1]
pydict["Co-Reference PRONOMINAL resolution (via Stanford CoreNLP)"] = ["Stanford_CoreNLP_main.py", 1]
pydict["Co-Occurrences viewer"] = ["NGrams_CoOccurrences_Viewer_main.py", 1]
pydict["Data manager (csv files via Pandas)"] = ["data_manager_main.py", 1]
pydict["File checker (file content)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File checker (file content utf-8 encoding)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File checker (file name)"] = ["file_manager_main.py", 1]
pydict["File cleaner (Change to ASCII non-ASCII apostrophes & quotes and % to percent)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File cleaner (Find & Replace string)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File cleaner (Remove blank lines from txt file(s))"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File cleaner (Add full stop (.) at the end of paragraphs without end-of-paragraph punctuation)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File cleaner (Pronominal resolution via CoreNLP)"] = ["Stanford_CoreNLP_coreference_main.py", 1]
pydict["File classifier (dumb classifier via embedded date) (file name)"] = ["file_filename_checker_main.py", 1]
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
pydict["Excel charts"] = ["Excel_charts_main.py", 1]
pydict["Network graphs (Gephi)"] = ["visualization_main.py", 1]  # ["", 0] not available
pydict["Geographic maps: Geocoding & maps"] = ["GIS_main.py", 1]
pydict["Geographic maps: Google Earth Pro"] = ["GIS_Google_Earth_main.py", 1]
pydict["Geographic maps: From texts to maps"] = ["GIS_main.py", 1]
pydict["Geographic distances between locations"] = ["GIS_distance_main.py", 1]  # GIS_distance_main.py
pydict["Gender guesser"] = ["Gender guesser", 0, 0, '']
pydict["Language detection"] = ["style_analysis_main.py", 1]
pydict["NER (Named Entity Recognition) extractor"] = ["Stanford_CoreNLP_NER_main.py", 1]  # ',0 not available
pydict["NER (Named Entity Recognition) extractor by sentence index"] = ["Stanford_CoreNLP_NER_main.py", 1]
pydict["Newspaper article/Document titles"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["N-grams (word & character)"] = ["NGrams_CoOccurrences_Viewer_main.py", 1]
pydict["N-grams viewer"] = ["NGrams_CoOccurrences_Viewer_main.py", 1]
pydict["Nominalization"] = ["nominalization_main.py", 1]
pydict["Search CoNLL table"] = ["CoNLL_table_analyzer_main.py", 1]
pydict["Search text file(s) for n-grams & co-occurrences (N-grams viewer)"] = ["NGrams_CoOccurrences_Viewer_main.py", 1]
pydict["Search text file(s) for words/collocations"] = ["file_search_byWord_main.py", 1]
pydict["Sentence analysis (An overall GUI)"] = ["sentence_analysis_main.py", 1]
pydict["Sentence complexity"] = ["sentence_analysis_main.py", 1]
pydict["Sentence/text readability (via textstat)"] = ["sentence_analysis_main.py", 1]
pydict["Sentence visualization: Dependency tree viewer (png graphs)"] = ["sentence_analysis_main.py", 1]
pydict["Sentence visualization: Dynamic sentence network viewer (Gephi graphs)"] = ["", 0]  # not available
pydict["Sentiment analysis"] = ["sentiment_analysis_main.py", 1]
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
pydict["SQL database (via SQLite)"] = ["DB_SQL_main.py", 1]
pydict["Stanford CoreNLP"] = ["Stanford_CoreNLP_main.py", 1]
pydict["Semantic analysis (via TensorFlow)"] = ["", 0]
pydict["SRL Semantic Role Labeling"] = ["", 0]
pydict["SVO extractor & visualization"] = ["SVO_main.py", 1]
pydict["Dictionary items by sentence index"] = ["sentence_analysis_util.dictionary_items_bySentenceID", 0, 3, 'txt']
pydict["Topic modeling (via Gensim)"] = ["topic_modeling_gensim_main.py", 1]
pydict["Topic modeling (via MALLET)"] = ["topic_modeling_mallet_main.py", 1]
pydict["utf-8 compliance"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["Style analysis"] = ["style_analysis_main.py", 1]
pydict["Narrative analysis"] = ["narrative_analysis_main.py", 1]
pydict["WHAT\'S IN YOUR CORPUS? A SWEEPING VIEW"] = ["whats_in_your_corpus_main.py", 1]
pydict["Corpus statistics (Sentences, words, lines)"] = ["statistics_NLP_main.py", 1]
pydict["Word clouds"] = ["wordclouds_main.py", 1]
pydict["WordNet"] = ["knowledge_graphs_WordNet_main.py", 1]
pydict["Word2Vec (via Gensim)"] = ["word2vec_main.py", 1]

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
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               setup_IO_OK_checkbox, True)

def setup_IO():
    GUI_util.setup_IO_configuration_options(False,scriptName,True)
    setup_IO_checkbox()

def setup_IO_checkbox():
    state = str(GUI_util.run_button['state'])
    if state != 'disabled':
        setup_IO_OK_checkbox_var.set(1)
    else:
        setup_IO_OK_checkbox_var.set(0)

IO_setup_button = tk.Button(window, text='Setup default I/O options: INPUT corpus file(s) and OUTPUT files directory', width=95, font=("Courier", 10, "bold"), command=lambda: setup_IO())
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+30, y_multiplier_integer,
                                               IO_setup_button,True)

open_default_IO_config_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, GUI_IO_util.configPath+os.sep+'default_config.csv'))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+GUI_IO_util.open_IO_config_button, y_multiplier_integer,
                                               open_default_IO_config_button)

setup_software_checkbox = tk.Checkbutton(window, state='disabled',
                                         variable=setup_software_OK_checkbox_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               setup_software_checkbox,True)
software_dir = ''

def setup_external_programs_checkbox(software):
    global software_dir
    silent = False
    only_check_missing = False
    if setup_software_OK_checkbox_var.get()==0:
        if software_dir == None and software == '':
            return
        software_dir, missing_external_software = IO_libraries_util.get_external_software_dir('NLP_menu', software, silent, only_check_missing)
        if len(missing_external_software) > 0:
            setup_software_OK_checkbox_var.set(0)
        else:
            setup_software_OK_checkbox_var.set(1)
setup_software_OK_checkbox_var.trace('w', lambda x, y, z: setup_external_programs_checkbox(''))

def callback(software: str):
    software_setup_var.set(software)
    setup_external_programs_checkbox(software)

def setup_software_warning():
    global software
    mb.showwarning('External software option', 'Please, select next the external software that you would like to download/install using the dropdown menu.')
    software = GUI_IO_util.dropdown_menu_widget(window, "Please, select the external software to setup using the dropdown menu on the left, then click OK to accept your selection", ['Stanford CoreNLP', 'Gephi', 'Google Earth Pro', 'MALLET', 'SENNA', 'WordNet'],'Stanford CoreNLP',callback)
    if software != None:
        setup_external_programs_checkbox(software)

software_setup_button = tk.Button(window, text='Setup external software', width=95, font=("Courier", 10, "bold"), command=lambda: setup_software_warning())
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+30, y_multiplier_integer,
                                               software_setup_button,True)

open_setup_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, GUI_IO_util.configPath+os.sep+'software_config.csv'))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+GUI_IO_util.open_setup_software_button, y_multiplier_integer,
                                               open_setup_button)

general_tools_lb = tk.Label(window, text='General Tools', foreground="red",font=("Courier", 12, "bold"))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               general_tools_lb)

# setup GUI widgets
data_file_handling_tools_var.set('')
file_handling_lb = tk.Label(window, text='Data & Files Handling Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               file_handling_lb, True)
data_file_handling_tools_menu = ttk.Combobox(window, width = 90, textvariable = data_file_handling_tools_var)
data_file_handling_tools_menu['values'] = constants_util.NLP_Suite_data_file_handling_tools_menu
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer, data_file_handling_tools_menu)

pre_processing_tools_var.set('')
pre_processing_lb = tk.Label(window, text='Pre-Processing Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               pre_processing_lb, True)

pre_processing_tools_menu = ttk.Combobox(window, width = 90, textvariable = pre_processing_tools_var)
pre_processing_tools_menu['values'] = constants_util.NLP_Suite_pre_processing_tools_menu
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer, pre_processing_tools_menu)

statistical_tools_var.set('')
statistical_tools_lb = tk.Label(window, text='Statistical Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               statistical_tools_lb, True)
statistical_tools_menu = ttk.Combobox(window, width = 90, textvariable = statistical_tools_var)
statistical_tools_menu['values'] = ['Statistics (csv & txt files)']
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer, statistical_tools_menu)

visualization_lb = tk.Label(window, text='Visualization Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               visualization_lb, True)
visualization_menu = ttk.Combobox(window, width = 90, textvariable = visualization_tools_var)
visualization_menu['values'] = constants_util.NLP_Suite_visualization_tools_menu
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer, visualization_menu)

# (startX, startY, endX, endY) where endX is the width of window
# https://stackoverflow.com/questions/40390746/how-to-correctly-use-tkinter-create-line-coordinates
# window.create_line(0,y_multiplier_integer,1000,y_multiplier_integer)

# leave a blank line to separate the linguistic analyses

linguistic_tools_lb = tk.Label(window, text='Linguistic Analysis Tools', foreground="red",font=("Courier", 12, "bold"))
# text.configure(font=("Times New Roman", 12, "bold"))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               linguistic_tools_lb)

corpus_tools_lb = tk.Label(window, text='CORPUS Analysis Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               corpus_tools_lb, True)
# tools that apply exclusively to a corpus
corpus_menu = ttk.Combobox(window, width = 90, textvariable = corpus_tools_var)
corpus_menu['values'] = constants_util.NLP_Suite_corpus_tools_menu
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer, corpus_menu)

# 'KWIC (Key Word In Context)')

# corpus_document_tools_var.set('')
corpus_document_tools_lb = tk.Label(window, text='CORPUS/DOCUMENT Analysis Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               corpus_document_tools_lb, True)
#tools that can be applied to either corpus or single document
corpus_documents_menu = ttk.Combobox(window, width = 90, textvariable = corpus_document_tools_var)
corpus_documents_menu['values'] = constants_util.NLP_Suite_corpus_document_tools_menu
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer, corpus_documents_menu)

sentence_tools_var.set('')
sentence_tools_lb = tk.Label(window, text='SENTENCE Analysis Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               sentence_tools_lb, True)
sentence_tools_menu = ttk.Combobox(window, width = 90, textvariable = sentence_tools_var)
sentence_tools_menu['values'] = ['Sentence analysis (An overall GUI)']
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer, sentence_tools_menu)


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

videos_lookup = {'Help':'Help.mp4','IO Setup':'IO_Setup.mp4'}
videos_options = 'Help','IO Setup'

TIPS_lookup = {'NLP Suite: Package description': 'TIPS_NLP_NLP Suite Package description.pdf',
               'Things to do with words: NLP approach': 'TIPS_NLP_Things to do with words NLP approach.pdf',
               'Setup Input/Output configuration for your corpus': 'TIPS_NLP_Setup INPUT-OUTPUT options.pdf',
               'Setup external software (e.g., MALLET)': 'TIPS_NLP_Setup external software.pdf',
               'NLP Suite: General tools': 'TIPS_NLP_NLP Suite general tools.pdf',
               'NLP Suite: Tools of linguistic analysis': 'TIPS_NLP_NLP Suite Tools of linguistic analysis.pdf',
               'NLP basic language': 'TIPS_NLP_NLP Basic Language.pdf',
               'Things to do with words: Overall view': 'TIPS_NLP_Things to do with words Overall view.pdf',
               'Things to do with words: Content analysis': 'TIPS_NLP_Things to do with words Content analysis.pdf',
               'Things to do with words: Frame analysis': 'TIPS_NLP_Things to do with words Frame analysis.pdf',
               'Things to do with words: Narrative analysis': 'TIPS_NLP_Things to do with words Narrative analysis.pdf',
               'Things to do with words: Rhetoric (Arguments)': 'TIPS_NLP_Things to do with words Rhetorical analysis Arguments.pdf',
               'Things to do with words: Rhetoric (Tropes & Figures)': 'TIPS_NLP_Things to do with words Rhetorical analysis Tropes and Figures.pdf',
               'Style analysis': 'TIPS_NLP_Style analysis.pdf',
               'Text encoding (utf-8)': 'TIPS_NLP_Text encoding (utf-8).pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf'}
TIPS_options = 'NLP Suite: Package description', 'Things to do with words: NLP approach', 'Setup Input/Output configuration for your corpus', 'Setup external software (e.g., MALLET)', 'NLP Suite: General tools', 'NLP Suite: Tools of linguistic analysis', 'NLP basic language', 'Things to do with words: Overall view', 'Things to do with words: Content analysis', 'Things to do with words: Frame analysis', 'Things to do with words: Narrative analysis', 'Things to do with words: Rhetoric (Arguments)', 'Things to do with words: Rhetoric (Tropes & Figures)', 'Style analysis', 'Text encoding (utf-8)','csv files - Problems & solutions'


# reminders content for specific GUIs are set in the csv file reminders

# 'KWIC',
# 'KWIC':'TIPS_NLP_KWIC (Key Words In Context).pdf'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, basic_y_coordinate, y_step):
    # GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",GUI_IO_util.msg_anyFile)
    # GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_anyData)
    # GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help",GUI_IO_util.msg_outputDirectory)
    # leave a blank line to separate general tools
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step, "Help",
                                  "Please, click on the button to the right to open the GUI that will allow you to setup default I/O options:\n   INPUT file and or directory of files (your corpus) and\n   OUTPUT directory where all files (csv, txt, html, kml, jpg) produced by the NLP-Suite tools will be saved.\n\nThese default I/O options will be used for all GUIs.\n\nThe checkbox at the beginning of the line is set to OK if all INPUT/OUTPUT options have been successfully selected and saved in the default_config.csv file under the subdirecory config.\n\nYou can open the default_config.csv file by clicking on the button at the end of the line." + GUI_IO_util.msg_IO_config)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 2, "Help",
                                  "The NLP-Suite relies for some of its operations on external software that needs to be downloaded and installed (Stanford CoreNLP, WordNet, MALLET, SENNA, Gephi, Google Earth Pro). When using any of these software, the NLP-Suite needs to know where they have been installed on your computer (e.g., C:\Program Files (x86)\WordNet).\n\nPlease, click on the 'Select external software' button to select the software option that you want to link to its installation directory. YOUR SELECTION WILL BE SAVED IN THE software_config.csv FILE UNDER THE SUBDIRECTORY config.\n\nThe checkbox at the beginning of the line is set to OK if all external software packages have been successfully installed.\n\nYou can open the software_config.csv file by clicking on the button at the end of the line.\n\n"
                                  "The software_config.csv file has three columns (with headers Software, Path, Download_link) and 6 rows, one for each of the external software and with the followining expected labels: Stanford CoreNLP, MALLET, SENNA, WordNet, Gephi, Google Earth Pro and where "
                                  "Path refers to the installation path of the software on your machine. "\
                                  "As an example, the three fields for the Stanford CoreNLP software would look like this: "
                                  "Stanford CoreNLP   C:/Program Files (x86)/stanford-corenlp-4.3.1   https://stanfordnlp.github.io/CoreNLP/download.html. "
                                  "Needless to say C:/Program Files (x86)/stanford-corenlp-4.3.1 will change, depending upon where you install CoreNLP locally.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 4, "Help",
                                  "Please, using the dropdown menu, select one of the many options available for data and file handling." + GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 5, "Help",
                                  "Please, using the dropdown menu, select one of the many options available for pre-processing text." + GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 6, "Help",
                                  "Please, using the dropdown menu, select the option available for statistical analyses." + GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 7, "Help",
                                  "Please, using the dropdown menu, select one of the many options available for visualizing data.\n\nNearly all linguistic tools, however, automatically visualize results, typically in Excel charts, but also in more specialized graphical tools, such as network graphs in Gephi or GIS (Geographic Information System) maps in Google Earth Pro or in Google Maps." + GUI_IO_util.msg_Esc)
    # leave a blank line to separate the linguistic analyses
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 9, "Help",
                                  "Please, using the dropdown menu, select one of the many options available for analyzing your corpus.\n\nCORPUS TOOLS APPLY TO MULTIPLE DOCUMENTS ONLY, RATHER THAN TO A SINGLE DOCUMENT.\n\nIn INPUT the tools expect multiple documents stored in a directory (the 'corpus')." + GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 10, "Help",
                                  "Please, using the dropdown menu, select one of the many options available for analyzing your corpus and/or a single document.\n\nTHE TOOLS IN THIS CATEGORY, APPLY TO EITHER MULTIPLE DOCUMENTS (THE 'CORPUS') OR TO A SINGLE DOCUMENT.\n\nIn INPUT the tools expect either multiple documents stored in a directory (the 'corpus') or a single document." + GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 11, "Help",
                                  "Please, using the dropdown menu, select one of the many options available for analyzing your corpus/document by sentence index.\n\nTHE TOOLS IN THIS CATEGORY, APPLY TO EITHER MULTIPLE DOCUMENTS (THE 'CORPUS') OR TO A SINGLE DOCUMENT; BUT THEY ALSO PROVIDE SENTENCE-BASED INFORMATION FOR MORE IN-GRAINED ANALYSES.\n\nIn INPUT the tools expect either multiple documents stored in a directory (the 'corpus') or a single document." + GUI_IO_util.msg_Esc)


help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), GUI_IO_util.get_basic_y_coordinate(),
             GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message = "This Python 3 script is the front end for a wide collection of Java and Python Natural Language Processing (NLP) tools.\n\nThe set of tools are divided into GENERAL TOOLS (data and file handling, pre-processing, statistical, visualization) and LINGUISTIC ANALYSIS TOOLS.\n\nLINGUISTIC ANALYSIS TOOLS are divided into tools that expect in input CORPUS DATA (i.e., multiple documents stored in a directory), CORPUS and/or SINGLE DOCUMENT, and SENTENCE.\n\nWhile some linguistic tools are specific for one of these three categories (e.g., topic modeling cannot be performed on a single document), MANY TOOLS OVERLAP. Tools that can work on a single file or a corpus are all classified under CORPUS/DOCUMENT tools. SENTENCE TOOLS still require either a corpus or a single document in input; but they also provide in output sentence-level information for more ingrained linguistic analyses.\n\nAll tools are open source freeware software released under the GNU LGPLv2.1 license (http://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html).\n\nYou can cite the NLP Suite as:\n\nFranzosi, Roberto. 2020. NLP Suite: A collection of natural language processing and visualization tools GitHub: https://github.com/NLP-Suite/NLP-Suite/wiki."
readMe_command = lambda: GUI_IO_util.readme_button(window, GUI_IO_util.get_help_button_x_coordinate(),
                                                   GUI_IO_util.get_basic_y_coordinate(), "Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

if platform == 'darwin':
    window.update()

routine_options = reminders_util.getReminders_list('NLP_config.csv')

reminders_util.checkReminder('NLP_config.csv',
                             reminders_util.title_options_NLP_Suite_welcome,
                             reminders_util.message_NLP_Suite_welcome,
                             True)

reminders_util.checkReminder('NLP_config.csv',
                             reminders_util.title_options_NLP_Suite_architecture,
                             reminders_util.message_NLP_Suite_architecture,
                             True)
routine_options = reminders_util.getReminders_list('NLP_config.csv')

# check for missing I/O configuration options
setup_IO_checkbox()

# check for missing external software
setup_external_programs_checkbox('')

GUI_util.window.mainloop()
