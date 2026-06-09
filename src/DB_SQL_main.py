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
import DB_PCACE_data_analysis_util

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
        for fn, rename_cols in DB_PCACE_data_analysis_util.reading_list:
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
            # Deduplicate column names: if pandas added .1, .2 suffixes
            # for duplicate columns, keep only the first occurrence
            if df.columns.duplicated().any():
                df = df.loc[:, ~df.columns.duplicated()]
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
            if source_complex_var.get() or target_complex_var.get() or _saved_pairs:
                mb.showwarning(title='Warning',
                               message='There are objects selected in the cross-complex query widgets. '
                                       'Please, click on the Generate SQL query button first and then RUN.')
            else:
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

        # Split on unique marker to handle multiple queries (e.g. different-source pairs)
        _QUERY_SEP = '-- @@NEXT_QUERY@@'
        if _QUERY_SEP in SQL_query_var:
            _raw_queries = [q.strip() for q in SQL_query_var.split(_QUERY_SEP) if q.strip()]
        else:
            _raw_queries = [SQL_query_var.strip()]
        if not _raw_queries:
            mb.showwarning(title='Warning', message='The SQL query area is empty.')
            return

        try:
            sql_rows = cur.execute(_raw_queries[0])
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
            colNames.append(col[0])
        results.append(colNames)
        for row in sql_rows:
            results.append(row)

        # Execute any additional queries (different-source pairs)
        _extra_results_list = []
        for _qi in range(1, len(_raw_queries)):
            try:
                _extra_rows = cur.execute(_raw_queries[_qi])
                _extra_cols = [col[0] for col in cur.description]
                _extra_data = [_extra_cols]
                for row in _extra_rows:
                    _extra_data.append(row)
                _extra_results_list.append(_extra_data)
            except Exception as e:
                print(f"  WARNING: additional query {_qi+1} failed: {e}")
        # Build meaningful output filename from cross-complex query name if available
        qname = query_name_var.get() if query_name_var.get() else ''

        # For PC-ACE cross-complex/source-only queries, use a PCACE subfolder (same as analyzer GUI)
        if (qname.startswith('Cross-complex:') or qname.startswith('Source-only:')) and inputDir:
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
            # Use only leaf complex names for a readable filename.
            body = qname.replace('Cross-complex:', '').strip()
            pair_strs = [p.strip() for p in body.split(';')]
            leaf_parts = []
            for pair_str in pair_strs:
                arrow_parts = pair_str.split('→')
                for ap in arrow_parts:
                    for sub in ap.split(','):
                        leaf = sub.strip().split('.')[-1].strip().replace(' ', '_')
                        if leaf:
                            leaf_parts.append(leaf)
            if leaf_parts:
                csv_name = 'SQL_{}.csv'.format('_'.join(leaf_parts))
            else:
                csv_name = 'sql_result.csv'
        elif qname.startswith('Source-only:'):
            src_part = qname.replace('Source-only:', '').strip().replace(', ', '_').replace(' ', '_')
            csv_name = 'SQL_{}.csv'.format(src_part)
        else:
            csv_name = 'sql_result.csv'
        csv_full_path = outputDir + os.sep + csv_name
        filesToOpen = [csv_full_path]
        IO_csv_util.list_to_csv(GUI_util.window, results, csv_full_path, colnum=0)

        # Write extra query results (different-source pairs) as separate CSVs
        for _ei, _extra_data in enumerate(_extra_results_list):
            _extra_name = csv_name.replace('.csv', '_{}.csv'.format(_ei + 2))
            _extra_path = outputDir + os.sep + _extra_name
            IO_csv_util.list_to_csv(GUI_util.window, _extra_data, _extra_path, colnum=0)
            filesToOpen.append(_extra_path)

        # Auto-populate the INPUT CSV file widget with the output CSV
        csv_file_var.set(csv_full_path)
        _refresh_csv_columns()

        # Auto-generate charts for cross-complex query results
        if (qname.startswith('Cross-complex:') or qname.startswith('Source-only:')) and chartPackage != 'No charts':
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

# Fix blue highlight on ttk.Combobox widgets (Windows theme paints
# the field blue when the widget has focus or is selected).
_style = ttk.Style()
_style.map('TCombobox', selectbackground=[('readonly', 'white'), ('disabled', 'white'),
                                           ('focus', 'white'), ('!focus', 'white')],
                        selectforeground=[('readonly', 'black'), ('disabled', 'black'),
                                           ('focus', 'black'), ('!focus', 'black')])
window.option_add('*TCombobox*Listbox.selectBackground', '#0078D7')
window.option_add('*TCombobox*Listbox.selectForeground', 'white')

select_SQLite_DB_var=tk.StringVar()
csv_file_var= tk.StringVar()
select_DB_tables_var=tk.StringVar()
select_DB_table_fields_var=tk.StringVar()
SQL_query_var=tk.StringVar()
distinct_var=tk.IntVar()
view_relations_var=tk.IntVar()

def clear(e):
    where_simplex_var.set('')
    where_operator_var.set('LIKE')
    where_value_var.set('')
    source_complex_var.set('')
    source_simplex_var.set('')
    target_complex_var.set('')
    target_simplex_var.set('')
    _saved_pairs.clear()
    _saved_extra_children.clear()
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
    # Re-populate WHERE filter dropdown from the CSV that is still loaded
    _refresh_csv_columns()
window.bind("<Escape>", clear)

_SQLITE_VERSION = 4  # bump when _build_sqlite column mappings change (4 = added setup_xref_Simplex_Document rename)

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
    "CREATE INDEX IF NOT EXISTS idx_xcc_higher ON data_xref_Complex_Complex(ID_data_complex_higher)",
    "CREATE INDEX IF NOT EXISTS idx_xcc_lower ON data_xref_Complex_Complex(ID_data_complex_lower)",
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
    "CREATE INDEX IF NOT EXISTS idx_xcc_lower_higher ON data_xref_Complex_Complex(ID_data_complex_lower, ID_data_complex_higher)",
    "CREATE INDEX IF NOT EXISTS idx_xcc_higher_lower ON data_xref_Complex_Complex(ID_data_complex_higher, ID_data_complex_lower)",
    # Document cross-reference indexes for document simplex queries
    "CREATE INDEX IF NOT EXISTS idx_xcd_complex ON data_xref_Complex_Document(ID_data_complex)",
    "CREATE INDEX IF NOT EXISTS idx_xcd_document ON data_xref_Complex_Document(ID_data_document)",
    "CREATE INDEX IF NOT EXISTS idx_xssd_document ON data_xref_Simplex_Simplex_Document(ID_data_document)",
    "CREATE INDEX IF NOT EXISTS idx_xssd_xrefid ON data_xref_Simplex_Simplex_Document(ID_setup_xref_simplex_document)",
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
        for btn in (open_gui_menu, view_relations_button,
                    view_grammar_button, update_grammar_button,
                    add_object_btn, generate_cross_btn,
                    import_query_button, save_query_button):
            btn.configure(state='disabled')
        for cb in (expand_complex_cb, _coalesce_src_cb, _coalesce_tgt_cb, distinct_checkbox):
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
        for btn in (open_gui_menu, view_relations_button,
                    view_grammar_button, update_grammar_button,
                    add_object_btn, generate_cross_btn,
                    import_query_button, save_query_button):
            btn.configure(state='normal')
        for cb in (expand_complex_cb, _coalesce_src_cb, _coalesce_tgt_cb, distinct_checkbox):
            cb.configure(state='normal')
        for combo in (source_complex_menu, source_simplex_menu,
                      target_complex_menu, target_simplex_menu):
            combo.configure(state='readonly')
        # NOTE: WHERE filter widgets (where_simplex_menu, where_operator_menu,
        # where_value_entry, filter_csv_button) are NOT enabled here — they are
        # controlled exclusively by _refresh_csv_columns() when a CSV is loaded.
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
    DB_PCACE_data_analysis_util.view_grammar(os.path.join(inputDir.get(), 'setup_Complex.xlsx'),
                                             'GrammarRule_Text', os.path.join(inputDir.get(),
                                                                              'PC-ACE grammar for database ' + tail + '.txt'))

def update_grammar():
    if inputDir.get() == '':
        mb.showwarning(title='Warning', message='No input directory selected.')
        return
    DB_PCACE_data_analysis_util.update_grammar_text(inputDir.get())

def open_pcace_analyzer():
    """Launch the PC-ACE data analysis GUI with the current input/output directories."""
    in_dir = inputDir.get() if hasattr(inputDir, 'get') else inputDir
    out_dir = outputDir.get() if hasattr(outputDir, 'get') else outputDir
    if not in_dir or not os.path.isdir(in_dir):
        mb.showwarning(title='Warning', message='No input directory selected.\n\nPlease, select a PC-ACE input directory first.')
        return
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DB_PCACE_data_analysis_main.py')
    cmd = [sys.executable, script_path]
    if in_dir:
        cmd.extend(['--inputdir', in_dir])
    if out_dir:
        cmd.extend(['--outputdir', out_dir])
    subprocess.Popen(cmd)

