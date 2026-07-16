# DB_PCACE_data_validation_main.py
# Data validation and cleaning GUI for PC-ACE simplex values and aggregate codes.

import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,
        "DB_PCACE_data_validation_main.py",
        ['os', 'tkinter', 'pandas'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.filedialog as filedialog
import pandas as pd
import subprocess

import IO_csv_util
import IO_files_util
import GUI_IO_util
import IO_user_interface_util
import TIPS_util
import DB_PCACE_data_analysis_util
import statistics_csv_util
import Stanza_util
import file_filename_util

# Track whether the database has been loaded
_database_loaded = False

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

def run():
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

GUI_label = 'Graphical User Interface (GUI) for PC-ACE Data Validation & Cleaning'
head, scriptName = os.path.split(os.path.basename(__file__))

# hardcode the default config at module init: config_filename_selected_config is empty this early,
# which would make the startup I/O check falsely report the INPUT/OUTPUT fields as missing
config_filename = 'NLP_default_IO_config.csv'

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
config_input_output_numeric_options = [0, 1, 0, 1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window = GUI_util.window
config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename
inputDir = GUI_util.input_main_dir_path
outputDir = GUI_util.output_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

# ── Open GUI dropdown (same pattern as DB_SQL_main) ─────────────────────────

def _open_sql_gui():
    """Launch the DB SQL GUI."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DB_SQL_main.py')
    cmd = [sys.executable, script_path]
    # hand over OUR I/O config: it is what DB_SQL renders its INPUT/OUTPUT DIR box from, so passing the
    # dirs alone would open it DISPLAYING the default config while operating on ours.
    if GUI_util.config_filename_selected_config.get():
        cmd.extend(['--config', GUI_util.config_filename_selected_config.get()])
    in_dir = inputDir.get() if hasattr(inputDir, 'get') else inputDir
    if in_dir:
        cmd.extend(['--inputdir', in_dir])
    out_dir = outputDir.get() if hasattr(outputDir, 'get') else outputDir
    if out_dir:
        cmd.extend(['--outputdir', out_dir])
    subprocess.Popen(cmd)

def _open_pcace_analyzer():
    """Launch the PC-ACE data analysis GUI."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DB_PCACE_data_analysis_main.py')
    cmd = [sys.executable, script_path]
    in_dir = inputDir.get() if hasattr(inputDir, 'get') else inputDir
    if in_dir:
        cmd.extend(['--inputdir', in_dir])
    out_dir = outputDir.get() if hasattr(outputDir, 'get') else outputDir
    if out_dir:
        cmd.extend(['--outputdir', out_dir])
    subprocess.Popen(cmd)

def _open_data_manipulation():
    """Launch the data manipulation GUI."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_manipulation_main.py')
    cmd = [sys.executable, script_path]
    in_dir = inputDir.get() if hasattr(inputDir, 'get') else inputDir
    if in_dir:
        cmd.extend(['--inputdir', in_dir])
    out_dir = outputDir.get() if hasattr(outputDir, 'get') else outputDir
    if out_dir:
        cmd.extend(['--outputdir', out_dir])
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
    out_dir = outputDir.get() if hasattr(outputDir, 'get') else outputDir
    if out_dir:
        cmd.extend(['--outputdir', out_dir])
    subprocess.Popen(cmd)

def _on_open_gui_selected(choice):
    if choice == 'Open DB SQL GUI':
        _open_sql_gui()
    elif choice == 'Open PC-ACE data analysis GUI':
        _open_pcace_analyzer()
    elif choice == 'Open data manipulation GUI':
        _open_data_manipulation()
    elif choice == 'Open data statistics GUI':
        _open_statistics_csv()

_open_gui_var = tk.StringVar()
_open_gui_var.set('Open DB SQL GUI')
open_gui_menu = tk.OptionMenu(window, _open_gui_var,
                              'Open DB SQL GUI',
                              'Open PC-ACE data analysis GUI',
                              'Open data manipulation GUI',
                              'Open data statistics GUI',
                              command=_on_open_gui_selected)
open_gui_menu.configure(width=25)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_gui_menu,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to open a related GUI.\n\n"
                                   "   Open DB SQL GUI: opens the SQL query GUI.\n"
                                   "   Open PC-ACE data analysis GUI: opens the PC-ACE data analysis.\n"
                                   "   Open data manipulation GUI: opens the data manipulation GUI.\n"
                                   "   Open data statistics GUI: open the GUI for statistical analyses.")

# ── Select INPUT CSV file row ───────────────────────────────────────────────

csv_file_var = tk.StringVar()

def get_csv_file(window, title, fileType, annotate):
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

csv_file_button = tk.Button(window, width=GUI_IO_util.select_file_directory_button_width,
                            text='Select INPUT CSV file',
                            command=lambda: get_csv_file(window, 'Select INPUT csv file', [("csv files", "*.csv")], True))
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               csv_file_button, True)

# Button to open the selected CSV file
openInputFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                 command=lambda: IO_files_util.openFile(window, csv_file_var.get()))
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               openInputFile_button,
                                               True, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                               "Open INPUT csv file")

# CSV file path entry
# GUI_IO_util.csv_file_width - 8
csv_file_entry = tk.Entry(window, width=115, textvariable=csv_file_var)
csv_file_entry.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                                               csv_file_entry, True)

# Clear button
def _clear_csv_file():
    csv_file_var.set('')

clear_csv_button = tk.Button(window, text='Clear', width=5, command=lambda: _clear_csv_file())
clear_csv_button.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu+GUI_IO_util.open_file_button_brief, y_multiplier_integer,
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

apply_changes_button = tk.Button(window, text='Apply changes', width=12, command=_apply_changes)
apply_changes_button.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu+GUI_IO_util.open_file_button_brief+60, y_multiplier_integer,
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

spell_check_lb = tk.Label(window, text='Spell-check simplex values')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   spell_check_lb, True)

spell_check_var = tk.IntVar()
spell_check_checkbox = tk.Checkbutton(window, text='Run spell-check', variable=spell_check_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
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
spell_check_simplex_menu = ttk.Combobox(window, textvariable=spell_check_simplex_var, width=30, state='readonly')
spell_check_simplex_menu['values'] = ['ALL text simplexes']
spell_check_simplex_menu.bind('<<ComboboxSelected>>', _combobox_release_focus)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 200, y_multiplier_integer,
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

lemmatize_lb = tk.Label(window, text='Lemmatize simplex values')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   lemmatize_lb, True)

lemmatize_var = tk.IntVar()
lemmatize_checkbox = tk.Checkbutton(window, text='Run lemmatization', variable=lemmatize_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
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
lemmatize_lang_menu = ttk.Combobox(window, textvariable=lemmatize_lang_var, width=20,
                                    values=_stanza_languages, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 200, y_multiplier_integer,
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

lemmatize_nouns_lb = tk.Label(window, text='Simplex types to lemmatize as NOUNS')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   lemmatize_nouns_lb, True)

lemmatize_nouns_var = tk.StringVar()
lemmatize_nouns_menu = ttk.Combobox(window, textvariable=lemmatize_nouns_var, width=30, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
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
                          GUI_IO_util.display_widget_info(window, e,
                              GUI_IO_util.open_TIPS_x_coordinate + 280, y_pos - 20,
                              GUI_IO_util.open_TIPS_x_coordinate + 280, t)))
    lemmatize_nouns_menu.bind('<Enter>',
        lambda e, t=combo_tip: GUI_IO_util.display_widget_info(window, e,
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

add_noun_button = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1, state='disabled', command=_add_noun_simplex)
_noun_btn_y = y_multiplier_integer
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 230, y_multiplier_integer,
                                   add_noun_button,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 280,
                                   "Click + to add the selected simplex type to the NOUN lemmatization list.")

reset_noun_button = tk.Button(window, text='Reset', width=GUI_IO_util.reset_button_width, height=1, state='disabled', command=_reset_noun_simplexes)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 270, y_multiplier_integer,
                                   reset_noun_button,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 320,
                                   "Click Reset to clear the NOUN simplex list and start fresh.")

# ── Verb simplex types (combobox + add) ──────────────────────────────────────

_verb_simplex_list = []

lemmatize_verbs_lb = tk.Label(window, text='as VERBS')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 380, y_multiplier_integer,
                                   lemmatize_verbs_lb, True)

lemmatize_verbs_var = tk.StringVar()
lemmatize_verbs_menu = ttk.Combobox(window, textvariable=lemmatize_verbs_var, width=30, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 450, y_multiplier_integer,
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
                          GUI_IO_util.display_widget_info(window, e,
                              GUI_IO_util.open_TIPS_x_coordinate + 700, y_pos - 20,
                              GUI_IO_util.open_TIPS_x_coordinate + 700, t)))
    lemmatize_verbs_menu.bind('<Enter>',
        lambda e, t=combo_tip: GUI_IO_util.display_widget_info(window, e,
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

add_verb_button = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1, state='disabled', command=_add_verb_simplex)
_verb_btn_y = y_multiplier_integer
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.close_button_x_coordinate, y_multiplier_integer,
                                   add_verb_button,
                                   True, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Click + to add the selected simplex type to the VERB lemmatization list.")

reset_verb_button = tk.Button(window, text='Reset', width=GUI_IO_util.reset_button_width, height=1, state='disabled', command=_reset_verb_simplexes)

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
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.close_button_x_coordinate + 35, y_multiplier_integer,
                                   reset_verb_button,
                                   False, False, True, False, 90, GUI_IO_util.run_button_x_coordinate,
                                   "Click Reset to clear the VERB simplex list and start fresh.")

# ══════════════════════════════════════════════════════════════════════════════
# ── Aggregate code validation ─────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

agg_lb = tk.Label(window, text='Aggregate code validation')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
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
agg_db_menu = ttk.Combobox(window, textvariable=agg_db_var, width=80, state='readonly')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
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

add_db_button = tk.Button(window, text='+', width=2, command=_add_db_dir)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.close_button_x_coordinate, y_multiplier_integer,
                                   add_db_button,
                                   True, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Click + to add a PC-ACE database directory for cross-DB comparison.\n"
                                   "Add 2 or more databases to compare aggregate codes across them.")

remove_db_button = tk.Button(window, text='−', width=2, command=_remove_db_dir)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.close_button_x_coordinate + 35, y_multiplier_integer,
                                   remove_db_button,
                                   False, False, True, False, 90, GUI_IO_util.run_button_x_coordinate,
                                   "Remove the selected database from the list.")

# ── Comparison controls ──────────────────────────────────────────────────────

_AGG_MODE_NONE = ''
_AGG_MODE_CROSS_DB = 'Cross-DB code comparison'
_AGG_MODE_SIDE_BY_SIDE = 'Side-by-side code mapping'
_AGG_MODE_BOTH = '*'

agg_mode_var = tk.StringVar()
agg_mode_menu = ttk.Combobox(window, textvariable=agg_mode_var, width=25, state='readonly',
                              values=[_AGG_MODE_BOTH, _AGG_MODE_CROSS_DB, _AGG_MODE_SIDE_BY_SIDE])
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
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
agg_orig_menu = ttk.Combobox(window, textvariable=agg_orig_var, width=30, state='readonly')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                   agg_orig_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "ORIGINAL VALUES: select the simplex containing the original (non-aggregated) values.\n\n"
                                   "This is the simplex whose values were coded into aggregate categories.\n"
                                   "e.g., 'Name of individual actor', 'Verbal phrase', 'Nome attore'.")

agg_orig_menu.bind('<<ComboboxSelected>>', _combobox_release_focus)

_agg_simplex_list = []

agg_simplex_var = tk.StringVar()
agg_simplex_menu = ttk.Combobox(window, textvariable=agg_simplex_var, width=30, state='readonly')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 230, y_multiplier_integer,
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
        lambda e, t=tip: GUI_IO_util.display_widget_info(window, e,
            GUI_IO_util.labels_x_indented_coordinate,
            agg_simplex_selected_label.winfo_y() - 20,
            GUI_IO_util.labels_x_indented_coordinate, t))

agg_add_button = tk.Button(window, text='+', width=2, command=_add_agg_simplex)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.close_button_x_coordinate, y_multiplier_integer,
                                   agg_add_button,
                                   True, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Click + to add the selected aggregate code simplex to the list.")

agg_reset_button = tk.Button(window, text='Reset', width=5, command=_reset_agg_simplex)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.close_button_x_coordinate+35, y_multiplier_integer,
                                   agg_reset_button,
                                   False, False, True, False, 90, GUI_IO_util.run_button_x_coordinate,
                                   "Clear the aggregate code list and start fresh.")

agg_simplex_selected_var = tk.StringVar()
_entry_width = (GUI_IO_util.close_button_x_coordinate + 80 - GUI_IO_util.labels_x_indented_coordinate) * 2 // 11
_entry_width = 165
agg_simplex_selected_label = tk.Entry(window, textvariable=agg_simplex_selected_var, width=_entry_width, state='readonly')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
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

# ── Help buttons ────────────────────────────────────────────────────────────

def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    # Row: Open GUI dropdown
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "Use the dropdown menu to open a related GUI. Each one opens on the SAME corpus you are working on "
        "here (your INPUT/OUTPUT configuration is passed on to it).\n\n"
        "   Open DB SQL GUI: run SQL queries on your data. The SQLite database is built automatically from "
        "the xlsx/csv tables in your input directory (and rebuilt only when they change), so there is "
        "nothing to export first.\n\n"
        "   Open PC-ACE data analysis GUI: analyze your PC-ACE tables.\n\n"
        "   Open data manipulation GUI: reshape and edit your data.\n\n"
        "   Open data statistics GUI: compute descriptive statistics on a csv file, for instance a query "
        "result saved from the DB SQL GUI." + GUI_IO_util.msg_Esc)

    # Row: Open csv file + Clear + Apply changes
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "The INPUT csv file widget displays a csv filename. There are two ways of entering a filename.\n\n"
                                  "   1. Click on the button 'Select INPUT csv file' to select a file of your choice.\n\n"
                                  "   2. The text widget is filled automatically after running a validation task.\n\n"
                                  "Click the small button between the 'Select...' button and the text widget to open the file.\n\n"
                                  "Click 'Clear' to remove the loaded CSV.\n\n"
                                  "APPLY CHANGES: writes corrections from the loaded CSV back to the PC-ACE database.\n"
                                  "   The button auto-detects the CSV type and applies the appropriate corrections:\n\n"
                                  "   - Spell-check CSV (has 'Suggested correction' column):\n"
                                  "       Overwrites misspelled/duplicate values in data_SimplexText.\n\n"
                                  "   - Lemmatization CSV (has 'Lemmatized form' column):\n"
                                  "       Adds a 'Lemma' column to data_SimplexText (original Value is preserved).\n\n"
                                  "   - Side-by-side mapping CSV (aggregate code corrections):\n"
                                  "       Overwrites aggregate code values in data_SimplexText.\n\n"
                                  "All three modify data_SimplexText.xlsx and data_SimplexText.pkl.\n"
                                  "NLP_data_Simplex_values_ALL.pkl is also invalidated and will rebuild on next run.\n\n"
                                  "A backup of the database files is created before applying any changes." + GUI_IO_util.msg_Esc)

    # Row 2: Spell-check checkbox + simplex dropdown
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "SPELL-CHECK: find near-duplicate and misspelled values in text simplexes.\n\n"
        "Uses difflib.SequenceMatcher, a purely character-based string similarity "
        "algorithm (Ratcliff/Obershelp) that is independent of any specific language.\n\n"
        "  1. Tick the 'Run spell-check' checkbox.\n"
        "  2. Select a specific simplex or leave as 'ALL text simplexes'.\n"
        "  3. Click RUN to produce a review CSV.\n"
        "  4. Review the CSV, edit corrections, set Accept? to N for rows to skip.\n"
        "  5. Click 'Apply changes' to write accepted changes back to the database.\n\n"
        "A BACKUP OF THE ORIGINAL FILES IS RECOMMENDED BEFORE APPLYING." + GUI_IO_util.msg_Esc)

    # # Row 3: Apply corrections button
    # y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
    #     y_multiplier_integer, "NLP Suite Help",
    #     "APPLY CORRECTIONS: apply reviewed spell-check corrections.\n\n"
    #     "Modifies data_SimplexText.xlsx and .pkl in the PC-ACE database directory.\n\n"
    #     "A BACKUP OF THE ORIGINAL FILES IS RECOMMENDED BEFORE APPLYING." + GUI_IO_util.msg_Esc)

    # Row 4: Lemmatize checkbox + language
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "LEMMATIZE: reduce inflected forms to base forms using Stanza.\n\n"
        "  Examples: 'went' → 'go', 'colpirono' → 'colpire', 'cities' → 'city'.\n\n"
        "  Select the language, then assign your database's simplex types\n"
        "  in the NOUNS and VERBS lists below.\n\n"
        "APPLY LEMMATIZATION: adds a 'Lemma' column to data_SimplexText\n"
        "(the original Value column is preserved).\n"
        "Modifies data_SimplexText.xlsx and .pkl; invalidates NLP_data_Simplex_values_ALL.pkl.\n\n"
        "A BACKUP OF THE ORIGINAL FILES IS RECOMMENDED BEFORE APPLYING.\n"
                                                         + GUI_IO_util.msg_Esc)

    # Row 5: Noun/Verb simplex listboxes (taller row due to listbox height=3)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "Select which simplex types contain NOUN vs VERB values.\n\n"
        "  NOUNS list: e.g., Name of individual actor, Physical objects, Nome attore\n"
        "  VERBS list: e.g., Verbal phrase, Nominalization, Frase verbale\n\n"
        "  The lists auto-populate from your database and auto-select likely matches.\n"
        "  Hold Ctrl to select/deselect multiple items.\n" + GUI_IO_util.msg_Esc)

    # Row 6: Aggregate code validation label + DB list
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "AGGREGATE CODE VALIDATION: compare and inspect aggregate codes.\n\n"
        "  Use + / − to add/remove PC-ACE database directories.\n"
        "  The INPUT directory is automatically included." + GUI_IO_util.msg_Esc)

    # Row 7: Cross-DB + Side-by-side + Original values + Aggregate codes + Reset
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "Cross-DB comparison: compares aggregate code vocabularies across databases.\n"
        "  Produces a full comparison CSV and a gaps report. Requires 2+ databases.\n\n"
        "Side-by-side mapping: for each complex instance, shows original values\n"
        "  alongside aggregate codes.\n\n"
        "  1st dropdown (Original values): the simplex with the raw values\n"
        "     e.g., 'Name of individual actor', 'Verbal phrase'\n"
        "  2nd dropdown (Aggregate codes): select aggregate code simplexes with +\n"
        "     e.g., 'Actor aggregate code', 'Action aggregate code NEW'" + GUI_IO_util.msg_Esc)

    # Row 8: Selected aggregate codes display
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "Shows the aggregate code simplexes you have selected.\n"
        "Hover over the text field for the full list." + GUI_IO_util.msg_Esc)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer - 1

y_multiplier_integer = y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,increment)

# increment = GUI_util.y_multiplier_integer
# content_y_multiplier_integer = y_multiplier_integer
# y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, increment)
# y_multiplier_integer = max(y_multiplier_integer, content_y_multiplier_integer)

# ── Videos / TIPS ───────────────────────────────────────────────────────────

videos_lookup = {'No videos available':''}
videos_options = 'No videos available'
TIPS_lookup = {}
TIPS_options = 'No TIPS available'
IO_setup_display_brief = False

readMe_message = ("This GUI provides tools for validating and cleaning PC-ACE data.\n\n"
                  "IN INPUT, select the PC-ACE database directory (containing the Excel/pkl files).\n\n"
                  "SPELL-CHECK: finds near-duplicate and misspelled text values in simplexes\n"
                  "  using difflib.SequenceMatcher (language-independent character similarity).\n"
                  "  Select a specific simplex or check ALL text simplexes.\n"
                  "  Review the output CSV, then apply accepted corrections.\n\n"
                  "LEMMATIZE: reduces inflected forms to base forms using Stanza (English & Italian).\n"
                  "  Select Nouns, Verbs, or both. Review the output CSV, then apply.\n\n"
                  "AGGREGATE CODE VALIDATION:\n"
                  "  Cross-DB comparison: compare aggregate code vocabularies across multiple databases.\n"
                  "  Side-by-side mapping: see how original simplex values map to aggregate codes.")

readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)

GUI_util.run_button.configure(command=run)

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options,
                    y_multiplier_integer, readMe_command,
                    videos_lookup, videos_options,
                    TIPS_lookup, TIPS_options,
                    IO_setup_display_brief, scriptName)

# ── ESC key resets all selections ─────────────────────────────────────────────

def _reset_all(e=None):
    """Clear all selections and restore default dropdown values."""
    spell_check_var.set(0)
    spell_check_simplex_var.set('ALL text simplexes')
    lemmatize_var.set(0)
    lemmatize_lang_var.set('English')
    lemmatize_nouns_var.set('')
    lemmatize_verbs_var.set('')
    _noun_simplex_list.clear()
    _verb_simplex_list.clear()
    agg_mode_var.set('')
    agg_orig_var.set('')
    agg_simplex_var.set('')
    _agg_simplex_list.clear()
    _refresh_agg_simplex_display()
    csv_file_var.set('')

window.bind("<Escape>", _reset_all)

# ── CLI arguments (launched from DB_SQL_main or analyzer dropdown) ────────────

def _apply_cli_args():
    if '--inputfile' in sys.argv:
        try:
            idx = sys.argv.index('--inputfile')
            _file = sys.argv[idx + 1]
            if os.path.isfile(_file):
                GUI_util.inputFilename.set(_file)
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

GUI_util.window.after(200, _apply_cli_args)

GUI_util.window.mainloop()
