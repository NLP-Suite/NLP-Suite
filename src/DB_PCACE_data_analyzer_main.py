
import sys
import IO_libraries_util
import GUI_util

# if IO_libraries_util.install_all_Python_packages(GUI_util.window, "DB_PC-ACE_data_analyzer_main.py", ['os', 'tkinter','pandas'])==False:
#     sys.exit(0)

import os
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

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
import IO_user_interface_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputDir,outputDir, openOutputFiles, createCharts, chartPackage,
        simplex_data_type, simplex_data,
        primary_complex_var,
        value_parent_object_var,
        setup_complex,setup_simplex,
        # print_narrative_var,
        ALL_objects_frequencies_var, SELECTED_objects_frequencies_var,
        ALL_simplex_objects_frequencies_var, SELECTED_simplex_objects_frequencies_var,
        select_parents_var, select_children_var,
        semantic_triplet_var,
        actors_var, time_var, space_var,
        gephi_var, wordcloud_var, google_earth_var,
        comments_var,
        document_sources_var):

    filesToOpen = []
    outputFile = ''

    if select_DB_tables_var.get()!='':
        IO_files_util.openFile(window, inputDir + os.sep + select_DB_tables_var.get() + ".xlsx")
        return

    outputDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                                     label='DB_PC-ACE',
                                                                     silent=True)

    # complex frequencies
    if ALL_objects_frequencies_var:
        outputFile = DB_PCACE_data_analyzer_util.get_complex_frequencies_all(inputDir, outputDir)
        if outputFile != '':
            filesToOpen.append(outputFile)
        outputFile = DB_PCACE_data_analyzer_util.get_simplex_frequencies_all(inputDir, outputDir)
        if outputFile!='':
            filesToOpen.append(outputFile)
    if SELECTED_objects_frequencies_var:
        if setup_complex!='':
            outputFile = DB_PCACE_data_analyzer_util.get_complex_frequencies(setup_complex, inputDir, outputDir)
        elif setup_simplex!='':
            outputFile = DB_PCACE_data_analyzer_util.get_simplex_frequencies(setup_simplex, inputDir, outputDir)
        else:
            mb.showwarning(title='Warning',
                   message="You must first select a specific complex or simplex object to run this function.\n\n"
                           "Please, select an object and try again.")
            return
        if outputFile != '':
            filesToOpen.append(outputFile)
    if simplex_data!='' and value_parent_object_var:
        outputFile = DB_PCACE_data_analyzer_util.individual_simplex_info_main(simplex_data, inputDir, outputDir)
        if outputFile!='':
            filesToOpen.append(outputFile)
        # headers=IO_csv_util.get_csvfile_headers(outputFile)
        # columns_to_be_plotted_xAxis=IO_csv_util.get_headerValue_from_columnNumber(headers,column_number=0)
        # chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFile,
        #                                                    outputDir,
        #                                                    columns_to_be_plotted_xAxis=[columns_to_be_plotted_xAxis], columns_to_be_plotted_yAxis=['Frequency'],
        #                                                    chart_title='Frequency Distribution of Simplex Object\n' + str(simplex_data),
        #                                                    # count_var = 1 for columns of alphabetic values
        #                                                    count_var=1, hover_label=[],
        #                                                    outputFileNameType=str(simplex_data), #'gender_bar',
        #                                                    column_xAxis_label=str(simplex_data),
        #                                                    groupByList=[],
        #                                                    plotList=[],
        #                                                    chart_title_label='')
        # if chart_outputFilename!=None:
        #     if len(chart_outputFilename) > 0:
        #         filesToOpen.extend(chart_outputFilename)

    if semantic_triplet_var:
        outputFile = ''
        if time_var and space_var:
            outputFile = DB_PCACE_data_analyzer_util.semantic_triplet_time_space(inputDir, outputDir, primary_complex_var)
        elif time_var:
            outputFile = DB_PCACE_data_analyzer_util.semantic_triplet_time(inputDir, outputDir, primary_complex_var)
        elif space_var:
            outputFile = DB_PCACE_data_analyzer_util.semantic_triplet_space_main(inputDir, outputDir, primary_complex_var)
        else: # only SVO
            outputFile = DB_PCACE_data_analyzer_util.semantic_triplet_simplex_main(inputDir, outputDir, primary_complex_var)

        if outputFile != '':
            filesToOpen.append(outputFile)

    # Gephi ----------------------------------------------------------------------------------------

        if gephi_var:
            svo_result_list=[]
            fileBase = os.path.basename(outputFile)[0:-5]
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
            filename_embeds_date_var = 0
            reminders_util.checkReminder(scriptName, reminders_util.title_options_geocoder,
                                         reminders_util.message_geocoder, True)
            # locationColumnNumber where locations are stored in the csv file; any changes to the columns will result in error
            date_present = (extract_date_from_text_var == True) or (filename_embeds_date_var == True)
            country_bias = ''
            area_var = ''
            restrict = False
            # TODO temporary for now
            location_filename=os.path.join(outputDir,'NLP_simplex_freq_Dir_Lynching_csv_SQLite.xlsx')

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

