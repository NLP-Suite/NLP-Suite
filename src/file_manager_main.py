# Written by Roberto Franzosi December 2019

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_manager.py",['csv','tkinter','os'])==False:
    sys.exit(0)

import tkinter as tk
import tkinter.messagebox as mb
import os
import csv

import IO_files_util
import GUI_IO_util
import IO_csv_util
import file_filename_util
import IO_user_interface_util

# RUN section ______________________________________________________________________________________________________________________________________________________


def run(inputDir, outputDir,
        openOutputFiles,
        createCharts,
        chartPackage,
        selectedCsvFile_var, selectedCsvFile_colName,
        utf8_var,
        ASCII_var,
        list_var,
        rename_var,
        copy_var,
        move_var,
        delete_var,
        count_file_manager_var,
        split_var,
        rename_new_entry,
        by_file_type_var,
        file_type_menu_var,
        by_creation_date_var,
        by_author_var,
        before_date_var,
        after_date_var,
        by_prefix_var,
        by_substring_var,
        string_entry_var,
        by_foldername_var,
        folder_character_separator_var,
        by_embedded_items_var,
        comparison_var,
        number_of_items_var,
        embedded_item_character_value_var,
        include_exclude_var,
        character_count_file_manager_var,
        character_entry_var,
        include_subdir_var,
        fileName_embeds_date,
        date_format,
        date_separator,
        date_position):

    if inputDir==outputDir and list_var==0:
        command = tk.messagebox.askyesno("File manager: Input and Output paths", "You have selected the same directory for both input and output.\n\nTHIS IS NOT A GOOD IDEA, PARTICULARLY IF YOU DO NOT HAVE BACKUPS OF THE FILES IN THE INPUT DIRECTORY!\n\nAre you sure you want to do continue?")
        if command==False:
            return

    output_filename=''
    options=0
    i=0
    itemCount=0
    msg=''
    operation=''
    fieldnames = []
    currentSubfolder=os.path.basename(os.path.normpath(inputDir))
    hasFullPath = False

    if utf8_var==1 or ASCII_var==1:
        mb.showwarning(title='Option not available',
                       message='The utf-8 and ASCII options are not available yet.\n\nSorry!')
        list_var=1
        return

    if list_var==1:
        options=options+1
        operation = 'listed'
        output_filename = "List_files_" + currentSubfolder + ".csv"
    if rename_var==1:
        options=options+1
        operation = 'renamed'
        output_filename = "List_renamed_files_" + currentSubfolder + ".csv"
    if copy_var==1:
        options=options+1
        operation = 'copied'
        output_filename = "List_copied_files_" + currentSubfolder + ".csv"
    if move_var==1:
        options=options+1
        operation = 'moved'
        output_filename = "List_moved_files_" + currentSubfolder + ".csv"
    if delete_var==1:
        options=options+1
        operation = 'deleted'
        output_filename = "List_deleted_files_" + currentSubfolder + ".csv"
        command = tk.messagebox.askyesno("Deleting files", "You are about to delete files. Make sure you have a backup! Files deleted via a Python command will not be recoverable from the Recycle Bin\n\nAre you sure you want to do continue?")
        if command==False:
            return
    if count_file_manager_var==1:
        i=1
        options=options+1
        operation = 'counted'
        output_filename = "Count_files_" + currentSubfolder + ".csv"

    if split_var==1:
        i=1
        options=options+1
        operation = 'split'
        output_filename = "split_files_" + currentSubfolder + ".csv"

    if options==0:
        mb.showwarning(title='File manager', message='No file manager option has been selected.\n\nPlease, select one option (rename, copy, move, delete) and try again.')
        return

    if options==1:
        if count_file_manager_var==0:
            if list_var==0 and by_file_type_var=='' and by_prefix_var==0 and by_substring_var==0:
                mb.showwarning(title='File manager', message='You have selected a file manager option, but no specific criteria for managing the files: By file type, By prefix value, or By substring value.\n\nPlease, select the file criteria to use and try again.')
                return

    if options>1:
        mb.showwarning(title='File manager', message='Only one option at a time can be selected. You have selected ' + str(options) + ' options.\n\nPlease, deselect some options and try again.')
        return

    if by_embedded_items_var:
        if embedded_item_character_value_var=='':
            mb.showwarning(title='File manager',
                           message='You have selected the option "By number of embedded items" but you have not entered the "Separator character(s).\n\nPlease, enter the character(s) and try again.')
            return

    # -------------------------------------------------------------------------------------------------
    # setup the field names of the output csv file
    fieldnames = ['File_Name', 'Path_To_File', 'File_Name_With_Path']

    if by_creation_date_var==1:
        if file_type_menu_var!='' and file_type_menu_var!='doc' and by_file_type_var!='docx':
            mb.showwarning(title='File manager', message='You have selected the options "By file type" as ' + file_type_menu_var + ' and "By creation date".\n\nThe "By creation date" option only works for "doc" and "docx" type of files.\n\nThe "By creation date" option will be ignored.')
        else:
            fieldnames = fieldnames + ['Creation_date', 'Modification_date']

    if by_author_var==1:
        if file_type_menu_var!='' and file_type_menu_var!='doc' and by_file_type_var!='docx':
            mb.showwarning(title='File manager', message='You have selected the options "By file type" as ' + file_type_menu_var + ' and "By author".\n\nThe "By author" option only works for "doc" and "docx" type of files.\n\nThe "By author" option will be ignored.')
        else:
            fieldnames = fieldnames + ['Author']

    if by_embedded_items_var==1:
        if number_of_items_var>0:
            fieldnames = fieldnames + ['Embedded items count ('+embedded_item_character_value_var+')']
            fieldnames = fieldnames + ['Count by document']
    if fileName_embeds_date==1:
        fieldnames = fieldnames + ['Date']

    if character_count_file_manager_var==1:
        fieldnames = fieldnames + ['Character count ('+character_entry_var+')']

    if split_var == 1:
        # must get the first file in order to compute the number of headers to be displayed in the output csv file
        for inputDir, subdirs, files in os.walk(inputDir):
            ID = 1
            for filename in files:
                if ID==1:
                    break
        filename_items = filename.split(embedded_item_character_value_var)
        ID = 1
        for item in filename_items:
            fieldnames = fieldnames + ['Split item' + str(ID)]
            ID = ID + 1

    # ------------------------------------------------------------------------------------------------------------------------------------------------

    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running File Manager at',
                                                 True, '', True, '', True)

    if list_var==1:
        # extract the last subfolder of the path to be displayed as part of the output filename
        subDir = os.path.basename(os.path.normpath(inputDir))
        # output_filename = "List__files" + str(subDir) + ".csv"

    if count_file_manager_var==True:
        # fieldnames = ['Main_Dir', 'Subdir', 'pdf', 'doc', 'docx', 'txt', 'Matching']
        #i=len(os.listdir(inputDir))
        i=file_filename_util.get_count(inputDir, outputDir, output_filename)
    else:
        with open(outputDir + os.sep + output_filename, 'w', errors='ignore', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()

    if rename_var==1:
        # You can in fact have a blank entry
        # if rename_new_entry=='' and string_entry_var=='':
        # 	mb.showwarning(title='File handling', message='You have selected the option "Rename files" but you have not entered the substring values old and new necessary for renaming the filename.\n\nPlease, enter the values in the fields "New substring for renaming" and "Enter value" and try again.')
        # 	return
        # if rename_new_entry=='':
        # 	mb.showwarning(title='File handling', message='You have selected the option "Rename files" but you have not entered the new substring value necessary for renaming the filename.\n\nPlease, enter the value in the field "New substring for renaming" and try again.')
        # 	return
        if by_prefix_var==False and by_substring_var==False and by_foldername_var==False and by_embedded_items_var==False:
            mb.showwarning(title='File manager', message='You have selected the option to Rename files but you have not selected any of the available options for renaming the files.\n\nPlease, make a selection and enter the appropriate values and try again.')
            return
        if (by_prefix_var or by_substring_var) and string_entry_var=='':
            mb.showwarning(title='File manager', message='You have selected the option to Rename files by prefix/sub-string value but you have not entered the values necessary for renaming the filename.\n\nPlease, enter the missing values in the fields \'Enter value\' and/or \'New renaming value\' and try again.')
            return
        if by_foldername_var and folder_character_separator_var=='':
            mb.showwarning(title='File manager', message='You have selected the option to Rename files by Folder name but you have not entered the Separator character(s).\n\nPlease, enter appropriate values in the \'Separator character(s)\' field and try again.')
            return

    if len(file_type_menu_var)>0:
        msg='of type "' + file_type_menu_var + '" '

    if by_prefix_var==1 and by_substring_var==1:
        mb.showwarning(title='File manager', message='Only one option at a time, "By prefix value" or "By sub-string value," can be selected.\n\nPlease, deselect one option and try again.')
        return

    if by_prefix_var==1:
        if len(string_entry_var)==0:
            mb.showwarning(title='File manager', message='You have selected the option "By prefix value" but no string value has been entered.\n\nPlease, enter the prefix value in the "Enter value" field and try again.')
            return
        if len(msg)>0:
            msg = msg + ' and with string prefix "' + string_entry_var + '" '
        else:
            msg ='with string prefix "' + string_entry_var + '" '

    if by_substring_var==1:
        if len(string_entry_var)==0:
            mb.showwarning(title='File manager', message='You have selected the option "By sub-string value" but no string value has been entered.\n\nPlease, enter the sub-string value in the "Enter value" field and try again.')
            return
        if len(msg)>0:
            msg = msg + ' and containing the substring "' + string_entry_var + '" '
        else:
            msg='containing the substring "' + string_entry_var + '" '

    # For cases where matching files beginning with a dot (.); like files in the current directory or hidden files on Unix based system, use the os.walk
    # import glob
    # include_subdir_var
    # for filename in glob.iglob(inputDir + os.sep+ '*.'+by_file_type_var, recursive=True):
    #      print(filename)

    # root: Current path which is "walked through"
    # subdirs: Files in root of type directory
    # files: Files in current root (not in subdirs) of type other than directory

    # must handle the case in which we use a csv file
    # _________________________________________________________________________________________________________________________________________________
    if selectedCsvFile_var != '':
        if noHeaders==False:
            selectedCsvFile_colNum=IO_csv_util.get_columnNumber_from_headerValue(headers, selectedCsvFile_colName, selectedCsvFile_var)
        else:
            # No headers, we assume the first column
            selectedCsvFile_colNum=0

        fileList = []
        with open(selectedCsvFile_var, 'r', encoding="utf-8", errors='ignore') as read_obj:
            csv_reader = csv.reader(read_obj)
            if noHeaders==False:
                # skip first row since it has headers
                next(csv_reader)
            for row in csv_reader:
                if row[selectedCsvFile_colNum][:10] == "=hyperlink":
                    f = IO_csv_util.undressFilenameForCSVHyperlink(row[selectedCsvFile_colNum])
                    print(f)
                else:
                    f = row[selectedCsvFile_colNum]
                head, tail = os.path.split(f)
                if head != '':
                    hasFullPath = True
                fileList.append(f)

    # _________________________________________________________________________________________________________________________________________________

    # processFile returns: fileFound, characterCount,creation_date,modification_date,author,date, dateStr
    if include_subdir_var==1:
        for inputDir, subdirs, files in os.walk(inputDir):
            for filename in files:
                print ("Processing file: {}".format(filename))
                fileFound, characterCount,\
                creation_date,modification_date,\
                author,date, \
                dateStr = file_filename_util.processFile(inputDir,outputDir,filename,output_filename,
							fieldnames,
							selectedCsvFile_var,
							hasFullPath,
							utf8_var,
							ASCII_var,
							rename_var,
							copy_var,
							move_var,
							delete_var,
                            split_var,
							rename_new_entry,
							file_type_menu_var,
							by_creation_date_var,
							by_author_var,
							by_prefix_var,
							by_substring_var,
							string_entry_var,
							by_foldername_var,
							folder_character_separator_var,
							by_embedded_items_var,
							comparison_var,
							number_of_items_var,
							embedded_item_character_value_var,
							include_exclude_var,
							character_count_file_manager_var,
							character_entry_var,
							include_subdir_var,
							fileName_embeds_date,
							date_format,
							date_separator,
							date_position)
                if fileFound:
                    i=i+1
    else:
        if hasFullPath: # This is used when full paths are present in the CSV file, we ignore the input directory
            print("Full path present, processing regardless of existence in input directory")
            for filename in fileList:
                fileFound, characterCount, creation_date, modification_date, author, date, dateStr = file_filename_util.processFile(
                    inputDir, outputDir, filename, output_filename, fieldnames, selectedCsvFile_var, hasFullPath,
					utf8_var, ASCII_var,
					list_var, rename_var,
                    copy_var, move_var, delete_var, split_var, rename_new_entry, file_type_menu_var, by_creation_date_var,
                    by_author_var, by_prefix_var, by_substring_var, string_entry_var, by_foldername_var,
                    folder_character_separator_var, by_embedded_items_var, comparison_var, number_of_items_var, embedded_item_character_value_var,
                    include_exclude_var, character_count_file_manager_var, character_entry_var, include_subdir_var,
                    fileName_embeds_date, date_format, date_separator, date_position)
                if fileFound:
                    i = i + 1
        elif count_file_manager_var==False: #list, copy, move, delete
            for filename in os.listdir(inputDir):
                if not os.path.isdir(os.path.join(inputDir,filename)):
                    print ("Processing file: {}".format(filename))
                    if selectedCsvFile_var != '':
                        if filename in fileList:
                            processFile = True
                        else:
                            processFile = False
                    else:
                        processFile = True
                    if processFile:
                        fileFound, characterCount,creation_date,modification_date,author,date, \
                            dateStr = file_filename_util.processFile(inputDir,outputDir,filename,output_filename,
                                fieldnames,
                                selectedCsvFile_var,
                                hasFullPath,
                                utf8_var,
                                ASCII_var,
                                list_var,rename_var,copy_var,move_var,delete_var, split_var, rename_new_entry,file_type_menu_var,by_creation_date_var,by_author_var,by_prefix_var,by_substring_var,string_entry_var,by_foldername_var,folder_character_separator_var,by_embedded_items_var,comparison_var, number_of_items_var,embedded_item_character_value_var,include_exclude_var,character_count_file_manager_var,character_entry_var,include_subdir_var,fileName_embeds_date,date_format,date_separator,date_position)
                        if fileFound:
                            i=i+1

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running File manager at', True, '', True, startTime)

    if i > 0:
        if rename_var==1:
            mb.showwarning(title='File manager', message=str(i) + ' files ' + msg + operation + '.\n\n'+operation + ' files have been renamed in the input directory ' + inputDir + '.')
        elif copy_var==1:
            mb.showwarning(title='File manager', message=str(i) + ' files ' + msg + operation + '.\n\n'+operation + ' files have been saved in the output directory ' + outputDir + '.')
        else:
            mb.showwarning(title='File manager', message=str(i) + ' files ' + msg + operation + '.')
            filesToOpen=[]
            filesToOpen.append(os.path.join(outputDir,output_filename))
            IO_files_util.OpenOutputFiles(GUI_util.window, True, filesToOpen, outputDir)
    else:
        mb.showwarning(title='File manager', message='No files ' + msg + operation + '.\n\nPlease, check the following information:\n  1. INPUT files directory;\n  2. selected file type (if you ticked the By file type option);\n  3. Include subdirectory option.')

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_chart_output_checkbox.get(),
                                GUI_util.charts_dropdown_field.get(),
                                selectedCsvFile_var.get(),
                                select_csv_field_var.get(),
                                utf8_var.get(),
                                ASCII_var.get(),
                                list_var.get(),
                                rename_var.get(),
                                copy_var.get(),
                                move_var.get(),
                                delete_var.get(),
                                count_file_manager_var.get(),
                                split_file_manager_var.get(),
                                rename_new_entry_var.get(),
                                by_file_type_var.get(),
                                file_type_menu_var.get(),
                                by_creation_date_var.get(),
                                by_author_var.get(),
                                before_date_var.get(),
                                after_date_var.get(),
                                by_prefix_var.get(),
                                by_substring_var.get(),
                                string_entry_var.get(),
                                by_foldername_var.get(),
                                folder_character_separator_var.get(),
                                by_embedded_items_var.get(),
                                comparison_var.get(),
                                number_of_items_var.get(),
                                embedded_item_character_value_var.get(),
                                include_exclude_var.get(),
                                character_count_file_manager_var.get(),
                                character_entry_var.get(),
                                include_subdir_var.get(),
                                fileName_embeds_date.get(),
                                date_format.get(),
                                date_separator_var.get(),
                                date_position_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=680, # height at brief display
                             GUI_height_full=720, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=1, # to be added for full display
                             increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for File Manager (by Filename)'
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
config_input_output_numeric_options=[0,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)


selectedCsvFile_var=tk.StringVar()
select_csv_field_var=tk.StringVar()
selectedCsvFile_colNum=0
utf8_var=tk.IntVar()
ASCII_var=tk.IntVar()
list_var=tk.IntVar()
rename_var=tk.IntVar()
rename_new_entry_var=tk.StringVar()
copy_var=tk.IntVar()
move_var=tk.IntVar()
delete_var=tk.IntVar()
# renamed from count_var so that the count_var used in Excel charts can be easily found
count_file_manager_var=tk.IntVar()
split_file_manager_var=tk.IntVar()
use_csv_var=tk.IntVar()
by_file_type_var=tk.IntVar()
file_type_menu_var=tk.StringVar()
by_creation_date_var=tk.IntVar()
by_author_var=tk.IntVar()
before_date_var=tk.StringVar()
after_date_var=tk.StringVar()
by_prefix_var=tk.IntVar()
by_substring_var=tk.IntVar()
string_entry_var=tk.StringVar()
by_foldername_var=tk.IntVar()
folder_character_separator_var=tk.StringVar()

comparison_var= tk.StringVar()
by_embedded_items_var=tk.IntVar()
number_of_items_var=tk.IntVar()
embedded_item_character_value_var=tk.StringVar()
include_exclude_var=tk.IntVar()

character_count_file_manager_var=tk.IntVar()
character_entry_var=tk.StringVar()

include_subdir_var=tk.IntVar()
fileName_embeds_date = tk.IntVar()
date_format = tk.StringVar()			#the following 3 fields are also used by SSR and NGRAMS
date_separator_var = tk.StringVar()
date_position_var = tk.IntVar()

def clear(e):
    selectedCsvFile_var.set('')
    selectedCsvFile.configure(state='disabled')
    select_csv_field_var.set('')
    select_csv_field_menu.configure(state='disabled')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

menu_values = " "
def get_additional_csvFile(window,title,fileType):
    global headers, noHeaders
    noHeaders = False
    menu_values=[]
    import os
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)
    if len(filePath)>0:
        select_csv_field_menu.configure(state='normal')
        selectedCsvFile.config(state='normal')
        selectedCsvFile_var.set(filePath)
        if IO_csv_util.get_csvfile_headers(filePath,True)=='':
            noHeaders=True
            menu_values=range(1, IO_csv_util.get_csvfile_numberofColumns(filePath)+1)
        else:
            data, headers = IO_csv_util.get_csv_data(filePath,True)
            menu_values=headers
            noHeaders = False
        m = select_csv_field_menu["menu"]
        m.delete(0,"end")
        for s in menu_values:
            m.add_command(label=s,command=lambda value=s:select_csv_field_var.set(value))

