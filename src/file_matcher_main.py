# Written by Roberto Franzosi December 2019

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_matcher.py",['csv','tkinter','os'])==False:
    sys.exit(0)

import tkinter as tk
import IO_user_interface_util
import file_matcher_util
import GUI_IO_util

# RUN section ______________________________________________________________________________________________________________________________________________________


def run(inputPath, outputPath, selectedCsvFile_var, openOutputFiles, create_Excel_chart_output, find_var, source_extension_var, target_extension_var, matching_var, copy_var, move_var, character_value, number_of_items):

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running File Matcher at', True, 'You can follow the script in command line.')

    file_matcher_util.run_default(GUI_util.window, [inputPath], outputPath, selectedCsvFile_var, openOutputFiles, matching_var, source_extension_var, target_extension_var, copy_var, move_var, character_value, number_of_items)

    # output_filename=''
    # i=0
    # fieldnames = []
    # currentSubfolder=os.path.basename(os.path.normpath(inputPath))

    # For cases where matching files beginning with a dot (.); like files in the current directory or hidden files on Unix based system, use the os.walk
    # import glob
    # include_subdir_var
    # for filename in glob.iglob(inputPath + os.sep+ '*.'+by_file_type_var, recursive=True):
    #      print(filename)

    # root: Current path which is "walked through"
    # subdirs: Files in root of type directory
    # files: Files in current root (not in subdirs) of type other than directory

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running File matcher at', True, '', True, startTime)

    # if i > 0:
    # 	mb.showwarning(title='File matcher', message=str(i) + ' files have been matched.')
    # 	filesToOpen=[]
    # 	filesToOpen.append(os.path.join(outputPath,output_filename))
    # 	IO_util.OpenOutputFiles(GUI_util.window,True,filesToOpen)
    # else:
    # 	mb.showwarning(title='File matcher', message='No files have been matched.')

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
# noi = file_filename_matcher_GUI.number_of_items_value.get()
# print("Number of items: ", noi)
# print("Type: ", type(file_filename_matcher_GUI.number_of_items_var.get()))
run_script_command=lambda: run(GUI_util.input_main_dir_path.get(),
                               GUI_util.output_dir_path.get(),
                               selectedCsvFile_var.get(),
                               GUI_util.open_csv_output_checkbox.get(),
                               GUI_util.create_Excel_chart_output_checkbox.get(),
                               find_var.get(),
                               source_file_type_menu_var.get(),
                               target_file_type_menu_var.get(),
                               matching_var.get(),
                               copy_var.get(),
                               move_var.get(),
                               character_value_var.get(),
                               number_of_items_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_width=GUI_IO_util.get_GUI_width(2)
GUI_height=430 # height of GUI with full I/O display

if IO_setup_display_brief:
    GUI_height = GUI_height - 40
    y_multiplier_integer = GUI_util.y_multiplier_integer  # IO BRIEF display
    increment=0 # used in the display of HELP messages
else: # full display
    # GUI CHANGES add following lines to every special GUI
    # +3 is the number of lines starting at 1 of IO widgets
    # y_multiplier_integer=GUI_util.y_multiplier_integer+2
    y_multiplier_integer = GUI_util.y_multiplier_integer + 1  # IO FULL display
    increment=1

GUI_size = str(GUI_width) + 'x' + str(GUI_height)

GUI_label='Graphical User Interface (GUI) for File Matcher'
config_filename='file-matcher-config.txt'
# The 6 values of config_option refer to: 
#	software directory
#   input file
        # 1 for CoNLL file 
        # 2 for TXT file 
        # 3 for csv file 
        # 4 for any type of file
        # 5 for txt or html
        # 6 for txt or csv
#	input dir
#	input secondary dir
#	output file
#	output dir
config_option=[0,0,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_options,config_filename,IO_setup_display_brief)

selectedCsvFile_var=tk.StringVar()
find_var=tk.IntVar()
source_file_type_menu_var=tk.StringVar()
target_file_type_menu_var=tk.StringVar()
matching_var=tk.IntVar()
#by_embedded_items_var=tk.IntVar()
character_value_var=tk.StringVar()
number_of_items_var=tk.IntVar()
include_exclude_var=tk.IntVar()
copy_var=tk.IntVar()
move_var=tk.IntVar()


def clear(e):
    source_file_type_menu_var.set('')
    target_file_type_menu_var.set('')
    GUI_util.tips_dropdown_field.set('Open TIPS files')
window.bind("<Escape>", clear)

def get_additional_csvFile(window,title,fileType):
    import os
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)
    if len(filePath)>0:
        selectedCsvFile.config(state='normal')
        selectedCsvFile_var.set(filePath)

