# Written by Roberto Franzosi December 2019

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"file_matcher.py",['csv','tkinter','os'])==False:
    sys.exit(0)

import os
import tkinter as tk
import IO_user_interface_util
import file_matcher_util
import GUI_IO_util
import IO_files_util

# RUN section ______________________________________________________________________________________________________________________________________________________


def run(inputPath, outputPath, selectedCsvFile_var, openOutputFiles, createCharts, chartPackage, find_var, source_extension_var, target_extension_var, matching_var, copy_var, move_var, character_value, number_of_items):

    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running File Matcher at',
                                                 True, '', True, '', False)

    file_matcher_util.run_default(GUI_util.window, [inputPath], outputPath, selectedCsvFile_var, openOutputFiles, matching_var, source_extension_var, target_extension_var, copy_var, move_var, character_value, number_of_items)

    # outputFilename=''
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

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running File matcher at', True, '', True, startTime, False)

    # if i > 0:
    # 	mb.showwarning(title='File matcher', message=str(i) + ' files have been matched.')
    # 	filesToOpen=[]
    # 	filesToOpen.append(os.path.join(outputPath,outputFilename))
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
                               GUI_util.create_chart_output_checkbox.get(),
                               GUI_util.charts_package_options_widget.get(),
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
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=400, # height at brief display
                             GUI_height_full=440, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=1, # to be added for full display
                             increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for File Matcher'
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = scriptName.replace('_main.py', '_config.csv')

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
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

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
    selectedCsvFile_var.set('')
    source_file_type_menu_var.set('')
    target_file_type_menu_var.set('')
    GUI_util.tips_dropdown_field.set('Open TIPS files')
window.bind("<Escape>", clear)

def add_csvFile(window,title,fileType):
    import os
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)
    if len(filePath)>0:
        selectedCsvFile.config(state='normal')
        selectedCsvFile_var.set(filePath)

add_file_button = tk.Button(window, text='Select csv file', command=lambda: add_csvFile(window,'Select INPUT csv file', [("csv files", "*.csv")]))
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer, add_file_button,
    True, False, True, False, 90, GUI_IO_util.labels_x_coordinate, "Click on the button to select the csv file to be used to find file matches")

openInputFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, selectedCsvFile_var.get()))
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.file_matcher_openInputFile_button_pos, y_multiplier_integer,openInputFile_button,
    True, False, True, False, 90, GUI_IO_util.file_matcher_openInputFile_button_pos, "Open INPUT csv file")

selectedCsvFile = tk.Entry(window,width=GUI_IO_util.widget_width_extra_long,state='disabled',textvariable=selectedCsvFile_var)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.file_matcher_selectedCsvFile_pos,y_multiplier_integer,selectedCsvFile)

find_var.set(1)
find_checkbox = tk.Checkbutton(window, text='Match files', variable=find_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer, find_checkbox,True)

source_file_type_menu_lb = tk.Label(window, text='Source file type ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate,y_multiplier_integer,source_file_type_menu_lb,True)

source_file_type_menu = tk.OptionMenu(window,source_file_type_menu_var,'*','bmp','csv','doc','docx','gexf','html','jpg','kml','pdf','png','tif','txt','xls','xlsm','xlsx')
source_file_type_menu.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.file_matcher_source_file_type_menu_pos,y_multiplier_integer,source_file_type_menu,True)

target_file_type_menu_lb = tk.Label(window, text='Target file type ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.file_matcher_target_file_type_menu_lb_pos,y_multiplier_integer,target_file_type_menu_lb,True)

target_file_type_menu = tk.OptionMenu(window,target_file_type_menu_var,'*','bmp','csv','doc','docx','gexf','html','jpg','kml','pdf','png','tif','txt','xls','xlsm','xlsx')
target_file_type_menu.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.file_matcher_target_file_type_menu_pos,y_multiplier_integer,target_file_type_menu)

matching_var.set(1)
matching_checkbox = tk.Checkbutton(window, variable=matching_var, onvalue=1, offvalue=0, command=lambda: GUI_util.trace_checkbox_NoLabel(matching_var, matching_checkbox, "Exact match", "Partial match (by number of embedded items)"))
matching_checkbox.config(text="Exact match")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,matching_checkbox,True)

character_value_var.set('_')
character_lb = tk.Label(window, text='Separator character(s)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate,y_multiplier_integer, character_lb,True)

character_value = tk.Entry(window, width=2,textvariable=character_value_var)
character_value.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.file_matcher_character_value_pos,y_multiplier_integer, character_value,True)

