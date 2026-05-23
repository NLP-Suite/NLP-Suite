
import sys
import tkinter

import IO_libraries_util
import GUI_util

# if IO_libraries_util.install_all_Python_packages(GUI_util.window, "DB_PC-ACE_data_analyzer_main.py", ['os', 'tkinter','pandas'])==False:
#     sys.exit(0)

import os
import datetime
import pandas as pd
from subprocess import call

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
        setup_complex, identifiers, extended_headers, setup_simplex,
        # print_narrative_var,
        complex_parents_var, complex_children_var,
        document_sources_var, comments_var, comments_type,
        from_dataID_setupID_objectType_var, enter_data_ID_var,
        search_simplex_value='', search_simplex_result='',
        required_object_type='', required_object_name=''):

    config_filename = GUI_util.config_filename_selected_config.get()

    filesToOpen = []
    outputFile = ''


    import os
    if select_DB_tables_var.get()!='':
        IO_files_util.openFile(window, inputDir + os.sep + select_DB_tables_var.get() + ".xlsx")
        return

    # Toggle REQUIRED boolean if an object type and name are selected
    if required_object_type != '' and required_object_name != '':
        _toggle_required()
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

    # Story form export from Complex identifier dropdown ______________________________________________
    # If user selected a specific identifier from the dropdown → export that one story form
    # But checkboxes, GIS, simplex operations, and search all take priority over auto-displayed identifier
    any_simplex_checkbox = (simplex_export_values_var.get() == 1 or
                            simplex_spell_check_var.get() == 1 or
                            simplex_charts_var.get() == 1 or
                            simplex_timechart_var.get() == 1 or
                            simplex_GIS_var.get() == 1)
    any_other_operation = (identifiers == 1 or extended_headers == 1 or
                           document_sources_var == 1 or comments_var == 1 or
                           parents_children_var.get() == 1 or
                           any_simplex_checkbox or
                           search_simplex_value != '' or
                           simplex_value != '')
    if primary_complex_var != '' and not any_other_operation:
        # User selected a specific identifier → export that one story form (txt + HTML)
        story_text, filepath = DB_PCACE_data_analyzer_util.story_form_from_dropdown(primary_complex_var, outputDir)
        if filepath:
            filesToOpen.append(filepath)
        html_filepath = DB_PCACE_data_analyzer_util.story_form_html_from_dropdown(primary_complex_var, outputDir)
        if html_filepath:
            filesToOpen.append(html_filepath)
            mb.showwarning(title='Story form',
                           message=f'Story form saved to:\n{filepath}\n\nHTML version saved to:\n{html_filepath}')
            if openOutputFiles:
                IO_files_util.openFile(window, html_filepath)
        elif filepath:
            mb.showwarning(title='Story form',
                           message=f'The story form has been saved to:\n{filepath}')
            if openOutputFiles:
                IO_files_util.openFile(window, filepath)
        return

    # Search simplex value → story form export (txt + HTML) ______________________________________
    if search_simplex_value != '':
        # Populate search results dropdown (in case user clicked RUN without pressing Enter first)
        dropdown_results = DB_PCACE_data_analyzer_util.build_search_results_dropdown(search_simplex_value)
        search_simplex_results['values'] = dropdown_results
        # Do NOT auto-select first item — let user selection determine single vs. all export

        if search_simplex_result != '':
            # User selected a specific result → show its story form (txt + HTML)
            story_text, filepath = DB_PCACE_data_analyzer_util.story_form_from_dropdown(search_simplex_result, outputDir)
            if filepath:
                filesToOpen.append(filepath)
            # Also export HTML version with highlighted simplex values
            html_filepath = DB_PCACE_data_analyzer_util.story_form_html_from_dropdown(search_simplex_result, outputDir)
            if html_filepath:
                filesToOpen.append(html_filepath)
                mb.showwarning(title='Story form',
                               message=f'Story form saved to:\n{filepath}\n\nHTML version (with highlighted simplex values) saved to:\n{html_filepath}')
                if openOutputFiles:
                    IO_files_util.openFile(window, html_filepath)
            elif filepath:
                mb.showwarning(title='Story form',
                               message=f'The story form has been saved to:\n{filepath}')
                if openOutputFiles:
                    IO_files_util.openFile(window, filepath)
        else:
            # No specific result selected → export all stories (txt + HTML)
            # Warn user if there are many objects
            n_objects = len(dropdown_results) if dropdown_results else 0
            proceed = True
            if n_objects > 50:
                proceed = mb.askyesno("Creating story forms",
                    f"There are {n_objects} complex objects. Creating a separate story form for each object "
                    f"will take a long time and create a large number of files.\n\n"
                    f"Are you sure you want to do that?\n\n"
                    f"(Tip: select a specific object from the dropdown and press Enter to view just that one.)",
                    default='no')
            if proceed:
                filepath = DB_PCACE_data_analyzer_util.search_and_export_stories(search_simplex_value, outputDir)
                if filepath:
                    filesToOpen.append(filepath)
                html_filepath = DB_PCACE_data_analyzer_util.search_and_export_stories_html(search_simplex_value, outputDir)
                if html_filepath:
                    filesToOpen.append(html_filepath)
                    if openOutputFiles:
                        IO_files_util.openFile(window, html_filepath)
                elif filepath:
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
            comment_files = DB_PCACE_data_analyzer_util.get_comment_info('', setup_complex, comment_type_str, inputDir, outputDir)
            if comment_files:
                filesToOpen.extend(comment_files)
        elif identifiers == 1:
            # Export identifiers only (Actor_IDENTIFIER)
            df = DB_PCACE_data_analyzer_util.higher_lower(inputDir, outputDir, setup_complex, export_identifier=True)
        elif extended_headers == 1:
            # Export expanded ALL headers (Actor_ALL)
            df = DB_PCACE_data_analyzer_util.higher_lower(inputDir, outputDir, setup_complex, export_identifier=False)
        else:
            # No checkbox selected: if identifier dropdown has items, export ALL story forms;
            # otherwise fall back to default higher_lower tabular export
            dropdown_vals = complex_identifiers['values']
            n_objects = len(dropdown_vals) if dropdown_vals else 0
            if n_objects > 0:
                proceed = True
                if n_objects > 50:
                    proceed = mb.askyesno("Export all story forms",
                        f'There are {n_objects} "{setup_complex}" objects. Creating a story form for each '
                        f'will take a long time and create large files.\n\n'
                        f'Are you sure you want to do that?\n\n'
                        f'(Tip: select a specific object from the Complex identifier dropdown and click RUN to export just that one.)',
                        default='no')
                if proceed:
                    filepath = DB_PCACE_data_analyzer_util.export_all_stories_for_type(setup_complex, outputDir)
                    if filepath:
                        filesToOpen.append(filepath)
                    html_filepath = DB_PCACE_data_analyzer_util.export_all_stories_html_for_type(setup_complex, outputDir)
                    if html_filepath:
                        filesToOpen.append(html_filepath)
                        if openOutputFiles:
                            IO_files_util.openFile(window, html_filepath)
                    elif filepath:
                        if openOutputFiles:
                            IO_files_util.openFile(window, filepath)
                return
            else:
                # No identifiers in dropdown — default tabular export
                df = DB_PCACE_data_analyzer_util.higher_lower(inputDir, outputDir, setup_complex, export_identifier=False)
        # df = DB_PCACE_data_analyzer_util.call_get_expanded_complex(inputDir, outputDir, setup_complex)

        # ── Auto-chart the higher_lower output ──────────────────────────────
        if df is not None and not df.empty and chartPackage != 'No charts':
            suffix = '_IDENTIFIER' if identifiers == 1 else '_ALL'
            csv_for_charts = os.path.join(outputDir, setup_complex + suffix + '.csv')
            # Always overwrite the CSV so charts reflect the latest data
            df.to_csv(csv_for_charts, index=False, encoding='utf-8')
            filesToOpen.append(csv_for_charts)
            charts_util.auto_chart_cross_complex(csv_for_charts, outputDir, chartPackage, filesToOpen)

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

    # display information about a specific simplex type and value (e.g., text type for "burley" value)

    if simplex_value!='' and value_parent_object_var:
        outputFiles = DB_PCACE_data_analyzer_util.get_data_simplex_info(inputDir, outputDir, simplex_value)
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # ── Simplex operations (checkbox-driven) ──────────────────────────────────────
    if setup_simplex != '':
        # Determine simplex value type once for checkbox-specific logic
        try:
            vtype = DB_PCACE_data_analyzer_util.get_simplex_value_type(setup_simplex)
        except Exception:
            vtype = 0

        # ── Values CSV ────────────────────────────────────────────────────────
        if simplex_export_values_var.get() == 1:
            values_csv = DB_PCACE_data_analyzer_util.get_data_simplex_values_listing(
                inputDir, outputDir, setup_simplex)
            if values_csv and os.path.isfile(values_csv):
                filesToOpen.append(values_csv)

        # ── Spell-check (text simplexes only) ─────────────────────────────────
        if simplex_spell_check_var.get() == 1:
            if vtype == 1:  # text
                try:
                    dupes_csv = DB_PCACE_data_analyzer_util.find_near_duplicate_simplex_values(
                        inputDir, outputDir, simplex_name=setup_simplex)
                    if dupes_csv and os.path.isfile(dupes_csv):
                        filesToOpen.append(dupes_csv)
                except Exception as e:
                    print(f"  Near-duplicate check skipped: {e}")
            else:
                mb.showwarning(title='Spell-check',
                               message=f'Spell-check is only available for text-typed simplexes.\n\n'
                                       f'The selected simplex "{setup_simplex}" is not text-typed.')

        # ── Charts (bar/pie of value frequencies) ─────────────────────────────
        if simplex_charts_var.get() == 1:
            # First ensure we have the values CSV to chart from
            values_csv = DB_PCACE_data_analyzer_util.get_data_simplex_values_listing(
                inputDir, outputDir, setup_simplex)
            if values_csv and os.path.isfile(values_csv):
                chart_outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                    values_csv, outputDir,
                    columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=[],
                    chart_title=f'Frequency of "{setup_simplex}" values',
                    count_var=1, hover_label=[],
                    outputFileNameType='',
                    column_xAxis_label=setup_simplex,
                    groupByList=[], plotList=[], chart_title_label='')
                if chart_outputFiles is not None:
                    if isinstance(chart_outputFiles, str):
                        filesToOpen.append(chart_outputFiles)
                    else:
                        filesToOpen.extend(chart_outputFiles)

        # ── Timechart (date simplexes only) ───────────────────────────────────
        if simplex_timechart_var.get() == 1:
            if vtype == 3:  # date
                try:
                    timechart_csv, date_fmt = DB_PCACE_data_analyzer_util.prepare_timechart_csv(
                        inputDir, outputDir, setup_simplex)
                    if timechart_csv and os.path.isfile(timechart_csv):
                        timechart_output = IO_files_util.generate_output_file_name(
                            '', inputDir, outputDir, '.html', setup_simplex + '_timechart')
                        parent_names = DB_PCACE_data_analyzer_util.get_setup_simplex_parent(setup_simplex)
                        var_name = parent_names[0] if parent_names else 'Object'
                        charts_util.timechart(timechart_csv, timechart_output, var_name,
                                              date_fmt, cumulative=False, yearly=True)
                        if os.path.isfile(timechart_output):
                            filesToOpen.append(timechart_output)
                except Exception as e:
                    print(f"  Timechart generation skipped: {e}")
            else:
                mb.showwarning(title='Timechart',
                               message=f'Timechart is only available for date-typed simplexes.\n\n'
                                       f'The selected simplex "{setup_simplex}" is not date-typed.')

        # ── GIS maps (5th checkbox) ──────────────────────────────────────────
        if simplex_GIS_var.get() == 1:
            gis_csv = DB_PCACE_data_analyzer_util.prepare_gis_locations_csv(
                inputDir, outputDir, setup_simplex)
            if gis_csv and os.path.isfile(gis_csv):
                proceed = mb.askyesno(
                    title='GIS Mapping',
                    message=f'The simplex "{setup_simplex}" contains location values that can be '
                            f'geocoded and displayed on a map.\n\n'
                            f'Would you like to create a GIS map from these values?\n\n'
                            f'(Requires an internet connection for Nominatim geocoding.)')
                if proceed:
                    reminders_util.checkReminder(scriptName,
                                                 reminders_util.title_options_geocoder,
                                                 reminders_util.message_geocoder, True)
                    gis_output = GIS_pipeline_util.GIS_pipeline(
                        GUI_util.window,
                        config_filename,
                        gis_csv,            # inputFilename — the prepared locations CSV
                        inputDir,
                        outputDir,
                        'Nominatim',        # geocoder
                        'Google Earth Pro & Google Maps & Folium',  # mapping_package — all tools
                        chartPackage,
                        dataTransformation,
                        False,              # datePresent
                        '',                 # country_bias
                        '',                 # area_var
                        False,              # restrict
                        'Location',         # locationColumnName
                        'utf-8',            # encodingValue
                        0, 1, [''], [''],   # group_var, group_number_var, group_values, group_labels
                        ['Pushpins'], ['red'],              # icon_var_list, specific_icon_var_list
                        [0], ['1'], [0], [''],               # name, scale, color, color_style
                        [1], [1])                            # bold, italic

                    if gis_output is not None and not isinstance(gis_output, pd.DataFrame):
                        if len(gis_output) > 0:
                            filesToOpen.extend(gis_output)
                    # Refresh GIS hover-over to show updated timestamp
                    _update_last_updated_hovers(inputDir, outputDir)

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
                                identifiers_var.get(),
                                extended_headers_var.get(),
                                setup_simplex.get(),
                                # print_narrative_var.get(),
                                complex_parents_var.get(),
                                complex_children_var.get(),
                                document_sources_var.get(), comments_var.get(), comments_type_var.get(),
                                from_dataID_setupID_objectType_var.get(), enter_data_ID_var.get(),
                                search_simplex_var.get(), search_simplex_results_var.get(),
                                object_type_var.get(), required_object_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________


# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(3),
                                                 GUI_height_brief=560, # height at brief display
                                                 GUI_height_full=600, # height at full display
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
# Hidden combobox — referenced by changed_filename but not displayed in the current layout
select_DB_tables = ttk.Combobox(window, textvariable=select_DB_tables_var, width=GUI_IO_util.widget_width_short)
select_DB_tables.configure(state='disabled')
select_DB_table_fields_var=tk.StringVar()
view_relations_var=tk.IntVar()


complex_objects_var = tk.StringVar()
identifiers_var = tk.IntVar()
extended_headers_var = tk.IntVar()
parents_children_var = tk.IntVar()

simplex_objects_var = tk.StringVar()

value_parent_object_var = tk.IntVar()

complex_parent_var = tk.IntVar()
complex_child_var = tk.IntVar()
simplex_complex_var = tk.IntVar()

complex_parents_var = tk.StringVar()
complex_children_var = tk.StringVar()

enter_data_ID_var = tk.StringVar()
setup_name_var = tk.StringVar()

def clear(e):
    value_parent_object_var.set(0)
    setup_complex=''
    setup_simplex=''
    select_DB_tables_var.set('')
    object_type_var.set('')
    required_object_var.set('')
    simplex_value_type_var.set('')
    simplex_list=[]
    simplex_value_var.set(simplex_list)
    simplex_value_var.set('')
    simplex_value['values'] = []

    complex_identifiers_var.set('')

    search_simplex_var.set('')
    search_simplex_results_var.set('')

    setup_complex_var.set('')
    setup_simplex_var.set('')
    identifiers_var.set(0)
    extended_headers_var.set(0)
    value_parent_object_var.set(0)
    parents_children_var.set(0)
    complex_parents_var.set('')
    complex_children_var.set('')

    simplex_export_values_var.set(0)
    simplex_spell_check_var.set(0)
    simplex_charts_var.set(0)
    simplex_timechart_var.set(0)
    simplex_GIS_var.set(0)

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
        # Launch DB_SQL_main.py with the database path pre-selected
        import subprocess
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DB_SQL_main.py')
        # Use "SQL queries" subdirectory for import/save query dialogs
        query_dir = os.path.join(inputDir.get(), 'SQL queries')
        if not os.path.exists(query_dir):
            os.makedirs(query_dir)
        subprocess.Popen([sys.executable, script_path, '--db', db_path, '--querydir', query_dir, '--inputdir', inputDir.get(), '--outputdir', outputDir.get()])

