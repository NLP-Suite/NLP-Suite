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
import Stanza_util

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

def run(inputFilename, outputDir, openOutputFiles, chartPackage, dataTransformation):

    config_filename = GUI_util.config_filename_selected_config.get()
    inputDir = GUI_util.input_main_dir_path.get()
    filesToOpen = []

    if not inputDir or not os.path.isdir(inputDir):
        mb.showwarning(title='Warning',
                       message='No INPUT directory selected.\n\nPlease, select the PC-ACE database directory and try again.')
        return

    if not _ensure_database_loaded(inputDir):
        mb.showwarning(title='Warning',
                       message='Could not load the PC-ACE database from the selected directory.\n\n'
                               'Please, check that the directory contains the expected Excel/pkl files.')
        return

    # ── Spell-check ──────────────────────────────────────────────────────────
    if spell_check_var.get() == 1:
        simplex_name = spell_check_simplex_var.get()
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
                        mb.showinfo(title='Spell-check review',
                                    message=f'Spell-check found potential duplicates/misspellings for '
                                            f'"{simplex_name}".\n\n'
                                            f'The review file has been saved to:\n{dupes_csv}\n\n'
                                            f'To apply corrections:\n'
                                            f'  1. Open the CSV and review each row.\n'
                                            f'  2. Edit the "Suggested correction" column if needed.\n'
                                            f'  3. Set "Accept?" to N for rows you want to skip.\n'
                                            f'  4. Save the CSV, then click the APPLY CORRECTIONS button.')
                    else:
                        mb.showinfo(title='Spell-check',
                                    message=f'No near-duplicate or misspelled values found for "{simplex_name}".')
                except Exception as e:
                    print(f"  Near-duplicate check skipped: {e}")
        else:
            # Check ALL text simplexes
            try:
                dupes_csv = DB_PCACE_data_analysis_util.find_near_duplicate_simplex_values(
                    inputDir, outputDir, simplex_name='')
                if dupes_csv and os.path.isfile(dupes_csv):
                    filesToOpen.append(dupes_csv)
                    mb.showinfo(title='Spell-check review',
                                message='Spell-check scanned ALL text simplexes in the database.\n\n'
                                        f'The review file has been saved to:\n{dupes_csv}\n\n'
                                        'To apply corrections:\n'
                                        '  1. Open the CSV and review each row.\n'
                                        '  2. Edit the "Suggested correction" column if needed.\n'
                                        '  3. Set "Accept?" to N for rows you want to skip.\n'
                                        '  4. Save the CSV, then click the APPLY CORRECTIONS button.')
                else:
                    mb.showinfo(title='Spell-check',
                                message='No near-duplicate or misspelled values found across any text simplex.')
            except Exception as e:
                print(f"  Spell-check (all simplexes) skipped: {e}")

    # ── Lemmatization ──────────────────────────────────────────────────────────
    if lemmatize_var.get() == 1:
        lang_name = lemmatize_lang_var.get()
        lang_code = Stanza_util.lang_dict_rev.get(lang_name, 'en')

        # Get selected simplex types from the + button lists
        noun_simplexes = list(_noun_simplex_list)
        verb_simplexes = list(_verb_simplex_list)

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
                    print(f"  Lemmatization of '{sx_name}' (noun) skipped: {e}")

            # Lemmatize verb-type simplexes (POS filter: VERB, AUX)
            for sx_name in verb_simplexes:
                try:
                    lemma_csv = DB_PCACE_data_analysis_util.lemmatize_simplex_values(
                        inputDir, outputDir, simplex_name=sx_name,
                        language=lang_code, pos_filter=['VERB', 'AUX'])
                    if lemma_csv and os.path.isfile(lemma_csv):
                        all_lemma_files.append(lemma_csv)
                except Exception as e:
                    print(f"  Lemmatization of '{sx_name}' (verb) skipped: {e}")

            if all_lemma_files:
                filesToOpen.extend(all_lemma_files)
                mb.showinfo(title='Lemmatization review',
                            message=f'Lemmatization produced {len(all_lemma_files)} review file(s).\n\n'
                                    f'To apply:\n'
                                    f'  1. Open each CSV and review the rows.\n'
                                    f'  2. Edit the "Lemmatized form" column if needed.\n'
                                    f'  3. Set "Accept?" to N for rows you want to skip.\n'
                                    f'  4. Save the CSV, then click APPLY LEMMATIZATION.')
            else:
                mb.showinfo(title='Lemmatization',
                            message='No values changed after lemmatization.\n\n'
                                    'All text values in the selected simplexes are already in their base form.')

    # ── Aggregate code validation ───────────────────────────────────────────────
    if agg_cross_db_var.get() == 1 or agg_side_by_side_var.get() == 1:
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
            if agg_cross_db_var.get() == 1:
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
                        print(f"  Cross-DB comparison error: {e}")
                        import traceback
                        traceback.print_exc()

            if agg_side_by_side_var.get() == 1:
                category = agg_category_var.get()
                for db_dir in db_dirs:
                    try:
                        side_file = DB_PCACE_data_analysis_util.build_aggregate_side_by_side(
                            db_dir, outputDir, category=category)
                        if side_file:
                            filesToOpen.append(side_file)
                    except Exception as e:
                        print(f"  Side-by-side error for {os.path.basename(db_dir)}: {e}")
                        import traceback
                        traceback.print_exc()
                if filesToOpen:
                    mb.showinfo(title='Side-by-side mapping',
                                message=f'Side-by-side mapping produced files for {len(db_dirs)} database(s).\n\n'
                                        f'Each CSV shows original values alongside their aggregate codes.')

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(3),
                                                 GUI_height_brief=880, # height at brief display
                                                 GUI_height_full=920, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=1, # to be added for full display
                                                 increment=1)  # to be added for full display

