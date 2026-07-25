
import sys
import tkinter

import IO_libraries_util
import GUI_util

# if IO_libraries_util.install_all_Python_packages(GUI_util.window, "DB_PC-ACE_data_analyzer_main.py", ['os', 'tkinter','pandas'])==False:
#     sys.exit(0)

import os
import datetime
import pandas as pd
import subprocess

import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
import tkinter.filedialog as filedialog


import IO_csv_util
import IO_files_util
import GUI_IO_util
import TIPS_util
import DB_PCACE_data_analysis_util
import statistics_csv_util
import Stanza_util
import file_filename_util
import Gephi_util
import GIS_pipeline_util
import reminders_util
import charts_util
import IO_user_interface_util

# RUN section ______________________________________________________________________________________________________________________________________________________
def run():
    # dispatch RUN by the active tab: validation on the Data validation tab, analysis otherwise
    try:
        _active = notebook.tab(notebook.select(), 'text').strip()
    except Exception:
        _active = ''
    if _active == 'Data validation':
        run_validation()
        return
    _run_analysis()

def _run_analysis():
    # widget values read here at RUN time (was: run_script_command lambda + run() params)
    inputDir = GUI_util.input_main_dir_path.get()
    outputDir = GUI_util.output_dir_path.get()
    openOutputFiles = GUI_util.open_csv_output_checkbox.get()
    chartPackage = GUI_util.charts_package_options_widget.get()
    dataTransformation = GUI_util.data_transformation_options_widget.get()
    simplex_value_type = simplex_value_type_var.get()
    simplex_value = globals()['simplex_value'].get()
    primary_complex_var = complex_identifiers_var.get()
    value_parent_object_var = globals()['value_parent_object_var'].get()
    setup_complex = globals()['setup_complex'].get()
    identifiers = identifiers_var.get()
    extended_headers = extended_headers_var.get()
    setup_simplex = globals()['setup_simplex'].get()
    complex_parents_var = globals()['complex_parents_var'].get()
    complex_children_var = globals()['complex_children_var'].get()
    document_sources_var = globals()['document_sources_var'].get()
    comments_var = globals()['comments_var'].get()
    comments_type = comments_type_var.get()
    from_dataID_setupID_objectType_var = globals()['from_dataID_setupID_objectType_var'].get()
    enter_data_ID_var = globals()['enter_data_ID_var'].get()
    search_simplex_value = search_simplex_var.get()
    search_simplex_result = search_simplex_results_var.get()
    required_object_type = object_type_var.get()
    required_object_name = required_object_var.get()

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
            ID_setup_complex, complex_name = DB_PCACE_data_analysis_util.get_setup_complex_ID_Name_from_data_complex_ID(int(enter_data_ID_var))
            setup_name_var.set(complex_name)
        elif from_dataID_setupID_objectType_var == 'Simplex':
            ID_setup_simplex, simplex_name = DB_PCACE_data_analysis_util.get_setup_simplex_ID_Name_from_simplex_value_ID(int(enter_data_ID_var))
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
        story_text, filepath = DB_PCACE_data_analysis_util.story_form_from_dropdown(primary_complex_var, outputDir)
        if filepath:
            filesToOpen.append(filepath)
        html_filepath = DB_PCACE_data_analysis_util.story_form_html_from_dropdown(primary_complex_var, outputDir)
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
        dropdown_results = DB_PCACE_data_analysis_util.build_search_results_dropdown(search_simplex_value)
        search_simplex_results['values'] = dropdown_results
        # Do NOT auto-select first item — let user selection determine single vs. all export

        if search_simplex_result != '':
            # User selected a specific result → show its story form (txt + HTML)
            story_text, filepath = DB_PCACE_data_analysis_util.story_form_from_dropdown(search_simplex_result, outputDir)
            if filepath:
                filesToOpen.append(filepath)
            # Also export HTML version with highlighted simplex values
            html_filepath = DB_PCACE_data_analysis_util.story_form_html_from_dropdown(search_simplex_result, outputDir)
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
                filepath = DB_PCACE_data_analysis_util.search_and_export_stories(search_simplex_value, outputDir)
                if filepath:
                    filesToOpen.append(filepath)
                html_filepath = DB_PCACE_data_analysis_util.search_and_export_stories_html(search_simplex_value, outputDir)
                if html_filepath:
                    filesToOpen.append(html_filepath)
                    if openOutputFiles:
                        IO_files_util.openFile(window, html_filepath)
                elif filepath:
                    if openOutputFiles:
                        IO_files_util.openFile(window, filepath)
        return

    df = None  # initialize so auto-chart check doesn't fail on branches that don't produce a DataFrame

    if setup_complex != '':
        # Checkbox 2: display parents/children/simplex — fast setup-only lookup
        if parents_children_var.get() == 1:
            activate_parents_children()
        # Checkbox 3: extract document sources for the selected complex
        elif document_sources_var == 1:
            df = DB_PCACE_data_analysis_util.get_document_sources_for_complex(inputDir, outputDir, setup_complex)
            if openOutputFiles:
                output_file = os.path.join(outputDir, setup_complex + "_documents.xlsx")
                if os.path.exists(output_file):
                    IO_files_util.openFile(window, output_file)
        # Checkbox 4: export comments for the selected complex
        elif comments_var == 1:
            comment_type_str = comments_type if comments_type != '' else '*'
            comment_files = DB_PCACE_data_analysis_util.get_comment_info('', setup_complex, comment_type_str, inputDir, outputDir)
            if comment_files:
                filesToOpen.extend(comment_files)
        elif identifiers == 1:
            # Export identifiers only (Actor_IDENTIFIER)
            IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'IDENTIFIER mode',
                f'Starting IDENTIFIER export for "{setup_complex}".\n\n'
                f'This may take a while for large databases.\n'
                f'Please be patient...')
            df = DB_PCACE_data_analysis_util.higher_lower(inputDir, outputDir, setup_complex, export_identifier=True)
        elif extended_headers == 1:
            # Export expanded ALL headers (Actor_ALL)
            IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'EXTENDED HEADERS mode',
                f'Starting EXTENDED HEADERS export for "{setup_complex}".\n\n'
                f'This may take a very long time for large databases (several minutes).\n'
                f'Please be patient...')
            df = DB_PCACE_data_analysis_util.higher_lower(inputDir, outputDir, setup_complex, export_identifier=False)
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
                    filepath = DB_PCACE_data_analysis_util.export_all_stories_for_type(setup_complex, outputDir)
                    if filepath:
                        filesToOpen.append(filepath)
                    html_filepath = DB_PCACE_data_analysis_util.export_all_stories_html_for_type(setup_complex, outputDir)
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
                IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Tabular export',
                    f'Starting tabular export for "{setup_complex}".\n\n'
                    f'Please be patient...')
                df = DB_PCACE_data_analysis_util.higher_lower(inputDir, outputDir, setup_complex, export_identifier=False)
        # df = DB_PCACE_data_analysis_util.call_get_expanded_complex(inputDir, outputDir, setup_complex)

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
        # data = DB_PCACE_data_analysis_util.get_complex_data_ID(setup_complex)
        # mb.showwarning(title='Warning',
        #                message="YOU HAVE ADDED A RETURN!!!!!!!!!!!!!!!!!!!!!!!!!!\n\nMUST REMOVE IT.")
        # return

        # the next lines are used to test the three functions; nothing to do with the function identified by # -------
        # data_IDs = DB_PCACE_data_analysis_util.get_complex_data_ID(setup_complex)
        # lowerComplex_IDs = DB_PCACE_data_analysis_util.get_lower_complex(setup_complex)
        # lowestComplex_IDs = DB_PCACE_data_analysis_util.get_lowest_complex(setup_complex)

        # mb.showwarning(title='Warning',
        #                message="YOU HAVE ADDED A RETURN in _main!!!!!!!!!!!!!!!!!!!!!!!!!!\n\nMUST REMOVE IT.")
        # return

# --------------------------------------------------------------------------------------

    # display information about a specific simplex type and value (e.g., text type for "burley" value)

    if simplex_value!='' and value_parent_object_var:
        outputFiles = DB_PCACE_data_analysis_util.get_data_simplex_info(inputDir, outputDir, simplex_value)
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # ── Simplex operations (checkbox-driven) ──────────────────────────────────────
    if setup_simplex != '':
        # Determine simplex value type once for checkbox-specific logic
        try:
            vtype = DB_PCACE_data_analysis_util.get_simplex_value_type(setup_simplex)
        except Exception:
            vtype = 0

        # ── Values CSV ────────────────────────────────────────────────────────
        if simplex_export_values_var.get() == 1:
            values_csv = DB_PCACE_data_analysis_util.get_data_simplex_values_listing(
                inputDir, outputDir, setup_simplex)
            if values_csv and os.path.isfile(values_csv):
                filesToOpen.append(values_csv)

        # ── Charts (bar/pie of value frequencies) ─────────────────────────────
        if simplex_charts_var.get() == 1:
            # First ensure we have the values CSV to chart from
            values_csv = DB_PCACE_data_analysis_util.get_data_simplex_values_listing(
                inputDir, outputDir, setup_simplex)
            if values_csv and os.path.isfile(values_csv):
                chart_outputFiles = charts_util.plot(values_csv, outputDir, columns=[], title=f'Frequency of "{setup_simplex}" values', x_label=setup_simplex, group_by=None)
                if chart_outputFiles is not None:
                    if isinstance(chart_outputFiles, str):
                        filesToOpen.append(chart_outputFiles)
                    else:
                        filesToOpen.extend(chart_outputFiles)

        # ── Timechart (date simplexes only) ───────────────────────────────────
        if simplex_timechart_var.get() == 1:
            if vtype == 3:  # date
                try:
                    timechart_csv, date_fmt = DB_PCACE_data_analysis_util.prepare_timechart_csv(
                        inputDir, outputDir, setup_simplex)
                    if timechart_csv and os.path.isfile(timechart_csv):
                        timechart_output = IO_files_util.generate_output_file_name(
                            '', inputDir, outputDir, '.html', setup_simplex + '_timechart')
                        parent_names = DB_PCACE_data_analysis_util.get_setup_simplex_parent(setup_simplex)
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
            gis_csv = DB_PCACE_data_analysis_util.prepare_gis_locations_csv(
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
                    # Load per-database GIS settings (country bias, area, restrict)
                    _gis_country, _gis_area, _gis_restrict = GIS_pipeline_util.load_GIS_settings(inputDir)
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
                        _gis_country,       # country_bias — from GIS_settings.json
                        _gis_area,          # area_var — from GIS_settings.json
                        _gis_restrict,      # restrict — from GIS_settings.json
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
GUI_util.run_button.configure(command=run)

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
config_filename = 'DB_PCACE_data_analysis_config.csv'
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
    """Open the DB SQL GUI (same as the validation GUI's dropdown).

    Nothing PC-ACE-specific is checked or exported here: DB_SQL needs SQL/SQLite input, not PC-ACE data,
    so it validates its OWN input. It builds the SQLite itself from the xlsx/csv in the input directory,
    applying the same DB_PCACE_data_analyzer_util.reading_list column renames -- which made the old
    export-then-pre-select step redundant."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DB_SQL_main.py')
    cmd = [sys.executable, script_path]
    # hand over OUR I/O config: it is what DB_SQL renders its INPUT/OUTPUT DIR box from, so passing the
    # dirs alone would open it DISPLAYING the default config while operating on ours.
    if GUI_util.config_filename_selected_config.get():
        cmd.extend(['--config', GUI_util.config_filename_selected_config.get()])
    if inputDir.get():
        cmd.extend(['--inputdir', inputDir.get()])
    if outputDir.get():
        cmd.extend(['--outputdir', outputDir.get()])
    subprocess.Popen(cmd)

# Data validation is now a tab in this GUI (see the Data validation tab), so there is no launcher for a
# separate validation GUI.

def _open_data_manipulation():
    """Launch the data manipulation GUI."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_manipulation_main.py')
    cmd = [sys.executable, script_path]
    if outputDir.get():
        cmd.extend(['--outputdir', outputDir.get()])
    subprocess.Popen(cmd)


def _open_statistics_csv():
    """Launch the csv statistics GUI.

    No csv is handed over: unlike DB_SQL -- whose RUN drops the query result straight into an INPUT CSV
    widget -- this GUI has no query result to pass, so statistics_csv opens with its INPUT CSV field empty
    for the user to fill (its 'Select INPUT CSV file' button offers this corpus's csv files)."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'statistics_csv_main.py')
    cmd = [sys.executable, script_path]
    # hand over OUR I/O config: it is what statistics_csv renders its INPUT/OUTPUT box from, so without it
    # the GUI would open displaying the DEFAULT config instead of the corpus we are working on.
    if GUI_util.config_filename_selected_config.get():
        cmd.extend(['--config', GUI_util.config_filename_selected_config.get()])
    if outputDir.get():
        cmd.extend(['--outputdir', outputDir.get()])
    subprocess.Popen(cmd)

def _open_corpus_checker():
    """Launch the corpus checker (PC-ACE data) GUI.

    No directory is handed over. This GUI's INPUT is the directory of PC-ACE table exports, whereas the
    corpus checker expects the DOCUMENT corpus those tables were coded from -- one subdirectory per event,
    each holding that event's txt articles. Seeding it with our inputDir would prefill a path of the wrong
    shape, so the corpus checker opens on its own configured directories."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'corpus_checker_PCACE_data_main.py')
    subprocess.Popen([sys.executable, script_path])

def _on_open_gui_selected(choice):
    if choice == 'Open DB SQL GUI':
        open_sql_query()
    elif choice == 'Open data manipulation GUI':
        _open_data_manipulation()
    elif choice == 'Open data statistics GUI':
        _open_statistics_csv()
    elif choice == 'Open corpus checker (PC-ACE data) GUI':
        _open_corpus_checker()

_open_gui_var = tk.StringVar()
_open_gui_var.set('Open DB SQL GUI')
open_gui_menu = tk.OptionMenu(window, _open_gui_var,
                              'Open DB SQL GUI',
                              'Open data manipulation GUI',
                              'Open data statistics GUI',
                              'Open corpus checker (PC-ACE data) GUI',
                              command=_on_open_gui_selected)
open_gui_menu.configure(width=25)
# Shell ? HELP for the top I/O rows (the classic left ? HELP column was dropped with the window-level
# help_buttons()). sameY, so it sits left of the launcher dropdown rather than on its own row.
_shell_help_button = tk.Button(window, text='? HELP',
    command=lambda: GUI_IO_util.display_help_button_info("NLP Suite Help",
        "PC-ACE Tables Analyzer -- all PC-ACE analysis in one window, in two tabs.\n\n"
        "Grammar tab: view table relations; view the grammar as text or as an interactive tree; update the "
        "grammar and identifiers; and rename / remove / merge grammar objects.\n\n"
        "Cross-complex query tab: map a data ID to a setup ID; query Complex objects (Identifiers, Extended "
        "headers, Parents & children, Document sources, Comments) and Simplex objects (Export values, Charts, "
        "Time chart, GIS map); search simplex values; and list parents/children.\n\n"
        "Use the 'Open ... GUI' dropdown to launch related PC-ACE tools (SQL, data validation, data "
        "manipulation, statistics, corpus checker)." + GUI_IO_util.msg_Esc))
GUI_IO_util.placeWidget(window, GUI_IO_util.help_button_x_coordinate, y_multiplier_integer,
                        _shell_help_button, True, True, False, False, 90,
                        GUI_IO_util.help_button_x_coordinate, '')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_gui_menu,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to open a related GUI.\n\n"
                                   "   Open DB SQL GUI: opens the SQL query GUI.\n"
                                   "   Open data manipulation GUI: opens the data manipulation GUI.\n"
                                   "   Open data statistics GUI: open the GUI for statistical analyses.\n"
                                   "   Open corpus checker (PC-ACE data) GUI: run reliability checks on the DOCUMENT "
                                   "corpus your PC-ACE tables were coded from (are documents filed under the right "
                                   "event? are names spelled consistently? are some documents duplicates?).")

