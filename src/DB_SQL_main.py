import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_packages(GUI_util.window, "DB_SQL_main.py", ['os', 'tkinter','pandas','sqlite3'])==False:
	sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
import sqlite3, pandas as pd

import IO_csv_util
import IO_files_util
import GUI_IO_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def dbFromCSV(inpath, outpath):

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
					   message='There are no csv files in the input directory!')
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
		df = pd.read_csv(inpath + os.sep + t + ".csv")
		df.to_sql(name=tableName, con=conn, index=False)

	print("Database saved as", dbOutput)

	cur.close()
	conn.close()
	return dbOutput


def run(inputDir,outputDir, openOutputFiles, createExcelCharts,SQL_query_var, createFromCSV):

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
		# IO_util.timed_alert(GUI_util.window,3000,'Analysis start','Started running Nominalization at',True)
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
			IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)


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
								GUI_util.create_Excel_chart_output_checkbox.get(),
								SQL_query_entry.get("1.0", "end-1c"),
								construct_SQLite_DB_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

GUI_size='1100x620'
GUI_label='Graphical User Interface (GUI) for Relational Database SQL queries'
config_filename='DB-SQL-config.txt'

# The 6 values of config_option refer to:
#   software directory
#   input file
        # 1 for CoNLL file
        # 2 for TXT file
        # 3 for csv file
        # 4 for any type of file
        # 5 for txt or html
        # 6 for txt or csv
#   input dir 0 no dir 1 dir
#   input secondary dir 0 no dir 1 dir
#   output file 0 no file 1 file
#   output dir 0 no dir 1 dir
config_option=[0,0,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

# GUI CHANGES add following lines to every special GUI
# +1 is the number of lines starting at 1 of IO widgets
y_multiplier_integer=GUI_util.y_multiplier_integer+1
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_options,config_filename)

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

def get_SQLite_file(window,title,fileType):
	#annotator_dictionary_var.set('')
	filePath = tk.filedialog.askopenfilename(title = title, initialdir =GUI_IO_util.namesGender_libPath, filetypes = fileType)
	if len(filePath)>0:
		SQLite_DB_file.config(state='normal')
		select_SQLite_DB_var.set(filePath)

construct_SQLite_DB_checkbox = tk.Checkbutton(window, text='Construct SQLite database', variable=construct_SQLite_DB_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,construct_SQLite_DB_checkbox)

select_SQLite_DB_button=tk.Button(window, width=23, text='Select SQLite database',command=lambda: get_SQLite_file(window,'Select INPUT SQLite file', [("SQLite files", "*.sqlite")]))
# select_SQLite_DB_button.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,select_SQLite_DB_button,True)

openInputFile_button  = tk.Button(window, width=3, state='disabled', text='', command=lambda: IO_files_util.openFile(window, select_SQLite_DB_var.get()))
openInputFile_button.place(x=GUI_IO_util.get_labels_x_coordinate()+190, y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

SQLite_DB_file=tk.Entry(window, width=100,textvariable=select_SQLite_DB_var)
SQLite_DB_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+250, y_multiplier_integer,SQLite_DB_file)

table_menu_values = []
def get_table_list(*args):
    select_DB_table_fields_menu.configure(state='disabled')
    if select_SQLite_DB_var.get()=='':
        select_DB_tables_menu.configure(state='disabled')
        return
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

select_DB_tables_lb = tk.Label(window, text='Select DB table ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,select_DB_tables_lb,True)
if len(table_menu_values)==0:
    select_DB_tables_menu = tk.OptionMenu(window, select_DB_tables_var, table_menu_values)
else:
    select_DB_tables_menu = tk.OptionMenu(window,select_DB_tables_var, *table_menu_values)
select_DB_tables_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+100,y_multiplier_integer,select_DB_tables_menu,True)

table_fields_menu_values = []

def get_table_fields_list(*args):
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
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+350,y_multiplier_integer,select_DB_table_fields_lb,True)
if len(table_fields_menu_values)==0:
    select_DB_table_fields_menu = tk.OptionMenu(window, select_DB_table_fields_var, table_fields_menu_values)
