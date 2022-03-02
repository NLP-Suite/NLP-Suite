# written by Roberto Franzosi October 2019, edited Spring 2020

import GUI_util

from subprocess import call
import tkinter as tk
import os

import GUI_IO_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run():
    print()
#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run()

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
GUI_label='Graphical User Interface (GUI) for ALL searches available in the NLP Suite'
head, scriptName = os.path.split(os.path.basename(__file__))
IO_setup_display_brief=True
config_filename = ''

GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=360, # height at brief display
                             GUI_height_full=440, # height at full display
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

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)

def clear(e):
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)


#setup GUI widgets

y_multiplier_integer = 0

open_word_search_GUI_button = tk.Button(window, text='Open GUI for words/collocations searches',width=40,command=lambda: call("python file_search_byWord_main.py", shell=True))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,open_word_search_GUI_button)

open_CoNLL_search_GUI_button = tk.Button(window, text='Open GUI for CoNLL table searches',width=40,command=lambda: call("python CoNLL_table_analyzer_main.py", shell=True))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,open_CoNLL_search_GUI_button)

open_nGram_VIEWER_search_GUI_button = tk.Button(window, text='Open GUI for N-grams/co-occurrences searches',width=40,command=lambda: call("python NGrams_CoOccurrences_Viewer_main.py", shell=True))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,open_nGram_VIEWER_search_GUI_button)

open_WordNet_search_GUI_button = tk.Button(window, text='Open GUI for WordNet searches',width=40,command=lambda: call("python knowledge_graphs_WordNet_main.py", shell=True))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,open_WordNet_search_GUI_button)

open_file_search_GUI_button = tk.Button(window, text='Open GUI for file searches',width=40,command=lambda: call("python file_manager_main.py", shell=True))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,open_file_search_GUI_button)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'No TIPS available':''}
TIPS_options='No TIPS available'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help", "Please, click on the button to open the GUI for searching words and collocations in text file(s).")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help", "Please, click on the button to open the GUI for searching a CoNLL table.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help","Please, click on the button to open the GUI for an N-grams/Co_occurrences VIEWER similar to Google Ngrams Viewer (https://books.google.com/ngrams) but applied to your own corpus.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*3,"Help","Please, click on the button to open the GUI for searching words in the WordNet knowledge graph.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*4,"Help","Please, click on the button to open the GUI for searching (and manipulating) files saved in your machine.")
help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The GUI allows you to access all the specialized searches available in the NLP Suite."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()

