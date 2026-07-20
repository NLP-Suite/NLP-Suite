
import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"Statistics_csv",['tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
import tkinter.filedialog

import GUI_IO_util
import IO_csv_util
import IO_user_interface_util
import IO_files_util
import statistics_csv_util
import statistics_statistical_tests_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run():
    # widget values read here at RUN time (was: run_script_command lambda + run() params)
    inputFilename = GUI_util.inputFilename.get()
    inputDir = GUI_util.input_main_dir_path.get()
    outputDir = GUI_util.output_dir_path.get()
    openOutputFiles = GUI_util.open_csv_output_checkbox.get()
    chartPackage = GUI_util.charts_package_options_widget.get()
    dataTransformation = GUI_util.data_transformation_options_widget.get()
    all_csv_stats = all_csv_stats_var.get()
    csv_field_freq = csv_field_freq_var.get()
    csv_list = globals()['csv_list']
    hover_over_list = globals()['hover_over_list']
    groupBy_list = globals()['groupBy_list']
    script_to_run = globals()['script_to_run']
    stat_test = stat_test_var.get()
    stat_test_option = stat_test_menu_var.get()
    stat_value_col = stat_value_col_var.get()
    stat_group_col = stat_group_col_var.get()
    stat_word_col = stat_word_col_var.get()
    stat_freq_col1 = stat_freq_col1_var.get()
    stat_freq_col2 = stat_freq_col2_var.get()
    stat_corpus_col = stat_corpus_col_var.get()

    config_filename = GUI_util.config_filename_selected_config.get()

    filesToOpen=[]

    window=GUI_util.window

    # if inputDir=='' and corpus_stats:
    #     mb.showwarning(title='Input error', message='The selected option - ' + script_to_run + ' - requires a directory in input.\n\nPlease, select a directory and try again.')
    #     return

    if inputFilename!='' and (all_csv_stats or csv_field_freq):
        if inputFilename[-4:]!='.csv':
            mb.showwarning(title='Input error', message='The selected option - ' + script_to_run + ' - requires an input file of type csv.\n\nPlease, select a csv input file and try again.')
            return

    if all_csv_stats or csv_field_freq:
        if IO_libraries_util.check_inputPythonJavaProgramFile('statistics_csv_util.py')==False:
            return
        if csv_field_freq and len(csv_list) == 0:
            mb.showwarning(title='Warning', message='You have selected to compute the frequency of a csv file field but no field has been selected.\n\nPlease, select a csv file field and try again.')
            return

    if all_csv_stats:
        # tempOutputFiles=statistics_csv_util.compute_csv_column_statistics(window,inputFilename,outputDir,
        #                         groupBy_list, [], '', chartPackage, dataTransformation)

        outputFiles=statistics_csv_util.compute_csv_column_statistics_NoGroupBy(window,inputFilename,outputDir,openOutputFiles,chartPackage, dataTransformation)
        if outputFiles:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    if csv_field_freq:
        if len(csv_list) == 0:
            mb.showwarning(title='Warning', message='You have selected to compute the frequency of a csv file field but no field has been selected.\n\nPlease, select a csv file field and try again.')
            return
        chart_title=''
        # csv_list=['Document','Date']
        outputFiles=statistics_csv_util.compute_csv_column_frequencies(window,
                                                           inputFilename,
                                                           None,
                                                           outputDir,
                                                           openOutputFiles, chartPackage,dataTransformation,
                                                           csv_list,hover_over_list,groupBy_list,
                                                           False,
                                                           chart_title=chart_title,
                                                           fileNameType='CSV',chartType='line',pivot=False)

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # --- Statistical hypothesis tests ---
    if stat_test:
        csv_file = input_csv_file_var.get() if input_csv_file_var.get() else inputFilename
        if csv_file == '' or not csv_file.endswith('.csv'):
            mb.showwarning(title='Input error',
                           message='Statistical hypothesis tests require a csv file in input.\n\nPlease, select a csv input file and try again.')
        else:
            run_mw_kw = stat_test_option in ('*', 'Mann-Whitney U / Kruskal-Wallis')
            run_ll = stat_test_option in ('*', 'Log-likelihood (corpus comparison)')
            run_chi = stat_test_option == 'Chi-square (independence)'
            run_crosstab = stat_test_option == 'Cross-tabulation (contingency table)'
            run_corr = stat_test_option == 'Correlation (Spearman / Kendall)'
            run_mk = stat_test_option == 'Mann-Kendall (temporal trend)'
            run_cp = stat_test_option == 'Change-point detection (temporal)'
            run_perm = stat_test_option == 'Permutation test (two groups)'
            run_bf = stat_test_option == 'Bayes factor (two groups)'
            run_ari = stat_test_option == 'Adjusted Rand index (clustering agreement)'
            run_sil = stat_test_option == 'Silhouette (cluster cohesion)'
            run_kappa = stat_test_option == "Inter-annotator agreement (Cohen's / Fleiss' kappa)"

            if run_mw_kw:
                if stat_value_col == '' or stat_group_col == '':
                    mb.showwarning(title='Missing fields',
                                   message='Mann-Whitney / Kruskal-Wallis requires a numeric value column and a group column.\n\nPlease, select both fields and try again.')
                else:
                    import pandas as _pd
                    _df = _pd.read_csv(csv_file, encoding='utf-8', on_bad_lines='skip')
                    n_groups = _df[stat_group_col].nunique() if stat_group_col in _df.columns else 0
                    if n_groups >= 3:
                        outputFiles = statistics_statistical_tests_util.run_kruskal_wallis_test(
                            csv_file, outputDir, stat_value_col, stat_group_col,
                            chartPackage, dataTransformation)
                    else:
                        outputFiles = statistics_statistical_tests_util.run_mann_whitney_test(
                            csv_file, outputDir, stat_value_col, stat_group_col,
                            chartPackage, dataTransformation)
                    if outputFiles:
                        filesToOpen.extend(outputFiles)

            if run_ll:
                if stat_word_col == '':
                    mb.showwarning(title='Missing fields',
                                   message='Log-likelihood requires at least a word column and either two frequency columns or a corpus identifier column.\n\nPlease, select the required fields and try again.')
                else:
                    outputFiles = statistics_statistical_tests_util.run_log_likelihood_test(
                        csv_file, outputDir, stat_word_col,
                        stat_freq_col1 if stat_freq_col1 != '' else None,
                        stat_freq_col2 if stat_freq_col2 != '' else None,
                        stat_corpus_col if stat_corpus_col != '' else None,
                        chartPackage, dataTransformation)
                    if outputFiles:
                        filesToOpen.extend(outputFiles)

            if run_chi:
                if stat_value_col == '' or stat_group_col == '':
                    mb.showwarning(title='Missing fields',
                                   message='The Chi-square test of independence requires two categorical columns.\n\nPlease, select the Value column (variable A) and the Group column (variable B) and try again.')
                else:
                    outputFiles = statistics_statistical_tests_util.run_chi_square_test(
                        csv_file, outputDir, stat_value_col, stat_group_col,
                        chartPackage, dataTransformation)
                    if outputFiles:
                        filesToOpen.extend(outputFiles)

            if run_crosstab:
                if stat_value_col == '' or stat_group_col == '':
                    mb.showwarning(title='Missing fields',
                                   message='Cross-tabulation requires two categorical columns.\n\nPlease, select the Value column (variable A = rows) and the Group column (variable B = columns) and try again.')
                else:
                    outputFiles = statistics_statistical_tests_util.run_crosstab(
                        csv_file, outputDir, stat_value_col, stat_group_col,
                        chartPackage, dataTransformation)
                    if outputFiles:
                        filesToOpen.extend(outputFiles)

            if run_corr:
                if stat_value_col == '' or stat_group_col == '':
                    mb.showwarning(title='Missing fields',
                                   message='The correlation test requires two numeric columns.\n\nPlease, select the Value column (Y) and the Group column (X) and try again.')
                else:
                    outputFiles = statistics_statistical_tests_util.run_correlation_test(
                        csv_file, outputDir, stat_group_col, stat_value_col,
                        'spearman', chartPackage, dataTransformation)
                    if outputFiles:
                        filesToOpen.extend(outputFiles)

            if run_mk:
                if stat_value_col == '' or stat_group_col == '':
                    mb.showwarning(title='Missing fields',
                                   message='The Mann-Kendall trend test requires a numeric Value column and a date/time Group column.\n\nPlease, select the Value column (numeric series) and the Group column (date/time) and try again.')
                else:
                    outputFiles = statistics_statistical_tests_util.run_mann_kendall_trend_test(
                        csv_file, outputDir, stat_group_col, stat_value_col,
                        chartPackage, dataTransformation)
                    if outputFiles:
                        filesToOpen.extend(outputFiles)

            if run_cp:
                if stat_value_col == '' or stat_group_col == '':
                    mb.showwarning(title='Missing fields',
                                   message='Change-point detection requires a numeric Value column and a date/time (or ordered) Group column.\n\nPlease, select the Value column (numeric series) and the Group column (date/time) and try again.')
                else:
                    outputFiles = statistics_statistical_tests_util.run_change_point_test(
                        csv_file, outputDir, stat_group_col, stat_value_col,
                        chartPackage, dataTransformation)
                    if outputFiles:
                        filesToOpen.extend(outputFiles)

            if run_perm:
                if stat_value_col == '' or stat_group_col == '':
                    mb.showwarning(title='Missing fields',
                                   message='The permutation test requires a numeric Value column and a 2-group Group column.\n\nPlease, select the Value column (numeric) and the Group column (category) and try again.')
                else:
                    outputFiles = statistics_statistical_tests_util.run_permutation_test(
                        csv_file, outputDir, stat_value_col, stat_group_col,
                        10000, chartPackage, dataTransformation)
                    if outputFiles:
                        filesToOpen.extend(outputFiles)

            if run_kappa:
                # every selected column is treated as one annotator's/tool's labels;
                # 2 columns -> Cohen's kappa, 3+ -> Fleiss' kappa
                rater_cols = [c for c in [stat_value_col, stat_group_col, stat_word_col,
                                          stat_freq_col1, stat_freq_col2, stat_corpus_col] if c != '']
                if len(rater_cols) < 2:
                    mb.showwarning(title='Missing fields',
                                   message="Inter-annotator agreement requires at least 2 annotator/tool columns.\n\n"
                                           "Select one column per annotator, e.g. Value column = Stanza tags, Group column = spaCy tags. "
                                           "Add more columns (Word / Freq / Corpus selectors) for 3+ annotators (Fleiss' kappa).\n\n"
                                           "Please, select the columns and try again.")
                else:
                    outputFiles = statistics_statistical_tests_util.run_kappa_test(
                        csv_file, outputDir, rater_cols,
                        chartPackage, dataTransformation)
                    if outputFiles:
                        filesToOpen.extend(outputFiles)

            if run_bf:
                if stat_value_col == '' or stat_group_col == '':
                    mb.showwarning(title='Missing fields',
                                   message='The Bayes factor requires a numeric Value column and a 2-group Group column.\n\nPlease, select the Value column (numeric) and the Group column (category) and try again.')
                else:
                    outputFiles = statistics_statistical_tests_util.run_bayes_factor_test(
                        csv_file, outputDir, stat_value_col, stat_group_col,
                        chartPackage, dataTransformation)
                    if outputFiles:
                        filesToOpen.extend(outputFiles)

            if run_ari:
                if stat_value_col == '' or stat_group_col == '':
                    mb.showwarning(title='Missing fields',
                                   message='The Adjusted Rand index requires two label/cluster columns.\n\nPlease, select the Value column (labeling A) and the Group column (labeling B) and try again.')
                else:
                    outputFiles = statistics_statistical_tests_util.run_adjusted_rand_test(
                        csv_file, outputDir, stat_value_col, stat_group_col,
                        chartPackage, dataTransformation)
                    if outputFiles:
                        filesToOpen.extend(outputFiles)

            if run_sil:
                if stat_group_col == '':
                    mb.showwarning(title='Missing fields',
                                   message='Silhouette requires the Group column as the cluster labels.\n\nAll numeric columns are used as features. Please, select the Group column (cluster labels) and try again.')
                else:
                    outputFiles = statistics_statistical_tests_util.run_silhouette_test(
                        csv_file, outputDir, stat_group_col, None,
                        chartPackage, dataTransformation)
                    if outputFiles:
                        filesToOpen.extend(outputFiles)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
#def run(inputFilename,inputDir,outputDir, dictionary_var, annotator_dictionary, DBpedia_var, annotator_extractor, openOutputFiles):
GUI_util.run_button.configure(command=run)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=560, # height at brief display
                             GUI_height_full=640, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Statistical Analyses of csv Files'
config_filename = 'NLP_default_IO_config.csv'
# ...but honour an I/O config handed over by a launching GUI (--config), e.g. DB_SQL passing on the config
# its query result was produced under. The config -- NOT the live vars -- is what the INPUT/OUTPUT box is
# rendered from, so without this we would DISPLAY the default config while working on the handed-over file.
# The seed is required: GUI_bottom() forces the default whenever config_filename_selected_config is still
# empty, which it ALWAYS is in a fresh process, silently discarding whatever we were passed.
if '--config' in sys.argv:
    try:
        _handover_config = sys.argv[sys.argv.index('--config') + 1]
        if _handover_config:
            config_filename = _handover_config
            GUI_util.config_filename_selected_config.set(config_filename)
    except (IndexError, ValueError):
        pass
head, scriptName = os.path.split(os.path.basename(__file__))

# The 4 values of config_option refer to:
#   input file
        # 1 for CoNLL file
        # 2 for TXT file
        # 3 for csv file
        # 4 for any type of file
        # 5 for txt or html
        # 6 for txt or csv
#   input dir
#   input secondary dir
#   output dir
config_input_output_numeric_options=[3,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window = GUI_util.window
# config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
# config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename
inputDir = GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

n_grams_list=[]
csv_list = []
hover_over_list = []
groupBy_list = []

all_csv_stats_var = tk.IntVar()
csv_field_freq_var = tk.IntVar()
csv_field_var = tk.StringVar()
csv_hover_over_field_var = tk.StringVar()
csv_groupBy_field_var = tk.StringVar()

# CSV file display row ─────────────────────────────────────────────────────────
input_csv_file_var = tk.StringVar()

def get_input_csv_file(window_ref, title, fileType):
    # Offer the csv files discovered for the current corpus (newest first) with a Browse fallback,
    # instead of dumping the user in the src folder (IO_files_util.pick_corpus_csv).
    filePath = IO_files_util.pick_corpus_csv(window_ref, input_csv_file_var.get(), title, fileType)
    if len(filePath) > 0:
        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(filePath, 'utf-8')
        if nRecords == 0:
            mb.showwarning(title='Warning', message="The selected input csv file is empty.\n\nPlease, select a different file and try again.")
            filePath = ''
        else:
            input_csv_file_var.set(filePath)
            # Mirror the selection into the standard GUI input file. The RUN button is gated on
            # GUI_util.inputFilename (config option [3,0,0,1] expects a csv FILE); the custom button
            # alone left it empty, so RUN stayed disabled. Clearing input_main_dir_path is required
            # too: activateRunButton disables RUN when an input dir is set but none is expected.
            GUI_util.inputFilename.set(filePath)
            GUI_util.input_main_dir_path.set('')
            changed_filename()
            refresh_run_button()
    return filePath


def refresh_run_button():
    # Re-evaluate the RUN button after selecting the input csv via the custom button.
    # The input file is validated live by GUI_util.check_fileName; the output directory is still
    # required, so flag it as missing when unset (keeps RUN disabled instead of failing at run time).
    out_dir = GUI_util.output_dir_path.get()
    missing = '' if out_dir != '' else 'OUTPUT files directory\n'
    cfg = GUI_util.config_filename_selected_config.get() or config_filename
    try:
        GUI_util.activateRunButton(cfg, IO_setup_display_brief, scriptName, missing, True)
    except Exception as e:
        print('refresh_run_button: could not re-evaluate RUN button:', e)

input_csv_file_button = tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT CSV file',
                                  command=lambda: get_input_csv_file(window, 'Select INPUT csv file', [("csv files", "*.csv")]))
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               input_csv_file_button, True)