# add_file_button = tk.Button(window, text='csv file', width=2,height=1,state='disabled',command=lambda: get_additional_csvFile(window,'Select INPUT csv file', [("csv files", "*.csv")]))
add_file_button = tk.Button(window, text='csv file', command=lambda: get_additional_csvFile(window,'Select INPUT csv file', [("csv files", "*.csv")]))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,add_file_button,True)

selectedCsvFile = tk.Entry(window,width=70,state='disabled',textvariable=selectedCsvFile_var)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+100,y_multiplier_integer,selectedCsvFile)

find_var.set(1)
find_checkbox = tk.Checkbutton(window, text='Match files', variable=find_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer, find_checkbox,True)

source_file_type_menu_lb = tk.Label(window, text='Source file type ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+110,y_multiplier_integer,source_file_type_menu_lb,True)
source_file_type_menu = tk.OptionMenu(window,source_file_type_menu_var,'*','bmp','csv','doc','docx','gexf','html','jpg','kml','pdf','png','tif','txt','xls','xlsm','xlsx')
source_file_type_menu.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+220,y_multiplier_integer,source_file_type_menu,True)

target_file_type_menu_lb = tk.Label(window, text='Target file type ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+330,y_multiplier_integer,target_file_type_menu_lb,True)
target_file_type_menu = tk.OptionMenu(window,target_file_type_menu_var,'*','bmp','csv','doc','docx','gexf','html','jpg','kml','pdf','png','tif','txt','xls','xlsm','xlsx')
target_file_type_menu.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+440,y_multiplier_integer,target_file_type_menu)

matching_var.set(1)
matching_checkbox = tk.Checkbutton(window, variable=matching_var, onvalue=1, offvalue=0, command=lambda: GUI_util.trace_checkbox_NoLabel(matching_var, matching_checkbox, "Exact match", "Partial match (by number of embedded items)"))
matching_checkbox.config(text="Exact match")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,matching_checkbox,True)

character_value_var.set('_')
character_lb = tk.Label(window, text='Separator character(s)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+370,y_multiplier_integer, character_lb,True)
character_value = tk.Entry(window, width=2,textvariable=character_value_var)
character_value.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+520,y_multiplier_integer, character_value,True)

number_of_items_lb = tk.Label(window, text='Number of items')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+560,y_multiplier_integer, number_of_items_lb,True)
number_of_items_value = tk.Entry(window, width=2,textvariable=number_of_items_var)
number_of_items_value.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+670,y_multiplier_integer, number_of_items_value,True)

include_exclude_var.set(1)
include_exclude_checkbox = tk.Checkbutton(window, variable=include_exclude_var, onvalue=1, offvalue=0, command=lambda: GUI_util.trace_checkbox_NoLabel(include_exclude_var, include_exclude_checkbox, "Include first # items only", "Exclude first # items"))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+760,y_multiplier_integer, include_exclude_checkbox)
include_exclude_checkbox.config(text='Include first # items only',state="disabled")

copy_var.set(0)
copy_checkbox = tk.Checkbutton(window, variable=copy_var, onvalue=1, offvalue=0)
copy_checkbox.config(text="COPY processed files")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,copy_checkbox,True)

move_var.set(0)
move_checkbox = tk.Checkbutton(window, variable=move_var, onvalue=1, offvalue=0)
move_checkbox.config(state='disabled',text="MOVE processed files")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+200,y_multiplier_integer,move_checkbox)

def activate_options(*args):
    copy_checkbox.config(state='normal')
    move_checkbox.config(state='normal')
    if copy_var.get()==True:
        move_checkbox.config(state='disabled')
        move_var.set(0)
    if move_var.get()==True:
        copy_checkbox.config(state='disabled')
        copy_var.set(0)
        # TODO need to set move_var.set(0)
        #	but the question gets repeated twice
        # command = mb.askyesno("MOVE files", "You have selected to MOVE any mathed files from the INPUT directory to the OUTPUT directory?\n\nAre you sure you want to do that? Matched files will be removed from their original locations.",default='no')
        # if command==False:
        # 	move_var.set(0)
        # 	copy_checkbox.config(state='normal')
copy_var.trace('w',activate_options)
move_var.trace('w',activate_options)

def activate_find_options(*args):
    source_file_type_menu_var.set('*')
    target_file_type_menu_var.set('*')
    if find_var.get()==True:
        source_file_type_menu.configure(state="normal")
        target_file_type_menu.configure(state="normal")
        # currently the matcher only works with exact match
        # need to use a csv file for partial matches
        # matching_checkbox.config(text="Exact match",state='normal')
        matching_checkbox.config(text="Exact match",state='normal')
        matching_var.set(1)
    else:
        source_file_type_menu.configure(state="disabled")
        target_file_type_menu.configure(state="disabled")
        matching_var.set(1)
        matching_checkbox.config(text="Exact match",state='disabled')
find_var.trace('w',activate_find_options)

activate_find_options()

