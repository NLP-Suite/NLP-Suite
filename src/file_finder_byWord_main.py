# written by Roberto Franzosi October 2019, edited Spring 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_finder_byWord_main.py",['os','tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb

import GUI_IO_util
import IO_files_util
import IO_user_interface_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,input_main_dir_path, output_dir_path,
    openOutputFiles,
    createExcelCharts,
    search_by_dictionary_var,
    selectedCsvFile_var,
    search_by_keyword_var,
    lemmatize_var,
    keyword_value_var):

    if search_by_dictionary_var==False and search_by_keyword_var==False:
        mb.showwarning(title='Input error', message='No search options have been selected.\n\nPlease, select a search option and try again.')
        return


    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', "Started running the file search script at", True)


    if input_main_dir_path=='' and inputFilename!='':
        inputDir=os.path.dirname(inputFilename)
        files=[inputFilename]
    elif input_main_dir_path!='':
        inputDir=input_main_dir_path
        files= IO_files_util.getFileList(inputFilename, inputDir, 'txt')
    if len(files) == 0:
        return

    #print("files",files)
    for file in files:
        #print("file",file)
        if search_by_dictionary_var:
            break
        if search_by_keyword_var:
            output_dir_path = inputDir + os.sep + "search_result_csv"
            if not os.path.exists(output_dir_path):
                os.mkdir(output_dir_path)
            if file[-4:]=='.txt':
                import file_finder_byWord_util
                file_finder_byWord_util.run(file, output_dir_path, keyword_value_var, lemmatize_var)
                    
            
    IO_user_interface_util.timed_alert(GUI_util.window, 2000, "Analysis end", "Finished running the file search script at", True)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_Excel_chart_output_checkbox.get(),
                            search_by_dictionary_var.get(),
                            selectedCsvFile_var.get(),
                            search_by_keyword_var.get(),
                            lemmatize_var.get(),
                            keyword_value_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

GUI_size='1100x470'
GUI_label='Graphical User Interface (GUI) for File Search by Single Word or Collocations'
config_filename='search-byWord-config.txt'
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
config_option=[0,6,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

# GUI CHANGES add following lines to every special GUI
# +2 is the number of lines starting at 1 of IO widgets
y_multiplier_integer=GUI_util.y_multiplier_integer+2
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
input_main_dir_path =GUI_util.input_main_dir_path
output_dir_path =GUI_util.output_dir_path

GUI_util.GUI_top(config_input_output_options,config_filename)

search_by_dictionary_var=tk.IntVar()
selectedCsvFile_var=tk.StringVar()
search_by_keyword_var=tk.IntVar()
lemmatize_var=tk.IntVar()
keyword_value_var=tk.StringVar()

def clear(e):
	GUI_util.clear("Escape")
window.bind("<Escape>", clear)


#setup GUI widgets

search_by_dictionary_var.set(0)
search_by_dictionary_checkbox = tk.Checkbutton(window, text='Search file by dictionary value', variable=search_by_dictionary_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,search_by_dictionary_checkbox)

dictionary_button=tk.Button(window, width=20, text='Select dictionary file',command=lambda: get_dictionary_file(window,'Select INPUT dictionary file', [("dictionary files", "*.csv")]))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20, y_multiplier_integer,dictionary_button,True)

def get_dictionary_file(window,title,fileType):
	filePath = tk.filedialog.askopenfilename(title = title, initialdir = os.getcwd(), filetypes = fileType)
	if len(filePath)>0:
		#always disabled; user cannot tinker with the selection
		#selectedCsvFile.config(state='disabled')
		selectedCsvFile_var.set(filePath)

#setup a button to open Windows Explorer on the selected input directory
current_y_multiplier_integer2=y_multiplier_integer-1
openInputFile_button  = tk.Button(window, width=3, text='', command=lambda: IO_files_util.openFile(window, selectedCsvFile_var.get()))
openInputFile_button.place(x=GUI_IO_util.get_labels_x_coordinate()+180, y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

selectedCsvFile = tk.Entry(window,width=100,state='disabled',textvariable=selectedCsvFile_var)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,selectedCsvFile)

search_by_keyword_var.set(0)
search_by_keyword_checkbox = tk.Checkbutton(window, text='Search file by single words/collocations', variable=search_by_keyword_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,search_by_keyword_checkbox)

lemmatize_var.set(0)
lemmatize_checkbox = tk.Checkbutton(window, text='Lemmatize', variable=lemmatize_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,lemmatize_checkbox,True)

keyword_value_var.set('')
keyword_value = tk.Entry(window,width=100,textvariable=keyword_value_var)
keyword_value.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,keyword_value)

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


TIPS_lookup = {'No TIPS available':''}
TIPS_options='No TIPS available'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
	clearOptions="\n\nTo clear a previously selected option for any of the tools, click on the appropriate dropdown menu and press ESCape."
	GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",GUI_IO_util.msg_anyFile)
	GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_anyData)
	GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help",GUI_IO_util.msg_outputDirectory)
	GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*3,"Help", "Please, tick the checkbox to search input txt file(s) using the values contained in a csv dictionary file.")
	GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*4,"Help", "Please, click to select a csv file containing a list of values to be used as a dictionary for searching the file(s).\n\nEntries in the file, one per line, can be single words or collocations, i.e., combinations of words such as 'coming out,' 'standing in line'.")
	GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*5,"Help","Please, tick the checkbox to search input txt file(s) by single words or collocations, i.e., combinations of words such as 'coming out,' 'standing in line'.")
	GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*6,"Help","Please, tick the checkbox to lemmatize the single words or collocations entered. When lemmatizing, the scripts would search 'coming out' in all its lemmatized forms: 'coming out', 'come out', 'comes out', 'came out'.\n\nPlease, also enter word(s) in the data entry widget.")
	GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*7,"Help",GUI_IO_util.msg_openOutputFiles)
help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="These Python 3 scripts search txt files by single words or collocations (e.g., a set of multiple words, such as 'coming out' or 'standing in line'). Search words can be entered in a csv dictionary or manually in the GUI enter widget.\n\nIn INPUT the scripts expect a single txt file or a set of txt files in a directory.\n\nIn OUTPUT the scripts generate a csv file with information about the document, sentence, word/collocation searched, and, most importantly, about the relative position where the search word appears in the text."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options)

# a reminder is in file_manager_merger_splitter_main
#	reminders_util.checkReminder("Split output files")

GUI_util.window.mainloop()