# def activate_csvfile_column(*args):
# 	if selectedCsvFile_var.get()!='':
# 		if noHeaders == False:
# 			print(IO_csv_util.get_columnNumber_from_headerValue(headers, select_csv_field_var.get()))
# 			selectedCsvFile_colNum= IO_csv_util.get_columnNumber_from_headerValue(headers, select_csv_field_var.get())
# 		else:
# 			selectedCsvFile_colNum= select_csv_field_var.get()-1
# select_csv_field_var.trace('w',activate_csvfile_column)

# add_file_button = tk.Button(window, text='csv file', width=2,height=1,state='disabled',command=lambda: get_additional_csvFile(window,'Select INPUT csv file', [("csv files", "*.csv")]))
add_file_button = tk.Button(window, text='csv file', command=lambda: get_additional_csvFile(window,'Select INPUT csv file', [("csv files", "*.csv")]))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,add_file_button,True)

#setup a button to open Windows Explorer on the selected input directory
current_y_multiplier_integer=y_multiplier_integer-1
openInputFile_button  = tk.Button(window, width=3, text='', command=lambda: IO_files_util.openFile(window, selectedCsvFile_var.get()))
y_multiplier_integer = GUI_IO_util.placeWidget(window,
    GUI_IO_util.get_labels_x_coordinate()+70, y_multiplier_integer,
    openInputFile_button, True)