number_of_items_lb = tk.Label(window, text='Number of items')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.file_matcher_number_of_items_lb_pos,y_multiplier_integer, number_of_items_lb,True)

number_of_items_value = tk.Entry(window, width=2,textvariable=number_of_items_var)
number_of_items_value.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.file_matcher_number_of_items_value_pos,y_multiplier_integer, number_of_items_value,True)

include_exclude_var.set(1)
include_exclude_checkbox = tk.Checkbutton(window, variable=include_exclude_var, onvalue=1, offvalue=0, command=lambda: GUI_util.trace_checkbox_NoLabel(include_exclude_var, include_exclude_checkbox, "Include first # items only", "Exclude first # items"))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.file_matcher_include_exclude_pos,y_multiplier_integer, include_exclude_checkbox)
include_exclude_checkbox.config(text='Include first # items only',state="disabled")

copy_var.set(0)
copy_checkbox = tk.Checkbutton(window, variable=copy_var, onvalue=1, offvalue=0)
copy_checkbox.config(text="COPY processed files")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,copy_checkbox,True)

move_var.set(0)
move_checkbox = tk.Checkbutton(window, variable=move_var, onvalue=1, offvalue=0)
move_checkbox.config(state='disabled',text="MOVE processed files")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate,y_multiplier_integer,move_checkbox)

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

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help",GUI_IO_util.msg_csvFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, click to select a csv file containing a list of filenames to be used for finding matches.\n\nTO GENERATE A LIST OF FILES FOR PARTIAL MATCH YOU CAN USE THE FILE_MANAGER_MAIN.PY, WITH THE LIST OPTION AND THE FILTER 'By number of embedded items'.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to use the script 'Match files'.\n\nThe script identifies files having the same filename and different extensions (e.g., The Atlanta Journal_3-12-1956_4_2.pdf and The Atlanta Journal_3-12-1956_8_2.txt). All subdirectories of a selected directory will be searched for a selected pair of source and target extensions (e.g., pdf and docx).\n\nThe script is very useful, for instance, for identifying pdf files that have been manually transcribed (or automatically converted) to doc/docx or txt format. But it can be used more generally to identify files with the same filename and different extensions.\n\nUsing * * for both source and target will identify any file with the same exact filename and different extensions of any type.\n\nYou can select to match files with an exact match with the baseline filename (e.g., The Atlanta Journal_3-12-1956_8_2), or with a partial match (e.g., only the first two items in the filenames, The Atlanta Journal_3-12-1956).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to find files with an exact match with the SOURCE filename (e.g., The Atlanta Journal_3-12-1956_8_2), or with a partial match (e.g., only the first two items in the filenames, The Atlanta Journal_3-12-1956).\n\nFor a partial match, untick the Exact match checkbox and enter the character separating items (e.g., _) and the number of items (e.g., 2) and whether you want to include only the first # items. For instance, if you want a partial match based on newspaper name and date of newspaper articles such as Alexandria Gazette_04-16-1910_3_1, enter _ as the Separator character(s), 2 as Number of items, and tick the checkbox Include first # items only.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick one or the other checkboxes to COPY or MOVE the matched files from the INPUT directory to the OUTPUT directory.\n\nIn the OUTPUT directory, the algorithm will create a new sub-directory 'file_matcher_OUTPUT' (any previous 'file_matcher_OUTPUT' subdirectory will be overwritten). Inside this sub-directory, three sub-directories will be created: matched, unmatched, duplicates where matched, unmatched, and duplicate files will be copied/moved.\n\nLeave the checkboxes unticked if you just want to get a list of files.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer -1

y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 script allows you to find matches between any SOURCE file of a selected type (e.g., pdf) and TARGET files with the same filename but same/different type (e.g., docx).\n\nThe script is very useful, for instance, for identifying pdf files that have been manually transcribed (or automatically converted) to doc/docx or txt format. But it can be used more generally to identify files with the same filename and different extensions.\n\nIn INPUT the algorithm expects a directory containing a set of files. All files in that directory will be processed against all selected-type files in all subdirectories (thus, to search your entire computer drive, select your top directory).\n\nIn OUTPUT the algorithm will produce 3 csv files listing MATCHED and UNMATCHED files. It will also list all DUPLICATE files found.\n\nThe output files will be placed inside the top searched INPUT directory regardless of selected OUTPUT directory in the I/O configuration."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()

