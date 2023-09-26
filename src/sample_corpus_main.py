# written by Roberto Franzosi April 2022

import GUI_util

from subprocess import call
import tkinter as tk
import os
import tkinter.messagebox as mb

import config_util
import IO_files_util
import GUI_IO_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(window, inputFilename, inputDir, outputDir, selectedFile,
            openOutputFiles,
            createCharts,
            chartPackage,
            sample_by_documentID,
            sample_by_date, date_menu, comparator, date_distance_value, date_type,
            sample_by_keywords_inFilename,
            keywords_inFilename,
            sample_by_keywords_inDocument,
            keywords_inDocument):

    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    else:
        config_filename = scriptName.replace('_main.py', '_config.csv')

    outputDir = os.path.join(inputDir, 'subcorpus_search')

    # # get the date options from filename
    # filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = config_util.get_date_options(
    #     config_filename, config_input_output_numeric_options)

    if sample_by_keywords_inFilename:
        if keywords_inFilename=='':
            mb.showwarning(title='Warning',message='You have selected the option of creating a subcorpus of the input files based on search words found in the filenames, but no search words have been entered.\n\nPlease, enter the search words that a filename must contain and try again.')
            return
        import sample_corpus_util
        sample_corpus_util.sample_corpus_by_search_words_inFileName(window, inputDir, config_filename, keywords_inFilename)
    elif sample_by_keywords_inDocument:
        if keywords_inDocument=='':
            mb.showwarning(title='Warning',message='You have selected the option of creating a subcorpus of the input files based on search words foound in the input documents, but no search words have been entered.\n\nPlease, enter the search words that documents must contain and try again.')
            return

        import file_search_byWord_util
        outputDir = os.path.join(inputDir, 'subcorpus_search')

        filesToOpen = file_search_byWord_util.search_sentences_documents(inputFilename,inputDir,outputDir,config_filename,
                                              search_by_dictionary=False, search_by_search_keywords=True,
                                              search_keywords_list=keywords_inDocument,
                                              create_subcorpus_var=True, search_options_list=[], lang='English',
                                              createCharts=createCharts, chartPackage=chartPackage)
    else:
        mb.showwarning(title='Warning',message='The selected option is not available yet. Please, check back soon.\n\nSorry!')
        return

    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

    # sample_corpus_util.sample_corpus_by_document_id(selectedFile, inputDir, outputDir)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(window, GUI_util.inputFilename.get(),
                               GUI_util.input_main_dir_path.get(),
                               GUI_util.output_dir_path.get(),
                               selectedFile.get(),
                               GUI_util.open_csv_output_checkbox.get(),
                               GUI_util.create_chart_output_checkbox.get(),
                               GUI_util.charts_package_options_widget.get(),
                               sample_by_documentID_var.get(),
                               sample_by_date_var.get(),
                               date_menu_var.get(),
                               comparator_var.get(),
                               date_distance_value_var.get(),
                               date_type_var.get(),
                               sample_by_keywords_inFilename_var.get(),
                               keywords_inFilename_var.get(),
                               sample_by_keywords_inDocument_var.get(),
                               keywords_inDocument_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
GUI_label='Graphical User Interface (GUI) for Sampling a Corpus of Files'
config_filename = 'NLP_default_IO_config.csv'
head, scriptName = os.path.split(os.path.basename(__file__))

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
config_input_output_numeric_options=[0,1,0,1]

IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=460, # height at brief display
                             GUI_height_full=540, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2) # to be added for full display

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

selectedFile_var = tk.StringVar()

def clear(e):
    selectedFile_var.set('')
    date_menu_var.set('')
    comparator_var.set('')
    date_value_var.set('')
    date_value=''
    keywords_inFilename_var.set('')
    keywords_inDocument_var.set('')

    GUI_util.clear("Escape")
window.bind("<Escape>", clear)


#setup GUI widgets

def option_not_available():
    mb.showwarning(title='Warning',
                   message='The selected option is not available yet.\n\nSorry!')

def get_file(window,title,fileType):
    selectedFile_var.set('')
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)
    if len(filePath)>0:
        selectedFile_var.set(filePath)

y_multiplier_integer= y_multiplier_integer +.5

# corpus_sampling_lb = tk.Label(window, text='Sampling corpus of files in a directory')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
#                                                corpus_sampling_lb)

sample_by_documentID_var = tk.IntVar()
sample_by_documentID_checkbox = tk.Checkbutton(window, text='Sample files by Document ID', variable=sample_by_documentID_var,
                                    onvalue=1, command=lambda:activate_all_options())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   sample_by_documentID_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox if you wish to sample your corpus by Document Ids contained in a csv file (csv file created by one of the NLP Suite algorithms)")