open_sql_button = tk.Button(window, text='Open SQL query GUI', width=17,height=1,state='normal', command=lambda: open_sql_query())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_sql_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to export all PC-ACE tables to an SQLite database and open the SQL query GUI.\nYou can then run any SQL query against the PC-ACE data.")

view_relations_button = tk.Button(window, text='View table relations', width=17,height=1,state='disabled', command=lambda: view_relations())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   view_relations_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to open a pdf file of the PC-ACE table relations. These relations are ALWAYS the same across any type of application of PC-ACE (e.g., Avanti! or Lynchings).\nTo view the grammar of data collection for a specific PC-ACE implementation click on the button View grrammar.")

view_grammar_button = tk.Button(window, text='View grammar', width=17,height=1,state='disabled', command=lambda: view_grammar())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+150, y_multiplier_integer,
                                   view_grammar_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to export as a text file the grammmar used for the selected, specific implementation of the PC-ACE database.\nThe grammar will be exported in the same directory of the Input Excel files.\nClick on the button View table relations to visualize the general table relations in the PC-ACE databasee, regardless of a selected, specific implementation (i./e., grammar setup).")

update_grammar_button = tk.Button(window, text='Update grammar', width=17,height=1,state='disabled', command=lambda: update_grammar())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+300, y_multiplier_integer,
                                   update_grammar_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to update the grammmar used for the selected, specific implementation of the PC-ACE database saved in setup_complex.xlsx and setup_complex.pkl.\nThe grammar will be saved in setup_complex.xlsx and setup_complex.pkl.\nClick on the button View table relations to visualize the general table relations in the PC-ACE databasee, regardless of a selected, specific implementation (i./e., grammar setup).")


update_identifier_button = tk.Button(window, text='Update identifiers', width=17,height=1,state='disabled', command=lambda: update_identifiers())
# place widget with hover-over info
_update_id_btn_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+20, y_multiplier_integer,
                                   update_identifier_button,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Click to update the current complex objects identifiers saved in the table data_Complex.xlsx and data_Complex.pkl")

object_type_lb = tk.Label(window, text='Object ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,object_type_lb,True)

object_type_var= tk.StringVar()
object_type_var_menu = tk.OptionMenu(window,object_type_var, 'Complex','Simplex')
object_type_var_menu.configure(state='disabled')
object_type_var.set('')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+50, y_multiplier_integer,
                                   object_type_var_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Use the dropdown menu to select the type of object (complex or simplex) for which to obtain a list of values.\nThe object list will then be displayed in the right-hand menu widget.")

setup_complex_menu, setup_simplex_menu = DB_PCACE_data_analyzer_util.get_setup_complex_simplex_names() # os.path.join(inputDir.get())

required_object_var=tk.StringVar()
required_object = ttk.Combobox(window, textvariable = required_object_var, width=GUI_IO_util.widget_width_short)
required_object.configure(state='disabled')
required_object['values'] = setup_complex_menu
# place widget with hover-over info
_required_object_y_row = y_multiplier_integer  # save for dynamic hover-over
_required_object_base_text = ("You can use the dropdown menu to scroll through the list of available objects.\n"
    "You can also select a complex or simplex object, then press Enter or click RUN to toggle its REQUIRED boolean value (from False to True or viceversa).\n"
    "The value is set in the setup_xref_Complex-Complex table or setup_xref_Simplex-Complex table. The xlsx, pkl, and grammar files will be updated.")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   required_object,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   _required_object_base_text)

def _update_required_object_dropdown(*args):
    """Switch required_object dropdown values between Complex and Simplex names.
    Re-fetches from the util each time to ensure values are current after DB load."""
    obj_type = object_type_var.get()
    try:
        c_menu, s_menu = DB_PCACE_data_analyzer_util.get_setup_complex_simplex_names()
    except:
        c_menu, s_menu = [], []
    if obj_type == 'Complex':
        required_object['values'] = c_menu
        n = len(c_menu)
        if c_menu:
            required_object_var.set(c_menu[0])
        else:
            required_object_var.set('')
    elif obj_type == 'Simplex':
        required_object['values'] = s_menu
        n = len(s_menu)
        if s_menu:
            required_object_var.set(s_menu[0])
        else:
            required_object_var.set('')
    else:
        required_object['values'] = []
        n = 0
        required_object_var.set('')
    _update_combo_hover(required_object, _required_object_y_row,
        GUI_IO_util.open_setup_x_coordinate+150, GUI_IO_util.open_TIPS_x_coordinate,
        n, _required_object_base_text)

object_type_var.trace('w', _update_required_object_dropdown)

def _toggle_required():
    """Toggle the REQUIRED boolean for the selected object, with confirmation."""
    obj_type = object_type_var.get()
    obj_name = required_object_var.get()
    if not obj_type or not obj_name:
        mb.showwarning(title='Warning',
                       message='Please select an object type (Complex or Simplex) and an object name from the dropdown menus.')
        return
    current_val, xref_info = DB_PCACE_data_analyzer_util.get_required_value(obj_type, obj_name)
    if current_val is None:
        mb.showwarning(title='Warning',
                       message=f'Could not find "{obj_name}" in the {obj_type} xref table.\n\nMake sure the object exists in the setup_xref tables.')
        return
    new_val = not current_val
    new_str = "TRUE (Required)" if new_val else "FALSE (Not required)"
    old_str = "TRUE (Required)" if current_val else "FALSE (Not required)"
    proceed = mb.askyesno("Change REQUIRED value",
        f'You are about to change the REQUIRED value for:\n\n'
        f'  Object type: {obj_type}\n'
        f'  Object name: {obj_name}\n\n'
        f'  Current value: {old_str}\n'
        f'  New value: {new_str}\n\n'
        f'This will update the xlsx, pkl, and grammar files.\n\n'
        f'Are you sure you want to do that?')
    if proceed:
        success = DB_PCACE_data_analyzer_util.toggle_required_value(obj_type, obj_name, new_val, inputDir.get())
        if success:
            mb.showwarning(title='REQUIRED updated',
                           message=f'The REQUIRED value for "{obj_name}" has been changed to {new_str}.\n\n'
                                   f'The xlsx, pkl, and grammar files have been updated.')
        else:
            mb.showwarning(title='Error',
                           message=f'Failed to update the REQUIRED value for "{obj_name}".\nCheck the command line for details.')

# Enter on the required_object dropdown or RUN triggers the toggle with confirmation
required_object.bind('<Return>', lambda e: _toggle_required())

# select_DB_tables_lb = tk.Label(window, text='PC-ACE table ')
# # open_setup_x_coordinate
# # y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate,y_multiplier_integer,select_DB_tables_lb,True)
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,select_DB_tables_lb,True)
#
# table_menu_values = ''
# table_list=[]
# if os.path.isdir(inputDir.get()):
#     table_list = DB_PCACE_data_analyzer_util.import_PCACE_tables(inputDir.get(), outputDir.get())
#     table_menu_values = ", ".join(table_list)
# select_DB_tables = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=select_DB_tables_var)
# select_DB_tables.configure(state='disabled')
# select_DB_tables['values'] = table_menu_values
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+100, y_multiplier_integer,
#                                    select_DB_tables,
#                                    False, False, True, False, 90, GUI_IO_util.setup_IO_brief_coordinate,
#                                    "Use the dropdown menu to select a PC-ACE table to be opened for display; click RUN after selection.")
#