# ── Notebook: Grammar + Cross-complex query tabs ────────────────────────────────
# The dense content below broke the grid layout (it shares columns across ~50 rows), so this GUI is
# reorganized like data_visualization: the top I/O rows + this notebook are gridded on the window; the
# dense content lives inside two tab frames, each .place'd (grid never finalizes tab-frame children).
tab_help_x = GUI_IO_util.close_button_x_coordinate - GUI_IO_util.labels_x_coordinate

def tab_help(parent, y, message, x=6):
    # ? HELP in the tab's LEFT margin (content starts at labels_x_coordinate), mirroring the classic
    # left ? HELP column so it never overlaps the row's widgets.
    btn = tk.Button(parent, text='? HELP', command=lambda m=message: mb.showinfo("NLP Suite Help", m))
    btn.place(x=x, y=y)

nb_style = ttk.Style()
try:
    nb_style.theme_use('clam')
except Exception:
    pass
nb_style.configure('PCACE.TNotebook.Tab', font=('Courier', 11, 'bold'), foreground='red', padding=[12, 4])
nb_style.map('PCACE.TNotebook.Tab',
             background=[('selected', '#d0e0f0'), ('!selected', '#e8e8e8')],
             foreground=[('selected', 'red'), ('!selected', '#999999')])

notebook = ttk.Notebook(window, style='PCACE.TNotebook')
nb_width = GUI_IO_util.get_GUI_width(3) - GUI_IO_util.labels_x_coordinate - 20
# Sized so the tallest tab fits AND the RUN/CLOSE bar stays on-screen on a 150%/short display (~640px
# window). The two standalone lookup rows (From data ID -> setup ID, Search simplex value) live in their
# own Look up tab, which keeps the Cross-complex query tab short enough (~340px) to fit here.
nb_height = 310
grammar_tab = ttk.Frame(notebook, width=nb_width, height=nb_height)
query_tab = ttk.Frame(notebook, width=nb_width, height=nb_height)
lookup_tab = ttk.Frame(notebook, width=nb_width, height=nb_height)
validation_tab = ttk.Frame(notebook, width=nb_width, height=nb_height)
notebook.add(grammar_tab, text='  Grammar  ')
notebook.add(query_tab, text='  Cross-complex query  ')
notebook.add(lookup_tab, text='  Data look up  ')
notebook.add(validation_tab, text='  Data validation  ')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, notebook, False, True)
# Restored before GUI_bottom so the .place'd RUN/CLOSE bar clears the notebook. Under .place the row
# counter doesn't auto-reserve the notebook's pixel height (grid did), so advance it past the notebook
# (nb_height + tab bar) or the bottom bar would overlap the tabs.
_shell_y_multiplier = y_multiplier_integer + int(nb_height / 40) + 1

# From here the tab content is .place'd inside the frames, not gridded.
GUI_IO_util.grid_layout_enabled = False
y_multiplier_integer = -1.75  # start the Grammar tab near the top of its frame (y = 90 + 40*mult)

