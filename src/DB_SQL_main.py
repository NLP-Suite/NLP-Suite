# Written by Brett Landau, Fall 2020
# edited Austin Cai, Fall 2021

import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "DB_SQL_main.py", ['os', 'tkinter','pandas','sqlite3'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import sqlite3, pandas as pd
from subprocess import call

import subprocess

import IO_csv_util
import IO_files_util
import GUI_IO_util
import IO_user_interface_util
import TIPS_util
import DB_PCACE_data_analyzer_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def _build_sqlite(inpath_str, outpath_str):
    """Construct an SQLite database from xlsx and/or csv files in the input directory.
    Prefers xlsx; falls back to csv for tables only available as csv.
    Applies the same column renames as the PC-ACE analyzer so that SQL queries
    work identically regardless of which path created the SQLite database.
    Returns the path to the created database, or -1 on failure."""
    dbFileName = os.path.basename(os.path.normpath(inpath_str)) + ".sqlite"
    dbOutput = inpath_str + os.sep + dbFileName
    dirSearch = os.listdir(inpath_str)

    # Build a lookup of column renames from the analyzer's reading_list
    # Maps filename (e.g. 'data_Complex.xlsx') -> rename dict (e.g. {'ID':'ID_data_complex', ...})
    rename_lookup = {}
    try:
        for fn, rename_cols in DB_PCACE_data_analyzer_util.reading_list:
            if rename_cols:
                # Key by base name without extension for matching
                base = os.path.splitext(fn)[0]
                rename_lookup[base] = rename_cols
    except (AttributeError, TypeError):
        pass  # reading_list not available — proceed without renames

    # Collect tables: prefer xlsx, fall back to csv
    # tableDict maps table_name -> (file_extension, full_filename)
    tableDict = {}
    for file in dirSearch:
        name, ext = os.path.splitext(file)
        if ext.lower() == '.xlsx' and not name.startswith('~$'):
            tableDict[name] = ('xlsx', file)
        elif ext.lower() == '.csv' and name not in tableDict:
            # Only use csv if no xlsx version exists
            tableDict[name] = ('csv', file)

    if len(tableDict) == 0:
        mb.showwarning(title='Warning',
                       message='There are no xlsx or csv files in the input directory.\n\nThe script expects a set of xlsx or csv files with overlapping ID fields across files in order to construct an SQLite relational database.\n\nPlease, select an input directory that contains data files and try again.')
        return -1

    xlsx_count = sum(1 for ext, _ in tableDict.values() if ext == 'xlsx')
    csv_count = sum(1 for ext, _ in tableDict.values() if ext == 'csv')
    print(f"Found {len(tableDict)} tables ({xlsx_count} xlsx, {csv_count} csv), creating database...")

    if os.path.exists(dbOutput):
        os.unlink(dbOutput)

    conn = sqlite3.connect(dbOutput)
    for table_name, (ext, filename) in tableDict.items():
        # Replace dashes with underscore — SQLite doesn't handle dashes well
        sqlTableName = table_name.replace("-", "_")
        filepath = os.path.join(inpath_str, filename)
        try:
            if ext == 'xlsx':
                df = pd.read_excel(filepath)
            else:
                df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip')
            # Apply the same column renames that the analyzer uses
            # so that SQL queries are compatible across both paths
            if table_name in rename_lookup:
                df.rename(columns=rename_lookup[table_name], inplace=True)
            df.to_sql(name=sqlTableName, con=conn, index=False, if_exists='replace')
        except Exception as e:
            print(f"  WARNING: Could not import '{filename}': {e}")

    # Create indexes for cross-complex query performance
    try:
        cur = conn.cursor()
        for stmt in _INDEX_STMTS:
            cur.execute(stmt)
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"  Note: Could not create indexes: {e}")

    print("Database saved as", dbOutput)
    conn.close()
    return dbOutput

def _auto_chart_cross_complex(csv_path, outputDir, chartPackage, filesToOpen):
    """Delegate to the shared function in charts_util."""
    import charts_util
    charts_util.auto_chart_cross_complex(csv_path, outputDir, chartPackage, filesToOpen)