from_dataID_setupID_lb = tk.Label(window, text='From data ID to setup ID ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,from_dataID_setupID_lb,True)

from_dataID_setupID_objectType_var = tk.StringVar()
from_dataID_setupID_objectType_var.set('')
from_dataID_setupID_menu = tk.OptionMenu(window, from_dataID_setupID_objectType_var, 'Complex', 'Simplex')
from_dataID_setupID_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu-50, y_multiplier_integer,
                                   from_dataID_setupID_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Use the dropdown menu to select the type of object - complex or simplex - to go from data ID to setup name")

enter_data_ID_lb = tk.Label(window, text='Enter data ID')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate,y_multiplier_integer,enter_data_ID_lb,True)

enter_data_ID = tk.Entry(window,width=GUI_IO_util.widget_width_extra_short,textvariable=enter_data_ID_var)
enter_data_ID.configure(state="disabled")
# place widget with hover-over info

y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+100,
    y_multiplier_integer,
    enter_data_ID, True, False, True, False, 90,
    GUI_IO_util.open_reminders_x_coordinate+100, "Enter the numeric data ID value")

setup_name = tk.Entry(window,width=GUI_IO_util.widget_width_short,textvariable=setup_name_var,state='disabled')
# setup_name.configure(state="disabled")
# place widget with hover-over info

y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,
    y_multiplier_integer,
    setup_name, False, False, True, False, 90,
    GUI_IO_util.open_setup_x_coordinate, "Extracted setup name")


complex_objects_lb = tk.Label(window, text='Complex ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,complex_objects_lb,True)

# setup_complex_menu, setup_simplex_menu = DB_PCACE_data_analyzer_util.get_setup_complex_simplex_names() # os.path.join(inputDir.get())

setup_complex_var=tk.StringVar()
setup_complex = ttk.Combobox(window, textvariable = setup_complex_var, width=GUI_IO_util.widget_width_short)
setup_complex.configure(state='disabled')
setup_complex['values'] = setup_complex_menu
# place widget with hover-over info
_setup_complex_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+90, y_multiplier_integer,
                                   setup_complex,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Select a complex object type from the dropdown.\n"
                                   "The Complex identifier dropdown (right) auto-populates with all instances.\n\n"
                                   "Checkboxes: Identifiers, Extended headers, Parents/children, Document sources, Comments.\n"
                                   "Tick a checkbox and click RUN to perform that operation.\n"
                                   "No checkbox: RUN exports the story form for the selected identifier.")

# FIRST checkbox ---------------------------------------------------
identifiers_checkbox = tk.Checkbutton(window, text='', variable=identifiers_var, onvalue=1, offvalue=0, state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate-10, y_multiplier_integer,
                                   identifiers_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "IDENTIFIER mode: export a compact summary with human-readable Identifier strings for the selected complex object and its children (e.g., '(mob lynched Negro)').\nOutput file suffix: _IDENTIFIER.\nUse this for a quick overview of all instances.")

# SECOND checkbox ---------------------------------------------------
extended_headers_checkbox = tk.Checkbutton(window, text='', variable=extended_headers_var, onvalue=1, offvalue=0, state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+10, y_multiplier_integer,
                                   extended_headers_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "EXTENDED HEADERS mode: export a fully expanded table with every simplex value in its own column (e.g., 'Participant-S > Individual > Name of individual').\nOutput file suffix: _ALL.\nUse this for detailed analysis, charting, and frequency computation.")

# THIRD checkbox ---------------------------------------------------
parents_children_checkbox = tk.Checkbutton(window, text='', variable=parents_children_var, onvalue=1, offvalue=0, state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+30, y_multiplier_integer,
                                   parents_children_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "PARENTS & CHILDREN mode: extract the parents and children of the selected complex object")

# FOURTH checkbox ---------------------------------------------------
document_sources_var = tk.IntVar()
document_sources_checkbox = tk.Checkbutton(window, text='', variable=document_sources_var, onvalue=1, offvalue=0, state='disabled')

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+50, y_multiplier_integer,
                                   document_sources_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "DOCUMENT mode: extract the document sources (newspaper name, newspaper date, page number, column number) for specific objects (e.g., Semantic triplets (SVO), Simple processes).")

# FIFTH checkbox ---------------------------------------------------
comments_var = tk.IntVar()
comments_var.set(0)
comments_checkbox = tk.Checkbutton(window, text='', variable=comments_var, onvalue=1, offvalue=0, state='disabled')

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+70, y_multiplier_integer,
                                   comments_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "COMMENT mode: extract the comments left by users and/or verifiers for specific objects (e.g., Semantic triplets (SVO)).")

comments_type_var = tk.StringVar()
comments_type_var.set('')
comments_menu = tk.OptionMenu(window, comments_type_var, '*', 'Users comments', 'Verifiers comments')
comments_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+95, y_multiplier_integer,
                                   comments_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Use the dropdown menu to extract the comments left by users and/or verifiers for specific objects (e.g., Semantic triplets (SVO)).")

complex_identifiers_lb = tk.Label(window, text='Complex identifier')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,complex_identifiers_lb,True)

complex_identifiers_menu = DB_PCACE_data_analyzer_util.build_macro_event_dropdown_menu(inputDir.get())

complex_identifiers_var=tk.StringVar()
complex_identifiers = ttk.Combobox(window, textvariable = complex_identifiers_var, width=GUI_IO_util.widget_width_short)
complex_identifiers.configure(state='disabled')
complex_identifiers['values'] = complex_identifiers_menu
_complex_id_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   complex_identifiers,
                                   False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Using the dropdown menu select the Simplex data type (date, number, text) to be used to visualize simplex values.\n"
                                   ""
                                   "RUN: export the story form, or perform a checkbox operation if a checkbox is ticked.")
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
#                                    complex_identifiers,
#                                    False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
#                                    "Auto-populated when a Complex type is selected. Lists all instances of the selected complex type (ID - Identifier).\n"
#                                    "Enter: export the story form for the selected object.\n"
#                                    "RUN: export the story form, or perform a checkbox operation if a checkbox is ticked.")

def _complex_identifier_enter(event):
    """Enter on Complex identifier → export story form for selected object."""
    selected = complex_identifiers_var.get()
    if not selected:
        return
    outputDir_val = GUI_util.output_dir_path.get()
    story_text, filepath = DB_PCACE_data_analyzer_util.story_form_from_dropdown(selected, outputDir_val)
    html_filepath = DB_PCACE_data_analyzer_util.story_form_html_from_dropdown(selected, outputDir_val)
    if html_filepath:
        IO_files_util.openFile(window, html_filepath)
    elif filepath:
        IO_files_util.openFile(window, filepath)

complex_identifiers.bind('<Return>', _complex_identifier_enter)


def _update_combo_hover(combo, y_row, x_coord, x_hover, count, base_text):
    """Re-bind hover-over text on a combobox to include item count."""
    count_line = f'{count} item(s) listed.' if count > 0 else 'No items listed.'
    tip = count_line + '\n' + base_text
    combo.bind('<Enter>',
        lambda e, t=tip: (
            e.widget.config(ttk.Style().map('Red.TCombobox',
                foreground=[('readonly', 'red')],
                selectforeground=[('readonly', 'red')])),
            GUI_IO_util.display_widget_info(window, e, x_coord,
                GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step * y_row,
                x_hover, t)))
    combo.bind('<Leave>',
        lambda e: (e.widget.config(background=combo.cget('background'), foreground=combo.cget('foreground')),
                   GUI_IO_util.delete_display_widget_lb(window, e, '')))