selectedCsvFile = tk.Entry(window,width=110,state='disabled',textvariable=selectedCsvFile_var)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+120,y_multiplier_integer,selectedCsvFile,True)

select_csv_field_lb = tk.Label(window,text='Select csv field')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+800,y_multiplier_integer,select_csv_field_lb,True)

if menu_values!=' ':
    select_csv_field_menu = tk.OptionMenu(window, select_csv_field_var, *menu_values)
else:
    select_csv_field_menu = tk.OptionMenu(window, select_csv_field_var, menu_values)
select_csv_field_menu.configure(state='disabled',width=12)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+900,y_multiplier_integer,select_csv_field_menu)

utf8_var.set(0)
utf8_checkbox = tk.Checkbutton(window, text='Check input filename(s) for utf-8 encoding ', variable=utf8_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,utf8_checkbox,True)

ASCII_var.set(0)
ASCII_checkbox = tk.Checkbutton(window, text='Convert non-ASCII apostrophes & quotes in filename(s)', variable=ASCII_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+400,y_multiplier_integer,ASCII_checkbox)

list_var.set(0)
list_checkbox = tk.Checkbutton(window, text='List', variable=list_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,list_checkbox,True)

rename_var.set(0)
rename_checkbox = tk.Checkbutton(window, text='Rename', variable=rename_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+60,y_multiplier_integer,rename_checkbox,True)