open_input_csv_file_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                       command=lambda: IO_files_util.openFile(window, input_csv_file_var.get()))
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               open_input_csv_file_button,
                                               True, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                               "Open INPUT csv file")

input_csv_file_entry = tk.Entry(window, width=GUI_IO_util.csv_file_width, textvariable=input_csv_file_var)
input_csv_file_entry.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                                               input_csv_file_entry)

# corpus_statistics_var = tk.IntVar()
# corpus_statistics_options_menu_var = tk.StringVar()
# corpus_text_options_menu_var = tk.StringVar()
#
# n_grams_var = tk.IntVar()
# n_grams_menu_var = tk.StringVar()
# csv_options_menu_var = tk.StringVar()
# n_grams_options_menu_var = tk.StringVar()

script_to_run = ''


def get_script_to_run(text):
    global script_to_run
    script_to_run = text


def clear(e):
    # corpus_statistics_var.set(0)
    # corpus_statistics_options_menu_var.set('*')
    # corpus_text_options_menu_var.set('')
    input_csv_file_var.set("")
    all_csv_stats_var.set(0)
    csv_field_freq_var.set(0)
    stat_test_var.set(0)
    stat_test_menu_var.set('*')
    stat_value_col_var.set('')
    stat_group_col_var.set('')
    stat_word_col_var.set('')
    stat_freq_col1_var.set('')
    stat_freq_col2_var.set('')
    stat_corpus_col_var.set('')
    # n_grams_menu_var.set('Word')
    # reset_n_grams_list()
    reset_csv_list()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)


