
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
import Gephi_util
import wordclouds_util
import GIS_pipeline_util
import reminders_util
import charts_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputDir,outputDir, openOutputFiles, createCharts, chartPackage, setup_simplex,
        ALL_simplex_objects_frequencies_var, SELECTED_simplex_objects_frequencies_var, semantic_triplet_var,
        gephi_var, wordcloud_var, google_earth_var):
    filesToOpen = []
    outputFile = ''

    # create a subdirectory of the output directory; should create a subdir with increasing number to avoid writing ver
    outputDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                                     label='DB_PC-ACE',
                                                                     silent=True)

    if ALL_simplex_objects_frequencies_var:
        outputFile = DB_PCACE_data_analyzer_util.get_simplex_frequencies(setup_simplex_menu, inputDir, outputDir)
    if SELECTED_simplex_objects_frequencies_var:
        outputFile = DB_PCACE_data_analyzer_util.get_simplex_frequencies(setup_simplex, inputDir, outputDir)
    if outputFile!='':
        filesToOpen.append(outputFile)
        headers=IO_csv_util.get_csvfile_headers(outputFile)
        columns_to_be_plotted_xAxis=IO_csv_util.get_headerValue_from_columnNumber(headers,column_number=0)
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFile,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[columns_to_be_plotted_xAxis], columns_to_be_plotted_yAxis=['Frequency'],
                                                           chartTitle='Frequency Distribution of Simplex Object\n' + str(setup_simplex),
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=0, hover_label=[],
                                                           outputFileNameType=str(setup_simplex), #'gender_bar',
                                                           column_xAxis_label=str(setup_simplex),
                                                           groupByList=[],
                                                           plotList=[],
                                                           chart_title_label='')
        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

    if semantic_triplet_var:
        outputFile = DB_PCACE_data_analyzer_util.semantic_triplet_simplex(inputDir, outputDir)
        if outputFile!='':
            filesToOpen.append(outputFile)

        # Gephi ----------------------------------------------------------------------------------------

        if gephi_var:
            svo_result_list=[]
            fileBase = os.path.basename(outputFile)[0:-4]
            nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(outputFile, encodingValue='utf-8')
            if nRecords > 1:  # including headers; file is empty
                gexf_file = Gephi_util.create_gexf(window, fileBase, outputDir, outputFile,
                                                   "Subject (S)", "Verb (V)", "Object (O)") # Sentence ID will be added as the last column
                filesToOpen.append(gexf_file)

            # wordcloud  _________________________________________________

            if wordcloud_var:
                nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(outputFile)
                if nRecords > 1:  # including headers; file is empty
                    myfile = IO_files_util.openCSVFile(outputFile, 'r')
                    out_file = wordclouds_util.SVOWordCloud(myfile, outputFile, outputDir,
                                                            "", prefer_horizontal=.9)
                    myfile.close()
                    filesToOpen.append(out_file)

     # GIS maps _____________________________________________________

    if google_earth_var and (setup_simplex=='City name' or setup_simplex=='County') and SELECTED_simplex_objects_frequencies_var:
        extract_date_from_text_var = 0
        extract_date_from_filename_var = 0
        reminders_util.checkReminder(config_filename, reminders_util.title_options_geocoder,
                                     reminders_util.message_geocoder, True)
        # locationColumnNumber where locations are stored in the csv file; any changes to the columns will result in error
        date_present = (extract_date_from_text_var == True) or (extract_date_from_filename_var == True)
        country_bias = ''
        area_var = ''
        restrict = False
        # TODO temporary for now
        location_filename=os.path.join(outputDir,'NLP_simplex_freq_Dir_Lynching_csv_SQLite.csv')

        if setup_simplex == 'City name':
            IO_csv_util.rename_header(location_filename, 'City name', 'Location')
        if setup_simplex == 'County':
            IO_csv_util.rename_header(location_filename, 'County', 'Location')

        out_file = GIS_pipeline_util.GIS_pipeline(GUI_util.window,
                                                  config_filename, location_filename, inputDir,
                                                  outputDir,
                                                  'Nominatim', 'Google Earth Pro & Google Maps',
                                                  createCharts, chartPackage,
                                                  date_present,
                                                  country_bias,
                                                  area_var,
                                                  restrict,
                                                  'Location', # TODO temporary to be changed
                                                  'utf-8',
                                                  0, 1, [''], [''],
                                                  # group_var, group_number_var, group_values_entry_var_list, group_label_entry_var_list,
                                                  ['Pushpins'], ['red'],
                                                  # icon_var_list, specific_icon_var_list,
                                                  [0], ['1'], [0], [''],
                                                  # name_var_list, scale_var_list, color_var_list, color_style_var_list,
                                                  [1], [1])  # bold_var_list, italic_var_list

        if out_file != None:
            if len(out_file) > 0:
                # since out_file produced by KML is a list cannot use append
                filesToOpen = filesToOpen + out_file

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_chart_output_checkbox.get(),
                                GUI_util.charts_package_options_widget.get(),
                                setup_simplex.get(),
                                ALL_simplex_objects_frequencies_var.get(),
                                SELECTED_simplex_objects_frequencies_var.get(),
                                semantic_triplet_var.get(),
                                gephi_var.get(),wordcloud_var.get(),google_earth_var.get())

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