copy_var.set(0)
copy_checkbox = tk.Checkbutton(window, text='Copy', variable=copy_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+160,y_multiplier_integer,copy_checkbox,True)

move_var.set(0)
move_checkbox = tk.Checkbutton(window, text='Move', variable=move_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+260,y_multiplier_integer,move_checkbox,True)

delete_var.set(0)
delete_checkbox = tk.Checkbutton(window, text='Delete', variable=delete_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+360,y_multiplier_integer,delete_checkbox,True)

count_file_manager_var.set(0)
count_checkbox = tk.Checkbutton(window, text='Count', state="normal", variable=count_file_manager_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+460,y_multiplier_integer,count_checkbox,True)

split_file_manager_var.set(0)
split_checkbox = tk.Checkbutton(window, text='Split', state="normal", variable=split_file_manager_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+560,y_multiplier_integer,split_checkbox)

# use_csv_var.set(0)
# use_csv_checkbox = tk.Checkbutton(window, text='Use csv for Source & Target fields', state="normal", variable=use_csv_var, onvalue=1, offvalue=0)
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+560,y_multiplier_integer,use_csv_checkbox)

def activate_list_options(*args):
    if list_var.get()==1:
        rename_checkbox.configure(state="disabled")
        copy_checkbox.configure(state="disabled")
        move_checkbox.configure(state="disabled")
        delete_checkbox.configure(state="disabled")
        count_checkbox.configure(state="disabled")
        split_checkbox.configure(state="disabled")
        character_count_checkbox.configure(state="normal")
        fileName_embeds_date_checkbox.config(state='normal')
        by_creation_date_checkbox.configure(state="normal")
        by_author_checkbox.configure(state="normal")
    else:
        rename_checkbox.configure(state="normal")
        copy_checkbox.configure(state="normal")
        move_checkbox.configure(state="normal")
        delete_checkbox.configure(state="normal")
        count_checkbox.configure(state="normal")
        split_checkbox.configure(state="normal")
        character_count_checkbox.configure(state="disabled")
        fileName_embeds_date.set(0)
        fileName_embeds_date_checkbox.config(state='disabled')
        date_format_menu.config(state="disabled")
        date_separator.config(state='disabled')
        date_position_menu.config(state="disabled")
        by_creation_date_checkbox.configure(state="disabled")
        by_author_checkbox.configure(state="disabled")
    # rename_new_entry.configure(state="disabled")