def open_data_manipulation():
    """Launch the data manipulation GUI with the current CSV file."""
    csv_path = csv_file_var.get()
    out_dir = outputDir.get() if hasattr(outputDir, 'get') else outputDir
    if not csv_path or not os.path.isfile(csv_path):
        mb.showwarning(title='Warning',
                       message='No CSV file currently loaded.\n\nPlease, run a query first or select an INPUT csv file.')
        return
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_manipulation_main.py')
    cmd = [sys.executable, script_path, '--inputfile', csv_path]
    if out_dir:
        cmd.extend(['--outputdir', out_dir])
    subprocess.Popen(cmd)

def open_data_validation():
    """Launch the data validation GUI with the current CSV file."""
    csv_path = csv_file_var.get()
    out_dir = outputDir.get() if hasattr(outputDir, 'get') else outputDir
    if not csv_path or not os.path.isfile(csv_path):
        mb.showwarning(title='Warning',
                       message='No CSV file currently loaded.\n\nPlease, run a query first or select an INPUT csv file.')
        return
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DB_PCACE_data_validation_main.py')
    cmd = [sys.executable, script_path, '--inputfile', csv_path]
    if out_dir:
        cmd.extend(['--outputdir', out_dir])
    subprocess.Popen(cmd)

def _on_open_gui_selected(choice):
    if choice == 'Open PC-ACE data analysis GUI':
        open_pcace_analyzer()
    elif choice == 'Open data manipulation GUI':
        open_data_manipulation()
    elif choice == 'Open data validation GUI':
        open_data_validation()

_open_gui_var = tk.StringVar()
_open_gui_var.set('Open PC-ACE data analysis GUI')
open_gui_menu = tk.OptionMenu(window, _open_gui_var,
                              'Open PC-ACE data analysis GUI',
                              'Open data manipulation GUI',
                              'Open data validation GUI',
                              command=_on_open_gui_selected)
open_gui_menu.configure(width=25, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_gui_menu,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to open a related GUI.\n\n"
                                   "   Open PC-ACE data analysis GUI: opens the PC-ACE data analysis with the current input directory.\n"
                                   "   Open data manipulation GUI: opens the data manipulation GUI with the current CSV file.\n"
                                   "   Open data validation GUI: opens the data validation and cleaning GUI with the current CSV file.")

def get_csv_file(window,title,fileType,annotate):
    #csv_file_var.set('')
    if csv_file!='':
        initialFolder=os.path.dirname(os.path.abspath(csv_file_var.get()))
    else:
        initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)

    if len(filePath)>0:
        nRecords, nColumns =IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(filePath, 'utf-8')
        if nRecords==0:
            mb.showwarning(title='Warning',
                           message="The selected input csv file is empty.\n\nPlease, select a different file and try again.")
            filePath=''
        else:
            csv_file_var.set(filePath)
    return filePath

csv_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT CSV file',command=lambda: get_csv_file(window,'Select INPUT csv file', [("csv files", "*.csv")],True))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               csv_file_button, True)

#setup a button to open Windows Explorer on the selected input directory
openInputFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, csv_file_var.get()))
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,openInputFile_button,
                    True, False, True,False, 90, GUI_IO_util.IO_configuration_menu, "Open INPUT csv file")

csv_file=tk.Entry(window, width=GUI_IO_util.csv_file_width - 8, textvariable=csv_file_var)
csv_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,csv_file, True)

def _clear_csv_file():
    """Clear the INPUT CSV file and reset the WHERE filter widgets."""
    csv_file_var.set('')
    where_simplex_var.set('')
    where_operator_var.set('LIKE')
    where_value_var.set('')

clear_csv_button = tk.Button(window, text='Clear', width=5, command=lambda: _clear_csv_file())
y_multiplier_integer = GUI_IO_util.placeWidget(window, 1150, y_multiplier_integer,
                                               clear_csv_button, False, False, True, False, 90,
                                               GUI_IO_util.open_setup_x_coordinate,
                                               "Click to clear the INPUT CSV file and reset the WHERE filter.")

headers = IO_csv_util.get_csvfile_headers(csv_file_var.get()) if csv_file_var.get() else []

def _refresh_csv_columns(*args):
    """Populate the WHERE-filter column dropdown from the headers of
    the currently selected CSV file."""
    csv_path = csv_file_var.get()
    if csv_path and os.path.isfile(csv_path):
        hdrs = IO_csv_util.get_csvfile_headers(csv_path)
        if hdrs:
            where_simplex_menu['values'] = [''] + hdrs
            where_simplex_menu.config(state='readonly')
            where_operator_menu.config(state='readonly')
            where_value_entry.config(state='normal')
            filter_csv_button.config(state='normal')
            return
    # No valid CSV — disable
    where_simplex_menu['values'] = []
    where_simplex_menu.config(state='disabled')
    where_operator_menu.config(state='disabled')
    where_value_entry.config(state='disabled')
    filter_csv_button.config(state='disabled')

## NOTE: csv_file_var trace is registered AFTER all widgets are created (see below)

def _apply_csv_filter():
    """Apply the WHERE filter to the current INPUT CSV file, or generate
    a frequency chart if no filter value is entered.

    - Column selected + value entered → filter rows and save filtered CSV
    - Column selected + no value → frequency distribution (bar chart + wordcloud)
    """
    csv_path = csv_file_var.get()
    if not csv_path or not os.path.isfile(csv_path):
        mb.showwarning(title='Warning', message='No INPUT CSV file selected.\n\nPlease select a CSV file first.')
        return

    col = where_simplex_var.get()
    val = where_value_var.get().strip()
    op = where_operator_var.get() or 'LIKE'

    if not col:
        mb.showwarning(title='Warning', message='Please select a column first.')
        return

    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except Exception as e:
        mb.showwarning(title='Error', message=f'Could not read CSV file.\n\n{e}')
        return

    if col not in df.columns:
        mb.showwarning(title='Warning', message=f'Column "{col}" not found in the CSV file.')
        return

    # No value → frequency distribution chart for the selected column
    if not val:
        _chart_column_frequency(df, col, csv_path)
        return

    # Value entered → filter rows
    col_series = df[col].astype(str)
    if op == 'LIKE':
        pattern = val.replace('%', '.*')
        mask = col_series.str.contains(pattern, case=False, na=False, regex=True)
    elif op == 'NOT LIKE':
        pattern = val.replace('%', '.*')
        mask = ~col_series.str.contains(pattern, case=False, na=False, regex=True)
    elif op == '=':
        mask = col_series.str.lower() == val.lower()
    elif op == '!=':
        mask = col_series.str.lower() != val.lower()
    else:
        mask = col_series.str.contains(val, case=False, na=False)

    filtered = df[mask]
    if len(filtered) == 0:
        mb.showinfo(title='Filter result', message=f'No rows match the filter:\n{col} {op} {val}\n\n({len(df)} rows checked)')
        return

    # Save filtered CSV with _filtered suffix
    base, ext = os.path.splitext(csv_path)
    out_path = base + '_filtered' + ext
    filtered.to_csv(out_path, index=False, encoding='utf-8')
    csv_file_var.set(out_path)

    mb.showinfo(title='Filter result',
                message=f'Filtered {len(filtered)} of {len(df)} rows where:\n{col} {op} {val}\n\nSaved to:\n{os.path.basename(out_path)}')
    IO_files_util.openFile(window, out_path)


def _chart_column_frequency(df, col, csv_path):
    """Generate a frequency bar chart and wordcloud for a single column."""
    import re as _re
    def _safe_fn(s):
        return _re.sub(r'[<>:"/\\|?*]', '_', s).replace(' ', '_')

    col_data = df[col].dropna().astype(str)
    col_data = col_data[col_data != '']
    if col_data.empty:
        mb.showinfo(title='Frequency', message=f'Column "{col}" has no non-empty values.')
        return

    out_dir = GUI_util.output_dir_path.get()
    if not out_dir or not os.path.isdir(out_dir):
        out_dir = os.path.dirname(csv_path)

    base_name = _safe_fn(os.path.splitext(os.path.basename(csv_path))[0])
    safe_col = _safe_fn(col)
    filesToOpen = []

    # Bar chart (top 30)
    try:
        import plotly.express as px
        freq = col_data.value_counts().head(30)
        freq_df = freq.reset_index()
        freq_df.columns = [col, 'Frequency']
        fig = px.bar(freq_df, x=col, y='Frequency',
                     title=f'Top 30 Frequency: {col}')
        fig.update_xaxes(type='category')
        bar_file = os.path.join(out_dir, f'{base_name}_{safe_col}_bar.html')
        fig.write_html(bar_file)
        filesToOpen.append(bar_file)
    except Exception as e:
        print(f"  WARNING: Bar chart: {e}")

    # Wordcloud
    try:
        from wordcloud import WordCloud
        word_freq = col_data.value_counts().to_dict()
        wc = WordCloud(width=1200, height=600, background_color='white',
                       max_words=200).generate_from_frequencies(word_freq)
        wc_file = os.path.join(out_dir, f'{base_name}_{safe_col}_wordcloud.png')
        wc.to_file(wc_file)
        filesToOpen.append(wc_file)
    except Exception as e:
        print(f"  WARNING: Wordcloud: {e}")

    if filesToOpen:
        IO_files_util.OpenOutputFiles(window, True, filesToOpen, out_dir, '')
    else:
        mb.showinfo(title='Frequency',
                    message=f'Column "{col}": {col_data.nunique()} unique values, {len(col_data)} total')

