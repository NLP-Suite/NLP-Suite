#written by Roberto Franzosi November 2019

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Wordclouds",['os','tkinter','webbrowser'])==False:
    sys.exit(0)

import os
import webbrowser
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_csv_util
import IO_internet_util


def run(inputFilename, inputDir, outputDir, visualization_tools, prefer_horizontal, lemmatize, stopwords, punctuation, lowercase, collocation, differentPOS_differentColors,selectedImage,
        differentColumns_differentColors, csvField_color_list, openOutputFiles, doNotCreateIntermediateFiles):
    if len(visualization_tools)==0 and differentColumns_differentColors==False:
        mb.showwarning("Warning",
                       "No options have been selected.\n\nPlease, select an option to run and try again.")
        return



#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            wordclouds_var.get(),
                            prefer_horizontal_var.get(),
                            lemmatize_var.get(),
                            stopwords_var.get(),
                            punctuation_var.get(),
                            lowercase_var.get(),
                            collocation_var.get(),
                            differentPOS_differentColors_var.get(),
                            selectedImage_var.get(),
                            differentColumns_differentColors_var.get(),
                            csvField_color_list,
                            GUI_util.open_csv_output_checkbox.get(),
                            doNotCreateIntermediateFiles_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_width=1200
GUI_height=460 # height of GUI with full I/O display

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

GUI_label='Graphical User Interface (GUI) for Visualization Tools'
config_filename='visualization-config.txt'
# The 6 values of config_option refer to:
#   software directory
#   input file
        # 1 for CoNLL file
        # 2 for TXT file
        # 3 for csv file
        # 4 for any type of file
        # 5 for txt or html
        # 6 for txt or csv
#   input dir
#   input secondary dir
#   output file
#   output dir
config_option=[0,3,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_options,config_filename,IO_setup_display_brief)

def clear(e):
    csvField_color_list.clear()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)


Gephi_var = tk.IntVar()

# def run_clouds(window,y_multiplier_integer, wordclouds_var,selectedImage_var,
# 	doNotCreateIntermediateFiles_var,input_main_dir_path):

Excel_button = tk.Button(window, text='Open Excel GUI', width=15, height=1,
                               command=lambda: call("python Excel_charts_main.py", shell=True))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               Excel_button)

GIS_button = tk.Button(window, text='Open GIS GUI', width=15, height=1,
                               command=lambda: call("python GIS_main.py", shell=True))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               GIS_button)

Gephi_var.set(0)
Gephi_checkbox = tk.Checkbutton(window, text='Visualize relations in a Gephi network graph', variable=Gephi_var,
                                    onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               Gephi_checkbox)

# wordclouds_var.set('')
# selectedImage_var.set('')
# wordclouds = tk.OptionMenu(window,wordclouds_var,'Python WordCloud','TagCrowd','Tagul','Tagxedo','Wordclouds','Wordle')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+120, y_multiplier_integer,wordclouds,True)
# wordclouds_lb = tk.Label(window, text='Select the word cloud service you wish to use (txt file(s)/CoNLL table)')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,wordclouds_lb)
#
# y_multiplier_integer_SV=y_multiplier_integer


def update_csvFields():
    csv_field_menu.configure(state="normal")
    color_var.set(0)


# def activateCsvField(*args):
#     if csv_field_var.get()!='':
#         color_checkbox.configure(state='normal')
#         state = str(csv_field_menu['state'])
#         if state != 'disabled':
#             if csv_field_var.get() in csvField_color_list:
#                 mb.showwarning(title='Warning', message='The selected csv field value, ' + csv_field_var.get() + ', has already been selected.\n\nPlease, select a different value. You can display all selected values by clicking on SHOW.')
#                 return
#             add_button.configure(state="normal")
#             reset_button.configure(state="normal")
#             show_columns_button.configure(state='normal')
#             csvField_color_list.append(csv_field_var.get())
#             csv_field_menu.configure(state='disabled')
#         else:
#             add_button.configure(state="normal")
#             reset_button.configure(state="normal")
#             show_columns_button.configure(state='normal')
#             csv_field_menu.configure(state='normal')
#     else:
#         add_button.configure(state="disabled")
#         reset_button.configure(state="disabled")
#         show_columns_button.configure(state='disabled')
#         color_checkbox.configure(state='disabled')
# csv_field_var.trace('w',activateCsvField)


