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
import BERT_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir,openOutputFiles, createCharts, chartPackage,
        remove_stopwords_var, lemmatize_var,
        BERT_var, Gensim_var,
        sg_menu_var, vector_size_var, window_var, min_count_var,
        vis_menu_var, dim_menu_var, keywords_var):

    filesToOpen = []

    ## if statements for any requirements

    if BERT_var:
        BERT_output = BERT_util.word_embeddings_BERT(window, inputFilename, inputDir, outputDir, openOutputFiles, createCharts,
                                                   chartPackage)
        filesToOpen.append(BERT_output)

    if Gensim_var:
        if 'Clustering' in vis_menu_var and keywords_var=='':
            mb.showwarning(title='Missing keywords',message='The algorithm requires a comma-separated list of keywords taken from the corpus to be used as a Word2Vec run.\n\nPlease, enter the keywords and try again.')
            return
        filesToOpen = word2vec_util.run_Gensim_word2vec(inputFilename, inputDir, outputDir,openOutputFiles, createCharts, chartPackage,
                                 remove_stopwords_var, lemmatize_var, sg_menu_var, vector_size_var, window_var, min_count_var, vis_menu_var, dim_menu_var, keywords_var)

    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_chart_output_checkbox.get(),
                                GUI_util.charts_dropdown_field.get(),
                                remove_stopwords_var.get(),
                                lemmatize_var.get(),
                                BERT_var.get(),
                                Gensim_var.get(),
                                sg_menu_var.get(),
                                vector_size_var.get(),
                                window_var.get(),
                                min_count_var.get(),
                                vis_menu_var.get(),
                                dim_menu_var.get(),
                                keywords_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=640, # height at brief display
                             GUI_height_full=720, # height at full display
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

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

remove_stopwords_var=tk.IntVar()
lemmatize_var=tk.IntVar()

BERT_var=tk.IntVar()
Gensim_var=tk.IntVar()

sg_menu_var=tk.StringVar()
vector_size_var=tk.IntVar()
window_var=tk.IntVar()
min_count_var=tk.IntVar()
vis_menu_var=tk.StringVar()
dim_menu_var=tk.StringVar()
keywords_var=tk.StringVar()

## option for stopwords
remove_stopwords_var.set(1)
remove_stopwords_checkbox = tk.Checkbutton(window, text='Remove stopwords', variable=remove_stopwords_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,remove_stopwords_checkbox)

## option for Lemmatization
lemmatize_var.set(1)
lemmatize_checkbox = tk.Checkbutton(window, text='Lemmatize', variable=lemmatize_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,lemmatize_checkbox)

## option for BERT
BERT_var.set(0)
BERT_checkbox = tk.Checkbutton(window, text='Word2Vec (via BERT)', variable=BERT_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,BERT_checkbox)

## option for Gensim
Gensim_var.set(0)
Gensim_checkbox = tk.Checkbutton(window, text='Word2Vec (via Gensim)', variable=Gensim_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,Gensim_checkbox)