# ── WHERE filter row ──────────────────────────────────────────────────────
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


# drop_column_lb = tk.Label(window, text='Select columns')
# y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate+20, y_multiplier_integer,
#                                                drop_column_lb, True)
#
where_filter_lb = tk.Label(window, text='Select CSV file column')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 20, y_multiplier_integer,
                                               where_filter_lb, True)

where_simplex_var = tk.StringVar()
where_simplex_menu = ttk.Combobox(window, textvariable=where_simplex_var, state='disabled', width=35)
_add_typeahead(where_simplex_menu)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 150, y_multiplier_integer,
                                               where_simplex_menu, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 150,
                                               "Select a CSV file column to filter or chart (requires an INPUT CSV file).\nWith a value: filters rows matching the condition.\nWithout a value: generates frequency bar chart and wordcloud.")

# Operator (=, LIKE, !=)
where_operator_var = tk.StringVar()
where_operator_menu = ttk.Combobox(window, textvariable=where_operator_var, state='disabled', width=5,
                                    values=['LIKE', '=', '!=', 'NOT LIKE'])
where_operator_var.set('LIKE')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 430, y_multiplier_integer,
                                               where_operator_menu, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 430,
                                               "SQL comparison operator.\nLIKE supports wildcards: %woman% matches any value containing 'woman'.\n= requires exact match.\n!= excludes exact match.\nNOT LIKE excludes pattern.")

# Value entry
where_value_var = tk.StringVar()
where_value_entry = tk.Entry(window, textvariable=where_value_var, width=20, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 520, y_multiplier_integer,
                                               where_value_entry, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 520,
                                               "Enter the filter value or pattern (requires an INPUT CSV file).\nFor LIKE, use % as wildcard (e.g., %lynching%, %woman%).\nFor =, enter the exact value.\nLeave empty and click Filter for frequency chart.")

add_filter_btn = tk.Button(window, width=2, text='+', state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 670, y_multiplier_integer,
                                               add_filter_btn, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 647,
                                               "Click to add another filter condition.")

# Filter button — applies the WHERE filter or charts frequency if no value
filter_csv_button = tk.Button(window, text='Filter', width=6, state='disabled', command=lambda: _apply_csv_filter())
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 710, y_multiplier_integer,
                                               filter_csv_button, False, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 710,
                                               "Click to apply the WHERE filter to the INPUT CSV file (requires an INPUT CSV file).\nThe filtered result is saved as a new CSV with '_filtered' suffix.")

# Register trace AFTER all CSV/WHERE widgets exist to avoid NameError
csv_file_var.trace('w', _refresh_csv_columns)

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
    _sql_setup_complex_menu, _sql_setup_simplex_menu = DB_PCACE_data_analysis_util.get_setup_complex_simplex_names()
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
        c_menu, s_menu = DB_PCACE_data_analysis_util.get_setup_complex_simplex_names()
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
        success = DB_PCACE_data_analysis_util.toggle_required_value(obj_type, obj_name, new_val, GUI_util.input_main_dir_path.get())
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
                                               "Object 1 (COMPLEX): select a source complex type (e.g., Individual, Event, Participant-S).\n\nObject 1 can be used alone (source-only query) or paired with Object 3 (cross-complex query).\nWhen used alone, the query extracts the simplex attributes of this complex type.\nWhen paired with Object 3, the query joins Object 1 to Object 3 across the PC-ACE hierarchy.")

# OBJECT 2 ---------------------------------------------------------------------------------------
source_simplex_var = tk.StringVar()
source_simplex_menu = ttk.Combobox(window, textvariable=source_simplex_var, state='disabled', width=17)
_add_typeahead(source_simplex_menu)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 310, y_multiplier_integer,
                                               source_simplex_menu, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 310,
                                               "Object 2 (SIMPLEX): select the simplex attribute of Object 1 (e.g., Name; * for all).\n\nIf Object 1 has no direct simplexes (e.g., Participant-S), this dropdown shows child complex types prefixed with '>'.\nClick a child (e.g., > Individual) to drill into its simplexes and pick one (e.g., Name).\nUse '<< back' to return to the children list.\n\nObject 2 works the same whether or not Object 3 is selected.")
# MERGE (COALESCE) CHECKBOX — source side (next to Object 2) ─────────────
_coalesce_src_var = tk.IntVar(value=0)
_coalesce_src_cb = tk.Checkbutton(window, text='', variable=_coalesce_src_var, onvalue=1, offvalue=0, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 468, y_multiplier_integer,
                                               _coalesce_src_cb, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 468,
                                               "Merge (COALESCE) source children.\n\nWhen checked: Enter-selected sibling children of Object 2 are MERGED into ONE column\n(e.g. Individual.Name + Collective.Name → one Actor Name column).\n\nWhen unchecked: Enter-selected siblings produce SEPARATE columns\n(e.g. Individual.Name column + Collective.Name column side by side).")

# OBJECT 3 ---------------------------------------------------------------------------------------
target_complex_var = tk.StringVar()
target_complex_menu = ttk.Combobox(window, textvariable=target_complex_var, state='disabled', width=20)
_add_typeahead(target_complex_menu)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 500, y_multiplier_integer,
                                               target_complex_menu, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate+500,
                                               "Object 3 (COMPLEX, optional): select a target complex type to join with Object 1 (e.g., Simple process, City).\n\nLeave Object 3 empty for a source-only query that extracts only Object 1's simplex attributes.\nWhen filled, the query navigates the PC-ACE hierarchy from Object 1 to Object 3 and returns both.\n\nYou can select ANY complex type as the target — Object 1 and Object 3 do not need to share a common parent.\nThe query generator uses a breadth-first search to find a path through the hierarchy, navigating up and down\nthrough any number of intermediate nodes (e.g., up to the Semantic Triplet hub, then down to the target branch).\n\nClick + to save the current selection and add more pairs.")
# OBJECT 4 ---------------------------------------------------------------------------------------
target_simplex_var = tk.StringVar()
target_simplex_menu = ttk.Combobox(window, textvariable=target_simplex_var, state='disabled', width=17)
_add_typeahead(target_simplex_menu)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 680, y_multiplier_integer,
                                               target_simplex_menu, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate+500,
                                               "Object 4 (SIMPLEX): select the simplex attribute of Object 3 (e.g., Verbal phrase; * for all).\n\nIf Object 3 has no direct simplexes, this dropdown shows child complex types prefixed with '>'.\nClick a child to drill into its simplexes and pick one.\nUse '<< back' to return to the children list.\n\nObject 4 is only used when Object 3 is selected. Leave both empty for a source-only query.")
# MERGE (COALESCE) CHECKBOX — target side (next to Object 4) ─────────────
_coalesce_tgt_var = tk.IntVar(value=0)
_coalesce_tgt_cb = tk.Checkbutton(window, text='', variable=_coalesce_tgt_var, onvalue=1, offvalue=0, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 838, y_multiplier_integer,
                                               _coalesce_tgt_cb, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 838,
                                               "Merge (COALESCE) target children.\n\nWhen checked: Enter-selected sibling children of Object 4 are MERGED into ONE column\n(e.g. Individual.Name + Collective.Name → one Actor Name column).\n\nWhen unchecked: Enter-selected siblings produce SEPARATE columns\n(e.g. Individual.Name column + Collective.Name column side by side).")
# + ADD OBJECTS ---------------------------------------------------------------------------------------
add_object_btn = tk.Button(window, width=2, text='+', state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 865, y_multiplier_integer,
                                               add_object_btn, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate+400,
                                               "Click + to save the current selection and add more pairs.\n\nYou can save a cross-complex pair (Object 1 + Object 3) or a source-only pair (Object 1 only, no Object 3).\nEach + resets the dropdowns so you can build the next pair.\n\nExample: Participant-S → Process (+), then Participant-O alone (Generate).")
# EXPAND OBJECTS ---------------------------------------------------------------------------------------
expand_complex_var = tk.IntVar(value=1)
expand_complex_cb = tk.Checkbutton(window, text='', variable=expand_complex_var, onvalue=1, offvalue=0, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 900, y_multiplier_integer,
                                               expand_complex_cb, True, False, True, False, 90,
                                               GUI_IO_util.open_reminders_x_coordinate,
                                               "Expand any complex object with no simplex attributes to its lowest complex with available simplex children.")