def activate_numberEmbeddedItems_options(*args):
    character_value_var.set('_')
    number_of_items_var.set(0)
    if matching_var.get()==1:
        character_value.configure(state="disabled")
        number_of_items_value.configure(state="disabled")
        include_exclude_checkbox.config(state="disabled")
    else:
        character_value.configure(state="normal")
        number_of_items_value.configure(state="normal")
        include_exclude_checkbox.config(state="normal")
matching_var.trace('w',activate_numberEmbeddedItems_options)
activate_numberEmbeddedItems_options()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'File manager':'TIPS_NLP_File manager.pdf','File handling in NLP Suite': "TIPS_NLP_File handling in NLP Suite.pdf",'Filename checker':'TIPS_NLP_Filename checker.pdf','Filename matcher':'TIPS_NLP_Filename matcher.pdf','File classifier (By date)':'TIPS_NLP_File classifier (By date).pdf','File classifier (By NER)':'TIPS_NLP_File classifier (By NER).pdf','File content checker & converter':'TIPS_NLP_File checker & converter.pdf','Text encoding (utf-8)':'TIPS_NLP_Text encoding (utf-8).pdf','Spelling checker':'TIPS_NLP_Spelling checker.pdf','File merger':'TIPS_NLP_File merger.pdf','File splitter':'TIPS_NLP_File splitter.pdf'}
TIPS_options= 'Filename matcher','File handling in NLP Suite','File manager', 'Filename checker', 'File classifier (By date)','File classifier (By NER)','File content checker & converter','Text encoding (utf-8)','Spelling checker','File merger','File splitter'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    if not IO_setup_display_brief:
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help", GUI_IO_util.msg_csvFile)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help", GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment + 1),"Help", "Please, click to select a csv file containing a list of filenames to be used for finding matches.\n\nTHIS IS PARTICULARLY USEFUL IF YOU WANT TO PROCESS PARTIAL MATCHES, since currently the partial match option is not available. TO GENERATE A LIST OF FILES FOR PARTIAL MATCH USE THE FILE_MANAGER_MAIN.PY, WITH THE LIST OPTION AND THE FILTER 'By number of embedded items'.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment + 2),"Help", "Please, tick the checkbox to use the script 'Match files'.\n\nThe script identifies files having the same filename and different extensions (e.g., The Atlanta Journal_3-12-1956_4_2.pdf and The Atlanta Journal_3-12-1956_8_2.txt). All subdirectories of a selected directory will be searched for a selected pair of source and target extensions (e.g., pdf and docx).\n\nThe script is very useful, for instance, for identifying pdf files that have been manually transcribed (or automatically converted) to doc/docx or txt format. But it can be used more generally to identify files with the same filename and different extensions.\n\nUsing * * for both source and target will identify any file with the same exact filename and different extensions of any type.\n\nYou can select to match files with an exact match with the baseline filename (e.g., The Atlanta Journal_3-12-1956_8_2), or with a partial match (e.g., only the first two items in the filenames, The Atlanta Journal_3-12-1956).")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment + 3),"Help", "Please, tick the checkbox to find files with an exact match with the SOURCE filename (e.g., The Atlanta Journal_3-12-1956_8_2), or with a partial match (e.g., only the first two items in the filenames, The Atlanta Journal_3-12-1956).\n\nFor a partial match you will need to enter the character separating items (e.g., _) and the number of items (e.g., 2) and whether you want to include only the first # items.\n\nTHE OPTION IS CURRENTLY DISABLED AND ONLY THE EXACT MATCH WORKS.\n\nIF YOU WANT TO PROCESS PARTIAL MATCHES, YOU NEED TO USE AN INPUT CSV FILE WITH A LIST OF FILES FOR PARTIAL MATCH. TO GENERATE THE CSV FILE, USE THE FILE_MANAGER_MAIN.PY, WITH THE LIST OPTION AND THE FILTER 'By number of embedded items'.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment + 4),"Help", "Please, tick one or the other checkboxes to COPY or MOVE the matched files from the INPUT directory to the OUTPUT directory.\n\nIn the OUTPUT directory, will create a new sub-directory 'file_matcher_OUTPUT' (any previous 'file_matcher_OUTPUT' subdirectory will be overwritten). Inside this sub-directory, three sub-directories will be created: matched, unmatched, duplicates where matched, unmatched, and duplicate files will be copied/moved.\n\nLeave the checkboxes unticked if you just want to get a list of files.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment + 5),"Help", GUI_IO_util.msg_openOutputFiles)

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The Python 3 script allows you to find matches between any SOURCE file of a selected type (e.g., pdf) and TARGET files with the same filename but same/different type (e.g., docx).\n\nThe script is very useful, for instance, for identifying pdf files that have been manually transcribed (or automatically converted) to doc/docx or txt format. But it can be used more generally to identify files with the same filename and different extensions."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief)

GUI_util.window.mainloop()

