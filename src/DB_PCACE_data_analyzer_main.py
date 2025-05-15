
import sys
import IO_libraries_util
import GUI_util

# if IO_libraries_util.install_all_Python_packages(GUI_util.window, "DB_PC-ACE_data_analyzer_main.py", ['os', 'tkinter','pandas'])==False:
#     sys.exit(0)

import os
import pandas as pd

import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb


import IO_csv_util
import IO_files_util
import GUI_IO_util
import TIPS_util
import DB_PCACE_data_analyzer_util
import Gephi_util
import GIS_pipeline_util
import reminders_util
import charts_util
import IO_user_interface_util

# RUN section ______________________________________________________________________________________________________________________________________________________
def run(inputDir,outputDir, openOutputFiles, chartPackage, dataTransformation,
        simplex_data_type, simplex_data,
        primary_complex_var,
        value_parent_object_var,
        setup_complex,setup_simplex,
        # print_narrative_var,
        ALL_objects_frequencies_var, SELECTED_objects_frequencies_var,
        ALL_simplex_objects_frequencies_var, SELECTED_simplex_objects_frequencies_var,
        select_parents_var, select_children_var,
        semantic_triplet_var,
        semantic_triplet_subject,
        semantic_triplet_verb,
        semantic_triplet_object,
        actors_var, time_var, time_label_var, space_var, space_label_var,
        gephi_var, wordcloud_var, google_earth_var,
        comments_var,
        document_sources_var):

    config_filename = GUI_util.config_filename_selected_config.get()

    filesToOpen = []
    outputFile = ''

    import os
    if select_DB_tables_var.get()!='':
        IO_files_util.openFile(window, inputDir + os.sep + select_DB_tables_var.get() + ".xlsx")
        return

    outputDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                                     label='DB_PC-ACE',
                                                                     silent=False)
    if outputDir == '':
        return

    # compute frequencies of complex/simplex objects ______________________________________________________________________________

    # complex frequencies
    # all frequencies
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

# display information about a specific simplex type and value (e.g., text type for burley value) _____________________________________________________________

    if simplex_data!='' and value_parent_object_var:
        outputFile = DB_PCACE_data_analyzer_util.individual_simplex_info_main(simplex_data, inputDir, outputDir)
        if outputFile!='':
            filesToOpen.append(outputFile)
        headers=IO_csv_util.get_csvfile_headers(outputFile)
        columns_to_be_plotted_xAxis=IO_csv_util.get_headerValue_from_columnNumber(headers,column_number=0)
        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFile,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[columns_to_be_plotted_xAxis], columns_to_be_plotted_yAxis=['Frequency'],
                                                           chart_title='Frequency Distribution of Simplex Object\n' + str(simplex_data),
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType=str(simplex_data), #'gender_bar',
                                                           column_xAxis_label=str(simplex_data),
                                                           groupByList=[],
                                                           plotList=[],
                                                           chart_title_label='')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

# compute SVO (Semantic triplets) data with NO time and space -------------------------------------------------------------------
    if semantic_triplet_var and (not semantic_triplet_subject or not semantic_triplet_verb or not semantic_triplet_object):
        mb.showwarning(title='Warning',
                        message="To run the Semantic triplet SVO extractor, you must specify the subject, verb and object.")
        return

    if semantic_triplet_var and google_earth_var:
        if setup_simplex == '':
            mb.showwarning(title='Warning',
                           message="To run the Semantic triplet SVO extractor with the option of visualizing the where via Google Earth Pro or Google Maps, you must first select the simplex name (e.g., City name, County) containing the location names to be geocoded and mapped, using the Simplex dropdown menu above.")
            return

    if semantic_triplet_var and not time_var and not space_var:
        # SVO only
        outputFile = DB_PCACE_data_analyzer_util.semantic_triplet_simplex_main(inputDir, outputDir,
                                                                               primary_complex_var,
                                                                               semantic_triplet_subject,semantic_triplet_verb, semantic_triplet_object,
                                                                               comments_var,
                                                                               document_sources_var)

# compute SVO (Semantic triplets) data with time and space -------------------------------------------------------------------

    if semantic_triplet_var and time_var and space_var:
        # SVO + time + space
        outputFile = DB_PCACE_data_analyzer_util.semantic_triplet_time_space(inputDir, outputDir, time_label_var,space_label_var,
                     primary_complex_var, semantic_triplet_subject,semantic_triplet_verb, semantic_triplet_object, comments_var, document_sources_var)

    if semantic_triplet_var and time_var and not space_var:
        # SVO + time
        outputFile = DB_PCACE_data_analyzer_util.semantic_triplet_time(inputDir, outputDir, time_label_var,
                     primary_complex_var, semantic_triplet_subject, semantic_triplet_verb, semantic_triplet_object, comments_var, document_sources_var)

    if semantic_triplet_var and space_var and not time_var:
        # SVO + space
        outputFile = DB_PCACE_data_analyzer_util.semantic_triplet_space(inputDir, outputDir, space_label_var,
                     primary_complex_var, semantic_triplet_subject,semantic_triplet_verb, semantic_triplet_object, comments_var, document_sources_var)

    if outputFile != '':
        filesToOpen.append(outputFile)