generate_cross_btn = tk.Button(window, width=15, text='Generate SQL query', state='disabled')
_gen_btn_y_row = y_multiplier_integer  # save for dynamic hover-over re-binding
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 960, y_multiplier_integer,
                                               generate_cross_btn, False, False, True, False, 90,
                                               GUI_IO_util.open_TIPS_x_coordinate,
                                               "Click to generate the SQL query for the selected objects.\nClick RUN after the SQL query is displayed in the SQL query area.")


# ── Extra objects (accumulated via the + button) ─────────────────────────
_saved_pairs = []  # list of 6-tuples: (src, src_child, src_sx, tgt, tgt_child, tgt_sx)
_saved_extra_children = []  # parallel list of (src_extras_set, tgt_extras_set)
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
    # Saved pairs (6-tuples: src, src_child, src_sx, tgt, tgt_child, tgt_sx)
    for pi, (s, s_child, ssx, t, t_child, tsx) in enumerate(_saved_pairs):
        parts.append('{}:{}'.format(obj_num, s))
        obj_num += 1
        sx_label = ssx or '*'
        if s_child:
            path_str = '.'.join(s_child) if isinstance(s_child, list) else s_child
            sx_label = '{}.{}'.format(path_str, sx_label)
        if pi < len(_saved_extra_children):
            s_extras, _ = _saved_extra_children[pi]
            if s_extras:
                sx_label += '+COALESCE({})'.format(','.join(sorted(s_extras)))
        parts.append('{}:{}'.format(obj_num, sx_label))
        obj_num += 1
        if t is not None:
            parts.append('{}:{}'.format(obj_num, t))
            obj_num += 1
            tx_label = tsx or '*'
            if t_child:
                path_str = '.'.join(t_child) if isinstance(t_child, list) else t_child
                tx_label = '{}.{}'.format(path_str, tx_label)
            if pi < len(_saved_extra_children):
                _, t_extras = _saved_extra_children[pi]
                if t_extras:
                    tx_label += '+COALESCE({})'.format(','.join(sorted(t_extras)))
            parts.append('{}:{}'.format(obj_num, tx_label))
            obj_num += 1
    # Current (unsaved) selection
    src = source_complex_var.get()
    if src:
        parts.append('{}:{}'.format(obj_num, src))
        obj_num += 1
        src_sx = source_simplex_var.get() or '*'
        # Show drilled path context if applicable
        try:
            src_drilled = _drilled_child.get(id(source_simplex_menu))
        except NameError:
            src_drilled = None
        if src_drilled and not src_sx.startswith('> ') and not src_sx.startswith('<< '):
            src_sx = '{}.{}'.format('.'.join(src_drilled), src_sx)
        # Show extras indicator for current extra children
        cur_src_extras = _get_extra_children(source_simplex_menu)
        if cur_src_extras:
            _merge_tag = 'COALESCE' if _coalesce_src_var.get() else 'SEPARATE'
            src_sx += '+{}({})'.format(_merge_tag, ','.join(sorted(cur_src_extras)))
        parts.append('{}:{}'.format(obj_num, src_sx))
        obj_num += 1
    tgt = target_complex_var.get()
    if tgt:
        parts.append('{}:{}'.format(obj_num, tgt))
        obj_num += 1
        tgt_sx = target_simplex_var.get() or '*'
        try:
            tgt_drilled = _drilled_child.get(id(target_simplex_menu))
        except NameError:
            tgt_drilled = None
        if tgt_drilled and not tgt_sx.startswith('> ') and not tgt_sx.startswith('<< '):
            tgt_sx = '{}.{}'.format('.'.join(tgt_drilled), tgt_sx)
        cur_tgt_extras = _get_extra_children(target_simplex_menu)
        if cur_tgt_extras:
            _merge_tag = 'COALESCE' if _coalesce_tgt_var.get() else 'SEPARATE'
            tgt_sx += '+{}({})'.format(_merge_tag, ','.join(sorted(cur_tgt_extras)))
        parts.append('{}:{}'.format(obj_num, tgt_sx))
    text = ', '.join(parts) if parts else ''
    extra_targets_var.set(text)
    # Update the hover-over text of the Generate button to show the current selection
    if text:
        wrapped_parts = []
        for p in text.split(', '):
            wrapped_parts.append(p)
        selection_line = 'Object selection:\n  ' + '\n  '.join(wrapped_parts)
    else:
        selection_line = 'No objects selected yet.'
    _gen_btn_hover_text = ("Click to generate the SQL query for the selected objects.\n"
                           "Click RUN after the SQL query is displayed in the SQL query area.\n\n"
                           + selection_line)
    # Re-bind hover-over with updated text; position tooltip at left edge
    generate_cross_btn.bind('<Enter>',
        lambda e, t=_gen_btn_hover_text: (
            e.widget.config(background='red', foreground='black'),
            GUI_IO_util.display_widget_info(window, e,
                GUI_IO_util.labels_x_coordinate + 960,
                GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step * _gen_btn_y_row,
                GUI_IO_util.labels_x_coordinate, t)))


def _add_object():
    """Save current Object 1 + Object 2 pair and reset all 4 dropdowns.
    Pairs are stored as 6-tuples:
        (src, src_child, src_sx, tgt, tgt_child, tgt_sx)
    where src_child/tgt_child is the drilled child complex (or None).
    Target fields are None for source-only pairs (Object 1 without Object 3).

    Behavior depends on the 'Merge' checkbox:
      - Checked (COALESCE mode): extra Enter-selected children are stored in
        _saved_extra_children for merging into one column.
      - Unchecked (separate columns): extra children produce additional pairs
        (one per selected child), each as its own column."""
    src = source_complex_var.get()
    tgt = target_complex_var.get()
    if not src:
        mb.showwarning(title='Warning', message='Please select at least Object 1 before clicking +.')
        return
    src, src_child, src_sx = _resolve_simplex_selection(src, source_simplex_var.get(), source_simplex_menu)
    if tgt:
        tgt, tgt_child, tgt_sx = _resolve_simplex_selection(tgt, target_simplex_var.get(), target_simplex_menu)
    else:
        tgt, tgt_child, tgt_sx = None, None, None

    src_extras = set(_get_extra_children(source_simplex_menu))
    tgt_extras = set(_get_extra_children(target_simplex_menu)) if tgt else set()
    src_merge = _coalesce_src_var.get()   # per-side merge checkbox
    tgt_merge = _coalesce_tgt_var.get() if tgt else 0

    # Determine what goes into COALESCE vs separate pairs
    src_coalesce = src_extras if src_merge else set()
    tgt_coalesce = tgt_extras if tgt_merge else set()
    src_separate = set() if src_merge else src_extras
    tgt_separate = set() if tgt_merge else tgt_extras

    # Primary pair (with any COALESCE extras)
    _saved_pairs.append((src, src_child, src_sx, tgt, tgt_child, tgt_sx))
    _saved_extra_children.append((src_coalesce, tgt_coalesce))
    # Expand separate source extras into individual pairs
    for extra_src in sorted(src_separate):
        _saved_pairs.append((src, extra_src, src_sx, tgt, tgt_child, tgt_sx))
        _saved_extra_children.append((set(), set()))
    # Expand separate target extras into individual pairs
    for extra_tgt in sorted(tgt_separate):
        _saved_pairs.append((src, src_child, src_sx, tgt, extra_tgt, tgt_sx))
        _saved_extra_children.append((set(), set()))

    # Reset all 4 dropdowns and merge checkboxes for next pair
    source_complex_var.set('')
    source_simplex_var.set('')
    target_complex_var.set('')
    target_simplex_var.set('')
    _coalesce_src_var.set(0)
    _coalesce_tgt_var.set(0)
    # Label updates automatically via trace


add_object_btn.configure(command=_add_object)
source_complex_var.trace('w', _update_extra_targets_label)
source_simplex_var.trace('w', _update_extra_targets_label)
target_complex_var.trace('w', _update_extra_targets_label)
target_simplex_var.trace('w', _update_extra_targets_label)
_coalesce_src_var.trace('w', _update_extra_targets_label)
_coalesce_tgt_var.trace('w', _update_extra_targets_label)


def _ensure_libraries_loaded():
    """Load PC-ACE libraries if needed."""
    input_dir = GUI_util.input_main_dir_path.get() if hasattr(GUI_util.input_main_dir_path, 'get') else ''
    if input_dir and os.path.isdir(input_dir):
        try:
            if DB_PCACE_data_analysis_util.setup_Complex_lib is None:
                DB_PCACE_data_analysis_util.build_libraries(input_dir, input_dir)
        except (AttributeError, NameError):
            try:
                DB_PCACE_data_analysis_util.build_libraries(input_dir, input_dir)
            except Exception as e:
                print(f"  WARNING loading libraries: {e}")


