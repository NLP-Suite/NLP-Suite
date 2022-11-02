# written by Roberto Franzosi October 2019, edited Spring 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_search_byWord_main.py",['os','tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_files_util
import file_search_byWord_util
import IO_user_interface_util
import reminders_util
import constants_util
import config_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,inputDir, outputDir,
    openOutputFiles,
    createCharts,
    chartPackage,
    search_options,
    search_by_dictionary,
    selectedCsvFile,
    search_by_keyword,
    search_keyword_values,
    extract_sentences_var,
    extract_sentences_search_words_var_str):

    filesToOpen = []

    if search_by_dictionary==False and search_by_keyword==False and extract_sentences_var==False:
            mb.showwarning(title='Input error', message='No search options have been selected.\n\nPlease, select a search option and try again.')
            return

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Word/collocation search start',
                        'Started running Word/collocation search at', True,
                        'SEARCH options: ' + str(search_options_list)+'\nSEARCH words: '+search_keyword_values,
                                       True, '', True)

    if not 'Search within document' in search_options_list:
        if not 'Search within sentence (default)' in search_options_list:
            search_options_list.append('Search within sentence (default)')

    if search_by_keyword:
        filesToOpen = file_search_byWord_util.search_sentences_documents(inputFilename, inputDir, outputDir, search_by_dictionary,
                                                  search_by_keyword, search_keyword_values, search_options_list, language,
                                                  createCharts, chartPackage)

    if extract_sentences_var:
        file_search_byWord_util.search_extract_sentences(window, inputFilename, inputDir, outputDir,
                                                 extract_sentences_search_words_var_str, search_options_list,
                                                 createCharts, chartPackage)
        extract_sentences_search_words_var.set('')
        extract_sentences_search_words_entry.configure(state='disabled')


    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_chart_output_checkbox.get(),
                            GUI_util.charts_dropdown_field.get(),
                            search_options_menu_var.get(),
                            search_by_dictionary_var.get(),
                            selectedCsvFile_var.get(),
                            search_by_keyword_var.get(),
                            keyword_value_var.get(),
                            extract_sentences_var.get(),
                            extract_sentences_search_words_var.get()
                               )

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=480, # height at brief display
                             GUI_height_full=560, # height at full display
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

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

language_list = []

search_options_menu_var=tk.StringVar()
search_by_dictionary_var=tk.IntVar()
selectedCsvFile_var=tk.StringVar()
search_by_keyword_var=tk.IntVar()
keyword_value_var=tk.StringVar()
search_options_list=[]
extract_sentences_var = tk.IntVar()
extract_sentences_search_words_var = tk.StringVar()
selectedFile_var=tk.StringVar()

def clear(e):
    GUI_util.clear("Escape")
    search_options_list.clear()
    search_options_menu_var.set('Case sensitive (default)')
    keyword_value_var.set('')
    extract_sentences_search_words_var.set('')
window.bind("<Escape>", clear)


#setup GUI widgets

search_options_menu_var.set('Case sensitive (default)')
search_options_menu_lb = tk.Label(window, text='Search options')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,search_options_menu_lb,True)

search_options_menu = tk.OptionMenu(window, search_options_menu_var, 'Case sensitive (default)','Case insensitive','Exact match','Partial match (default)','Search within sentence (default)', 'Search within document','Lemmatize')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_file_directory_coordinate,y_multiplier_integer,search_options_menu, True)

add_search_button = tk.Button(window, text='+', width=2,height=1,state='disabled',command=lambda: activate_search_var())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.file_search_byWord_add_search_button_pos,y_multiplier_integer,add_search_button, True)

reset_search_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: reset_search_options_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.file_search_byWord_reset_search_button_pos,y_multiplier_integer,reset_search_button,True)

show_search_button = tk.Button(window, text='Show', width=5,height=1,state='disabled',command=lambda: show_search_options_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.file_search_byWord_show_search_button_pos,y_multiplier_integer,show_search_button)

def reset_search_options_list():
    search_options_list.clear()
    search_options_menu_var.set('Case sensitive (default)')
    search_options_menu.configure(state='normal')

