import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"word2vec_main.py",['os','tkinter', 'gensim', 'spacy'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb

import GUI_IO_util
import IO_files_util
import word2vec_util
import reminders_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir,openOutputFiles, createExcelCharts,
        remove_stopwords_var, lemmatize_var, sg_menu_var, vector_size_var, window_var, min_count_var,
        vis_menu_var, keywords_var):

    ## if statements for any requirements

    if 'Clustering' in vis_menu_var and keywords_var=='':
        mb.showwarning(title='Missing keywords',message='The algorithm requires a list of comma-separated keywords taken from the corpus to be used as a Word2Vec run.\n\nPlease, enter the keywords and try again.')
        return
    filesToOpen = word2vec_util.run_Gensim_word2vec(inputFilename, inputDir, outputDir,openOutputFiles, createExcelCharts,
                             remove_stopwords_var, lemmatize_var, sg_menu_var, vector_size_var, window_var, min_count_var, vis_menu_var, keywords_var)

    reminders_util.checkReminder('*',
                                 reminders_util.title_options_Word2Vec,
                                 reminders_util.message_Word2Vec,
                                 True)

    title_options_Word2Vec = ['Word2Vec HTML visual']
    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_Excel_chart_output_checkbox.get(),
                                remove_stopwords_var.get(),
                                lemmatize_var.get(),
                                sg_menu_var.get(),
                                vector_size_var.get(),
                                window_var.get(),
                                min_count_var.get(),
                                vis_menu_var.get(),
                                keywords_var.get())

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

GUI_label='Graphical User Interface (GUI) for Word2Vec with Gensim'
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
config_input_output_numeric_options=[2,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window

# config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
# config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path
outputDir = GUI_util.output_dir_path

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)

remove_stopwords_var=tk.IntVar()
lemmatize_var=tk.IntVar()
sg_menu_var=tk.StringVar()
vector_size_var=tk.IntVar()
window_var=tk.IntVar()
min_count_var=tk.IntVar()
vis_menu_var=tk.StringVar()
keywords_var=tk.StringVar()

##
remove_stopwords_var.set(1)
remove_stopwords_checkbox = tk.Checkbutton(window, text='Remove stopwords', variable=remove_stopwords_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,remove_stopwords_checkbox)
##
lemmatize_var.set(1)
lemmatize_checkbox = tk.Checkbutton(window, text='Lemmatize', variable=lemmatize_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,lemmatize_checkbox)
##
sg_lb = tk.Label(window,text='Select the learning architecture')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,sg_lb,True)
sg_menu_var.set('Skip-Gram')
sg_menu = tk.OptionMenu(window,sg_menu_var, 'Skip-Gram','CBOW')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+30,y_multiplier_integer,sg_menu)
##
vector_size_lb = tk.Label(window,text='Vector size')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,vector_size_lb,True)
vector_size_var.set(100)
vector_size_entry = tk.Entry(window,width=5,textvariable=vector_size_var)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate()+100,y_multiplier_integer,vector_size_entry)
##
window_lb = tk.Label(window,text='Window size')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,window_lb,True)
window_var.set(5)
window_entry = tk.Entry(window,width=5,textvariable=window_var)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate()+100,y_multiplier_integer,window_entry)
##
min_count_lb = tk.Label(window,text='Minimum count')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,min_count_lb,True)
min_count_var.set(5)
min_count_entry = tk.Entry(window,width=5,textvariable=min_count_var)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate()+100,y_multiplier_integer,min_count_entry)
##
vis_var_lb = tk.Label(window,text='Select the visualization method')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,vis_var_lb,True)
vis_menu_var.set('Plot all word vectors')
vis_menu = tk.OptionMenu(window,vis_menu_var, 'Plot all word vectors', 'Clustering of word vectors')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+20,y_multiplier_integer,vis_menu)

keywords_var.set('')
keywords_lb = tk.Label(window, text='Keywords')
cluster_var_entry = tk.Entry(window,width=10,textvariable=keywords_var)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+30,y_multiplier_integer,keywords_lb,True)

keywords_entry = tk.Entry(window, textvariable=keywords_var)
keywords_entry.configure(state='disabled',width=100)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+140,y_multiplier_integer,keywords_entry)

def activate_keywords_var(*args):
    if vis_menu_var.get() == 'Clustering of word vectors':
        keywords_entry.config(state='normal')
    else:
        keywords_entry.config(state='disabled')

vis_menu_var.trace('w', activate_keywords_var)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {"Lemmas & stopwords":"TIPS_NLP_NLP Basic Language.pdf","Word2Vec with Gensim":"TIPS_NLP_Word2Vec.pdf"}
TIPS_options = 'Lemmas & stopwords', 'Word2Vec with Gensim'

def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    if not IO_setup_display_brief:

        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help", GUI_IO_util.msg_csv_txtFile)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step, "Help", GUI_IO_util.msg_corpusData)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 2, "Help", GUI_IO_util.msg_outputDirectory)

    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+1),"Help", "Please, tick the checkbox to exclude stopwords from the analyzes (e.g, determiners, personal and possessive pronouns, auxiliaries).")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+2),"Help", "Please, tick the checkbox to lemmatize nouns (using the singular version instead of plural, e.g., ox iinstead of oxen, child instead of children) and verbs (using the infinitive form instead of any verb forms, e.g., go gor going, went, goes).")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 3),"Help", "-")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 4), "Help", "Vector size refers to the dimensionality of the word vectors.\n\nIf you have a large corpus (> billions of tokens), you can go up to 100-300 dimensions.\n\nIn general, word vectors with more dimensions give better results.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 5), "Help", "Window size refers to the maximum distance between the current and predicted word within a sentence, in other words, how many words come before and after your given word.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 6), "Help", "Minimum count refers to the minimum frequency threshold.\n\nThe words with total frequency lower than the selected value will be ignored.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 7), "Help","Using the dropdown menu, select the option you want to use in running WordNet.\n\nSelect \'Plot all word vectors\' if you want to use ALL the words in your input file(s).\n\nSelect \'Clustering of word vectors\' if you want to focus on selected keywords. THE KEYWORDS MUST BE CONTAINED IN THE INPUT FILE(S).\n\nA good analysis strategy is to run Word2Vec for all words first, then re-run the algorithm on a special subset of keywords.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 8),
                                  "Help", "Enter comma-separated keywords you want to focus on for semantic similarity. The words MUST be in the file(s) you are analyzing.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment + 9),"Help",GUI_IO_util.msg_openOutputFiles)

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="This Python 3 script analyzes file(s) with Gensim Word2Vec .\n\nIn INPUT the algorith can take a single txt file or a set of files in a directory.\n\nIn OUTPUT the algorithm produces two types of files:\n   1. a csv file;\n   2. an HTML file that visualizes a T-SNE graph of semantic distances between words. YOU CAN ENLARGE A TYPICAL MESSY DISPLAY BY SELECTING WITH YOUR MOUSE AN AREA OF INTEREST OF THE GRAPH. Hit REFRESH to go back to the original display."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