view_relations_button = tk.Button(grammar_tab, text='View table relations', width=17,height=1,state='disabled', command=lambda: view_relations())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(grammar_tab,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   view_relations_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to open a pdf file of the PC-ACE table relations. These relations are ALWAYS the same across any type of application of PC-ACE (e.g., Avanti! or Lynchings).\nTo view the grammar of data collection for a specific PC-ACE implementation click on the button View grrammar.")

view_grammar_button = tk.Button(grammar_tab, text='View grammar (as text)', width=17,height=1,state='disabled', command=lambda: view_grammar())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(grammar_tab,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                   view_grammar_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to export as a text file the grammmar used for the selected, specific implementation of the PC-ACE database.\nThe grammar will be exported in the same directory of the Input Excel files.\nClick on the button View table relations to visualize the general table relations in the PC-ACE databasee, regardless of a selected, specific implementation (i./e., grammar setup).")

def visualize_grammar_tree():
    outputDir_val = GUI_util.output_dir_path.get()
    inputDir_val = inputDir.get()
    if not inputDir_val:
        mb.showwarning(title='Warning', message='Please, select an input directory containing PC-ACE xlsx tables.')
        return
    csv_path = DB_PCACE_data_analysis_util.export_grammar_tree_csv(inputDir_val, outputDir_val)
    if csv_path:
        import charts_util
        outputFiles = charts_util.hierarchical_tree(csv_path, outputDir_val,
            parent_col='Parent', child_col='Child', color_col='Type')
        if outputFiles:
            IO_files_util.OpenOutputFiles(GUI_util.window, True, outputFiles, outputDir_val)
    else:
        mb.showwarning(title='Warning', message='No grammar structure found.\n\nPlease, make sure the PC-ACE database is loaded.')

visualize_grammar_tree_button = tk.Button(grammar_tab, text='View grammar (as tree)', width=20, height=1, state='disabled',
    command=lambda: visualize_grammar_tree())
y_multiplier_integer = GUI_IO_util.placeWidget(grammar_tab, GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                   visualize_grammar_tree_button,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Click to export the grammar as a parent-child CSV and visualize it as an interactive D3.js hierarchical tree.\nThe tree shows complex objects and their simplex children, color-coded by type.")

update_grammar_button = tk.Button(grammar_tab, text='Update grammar', width=17,height=1,state='disabled', command=lambda: update_grammar())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(grammar_tab,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                   update_grammar_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to update the grammmar used for the selected, specific implementation of the PC-ACE database saved in setup_complex.xlsx and setup_complex.pkl.\nThe grammar will be saved in setup_complex.xlsx and setup_complex.pkl.\nClick on the button View table relations to visualize the general table relations in the PC-ACE databasee, regardless of a selected, specific implementation (i./e., grammar setup).")


update_identifier_button = tk.Button(grammar_tab, text='Update identifiers', width=17,height=1,state='disabled', command=lambda: update_identifiers())
# place widget with hover-over info
_update_id_btn_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(grammar_tab,GUI_IO_util.run_button_x_coordinate, y_multiplier_integer,
                                   update_identifier_button,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Click to update the current complex objects identifiers saved in the table data_Complex.xlsx and data_Complex.pkl")


object_type_lb = tk.Label(grammar_tab, text='Object ')
y_multiplier_integer=GUI_IO_util.placeWidget(grammar_tab,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,object_type_lb,True)

object_type_var= tk.StringVar()
object_type_var_menu = tk.OptionMenu(grammar_tab,object_type_var, 'Complex','Simplex')
object_type_var_menu.configure(state='disabled')
object_type_var.set('')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(grammar_tab,GUI_IO_util.labels_x_coordinate+50, y_multiplier_integer,
                                   object_type_var_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Use the dropdown menu to select the type of object (complex or simplex) for which to obtain a list of values.\nThe object list will then be displayed in the right-hand menu widget.")

setup_complex_menu, setup_simplex_menu = DB_PCACE_data_analysis_util.get_setup_complex_simplex_names() # os.path.join(inputDir.get())

required_object_var=tk.StringVar()
required_object = ttk.Combobox(grammar_tab, textvariable = required_object_var, width=GUI_IO_util.widget_width_short)
required_object.configure(state='disabled')
required_object['values'] = setup_complex_menu
# place widget with hover-over info
_required_object_y_row = y_multiplier_integer  # save for dynamic hover-over
_required_object_base_text = ("You can use the dropdown menu to scroll through the list of available objects.\n"
    "You can also select a complex or simplex object, then press Enter or click RUN to toggle its REQUIRED boolean value (from False to True or viceversa).\n"
    "The value is set in the setup_xref_Complex-Complex table or setup_xref_Simplex-Complex table. The xlsx, pkl, and grammar files will be updated.")
y_multiplier_integer = GUI_IO_util.placeWidget(grammar_tab,GUI_IO_util.labels_x_coordinate+150, y_multiplier_integer,
                                   required_object,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   _required_object_base_text)

def _update_required_object_dropdown(*args):
    """Switch required_object dropdown values between Complex and Simplex names.
    Re-fetches from the util each time to ensure values are current after DB load."""
    obj_type = object_type_var.get()
    try:
        c_menu, s_menu = DB_PCACE_data_analysis_util.get_setup_complex_simplex_names()
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
    current_val, xref_info = DB_PCACE_data_analysis_util.get_required_value(obj_type, obj_name)
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
        success = DB_PCACE_data_analysis_util.toggle_required_value(obj_type, obj_name, new_val, inputDir.get())
        if success:
            mb.showwarning(title='REQUIRED updated',
                           message=f'The REQUIRED value for "{obj_name}" has been changed to {new_str}.\n\n'
                                   f'The xlsx, pkl, and grammar files have been updated.')
        else:
            mb.showwarning(title='Error',
                           message=f'Failed to update the REQUIRED value for "{obj_name}".\nCheck the command line for details.')

# Enter on the required_object dropdown or RUN triggers the toggle with confirmation
required_object.bind('<Return>', lambda e: _toggle_required())

# ── Grammar object management: Rename, Remove, Merge ────────────────────────

def _rename_grammar_object():
    """Rename the selected grammar object."""
    obj_type = object_type_var.get()
    obj_name = required_object_var.get()
    if not obj_type or not obj_name:
        mb.showwarning(title='Rename',
                       message='Please select an Object type (Complex or Simplex) and an object name from the dropdown above.')
        return
    new_name = tk.simpledialog.askstring("Rename " + obj_type,
        f"Current name: {obj_name}\n\nEnter new name:",
        initialvalue=obj_name)
    if not new_name or new_name.strip() == obj_name:
        return
    proceed = mb.askyesno("Confirm rename",
        f"Rename {obj_type}:\n\n"
        f"  '{obj_name}'  →  '{new_name.strip()}'\n\n"
        f"This will update setup files and regenerate the grammar.\n\nProceed?")
    if proceed:
        success, msg = DB_PCACE_data_analysis_util.rename_grammar_object(obj_type, obj_name, new_name.strip(), inputDir.get())
        if success:
            mb.showinfo(title='Renamed', message=msg)
            _update_required_object_dropdown()
        else:
            mb.showwarning(title='Rename failed', message=msg)

def _remove_grammar_object():
    """Remove the selected grammar object (only if empty)."""
    obj_type = object_type_var.get()
    obj_name = required_object_var.get()
    if not obj_type or not obj_name:
        mb.showwarning(title='Remove',
                       message='Please select an Object type (Complex or Simplex) and an object name from the dropdown above.')
        return
    # Show data count first
    count, info = DB_PCACE_data_analysis_util.get_grammar_object_data_count(obj_type, obj_name)
    if count < 0:
        mb.showwarning(title='Remove', message=info)
        return
    if count > 0:
        mb.showwarning(title='Cannot remove',
                       message=f"{obj_type} '{obj_name}' has {count} data instance(s).\n\n"
                               f"Removing it would cause data loss.\n\n"
                               f"Use Merge to reassign the data to another {obj_type} first.")
        return
    proceed = mb.askyesno("Confirm remove",
        f"Remove {obj_type} '{obj_name}' from the grammar?\n\n"
        f"This object has 0 data instances, so no data will be lost.\n"
        f"It will be removed from setup tables and xref tables.\n\nProceed?")
    if proceed:
        success, msg = DB_PCACE_data_analysis_util.remove_grammar_object(obj_type, obj_name, inputDir.get())
        if success:
            mb.showinfo(title='Removed', message=msg)
            _update_required_object_dropdown()
        else:
            mb.showwarning(title='Remove failed', message=msg)

def _merge_grammar_objects():
    """Merge the selected grammar object into another (reassign all data)."""
    obj_type = object_type_var.get()
    source_name = required_object_var.get()
    if not obj_type or not source_name:
        mb.showwarning(title='Merge',
                       message='Please select an Object type (Complex or Simplex) and the SOURCE object to merge FROM in the dropdown above.')
        return
    # Get the list of possible targets (all objects of same type except source)
    try:
        c_menu, s_menu = DB_PCACE_data_analysis_util.get_setup_complex_simplex_names()
    except:
        c_menu, s_menu = [], []
    if obj_type == 'Complex':
        targets = [n for n in c_menu if n != source_name]
    else:
        targets = [n for n in s_menu if n != source_name]
    if not targets:
        mb.showwarning(title='Merge', message=f'No other {obj_type} objects to merge into.')
        return

    # Show data count for source
    count, info = DB_PCACE_data_analysis_util.get_grammar_object_data_count(obj_type, source_name)
    count_str = f"{count} data instance(s)" if count >= 0 else "unknown"

    # Ask user to pick target
    merge_win = tk.Toplevel(window)
    merge_win.title(f"Merge {obj_type}: {source_name}")
    merge_win.geometry("450x200")
    merge_win.resizable(False, False)

    tk.Label(merge_win, text=f"Merge '{source_name}' ({count_str}) INTO:", font=('', 10, 'bold')).pack(pady=(15, 5))

    target_var = tk.StringVar()
    target_var.set(targets[0])
    target_combo = ttk.Combobox(merge_win, textvariable=target_var, values=targets, state='readonly', width=40)
    target_combo.pack(pady=5)

    tk.Label(merge_win, text=f"All data from '{source_name}' will be reassigned\n"
                              f"to the selected target. '{source_name}' will then\n"
                              f"be removed from the grammar.", fg='gray').pack(pady=5)

    def _do_merge():
        target_name = target_var.get()
        if not target_name:
            return
        proceed = mb.askyesno("Confirm merge",
            f"Merge {obj_type}:\n\n"
            f"  '{source_name}' → '{target_name}'\n\n"
            f"  {count_str} will be reassigned.\n"
            f"  '{source_name}' will be removed from the grammar.\n\n"
            f"This cannot be undone. Proceed?",
            parent=merge_win)
        if proceed:
            merge_win.destroy()
            success, msg = DB_PCACE_data_analysis_util.merge_grammar_objects(obj_type, source_name, target_name, inputDir.get())
            if success:
                mb.showinfo(title='Merged', message=msg)
                _update_required_object_dropdown()
            else:
                mb.showwarning(title='Merge failed', message=msg)

    tk.Button(merge_win, text='Merge', width=10, command=_do_merge).pack(pady=10)

import tkinter.simpledialog

rename_button = tk.Button(grammar_tab, text='Rename', width=8, height=1, state='disabled', command=_rename_grammar_object)
y_multiplier_integer = GUI_IO_util.placeWidget(grammar_tab, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   rename_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Rename the selected Complex or Simplex grammar object.\n"
                                   "Select the object type and name in the row above, then click Rename.\n\n"
                                   "Only the name in the setup table is changed — data references use IDs\n"
                                   "and are not affected.")

remove_button = tk.Button(grammar_tab, text='Remove', width=8, height=1, state='disabled', command=_remove_grammar_object)
y_multiplier_integer = GUI_IO_util.placeWidget(grammar_tab, GUI_IO_util.labels_x_coordinate + 80, y_multiplier_integer,
                                   remove_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Remove the selected Complex or Simplex grammar object.\n\n"
                                   "SAFETY: the object must have 0 data instances to be removed.\n"
                                   "If it has data, use Merge first to reassign data to another object.")

merge_button = tk.Button(grammar_tab, text='Merge', width=8, height=1, state='disabled', command=_merge_grammar_objects)
y_multiplier_integer = GUI_IO_util.placeWidget(grammar_tab, GUI_IO_util.labels_x_coordinate + 160, y_multiplier_integer,
                                   merge_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Merge the selected grammar object INTO another object of the same type.\n\n"
                                   "All data instances are reassigned from the source to the target.\n"
                                   "The source object is then removed from the grammar.\n\n"
                                   "Use this to consolidate duplicates (e.g., 'City', 'City 2', 'Comune' → 'City').")

merge_info_lb = tk.Label(grammar_tab, text='Select Object type and name above, then click Rename / Remove / Merge',
                         font=('', 8), fg='gray')
y_multiplier_integer = GUI_IO_util.placeWidget(grammar_tab, GUI_IO_util.labels_x_coordinate + 240, y_multiplier_integer,
                                   merge_info_lb,
                                   False, True, False, False, 90, GUI_IO_util.labels_x_coordinate, '')

# select_DB_tables_lb = tk.Label(window, text='PC-ACE table ')
# # open_setup_x_coordinate
# # y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate,y_multiplier_integer,select_DB_tables_lb,True)
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,select_DB_tables_lb,True)
#
# table_menu_values = ''
# table_list=[]
# if os.path.isdir(inputDir.get()):
#     table_list = DB_PCACE_data_analysis_util.import_PCACE_tables(inputDir.get(), outputDir.get())
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


y_multiplier_integer = -1.75  # start the Cross-complex query tab near the top of its frame

# ── Look up tab content (part 1 of 2): From data ID -> setup ID ──────────────────────────────
# The two lookup rows (this one and Search simplex, further down) live in the Look up tab, NOT the
# query tab, so they don't add height to it. They use their own row counter (lookup_y) and are
# reparented to lookup_tab; the vars and run()/enable logic are unchanged. Because they use lookup_y,
# they leave y_multiplier_integer at -1.75, so the Complex row below starts at the top of the query tab.
lookup_y = -1.75

from_dataID_setupID_lb = tk.Label(lookup_tab, text='From data ID to setup ID ')
lookup_y=GUI_IO_util.placeWidget(lookup_tab,GUI_IO_util.labels_x_coordinate,lookup_y,from_dataID_setupID_lb,True)

from_dataID_setupID_objectType_var = tk.StringVar()
from_dataID_setupID_objectType_var.set('')
from_dataID_setupID_menu = tk.OptionMenu(lookup_tab, from_dataID_setupID_objectType_var, 'Complex', 'Simplex')
from_dataID_setupID_menu.configure(state='disabled')
# place widget with hover-over info
lookup_y = GUI_IO_util.placeWidget(lookup_tab,GUI_IO_util.IO_configuration_menu-50, lookup_y,
                                   from_dataID_setupID_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Use the dropdown menu to select the type of object - complex or simplex - to go from data ID to setup name")

enter_data_ID_lb = tk.Label(lookup_tab, text='Enter data ID')
lookup_y=GUI_IO_util.placeWidget(lookup_tab,GUI_IO_util.open_reminders_x_coordinate,lookup_y,enter_data_ID_lb,True)

enter_data_ID = tk.Entry(lookup_tab,width=GUI_IO_util.widget_width_extra_short,textvariable=enter_data_ID_var)
enter_data_ID.configure(state="disabled")
# place widget with hover-over info

lookup_y = GUI_IO_util.placeWidget(lookup_tab,GUI_IO_util.open_reminders_x_coordinate+100,
    lookup_y,
    enter_data_ID, True, False, True, False, 90,
    GUI_IO_util.open_reminders_x_coordinate+100, "Enter the numeric data ID value")

setup_name = tk.Entry(lookup_tab,width=GUI_IO_util.widget_width_short,textvariable=setup_name_var,state='disabled')
# setup_name.configure(state="disabled")
# place widget with hover-over info

lookup_y = GUI_IO_util.placeWidget(lookup_tab,GUI_IO_util.open_setup_x_coordinate,
    lookup_y,
    setup_name, False, False, True, False, 90,
    GUI_IO_util.open_setup_x_coordinate, "Extracted setup name")


complex_objects_lb = tk.Label(query_tab, text='Complex ')
y_multiplier_integer=GUI_IO_util.placeWidget(query_tab,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,complex_objects_lb,True)

# setup_complex_menu, setup_simplex_menu = DB_PCACE_data_analysis_util.get_setup_complex_simplex_names() # os.path.join(inputDir.get())

setup_complex_var=tk.StringVar()
setup_complex = ttk.Combobox(query_tab, textvariable = setup_complex_var, width=GUI_IO_util.widget_width_short)
setup_complex.configure(state='disabled')
setup_complex['values'] = setup_complex_menu
# place widget with hover-over info
_setup_complex_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(query_tab,GUI_IO_util.labels_x_coordinate+90, y_multiplier_integer,
                                   setup_complex,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Select a complex object type from the dropdown.\n"
                                   "The Complex identifier dropdown (right) auto-populates with all instances.\n\n"
                                   "Checkboxes: Identifiers, Extended headers, Parents/children, Document sources, Comments.\n"
                                   "Tick a checkbox and click RUN to perform that operation.\n"
                                   "No checkbox: RUN exports the story form for the selected identifier.")

# Complex export options -- grouped into a titled frame with LABELED checkboxes. These were five BLANK
# checkboxes crammed on the Complex row whose meaning lived only in the hover-over; the frame gives each
# a visible label. The vars are unchanged, so run() and the enable/disable logic are unaffected. The
# frame is .place'd below the Complex combobox row (tab content is .place'd, not gridded).
document_sources_var = tk.IntVar()
comments_var = tk.IntVar()
comments_var.set(0)
comments_type_var = tk.StringVar()
comments_type_var.set('')

complex_options_frame = tk.LabelFrame(query_tab, text='Complex export options', padx=6, pady=2)
identifiers_checkbox      = tk.Checkbutton(complex_options_frame, text='Identifiers',        variable=identifiers_var,      onvalue=1, offvalue=0, state='disabled')
extended_headers_checkbox = tk.Checkbutton(complex_options_frame, text='Extended headers',   variable=extended_headers_var, onvalue=1, offvalue=0, state='disabled')
parents_children_checkbox = tk.Checkbutton(complex_options_frame, text='Parents & children', variable=parents_children_var, onvalue=1, offvalue=0, state='disabled')
document_sources_checkbox = tk.Checkbutton(complex_options_frame, text='Document sources',   variable=document_sources_var, onvalue=1, offvalue=0, state='disabled')
comments_checkbox         = tk.Checkbutton(complex_options_frame, text='Comments',           variable=comments_var,         onvalue=1, offvalue=0, state='disabled')
comments_menu             = tk.OptionMenu(complex_options_frame, comments_type_var, '*', 'Users comments', 'Verifiers comments')
comments_menu.configure(state='disabled')
identifiers_checkbox.grid(     row=0, column=0, sticky='w', padx=4, pady=1)
extended_headers_checkbox.grid(row=0, column=1, sticky='w', padx=4, pady=1)
parents_children_checkbox.grid(row=0, column=2, sticky='w', padx=4, pady=1)
document_sources_checkbox.grid(row=1, column=0, sticky='w', padx=4, pady=1)
comments_checkbox.grid(        row=1, column=1, sticky='w', padx=4, pady=1)
comments_menu.grid(            row=1, column=2, sticky='w', padx=4, pady=1)
# Place below the Complex combobox row without advancing the shared row counter -- the Complex
# identifier (right of the combobox) stays on the combobox row; the row counter is bumped past the
# frame just before the Simplex row below.
complex_options_frame.place(x=GUI_IO_util.labels_x_coordinate + 90,
                            y=GUI_IO_util.basic_y_coordinate + 40 * (_setup_complex_y_row + 1))

complex_identifiers_lb = tk.Label(query_tab, text='Complex identifier')
y_multiplier_integer=GUI_IO_util.placeWidget(query_tab,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,complex_identifiers_lb,True)

complex_identifiers_menu = DB_PCACE_data_analysis_util.build_macro_event_dropdown_menu(inputDir.get())

complex_identifiers_var=tk.StringVar()
complex_identifiers = ttk.Combobox(query_tab, textvariable = complex_identifiers_var, width=35)
complex_identifiers.configure(state='disabled')
complex_identifiers['values'] = complex_identifiers_menu
_complex_id_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(query_tab,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   complex_identifiers,
                                   False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Using the dropdown menu select the Simplex data type (date, number, text) to be used to visualize simplex values.\n"
                                   ""
                                   "RUN: export the story form, or perform a checkbox operation if a checkbox is ticked.")
# y_multiplier_integer = GUI_IO_util.placeWidget(query_tab,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
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
    story_text, filepath = DB_PCACE_data_analysis_util.story_form_from_dropdown(selected, outputDir_val)
    html_filepath = DB_PCACE_data_analysis_util.story_form_html_from_dropdown(selected, outputDir_val)
    if html_filepath:
        IO_files_util.openFile(query_tab, html_filepath)
    elif filepath:
        IO_files_util.openFile(query_tab, filepath)

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
            GUI_IO_util.display_widget_info(query_tab, e, x_coord,
                GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step * y_row,
                x_hover, t)))
    combo.bind('<Leave>',
        lambda e: (e.widget.config(background=combo.cget('background'), foreground=combo.cget('foreground')),
                   GUI_IO_util.delete_display_widget_lb(query_tab, e, '')))

def update_complex_identifier_dropdown(*args):
    """When user selects a hierarchical complex type, update the Complex identifier dropdown
    with all instances of that type (ID - Identifier).
    Does NOT auto-select the first item so that RUN can distinguish
    'export all' (nothing selected) vs 'export selected one'."""
    selected_type = setup_complex_var.get()
    if selected_type:
        identifier_list = DB_PCACE_data_analysis_util.build_story_dropdown(selected_type)
        complex_identifiers['values'] = identifier_list
        if identifier_list:
            complex_identifiers_var.set(identifier_list[0])
        else:
            complex_identifiers_var.set('')
    else:
        # Reset to macro event list
        macro_list = DB_PCACE_data_analysis_util.build_macro_event_dropdown_menu(inputDir.get())
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

# Drop below the Complex export-options frame (placed under the Complex row) before starting the
# Simplex row, so the frame and the Simplex row don't overlap.
y_multiplier_integer = _setup_complex_y_row + 3.5

simplex_objects_lb = tk.Label(query_tab, text='Simplex ')
y_multiplier_integer=GUI_IO_util.placeWidget(query_tab,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,simplex_objects_lb, True)

# setup_simplex_menu = DB_PCACE_data_analysis_util.get_complex_simplex_names(os.path.join(inputDir.get()))
#
setup_simplex_var = tk.StringVar()

setup_simplex = ttk.Combobox(query_tab, textvariable = setup_simplex_var, width=GUI_IO_util.widget_width_short)
setup_simplex.configure(state='disabled')
setup_simplex['values'] = setup_simplex_menu
# place widget with hover-over info
_setup_simplex_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(query_tab,GUI_IO_util.labels_x_coordinate+90, y_multiplier_integer,
                                   setup_simplex,
                                   True, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Select a simplex object type from the dropdown.\n"
                                   "The Simplex values dropdown (right) auto-populates with all data values.\n\n"
                                   "Checkboxes: Values, Spell-check, Charts, Timechart, GIS map.\n"
                                   "Tick a checkbox and click RUN to perform that operation.")

# Simplex output options -- titled frame with LABELED checkboxes (were four BLANK checkboxes). Same
# pattern as the Complex frame above; vars unchanged so run()/enable logic are unaffected.
simplex_export_values_var = tk.IntVar()
simplex_charts_var = tk.IntVar()
simplex_timechart_var = tk.IntVar()
simplex_GIS_var = tk.IntVar()

simplex_options_frame = tk.LabelFrame(query_tab, text='Simplex output', padx=6, pady=2)
simplex_export_values_checkbox = tk.Checkbutton(simplex_options_frame, text='Export values', variable=simplex_export_values_var, onvalue=1, offvalue=0, state='disabled')
simplex_charts_checkbox        = tk.Checkbutton(simplex_options_frame, text='Charts',        variable=simplex_charts_var,        onvalue=1, offvalue=0, state='disabled')
simplex_timechart_checkbox     = tk.Checkbutton(simplex_options_frame, text='Time chart',    variable=simplex_timechart_var,     onvalue=1, offvalue=0, state='disabled')
simplex_GIS_checkbox           = tk.Checkbutton(simplex_options_frame, text='GIS map',       variable=simplex_GIS_var,           onvalue=1, offvalue=0, state='disabled')
simplex_export_values_checkbox.grid(row=0, column=0, sticky='w', padx=4, pady=1)
simplex_charts_checkbox.grid(       row=0, column=1, sticky='w', padx=4, pady=1)
simplex_timechart_checkbox.grid(    row=0, column=2, sticky='w', padx=4, pady=1)
simplex_GIS_checkbox.grid(          row=0, column=3, sticky='w', padx=4, pady=1)
# kept so the dynamic GIS "last updated" hover-over (bound below) still resolves a row
_gis_checkbox_y_row = _setup_simplex_y_row
simplex_options_frame.place(x=GUI_IO_util.labels_x_coordinate + 90,
                            y=GUI_IO_util.basic_y_coordinate + 40 * (_setup_simplex_y_row + 1))

simplex_values_var = tk.StringVar()
simplex_values_lb = tk.Label(query_tab, text='Simplex values')
y_multiplier_integer = GUI_IO_util.placeWidget(query_tab, GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                   simplex_values_lb, True)

simplex_values = ttk.Combobox(query_tab, textvariable = simplex_values_var, width=35)
simplex_values.configure(state='disabled')
simplex_values['values'] = []
_simplex_val_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(query_tab,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                   simplex_values,
                                   False, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Auto-populated when a Simplex type is selected.\n"
                                   "Lists all data values for the selected simplex.\n"
                                   "Enter: export the values listing to a CSV file.\n"
                                   "RUN: perform the operation(s) selected via checkboxes or GIS map.")

simplex_values_var.set('')

# Drop below the Simplex output frame (placed under the Simplex row) before the next row.
y_multiplier_integer = _setup_simplex_y_row + 3

def _simplex_values_enter(event):
    """Enter on Simplex values → export values listing to CSV."""
    simplex_name = setup_simplex_var.get()
    if not simplex_name:
        return
    outputDir_val = GUI_util.output_dir_path.get()
    inputDir_val = GUI_util.input_main_dir_path.get()
    values_csv = DB_PCACE_data_analysis_util.get_data_simplex_values_listing(
        inputDir_val, outputDir_val, simplex_name)
    if values_csv and os.path.isfile(values_csv):
        IO_files_util.openFile(query_tab, values_csv)

simplex_values.bind('<Return>', _simplex_values_enter)

def _populate_simplex_values(*args):
    """Populate the Simplex values dropdown when a simplex is selected."""
    simplex_name = setup_simplex_var.get()
    if not simplex_name:
        simplex_values['values'] = []
        simplex_values_var.set('')
        return
    try:
        vals = DB_PCACE_data_analysis_util.get_simplex_values_by_name(simplex_name)
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

simplex_value_type_lb = tk.Label(lookup_tab, text='Simplex data type ')
lookup_y=GUI_IO_util.placeWidget(lookup_tab,GUI_IO_util.labels_x_coordinate,lookup_y,simplex_value_type_lb,True)

simplex_value_type_var= tk.StringVar()
simplex_value_type_menu = tk.OptionMenu(lookup_tab, simplex_value_type_var, 'text','date', 'number')
simplex_value_type_menu.configure(state='disabled')
simplex_value_type_var.set('')
# place widget with hover-over info
lookup_y = GUI_IO_util.placeWidget(lookup_tab,GUI_IO_util.IO_configuration_menu-50, lookup_y,
                                   simplex_value_type_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_S_dictionary,
                                   "Use the dropdown menu to select the simplex data type to be used to extract a list of all available values.")

inputDirSV = ''
# simplex_value = ''
simplex_value_var = tk.StringVar()
# simplex_value_var.set(simplex_list)
# simplex_value_var = simplex_list
simplex_value = ttk.Combobox(lookup_tab, textvariable = simplex_value_var, width=GUI_IO_util.widget_width_short)
simplex_value.configure(state='disabled')

try:
    simplex_list = DB_PCACE_data_analysis_util.get_data_simplex_text_date_number(simplex_value_type_var.get())
except:
    simplex_list=[]
simplex_value_menu = simplex_list
simplex_value['values'] = simplex_value_menu
# place widget with hover-over info
lookup_y = GUI_IO_util.placeWidget(lookup_tab,GUI_IO_util.open_reminders_x_coordinate, lookup_y,
                                   simplex_value,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate+300,
                                   "Use the dropdown menu to select the simplex data type value (e.g., police) for which you want to find simplex & complex objects usage.")

value_parent_object_checkbox = tk.Checkbutton(lookup_tab, text='Get simplex/complex objects of selected data type (& value)', variable=value_parent_object_var, onvalue=1, offvalue=0)
# place widget with hover-over info
lookup_y = GUI_IO_util.placeWidget(lookup_tab,GUI_IO_util.open_setup_x_coordinate+150, lookup_y,
                                   value_parent_object_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Tick the checkbox to export simplex and complex objects that use the selected data type and, perhaps, value")

def activate_date_number_text(*args):
    if simplex_value_type_var.get()!='':
        simplex_value.configure(state='normal')
    else:
        simplex_value.configure(state='disabled')
    simplex_list = DB_PCACE_data_analysis_util.get_data_simplex_text_date_number(simplex_value_type_var.get())
    simplex_value['values'] = simplex_list
    if simplex_list:
        simplex_value_var.set(simplex_list[0])
    else:
        simplex_value_var.set('')
simplex_value_type_var.trace('w',activate_date_number_text)

# Search simplex value → story form row (Look up tab, part 2 of 2) _________________________
# Reparented to lookup_tab and continues the lookup_y counter (stacks below From data ID). Removing it
# from the query tab lets Parents/children close up under Simplex, keeping the query tab short.

search_simplex_lb = tk.Label(lookup_tab, text='Search simplex value')
lookup_y=GUI_IO_util.placeWidget(lookup_tab,GUI_IO_util.labels_x_coordinate,lookup_y,search_simplex_lb,True)

search_simplex_var = tk.StringVar()
search_simplex_entry = tk.Entry(lookup_tab, textvariable=search_simplex_var, width=20, state='disabled')
lookup_y = GUI_IO_util.placeWidget(lookup_tab,GUI_IO_util.IO_configuration_menu-50, lookup_y,
                                   search_simplex_entry,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Type a simplex value to search for (e.g., a city name, a person name) and press Enter.\n"
                                   "The search is case-insensitive.\n"
                                   "The Search results dropdown (right) auto-populates with all matching hierarchical objects (++).\n\n"
                                   "Enter (in this field): search and populate results.\n"
                                   "Enter (in results dropdown): export the story form for the selected object.")

# The 'Search results' label is dropped; the results dropdown itself sits where the label was
# (open_setup_x_coordinate), on the same row as 'Search simplex value'.
search_simplex_results_var = tk.StringVar()
search_simplex_results = ttk.Combobox(lookup_tab, textvariable=search_simplex_results_var, width=GUI_IO_util.widget_width_short)
search_simplex_results.configure(state='disabled')
search_simplex_results['values'] = []
_search_results_y_row = lookup_y  # save for dynamic hover-over
lookup_y = GUI_IO_util.placeWidget(lookup_tab,GUI_IO_util.open_reminders_x_coordinate, lookup_y,
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
    story_text, filepath = DB_PCACE_data_analysis_util.story_form_from_dropdown(selected, outputDir_val)
    html_filepath = DB_PCACE_data_analysis_util.story_form_html_from_dropdown(selected, outputDir_val)
    if html_filepath:
        IO_files_util.openFile(query_tab, html_filepath)
    elif filepath:
        IO_files_util.openFile(query_tab, filepath)

search_simplex_results.bind('<Return>', _search_results_enter)

def run_simplex_search(*args):
    """When user presses Enter in the search box, search and populate results dropdown."""
    search_term = search_simplex_var.get().strip()
    print(f"  run_simplex_search triggered with: '{search_term}'")
    if not search_term:
        return
    results = DB_PCACE_data_analysis_util.build_search_results_dropdown(search_term)
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

select_parents_lb = tk.Label(query_tab, text='Parents ')
y_multiplier_integer=GUI_IO_util.placeWidget(query_tab,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,select_parents_lb,True)

select_parents = ttk.Combobox(query_tab, width=GUI_IO_util.widget_width_short, textvariable=complex_parents_var, state='disabled')
# select_parents.configure(state='disabled')
# place widget with hover-over info
_select_parents_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(query_tab,GUI_IO_util.labels_x_coordinate+90, y_multiplier_integer,
                                   select_parents,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "The menu displays a list of complex objects parent of the 'Complex' or 'Simplex' selected in the widgets above.")

select_children_lb = tk.Label(query_tab, text='Complex children ')
y_multiplier_integer=GUI_IO_util.placeWidget(query_tab,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,select_children_lb,True)

select_children = ttk.Combobox(query_tab, width=35, textvariable=complex_children_var, state='disabled')
# select_children.configure(state='disabled')
# place widget with hover-over info
_select_children_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(query_tab,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
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
        table_list = DB_PCACE_data_analysis_util.import_PCACE_tables(inputDir.get(), outputDir.get())
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
            # DB_PCACE_data_analysis_util.load_lib(inputDir.get(), outputDir.get())
            DB_PCACE_data_analysis_util.build_libraries(inputDir.get(), outputDir.get())
            currentInputDir = inputDir.get()
            readDir = True

        setup_complex_menu, setup_simplex_menu = DB_PCACE_data_analysis_util.get_setup_complex_simplex_names() # os.path.join(inputDir.get())
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
            visualize_grammar_tree_button.configure(state='normal')
            rename_button.configure(state='normal')
            remove_button.configure(state='normal')
            merge_button.configure(state='normal')
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
                    complex_identifiers_menu = DB_PCACE_data_analysis_util.build_macro_event_dropdown_menu(inputDir.get())
                    complex_identifiers['values'] = complex_identifiers_menu
                    if complex_identifiers_menu:
                        complex_identifiers_var.set(complex_identifiers_menu[0])
                    # Populate hierarchical complex dropdown
                    hierarchical_complex_menu = DB_PCACE_data_analysis_util.build_hierarchical_complex_dropdown_menu(inputDir.get())
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
        if DB_PCACE_data_analysis_util.setup_Complex_lib is None:
            return
    except (AttributeError, NameError):
        return
    if setup_complex_var.get()!='':
        parents_complex_list = DB_PCACE_data_analysis_util.get_setup_complex_parents(setup_complex_var.get())
        children_complex_list_all, children_complex_list_required = DB_PCACE_data_analysis_util.get_setup_complex_children(setup_complex_var.get())
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
        simplex_children_all_list, simplex_children_required_list = DB_PCACE_data_analysis_util.get_setup_complex_simplex_children(setup_complex_var.get())
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
        parents_complex_list = DB_PCACE_data_analysis_util.get_setup_simplex_parent(setup_simplex_var.get())
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
    DB_PCACE_data_analysis_util.view_grammar(os.path.join(inputDir.get(), 'setup_Complex.xlsx'),
                                             'GrammarRule_Text', os.path.join(inputDir.get(),
                                                                              'PC-ACE grammar for database ' + tail + '.txt'))
def update_grammar():
    head, tail = os.path.split(inputDir.get())
    DB_PCACE_data_analysis_util.update_grammar_text(inputDir.get())

def update_identifiers():
    head, tail = os.path.split(inputDir.get())
    DB_PCACE_data_analysis_util.update_all_identifiers(inputDir.get())
    # Refresh hover-over to show updated timestamp
    _update_last_updated_hovers(inputDir.get(), outputDir.get())

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'PC-ACE tables analyzer via Pandas':'TIPS_NLP_PC-ACE Access DB Analyzer.pdf',
               'PC-ACE - Export ACCESS tables to Excel':'TIPS_NLP_PC-ACE - Export ACCESS tables to Excel.pdf',
               'SVO automatic extraction and visualization': 'TIPS_NLP_SVO extraction and visualization.pdf',
               "Google Earth Pro": "TIPS_NLP_GIS_Google Earth Pro.pdf",
               "Google API Key": "TIPS_NLP_GIS_Google API Key.pdf",
               "Geocoding": "TIPS_NLP_GIS_Geocoding.pdf",
               "Geocoding: How to Improve Nominatim": "TIPS_NLP_GIS_Geocoding Nominatim.pdf",
               "Gephi network graphs": "TIPS_NLP_Gephi network graphs.pdf",
               "Word clouds":"TIPS_NLP_Wordclouds Visualizing word clouds.pdf",
               'Filtering data in PC-ACE':'TIPS_NLP_Filtering Function.pdf'}
TIPS_options='PC-ACE tables analyzer via Pandas', 'PC-ACE - Export ACCESS tables to Excel', 'SVO automatic extraction and visualization', 'Google Earth Pro', 'Google API Key', 'Geocoding', 'Geocoding: How to Improve Nominatim', 'Gephi network graphs', 'Word clouds','Filtering data in PC-ACE'

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

    # Row: Open GUI dropdown
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                "Use the dropdown menu to open a related GUI. Each one opens on the SAME corpus you are "
                                "working on here (your INPUT/OUTPUT configuration is passed on to it).\n\n"
                                "   Open DB SQL GUI: run SQL queries on your data. The SQLite database is built "
                                "automatically from the xlsx/csv tables in your input directory (and rebuilt only when "
                                "they change), so there is nothing to export first.\n\n"
                                "   Open data manipulation GUI: reshape and edit your data.\n\n"
                                "   Open data statistics GUI: compute descriptive statistics on a csv file, for "
                                "instance a query result saved from the DB SQL GUI.\n\n"
                                "   Open corpus checker (PC-ACE data) GUI: run a pipeline of reliability checks on the "
                                "DOCUMENT corpus your PC-ACE tables were coded from, rather than on the tables "
                                "themselves: whether documents are filed under the right event, whether the same "
                                "people and places are spelled consistently, and whether some documents are "
                                "duplicates of others." + GUI_IO_util.msg_Esc)
    # Row: View table relations / View grammar / Update grammar / Update identifiers / Object type / required object
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                "Click View table relations to see PC-ACE table relations.\n"
                                "Click View grammar / Update grammar to see or regenerate the grammar rules."+ GUI_IO_util.msg_Esc)
    # Row: Object type
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                "Select Object type (Complex/Simplex) and an object name, then press Enter to toggle its REQUIRED value." + GUI_IO_util.msg_Esc)
    # Row: Rename / Remove / Merge
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                "RENAME: change the name of a Complex or Simplex grammar object.\n"
                                "REMOVE: delete an empty grammar object (must have 0 data instances).\n"
                                "MERGE: consolidate a grammar object into another — all data is reassigned.\n\n"
                                "Select the Object type and name in the row above first." + GUI_IO_util.msg_Esc)
    # Row: From data ID to setup ID
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                "Enter a data ID to look up the corresponding setup Complex or Simplex name." + GUI_IO_util.msg_Esc)
    # Row: Complex
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "COMPLEX: select a complex object type from the dropdown.\n\n"
                                                         "Checkboxes (left to right):\n"
                                                         "  1. IDENTIFIERS: compact summary with human-readable Identifier strings.\n"
                                                         "  2. EXTENDED HEADERS: fully expanded table with every simplex in its own column.\n"
                                                         "  3. PARENTS/CHILDREN: display parents and children of the selected object.\n"
                                                         "  4. DOCUMENT SOURCES: extract the documents (e.g., newspapers) for the selected object.\n"
                                                         "  5. COMMENTS: extract comments left by users and/or verifiers. Use the dropdown mnu to select the type of comment.\n\n"
                                                         "When no checkbox is ticked, RUN exports the story form for the identifier shown in the right-hand dropdown.\n\n"
                                                         "COMPLEX IDENTIFIER: auto-populated when a Complex type is selected.\n"
                                                         "Enter: export the story form for the selected object.\n"
                                                         "RUN: export the story form, or perform a checkbox operation."
                                                         + GUI_IO_util.msg_Esc)
    # Row: Simplex
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "SIMPLEX: select a simplex object type from the dropdown.\n\n"
                                                         "Checkboxes (left to right):\n"
                                                         "  1. VALUES: export all data values with frequencies to CSV.\n"
                                                         "  2. CHARTS: produce bar and pie charts of value frequencies.\n"
                                                         "  3. TIMECHART: generate a timeline chart (date simplexes only).\n"
                                                         "  4. GIS MAP: geocode location values and display on Google Earth Pro, Google Maps, and Folium.\n\n"
                                                         "Spell-check and lemmatization have been moved to the Data Validation GUI."
                                                         + GUI_IO_util.msg_Esc)
    # Row: simplex data type
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "Please, using the dropdown menu, select the simplex data value (text, date, or number) for which you want to see its usage among parent simplex and complex.\n\nThe available values will be displayed in the next dropdown menu widget where you can select a specific value.\n\nYou can then tick the 'Get simplex/complex objects...' checkbox if you wish to visualize all simplex and complex objects that use the selected value (e.g.,'police')."
                                                         + GUI_IO_util.msg_Esc)
    # Row: Search simplex value
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "SEARCH: type a simplex value and press Enter to search.\n"
                                                         "RESULTS: select a match and press Enter to export its story form."
                                                         + GUI_IO_util.msg_Esc)
    # Row: Parents / Complex children
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                "Select the PARENT object and/or CHILD object." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer -1
"COUNT Display a template SQL COUNT query."
"DUPLICATES The query builds a temporary table of duplicate records, then, depending on user's choice, extracts only one occurrence of all duplicate records or all duplicate occurrences except one (all DISTINCT records will not be displayed). Query results can be used to move occurrences of objects for which multiples should not be allowed."
"UNMATCHED Automatically build a simple query that will give a list of all unmatched records between any two given tables/queries on the basis of a specific field (MEMO type fields cannot be matched!)\nThe query will give you a list of the fields in the first selected table/query that do not find a match in the second selected table/query."

