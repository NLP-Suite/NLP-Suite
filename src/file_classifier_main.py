# written by Roberto Franzosi October 2019, edited Spring 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_classifier_main.py",['os','tkinter','subprocess'])==False:
    sys.exit(0)

import tkinter as tk
import tkinter.messagebox as mb

import GUI_IO_util
import IO_user_interface_util
import file_classifier_date_util
import file_classifier_NER_util
import IO_files_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(input_main_dir_path, input_secondary_dir_path, output_dir_path,
        openOutputFiles,
        createExcelCharts,
        by_date_var,
        date_format,
        date_separator,
        date_position,
        date_distance_value,
        date_type,
        by_NER_var,
        similarityIndex_var):

    filesToOpen=[]

    if by_date_var==0 and by_NER_var==0:
        mb.showwarning("Warning", "No options have been selected.\n\nPlease, tick either the 'By date embedded in filenames' or 'By NER values' checkbox and try again.")
        return

    if by_date_var:
        if date_distance_value.isnumeric()==False:
            mb.showwarning("Warning", "The required 'Date distance' is expected to be a number.\n\nPlease, enter a 'Date distance' numeric value and try again.")
            return

        if date_distance_value=='':
            mb.showwarning("Warning", "The required 'Date distance' is missing.\n\nPlease, enter a 'Date distance' value and try again.")
            return

        if date_type=='':
            mb.showwarning("Warning", "The required 'Date type' value is missing.\n\nPlease, enter a 'Date type' value and try again.")
            return
        outputFiles=file_classifier_date_util.classifier(input_main_dir_path, input_secondary_dir_path, output_dir_path,openOutputFiles,
                        date_format,date_separator,date_position, date_distance_value, date_type)
        if len(outputFiles) > 0:
            filesToOpen.append(outputFiles)
    if by_NER_var:
        outputFiles=file_classifier_NER_util.main(GUI_util.window,input_main_dir_path, input_secondary_dir_path, output_dir_path, openOutputFiles, createExcelCharts, similarityIndex_var)
        if len(outputFiles)>0:
            filesToOpen.append(outputFiles)

    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running the File Classifier at', True)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.input_main_dir_path.get(),
                            GUI_util.input_secondary_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_Excel_chart_output_checkbox.get(),
                            by_date_var.get(),
                            date_format.get(),
                            date_separator_var.get(),
                            date_position_var.get(),
                            date_distance_value_var.get(),
                            date_type_var.get(),
                            by_NER_var.get(),
                            similarityIndex_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

GUI_size='1100x430'
GUI_label='Graphical User Interface (GUI) for File Classifier'
config_filename='file-classifier-config.txt'
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
config_option=[0,0,1,1,0,1]
IO_setup_display_brief=False

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

# GUI CHANGES add following lines to every special GUI
y_multiplier_integer=GUI_util.y_multiplier_integer+2
# +3 is the number of lines starting at 1 of IO widgets
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_options,config_filename, IO_setup_display_brief)


by_date_var = tk.IntVar()
date_format = tk.StringVar()
date_separator_var = tk.StringVar()
date_position_var = tk.IntVar()
date_distance_value_var=tk.StringVar()
date_type_var=tk.StringVar()
by_NER_var=tk.IntVar()
similarityIndex_var = tk.DoubleVar()

# applies to list files only
# character_count_var.set(0)
# character_count_checkbox = tk.Checkbutton(window, text='By count of character(s) embedded in filename', variable=character_count_var, onvalue=1, offvalue=0)
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+50,y_multiplier_integer, character_count_checkbox)

by_date_var.set(0)
date_format.set('mm-dd-yyyy')
date_separator_var.set('_')
date_position_var.set(2)
by_NER_var.set(0)

by_date_checkbox = tk.Checkbutton(window, text='By date embedded in filenames', variable=by_date_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer, by_date_checkbox,True)

date_format_lb = tk.Label(window,text='Date format ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+270,y_multiplier_integer, date_format_lb,True)
date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy','yyyy-mm-dd','yyyy-dd-mm','yyyy-mm','yyyy')
date_format_menu.configure(state='normal', width=10)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+350,y_multiplier_integer, date_format_menu,True)

date_separator_lb = tk.Label(window, text='Date character separator ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+210,y_multiplier_integer, date_separator_lb,True)
date_separator = tk.Entry(window, state='normal', textvariable=date_separator_var)
date_separator.configure(width=2)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+350,y_multiplier_integer, date_separator,True)

date_position_menu_lb = tk.Label(window, state='normal', text='Date position ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+400,y_multiplier_integer, date_position_menu_lb,True)
date_position_menu = tk.OptionMenu(window,date_position_var,1,2,3,4,5)
date_position_menu.configure(width=2)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+490,y_multiplier_integer, date_position_menu)

