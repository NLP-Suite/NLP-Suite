
import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_packages(GUI_util.window, "DB_PC-ACE_data_analyzer_main.py", ['os', 'tkinter','pandas'])==False:
    sys.exit(0)

import os
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
import pandas as pd
from subprocess import call

import IO_csv_util
import IO_files_util
import GUI_IO_util
import TIPS_util
import DB_PCACE_data_analyzer_util

# RUN section ______________________________________________________________________________________________________________________________________________________

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
                                                 GUI_height_brief=720, # height at brief display
                                                 GUI_height_full=760, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=1, # to be added for full display
                                                 increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for PC-ACE Tables Analyzer (via Pandas)'
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
view_relations_var=tk.IntVar()


simplex_objects_var = tk.StringVar()
complex_objects_var = tk.StringVar()

complex_frequencies_var = tk.IntVar()
simplex_frequencies_var = tk.IntVar()

complex_parent_var = tk.IntVar()
complex_child_var = tk.IntVar()
simplex_complex_var = tk.IntVar()
semantic_triplet_var = tk.IntVar()
actors_var = tk.IntVar()
time_var = tk.IntVar()
space_var = tk.IntVar()

select_parents_var = tk.StringVar()
select_children_var = tk.StringVar()
gephi_var = tk.IntVar()
wordcloud_var = tk.IntVar()
google_earth_var = tk.IntVar()

def clear(e):
    select_DB_tables.set('')
    setup_complex.set('')
    setup_simplex.set('')
    GUI_util.tips_dropdown_field.set('Open TIPS files')
window.bind("<Escape>", clear)

table_list = []
table_menu_list = []

view_relations_button = tk.Button(window, text='View table relations', width=20,height=1,state='normal', command=lambda: view_relations())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,view_relations_button)

select_DB_tables_lb = tk.Label(window, text='Select DB table ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,select_DB_tables_lb,True)

table_menu_values = ''
table_list=[]
if os.path.isdir(inputDir.get()):
    table_list = DB_PCACE_data_analyzer_util.import_PCACE_tables(inputDir.get())
    table_menu_values = ", ".join(table_list)
select_DB_tables = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=select_DB_tables_var)
select_DB_tables.configure(state='disabled')
select_DB_tables['values'] = table_menu_values
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+200,y_multiplier_integer,select_DB_tables)

complex_objects_lb = tk.Label(window, text='Select complex object ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,complex_objects_lb,True)

setup_complex_menu = DB_PCACE_data_analyzer_util.get_all_table_names(os.path.join(inputDir.get(),'setup_complex.csv'))

setup_complex = ttk.Combobox(window, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
setup_complex['values'] = setup_complex_menu
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+200, y_multiplier_integer,setup_complex, True)

complex_objects_checkbox = tk.Checkbutton(window, text='Get value frequencies', variable=complex_frequencies_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+600,y_multiplier_integer,complex_objects_checkbox)

def activate_complex_label(*args):
    if complex_frequencies_var.get():
        complex_objects_checkbox.configure(text='Get value frequencies for SELECTED object')
    else:
        complex_objects_checkbox.configure(text='Get value frequencies for ALL objects')
complex_frequencies_var.trace('w',activate_complex_label)

simplex_objects_lb = tk.Label(window, text='Select simplex object ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,simplex_objects_lb,True)

setup_simplex_menu = DB_PCACE_data_analyzer_util.get_all_table_names(os.path.join(inputDir.get(),'setup_simplex.csv'))

setup_simplex = ttk.Combobox(window, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
setup_simplex['values'] = setup_simplex_menu
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+200, y_multiplier_integer,setup_simplex, True)

simplex_objects_checkbox = tk.Checkbutton(window, text='Get value frequencies', variable=simplex_frequencies_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+600,y_multiplier_integer,simplex_objects_checkbox)

def activate_simplex_label(*args):
    if simplex_frequencies_var.get():
        simplex_objects_checkbox.configure(text='Get value frequencies for SELECTED object')
    else:
        simplex_objects_checkbox.configure(text='Get value frequencies for ALL objects')
simplex_frequencies_var.trace('w',activate_simplex_label)

select_parents_lb = tk.Label(window, text='Select parent objects ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,select_parents_lb,True)

select_parents = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=select_parents_var)
select_parents.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+200, y_multiplier_integer,select_parents)

select_children_lb = tk.Label(window, text='Select children objects ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,select_children_lb,True)

select_children = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=select_children_var)
select_children.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+200, y_multiplier_integer,select_children)