# Per-tab ? HELP, top-left of each tab (the window-level help_buttons() column was dropped -- it can't
# align with tab content). Per-widget detail still lives in the hover-over tooltips.
tab_help(grammar_tab, 6,
    "GRAMMAR\n\n"
    "View table relations -- show how the PC-ACE tables relate.\n"
    "View grammar (as text / as tree) -- inspect the complex/simplex grammar; the tree is an interactive view.\n"
    "Update grammar / Update identifiers -- refresh the saved grammar and the complex-object identifiers.\n\n"
    "Object type + name -- pick a Complex or Simplex object, then:\n"
    "  Rename -- rename it everywhere.\n"
    "  Remove -- delete it (only if empty).\n"
    "  Merge -- reassign all its data into another object.")
tab_help(query_tab, 6,
    "CROSS-COMPLEX QUERY\n\n"
    "Complex -- pick a complex type; Complex identifier lists its instances. Export options: Identifiers, "
    "Extended headers, Parents & children, Document sources, Comments. Tick one and RUN; no tick = export "
    "the story form for the selected identifier.\n\n"
    "Simplex -- pick a simplex type; Simplex values lists its data values. Output: Export values, Charts, "
    "Time chart, GIS map.\n\n"
    "Parents / Complex children -- auto-filled with the parents and children of the Complex or Simplex "
    "object you select above.\n\n"
    "(Data-ID lookups, data-type/value lookups, and simplex-value search are in the Look up tab.)")