else:
    select_DB_table_fields_menu = tk.OptionMenu(window,select_DB_table_fields_var, *table_fields_menu_values)
select_DB_table_fields_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+480,y_multiplier_integer,select_DB_table_fields_menu,True)

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
        filePath = tk.filedialog.asksaveasfile(initialdir=GUI_util.output_dir_path.get(), initialfile='saveQry.txt', title="Save SQL query file",
                                               filetypes=[('SQL query file','.txt')])
        if filePath is None:
            filePath = ""
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

import_query_button=tk.Button(window, width=15, text='Import SQL query',command=lambda: import_query(window,'Select INPUT SQL query file', [("SQL files", "*.txt")]))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+700, y_multiplier_integer,import_query_button,True)

save_query_button=tk.Button(window, width=15, text='Save SQL query',command=lambda: save_query())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+850, y_multiplier_integer,save_query_button)

SQL_query_entry = tk.Text(window,width=120,height=10)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,SQL_query_entry)

y_multiplier_integer=y_multiplier_integer+3.5

auto_SQL_var=tk.StringVar()
auto_SQL_lb = tk.Label(window, text='Select SQL query type (template)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,auto_SQL_lb,True)
auto_SQL_value = tk.OptionMenu(window,auto_SQL_var,'SQL standard','SQL count', 'SQL duplicates', 'SQL unmatched', 'SQL union', 'SQL join')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+250, y_multiplier_integer,auto_SQL_value,True)

distinct_checkbox = tk.Checkbutton(window, text='Distinct', variable=distinct_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+400,y_multiplier_integer,distinct_checkbox,True)

# view_relations_button = tk.Button(window, text='View table relations', width=5,height=1,state='disabled',command=lambda: clear_DBpedia_YAGO_class_list())
view_relations_button = tk.Button(window, text='View table relations', width=20,height=1,state='normal', command=lambda: view_relations())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+500,y_multiplier_integer,view_relations_button)

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


TIPS_lookup = {'No TIPS available':''}
TIPS_options='No TIPS available'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help", GUI_IO_util.msg_corpusData)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help", GUI_IO_util.msg_outputDirectory)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help", "Please, click on the Construct SQLlite button to construct an SQLite database from a set of INPUT csv files." + GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*3,"Help", "Please, click on the Select SQLite database button to select the database you want to work with.\n\nAn SQLite database has extension sqlite." + GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*4,"Help", "Please, using the 'Select DB table' dropdown menu, select the table available in the SQLite database.\n\nOnce an SQLite table has been selected, use the 'Select DB table field' dropdown menu to select a specific field available in the selected table.\n\nClick on the Import SQL query button to import a previously saved query.\n\nClick on the Save SQL query button to save the query currently available in the query text box." + GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*5,"Help", "Please, enter an SQL query in the form SELECT ...\n\nYou can visualize a preset template query, using the dropdown menu 'Select the type of SQL query'."+ GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(9.5),"Help", "Please, using the dropdown menu, select the type of SQL query for which to display a standard template. You will name to change table names and field names to the appropriate nams in your database.\n\nTick the Distinct checkbox to display the SQL query as distinct."+ GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*10.5,"Help",GUI_IO_util.msg_openOutputFiles)

"COUNT Display a template SQL COUNT query."
"DUPLICATES The query builds a temporary table of duplicate records, then, depending on user's choice, extracts only one occurrence of all duplicate records or all duplicate occurrences except one (all DISTINCT records will not be displayed). Query results can be used to move occurrences of objects for which multiples should not be allowed."
"UNMATCHED Automatically build a simple query that will give a list of all unmatched records between any two given tables/queries on the basis of a specific field (MEMO type fields cannot be matched!)\n\nThe query will give you a list of the fields in the first selected table/query that do not find a match in the second selected table/query."

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="This Python 3 script can construct an SQLite relational database from a set of input csv files characterized by the presence of overlaping relational fields.\n\nThe script allows to perform SQL queries on any sqlite databases thus constructed."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options)

GUI_util.window.mainloop()