list_var.trace('w',activate_list_options)

def activate_rename_options(*args):
    if rename_var.get()==1:
        list_checkbox.configure(state="disabled")
        copy_checkbox.configure(state="disabled")
        move_checkbox.configure(state="disabled")
        delete_checkbox.configure(state="disabled")
        count_checkbox.configure(state="disabled")
        split_checkbox.configure(state="disabled")
        rename_new_entry.configure(state="normal")
        by_foldername_checkbox.config(state="normal")
    else:
        list_checkbox.configure(state="normal")
        copy_checkbox.configure(state="normal")
        move_checkbox.configure(state="normal")
        delete_checkbox.configure(state="normal")
        count_checkbox.configure(state="normal")
        split_checkbox.configure(state="normal")
        rename_new_entry.configure(state="disabled")
        by_foldername_checkbox.config(state="disabled")
    #activate_prefix_options()
    character_count_checkbox.configure(state="disabled")
    by_creation_date_checkbox.configure(state="disabled")
    by_author_checkbox.configure(state="disabled")
rename_var.trace('w',activate_rename_options)

def activate_copy_options(*args):
    if copy_var.get()==1:
        list_checkbox.configure(state="disabled")
        rename_checkbox.configure(state="disabled")
        move_checkbox.configure(state="disabled")
        delete_checkbox.configure(state="disabled")
        count_checkbox.configure(state="disabled")
        split_checkbox.configure(state="disabled")
    else:
        list_checkbox.configure(state="normal")
        rename_checkbox.configure(state="normal")
        move_checkbox.configure(state="normal")
        delete_checkbox.configure(state="normal")
        count_checkbox.configure(state="normal")
        split_checkbox.configure(state="normal")
    character_count_checkbox.configure(state="disabled")
    rename_new_entry.configure(state="disabled")
    by_creation_date_checkbox.configure(state="disabled")
    by_author_checkbox.configure(state="disabled")
copy_var.trace('w',activate_copy_options)

def activate_move_options(*args):
    if move_var.get()==1:
        list_checkbox.configure(state="disabled")
        rename_checkbox.configure(state="disabled")
        copy_checkbox.configure(state="disabled")
        delete_checkbox.configure(state="disabled")
        count_checkbox.configure(state="disabled")
        split_checkbox.configure(state="disabled")
    else:
        list_checkbox.configure(state="normal")
        rename_checkbox.configure(state="normal")
        copy_checkbox.configure(state="normal")
        delete_checkbox.configure(state="normal")
        count_checkbox.configure(state="normal")
        split_checkbox.configure(state="normal")
    character_count_checkbox.configure(state="disabled")
    rename_new_entry.configure(state="disabled")
    by_creation_date_checkbox.configure(state="disabled")
    by_author_checkbox.configure(state="disabled")
move_var.trace('w',activate_move_options)

def activate_delete_options(*args):
    if delete_var.get()==1:
        list_checkbox.configure(state="disabled")
        rename_checkbox.configure(state="disabled")
        copy_checkbox.configure(state="disabled")
        move_checkbox.configure(state="disabled")
        split_checkbox.configure(state="disabled")
    else:
        list_checkbox.configure(state="normal")
        rename_checkbox.configure(state="normal")
        copy_checkbox.configure(state="normal")
        move_checkbox.configure(state="normal")
        split_checkbox.configure(state="normal")
    character_count_checkbox.configure(state="disabled")
    by_creation_date_checkbox.configure(state="disabled")
    by_author_checkbox.configure(state="disabled")
delete_var.trace('w',activate_delete_options)

