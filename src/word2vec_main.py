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

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir,openOutputFiles, createExcelCharts,
        remove_stopwords_var, lemmatize_var, vector_size_var, window_var, min_count_var):

    ## if statements for any requirements
    filesToOpen = []
    filesToOpen = word2vec_util.run_Gensim_word2vec(inputFilename, inputDir, outputDir,openOutputFiles, createExcelCharts,
                             remove_stopwords_var, lemmatize_var, vector_size_var, window_var, min_count_var)

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
                                vector_size_var.get(),
                                window_var.get(),
                                min_count_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_width=1100
GUI_height=520 # height of GUI with full I/O display

if IO_setup_display_brief:
    GUI_height = GUI_height - 80
    y_multiplier_integer = GUI_util.y_multiplier_integer  # IO BRIEF display
    increment=0 # used in the display of HELP messages
else: # full display
    # GUI CHANGES add following lines to every special GUI
    # +3 is the number of lines starting at 1 of IO widgets
    # y_multiplier_integer=GUI_util.y_multiplier_integer+2
    y_multiplier_integer = GUI_util.y_multiplier_integer + 2  # IO FULL display
    increment=2

GUI_size = str(GUI_width) + 'x' + str(GUI_height)

GUI_label='Graphical User Interface (GUI) for Word2Vec with Gensim'
config_filename='word2vec-gensim-config.txt'
# The 6 values of config_option refer to:
#   software directory
#   input file
# 1 for CoNLL file
# 2 for TXT file
# 3 for csv file
# 4 for any type of file
# 5 for txt or html
# 6 for txt or csv
config_option=[0,2,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

window=GUI_util.window

config_input_output_options = GUI_util.config_input_output_options
config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path
outputDir = GUI_util.output_dir_path

GUI_util.GUI_top(config_input_output_options,config_filename,IO_setup_display_brief)

remove_stopwords_var=tk.IntVar()
lemmatize_var=tk.IntVar()
vector_size_var=tk.IntVar()
window_var=tk.IntVar()
min_count_var=tk.IntVar()


##
remove_stopwords_var.set(1)
remove_stopwords_checkbox = tk.Checkbutton(window, text='Remove stopwords', variable=remove_stopwords_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,remove_stopwords_checkbox)
##
lemmatize_var.set(1)
lemmatize_checkbox = tk.Checkbutton(window, text='Lemmatize', variable=lemmatize_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,lemmatize_checkbox)

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
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 3), "Help", "It refers to the dimensionality of the word vectors. If you have a large corpus (> billions of tokens), you can go up to 100-300 dimensions. Generally word vectors with more dimensions give better results")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 4), "Help", "It refers to the maximum distance between the current and predicted word within a sentence. In other words, how many words come before and after your given word.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment + 5), "Help", "It refers to the minimum frequency threshold. The words with total frequency lower than this will be ignored.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+6),"Help",GUI_IO_util.msg_openOutputFiles)

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="This Python 3 script analyzes a set of documents for Word2Vec with Gensim."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options,IO_setup_display_brief)

GUI_util.window.mainloop()
