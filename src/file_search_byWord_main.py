# written by Roberto Franzosi October 2019, edited Spring 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_search_byWord_main.py",['os','tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_files_util
import file_search_byWord_util
import IO_user_interface_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,inputDir, outputDir,
    openOutputFiles,
    createExcelCharts,
    search_options,
    search_by_dictionary,
    selectedCsvFile,
    search_by_keyword,
    search_keyword_values):

    filesToOpen = []

    if search_by_dictionary==False and search_by_keyword==False:
            mb.showwarning(title='Input error', message='No search options have been selected.\n\nPlease, select a search option and try again.')
            return

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Word/collocation search start',
                        'Started running Word/collocation search at', True,
                        'SEARCH options: ' + str(search_options_list)+'\nSEARCH words: '+search_keyword_values,
                                       True, '', True)

    outputFile = file_search_byWord_util.run(inputFilename, inputDir, outputDir, search_by_dictionary, search_by_keyword, search_keyword_values, search_options_list)

    if outputFile!='':
        filesToOpen.append(outputFile)
    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_Excel_chart_output_checkbox.get(),
                            search_options_menu_var.get(),
                            search_by_dictionary_var.get(),
                            selectedCsvFile_var.get(),
                            search_by_keyword_var.get(),
                            keyword_value_var.get(),
                               )

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=440, # height at brief display
                             GUI_height_full=520, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for File Search by Single Word or Collocations'
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
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputDir =GUI_util.input_main_dir_path
outputDir =GUI_util.output_dir_path

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)

search_options_menu_var=tk.StringVar()
search_by_dictionary_var=tk.IntVar()
selectedCsvFile_var=tk.StringVar()
search_by_keyword_var=tk.IntVar()
keyword_value_var=tk.StringVar()
search_options_list=[]

def clear(e):
    GUI_util.clear("Escape")
    search_options_list.clear()
    search_options_menu_var.set('Case sensitive (default)')
    keyword_value_var.set('')
window.bind("<Escape>", clear)


#setup GUI widgets

search_options_menu_var.set('Case sensitive (default)')
search_options_menu_lb = tk.Label(window, text='Search options')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,search_options_menu_lb,True)
search_options_menu = tk.OptionMenu(window, search_options_menu_var, 'Case sensitive (default)','Case insensitive','Lemmatize', 'Search within sentence (default)', 'Search within document')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,search_options_menu, True)

add_search_button = tk.Button(window, text='+', width=2,height=1,state='disabled',command=lambda: activate_search_var())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+300,y_multiplier_integer,add_search_button, True)

reset_search_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: reset_search_options_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+340,y_multiplier_integer,reset_search_button,True)

show_search_button = tk.Button(window, text='Show', width=5,height=1,state='disabled',command=lambda: show_search_options_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+400,y_multiplier_integer,show_search_button)

def reset_search_options_list():
    search_options_list.clear()
    search_options_menu_var.set('Case sensitive (default)')
    search_options_menu.configure(state='normal')

def show_search_options_list():
    if len(search_options_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected SEARCH options.')
    else:
        mb.showwarning(title='Warning', message='The currently selected SEARCH options are:\n\n' + ','.join(search_options_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

def activate_search_var():
    # Disable the + after clicking on it and enable the menu
    add_search_button.configure(state='disabled')
    search_options_menu.configure(state='normal')

def activate_search_options(*args):
    if search_options_menu_var.get()!='':
        if search_options_menu_var.get() in search_options_list:
            mb.showwarning(title='Warning', message='The option has already been selected. Selection ignored.\n\nYou can see your current selections by clicking the Show button.')
            return
        # remove the case option, when a different one is selected
        if 'insensitive' in search_options_menu_var.get() and 'sensitive' in str(search_options_list):
            search_options_list.remove('Case sensitive (default)')
        if 'sensitive' in search_options_menu_var.get() and 'insensitive' in str(search_options_list):
            search_options_list.remove('Case insensitive')
        if search_options_menu_var.get()=='Lemmatize':
            mb.showwarning(title='Warning', message='The option is not available yet.\n\nSorry!')
            # search_options_menu_var.set('')
            if len(search_options_list) > 0:
                add_search_button.configure(state='normal')
                reset_search_button.configure(state='normal')
                show_search_button.configure(state='normal')
                return
        search_options_list.append(search_options_menu_var.get())
        # search_options_menu.configure(state="disabled")
        add_search_button.configure(state='normal')
        reset_search_button.configure(state='normal')
        show_search_button.configure(state='normal')
    else:
        add_search_button.configure(state='disabled')
        reset_search_button.configure(state='disabled')
        show_search_button.configure(state='disabled')
        # for now... always disabled
        # search_options_menu.configure(state="disabled")
        search_options_menu.configure(state="normal")
search_options_menu_var.trace('w',activate_search_options)

activate_search_options()

# lemmatize_var.set(0)
# lemmatize_checkbox = tk.Checkbutton(window, text='Lemmatize', variable=lemmatize_var, onvalue=1, offvalue=0)
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+120,y_multiplier_integer,lemmatize_checkbox,True)
#
# within_sentence_var.set(0)
# within_sentence_checkbox = tk.Checkbutton(window, text='Within sentence', variable=within_sentence_var, onvalue=1, offvalue=0)
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+120,y_multiplier_integer,within_sentence_checkbox,True)

search_by_dictionary_var.set(0)
search_by_dictionary_checkbox = tk.Checkbutton(window, text='Search corpus by dictionary value', variable=search_by_dictionary_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,search_by_dictionary_checkbox)

dictionary_button=tk.Button(window, width=20, text='Select dictionary file',command=lambda: get_dictionary_file(window,'Select INPUT dictionary file', [("dictionary files", "*.csv")]))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20, y_multiplier_integer,dictionary_button,True)