# Gephi for semantic triplets SVO ----------------------------------------------------------------------------------------
    if semantic_triplet_var and gephi_var:
        svo_result_list=[]
        fileBase = os.path.basename(outputFile)[0:-5]
        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(outputFile, encodingValue='utf-8')

        if nRecords > 1:  # including headers; file is empty
            import pandas as pd

            # the next lines do not seem to do anything,
            #   perhaps, should take the date from the date in the database to create a dynamic network graph
            # df = pd.read_csv(outputFile,encoding='utf-8',on_bad_lines='skip')
            # # Add a new empty column called 'data expression'
            # df['Date expression'] = '' # '1998-09-01' should take the date from the date in the database
            # df['Normalized date'] = ''
            # df['Date type'] = ''
            # # Write the updated DataFrame back to the CSV file
            # df.to_csv(outputFile, index=False)
            # print("New column 'Date expression' added successfully!")

            gexf_file = Gephi_util.create_gexf(window, fileBase, outputDir, outputFile,
                                               "Subject (S)", "Verb (V)", "Object (O)",'',"non-default") # Sentence ID will be added as the last column
            filesToOpen.append(gexf_file)

        # Sankey charts

            Sankey_limit1_var = 5
            Sankey_limit2_var = 10
            Sankey_limit3_var = 20
            three_way_Sankey = True

            output_label = 'sankey'
            outputFilename_sankey = IO_files_util.generate_output_file_name(outputFile, inputDir, outputDir,
                                                                            '.html', output_label)
            outputFiles = charts_util.Sankey(outputFile, outputFilename_sankey,
                                             'Subject (S)', Sankey_limit1_var, 'Verb (V)', Sankey_limit2_var,
                                             three_way_Sankey, 'Object (O)', Sankey_limit3_var)

            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            # output_label = 'sunburst'
            # outputFilename_sunburst = IO_files_util.generate_output_file_name(outputFile, inputDir, outputDir,
            #                                                                 '.html', output_label)
            outputFilename_sunburst = ''
            csv_file_categorical_field_list = [['Subject (S)|'], ['Verb (V)|'], ['Object (O)|']]
            suntree = 3
            fixed_param_var = 30
            rate_param_var = None
            base_param_var = None
            filter_options_var = 'Fixed parameter'
            case_sensitive_var = 1
            outputFiles = charts_util.Sunburst_Treemap(outputFile, outputFilename_sunburst, outputDir, csv_file_categorical_field_list, suntree, fixed_param_var, rate_param_var, base_param_var, filter_options_var, case_sensitive_var)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)


    # wordcloud for semantic triplets SVO _________________________________________________

    if semantic_triplet_var and wordcloud_var:
        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(outputFile)
        if nRecords > 1:  # including headers; file is empty
            myfile = IO_files_util.openCSVFile(outputFile, 'r')

            # run with all default values;
            use_contour_only = False
            max_words = 100
            font = 'Default'
            prefer_horizontal = .9
            # lemmatize = False
            exclude_stopwords = True
            exclude_punctuation = True
            lowercase = False
            differentPOS_differentColors = False
            differentColumns_differentColors = False
            csvField_color_list = []
            doNotListIndividualFiles = True
            collocation = False
            import wordclouds_util

            outputFile = wordclouds_util.SVOWordCloud(myfile, outputFile, outputDir,
                                                    "", wordcloud_title='', prefer_horizontal=.9)
            myfile.close()
            filesToOpen.append(outputFile)