semantic_triplet_checkbox = tk.Checkbutton(window, text='Semantic triplet (SVO)', variable=semantic_triplet_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,semantic_triplet_checkbox)

actors_checkbox = tk.Checkbutton(window, text='Actors', variable=actors_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,actors_checkbox)

time_checkbox = tk.Checkbutton(window, text='Time', variable=time_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,time_checkbox)

space_checkbox = tk.Checkbutton(window, text='Space', variable=space_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,space_checkbox)

gephi_var.set(1)
gephi_checkbox = tk.Checkbutton(window, text='Visualize SVO relations in network graphs (via Gephi) ',
                                variable=gephi_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               gephi_checkbox, True)

wordcloud_var.set(1)
wordcloud_checkbox = tk.Checkbutton(window, text='Visualize SVO relations in wordcloud', variable=wordcloud_var,
                                    onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.SVO_2nd_column, y_multiplier_integer, wordcloud_checkbox,
                                               True)

google_earth_var.set(1)
google_earth_checkbox = tk.Checkbutton(window, text='Visualize Where (via Google Maps & Google Earth Pro)',
                                       variable=google_earth_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.SVO_3rd_column, y_multiplier_integer,
                                               google_earth_checkbox)

error = False
table_values = []
def changed_filename(*args):
    global error
    # 25 PC-ACE files
    if GUI_util.input_main_dir_path.get()!='':
        GUI_util.run_button.configure(state='normal')
        table_list = DB_PCACE_data_analyzer_util.import_PCACE_tables(inputDir.get())
        # 25 files including all comments files
        if (len(table_list) == 0) or ((len(table_list) > 18) and (not "data_Document.csv" in str(table_list) and not "data_Complex.csv" in str(table_list))):
                GUI_util.run_button.configure(state='disabled')
                table_menu_values=[]
                error = True
        else:
            for table in table_list:
                # keep only table name and Strip off the .csv extension
                table_values.append(table[:len(table)-4])
            table_menu_values = table_values # ", ".join(table_values)
            select_DB_tables['values'] = table_menu_values
        if len(table_menu_values)>0:
            select_DB_tables.configure(state='normal')
            select_DB_tables.set(table_menu_values[0])
        else:
            select_DB_tables.set('')
            select_DB_tables.configure(state='disabled')
        setup_complex_menu = DB_PCACE_data_analyzer_util.get_all_table_names(os.path.join(inputDir.get(), 'setup_complex.csv'))
        setup_complex['values'] = setup_complex_menu
        if len(setup_complex_menu)>0:
            setup_complex.configure(state='normal')
            setup_complex.set(setup_complex_menu[0])
        else:
            setup_complex.set('')
            setup_complex.configure(state='disabled')
        setup_simplex_menu = DB_PCACE_data_analyzer_util.get_all_table_names(os.path.join(inputDir.get(), 'setup_simplex.csv'))
        setup_simplex['values'] = setup_simplex_menu
        if len(setup_simplex_menu)>0:
            setup_simplex.configure(state='normal')
            setup_simplex.set(setup_simplex_menu[0])
        else:
            setup_simplex.set('')
            setup_simplex.configure(state='disabled')
    else:
        if inputFilename.get()!='':
            GUI_util.run_button.configure(state='disabled')
            error = True
GUI_util.inputFilename.trace('w', changed_filename)
GUI_util.input_main_dir_path.trace('w', changed_filename)

changed_filename()

table_fields_menu_values = []

def view_relations():
    TIPS_util.open_TIPS('TIPS_NLP_PC-ACE table relations.pdf')

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
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
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

if error:
    mb.showwarning(title='Warning',
                   message="The PC-ACE Table Analyzer scripts require in input a set of csv PC-ACE tables in a directory.\n\nPlease, select in input a PC-ACE tables directory and try again.")
    select_DB_tables.configure(state='disabled')
    setup_complex.configure(state='disabled')
    setup_simplex.configure(state='disabled')
    error = False
GUI_util.window.mainloop()