sample_by_documentID_button = tk.Button(window, text='Select csv file',width=GUI_IO_util.widget_width_extra_short,command=lambda: get_file(window,'Select INPUT csv file', [("csv files", "*.csv")]))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               sample_by_documentID_button, True, False, True, False, 90,
                                               GUI_IO_util.IO_configuration_menu, "Click on the button to select the input csv file")

# setup a button to open Windows Explorer on open the csv file
openFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                 command=lambda: IO_files_util.openFile(window,
                                                                        selectedFile_var.get()))

x_coordinate_hover_over = GUI_IO_util.labels_x_indented_coordinate+500

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate, y_multiplier_integer,
                                               openFile_button, True, False, True, False, 90, GUI_IO_util.setup_pop_up_text_widget, "Open selected csv file")

selectedFile_var.set('')
selectedFile=tk.Entry(window, width=GUI_IO_util.widget_width_medium,textvariable=selectedFile_var)
selectedFile.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate+80, y_multiplier_integer,selectedFile)

sample_by_date_var = tk.IntVar()
sample_by_date_checkbox = tk.Checkbutton(window, text='Sample files by date in filename', variable=sample_by_date_var,
                                    onvalue=1, command=lambda:activate_all_options())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   sample_by_date_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox if you wish to sample your corpus by dates embedded in the filename"
                                   "\nThe date options (format, item separator, and position in filename; e.g., New York Time_4_12-21-1982) are set in the Setup INPUT/OUTPUT configuration")

# date_format_lb = tk.Label(window,text='Format ')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate,y_multiplier_integer, date_format_lb, True)
#
# date_format_var = tk.StringVar()
# date_format_var.set('mm-dd-yyyy')
# date_format_menu = tk.OptionMenu(window, date_format_var, 'mm-dd-yyyy', 'dd-mm-yyyy','yyyy-mm-dd','yyyy-dd-mm','yyyy-mm','yyyy')
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,
#                                                GUI_IO_util.date_format_coordinate,
#                                                y_multiplier_integer,
#                                                date_format_menu,
#                                                True, False, False, False, 90,
#                                                GUI_IO_util.date_format_coordinate,
#                                                'Select the date type embedded in your filename')
#
# items_separator_var = tk.StringVar()
# items_separator_var.set('_')
# date_separator_lb = tk.Label(window, text='Character separator ')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.date_char_sep_lb_coordinate,
#                                                y_multiplier_integer, date_separator_lb, True)
#
# date_separator = tk.Entry(window, textvariable=items_separator_var, width=3)
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,
#                                                GUI_IO_util.open_setup_x_coordinate,
#                                                y_multiplier_integer,
#                                                date_separator,
#                                                True, False, False, False, 90,
#                                                GUI_IO_util.open_TIPS_x_coordinate,
#                                                'Enter the character that separate items embedded in filename (default _)\nIn New York Time_01-15-1999_4_3, _ is the character separating the 3 items embedded in filename: newspaper name, date, page number, column number')
#
# date_position_menu_lb = tk.Label(window, text='Position ')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.date_position_lb_coordinate,
#                                                y_multiplier_integer, date_position_menu_lb, True)
#
# date_position_var = tk.StringVar()
# date_position_var.set(2)
# date_position_menu = tk.OptionMenu(window,date_position_var,1,2,3,4,5)
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,
#                                                GUI_IO_util.date_position_coordinate,
#                                                y_multiplier_integer,
#                                                date_position_menu,
#                                                False, False, False, False, 90,
#                                                GUI_IO_util.open_reminders_x_coordinate,
#                                                'Select the date position in the filename, starting with 1 if the date is the first item in the filename\nIn New York Time_01-15-1999_4_3, 2 is the date position as the second embedded item')

where_lb = tk.Label(window, text='WHERE clause')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               where_lb, True)

date_menu_var = tk.StringVar()
date_values = ['Entire date', 'month', 'day', 'year']

date_menu = tk.OptionMenu(window, date_menu_var, *date_values)  # , command=lambda:extractSelection()
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,
                                               GUI_IO_util.IO_configuration_menu + 100,
                                               y_multiplier_integer,
                                               date_menu,
                                               True, False, False, False, 90,
                                               GUI_IO_util.IO_configuration_menu + 100,
                                               'Select the date value to be used for filtering files by date')

comparator_var = tk.StringVar()
comp_menu_values = ['<>', '=', '>', '>=', '<', '<=']
##
# select_csv_field_extract_menu = tk.OptionMenu(window, select_csv_field_extract_var, *menu_values, command=lambda:activate_csv_fields_selection('extract', extract_var.get(), False, False))
comparator_menu = tk.OptionMenu(window, comparator_var, *comp_menu_values)  # , command=lambda:extractSelection()
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,
                                               GUI_IO_util.setup_IO_brief_coordinate,
                                               y_multiplier_integer,
                                               comparator_menu,
                                               True, False, False, False, 90,
                                               GUI_IO_util.IO_configuration_menu + 200,
                                               'Select the comparator operator to be used in filtering files by date')