def show_search_options_list():
    if len(search_options_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected SEARCH options.')
    else:
        mb.showwarning(title='Warning', message='The currently selected SEARCH options are:\n\n  ' + '\n  '.join(search_options_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

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
        if search_options_menu_var.get()=='Lemmatize' or search_options_menu_var.get()=='Exact match':
            mb.showwarning(title='Warning', message='The option is not available yet.\n\nSorry!')
            # search_options_menu_var.set('')
            if len(search_options_list) > 0:
                add_search_button.configure(state='normal')
                reset_search_button.configure(state='normal')
                show_search_button.configure(state='normal')
                return
        if not search_options_menu_var.get() in search_options_list:
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

search_by_dictionary_var.set(0)
search_by_dictionary_checkbox = tk.Checkbutton(window, text='Search corpus by dictionary value', variable=search_by_dictionary_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,search_by_dictionary_checkbox)

dictionary_button=tk.Button(window, width=20, text='Select dictionary file',command=lambda: get_dictionary_file(window,'Select INPUT dictionary file', [("dictionary files", "*.csv")]))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,dictionary_button,True)

def get_dictionary_file(window,title,fileType):
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)
    if len(filePath)>0:
        #always disabled; user cannot tinker with the selection
        #selectedCsvFile.config(state='disabled')
        selectedCsvFile_var.set(filePath)

#setup a button to open Windows Explorer on the selected input directory
# current_y_multiplier_integer=y_multiplier_integer-1
openInputFile_button = tk.Button(window, width=3, text='', command=lambda: IO_files_util.openFile(window, selectedCsvFile_var.get()))
# the button widget has hover-over effects (no_hover_over_widget=False) and the info displayed is in text_info
# the two x-coordinate and x-coordinate_hover_over must have the same values
y_multiplier_integer = GUI_IO_util.placeWidget(window,
    GUI_IO_util.file_search_byWord_openInputFile_button_pos, y_multiplier_integer,
    openInputFile_button, True, False, True, False, 90, GUI_IO_util.file_search_byWord_openInputFile_button_pos, "Open selected csv dictionary file")

selectedCsvFile = tk.Entry(window,width=GUI_IO_util.widget_width_extra_long,state='disabled',textvariable=selectedCsvFile_var)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.file_search_byWord_selectedCsvFile_pos,y_multiplier_integer,selectedCsvFile)

search_by_keyword_var.set(0)
search_by_keyword_checkbox = tk.Checkbutton(window, text='Search corpus by single word(s)/collocation(s)', variable=search_by_keyword_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,search_by_keyword_checkbox,True)

keyword_value_var.set('')
keyword_value = tk.Entry(window,width=GUI_IO_util.widget_width_extra_long,textvariable=keyword_value_var)
keyword_value.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.file_search_byWord_keyword_value_pos,y_multiplier_integer,keyword_value)


def activate_options():
    extract_sentences_search_words_entry.configure(state='normal')

extract_sentences_var.set(0)
extract_sentences_checkbox = tk.Checkbutton(window, text='Search corpus by single word(s)/collocation(s) (extract sentences)',
                                            variable=extract_sentences_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               extract_sentences_checkbox, True)

extract_sentences_search_words_var.set('')
extract_sentences_search_words_entry = tk.Entry(window, textvariable=extract_sentences_search_words_var)
extract_sentences_search_words_entry.configure(width=GUI_IO_util.widget_width_extra_long, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.file_search_byWord_extract_sentences_search_words_entry_pos, y_multiplier_integer,
                                               extract_sentences_search_words_entry)

open_GUI_button = tk.Button(window, text='Open GUI for N-grams/co-occurrences VIEWER',command=lambda: call("python NGrams_CoOccurrences_Viewer_main.py", shell=True))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,open_GUI_button)

def activate_allOptions(*args):
    search_by_dictionary_checkbox.configure(state='normal')
    selectedCsvFile.configure(state='disabled')
    search_by_keyword_checkbox.configure(state='normal')
    keyword_value.configure(state='disabled')
    keyword_value_var.set('')
    extract_sentences_checkbox.configure(state='normal')
    extract_sentences_search_words_entry.configure(state='disabled')
    extract_sentences_search_words_var.set('')
    if search_by_dictionary_var.get()==True:
        dictionary_button.config(state='normal')
        search_by_keyword_checkbox.configure(state='disabled')
        keyword_value.configure(state='disabled')
        keyword_value_var.set('')
        extract_sentences_checkbox.configure(state='disabled')
        extract_sentences_search_words_entry.configure(state='disabled')
        extract_sentences_search_words_var.set('')
    elif search_by_keyword_var.get() == True:
        search_by_dictionary_checkbox.configure(state='disabled')
        dictionary_button.config(state='disabled')
        selectedCsvFile_var.set('')
        keyword_value.configure(state='normal')
        extract_sentences_checkbox.configure(state='disabled')
        extract_sentences_search_words_entry.configure(state='disabled')
        extract_sentences_search_words_var.set('')
    elif extract_sentences_var.get()==True:
        search_by_dictionary_checkbox.configure(state='disabled')
        dictionary_button.config(state='disabled')
        selectedCsvFile_var.set('')
        search_by_keyword_checkbox.configure(state='disabled')
        keyword_value.configure(state='disabled')
        extract_sentences_search_words_var.set('')
        extract_sentences_search_words_entry.configure(state='normal')

