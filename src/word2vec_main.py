import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"word2vec_main.py",['os','tkinter', 'gensim', 'spacy'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb

import reminders_util
import GUI_IO_util
import IO_files_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir,openOutputFiles, createCharts, chartPackage,
        remove_stopwords_var, lemmatize_var,
        BERT_var, Gensim_var, compute_distances_var, top_words_var,
        sg_menu_var, vector_size_var, window_var, min_count_var,
        vis_menu_var, dim_menu_var, keywords_var):

    if not BERT_var and not Gensim_var:
        mb.showwarning(title='Warning',message='No option has been selected.\n\nPlease select the Word2Vec package you wish to use (BERT and/or Gensim) and try again.')
        return

    filesToOpen = []

    if not 'Do not' in vis_menu_var:
        result = mb.askyesno('Visualization via t-SNE',
                             'You have selected to run Word2Vec with the t-SNE visualization option. Depending upon the total number of words in your corpus, this option is computationally VERY demanding (it can take many hours on a standard laptop, particularly with BERT). Compressing an n-dimensional space into a a 2D or 3D graph can also be somewhat misleading (cosine similarities provide a better alternative).\n\nAre you sure you want to continue?')
        if not result:
            return

    # create a subdirectory of the output directory; should create a subdir with increasing number to avoid writing ver
    label=''
    if BERT_var:
        label='Word2Vec_BERT'
    else:
        label='Word2Vec_Gensim'
    Word2Vec_Dir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label=label,
                                                            silent=True)
    if Word2Vec_Dir == '':
        return

    ## if statements for any requirements

    if BERT_var:
        reminders_util.checkReminder(config_filename,
                                     reminders_util.title_options_BERT_Word2Vec_timing,
                                     reminders_util.message_BERT_Word2Vec_timing,
                                     True)
        import BERT_util
        BERT_output = BERT_util.word_embeddings_BERT(window, inputFilename, inputDir, Word2Vec_Dir, openOutputFiles, createCharts,
                                                   chartPackage, vis_menu_var, dim_menu_var, compute_distances_var, top_words_var, keywords_var, lemmatize_var, remove_stopwords_var)
        filesToOpen.append(BERT_output)

    if Gensim_var:
        reminders_util.checkReminder(config_filename,
                                     reminders_util.title_options_Gensim_Word2Vec_timing,
                                     reminders_util.message_Gensim_Word2Vec_timing,
                                     True)
        if 'Clustering' in vis_menu_var and keywords_var=='':
            mb.showwarning(title='Missing keywords',message='The algorithm requires a comma-separated list of case-sensitive keywords taken from the corpus to be used as a Word2Vec run.\n\nPlease, enter the keywords and try again.')
            return
        import word2vec_Gensim_util
        filesToOpen = word2vec_Gensim_util.run_Gensim_word2vec(inputFilename, inputDir, Word2Vec_Dir,openOutputFiles, createCharts, chartPackage,
                                 remove_stopwords_var, lemmatize_var,
                                 keywords_var,
                                 compute_distances_var, top_words_var,
                                 sg_menu_var, vector_size_var, window_var, min_count_var, vis_menu_var, dim_menu_var)

    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, Word2Vec_Dir)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_chart_output_checkbox.get(),
                                GUI_util.charts_package_options_widget.get(),
                                remove_stopwords_var.get(),
                                lemmatize_var.get(),
                                BERT_var.get(),
                                Gensim_var.get(),
                                compute_distances_var.get(),
                                top_words_var.get(),
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
                             GUI_height_brief=600, # height at brief display
                             GUI_height_full=680, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Word2Vec with BERT and Gensim'
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
config_input_output_numeric_options=[6,1,0,1]

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
compute_distances_var=tk.IntVar()
top_words_var=tk.IntVar()

sg_menu_var=tk.StringVar()
vector_size_var=tk.IntVar()
window_var=tk.IntVar()
min_count_var=tk.IntVar()
vis_menu_var=tk.StringVar()
dim_menu_var=tk.StringVar()
keywords_var=tk.StringVar()

def clear(e):
    remove_stopwords_var.set(1)
    lemmatize_var.set(1)
    vis_menu_var.set('Do not plot word vectors')
    dim_menu_var.set('')
    sg_menu_var.set('Skip-Gram')
    vector_size_var.set(100)
    window_var.set(5)
    min_count_var.set(5)
    top_words_var.set(200)
    keywords_var.set('')
    activate_all_options()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

## option for stopwords
remove_stopwords_var.set(1)
remove_stopwords_checkbox = tk.Checkbutton(window, text='Remove stopwords & punctuation', variable=remove_stopwords_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,remove_stopwords_checkbox)

## option for Lemmatization
lemmatize_var.set(1)
lemmatize_checkbox = tk.Checkbutton(window, text='Lemmatize', variable=lemmatize_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,lemmatize_checkbox)

