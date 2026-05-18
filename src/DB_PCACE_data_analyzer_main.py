
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
        simplex_value_type, simplex_value,
        primary_complex_var,
        value_parent_object_var,
        setup_complex, extended_headers, setup_simplex,
        # print_narrative_var,
        ALL_objects_frequencies_var, SELECTED_objects_frequencies_var,
        ALL_simplex_objects_frequencies_var, SELECTED_simplex_objects_frequencies_var,
        complex_parents_var, complex_children_var,
        semantic_triplet_var,
        semantic_triplet_subject,
        semantic_triplet_verb,
        semantic_triplet_object,
        actors_var, time_var, time_label_var, space_var, space_label_var,
        SVO_relations_visuals_var, wordcloud_var, google_earth_var,
        document_sources_var, comments_var, comments_type,
        from_dataID_setupID_objectType_var, enter_data_ID_var,
        hierarchical_complex_var='',
        search_simplex_value='', search_simplex_result=''):

    config_filename = GUI_util.config_filename_selected_config.get()

    filesToOpen = []
    outputFile = ''


    # test functions; simply click on RUN after selecting the appropriate database

    # semantic_triplet_var = 1
    # semantic_triplet = 'Semantic Triplet'
    # semantic_triplet_subject = 'Participant-S'
    # semantic_triplet_verb = 'Process'
    # semantic_triplet_object = 'Participant-O'
    #
    # complex_name = 'Semantic Triplet'
    # comment_type = ''
    # document_info = False

    # # complex_name = ''
    # # complex_name = 'Process'
    # output_file_name = DB_PCACE_data_analyzer_util.get_data_complex_frequencies(inputDir, outputDir, complex_name)
    # return
    #
    # # simplex_name = 'Proper name'
    # simplex_name = ''
    # output_file_name = DB_PCACE_data_analyzer_util.get_data_simplex_frequencies(inputDir, outputDir, simplex_name)
    # return
    #
    # simplex_value = 'woman'
    # output_file_name = DB_PCACE_data_analyzer_util.get_data_simplex_info(inputDir, outputDir, simplex_value)
    # return
    #
    # temp = DB_PCACE_data_analyzer_util.get_data_complex_info(inputDir, outputDir, complex_name, comment_type, document_info, extended_headers=False)

    # temp = DB_PCACE_data_analyzer_util.get_data_semantic_triplet_info(semantic_triplet, semantic_triplet_subject, semantic_triplet_verb, semantic_triplet_object)
    # return
    #
    # simplex_name = 'Name of individual actor'
    # simplex_parent_list = DB_PCACE_data_analyzer_util.get_setup_simplex_parent(simplex_name)
    # return
    #
    # complex_name = 'Semantic Triplet'
    # # complex_name = 'Participant-S'
    # get_setup_complex_children_all, get_setup_complex_children_required = DB_PCACE_data_analyzer_util.get_setup_complex_children(complex_name, get_required_only=False)
    # df = DB_PCACE_data_analyzer_util.get_lower_setup_complex(complex_name)
    # df = DB_PCACE_data_analyzer_util.call_get_expanded_complex(inputDir, outputDir, complex_name)
    stop = "stop"
    # return
    # get_setup_simplex_children_all, get_setup_simplex_children_required = DB_PCACE_data_analyzer_util.get_setup_simplex_names_for_complex(complex_name, get_required_only=True)
    #
    #
    # lowest_complex_list = DB_PCACE_data_analyzer_util.lower(start=complex_name, lower_complex_list=[], search_complex=complex_name)
    #
    # # list
    # setup_complex_parent_name = DB_PCACE_data_analyzer_util.get_setup_complex_parents(complex_name)
    #
    # # dataframe
    # higher_level_complex_ID_name = DB_PCACE_data_analyzer_util.get_higher_setup_complex(complex_name)

    import os
    if select_DB_tables_var.get()!='':
        IO_files_util.openFile(window, inputDir + os.sep + select_DB_tables_var.get() + ".xlsx")
        return

    if enter_data_ID_var != '':
        if from_dataID_setupID_objectType_var=='':
            mb.showwarning(title='Warning',
                       message='You must select the object type - complex or simplex - using the dropdown menu "From data ID to setup ID".\n\nPlease, select the object type and try again')
            return
        if from_dataID_setupID_objectType_var == 'Complex':
            ID_setup_complex, complex_name = DB_PCACE_data_analyzer_util.get_setup_complex_ID_Name_from_data_complex_ID(int(enter_data_ID_var))
            setup_name_var.set(complex_name)
        elif from_dataID_setupID_objectType_var == 'Simplex':
            ID_setup_simplex, simplex_name = DB_PCACE_data_analyzer_util.get_setup_simplex_ID_Name_from_simplex_value_ID(int(enter_data_ID_var))
            setup_name_var.set(simplex_name)
        return

    head, tail = os.path.split(inputDir)
    outputSubDir = os.path.join(outputDir, tail[:-5])

    if not os.path.exists(outputSubDir):
        outputDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                                         label= tail[:-5],
                                                                         silent=False)
        if outputDir == '':
            return
    else:
        outputDir = outputSubDir

    # Story form export ______________________________________________________________________________
    if hierarchical_complex_var != '' and complex_identifiers_var != '':
        story_text, filepath = DB_PCACE_data_analyzer_util.story_form_from_dropdown(primary_complex_var, outputDir)
        if filepath:
            filesToOpen.append(filepath)
            mb.showwarning(title='Story form',
                           message=f'The story form has been saved to:\n{filepath}')
            if openOutputFiles:
                IO_files_util.openFile(window, filepath)
        return

    # Search simplex value → story form export ___________________________________________________
    if search_simplex_value != '':
        # Always populate the search results dropdown
        dropdown_results = DB_PCACE_data_analyzer_util.build_search_results_dropdown(search_simplex_value)
        search_simplex_results['values'] = dropdown_results
        if dropdown_results:
            search_simplex_results_var.set(dropdown_results[0])

        if search_simplex_result != '':
            # User selected a specific result → show its story form
            story_text, filepath = DB_PCACE_data_analyzer_util.story_form_from_dropdown(search_simplex_result, outputDir)
            if filepath:
                filesToOpen.append(filepath)
                mb.showwarning(title='Story form',
                               message=f'The story form has been saved to:\n{filepath}')
                if openOutputFiles:
                    IO_files_util.openFile(window, filepath)
        else:
            # No specific result selected → export all stories
            filepath = DB_PCACE_data_analyzer_util.search_and_export_stories(search_simplex_value, outputDir)
            if filepath:
                filesToOpen.append(filepath)
                if openOutputFiles:
                    IO_files_util.openFile(window, filepath)
        return

    if setup_complex != '':
        # Checkbox 2: display parents/children/simplex — fast setup-only lookup
        if parents_children_var.get() == 1:
            activate_parents_children()
        # Checkbox 3: extract document sources for the selected complex
        elif document_sources_var == 1:
            df = DB_PCACE_data_analyzer_util.get_document_sources_for_complex(inputDir, outputDir, setup_complex)
            if len(df) > 0 and openOutputFiles:
                output_file = os.path.join(outputDir, setup_complex + "_documents.xlsx")
                if os.path.exists(output_file):
                    IO_files_util.openFile(window, output_file)
        # Checkbox 4: export comments for the selected complex
        elif comments_var == 1:
            comment_type_str = comments_type if comments_type != '' else '*'
            outputFile = DB_PCACE_data_analyzer_util.get_comment_info('', setup_complex, comment_type_str, inputDir, outputDir)
            if outputFile is not None and not isinstance(outputFile, pd.DataFrame):
                if isinstance(outputFile, str):
                    filesToOpen.append(outputFile)
                elif isinstance(outputFile, list):
                    filesToOpen.extend(outputFile)
        else:
            # Export complex data via higher_lower, with extended headers option
            df = DB_PCACE_data_analyzer_util.higher_lower(inputDir, outputDir, setup_complex, extended_headers)
        # df = DB_PCACE_data_analyzer_util.call_get_expanded_complex(inputDir, outputDir, setup_complex)

    # get complex object identifier and values  ______________________________________________________________________________
    # if setup_complex != '':
        # data = DB_PCACE_data_analyzer_util.get_complex_data_ID(setup_complex)
        # mb.showwarning(title='Warning',
        #                message="YOU HAVE ADDED A RETURN!!!!!!!!!!!!!!!!!!!!!!!!!!\n\nMUST REMOVE IT.")
        # return

        # the next lines are used to test the three functions; nothing to do with the function identified by # -------
        # data_IDs = DB_PCACE_data_analyzer_util.get_complex_data_ID(setup_complex)
        # lowerComplex_IDs = DB_PCACE_data_analyzer_util.get_lower_complex(setup_complex)
        # lowestComplex_IDs = DB_PCACE_data_analyzer_util.get_lowest_complex(setup_complex)

        # mb.showwarning(title='Warning',
        #                message="YOU HAVE ADDED A RETURN in _main!!!!!!!!!!!!!!!!!!!!!!!!!!\n\nMUST REMOVE IT.")
        # return