# GIS maps for semantic triplets SVO _____________________________________________________
    def generateChart(outputFile, label):
        filesToOpen.append(outputFile)
        print('------------------------------------------------------')
        print('------------------------------------------------------')
        print('------------------------------------------------------')
        print(label)
        simplexes = DB_PCACE_data_analyzer_util.corresponding_name_simplex_complex(label)

        # headers=IO_csv_util.get_csvfile_headers(outputFile)
        # columns_to_be_plotted_xAxis=IO_csv_util.get_headerValue_from_columnNumber(headers,column_number=0)
        result = ', '.join(simplexes[0])
        print(simplex_list)
        columns_to_be_plotted_yAxis = [result]
        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFile,
                                                  outputDir,
                                                  columns_to_be_plotted_xAxis=[],
                                                  columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
                                                  chart_title='Frequency Distribution of simplexes of ' + label,
                                                  count_var=1, hover_label=[],
                                                  outputFileNameType='time',  # 'gender_bar',
                                                  column_xAxis_label=result,
                                                  groupByList=[],
                                                  plotList=[],
                                                  chart_title_label='')
        print(outputFiles)
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    if semantic_triplet_var or space_var or time_var:
        if time_var and not time_label_var:
            mb.showwarning(title='Warning',
                           message="You must select the time complex to be analyzed, using the complex dropdown menu on the right of the checkbox.")
            return

        if time_var and not semantic_triplet_var:
            outputFile = DB_PCACE_data_analyzer_util.get_time_simplex(inputDir, outputDir, time_label_var,
                                                                      semantic_triplet_subject, semantic_triplet_verb,
                                                                      semantic_triplet_object, primary_complex_var, comments_var, document_sources_var)
            if outputFile and time_label_var:
                generateChart(outputFile, time_label_var)

        if space_var and not space_label_var:
            mb.showwarning(title='Warning',
                           message="You must select the space complex to be analyzed, using the complex dropdown menu on the right of the checkbox.")
            return

        if space_var and not semantic_triplet_var:
            outputFile = DB_PCACE_data_analyzer_util.get_space_simplex(inputDir, outputDir, space_label_var,
                                                                      semantic_triplet_subject, semantic_triplet_verb,
                                                                      semantic_triplet_object, primary_complex_var, comments_var, document_sources_var)
            if outputFile and space_label_var:
                generateChart(outputFile, space_label_var)


        if google_earth_var:
            extract_date_from_text_var = 0
            filename_embeds_date_var = 0
            reminders_util.checkReminder(scriptName, reminders_util.title_options_geocoder,
                                         reminders_util.message_geocoder, True)
            # locationColumnNumber where locations are stored in the csv file; any changes to the columns will result in error
            date_present = (extract_date_from_text_var == True) or (filename_embeds_date_var == True)
            country_bias = ''
            area_var = ''
            restrict = False
            if setup_simplex == '':
                mb.showwarning(title='Warning',
                               message="You must first select the simplex name (e.g., City name, County) containing the location names to be geocoded and mapped, using the Simplex dropdown menu above.")
                return
            # location_filename = os.path.join(outputDir,'NLP_' + setup_simplex + '_simplex_freq_Dir_Lynching_PCACE_xlsx.csv')
            # if not os.path.isfile(location_filename):
            location_filename = DB_PCACE_data_analyzer_util.get_simplex_frequencies(setup_simplex, inputDir, outputDir, False)

            # IO_csv_util.rename_header(location_filename, setup_simplex, 'Location')
            IO_csv_util.rename_header(location_filename, 'Value', 'Location')

            columns_to_be_plotted_yAxis = ['Location']
            outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, location_filename,
                                                      outputDir,
                                                      columns_to_be_plotted_xAxis=[],
                                                      columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
                                                      chart_title='Frequency Distribution of Locations',
                                                      count_var=1, hover_label=[],
                                                      outputFileNameType='time',  # 'gender_bar',
                                                      column_xAxis_label='Location',
                                                      groupByList=[],
                                                      plotList=[],
                                                      chart_title_label='')
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            outputFile = GIS_pipeline_util.GIS_pipeline(GUI_util.window,
                                                      config_filename, location_filename, inputDir,
                                                      outputDir,
                                                      'Nominatim', 'Google Earth Pro & Google Maps',
                                                      chartPackage, dataTransformation,
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

            if outputFile != None:
                if len(outputFile) > 0:
                    # since outputFile produced by KML is a list cannot use append
                    filesToOpen = filesToOpen + outputFile

# actors ----------------------------------------------------------------------
    def process_actor(inputDir, outputDir, actors_var, chart_title, yAxis_columns, output_type):
        outputFile = DB_PCACE_data_analyzer_util.actor_characteristics(inputDir, outputDir, actors_var)

        files_to_open = []
        if outputFile:
            files_to_open.append(outputFile)
            outputFiles = charts_util.visualize_chart(
                chartPackage, dataTransformation, outputFile, outputDir,
                columns_to_be_plotted_xAxis=[],
                columns_to_be_plotted_yAxis=yAxis_columns,
                chart_title=f'Frequency Distribution of {actors_var.capitalize()}s',
                count_var=1, hover_label=[],
                outputFileNameType=output_type,
                column_xAxis_label=actors_var,
                groupByList=[], plotList=[], chart_title_label=''
            )

            if outputFiles:
                if isinstance(outputFiles, str):
                    files_to_open.append(outputFiles)
                else:
                    files_to_open.extend(outputFiles)
        return files_to_open

    # Define the actor configurations
    # Taeeun must generalize names
    actor_configs = {
        'Attore collettivo': {
            'chart_title': 'Frequency Distribution of Collective Actors',
            'yAxis_columns': ['Name of collective actor Simplex'],
            'output_file_type': 'coll'
        },
        'Individuo': {
            'chart_title': 'Frequency Distribution of Individuals',
            'yAxis_columns': ['Name of individual actor Simplex'],
            'output_file_type': 'ind'
        },
        'Organizzazione': {
            'chart_title': 'Frequency Distribution of Organizations',
            'yAxis_columns': [
                'State organisation Simplex', 'Political party Simplex', 'Other institution Simplex',
                'Actor aggregate code Simplex', 'Actor aggregate (Institution) COLIN Simplex'
            ],
            'output_file_type': 'org'
        }
    }

    # Taeeun must generalize names
    # uncomment after generalization
    # for actor_type, config in actor_configs.items():
    #     if actor_type == actors_var:
    #         filesToOpen.extend(process_actor(
    #             inputDir, outputDir, actors_var,
    #             config['chart_title'], config['yAxis_columns'], config['output_file_type']
    #         ))
    #
    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.charts_package_options_widget.get(),
                                GUI_util.data_transformation_options_widget.get(),
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
                                semantic_triplet_subject.get(),
                                semantic_triplet_verb.get(),
                                semantic_triplet_object.get(),
                                actors_var.get(),
                                time_var.get(),
                                time_label_var.get(),
                                space_var.get(),
                                space_label_var.get(),
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
                                                 GUI_height_brief=640, # height at brief display
                                                 GUI_height_full=680, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=1, # to be added for full display
                                                 increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for PC-ACE Tables Analyzer (via Pandas)'
config_filename = 'DB_PCACE_data_analyzer_config.csv'
head, scriptName = os.path.split(os.path.basename(__file__))

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
semantic_triplet_subject = tk.StringVar()
semantic_triplet_verb = tk.StringVar()
semantic_triplet_object = tk.StringVar()
actors_var = tk.StringVar()
time_var = tk.IntVar()
time_label_var = tk.StringVar()
space_var = tk.IntVar()
space_label_var = tk.StringVar()

select_parents_var = tk.StringVar()
select_children_var = tk.StringVar()
gephi_var = tk.IntVar()
wordcloud_var = tk.IntVar()
google_earth_var = tk.IntVar()

def clear(e):
    primary_complex_var.set('')
    value_parent_object_var.set(0)
    setup_complex=''
    setup_simplex=''
    select_DB_tables_var.set('')

    simplex_data_type_var.set('')
    simplex_list=[]
    simplex_data_var.set(simplex_list)
    simplex_data_var.set('')
    simplex_data['values'] = []

    setup_complex_var.set('')
    setup_simplex_var.set('')

    value_parent_object_var.set(0)

    select_parents_var.set('')
    select_children_var.set('')

    # print_narrative_var.set(0)

    ALL_objects_frequencies_var.set(0)
    SELECTED_objects_frequencies_var.set(0)

    semantic_triplet_var.set(0)
    semantic_triplet_subject.set(''),
    semantic_triplet_verb.set(''),
    semantic_triplet_object.set(''),
    gephi_var.set(0)
    wordcloud_var.set(0)
    google_earth_var.set(0)
    time_var.set(0)
    time_label_var.set('')
    space_var.set(0)
    space_label_var.set('')
    actors_var.set('')
    setup_complex_var.set('')
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
                                   "Click to open a pdf file of the PC-ACE table relations. These relations are ALWAYS the same across any type of application of PC-ACE (e.g., Avanti! or Lynchings).\nTo view the grammar of data collection for a specific PC-ACE implementation click on the button View grrammar.")