# def changed_filename(*args):
#     # menu_values is the number of headers in the csv dictionary file
#     menu_values=IO_csv_util.get_csvfile_headers(inputFilename.get())
#     m = csv_field_menu["menu"]
#     m.delete(0,"end")
#     for s in menu_values:
#         m.add_command(label=s,command=lambda value=s:csv_field_var.set(value))
# inputFilename.trace('w',changed_filename)
# input_main_dir_path.trace('w',changed_filename)
#
# changed_filename()

# doNotCreateIntermediateFiles_var.set(1)
# doNotCreateIntermediateFiles_checkbox = tk.Checkbutton(window, variable=doNotCreateIntermediateFiles_var, onvalue=1, offvalue=0)
# doNotCreateIntermediateFiles_checkbox.config(text="Do NOT produce intermediate word cloud files when processing all txt files in a directory")
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,doNotCreateIntermediateFiles_checkbox)

TIPS_lookup = {"Lemmas & stopwords":"TIPS_NLP_NLP Basic Language.pdf", "Word clouds":"TIPS_NLP_Wordclouds Visualizing word clouds.pdf","Wordle":"TIPS_NLP_Wordclouds Wordle.pdf","Tagxedo":"TIPS_NLP_Wordclouds Tagxedo.pdf","Tagcrowd":"TIPS_NLP_Wordclouds Tagcrowd.pdf"}
TIPS_options='Lemmas & stopwords', 'Word clouds', 'Tagcrowd', 'Tagxedo', 'Wordle'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    if not IO_setup_display_brief:
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",GUI_IO_util.msg_CoNLL)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_corpusData)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help",GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+1),"Help","Please, using the dropdown menu, select the word cloud service you want to use to generate a worldcloud.\n\nFor 'TagCrowd', 'Tagul', 'Tagxedo', 'Wordclouds', and 'Wordle' you must be connected to the internet. You will also need to copy/paste text or upload a text file, depending upon the word clouds service. If you wish to visualize the words in all the files in a directory, you would need to merge the files first via the file_merger_main, then use your merged file.\n\nThe Python algorithm uses Andreas Mueller's Python package WordCloud (https://amueller.github.io/word_cloud/) can be run without internet connection.\n\nIn INPUT the algorithm expects a single txt file or a directory of txt files or a csv CoNLL table file.\n\nIn OUTPUT the algorithm creates word cloud image file(s).")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+2),"Help","\n\nThe filter options are only available when selecting Python as the wordcloud service to use. When available,\n\n   1. tick the 'Horizonal' checkbox if you wish to display words in the wordcloud horizonally only;\n   2. tick the 'Lemmas' checkbox if you wish to lemmatize the words in the input file(s);\n   3. tick the 'Stopwords' checkbox if you wish to exclude from processing stopwords present in the input file(s);\n   4. tick the 'Punctuation' checkbox if you wish to exclude from processing punctuation symbols present in the input file(s);\n   5. tick the 'Lowercase' checkbox if you wish to convert all words to lowercase to avoid having some words capitalized simly because they are the first words in a sentence;\n   6. tick the 'Collocation' checkbox if you wish to keep together common combinations of words (South Carolina; White House);\n   7. tick the 'Different colors for different POS tags' checkbox if you wish to display different POSTAG values (namely, nouns, verbs, adjectives, and adverbs) in different colors (RED for NOUNS, BLUE for VERBS, GREEN for ADJECTIVES, and GREY for ADVERBS; YELLOW for any other POS tags). For greater control over the use of different colors for different items, you can use the csv file option below with a CoNLL table as input. You will then be able to use NER or DEPREL and not just POSTAG (or more POSTAG values).\n\nStanford CoreNLP STANZA will be used to tokenize sentences, lemmatize words, and compute POS tags. Depending upon the number of files processed and length of files, the process can be time consuming. Please, be patient.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+3),"Help","Please, select a png image file to be used to dislay the word cloud in the image.\n\nThe image must be a completely black image set in a white background.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+4),"Help",GUI_IO_util.msg_openOutputFiles)
help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The Python 3 script and online services display the content of text files as word cloud.\n\nA word cloud, also known as text cloud or tag cloud, is a collection of words depicted visually in different sizes (and colors). The bigger and bolder the word appears, the more often it’s mentioned within a given text and the more important it is.\n\nDifferent, freeware, word cloud applications are available: 'TagCrowd', 'Tagul', 'Tagxedo', 'Wordclouds', and 'Wordle'. These applications require internet connection.\n\nThe script also provides Python word clouds (via Andreas Mueller's Python package WordCloud https://amueller.github.io/word_cloud/) for which no internet connection is required."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup, TIPS_options, IO_setup_display_brief)

GUI_util.window.mainloop()