# --------------------------------------------------------------------------------------

    # compute frequencies of complex/simplex objects ______________________________________________________________________________
    # complex frequencies
    # all frequencies
    if ALL_objects_frequencies_var:
        outputFile = DB_PCACE_data_analyzer_util.get_data_complex_frequencies(inputDir, outputDir, setup_complex)
        if outputFile != '':
            filesToOpen.append(outputFile)
        outputFile = DB_PCACE_data_analyzer_util.get_data_simplex_frequencies(inputDir, outputDir, setup_simplex)
        if outputFile!='':
            filesToOpen.append(outputFile)
    if SELECTED_objects_frequencies_var:
        if setup_complex!='':
            outputFile = DB_PCACE_data_analyzer_util.get_data_complex_frequencies(inputDir, outputDir, setup_complex)
            if outputFile != '':
                filesToOpen.append(outputFile)
        if setup_simplex!='':
            outputFile = DB_PCACE_data_analyzer_util.get_data_simplex_frequencies(inputDir, outputDir, setup_simplex)
            if outputFile != '':
                filesToOpen.append(outputFile)
        if setup_complex == '' and setup_simplex=='':
            mb.showwarning(title='Warning',
                   message="You must first select a specific complex or simplex object to run this function.\n\n"
                           "Please, select an object and try again.")
            return
        if outputFile != '':
            filesToOpen.append(outputFile)

    # display information about a specific simplex type and value (e.g., text type for "burley" value)

    if simplex_value!='' and value_parent_object_var:
        outputFiles = DB_PCACE_data_analyzer_util.get_data_simplex_info(inputDir, outputDir, simplex_value)
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)


    if semantic_triplet_var and google_earth_var:
        if setup_simplex == '':
            mb.showwarning(title='Warning',
                           message="To run the Semantic triplet SVO extractor with the option of visualizing the where via Google Earth Pro or Google Maps, you must first select the simplex name (e.g., City name, County) containing the location names to be geocoded and mapped, using the Simplex dropdown menu above.")
            return