def _expand_if_no_simplex(complex_name, child_name=None):
    """If a complex has no simplex attributes, return its children that do.
    Returns a list of (parent_complex, child_complex, simplex) 3-tuples."""
    effective = (child_name[-1] if isinstance(child_name, list) and child_name else child_name) or complex_name
    names = DB_PCACE_data_analysis_util.get_cross_complex_simplex_names(effective)
    if names:
        return [(complex_name, child_name, None)]
    children = DB_PCACE_data_analysis_util.get_children_with_simplexes(effective)
    if children:
        return [(complex_name, c, None) for c in children]
    return [(complex_name, child_name, None)]


def _expand_pairs(pairs):
    """Expand pairs where source or target has no simplexes (replace with children).
    Input and output are 6-tuples: (src, src_child, src_sx, tgt, tgt_child, tgt_sx).
    Target fields may be None for source-only pairs."""
    expanded = []
    for src, src_child, src_sx, tgt, tgt_child, tgt_sx in pairs:
        # Expand source if needed
        src_list = [(src, src_child, src_sx)]
        if not src_sx:
            effective_src = (src_child[-1] if isinstance(src_child, list) and src_child else src_child) or src
            src_names = DB_PCACE_data_analysis_util.get_cross_complex_simplex_names(effective_src)
            if not src_names:
                src_list = _expand_if_no_simplex(src, src_child)
        # Expand target if needed (skip for source-only pairs)
        if tgt is None:
            for s, sc, ssx in src_list:
                expanded.append((s, sc, ssx, None, None, None))
        else:
            tgt_list = [(tgt, tgt_child, tgt_sx)]
            if not tgt_sx:
                effective_tgt = (tgt_child[-1] if isinstance(tgt_child, list) and tgt_child else tgt_child) or tgt
                tgt_names = DB_PCACE_data_analysis_util.get_cross_complex_simplex_names(effective_tgt)
                if not tgt_names:
                    tgt_list = _expand_if_no_simplex(tgt, tgt_child)
            for s, sc, ssx in src_list:
                for t, tc, tsx in tgt_list:
                    expanded.append((s, sc, ssx, t, tc, tsx))
    return expanded


def _resolve_simplex_selection(complex_name, simplex_val, simplex_combo):
    """Resolve a simplex dropdown selection.

    Returns a 3-tuple: (parent_complex, drill_path_or_None, simplex_or_None)

    The parent complex is ALWAYS the original complex shown in Object 1/3.
    The drill_path is a list of child complex names representing the drill
    path (e.g., ['Individual', 'Personal Characteristics'] for a two-level
    drill).  None when not drilled.

    Three cases:
    1. Drilled into a child (e.g., Participant-S → Individual → Personal Characteristics):
       - '*'   → (Participant-S, ['Individual', 'Personal Characteristics'], None)
       - 'Race'→ (Participant-S, ['Individual', 'Personal Characteristics'], Race)
    2. Showing children (not drilled):
       - '*'       → (Participant-S, None, None) — expand all children
       - '> Child' → (Participant-S, ['Child'], None) — all simplexes of child
    3. Showing simplexes directly (complex has its own simplexes):
       - '*'   → (Individual, None, None) — all simplexes
       - 'Name'→ (Individual, None, Name) — specific simplex
    """
    # Case 1: drilled into a child complex (path is a list)
    drilled = _drilled_child.get(id(simplex_combo))
    if drilled:
        if not simplex_val or simplex_val == '*':
            return complex_name, list(drilled), None
        if simplex_val.startswith('<< '):
            return complex_name, None, None
        return complex_name, list(drilled), simplex_val

    # Case 2: showing children (not drilled)
    if not simplex_val or simplex_val == '*':
        return complex_name, None, None
    if simplex_val.startswith('> ') or simplex_val.startswith('✓ '):
        child_name = simplex_val[2:]
        return complex_name, [child_name], None

    # Case 3: normal simplex (including Doc > prefixed document simplex names)
    return complex_name, None, simplex_val


def _get_extra_children(simplex_combo):
    """Return the set of Enter-selected children for multi-child COALESCE,
    EXCLUDING the primary drilled child (which is already handled).
    Returns an empty set if no extra children were selected."""
    try:
        sel = _selected_children.get(id(simplex_combo), set())
        drilled = _drilled_child.get(id(simplex_combo))
    except NameError:
        return set()
    if drilled:
        # Exclude the first child in the drill path (the primary drilled child
        # at the same level as the selected siblings)
        primary = drilled[0] if isinstance(drilled, list) else drilled
        return sel - {primary}
    return set()

def _child_str(child):
    """Convert a drill-path list to the single child name the util functions expect."""
    if isinstance(child, list):
        return child[-1] if child else None
    return child