def update_complex_identifier_dropdown(*args):
    """When user selects a hierarchical complex type, update the Complex identifier dropdown
    with all instances of that type (ID - Identifier).
    Does NOT auto-select the first item so that RUN can distinguish
    'export all' (nothing selected) vs 'export selected one'."""
    selected_type = setup_complex_var.get()
    if selected_type:
        identifier_list = DB_PCACE_data_analyzer_util.build_story_dropdown(selected_type)
        complex_identifiers['values'] = identifier_list
        if identifier_list:
            complex_identifiers_var.set(identifier_list[0])
        else:
            complex_identifiers_var.set('')
    else:
        # Reset to macro event list
        macro_list = DB_PCACE_data_analyzer_util.build_macro_event_dropdown_menu(inputDir.get())
        complex_identifiers['values'] = macro_list
        if macro_list:
            complex_identifiers_var.set(macro_list[0])
        else:
            complex_identifiers_var.set('')
    # Update hover-over with item count
    n = len(complex_identifiers['values']) if complex_identifiers['values'] else 0
    _update_combo_hover(complex_identifiers, _complex_id_y_row,
        GUI_IO_util.open_setup_x_coordinate+150, GUI_IO_util.open_reminders_x_coordinate, n,
        "Auto-populated when a Complex type is selected. Lists all instances of the selected complex type (ID - Identifier).\n"
        "Enter: export the story form for the selected object.\n"
        "RUN: export the story form, or perform a checkbox operation if a checkbox is ticked.")

setup_complex_var.trace('w', update_complex_identifier_dropdown)

simplex_objects_lb = tk.Label(window, text='Simplex ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,simplex_objects_lb, True)

# setup_simplex_menu = DB_PCACE_data_analyzer_util.get_complex_simplex_names(os.path.join(inputDir.get()))
#
setup_simplex_var = tk.StringVar()

setup_simplex = ttk.Combobox(window, textvariable = setup_simplex_var, width=GUI_IO_util.widget_width_short)
setup_simplex.configure(state='disabled')
setup_simplex['values'] = setup_simplex_menu
# place widget with hover-over info
_setup_simplex_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+90, y_multiplier_integer,
                                   setup_simplex,
                                   True, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Select a simplex object type from the dropdown.\n"
                                   "The Simplex values dropdown (right) auto-populates with all data values.\n\n"
                                   "Checkboxes: Values, Spell-check, Charts, Timechart, GIS map.\n"
                                   "Tick a checkbox and click RUN to perform that operation.")

# Simplex operation checkboxes (mirror the Complex checkbox pattern) ─────────────

# FIRST simplex checkbox: Export values to CSV
simplex_export_values_var = tk.IntVar()
simplex_export_values_checkbox = tk.Checkbutton(window, text='', variable=simplex_export_values_var, onvalue=1, offvalue=0, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate-10, y_multiplier_integer,
                                   simplex_export_values_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "VALUES mode: export all data values for the selected simplex to a CSV file with frequencies.")

# SECOND simplex checkbox: Spell-check (text simplexes)
simplex_spell_check_var = tk.IntVar()
simplex_spell_check_checkbox = tk.Checkbutton(window, text='', variable=simplex_spell_check_var, onvalue=1, offvalue=0, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate+10, y_multiplier_integer,
                                   simplex_spell_check_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "SPELL-CHECK mode: find near-duplicate and misspelled text values for the selected simplex.\nOnly available for text-typed simplexes (ValueType = 1).")

# THIRD simplex checkbox: Charts (bar/pie of frequencies)
simplex_charts_var = tk.IntVar()
simplex_charts_checkbox = tk.Checkbutton(window, text='', variable=simplex_charts_var, onvalue=1, offvalue=0, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate+30, y_multiplier_integer,
                                   simplex_charts_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "CHARTS mode: produce bar and pie charts of value frequencies for the selected simplex.")

# FOURTH simplex checkbox: Timechart (date simplexes)
simplex_timechart_var = tk.IntVar()
simplex_timechart_checkbox = tk.Checkbutton(window, text='', variable=simplex_timechart_var, onvalue=1, offvalue=0, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate+50, y_multiplier_integer,
                                   simplex_timechart_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "TIMECHART mode: generate a timeline chart for date-typed simplexes (ValueType = 3).")

# FIFTH simplex checkbox: GIS map (geocode + map location simplexes)
simplex_GIS_var = tk.IntVar()
simplex_GIS_checkbox = tk.Checkbutton(window, text='', variable=simplex_GIS_var, onvalue=1, offvalue=0, state='disabled')
_gis_checkbox_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate+70, y_multiplier_integer,
                                   simplex_GIS_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "GIS MAPS mode: geocode location values and display on Google Earth Pro, Google Maps, and Folium.\n"
                                   "Only meaningful for location simplexes (e.g., City name).\n"
                                   "First run is slow (~1 req/sec for Nominatim); subsequent runs use disk cache.")

simplex_values_var = tk.StringVar()
simplex_values_lb = tk.Label(window, text='Simplex values')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                   simplex_values_lb, True)

simplex_values = ttk.Combobox(window, textvariable = simplex_values_var, width=GUI_IO_util.widget_width_short)
simplex_values.configure(state='disabled')
simplex_values['values'] = []
_simplex_val_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   simplex_values,
                                   False, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Auto-populated when a Simplex type is selected.\n"
                                   "Lists all data values for the selected simplex.\n"
                                   "Enter: export the values listing to a CSV file.\n"
                                   "RUN: perform the operation(s) selected via checkboxes or GIS map.")

simplex_values_var.set('')

def _simplex_values_enter(event):
    """Enter on Simplex values → export values listing to CSV."""
    simplex_name = setup_simplex_var.get()
    if not simplex_name:
        return
    outputDir_val = GUI_util.output_dir_path.get()
    inputDir_val = GUI_util.input_main_dir_path.get()
    values_csv = DB_PCACE_data_analyzer_util.get_data_simplex_values_listing(
        inputDir_val, outputDir_val, simplex_name)
    if values_csv and os.path.isfile(values_csv):
        IO_files_util.openFile(window, values_csv)

simplex_values.bind('<Return>', _simplex_values_enter)

def _populate_simplex_values(*args):
    """Populate the Simplex values dropdown when a simplex is selected."""
    simplex_name = setup_simplex_var.get()
    if not simplex_name:
        simplex_values['values'] = []
        simplex_values_var.set('')
        return
    try:
        vals = DB_PCACE_data_analyzer_util.get_simplex_values_by_name(simplex_name)
        simplex_values['values'] = vals
        if vals:
            simplex_values_var.set(vals[0])
        else:
            simplex_values_var.set('')
    except Exception as e:
        print(f"  Could not populate simplex values: {e}")
        simplex_values['values'] = []
        simplex_values_var.set('')
    # Update hover-over with item count
    n = len(simplex_values['values']) if simplex_values['values'] else 0
    _update_combo_hover(simplex_values, _simplex_val_y_row,
        GUI_IO_util.open_setup_x_coordinate+150, GUI_IO_util.open_setup_x_coordinate, n,
        "Auto-populated when a Simplex type is selected.\n"
        "Lists all data values for the selected simplex.\n"
        "Enter: export the values listing to a CSV file.\n"
        "RUN: perform the operation(s) selected via checkboxes or GIS map.")

setup_simplex_var.trace('w', _populate_simplex_values)

simplex_value_type_lb = tk.Label(window, text='Simplex data type ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,simplex_value_type_lb,True)

simplex_value_type_var= tk.StringVar()
simplex_value_type_menu = tk.OptionMenu(window, simplex_value_type_var, 'text','date', 'number')
simplex_value_type_menu.configure(state='disabled')
simplex_value_type_var.set('')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu-50, y_multiplier_integer,
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
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                   simplex_value,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate+300,
                                   "Use the dropdown menu to select the simplex data type value (e.g., police) for which you want to find simplex & complex objects usage.")