all_csv_stats_var.set(0)
all_csv_field_checkbox = tk.Checkbutton(window, text='Compute statistics on all csv-file fields (numeric fields only)',
                                        variable=all_csv_stats_var, onvalue=1, offvalue=0,
                                        command=lambda: get_script_to_run(
                                            'Compute statistics on all csv-file fields (numeric fields only)'))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   all_csv_field_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox then the RUN button to compute basic statistics for all the NUMERIC fields in the input csv file"
                                   "\nCount, Mean, Mode, Median, Standard deviation, Minimum, Maximum, Skewness, Kurtosis, 25% quantile, 50% quantile; 75% quantile")

csv_field_freq_var.set(0)
csv_field_checkbox = tk.Checkbutton(window, text='Compute frequencies of csv-file field(s)',
                                    variable=csv_field_freq_var, onvalue=1, offvalue=0,
                                    command=lambda: get_script_to_run('Compute frequencies of selected csv-file field'))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   csv_field_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox to compute the frequency of a selected csv field"
                                   "\nONLY ONE FIELD CAN BE SELECTED (although multiple group-by and hover-over fields can be selected)")


def activate_viewer_options(*args):
    print()
    # if csv_field_var.get()!='':
    #     if csv_field_var.get() in csv_field_list:
    #         mb.showwarning(title='Warning', message='The option has already been selected. Selection ignored.\n\nYou can see your current selections by clicking the Show button.')
    #         return
    #     if 'Partial match' in viewer_options_menu_var.get() or \
    #             'Normalize' in viewer_options_menu_var.get() or \
    #             'Scale' in viewer_options_menu_var.get():
    #             mb.showwarning(title='Warning', message='The option is not available yet.\n\nSorry!')
    #             return
    #     # remove the case option, when a different one is selected
    #     if 'insensitive' in viewer_options_menu_var.get() and 'sensitive' in str(viewer_options_list):
    #         viewer_options_list.remove('Case sensitive (default)')
    #     if 'sensitive' in viewer_options_menu_var.get() and 'insensitive' in str(viewer_options_list):
    #         viewer_options_list.remove('Case insensitive')
    #     viewer_options_list.append(viewer_options_menu_var.get())
    #     viewer_options_menu.configure(state="disabled")
    #     add_viewer_button.configure(state='normal')
    #     reset_viewer_button.configure(state='normal')
    #     show_viewer_button.configure(state='normal')
    # else:
    #     add_viewer_button.configure(state='disabled')
    #     reset_viewer_button.configure(state='disabled')
    #     show_viewer_button.configure(state='disabled')
    #     viewer_options_menu.configure(state="normal")