# Visualization of semantic triplets SVO ----------------------------------------------------------------------------------------
    if semantic_triplet_var:
        svo_result_list=[]
        fileBase = os.path.basename(outputFile)[0:-5]
        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(outputFile, encodingValue='utf-8')

        if nRecords > 1:  # including headers; file is empty

            outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFile,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[],
                                                               columns_to_be_plotted_yAxis=['S Type'],
                                                               chart_title='Frequency Distribution of Subject Type',
                                                               # count_var = 1 for columns of alphabetic values
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType=str('S type'),
                                                               column_xAxis_label=str('Subject type'),
                                                               groupByList=[],
                                                               plotList=[],
                                                               chart_title_label='')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFile,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[],
                                                               columns_to_be_plotted_yAxis=['O Type'],
                                                               chart_title='Frequency Distribution of Object Type',
                                                               # count_var = 1 for columns of alphabetic values
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType=str('O type'),
                                                               column_xAxis_label=str('Object type'),
                                                               groupByList=[],
                                                               plotList=[],
                                                               chart_title_label='')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)


            outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFile,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[],
                                                               columns_to_be_plotted_yAxis=['Subject (S)'],
                                                               chart_title='Frequency Distribution of Subjects',
                                                               # count_var = 1 for columns of alphabetic values
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType=str('Subject (S)'),
                                                               column_xAxis_label=str('Subject (S)'),
                                                               groupByList=[],
                                                               plotList=[],
                                                               chart_title_label='')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFile,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[],
                                                               columns_to_be_plotted_yAxis=['Verb (V)'],
                                                               chart_title='Frequency Distribution of Verbs',
                                                               # count_var = 1 for columns of alphabetic values
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType=str('Verb (V)'),
                                                               column_xAxis_label=str('Verb (V)'),
                                                               groupByList=[],
                                                               plotList=[],
                                                               chart_title_label='')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFile,
                                                      outputDir,
                                                      columns_to_be_plotted_xAxis=[],
                                                      columns_to_be_plotted_yAxis=['Object (O)'],
                                                      chart_title='Frequency Distribution of Objects',
                                                      # count_var = 1 for columns of alphabetic values
                                                      count_var=1, hover_label=[],
                                                      outputFileNameType=str('Object (O)'),
                                                      column_xAxis_label=str('Object (O)'),
                                                      groupByList=[],
                                                      plotList=[],
                                                      chart_title_label='')
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            # Gephi graph

            if SVO_relations_visuals_var:

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
                fixed_param_var = 15
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

        # if semantic_triplet_var and wordcloud_var:
        #     nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(outputFile)
        #     if nRecords > 1:  # including headers; file is empty
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
                           message="You must select the time complex to be analyzed, using the complex dropdown menu on the right of the Time checkbox.")
            return

        if time_var and not semantic_triplet_var:
            # get_time_simplex(inputDir, outputDir, time_label, subject, verb, object, document_info, comment_type):
            outputFile = DB_PCACE_data_analyzer_util.get_time_simplex(inputDir, outputDir, time_label_var,
                                                                      semantic_triplet_subject, semantic_triplet_verb,
                                                                      semantic_triplet_object, document_sources_var, comments_var)
            if outputFile and time_label_var:
                generateChart(outputFile, time_label_var)

        if space_var and not space_label_var:
            mb.showwarning(title='Warning',
                           message="You must select the space complex to be analyzed, using the complex dropdown menu on the right of the Space checkbox.")
            return

        if space_var and not semantic_triplet_var:
            # def get_space_simplex(inputDir, outputDir, space_label_var, subject, verb, object, macro_event_ID, comment_type='', document_info=False):
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
            location_filename = DB_PCACE_data_analyzer_util.get_data_simplex_frequencies(setup_simplex, inputDir, outputDir, False)

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

            if outputFile is not None and not isinstance(outputFile, pd.DataFrame):
                if len(outputFile) > 0:
                    # since outputFile produced by KML is a list cannot use append
                    filesToOpen = filesToOpen + outputFile

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.charts_package_options_widget.get(),
                                GUI_util.data_transformation_options_widget.get(),
                                simplex_value_type_var.get(),
                                simplex_value.get(),
                                complex_identifiers_var.get(),
                                value_parent_object_var.get(),
                                setup_complex.get(),
                                extended_headers_var.get(),
                                setup_simplex.get(),
                                # print_narrative_var.get(),
                                ALL_objects_frequencies_var.get(),
                                SELECTED_objects_frequencies_var.get(),
                                ALL_simplex_objects_frequencies_var.get(),
                                SELECTED_simplex_objects_frequencies_var.get(),
                                complex_parents_var.get(),
                                complex_children_var.get(),
                                semantic_triplet_var.get(),
                                semantic_triplet_subject.get(),
                                semantic_triplet_verb.get(),
                                semantic_triplet_object.get(),
                                actors_var.get(),
                                time_var.get(),
                                time_label_var.get(),
                                space_var.get(),
                                space_label_var.get(),
                                SVO_relations_visuals_var.get(),wordcloud_var.get(),google_earth_var.get(),
                                document_sources_var.get(), comments_var.get(), comments_type_var.get(),
                                from_dataID_setupID_objectType_var.get(), enter_data_ID_var.get(),
                                hierarchical_complex_var.get(),
                                search_simplex_var.get(), search_simplex_results_var.get())

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
extended_headers_var = tk.IntVar()
parents_children_var = tk.IntVar()

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

complex_parents_var = tk.StringVar()
complex_children_var = tk.StringVar()
SVO_relations_visuals_var = tk.IntVar()
wordcloud_var = tk.IntVar()
google_earth_var = tk.IntVar()