def _generate_cross_complex_query():
    # Collect all pairs: saved + current (if complete)
    all_pairs = list(_saved_pairs)
    all_extras = list(_saved_extra_children)  # parallel list of (src_extras, tgt_extras)
    cur_src = source_complex_var.get()
    cur_tgt = target_complex_var.get()
    if cur_src and cur_tgt:
        src, src_child, src_sx = _resolve_simplex_selection(cur_src, source_simplex_var.get(), source_simplex_menu)
        tgt, tgt_child, tgt_sx = _resolve_simplex_selection(cur_tgt, target_simplex_var.get(), target_simplex_menu)
        cur_src_extras = set(_get_extra_children(source_simplex_menu))
        cur_tgt_extras = set(_get_extra_children(target_simplex_menu))
        src_merge = _coalesce_src_var.get()
        tgt_merge = _coalesce_tgt_var.get()

        src_coalesce = cur_src_extras if src_merge else set()
        tgt_coalesce = cur_tgt_extras if tgt_merge else set()
        src_separate = set() if src_merge else cur_src_extras
        tgt_separate = set() if tgt_merge else cur_tgt_extras

        # Primary pair (with any COALESCE extras)
        all_pairs.append((src, src_child, src_sx, tgt, tgt_child, tgt_sx))
        all_extras.append((src_coalesce, tgt_coalesce))
        # Expand separate extras into individual pairs
        for extra_src in sorted(src_separate):
            all_pairs.append((src, extra_src, src_sx, tgt, tgt_child, tgt_sx))
            all_extras.append((set(), set()))
        for extra_tgt in sorted(tgt_separate):
            all_pairs.append((src, src_child, src_sx, tgt, extra_tgt, tgt_sx))
            all_extras.append((set(), set()))
    elif cur_src and not cur_tgt:
        src, src_child, src_sx = _resolve_simplex_selection(cur_src, source_simplex_var.get(), source_simplex_menu)
        cur_src_extras = set(_get_extra_children(source_simplex_menu))
        src_merge = _coalesce_src_var.get()
        src_coalesce = cur_src_extras if src_merge else set()
        src_separate = set() if src_merge else cur_src_extras
        all_pairs.append((src, src_child, src_sx, None, None, None))
        all_extras.append((src_coalesce, set()))
        for extra_src in sorted(src_separate):
            all_pairs.append((src, extra_src, src_sx, None, None, None))
            all_extras.append((set(), set()))

    if not all_pairs:
        mb.showwarning(title='Warning', message='Please select at least Object 1.')
        return

    # Collect WHERE filter (optional)
    _where_simplex = where_simplex_var.get() or None
    _where_value = where_value_var.get().strip() or None
    _where_operator = where_operator_var.get() or 'LIKE'

    _ensure_libraries_loaded()

    # Expand complex types with no simplexes to their children (if checkbox is checked)
    if expand_complex_var.get():
        all_pairs = _expand_pairs(all_pairs)

    # Pad all_extras to match all_pairs length (expansion may have changed count)
    while len(all_extras) < len(all_pairs):
        all_extras.append((set(), set()))

    # Separate source-only pairs (no target) from cross-complex pairs
    source_only_pairs = [(i, p) for i, p in enumerate(all_pairs) if p[3] is None]
    cross_pairs = [(i, p) for i, p in enumerate(all_pairs) if p[3] is not None]

    if source_only_pairs and not cross_pairs:
        # All pairs are source-only — generate source-only queries
        all_queries = []
        all_warnings = []
        for idx, (src, src_child, src_sx, _, _, _) in source_only_pairs:
            se = all_extras[idx][0] if idx < len(all_extras) else set()
            # Detect document simplex selections (prefixed with "Doc > ")
            src_doc_simplex = None
            if src_sx and src_sx.startswith('Doc > '):
                src_doc_simplex = src_sx[6:]
                src_sx = None
            query, info = DB_PCACE_data_analysis_util.generate_source_only_query(
                src,
                source_filter_simplex=src_sx,
                source_filter_value=_where_value,
                source_filter_operator=_where_operator,
                where_simplex=_where_simplex,
                source_child=_child_str(src_child),
                source_extra_children=se or None,
                source_document_simplex=src_doc_simplex)
            if query is None:
                mb.showwarning(title='Warning', message=str(info))
                return
            all_queries.append(query)
            if isinstance(info, dict) and info.get('warnings'):
                all_warnings.extend(info['warnings'])
        SQL_query_entry.delete(0.1, tk.END)
        SQL_query_entry.insert("end", '\n\n-- @@NEXT_QUERY@@\n\n'.join(all_queries))
        src_labels = []
        for _, (src, src_child, _, _, _, _) in source_only_pairs:
            src_labels.append('{}.{}'.format(src, src_child) if src_child else src)
        query_name_var.set('Source-only: {}'.format(', '.join(src_labels)))
        if all_warnings:
            mb.showinfo(title='Simplex attributes', message='\n\n'.join(all_warnings))

    elif not source_only_pairs and len(cross_pairs) == 1:
        # Single cross-complex pair: use the original (faster) single-target generator
        idx, (src, src_child, src_simplex, tgt_name, tgt_child, tgt_simplex) = cross_pairs[0]
        src_extras, tgt_extras = all_extras[idx]
        # Detect document simplex selections (prefixed with "Doc > ")
        src_doc_simplex = None
        tgt_doc_simplex = None
        if src_simplex and src_simplex.startswith('Doc > '):
            src_doc_simplex = src_simplex[6:]
            src_simplex = None
        if tgt_simplex and tgt_simplex.startswith('Doc > '):
            tgt_doc_simplex = tgt_simplex[6:]
            tgt_simplex = None
        query, result = DB_PCACE_data_analysis_util.generate_cross_complex_query(
            src, tgt_name,
            source_filter_simplex=src_simplex,
            source_filter_value=_where_value,
            source_filter_operator=_where_operator,
            where_simplex=_where_simplex,
            target_simplex=tgt_simplex,
            source_child=_child_str(src_child),
            target_child=_child_str(tgt_child),
            source_extra_children=src_extras or None,
            target_extra_children=tgt_extras or None,
            source_document_simplex=src_doc_simplex,
            target_document_simplex=tgt_doc_simplex)
        if query is None:
            mb.showwarning(title='Warning', message=str(result))
            return
        SQL_query_entry.delete(0.1, tk.END)
        SQL_query_entry.insert("end", query)
        src_path_str = '.'.join([src] + src_child) if src_child else src
        tgt_path_str = '.'.join([tgt_name] + tgt_child) if tgt_child else tgt_name
        query_name_var.set('Cross-complex: {} → {}'.format(src_path_str, tgt_path_str))
        warnings = []
        effective_src = src_child[-1] if src_child else src
        if not DB_PCACE_data_analysis_util.get_cross_complex_simplex_names(effective_src):
            children = DB_PCACE_data_analysis_util.get_children_with_simplexes(effective_src)
            msg = "'{}' has no simplex attributes.".format(effective_src)
            if children:
                msg += "\nTry: {}".format(', '.join(children))
            warnings.append(msg)
        effective_tgt = tgt_child[-1] if tgt_child else tgt_name
        if not DB_PCACE_data_analysis_util.get_cross_complex_simplex_names(effective_tgt):
            children = DB_PCACE_data_analysis_util.get_children_with_simplexes(effective_tgt)
            msg = "'{}' has no simplex attributes.".format(effective_tgt)
            if children:
                msg += "\nTry: {}".format(', '.join(children))
            warnings.append(msg)
        if warnings:
            mb.showinfo(title='Simplex attributes', message='\n\n'.join(warnings))

    else:
        # Multiple pairs (possibly mixed source-only and cross-complex)
        # Generate each pair individually and concatenate
        all_queries = []
        pair_labels = []
        for pi, (src, src_child, src_sx, tgt, tgt_child, tgt_sx) in enumerate(all_pairs):
            se, te = all_extras[pi] if pi < len(all_extras) else (set(), set())
            # Detect document simplex selections
            src_doc_sx = None
            tgt_doc_sx = None
            if src_sx and src_sx.startswith('Doc > '):
                src_doc_sx = src_sx[6:]
                src_sx = None
            if tgt_sx and tgt_sx.startswith('Doc > '):
                tgt_doc_sx = tgt_sx[6:]
                tgt_sx = None
            if tgt is None:
                q, info = DB_PCACE_data_analysis_util.generate_source_only_query(
                    src, source_filter_simplex=src_sx,
                    source_child=_child_str(src_child),
                    source_extra_children=se or None,
                    source_document_simplex=src_doc_sx)
                src_l = '.'.join([src] + src_child) if src_child else src
                pair_labels.append(src_l)
            else:
                q, info = DB_PCACE_data_analysis_util.generate_cross_complex_query(
                    src, tgt, source_filter_simplex=src_sx, target_simplex=tgt_sx,
                    source_child=_child_str(src_child), target_child=_child_str(tgt_child),
                    source_extra_children=se or None, target_extra_children=te or None,
                    source_document_simplex=src_doc_sx, target_document_simplex=tgt_doc_sx)
                src_l = '.'.join([src] + src_child) if src_child else src
                tgt_l = '.'.join([tgt] + tgt_child) if tgt_child else tgt
                pair_labels.append('{} → {}'.format(src_l, tgt_l))
            if q:
                all_queries.append(q)
        if not all_queries:
            mb.showwarning(title='Warning', message='Could not generate queries for the selected pairs.')
            return
        # Check if all cross-pairs share the same source — use multi-target generator
        cross_only = [p for p in all_pairs if p[3] is not None]
        cross_sources = set((s, tuple(sc) if sc else None, ssx) for s, sc, ssx, _, _, _ in cross_only) if cross_only else set()
        if not source_only_pairs and len(cross_sources) == 1 and len(cross_only) > 1:
            src, src_child_tup, src_simplex = list(cross_sources)[0]
            src_child = list(src_child_tup) if src_child_tup else None
            targets = [(t, tc, tsx) for _, _, _, t, tc, tsx in cross_only]
            se0 = all_extras[0][0] if all_extras else set()
            tgt_extras_list = [all_extras[i][1] if i < len(all_extras) else set()
                               for i in range(len(all_pairs))]
            query, info = DB_PCACE_data_analysis_util.generate_multi_target_query(
                src, source_simplex=src_simplex, targets=targets,
                source_child=_child_str(src_child),
                source_extra_children=se0 or None,
                target_extra_children_list=tgt_extras_list or None)
            if query is None:
                mb.showwarning(title='Warning', message=str(info))
                return
            SQL_query_entry.delete(0.1, tk.END)
            SQL_query_entry.insert("end", query)
            tgt_names = [t[0] for t in targets]
            src_label = '.'.join([src] + src_child) if src_child else src
            query_name_var.set('Cross-complex: {} → {}'.format(src_label, ', '.join(tgt_names)))
            if info.get('warnings'):
                mb.showinfo(title='Simplex attributes', message='\n\n'.join(info['warnings']))
        else:
            SQL_query_entry.delete(0.1, tk.END)
            SQL_query_entry.insert("end", '\n\n-- @@NEXT_QUERY@@\n\n'.join(all_queries))
            query_name_var.set('Query: {}'.format('; '.join(pair_labels)))


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
    _saved_extra_children.clear()
    _update_extra_targets_label()
    _complex_names_cache = []
    # Clear SQL query area and query name
    try:
        SQL_query_entry.delete("1.0", tk.END)
        SQL_query_var.set('')
        query_name_var.set('')
    except (NameError, tk.TclError):
        pass
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


# Track which simplex dropdowns are showing child complex names instead of simplex names.
# Key = combo widget id, Value = True if showing children, False if showing simplexes.
_simplex_showing_children = {}

# Track the drill-down path per simplex combo.
# Key = combo widget id, Value = list of child complex names representing the
# drill path (e.g., ['Individual', 'Personal Characteristics'] means
# top-level → Individual → Personal Characteristics).
# When set, the combo is showing the deepest child's simplexes.
_drilled_child = {}

# Track Enter-selected children for multi-child COALESCE.
# Key = combo widget id, Value = set of child complex names.
# When multiple children are selected, the SQL merges their simplex values
# into one column using COALESCE (matched by simplex Order position).
_selected_children = {}

