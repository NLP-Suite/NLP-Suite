# written by Roberto Franzosi October 2019, 
# edited Spring 2020, July 2020

#input: 1. file name
#input: 1. directory name
#output: directory name

import sys
import GUI_util
import IO_libraries_util

# if IO_util.install_all_packages("NLP",['os','tkinter','subprocess','ntpath','nltk','webbrowser'])==False:
import IO_user_interface_util

if IO_libraries_util.install_all_packages(GUI_util.window,"NLP",['os','tkinter'])==False:
    sys.exit(0)

import tkinter as tk
import tkinter.messagebox as mb
from sys import platform
from subprocess import call

import GUI_IO_util
import IO_files_util
import reminders_util
import config_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,input_main_dir_path, output_dir_path,
    openOutputFiles,
    createExcelCharts,
    script_to_run,
    IO_values):
    if script_to_run=='':
        mb.showwarning('No option selection','No option has been selected.\n\nPlease, select an option and try again.')
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

GUI_size='1150x670'
GUI_label='Graphical User Interface (GUI) for a suite of tools of Natural Language Processing (NLP) & Data Visualization'
# config_filename='NLP-config.txt'
# there is now now way to setup a specific I/O config for the NLP_menu_main; it can only have the default setup
config_filename='default-config.txt'
# The 6 values of config_option refer to:
#   software directory
#   input file 1 for CoNLL file 2 for TXT file 3 for csv file 4 for any type of file
#   input dir
#   input secondary dir
#   output file
#   output dir
config_option=[0,2,1,0,0,1]
# config_option=[0,0,0,0,0,0]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

# # GUI CHANGES add following lines to every special GUI
# # +2 is the number of lines starting at 1 of IO widgets
y_multiplier_integer = GUI_util.y_multiplier_integer + 0
window = GUI_util.window
config_input_output_options = GUI_util.config_input_output_options
config_filename = GUI_util.config_filename

ScriptName = 'NLP_menu_main'

GUI_util.GUI_top(config_input_output_options, config_filename, IO_setup_display_brief, ScriptName)

setup_IO_OK_checkbox_var = tk.IntVar()
setup_software_OK_checkbox_var = tk.IntVar()


script_to_run=''
IO_values=''

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