def run(inputDir,outputDir, openOutputFiles, chartPackage, dataTransformation, SQL_query_var):

    config_filename = GUI_util.config_filename_selected_config.get()

    if object_type_var_sql.get() != '' and required_object_var_sql.get() != '':
        _toggle_required_sql()
        return

    if select_SQLite_DB_var.get() != "":
        if not SQL_query_var or SQL_query_var.strip() == "":
            mb.showwarning(title='Warning',
                           message='The SQL query area is empty. Please, create or import a query and try again.')
            return
        print("SQL_query_var", SQL_query_var)
        dbVar = select_SQLite_DB_var.get()
        conn = sqlite3.connect(dbVar)
        cur = conn.cursor()
        colNames = []
        results = []
        # Detect data-modifying statements (UPDATE, INSERT, DELETE)
        _sql_verb = SQL_query_var.strip().split()[0].upper() if SQL_query_var.strip() else ''
        _is_modify = _sql_verb in ('UPDATE', 'INSERT', 'DELETE')

        try:
            # SQL_query_var contains the query a user has entered
            sql_rows = cur.execute(SQL_query_var)
        except Exception as e:
            mb.showwarning(title='SQL Error',
                           message=f'The query did not execute properly.\n\nError: {e}\n\nIf you are running a template query, you will need to change the table and column names to match your database.\n\nPlease, check your query and try again.')
            return

        if _is_modify:
            # Data-modifying query — commit and report affected rows
            affected = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            mb.showinfo(title='SQL UPDATE',
                        message=f'{_sql_verb} completed successfully.\n\n{affected} row(s) affected.\n\nNote: the change has been applied to the SQLite database only. The source xlsx/pkl files are NOT modified. If you need the change in the source files, re-export from the SQLite database or edit the xlsx files directly.')
            return

        for col in cur.description:
            # .description returns column names from the resulting SQL query
            # Each column is a 7-tuple, but we just need the first index to get it's name
            colNames.append(col[0])
        results.append(colNames)
        for row in sql_rows:
            results.append(row)
        # Build meaningful output filename from cross-complex query name if available
        qname = query_name_var.get() if query_name_var.get() else ''

        # For PC-ACE cross-complex queries, use a PCACE subfolder (same as analyzer GUI)
        if qname.startswith('Cross-complex:') and inputDir:
            head, tail = os.path.split(inputDir)
            if tail.endswith('_xlsx') or tail.endswith('_XLSX'):
                pcace_subdir = os.path.join(outputDir, tail[:-5])
            else:
                pcace_subdir = os.path.join(outputDir, tail)
            if not os.path.exists(pcace_subdir):
                pcace_subdir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                                      label=os.path.basename(pcace_subdir),
                                                                      silent=False)
            if pcace_subdir:
                outputDir = pcace_subdir

        if qname.startswith('Cross-complex:'):
            # e.g. 'Cross-complex: Individual → Simple process' or
            #      'Cross-complex: Individual → Simple process, City, Time'
            parts = qname.replace('Cross-complex:', '').strip().split('→')
            if len(parts) >= 2:
                src_part = parts[0].strip()
                tgt_part = parts[1].strip().replace(', ', '_').replace(' ', '_')
                csv_name = 'SQL_{}_{}.csv'.format(src_part, tgt_part)
            else:
                csv_name = 'sql_result.csv'
        else:
            csv_name = 'sql_result.csv'
        csv_full_path = outputDir + os.sep + csv_name
        filesToOpen = [csv_full_path]
        IO_csv_util.list_to_csv(GUI_util.window, results, csv_full_path, colnum=0)

        # Auto-generate charts for cross-complex query results
        if qname.startswith('Cross-complex:') and chartPackage != 'No charts':
            _auto_chart_cross_complex(csv_full_path, outputDir, chartPackage, filesToOpen)

        if openOutputFiles:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

        cur.close()
        conn.close()
    else:
        mb.showwarning(title='Warning',
                       message='No SQLite database available.\n\nPlease, select an input directory containing xlsx or csv data files, or select an existing SQLite database.')

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                # GUI_util.create_chart_output_checkbox.get(),
                                GUI_util.charts_package_options_widget.get(),
                                GUI_util.data_transformation_options_widget.get(),
                                SQL_query_entry.get("1.0", "end-1c"))

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(3),
                                                 GUI_height_brief=680, # height at brief display
                                                 GUI_height_full=720, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=1, # to be added for full display
                                                 increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Relational Database SQL queries'
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
config_input_output_numeric_options=[0,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
inputDir=GUI_util.input_main_dir_path
outputDir=GUI_util.output_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

select_SQLite_DB_var=tk.StringVar()
select_DB_tables_var=tk.StringVar()
select_DB_table_fields_var=tk.StringVar()
SQL_query_var=tk.StringVar()
distinct_var=tk.IntVar()
view_relations_var=tk.IntVar()

def clear(e):
    # complex_objects_var.set('')
    # simplex_objects_var.set('')
    source_complex_var.set('')
    source_simplex_var.set('')
    target_complex_var.set('')
    target_simplex_var.set('')
    _saved_pairs.clear()
    _update_extra_targets_label()
    auto_SQL_var.set('')
    distinct_var.set(0)
    SQL_query_var.set('')
    query_name_var.set('')
    try:
        SQL_query_entry.delete(0.1, tk.END)
    except Exception:
        pass  # widget may be disabled
    select_DB_tables_var.set('')
    select_DB_table_fields_var.set('')
    object_type_var_sql.set('')
    required_object_var_sql.set('')
    GUI_util.tips_dropdown_field.set('Open TIPS files')
window.bind("<Escape>", clear)

_SQLITE_VERSION = 3  # bump when _build_sqlite column mappings change (3 = added indexes)

def _check_sqlite_version(in_dir):
    """Check if the SQLite database was built with the current column-rename version.
    Returns True if the version matches (database is up to date), False otherwise."""
    version_file = os.path.join(in_dir, '_sqlite_version.txt')
    if os.path.exists(version_file):
        try:
            with open(version_file, 'r') as f:
                stored = int(f.read().strip())
            return stored == _SQLITE_VERSION
        except (ValueError, IOError):
            pass
    return False

def _write_sqlite_version(in_dir):
    with open(os.path.join(in_dir, '_sqlite_version.txt'), 'w') as f:
        f.write(str(_SQLITE_VERSION))

_INDEX_STMTS = [
    "CREATE INDEX IF NOT EXISTS idx_dc_setup ON data_Complex(ID_setup_complex)",
    "CREATE INDEX IF NOT EXISTS idx_dc_id ON data_Complex(ID_data_complex)",
    "CREATE INDEX IF NOT EXISTS idx_xcc_higher ON data_xref_Complex_Complex(ID_data_complex_HIGHER)",
    "CREATE INDEX IF NOT EXISTS idx_xcc_lower ON data_xref_Complex_Complex(ID_data_complex_LOWER)",
    "CREATE INDEX IF NOT EXISTS idx_xsc_complex ON [data_xref_Simplex_Complex](ID_data_complex)",
    "CREATE INDEX IF NOT EXISTS idx_xsc_simplex ON [data_xref_Simplex_Complex](ID_data_simplex)",
    "CREATE INDEX IF NOT EXISTS idx_ds_id ON data_Simplex(ID_data_simplex)",
    "CREATE INDEX IF NOT EXISTS idx_ds_setup ON data_Simplex(ID_setup_simplex)",
    "CREATE INDEX IF NOT EXISTS idx_ds_ref ON data_Simplex(ID_data_date_number_text)",
    "CREATE INDEX IF NOT EXISTS idx_ss_id ON setup_Simplex(ID_setup_simplex)",
    "CREATE INDEX IF NOT EXISTS idx_st_id ON data_SimplexText(ID_data_date_number_text)",
    "CREATE INDEX IF NOT EXISTS idx_sn_id ON data_SimplexNumber(ID_data_date_number_text)",
    "CREATE INDEX IF NOT EXISTS idx_sd_id ON data_SimplexDate(ID_data_date_number_text)",
    # Composite covering indexes for cross-complex query performance
    "CREATE INDEX IF NOT EXISTS idx_dc_setup_id ON data_Complex(ID_setup_complex, ID_data_complex)",
    "CREATE INDEX IF NOT EXISTS idx_dc_id_setup ON data_Complex(ID_data_complex, ID_setup_complex)",
    "CREATE INDEX IF NOT EXISTS idx_xcc_lower_higher ON data_xref_Complex_Complex(ID_data_complex_LOWER, ID_data_complex_HIGHER)",
    "CREATE INDEX IF NOT EXISTS idx_xcc_higher_lower ON data_xref_Complex_Complex(ID_data_complex_HIGHER, ID_data_complex_LOWER)",
]

def _ensure_indexes(db_path):
    """Add indexes to an existing SQLite database if missing."""
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        for stmt in _INDEX_STMTS:
            cur.execute(stmt)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  Note: Could not ensure indexes: {e}")

def _disable_all_widgets():
    """Disable all data-dependent widgets (called when input is invalid)."""
    try:
        for btn in (open_analyzer_button, view_relations_button,
                    view_grammar_button, update_grammar_button,
                    add_object_btn, generate_cross_btn,
                    import_query_button, save_query_button):
            btn.configure(state='disabled')
        for cb in (expand_complex_cb, distinct_checkbox):
            cb.configure(state='disabled')
        for combo in (source_complex_menu, source_simplex_menu,
                      target_complex_menu, target_simplex_menu,
                      where_simplex_menu, where_operator_menu):
            combo.configure(state='disabled')
        where_value_entry.configure(state='disabled')
        object_type_var_sql_menu.configure(state='disabled')
        required_object_sql.configure(state='disabled')
        auto_SQL_value.configure(state='disabled')
        SQL_query_entry.configure(state='disabled')
    except NameError:
        pass  # widgets not yet created during startup

def _enable_all_widgets():
    """Enable all data-dependent widgets (called when database loads)."""
    try:
        for btn in (open_analyzer_button, view_relations_button,
                    view_grammar_button, update_grammar_button,
                    add_object_btn, generate_cross_btn,
                    import_query_button, save_query_button):
            btn.configure(state='normal')
        for cb in (expand_complex_cb, distinct_checkbox):
            cb.configure(state='normal')
        for combo in (source_complex_menu, source_simplex_menu,
                      target_complex_menu, target_simplex_menu,
                      where_simplex_menu, where_operator_menu):
            combo.configure(state='readonly')
        where_value_entry.configure(state='normal')
        object_type_var_sql_menu.configure(state='normal')
        required_object_sql.configure(state='normal')
        auto_SQL_value.configure(state='normal')
        SQL_query_entry.configure(state='normal')
    except NameError:
        pass  # widgets not yet created during startup

def _auto_build_sqlite(*args):
    """Automatically construct SQLite when input directory changes.
    If a database already exists for this directory, reuse it."""
    in_dir = inputDir.get() if hasattr(inputDir, 'get') else inputDir
    out_dir = outputDir.get() if hasattr(outputDir, 'get') else outputDir
    if not in_dir or not out_dir or not os.path.isdir(in_dir) or not os.path.isdir(out_dir):
        _disable_all_widgets()
        return
    # Count data files in this directory
    data_files = [f for f in os.listdir(in_dir)
                  if f.lower().endswith(('.xlsx', '.csv')) and not f.startswith('~$')]
    if not data_files:
        _disable_all_widgets()
        return
    db_folder_name = os.path.basename(os.path.normpath(in_dir))
    # Check if SQLite already exists in the input directory
    dbFileName = db_folder_name + ".sqlite"
    dbOutput = os.path.join(in_dir, dbFileName)
    if os.path.exists(dbOutput) and _check_sqlite_version(in_dir):
        # Reuse existing database — version matches; ensure indexes exist
        _ensure_indexes(dbOutput)
        select_SQLite_DB_var.set(dbOutput)
        IO_user_interface_util.timed_alert(window, 2000, 'SQLite database',
            'Reusing existing SQLite database for ' + db_folder_name + '.',
            False, '', True, '', False)
    else:
        # Build (or rebuild if version mismatch)
        if os.path.exists(dbOutput):
            IO_user_interface_util.timed_alert(window, 3000, 'Rebuilding SQLite database',
                'Rebuilding SQLite database for ' + db_folder_name + ' (' + str(len(data_files)) + ' data files).\n\nColumn names have been updated.\n\nPlease, be patient... Depending on database size this may take several minutes.',
                False, '', True, '', False)
        else:
            IO_user_interface_util.timed_alert(window, 3000, 'Building SQLite database',
                'Building SQLite database from ' + str(len(data_files)) + ' data files in ' + db_folder_name + '.\n\nPlease, be patient... Depending on database size this may take several minutes.',
                False, '', True, '', False)
        window.title(GUI_label + '  —  Loading ' + db_folder_name + '...')
        window.update_idletasks()
        result = _build_sqlite(in_dir, out_dir)
        if result != -1:
            select_SQLite_DB_var.set(result)
            _write_sqlite_version(in_dir)
        # Restore title (remove "Loading...")
        window.title(GUI_label + '  —  ' + db_folder_name)
    # Enable RUN and all widgets if database and output are set
    if select_SQLite_DB_var.get() != '' and out_dir != '':
        GUI_util.run_button.configure(state='normal')
        _enable_all_widgets()
    # Create SQL queries subdirectory if it doesn't exist
    sql_subdir = os.path.join(in_dir, 'SQL queries')
    if not os.path.exists(sql_subdir):
        os.makedirs(sql_subdir)

GUI_util.input_main_dir_path.trace('w', _auto_build_sqlite)

def view_relations():
    TIPS_util.open_TIPS('TIPS_NLP_PC-ACE table relations.pdf')

def view_grammar():
    if inputDir.get() == '':
        mb.showwarning(title='Warning', message='No input directory selected.')
        return
    head, tail = os.path.split(inputDir.get())
    DB_PCACE_data_analyzer_util.view_grammar(os.path.join(inputDir.get(), 'setup_Complex.xlsx'),
                                             'GrammarRule_Text', os.path.join(inputDir.get(),
                                                                              'PC-ACE grammar for database ' + tail + '.txt'))

def update_grammar():
    if inputDir.get() == '':
        mb.showwarning(title='Warning', message='No input directory selected.')
        return
    DB_PCACE_data_analyzer_util.update_grammar_text(inputDir.get())

def open_pcace_analyzer():
    """Launch the PC-ACE data analyzer GUI with the current input/output directories."""
    in_dir = inputDir.get() if hasattr(inputDir, 'get') else inputDir
    out_dir = outputDir.get() if hasattr(outputDir, 'get') else outputDir
    if not in_dir or not os.path.isdir(in_dir):
        mb.showwarning(title='Warning', message='No input directory selected.\n\nPlease, select a PC-ACE input directory first.')
        return
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DB_PCACE_data_analyzer_main.py')
    cmd = [sys.executable, script_path]
    if in_dir:
        cmd.extend(['--inputdir', in_dir])
    if out_dir:
        cmd.extend(['--outputdir', out_dir])
    subprocess.Popen(cmd)

open_analyzer_button = tk.Button(window, text='Open PC-ACE analyzer GUI', width=25, height=1, state='disabled', command=lambda: open_pcace_analyzer())
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_analyzer_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to open the PC-ACE data analyzer GUI with the current input directory.")

view_relations_button = tk.Button(window, text='View table relations', width=17, height=1, state='disabled', command=lambda: view_relations())
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   view_relations_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to open a pdf file of the PC-ACE table relations.")

view_grammar_button = tk.Button(window, text='View grammar', width=17, height=1, state='disabled', command=lambda: view_grammar())
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate+150, y_multiplier_integer,
                                   view_grammar_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to export the grammar used for the selected PC-ACE database.")

update_grammar_button = tk.Button(window, text='Update grammar', width=17, height=1, state='disabled', command=lambda: update_grammar())
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate+300, y_multiplier_integer,
                                   update_grammar_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click to update the grammar saved in setup_complex.xlsx and setup_complex.pkl.")

# ── Update REQUIRED boolean ─────────────────────────────────────────────
object_type_lb = tk.Label(window, text='Object ')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate+450, y_multiplier_integer,
                                   object_type_lb, True)