tab_help(lookup_tab, 6,
    "LOOK UP\n\n"
    "From data ID to setup ID -- pick Complex or Simplex, enter a coded data ID, and RUN to resolve its "
    "setup object name.\n\n"
    "Simplex data type -- pick a data type (text/date/number) and a value, tick 'Get simplex/complex "
    "objects of selected data type' and RUN to export the objects that use it.\n\n"
    "Search simplex value -- type a simplex value (a city, a person name, ...) and press Enter; the Search "
    "results dropdown lists every hierarchical object containing it. Select one and press Enter (or RUN) to "
    "export its story form.")



# ===== Data validation tab (merged from DB_PCACE_data_validation_main; reparented to validation_tab) =====
# The RUN button dispatches to run_validation() when this tab is active (see run()).
valid_y = -1.75
def _ensure_database_loaded(inputDir):
    """Load the PC-ACE database tables if not already loaded."""
    global _database_loaded
    if _database_loaded:
        return True
    if not inputDir or not os.path.isdir(inputDir):
        return False
    try:
        outputDir_val = GUI_util.output_dir_path.get() if hasattr(GUI_util.output_dir_path, 'get') else ''
        if not outputDir_val:
            outputDir_val = inputDir
        DB_PCACE_data_analysis_util.build_libraries(inputDir, outputDir_val)
        DB_PCACE_data_analysis_util.build_NLP_libraries(inputDir, outputDir_val)
        _database_loaded = True
        return True
    except Exception as e:
        print(f"  WARNING: Could not load PC-ACE database: {e}")
        return False

# RUN section ______________________________________________________________________________________________________________________________________________________