date_value_var = tk.StringVar()
date_value_var.set('')
date_value = tk.Entry(window,width=GUI_IO_util.widget_width_medium,textvariable=date_value_var)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate+80, y_multiplier_integer,
                    date_value, False, False, True, False,
                    90, GUI_IO_util.date_char_sep_lb_coordinate,
                    "Enter the date value to be used in filtering files by date (e.g., 1995, 12-11-1898)")

date_distance_value_lb = tk.Label(window, text='Date distance ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,y_multiplier_integer, date_distance_value_lb,True)

date_distance_value_var=tk.StringVar()
date_distance_value = tk.Entry(window, textvariable=date_distance_value_var)
date_distance_value.configure(width=4)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu+100, y_multiplier_integer,
                    date_distance_value, True, False, True, False,
                    90, GUI_IO_util.IO_configuration_menu+100,
                    "Enter the distance as an integer value to be used in computing the distance between dates (e.g., 1, 6 for a distance of 1 or 6 day/month/year)")

date_type_lb = tk.Label(window, text='Date type ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate+210,y_multiplier_integer, date_type_lb,True)

date_type_var=tk.StringVar()
date_type = tk.OptionMenu(window, date_type_var, 'day', 'month','year')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate+300, y_multiplier_integer,
                    date_type, False, False, True, False,
                    90, GUI_IO_util.IO_configuration_menu+100,
                    "Select the date type to be used to compute the date distance (e.g., month)")

sample_by_keywords_inFilename_var = tk.IntVar()
sample_by_keywords_inFilename_checkbox = tk.Checkbutton(window, text='Sample files by string in filename', variable=sample_by_keywords_inFilename_var,
                                    onvalue=1, command=lambda:activate_all_options())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   sample_by_keywords_inFilename_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox if you wish to sample your corpus by a string contained in the filename (NOT THE DOCUMENT CONTENT)")

keywords_inFilename_var = tk.StringVar()
keywords_inFilename_var.set('')
keywords_inFilename_value = tk.Entry(window,width=GUI_IO_util.widget_width_long,textvariable=keywords_inFilename_var)

y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                    keywords_inFilename_value, False, False, True, False,
                    90, GUI_IO_util.watch_videos_x_coordinate,
                    "Enter the comma-separated, case-sensitive words/set of words that a FILENAME (NOT DOCUMENT CONTENT) must contain")

sample_by_keywords_inDocument_var = tk.IntVar()
sample_by_keywords_inDocument_var.set(0)
sample_by_keywords_inDocument_checkbox = tk.Checkbutton(window, text='Sample corpus by search word(s)', variable=sample_by_keywords_inDocument_var, onvalue=1, offvalue=0, command=lambda:activate_all_options())
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                    sample_by_keywords_inDocument_checkbox, True, False, True, False,
                    90, GUI_IO_util.labels_x_coordinate,
                    "Tick the checkbox to sample your corpus by word(s) contained in your document(s) (NOT THE FILENAME) (e.g, coming out, standing in line, boyfriend)")

keywords_inDocument_var = tk.StringVar()
keywords_inDocument_var.set('')
keywords_inDocument_value = tk.Entry(window,width=GUI_IO_util.widget_width_long,textvariable=keywords_inDocument_var)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                    keywords_inDocument_value, False, False, True, False,
                    90, GUI_IO_util.watch_videos_x_coordinate,
                    "Enter the comma-separated, case-sensitive words/set of words that a DOCUMENT (NOT FILENAME) must contain (e.g, coming out, standing in line, boyfriend).")