activate_viewer_options()

add_csv_field_button = tk.Button(window, text='+', width=GUI_IO_util.add_button_width,height=1,state='normal',command=lambda: activate_viewer_options())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate+20, y_multiplier_integer,
                                               add_csv_field_button, True, False, False, False, 90,
                                               GUI_IO_util.open_reminders_x_coordinate,
                                               "Click on the + button to add another csv file field")

menu_values = ['']
reset_csv_button = tk.Button(window, text='Reset ', width=GUI_IO_util.reset_button_width,height=1,state='disabled',command=lambda: reset_csv_list())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.statistics_csv_reset_csv_button_pos, y_multiplier_integer,
                                   reset_csv_button,
                                   True, False, True, False, 90, GUI_IO_util.statistics_csv_reset_csv_button_pos,
                                   "Click the 'Reset ' button to clear all selected csv field, group-by field and hover-over field, and start fresh")

show_csv_button = tk.Button(window, text='Show', width=GUI_IO_util.show_button_width,height=1,state='disabled',command=lambda: show_csv_list())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.statistics_csv_show_csv_button_pos, y_multiplier_integer,
                                   show_csv_button,
                                   True, False, True, False, 90, GUI_IO_util.statistics_csv_show_csv_button_pos,
                                   "Click the 'Show' button to display the currrently selected csv field, group-by field and hover-over field")

csv_field_lb = tk.Label(window, text='csv field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.statistics_csv_csv_field_lb_pos, y_multiplier_integer,
                                               csv_field_lb, True)

csv_field_menu = tk.OptionMenu(window, csv_field_var, *menu_values)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+110, y_multiplier_integer,
                                   csv_field_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Use the dropdown menu to select the csv file field to be used to compute frequencies"
                                   "\nONLY ONE FIELD CAN BE SELECTED (although multiple group-by and hover-over fields can be selected)")

def reset_csv_list():
    csv_list.clear()
    hover_over_list.clear()
    groupBy_list.clear()
    csv_field_var.set('')
    csv_groupBy_field_var.set('')
    csv_hover_over_field_var.set('')
    csv_field_menu.configure(state='normal')

def show_csv_list():
    if len(csv_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected csv field options.')
    else:
        mb.showwarning(title='Warning', message='The currently selected csv field options are:\n'
        '\n   CSV FIELD: ' + ', '.join(csv_list) +
        '\n   GROUP-BY FIELD(S): ' + ', ' .join(groupBy_list) +
        '\n   HOVER-OVER FIELD(S): ' + ', ' .join(hover_over_list) +
        '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

def activate_plus1(*args):
    # if csv_field_var.get() in csv_list:
    # 	mb.showwarning(title='Warning', message='The csv field "'+ csv_field_var.get() + '" is already in your selection list: '+ str(csv_list) + '.\n\nPlease, select another field.')
    # 	window.focus_force()
    # 	return
    if csv_field_var.get() != '':
        csv_list.clear()  # only 1 value is now allowed
        csv_list.append(csv_field_var.get())
        csv_hover_over_field_menu.configure(state='normal')
        csv_groupBy_field_menu.configure(state='normal')


# csv_field_menu.configure(state="disabled")
# add_field1_button.configure(state='normal')
csv_field_var.trace('w', activate_plus1)


def activate_hover_over_field_menu():
    if csv_hover_over_field_var.get() != '':
        csv_hover_over_field_menu.configure(state="normal")

# add extra group_by field
add_field3_button = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1, state='disabled',
                              command=lambda: activate_groupBy_field_menu())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   add_field3_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Click the + button, when available, to add another group-by field to aggregate the data")

csv_groupBy_field_lb = tk.Label(window, text='Group-by field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.statistics_csv_csv_groupBy_field_lb_pos, y_multiplier_integer,
                                               csv_groupBy_field_lb, True)

csv_groupBy_field_menu = tk.OptionMenu(window, csv_groupBy_field_var, *menu_values)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.statistics_csv_csv_groupBy_field_menu_pos, y_multiplier_integer,
                                   csv_groupBy_field_menu,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Use the dropdown menu to select the csv file field to be used to group the selected csv file field"
                                   "\nMULTIPLE GROUP-BY FIELDS CAN BE SELECTED")