value_parent_object_checkbox = tk.Checkbutton(window, text='Get simplex/complex objects of selected data type (& value)', variable=value_parent_object_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   value_parent_object_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Tick the checkbox to export simplex and complex objects that use the selected data type and, perhaps, value")

def activate_date_number_text(*args):
    if simplex_value_type_var.get()!='':
        simplex_value.configure(state='normal')
    else:
        simplex_value.configure(state='disabled')
    simplex_list = DB_PCACE_data_analyzer_util.get_data_simplex_text_date_number(simplex_value_type_var.get())
    simplex_value['values'] = simplex_list
    if simplex_list:
        simplex_value_var.set(simplex_list[0])
    else:
        simplex_value_var.set('')
simplex_value_type_var.trace('w',activate_date_number_text)

# Search simplex value → story form row ___________________________________________

search_simplex_lb = tk.Label(window, text='Search simplex value')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,search_simplex_lb,True)

search_simplex_var = tk.StringVar()
search_simplex_entry = tk.Entry(window, textvariable=search_simplex_var, width=20, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu-50, y_multiplier_integer,
                                   search_simplex_entry,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Type a simplex value to search for (e.g., a city name, a person name) and press Enter.\n"
                                   "The search is case-insensitive.\n"
                                   "The Search results dropdown (right) auto-populates with all matching hierarchical objects (++).\n\n"
                                   "Enter (in this field): search and populate results.\n"
                                   "Enter (in results dropdown): export the story form for the selected object.")

search_simplex_results_lb = tk.Label(window, text='Search results')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,search_simplex_results_lb,True)

search_simplex_results_var = tk.StringVar()
search_simplex_results = ttk.Combobox(window, textvariable=search_simplex_results_var, width=GUI_IO_util.widget_width_short)
search_simplex_results.configure(state='disabled')
search_simplex_results['values'] = []
_search_results_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   search_simplex_results,
                                   False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Auto-populated when you type a search term and press Enter in the Search simplex value field.\n"
                                   "Lists all hierarchical objects (++) containing the searched value.\n"
                                   "Enter: export the story form for the selected object.\n"
                                   "RUN: export the story form for the selected object, or ALL if none selected.")

def _search_results_enter(event):
    """Enter on Search results → export story form for selected result."""
    selected = search_simplex_results_var.get()
    if not selected:
        return
    outputDir_val = GUI_util.output_dir_path.get()
    story_text, filepath = DB_PCACE_data_analyzer_util.story_form_from_dropdown(selected, outputDir_val)
    html_filepath = DB_PCACE_data_analyzer_util.story_form_html_from_dropdown(selected, outputDir_val)
    if html_filepath:
        IO_files_util.openFile(window, html_filepath)
    elif filepath:
        IO_files_util.openFile(window, filepath)

search_simplex_results.bind('<Return>', _search_results_enter)

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
                       message=f'Found {len(results)} hierarchical object(s) containing "{search_term}".\n\nThe first result is displayed. Use the dropdown to select a different one.\nClick RUN to export the selected story form,\nor clear the selection and click RUN to export ALL.')
    else:
        search_simplex_results_var.set('')
        mb.showwarning(title='Search results',
                       message=f'No hierarchical objects found containing "{search_term}".')
    # Update hover-over with item count
    n = len(results) if results else 0
    _update_combo_hover(search_simplex_results, _search_results_y_row,
        GUI_IO_util.open_setup_x_coordinate+150, GUI_IO_util.open_reminders_x_coordinate, n,
        "Auto-populated when you type a search term and press Enter in the Search simplex value field.\n"
        "Lists all hierarchical objects (++) containing the searched value.\n"
        "Enter: export the story form for the selected object.\n"
        "RUN: export the story form for the selected object, or ALL if none selected.")

search_simplex_entry.bind('<Return>', run_simplex_search)

select_parents_lb = tk.Label(window, text='Parents ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,select_parents_lb,True)

select_parents = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=complex_parents_var, state='disabled')
# select_parents.configure(state='disabled')
# place widget with hover-over info
_select_parents_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+90, y_multiplier_integer,
                                   select_parents,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "The menu displays a list of complex objects parent of the 'Complex' or 'Simplex' selected in the widgets above.")

select_children_lb = tk.Label(window, text='Complex children ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,select_children_lb,True)

select_children = ttk.Combobox(window, width=GUI_IO_util.widget_width_short, textvariable=complex_children_var, state='disabled')
# select_children.configure(state='disabled')
# place widget with hover-over info
_select_children_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   select_children,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "The menu displays a list of complex objects children of the 'Complex objects' selected in the widget above.\nThe option is only available for the 'Complex objects' widget above (Simplex objects do not have children).")

def _get_file_date(filepath):
    """Return the last-modified date of a file as a formatted string, or None."""
    try:
        if os.path.isfile(filepath):
            mtime = os.path.getmtime(filepath)
            return datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
    except Exception:
        pass
    return None