vis_var_lb = tk.Label(window,text='Select visualization option')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,vis_var_lb,True)
vis_menu_var.set('Do not plot word vectors')
vis_menu = tk.OptionMenu(window,vis_menu_var, 'Do not plot word vectors', 'Plot word vectors')
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,
    y_multiplier_integer,
    vis_menu,
    True, False, False, False, 90, GUI_IO_util.IO_configuration_menu,
    "The visualizaton of an n-dimensional space in a 2 or 3 dimensional space is\n1. computationally very demanding (depending upon the number of words)\n2. somewhat misleading (you are better off looking at cosine similarities).")

#### 2D or 3D plot
dim_menu_var.set('')
dim_menu = tk.OptionMenu(window,dim_menu_var, '2D', '3D')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.setup_pop_up_text_widget,y_multiplier_integer,dim_menu)

def activate_plot_options(*args):
    if not 'Do not' in vis_menu_var.get():
        dim_menu_var.set('2D')
        dim_menu.configure(state='normal')
    else:
        dim_menu_var.set('')
        dim_menu.configure(state='disabled')
vis_menu_var.trace('w',activate_plot_options)

## option for BERT
BERT_var.set(0)
BERT_checkbox = tk.Checkbutton(window, text='Word embeddings (via BERT (English language model))', variable=BERT_var, onvalue=1, offvalue=0, command=lambda:activate_all_options())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,BERT_checkbox)

## option for Gensim
Gensim_var.set(0)
Gensim_checkbox = tk.Checkbutton(window, text='Word2Vec (via Gensim)', variable=Gensim_var, onvalue=1, offvalue=0, command=lambda:activate_all_options())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,Gensim_checkbox)

## option for Gensim model architecture
sg_lb = tk.Label(window,text='Training model architecture')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,sg_lb,True)
sg_menu_var.set('Skip-Gram')
sg_menu = tk.OptionMenu(window,sg_menu_var, 'Skip-Gram','CBOW')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,y_multiplier_integer,sg_menu)

## option for Gensim vector size
vector_size_lb = tk.Label(window,text='Vector size')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,vector_size_lb,True)

vector_size_var.set(100)
vector_size_entry = tk.Entry(window,width=5,textvariable=vector_size_var)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.Word2Vec_vector_size_entry_pos,y_multiplier_integer,vector_size_entry, True)

## option for window size
window_lb = tk.Label(window,text='Window size')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,y_multiplier_integer,window_lb,True)

window_var.set(5)
window_size_entry = tk.Entry(window,width=5,textvariable=window_var)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.Word2Vec_window_size_entry_pos,y_multiplier_integer,window_size_entry, True)

## option for minimum count
min_count_lb = tk.Label(window,text='Minimum count')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.Word2Vec_min_count_lb_pos,y_multiplier_integer,min_count_lb,True)

min_count_var.set(5)
min_count_entry = tk.Entry(window,width=5,textvariable=min_count_var)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.Word2Vec_min_count_entry_pos,y_multiplier_integer,min_count_entry)

## option for visualization method

compute_distances_var.set(1)
compute_distances_checkbox = tk.Checkbutton(window, text='Compute word distances', variable=compute_distances_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
    y_multiplier_integer,
    compute_distances_checkbox,
    True, False, False, False, 90, GUI_IO_util.labels_x_coordinate,
    "Tick/untick the checkbox to (not)compute Eucledian 2-dimensional and n-dimensional distances and cosine similarity between words.\nComputing word similarities can be computationally demanding and time consuming, but VERY useful in locating words in a semantic space.\nYOU DO NOT NEED TO RE-RUN WORD2VC ON A SET OF TXT FILES. YOU CAN USE A CSV VECTOR FILE PREVIOUSLY COMPUTED.")

## option for number of words for Euclidean distance
top_words_lb = tk.Label(window,text='Number of top words for Euclidean distance & cosine similarity combinations')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,y_multiplier_integer,top_words_lb,True)

top_words_var.set(200)
top_words_entry = tk.Entry(window,width=5,textvariable=top_words_var)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.Word2Vec_top_words_pos,
    y_multiplier_integer,
    top_words_entry,
    False, False, False, False, 90, GUI_IO_util.labels_x_coordinate,
    "Enter the number of top words to be used in computing distances (the more words, the longer it takes to compute distances)")

keywords_var.set('')
keywords_lb = tk.Label(window, text='Keywords')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,keywords_lb,True)

keywords_entry = tk.Entry(window, textvariable=keywords_var)
keywords_entry.configure(state='normal',width=GUI_IO_util.widget_width_extra_long)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,
    y_multiplier_integer,
    keywords_entry,
    False, False, False, False, 90, GUI_IO_util.IO_configuration_menu,
    "Enter the comma-separated, case-sensitive words to be used to visualize Euclidean distances and cosine similarity between selected words.\nCosine similarity will always be computed for the top selected n words whether the checkbox 'Compute word distances' is ticked or not.")