pydict = {}
pydict[""] = ["", 0]  # not available
# https://stanfordnlp.github.io/CoreNLP/quote.html
pydict["Stanford CoreNLP"] = ["annotator_main.py", 1]
pydict["Annotator extractor"] = ["annotator_main.py", 1]
pydict["Annotator - date (NER normalized date, via CoreNLP)"] = ["Stanford_CoreNLP_main.py", 1]
pydict["Annotator - gender (male & female names; via CoreNLP and dictionaries)"] = ["annotator_gender_main.py", 1]
pydict["Annotator - quote (via CoreNLP)"] = ["Stanford_CoreNLP_main.py", 1]
pydict["Annotator - dictionary, gender, DBpedia, YAGO"] = ["annotator_main.py", 1]
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
pydict["File classifier (dumb classifier via embedded date) (file name)"] = ["file_filename_checker_main.py", 1]
pydict["File finder (file name)"] = ["file_manager_main.py", 1]
pydict["File finder (file content for words/collocations)"] = ["file_finder_byWord_main.py", 1]
pydict["File-type converter (csv, docx, pdf, rtf --> txt)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File matcher (file name)"] = ["file_matcher_main.py", 1]
pydict["File merger (file content)"] = ["file_merger_main.py", 1]
pydict["File splitter (file content)"] = ["file_splitter_main.py", 1]
pydict["File manager (List, Rename, Copy, Move, Delete, Count)"] = ["file_manager_main.py", 1]
pydict["Find non-related documents"] = ["social_science_research_main.py", 1]
pydict["Excel charts"] = ["Excel_charts_main.py", 1]
pydict["Network graphs (Gephi)"] = ["", 0]  # not available
pydict["Geographic maps: Geocoding & maps"] = ["GIS_main.py", 1]
pydict["Geographic maps: Google Earth Pro"] = ["GIS_Google_Earth_main.py", 1]
pydict["Geographic maps: From texts to maps"] = ["GIS_main.py", 1]
pydict["Geographic distances between locations"] = ["", 0]  # GIS_distance_main.py
pydict["Gender guesser"] = ["Gender guesser", 0, 0, '']
pydict["Language detection"] = ["style_analysis_main.py", 1]
pydict["NER (Named Entity Recognition) extractor"] = ["Stanford_CoreNLP_NER_main.py", 1]  # ',0 not available
pydict["NER (Named Entity Recognition) extractor by sentence index"] = ["Stanford_CoreNLP_NER_main.py", 1]
pydict["Newspaper article/Document titles"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["N-grams (word & character)"] = ["NGrams_CoOccurrences_Viewer_main.py", 1]
pydict["N-grams viewer"] = ["NGrams_CoOccurrences_Viewer_main.py", 1]
pydict["Nominalization"] = ["nominalization_main.py", 1]
pydict["Search text file(s) for n-grams & co-occurrences"] = ["NGrams_CoOccurrences_Viewer_main.py", 1]
pydict["Search text file(s) for words/collocations"] = ["file_finder_byWord_main.py", 1]
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
pydict["Topic modeling (via Mallet)"] = ["topic_modeling_mallet_main.py", 1]
pydict["utf-8 compliance"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["Style analysis"] = ["style_analysis_main.py", 1]
pydict["Narrative analysis"] = ["narrative_analysis_main.py", 1]
pydict["WHAT\'S IN YOUR CORPUS? A SWEEPING VIEW"] = ["whats_in_your_corpus_main.py", 1]
pydict["Corpus statistics (Sentences, words, lines)"] = ["statistics_NLP_main.py", 1]
pydict["Word clouds"] = ["wordclouds_main.py", 1]
pydict["WordNet"] = ["WordNet_main.py", 1]
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

def setup_IO():
    # the call to the IO_setup_main.py GUI is based on the standard I/O configuration (0, 2, 1, 0, 0, 1):
    #   filename, inputDir, outputDir
    call("python IO_setup_main.py --config_option \"0, 2, 1, 0, 0, 1\" --config_filename \"default-config.txt\"",
         shell=True)
    IO_options = config_util.get_IO_options(config_filename,config_input_output_options)
    GUI_util.display_IO_setup(window, IO_setup_display_brief, config_filename, IO_options,ScriptName)

    GUI_util.activateRunButton(False,ScriptName)
    setup_IO_checkbox()

def setup_IO_checkbox():
    state = str(GUI_util.run_button['state'])
    if state != 'disabled':
        setup_IO_OK_checkbox_var.set(1)
    else:
        setup_IO_OK_checkbox_var.set(0)

IO_setup_button = tk.Button(window, text='Setup default I/O options: INPUT corpus file(s) and OUTPUT files directory', font=("Courier", 12, "bold"), command=lambda: setup_IO())
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               IO_setup_button,True)

setup_IO_OK_checkbox = tk.Checkbutton(window, state='disabled',
                                      variable=setup_IO_OK_checkbox_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 800, y_multiplier_integer,
                                               setup_IO_OK_checkbox)

IO_setup_var.trace('w',setup_IO)

def setup_software_warning():
    mb.showwarning('Software option', 'Please, using the dropdown menu, select the external software that you would like to install.')
    return

software_setup_button = tk.Button(window, text='Setup external software', font=("Courier", 12, "bold"), command=lambda: setup_software_warning())
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               software_setup_button,True)

software_setup_menu = tk.OptionMenu(window, software_setup_var,
                                   'Stanford CoreNLP',
                                   'WordNet',
                                   'Mallet',
                                   'SENNA')

software_setup_menu.configure(width=70)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               software_setup_menu,True)

setup_software_checkbox = tk.Checkbutton(window, state='disabled',
                                         variable=setup_software_OK_checkbox_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 800, y_multiplier_integer,
                                               setup_software_checkbox)


# check for external software installation (Stanford CoreNLP, WordNet, Mallet, SENNA)
def setup_software(*args):
    silent = False
    only_check_missing = False
    # if software_setup_var.get()!='':
    #     silent = False
    #     only_check_missing = False
    # else:
    #     silent = True
    #     only_check_missing = True
    output, missing_external_software = IO_libraries_util.get_external_software_dir('NLP_menu', software_setup_var.get(),silent,only_check_missing)
    # must be recomputed because the return variable missing_external_software will STILL contain the missing software
    # that could have been updated
    setup_software_checkbox()