# add extra hover_over field
add_field2_button = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1, state='disabled',
                              command=lambda: activate_hover_over_field_menu())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+110, y_multiplier_integer,
                                   add_field2_button,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Click the + button, when available, to add another hover-over field")

csv_hover_over_field_lb = tk.Label(window, text='Hover-over field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                               csv_hover_over_field_lb, True)

csv_hover_over_field_menu = tk.OptionMenu(window, csv_hover_over_field_var, *menu_values)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+120, y_multiplier_integer,
                                   csv_hover_over_field_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Use the dropdown menu to select the csv file field to be used to display hover-over information"
                                   "\nMULTIPLE HOVER-OVER FIELDS CAN BE SELECTED"
                                   "\nTHE OPTION IS AVAILABLE FOR EXCEL CHARTS ONLY" )

# groupBy_list=[]
def activate_plus2(*args):
    if csv_hover_over_field_var.get() in hover_over_list:
        mb.showwarning(title='Warning',
                       message='The csv field "' + csv_hover_over_field_var.get() + '" is already in your selection list: ' + str(
                           hover_over_list) + '.\n\nPlease, select another field.')
        window.focus_force()
        return
    if csv_hover_over_field_var.get() != '':
        hover_over_list.append(csv_hover_over_field_var.get())
        csv_hover_over_field_menu.configure(state="disabled")
        add_field2_button.configure(state='normal')

csv_hover_over_field_var.trace('w', activate_plus2)


def activate_groupBy_field_menu():
    if csv_groupBy_field_var.get() != '':
        csv_groupBy_field_menu.configure(state="normal")


def activate_plus3(*args):
    if csv_groupBy_field_var.get() in groupBy_list:
        mb.showwarning(title='Warning',
                       message='The csv field "' + csv_groupBy_field_var.get() + '" is already in your selection list: ' + str(
                           groupBy_list) + '.\n\nPlease, select another field.')
        window.focus_force()
        return
    if csv_groupBy_field_var.get() != '':
        groupBy_list.append(csv_groupBy_field_var.get())
        csv_groupBy_field_menu.configure(state="disabled")
        add_field3_button.configure(state='normal')


csv_groupBy_field_var.trace('w', activate_plus3)


def activate_all_options(menu_values, from_csv_field_freq_var=False):
    if inputFilename.get()[-4:] == '.txt':
        # corpus_statistics_checkbox.configure(state='normal')
        all_csv_field_checkbox.configure(state='disabled')
        csv_field_checkbox.configure(state='disabled')
        # n_grams_checkbox.configure(state='normal')
        # n_grams_menu.configure(state='normal')
        # n_grams_options_menu.configure(state='normal')
    elif inputFilename.get()[-4:] == '.csv':
        all_csv_field_checkbox.configure(state='normal')
        csv_field_checkbox.configure(state='normal')
        # corpus_statistics_checkbox.configure(state='disabled')
        # n_grams_checkbox.configure(state='disabled')
        # n_grams_menu.configure(state='disabled')
        # n_grams_options_menu .configure(state='disabled')
    else:
        # corpus_statistics_checkbox.configure(state='normal')
        all_csv_field_checkbox.configure(state='normal')
        csv_field_checkbox.configure(state='normal')
        # n_grams_checkbox.configure(state='normal')
        # n_grams_menu.configure(state='disabled')
        # n_grams_options_menu.configure(state='disabled')

    # if corpus_statistics_var.get() == 1:
    #     all_csv_field_checkbox.configure(state='disabled')
    #     csv_field_checkbox.configure(state='disabled')
    #     # n_grams_checkbox.configure(state='disabled')
    #     # n_grams_menu.configure(state='disabled')
    #     # n_grams_options_menu .configure(state='disabled')

    if all_csv_stats_var.get() == 1:
        # corpus_statistics_checkbox.configure(state='disabled')
        csv_field_checkbox.configure(state='disabled')
        # n_grams_checkbox.configure(state='disabled')
        # n_grams_menu.configure(state='disabled')
        # n_grams_options_menu.configure(state='disabled')

    if csv_field_freq_var.get() == 1:
        if from_csv_field_freq_var == True:
            if menu_values == ['']:  # first time through
                changed_filename()
        # corpus_statistics_checkbox.configure(state='disabled')
        all_csv_field_checkbox.configure(state='disabled')
        # n_grams_checkbox.configure(state='disabled')
        # n_grams_menu.configure(state='disabled')
        # n_grams_options_menu .configure(state='disabled')
        reset_csv_button.configure(state='normal')
        show_csv_button.configure(state='normal')
        csv_field_menu.configure(state='normal')
        csv_hover_over_field_menu.configure(state='disabled')
        csv_groupBy_field_menu.configure(state='disabled')
    else:
        csv_field_var.set('')
        reset_csv_button.configure(state='normal')
        show_csv_button.configure(state='normal')
        csv_hover_over_field_var.set('')
        csv_field_menu.configure(state='disabled')
        csv_hover_over_field_menu.configure(state='disabled')
        csv_groupBy_field_menu.configure(state='disabled')

    # if n_grams_var.get() == 1:
    #     # corpus_statistics_checkbox.configure(state='disabled')
    #     all_csv_field_checkbox.configure(state='disabled')
    #     csv_field_checkbox.configure(state='disabled')
    #     # n_grams_menu.configure(state='normal')
        # n_grams_options_menu.configure(state='normal')
    # else:
    #     n_grams_menu.configure(state='disabled')
    #     n_grams_options_menu.configure(state='disabled')