def activate_all_options():
    BERT_checkbox.configure(state='normal')
    Gensim_checkbox.configure(state='normal')
    sg_menu.configure(state='normal')
    vector_size_entry.configure(state='normal')
    window_size_entry.configure(state='normal')
    min_count_entry.configure(state='normal')
    if BERT_var.get():
        Gensim_checkbox.configure(state='disabled')
        sg_menu.configure(state='disabled')
        vector_size_entry.configure(state='disabled')
        window_size_entry.configure(state='disabled')
        min_count_entry.configure(state='disabled')
    if Gensim_var.get():
        BERT_checkbox.configure(state='disabled')
        sg_menu.configure(state='normal')
        vector_size_entry.configure(state='normal')
        window_size_entry.configure(state='normal')
        min_count_entry.configure(state='normal')
#
videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {"Lemmas & stopwords":"TIPS_NLP_NLP Basic Language.pdf",
               "Word embeddings with BERT": "TIPS_NLP_BERT word embeddings.pdf",
               "Word2Vec with Gensim":"TIPS_NLP_Word2Vec.pdf",
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf'}

TIPS_options = 'Lemmas & stopwords', 'Word embeddings with BERT', 'Word2Vec with Gensim', 'csv files - Problems & solutions', 'Statistical measures'

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
                                  "Please, using the dropdown menus, select the types of preferred display.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "Please, tick the checkbox to run word embeddings via BERT.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "Please, tick the checkbox to run Word2Vec via Gensim.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "Please, using the dropdown menu, select the preferred model architecture for training Word2Vec: Skip-Gram and CBOW (Continuous Bag of Words).\n\nWhich model is better?\n\nAccording to the original paper by Mikolov et al. (2013) Skip-Gram works well with small datasets, and can better represent less frequent words. However, CBOW is found to train faster than Skip-Gram, and can better represent more frequent words.\n\nMikolov, Tomas, Kai Chen, Greg Corrado, and Jeffrey Dean. 2013. 'Efficient Estimation of Word Representations in Vector Space' arXiv:1301.3781.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "'Vector size' refers to the dimensionality of the word vectors. If you have a large corpus (> billions of tokens), you can go up to 100-300 dimensions. Generally word vectors with more dimensions give better results." \
                                  "\n\n'Window size' refers to the maximum distance between the current and predicted word within a sentence. In other words, how many words come before and after your given word." \
                                  "\n\n'Minimum count' refers to the minimum frequency threshold. The words with total frequency lower than this will be ignored.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "Please, tick the checkbox to compute Euclidean distances and cosine similarity between words. Cosine similarity measure will be computed whether the checkbox 'Compute word distances' is ticked or not.\n\n2-dimentional distances reflect the position of words in the two-dimentional html graph. But... it may not reflect the 'true' semantic distance between words, more accurately measured by the n-dimenional distance (which, of course, you cannot see).\n\nCosine similarity varies betwteen 0 and 1 (a value 0 indicates that the words are orthgonal to each other, i.e., they are distant in the semantic space; a value of 1 indicates the opposite.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "Enter comma-separated, case-sensitive keywords you want to focus on for semantic similarity. The words MUST be in the file(s) being analyzed, either as lemma or as the original word. Words not present in the document(s) will be skipped silently.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help", GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

error=False
def changed_filename(tracedInputFile):
    global error
    if os.path.isfile(tracedInputFile):
        if not tracedInputFile.endswith('.csv') and not tracedInputFile.endswith('.txt'):
            error = True
            return
        else:
            error = False
    clear("<Escape>")
GUI_util.inputFilename.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))

# change the value of the readMe_message
readMe_message="This Python 3 script analyzes a set of documents for Gensim Word2Vec or BERT context-dependent word embeddings.\n\nIn INPUT the algorithms expect either a single txt file or a set of txt files in a directory or a csv file containing each word, their n-dimensional vectors, sentence, document, the output of a previous Word2Vec run with txt file(s) in input.\n\nIn OUTPUT, the algorithms display the multi-dimensional output vectors in an html interactive file in either a 2- or 3-dimensional space. To facilitate the search for words in the vsual output, the algorithms also produce a csv file with the Eucledian distances of every word with every other word for the 10 most-frequent words."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

reminders_util.checkReminder(
    config_filename,
    reminders_util.title_options_Word2Vec,
    reminders_util.message_Word2Vec,
    True)

reminders_util.checkReminder(
    config_filename,
    reminders_util.title_options_Word2Vec_eucledian_distance,
    reminders_util.message_Word2Vec_eucledian_distance,
    True)

if error:
    mb.showwarning(title='Warning',message='The Word2Vec algorithms expect in input either a txt file/directory of txt files or a csv file of previosuly computed Euclidean distances.')
GUI_util.window.mainloop()