def setup_software_checkbox():
    missing_external_software=IO_libraries_util.get_missing_software_list('')
    if len(missing_external_software)>0:
        setup_software_OK_checkbox_var.set(0)
    else:
        setup_software_OK_checkbox_var.set(1)

software_setup_var.trace('w',setup_software)

general_tools_lb = tk.Label(window, text='General tools', foreground="red",font=("Courier", 12, "bold"))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               general_tools_lb)

# setup GUI widgets
data_file_handling_tools_var.set('')
file_handling_lb = tk.Label(window, text='Data & Files Handling Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               file_handling_lb, True)

file_handling_menu = tk.OptionMenu(window, data_file_handling_tools_var,
                                   'Data manager (csv files via Pandas)',
                                   'File checker (file content)',
                                   'File checker (file content utf-8 encoding)',
                                   'File checker (file name)',
                                   'File classifier (dumb classifier via embedded date) (file name)',
                                   'File-type converter (csv, docx, pdf, rtf --> txt)',
                                   'File matcher (file name)',
                                   'File merger (file content)',
                                   'File splitter (file content)',
                                   'File manager (List, Rename, Copy, Move, Delete, Count)',
                                   'SQL database (via SQLite)'
                                   )

file_handling_menu.configure(width=70)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               file_handling_menu)

pre_processing_tools_var.set('')
pre_processing_lb = tk.Label(window, text='Pre-Processing Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               pre_processing_lb, True)
pre_processing_menu = tk.OptionMenu(window, pre_processing_tools_var,
                                    'File checker (file content)',
                                    'File checker (file content utf-8 encoding)',
                                    'File checker (file name)',
                                    'File cleaner (Change to ASCII non-ASCII apostrophes & quotes and % to percent)',
                                    'File cleaner (Find & Replace string)',
                                    'File cleaner (Remove blank lines from txt file(s))',
                                    'File finder (file name)',
                                    'File finder (file content for words/collocations)',
                                    'File-type converter (csv, docx, pdf, rtf --> txt)',
                                    'File merger (file content)',
                                    'File splitter (file content)',
                                    'Annotator - date (NER normalized date, via CoreNLP)',
                                    'Annotator - gender (male & female names; via CoreNLP and dictionaries)',
                                    'Annotator - quote (via CoreNLP)',
                                    'Co-Reference PRONOMINAL resolution (via Stanford CoreNLP)',
                                    'Find non-related documents',
                                    'Language detection',
                                    'Newspaper article/Document titles',
                                    'Similarities between documents (via Java Lucene)',
                                    'Similarities between documents (via Python difflib)',
                                    'Similarities between words (Levenshtein distance)',
                                    'Spelling checkers',
                                    'Spelling checker cleaner (Find & Replace string)')
                                    # 'Spelling checker/Unusual words (via NLTK)',
                                    # 'Spelling checker (via autocorrect)',
                                    # 'Spelling checker (via pyspellchecker)',
                                    # 'Spelling checker (via textblob)')

pre_processing_menu.configure(width=70)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               pre_processing_menu)

statistical_tools_var.set('')
statistical_tools_lb = tk.Label(window, text='Statistical Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               statistical_tools_lb, True)
statistical_menu = tk.OptionMenu(window, statistical_tools_var,
                                 'Statistics (csv & txt files)')
statistical_menu.configure(width=70)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               statistical_menu)

visualization_tools_var.set('')
visualization_lb = tk.Label(window, text='Visualization Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               visualization_lb, True)
visualization_menu = tk.OptionMenu(window, visualization_tools_var,
                                   'Excel charts',
                                   'Geographic maps: Geocoding & maps',
                                   'Geographic maps: Google Earth Pro',
                                   'Geographic distances between locations',
                                   'Annotator - dictionary, gender, DBpedia, YAGO',
                                   'Network graphs (Gephi)',
                                   'Sentence visualization: Dependency tree viewer (png graphs)',
                                   'Word clouds')
visualization_menu.configure(width=70)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               visualization_menu)

# (startX, startY, endX, endY) where endX is the width of window
# https://stackoverflow.com/questions/40390746/how-to-correctly-use-tkinter-create-line-coordinates
# window.create_line(0,y_multiplier_integer,1000,y_multiplier_integer)

# leave a blank line to separate the linguistic analyses

linguistic_tools_lb = tk.Label(window, text='Tools of linguistic analysis', foreground="red",font=("Courier", 12, "bold"))
# text.configure(font=("Times New Roman", 12, "bold"))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               linguistic_tools_lb)