def get_dictionary_file(window,title,fileType):
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)
    if len(filePath)>0:
        #always disabled; user cannot tinker with the selection
        #selectedCsvFile.config(state='disabled')
        selectedCsvFile_var.set(filePath)

#setup a button to open Windows Explorer on the selected input directory
current_y_multiplier_integer=y_multiplier_integer-1
openInputFile_button  = tk.Button(window, width=3, text='', command=lambda: IO_files_util.openFile(window, selectedCsvFile_var.get()))
openInputFile_button.place(x=GUI_IO_util.get_labels_x_coordinate()+180, y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

selectedCsvFile = tk.Entry(window,width=100,state='disabled',textvariable=selectedCsvFile_var)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,selectedCsvFile)

search_by_keyword_var.set(0)
search_by_keyword_checkbox = tk.Checkbutton(window, text='Search corpus by single words/collocations', variable=search_by_keyword_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,search_by_keyword_checkbox,True)

keyword_value_var.set('')
keyword_value = tk.Entry(window,width=100,textvariable=keyword_value_var)
keyword_value.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,keyword_value)

open_GUI_button = tk.Button(window, text='Open GUI for N-grams/co-occurrences VIEWER',command=lambda: call("python NGrams_CoOccurrences_Viewer_main.py", shell=True))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,open_GUI_button)


def activate_allOptions(*args):
    selectedCsvFile.configure(state='disabled')
    if search_by_dictionary_var.get()==True:
        dictionary_button.config(state='normal')
        search_by_keyword_checkbox.configure(state='disabled')
        keyword_value.configure(state='disabled')
    else:
        dictionary_button.config(state='disabled')
        selectedCsvFile_var.set('')
        search_by_keyword_checkbox.configure(state='normal')
        keyword_value.configure(state='disabled')
    if search_by_keyword_var.get()==True:
        dictionary_button.config(state='disabled')
        search_by_dictionary_checkbox.configure(state='disabled')
        selectedCsvFile_var.set('')
        keyword_value.configure(state='normal')
    else:
        search_by_dictionary_checkbox.configure(state='normal')
        keyword_value.configure(state='disabled')
search_by_dictionary_var.trace('w',activate_allOptions)
search_by_keyword_var.trace('w',activate_allOptions)

activate_allOptions()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'No TIPS available':''}
TIPS_options='No TIPS available'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    clearOptions="\n\nTo clear a previously selected option for any of the tools, click on the appropriate dropdown menu and press ESCape."
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_anyFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_anyData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, use the dropdown menu to set up the search criteria. Multiple criteria can be seleced by clicking on the + button. Currently selected criteria can be displayed by clicking on the Show button.\n\nWhen lemmatizing, the scripts would search 'coming out' in all its lemmatized forms: 'coming out', 'come out', 'comes out', 'came out'.\n\nWhen searching 'Within sentence' combinations of words or collocations will be searched and displayed within SENTENCE otherwise within DOCUMENT.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to search input txt file(s) using the values contained in a csv dictionary file.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, click to select a csv file containing a list of values to be used as a dictionary for searching the file(s).\n\nEntries in the file, one per line, can be single words or collocations, i.e., combinations of words such as 'coming out,' 'standing in line'.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox to search input txt file(s) by single words or collocations, i.e., combinations of words such as 'coming out,' 'standing in line'.\n\nSeveral words/collocations can also be entered, comma separated (e.g, coming out, gay, boyfriend).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, click on the button to open a GUI with more options for an N-grams/Co_occurrences VIEWER similar to Google Ngrams Viewer (https://books.google.com/ngrams) but applied to your own corpus.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1

y_multiplier_integer = help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),0)

# change the value of the readMe_message
readMe_message="These Python 3 scripts search txt files by single words or collocations (e.g., a set of multiple words, such as 'coming out' or 'standing in line'). Search words can be entered in a csv dictionary or manually in the GUI enter widget.\n\nIn INPUT the scripts expect a single txt file or a set of txt files in a directory.\n\nIn OUTPUT the scripts generate a csv file with information about the document, sentence, word/collocation searched, and, most importantly, about the relative position where the search word appears in the text."
readMe_command = lambda: GUI_IO_util.display_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

# a reminder is in file_manager_merger_splitter_main
#	reminders_util.checkReminder("Split output files")

GUI_util.window.mainloop()