# corpus_statistics_var.trace('w', lambda x, y, z: activate_all_options(menu_values))
all_csv_stats_var.trace('w', lambda x, y, z: activate_all_options(menu_values))
csv_field_freq_var.trace('w', lambda x, y, z: activate_all_options(menu_values, True))
# n_grams_var.trace('w', lambda x, y, z: activate_all_options(menu_values))

activate_all_options(menu_values)


# the first call is placed at the buttom of this script so that all widgets would have been dispayed
def changed_filename(*args):
    clear('Escape')
    global menu_values
    csv_file = input_csv_file_var.get() if input_csv_file_var.get() else inputFilename.get()
    if csv_file != '' and csv_file[-4:] == '.csv':
        menu_values = IO_csv_util.get_csvfile_headers(csv_file)
        m = csv_field_menu["menu"]
        m1 = csv_hover_over_field_menu["menu"]
        m2 = csv_groupBy_field_menu["menu"]
        m.delete(0, "end")
        m1.delete(0, "end")
        m2.delete(0, "end")
        for s in menu_values:
            m.add_command(label=s, command=lambda value=s: csv_field_var.set(value))
            m1.add_command(label=s, command=lambda value=s: csv_hover_over_field_var.set(value))
            m2.add_command(label=s, command=lambda value=s: csv_groupBy_field_var.set(value))
        # populate stat test column menus
        for stat_menu, stat_var in [
            (stat_value_col_menu, stat_value_col_var),
            (stat_group_col_menu, stat_group_col_var),
            (stat_word_col_menu, stat_word_col_var),
            (stat_freq_col1_menu, stat_freq_col1_var),
            (stat_freq_col2_menu, stat_freq_col2_var),
            (stat_corpus_col_menu, stat_corpus_col_var)]:
            sm = stat_menu["menu"]
            sm.delete(0, "end")
            for s in menu_values:
                sm.add_command(label=s, command=lambda value=s, sv=stat_var: sv.set(value))
    activate_all_options(menu_values)

# at the bottom of the script after laying out the GUI
# inputFilename.trace('w',changed_filename)
# changed_filename()

# Statistical hypothesis tests row ─────────────────────────────────────────────
stat_test_var = tk.IntVar()
stat_test_menu_var = tk.StringVar()
stat_test_menu_var.set('*')

stat_value_col_var = tk.StringVar()
stat_group_col_var = tk.StringVar()
stat_word_col_var = tk.StringVar()
stat_freq_col1_var = tk.StringVar()
stat_freq_col2_var = tk.StringVar()
stat_corpus_col_var = tk.StringVar()

stat_test_checkbox = tk.Checkbutton(window, text='Hypothesis tests',
                                    variable=stat_test_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               stat_test_checkbox,
                                               True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                               "Tick the checkbox to run statistical hypothesis tests on the selected csv file.\n\n"
                                               "Use the dropdown menu to select a specific test or * for all available tests.")

stat_test_options = ['*', 'Mann-Whitney U / Kruskal-Wallis', 'Chi-square (independence)',
                     'Cross-tabulation (contingency table)',
                     'Correlation (Spearman / Kendall)', 'Mann-Kendall (temporal trend)',
                     'Change-point detection (temporal)', 'Permutation test (two groups)',
                     'Bayes factor (two groups)', 'Adjusted Rand index (clustering agreement)',
                     'Silhouette (cluster cohesion)', 'Log-likelihood (corpus comparison)',
                     "Inter-annotator agreement (Cohen's / Fleiss' kappa)"]
stat_test_menu = tk.OptionMenu(window, stat_test_menu_var, *stat_test_options)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.statistics_csv_csv_groupBy_field_menu_pos, y_multiplier_integer,
                                               stat_test_menu,
                                               False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                               "Select which hypothesis test to run. Most tests use two columns: the Value column (first variable) and the Group column (second variable).\n\n"
                                               "* = run Mann-Whitney/Kruskal-Wallis AND Log-likelihood.\n\n"
                                               "Mann-Whitney U / Kruskal-Wallis (Value=numeric, Group=category): compare a numeric variable across groups "
                                               "(2 groups → Mann-Whitney; 3+ groups → Kruskal-Wallis with Dunn's post-hoc).\n\n"
                                               "Chi-square (independence) (Value=category A, Group=category B): test whether two categorical variables are associated (+ Cramer's V).\n\n"
                                               "Cross-tabulation (contingency table) (Value=category A=rows, Group=category B=columns): the A x B counts table (with row/column totals) plus a row-percentage table and a grouped-bar chart. Descriptive only -- no significance test (use Chi-square for that).\n\n"
                                               "Correlation (Spearman / Kendall) (Value=Y numeric, Group=X numeric): test monotonic association between two numeric variables.\n\n"
                                               "Mann-Kendall (temporal trend) (Value=numeric series, Group=date/time): test for a significant increasing/decreasing trend over time (+ Sen's slope).\n\n"
                                               "Change-point detection (temporal) (Value=numeric series, Group=date/time): find a single abrupt shift in the series (Pettitt's test) and the mean before/after.\n\n"
                                               "Permutation test (two groups) (Value=numeric, Group=2 categories): distribution-free test of the difference in group means by shuffling labels (+ Cohen's d).\n\n"
                                               "Bayes factor (two groups) (Value=numeric, Group=2 categories): Bayesian evidence for a difference vs none — BF10>3 moderate, >10 strong evidence FOR a difference; BF10<1/3 evidence for NO difference (+ Cohen's d).\n\n"
                                               "Adjusted Rand index (clustering agreement) (Value=labeling/clustering A, Group=labeling/clustering B): chance-corrected agreement between two clusterings (1=identical, 0=chance, <0=worse than chance; + NMI). The clustering equivalent of kappa.\n\n"
                                               "Silhouette (cluster cohesion) (Group=cluster labels; all numeric columns used as features): how tight and well-separated the clusters are (-1..1; ~1=strong, ~0=overlapping), with per-cluster means.\n\n"
                                               "Log-likelihood (corpus comparison): identify words statistically over/under-represented in one corpus vs another (uses Word / Freq / Corpus columns below).\n\n"
                                               "Inter-annotator agreement (Cohen's / Fleiss' kappa): measure how well 2+ annotators/tools agree. Each selected column (Value, Group, and optionally Word / Freq / Corpus) is one annotator's labels; 2 columns → Cohen's, 3+ → Fleiss'.")

