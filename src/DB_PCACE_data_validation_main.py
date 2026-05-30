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
import pandas as pd
import subprocess

import IO_csv_util
import IO_files_util
import GUI_IO_util
import IO_user_interface_util
import TIPS_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, outputDir, openOutputFiles, chartPackage, dataTransformation):

    config_filename = GUI_util.config_filename_selected_config.get()

    csv_path = csv_file_var.get()
    if not csv_path or not os.path.isfile(csv_path):
        mb.showwarning(title='Warning',
                       message='No CSV file selected.\n\nPlease, select an INPUT csv file and try again.')
        return

    # Placeholder — validation logic will go here
    mb.showinfo(title='Info',
                message='Data validation GUI is ready.\n\nValidation features will be added here.')

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
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DB_PCACE_data_analyzer_main.py')
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
csv_file_entry = tk.Entry(window, width=GUI_IO_util.csv_file_width - 8, textvariable=csv_file_var)
csv_file_entry.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                                               csv_file_entry, True)

# Clear button
def _clear_csv_file():
    csv_file_var.set('')

clear_csv_button = tk.Button(window, text='Clear', width=5, command=lambda: _clear_csv_file())
y_multiplier_integer = GUI_IO_util.placeWidget(window, 1150, y_multiplier_integer,
                                               clear_csv_button, False, False, True, False, 90,
                                               GUI_IO_util.open_setup_x_coordinate,
                                               "Click to clear the INPUT CSV file.")

# ── Placeholder widgets for future validation features ──────────────────────

# TODO: Lemmatize simplex values (Stanza, English + Italian)
# TODO: Validate aggregate codes (side-by-side original wording vs classification)
# TODO: Data cleaning workflows

placeholder_lb = tk.Label(window, text='Data validation features will be added here.',
                          font=('Helvetica', 11, 'italic'), fg='gray')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer,
                                               placeholder_lb, False)

# ── Help buttons ────────────────────────────────────────────────────────────

def help_buttons(window, help_button_x_coordinate, increment):
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        increment, "NLP Suite Help",
        "Use the dropdown menu to open a related GUI." + GUI_IO_util.msg_Esc)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "INPUT CSV file: the csv file to validate and clean.\n\n"
        "This GUI can be launched from the DB SQL GUI dropdown menu, which will "
        "automatically pass the currently loaded csv file.\n\n"
        "You can also select a csv file manually using the Select INPUT CSV file button." + GUI_IO_util.msg_Esc)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,
        y_multiplier_integer, "NLP Suite Help",
        "Data validation and cleaning tools for PC-ACE simplex values.\n\n"
        "Planned features:\n"
        "   - Lemmatize verbal phrases and other simplex values (English & Italian via Stanza)\n"
        "   - Validate aggregate codes: check that raw wording matches the expected classification\n"
        "   - Side-by-side comparison of original values and aggregate codes\n"
        "   - Data cleaning workflows" + GUI_IO_util.msg_Esc)

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
                  "In INPUT, select a csv file (e.g., a query result from the DB SQL GUI).\n\n"
                  "Planned features include lemmatization of simplex values, "
                  "aggregate code validation, and side-by-side value comparison.")

readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)

run_script_command = lambda: run(
    csv_file_var.get(),
    GUI_util.output_dir_path.get(),
    GUI_util.open_csv_output_checkbox.get(),
    GUI_util.charts_package_options_widget.get(),
    GUI_util.data_transformation_options_widget.get())

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options,
                    y_multiplier_integer, readMe_command,
                    videos_lookup, videos_options,
                    TIPS_lookup, TIPS_options,
                    IO_setup_display_brief, scriptName)

# ── CLI arguments (launched from DB_SQL_main dropdown) ──────────────────────

def _apply_cli_args():
    if '--inputfile' in sys.argv:
        try:
            idx = sys.argv.index('--inputfile')
            _file = sys.argv[idx + 1]
            if os.path.isfile(_file):
                GUI_util.inputFilename.set(_file)
                csv_file_var.set(_file)
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