select_DB_tables_var=tk.StringVar()
select_DB_table_fields_var=tk.StringVar()
view_relations_var=tk.IntVar()

complex_objects_var = tk.StringVar()
simplex_objects_var = tk.StringVar()

ALL_complex_objects_frequencies_var = tk.IntVar()
SELECTED_complex_objects_frequencies_var = tk.IntVar()

ALL_simplex_objects_frequencies_var = tk.IntVar()
SELECTED_simplex_objects_frequencies_var = tk.IntVar()

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
    # select_DB_tables.set('')
    # setup_complex.set('')
    # setup_simplex.set('')
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
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+120,y_multiplier_integer,select_DB_tables)



# simplex_data_text_lb = tk.Label(window, text='Text ')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,simplex_data_text_lb,True)

simplex_data_text_menu = DB_PCACE_data_analyzer_util.get_all_table_names(os.path.join(inputDir.get(),'setup_complex.csv'))

simplex_data_text = ttk.Combobox(window, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
simplex_data_text['values'] = simplex_data_text_menu
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+120, y_multiplier_integer,
                                   simplex_data_text,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate+120,
                                   "Use the dropdown menu to select the simplex TEXT data value for which you want to find simplex & complex objects usage")

# simplex_data_date_lb = tk.Label(window, text='Date ')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate,y_multiplier_integer,simplex_data_date_lb,True)

simplex_data_date_menu = DB_PCACE_data_analyzer_util.get_all_table_names(os.path.join(inputDir.get(),'setup_complex.csv'))

simplex_data_date = ttk.Combobox(window, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
simplex_data_date['values'] = simplex_data_date_menu
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate-10, y_multiplier_integer,
                                   simplex_data_date,
                                   True, False, True, False, 90, GUI_IO_util.setup_IO_brief_coordinate-10,
                                   "Use the dropdown menu to select the simplex DATE data value for which you want to find simplex & complex objects usage")

# simplex_data_number_lb = tk.Label(window, text='Number ')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate,y_multiplier_integer,simplex_data_number_lb,True)

simplex_data_number_menu = DB_PCACE_data_analyzer_util.get_all_table_names(os.path.join(inputDir.get(),'setup_complex.csv'))

simplex_data_number = ttk.Combobox(window, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
simplex_data_number['values'] = simplex_data_number_menu
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate+340, y_multiplier_integer,
                                   simplex_data_number,
                                   False, False, True, False, 90, GUI_IO_util.setup_IO_brief_coordinate-10,
                                   "Use the dropdown menu to select the simplex NUMBER data value for which you want to find simplex & complex objects usage")