GUI_label = 'Graphical User Interface (GUI) for PC-ACE Data Validation & Cleaning'
head, scriptName = os.path.split(os.path.basename(__file__))

config_filename = GUI_util.config_filename_selected_config.get()

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
    out_dir = outputDir.get() if hasattr(outputDir, 'get') else outputDir
    if out_dir:
        cmd.extend(['--outputdir', out_dir])
    subprocess.Popen(cmd)

def _open_pcace_analyzer():
    """Launch the PC-ACE data analyzer GUI."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DB_PCACE_data_analysis_main.py')
    cmd = [sys.executable, script_path]
    out_dir = outputDir.get() if hasattr(outputDir, 'get') else outputDir
    if out_dir:
        cmd.extend(['--outputdir', out_dir])
    subprocess.Popen(cmd)

def _on_open_gui_selected(choice):
    if choice == 'Open DB SQL GUI':
        _open_sql_gui()
    elif choice == 'Open PC-ACE analyzer GUI':
        _open_pcace_analyzer()

_open_gui_var = tk.StringVar()
_open_gui_var.set('Open DB SQL GUI')
open_gui_menu = tk.OptionMenu(window, _open_gui_var,
                              'Open DB SQL GUI',
                              'Open PC-ACE analyzer GUI',
                              command=_on_open_gui_selected)
open_gui_menu.configure(width=25)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_gui_menu,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to open a related GUI.\n\n"
                                   "   Open DB SQL GUI: opens the SQL query GUI.\n"
                                   "   Open PC-ACE analyzer GUI: opens the PC-ACE data analyzer.")

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
                                   "Find near-duplicate and misspelled text values in the PC-ACE database.\n"
                                   "Select a specific simplex from the dropdown or leave as 'ALL text simplexes'\n"
                                   "to scan every text simplex in the database.\n\n"
                                   "Produces a review CSV with suggested corrections and an Accept?/Reject column.")

spell_check_simplex_var = tk.StringVar()
spell_check_simplex_var.set('ALL text simplexes')
spell_check_simplex_menu = ttk.Combobox(window, textvariable=spell_check_simplex_var, width=30, state='readonly')
spell_check_simplex_menu['values'] = ['ALL text simplexes']
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 200, y_multiplier_integer,
                                   spell_check_simplex_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 200,
                                   "Select which simplex to spell-check.\n"
                                   "'ALL text simplexes' checks every text-typed simplex in the database.")

# ── Apply corrections button ─────────────────────────────────────────────────

def _apply_spell_check_corrections():
    """Open a file dialog for the reviewed spell-check CSV and apply accepted corrections."""
    inputDir_val = inputDir.get() if hasattr(inputDir, 'get') else inputDir
    outputDir_val = outputDir.get() if hasattr(outputDir, 'get') else outputDir
    if not inputDir_val:
        mb.showwarning(title='Apply corrections',
                       message='Please select a PC-ACE database directory first.')
        return
    if not _ensure_database_loaded(inputDir_val):
        mb.showwarning(title='Apply corrections',
                       message='Could not load the PC-ACE database. Please check the input directory.')
        return
    csv_path = filedialog.askopenfilename(
        title='Select the reviewed spell-check CSV',
        initialdir=outputDir_val if outputDir_val else inputDir_val,
        filetypes=[('CSV files', '*.csv'), ('All files', '*.*')])
    if not csv_path:
        return
    answer = mb.askyesno(title='Apply corrections',
                         message=f'Apply accepted corrections from:\n{csv_path}\n\n'
                                 f'This will modify data_SimplexText.xlsx and .pkl in:\n{inputDir_val}\n\n'
                                 f'A backup of the original files is recommended.\n\nProceed?')
    if not answer:
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

apply_corrections_button = tk.Button(window, text='Apply corrections', command=_apply_spell_check_corrections)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   apply_corrections_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "After running spell-check, review the CSV output, then click here\n"
                                   "to apply accepted corrections back to data_SimplexText.xlsx and .pkl.\n\n"
                                   "Steps:\n"
                                   "  1. Run spell-check (checkbox above) to produce the review CSV.\n"
                                   "  2. Open the CSV and review each row.\n"
                                   "  3. Edit 'Suggested correction' if needed.\n"
                                   "  4. Set 'Accept?' to N for rows you want to skip.\n"
                                   "  5. Save the CSV, then click this button.")

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
                                    values=_stanza_languages, state='readonly')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 200, y_multiplier_integer,
                                   lemmatize_lang_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 200,
                                   "Select the language for Stanza lemmatization.\n"
                                   "All languages supported by Stanza are listed.")

# ── Noun simplex types (combobox + add) ──────────────────────────────────────

_noun_simplex_list = []

lemmatize_nouns_lb = tk.Label(window, text='Simplex types to lemmatize as NOUNS')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   lemmatize_nouns_lb, True)

lemmatize_nouns_var = tk.StringVar()
lemmatize_nouns_menu = ttk.Combobox(window, textvariable=lemmatize_nouns_var, width=30, state='readonly')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                   lemmatize_nouns_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Select a simplex type that contains NOUN values, then click + to add it.\n\n"
                                   "Examples: Name of individual actor, Name of collective actor,\n"
                                   "Physical objects, Role in organizations, Nome attore, etc.\n\n"
                                   "Stanza will apply NOUN lemmatization to values from these simplexes.")

def _update_noun_hover():
    """Update the + button hover-over to show current NOUN selections."""
    if _noun_simplex_list:
        tip = 'Click + to add another NOUN simplex.\n\nCurrent NOUN selections:\n  ' + \
              ', '.join(_noun_simplex_list)
    else:
        tip = 'Click + to add the selected simplex type to the NOUN lemmatization list.'
    y_pos = GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step * _noun_btn_y
    add_noun_button.bind('<Enter>',
        lambda e, t=tip: (e.widget.config(background='red', foreground='black'),
                          GUI_IO_util.display_widget_info(window, e,
                              GUI_IO_util.open_TIPS_x_coordinate + 280, y_pos - 20,
                              GUI_IO_util.open_TIPS_x_coordinate + 280, t)))

def _add_noun_simplex():
    val = lemmatize_nouns_var.get()
    if val and val not in _noun_simplex_list:
        _noun_simplex_list.append(val)
    _update_noun_hover()

def _reset_noun_simplexes():
    _noun_simplex_list.clear()
    lemmatize_nouns_var.set('')
    _update_noun_hover()

add_noun_button = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1, command=_add_noun_simplex)
_noun_btn_y = y_multiplier_integer
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 280, y_multiplier_integer,
                                   add_noun_button,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 280,
                                   "Click + to add the selected simplex type to the NOUN lemmatization list.")

reset_noun_button = tk.Button(window, text='Reset', width=GUI_IO_util.reset_button_width, height=1, command=_reset_noun_simplexes)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 320, y_multiplier_integer,
                                   reset_noun_button,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 320,
                                   "Click Reset to clear the NOUN simplex list and start fresh.")

# ── Verb simplex types (combobox + add) ──────────────────────────────────────

_verb_simplex_list = []

lemmatize_verbs_lb = tk.Label(window, text='as VERBS')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 400, y_multiplier_integer,
                                   lemmatize_verbs_lb, True)

lemmatize_verbs_var = tk.StringVar()
lemmatize_verbs_menu = ttk.Combobox(window, textvariable=lemmatize_verbs_var, width=30, state='readonly')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 470, y_multiplier_integer,
                                   lemmatize_verbs_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 470,
                                   "Select a simplex type that contains VERB values, then click + to add it.\n\n"
                                   "Examples: Verbal phrase, Nominalization, Frase verbale, etc.\n\n"
                                   "Stanza will apply VERB lemmatization to values from these simplexes.")

def _update_verb_hover():
    """Update the + button hover-over to show current VERB selections."""
    if _verb_simplex_list:
        tip = 'Click + to add another VERB simplex.\n\nCurrent VERB selections:\n  ' + \
              ', '.join(_verb_simplex_list)
    else:
        tip = 'Click + to add the selected simplex type to the VERB lemmatization list.'
    y_pos = GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step * _verb_btn_y
    add_verb_button.bind('<Enter>',
        lambda e, t=tip: (e.widget.config(background='red', foreground='black'),
                          GUI_IO_util.display_widget_info(window, e,
                              GUI_IO_util.open_TIPS_x_coordinate + 740, y_pos - 20,
                              GUI_IO_util.open_TIPS_x_coordinate + 740, t)))

def _add_verb_simplex():
    val = lemmatize_verbs_var.get()
    if val and val not in _verb_simplex_list:
        _verb_simplex_list.append(val)
    _update_verb_hover()

def _reset_verb_simplexes():
    _verb_simplex_list.clear()
    lemmatize_verbs_var.set('')
    _update_verb_hover()

add_verb_button = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1, command=_add_verb_simplex)
_verb_btn_y = y_multiplier_integer
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 740, y_multiplier_integer,
                                   add_verb_button,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 740,
                                   "Click + to add the selected simplex type to the VERB lemmatization list.")

reset_verb_button = tk.Button(window, text='Reset', width=GUI_IO_util.reset_button_width, height=1, command=_reset_verb_simplexes)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 780, y_multiplier_integer,
                                   reset_verb_button,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 780,
                                   "Click Reset to clear the VERB simplex list and start fresh.")

# Apply lemmatization corrections button
def _apply_lemmatization_corrections():
    """Open a file dialog for the reviewed lemmatization CSV and apply accepted corrections."""
    inputDir_val = inputDir.get() if hasattr(inputDir, 'get') else inputDir
    outputDir_val = outputDir.get() if hasattr(outputDir, 'get') else outputDir
    if not inputDir_val:
        mb.showwarning(title='Apply lemmatization',
                       message='Please select a PC-ACE database directory first.')
        return
    if not _ensure_database_loaded(inputDir_val):
        mb.showwarning(title='Apply lemmatization',
                       message='Could not load the PC-ACE database. Please check the input directory.')
        return
    csv_path = filedialog.askopenfilename(
        title='Select the reviewed lemmatization CSV',
        initialdir=outputDir_val if outputDir_val else inputDir_val,
        filetypes=[('CSV files', '*.csv'), ('All files', '*.*')])
    if not csv_path:
        return
    answer = mb.askyesno(title='Apply lemmatization',
                         message=f'Apply accepted lemmatization from:\n{csv_path}\n\n'
                                 f'This will modify data_SimplexText.xlsx and .pkl in:\n{inputDir_val}\n\n'
                                 f'A backup of the original files is recommended.\n\nProceed?')
    if not answer:
        return
    n_applied = DB_PCACE_data_analysis_util.apply_lemmatization_corrections(csv_path, inputDir_val)
    if n_applied > 0:
        mb.showinfo(title='Lemmatization applied',
                    message=f'Successfully applied {n_applied} lemmatization correction(s) to data_SimplexText.\n\n'
                            f'The xlsx and pkl files have been updated.')
    elif n_applied == 0:
        mb.showinfo(title='No changes',
                    message='No lemmatization corrections were applied.\n\n'
                            'Either all rows were marked Accept? = N, or the original values '
                            'were not found in data_SimplexText.')
    else:
        mb.showerror(title='Error',
                     message='An error occurred while applying lemmatization.\nCheck the console output for details.')

apply_lemma_button = tk.Button(window, text='Apply lemmatization', command=_apply_lemmatization_corrections)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   apply_lemma_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "After running lemmatization, review the CSV output, then click here\n"
                                   "to apply accepted lemmatizations back to data_SimplexText.xlsx and .pkl.")

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

add_db_button = tk.Button(window, text='+', width=2, command=_add_db_dir)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                   add_db_button,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Click to add a PC-ACE database directory for cross-DB comparison.\n"
                                   "Add 2 or more databases to compare aggregate codes across them.")

remove_db_button = tk.Button(window, text='−', width=2, command=_remove_db_dir)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 35, y_multiplier_integer,
                                   remove_db_button,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 35,
                                   "Remove the selected database from the list.")

agg_db_var = tk.StringVar()
agg_db_menu = ttk.Combobox(window, textvariable=agg_db_var, width=80, state='readonly')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 70, y_multiplier_integer,
                                   agg_db_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 70,
                                   "List of PC-ACE database directories to compare.\n"
                                   "Use + to add directories, − to remove.\n"
                                   "The INPUT directory (if set) is automatically included.")

# ── Comparison controls ──────────────────────────────────────────────────────

agg_cross_db_var = tk.IntVar()
agg_cross_db_cb = tk.Checkbutton(window, text='Cross-DB comparison', variable=agg_cross_db_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   agg_cross_db_cb,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Compare aggregate code vocabularies across all databases in the list.\n\n"
                                   "Produces two CSVs:\n"
                                   "  1. Full comparison: Database | Aggregate simplex | Code value | Frequency\n"
                                   "  2. Gaps report: shows which codes exist in which DBs (empty = missing)")

agg_side_by_side_var = tk.IntVar()
agg_side_by_side_cb = tk.Checkbutton(window, text='Side-by-side mapping', variable=agg_side_by_side_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 200, y_multiplier_integer,
                                   agg_side_by_side_cb,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 200,
                                   "For each database, produce a side-by-side CSV showing:\n"
                                   "  Original simplex value | Aggregate code | Aggregate code NEW | COLIN code\n\n"
                                   "One row per complex instance, so you can see how each original value\n"
                                   "maps through the different coding schemes.")

# Category selection (Actor vs Action)
agg_category_var = tk.StringVar()
agg_category_var.set('Actor')
agg_category_menu = ttk.Combobox(window, textvariable=agg_category_var, width=10,
                                  values=['Actor', 'Action'], state='readonly')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 400, y_multiplier_integer,
                                   agg_category_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate + 400,
                                   "Select the category for side-by-side mapping:\n"
                                   "  Actor: individual, collective, organization aggregate codes\n"
                                   "  Action: simple/complex process aggregate codes")

# ── Populate simplex dropdown when database directory changes ─────────────────

def _on_inputDir_change(*args):
    """When the input directory changes, populate the simplex dropdown."""
    global _database_loaded
    _database_loaded = False
    dir_val = inputDir.get() if hasattr(inputDir, 'get') else inputDir
    if not dir_val or not os.path.isdir(dir_val):
        spell_check_simplex_menu['values'] = ['ALL text simplexes']
        spell_check_simplex_var.set('ALL text simplexes')
        return
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
        except Exception as e:
            print(f"  Could not populate simplex dropdown: {e}")
            spell_check_simplex_menu['values'] = ['ALL text simplexes']

if hasattr(inputDir, 'trace'):
    inputDir.trace('w', _on_inputDir_change)

# ── Help buttons ────────────────────────────────────────────────────────────

def help_buttons(window, help_button_x_coordinate, increment):
    # Row 1: Open GUI dropdown
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        increment, "NLP Suite Help",
        "Use the dropdown menu to open a related GUI." + GUI_IO_util.msg_Esc)

    # Row 2: Spell-check checkbox + simplex dropdown
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "SPELL-CHECK: find near-duplicate and misspelled values in text simplexes.\n\n"
        "  1. Tick the 'Run spell-check' checkbox.\n"
        "  2. Select a specific simplex or leave as 'ALL text simplexes'.\n"
        "  3. Click RUN to produce a review CSV.\n"
        "  4. Review the CSV, edit corrections, set Accept? to N for rows to skip.\n"
        "  5. Click 'Apply corrections' to write accepted changes back to the database." + GUI_IO_util.msg_Esc)

    # Row 3: Apply corrections button
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "APPLY CORRECTIONS: apply reviewed spell-check corrections.\n\n"
        "Modifies data_SimplexText.xlsx and .pkl in the PC-ACE database directory.\n"
        "A backup of the original files is recommended before applying." + GUI_IO_util.msg_Esc)

    # Row 4: Lemmatize checkbox + language
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "LEMMATIZE: reduce inflected forms to base forms using Stanza.\n\n"
        "  Examples: 'went' → 'go', 'colpirono' → 'colpire', 'cities' → 'city'.\n\n"
        "  Select the language, then assign your database's simplex types\n"
        "  in the NOUNS and VERBS lists below." + GUI_IO_util.msg_Esc)

    # Row 5: Noun/Verb simplex listboxes (taller row due to listbox height=3)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "Select which simplex types contain NOUN vs VERB values.\n\n"
        "  NOUNS list: e.g., Name of individual actor, Physical objects, Nome attore\n"
        "  VERBS list: e.g., Verbal phrase, Nominalization, Frase verbale\n\n"
        "  The lists auto-populate from your database and auto-select likely matches.\n"
        "  Hold Ctrl to select/deselect multiple items." + GUI_IO_util.msg_Esc)

    # Row 6: Apply lemmatization button
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "APPLY LEMMATIZATION: apply reviewed lemmatization corrections.\n\n"
        "Modifies data_SimplexText.xlsx and .pkl in the PC-ACE database directory.\n"
        "A backup of the original files is recommended before applying." + GUI_IO_util.msg_Esc)

    # Row 7: Aggregate code validation label + DB list
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "AGGREGATE CODE VALIDATION: compare and inspect aggregate codes.\n\n"
        "  Use + / − to add/remove PC-ACE database directories.\n"
        "  The INPUT directory is automatically included." + GUI_IO_util.msg_Esc)

    # Row 8: Cross-DB comparison + Side-by-side mapping + Actor/Action
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "Cross-DB comparison: compares aggregate code vocabularies across databases.\n"
        "  Produces a full comparison CSV and a gaps report showing codes\n"
        "  that exist in some DBs but not others.\n\n"
        "Side-by-side mapping: for each complex instance, shows the original\n"
        "  simplex value alongside all aggregate coding schemes.\n"
        "  Select Actor or Action to choose which codes to inspect." + GUI_IO_util.msg_Esc)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer + 4.5, "NLP Suite Help", GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer - 1

increment = GUI_util.y_multiplier_integer
content_y_multiplier_integer = y_multiplier_integer
y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, increment)
y_multiplier_integer = max(y_multiplier_integer, content_y_multiplier_integer)

# ── Videos / TIPS ───────────────────────────────────────────────────────────

videos_lookup = {'No videos available':''}
videos_options = 'No videos available'
TIPS_lookup = {}
TIPS_options = 'No TIPS available'
IO_setup_display_brief = False

readMe_message = ("This GUI provides tools for validating and cleaning PC-ACE data.\n\n"
                  "IN INPUT, select the PC-ACE database directory (containing the Excel/pkl files).\n\n"
                  "SPELL-CHECK: finds near-duplicate and misspelled text values in simplexes.\n"
                  "  Select a specific simplex or check ALL text simplexes.\n"
                  "  Review the output CSV, then apply accepted corrections.\n\n"
                  "LEMMATIZE: reduces inflected forms to base forms using Stanza (English & Italian).\n"
                  "  Select Nouns, Verbs, or both. Review the output CSV, then apply.\n\n"
                  "AGGREGATE CODE VALIDATION:\n"
                  "  Cross-DB comparison: compare aggregate code vocabularies across multiple databases.\n"
                  "  Side-by-side mapping: see how original simplex values map to aggregate codes.")

readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)

run_script_command = lambda: run(
    GUI_util.inputFilename.get() if hasattr(GUI_util.inputFilename, 'get') else '',
    GUI_util.output_dir_path.get(),
    GUI_util.open_csv_output_checkbox.get(),
    GUI_util.charts_package_options_widget.get(),
    GUI_util.data_transformation_options_widget.get())

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options,
                    y_multiplier_integer, readMe_command,
                    videos_lookup, videos_options,
                    TIPS_lookup, TIPS_options,
                    IO_setup_display_brief, scriptName)

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
