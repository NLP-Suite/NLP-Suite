# Written by Brett Landau, Fall 2020
# edited Austin Cai, Fall 2021

import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_packages(GUI_util.window, "DB_SQL_main.py", ['os', 'tkinter','pandas','sqlite3'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
import sqlite3, pandas as pd
from subprocess import call

import IO_csv_util
import IO_files_util
import GUI_IO_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def dbFromCSV(inpath, outpath):
    inpath=inpath.get()
    outpath=outpath.get()
    dbFileName = os.path.basename(os.path.normpath(inpath)) + ".sqlite"
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

    conn = sqlite3.connect(dbOutput)
    cur = conn.cursor()
    for t in tableList:
        # Replace dashes with underscore, SQLite bug.
        tableName = t.replace("-", "_")
        # Read in fullpath of csv file
        df = pd.read_csv(inpath + os.sep + t + ".csv", encoding='utf-8', error_bad_lines=False)
        df.to_sql(name=tableName, con=conn, index=False)

    print("Database saved as", dbOutput)

    cur.close()
    conn.close()
    return dbOutput


def run(inputDir,outputDir, openOutputFiles, createCharts, chartPackage,SQL_query_var, createFromCSV):

    if createFromCSV==1:
        dbOutput = dbFromCSV(inputDir,outputDir)
        if dbOutput != -1:
            # != -1 means that the DB was created successfully, we can use it.
            # Use the newly created DB to fill in the sqlite selection box
            select_SQLite_DB_var.set(dbOutput)
            # Uncheck the box
            construct_SQLite_DB_var.set(0)
            mb.showwarning(title='Alert',
                           message='Your DB has been created and is selected for use. You may now input and run queries.')
    elif select_SQLite_DB_var.get() != "":
        # IO_util.timed_alert(GUI_util.window,2000,'Analysis start','Started running Nominalization at',True)
        print("SQL_query_var", SQL_query_var)
        dbVar = select_SQLite_DB_var.get()
        conn = sqlite3.connect(dbVar)
        cur = conn.cursor()
        colNames = []
        results = []
        try:
            # SQL_query_var contains the query a user has entered
            sql_rows = cur.execute(SQL_query_var)
        except:
            # Exception as e:
            # print("error: ", e.__doc__)
            mb.showwarning(title='Warning',
                           message='The query you are running did not execute properly. If you are running a template query selected from the dropdown menu of the \'Select the type of SQL query\' widget, you will need to change the table names to the table names in your database.\n\nPlease, check your query and try again.')
            return
        for col in cur.description:
            # .description returns column names from the resulting SQL query
            # Each column is a 7-tuple, but we just need the first index to get it's name
            colNames.append(col[0])
        results.append(colNames)
        for row in sql_rows:
            results.append(row)
        filesToOpen=[outputDir+os.sep+'sql_result.csv']
        IO_csv_util.list_to_csv(GUI_util.window, results, outputDir+os.sep+'sql_result.csv', colnum=0)
        if openOutputFiles:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)


        cur.close()
        conn.close()
    else:
        mb.showwarning(title='Warning',
                       message='No SQLite database selected.\n\nPlease, select an SQLite file or tick the checkbox the \'Construct an SQLite database\'.')

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_chart_output_checkbox.get(),
                                GUI_util.charts_package_options_widget.get(),
                                SQL_query_entry.get("1.0", "end-1c"),
                                construct_SQLite_DB_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(3),
                                                 GUI_height_brief=660, # height at brief display
                                                 GUI_height_full=700, # height at full display
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
    SQL_query_var.set('')
    SQL_query_entry.delete(0.1, tk.END)
    select_DB_tables_var.set('')
    select_DB_table_fields_var.set('')
    GUI_util.tips_dropdown_field.set('Open TIPS files')
window.bind("<Escape>", clear)

# TODO Anna please add comments about what this function does
def get_SQLite_file(window,title,fileType):
    #annotator_dictionary_var.set('')
    filePath = tk.filedialog.askopenfilename(title = title, initialdir =inputDir, filetypes = fileType)
    if len(filePath)>0:
        SQLite_DB_file.config(state='normal')
        select_SQLite_DB_var.set(filePath)

construct_SQLite_DB_button=tk.Button(window, width=23, text='Construct SQLite database',command=lambda: dbFromCSV(inputDir,outputDir))
#construct_SQLite_DB_checkbox = tk.Checkbutton(window, text='Construct SQLite database', variable=construct_SQLite_DB_var, onvalue=1, offvalue=0)
#y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,construct_SQLite_DB_checkbox)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,construct_SQLite_DB_button)

select_SQLite_DB_button=tk.Button(window, width=23, text='Select SQLite database',command=lambda: get_SQLite_file(window,'Select INPUT SQLite file', [("SQLite files", "*.sqlite")]))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,select_SQLite_DB_button,True)