# actors ----------------------------------------------------------------------

    if actors_var != '':
        if actors_var == '*' or actors_var == 'collective actor':
            outputFile = DB_PCACE_data_analyzer_util.collective_actor_characteristics(inputDir, outputDir)
            if outputFile != '':
                filesToOpen.append(outputFile)
        if actors_var == '*' or actors_var == 'individual':
            outputFile = DB_PCACE_data_analyzer_util.individual_characteristics(inputDir, outputDir)
            if outputFile != '':
                filesToOpen.append(outputFile)
        if actors_var == '*' or actors_var == 'organization':
            outputFile = DB_PCACE_data_analyzer_util.organization_characteristics_main(inputDir, outputDir)
            if outputFile != '':
                filesToOpen.append(outputFile)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_chart_output_checkbox.get(),
                                GUI_util.charts_package_options_widget.get(),
                                simplex_data_type_var.get(),
                                simplex_data.get(),
                                primary_complex_var.get(),
                                value_parent_object_var.get(),
                                setup_complex.get(),
                                setup_simplex.get(),
                                # print_narrative_var.get(),
                                ALL_objects_frequencies_var.get(),
                                SELECTED_objects_frequencies_var.get(),
                                ALL_simplex_objects_frequencies_var.get(),
                                SELECTED_simplex_objects_frequencies_var.get(),
                                select_parents_var.get(),
                                select_children_var.get(),
                                semantic_triplet_var.get(),
                                actors_var.get(),
                                time_var.get(),
                                space_var.get(),
                                gephi_var.get(),wordcloud_var.get(),google_earth_var.get(),
                                comments_var.get(),
                                document_sources_var.get())

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
config_filename = scriptName.replace('_main.py', '_config.csv')

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

ALL_objects_frequencies_var = tk.IntVar()
SELECTED_objects_frequencies_var = tk.IntVar()

value_parent_object_var = tk.IntVar()

ALL_simplex_objects_frequencies_var = tk.IntVar()
SELECTED_simplex_objects_frequencies_var = tk.IntVar()

complex_parent_var = tk.IntVar()
complex_child_var = tk.IntVar()
simplex_complex_var = tk.IntVar()
semantic_triplet_var = tk.IntVar()
actors_var = tk.StringVar()
time_var = tk.IntVar()
space_var = tk.IntVar()

select_parents_var = tk.StringVar()
select_children_var = tk.StringVar()
gephi_var = tk.IntVar()
wordcloud_var = tk.IntVar()
google_earth_var = tk.IntVar()

def clear(e):
    value_parent_object_var.set(0)
    setup_complex=''
    setup_simplex=''
    select_DB_tables_var.set('')

    simplex_data_type_var.set('')
    simplex_list=[]
    simplex_data_menu_var.set('')
    value_parent_object_var.set(0)

    select_parents_var.set('')
    select_children_var.set('')

    # print_narrative_var.set(0)

    ALL_objects_frequencies_var.set(0)
    SELECTED_objects_frequencies_var.set(0)

    semantic_triplet_var.set(0)
    gephi_var.set(0)
    wordcloud_var.set(0)
    google_earth_var.set(0)
    time_var.set(0)
    space_var.set(0)

    actors_var.set('')

    setup_complex_var.set('')
    setup_simplex_var.set('')

    actors_var.set('')

    comments_var.set('')

    document_sources_var.set(0)
    GUI_util.clear("Escape")

    GUI_util.tips_dropdown_field.set('Open TIPS files')
window.bind("<Escape>", clear)

table_list = []
table_menu_list = []

view_relations_button = tk.Button(window, text='View table relations', width=20,height=1,state='normal', command=lambda: view_relations())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   view_relations_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to open a pdf file of the PC-ACE table relations")