object_type_var_sql = tk.StringVar()
object_type_var_sql_menu = tk.OptionMenu(window, object_type_var_sql, 'Complex', 'Simplex')
object_type_var_sql_menu.configure(state='disabled')
object_type_var_sql.set('')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate+500, y_multiplier_integer,
                                   object_type_var_sql_menu,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to select the type of object (complex or simplex) for which to obtain a list of values.\nThe object list will then be displayed in the right-hand menu widget.")
# Besides inspecting the list, you can select a specific object whose current REQUIRED value you want to change

# Get the setup names for the dropdowns (may be empty if no DB loaded yet)
try:
    _sql_setup_complex_menu, _sql_setup_simplex_menu = DB_PCACE_data_analyzer_util.get_setup_complex_simplex_names()
except:
    _sql_setup_complex_menu, _sql_setup_simplex_menu = [], []

def _update_combo_hover(combo, y_row, x_coord, x_hover, count, base_text):
    """Re-bind hover-over text on a combobox to include item count."""
    count_line = f'{count} item(s) listed.' if count > 0 else 'No items listed.'
    tip = count_line + '\n' + base_text
    combo.bind('<Enter>',
        lambda e, t=tip: GUI_IO_util.display_widget_info(window, e, x_coord,
            GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step * y_row,
            x_hover, t))
    combo.bind('<Leave>',
        lambda e: GUI_IO_util.delete_display_widget_lb(window, e, ''))

required_object_var_sql = tk.StringVar()
required_object_sql = ttk.Combobox(window, textvariable=required_object_var_sql, width=GUI_IO_util.widget_width_short)
required_object_sql.configure(state='disabled')
required_object_sql['values'] = _sql_setup_complex_menu
_required_object_sql_base_text = ("You can use the dropdown menu to scroll through the list of available objects.\n"
    "You can also select a complex or simplex object, then press Enter or click RUN to toggle its REQUIRED boolean value (from False to True or viceversa).\n"
    "The value is set in the setup_xref_Complex-Complex table or setup_xref_Simplex-Complex table. The xlsx, pkl, and grammar files will be updated.")
_required_object_sql_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate+600, y_multiplier_integer,
                                   required_object_sql,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   _required_object_sql_base_text)

def _update_required_object_dropdown_sql(*args):
    """Switch required_object dropdown values between Complex and Simplex names.
    Re-fetches from the util each time to ensure values are current after DB load."""
    obj_type = object_type_var_sql.get()
    _ensure_libraries_loaded()
    try:
        c_menu, s_menu = DB_PCACE_data_analyzer_util.get_setup_complex_simplex_names()
    except:
        c_menu, s_menu = [], []
    if obj_type == 'Complex':
        required_object_sql['values'] = c_menu
        n = len(c_menu)
        if c_menu:
            required_object_var_sql.set(c_menu[0])
        else:
            required_object_var_sql.set('')
    elif obj_type == 'Simplex':
        required_object_sql['values'] = s_menu
        n = len(s_menu)
        if s_menu:
            required_object_var_sql.set(s_menu[0])
        else:
            required_object_var_sql.set('')
    else:
        # Do not pre-populate until user picks Complex or Simplex
        required_object_sql['values'] = []
        n = 0
        required_object_var_sql.set('')
    _update_combo_hover(required_object_sql, _required_object_sql_y_row,
        GUI_IO_util.labels_x_coordinate+600, GUI_IO_util.open_TIPS_x_coordinate,
        n, _required_object_sql_base_text)