def _populate_simplex_menu(complex_var, simplex_combo, simplex_var):
    """Populate a simplex Combobox based on the selected complex type.
    If the complex has no direct simplex attributes, show child complex
    names instead (prefixed with '> ') so the user can pick which child
    to drill into."""
    simplex_combo['values'] = ()
    simplex_var.set('')
    _simplex_showing_children[id(simplex_combo)] = False
    _drilled_child.pop(id(simplex_combo), None)
    _selected_children.pop(id(simplex_combo), None)
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
            # Get direct simplex attributes
            cur.execute("""SELECT DISTINCT ss.Name
                           FROM setup_xref_Simplex_Complex sxsc
                           JOIN setup_Simplex ss ON ss.ID_setup_simplex = sxsc.ID_setup_simplex
                           WHERE sxsc.ID_setup_complex = ?
                           ORDER BY ss.Name""", (cid,))
            names = [r[0] for r in cur.fetchall()]
            # Always check for child complex types too
            cur.execute("""SELECT DISTINCT sc_child.Name
                           FROM setup_xref_Complex_Complex sxcc
                           JOIN setup_Complex sc_child
                               ON sc_child.ID_setup_complex = sxcc.LowerComplex
                           WHERE sxcc.HigherComplex = ?
                           ORDER BY sc_child.Name""", (cid,))
            children = [r[0] for r in cur.fetchall()]
            # Get document-level simplex attributes (date, newspaper name, etc.)
            doc_names = []
            try:
                cur.execute('SELECT DISTINCT ss.Name'
                           ' FROM setup_xref_Simplex_Document sxsd'
                           ' JOIN setup_Simplex ss ON ss.ID_setup_simplex = sxsd.ID_setup_simplex'
                           ' ORDER BY sxsd."Order"')
                doc_names = [r[0] for r in cur.fetchall()]
            except Exception as e1:
                try:
                    cur.execute('SELECT DISTINCT ss.Name'
                               ' FROM setup_xref_Simplex_Document sxsd'
                               ' JOIN setup_Simplex ss ON ss.ID_setup_simplex = sxsd.Simplex'
                               ' ORDER BY sxsd."Order"')
                    doc_names = [r[0] for r in cur.fetchall()]
                except Exception as e2:
                    print(f"  WARNING: Could not query document simplex names: {e1} / {e2}")
            doc_entries = ['Doc > ' + n for n in doc_names]
            if names and children:
                simplex_combo['values'] = ['*'] + names + ['> ' + c for c in children] + doc_entries
                simplex_var.set('*')
                _simplex_showing_children[id(simplex_combo)] = True
            elif names:
                simplex_combo['values'] = ['*'] + names + doc_entries
                simplex_var.set('*')
            elif children:
                simplex_combo['values'] = ['*'] + ['> ' + c for c in children] + doc_entries
                simplex_var.set('*')
                _simplex_showing_children[id(simplex_combo)] = True
            elif doc_entries:
                simplex_combo['values'] = ['*'] + doc_entries
                simplex_var.set('*')
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  WARNING populating simplex menu: {e}")

def _populate_source_simplex(*args):
    _populate_simplex_menu(source_complex_var, source_simplex_menu, source_simplex_var)
    # NOTE: WHERE filter dropdown is populated from CSV headers by
    # _refresh_csv_columns(), NOT from grammar simplex names.
    # Warn if showing children instead of simplexes
    cname = source_complex_var.get()
    if cname and _simplex_showing_children.get(id(source_simplex_menu), False):
        children = [v[2:] for v in source_simplex_menu['values'] if v.startswith('> ')]
        mb.showinfo(title='No simplex attributes',
                    message="'{}' has no direct simplex attributes.\n\n"
                            "Object 2 shows child complex types instead:\n{}\n\n"
                            "Click a child (e.g., > Individual) to drill into its "
                            "simplexes and pick one (e.g., Name).\n"
                            "Or select * for all children and all simplexes.".format(
                                cname, ', '.join(children)))

def _populate_target_simplex(*args):
    _populate_simplex_menu(target_complex_var, target_simplex_menu, target_simplex_var)
    # Warn if showing children instead of simplexes
    cname = target_complex_var.get()
    if cname and _simplex_showing_children.get(id(target_simplex_menu), False):
        children = [v[2:] for v in target_simplex_menu['values'] if v.startswith('> ')]
        mb.showinfo(title='No simplex attributes',
                    message="'{}' has no direct simplex attributes.\n\n"
                            "Object 4 shows child complex types instead:\n{}\n\n"
                            "Click a child to drill into its simplexes and pick one.\n"
                            "Or select * for all children and all simplexes.".format(
                                cname, ', '.join(children)))

def _drill_into_child(child_name, simplex_combo, simplex_var, complex_var):
    """Navigate into a child complex, showing its simplexes (or its children
    if it has no simplexes).  Used by both click-drill and Enter-then-drill.
    Supports arbitrary-depth drill: each call appends to the drill path."""
    path = _drilled_child.get(id(simplex_combo), [])
    path = list(path)  # copy
    path.append(child_name)
    _drilled_child[id(simplex_combo)] = path
    _simplex_showing_children[id(simplex_combo)] = False
    db_path = select_SQLite_DB_var.get()
    if not db_path or not os.path.exists(db_path):
        return
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT ID_setup_complex FROM setup_Complex WHERE Name=?",
                    (child_name,))
        row = cur.fetchone()
        if row:
            cid = row[0]
            cur.execute("""SELECT DISTINCT ss.Name
                           FROM setup_xref_Simplex_Complex sxsc
                           JOIN setup_Simplex ss
                                ON ss.ID_setup_simplex = sxsc.ID_setup_simplex
                           WHERE sxsc.ID_setup_complex = ?
                           ORDER BY ss.Name""", (cid,))
            names = [r[0] for r in cur.fetchall()]
            # Back label shows the immediate parent (one level up)
            if len(path) > 1:
                back_parent = path[-2]
            else:
                back_parent = complex_var.get()
            sel = _selected_children.get(id(simplex_combo), set())
            back_label = '<< ' + back_parent
            if len(sel) > 1:
                back_label += '  [{} children selected]'.format(len(sel))
            # Always check for child complex types too
            cur.execute("""SELECT DISTINCT sc2.Name
                           FROM setup_xref_Complex_Complex sxcc
                           JOIN setup_Complex sc2
                               ON sc2.ID_setup_complex = sxcc.LowerComplex
                           WHERE sxcc.HigherComplex = ?
                           ORDER BY sc2.Name""", (cid,))
            grandchildren = [r[0] for r in cur.fetchall()]
            child_items = []
            for c in grandchildren:
                if c in sel:
                    child_items.append('✓ ' + c)
                else:
                    child_items.append('> ' + c)
            # Get document-level simplex attributes
            doc_entries = []
            try:
                cur.execute('SELECT DISTINCT ss.Name'
                           ' FROM setup_xref_Simplex_Document sxsd'
                           ' JOIN setup_Simplex ss ON ss.ID_setup_simplex = sxsd.ID_setup_simplex'
                           ' ORDER BY sxsd."Order"')
                doc_entries = ['Doc > ' + r[0] for r in cur.fetchall()]
            except Exception:
                try:
                    cur.execute('SELECT DISTINCT ss.Name'
                               ' FROM setup_xref_Simplex_Document sxsd'
                               ' JOIN setup_Simplex ss ON ss.ID_setup_simplex = sxsd.Simplex'
                               ' ORDER BY sxsd."Order"')
                    doc_entries = ['Doc > ' + r[0] for r in cur.fetchall()]
                except Exception:
                    pass
            if names and child_items:
                simplex_combo['values'] = [back_label, '*'] + names + child_items + doc_entries
                simplex_var.set('*')
                _simplex_showing_children[id(simplex_combo)] = True
            elif names:
                simplex_combo['values'] = [back_label, '*'] + names + doc_entries
                simplex_var.set('*')
            elif child_items:
                simplex_combo['values'] = [back_label, '*'] + child_items + doc_entries
                simplex_var.set('*')
                _simplex_showing_children[id(simplex_combo)] = True
            else:
                simplex_combo['values'] = [back_label, '*'] + doc_entries
                simplex_var.set('*')
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  WARNING drill-down: {e}")


