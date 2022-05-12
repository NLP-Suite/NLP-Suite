# command line tool for implementing gensim
# by Jack Hester
# code partly based on "https://www.machinelearningplus.com/nlp/topic-modeling-gensim-python/"
# OFFICIAL DOCUMENTATION https://pyldavis.readthedocs.io/en/latest/modules/API.html

# last updated 11/3/2019
# TODO: make GUI and save topics to a single text file separate from html
# WARNING: you may need to comment out matplotlib.use(...) especially if on windows

# TODO
# https://radimrehurek.com/gensim/models/ldamodel.html
# get_document_topics(bow, minimum_probability=None, minimum_phi_value=None, per_word_topics=False)
# Get the topic distribution for the given document.

# Parameters
# bow (corpus : list of (int, float)) – The document in BOW format.
# minimum_probability (float) – Topics with an assigned probability lower than this threshold will be discarded.
# minimum_phi_value (float) –
# If per_word_topics is True, this represents a lower bound on the term probabilities that are included.
# If set to None, a value of 1e-8 is used to prevent 0s.
# per_word_topics (bool) – If True, this function will also return two extra lists as explained in the “Returns” section.
# Returns
# list of (int, float) – Topic distribution for the whole document. Each element in the list is a pair of a topic’s id, and the probability that was assigned to it.
# list of (int, list of (int, float), optional – Most probable topics per word. Each element in the list is a pair of a word’s id, and a list of topics sorted by their relevance to this word. Only returned if per_word_topics was set to True.
# list of (int, list of float), optional – Phi relevance values, multiplied by the feature length, for each word-topic combination. Each element in the list is a pair of a word’s id and a list of the phi values between this word and each topic. Only returned if per_word_topics was set to True.

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"topic_modeling_gensim_main.py",['nltk','os','tkinter','multiprocessing','pandas','gensim','spacy','pyLDAvis','matplotlib','logging','IPython'])==False:
    sys.exit(0)

import os
import tkinter as tk
# necessary to avoid opening the GUI repeatedly
from multiprocessing import current_process

import GUI_IO_util
import topic_modeling_gensim_util
import IO_internet_util
import reminders_util

# RUN section ______________________________________________________________________________________________________________________________________________________

"""
# get CLAs of input dir and output file name
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputDir", help="Directs the input to your text directory")
parser.add_argument("-o", "--outputFilename", help="Directs the output to a file name and path of your choice, MUST end in .html")
args = parser.parse_args()
"""


def run(inputDir, outputDir, openOutputFiles,createExcelCharts, num_topics, remove_stopwords_var, lemmatize_var, nounsOnly_var, Mallet_var):
    if not IO_internet_util.check_internet_availability_warning('Gensim Topic Modeling'):
        return

    if num_topics==20:
        reminders_util.checkReminder(config_filename, reminders_util.title_options_topic_modelling_number_of_topics,
                                     reminders_util.message_topic_modelling_number_of_topics, True)

    topic_modeling_gensim_util.run_Gensim(GUI_util.window, inputDir, outputDir, num_topics,
                                          remove_stopwords_var, lemmatize_var, nounsOnly_var, Mallet_var, openOutputFiles,createExcelCharts)

run_script_command = lambda: run(GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.create_Excel_chart_output_checkbox.get(),
                                 num_topics_var.get(),
                                 remove_stopwords_var.get(),
                                 lemmatize_var.get(),
                                 nounsOnly_var.get(),
                                 Mallet_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=140, # height at brief display
                             GUI_height_full=480, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=1, # to be added for full display
                             increment=1)  # to be added for full display

GUI_label = 'Graphical User Interface (GUI) for Topic Modeling with Gensim'
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

# necessary to avoid opening the GUI repeatedly
if current_process().name == 'MainProcess':
    GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)
    window = GUI_util.window
    # config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
    # config_filename = GUI_util.config_filename
    inputFilename = GUI_util.inputFilename

    GUI_util.GUI_top(config_input_output_numeric_options, config_filename,IO_setup_display_brief)


    # change the value of the readMe_message
    readMe_message = "This Python 3 script analyzes a set of documents for topic modeling with Gensim.\n\nIn INPUT the script expects a set of text files stored in a directory.\n\nIn OUTPUT, the script creates an html file with graphical displays of topic information.\n\nGensim topc modelling requires internet connection to run."
    readMe_command = lambda: GUI_IO_util.display_button_info("NLP Suite Help", readMe_message)

    GUI_util.window.mainloop()