object_type_var_sql.trace('w', _update_required_object_dropdown_sql)

def _toggle_required_sql():
    """Toggle the REQUIRED boolean for the selected object, with confirmation."""
    _ensure_libraries_loaded()
    obj_type = object_type_var_sql.get()
    obj_name = required_object_var_sql.get()
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
        success = DB_PCACE_data_analyzer_util.toggle_required_value(obj_type, obj_name, new_val, GUI_util.input_main_dir_path.get())
        if success:
            mb.showwarning(title='REQUIRED updated',
                           message=f'The REQUIRED value for "{obj_name}" has been changed to {new_str}.\n\n'
                                   f'The xlsx, pkl, and grammar files have been updated.')
        else:
            mb.showwarning(title='Error',
                           message=f'Failed to update the REQUIRED value for "{obj_name}".\nCheck the command line for details.')

required_object_sql.bind('<Return>', lambda e: _toggle_required_sql())

table_menu_values = []
_populating_tables = False  # guard flag to suppress auto-insert during initial population
def get_table_list(*args):
    global _populating_tables
    _populating_tables = True
    select_DB_table_fields_menu.configure(state='disabled')
    if select_SQLite_DB_var.get()=='':
        select_DB_tables_menu.configure(state='disabled')
        _populating_tables = False
        return
    # get_complex_simplex_list('setup_Complex')
    select_DB_tables_menu.configure(state='normal')
    conn = sqlite3.connect(select_SQLite_DB_var.get())
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
    # construct menu values — clear first to avoid duplicates on reload
    table_menu_values.clear()
    for row in cur:
        table_menu_values.append(row[0])
    cur.close()
    conn.close()
    m = select_DB_tables_menu["menu"]
    m.delete(0, "end")
    for s in table_menu_values:
        m.add_command(label=s, command=lambda value=s: select_DB_tables_var.set(value))
    # Populate but do not display a value — user must explicitly select
    select_DB_tables_var.set('')
    _populating_tables = False
select_SQLite_DB_var.trace('w',get_table_list)


def _add_typeahead(combo):
    """Add keyboard typeahead to a ttk.Combobox: type a letter to jump to
    the first matching item."""
    def _on_key(event):
        ch = event.char.lower()
        if not ch or not ch.isalpha():
            return
        values = combo['values']
        if not values:
            return
        for val in values:
            if val.lower().startswith(ch):
                combo.set(val)
                combo.event_generate('<<ComboboxSelected>>')
                return
    combo.bind('<KeyPress>', _on_key)

# ── Cross-complex query generator ─────────────────────────────────────────
cross_complex_lb = tk.Label(window, text='Cross-complex query')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer, cross_complex_lb, True)

# OBJECT 1 ---------------------------------------------------------------------------------------
source_complex_var = tk.StringVar()
source_complex_menu = ttk.Combobox(window, textvariable=source_complex_var, state='disabled', width=20)
_add_typeahead(source_complex_menu)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 130, y_multiplier_integer,
                                               source_complex_menu, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 130,
                                               "Object 1 (COMPLEX): select a complex type (e.g. Individual, Event).")

# OBJECT 2 ---------------------------------------------------------------------------------------
source_simplex_var = tk.StringVar()
source_simplex_menu = ttk.Combobox(window, textvariable=source_simplex_var, state='disabled', width=20)
_add_typeahead(source_simplex_menu)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 310, y_multiplier_integer,
                                               source_simplex_menu, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 310,
                                               "Object 2 (SIMPLEX): select the simplex to be displayed for Object 1 (e.g., Name of individual; * for all simplex)")

# OBJECT 3 ---------------------------------------------------------------------------------------
target_complex_var = tk.StringVar()
target_complex_menu = ttk.Combobox(window, textvariable=target_complex_var, state='disabled', width=20)
_add_typeahead(target_complex_menu)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 500, y_multiplier_integer,
                                               target_complex_menu, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate+500,
                                               "Object 3 (COMPLEX): select a complex type to be joined with Object 1 (e.g. Simple process, City). Click + to add more.")
# OBJECT 4 ---------------------------------------------------------------------------------------
target_simplex_var = tk.StringVar()
target_simplex_menu = ttk.Combobox(window, textvariable=target_simplex_var, state='disabled', width=20)
_add_typeahead(target_simplex_menu)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 680, y_multiplier_integer,
                                               target_simplex_menu, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate+500,
                                               "Object 4 (SIMPLEX): select the simplex to be displayed for Object 3 (e.g., Verbal phrase; * for all simplex)")

# + ADD OBJECTS ---------------------------------------------------------------------------------------
add_object_btn = tk.Button(window, width=2, text='+', state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 840, y_multiplier_integer,
                                               add_object_btn, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate+400,
                                               "Click on + to add another set of objects.\nEach + saves the current 4-object selection and resets the dropdowns for the next set (Object 5, 6, 7, 8...).")
# EXPAND OBJECTS ---------------------------------------------------------------------------------------
expand_complex_var = tk.IntVar(value=1)
expand_complex_cb = tk.Checkbutton(window, text='', variable=expand_complex_var, onvalue=1, offvalue=0, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 880, y_multiplier_integer,
                                               expand_complex_cb, True, False, True, False, 90,
                                               GUI_IO_util.open_reminders_x_coordinate,
                                               "Expand any complex object with no simplex attributes to its lowest complex with available simplex children.")

generate_cross_btn = tk.Button(window, width=15, text='Generate SQL query', state='disabled')
_gen_btn_y_row = y_multiplier_integer  # save for dynamic hover-over re-binding
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 960, y_multiplier_integer,
                                               generate_cross_btn, False, False, True, False, 90,
                                               GUI_IO_util.open_setup_x_coordinate,
                                               "Click to generate the SQL query for the selected objects.\nClick RUN after the SQL query is displayed in the SQL query area.")

# ── WHERE filter row ──────────────────────────────────────────────────────
where_filter_lb = tk.Label(window, text='WHERE filter')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               where_filter_lb, True)

# Simplex to filter on (populated dynamically when source complex is selected)
where_simplex_var = tk.StringVar()
where_simplex_menu = ttk.Combobox(window, textvariable=where_simplex_var, state='disabled', width=20)
_add_typeahead(where_simplex_menu)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 130, y_multiplier_integer,
                                               where_simplex_menu, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 130,
                                               "Select a simplex attribute to filter on (e.g., Type of actor, Verbal phrase).\nLeave empty for no filter.")

# Operator (=, LIKE, !=)
where_operator_var = tk.StringVar()
where_operator_menu = ttk.Combobox(window, textvariable=where_operator_var, state='disabled', width=5,
                                    values=['LIKE', '=', '!=', 'NOT LIKE'])
where_operator_var.set('LIKE')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 310, y_multiplier_integer,
                                               where_operator_menu, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 310,
                                               "SQL comparison operator.\nLIKE supports wildcards: %woman% matches any value containing 'woman'.\n= requires exact match.\n!= excludes exact match.\nNOT LIKE excludes pattern.")

# Value entry
where_value_var = tk.StringVar()
where_value_entry = tk.Entry(window, textvariable=where_value_var, width=25, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 400, y_multiplier_integer,
                                               where_value_entry, False, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 400,
                                               "Enter the filter value or pattern.\nFor LIKE, use % as wildcard (e.g., %lynching%, %woman%).\nFor =, enter the exact value.")