openInputFile_button = tk.Button(window, width=3, state='disabled', text='', command=lambda: IO_files_util.openFile(window, select_SQLite_DB_var.get()))
# place widget with hover-over info
# the button widget has hover-over effects (no_hover_over_widget=False) and the info displayed is in text_info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+200, y_multiplier_integer,openInputFile_button,True, False, True,False, 90, GUI_IO_util.labels_x_coordinate+190, "Open INPUT SQLite database")

SQLite_DB_file=tk.Entry(window, width=GUI_IO_util.SQLite_DB_file_width,textvariable=select_SQLite_DB_var)
SQLite_DB_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+250, y_multiplier_integer,SQLite_DB_file)

table_menu_values = []
# TODO Anna please add comments about what this function does
def get_table_list(*args):
    select_DB_table_fields_menu.configure(state='disabled')
    if select_SQLite_DB_var.get()=='':
        select_DB_tables_menu.configure(state='disabled')
        return
    # get_complex_simplex_list('setup_Complex')
    select_DB_tables_menu.configure(state='normal')
    conn = sqlite3.connect(select_SQLite_DB_var.get())
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
    # construct menu values
    for row in cur:
        table_menu_values.append(row[0])
    cur.close()
    conn.close()
    m = select_DB_tables_menu["menu"]
    m.delete(0, "end")
    for s in table_menu_values:
        m.add_command(label=s, command=lambda value=s: select_DB_tables_var.set(value))
select_SQLite_DB_var.trace('w',get_table_list)

# TODO Anna, I tried to get a list of row values in setup_Complex or setup_Simplex but... could not get it to work
# TODO  please finish the function
def get_complex_simplex_list(tableName):
    if select_SQLite_DB_var.get() == '':
        return
    conn = sqlite3.connect(select_SQLite_DB_var.get())
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT Name FROM '%s'" % tableName)
    # construct menu values
    # fields is a list of the column names from input tableName
    r = cur.fetchone()
    fields = r.keys()
    table_fields_menu_values = fields
    cur.close()
    m = select_DB_table_fields_menu["menu"]
    m.delete(0, "end")
    for s in table_fields_menu_values:
        m.add_command(label=s, command=lambda value=s: select_DB_table_fields_var.set(value))
    conn.close()
    menu=''
    return menu

# complex_objects_lb = tk.Label(window, text='Select complex object ')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,complex_objects_lb,True)

complex_objects_var = tk.StringVar()
menu = get_complex_simplex_list('setup_Complex')
complex_objects = tk.OptionMenu(window,complex_objects_var, menu)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+200, y_multiplier_integer,
                                   complex_objects,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to select a specific complex object for which to compute frequencies.\nWhen a hierarchical complex objcet is selectd (e.g., macro-event or event) and the checkbox Semantic triplets is ticked, semantic triplets will be listed in chronological order within a specific higher-level hierarchical complex object selected (e.g., macro-events, events).")

# simplex_objects_lb = tk.Label(window, text='Select simplex object ')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,simplex_objects_lb,True)

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
    conn = sqlite3.connect(select_SQLite_DB_var.get())
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM '%s'" % tableName)
    # construct menu values
    # fields is a list of the column names from input tableName
    r = cur.fetchone()
    fields = r.keys()
    table_fields_menu_values=fields
    cur.close()
    m = select_DB_table_fields_menu["menu"]
    m.delete(0, "end")
    for s in table_fields_menu_values:
        m.add_command(label=s, command=lambda value=s: select_DB_table_fields_var.set(value))
    conn.close()
    SQL_query_entry.insert(SQL_query_entry.index(tk.INSERT), tableName)

select_DB_tables_var.trace('w',get_table_fields_list)
def get_table_fields_name(*args):
    SQL_query_entry.insert(SQL_query_entry.index(tk.INSERT), select_DB_table_fields_var.get())

select_DB_table_fields_var.trace('w',get_table_fields_name)


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
    if len(filePath) > 0:
        SQL_query_entry.delete(0.1, tk.END)
        with open(filePath, 'r', encoding='utf_8', errors='ignore') as file:
            importedQuery = file.read()
        SQL_query_var.set(importedQuery)
        SQL_query_entry.insert("end", str(importedQuery))

def save_query():
    boxContent = SQL_query_entry.get(0.1, tk.END)
    if len(boxContent)>0:
        filePath = tk.filedialog.asksaveasfile(initialdir=inputDir, initialfile='saveQry.txt', title="Save SQL query file",
                                               filetypes=[('SQL query file','.sql')])
        if filePath is None:
            filePath = ""
        else:
            filePath = str(filePath.name)

        if len(filePath)>0:
            with open(filePath, 'w+', encoding='utf_8', errors='ignore') as file:
                file.seek(0)
                file.write(boxContent)
                file.close()
            mb.showwarning(title='Warning',
                           message='The SQL query has been saved to\n\n' + filePath)

def view_relations():
    if select_SQLite_DB_var.get() == "":
        mb.showwarning(title='Warning', message='No DB file has been selected! Cannot view relations.')
    else:
        view_rels_command = ['C:\\Program Files\\DBeaver\\dbeaver-cli.exe', '-con', 'driver=sqlite|database='+select_SQLite_DB_var.get()]
        call(view_rels_command)