def activate_count_options(*args):
    if count_file_manager_var.get()==1:
        list_checkbox.configure(state="disabled")
        rename_checkbox.configure(state="disabled")
        copy_checkbox.configure(state="disabled")
        move_checkbox.configure(state="disabled")
        delete_checkbox.configure(state="disabled")
        split_checkbox.configure(state="disabled")
    else:
        list_checkbox.configure(state="normal")
        rename_checkbox.configure(state="normal")
        copy_checkbox.configure(state="normal")
        move_checkbox.configure(state="normal")
        delete_checkbox.configure(state="normal")
        split_checkbox.configure(state="normal")
    character_count_checkbox.configure(state="disabled")
    rename_new_entry.configure(state="disabled")
count_file_manager_var.trace('w',activate_count_options)

def activate_split_options(*args):
    if split_file_manager_var.get()==1:
        list_checkbox.configure(state="disabled")
        rename_checkbox.configure(state="disabled")
        copy_checkbox.configure(state="disabled")
        move_checkbox.configure(state="disabled")
        delete_checkbox.configure(state="disabled")
        count_checkbox.configure(state="disabled")
        by_embedded_items_checkbox.configure(state="normal")

        by_creation_date_checkbox.configure(state="disabled")
        by_author_checkbox.configure(state="disabled")
        character_count_checkbox.configure(state="disabled")
        rename_new_entry.configure(state="disabled")
        by_prefix_checkbox.configure(state="disabled")
        by_substring_checkbox.configure(state="disabled")

    else:
        list_checkbox.configure(state="normal")
        rename_checkbox.configure(state="normal")
        copy_checkbox.configure(state="normal")
        move_checkbox.configure(state="normal")
        delete_checkbox.configure(state="normal")
        count_checkbox.configure(state="normal")

        by_embedded_items_checkbox.configure(state="normal")
        by_creation_date_checkbox.configure(state="normal")
        by_author_checkbox.configure(state="normal")
        character_count_checkbox.configure(state="normal")
        rename_new_entry.configure(state="normal")
        by_prefix_checkbox.configure(state="normal")
        by_substring_checkbox.configure(state="normal")
split_file_manager_var.trace('w',activate_split_options)

by_file_type_var.set(0)
by_file_type_checkbox = tk.Checkbutton(window, text='By file type', variable=by_file_type_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,by_file_type_checkbox,True)

file_type_menu_lb = tk.Label(window, text='Select file type ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+280,y_multiplier_integer,file_type_menu_lb,True)
file_type_menu = tk.OptionMenu(window,file_type_menu_var,'*','bmp','csv','doc','docx','gexf','html','jpg','kml','pdf','png','tif','txt','xls','xlsm','xlsx')
file_type_menu.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+370,y_multiplier_integer,file_type_menu)


def activate_file_type_options(*args):
    file_type_menu_var.set('')
    if by_file_type_var.get()==1:
        file_type_menu.configure(state="normal")
    else:
        file_type_menu.configure(state="disabled")
by_file_type_var.trace('w',activate_file_type_options)

by_creation_date_checkbox = tk.Checkbutton(window, text='By creation & modification date', variable=by_creation_date_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,by_creation_date_checkbox,True)
# before_date,
# after_date,
# on_date,

by_author_checkbox = tk.Checkbutton(window, text='By author (Windows Office files)', variable=by_author_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+400,y_multiplier_integer,by_author_checkbox)

by_prefix_var.set(0)
by_prefix_checkbox = tk.Checkbutton(window, text='By prefix value', variable=by_prefix_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,by_prefix_checkbox,True)

by_substring_var.set(0)
by_substring_checkbox = tk.Checkbutton(window, text='By sub-string value', variable=by_substring_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+140,y_multiplier_integer,by_substring_checkbox,True)

string_entry_lb = tk.Label(window, text='Enter value (case sensitive)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+280,y_multiplier_integer,string_entry_lb,True)

string_entry = tk.Entry(window,width=30,textvariable=string_entry_var)
string_entry.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+450,y_multiplier_integer,string_entry,True)

rename_new_entry_lb = tk.Label(window, text='New renaming value (case sensitive)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+580,y_multiplier_integer,rename_new_entry_lb,True)

rename_new_entry = tk.Entry(window,width=30,textvariable=rename_new_entry_var)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+ 720,y_multiplier_integer,rename_new_entry)

y_multiplier_integer_save=y_multiplier_integer-1

rename_new_entry_lb.place_forget() #invisible
rename_new_entry.place_forget() #invisible

rename_new_entry.configure(state="disabled")

def activate_prefix_substring_options(*args):
    by_foldername_var.set(0)
    by_embedded_items_var.set(0)
    if by_prefix_var.get()==1 or by_substring_var.get()==1:
        if by_prefix_var.get()==1:
            by_substring_checkbox.configure(state="disabled")
        if by_substring_var.get()==1:
            by_prefix_checkbox.configure(state="disabled")
        else:
            by_prefix_checkbox.configure(state="normal")
        string_entry.configure(state="normal")
        if rename_var.get()==False:
            rename_new_entry_lb.place_forget() #invisible
            rename_new_entry.place_forget() #invisible
        else:
            y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 400,y_multiplier_integer_save,rename_new_entry_lb,True)
            y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate()+ 600,y_multiplier_integer_save,rename_new_entry)
    else:
        if by_substring_var.get()==0:
            by_prefix_checkbox.configure(state="normal")
        by_substring_checkbox.configure(state="normal")
        string_entry.configure(state="disabled")
        rename_new_entry_lb.place_forget() #invisible
        rename_new_entry.place_forget() #invisible
    string_entry_var.set("")
by_prefix_var.trace('w',activate_prefix_substring_options)
by_substring_var.trace('w',activate_prefix_substring_options)

by_foldername_var.set(0)
by_foldername_checkbox = tk.Checkbutton(window, text='By subfolder name (renaming only)', variable=by_foldername_var, onvalue=1, offvalue=0)
by_foldername_checkbox.config(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,by_foldername_checkbox,True)