# ── Extra objects (accumulated via the + button) ─────────────────────────
_saved_pairs = []  # list of (src_name, src_simplex, tgt_name, tgt_simplex)
_complex_names_cache = []

# Object selection summary — no longer on a separate row.
# The selection is shown in the hover-over text of the "Generate SQL query" button.
extra_targets_var = tk.StringVar()


def _update_extra_targets_label(*args):
    """Update the summary of all saved pairs + current selection.
    The summary is stored in extra_targets_var and shown in the
    hover-over text of the 'Generate SQL query' button."""
    parts = []
    obj_num = 1
    # Saved pairs
    for s, ssx, t, tsx in _saved_pairs:
        parts.append('{}:{}'.format(obj_num, s))
        obj_num += 1
        parts.append('{}:{}'.format(obj_num, ssx or '*'))
        obj_num += 1
        parts.append('{}:{}'.format(obj_num, t))
        obj_num += 1
        parts.append('{}:{}'.format(obj_num, tsx or '*'))
        obj_num += 1
    # Current (unsaved) selection
    src = source_complex_var.get()
    if src:
        parts.append('{}:{}'.format(obj_num, src))
        obj_num += 1
        src_sx = source_simplex_var.get() or '*'
        parts.append('{}:{}'.format(obj_num, src_sx))
        obj_num += 1
    tgt = target_complex_var.get()
    if tgt:
        parts.append('{}:{}'.format(obj_num, tgt))
        obj_num += 1
        tgt_sx = target_simplex_var.get() or '*'
        parts.append('{}:{}'.format(obj_num, tgt_sx))
    text = ', '.join(parts) if parts else ''
    extra_targets_var.set(text)
    # Update the hover-over text of the Generate button to show the current selection
    selection_line = 'Object selection: ' + text if text else 'No objects selected yet.'
    _gen_btn_hover_text = ("Click to generate the SQL query for the selected objects.\n"
                           "Click RUN after the SQL query is displayed in the SQL query area.\n\n"
                           + selection_line)
    # Re-bind hover-over with updated text
    generate_cross_btn.bind('<Enter>',
        lambda e, t=_gen_btn_hover_text: (
            e.widget.config(background='red', foreground='black'),
            GUI_IO_util.display_widget_info(window, e,
                GUI_IO_util.labels_x_coordinate + 960,
                GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step * _gen_btn_y_row,
                GUI_IO_util.open_setup_x_coordinate, t)))


def _add_object():
    """Save current Object 1 + Object 2 pair and reset all 4 dropdowns."""
    src = source_complex_var.get()
    tgt = target_complex_var.get()
    if not src or not tgt:
        mb.showwarning(title='Warning', message='Please select both Object 1 and Object 2 before clicking +.')
        return
    src_sx = source_simplex_var.get() or None
    if src_sx == '*':
        src_sx = None
    tgt_sx = target_simplex_var.get() or None
    if tgt_sx == '*':
        tgt_sx = None
    _saved_pairs.append((src, src_sx, tgt, tgt_sx))
    # Reset all 4 dropdowns for next pair
    source_complex_var.set('')
    source_simplex_var.set('')
    target_complex_var.set('')
    target_simplex_var.set('')
    # Label updates automatically via trace


add_object_btn.configure(command=_add_object)
source_complex_var.trace('w', _update_extra_targets_label)
source_simplex_var.trace('w', _update_extra_targets_label)
target_complex_var.trace('w', _update_extra_targets_label)
target_simplex_var.trace('w', _update_extra_targets_label)


def _ensure_libraries_loaded():
    """Load PC-ACE libraries if needed."""
    input_dir = GUI_util.input_main_dir_path.get() if hasattr(GUI_util.input_main_dir_path, 'get') else ''
    if input_dir and os.path.isdir(input_dir):
        try:
            if DB_PCACE_data_analyzer_util.setup_Complex_lib is None:
                DB_PCACE_data_analyzer_util.build_libraries(input_dir, input_dir)
        except (AttributeError, NameError):
            try:
                DB_PCACE_data_analyzer_util.build_libraries(input_dir, input_dir)
            except Exception as e:
                print(f"  WARNING loading libraries: {e}")


def _expand_if_no_simplex(complex_name):
    """If a complex has no simplex attributes, return its children that do.
    Returns a list of (child_name, None) tuples, or [(complex_name, None)] if it has simplexes."""
    names = DB_PCACE_data_analyzer_util.get_cross_complex_simplex_names(complex_name)
    if names:
        return [(complex_name, None)]
    children = DB_PCACE_data_analyzer_util.get_children_with_simplexes(complex_name)
    if children:
        return [(c, None) for c in children]
    return [(complex_name, None)]


def _expand_pairs(pairs):
    """Expand pairs where source or target has no simplexes (replace with children)."""
    expanded = []
    for src, src_sx, tgt, tgt_sx in pairs:
        # Expand source if needed
        src_list = [(src, src_sx)]
        if not src_sx:
            src_names = DB_PCACE_data_analyzer_util.get_cross_complex_simplex_names(src)
            if not src_names:
                src_list = _expand_if_no_simplex(src)
        # Expand target if needed
        tgt_list = [(tgt, tgt_sx)]
        if not tgt_sx:
            tgt_names = DB_PCACE_data_analyzer_util.get_cross_complex_simplex_names(tgt)
            if not tgt_names:
                tgt_list = _expand_if_no_simplex(tgt)
        # Cross-product of expanded sources and targets
        for s, ssx in src_list:
            for t, tsx in tgt_list:
                expanded.append((s, ssx, t, tsx))
    return expanded


