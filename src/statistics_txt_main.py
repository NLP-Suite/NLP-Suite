# written by Roberto Franzosi (Spring/summer 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"statistics_txt_main.py",['os','csv','tkinter','ntpath','collections','subprocess'])==False:
    sys.exit(0)

import os
import tkinter as tk
from subprocess import call

import GUI_IO_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir,openOutputFiles,createCharts,chartPackage,
    n_grams_var,
    corpus_statistics_var):

    filesToOpen = []  # Store all files that are to be opened once finished
    openOutputFilesSV=openOutputFiles
    outputDir_style=outputDir

    if n_grams_var == True:
        call("python NGrams_CoOccurrences_Viewer_main.py", shell=True)
        return

    if corpus_statistics_var:
        call("python style_analysis_main.py", shell=True)
        return

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_chart_output_checkbox.get(),
                                GUI_util.charts_dropdown_field.get(),
                                n_grams_var.get(),
                                corpus_statistics_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=320, # height at brief display
                             GUI_height_full=360, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=1, # to be added for full display
                             increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Statistical Analyses of txt Files'
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

GUI_util.set_window(GUI_size, GUI_label, config_filename,config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

def clear(e):
    n_grams_checkbox.configure(state='normal')
    corpus_statistics_checkbox.configure(state='normal')

    n_grams_var.set(0)
    corpus_statistics_var.set(0)

    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

# GUI CHANGES cut/paste special GUI widgets from GUI_util

n_grams_list=[]

bySentenceIndex_var=tk.IntVar()

n_grams_button = tk.Button(window, width=70, text='Compute N-Grams (Open GUI)',  command=lambda: call("python html_annotator_gender_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                   n_grams_button,
                                   False, False, True, False, 90, GUI_IO_util.get_labels_x_coordinate(),
                                   "Click on the button to open the GUI")

corpus_statistics_button = tk.Button(window, width=70, text='Compute document(s) statistics (Open GUI)',  command=lambda: call("python html_annotator_gender_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                   corpus_statistics_button,
                                   False, False, True, False, 90, GUI_IO_util.get_labels_x_coordinate(),
                                   "Click on the button to open the GUI")

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Style analysis':'TIPS_NLP_Style analysis.pdf',
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',
               'N-Grams (word & character)':"TIPS_NLP_Ngrams (word & character).pdf",
               'NLP Ngram and Word Co-Occurrence VIEWER':"TIPS_NLP_Ngram and Word Co-Occurrence VIEWER.pdf",
               'Google Ngram Viewer':'TIPS_NLP_Ngram Google Ngram Viewer.pdf',
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf'}

TIPS_options='Style analysis', 'English Language Benchmarks', 'N-Grams (word & character)','NLP Ngram and Word Co-Occurrence VIEWER','Google Ngram Viewer','Excel smoothing data series', 'csv files - Problems & solutions', 'Statistical measures'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_csv_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",'Please, tick the \'N-Grams\' checkbox if you wish to open the N-Grams GUI to analyze n-grams (1, 2, 3) present in your corpus.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  'Please, tick the checkbox if you wish to open the style GUI to compute basic statistics on your corpus.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),0)

# change the value of the readMe_message
readMe_message="The Python 3 scripts provides a quick link to various NLP Suite GUIs for obtaining basic statistics about the corpus (e.g., n-grams, sentence lenght)."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()