def run_validation():
    # widget values read here at RUN time (was: run_script_command lambda + run() params)
    inputFilename = GUI_util.inputFilename.get() if hasattr(GUI_util.inputFilename, 'get') else ''
    outputDir = GUI_util.output_dir_path.get()
    openOutputFiles = GUI_util.open_csv_output_checkbox.get()
    chartPackage = GUI_util.charts_package_options_widget.get()
    dataTransformation = GUI_util.data_transformation_options_widget.get()

    config_filename = GUI_util.config_filename_selected_config.get()
    inputDir = GUI_util.input_main_dir_path.get()
    filesToOpen = []

    if not inputDir or not os.path.isdir(inputDir):
        mb.showwarning(title='Warning',
                       message='No INPUT directory selected.\n\nPlease, select the PC-ACE database directory and try again.')
        return

    outputDir = IO_files_util.make_output_subdirectory('', inputDir, outputDir, label='PCACE')
    if not outputDir:
        return

    GUI_util.window.focus_set()
    GUI_util.window.config(cursor='watch')
    GUI_util.window.update()

    if not _ensure_database_loaded(inputDir):
        mb.showwarning(title='Warning',
                       message='Could not load the PC-ACE database from the selected directory.\n\n'
                               'Please, check that the directory contains the expected Excel/pkl files.')
        return

    has_agg_simplexes = len(_agg_simplex_list) > 0
    agg_mode = agg_mode_var.get()
    run_cross_db = agg_mode in (_AGG_MODE_CROSS_DB, _AGG_MODE_BOTH)
    run_side_by_side = agg_mode in (_AGG_MODE_SIDE_BY_SIDE, _AGG_MODE_BOTH)
    nothing_selected = (spell_check_var.get() == 0
                        and lemmatize_var.get() == 0
                        and not run_cross_db
                        and not run_side_by_side
                        and not has_agg_simplexes)
    if nothing_selected:
        mb.showwarning(title='Nothing selected',
                       message='No validation task selected.\n\n'
                               'Please select at least one option:\n'
                               '  - Run spell-check\n'
                               '  - Run lemmatization\n'
                               '  - Cross-DB comparison\n'
                               '  - Side-by-side mapping with aggregate simplexes')
        return

    def _spell_check_bar_chart(dupes_csv, n_total, outputDir):
        """Create a bar chart: flagged vs correct unique text values."""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            dupes_df = pd.read_csv(dupes_csv)
            n_flagged = dupes_df['Value'].nunique() if 'Value' in dupes_df.columns else len(dupes_df)
            n_correct = max(0, n_total - n_flagged)
            fig, ax = plt.subplots(figsize=(6, 4))
            bars = ax.bar(['Flagged for review', 'No issues'], [n_flagged, n_correct],
                          color=['#e74c3c', '#2ecc71'])
            for bar in bars:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                        str(int(bar.get_height())), ha='center', va='bottom', fontweight='bold')
            ax.set_ylabel('Unique text values')
            ax.set_title('Spell-check results')
            chart_path = os.path.join(outputDir, 'spell_check_summary.png')
            plt.tight_layout()
            plt.savefig(chart_path, dpi=150)
            plt.close()
            return chart_path
        except Exception as e:
            print(f"  WARNING: Could not create spell-check bar chart: {e}")
            return None

    # ── Spell-check ──────────────────────────────────────────────────────────
    if spell_check_var.get() == 1:
        simplex_name = spell_check_simplex_var.get()
        sx_for_est = simplex_name if (simplex_name and simplex_name != 'ALL text simplexes') else ''
        n_vals, est_sec = DB_PCACE_data_analysis_util.get_spell_check_estimate(sx_for_est)
        if est_sec >= 60:
            est_msg = f'\n\n{n_vals} unique text values to compare. Estimated time: ~{est_sec // 60} minute(s).'
        else:
            est_msg = f'\n\n{n_vals} unique text values to compare. Estimated time: ~{est_sec} second(s).'
        startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
            'Started running PC-ACE data validation spell check at',
            True, est_msg, True, '', False)
        if simplex_name and simplex_name != 'ALL text simplexes':
            # Check specific simplex — verify it's text-typed
            vtype = DB_PCACE_data_analysis_util.get_simplex_value_type(simplex_name)
            if vtype != 1:
                mb.showwarning(title='Spell-check',
                               message=f'Spell-check is only available for text-typed simplexes.\n\n'
                                       f'The selected simplex "{simplex_name}" is not text-typed.')
            else:
                try:
                    dupes_csv = DB_PCACE_data_analysis_util.find_near_duplicate_simplex_values(
                        inputDir, outputDir, simplex_name=simplex_name)
                    if dupes_csv and os.path.isfile(dupes_csv):
                        filesToOpen.append(dupes_csv)
                        csv_file_var.set(dupes_csv)
                        chart = _spell_check_bar_chart(dupes_csv, n_vals, outputDir)
                        if chart:
                            filesToOpen.append(chart)
                        mb.showinfo(title='Spell-check review',
                                    message=f'Spell-check found potential duplicates/misspellings for '
                                            f'"{simplex_name}".\n\n'
                                            f'The review file has been saved to:\n{dupes_csv}\n\n'
                                            f'To apply corrections:\n'
                                            f'  1. Open the CSV and review each row.\n'
                                            f'  2. Edit the "Suggested correction" column if needed.\n'
                                            f'  3. Set "Accept?" to N for rows you want to skip.\n'
                                            f'  4. Save the CSV, then click the "Apply changes" button.')
                    else:
                        mb.showinfo(title='Spell-check',
                                    message=f'No near-duplicate or misspelled values found for "{simplex_name}".')
                except Exception as e:
                    mb.showerror(title='Spell-check error',
                                 message=f'Spell-check failed for "{simplex_name}":\n\n{e}')
        else:
            # Check ALL text simplexes
            try:
                dupes_csv = DB_PCACE_data_analysis_util.find_near_duplicate_simplex_values(
                    inputDir, outputDir, simplex_name='')
                if dupes_csv and os.path.isfile(dupes_csv):
                    filesToOpen.append(dupes_csv)
                    csv_file_var.set(dupes_csv)
                    chart = _spell_check_bar_chart(dupes_csv, n_vals, outputDir)
                    if chart:
                        filesToOpen.append(chart)
                    mb.showinfo(title='Spell-check review',
                                message='Spell-check scanned ALL text simplexes in the database.\n\n'
                                        f'The review file has been saved to:\n{dupes_csv}\n\n'
                                        'To apply corrections:\n'
                                        '  1. Open the CSV and review each row.\n'
                                        '  2. Edit the "Suggested correction" column if needed.\n'
                                        '  3. Set "Accept?" to N for rows you want to skip.\n'
                                        '  4. Save the CSV, then click the "Apply changes" button.')
                else:
                    mb.showinfo(title='Spell-check',
                                message='No near-duplicate or misspelled values found across any text simplex.')
            except Exception as e:
                mb.showerror(title='Spell-check error',
                             message=f'Spell-check failed:\n\n{e}')

        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
            'Finished running PC-ACE data validation spell check at',
            True, '', True, startTime, False)

    # ── Lemmatization ──────────────────────────────────────────────────────────
    if lemmatize_var.get() == 1:
        startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
            'Started running PC-ACE data validation lemmatization at',
            True, '', True, '', False)
        lang_name = lemmatize_lang_var.get()
        lang_code = Stanza_util.lang_dict_rev.get(lang_name, 'en')

        # Get selected simplex types from the + button lists
        # Also include the currently selected dropdown value if not already added
        noun_simplexes = list(_noun_simplex_list)
        cur_noun = lemmatize_nouns_var.get()
        if cur_noun and cur_noun not in noun_simplexes:
            noun_simplexes.append(cur_noun)
        verb_simplexes = list(_verb_simplex_list)
        cur_verb = lemmatize_verbs_var.get()
        if cur_verb and cur_verb not in verb_simplexes:
            verb_simplexes.append(cur_verb)

        if not noun_simplexes and not verb_simplexes:
            mb.showwarning(title='Lemmatization',
                           message='No simplex types selected for lemmatization.\n\n'
                                   'Please select at least one simplex type from the Nouns or Verbs list.')
        else:
            all_lemma_files = []

            # Lemmatize noun-type simplexes (POS filter: NOUN, PROPN)
            for sx_name in noun_simplexes:
                try:
                    lemma_csv = DB_PCACE_data_analysis_util.lemmatize_simplex_values(
                        inputDir, outputDir, simplex_name=sx_name,
                        language=lang_code, pos_filter=['NOUN', 'PROPN'])
                    if lemma_csv and os.path.isfile(lemma_csv):
                        all_lemma_files.append(lemma_csv)
                except Exception as e:
                    mb.showerror(title='Lemmatization error',
                                 message=f'Lemmatization failed for "{sx_name}" (noun):\n\n{e}')

            # Lemmatize verb-type simplexes (POS filter: VERB, AUX)
            for sx_name in verb_simplexes:
                try:
                    lemma_csv = DB_PCACE_data_analysis_util.lemmatize_simplex_values(
                        inputDir, outputDir, simplex_name=sx_name,
                        language=lang_code, pos_filter=['VERB', 'AUX'])
                    if lemma_csv and os.path.isfile(lemma_csv):
                        all_lemma_files.append(lemma_csv)
                except Exception as e:
                    mb.showerror(title='Lemmatization error',
                                 message=f'Lemmatization failed for "{sx_name}" (verb):\n\n{e}')

            if all_lemma_files:
                filesToOpen.extend(all_lemma_files)
                csv_file_var.set(all_lemma_files[-1])
                mb.showinfo(title='Lemmatization review',
                            message=f'Lemmatization produced {len(all_lemma_files)} review file(s).\n\n'
                                    f'To apply:\n'
                                    f'  1. Open each CSV and review the rows.\n'
                                    f'  2. Edit the "Lemmatized form" column if needed.\n'
                                    f'  3. Set "Accept?" to N for rows you want to skip.\n'
                                    f'  4. Save the CSV, then click the "Apply changes" button.')
            else:
                mb.showinfo(title='Lemmatization',
                            message='No values changed after lemmatization.\n\n'
                                    'All text values in the selected simplexes are already in their base form.')

        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
            'Finished running PC-ACE data validation lemmatization at',
            True, '', True, startTime, False)

    # ── Aggregate code validation ───────────────────────────────────────────────
    if run_cross_db or run_side_by_side or has_agg_simplexes:
        startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
            'Started running PC-ACE data validation aggregate code assessment at',
            True, '', True, '', False)
        # Build the list of DB directories
        db_dirs = list(_agg_db_dirs)
        # Include the current inputDir if not already in the list
        if inputDir and os.path.isdir(inputDir) and inputDir not in db_dirs:
            db_dirs.insert(0, inputDir)

        if not db_dirs:
            mb.showwarning(title='Aggregate validation',
                           message='No PC-ACE database directories selected.\n\n'
                                   'Use the + button to add database directories, or set an INPUT directory.')
        else:
            if run_cross_db:
                if len(db_dirs) < 2:
                    mb.showwarning(title='Cross-DB comparison',
                                   message='Cross-DB comparison requires at least 2 databases.\n\n'
                                           'Use the + button to add more database directories.')
                else:
                    try:
                        cross_files = DB_PCACE_data_analysis_util.compare_aggregate_codes_across_dbs(
                            db_dirs, outputDir)
                        filesToOpen.extend(cross_files)
                        if cross_files:
                            mb.showinfo(title='Cross-DB comparison',
                                        message=f'Cross-DB comparison produced {len(cross_files)} file(s).\n\n'
                                                f'Check the output files for aggregate code differences across databases.')
                    except Exception as e:
                        mb.showerror(title='Cross-DB comparison error',
                                     message=f'Cross-DB comparison failed:\n\n{e}')

            if run_side_by_side or has_agg_simplexes:
                orig_name = agg_orig_var.get()
                if not orig_name:
                    mb.showwarning(title='Side-by-side mapping',
                                   message='No original simplex selected.\n\n'
                                           'Please select the simplex containing the original (non-aggregated) values\n'
                                           'in the "Original values" dropdown.')
                elif not _agg_simplex_list:
                    mb.showwarning(title='Side-by-side mapping',
                                   message='No aggregate code simplexes selected.\n\n'
                                           'Use the "Aggregate codes" dropdown and + button to select\n'
                                           'one or more aggregate code simplexes.')
                else:
                    for db_dir in db_dirs:
                        try:
                            side_file = DB_PCACE_data_analysis_util.build_aggregate_side_by_side(
                                db_dir, outputDir,
                                original_simplex=orig_name,
                                simplex_names=list(_agg_simplex_list))
                            if side_file:
                                filesToOpen.append(side_file)
                                plot_cols = []
                                if orig_name:
                                    plot_cols.append(orig_name)
                                plot_cols.extend(_agg_simplex_list)
                                db_short = os.path.basename(db_dir)
                                short_csv = os.path.join(outputDir, db_short + '_codes.csv')
                                import shutil
                                shutil.copy2(side_file, short_csv)
                                for pc in plot_cols:
                                    cf = statistics_csv_util.compute_csv_column_frequencies(
                                        GUI_util.window, short_csv, None, outputDir,
                                        False, chartPackage, dataTransformation,
                                        [pc], [], [],
                                        False, chart_title=f'Distribution: {pc}',
                                        fileNameType='', chartType='bar', pivot=False)
                                    if cf:
                                        if isinstance(cf, str):
                                            cf = [cf]
                                        for f in cf:
                                            if f.endswith('.xlsx'):
                                                filesToOpen.append(f)
                                try:
                                    os.remove(short_csv)
                                except OSError:
                                    pass
                                if orig_name:
                                    crosstab_files = DB_PCACE_data_analysis_util.build_crosstab(
                                        side_file, outputDir, orig_name, list(_agg_simplex_list))
                                    filesToOpen.extend(crosstab_files)
                                all_simplex_cols = []
                                if orig_name:
                                    all_simplex_cols.append(orig_name)
                                all_simplex_cols.extend(_agg_simplex_list)
                                heatmap_file = DB_PCACE_data_analysis_util.build_coverage_heatmap(
                                    side_file, outputDir, all_simplex_cols)
                                if heatmap_file:
                                    filesToOpen.append(heatmap_file)
                        except Exception as e:
                            mb.showerror(title='Side-by-side error',
                                         message=f'Side-by-side mapping failed for {os.path.basename(db_dir)}:\n\n{e}')
                    if filesToOpen:
                        side_csvs = [f for f in filesToOpen if f.endswith('.csv')]
                        if side_csvs:
                            csv_file_var.set(side_csvs[-1])
                            _original_side_by_side_csv[0] = side_csvs[-1] + '.orig'
                            import shutil
                            shutil.copy2(side_csvs[-1], _original_side_by_side_csv[0])
                        mb.showinfo(title='Side-by-side mapping',
                                    message=f'Side-by-side mapping produced files for {len(db_dirs)} database(s).\n\n'
                                            f'Each CSV shows original values alongside their aggregate codes.\n\n'
                                            f'To update aggregate codes: edit the CSV, then click the "Apply changes" button.')

        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
            'Finished running PC-ACE data validation aggregate code assessment at',
            True, '', True, startTime, False)

    GUI_util.window.config(cursor='')

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

# ── Select INPUT CSV file row ───────────────────────────────────────────────

csv_file_var = tk.StringVar()

def get_csv_file(validation_tab, title, fileType, annotate):
    initialFolder = os.path.dirname(os.path.abspath(csv_file_var.get())) if csv_file_var.get() else os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title=title, initialdir=initialFolder, filetypes=fileType)
    if len(filePath) > 0:
        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(filePath, 'utf-8')
        if nRecords == 0:
            mb.showwarning(title='Warning',
                           message="The selected input csv file is empty.\n\nPlease, select a different file and try again.")
            filePath = ''
        else:
            csv_file_var.set(filePath)
    return filePath

csv_file_button = tk.Button(validation_tab, width=GUI_IO_util.select_file_directory_button_width,
                            text='Select INPUT CSV file',
                            command=lambda: get_csv_file(validation_tab, 'Select INPUT csv file', [("csv files", "*.csv")], True))
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.labels_x_coordinate, valid_y,
                                               csv_file_button, True)

# Button to open the selected CSV file
openInputFile_button = tk.Button(validation_tab, width=GUI_IO_util.open_file_directory_button_width, text='',
                                 command=lambda: IO_files_util.openFile(validation_tab, csv_file_var.get()))
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.IO_configuration_menu, valid_y,
                                               openInputFile_button,
                                               True, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                               "Open INPUT csv file")

# CSV file path entry
# GUI_IO_util.csv_file_width - 8
csv_file_entry = tk.Entry(validation_tab, width=115, textvariable=csv_file_var)
csv_file_entry.config(state='disabled')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.entry_box_x_coordinate, valid_y,
                                               csv_file_entry, True)

# Clear button
def _clear_csv_file():
    csv_file_var.set('')

clear_csv_button = tk.Button(validation_tab, text='Clear', width=5, command=lambda: _clear_csv_file())
clear_csv_button.config(state='disabled')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.IO_configuration_menu+GUI_IO_util.open_file_button_brief, valid_y,
                                               clear_csv_button, True, False, True, False, 90,
                                               GUI_IO_util.run_button_x_coordinate,
                                               "Click to clear the INPUT CSV file.")

def _on_csv_file_changed(*args):
    if csv_file_var.get():
        clear_csv_button.config(state='normal')
        apply_changes_button.config(state='normal')
    else:
        clear_csv_button.config(state='disabled')
        apply_changes_button.config(state='disabled')

def _apply_changes():
    """Detect CSV type from column headers and dispatch to the right apply function."""
    csv_path = csv_file_var.get()
    if not csv_path or not os.path.isfile(csv_path):
        mb.showwarning(title='Apply changes',
                       message='No CSV file loaded.\n\n'
                               'Run a validation task first, then load or select the output CSV.')
        return
    inputDir_val = inputDir.get() if hasattr(inputDir, 'get') else inputDir
    if not inputDir_val:
        mb.showwarning(title='Apply changes',
                       message='Please select a PC-ACE database directory first.')
        return
    if not _ensure_database_loaded(inputDir_val):
        mb.showwarning(title='Apply changes',
                       message='Could not load the PC-ACE database. Please check the input directory.')
        return
    import pandas as pd
    try:
        cols = set(pd.read_csv(csv_path, nrows=0).columns)
    except Exception as e:
        mb.showerror(title='Apply changes', message=f'Could not read CSV headers:\n\n{e}')
        return
    if 'Suggested correction' in cols:
        _apply_spell_check_corrections(csv_path)
    elif 'Lemmatized form' in cols:
        _apply_lemmatization_corrections(csv_path)
    else:
        _apply_aggregate_corrections()

apply_changes_button = tk.Button(validation_tab, text='Apply changes', width=12, command=_apply_changes)
apply_changes_button.config(state='disabled')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.IO_configuration_menu+GUI_IO_util.open_file_button_brief+60, valid_y,
                                               apply_changes_button, False, False, True, False, 90,
                                               GUI_IO_util.open_reminders_x_coordinate,
                                               "Apply corrections from the loaded CSV back to the PC-ACE database.\n\n"
                                               "Automatically detects the CSV type:\n"
                                               "  - Spell-check (has 'Suggested correction' column)\n"
                                               "  - Lemmatization (has 'Lemmatized form' column)\n"
                                               "  - Aggregate codes (side-by-side mapping CSV)\n\n"
                                               "Steps:\n"
                                               "  1. Run a validation task to produce a review CSV.\n"
                                               "  2. Open and edit the CSV as needed.\n"
                                               "  3. Save it, then click this button.")

csv_file_var.trace_add('write', _on_csv_file_changed)

# ══════════════════════════════════════════════════════════════════════════════
# ── Spell-check / near-duplicate detection ────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

spell_check_lb = tk.Label(validation_tab, text='Spell-check simplex values')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.labels_x_coordinate, valid_y,
                                   spell_check_lb, True)

spell_check_var = tk.IntVar()
spell_check_checkbox = tk.Checkbutton(validation_tab, text='Run spell-check', variable=spell_check_var, onvalue=1, offvalue=0)
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.open_TIPS_x_coordinate, valid_y,
                                   spell_check_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Find near-duplicate and misspelled text values in the PC-ACE database\n"
                                   "using language-independent character similarity.\n\n"
                                   "Select a specific simplex from the dropdown or leave as 'ALL text simplexes'\n"
                                   "to scan every text simplex in the database.\n\n"
                                   "Produces a review CSV with suggested corrections and an Accept?/Reject column.")

def _combobox_release_focus(event):
    window.focus_set()

spell_check_simplex_var = tk.StringVar()
spell_check_simplex_var.set('ALL text simplexes')
spell_check_simplex_menu = ttk.Combobox(validation_tab, textvariable=spell_check_simplex_var, width=30, state='readonly')
spell_check_simplex_menu['values'] = ['ALL text simplexes']
spell_check_simplex_menu.bind('<<ComboboxSelected>>', _combobox_release_focus)
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.open_TIPS_x_coordinate + 200, valid_y,
                                   spell_check_simplex_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 200,
                                   "Select which simplex to spell-check.\n"
                                   "'ALL text simplexes' checks every text-typed simplex in the database.")