enter_data_ID_var = tk.StringVar()
setup_name_var = tk.StringVar()

def clear(e):
    value_parent_object_var.set(0)
    setup_complex=''
    setup_simplex=''
    select_DB_tables_var.set('')

    simplex_value_type_var.set('')
    simplex_list=[]
    simplex_value_var.set(simplex_list)
    simplex_value_var.set('')
    simplex_value['values'] = []

    hierarchical_complex_var.set('')
    complex_identifiers_var.set('')

    search_simplex_var.set('')
    search_simplex_results_var.set('')

    setup_complex_var.set('')
    setup_simplex_var.set('')

    extended_headers_var.set(0)
    value_parent_object_var.set(0)
    parents_children_var.set(0)
    complex_parents_var.set('')
    complex_children_var.set('')

    ALL_objects_frequencies_var.set(0)
    SELECTED_objects_frequencies_var.set(0)

    semantic_triplet_var.set(0)
    semantic_triplet_subject.set(''),
    semantic_triplet_verb.set(''),
    semantic_triplet_object.set(''),
    SVO_relations_visuals_var.set(0)
    wordcloud_var.set(0)
    google_earth_var.set(0)
    time_var.set(0)
    time_label_var.set('')
    space_var.set(0)
    space_label_var.set('')
    actors_var.set('')
    setup_complex_var.set('')
    comments_var.set(0)
    comments_type_var.set('')
    document_sources_var.set(0)
    from_dataID_setupID_objectType_var.set('')
    enter_data_ID_var.set('')
    setup_name_var.set('')
    GUI_util.clear("Escape")

    GUI_util.tips_dropdown_field.set('Open TIPS files')
window.bind("<Escape>", clear)

table_list = []
table_menu_list = []

def open_sql_query():
    """Export PC-ACE tables to SQLite and open the SQL query GUI."""
    if inputDir.get() == '':
        mb.showwarning(title='Warning', message='No input directory selected.\n\nPlease, select a PC-ACE input directory first.')
        return
    db_path = DB_PCACE_data_analyzer_util.create_sqlite_from_pcace(inputDir.get(), outputDir.get())
    if db_path:
        mb.showwarning(title='SQLite database created',
                       message=f'PC-ACE tables have been exported to SQLite:\n\n{db_path}\n\nThe SQL query GUI will now open with this database pre-selected.')
        # Launch DB_SQL_main.py
        import subprocess
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DB_SQL_main.py')
        subprocess.Popen([sys.executable, script_path])

open_sql_button = tk.Button(window, text='Open SQL query', width=17,height=1,state='normal', command=lambda: open_sql_query())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_sql_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to export all PC-ACE tables to an SQLite database and open the SQL query GUI.\nYou can then run any SQL query against the PC-ACE data.")

view_relations_button = tk.Button(window, text='View table relations', width=17,height=1,state='normal', command=lambda: view_relations())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   view_relations_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to open a pdf file of the PC-ACE table relations. These relations are ALWAYS the same across any type of application of PC-ACE (e.g., Avanti! or Lynchings).\nTo view the grammar of data collection for a specific PC-ACE implementation click on the button View grrammar.")

view_grammar_button = tk.Button(window, text='View grammar', width=17,height=1,state='normal', command=lambda: view_grammar())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+150, y_multiplier_integer,
                                   view_grammar_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to export as a text file the grammmar used for the selected, specific implementation of the PC-ACE database.\nThe grammar will be exported in the same directory of the Input Excel files.\nClick on the button View table relations to visualize the general table relations in the PC-ACE databasee, regardless of a selected, specific implementation (i./e., grammar setup).")

update_grammar_button = tk.Button(window, text='Update grammar', width=17,height=1,state='normal', command=lambda: update_grammar())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+300, y_multiplier_integer,
                                   update_grammar_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to update the grammmar used for the selected, specific implementation of the PC-ACE database saved in setup_complex.xlsx and setup_complex.pkl.\nThe grammar will be saved in setup_complex.xlsx and setup_complex.pkl.\nClick on the button View table relations to visualize the general table relations in the PC-ACE databasee, regardless of a selected, specific implementation (i./e., grammar setup).")


update_identifier_button = tk.Button(window, text='Update identifiers', width=17,height=1,state='normal', command=lambda: update_identifiers())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+20, y_multiplier_integer,
                                   update_identifier_button,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Click to update the current complex objects identifiers saved in the table data_Complex.xlsx and data_Complex.pkl")

select_DB_tables_lb = tk.Label(window, text='PC-ACE table ')
# open_setup_x_coordinate
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate,y_multiplier_integer,select_DB_tables_lb,True)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,select_DB_tables_lb,True)

table_menu_values = ''
table_list=[]
if os.path.isdir(inputDir.get()):
    table_list = DB_PCACE_data_analyzer_util.import_PCACE_tables(inputDir.get(), outputDir.get())
    table_menu_values = ", ".join(table_list)
select_DB_tables = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=select_DB_tables_var)
select_DB_tables.configure(state='disabled')
select_DB_tables['values'] = table_menu_values
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+100, y_multiplier_integer,
                                   select_DB_tables,
                                   False, False, True, False, 90, GUI_IO_util.setup_IO_brief_coordinate,
                                   "Use the dropdown menu to select a PC-ACE table to be opened for display; click RUN after selection.")