folder_character_separator_lb = tk.Label(window, text='Separator character(s)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+280,y_multiplier_integer, folder_character_separator_lb,True)
folder_character_separator = tk.Entry(window, textvariable=folder_character_separator_var)
folder_character_separator.configure(width=2,state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+420,y_multiplier_integer, folder_character_separator)

def activateFolderCharacterSeparator(*args):
    folder_character_separator_var.set('')
    if by_foldername_var.get()==1:
        folder_character_separator.configure(width=2,state="normal")
    else:
        folder_character_separator.configure(width=2,state="disabled")
by_foldername_var.trace('w',activateFolderCharacterSeparator)

by_embedded_items_var.set(0)
by_embedded_items_checkbox = tk.Checkbutton(window, text='By number of embedded items', variable=by_embedded_items_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,by_embedded_items_checkbox,True)
# by_embedded_items_checkbox.configure(state="disabled")

comparison_var.set('=')
comparison_menu = tk.OptionMenu(window, comparison_var, '=', '<=','>=')
comparison_menu.configure(width=4)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+280,y_multiplier_integer, comparison_menu,True)

number_of_items_lb = tk.Label(window, text='Number of items')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+400,y_multiplier_integer, number_of_items_lb,True)
number_of_items_value = tk.Entry(window, width=2,textvariable=number_of_items_var)
number_of_items_value.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+530,y_multiplier_integer, number_of_items_value,True)

embedded_item_character_value_var.set("_")
embedded_item_character_value_lb = tk.Label(window, text='Separator character(s)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+580,y_multiplier_integer, embedded_item_character_value_lb,True)
embedded_item_character_value = tk.Entry(window, width=2,textvariable=embedded_item_character_value_var)
embedded_item_character_value.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+750,y_multiplier_integer, embedded_item_character_value,True)

include_exclude_var.set(1)
include_exclude_checkbox = tk.Checkbutton(window, variable=include_exclude_var, onvalue=1, offvalue=0, command=lambda: GUI_util.trace_checkbox_NoLabel(include_exclude_var, include_exclude_checkbox, "Include first # items only", "Exclude first # items"))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+850,y_multiplier_integer, include_exclude_checkbox)
include_exclude_checkbox.config(text='Include first # items only',state="disabled")

def activate_numberEmbeddedItems_options(*args):
    number_of_items_var.set(0)
    embedded_item_character_value_var.set('_')
    if by_embedded_items_var.get()==1:
        if split_file_manager_var.get()==False:
            comparison_menu.configure(state="normal")
            number_of_items_value.configure(state="normal")
            include_exclude_checkbox.config(state="normal")
        else:
            comparison_menu.configure(state="disabled")
            number_of_items_value.configure(state="disabled")
            include_exclude_checkbox.config(state="disabled")
        embedded_item_character_value.configure(state="normal")
    else:
        comparison_menu.configure(state="disabled")
        embedded_item_character_value.configure(state="disabled")
        number_of_items_value.configure(state="disabled")
        include_exclude_checkbox.config(state="disabled")
by_embedded_items_var.trace('w',activate_numberEmbeddedItems_options)

# applies to list files only
character_count_file_manager_var.set(0)
character_count_checkbox = tk.Checkbutton(window, text='By number of embedded character(s)', variable=character_count_file_manager_var, onvalue=1, offvalue=0)
character_count_checkbox.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer, character_count_checkbox,True)

characters_entry_lb = tk.Label(window, text='Enter character(s) ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate() + 280,y_multiplier_integer,characters_entry_lb,True)

characters_entry = tk.Entry(window,width=2,textvariable=character_entry_var)
characters_entry.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+ 420,y_multiplier_integer,characters_entry)

def activate_characters_entry_option(*args):
    character_entry_var.set('')
    if character_count_file_manager_var.get()==1:
        characters_entry.configure(state="normal")
    else:
        characters_entry.configure(state="disabled")
character_count_file_manager_var.trace('w',activate_characters_entry_option)

date_format.set('mm-dd-yyyy')
date_separator_var.set('_')
date_position_var.set(2)

fileName_embeds_date_checkbox = tk.Checkbutton(window, text='Filename embeds date', variable=fileName_embeds_date, onvalue=1, offvalue=0)
fileName_embeds_date_checkbox.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer, fileName_embeds_date_checkbox,True)

date_format_lb = tk.Label(window,text='Date format ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+280,y_multiplier_integer, date_format_lb,True)
date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy','yyyy-mm-dd','yyyy-dd-mm','yyyy-mm','yyyy')
date_format_menu.configure(width=10)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate()+80,y_multiplier_integer, date_format_menu,True)

date_separator_lb = tk.Label(window, text='Date character separator ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate()+210,y_multiplier_integer, date_separator_lb,True)
date_separator = tk.Entry(window, textvariable=date_separator_var)
date_separator.configure(width=2)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate()+350,y_multiplier_integer, date_separator,True)

date_position_menu_lb = tk.Label(window, text='Date position ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate()+400,y_multiplier_integer, date_position_menu_lb,True)
date_position_menu = tk.OptionMenu(window,date_position_var,1,2,3,4,5)
date_position_menu.configure(width=2)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate()+490,y_multiplier_integer, date_position_menu)

def check_CoreNLP_dateFields(*args):
    if fileName_embeds_date.get() == 1:
        date_format_menu.config(state="normal")
        date_separator.config(state='normal')
        date_position_menu.config(state='normal')
    else:
        date_format_menu.config(state="disabled")
        date_separator.config(state='disabled')
        date_position_menu.config(state="disabled")
fileName_embeds_date.trace('w',check_CoreNLP_dateFields)