def _generate_cross_complex_query():
    # Collect all pairs: saved + current (if complete)
    all_pairs = list(_saved_pairs)
    cur_src = source_complex_var.get()
    cur_tgt = target_complex_var.get()
    if cur_src and cur_tgt:
        src_sx = source_simplex_var.get() or None
        if src_sx == '*':
            src_sx = None
        tgt_sx = target_simplex_var.get() or None
        if tgt_sx == '*':
            tgt_sx = None
        all_pairs.append((cur_src, src_sx, cur_tgt, tgt_sx))

    if not all_pairs:
        mb.showwarning(title='Warning', message='Please select Object 1 and Object 2.')
        return

    # Collect WHERE filter (optional)
    _where_simplex = where_simplex_var.get() or None
    _where_value = where_value_var.get().strip() or None
    _where_operator = where_operator_var.get() or 'LIKE'

    _ensure_libraries_loaded()

    # Expand complex types with no simplexes to their children (if checkbox is checked)
    if expand_complex_var.get():
        all_pairs = _expand_pairs(all_pairs)

    if len(all_pairs) == 1:
        # Single pair: use the original (faster) single-target generator
        src, src_simplex, tgt_name, tgt_simplex = all_pairs[0]
        query, result = DB_PCACE_data_analyzer_util.generate_cross_complex_query(
            src, tgt_name,
            source_filter_simplex=src_simplex,
            source_filter_value=_where_value,
            source_filter_operator=_where_operator,
            where_simplex=_where_simplex,
            target_simplex=tgt_simplex)
        if query is None:
            mb.showwarning(title='Warning', message=str(result))
            return
        SQL_query_entry.delete(0.1, tk.END)
        SQL_query_entry.insert("end", query)
        query_name_var.set('Cross-complex: {} → {}'.format(src, tgt_name))
        # Warn about missing simplexes
        warnings = []
        if not DB_PCACE_data_analyzer_util.get_cross_complex_simplex_names(src):
            children = DB_PCACE_data_analyzer_util.get_children_with_simplexes(src)
            msg = "'{}' has no simplex attributes.".format(src)
            if children:
                msg += "\nTry: {}".format(', '.join(children))
            warnings.append(msg)
        if not DB_PCACE_data_analyzer_util.get_cross_complex_simplex_names(tgt_name):
            children = DB_PCACE_data_analyzer_util.get_children_with_simplexes(tgt_name)
            msg = "'{}' has no simplex attributes.".format(tgt_name)
            if children:
                msg += "\nTry: {}".format(', '.join(children))
            warnings.append(msg)
        if warnings:
            mb.showinfo(title='Simplex attributes', message='\n\n'.join(warnings))
    else:
        # Multiple pairs: group by source, generate one query per unique source
        # For now, all pairs must share the same Object 1 for multi-target CTE query
        sources = set((s, ssx) for s, ssx, _, _ in all_pairs)
        if len(sources) > 1:
            # Different sources — generate separate queries concatenated
            all_queries = []
            for src, src_sx, tgt, tgt_sx in all_pairs:
                q, res = DB_PCACE_data_analyzer_util.generate_cross_complex_query(
                    src, tgt, source_filter_simplex=src_sx, target_simplex=tgt_sx)
                if q:
                    all_queries.append(q)
            if not all_queries:
                mb.showwarning(title='Warning', message='Could not generate queries for the selected pairs.')
                return
            SQL_query_entry.delete(0.1, tk.END)
            SQL_query_entry.insert("end", '\n\n'.join(all_queries))
            pair_labels = ['{} → {}'.format(s, t) for s, _, t, _ in all_pairs]
            query_name_var.set('Cross-complex: {}'.format('; '.join(pair_labels)))
        else:
            # Same source — use CTE multi-target generator
            src, src_simplex = list(sources)[0]
            targets = [(t, tsx) for _, _, t, tsx in all_pairs]
            query, info = DB_PCACE_data_analyzer_util.generate_multi_target_query(
                src, source_simplex=src_simplex, targets=targets)
            if query is None:
                mb.showwarning(title='Warning', message=str(info))
                return
            SQL_query_entry.delete(0.1, tk.END)
            SQL_query_entry.insert("end", query)
            tgt_names = [t[0] for t in targets]
            query_name_var.set('Cross-complex: {} → {}'.format(src, ', '.join(tgt_names)))
            if info.get('warnings'):
                mb.showinfo(title='Simplex attributes', message='\n\n'.join(info['warnings']))


generate_cross_btn.configure(command=_generate_cross_complex_query)


def _populate_cross_complex_menus(*args):
    """Populate source and target complex menus and cache names for extra targets."""
    global _complex_names_cache
    db_path = select_SQLite_DB_var.get()
    # Reset all
    for combo, var in [(source_complex_menu, source_complex_var),
                       (target_complex_menu, target_complex_var),
                       (source_simplex_menu, source_simplex_var),
                       (target_simplex_menu, target_simplex_var)]:
        combo['values'] = ()
        var.set('')
    _saved_pairs.clear()
    _update_extra_targets_label()
    _complex_names_cache = []
    if not db_path or not os.path.exists(db_path):
        return
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT Name FROM setup_Complex ORDER BY Name")
        names = [row[0] for row in cur.fetchall()]
        _complex_names_cache = names
        source_complex_menu['values'] = names
        target_complex_menu['values'] = names
        # Do NOT auto-populate — user must explicitly select objects
        source_complex_var.set('')
        target_complex_var.set('')
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  WARNING populating cross-complex menus: {e}")


def _populate_simplex_menu(complex_var, simplex_combo, simplex_var):
    """Populate a simplex Combobox based on the selected complex type."""
    simplex_combo['values'] = ()
    simplex_var.set('')
    cname = complex_var.get()
    if not cname:
        return
    db_path = select_SQLite_DB_var.get()
    if not db_path or not os.path.exists(db_path):
        return
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT ID_setup_complex FROM setup_Complex WHERE Name=?", (cname,))
        row = cur.fetchone()
        if row:
            cid = row[0]
            cur.execute("""SELECT DISTINCT ss.Name
                           FROM setup_xref_Simplex_Complex sxsc
                           JOIN setup_Simplex ss ON ss.ID_setup_simplex = sxsc.ID_setup_simplex
                           WHERE sxsc.ID_setup_complex = ?
                           ORDER BY ss.Name""", (cid,))
            names = [r[0] for r in cur.fetchall()]
            if names:
                simplex_combo['values'] = ['*'] + names
                simplex_var.set('*')
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  WARNING populating simplex menu: {e}")

def _populate_source_simplex(*args):
    _populate_simplex_menu(source_complex_var, source_simplex_menu, source_simplex_var)
    # Also populate WHERE filter simplex with the same list
    _populate_simplex_menu(source_complex_var, where_simplex_menu, where_simplex_var)

def _populate_target_simplex(*args):
    _populate_simplex_menu(target_complex_var, target_simplex_menu, target_simplex_var)

select_SQLite_DB_var.trace('w', _populate_cross_complex_menus)
source_complex_var.trace('w', _populate_source_simplex)
target_complex_var.trace('w', _populate_target_simplex)

# ── DB table / field selection row ────────────────────────────────────────
select_DB_tables_lb = tk.Label(window, text='DB tables ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,select_DB_tables_lb,True)
if len(table_menu_values)==0:
    select_DB_tables_menu = tk.OptionMenu(window, select_DB_tables_var, table_menu_values)
else:
    select_DB_tables_menu = tk.OptionMenu(window,select_DB_tables_var, *table_menu_values)
select_DB_tables_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+70,y_multiplier_integer,select_DB_tables_menu,True)

table_fields_menu_values = []

def _insert_or_replace_placeholder(value, is_table=True):
    """Insert a table or field name into the SQL query area.
    If the cursor is inside a placeholder like [table] or [Field1],
    replace the entire placeholder. Otherwise insert at cursor position."""
    if not value:
        return
    was_disabled = (SQL_query_entry.cget('state') == 'disabled')
    if was_disabled:
        SQL_query_entry.configure(state='normal')

    cursor_pos = SQL_query_entry.index(tk.INSERT)
    query_text = SQL_query_entry.get("1.0", tk.END)

    # Convert cursor index (e.g., "1.45") to a flat character offset
    row, col = map(int, str(cursor_pos).split('.'))
    lines = query_text.split('\n')
    flat_pos = sum(len(lines[i]) + 1 for i in range(row - 1)) + col

    # Look for a bracketed placeholder surrounding the cursor
    # Search backward for '[' and forward for ']'
    bracket_start = -1
    bracket_end = -1
    for i in range(flat_pos - 1, -1, -1):
        if i < len(query_text) and query_text[i] == '[':
            bracket_start = i
            break
        if i < len(query_text) and query_text[i] == ']':
            break  # Hit a closing bracket before an opening one — not inside a placeholder

    if bracket_start >= 0:
        for i in range(flat_pos, len(query_text)):
            if query_text[i] == ']':
                bracket_end = i + 1
                break
            if query_text[i] == '[':
                break  # Hit another opening bracket — malformed

    replaced = False
    if bracket_start >= 0 and bracket_end > bracket_start:
        placeholder = query_text[bracket_start:bracket_end]
        # Check if it's a table or field placeholder
        ph_lower = placeholder.lower()
        if is_table and 'table' in ph_lower:
            # Replace ALL occurrences of this same placeholder (case-insensitive)
            import re
            new_text = re.sub(re.escape(placeholder), value, query_text, flags=re.IGNORECASE)
            SQL_query_entry.delete("1.0", tk.END)
            SQL_query_entry.insert("1.0", new_text.rstrip('\n'))
            replaced = True
        elif not is_table and ('field' in ph_lower or ph_lower in ('[1]', '[2]')):
            # Replace ALL occurrences of this same placeholder (case-insensitive)
            # e.g., clicking inside [Field1] replaces every [Field1] and [field1]
            import re
            new_text = re.sub(re.escape(placeholder), value, query_text, flags=re.IGNORECASE)
            SQL_query_entry.delete("1.0", tk.END)
            SQL_query_entry.insert("1.0", new_text.rstrip('\n'))
            replaced = True

    if not replaced:
        # No matching placeholder found — insert at cursor position
        SQL_query_entry.insert(cursor_pos, value)

    if was_disabled:
        SQL_query_entry.configure(state='disabled')