# https://www.geeksforgeeks.org/convert-excel-to-csv-in-python/
# view_relations_button = tk.Button(window, text='Convert PC-ACE Excel tables to csv  ', height=1,state='normal', command=lambda: view_relations())
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
#                                    view_relations_button,
#                                    True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
#                                    "Click to convert the Excel files exported from Microsoft ACCESS database to csv files for use in this GUI")

select_DB_tables_lb = tk.Label(window, text='PC-ACE table ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,y_multiplier_integer,select_DB_tables_lb,True)

table_menu_values = ''
table_list=[]
if os.path.isdir(inputDir.get()):
    table_list = DB_PCACE_data_analyzer_util.import_PCACE_tables(inputDir.get())
    table_menu_values = ", ".join(table_list)
select_DB_tables = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=select_DB_tables_var)
select_DB_tables.configure(state='disabled')
select_DB_tables['values'] = table_menu_values
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+350, y_multiplier_integer,
                                   select_DB_tables,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate+120,
                                   "Use the dropdown menu to select a PC-ACE table to be opened for display; click RUN after selection.")

simplex_data_type_lb = tk.Label(window, text='PC-ACE data type ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,simplex_data_type_lb,True)

simplex_data_type_var= tk.StringVar()
simplex_data_type_menu = tk.OptionMenu(window, simplex_data_type_var, 'text','date', 'number')
simplex_data_type_var.set('')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+120, y_multiplier_integer,
                                   simplex_data_type_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_S_dictionary,
                                   "Use the dropdown menu to select the data type to be used to extract a list of values.")

simplex_data_menu_var = tk.StringVar()
simplex_list = DB_PCACE_data_analyzer_util.give_Simplex_text_date_number(simplex_data_type_var.get(), os.path.join(inputDir.get(),'data_SimplexText.xlsx'), os.path.join(inputDir.get(),'data_SimplexDate.xlsx'), os.path.join(inputDir.get(),'data_SimplexNumber.xlsx'))
simplex_data_menu_var.set(simplex_list)
simplex_data_menu = ttk.Combobox(window, textvariable = simplex_data_menu_var, width=GUI_IO_util.widget_width_short)
# simplex_data_menu = DB_PCACE_data_analyzer_util.get_all_table_names(os.path.join(inputDir.get(),'setup_simplex.csv'))
# simplex_data_menu = DB_PCACE_data_analyzer_util.give_Simplex_text_date_number(simplex_data_menu_var, data_SimplexText, data_SimplexDate, data_SimplexNumber)

simplex_data = ttk.Combobox(window, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
simplex_data['values'] = simplex_data_menu
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+350, y_multiplier_integer,
                                   simplex_data,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate+300,
                                   "Use the dropdown menu to select the simplex data type value (e.g., police) for which you want to find simplex & complex objects usage")

def activate_date_number_text(*args):
    simplex_list = DB_PCACE_data_analyzer_util.give_Simplex_text_date_number(simplex_data_type_var.get(),
                                    os.path.join(inputDir.get(),
                                             'data_SimplexText.xlsx'),
                                     os.path.join(inputDir.get(),
                                              'data_SimplexDate.xlsx'),
                                     os.path.join(inputDir.get(),
                                            'data_SimplexNumber.xlsx'))
    simplex_data_menu_var.set(simplex_list)
    simplex_data['values'] = simplex_list
simplex_data_type_var.trace('w',activate_date_number_text)