corpus_tools_var.set('')
corpus_tools_lb = tk.Label(window, text='CORPUS Analysis Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               corpus_tools_lb, True)
# tools that apply exclusively to a corpus
corpus_tools_menu = tk.OptionMenu(window, corpus_tools_var,
                                  'WHAT\'S IN YOUR CORPUS? A SWEEPING VIEW',
                                  'Corpus statistics (Sentences, words, lines)',
                                  'Co-Occurrences viewer',
                                  'N-grams viewer',
                                  'Shape of stories',
                                  'Similarities between documents (via Python difflib)',
                                  'Similarities between documents (via Java Lucene)',
                                  'Topic modeling (via Gensim)',
                                  'Topic modeling (via Mallet)',
                                  'Word2Vec (via Gensim)')

corpus_tools_menu.configure(width=70)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               corpus_tools_menu)

# 'KWIC (Key Word In Context)')

corpus_document_tools_var.set('')
corpus_document_tools_lb = tk.Label(window, text='CORPUS/DOCUMENT Analysis Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               corpus_document_tools_lb, True)
# tools that can be applied to either corpus or single document
corpus_document_tools_menu = tk.OptionMenu(window, corpus_document_tools_var,
                                           'Stanford CoreNLP',
                                           'CoNLL table analyzer - Search the CoNLL table',
                                           'CoNLL table analyzer - Clause, noun, verb, function words frequencies',
                                           'Annotator - date (NER normalized date, via CoreNLP)',
                                           'Annotator - gender (male & female names; via CoreNLP and dictionaries)',
                                           'Annotator - quote (via CoreNLP)',
                                           'Annotator - dictionary, gender, DBpedia, YAGO',
                                           'Annotator - hedge/uncertainty',
                                           'Annotator extractor',
                                           'Narrative analysis',
                                           'Style analysis',
                                           'Sentiment analysis',
                                           'Gender guesser',
                                           'Geographic maps: From texts to maps',
                                           'Geographic maps: Google Earth Pro',
                                           'NER (Named Entity Recognition) extractor',
                                           'N-grams (word & character)',
                                           'Nominalization',
                                           'Search text file(s) for n-grams & co-occurrences',
                                           'Search text file(s) for words/collocations',
                                           'Sentence complexity',
                                           'Sentence/text readability (via textstat)',
                                           'Similarities between words (Levenshtein distance)',
                                           'Spelling checkers',
                                           'Spelling checker cleaner (Find & Replace string)',
                                           # 'Spelling checker/Unusual words (via NLTK)',
                                           # 'Spelling checker (via autocorrect)',
                                           # 'Spelling checker (via pyspellchecker)',
                                           # 'Spelling checker (via textblob)',
                                           'Semantic analysis (via TensorFlow)',
                                           'SRL Semantic Role Labeling',
                                           'SVO extractor & visualization',
                                           'Word clouds',
                                           'WordNet')

corpus_document_tools_menu.configure(width=70)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               corpus_document_tools_menu)

sentence_tools_var.set('')
sentence_tools_lb = tk.Label(window, text='SENTENCE Analysis Tools')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               sentence_tools_lb, True)
sentence_tools_menu = tk.OptionMenu(window, sentence_tools_var,
                                    'Sentence analysis (An overall GUI)')

sentence_tools_menu.configure(width=70)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               sentence_tools_menu)


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

# further_options.set('')
# further_options_lb = tk.Label(window, text='Further Options (Not Supported)')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,further_options_lb,True)
# further_options_menu = tk.OptionMenu(window,further_options,'AntConc',
# 																'Apache OpenNLP',
# 																'Automap',
# 																'CleaNLP',
# 																'ConText',
# 																'GATE',
# 																'Knime',
# 																'LIWC',
# 																'NLTK',
# 																'SEANCE',
# 																'Tacit',
# 																'Voyant')
# further_options_menu.configure(width=70)
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,further_options_menu)