def _flat_to_tk_index(text, flat_pos):
    """Convert a flat character offset to a tkinter 'row.col' index string."""
    row = 1
    col = 0
    for i in range(flat_pos):
        if i < len(text) and text[i] == '\n':
            row += 1
            col = 0
        else:
            col += 1
    return f"{row}.{col}"

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
    # Populate but do not display a value — user must explicitly select
    select_DB_table_fields_var.set('')
    conn.close()
    # Only insert into query area when user manually selects a table, not during initial population
    if not _populating_tables:
        _insert_or_replace_placeholder(tableName, is_table=True)

select_DB_tables_var.trace('w',get_table_fields_list)
def get_table_fields_name(*args):
    # Only insert into query area when user manually selects a field, not during initial population
    if not _populating_tables:
        _insert_or_replace_placeholder(select_DB_table_fields_var.get(), is_table=False)

select_DB_table_fields_var.trace('w',get_table_fields_name)


select_DB_table_fields_lb = tk.Label(window, text='DB table fields')

y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 280, y_multiplier_integer,
                                               select_DB_table_fields_lb, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate+28,
                                               "Use the dropdown menu to list the fields of the selected DB table.")

if len(table_fields_menu_values)==0:
    select_DB_table_fields_menu = tk.OptionMenu(window, select_DB_table_fields_var, table_fields_menu_values)
else:
    select_DB_table_fields_menu = tk.OptionMenu(window,select_DB_table_fields_var, *table_fields_menu_values)
select_DB_table_fields_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+380,y_multiplier_integer,select_DB_table_fields_menu,True)

auto_SQL_lb = tk.Label(window, text='Templates')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+510,y_multiplier_integer,auto_SQL_lb,True)

auto_SQL_var=tk.StringVar()
auto_SQL_value = tk.OptionMenu(window,auto_SQL_var,'SQL standard','SQL count', 'SQL duplicates', 'SQL join', 'SQL left join', 'SQL union', 'SQL unmatched', 'SQL update', 'SQL subquery', 'SQL group concat', 'SQL case')
auto_SQL_value.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 600, y_multiplier_integer,
                                               auto_SQL_value, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate+600,
                                               "Use the dropdown menu to import an SQL query template.")
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,auto_SQL_value,True)

distinct_checkbox = tk.Checkbutton(window, text='Distinct', variable=distinct_var, onvalue=1, offvalue=0, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 680, y_multiplier_integer,
                                               distinct_checkbox, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate+680,
                                               "Tick the checkbox to display a query as DISTINCT.")
def _get_query_dir():
    """Get the best directory for SQL query files.
    Priority: 1) --querydir from PC-ACE analyzer
              2) 'SQL queries' subdirectory inside input dir
              3) database file's directory
              4) GUI input dir"""
    if _pcace_query_dir and os.path.isdir(_pcace_query_dir):
        return _pcace_query_dir
    # Check for 'SQL queries' subdirectory inside input dir
    input_dir = GUI_util.input_main_dir_path.get() if hasattr(GUI_util.input_main_dir_path, 'get') else GUI_util.input_main_dir_path
    if input_dir:
        sql_subdir = os.path.join(input_dir, 'SQL queries')
        if os.path.isdir(sql_subdir):
            return sql_subdir
    if select_SQLite_DB_var.get() != '':
        return os.path.dirname(select_SQLite_DB_var.get())
    return input_dir or ''

query_name_var = tk.StringVar()

def import_query(window, title, fileType):
    init_dir = _get_query_dir()
    # Check if there are any .txt query files in the directory
    if init_dir and os.path.isdir(init_dir):
        txt_files = [f for f in os.listdir(init_dir) if f.lower().endswith('.txt')]
        if len(txt_files) == 0:
            mb.showwarning(title='Warning',
                           message='No SQL queries are available for import in the default subdirectory\n\n' + init_dir + '\n\nPlease, build a query first, save it for future import.')
            return
    filePath = tk.filedialog.askopenfilename(title=title, initialdir=init_dir,
                                             filetypes=fileType)
    if len(filePath) > 0:
        SQL_query_entry.delete(0.1, tk.END)
        with open(filePath, 'r', encoding='utf_8', errors='ignore') as file:
            importedQuery = file.read()
        SQL_query_var.set(importedQuery)
        SQL_query_entry.insert("end", str(importedQuery))
        # Display the imported query filename
        query_name_var.set(os.path.basename(filePath))

def save_query():
    boxContent = SQL_query_entry.get(0.1, tk.END)
    if len(boxContent)>0:
        save_dir = _get_query_dir()
        filePath = tk.filedialog.asksaveasfile(initialdir=save_dir, initialfile='saveQry.txt', title="Save SQL query file",
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

import_query_button=tk.Button(window, width=15, text='Import SQL query', state='disabled', command=lambda: import_query(window,'Select INPUT SQL query file', [("SQL files", "*.txt")]))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+770, y_multiplier_integer,import_query_button,True)

save_query_button=tk.Button(window, width=15, text='Save SQL query', state='disabled', command=lambda: save_query())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+850, y_multiplier_integer,save_query_button)

# SQL query name — no longer on a separate row.
# The query name is shown in the hover-over text of the SQL query text area.

SQL_query_entry = tk.Text(window,height=12,state='disabled')
_sql_entry_y_row = y_multiplier_integer  # save for dynamic hover-over
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,SQL_query_entry)

def _update_sql_query_hover(*args):
    """Update the SQL query text area hover-over to show the query name."""
    qname = query_name_var.get()
    if qname:
        tip = 'SQL query name: ' + qname + '\n\nType or generate an SQL query. Click RUN to execute.'
    else:
        tip = 'Type or generate an SQL query. Click RUN to execute.\nUse Import/Save buttons to load/store queries.'
    SQL_query_entry.bind('<Enter>',
        lambda e, t=tip: GUI_IO_util.display_widget_info(window, e,
            GUI_IO_util.labels_x_coordinate,
            GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step * _sql_entry_y_row,
            GUI_IO_util.labels_x_coordinate, t))
    SQL_query_entry.bind('<Leave>',
        lambda e: GUI_IO_util.delete_display_widget_lb(window, e, ''))

query_name_var.trace('w', _update_sql_query_hover)
_update_sql_query_hover()  # Initial bind

# Right-align the SQL query text area and Save button
# with the CLOSE button at the bottom of the GUI.
# The CLOSE button (width=10, height=2) starts at close_button_x_coordinate
# and is approximately 90 pixels wide on Windows, 100 on Mac.
_close_right_edge = GUI_IO_util.close_button_x_coordinate + 90

def _align_widgets_to_close(event=None):
    target_right = _close_right_edge
    text_left = GUI_IO_util.labels_x_coordinate

    # Align SQL query text area
    SQL_query_entry.place(width=target_right - text_left)

    # Align Save SQL query button so its right edge matches
    window.update_idletasks()
    save_btn_width = save_query_button.winfo_reqwidth()
    save_query_button.place(x=target_right - save_btn_width)

    # Align Generate and + Target buttons to same right edge as Save SQL query
    gen_btn_width = generate_cross_btn.winfo_reqwidth()
    generate_cross_btn.place(x=target_right - gen_btn_width)
    # No alignment needed for + button (it sits inline)

window.after(100, _align_widgets_to_close)

y_multiplier_integer=y_multiplier_integer+4.5