def _go_back_to_children(complex_var, simplex_combo, simplex_var):
    """Go back ONE level in the drill path, PRESERVING accumulated
    _selected_children so the user can drill into another sibling
    without losing previous selections.

    Multi-level: if path is [Individual, Personal Characteristics],
    going back pops to [Individual] and shows Individual's children+simplexes.
    Going back from [Individual] pops to [] and shows the top-level complex's children."""
    path = _drilled_child.get(id(simplex_combo), [])
    sel = _selected_children.get(id(simplex_combo), set())

    if path:
        path = list(path)
        path.pop()  # go up one level
        if path:
            _drilled_child[id(simplex_combo)] = path
        else:
            _drilled_child.pop(id(simplex_combo), None)

    # Determine which complex to show children of
    if path:
        parent_name = path[-1]
    else:
        parent_name = complex_var.get()
    if not parent_name:
        return
    db_path = select_SQLite_DB_var.get()
    if not db_path or not os.path.exists(db_path):
        return
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT ID_setup_complex FROM setup_Complex WHERE Name=?", (parent_name,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return
        cid = row[0]
        # Get direct simplexes of this complex
        cur.execute("""SELECT DISTINCT ss.Name
                       FROM setup_xref_Simplex_Complex sxsc
                       JOIN setup_Simplex ss ON ss.ID_setup_simplex = sxsc.ID_setup_simplex
                       WHERE sxsc.ID_setup_complex = ?
                       ORDER BY ss.Name""", (cid,))
        parent_simplexes = [r[0] for r in cur.fetchall()]
        # Get child complex types
        cur.execute("""SELECT DISTINCT sc_child.Name
                       FROM setup_xref_Complex_Complex sxcc
                       JOIN setup_Complex sc_child
                           ON sc_child.ID_setup_complex = sxcc.LowerComplex
                       WHERE sxcc.HigherComplex = ?
                       ORDER BY sc_child.Name""", (cid,))
        children = [r[0] for r in cur.fetchall()]
        if not children and not parent_simplexes:
            cur.close()
            conn.close()
            _populate_simplex_menu(complex_var, simplex_combo, simplex_var)
            return
        # Rebuild list: back label + direct simplexes + children with ✓/> marks
        child_items = []
        for c in children:
            if c in sel:
                child_items.append('✓ ' + c)
            else:
                child_items.append('> ' + c)
        # If we're still drilled (path not empty), show a back label
        if path:
            if len(path) > 1:
                back_parent = path[-2]
            else:
                back_parent = complex_var.get()
            back_label = '<< ' + back_parent
            simplex_combo['values'] = [back_label, '*'] + parent_simplexes + child_items
        else:
            simplex_combo['values'] = ['*'] + parent_simplexes + child_items
        simplex_var.set('*')
        _simplex_showing_children[id(simplex_combo)] = True
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  WARNING go-back: {e}")


def _handle_simplex_drill(event, simplex_combo, simplex_var, complex_var):
    """Handle CLICK on a simplex dropdown item.

    - '> Child' or '✓ Child': drill into that child's simplexes
    - '<< Parent': go back to top level
    - Anything else: normal simplex selection (no action needed)"""
    val = simplex_var.get()
    if val.startswith('> ') or val.startswith('✓ '):
        child_name = val[2:]
        # Only track as sibling selection at the first drill level.
        # Deeper drilling is navigation, not sibling selection for COALESCE.
        path = _drilled_child.get(id(simplex_combo), [])
        if not path:
            sel = _selected_children.setdefault(id(simplex_combo), set())
            sel.add(child_name)
        _drill_into_child(child_name, simplex_combo, simplex_var, complex_var)
    elif val.startswith('<< '):
        # Go back ONE level in the drill path WITHOUT clearing accumulated selections.
        if simplex_combo is source_simplex_menu:
            _coalesce_src_var.set(0)
        elif simplex_combo is target_simplex_menu:
            _coalesce_tgt_var.set(0)
        _go_back_to_children(complex_var, simplex_combo, simplex_var)


def _handle_simplex_enter(event, simplex_combo, simplex_var, complex_var):
    """Handle ENTER key on a simplex dropdown item.

    At the children level, Enter TOGGLES selection of a child without
    drilling.  This lets the user select multiple children (e.g., both
    Individual and Collective actor).

    What happens with Enter-selected children depends on the 'Merge' checkbox:
      - Checked: children are MERGED via COALESCE into one column.
      - Unchecked: children produce SEPARATE columns (one per child).

    After selecting children with Enter, click one to drill into its
    simplexes — the chosen simplex will be extracted from ALL selected
    children."""
    val = simplex_var.get()
    if not val:
        return
    # Only works on child items (> or ✓ prefix), and only at the first
    # drill level.  Deeper levels are navigation, not sibling selection.
    if val.startswith('> ') or val.startswith('✓ '):
        path = _drilled_child.get(id(simplex_combo), [])
        if path:
            return  # Enter-selection only works at the top children level
        child_name = val[2:]
        sel = _selected_children.setdefault(id(simplex_combo), set())
        # Toggle
        if child_name in sel:
            sel.discard(child_name)
        else:
            sel.add(child_name)
        # Rebuild the dropdown values with updated ✓ marks
        current_values = list(simplex_combo['values'])
        new_values = []
        for v in current_values:
            if v.startswith('> ') or v.startswith('✓ '):
                cname = v[2:]
                if cname in sel:
                    new_values.append('✓ ' + cname)
                else:
                    new_values.append('> ' + cname)
            else:
                new_values.append(v)
        simplex_combo['values'] = new_values
        # Update the display to show the toggled state
        if child_name in sel:
            simplex_var.set('✓ ' + child_name)
        else:
            simplex_var.set('> ' + child_name)
        # Show feedback
        if sel:
            print("  Selected children: {}".format(', '.join(sorted(sel))))


source_simplex_menu.bind('<<ComboboxSelected>>',
    lambda e: _handle_simplex_drill(e, source_simplex_menu, source_simplex_var, source_complex_var))
target_simplex_menu.bind('<<ComboboxSelected>>',
    lambda e: _handle_simplex_drill(e, target_simplex_menu, target_simplex_var, target_complex_var))
source_simplex_menu.bind('<Return>',
    lambda e: _handle_simplex_enter(e, source_simplex_menu, source_simplex_var, source_complex_var))
target_simplex_menu.bind('<Return>',
    lambda e: _handle_simplex_enter(e, target_simplex_menu, target_simplex_var, target_complex_var))

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

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Use the dropdown menu to open a related GUI.\n\n   Open PC-ACE data analysis GUI: opens the PC-ACE data analysis with the current input directory.\n   Open data manipulation GUI: opens the data manipulation GUI with the current CSV file.\n   Open data validation GUI: opens the data validation and cleaning GUI with the current CSV file." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "The INPUT csv file widget displays a csv filename. There are two ways of entering a filename.\n\n   1. Click on the button 'Select INPUT csv file' to select a file of your choice.\n\n   2. The text widget is filled automatically as soon as produced by the query Generator.\n\nClick the small button between the 'Select...' button and the text widget to open the file and visualize its content.\n\nClick the 'Clear' button to remove the loaded CSV and reset the WHERE filter." + GUI_IO_util.msg_openFile)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "WHERE filter (requires an INPUT CSV file): select a column, then enter a filter value and click Filter to extract matching rows.\n\n"
                   "Leave the value empty and click Filter to generate a frequency bar chart and wordcloud for the selected column.\n\n"
                   "Operators: LIKE (with % wildcard), =, !=, NOT LIKE."+ GUI_IO_util.msg_Esc)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Click View table relations to open the PC-ACE table relations diagram.\nClick View grammar to export the grammar.\nClick Update grammar to refresh the grammar in setup_complex.\nUse the Object dropdown to toggle the REQUIRED boolean for complex or simplex objects." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help",
                                                         "Cross-complex query generator: build SQL queries that extract or join complex types across the PC-ACE hierarchy.\n\n"
                                                         "WIDGETS:\n"
                                                         "   Object 1 (COMPLEX): the source complex type (e.g., Individual, Event, Participant-S).\n"
                                                         "   Object 2 (SIMPLEX): the simplex attribute of Object 1 to display (e.g., Name; * for all).\n"
                                                         "      If Object 1 has no direct simplexes (e.g., Participant-S), this dropdown shows child complex types\n"
                                                         "      prefixed with '>' — click a child (e.g., > Individual) to drill into its simplexes and pick one\n"
                                                         "      (e.g., Name for actor names). Use '<< back' to return to the children list.\n"
                                                         "   Object 3 (COMPLEX, optional): the target complex type to join with Object 1. Leave empty for a source-only query.\n"
                                                         "      You can select ANY complex type — Object 1 and Object 3 do not need to share a common parent.\n"
                                                         "      The query generator finds a path through the hierarchy automatically (up and down through\n"
                                                         "      intermediate nodes, e.g., up to the Semantic Triplet hub, then down to the target branch).\n"
                                                         "   Object 4 (SIMPLEX): same as Object 2 but for Object 3. Only used when Object 3 is selected.\n\n"
                                                         "TWO MODES:\n"
                                                         "   Cross-complex: fill Object 1 + Object 3 to join two complex types (e.g., Participant-S → Process).\n"
                                                         "   Source-only: fill only Object 1 + Object 2 (leave Object 3/4 empty) to extract simplex attributes of one complex type.\n\n"
                                                         "MIXING MODES with the + button:\n"
                                                         "   You can mix cross-complex and source-only pairs. For example:\n"
                                                         "   1. Set Object 1=Participant-S, Object 3=Process, click +\n"
                                                         "   2. Set Object 1=Participant-O (leave Object 3 empty), click Generate\n"
                                                         "   This produces two queries: one joining Participant-S to Process, one extracting Participant-O's attributes.\n\n"
                                                         "Example SVO: Object 1=Participant-S, Object 2=drill into > Individual then pick Name,\n"
                                                         "   Object 3=Process, Object 4=drill into > Simple process then pick Verbal phrase.\n\n"
                                                         "Hover over the Generate SQL query button to see the current object selection." + GUI_IO_util.msg_Esc)

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