search_by_dictionary_var.trace('w',activate_allOptions)
search_by_keyword_var.trace('w',activate_allOptions)
extract_sentences_var.trace('w', activate_allOptions)

activate_allOptions()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',
                'Things to do with words: Overall view': 'TIPS_NLP_Things to do with words Overall view.pdf'}
TIPS_options='English Language Benchmarks', 'Things to do with words: Overall view'

# add all the lines to the end to every special GUI
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

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, use the dropdown menu to set up the search criteria. Multiple criteria can be selected by clicking on the + button. Currently selected criteria can be displayed by clicking on the Show button.\n\nWhen running the search as case sensitive, a sentence containing the word 'King' will not be selected in output if you search for 'King')\n\nWhen lemmatizing, the scripts would search 'coming out' in all its lemmatized forms: 'coming out', 'come out', 'comes out', 'came out'.\n\nWhen searching 'Within sentence' combinations of words or collocations will be searched and displayed within SENTENCE otherwise within DOCUMENT.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to search input txt file(s) using the values contained in a csv dictionary file.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, click to select a csv file containing a list of values to be used as a dictionary for searching the input file(s).\n\nEntries in the file, one per line, can be single words or collocations, i.e., combinations of words such as 'coming out,' 'standing in line'.\n\nThe little square button to the right will allow you to open the selected csv file.\n\nThe csv filename will be displayed in the entry widget to the right.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox to search input txt file(s) by single words or collocations, i.e., combinations of words such as 'coming out,' 'standing in line'.\n\nThe widget where you can enter your words/collocations will become available once you select the option. Enter there the comma-separated words/set of words that a sentence must contain in order to be extracted from input and saved in output (e.g, coming out, standing in line, boyfriend).\n\nIn INPUT the scripts expect a single txt file or a set of txt files in a directory.\n\nIn OUTPUT the scripts generate a csv file with information about the document, sentence, word/collocation searched, and, most importantly, about the relative position where the search word appears in a document.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to extract all the sentences from your input txt file(s) that contain specific words (single words or collocations, i.e., sets of words, such as coming out, falling in love).\n\nThe widget where you can enter your words/collocations will become available once you select the option. Enter there the comma-separated words/set of words that a sentence must contain in order to be extracted from input and saved in output (e.g, coming out, standing in line, boyfriend).\n\nIn INPUT, the script expects a single txt file or a directory of txt files.\n\nIn OUTPUT the script produces two types of files:\n1. files ending with _extract_with_searchword.txt and containing, for each input file, all the sentences that have the search word(s) in them;\n2. files ending with _extract_wo_searchword.txt and containing, for each input file, the sentences that do NOT have the search word(s) in them." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, click on the button to open a GUI with more options for an N-grams/Co_occurrences VIEWER similar to Google Ngrams Viewer (https://books.google.com/ngrams) but applied to your own corpus.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1

y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="These Python 3 scripts provide various options for searching txt files for specific values."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

# a reminder is in file_manager_merger_splitter_main
#   reminders_util.checkReminder("Split output files")

def activate_NLP_options(*args):
    global error, package_basics, package, language
    error, package, parsers, package_basics, language, package_display_area_value_new, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
GUI_util.setup_menu.trace('w', activate_NLP_options)
activate_NLP_options()

if error:
    mb.showwarning(title='Warning',
               message="The config file 'NLP_default_package_language_config.csv' could not be found in the sub-directory 'config' of your main NLP Suite folder.\n\nPlease, setup next the default NLP package and language options.")
    call("python NLP_setup_package_language_main.py", shell=True)
    # this will display the correct hover-over info after the python call, in case options were changed
    error, package, parsers, package_basics, language, package_display_area_value_new, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()

title=["NLP setup options"]
message="Some of the algorithms behind this GUI rely on a specific NLP package to carry out basic NLP functions (e.g., sentence splitting, tokenizing, lemmatizing) for a specific language your corpus is written in.\n\nYour selected corpus language is " + ', '.join(language_list) + ".\nYour selected NLP package for basic functions (e.g., sentence splitting, tokenizing, lemmatizing) is " + package_basics + ".\n\nYou can always view your default selection saved in the config file NLP_default_package_language_config.csv by hovering over the Setup widget at the bottom of this GUI and change your default options by selecting Setup NLP package and corpus language."
reminders_util.checkReminder(config_filename, title, message)

GUI_util.window.mainloop()