value_parent_object_checkbox = tk.Checkbutton(window, text='Get simplex/complex objects of selected data type (& value)', variable=value_parent_object_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   value_parent_object_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Tick the checkbox to export simplex and complex objects that use the selected data type and, perhaps, value")

primary_complex_objects_lb = tk.Label(window, text='Primary complex (Macro event)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,primary_complex_objects_lb,True)

primary_complex_menu = '' # DB_PCACE_data_analyzer_util.build_macro_event_dropdown_menu(inputDir.get())

primary_complex_var=tk.StringVar()
primary_complex = ttk.Combobox(window, textvariable = primary_complex_var, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
primary_complex['values'] = primary_complex_menu
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   primary_complex,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to select a specific primary complex object (Macro event) to analyze.\nWhen a specific macro event is selected, all analyses (e.g., SVO, actors) will be based on that macro event.")

def set_visualization():
    if semantic_triplet_var.get()==1:
        gephi_var.set(1)
        wordcloud_var.set(1)
        google_earth_var.set(1)
    else:
        gephi_var.set(0)
        wordcloud_var.set(0)
        google_earth_var.set(0)

semantic_triplet_var_checkbox = tk.Checkbutton(window, text='Semantic triplets (SVO)', variable=semantic_triplet_var, onvalue=1, offvalue=0, command=lambda: set_visualization())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   semantic_triplet_var_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox to extract semantic triplets/SVOs (i.e., combinations of Subject, Verb, Object).\nWhen a specific macro event is selected, SVOs will be extracted for that specific macro event.")

time_checkbox = tk.Checkbutton(window, text='Time', variable=time_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   time_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox to extract the time of action.\nWhen a specific macro event is selected, the time will be extracted for that specific macro event.")

space_checkbox = tk.Checkbutton(window, text='Space', variable=space_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+350, y_multiplier_integer,
                                   space_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox to extract the space of action.\nWhen a specific macro event is selected, the space will be extracted for that specific macro event.")

gephi_var.set(0)
gephi_checkbox = tk.Checkbutton(window, text='Visualize SVO relations in network graphs (via Gephi) ',
                                variable=gephi_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+20, y_multiplier_integer,
                                   gephi_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox to visualize the triplet SVOs as a network graph in Gephi")

wordcloud_var.set(0)
wordcloud_checkbox = tk.Checkbutton(window, text='Visualize SVO relations in wordcloud', variable=wordcloud_var,
                                    onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+350, y_multiplier_integer,
                                   wordcloud_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate+350,
                                   "Tick the checkbox to visualize the triplet SVOs in a wordcloud")

google_earth_var.set(0)
google_earth_checkbox = tk.Checkbutton(window, text='Visualize Where (via Google Maps & Google Earth Pro)',
                                       variable=google_earth_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   google_earth_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Tick the checkbox to visualize the space of SVOs as in a Google Earth Pro pin map and Google Maps heat map")

actors_lb = tk.Label(window, text='Extract actors ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,actors_lb,True)

actors_var.set('')
actors_menu = tk.OptionMenu(window, actors_var, '*', 'collective actor', 'individual', 'organization')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                   actors_menu,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to select the type of actor you want to extract ")

complex_objects_lb = tk.Label(window, text='Complex ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,complex_objects_lb,True)

setup_complex_menu = DB_PCACE_data_analyzer_util.get_all_table_names(os.path.join(inputDir.get(),'setup_complex.xlsx'))

setup_complex_var=tk.StringVar()
setup_complex = ttk.Combobox(window, textvariable = setup_complex_var, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
setup_complex['values'] = setup_complex_menu
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+120, y_multiplier_integer,
                                   setup_complex,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to select a specific complex object for which to compute frequencies.\nWhen a hierarchical complex object is selected (e.g., macro-event or event) and the checkbox Semantic triplets below is ticked...\n...semantic triplets will be listed in chronological order within the specific higher-level hierarchical complex object selected (e.g., macro-events, events).")


simplex_objects_lb = tk.Label(window, text='Simplex ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,simplex_objects_lb, True)

setup_simplex_menu = DB_PCACE_data_analyzer_util.get_all_table_names(os.path.join(inputDir.get(),'setup_simplex.xlsx'))

setup_simplex_var = tk.StringVar()

setup_simplex = ttk.Combobox(window, textvariable = setup_simplex_var, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
setup_simplex['values'] = setup_simplex_menu
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   setup_simplex,
                                   False, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Use the dropdown menu to select a specific simplex object for which to compute frequencies")


# print_narrative_var = tk.StringVar()
# print_narrative_var.set(0)
# print_narrative_checkbox = tk.Checkbutton(window, text='Print selected complex object in narrative form', variable=print_narrative_var, onvalue=1, offvalue=0)
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,print_narrative_checkbox)

ALL_complex_objects_checkbox = tk.Checkbutton(window, text='Get value frequencies for ALL objects', variable=ALL_objects_frequencies_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   ALL_complex_objects_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Tick the checkbox to extract the value frequencies for ALL objects (complex & simplex)")

SELECTED_complex_objects_checkbox = tk.Checkbutton(window, text='Get value frequencies for SELECTED object', variable=SELECTED_objects_frequencies_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                   SELECTED_complex_objects_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Tick the checkbox to extract the value frequencies for a SELECTED object (complex OR simplex)")

select_parents_lb = tk.Label(window, text='Parents ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,select_parents_lb,True)

select_parents = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=select_parents_var)
# select_parents.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+120, y_multiplier_integer,
                                   select_parents,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "The menu displays a list of complex objects parent of the 'Complex objects' or 'Simplex objects' selected in the widgets above")

select_children_lb = tk.Label(window, text='Children ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,select_children_lb,True)

select_children = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=select_children_var)
# select_children.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   select_children,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "The menu displays a list of complex objects children of the 'Complex objects' selected in the widget above.\nThe option is only available for the 'Complex objects' widget above.")

def activate_children(*args):
    parent_complex_list = []
    parent_simplex_list = []
    parent_complex_list = DB_PCACE_data_analyzer_util.find_parent_complex(setup_complex_var.get(),inputDir.get())
    parent_simplex_list = DB_PCACE_data_analyzer_util.find_parent_simplex(setup_simplex_var.get(),inputDir.get())
    parent_menu_values = ''
    if len(parent_complex_list)>0:
        parent_menu_values = ", ".join(parent_complex_list)
    if len(parent_simplex_list)>0:
        parent_menu_values = ", ".join(parent_simplex_list)
    select_parents['values'] = parent_menu_values

    children_list = []
    children_menu_values = ''
    children_list = DB_PCACE_data_analyzer_util.find_child_complex(setup_complex_var.get(),inputDir.get())
    children_menu_values = ", ".join(children_list)
    select_children['values'] = children_menu_values
    # select_children_var.set(children_menu[0])
setup_complex_var.trace('w',activate_children)
setup_simplex_var.trace('w',activate_children)

comments_lb = tk.Label(window, text='Extract comments ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,comments_lb,True)

comments_var = tk.StringVar()
comments_var.set('')
comments_menu = tk.OptionMenu(window, comments_var, '*', 'users comments', 'verifiers comments')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                   comments_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Use the dropdown menu to extract the comments left by users and/or verifiers ")

# verifier_comments_var = tk.IntVar()
# verifier_comments_checkbox = tk.Checkbutton(window, text='Get verifiers comments ', variable=verifier_comments_var, onvalue=1, offvalue=0)
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,verifier_comments_checkbox)

document_sources_var = tk.IntVar()
document_sources_checkbox = tk.Checkbutton(window, text='Extract document sources ', variable=document_sources_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   document_sources_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox to extract the documents (e.g., newspaper articles) that are the sources of information for specific objects. ")

error = False
table_values = []
def changed_filename(*args):
    global error, setup_simplex_menu
    # 25 PC-ACE files
    if GUI_util.input_main_dir_path.get()!='':
        GUI_util.run_button.configure(state='normal')
        table_list = DB_PCACE_data_analyzer_util.import_PCACE_tables(inputDir.get())
        # 25 files including all comments files
        if (len(table_list) == 0) or ((len(table_list) > 18) and (not "data_Document.xlsx" in str(table_list) and not "data_Complex.xlsx" in str(table_list))):
                GUI_util.run_button.configure(state='disabled')
                table_menu_values=[]
                error = True
        else:
            for table in table_list:
                # keep only table name and Strip off the .csv extension
                table_values.append(table[:len(table)-5])
            table_menu_values = table_values # ", ".join(table_values)
            select_DB_tables['values'] = table_menu_values
        if len(table_menu_values)>0:
            select_DB_tables.configure(state='normal')
            select_DB_tables.set(table_menu_values[0])
            select_DB_tables.set('')

        else:
            select_DB_tables.set('')
            select_DB_tables.configure(state='disabled')
        setup_complex_menu = DB_PCACE_data_analyzer_util.get_all_table_names(os.path.join(inputDir.get(), 'setup_complex.xlsx'))
        setup_complex['values'] = setup_complex_menu
        if len(setup_complex_menu)>0:
            setup_complex.configure(state='normal')
            # setup_complex.set(setup_complex_menu[0])
            setup_complex.set('')
        else:
            setup_complex.set('')
            setup_complex.configure(state='disabled')
        setup_simplex_menu = DB_PCACE_data_analyzer_util.get_all_table_names(os.path.join(inputDir.get(), 'setup_simplex.xlsx'))
        setup_simplex['values'] = setup_simplex_menu
        if len(setup_simplex_menu)>0:
            setup_simplex.configure(state='normal')
            # setup_simplex.set(setup_simplex_menu[0])
            setup_simplex_var.set('')
        else:
            setup_simplex.set('')
            setup_simplex.configure(state='disabled')
    else:
        if inputFilename.get()!='':
            GUI_util.run_button.configure(state='disabled')
            error = True
GUI_util.inputFilename.trace('w', changed_filename)
GUI_util.input_main_dir_path.trace('w', changed_filename)

table_fields_menu_values = []

def view_relations():
    TIPS_util.open_TIPS('TIPS_NLP_PC-ACE table relations.pdf')

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'PC-ACE tables to Pandas':'TIPS_NLP_PC-ACE tables to Pandas.pdf'}
TIPS_options='PC-ACE tables to Pandas'

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

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, click on the View table relations button to open a pdf file visualizing PC-ACE table relations." +
                                "\n\nUse the dropdown menu to open a selected table file." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the simplex data value (text, date, or number) "
                            "for which you want to see its usage among parent simplex and complex."
                            "\n\nThe available values will be displayed in the next dropdown menu widget where you can select a specific value."
                            "\n\nYou can then tick the 'Get simplex/complex objects...' checkbox if you wish to visualize all simplex and complex ojects that use the selected value (e.g.,'police') " + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "The dropdown menu displays all the PRIMARY COMPLEX objects (Macro events)." + GUI_IO_util.msg_Esc)
    # SVO + time + space
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "Please, tick the checkbox to extract Subject, Verb, Objet relations (semantic triplet) and the time and space of action.\n\nWhen a primary complex (or macro event) has been selected, SVOs, time, and space will be selected for the selected macro event only." + GUI_IO_util.msg_Esc)
    # SVO visualization
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkboxes to visualize Subjects, Verbs, Objects in network graphs and wordclouds, and to visualize space in geographic maps." + GUI_IO_util.msg_Esc)
    # actors
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, use the dropdown menu to select the type of actor for which you wish to extract all instances of semantic triplets, i.e., Subject-Verb-Object combinations (* for all types of actors)." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "The dropdown menu displays all the COMPLEX or SIMPLEX objects parent and children of the objects selected in the 'Complex objects' or 'Simplex objects' dropdown menu widgets." + GUI_IO_util.msg_Esc)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "Please, tick the 'Get value frequencies for ALL objects' checkbox to compute the frequencies of all available complex and simplex objects."
                                                         "\n\nTick the 'Get value frequencies for SELECTED object' checkbox to compute the frequencies of the selected Complex or Simplex object." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the PARENT object and/or the CHILD object." + GUI_IO_util.msg_Esc)
    # comments
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, use the dropdown menu to extract the users and/or visualize Verifiers comments." + GUI_IO_util.msg_Esc)
    # documents
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox to extract the documents (e.g., newspaper articles) that are the sources of information for specific objects." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer -1
"COUNT Display a template SQL COUNT query."
"DUPLICATES The query builds a temporary table of duplicate records, then, depending on user's choice, extracts only one occurrence of all duplicate records or all duplicate occurrences except one (all DISTINCT records will not be displayed). Query results can be used to move occurrences of objects for which multiples should not be allowed."
"UNMATCHED Automatically build a simple query that will give a list of all unmatched records between any two given tables/queries on the basis of a specific field (MEMO type fields cannot be matched!)\n\nThe query will give you a list of the fields in the first selected table/query that do not find a match in the second selected table/query."

y_multiplier_integer = y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,increment)

# change the value of the readMe_message
readMe_message="The Python 3 scripts convert, via the Python Pandas package, and analyze, via various visualization packages, data collected via the Microsoft Access PC-ACE (Program for Computer-Assisted Coding of Events).\n\nIn INPUT the algorithms expect a set of xlsx files exported from the PC-ACE database tables data, setup, and utility.\n\nIn OUTPUT the algorithms produce a set of csv files and different types of visuals, from Excel charts to network graphs via Gephi and Sankey, geographic pin maps via Google Earth Pro and heat maps via Google Maps, wordclouds, and interactive time maps."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

changed_filename()
if error:
    error = True
    # check to see if there is a GUI-specific config file and set it to the setup_IO_menu_var
    if os.path.isfile(os.path.join(GUI_IO_util.configPath, config_filename)):
        GUI_util.setup_IO_menu_var.set('GUI-specific I/O configuration')
        mb.showwarning(title='Warning',
                       message="The PC-ACE table analyzer scripts require in input a directory of Excel (xlsx) files. But the directory in 'Default I/O configuration' does not contain the required PC-ACE Excel files.\n\n"
                                "Since a GUI-specific " + config_filename + " file is available, the I/O configuration has been automatically set to GUI-specific I/O configuration.")
        error = False
IO_user_interface_util.timed_alert(window, 1000, 'Warning',
                                   'Loading data... Please wait...',
                                   False, '', False, '', False)
primary_complex_menu = DB_PCACE_data_analyzer_util.build_macro_event_dropdown_menu(inputDir.get())
primary_complex['values'] = primary_complex_menu
GUI_util.window.mainloop()