# Mann-Whitney / Kruskal-Wallis field selectors
stat_value_col_lb = tk.Label(window, text='Value column')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               stat_value_col_lb, True)
stat_value_col_menu = tk.OptionMenu(window, stat_value_col_var, *menu_values)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.statistics_csv_csv_groupBy_field_menu_pos, y_multiplier_integer,
                                               stat_value_col_menu,
                                               True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                               "Select the numeric column to compare across groups (e.g., Sentiment score, Frequency)")

stat_group_col_lb = tk.Label(window, text='Group column')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                               stat_group_col_lb, True)
stat_group_col_menu = tk.OptionMenu(window, stat_group_col_var, *menu_values)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate+110, y_multiplier_integer,
                                               stat_group_col_menu,
                                               False, False, True, False, 90, GUI_IO_util.statistics_csv_csv_groupBy_field_lb_pos,
                                               "Select the categorical column that defines groups to compare (e.g., Document, Corpus)")

# Log-likelihood field selectors
stat_word_col_lb = tk.Label(window, text='Word column')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               stat_word_col_lb, True)
stat_word_col_menu = tk.OptionMenu(window, stat_word_col_var, *menu_values)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.statistics_csv_csv_groupBy_field_menu_pos, y_multiplier_integer,
                                               stat_word_col_menu,
                                               True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                               "Select the column containing words/tokens for corpus comparison")

stat_freq_col1_lb = tk.Label(window, text='Freq column 1')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                               stat_freq_col1_lb, True)
stat_freq_col1_menu = tk.OptionMenu(window, stat_freq_col1_var, *menu_values)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate+110, y_multiplier_integer,
                                               stat_freq_col1_menu,
                                               False, False, True, False, 90, GUI_IO_util.statistics_csv_csv_groupBy_field_lb_pos,
                                               "Select the frequency column for corpus 1 (or the shared frequency column when using a corpus identifier)")

stat_freq_col2_lb = tk.Label(window, text='Freq column 2')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                               stat_freq_col2_lb, True)
stat_freq_col2_menu = tk.OptionMenu(window, stat_freq_col2_var, *menu_values)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate+110, y_multiplier_integer,
                                               stat_freq_col2_menu,
                                               True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                               "Select the frequency column for corpus 2 (leave empty if using a corpus identifier column)")

stat_corpus_col_lb = tk.Label(window, text='Corpus ID column')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               stat_corpus_col_lb, True)
stat_corpus_col_menu = tk.OptionMenu(window, stat_corpus_col_var, *menu_values)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.statistics_csv_csv_groupBy_field_menu_pos, y_multiplier_integer,
                                               stat_corpus_col_menu,
                                               False, False, True, False, 90, GUI_IO_util.statistics_csv_csv_groupBy_field_lb_pos,
                                               "Select the column identifying which corpus each row belongs to (alternative to two separate frequency columns)")


def activate_stat_test_options(*args):
    if stat_test_var.get() == 1:
        stat_test_menu.configure(state='normal')
        option = stat_test_menu_var.get()
        run_kappa = option == "Inter-annotator agreement (Cohen's / Fleiss' kappa)"
        # tests that use the Value column (var A) + Group column (var B)
        run_value_group = option in ('*', 'Mann-Whitney U / Kruskal-Wallis',
                                     'Chi-square (independence)',
                                     'Cross-tabulation (contingency table)',
                                     'Correlation (Spearman / Kendall)',
                                     'Mann-Kendall (temporal trend)',
                                     'Change-point detection (temporal)',
                                     'Permutation test (two groups)',
                                     'Bayes factor (two groups)',
                                     'Adjusted Rand index (clustering agreement)',
                                     'Silhouette (cluster cohesion)')
        run_ll = option in ('*', 'Log-likelihood (corpus comparison)')
        # kappa can use every column selector (each column = one annotator)
        state_vg = 'normal' if (run_value_group or run_kappa) else 'disabled'
        state_ll = 'normal' if (run_ll or run_kappa) else 'disabled'
        stat_value_col_menu.configure(state=state_vg)
        stat_group_col_menu.configure(state=state_vg)
        stat_word_col_menu.configure(state=state_ll)
        stat_freq_col1_menu.configure(state=state_ll)
        stat_freq_col2_menu.configure(state=state_ll)
        stat_corpus_col_menu.configure(state=state_ll)
    else:
        stat_test_menu.configure(state='disabled')
        stat_value_col_menu.configure(state='disabled')
        stat_group_col_menu.configure(state='disabled')
        stat_word_col_menu.configure(state='disabled')
        stat_freq_col1_menu.configure(state='disabled')
        stat_freq_col2_menu.configure(state='disabled')
        stat_corpus_col_menu.configure(state='disabled')

stat_test_var.trace('w', activate_stat_test_options)
stat_test_menu_var.trace('w', activate_stat_test_options)
activate_stat_test_options()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical tools in the NLP Suite': 'TIPS_NLP_Statistical tools.pdf',
               'Statistical descriptive measures': "TIPS_NLP_Statistical measures.pdf",
               'Lemmas & stopwords':'TIPS_NLP_NLP Basic language.pdf',
               'Style measures': 'TIPS_NLP_Style analysis.pdf',
               # 'N-Grams (word & character)': "TIPS_NLP_Ngram (word & character).pdf",
               # 'NLP Ngram and Word Co-Occurrence Viewer': "TIPS_NLP_Ngram and Word Co-Occurrence VIEWER.pdf",
               # 'Google Ngram Viewer': 'TIPS_NLP_Ngram Google Ngram Viewer.pdf',
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf'}
TIPS_options = 'Statistical tools in the NLP Suite', 'Statistical descriptive measures', 'csv files - Problems & solutions', 'Lemmas & stopwords', 'Excel smoothing data series'


# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, click the 'Select INPUT CSV file' button to select a csv file to analyze.\n\nThe csv file headers will be used to populate the dropdown menus for selecting the fields to be used for statistical analyses.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  'Please, tick the checkbox if you wish to compute basic statistics on all the numeric fields of a csv file.\n\nIn INPUT the script expects a csv file.\n\nIn OUTPUT, the script generates a csv file of statistics for each numeric field in the input csv file: Count, Mean, Mode, Median, Standard deviation, Minimum, Maximum, Skewness, Kurtosis, 25% quantile, 50% quantile; 75% quantile.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  'Please, tick the checkbox if you wish to compute the frequency of a specific field of a csv file. ONLY ONE FIELD CAN BE CURRENTLY SELECTED. But multiple group-by fields and hover-over fields can be selected.\n\nYou can select to group the frequencies by specific field(s) and/or have hover-over field(s) if you wish to display information in an Excel chart.\n\nIn INPUT the script expects a csv file.\n\nIn OUTPUT, the script generates a csv file of frequencies for the selected field.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  'Please, using the dropdown menu, for the selected csv field, selected  one or more group-by fields (e.g., compute the frequencies of POSTAG values by DocumentID in a CoNLL table displaying both words and lemmas in hover over.) \n\nMultiple fields can be selected by pressing the + button.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox to run statistical hypothesis tests.\n\n"
                                  "Most tests use two columns: the Value column (first variable) and the Group column (second variable).\n\n"
                                  "Use the dropdown menu to select:\n"
                                  "   * = run Mann-Whitney/Kruskal-Wallis AND Log-likelihood\n"
                                  "   Mann-Whitney U / Kruskal-Wallis (Value=numeric, Group=category): compare a numeric variable across groups "
                                  "(2 groups → Mann-Whitney U; 3+ groups → Kruskal-Wallis with Dunn's post-hoc).\n"
                                  "   Chi-square (independence) (Value=category A, Group=category B): test association between two categorical variables (+ Cramer's V).\n"
                                  "   Cross-tabulation (contingency table) (Value=category A=rows, Group=category B=columns): the A x B counts table (with row/column totals), a row-percentage table, and a grouped-bar chart. Descriptive only - no significance test.\n"
                                  "   Correlation (Spearman / Kendall) (Value=Y, Group=X, both numeric): test monotonic association between two numeric variables.\n"
                                  "   Mann-Kendall (temporal trend) (Value=numeric series, Group=date/time): test for a significant trend over time (+ Sen's slope).\n"
                                  "   Change-point detection (temporal) (Value=numeric series, Group=date/time): find a single abrupt shift in the series (Pettitt's test).\n"
                                  "   Permutation test (two groups) (Value=numeric, Group=2 categories): distribution-free test of the difference in group means (+ Cohen's d).\n"
                                  "   Bayes factor (two groups) (Value=numeric, Group=2 categories): Bayesian evidence for a difference vs none (BF10>3 moderate, >10 strong evidence FOR a difference; BF10<1/3 evidence for NO difference; + Cohen's d).\n"
                                  "   Adjusted Rand index (clustering agreement) (Value=clustering A, Group=clustering B): chance-corrected agreement between two clusterings (1=identical, 0=chance, <0=worse than chance; + NMI). The clustering equivalent of kappa.\n"
                                  "   Silhouette (cluster cohesion) (Group=cluster labels; all numeric columns used as features): how tight and well-separated the clusters are (-1..1; ~1=strong, ~0=overlapping), with per-cluster means.\n"
                                  "   Log-likelihood (corpus comparison): identify words statistically over/under-represented in one corpus vs another.\n"
                                  "   Inter-annotator agreement (Cohen's / Fleiss' kappa): measure how well 2+ annotators/tools agree; each selected column is one annotator (2 → Cohen's, 3+ → Fleiss').")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Mann-Whitney / Kruskal-Wallis fields: select the numeric Value column (e.g., Sentiment score) and the categorical Group column (e.g., Document, Corpus).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Log-likelihood fields: select the Word column and the Freq column 1.\n\n"
                                  "Then EITHER select Freq column 2 (pre-computed frequencies for a second corpus) OR select a Corpus ID column (to split one frequency column by corpus).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Log-likelihood fields (continued): Freq column 2 and Corpus ID column.\n\n"
                                  "Use Freq column 2 when your csv has separate frequency columns for each corpus.\n"
                                  "Use Corpus ID column when your csv has one frequency column and a column identifying which corpus each row belongs to.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

# change the value of the readMe_message
readMe_message = "The Python 3 scripts provide ways of analyzing csv files and obtain basic descriptive statistics."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

changed_filename()
inputFilename.trace('w', changed_filename)

# Handover from a launching GUI (e.g. DB_SQL passing the csv its query just produced): land the file
# pre-selected in the INPUT CSV widget so the user does not have to hunt for it. Done AFTER GUI_bottom so
# every widget exists. Silently ignored when launched standalone.
if '--csvfile' in sys.argv:
    try:
        _csv = sys.argv[sys.argv.index('--csvfile') + 1]
        if os.path.isfile(_csv):
            input_csv_file_var.set(_csv)
    except (IndexError, ValueError):
        pass
if '--outputdir' in sys.argv:
    try:
        _out = sys.argv[sys.argv.index('--outputdir') + 1]
        if os.path.isdir(_out):
            GUI_util.output_dir_path.set(_out)
    except (IndexError, ValueError):
        pass

GUI_util.window.mainloop()

