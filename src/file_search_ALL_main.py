# written by Roberto Franzosi October 2019, edited Spring 2020

import GUI_util

from subprocess import call
import tkinter as tk
import os

import GUI_IO_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run():
    print('Exit')

# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run()

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
GUI_label='Graphical User Interface (GUI) for ALL Searches Available in the NLP Suite'
head, scriptName = os.path.split(os.path.basename(__file__))
IO_setup_display_brief=True
config_filename = ''

GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=480, # height at brief display
                             GUI_height_full=560, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

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
config_input_output_numeric_options=[0,0,0,0]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

#setup GUI widgets

y_multiplier_integer = 0

open_CoNLL_search_GUI_button = tk.Button(window, text='CoNLL table searches (Open GUI)',width=GUI_IO_util.widget_width_medium,command=lambda: call("python CoNLL_table_analyzer_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_CoNLL_search_GUI_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")


open_file_search_GUI_button = tk.Button(window, text='File searches (Open GUI)',width=GUI_IO_util.widget_width_medium,command=lambda: call("python file_manager_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_file_search_GUI_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

open_nGram_VIEWER_search_GUI_button = tk.Button(window, text='N-grams/co-occurrences searches (Open GUI)',width=GUI_IO_util.widget_width_medium,command=lambda: call("python NGrams_CoOccurrences_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_nGram_VIEWER_search_GUI_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

open_word_sense_search_GUI_button = tk.Button(window, text='Search word(s) for different word senses (Open GUI)',width=GUI_IO_util.widget_width_medium,command=lambda: call("python word2vec_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_word_sense_search_GUI_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

open_word_distance_search_GUI_button = tk.Button(window, text='Search word(s) for distance to other words in the semantic space (Open GUI)',width=GUI_IO_util.widget_width_medium,command=lambda: call("python word2vec_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_word_distance_search_GUI_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

open_WordNet_search_GUI_button = tk.Button(window, text='WordNet searches (Open GUI)',width=GUI_IO_util.widget_width_medium,command=lambda: call("python knowledge_graphs_WordNet_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_WordNet_search_GUI_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

open_word_search_GUI_button = tk.Button(window, text='Words/collocations searches (Open GUI)',width=GUI_IO_util.widget_width_medium,command=lambda: call("python file_search_byWord_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_word_search_GUI_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")
export_csv_field_GUI_button = tk.Button(window, text='Export csv field content to csv/txt file (Open GUI)',width=GUI_IO_util.widget_width_medium,command=lambda: call("python data_manipulation_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   export_csv_field_GUI_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'No TIPS available':''}
TIPS_options='No TIPS available'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, click on the button to open the GUI for searching a CoNLL table.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, click on the button to open the GUI for searching (and manipulating) files saved in your machine.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, click on the button to open the GUI for an N-grams/Co_occurrences VIEWER similar to Google Ngrams Viewer (https://books.google.com/ngrams) but applied to your own corpus.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, click on the button to open the GUI to run the word sense induction algorithm. The BERT algorithm will compute all the different meanings a word has in your corpus.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, click on the button to open the GUI to run the word embeddings algorithm. The BERT and Gensim algorithms will compute the word embeddings of each word, then compute the cosine similarity and Euclidean distance of each pair of words in your corpus. These distance values will allow to measure the distance of words in the semantic space, i.e., how closely they are used in the corpus.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, click on the button to open the GUI for searching words in the WordNet knowledge graph.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, click on the button to open the GUI for searching words and collocations in text file(s).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help",
                              "Please, click on the button to open the GUI for exporting the content of csv field(s) to a text or csv file.\n\nYou can use this option, for instance, to export all the sentences extracted via any of the searches to a txt file for further analysis.")
    return y_multiplier_integer
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The GUI allows you to access all the specialized searches available in the NLP Suite."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()