def _apply_spell_check_corrections(csv_path=None):
    """Apply accepted spell-check corrections from the CSV back to data_SimplexText."""
    inputDir_val = inputDir.get() if hasattr(inputDir, 'get') else inputDir
    if not csv_path:
        outputDir_val = outputDir.get() if hasattr(outputDir, 'get') else outputDir
        csv_path = filedialog.askopenfilename(
            title='Select the reviewed spell-check CSV',
            initialdir=outputDir_val if outputDir_val else inputDir_val,
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')])
        if not csv_path:
            return
    proceed = file_filename_util.backup_files('', inputDir_val, 'Apply spell-check corrections', fileType='.xlsx')
    if not proceed:
        return
    n_applied = DB_PCACE_data_analysis_util.apply_spell_check_corrections(csv_path, inputDir_val)
    if n_applied > 0:
        mb.showinfo(title='Corrections applied',
                    message=f'Successfully applied {n_applied} correction(s) to data_SimplexText.\n\n'
                            f'The xlsx and pkl files have been updated.\n'
                            f'The cached simplex data has been cleared and will rebuild on next run.')
    elif n_applied == 0:
        mb.showinfo(title='No corrections',
                    message='No corrections were applied.\n\n'
                            'Either all rows were marked Accept? = N, or the old values '
                            'were not found in data_SimplexText.')
    else:
        mb.showerror(title='Error',
                     message='An error occurred while applying corrections.\nCheck the console output for details.')

# ══════════════════════════════════════════════════════════════════════════════
# ── Lemmatize simplex values (Stanza) ─────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

lemmatize_lb = tk.Label(validation_tab, text='Lemmatize simplex values')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.labels_x_coordinate, valid_y,
                                   lemmatize_lb, True)

lemmatize_var = tk.IntVar()
lemmatize_checkbox = tk.Checkbutton(validation_tab, text='Run lemmatization', variable=lemmatize_var, onvalue=1, offvalue=0)
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.open_TIPS_x_coordinate, valid_y,
                                   lemmatize_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Lemmatize text simplex values using Stanza.\n"
                                   "Reduces inflected forms to base forms (e.g., 'went' → 'go', 'colpirono' → 'colpire').\n\n"
                                   "Select which simplex types contain nouns and which contain verbs\n"
                                   "from the two lists below (populated from your database).\n\n"
                                   "Produces a review CSV — review before applying.")

# Language selection — all languages supported by Stanza
_stanza_languages = Stanza_util.list_all_languages()
lemmatize_lang_var = tk.StringVar()
lemmatize_lang_var.set('English')
lemmatize_lang_menu = ttk.Combobox(validation_tab, textvariable=lemmatize_lang_var, width=20,
                                    values=_stanza_languages, state='disabled')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.open_TIPS_x_coordinate + 200, valid_y,
                                   lemmatize_lang_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 200,
                                   "Select the language for Stanza lemmatization.\n"
                                   "All languages supported by Stanza are listed.")
lemmatize_lang_menu.bind('<<ComboboxSelected>>', _combobox_release_focus)

def _apply_lemmatization_corrections(csv_path=None):
    """Apply accepted lemmatization corrections from the CSV back to data_SimplexText."""
    inputDir_val = inputDir.get() if hasattr(inputDir, 'get') else inputDir
    if not csv_path:
        outputDir_val = outputDir.get() if hasattr(outputDir, 'get') else outputDir
        csv_path = filedialog.askopenfilename(
            title='Select the reviewed lemmatization CSV',
            initialdir=outputDir_val if outputDir_val else inputDir_val,
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')])
        if not csv_path:
            return
    proceed = file_filename_util.backup_files('', inputDir_val, 'Apply lemmatization corrections', fileType='.xlsx')
    if not proceed:
        return
    n_applied = DB_PCACE_data_analysis_util.apply_lemmatization_corrections(csv_path, inputDir_val)
    if n_applied > 0:
        mb.showinfo(title='Lemmatization applied',
                    message=f'Added Lemma column for {n_applied} row(s) in data_SimplexText.\n\n'
                            f'Original values are preserved. The xlsx and pkl files have been updated.')
    elif n_applied == 0:
        mb.showinfo(title='No changes',
                    message='No lemmatization corrections were applied.\n\n'
                            'Either all rows were marked Accept? = N, or the original values '
                            'were not found in data_SimplexText.')
    else:
        mb.showerror(title='Error',
                     message='An error occurred while applying lemmatization.\nCheck the console output for details.')


# ── Noun simplex types (combobox + add) ──────────────────────────────────────

_noun_simplex_list = []

lemmatize_nouns_lb = tk.Label(validation_tab, text='Simplex types to lemmatize as NOUNS')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.labels_x_indented_coordinate, valid_y,
                                   lemmatize_nouns_lb, True)

lemmatize_nouns_var = tk.StringVar()
lemmatize_nouns_menu = ttk.Combobox(validation_tab, textvariable=lemmatize_nouns_var, width=30, state='disabled')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.open_TIPS_x_coordinate, valid_y,
                                   lemmatize_nouns_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Select a simplex type that contains NOUN values, then click + to add it.\n\n"
                                   "Examples: Name of individual actor, Name of collective actor,\n"
                                   "Physical objects, Role in organizations, Nome attore, etc.\n\n"
                                   "Stanza will apply NOUN lemmatization to values from these simplexes.")
lemmatize_nouns_menu.bind('<<ComboboxSelected>>', _combobox_release_focus)

def _update_noun_hover():
    """Update hover-overs for the NOUN combobox and + button to show current selections."""
    if _noun_simplex_list:
        selected = '\n\nSelected NOUN simplexes:\n  ' + '\n  '.join(_noun_simplex_list)
        btn_tip = 'Click + to add another NOUN simplex.' + selected
    else:
        selected = ''
        btn_tip = 'Click + to add the selected simplex type to the NOUN lemmatization list.'
    combo_tip = ("Select a simplex type that contains NOUN values, then click + to add it.\n\n"
                 "Examples: Name of individual actor, Name of collective actor,\n"
                 "Physical objects, Role in organizations, Nome attore, etc.\n\n"
                 "Stanza will apply NOUN lemmatization to values from these simplexes." + selected)
    y_pos = GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step * _noun_btn_y
    add_noun_button.bind('<Enter>',
        lambda e, t=btn_tip: (e.widget.config(background='red', foreground='black'),
                          GUI_IO_util.display_widget_info(validation_tab, e,
                              GUI_IO_util.open_TIPS_x_coordinate + 280, y_pos - 20,
                              GUI_IO_util.open_TIPS_x_coordinate + 280, t)))
    lemmatize_nouns_menu.bind('<Enter>',
        lambda e, t=combo_tip: GUI_IO_util.display_widget_info(validation_tab, e,
            GUI_IO_util.open_TIPS_x_coordinate, y_pos - 20,
            GUI_IO_util.open_TIPS_x_coordinate, t))

def _add_noun_simplex():
    val = lemmatize_nouns_var.get()
    if val and val not in _noun_simplex_list:
        _noun_simplex_list.append(val)
    _update_noun_hover()
    lemmatize_nouns_menu.event_generate('<Button-1>')

def _reset_noun_simplexes():
    _noun_simplex_list.clear()
    lemmatize_nouns_var.set('')
    _update_noun_hover()

add_noun_button = tk.Button(validation_tab, text='+', width=GUI_IO_util.add_button_width, height=1, state='disabled', command=_add_noun_simplex)
_noun_btn_y = valid_y
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.open_TIPS_x_coordinate + 230, valid_y,
                                   add_noun_button,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 280,
                                   "Click + to add the selected simplex type to the NOUN lemmatization list.")

reset_noun_button = tk.Button(validation_tab, text='Reset', width=GUI_IO_util.reset_button_width, height=1, state='disabled', command=_reset_noun_simplexes)
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.open_TIPS_x_coordinate + 270, valid_y,
                                   reset_noun_button,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 320,
                                   "Click Reset to clear the NOUN simplex list and start fresh.")

# ── Verb simplex types (combobox + add) ──────────────────────────────────────

_verb_simplex_list = []

lemmatize_verbs_lb = tk.Label(validation_tab, text='as VERBS')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.open_TIPS_x_coordinate + 380, valid_y,
                                   lemmatize_verbs_lb, True)

lemmatize_verbs_var = tk.StringVar()
lemmatize_verbs_menu = ttk.Combobox(validation_tab, textvariable=lemmatize_verbs_var, width=30, state='disabled')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.open_TIPS_x_coordinate + 450, valid_y,
                                   lemmatize_verbs_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 470,
                                   "Select a simplex type that contains VERB values, then click + to add it.\n\n"
                                   "Examples: Verbal phrase, Nominalization, Frase verbale, etc.\n\n"
                                   "Stanza will apply VERB lemmatization to values from these simplexes.")
lemmatize_verbs_menu.bind('<<ComboboxSelected>>', _combobox_release_focus)

def _update_verb_hover():
    """Update hover-overs for the VERB combobox and + button to show current selections."""
    if _verb_simplex_list:
        selected = '\n\nSelected VERB simplexes:\n  ' + '\n  '.join(_verb_simplex_list)
        btn_tip = 'Click + to add another VERB simplex.' + selected
    else:
        selected = ''
        btn_tip = 'Click + to add the selected simplex type to the VERB lemmatization list.'
    combo_tip = ("Select a simplex type that contains VERB values, then click + to add it.\n\n"
                 "Examples: Verbal phrase, Nominalization, Frase verbale, etc.\n\n"
                 "Stanza will apply VERB lemmatization to values from these simplexes." + selected)
    y_pos = GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step * _verb_btn_y
    add_verb_button.bind('<Enter>',
        lambda e, t=btn_tip: (e.widget.config(background='red', foreground='black'),
                          GUI_IO_util.display_widget_info(validation_tab, e,
                              GUI_IO_util.open_TIPS_x_coordinate + 700, y_pos - 20,
                              GUI_IO_util.open_TIPS_x_coordinate + 700, t)))
    lemmatize_verbs_menu.bind('<Enter>',
        lambda e, t=combo_tip: GUI_IO_util.display_widget_info(validation_tab, e,
            GUI_IO_util.open_TIPS_x_coordinate + 470, y_pos - 20,
            GUI_IO_util.open_TIPS_x_coordinate + 470, t))

def _add_verb_simplex():
    val = lemmatize_verbs_var.get()
    if val and val not in _verb_simplex_list:
        _verb_simplex_list.append(val)
    _update_verb_hover()
    lemmatize_verbs_menu.event_generate('<Button-1>')

def _reset_verb_simplexes():
    _verb_simplex_list.clear()
    lemmatize_verbs_var.set('')
    _update_verb_hover()

add_verb_button = tk.Button(validation_tab, text='+', width=GUI_IO_util.add_button_width, height=1, state='disabled', command=_add_verb_simplex)
_verb_btn_y = valid_y
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.close_button_x_coordinate, valid_y,
                                   add_verb_button,
                                   True, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Click + to add the selected simplex type to the VERB lemmatization list.")

reset_verb_button = tk.Button(validation_tab, text='Reset', width=GUI_IO_util.reset_button_width, height=1, state='disabled', command=_reset_verb_simplexes)

# Enable/disable NOUN/VERB widgets based on Run lemmatization checkbox
def _toggle_lemmatize_widgets(*args):
    if lemmatize_var.get() == 1:
        lemmatize_nouns_menu.configure(state='readonly')
        add_noun_button.configure(state='normal')
        reset_noun_button.configure(state='normal')
        lemmatize_verbs_menu.configure(state='readonly')
        add_verb_button.configure(state='normal')
        reset_verb_button.configure(state='normal')
        lemmatize_lang_menu.configure(state='readonly')
    else:
        lemmatize_nouns_menu.configure(state='disabled')
        add_noun_button.configure(state='disabled')
        reset_noun_button.configure(state='disabled')
        lemmatize_verbs_menu.configure(state='disabled')
        add_verb_button.configure(state='disabled')
        reset_verb_button.configure(state='disabled')
        lemmatize_lang_menu.configure(state='disabled')

lemmatize_var.trace('w', _toggle_lemmatize_widgets)
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.close_button_x_coordinate + 35, valid_y,
                                   reset_verb_button,
                                   False, False, True, False, 90, GUI_IO_util.run_button_x_coordinate,
                                   "Click Reset to clear the VERB simplex list and start fresh.")

# ══════════════════════════════════════════════════════════════════════════════
# ── Aggregate code validation ─────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

agg_lb = tk.Label(validation_tab, text='Aggregate code validation')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.labels_x_coordinate, valid_y,
                                   agg_lb, True)

# ── Multi-DB directory list ───────────────────────────────────────────────────
_agg_db_dirs = []  # list of selected DB directories

def _add_db_dir():
    """Add a PC-ACE database directory to the comparison list."""
    d = filedialog.askdirectory(title='Select a PC-ACE database directory')
    if d and os.path.isdir(d):
        if d not in _agg_db_dirs:
            _agg_db_dirs.append(d)
            _refresh_db_listbox()

def _remove_db_dir():
    """Remove the selected directory from the comparison list."""
    sel = agg_db_var.get()
    if sel:
        for i, d in enumerate(_agg_db_dirs):
            if os.path.basename(d) == sel:
                _agg_db_dirs.pop(i)
                break
        _refresh_db_listbox()

def _refresh_db_listbox():
    names = [os.path.basename(d) for d in _agg_db_dirs]
    agg_db_menu['values'] = names
    if names:
        agg_db_var.set(names[-1])
    else:
        agg_db_var.set('')

agg_db_var = tk.StringVar()
agg_db_menu = ttk.Combobox(validation_tab, textvariable=agg_db_var, width=80, state='readonly')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.open_TIPS_x_coordinate, valid_y,
                                   agg_db_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "List of PC-ACE database directories to compare.\n"
                                   "Use + to add directories, − to remove.\n"
                                   "The INPUT directory (if set) is automatically included.")
agg_db_menu.bind('<<ComboboxSelected>>', _combobox_release_focus)

_init_input = GUI_util.input_main_dir_path.get() if hasattr(GUI_util.input_main_dir_path, 'get') else GUI_util.input_main_dir_path
if _init_input and os.path.isdir(str(_init_input)) and os.path.isfile(os.path.join(str(_init_input), 'data_Complex.xlsx')):
    _agg_db_dirs.append(str(_init_input))
    _refresh_db_listbox()

add_db_button = tk.Button(validation_tab, text='+', width=2, command=_add_db_dir)
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.close_button_x_coordinate, valid_y,
                                   add_db_button,
                                   True, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Click + to add a PC-ACE database directory for cross-DB comparison.\n"
                                   "Add 2 or more databases to compare aggregate codes across them.")