def _update_last_updated_hovers(in_dir, out_dir):
    """Update hover-over text on GIS checkbox and Update identifiers button
    to show when their outputs were last updated."""
    # ── GIS geocode cache ──────────────────────────────────────────────────
    # The cache file lives in the PCACE output subfolder.
    # run() always strips the last 5 characters from the input folder name
    # (e.g. PCACE_Popolo_xlxs → PCACE_Popolo) regardless of actual suffix.
    head, tail = os.path.split(in_dir)
    pcace_subdir = tail[:-5]
    cache_path = os.path.join(out_dir, pcace_subdir, 'GIS_geocode_cache.json')
    cache_date = _get_file_date(cache_path)
    # Also check directly in the output directory
    if cache_date is None:
        cache_path_alt = os.path.join(out_dir, 'GIS_geocode_cache.json')
        cache_date = _get_file_date(cache_path_alt)
    # Determine which cache path was found (for display)
    if cache_date and os.path.isfile(cache_path):
        found_cache_path = cache_path
    elif cache_date:
        found_cache_path = cache_path_alt
    else:
        found_cache_path = cache_path  # expected path (even if not yet created)
    gis_base = ("GIS MAP: geocode location values and display on Google Earth Pro, Google Maps, and Folium.\n"
                "Only meaningful for location simplexes (e.g., City name).\n"
                "First run is slow (~1 req/sec for Nominatim); subsequent runs use disk cache.")
    if cache_date:
        gis_tip = gis_base + f'\n\nGeocoding last updated on {cache_date}.\nCache: {found_cache_path}'
    else:
        gis_tip = gis_base + f'\n\nGeocoding has not been run yet for this database.\nCache will be saved to: {found_cache_path}'
    simplex_GIS_checkbox.bind('<Enter>',
        lambda e, t=gis_tip: (
            e.widget.config(background='light sea green', foreground='black'),
            GUI_IO_util.display_widget_info(window, e,
                GUI_IO_util.open_reminders_x_coordinate+70,
                GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step * _gis_checkbox_y_row,
                GUI_IO_util.open_TIPS_x_coordinate, t)))

    # ── Update identifiers (data_Complex.xlsx) ─────────────────────────────
    id_xlsx_path = os.path.join(in_dir, 'data_Complex.xlsx')
    id_date = _get_file_date(id_xlsx_path)
    id_base = "Click to update the current complex objects identifiers saved in the table data_Complex.xlsx and data_Complex.pkl"
    if id_date:
        id_tip = id_base + f'\n\nIdentifiers last updated on {id_date}.'
    else:
        id_tip = id_base + '\n\ndata_Complex.xlsx not found.'
    update_identifier_button.bind('<Enter>',
        lambda e, t=id_tip: (
            e.widget.config(background='red', foreground='black'),
            GUI_IO_util.display_widget_info(window, e,
                GUI_IO_util.open_reminders_x_coordinate+20,
                GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step * _update_id_btn_y_row,
                GUI_IO_util.open_TIPS_x_coordinate, t)))

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
        # Show the selected database name immediately in the window title
        db_folder_name = os.path.basename(inputDirSV)
        window.title(GUI_label + '  —  Loading ' + db_folder_name + '...')
        window.update_idletasks()
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
        # Populate the Simplex dropdown immediately (before identifier building which can fail)
        setup_simplex['values'] = setup_simplex_menu
        if len(setup_simplex_menu) > 0:
            setup_simplex.configure(state='normal')
            setup_simplex_var.set('')
        else:
            setup_simplex.set('')

        # Update hover-over with item counts
        _update_combo_hover(setup_complex, _setup_complex_y_row,
            GUI_IO_util.labels_x_coordinate+90, GUI_IO_util.labels_x_coordinate,
            len(setup_complex_menu),
            "Select a complex object type from the dropdown.\n"
            "The Complex identifier dropdown (right) auto-populates with all instances.\n\n"
            "Checkboxes: Identifiers, Extended headers, Parents/children, Document sources, Comments.\n"
            "Tick a checkbox and click RUN to perform that operation.\n"
            "No checkbox: RUN exports the story form for the selected identifier.")
        _update_combo_hover(setup_simplex, _setup_simplex_y_row,
            GUI_IO_util.labels_x_coordinate+90, GUI_IO_util.open_setup_x_coordinate,
            len(setup_simplex_menu),
            "Select a simplex object type from the dropdown.\n"
            "The Simplex values dropdown (right) auto-populates with all data values.\n\n"
            "Checkboxes: Values, Spell-check, Charts, Timechart, GIS map.\n"
            "Tick a checkbox and click RUN to perform that operation.")

        # Refresh the REQUIRED object dropdown based on current Object type selection.
        # Do NOT pre-populate until the user picks Complex or Simplex.
        obj_type = object_type_var.get()
        if obj_type == 'Complex':
            required_object['values'] = setup_complex_menu
            _req_n = len(setup_complex_menu)
        elif obj_type == 'Simplex':
            required_object['values'] = setup_simplex_menu
            _req_n = len(setup_simplex_menu)
        else:
            required_object['values'] = []
            required_object_var.set('')
            _req_n = 0
        _update_combo_hover(required_object, _required_object_y_row,
            GUI_IO_util.open_setup_x_coordinate+150, GUI_IO_util.open_TIPS_x_coordinate,
            _req_n, _required_object_base_text)
        if len(setup_complex_menu)>0:
            simplex_value_type_menu.configure(state='normal')
            select_DB_tables.configure(state='normal')
            setup_complex.configure(state='normal')
            # Enable all widgets that depend on a loaded database
            view_relations_button.configure(state='normal')
            view_grammar_button.configure(state='normal')
            update_grammar_button.configure(state='normal')
            update_identifier_button.configure(state='normal')
            object_type_var_menu.configure(state='normal')
            required_object.configure(state='readonly')
            from_dataID_setupID_menu.configure(state='normal')
            enter_data_ID.configure(state='normal')
            complex_identifiers.configure(state='normal')
            comments_menu.configure(state='normal')
            identifiers_checkbox.configure(state='normal')
            extended_headers_checkbox.configure(state='normal')
            parents_children_checkbox.configure(state='normal')
            document_sources_checkbox.configure(state='normal')
            comments_checkbox.configure(state='normal')
            simplex_export_values_checkbox.configure(state='normal')
            simplex_spell_check_checkbox.configure(state='normal')
            simplex_charts_checkbox.configure(state='normal')
            simplex_timechart_checkbox.configure(state='normal')
            simplex_GIS_checkbox.configure(state='normal')
            simplex_values.configure(state='normal')
            search_simplex_entry.configure(state='normal')
            search_simplex_results.configure(state='normal')
            setup_name.configure(state='normal')
            select_parents.configure(state='readonly')
            select_children.configure(state='readonly')
            # setup_complex.set(setup_complex_menu[0])
            setup_complex.set('')
            if not database_already_loaded:
                try:
                    complex_identifiers_menu = DB_PCACE_data_analyzer_util.build_macro_event_dropdown_menu(inputDir.get())
                    complex_identifiers['values'] = complex_identifiers_menu
                    if complex_identifiers_menu:
                        complex_identifiers_var.set(complex_identifiers_menu[0])
                    # Populate hierarchical complex dropdown
                    hierarchical_complex_menu = DB_PCACE_data_analyzer_util.build_hierarchical_complex_dropdown_menu(inputDir.get())
                    complex_identifiers['values'] = complex_identifiers_menu
                except Exception as e:
                    print(f"  WARNING: Could not build identifier/hierarchical menus: {e}")
                database_already_loaded = True
        else:
            simplex_value_type_menu.configure(state='disabled')
            setup_complex.set('')
            setup_complex.configure(state='disabled')
            # Keep all dependent widgets disabled
            complex_identifiers.configure(state='disabled')
            comments_menu.configure(state='disabled')
            identifiers_checkbox.configure(state='disabled')
            extended_headers_checkbox.configure(state='disabled')
            parents_children_checkbox.configure(state='disabled')
            document_sources_checkbox.configure(state='disabled')
            comments_checkbox.configure(state='disabled')
            setup_simplex.configure(state='disabled')
            simplex_export_values_checkbox.configure(state='disabled')
            simplex_spell_check_checkbox.configure(state='disabled')
            simplex_charts_checkbox.configure(state='disabled')
            simplex_timechart_checkbox.configure(state='disabled')
            simplex_GIS_checkbox.configure(state='disabled')
            simplex_values.configure(state='disabled')
            search_simplex_entry.configure(state='disabled')
            search_simplex_results.configure(state='disabled')

        # Update hover-over text with last-updated dates for GIS and identifiers
        _update_last_updated_hovers(inputDir.get(), outputDir.get())

        # Update window title to show loaded database name
        window.title(GUI_label + '  —  ' + db_folder_name)
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
    # Guard: skip if libraries not loaded yet
    try:
        if DB_PCACE_data_analyzer_util.setup_Complex_lib is None:
            return
    except (AttributeError, NameError):
        return
    if setup_complex_var.get()!='':
        parents_complex_list = DB_PCACE_data_analyzer_util.get_setup_complex_parents(setup_complex_var.get())
        children_complex_list_all, children_complex_list_required = DB_PCACE_data_analyzer_util.get_setup_complex_children(setup_complex_var.get())
        if len(parents_complex_list)>0:
            complex_parents_var.set(str(parents_complex_list[0]))
            # if len(parents_complex_list) > 1:
                # timing = 2000
                # IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Warning',
                #                                    "The selected complex '" + str(setup_complex_var.get()) + "' has " + str(len(parents_complex_list)) + " complex parents. Only the first one is displayed. Use the dropdown menu to scroll through all available complex parent names.",
                #                                    False, '', True, '', False)
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
            # if len(children_complex_list_all) > 1:
                # timing = 2000
                # IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Warning',
                #                                    "The selected complex '" + str(setup_complex_var.get()) + "' has " + str(
                #                                     len(children_complex_list_all)) + " complex children. Only the first one is displayed. Use the dropdown menu to scroll through all available complex children names.",
                #                                    False, '', True, '', False)

                # mb.showwarning(title='Warning',
                #                message="The selected complex " + str(setup_complex_var.get()) + " has " + str(
                #                    len(children_list)) + " complex children. Only the first one is displayed. Use the dropdown menu to scroll through all available complex children names.")
        else:
            mb.showwarning(title='Warning',
                           message="The selected complex '" + str(setup_complex_var.get()) + "' has no complex children.")
        select_children['values'] = children_complex_list_all

        # Update hover-over with item counts for parents, children, and simplex
        _update_combo_hover(select_parents, _select_parents_y_row,
            GUI_IO_util.labels_x_coordinate+90, GUI_IO_util.labels_x_coordinate,
            len(parents_complex_list),
            "The menu displays a list of complex objects parent of the 'Complex' or 'Simplex' selected in the widgets above.")
        _update_combo_hover(select_children, _select_children_y_row,
            GUI_IO_util.open_setup_x_coordinate+150, GUI_IO_util.open_TIPS_x_coordinate,
            len(children_complex_list_all),
            "The menu displays a list of complex objects children of the 'Complex objects' selected in the widget above.\n"
            "The option is only available for the 'Complex objects' widget above (Simplex objects do not have children).")
        _update_combo_hover(setup_simplex, _setup_simplex_y_row,
            GUI_IO_util.labels_x_coordinate+90, GUI_IO_util.open_setup_x_coordinate,
            len(setup_simplex_menu),
            "Select a simplex object type from the dropdown.\n"
            "The Simplex values dropdown (right) auto-populates with all data values.\n\n"
            "Checkboxes: Values, Spell-check, Charts, Timechart, GIS map.\n"
            "Tick a checkbox and click RUN to perform that operation.")

    if setup_simplex_var.get()!='':
        # setup_simplex_var.set(str(setup_simplex_menu[0]))
        parents_complex_list = DB_PCACE_data_analyzer_util.get_setup_simplex_parent(setup_simplex_var.get())
        if len(parents_complex_list) > 0:
            complex_parents_var.set(str(parents_complex_list[0]))
            # if len(parents_complex_list) > 1:
            #     mb.showwarning(title='Warning',
            #                    message="The selected simplex " + str(setup_simplex_var.get()) + " has " + str(
            #                        len(parents_complex_list)) + " complex parents. Only the first one is displayed. Use the dropdown menu to scroll through all available complex parent names.")
            select_parents['values'] = parents_complex_list
            # Update hover-over with item count for parents
            _update_combo_hover(select_parents, _select_parents_y_row,
                GUI_IO_util.labels_x_coordinate+90, GUI_IO_util.labels_x_coordinate,
                len(parents_complex_list),
                "The menu displays a list of complex objects parent of the 'Complex' or 'Simplex' selected in the widgets above.")