view_grammar_button = tk.Button(window, text='View grammar', width=20,height=1,state='normal', command=lambda: view_grammar())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   view_grammar_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to view the grammmar used for the selected, specific implementation of the PC-ACE database.\nClick on the button View table relations to visualize the general table relations in the PC-ACE databasee, regardless of a selected, specific implementation (i./e., grammar setup).")
# https://www.geeksforgeeks.org/convert-excel-to-csv-in-python/
# view_relations_button = tk.Button(window, text='Convert PC-ACE Excel tables to csv  ', height=1,state='normal', command=lambda: view_relations())
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
#                                    view_relations_button,
#                                    True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
#                                    "Click to convert the Excel files exported from Microsoft ACCESS database to csv files for use in this GUI")

select_DB_tables_lb = tk.Label(window, text='PC-ACE table ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate,y_multiplier_integer,select_DB_tables_lb,True)

table_menu_values = ''
table_list=[]
if os.path.isdir(inputDir.get()):
    table_list = DB_PCACE_data_analyzer_util.import_PCACE_tables(inputDir.get())
    table_menu_values = ", ".join(table_list)
select_DB_tables = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=select_DB_tables_var)
select_DB_tables.configure(state='disabled')
select_DB_tables['values'] = table_menu_values
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate+100, y_multiplier_integer,
                                   select_DB_tables,
                                   False, False, True, False, 90, GUI_IO_util.setup_IO_brief_coordinate,
                                   "Use the dropdown menu to select a PC-ACE table to be opened for display; click RUN after selection.")

simplex_data_type_lb = tk.Label(window, text='PC-ACE data type ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,simplex_data_type_lb,True)

simplex_data_type_var= tk.StringVar()
simplex_data_type_menu = tk.OptionMenu(window, simplex_data_type_var, 'text','date', 'number')
simplex_data_type_menu.configure(state='disabled')
simplex_data_type_var.set('')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+120, y_multiplier_integer,
                                   simplex_data_type_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_S_dictionary,
                                   "Use the dropdown menu to select the data type to be used to extract a list of values.")

inputDirSV = ''
# simplex_data = ''
simplex_data_var = tk.StringVar()
# simplex_data_var.set(simplex_list)
# simplex_data_var = simplex_list
simplex_data = ttk.Combobox(window, textvariable = simplex_data_var, width=GUI_IO_util.widget_width_short)
simplex_data.configure(state='disabled')

simplex_list = DB_PCACE_data_analyzer_util.get_Simplex_text_date_number(simplex_data_type_var.get(), os.path.join(inputDir.get(),'data_SimplexText.xlsx'), os.path.join(inputDir.get(),'data_SimplexDate.xlsx'), os.path.join(inputDir.get(),'data_SimplexNumber.xlsx'))
simplex_data_menu = simplex_list
simplex_data['values'] = simplex_data_menu
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+350, y_multiplier_integer,
                                   simplex_data,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate+300,
                                   "Use the dropdown menu to select the simplex data type value (e.g., police) for which you want to find simplex & complex objects usage")

def activate_date_number_text(*args):
    if simplex_data_type_var.get()!='':
        simplex_data.configure(state='normal')
    else:
        simplex_data.configure(state='disabled')
    simplex_list = DB_PCACE_data_analyzer_util.get_Simplex_text_date_number(simplex_data_type_var.get(),
                                    os.path.join(inputDir.get(),
                                             'data_SimplexText.xlsx'),
                                     os.path.join(inputDir.get(),
                                              'data_SimplexDate.xlsx'),
                                     os.path.join(inputDir.get(),
                                            'data_SimplexNumber.xlsx'))
    simplex_data_var.set(simplex_list)
    simplex_data['values'] = simplex_list
