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

import IO_csv_util
import IO_files_util
import GUI_IO_util
import IO_user_interface_util
import TIPS_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, outputDir, openOutputFiles, chartPackage, dataTransformation):

    config_filename = GUI_util.config_filename_selected_config.get()

    if not inputFilename or not os.path.isfile(inputFilename):
        mb.showwarning(title='Warning',
                       message='No CSV file selected.\n\nPlease, select an INPUT csv file and try again.')
        return

    # Placeholder — validation logic will go here
    mb.showinfo(title='Info',
                message='Data validation GUI is ready.\n\nValidation features will be added here.')

# GUI section ______________________________________________________________________________________________________________________________________________________

GUI_size = '1200x650'
GUI_label = 'Graphical User Interface (GUI) for PC-ACE Data Validation & Cleaning'
config_filename = 'NLP_default_IO_config.csv'
head, scriptName = os.path.split(os.path.basename(__file__))

config_input_output_numeric_options = [0, 1, 0, 0]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window = GUI_util.window
config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief=False, scriptName=scriptName)

outputDir = GUI_util.output_dir_path

# Variables
csv_file_var = tk.StringVar()

y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               GUI_util.y_multiplier_integer,
                                               tk.Label(window, text='INPUT CSV file'),
                                               True)

csv_file_entry = tk.Entry(window, width=120, textvariable=csv_file_var, state='readonly')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 120,
                                               y_multiplier_integer,
                                               csv_file_entry, False)

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
        "INPUT CSV file: the csv file to validate and clean.\n\n"
        "This GUI can be launched from the DB SQL GUI dropdown menu, which will "
        "automatically pass the currently loaded csv file." + GUI_IO_util.msg_Esc)

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
    GUI_util.inputFilename.get(),
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