# Auto-populate parents/children when a complex or simplex is selected
setup_complex_var.trace('w', activate_parents_children)
setup_simplex_var.trace('w', activate_parents_children)

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
    # Refresh hover-over to show updated timestamp
    _update_last_updated_hovers(inputDir.get(), outputDir.get())

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
                            "\n\nYou can then tick the 'Get simplex/complex objects...' checkbox if you wish to visualize all simplex and complex objects that use the selected value (e.g.,'police') " + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "COMPLEX: select a complex object type from the dropdown.\n\n"
                                                         "Checkboxes (left to right):\n"
                                                         "  1. IDENTIFIERS: compact summary with human-readable Identifier strings.\n"
                                                         "  2. EXTENDED HEADERS: fully expanded table with every simplex in its own column.\n"
                                                         "  3. PARENTS/CHILDREN: display parents and children of the selected object.\n"
                                                         "  4. DOCUMENT SOURCES: extract the documents (e.g., newspapers) for the selected object.\n"
                                                         "  5. COMMENTS: extract comments left by users and/or verifiers.\n\n"
                                                         "When no checkbox is ticked, RUN exports the story form for the identifier shown in the right-hand dropdown."
                                                         + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "SIMPLEX: select a simplex object type from the dropdown.\n\n"
                                                         "Checkboxes (left to right):\n"
                                                         "  1. VALUES: export all data values with frequencies to CSV.\n"
                                                         "  2. SPELL-CHECK: find near-duplicate and misspelled values (text simplexes only).\n"
                                                         "  3. CHARTS: produce bar and pie charts of value frequencies.\n"
                                                         "  4. TIMECHART: generate a timeline chart (date simplexes only).\n"
                                                         "  5. GIS MAP: geocode location values and display on Google Earth Pro, Google Maps, and Folium.\n"
                                                         "     The first geocoding run is slow (~1 request/second for Nominatim).\n"
                                                         "     Subsequent runs are fast because results are saved to a disk cache (GIS_geocode_cache.json in the output directory).\n"
                                                         "     Hover over the GIS checkbox to see the cache location and when it was last updated.\n\n"
                                                         "The right-hand Simplex values widget auto-populates when a simplex is selected. Press Enter in that widget to export values to CSV."
                                                         + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "COMPLEX IDENTIFIER: auto-populated when a Complex type is selected above. Lists all instances of the selected complex type (ID - Identifier).\n"
                                                         "Enter: export the story form for the selected object.\n"
                                                         "RUN: export the story form, or perform a checkbox operation if a checkbox is ticked above."
                                                         + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "SEARCH SIMPLEX VALUE: type a simplex value (e.g., a city name, a person name) and press Enter to search.\n"
                                                         "The search is case-insensitive and finds all hierarchical objects (++) containing that value.\n"
                                                         "SEARCH RESULTS: auto-populated after a search. Lists the matching hierarchical objects.\n"
                                                         "Enter (in results dropdown): export the story form for the selected object.\n"
                                                         "RUN: export the selected story form, or ALL story forms if none selected."
                                                         + GUI_IO_util.msg_Esc)

    # y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
    #                                                      "NLP Suite Help",
    #                                                      "Please, tick the 'Get value frequencies for ALL objects' checkbox to compute the frequencies of all available complex and simplex objects."
    #                                                      "\n\nTick the 'Get value frequencies for SELECTED object' checkbox to compute the frequencies of the selected Complex or Simplex object." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the PARENT object and/or the CHILD object." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","COMMENT mode: Please, use the dropdown menu to select the type of comments to extract (users and/or verifiers) for specific objects (e.g., Semantic triplets (SVO)).\n\nTick the checkbox to extract the documents (e.g., newspaper articles) that are the sources of information for specific objects." + GUI_IO_util.msg_Esc)

    return y_multiplier_integer -1
"COUNT Display a template SQL COUNT query."
"DUPLICATES The query builds a temporary table of duplicate records, then, depending on user's choice, extracts only one occurrence of all duplicate records or all duplicate occurrences except one (all DISTINCT records will not be displayed). Query results can be used to move occurrences of objects for which multiples should not be allowed."
"UNMATCHED Automatically build a simple query that will give a list of all unmatched records between any two given tables/queries on the basis of a specific field (MEMO type fields cannot be matched!)\nThe query will give you a list of the fields in the first selected table/query that do not find a match in the second selected table/query."

y_multiplier_integer = y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,increment)

# change the value of the readMe_message
readMe_message="The Python 3 scripts convert, via the Python Pandas package, and analyze, via various visualization packages, data collected via the Microsoft ACCESS PC-ACE (Program for Computer-Assisted Coding of Events).\nIn INPUT the algorithms expect a set of xlsx files in the input directory. The xlsx files must be exported from the PC-ACE database tables data, setup, and utility (see TIPS file on how to export tables from PC-ACE).\n\nIn OUTPUT the algorithms produce a set of csv files and different types of visuals, from Excel charts to network graphs via Gephi and Sankey, geographic pin maps via Google Earth Pro and heat maps via Google Maps, word clouds, and interactive time maps."
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

# Auto-set input/output directories when launched from the SQL GUI.
# Use window.after() so these run after all widget initialization,
# ensuring they override any config-file defaults.
def _apply_cli_dirs():
    if '--inputdir' in sys.argv:
        try:
            idx = sys.argv.index('--inputdir')
            _dir = sys.argv[idx + 1]
            if os.path.isdir(_dir):
                GUI_util.input_main_dir_path.set(_dir)
        except (IndexError, ValueError):
            pass
    if '--outputdir' in sys.argv:
        try:
            idx = sys.argv.index('--outputdir')
            _dir = sys.argv[idx + 1]
            if os.path.isdir(_dir):
                GUI_util.output_dir_path.set(_dir)
        except (IndexError, ValueError):
            pass

GUI_util.window.after(200, _apply_cli_dirs)

GUI_util.window.mainloop()