remove_db_button = tk.Button(validation_tab, text='−', width=2, command=_remove_db_dir)
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.close_button_x_coordinate + 35, valid_y,
                                   remove_db_button,
                                   False, False, True, False, 90, GUI_IO_util.run_button_x_coordinate,
                                   "Remove the selected database from the list.")

# ── Comparison controls ──────────────────────────────────────────────────────

_AGG_MODE_NONE = ''
_AGG_MODE_CROSS_DB = 'Cross-DB code comparison'
_AGG_MODE_SIDE_BY_SIDE = 'Side-by-side code mapping'
_AGG_MODE_BOTH = '*'

agg_mode_var = tk.StringVar()
agg_mode_menu = ttk.Combobox(validation_tab, textvariable=agg_mode_var, width=25, state='readonly',
                              values=[_AGG_MODE_BOTH, _AGG_MODE_CROSS_DB, _AGG_MODE_SIDE_BY_SIDE])
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.labels_x_indented_coordinate, valid_y,
                                   agg_mode_menu,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Select the aggregate code validation task:\n\n"
                                   "  * = run BOTH Cross-DB comparison AND Side-by-side mapping\n\n"
                                   "  Cross-DB code comparison: compares aggregate code vocabularies\n"
                                   "    across all databases in the list. Requires 2+ databases.\n"
                                   "    Produces a full comparison CSV and a gaps report.\n\n"
                                   "  Side-by-side code mapping: for each complex instance, shows\n"
                                   "    original values alongside aggregate codes.")

def _on_agg_mode_change(*args):
    mode = agg_mode_var.get()
    if mode in (_AGG_MODE_CROSS_DB, _AGG_MODE_BOTH) and len(_agg_db_dirs) < 2:
        mb.showwarning(title='Cross-DB comparison',
                       message='Cross-DB comparison requires at least 2 databases.\n\n'
                               'Use the + / − buttons above to add more PC-ACE database directories.')

agg_mode_var.trace('w', _on_agg_mode_change)

agg_mode_menu.bind('<<ComboboxSelected>>', _combobox_release_focus)

# ── Original simplex + Aggregate code simplexes (same row as checkboxes) ────

agg_orig_var = tk.StringVar()
agg_orig_menu = ttk.Combobox(validation_tab, textvariable=agg_orig_var, width=30, state='readonly')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.open_TIPS_x_coordinate, valid_y,
                                   agg_orig_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "ORIGINAL VALUES: select the simplex containing the original (non-aggregated) values.\n\n"
                                   "This is the simplex whose values were coded into aggregate categories.\n"
                                   "e.g., 'Name of individual actor', 'Verbal phrase', 'Nome attore'.")

agg_orig_menu.bind('<<ComboboxSelected>>', _combobox_release_focus)

_agg_simplex_list = []

agg_simplex_var = tk.StringVar()
agg_simplex_menu = ttk.Combobox(validation_tab, textvariable=agg_simplex_var, width=30, state='readonly')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.open_TIPS_x_coordinate + 230, valid_y,
                                   agg_simplex_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 230,
                                   "AGGREGATE CODES: select an aggregate code simplex, then click + to add it.\n"
                                   "You can add multiple aggregate code simplexes.\n"
                                   "Use Reset to clear the list and start over.")

agg_simplex_menu.bind('<<ComboboxSelected>>', _combobox_release_focus)

def _add_agg_simplex():
    sel = agg_simplex_var.get()
    if sel and sel not in _agg_simplex_list:
        _agg_simplex_list.append(sel)
        _refresh_agg_simplex_display()
    agg_simplex_menu.event_generate('<Button-1>')

def _reset_agg_simplex():
    _agg_simplex_list.clear()
    agg_simplex_var.set('')
    _refresh_agg_simplex_display()

def _refresh_agg_simplex_display():
    if _agg_simplex_list:
        agg_simplex_selected_var.set(f'{len(_agg_simplex_list)} selected: ' + ', '.join(_agg_simplex_list))
        tip = f'{len(_agg_simplex_list)} selected aggregate code simplexes:\n\n  ' + \
              '\n  '.join(_agg_simplex_list)
    else:
        agg_simplex_selected_var.set('')
        tip = 'No aggregate code simplexes selected yet.'
    agg_simplex_selected_label.unbind('<Enter>')
    agg_simplex_selected_label.bind('<Enter>',
        lambda e, t=tip: GUI_IO_util.display_widget_info(validation_tab, e,
            GUI_IO_util.labels_x_indented_coordinate,
            agg_simplex_selected_label.winfo_y() - 20,
            GUI_IO_util.labels_x_indented_coordinate, t))

agg_add_button = tk.Button(validation_tab, text='+', width=2, command=_add_agg_simplex)
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.close_button_x_coordinate, valid_y,
                                   agg_add_button,
                                   True, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Click + to add the selected aggregate code simplex to the list.")

agg_reset_button = tk.Button(validation_tab, text='Reset', width=5, command=_reset_agg_simplex)
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.close_button_x_coordinate+35, valid_y,
                                   agg_reset_button,
                                   False, False, True, False, 90, GUI_IO_util.run_button_x_coordinate,
                                   "Clear the aggregate code list and start fresh.")

agg_simplex_selected_var = tk.StringVar()
_entry_width = (GUI_IO_util.close_button_x_coordinate + 80 - GUI_IO_util.labels_x_indented_coordinate) * 2 // 11
_entry_width = 165
agg_simplex_selected_label = tk.Entry(validation_tab, textvariable=agg_simplex_selected_var, width=_entry_width, state='readonly')
valid_y = GUI_IO_util.placeWidget(validation_tab, GUI_IO_util.labels_x_indented_coordinate, valid_y,
                                   agg_simplex_selected_label,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Shows the aggregate code simplexes you have selected.\n"
                                   "Hover over for the full list.")


# ── Apply aggregate corrections ─────────────────────────────────────────────

_original_side_by_side_csv = [None]

def _apply_aggregate_corrections():
    """Read the CSV from the file widget, diff against original, write corrections back."""
    edited_path = csv_file_var.get()
    if not edited_path or not os.path.isfile(edited_path):
        mb.showwarning(title='Apply corrections',
                       message='No CSV file selected.\n\n'
                               'Run side-by-side mapping first, edit the output CSV,\n'
                               'then click this button.')
        return
    inputDir_val = inputDir.get() if hasattr(inputDir, 'get') else inputDir
    if not inputDir_val or not os.path.isdir(inputDir_val):
        mb.showwarning(title='Apply corrections',
                       message='Please select a PC-ACE database directory first.')
        return
    if not _ensure_database_loaded(inputDir_val):
        mb.showwarning(title='Apply corrections',
                       message='Could not load the PC-ACE database.')
        return
    proceed = file_filename_util.backup_files('', inputDir_val, 'Apply aggregate corrections', fileType='.xlsx')
    if not proceed:
        return
    GUI_util.window.config(cursor='watch')
    GUI_util.window.update()
    try:
        n_applied = DB_PCACE_data_analysis_util.apply_aggregate_corrections(
            edited_path, inputDir_val,
            original_csv_path=_original_side_by_side_csv[0])
        if n_applied > 0:
            mb.showinfo(title='Corrections applied',
                        message=f'Applied {n_applied} aggregate code correction(s).\n\n'
                                f'The xlsx and pkl files have been updated.\n'
                                f'Cached xref data has been cleared and will rebuild on next run.')
        elif n_applied == 0:
            mb.showinfo(title='No changes',
                        message='No changes detected between the edited CSV and the original values.')
        else:
            mb.showerror(title='Error',
                         message='An error occurred. Check the console output for details.')
    except Exception as e:
        mb.showerror(title='Apply corrections error', message=f'Failed:\n\n{e}')
    finally:
        GUI_util.window.config(cursor='')



# ── Enable/disable all widgets based on DB state ────────────────────────────

def _set_all_widgets_state(state):
    """Enable or disable all validation widgets. state='normal' or 'disabled'."""
    combo_state = 'readonly' if state == 'normal' else 'disabled'
    for w in [spell_check_checkbox,
              lemmatize_checkbox,
              agg_mode_menu, agg_orig_menu, agg_simplex_menu,
              agg_add_button, agg_reset_button,
              add_db_button, remove_db_button,
              csv_file_button]:
        try:
            w.configure(state=state)
        except Exception:
            pass
    for w in [spell_check_simplex_menu, agg_db_menu]:
        try:
            w.configure(state=combo_state)
        except Exception:
            pass

_set_all_widgets_state('disabled')

# ── Populate simplex dropdown when database directory changes ─────────────────

def _on_inputDir_change(*args):
    """When the input directory changes, populate the simplex dropdown."""
    global _database_loaded
    _database_loaded = False
    dir_val = inputDir.get() if hasattr(inputDir, 'get') else inputDir
    if not dir_val or not os.path.isdir(dir_val):
        _set_all_widgets_state('disabled')
        spell_check_simplex_menu['values'] = ['ALL text simplexes']
        spell_check_simplex_var.set('ALL text simplexes')
        return
    if not os.path.isfile(os.path.join(dir_val, 'data_Complex.xlsx')):
        _set_all_widgets_state('disabled')
        return
    _set_all_widgets_state('normal')
    if _ensure_database_loaded(dir_val):
        try:
            simplex_names = DB_PCACE_data_analysis_util.get_all_simplex_names()
            text_names = []
            for sn in simplex_names:
                vt = DB_PCACE_data_analysis_util.get_simplex_value_type(sn)
                if vt == 1:
                    text_names.append(sn)
            sorted_text = sorted(text_names)
            spell_check_simplex_menu['values'] = ['ALL text simplexes'] + sorted_text
            # Populate noun and verb comboboxes with all text simplex names
            lemmatize_nouns_menu['values'] = sorted_text
            lemmatize_verbs_menu['values'] = sorted_text
            # Auto-add likely noun/verb simplexes to the backing lists
            _noun_keywords = ['name', 'nome', 'individual', 'individuo', 'collective', 'collettivo',
                              'organization', 'organizzazione', 'institution', 'istituzione',
                              'physical', 'fisico', 'object', 'oggetto', 'role', 'ruolo',
                              'actor', 'attore', 'city', 'città', 'location', 'luogo',
                              'reason', 'ragione', 'occupation', 'occupazione']
            _verb_keywords = ['verbal', 'verbale', 'phrase', 'frase', 'process', 'processo',
                              'nominalization', 'nominalizzazione', 'action', 'azione']
            _noun_simplex_list.clear()
            _verb_simplex_list.clear()
            for sn in sorted_text:
                sn_lower = sn.lower()
                if any(kw in sn_lower for kw in _noun_keywords):
                    _noun_simplex_list.append(sn)
                if any(kw in sn_lower for kw in _verb_keywords):
                    _verb_simplex_list.append(sn)
            _agg_db_dirs.clear()
            _agg_db_dirs.append(dir_val)
            _refresh_db_listbox()
            all_sorted = sorted(simplex_names)
            agg_orig_menu['values'] = all_sorted
            agg_simplex_menu['values'] = all_sorted
            agg_orig_var.set('')
            _agg_simplex_list.clear()
            _refresh_agg_simplex_display()
        except Exception as e:
            print(f"  Could not populate simplex dropdown: {e}")
            spell_check_simplex_menu['values'] = ['ALL text simplexes']

if hasattr(inputDir, 'trace'):
    inputDir.trace('w', _on_inputDir_change)
try:
    _set_all_widgets_state('normal')
except Exception:
    pass

# This GUI is grid-opted-out (see GUI_IO_util.GRID_OPT_OUT): the whole thing -- shell + tabs -- uses
# .place, so GUI_bottom does NOT finalize a grid (which reflowed RUN/CLOSE off-screen on the I/O-setup
# refresh). Keep grid disabled and restore the shell's row for the .place bottom bar.
GUI_IO_util.grid_layout_enabled = False
y_multiplier_integer = _shell_y_multiplier

# change the value of the readMe_message
readMe_message="The Python 3 scripts convert, via the Python Pandas package, and analyze, via various visualization packages, data collected via the Microsoft ACCESS PC-ACE (Program for Computer-Assisted Coding of Events).\nIn INPUT the algorithms expect a set of xlsx files in the input directory. The xlsx files must be exported from the PC-ACE database tables data, setup, and utility (see TIPS file on how to export tables from PC-ACE).\n\nIn OUTPUT the algorithms produce a set of csv files and different types of visuals, from Excel charts to network graphs via Gephi and Sankey, geographic pin maps via Google Earth Pro and heat maps via Google Maps, word clouds, and interactive time maps."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
# ? HELP for the output-options row (Open output files / chart / transformation / data tools). GUI_bottom
# renders that row at this y_multiplier and places no ? HELP itself; the tabbed's own help_buttons() column
# was dropped, so add this one explicitly. Return value discarded so GUI_bottom keeps the same row.
GUI_IO_util.place_help_button(window, GUI_IO_util.help_button_x_coordinate, y_multiplier_integer,
                              "NLP Suite Help", GUI_IO_util.msg_openOutputFiles)
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
#     primary_complex_menu = DB_PCACE_data_analysis_util.build_macro_event_dropdown_menu(inputDir.get())
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
                GUI_util.config_input_output_alphabetic_options[1][1] = _dir
        except (IndexError, ValueError):
            pass
    if '--outputdir' in sys.argv:
        try:
            idx = sys.argv.index('--outputdir')
            _dir = sys.argv[idx + 1]
            if os.path.isdir(_dir):
                GUI_util.output_dir_path.set(_dir)
                GUI_util.config_input_output_alphabetic_options[3][1] = _dir
        except (IndexError, ValueError):
            pass
    _refresh_io_display()

def _refresh_io_display():
    in_dir = GUI_util.input_main_dir_path.get()
    out_dir = GUI_util.output_dir_path.get()
    display = "INPUT DIR: " + os.path.basename(os.path.normpath(in_dir)) if in_dir else "INPUT DIR:"
    display += "\nOUTPUT DIR: " + os.path.basename(out_dir) if out_dir else "\nOUTPUT DIR:"
    try:
        GUI_util.update_display_area(display, GUI_util.IO_setup_brief_display_area)
    except Exception:
        pass

GUI_util.window.after(200, _apply_cli_dirs)

GUI_util.window.mainloop()