simplex_value_type_lb = tk.Label(window, text='Simplex data type ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,simplex_value_type_lb,True)

simplex_value_type_var= tk.StringVar()
simplex_value_type_menu = tk.OptionMenu(window, simplex_value_type_var, 'text','date', 'number')
simplex_value_type_menu.configure(state='disabled')
simplex_value_type_var.set('')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_S_dictionary, y_multiplier_integer,
                                   simplex_value_type_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_S_dictionary,
                                   "Use the dropdown menu to select the simplex data type to be used to extract a list of all available values.")

inputDirSV = ''
# simplex_value = ''
simplex_value_var = tk.StringVar()
# simplex_value_var.set(simplex_list)
# simplex_value_var = simplex_list
simplex_value = ttk.Combobox(window, textvariable = simplex_value_var, width=GUI_IO_util.widget_width_short)
simplex_value.configure(state='disabled')

try:
    simplex_list = DB_PCACE_data_analyzer_util.get_data_simplex_text_date_number(simplex_value_type_var.get())
except:
    simplex_list=[]
simplex_value_menu = simplex_list
simplex_value['values'] = simplex_value_menu
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+350, y_multiplier_integer,
                                   simplex_value,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate+300,
                                   "Use the dropdown menu to select the simplex data type value (e.g., police) for which you want to find simplex & complex objects usage")

def activate_date_number_text(*args):
    if simplex_value_type_var.get()!='':
        simplex_value.configure(state='normal')
    else:
        simplex_value.configure(state='disabled')
    simplex_list = DB_PCACE_data_analyzer_util.get_data_simplex_text_date_number(simplex_value_type_var.get())
    simplex_value_var.set(simplex_list)
    simplex_value['values'] = simplex_list
simplex_value_type_var.trace('w',activate_date_number_text)

value_parent_object_checkbox = tk.Checkbutton(window, text='Get simplex/complex objects of selected data type (& value)', variable=value_parent_object_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   value_parent_object_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Tick the checkbox to export simplex and complex objects that use the selected data type and, perhaps, value")

hierarchical_complex_objects_lb = tk.Label(window, text='Hierarchical complex objects')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,hierarchical_complex_objects_lb,True)

hierarchical_complex_menu = []  # populated in changed_filename after build_libraries

hierarchical_complex_var=tk.StringVar()
hierarchical_complex = ttk.Combobox(window, textvariable = hierarchical_complex_var, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
hierarchical_complex['values'] = hierarchical_complex_menu
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu-50, y_multiplier_integer,
                                   hierarchical_complex,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to select a specific hierarchical complex oject (e.g., Macro event, Event, SDemantic triplet.")

complex_identifiers_lb = tk.Label(window, text='Complex identifier')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,complex_identifiers_lb,True)

complex_identifiers_menu = DB_PCACE_data_analyzer_util.build_macro_event_dropdown_menu(inputDir.get())

complex_identifiers_var=tk.StringVar()
complex_identifiers = ttk.Combobox(window, textvariable = complex_identifiers_var, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
complex_identifiers['values'] = complex_identifiers_menu
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   complex_identifiers,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to select a specific hierarchical complex object by its identifier to analyze.\nWhen a specific hierarchical complex is selected, all analyses (e.g., SVO, actors) will be based on that hierarchical complex object..")

def update_complex_identifier_dropdown(*args):
    """When user selects a hierarchical complex type, update the Complex identifier dropdown
    with all instances of that type (ID - Identifier)."""
    selected_type = hierarchical_complex_var.get()
    if selected_type:
        identifier_list = DB_PCACE_data_analyzer_util.build_story_dropdown(selected_type)
        complex_identifiers['values'] = identifier_list
        complex_identifiers_var.set('')
    else:
        # Reset to macro event list
        macro_list = DB_PCACE_data_analyzer_util.build_macro_event_dropdown_menu(inputDir.get())
        complex_identifiers['values'] = macro_list
        complex_identifiers_var.set('')

hierarchical_complex_var.trace('w', update_complex_identifier_dropdown)

# Search simplex value → story form row ___________________________________________

search_simplex_lb = tk.Label(window, text='Search simplex value')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,search_simplex_lb,True)

search_simplex_var = tk.StringVar()
search_simplex_entry = tk.Entry(window, textvariable=search_simplex_var, width=20)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu-50, y_multiplier_integer,
                                   search_simplex_entry,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Enter a simplex value to search for (e.g., a city name like 'Barnesville', a person name, etc.).\nThe search is case insensitive (both barnesville and Barneville will produce the same result).\nThe search will find all hierarchical objects (++, e.g., Macro Event, Event, Semantic Triplet) containing that value.")

search_simplex_results_lb = tk.Label(window, text='Search results')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,search_simplex_results_lb,True)

search_simplex_results_var = tk.StringVar()
search_simplex_results = ttk.Combobox(window, textvariable=search_simplex_results_var, width=GUI_IO_util.widget_width_short)
search_simplex_results['values'] = []
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                   search_simplex_results,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Displays the hierarchical objects (++) that contain the searched simplex value.\nSelect one to view its story form, or click RUN to export all to a text file.")


from_dataID_setupID_lb = tk.Label(window, text='From data ID to setup ID ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,from_dataID_setupID_lb,True)

from_dataID_setupID_objectType_var = tk.StringVar()
from_dataID_setupID_objectType_var.set('')
from_dataID_setupID_menu = tk.OptionMenu(window, from_dataID_setupID_objectType_var, 'Complex', 'Simplex')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu-50, y_multiplier_integer,
                                   from_dataID_setupID_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Use the dropdown menu to select the type of object - complex or simplex - to go from data ID to setup name")

enter_data_ID_lb = tk.Label(window, text='Enter data ID')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate,y_multiplier_integer,enter_data_ID_lb,True)