def display_SQL(*args):
    was_disabled = (SQL_query_entry.cget('state') == 'disabled')
    if was_disabled:
        SQL_query_entry.configure(state='normal')
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
        SQL_text=SQL_text+ "[Table1].[field1], [Table1].[field2]\n  FROM [Table1]\n  LEFT JOIN [Table2] ON [Table1].[field1]=[Table2].[field1]\n  WHERE [Table2].[field1] IS NULL;"
    elif auto_SQL_var.get()=="SQL union":
        SQL_text=SQL_text+ "[Table1_Field] AS Field1\n  FROM [Table1]\n\nUNION\n\nSELECT [Table2_Field] AS Field1\n  FROM [Table2]\n  ORDER BY Field1;"
    elif auto_SQL_var.get()=="SQL join":
        SQL_text=SQL_text+ "[Table1_Field1], [Table1_Field2], ...\n  FROM [Table1]\n  JOIN [Table2] ON [Table1].[Table1_Field1]=[Table2].[Table2_Field1]"
    elif auto_SQL_var.get()=="SQL left join":
        SQL_text=SQL_text+ "[Table1].[field1], [Table2].[field2]\n  FROM [Table1]\n  LEFT JOIN [Table2] ON [Table1].[field1]=[Table2].[field1];"
    elif auto_SQL_var.get()=="SQL update":
        SQL_text='UPDATE [table]\n  SET [field] = "new value"\n  WHERE [field2] = "condition";'
    elif auto_SQL_var.get()=="SQL subquery":
        SQL_text=SQL_text+ "[field1], [field2]\n  FROM [Table1]\n  WHERE [field1] IN (\n    SELECT [field1] FROM [Table2]\n  );"
    elif auto_SQL_var.get()=="SQL group concat":
        SQL_text=SQL_text+ "[field1], GROUP_CONCAT([field2], '; ') AS Combined\n  FROM [table]\n  GROUP BY [field1]\n  ORDER BY [field1];"
    elif auto_SQL_var.get()=="SQL case":
        SQL_text=SQL_text+ "[field1],\n  CASE\n    WHEN [field2] = 'value1' THEN 'Category A'\n    WHEN [field2] = 'value2' THEN 'Category B'\n    ELSE 'Other'\n  END AS Category\n  FROM [table];"
    else:
        SQL_query_var.set('')
        SQL_query_entry.delete(0.1, tk.END)
    SQL_query_var.set(SQL_text)
    SQL_query_entry.insert("end", str(SQL_text))
    if was_disabled:
        SQL_query_entry.configure(state='disabled')
auto_SQL_var.trace('w',display_SQL)
#SQL_query_var.trace('w',display_SQL)

display_SQL()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

# TIPS_lookup = {'No TIPS available':''}
# TIPS_options='No TIPS available'

TIPS_lookup = {'SQL template queries':'TIPS_NLP_SQL Template Queries.pdf',
               'PC-ACE tables analyzer via Pandas':'TIPS_NLP_PC-ACE ACCESS DB Analyzer.pdf',
               'PC-ACE - Export ACCESS tables to Excel':'TIPS_NLP_PC-ACE - Export ACCESS tables to Excel.pdf',
               'SVO automatic extraction and visualization': 'TIPS_NLP_SVO extraction and visualization.pdf',
               "Google Earth Pro": "TIPS_NLP_GIS_Google Earth Pro.pdf",
               "Google API Key": "TIPS_NLP_GIS_Google API Key.pdf",
               "Geocoding": "TIPS_NLP_GIS_Geocoding.pdf",
               "Geocoding: How to Improve Nominatim": "TIPS_NLP_GIS_Geocoding Nominatim.pdf",
               "Gephi network graphs": "TIPS_NLP_Gephi network graphs.pdf",
               "Word clouds":"TIPS_NLP_Wordclouds Visualizing word clouds.pdf"
               }
TIPS_options='SQL template queries', 'PC-ACE tables analyzer via Pandas', 'PC-ACE - Export ACCESS tables to Excel', 'SVO automatic extraction and visualization', 'Google Earth Pro', 'Google API Key', 'Geocoding', 'Geocoding: How to Improve Nominatim', 'Gephi network graphs', 'Word clouds'

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

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Click View table relations to open the PC-ACE table relations diagram.\nClick View grammar to export the grammar.\nClick Update grammar to refresh the grammar in setup_complex.\nClick Open PC-ACE analyzer to open the PC-ACE data analyzer GUI with the current input directory." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "Use the Complex object and Simplex object dropdown menus to insert object names into your SQL query.\n\nThe SQLite database is constructed automatically when the input directory is selected." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "Cross-complex query generator: select a SOURCE and TARGET complex type, then click Generate to automatically build a SQL query that navigates the PC-ACE hierarchy.\n\nOptionally filter the source by selecting a simplex name and entering a LIKE pattern (e.g. %woman% or lynching).\n\nHover over the Generate SQL query button to see the current object selection." + GUI_IO_util.msg_Esc)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, using the 'Select DB table' dropdown menu, select the table available in the SQLite database.\n\nOnce an SQLite table has been selected, use the 'Select DB table field' dropdown menu to select a specific field available in the selected table.\n\nUsing the Templates dropdown menu select the type of SQL query for which to display a standard template (e.g., UNION, JOIN). You will need to change table names and field names to the appropriate names in your database.\n\nTick the Distinct checkbox to display the SQL query as distinct\n\nClick Import SQL query to load a previously saved query.\nClick Save SQL query to save the current query to a file." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Enter an SQL query in the form SELECT ...\n\nYou can also generate a new SQL query, import a saved query or use a template from the dropdown menu.\n\nHover over the query area to see the name of the currently loaded query."+ GUI_IO_util.msg_Esc)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer+4.5,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer -1
"COUNT Display a template SQL COUNT query."
"DUPLICATES The query builds a temporary table of duplicate records, then, depending on user's choice, extracts only one occurrence of all duplicate records or all duplicate occurrences except one (all DISTINCT records will not be displayed). Query results can be used to move occurrences of objects for which multiples should not be allowed."
"UNMATCHED Automatically build a simple query that will give a list of all unmatched records between any two given tables/queries on the basis of a specific field (MEMO type fields cannot be matched!)\n\nThe query will give you a list of the fields in the first selected table/query that do not find a match in the second selected table/query."

content_y_multiplier_integer = y_multiplier_integer
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,increment)
y_multiplier_integer = max(y_multiplier_integer, content_y_multiplier_integer)

# change the value of the readMe_message
readMe_message="This Python 3 script can construct an SQLite relational database from a set of input csv files characterized by the presence of overlapping relational fields.\n\nThe script allows to perform SQL queries on any sqlite databases thus constructed."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

# Auto-select database if launched with --db argument (e.g., from PC-ACE analyzer)
# Also accept --querydir to set the directory for importing SQL query files
_pcace_query_dir = ''
if '--db' in sys.argv:
    try:
        db_idx = sys.argv.index('--db')
        db_file = sys.argv[db_idx + 1]
        if os.path.exists(db_file):
            select_SQLite_DB_var.set(db_file)
    except (IndexError, ValueError):
        pass
if '--querydir' in sys.argv:
    try:
        qd_idx = sys.argv.index('--querydir')
        _pcace_query_dir = sys.argv[qd_idx + 1]
    except (IndexError, ValueError):
        pass

# Auto-set input/output directories when launched from PC-ACE analyzer
# and force the RUN button enabled since the database is already created
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
# When launched from PC-ACE analyzer, force RUN button and all widgets enabled
# since the database and output directory are already set
if select_SQLite_DB_var.get() != '' and GUI_util.output_dir_path.get() != '':
    GUI_util.run_button.configure(state='normal')
    _enable_all_widgets()

GUI_util.window.mainloop()
