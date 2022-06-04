# written by Roberto Franzosi April 2022

import GUI_util

from subprocess import call
import tkinter as tk
import os
import tkinter.messagebox as mb

import IO_files_util
import GUI_IO_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(window, inputFilename, inputDir, outputDir, extract_sentences_search_words_var):

    if extract_sentences_var:
        import sentence_analysis_util
        sentence_analysis_util.extract_sentences(window, inputFilename, inputDir, outputDir, extract_sentences_search_words_var)
        extract_sentences_search_words_var=''
        search_words_entry.configure(state='disabled')
        return

    import sample_corpus_util
    sample_corpus_util.sample_corpus_by_document_id(selectedFile, inputDir, outputDir)


#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(window, GUI_util.inputFilename.get(),
                               GUI_util.input_main_dir_path.get(),
                               GUI_util.output_dir_path.get(),
                               extract_sentences_search_words_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
GUI_label='Graphical User Interface (GUI) for ALL Data Sampling Options Available in the NLP Suite'
head, scriptName = os.path.split(os.path.basename(__file__))
IO_setup_display_brief=True
config_filename = scriptName.replace('main.py', 'config.csv')

GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=460, # height at brief display
                             GUI_height_full=540, # height at full display
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
config_input_output_numeric_options=[0,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)

extract_sentences_var = tk.IntVar()
extract_sentences_search_words_var = tk.StringVar()
selectedFile_var=tk.StringVar()

def clear(e):
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

sample_by_documentID_button = tk.Button(window, text='Sample files by Document ID in csv file',width=70,command=lambda: get_file(window,'Select INPUT csv file', [("csv files", "*.csv")]))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,sample_by_documentID_button,True)

# setup a button to open Windows Explorer on open the csv file
openFile_button = tk.Button(window, width=3, text='',
                                 command=lambda: IO_files_util.openFile(window,
                                                                        selectedFile_var.get()))

x_coordinate_hover_over = GUI_IO_util.get_labels_x_indented_coordinate()+500

y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_indented_coordinate()+500, y_multiplier_integer,
                                               openFile_button, True, False, True, False, 90, x_coordinate_hover_over, "Open selected csv file")

selectedFile_var.set('')
selectedFile=tk.Entry(window, width=90,textvariable=selectedFile_var)
selectedFile.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_indented_coordinate()+560, y_multiplier_integer,selectedFile)

def activate_options():
    search_words_entry.configure(state='normal')

extract_sentences_var.set(0)
sample_sentences_button = tk.Button(window, text='Sample files by search word(s) (extract sentences)',width=70,command=lambda: activate_options())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,sample_sentences_button,True)

y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               sample_sentences_button, True)

extract_sentences_search_words_var.set('')
search_words_entry = tk.Entry(window, textvariable=extract_sentences_search_words_var)
search_words_entry.configure(width=100, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_indented_coordinate()+500, y_multiplier_integer,
                                               search_words_entry)

sample_sentences_by_documentID_button = tk.Button(window, text='Sample sentences by Document ID and other fields values in csv file (Open GUI)',width=70,command=lambda: call("python data_manager_main.py", shell=True))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,sample_sentences_by_documentID_button)

sample_by_date_button = tk.Button(window, text='Sample files by date in filename',width=70,command=lambda: option_not_available())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,sample_by_date_button)

export_csv_field_GUI_button = tk.Button(window, text='Export csv field content in csv file to csv/txt file (Open GUI)',width=70,command=lambda: call("python data_manager_main.py", shell=True))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,export_csv_field_GUI_button)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'No TIPS available':''}
TIPS_options='No TIPS available'

# add all the lines lines to the end to every special GUI
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
                                  "Please, click on the button to sample your corpus by copying the files listed under 'Document' in a csv file.\nAfter clicking the button you will be prompted to select the input scv file. After selecting the csv file, you can clisk on the little button to open the file for inspection.\n\nIn INPUT the function expects:\n   1. a directory containing the files to be sampled; the directory is selected above in the INPUT/OUTPUT configuration;\n   2. a csv file containing a list of documents under the header 'Document' that will be used to sample; this csv file can be generated in a number of ways, e.g., using the 'Data Manager' GUI with the option to 'Extract field(s) from csv file' in a file generated by any of the NLP Suite scripts.\n\nIn OUTPUT the function will copy the sampled files to a sub-folder of the input folder.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, click on the button to extract sentences from file(s) by the value specific words/collocations in the sentences.\nAfter clicking the button the data entry widget will be become available. You can enter there, the comma separated list of strings to be used to search the input text file(s) and export all the sentences where the search strings were found.\n\nIn INPUT the function takes the txt file(s) listed in the Setup I/O configuration widget.\n\nIn OUTPUT the function will create a 'sentences_' subdirectory of the output directory with two further subdirectories: extract and extract_minus. The two subdirectories contain, respectively, the same input file(s) with only the sentences that match the search string(s) (extract) and the the sentences that do NOT match the search string(s) (extract_minus).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, click on the button to open the Data Manager GUI for extracting data from inut file(s) in a variety of ways.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, click on the button to sample your corpus by dates embedded in the filename.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, click on the button to open the GUI for extracting field(s) from a csv file and exporting content to a csv or txt files.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),0)

# change the value of the readMe_message
readMe_message="The GUI allows you to access various functions for sampling your data (your corpus in particular)."
readMe_command = lambda: GUI_IO_util.display_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()