date_distance_value_lb = tk.Label(window, text='Date distance ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+270,y_multiplier_integer, date_distance_value_lb,True)

date_distance_value = tk.Entry(window, textvariable=date_distance_value_var)
date_distance_value.configure(width=4)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+350,y_multiplier_integer, date_distance_value,True)

date_type_lb = tk.Label(window, text='Date type ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+210,y_multiplier_integer, date_type_lb,True)

date_type = tk.OptionMenu(window, date_type_var, 'day', 'month','year')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+300,y_multiplier_integer, date_type)

by_NER_checkbox = tk.Checkbutton(window, text='By NER values',variable=by_NER_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer, by_NER_checkbox,True)

similarityIndex_var.set(0.25) # or 0.3
similarityIndex_menu_lb = tk.Label(window, text='Relativity index threshold ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+270,y_multiplier_integer,similarityIndex_menu_lb,True)
similarityIndex_menu = tk.OptionMenu(window,similarityIndex_var,.1,.15,.2,.25,.3,.35,.4,.45,.5,.45,.5,.55,.6,.65,.7,.75,.8,.85,.9)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+450,y_multiplier_integer,similarityIndex_menu)

TIPS_lookup = {'Classify files (By date)':'TIPS_NLP_Files classifier (By date).pdf','Classify files (By NER)':'TIPS_NLP_Files classifier (By NER).pdf', 'NER (Named Entity Recognition)':'TIPS_NLP_NER (Named Entity Recognition) Stanford CoreNLP.pdf','CoNLL Table':'TIPS_NLP_Stanford CoreNLP CoNLL table.pdf'}
TIPS_options='Classify files (By date)', 'Classify files (By NER)','NER (Named Entity Recognition)','CoNLL Table'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help", "Please, select the directory that contains the set of SOURCE unflassified documents that require classification into TARGET directories.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help", "Please, select the directory that contains the set of TARGET subdirectories.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help", GUI_IO_util.msg_outputDirectory)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*3,"Help", "Please, tick the checkbox to classify files by dates embedded in the filenames.\n\nThe script can only work if the filename embeds a date (e.g., The New York Time_2-18-1872).\n\nEnter the appropriate values for the date options.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*4,"Help", "Please, enter the number of units (e.g., 1, 2, ..., 5, ...) and select the date type from the dropdown menu (day, month, year) that you wish to consider as the date distance for classification (e.g., the SOURCE date being + or - 5 days around the dates of the TARGET filename dates).\n\nAny SOURCE file within the selected date distance will be copied to the appropriate TARGET subdirectory.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*5,"Help", "Please, tick the checkbox to classify files by social actors and Stanford CoreNLP NER values: location, date, person, organization.\n\nThe script will first build a dictionary of NER values for the documents in each subfolder, then process each unclassified document.\n\nPlease, using the dropdown menu, select a value for the similarity index. The similarity index is used to compute the degree of similarity between documents. The default value is set as 0.25. If you set a high value >.6, then fewer documents will be classified; if you set the valuue <.25 you may end up with too many repeated documents. The recommended value should be >.2 and <.4.\n\n\n\nIn INPUT the script expects 3 paths\n  path to the stanfordCoreNLP directory;\n  path to a directory containing a set of SOURCE documents to be classified;\n  path to a TARGET directory containing several folders, each folder containing a set of related documents (e.g., all describing the same event).\n\nIn OUTPUT, the script creates a csv file that provides a classification of all unclassified source documents. For documents classified as repeated (i.e., they potentially belong to several target folders), the  script marks with an * the highest value Relativity index, signaling the record as the best target.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*6,"Help", GUI_IO_util.msg_openOutputFiles)

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The Python 3 script provides a way to classify unsorted files into the proper subdirectory using either a naive approach based on dates embedded in the filenames or a more sophisticated approach based on social actors and CoreNLP NER values of location, date, person, organization.\n\nThe NER classifier \n\nThe script will first build a dictionary of NER values for the documents in each subfolder, then process each unclassified document.\n\nIn INPUT the script takes three directories:\n  1. a directory where the Stanford CoreNLP was downloaded\n  2. a main directory containing a list of SOURCE files with a date embedded in the filename;\n  3. a secondary directory containing a set of TARGET subdirectories, each with a set of files also with embedded dates.\n\nIn OUTPUT the sript produces a 2-columns csv file with: SOURCE filename; TARGET subdirectory.\n\nThe csv output file, after inspection, can be used to move the SOURCE files to the TARGET subdirectory.\n\nThe script processes each file in the SOURCE directory against each file in each sub-directory in the TARGET directory to compare embedded dates."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options, IO_setup_display_brief)

GUI_util.window.mainloop()