complex_objects_lb = tk.Label(window, text='Complex objects ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,complex_objects_lb,True)

setup_complex_menu = DB_PCACE_data_analyzer_util.get_all_table_names(os.path.join(inputDir.get(),'setup_complex.csv'))

setup_complex = ttk.Combobox(window, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
setup_complex['values'] = setup_complex_menu
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+120, y_multiplier_integer,
                                   setup_complex,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to select a specific complex object for which to compute frequencies.\nWhen a hierarchical complex object is selected (e.g., macro-event or event) and the checkbox Semantic triplets below is ticked...\n...semantic triplets will be listed in chronological order within the specific higher-level hierarchical complex object selected (e.g., macro-events, events).")
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+120, y_multiplier_integer,setup_complex)

ALL_complex_objects_checkbox = tk.Checkbutton(window, state='disabled', text='Get value frequencies for ALL objects', variable=ALL_complex_objects_frequencies_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,ALL_complex_objects_checkbox, True)

SELECTED_complex_objects_checkbox = tk.Checkbutton(window, state='disabled', text='Get value frequencies for SELECTED object', variable=SELECTED_complex_objects_frequencies_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+300,y_multiplier_integer,SELECTED_complex_objects_checkbox)

simplex_objects_lb = tk.Label(window, text='Simplex objects ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,simplex_objects_lb, True)

setup_simplex_menu = DB_PCACE_data_analyzer_util.get_all_table_names(os.path.join(inputDir.get(),'setup_simplex.csv'))

setup_simplex = ttk.Combobox(window, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
setup_simplex['values'] = setup_simplex_menu
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+120, y_multiplier_integer,setup_simplex)

ALL_simplex_objects_checkbox = tk.Checkbutton(window, state='disabled', text='Get value frequencies for ALL objects', variable=ALL_simplex_objects_frequencies_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,ALL_simplex_objects_checkbox,True)

SELECTED_simplex_objects_checkbox = tk.Checkbutton(window, text='Get value frequencies for SELECTED object', variable=SELECTED_simplex_objects_frequencies_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+300,y_multiplier_integer,SELECTED_simplex_objects_checkbox)

select_parents_lb = tk.Label(window, text='Parent objects ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,select_parents_lb,True)

select_parents = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=select_parents_var)
select_parents.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+120, y_multiplier_integer,select_parents,True)

select_children_lb = tk.Label(window, text='Children objects ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+500,y_multiplier_integer,select_children_lb,True)

select_children = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=select_children_var)
select_children.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,select_children)

semantic_triplet_checkbox = tk.Checkbutton(window, text='Semantic triplet (SVO)', variable=semantic_triplet_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   semantic_triplet_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox to list in chronological order the semantic triplets within a specific higher-level hierarchical complex object (selected in the Complex objects widget, e.g., event, macro-event).\nWhen no hierarchical complex oject is selected in the Complex objects widget, all triplets are listed for all higher-level hierarchical complex objects (e.g., macro-events, events).")

actors_checkbox = tk.Checkbutton(window, text='Actors', variable=actors_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,actors_checkbox, True)

time_checkbox = tk.Checkbutton(window, text='Time', variable=time_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate,y_multiplier_integer,time_checkbox, True)

space_checkbox = tk.Checkbutton(window, text='Space', variable=space_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate,y_multiplier_integer,space_checkbox)

gephi_var.set(1)
gephi_checkbox = tk.Checkbutton(window, text='Visualize SVO relations in network graphs (via Gephi) ',
                                variable=gephi_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               gephi_checkbox, True)

wordcloud_var.set(1)
wordcloud_checkbox = tk.Checkbutton(window, text='Visualize SVO relations in wordcloud', variable=wordcloud_var,
                                    onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer, wordcloud_checkbox,
                                               True)

google_earth_var.set(1)
google_earth_checkbox = tk.Checkbutton(window, text='Visualize Where (via Google Maps & Google Earth Pro)',
                                       variable=google_earth_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.SVO_3rd_column, y_multiplier_integer,
                                               google_earth_checkbox)

error = False
table_values = []
def changed_filename(*args):
    global error, setup_simplex_menu
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
            SELECTED_simplex_objects_checkbox.configure(state='normal')
            setup_simplex.set(setup_simplex_menu[0])
        else:
            setup_simplex.set('')
            SELECTED_simplex_objects_checkbox.configure(state='disabled')
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

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, click on the View table relations button to open a pdf file visualizing PC-ACE table relations." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, use the dropdown menu to select the PC-ACE table you want to open to inspect its content." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the simplex data value for which you want to see its usage among parent simplex and complex." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "Please, using the dropdown menu, select the COMPLEX object for which you would like to obtain query results." + GUI_IO_util.msg_Esc)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "Please, tick the checkbox for the type of complex object for which you want to compute frequencies." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "Please, using the dropdown menu, select the SIMPLEX object for which you would like to obtain query results." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "Please, tick the checkbox for the type of simplex object for which you want to compute frequencies." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the PARENT object and/or the CHILD object." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox to visualize semantic triplets." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkboxes to visualize actors, time, and space." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkboxes to visualize Subejcts, Verbs, Objects in network graphs and wordclouds, and to visualize space in geographic maps." + GUI_IO_util.msg_Esc)
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