## option for model architecture
sg_lb = tk.Label(window,text='Select the training model architecture')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,sg_lb,True)
sg_menu_var.set('Skip-Gram')
sg_menu = tk.OptionMenu(window,sg_menu_var, 'Skip-Gram','CBOW')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate+50,y_multiplier_integer,sg_menu)
## option for vector size
vector_size_lb = tk.Label(window,text='Vector size')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,vector_size_lb,True)
vector_size_var.set(100)
vector_size_entry = tk.Entry(window,width=5,textvariable=vector_size_var)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+120,y_multiplier_integer,vector_size_entry)
## option for window size
window_lb = tk.Label(window,text='Window size')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,window_lb,True)
window_var.set(5)
window_entry = tk.Entry(window,width=5,textvariable=window_var)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+120,y_multiplier_integer,window_entry)
## option for minimum count
min_count_lb = tk.Label(window,text='Minimum count')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,min_count_lb,True)
min_count_var.set(5)
min_count_entry = tk.Entry(window,width=5,textvariable=min_count_var)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+120,y_multiplier_integer,min_count_entry)
## option for visualization method
vis_var_lb = tk.Label(window,text='Select the visualization method')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,vis_var_lb,True)
vis_menu_var.set('Plot all word vectors')
vis_menu = tk.OptionMenu(window,vis_menu_var, 'Plot all word vectors', 'Clustering of word vectors')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate,y_multiplier_integer,vis_menu, True)
#### 2D or 3D plot
dim_menu_var.set('2D')
dim_menu = tk.OptionMenu(window,dim_menu_var, '2D', '3D')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate+260,y_multiplier_integer,dim_menu)
#### entry for clustering keywords
keywords_var.set('')
keywords_lb = tk.Label(window, text='Keywords')
cluster_var_entry = tk.Entry(window,width=10,textvariable=keywords_var)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+50,y_multiplier_integer,keywords_lb,True)
keywords_entry = tk.Entry(window, textvariable=keywords_var)
keywords_entry.configure(state='disabled',width=100)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+160,y_multiplier_integer,keywords_entry)

def activate_keywords_var(*args):
    if vis_menu_var.get() == 'Clustering of word vectors':
        keywords_entry.config(state='normal')
    else:
        keywords_entry.config(state='disabled')

vis_menu_var.trace('w', activate_keywords_var)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {"Lemmas & stopwords":"TIPS_NLP_NLP Basic Language.pdf",
               "Word2Vec with Gensim":"TIPS_NLP_Word2Vec.pdf",
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf'}

TIPS_options = 'Lemmas & stopwords', 'Word2Vec with Gensim', 'csv files - Problems & solutions', 'Statistical measures'

def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:

        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_csv_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_outputDirectory)

    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "Please, tick the checkbox to exclude stopwords from the analyzes (e.g, determiners, personal and possessive pronouns, auxiliaries).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "Please, tick the checkbox to lemmatize nouns (using the singular version instead of plural, e.g., ox iinstead of oxen, child instead of children) and verbs (using the infinitive form instead of any verb forms, e.g., go gor going, went, goes).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "Please, tick the checkbox to run Word2Vec word embeddings via BERT.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "Please, tick the checkbox to run Word2Vec word embeddings via Gensim.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "Please, using the dropdown menu, select the preferred model architecture for training Word2Vec: Skip-Gram and CBOW (Continuous Bag of Words).\n\nWhich model is better?\n\nAccording to the original paper by Mikolov et al. (2013) Skip-Gram works well with small datasets, and can better represent less frequent words. However, CBOW is found to train faster than Skip-Gram, and can better represent more frequent words.\n\nMikolov, Tomas, Kai Chen, Greg Corrado, and Jeffrey Dean. 2013. 'Efficient Estimation of Word Representations in Vector Space' arXiv:1301.3781.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "'Vector size' refers to the dimensionality of the word vectors. If you have a large corpus (> billions of tokens), you can go up to 100-300 dimensions. Generally word vectors with more dimensions give better results.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "'Window size' refers to the maximum distance between the current and predicted word within a sentence. In other words, how many words come before and after your given word.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "'Minimum count' refers to the minimum frequency threshold. The words with total frequency lower than this will be ignored.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help", GUI_IO_util.msg_openOutputFiles)
                                  # "NLP Suite Help", "Please, using the dropdown menu, select the architecture to be used in training Word2Vec: CBOW (Continuous Bag-of-Words) and Skip-gram. Both approaches are based on neural networks. Generally, CBOW is much faster and with slightly better accuracy for larger corpora. Skip-gram is better for smaller corpora.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "Enter comma-separated keywords you want to focus on for semantic similarity. The words MUST be in the file(s) you are analyzing.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help", GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="This Python 3 script analyzes a set of documents for Word2Vec with Gensim."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