TIPS_lookup = {'NLP Suite: Package description': 'TIPS_NLP_NLP Suite Package description.pdf',
               'Things to do with words: NLP approach': 'TIPS_NLP_Things to do with words NLP approach.pdf',
               'Setup Input/Output configuration for your corpus': 'TIPS_NLP_Setup INPUT-OUTPUT options.pdf',
               'Setup external software (e.g., Mallet)': 'TIPS_NLP_Setup external software.pdf',
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
TIPS_options = 'NLP Suite: Package description', 'Things to do with words: NLP approach', 'Setup Input/Output configuration for your corpus', 'Setup external software (e.g., Mallet)', 'NLP Suite: General tools', 'NLP Suite: Tools of linguistic analysis', 'NLP basic language', 'Things to do with words: Overall view', 'Things to do with words: Content analysis', 'Things to do with words: Frame analysis', 'Things to do with words: Narrative analysis', 'Things to do with words: Rhetoric (Arguments)', 'Things to do with words: Rhetoric (Tropes & Figures)', 'Style analysis', 'Text encoding (utf-8)','csv files - Problems & solutions'


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
                                  "Please, click on the button to the right to open the GUI that will allow you to setup default I/O options:\n   INPUT file and or directory of files (your corpus)and\n   OUTPUT directory where all files (csv, txt, html, kml, jpg) produced by the NLP-Suite tools will be saved.\n\nThese default I/O options will be used for all GUIs.\n\nThe checkbox at the end of the line is set to OK if all INPUT/OUTPUT options have been successfully selected and saved in the default-config.txt file under the subdirecory config.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 2, "Help",
                                  "The NLP-Suite relies for some of its operations on external software that needs to be downloaded and installed (Stanford CoreNLP, WordNet, Mallet, SENNA). When using any of these software, the NLP-Suite needs to know where they have been installed on your computer (e.g., C:\Program Files (x86)\WordNet).\n\nPlease, using the dropdown menu, select the software option that you want to link to its installation directory. YOUR SELECTION WILL BE SAVED IN THE software_config.csv FILE UNDER THE SUBDIRECTORY config.\n\nThe checkbox at the end of the line is set to OK if all external software packages have been successfully installed.")
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
readMe_message = "This Python 3 script is the front end for a wide collection of Java and Python Natural Language Processing (NLP) tools.\n\nThe set of tools are divided into GENERAL TOOLS (data and file handling, pre-processing, statistical, visualization) and LINGUISTIC ANALYSIS TOOLS.\n\nLINGUISTIC ANALYSIS TOOLS are divided into tools that expect in input CORPUS DATA (i.e., multiple documents stored in a directory), CORPUS and/or SINGLE DOCUMENT, and SENTENCE.\n\nWhile some linguistic tools are specific for one of these three categories (e.g., topic modeling cannot be performed on a single document), MANY TOOLS OVERLAP. As a result, you may find the same tool under BOTH corpus and corpus/document. SENTENCE TOOLS still require either a corpus or a single document in input; but they also provide in output sentence-level information for more in-grained linguistic analyses.\n\nAll tools are open source freeware software released under the GNU LGPLv2.1 license (http://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html).\n\nYou can cite the NLP Suite as:\n\nR. Franzosi. 2020. NLP Suite: A  set of tools of Natural Language Processing (NLP) & Data Visualization."
readMe_command = lambda: GUI_IO_util.readme_button(window, GUI_IO_util.get_help_button_x_coordinate(),
                                                   GUI_IO_util.get_basic_y_coordinate(), "Help", readMe_message)
GUI_util.GUI_bottom(config_input_output_options, y_multiplier_integer, readMe_command, TIPS_lookup, TIPS_options, IO_setup_display_brief, ScriptName)

routine_options = reminders_util.getReminders_list('NLP')

reminders_util.checkReminder('NLP',
                             reminders_util.title_options_NLP_Suite_welcome,
                             reminders_util.message_NLP_Suite_welcome,
                             True)

reminders_util.checkReminder('NLP',
                             reminders_util.title_options_NLP_Suite_architecture,
                             reminders_util.message_NLP_Suite_architecture,
                             True)

routine_options = reminders_util.getReminders_list('NLP')

# this problem seems to have been fixed by tkinter
# if platform == "darwin":
#     reminders_util.checkReminder(config_filename,
#                                  reminders_util.title_options_Mac_tkinter_bug,
#                                  reminders_util.message_Mac_tkinter_bug,
#                                  True)

# check for external software installation (Stanford CoreNLP, WordNet, Mallet, SENNA)
# IO_libraries_util.get_external_software_dir('NLP_menu','')

# check for missing I/O configuration options
setup_IO_checkbox()
# check for missing external software
setup_software()

GUI_util.window.mainloop()