enter_data_ID = tk.Entry(window,width=GUI_IO_util.widget_width_extra_short,textvariable=enter_data_ID_var)
# enter_data_ID.configure(state="disabled")
# place widget with hover-over info

y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+100,
    y_multiplier_integer,
    enter_data_ID, True, False, True, False, 90,
    GUI_IO_util.open_setup_x_coordinate+130, "Enter the numeric data ID value")

setup_name = tk.Entry(window,width=GUI_IO_util.widget_width_short,textvariable=setup_name_var)
# setup_name.configure(state="disabled")
# place widget with hover-over info

y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,
    y_multiplier_integer,
    setup_name, False, False, True, False, 90,
    GUI_IO_util.run_button_x_coordinate+20, "Extracted setup name")

def run_simplex_search(*args):
    """When user presses Enter in the search box, search and populate results dropdown."""
    search_term = search_simplex_var.get().strip()
    print(f"  run_simplex_search triggered with: '{search_term}'")
    if not search_term:
        return
    results = DB_PCACE_data_analyzer_util.build_search_results_dropdown(search_term)
    print(f"  build_search_results_dropdown returned {len(results)} results: {results[:3]}")
    search_simplex_results['values'] = results
    if results:
        search_simplex_results_var.set(results[0])
        mb.showwarning(title='Search results',
                       message=f'Found {len(results)} hierarchical object(s) containing "{search_term}".\n\nSelect one from the dropdown and click RUN to display its story form, or clear the dropdown and click RUN to export all stories.')
    else:
        search_simplex_results_var.set('')
        mb.showwarning(title='Search results',
                       message=f'No hierarchical objects found containing "{search_term}".')

search_simplex_entry.bind('<Return>', run_simplex_search)

SVO_relations_visuals_var.set(0)
SVO_relations_visuals_checkbox = tk.Checkbutton(window, text='Visualize SVO relations (Gephi, Sankey, Sunburst, Word cloud)',
                                variable=SVO_relations_visuals_var, onvalue=1, offvalue=0)
SVO_relations_visuals_checkbox.configure(state='disabled')

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+20, y_multiplier_integer,
                                   SVO_relations_visuals_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox to visualize the triplet SVOs via  Gephi, Sankey, sunburst, treemap, colormap, and word clouds.\nSankey graphs display top 10 Subject (S), 20 Verb (V), 20 Object (O). Sunburst and Treemap charts display top 15 values. Use data_visualization_1 GUI to change default values.\nSpace information is geocoded via Google if the Google-geocode-API_config.csv file is present in the config subdirectory; otherwise Nominatim is used. Geocoded waypoints are displayed as pin map via Google Earth Pro and heat map via Google Maps (Python Folium will be used if no Google API key is found).")

google_earth_var.set(0)
google_earth_checkbox = tk.Checkbutton(window, text='Visualize Where (via Google Maps & Google Earth Pro or Python Folium)',
                                       variable=google_earth_var, onvalue=1, offvalue=0)
google_earth_checkbox.configure(state='disabled')

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                   google_earth_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.watch_videos_x_coordinate,
                                   "Tick the checkbox to visualize the space of SVOs as in a Google Earth Pro pin map and Google Maps heat map.\nSpace information will be geocoded using Google if the Google-geocode-API_config.csv file is present in the config subdirectory; otherwise Nominatim will be used.\nGeocoded waypoints will be displayed as pin map via Google Earth Pro and heat map via Google Maps (Python Folium will be used if no Google API key is found).")