simplex_data_type_var.trace('w',activate_date_number_text)
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
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu-50, y_multiplier_integer,
                                   primary_complex,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to select a specific primary complex object (Macro event) by its identifier to analyze.\nWhen a specific macro event is selected, all analyses (e.g., SVO, actors) will be based on that macro event.")

# actors_lb = tk.Label(window, text='Actors ')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate+400,y_multiplier_integer,actors_lb,True)
# actors = ttk.Combobox(window, textvariable = actors_var, width=GUI_IO_util.widget_width_short)
# # place widget with hover-over info
# #GUI_IO_util.IO_configuration_menu+300
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate+475, y_multiplier_integer,
#                                    actors,
#                                    False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
#                                    "Use the dropdown menu to select the complex object that is a type of actor that you want to extract (e.g., Collective actor, Individual, Organization)")
#

def activate_SVO_visualization():
    if semantic_triplet_var.get() == 1:
        mb.showwarning(title='Warning',
                       message='You have selected to extract the SVO information (Subject-Verb-Object) from the database. Using the respective dropdown menus, please select the appropriate complex object.\n\nDifferent databases may have different names for the SVO, depending also upon user preferences and the language used for the setup (e.g., English or Italian). The Subject could be named Participant-S or Actor-S; the Verb, Process or Action; the Object, Participant-O or Actor-O.')
        semantic_triplet_subject.set('')
        semantic_triplet_verb.set('')
        semantic_triplet_object.set('')

        time_checkbox.configure(state='normal')
        time_label_var_box.configure(state='normal')
        space_checkbox.configure(state='normal')
        space_label_var_box.configure(state='normal')
        semantic_triplet_subject_box.configure(state='normal')
        semantic_triplet_verb_box.configure(state='normal')
        semantic_triplet_object_box.configure(state='normal')
        gephi_checkbox.configure(state='normal')
        wordcloud_checkbox.configure(state='normal')
        google_earth_checkbox.configure(state='normal')
    else:
        time_checkbox.configure(state='disabled')
        time_label_var_box.configure(state='disabled')
        space_checkbox.configure(state='disabled')
        space_label_var_box.configure(state='disabled')
        semantic_triplet_subject_box.configure(state='disabled')
        semantic_triplet_verb_box.configure(state='disabled')
        semantic_triplet_object_box.configure(state='disabled')
        gephi_checkbox.configure(state='disabled')
        wordcloud_checkbox.configure(state='disabled')
        google_earth_checkbox.configure(state='disabled')

semantic_triplet_var_checkbox = tk.Checkbutton(window, text='Semantic triplets (SVO)', variable=semantic_triplet_var, onvalue=1, offvalue=0, command=lambda: activate_SVO_visualization())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   semantic_triplet_var_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox to extract semantic triplets/SVOs (i.e., combinations of Subject, Verb, Object).\nWhen a specific macro event is selected, SVOs will be extracted for that specific macro event.")

time_checkbox = tk.Checkbutton(window, text='Time', variable=time_var, onvalue=1, offvalue=0)
time_checkbox.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                   time_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Tick the checkbox to extract the time of action when running SVO. Columns with time information will be added to the SVO csv output file.\nWhen a specific macro event is selected, the time will be extracted for that specific macro event.")


time_label_var_box = ttk.Combobox(window, textvariable = time_label_var, width=GUI_IO_util.widget_width_short)
time_label_var_box.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate+60, y_multiplier_integer,
                                               time_label_var_box,
                                               True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                               "Using the dropdown menu, select the complex object used for Time in the selected database.\nDifferent databases may have different names for Time, depending also upon user preferences and the language used for the setup (e.g., English or Italian).")

space_checkbox = tk.Checkbutton(window, text='Space', variable=space_var, onvalue=1, offvalue=0)
space_checkbox.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate+400, y_multiplier_integer,
                                   space_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.read_button_x_coordinate,
                                   "Tick the checkbox to extract space information. When running Space in conjuction with SVO, columns with space information will be added to the SVO csv output file.\nWhen a specific macro event is selected, the space will be extracted for that specific macro event.\nWhen the Visualize Where checkbox is ticked and a Simplex location name is selected, space information will be geocoded using Nominatim and displayed as pin map via Google Earth Pro and heat map via Google Maps.")
space_label_var_box = ttk.Combobox(window, textvariable = space_label_var, width=GUI_IO_util.widget_width_short)
space_label_var_box.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate+475, y_multiplier_integer,
                                               space_label_var_box,
                                               False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                               "Using the dropdown menu, select the complex object used for Space in the selected database.\nDifferent databases may have different names for Time, depending also upon user preferences and the language used for the setup (e.g., English or Italian).")

subject_lb = tk.Label(window, text='Subject ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,subject_lb,True)
semantic_triplet_subject_box = ttk.Combobox(window, textvariable = semantic_triplet_subject, width=GUI_IO_util.widget_width_short)
semantic_triplet_subject_box.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+50, y_multiplier_integer,
                                               semantic_triplet_subject_box,
                                               True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                               "Using the Subject dropdown menu, select the complex object used for Subject in the selected database.\nDifferent databases may have different names for the Subject, depending also upon user preferences and the language used for the setup (e.g., English or Italian).\nThe Subject could be named Participant-S or Actor-S, Soggetto. The selected name will be used for the query.")