include_subdir_var.set(0)
include_subdir_checkbox = tk.Checkbutton(window, text='Include subdirectories', variable=include_subdir_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,include_subdir_checkbox)

videos_lookup = {'File manager':'NLP_File manager.mp4'}
videos_options = 'File manager'

TIPS_lookup = {'File manager':'TIPS_NLP_File manager.pdf','File handling in NLP Suite': "TIPS_NLP_File handling in NLP Suite.pdf",'Filename checker':'TIPS_NLP_Filename checker.pdf','Filename matcher':'TIPS_NLP_Filename matcher.pdf','File classifier (By date)':'TIPS_NLP_File classifier (By date).pdf','File classifier (By NER)':'TIPS_NLP_File classifier (By NER).pdf','File content checker & converter':'TIPS_NLP_File checker & converter.pdf','Text encoding (utf-8)':'TIPS_NLP_Text encoding (utf-8).pdf','Spelling checker':'TIPS_NLP_Spelling checker.pdf','File merger':'TIPS_NLP_File merger.pdf','File splitter':'TIPS_NLP_File splitter.pdf'}
TIPS_options= 'File manager','File handling in NLP Suite', 'Filename checker', 'Filename matcher', 'File classifier (By date)','File classifier (By NER)','File content checker & converter','Text encoding (utf-8)','Spelling checker','File merger','File splitter'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_csvFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, click to select a csv file containing a list of filenames to be handled by a selected file operation: Rename, Copy, Delete, Count, Split.\n\nThe csv file can contain several columns. Once a csv file has been selected, using the dropdown menu, select the field containing the filenames to be processed.\n\nWHEN THE FILENAME IN THE SELECTED FIELD CONTAINS A FULL PATH, THE SELECTED INPUT FILE DIRECTORY WILL BE IGNORED.\n\nSuch csv file can be obtained, for instance, by using the List option.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkboxes if you wish to check the input text filename for utf-8 compliance. Non utf-8 compliant filename(s) are likely to lead to code breakdown in some scripts.\n\nTick the checkbox to convert non-ASCII apostrophes & quotes. ASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the appropriate checkbox for the file operation you wish to run.\n\nNot all filter options (By_...) are available for all operations (e.g., the filter option 'Filename embeds date' is only available when listing files).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, using the dropdown menu, select the file type to restrict the selected file handling option.\n\nThe 'By file type' option can be used in conjuction with the options 'By prefix value' or 'By sub-string value.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to restrict by file creation/modification date and by author the selected file handling option.\n\nThe 'By author' option is available for Windows Office files only (doc, docx, xls, xlsx, xlsm).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to restrict the selected file handling option by prefix value (e.g., all filenames starting with ._) or sub-string value (e.g., all filenames that contain the string _NLP_SSR_).\n\nAppropriate prefix and sub-string values will need to be entered.\n\nWhen renaming files, the 'New substring for renaming' will also need to be entered.\n\nThe options 'By prefix value' or 'By sub-string value can be used in conjuction with the 'By file type' option.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to rename files in a folder by embedding the LAST PART of folder path in the renamed filename (e.g., The Boston Globe_19-19-1919 found in the subfolder 'John Willis' of a folder path 'c:\mydata\\newspapers\lynching\John Willis' will be remamed as The Boston Globe_19-19-1919__John Willis if __ is selected as the separator character(s).\n\nThe option is available only when renaming files.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to list, copy, move files in a folder by filtering files by the number of items embedded in a filename and separated by specific character(s).\n\nThe user can choose to exclude or include the selected items.\n\nThus, for instance, given the file The Chicago Tribune_17-22-1922_4_3__Ben Treppard, and the options Separator character(s) __, Number of characters 1, and Exclude would result in th filename The Chicago Tribune_17-22-1922_4_3   items embedding the directory name in the renamed filename (e.g., The Boston Globe_19-19-1919 found in the folder John Willis will be remamed as The Boston Globe_19-19-1919__John Willis if __ is selected as the separator character(s).\n\nThe option is available only when listing, copying, moving, or splitting files.\n\nWhen splitting files, all is needed is the 'Separator character(s)' value.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "The 'By number of embedded character(s)' checkbox is available only when listing files in a folder.\n\nWhen available, tick the checkbox to provide a list of files with a count of characters embedded in the filename (e.g., the character _ counted).\n\nOnce ticked, you must enter appropriate character value(s) (e.g. _).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "The 'Filename embeds date' checkbox is available only when listing files in a folder.\n\nWHEN THE OPTION IS SELECTED, SINCE THE DATE FUNCTION AUTOMATICALLY CHECKS EMBEDDED DATES FOR THE CORRECT FORMAT, THE OPTION CAN BE USED TO CHECK THAT FILENAMES HAVE THE CORRECT DATE FORMAT. FAULTY DATES ARE EXPORTED AS BLANK.\n\nWhen available, tick the checkbox if filenames contain a date (e.g., The New York Time_2-18-1872). Once the checkbox is ticked, date options will become available. The date in the filename will then be exported, along with filename and path, to the output csv file that lists all files in a folder.\n\nThe embedded date will be checked automatically to ensure that the date has the correct date format. Detected incorrect dates will be listed with a BLANK date.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to process all files found in the input directory and all its subdirectories.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1

y_multiplier_integer = help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),0)

# change the value of the readMe_message
readMe_message="The Python 3 scripts provide several ways of handling files in a directory:\n\nLIST, RENAME, COPY, MOVE, DELETE, COUNT, SPLIT files in a directory (and subdirectories), by a variety of filename filters.\n\nMore specialized file managment options based on the filename are available as separate tools (e.g., Filename checker, File matcher, File classifier)\n\nAll these tools deal with the name of a file, rather than its content. A number of other tools deal with file content (e.g., File merger, File splitter, File type converter, File utf-8 encoding checker)."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