complex_objects_lb = tk.Label(window, text='Complex ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,complex_objects_lb,True)

setup_complex_menu, setup_simplex_menu = DB_PCACE_data_analyzer_util.get_setup_complex_simplex_names() # os.path.join(inputDir.get())

setup_complex_var=tk.StringVar()
setup_complex = ttk.Combobox(window, textvariable = setup_complex_var, width=GUI_IO_util.widget_width_short)
# setup_complex.configure(state='disabled')
setup_complex['values'] = setup_complex_menu
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+120, y_multiplier_integer,
                                   setup_complex,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to select a specific complex object for which to display identifier and values and compute frequencies.\nWhen a hierarchical complex object is selected (e.g., macro-event or event) and the checkbox Semantic triplets below is ticked...\n...semantic triplets will be listed in chronological order within the specific higher-level hierarchical complex object selected (e.g., macro-events, events).")


extended_headers_checkbox = tk.Checkbutton(window, text='', variable=extended_headers_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+20, y_multiplier_integer,
                                   extended_headers_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Tick the checkbox to display the selected complex object as an Excel and text story form outputs")

parents_children_checkbox = tk.Checkbutton(window, text='', variable=parents_children_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+40, y_multiplier_integer,
                                   parents_children_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Tick the checkbox to display the parents and children of the selected complex object")

document_sources_var = tk.IntVar()
document_sources_checkbox = tk.Checkbutton(window, text='', variable=document_sources_var, onvalue=1, offvalue=0)

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+60, y_multiplier_integer,
                                   document_sources_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox to extract the documents (e.g., newspaper articles) that are the sources of information for specific objects (e.g., Semantic triplets (SVO)).")

comments_var = tk.IntVar()
comments_var.set(0)
comments_checkbox = tk.Checkbutton(window, text='', variable=comments_var, onvalue=1, offvalue=0)

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+80, y_multiplier_integer,
                                   comments_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox to extract the comments left by users and/or verifiers for specific objects (e.g., Semantic triplets (SVO)).")

# comments_lb = tk.Label(window, text='Extract comments ')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate,y_multiplier_integer,comments_lb,True)
#
comments_type_var = tk.StringVar()
comments_type_var.set('')
comments_menu = tk.OptionMenu(window, comments_type_var, '*', 'Users comments', 'Verifiers comments')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+105, y_multiplier_integer,
                                   comments_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Use the dropdown menu to extract the comments left by users and/or verifiers for specific objects (e.g., Semantic triplets (SVO)).")

simplex_objects_lb = tk.Label(window, text='Simplex ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,simplex_objects_lb, True)

# setup_simplex_menu = DB_PCACE_data_analyzer_util.get_complex_simplex_names(os.path.join(inputDir.get()))
#
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

select_parents = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=complex_parents_var)
# select_parents.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+120, y_multiplier_integer,
                                   select_parents,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "The menu displays a list of complex objects parent of the 'Complex objects' or 'Simplex objects' selected in the widgets above")

select_children_lb = tk.Label(window, text='Complex children ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,select_children_lb,True)

select_children = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=complex_children_var)
# select_children.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   select_children,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "The menu displays a list of complex objects children of the 'Complex objects' selected in the widget above.\nThe option is only available for the 'Complex objects' widget above (Simplex objects do not have children).")


# def activate_parents_children(*args):
#     # @@@
#     # DB_PCACE_data_analyzer_util.load_lib(inputDir.get())
#     parents_complex_list = DB_PCACE_data_analyzer_util.get_parent_complex(setup_complex_var.get())
#     select_parents['values'] = parents_complex_list
#
#     children_list = DB_PCACE_data_analyzer_util.get_child_complex(setup_complex_var.get())
#     select_children['values'] = children_list
#     # complex_children_var.set(children_menu[0])
# setup_complex_var.trace('w',activate_parents_children)
# setup_simplex_var.trace('w',activate_parents_children)
#


error = False
database_already_loaded = False
table_values = []
currentInputDir = inputDir.get()
readDir = False
def changed_filename(*args):
    global error, setup_simplex_menu, currentInputDir, readDir, database_already_loaded, inputDirSV
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
        table_list = DB_PCACE_data_analyzer_util.import_PCACE_tables(inputDir.get(), outputDir.get())
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
            # select_DB_tables.set(table_menu_values[0])
            select_DB_tables.set('')

        else:
            select_DB_tables.set('')
            select_DB_tables.configure(state='disabled')

        if currentInputDir != inputDir.get() or not readDir:
            # load all Excel sheets and store in data
            # DB_PCACE_data_analyzer_util.load_lib(inputDir.get(), outputDir.get())
            DB_PCACE_data_analyzer_util.build_libraries(inputDir.get(), outputDir.get())
            currentInputDir = inputDir.get()
            readDir = True

        setup_complex_menu, setup_simplex_menu = DB_PCACE_data_analyzer_util.get_setup_complex_simplex_names() # os.path.join(inputDir.get())
        setup_complex['values'] = setup_complex_menu
        if len(setup_complex_menu)>0:
            simplex_value_type_menu.configure(state='normal')
            select_DB_tables.configure(state='normal')
            setup_complex.configure(state='normal')
            # setup_complex.set(setup_complex_menu[0])
            setup_complex.set('')
            if not database_already_loaded:
                complex_identifiers_menu = DB_PCACE_data_analyzer_util.build_macro_event_dropdown_menu(inputDir.get())
                complex_identifiers['values'] = complex_identifiers_menu
                # Populate hierarchical complex dropdown
                hierarchical_complex_menu = DB_PCACE_data_analyzer_util.build_hierarchical_complex_dropdown_menu(inputDir.get())
                hierarchical_complex['values'] = hierarchical_complex_menu
                complex_identifiers['values'] = complex_identifiers_menu
                database_already_loaded = True
        else:
            simplex_value_type_menu.configure(state='disabled')
            setup_complex.set('')
            setup_complex.configure(state='disabled')
        # setup_simplex_menu = DB_PCACE_data_analyzer_util.get_data_complex_simplex_names(os.path.join(inputDir.get()))

        # @@@
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
            simplex_value_type_menu.configure(state='disabled')
            GUI_util.run_button.configure(state='disabled')
            error = True
    clear("Escape")
GUI_util.inputFilename.trace('w', changed_filename)
GUI_util.input_main_dir_path.trace('w', changed_filename)


def activate_parents_children(*args):
    parents_complex_list = []
    children_complex_list_all = []
    children_complex_list_required = []
    simplex_children_all_list = []
    simplex_children_required_list = []
    if setup_complex_var.get()!='':
        parents_complex_list = DB_PCACE_data_analyzer_util.get_setup_complex_parents(setup_complex_var.get())
        children_complex_list_all, children_complex_list_required = DB_PCACE_data_analyzer_util.get_setup_complex_children(setup_complex_var.get())
        if len(parents_complex_list)>0:
            complex_parents_var.set(str(parents_complex_list[0]))
            if len(parents_complex_list) > 1:
                timing = 2000
                IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Warning',
                                                   "The selected complex '" + str(setup_complex_var.get()) + "' has " + str(len(parents_complex_list)) + " complex parents. Only the first one is displayed. Use the dropdown menu to scroll through all available complex parent names.",
                                                   False, '', True, '', False)
                # mb.showwarning(title='Warning',
                #                message="The selected complex '" + str(setup_complex_var.get()) + "' has " + str(len(parents_complex_list)) + " complex parents. Only the first one is displayed. Use the dropdown menu to scroll through all available complex parent names.")
            select_parents['values'] = parents_complex_list

        if len(children_complex_list_all)>0:
            complex_children_var.set(str(children_complex_list_all[0]))
        #     if len(children_complex_list_all) > 1:
        #         timing = 2000
        #         IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Warning',
        #                                            "The selected complex '" + str(setup_complex_var.get()) + "' has " + str(len(parents_complex_list)) + " complex parents. Only the first one is displayed. Use the dropdown menu to scroll through all available complex parent names.",
        #                                            False, '', True, '', False)
        #
        simplex_children_all_list, simplex_children_required_list = DB_PCACE_data_analyzer_util.get_setup_complex_simplex_children(setup_complex_var.get())
        setup_simplex_menu = simplex_children_all_list
        setup_simplex['values'] = setup_simplex_menu
        if len(setup_simplex_menu)>0:
            setup_simplex_var.set(str(simplex_children_all_list[0]))
        # if len(simplex_children_list)>0:
        #     if len(parents_complex_list) > 1:
        #         timing = 2000
        #         IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Warning',
        #                                            "The selected complex " + str(setup_complex_var.get()) + " has " + str(len(parents_complex_list)) + " complex parents. Only the first one is displayed. Use the dropdown menu to scroll through all available complex parent names.",
        #                                            False, '', True, '', False)
                # mb.showwarning(title='Warning',
                #                message="The selected complex " + str(setup_complex_var.get()) + " has " + str(len(parents_complex_list)) + " complex parents. Only the first one is displayed. Use the dropdown menu to scroll through all available complex parent names.")

        if len(children_complex_list_all) > 0:
            complex_children_var.set(str(children_complex_list_all[0]))
            if len(children_complex_list_all) > 1:
                timing = 2000
                IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Warning',
                                                   "The selected complex '" + str(setup_complex_var.get()) + "' has " + str(
                                                    len(children_complex_list_all)) + " complex children. Only the first one is displayed. Use the dropdown menu to scroll through all available complex children names.",
                                                   False, '', True, '', False)

                # mb.showwarning(title='Warning',
                #                message="The selected complex " + str(setup_complex_var.get()) + " has " + str(
                #                    len(children_list)) + " complex children. Only the first one is displayed. Use the dropdown menu to scroll through all available complex children names.")
        else:
            mb.showwarning(title='Warning',
                           message="The selected complex '" + str(setup_complex_var.get()) + "' has no complex children.")
        select_children['values'] = children_complex_list_all

    if setup_simplex_var.get()!='':
        # setup_simplex_var.set(str(setup_simplex_menu[0]))
        parents_complex_list = DB_PCACE_data_analyzer_util.get_setup_simplex_parent(setup_simplex_var.get())
        if len(parents_complex_list) > 0:
            complex_parents_var.set(str(parents_complex_list[0]))
            if len(parents_complex_list) > 1:
                mb.showwarning(title='Warning',
                               message="The selected simplex " + str(setup_simplex_var.get()) + " has " + str(
                                   len(parents_complex_list)) + " complex parents. Only the first one is displayed. Use the dropdown menu to scroll through all available complex parent names.")
            select_parents['values'] = parents_complex_list