verb_lb = tk.Label(window, text='Verb ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+380,y_multiplier_integer,verb_lb,True)
semantic_triplet_verb_box = ttk.Combobox(window, textvariable = semantic_triplet_verb, width=GUI_IO_util.widget_width_short)
semantic_triplet_verb_box.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+430, y_multiplier_integer,
                                               semantic_triplet_verb_box,
                                               True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                               "Using the Verb dropdown menu, select the complex object used for Verbs.\nDifferent databases may have different names for the Verb, depending upon user preferences and the language used for the setup (e.g., English or Italian).\nThe Verb could be named Process or Action or Azione. The selected name will be used for the query.")

object_lb = tk.Label(window, text='Object ')
#labels_x_coordinate+750
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150,y_multiplier_integer,object_lb,True)

semantic_triplet_object_box = ttk.Combobox(window, textvariable = semantic_triplet_object, width=GUI_IO_util.widget_width_short-9)
semantic_triplet_object_box.configure(state='disabled')
#labels_x_coordinate+800
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+200, y_multiplier_integer,
                                               semantic_triplet_object_box,
                                               False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                               "Using the Object dropdown menu, select the complex object used for Object in the selected database.\nDifferent databases may have different names for the Object, depending upon user preferences and the language used for the setup (e.g., English or Italian).\nThe Object could be named Participant-O or Actor-O or Oggetto. The selected name will be used for the query.")

gephi_var.set(0)
gephi_checkbox = tk.Checkbutton(window, text='Visualize SVO relations ',
                                variable=gephi_var, onvalue=1, offvalue=0)
gephi_checkbox.configure(state='disabled')

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+20, y_multiplier_integer,
                                   gephi_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox to visualize the triplet SVOs as a network graph in Gephi and Sankey flowcharts and in sunburst, treemap, and colormap charts.")

wordcloud_var.set(0)
wordcloud_checkbox = tk.Checkbutton(window, text='Visualize SVO relations in wordcloud', variable=wordcloud_var,
                                    onvalue=1, offvalue=0)
wordcloud_checkbox.configure(state='disabled')

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                   wordcloud_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate+350,
                                   "Tick the checkbox to visualize the triplet SVOs in a wordcloud: Subjects in red, Verbs in blue, Objects in green.")

google_earth_var.set(0)
google_earth_checkbox = tk.Checkbutton(window, text='Visualize Where (via Google Maps & Google Earth Pro)',
                                       variable=google_earth_var, onvalue=1, offvalue=0)
google_earth_checkbox.configure(state='disabled')

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   google_earth_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Tick the checkbox to visualize the space of SVOs as in a Google Earth Pro pin map and Google Maps heat map")

# Taeeun the complex objects widget only displays the object identifier;
# but... like the functions for the SVO extractor, it should display the value of all the simplex objects that make up the complex object

