
import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_packages(GUI_util.window, "DB_PC-ACE_data_analyzer_main.py", ['os', 'tkinter','pandas'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
import pandas as pd
from subprocess import call

import IO_csv_util
import IO_files_util
import GUI_IO_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def dbFromCSV(inpath, outpath):
    inpath=inpath.get()
    outpath=outpath.get()
    dbOutput = outpath + os.sep + dbFileName
    dirSearch = os.listdir(inpath)
    tableList = []

    for file in dirSearch:
        # Only include .csv files from the input dir
        if ".csv" in file and len(file) > 4:
            # Strip off the .csv extension
            tableList.append(file[:len(file) - 4])
    if len(tableList) == 0:
        mb.showwarning(title='Warning',
                       message='There are no csv files in the input directory.\n\nThe script expects a set of csv files with overlapping ID fields across files in order to construct an SQLite relational database.\n\nPlease, select an input directory that contains csv files and try again.')
        return -1
    print("Found", len(tableList), ".csv files, creating database...")

    if os.path.exists(dbOutput):
        # Delete the DB if it already exists, we will replace it.
        os.unlink(dbOutput)

    # for t in tableList:
    #     # Replace dashes with underscore, SQLite bug.
    #     tableName = t.replace("-", "_")
    #     # Read in fullpath of csv file
    #     df = pd.read_csv(inpath + os.sep + t + ".csv", encoding='utf-8', error_bad_lines=False)
    #     df.to_sql(name=tableName, con=conn, index=False)

    print("Database saved as", dbOutput)

def run(inputDir,outputDir, openOutputFiles, createCharts, chartPackage):
    print('')

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_chart_output_checkbox.get(),
                                GUI_util.charts_dropdown_field.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(3),
                                                 GUI_height_brief=400, # height at brief display
                                                 GUI_height_full=460, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=1, # to be added for full display
                                                 increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Relational Database SQL queries'
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
#   input dir 0 no dir 1 dir
#   input secondary dir 0 no dir 1 dir
#   output dir 0 no dir 1 dir
config_input_output_numeric_options=[0,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
inputDir=GUI_util.input_main_dir_path
outputDir=GUI_util.output_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

construct_SQLite_DB_var=tk.IntVar()
select_SQLite_DB_var=tk.StringVar()
select_DB_tables_var=tk.StringVar()
select_DB_table_fields_var=tk.StringVar()
SQL_query_var=tk.StringVar()
distinct_var=tk.IntVar()
view_relations_var=tk.IntVar()

def clear(e):
    GUI_util.tips_dropdown_field.set('Open TIPS files')
window.bind("<Escape>", clear)


table_menu_values = []
# TODO Anna please add comments about what this function does
def get_table_list(*args):
    select_DB_table_fields_menu.configure(state='disabled')
    if select_SQLite_DB_var.get()=='':
        select_DB_tables_menu.configure(state='disabled')
        return
    # get_complex_simplex_list('setup_Complex')
    # construct menu values
select_SQLite_DB_var.trace('w',get_table_list)

# TODO Anna, I tried to get a list of row values in setup_Complex or setup_Simplex but... could not get it to work
# TODO  please finish the function
def get_complex_simplex_list(tableName):
    if select_SQLite_DB_var.get() == '':
        return
    menu=''
    return menu

complex_objects_lb = tk.Label(window, text='Select complex object ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,complex_objects_lb,True)

complex_objects_var = tk.StringVar()
menu = get_complex_simplex_list('setup_Complex')
complex_objects = tk.OptionMenu(window,complex_objects_var, menu)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+200, y_multiplier_integer,complex_objects)

simplex_objects_lb = tk.Label(window, text='Select simplex object ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,simplex_objects_lb,True)

simplex_objects_var = tk.StringVar()
menu = get_complex_simplex_list('setup_Simplex')
simplex_objects = tk.OptionMenu(window,simplex_objects_var, menu)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+200, y_multiplier_integer,simplex_objects)

select_DB_tables_lb = tk.Label(window, text='Select DB table ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,select_DB_tables_lb,True)
if len(table_menu_values)==0:
    select_DB_tables_menu = tk.OptionMenu(window, select_DB_tables_var, table_menu_values)
else:
    select_DB_tables_menu = tk.OptionMenu(window,select_DB_tables_var, *table_menu_values)
select_DB_tables_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+100,y_multiplier_integer,select_DB_tables_menu,True)

table_fields_menu_values = []

# TODO Anna please add comments about what this function does
def get_table_fields_list():
    tableName=select_DB_tables_var.get()
    if tableName=='':
        select_DB_table_fields_menu.configure(state='disabled')
        return
    select_DB_table_fields_menu.configure(state='normal')

select_DB_tables_var.trace('w',get_table_fields_list)

select_DB_table_fields_lb = tk.Label(window, text='Select DB table field')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+350,y_multiplier_integer,select_DB_table_fields_lb,True)
if len(table_fields_menu_values)==0:
    select_DB_table_fields_menu = tk.OptionMenu(window, select_DB_table_fields_var, table_fields_menu_values)
else:
    select_DB_table_fields_menu = tk.OptionMenu(window,select_DB_table_fields_var, *table_fields_menu_values)
select_DB_table_fields_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+480,y_multiplier_integer,select_DB_table_fields_menu,True)

def import_query(window, title, fileType):
    filePath = tk.filedialog.askopenfilename(title=title, initialdir=GUI_util.input_main_dir_path,
                                             filetypes=fileType)

distinct_checkbox = tk.Checkbutton(window, text='Distinct', variable=distinct_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+800,y_multiplier_integer,distinct_checkbox)

def view_relations():
    return

# view_relations_button = tk.Button(window, text='View table relations', width=5,height=1,state='disabled',command=lambda: clear_DBpedia_YAGO_class_list())
view_relations_button = tk.Button(window, text='View table relations', width=20,height=1,state='normal', command=lambda: view_relations())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,view_relations_button)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'No TIPS available':''}
TIPS_options='No TIPS available'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, click on the Construct SQLlite button to construct an SQLite database from a set of INPUT csv files." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, click on the Select SQLite database button to select the database you want to work with.\n\nAn SQLite database has extension sqlite." + GUI_IO_util.msg_Esc)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "Please, using the dropdown menu, select the COMPLEX object for which you would like to obtain query results." + GUI_IO_util.msg_Esc)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "Please, using the dropdown menu, select the SIMPLEX object for which you would like to obtain query results." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer -1
"COUNT Display a template SQL COUNT query."
"DUPLICATES The query builds a temporary table of duplicate records, then, depending on user's choice, extracts only one occurrence of all duplicate records or all duplicate occurrences except one (all DISTINCT records will not be displayed). Query results can be used to move occurrences of objects for which multiples should not be allowed."
"UNMATCHED Automatically build a simple query that will give a list of all unmatched records between any two given tables/queries on the basis of a specific field (MEMO type fields cannot be matched!)\n\nThe query will give you a list of the fields in the first selected table/query that do not find a match in the second selected table/query."

y_multiplier_integer = y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,increment)

# change the value of the readMe_message
readMe_message="This Python 3 script can construct an SQLite relational database from a set of input csv files characterized by the presence of overlapping relational fields.\n\nThe script allows to perform SQL queries on any sqlite databases thus constructed."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