# Traces removed — parents/children/simplex lookups now happen only via RUN + checkbox
# setup_complex_var.trace('w',activate_parents_children)
# setup_simplex_var.trace('w',activate_parents_children)

table_fields_menu_values = []

def view_relations():
    TIPS_util.open_TIPS('TIPS_NLP_PC-ACE table relations.pdf')


def view_grammar():
    head, tail = os.path.split(inputDir.get())
    DB_PCACE_data_analyzer_util.view_grammar(os.path.join(inputDir.get(), 'setup_Complex.xlsx'),
                                             'GrammarRule_Text', os.path.join(inputDir.get(),
                                                                              'PC-ACE grammar for database ' + tail + '.txt'))
def update_grammar():
    head, tail = os.path.split(inputDir.get())
    DB_PCACE_data_analyzer_util.update_grammar_text(inputDir.get())

def update_identifiers():
    head, tail = os.path.split(inputDir.get())
    DB_PCACE_data_analyzer_util.update_all_identifiers(inputDir.get())

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
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, click on the View table relations button to open a pdf file visualizing PC-ACE table relations." +
                                "\n\nUse the dropdown menu to open a selected table file." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the simplex data value (text, date, or number) "
                            "for which you want to see its usage among parent simplex and complex."
                            "\n\nThe available values will be displayed in the next dropdown menu widget where you can select a specific value."
                            "\n\nYou can then tick the 'Get simplex/complex objects...' checkbox if you wish to visualize all simplex and complex ojects that use the selected value (e.g.,'police') " + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "The dropdown menu displays all the PRIMARY COMPLEX objects (Macro events)." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "The dropdown menu displays all the PRIMARY COMPLEX objects (Macro events)." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "The dropdown menu displays all the PRIMARY COMPLEX objects (Macro events)." + GUI_IO_util.msg_Esc)
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
readMe_message="The Python 3 scripts convert, via the Python Pandas package, and analyze, via various visualization packages, data collected via the Microsoft ACCESS PC-ACE (Program for Computer-Assisted Coding of Events).\n\nIn INPUT the algorithms expect a set of xlsx files in the input directory. The xlsx files must be exported from the PC-ACE database tables data, setup, and utility (see TIPS file on how to export tables from PC-ACE).\n\nIn OUTPUT the algorithms produce a set of csv files and different types of visuals, from Excel charts to network graphs via Gephi and Sankey, geographic pin maps via Google Earth Pro and heat maps via Google Maps, word clouds, and interactive time maps."
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
#     primary_complex_menu = DB_PCACE_data_analyzer_util.build_macro_event_dropdown_menu(inputDir.get())
#     primary_complex['values'] = primary_complex_menu
GUI_util.window.mainloop()