complex_objects_lb = tk.Label(window, text='Complex ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,complex_objects_lb,True)

setup_complex_menu = DB_PCACE_data_analyzer_util.get_complex_simplex_names(os.path.join(inputDir.get(),'setup_complex.xlsx'))

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

setup_simplex_menu = DB_PCACE_data_analyzer_util.get_complex_simplex_names(os.path.join(inputDir.get(),'setup_Simplex.xlsx'))

setup_simplex_var = tk.StringVar()

setup_simplex = ttk.Combobox(window, textvariable = setup_simplex_var, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
setup_simplex['values'] = setup_simplex_menu
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   setup_simplex,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Use the dropdown menu to select a specific simplex object for which to compute frequencies.\nWhen running SVO extractor with the option of visualizing Where, the simplex containing the location values to be used for mapping must be selected.")


# print_narrative_var = tk.StringVar()
# print_narrative_var.set(0)
# print_narrative_checkbox = tk.Checkbutton(window, text='Print selected complex object in narrative form', variable=print_narrative_var, onvalue=1, offvalue=0)
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,print_narrative_checkbox)

ALL_complex_objects_checkbox = tk.Checkbutton(window, text='Get value frequencies for ALL objects (complex & simplex)', variable=ALL_objects_frequencies_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   ALL_complex_objects_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Tick the checkbox to extract the value frequencies for ALL objects (complex & simplex)")

SELECTED_complex_objects_checkbox = tk.Checkbutton(window, text='Get value frequencies for SELECTED Complex OR Simplex object', variable=SELECTED_objects_frequencies_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                   SELECTED_complex_objects_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Tick the checkbox to extract the value frequencies for a SELECTED object (complex OR simplex).\nFor complex objects, the object identifiers will be counted.")

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
                                   "The menu displays a list of complex objects children of the 'Complex objects' selected in the widget above.\nThe option is only available for the 'Complex objects' widget above (Simplex objects do not have children).")


def activate_parents_children(*args):
    parent_complex_list = DB_PCACE_data_analyzer_util.find_parent_complex(setup_complex_var.get(),inputDir.get())
    select_parents['values'] = parent_complex_list

    children_list = DB_PCACE_data_analyzer_util.find_child_complex(setup_complex_var.get(),inputDir.get())
    select_children['values'] = children_list
    # select_children_var.set(children_menu[0])
setup_complex_var.trace('w',activate_parents_children)
setup_simplex_var.trace('w',activate_parents_children)


comments_lb = tk.Label(window, text='Extract comments ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,comments_lb,True)

comments_var = tk.StringVar()
comments_var.set('')
comments_menu = tk.OptionMenu(window, comments_var, '*', 'users comments', 'verifiers comments')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                   comments_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Use the dropdown menu to extract the comments left by users and/or verifiers for specific objects (e.g., Semantic triplets (SVO)).")

# verifier_comments_var = tk.IntVar()
# verifier_comments_checkbox = tk.Checkbutton(window, text='Get verifiers comments ', variable=verifier_comments_var, onvalue=1, offvalue=0)
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,verifier_comments_checkbox)

document_sources_var = tk.IntVar()
document_sources_checkbox = tk.Checkbutton(window, text='Extract document sources ', variable=document_sources_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                   document_sources_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox to extract the documents (e.g., newspaper articles) that are the sources of information for specific objects (e.g., Semantic triplets (SVO)).")

error = False
database_already_loaded = False
table_values = []
currentInputDir = inputDir.get()
readDir = False
def changed_filename(*args):
    global error, setup_simplex_menu, currentInputDir, readDir
    global error, setup_simplex_menu, database_already_loaded, inputDirSV
    # 25 PC-ACE files
    # if GUI_util.input_main_dir_path.get()!='' and not error:
    if GUI_util.input_main_dir_path.get() != '' and GUI_util.input_main_dir_path.get() != inputDirSV:
        inputDirSV = GUI_util.input_main_dir_path.get()
        inputDocs = IO_files_util.getFileList('', GUI_util.input_main_dir_path.get(), fileType='.xlsx', silent=True)
        nDocs = len(inputDocs)
        if nDocs < 20:
            GUI_util.run_button.configure(state='disabled')
            table_menu_values = []
            error = True
            mb.showwarning(title='Warning',
                           message="The PC-ACE table analyzer scripts require in input a directory of Excel (xlsx) files. But the selected directory\n\n" + inputDir.get() + "\n\ndoes not contain the required PC-ACE Excel files.\n\nPlease, select a PC-ACE directory and try again")
            return
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
        # if error:
        #     return
        if len(table_menu_values)>0:
            select_DB_tables.configure(state='normal')
            select_DB_tables.set(table_menu_values[0])
            select_DB_tables.set('')

        else:
            select_DB_tables.set('')
            select_DB_tables.configure(state='disabled')

        if currentInputDir != inputDir.get() or not readDir:
            # load all excel sheets and store in data
            DB_PCACE_data_analyzer_util.load_df(inputDir.get())
            currentInputDir = inputDir.get()
            readDir = True

        setup_complex_menu = DB_PCACE_data_analyzer_util.get_complex_simplex_names(os.path.join(inputDir.get(), 'setup_complex.xlsx'))
        setup_complex['values'] = setup_complex_menu
        # actors['values'] = setup_complex_menu
        semantic_triplet_object_box['values'] = setup_complex_menu
        semantic_triplet_subject_box['values'] = setup_complex_menu
        semantic_triplet_verb_box['values'] = setup_complex_menu
        time_label_var_box['values'] = setup_complex_menu
        space_label_var_box['values'] = setup_complex_menu

        if len(setup_complex_menu)>0:
            simplex_data_type_menu.configure(state='normal')
            select_DB_tables.configure(state='normal')
            setup_complex.configure(state='normal')
            # setup_complex.set(setup_complex_menu[0])
            setup_complex.set('')
            if not database_already_loaded:
                primary_complex_menu = DB_PCACE_data_analyzer_util.build_macro_event_dropdown_menu(window,inputDir.get())
                primary_complex['values'] = primary_complex_menu
                database_already_loaded = True
        else:
            simplex_data_type_menu.configure(state='disabled')
            setup_complex.set('')
            setup_complex.configure(state='disabled')
        setup_simplex_menu = DB_PCACE_data_analyzer_util.get_complex_simplex_names(os.path.join(inputDir.get(), 'setup_Simplex.xlsx'))
        setup_simplex_menu = DB_PCACE_data_analyzer_util.get_complex_simplex_names(os.path.join(inputDir.get(), 'setup_Simplex.xlsx'))
        setup_simplex['values'] = setup_simplex_menu
        if len(setup_simplex_menu)>0:
            setup_simplex.configure(state='normal')
            # setup_simplex.set(setup_simplex_menu[0])
            setup_simplex_var.set('')
        else:
            setup_simplex.set('')
            # setup_simplex.configure(state='disabled')
    else:
        if inputFilename.get()!='':
            simplex_data_type_menu.configure(state='disabled')
            GUI_util.run_button.configure(state='disabled')
            error = True
    clear("Escape")
    # if not error:
    #     primary_complex_menu = DB_PCACE_data_analyzer_util.build_macro_event_dropdown_menu(window, inputDir.get())
    #     primary_complex['values'] = primary_complex_menu
GUI_util.inputFilename.trace('w', changed_filename)
GUI_util.input_main_dir_path.trace('w', changed_filename)

table_fields_menu_values = []

def view_relations():
    TIPS_util.open_TIPS('TIPS_NLP_PC-ACE table relations.pdf')


def view_grammar():
    head, tail = os.path.split(inputDir.get())
    DB_PCACE_data_analyzer_util.view_grammar(os.path.join(inputDir.get(), 'setup_Complex.xlsx'),
                                             'GrammarRule_Text', os.path.join(outputDir.get(),
                                                                              'PC-ACE grammar for database ' + tail + '.txt'))


videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'PC-ACE tables analyzer via Pandas':'TIPS_NLP_PC-ACE ACCESS DB Analyzer.pdf',
               'PC-ACE - Export ACCESS tables to Excel':'TIPS_NLP_PC-ACE - Export ACCESS tables to Excel.pdf',
               'SVO automatic extraction and visualization': 'TIPS_NLP_SVO extraction and visualization.pdf',
               "Google Earth Pro": "TIPS_NLP_GIS_Google Earth Pro.pdf",
               "Google API Key": "TIPS_NLP_GIS_Google API Key.pdf",
               "Geocoding": "TIPS_NLP_GIS_Geocoding.pdf",
               "Geocoding: How to Improve Nominatim": "TIPS_NLP_GIS_Geocoding Nominatim.pdf",
               "Gephi network graphs": "TIPS_NLP_Gephi network graphs.pdf",
               "Word clouds":"TIPS_NLP_Wordclouds Visualizing word clouds.pdf"
               }
TIPS_options='PC-ACE tables analyzer via Pandas', 'PC-ACE - Export ACCESS tables to Excel', 'SVO automatic extraction and visualization', 'Google Earth Pro', 'Google API Key', 'Geocoding', 'Geocoding: How to Improve Nominatim', 'Gephi network graphs', 'Word clouds'

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
                                                         "Please, tick the checkbox to extract Subject, Verb, Objet relations (semantic triplet) and/or the type of actor for which you wish to extract all instances of semantic triplets, i.e., Subject-Verb-Object combinations (* for all types of actors) and/or the time and/or space of action.\n\nWhen a primary complex (or macro event) has been selected, SVOs, time, and space will be selected for the selected macro event only." + GUI_IO_util.msg_Esc)
    # name of S V O in specific databases (e.g., Participant-S or Soggetto in Italian)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, use the dropdown menu to extract the users and/or visualize Verifiers comments." + GUI_IO_util.msg_Esc)
    # SVO visualization
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkboxes to visualize Subjects, Verbs, Objects in network graphs and wordclouds, and to visualize space in geographic maps." + GUI_IO_util.msg_Esc)
    # actors
    # y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, use the dropdown menu to select the type of actor for which you wish to extract all instances of semantic triplets, i.e., Subject-Verb-Object combinations (* for all types of actors)." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "The dropdown menu displays all the COMPLEX or SIMPLEX objects parent and children of the objects selected in the 'Complex objects' or 'Simplex objects' dropdown menu widgets." + GUI_IO_util.msg_Esc)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "Please, tick the 'Get value frequencies for ALL objects' checkbox to compute the frequencies of all available complex and simplex objects."
                                                         "\n\nTick the 'Get value frequencies for SELECTED object' checkbox to compute the frequencies of the selected Complex or Simplex object." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the PARENT object and/or the CHILD object." + GUI_IO_util.msg_Esc)
    # comments & documents
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, use the dropdown menu to extract the comments left by users and/or verifiers for specific objects (e.g., Semantic triplets (SVO)).\n\nTick the checkbox to extract the documents (e.g., newspaper articles) that are the sources of information for specific objects." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer -1
"COUNT Display a template SQL COUNT query."
"DUPLICATES The query builds a temporary table of duplicate records, then, depending on user's choice, extracts only one occurrence of all duplicate records or all duplicate occurrences except one (all DISTINCT records will not be displayed). Query results can be used to move occurrences of objects for which multiples should not be allowed."
"UNMATCHED Automatically build a simple query that will give a list of all unmatched records between any two given tables/queries on the basis of a specific field (MEMO type fields cannot be matched!)\n\nThe query will give you a list of the fields in the first selected table/query that do not find a match in the second selected table/query."

y_multiplier_integer = y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,increment)

