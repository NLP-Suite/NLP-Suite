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

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"topic_modeling_gensim_main.py",['nltk','os','tkinter','multiprocessing','pandas','gensim','spacy','pyLDAvis','matplotlib','logging','IPython'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
# necessary to avoid opening the GUI repeatedly
from multiprocessing import current_process

import GUI_IO_util
import topic_modeling_mallet_util
import topic_modeling_gensim_util
import IO_internet_util
import reminders_util
import IO_files_util

# RUN section ______________________________________________________________________________________________________________________________________________________

"""
# get CLAs of input dir and output file name
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputDir", help="Directs the input to your text directory")
parser.add_argument("-o", "--outputFilename", help="Directs the output to a file name and path of your choice, MUST end in .html")
args = parser.parse_args()
"""


def run(inputDir, outputDir, openOutputFiles,createCharts,chartPackage, num_topics,
        MALLET_var,
        optimize_intervals_var,
        Gensim_var,
        remove_stopwords_var, lemmatize_var, nounsOnly_var, Gensim_MALLET_var):

    filesToOpen = []

    if MALLET_var:
        label='MALLET'
    else:
        label='Gensim'

    if not IO_internet_util.check_internet_availability_warning(label + ' Topic Modeling'):
        return

    if num_topics==20:
        reminders_util.checkReminder(config_filename, reminders_util.title_options_topic_modelling_number_of_topics,
                                     reminders_util.message_topic_modelling_number_of_topics, True)

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory('', inputDir, outputDir, label='TM-'+label,
                                                       silent=True)
    if outputDir == '':
        return

    if MALLET_var:
        filesToOpen = topic_modeling_mallet_util.run_MALLET(inputDir, outputDir, openOutputFiles, createCharts, chartPackage,
                                                     optimize_intervals_var, num_topics)
    if Gensim_var:
        filesToOpen = topic_modeling_gensim_util.run_Gensim(GUI_util.window, inputDir, outputDir, num_topics,
                                          remove_stopwords_var, lemmatize_var, nounsOnly_var, Gensim_MALLET_var, openOutputFiles,createCharts, chartPackage)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

run_script_command = lambda: run(GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.create_chart_output_checkbox.get(),
                                 GUI_util.charts_package_options_widget.get(),
                                 num_topics_var.get(),
                                 MALLET_var.get(),
                                 optimize_intervals_var.get(),
                                 Gensim_var.get(),
                                 remove_stopwords_var.get(),
                                 lemmatize_var.get(),
                                 nounsOnly_var.get(),
                                 Gensim_MALLET_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=560, # height at brief display
                             GUI_height_full=600, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=1, # to be added for full display
                             increment=1)  # to be added for full display

GUI_label = 'Graphical User Interface (GUI) for Topic Modeling with MALLET and Gensim'
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

    GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

    num_topics_var = tk.IntVar()
    Gensim_var = tk.IntVar()
    MALLET_var = tk.IntVar()
    remove_stopwords_var = tk.IntVar()
    lemmatize_var = tk.IntVar()
    nounsOnly_var = tk.IntVar()
    Gensim_MALLET_var = tk.IntVar()
    optimize_intervals_var = tk.IntVar()

    num_topics_lb = tk.Label(window, text='Number of topics ')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   num_topics_lb, True)

    num_topics_var.set(20)
    num_topics_entry = tk.Entry(window, width=5, textvariable=num_topics_var)
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_coordinate + 100, y_multiplier_integer,
                                                   num_topics_entry,
                                                   False, False, True, False, 90,
                                                   GUI_IO_util.labels_x_coordinate,
                                                   "Enter the number of topics to be used. Try different number of topics for better results (e.g., 70, 5).")

    MALLET_var.set(0)
    MALLET_checkbox = tk.Checkbutton(window, text='Topic modeling (via MALLET)', variable=MALLET_var,
                                               onvalue=1, offvalue=0, command=lambda: activate_options())
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   MALLET_checkbox,
                                                   False, False, True, False, 90,
                                                   GUI_IO_util.labels_x_coordinate,
                                                   "Tick/untick the checkbox to run the MALLET topic modeling algorithm")

    optimize_intervals_var.set(1)
    optimize_intervals_checkbox = tk.Checkbutton(window, text='Optimize topic intervals',
                                                 variable=optimize_intervals_var,
                                                 onvalue=1, offvalue=0)
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                                   optimize_intervals_checkbox)

    Gensim_var.set(0)
    Gensim_checkbox = tk.Checkbutton(window, text='Topic modeling (via Gensim)', variable=Gensim_var,
                                               onvalue=1, offvalue=0, command=lambda: activate_options())
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   Gensim_checkbox,
                                                   False, False, True, False, 90,
                                                   GUI_IO_util.labels_x_coordinate,
                                                   "Tick/untick the checkbox to run the Gensim topic modeling algorithm")

    remove_stopwords_var.set(1)
    remove_stopwords_checkbox = tk.Checkbutton(window, text='Remove stopwords', variable=remove_stopwords_var,
                                               onvalue=1, offvalue=0)
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                                   remove_stopwords_checkbox)

    lemmatize_var.set(1)
    lemmatize_checkbox = tk.Checkbutton(window, text='Lemmatize words (Nouns, verbs, adverbs, adjectives)', variable=lemmatize_var, onvalue=1, offvalue=0)
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                                   lemmatize_checkbox)

    nounsOnly_var.set(0)
    nounsOnly_checkbox = tk.Checkbutton(window, text='Use nouns only (lemmatized)', variable=nounsOnly_var, onvalue=1, offvalue=0)
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+20, y_multiplier_integer,
                                                   nounsOnly_checkbox)

    Gensim_MALLET_var.set(0)
    Gensim_MALLET_checkbox = tk.Checkbutton(window, text='Run MALLET (Topic coherence values and plot visualization)', variable=Gensim_MALLET_var, onvalue=1, offvalue=0)
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                                   Gensim_MALLET_checkbox)

    def Mallet_reminder(*args):
        if Gensim_MALLET_var.get():
            routine_options = reminders_util.getReminders_list(config_filename)
            reminders_util.checkReminder(config_filename,
                                         reminders_util.title_options_gensim_release,
                                         reminders_util.message_gensim_release,
                                         True)
            routine_options = reminders_util.getReminders_list(config_filename)
    Gensim_MALLET_var.trace('w',Mallet_reminder)

    def activate_options():
        if MALLET_var.get():
            Gensim_checkbox.configure(state='disabled')
            remove_stopwords_checkbox.configure(state='disabled')
            lemmatize_checkbox.configure(state='disabled')
            nounsOnly_checkbox.configure(state='disabled')
            Gensim_MALLET_checkbox.configure(state='disabled')
        else:
            Gensim_checkbox.configure(state='normal')
            remove_stopwords_checkbox.configure(state='normal')
            lemmatize_checkbox.configure(state='normal')
            nounsOnly_checkbox.configure(state='normal')
            Gensim_MALLET_checkbox.configure(state='normal')
        if Gensim_var.get():
            MALLET_checkbox.configure(state='disabled')
            optimize_intervals_checkbox.configure(state='disabled')
        else:
            MALLET_checkbox.configure(state='normal')
            optimize_intervals_checkbox.configure(state='normal')

    videos_lookup = {'No videos available': ''}
    videos_options = 'No videos available'

    TIPS_lookup = {"Topic modeling": "TIPS_NLP_Topic modeling.pdf",
                   "Topic modeling in Gensim": "TIPS_NLP_Topic modeling Gensim.pdf",
                   "Topic modeling in Mallet": "TIPS_NLP_Topic modeling Mallet.pdf",
                   'Topic modeling and corpus size': 'TIPS_NLP_Topic modeling and corpus size.pdf',
                   'Lemmas & stopwords':'TIPS_NLP_NLP Basic Language.pdf',
                   'csv files - Problems & solutions': 'TIPS_NLP_csv files - Problems & solutions.pdf',
                   'Statistical measures': 'TIPS_NLP_Statistical measures.pdf'}
    TIPS_options = 'Topic modeling', 'Topic modeling in Gensim', 'Topic modeling in Mallet', 'Topic modeling and corpus size', 'Lemmas & stopwords', 'csv files - Problems & solutions', 'Statistical measures'


    # add all the lines to the end to every special GUI
    # change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
    # any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
    def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
        if not IO_setup_display_brief:
            y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_corpusData)
            y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                          GUI_IO_util.msg_outputDirectory)
        else:
            y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                          GUI_IO_util.msg_IO_setup)

        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, enter the number of topics to be used (recommended default = 20).\n\nVarying the number of topics may provide better results.")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, tick the checkbox if you wish to run MALLET LDA topic modeling.")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                             "NLP Suite Help",
                                                             "Please, tick the checkbox if you do NOT wish to optimize intervals.\n\n"
                                                             "Optimization, however, seems to lead to better reults "
                                                             "(https://programminghistorian.org/lessons/topic-modeling-and-mallet).")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, tick the checkbox if you wish to run Gensim LDA topic modeling.")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, tick the checkbox if you wish to run Gensim LDA topic modeling removing stopwords first.\n\nRemoving stopwords may provide better results.")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, tick the checkbox if you wish to run Gensim LDA topic modeling using lemmatized words. Nouns, verbs, adjectives, and advervbs will be lemmatized.\n\nLemmatizing words may provide better results.")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, tick the checkbox if you wish to run Gensim LDA topic modeling using lemmatized nouns only.\n\nFocusing on nouns only may provide better results.\n\nhttps://msaxton.github.io/topic-model-best-practices/compare_noun_and_regular.html\n\nMartin, Fiona and Mark Johnson. 2015. “More Efficient Topic Modelling Through a Noun Only Approach.” Proceedings of the Australasian Language Technology Association Workshop, pp. 111−115.")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, tick the checkbox if you wish to run the LDA Mallet topic modeling via Gensim.\n\nThe algorithm will compute\n   1. the coherence value of each topic and\n   2. a plot that provides a visual clue for the 'best' number of topics to be used.\n\nTHESE ALGORITHMS CAN BE VERY SLOW DEPENDING UPON THE NUMBER OF INPUT DOCUMENTS PROCESSED.")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_openOutputFiles)
        return y_multiplier_integer -1
    y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

    # change the value of the readMe_message
    readMe_message = "This Python 3 script analyzes a set of documents for topic modeling with Gensim.\n\nIn INPUT the script expects a set of text files stored in a directory.\n\nIn OUTPUT, the script creates an html file with graphical displays of topic information.\n\nGensim topc modelling requires internet connection to run."
    readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
    GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

    reminders_util.checkReminder(
        config_filename,
        reminders_util.title_options_English_language_Gensim,
        reminders_util.message_English_language_Gensim,
        True)

    state = str(GUI_util.run_button['state'])
    if state == 'disabled':
        # check to see if there is a GUI-specific config file and set it to the setup_IO_menu_var
        if os.path.isfile(os.path.join(GUI_IO_util.configPath, config_filename)):
            GUI_util.setup_IO_menu_var.set('GUI-specific I/O configuration')
            mb.showwarning(title='Warning',
                           message="Since a GUI-specific " + config_filename + " file is available, the I/O configuration has been automatically set to GUI-specific I/O configuration.")

    GUI_util.window.mainloop()