def activate_all_options():
    sample_by_documentID_checkbox.configure(state='normal')
    sample_by_date_checkbox.configure(state='normal')
    sample_by_keywords_inFilename_checkbox.configure(state='normal')
    sample_by_keywords_inDocument_checkbox.configure(state='normal')

    sample_by_documentID_button.configure(state="disabled")
    openFile_button.configure(state="disabled")
    selectedFile.configure(state="disabled")

    # date_format_menu.configure(state="disabled")
    # date_separator.configure(state="disabled")
    # date_position_menu.configure(state="disabled")
    date_menu.configure(state="disabled")
    comparator_menu.configure(state="disabled")
    date_value.configure(state="disabled")

    keywords_inFilename_value.configure(state="disabled")

    keywords_inDocument_value.configure(state="disabled")

    if sample_by_documentID_var.get():
        sample_by_documentID_button.configure(state="normal")
        openFile_button.configure(state="normal")
        selectedFile.configure(state="normal")

        # sample_by_documentID_checkbox.configure(state='disabled')
        sample_by_date_checkbox.configure(state='disabled')
        sample_by_keywords_inFilename_checkbox.configure(state='disabled')
        sample_by_keywords_inFilename_checkbox.configure(state='disabled')

        date_value_var.set('')
        keywords_inFilename_var.set('')
        keywords_inDocument_var.set('')

    elif sample_by_date_var.get():
        # date_format_menu.configure(state="normal")
        # date_separator.configure(state="normal")
        # date_position_menu.configure(state="normal")
        date_menu.configure(state="normal")
        comparator_menu.configure(state="normal")
        date_value.configure(state="normal")

        sample_by_documentID_checkbox.configure(state='disabled')
        # sample_by_date_checkbox.configure(state='disabled')
        sample_by_keywords_inFilename_checkbox.configure(state='disabled')
        sample_by_keywords_inDocument_checkbox.configure(state='disabled')

        selectedFile_var.set('')
        keywords_inFilename_var.set('')
        keywords_inDocument_var.set('')

    elif sample_by_keywords_inFilename_var.get():
        keywords_inFilename_value.configure(state="normal")

        sample_by_documentID_checkbox.configure(state='disabled')
        sample_by_date_checkbox.configure(state='disabled')
        # sample_by_keywords_inFilename_var.configure(state='disabled')
        sample_by_keywords_inDocument_checkbox.configure(state='disabled')

        selectedFile_var.set('')
        date_value_var.set('')
        keywords_inDocument_var.set('')

    elif sample_by_keywords_inDocument_var.get():
        keywords_inDocument_value.configure(state="normal")

        sample_by_documentID_checkbox.configure(state='disabled')
        sample_by_date_checkbox.configure(state='disabled')
        sample_by_keywords_inFilename_checkbox.configure(state='disabled')
        # search_by_keyword_checkbox.configure(state='disabled')

        selectedFile_var.set('')
        date_value_var.set('')
        keywords_inFilename_var.set('')

activate_all_options()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'No TIPS available':''}
TIPS_options='No TIPS available'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", inputFileMsg+GUI_IO_util.msg_openFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", inputDirTXTCSVMsg+GUI_IO_util.msg_openExplorer)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = y_multiplier_integer +.5

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, tick the checkbox to sample your corpus by copying the files listed under 'Document ID' in a csv file.\nAfter clicking the button you will be prompted to select the input scv file. After selecting the csv file, you can clisk on the little button to open the file for inspection.\n\nIn INPUT the function expects:\n   1. a directory containing the files to be sampled; the directory is selected above in the INPUT/OUTPUT configuration;\n   2. a csv file containing a list of documents under the header 'Document' that will be used to sample; this csv file can be generated in a number of ways, e.g., using the 'Data manipulation' GUI with the option to 'Extract field(s) from csv file' in a file generated by any of the NLP Suite scripts.\n\nIn OUTPUT the function will copy the sampled files to a sub-folder of the input folder.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, tick the checkbox to sample your corpus by dates embedded in the filename. Once available, enter the various options for filtering your corpus by date (format, date separator character(s), date position in filename (e.g., in the filename New York Time_4_12-21-1982, the date position is 3, the date separator character _, and the date format is mm-dd-yyyy) .\n\nThe date options are set by clicking the 'Setup INPUT/OUTPUT configuration' button at the top of this GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, enter the number of units (e.g., 1, 2, ..., 5, ...) and select the date type from the dropdown menu (day, month, year) that you wish to consider as the date distance for classification (e.g., the SOURCE date being + or - 5 days around the dates of the TARGET filename dates).\n\nAny SOURCE file within the selected date distance will be copied to the appropriate TARGET subdirectory.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, tick the checkbox to sample your corpus by specific word(s) in the input filename (NOT file content) (e.g., 'The New York Times' in a corpus of articles from many different newspapers)." \
                                    "\n\nIn INPUT the scripts expect a set of txt files in a directory." \
                                    "\n\nIn OUTPUT the algorithm will export all the txt files that contain the search words to a directory called 'subcorpus_search' inside the input directory. It will also generate a csv file with information about the document, sentence, word/collocation searched, and, most importantly, about the relative position where the search word appears in a document.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, tick the checkbox to sample your corpus by specific word(s) contained in the input documents (NOT filenames)." \
                                    "\n\nIn INPUT the scripts expect a set of txt files in a directory." \
                                    "\n\nIn OUTPUT the algorithm will export all the txt files that contain the search words to a directory called 'subcorpus_search' inside the input directory. It will also generate a csv file with information about the document, sentence, word/collocation searched, and, most importantly, about the relative position where the search word appears in a document.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The GUI allows you to access various functions for sampling your corpus."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

# get the date options from filename
filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = config_util.get_date_options(
    config_filename, config_input_output_numeric_options)

GUI_util.window.mainloop()