# change the value of the readMe_message
readMe_message="The Python 3 scripts convert, via the Python Pandas package, and analyze, via various visualization packages, data collected via the Microsoft ACCESS PC-ACE (Program for Computer-Assisted Coding of Events).\n\nIn INPUT the algorithms expect a set of xlsx files in the input directory. The xlsx files must be exported from the PC-ACE database tables data, setup, and utility (see TIPS file on how to export tables from PC-ACE).\n\nIn OUTPUT the algorithms produce a set of csv files and different types of visuals, from Excel charts to network graphs via Gephi and Sankey, geographic pin maps via Google Earth Pro and heat maps via Google Maps, wordclouds, and interactive time maps."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

changed_filename()
if error and GUI_util.input_main_dir_path.get()!='':
    # check to see if there is a GUI-specific config file and set it to the setup_IO_menu_var
    if os.path.isfile(os.path.join(GUI_IO_util.configPath, config_filename)):
        GUI_util.setup_IO_menu_var.set('Select any I/O csv config file')
        mb.showwarning(title='Warning',
                       message="The PC-ACE table analyzer scripts require in input a directory of Excel (xlsx) files. But the selected directory\n\n" + inputDir.get() + "\n\ndoes not contain the required PC-ACE Excel files.\n\nPlease, select a PC-ACE directory and try again")
                                # "Since a GUI-specific " + config_filename + " file is available, the I/O configuration has been automatically set to GUI-specific I/O configuration.")
                                # "Since a GUI-specific " + config_filename + " file is available, the I/O configuration has been automatically set to GUI-specific I/O configuration.")
        select_DB_tables.configure(state='disabled')
        error = False
        database_already_loaded = False

# if inputDir.get()!='' and not error:
#     primary_complex_menu = DB_PCACE_data_analyzer_util.build_macro_event_dropdown_menu(window, inputDir.get())
#     primary_complex['values'] = primary_complex_menu
GUI_util.window.mainloop()