import_query_button=tk.Button(window, width=15, text='Import SQL query',command=lambda: import_query(window,'Select INPUT SQL query file', [("SQL files", "*.sql")]))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+700, y_multiplier_integer,import_query_button,True)

save_query_button=tk.Button(window, width=15, text='Save SQL query',command=lambda: save_query())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+850, y_multiplier_integer,save_query_button)

SQL_query_entry = tk.Text(window,width=120,height=10)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,SQL_query_entry)

y_multiplier_integer=y_multiplier_integer+3.5

auto_SQL_var=tk.StringVar()
auto_SQL_lb = tk.Label(window, text='Select SQL query type (template)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,auto_SQL_lb,True)
auto_SQL_value = tk.OptionMenu(window,auto_SQL_var,'SQL standard','SQL count', 'SQL duplicates', 'SQL unmatched', 'SQL union', 'SQL join')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+250, y_multiplier_integer,auto_SQL_value,True)

distinct_checkbox = tk.Checkbutton(window, text='Distinct', variable=distinct_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+400,y_multiplier_integer,distinct_checkbox,True)

# view_relations_button = tk.Button(window, text='View table relations', width=5,height=1,state='disabled',command=lambda: clear_DBpedia_YAGO_class_list())
view_relations_button = tk.Button(window, text='View table relations', width=20,height=1,state='normal', command=lambda: view_relations())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+500,y_multiplier_integer,view_relations_button)

def display_SQL(*args):
    SQL_query_entry.delete(0.1, tk.END)
    SQL_text=''
    if auto_SQL_var.get()!='':
        if distinct_var.get()==True:
            SQL_text='SELECT DISTINCT '
        else:
            SQL_text='SELECT '
    if auto_SQL_var.get()=="SQL standard":
        SQL_text=SQL_text+ '[Field1], [Field2], [Field3], ...\n  FROM [table]\n  WHERE [field2] = "string value"\n  ORDER BY [Field1], [Field3] DESC;'
    elif auto_SQL_var.get()== "SQL count":
        SQL_text=SQL_text+ "[field1], COUNT([Field1]) AS FREQUENCY\n  FROM [table]\n  GROUP BY [field1]\n  ORDER BY COUNT([field1]) DESC;"
    elif auto_SQL_var.get()=="SQL duplicates":
        SQL_text=SQL_text+ "[1].[field1], [1].[field2], [1].[field3], ...\n  FROM [table] AS [1] INNER JOIN (SELECT [table].[Field1]\n  GROUP BY [table].[Field1]\n  HAVING (COUNT([table].[Field1]) > 1)) AS [2] ON [1].[Field1]=[2].[Field1]\n  ORDER BY [1].[Field1], [1].[Field2], [1].[Field3], ... DESC;"
    elif auto_SQL_var.get()=="SQL unmatched":
        mb.showwarning(title='Warning',
                       message='A template query for unmatched records is currently not available.\n\nSorry!')
        return
    elif auto_SQL_var.get()=="SQL union":
        SQL_text=SQL_text+ "Table1_Field_Name AS Field1\n  FROM Table_Name1\n\nUNION\n\nSELECT Table2_Field_Name AS Field1\n  FROM Table_Name2\n  ORDER BY Field1;"
    elif auto_SQL_var.get()=="SQL join":
        SQL_text=SQL_text+ "Table1_Field_Name1, Table1_Field_Name2, ...\n  FROM Table_Name1\n  JOIN Table_Name2 ON [Table_Name1].[Table1_Field_Name1]=[Table_Name2].[Table2_Field_Name2]"
    else:
        SQL_query_var.set('')
        SQL_query_entry.delete(0.1, tk.END)
    SQL_query_var.set(SQL_text)
    SQL_query_entry.insert("end", str(SQL_text))
auto_SQL_var.trace('w',display_SQL)
#SQL_query_var.trace('w',display_SQL)

display_SQL()

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

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, using the 'Select DB table' dropdown menu, select the table available in the SQLite database.\n\nOnce an SQLite table has been selected, use the 'Select DB table field' dropdown menu to select a specific field available in the selected table.\n\nClick on the Import SQL query button to import a previously saved query.\n\nClick on the Save SQL query button to save the query currently available in the query text box.\n\nSaved and imported queries will be of file type .txt." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, enter an SQL query in the form SELECT ...\n\nYou can visualize a preset template query, using the dropdown menu 'Select the type of SQL query'."+ GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer+3.5,"NLP Suite Help", "Please, using the dropdown menu, select the type of SQL query for which to display a standard template. You will need to change table names and field names to the appropriate names in your database.\n\nTick the Distinct checkbox to display the SQL query as distinct.\n\nClick on the View table relations button to visualize the table relations via their overlapping IDs. "+ GUI_IO_util.msg_Esc)
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
