import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"data_manipulation_main.py", ['os', 'tkinter', 'pandas', 'functools'])==False:
    sys.exit(0)

import os
import tkinter as tk
from tkinter import ttk
from subprocess import call
import tkinter.messagebox as mb

import IO_files_util
import GUI_util
import GUI_IO_util
import IO_csv_util
import data_manipulation_util
import reminders_util
import run_script_util

# RUN section ________________________________________________________________________________________________________

def run():
    # widget values read here at RUN time (was: run_script_command lambda + run() params)
    inputFilename = GUI_util.inputFilename.get()
    selectedCsvFile = globals()['selectedCsvFile_var'].get()
    operation_results_text_list = globals()['operation_results_text_list']
    operation = operation_name_var.get()
    append_var = globals()['append_var'].get()
    concatenate_var = globals()['concatenate_var'].get()
    drop_var = globals()['drop_var'].get()
    extract_var = globals()['extract_var'].get()
    merge_var = globals()['merge_var'].get()
    split_var = globals()['split_var'].get()
    sort_var = globals()['sort_var'].get()
    deduplicate_var = globals()['deduplicate_var'].get()
    rename_var = globals()['rename_var'].get()
    output_to_csv_var = globals()['output_to_csv_var'].get()
    openOutputFiles = GUI_util.open_csv_output_checkbox.get()
    outputDir = GUI_util.output_dir_path.get()

    config_filename = GUI_util.config_filename_selected_config.get()

    filesToOpen = []  # Store all files that are to be opened once finished

    # data_files = [file for file in data_manipulation_util.select_csv(filePath)]  # dataframes
    # headers = [s.split(',')[1] for s in operation_results_text_list]  # headers
    # data_cols = [file for file in data_manipulation_util.get_cols(data_files, headers)]  # selected cols

# APPEND https://www.geeksforgeeks.org/how-to-append-a-new-row-to-an-existing-csv-file/

    if (operation=='CONCATENATE') and len(operation_results_text_list)<2:
        mb.showwarning(title='Warning',
                       message='The ' + str(operation).upper() + ' operation requires at least two fields. Please, click on the + button to select a second field and try again.')
        operation_name_var.set('')
        # a text widget is read only when disabled
        operation_results_text.configure(state='normal')
        operation_results_text.delete(0.1, tk.END)
        operation_results_text.configure(state='disabled')
        operation_results_text_list.clear()

    if operation_name_var.get()=='':
        mb.showwarning(title='Warning',
                       message="You must click the 'OK' button to approve the selections made before running the algorithm.\n\nUpon clicking OK, your current selection will be displayed above in the large text box. If the selections is OK, click RUN; otherwise, click the Reset all button and start over.")
        return


# APPEND ______________________________________________________________________________

    if append_var:
        outputFilename=data_manipulation_util.append(outputDir,operation_results_text_list)
        if outputFilename!=None:
            filesToOpen.append(outputFilename)


# CONCATENATE ______________________________________________________________________________

    if concatenate_var:
        outputFilename=data_manipulation_util.concatenate(outputDir, operation_results_text_list)
        if outputFilename!=None:
            filesToOpen.append(outputFilename)

#   ______________________________________________________________________________

    if merge_var:
        if selectedCsvFile == inputFilename:
            mb.showwarning(title='Warning',
                           message='You have selected the merge operation. This requires two different csv files in input.\n\nPlease, click on the + button next to File, select another csv file, select the field that yu want to use in this file as the overlaping field(s) with the previous file (the key(s)), click OK and RUN.')
            return
        operation_results_text_list = operation_results_text.get(0.1, tk.END)
        # the util defines MERGE (uppercase); calling .merge raised AttributeError, so the operation could
        # never run -- Python is case-sensitive and nothing here catches it.
        outputFilename = data_manipulation_util.MERGE(outputDir, operation_results_text_list)
        if outputFilename != None:
            filesToOpen.append(outputFilename)

# DROP ______________________________________________________________________________

    if drop_var:
        outputFilename = data_manipulation_util.drop(outputDir, operation_results_text_list)
        if outputFilename != None:
            filesToOpen.append(outputFilename)

    # EXTRACT ______________________________________________________________________________

    if extract_var:
        if output_to_csv_var:
            export_type = '.csv'
        else:
            export_type = '.txt'
        outputFilename = data_manipulation_util.export_csv_to_csv_txt(outputDir,operation_results_text_list,export_type)
        if outputFilename != None:
            filesToOpen.append(outputFilename)

# SPLIT ______________________________________________________________________________

    if split_var:
        outputFilename = data_manipulation_util.split_field(outputDir, operation_results_text_list)
        if outputFilename != None:
            filesToOpen.append(outputFilename)

# SORT ______________________________________________________________________________

    if sort_var:
        outputFilename = data_manipulation_util.sort_rows(outputDir, operation_results_text_list)
        if outputFilename != None:
            filesToOpen.append(outputFilename)

# DEDUPLICATE ______________________________________________________________________________

    if deduplicate_var:
        outputFilename = data_manipulation_util.deduplicate(outputDir, operation_results_text_list)
        if outputFilename != None:
            filesToOpen.append(outputFilename)

# RENAME ______________________________________________________________________________

    if rename_var:
        outputFilename = data_manipulation_util.rename_field(outputDir, operation_results_text_list)
        if outputFilename != None:
            filesToOpen.append(outputFilename)


    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)


# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated

if __name__ == '__main__':
    GUI_util.run_button.configure(command=run)

    # GUI section ______________________________________________________________________________________________________________________________________________________

    IO_setup_display_brief=True
    GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                     GUI_width=GUI_IO_util.get_GUI_width(3),
                                                     GUI_height_brief=480,
                                                     # height at brief display
                                                     GUI_height_full=520,  # height at full display
                                                     y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                     y_multiplier_integer_add=1,
                                                     # to be added for full display
                                                     increment=1)  # to be added for full display

    GUI_label = 'Graphical User Interface (GUI) for csv Data Manipulation'
    config_filename = 'NLP_default_IO_config.csv'
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

    # in operation_results_text_list, the script returns a list of comma-separated csv filename + csv field
    # when using the extract option, operation_results_text_list will also list the where and and/or values
    # repeated csv fields will be skipped
    # for instance
    # ['C:/Program Files (x86)/NLP_backup/Output/EnglishANEW.csv,A.SD.F', 'C:/Program Files (x86)/NLP_backup/Output/EnglishANEW.csv,D.Mean.M']

    # GUI CHANGES search for GUI CHANGES

    window = GUI_util.window
    # config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
    # config_filename = GUI_util.config_filename
    inputFilename = GUI_util.inputFilename

    GUI_util.GUI_top(config_input_output_numeric_options, config_filename,IO_setup_display_brief,scriptName,True)

    # GUI CHANGES cut/paste special GUI widgets from GUI_util

    extra_GUIs_var = tk.IntVar()
    extra_GUIs_menu_var = tk.StringVar()
    operation_results_text_list = []
    merge_var = tk.IntVar()
    concatenate_var = tk.IntVar()
    character_separator_var = tk.StringVar()
    append_var = tk.IntVar()
    extract_var = tk.IntVar()
    output_to_csv_var = tk.IntVar()
    output_to_csv_var.set(1)   # EXTRACT defaults to csv output (the csv/txt checkbox was dropped in the single-row redesign)
    drop_var = tk.IntVar()
    split_var = tk.IntVar()
    sort_var = tk.IntVar()
    deduplicate_var = tk.IntVar()
    rename_var = tk.IntVar()

    selectedCsvFile_var = tk.StringVar()

    selected_csv_files_var = tk.StringVar()

    where_entry_var = tk.StringVar()
    and_or_var = tk.StringVar()

    comparator_var = tk.StringVar()

    selected_csv_fields_var = tk.StringVar()
    operation_name_var = tk.StringVar()
    csv_file_operations_var = tk.StringVar()
    select_csv_field_var = tk.StringVar()
    select_csv_field_append_var = tk.StringVar()
    select_csv_field_concatenate_var = tk.StringVar()
    selectedCsvFile_var = tk.StringVar()
    select_csv_field_merge_var = tk.StringVar()

    add_field_var = tk.IntVar()
    add_merge_options_var = tk.IntVar()
    add_file_var = tk.IntVar()

    # ---- INPUT csv file(s) ----------------------------------------------------------------------------
    # A wired 'Select INPUT CSV file' button, a '+' to add MORE files, and a dropdown to ROLL THROUGH the
    # accumulated files (picking one makes it the CURRENT file -> its fields load in the dropdowns below via
    # the selectedCsvFile_var trace). Esc / Reset all clear the list (see clear()). Replaces the old dead
    # 'Select csv file' label + a never-populated OptionMenu.
    csv_files_list = []

    def _default_open_dir_and_file():
        """Where the 'select a csv' dialogs should open: the NLP output dir set in the I/O config, defaulting
        to the MOST RECENT .csv there (so the user usually just clicks Open). Falls back to this script's dir
        if no output dir is configured / it has no csv files."""
        import os
        out_dir = GUI_util.output_dir_path.get()
        if not out_dir or not os.path.isdir(out_dir):
            return os.path.dirname(os.path.abspath(__file__)), ''
        csvs = [os.path.join(out_dir, f) for f in os.listdir(out_dir) if f.lower().endswith('.csv')]
        if not csvs:
            return out_dir, ''
        try:
            most_recent = max(csvs, key=os.path.getmtime)
        except OSError:
            return out_dir, ''
        return out_dir, os.path.basename(most_recent)

    def _refresh_csv_file_dropdown():
        """Repopulate the file-roll dropdown from csv_files_list (shows basenames). The displayed value tracks
        the CURRENT file (selectedCsvFile_var), so picking any item -- not just the newest -- keeps showing.
        (Selecting sets selectedCsvFile_var, whose trace re-enters here; anchoring the display on the last
        file instead would snap the label back to the newest and lose the user's pick.)"""
        import os
        _m = csv_file_dropdown['menu']
        _m.delete(0, 'end')
        for _f in csv_files_list:
            _m.add_command(label=os.path.basename(_f),
                           command=lambda v=_f: (csv_file_dropdown_var.set(os.path.basename(v)),
                                                 selectedCsvFile_var.set(v)))
        _current = selectedCsvFile_var.get()
        if _current in csv_files_list:
            csv_file_dropdown_var.set(os.path.basename(_current))
        elif csv_files_list:
            csv_file_dropdown_var.set(os.path.basename(csv_files_list[-1]))
        else:
            csv_file_dropdown_var.set('')

    def _select_csv_file(reset):
        """Pick a csv via dialog. reset=True starts a FRESH list (the top Select button). The chosen file
        becomes current: the selectedCsvFile_var trace -> changed_filename loads its fields AND records it in
        the roll dropdown (the single source of truth), so no manual append is needed here."""
        # reset=True discards the accumulated roll list. Once the user has built up a list (more than one
        # file -- one entry is just the I/O input auto-recorded), confirm before wiping it so an accidental
        # click doesn't silently lose their selections.
        if reset and len(csv_files_list) > 1:
            if not mb.askyesno('Reset the INPUT csv file list?',
                               'You currently have ' + str(len(csv_files_list)) + ' csv files in the roll-through '
                               'list.\n\nSelecting a new INPUT csv file will CLEAR that list and start over with '
                               'only the file you pick.\n\nDo you want to continue?'):
                return
        initial_dir, initial_file = _default_open_dir_and_file()
        fp = tk.filedialog.askopenfilename(title='Select INPUT csv file',
                                           initialdir=initial_dir,
                                           initialfile=initial_file,
                                           filetypes=[("csv files", "*.csv")])
        if not fp:
            return
        if reset:
            csv_files_list.clear()
        select_csv_field_merge_var.set('')
        selected_csv_fields_var.set('')
        selectedCsvFile_var.set(fp)   # trace -> changed_filename loads fields + records it in the dropdown

    csv_file_button = tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT CSV file',
                                command=lambda: _select_csv_file(reset=True))
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   csv_file_button, True)

    menu_values=[]
    menu_values = " "
    n_concatenate_fields=0

    # dropdown to ROLL THROUGH the added files -- created here, PLACED on its own row below (after the
    # button/open/'+' row) so it doesn't overlap the wide Select button. Given an explicit width because an
    # empty OptionMenu otherwise renders as a tiny sliver even once it's populated.
    csv_file_dropdown_var = tk.StringVar()
    csv_file_dropdown = tk.OptionMenu(window, csv_file_dropdown_var, '')
    csv_file_dropdown.config(width=125)

    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                                   csv_file_dropdown, True, False, True, False, 90,
                                                   GUI_IO_util.labels_x_coordinate,
                                                   "Roll through the INPUT csv files you have added; select one to make it the current file (its fields load in the dropdowns below).")

    # open the current file
    openInputFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                     command=lambda: IO_files_util.openFile(window,
                                                                            selectedCsvFile_var.get()))
    # sameY True so the '+' can share the row
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate + 1050, y_multiplier_integer,
                                                   openInputFile_button,False, False, True, False, 90,
                                                   GUI_IO_util.close_button_x_coordinate, "Open displayed file")

    extra_GUIs_var.set(0)
    extra_GUIs_checkbox = tk.Checkbutton(window, text='GUIs available for more analyses ', variable=extra_GUIs_var,
                                         onvalue=1, offvalue=0, command=lambda: activate_all_options())
    # extra_GUIs_checkbox.configure(state='disabled')
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   extra_GUIs_checkbox, True)

    extra_GUIs_menu_var.set('')
    extra_GUIs_menu = tk.OptionMenu(window, extra_GUIs_menu_var, 'CSV data manipulation with SQL (Open GUI)',
                                    'CSV data visualization (Open GUI)',
                                    'Statistics on csv files (Open GUI)')
    extra_GUIs_menu.configure(state='disabled')
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                                   extra_GUIs_menu,
                                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                                   "Select other related types of analysis you wish to perform" \
                                                   "\nThe selected GUI will open without having to press RUN")


    def open_GUI(*args):
        extra_GUIs_menu.configure(state='disabled')
        if extra_GUIs_var.get():
            extra_GUIs_menu.configure(state='normal')
        else:
            return
        if extra_GUIs_var.get():
            if 'Statistics' in extra_GUIs_menu_var.get():
                run_script_util.run_script("statistics_csv_main.py")
            elif 'SQL' in extra_GUIs_menu_var.get():
                run_script_util.run_script("DB_SQL_main.py")
            elif 'visualization' in extra_GUIs_menu_var.get():
                run_script_util.run_script("data_visualization_main.py")


    extra_GUIs_menu_var.trace('w', open_GUI)


    pressedPlus = False

    def activate_extract_options():
        global pressedPlus
        pressedPlus = True
        activate_extract_fields(True, False)
        pressedPlus = False

    def activate_extract_fields(comingFrom_Plus, comingFrom_OK):
        global pressedPlus
        if extract_var.get() == True:
            if select_csv_field_var.get() != '':
                if comingFrom_Plus == True:
                    select_csv_field_menu.configure(state='normal')
                    where_entry_var.set('')
                    and_or_var.set('')
                else:
                    try:
                        if pressedPlus==False:
                            select_csv_field_menu.configure(state='disabled')
                    except:
                        pass
                    comparator_menu.configure(state="disabled")

                if select_csv_field_var.get() != '':
                    comparator_menu.configure(state="normal")
                    add_extract_options.config(state='normal')
                    # OK_WHERE_button.config(state='normal')
                else:
                    comparator_menu.configure(state="disabled")
                    add_extract_options.config(state='disabled')
                    # OK_WHERE_button.config(state='disabled')
                if comparator_var.get() != '':
                    where_entry.configure(state="normal")
                else:
                    where_entry.configure(state="disabled")
                if where_entry_var.get() != '':
                    and_or_menu.configure(state='normal')
                else:
                    and_or_menu.configure(state='disabled')

                if comingFrom_OK == True:
                    comparator_menu.configure(state="disabled")
                    where_entry.configure(state="disabled")
                    and_or_menu.configure(state='disabled')
                    # add_file_button.config(state='disabled')
                    add_extract_options.config(state='disabled')
                    # WHERE_button.config(state='disabled')
                else:
                    # add_file_button.config(state='normal')
                    add_extract_options.config(state='normal')
                    # OK_WHERE_button.config(state='normal')
                    comparator_menu.configure(state="normal")
                    where_entry.configure(state="normal")
            else:
                select_csv_field_menu.configure(state='normal')
                # add_file_button.config(state='disabled')
                comparator_menu.configure(state="disabled")

        else:
            # select_csv_field_var.set('')
            select_csv_field_menu.config(state='disabled')

            comparator_menu.configure(state="disabled")
            where_entry.configure(state="disabled")
            and_or_menu.configure(state="disabled")
            # OK_WHERE_button.config(state='disabled')

            where_entry_var.set("")
            comparator_var.set("")
            and_or_var.set("")

    ##
    def extractSelection(comingfrom_Plus, comingfrom_OK=False):
        activate_all_options()
        if extract_var.get():
            activate_extract_fields(comingfrom_Plus, comingfrom_OK)

    comparator_var.trace('w', lambda x, y, z: extractSelection(False))
    where_entry_var.trace("w", lambda x, y, z: extractSelection(False))
    and_or_var.trace("w", lambda x, y, z: extractSelection(False))
    # add_extract_options_var.trace("w", lambda x, y, z: extractSelection(True))


    avoidLoop = False
    error = False

    def clear(e):
        # NOTE: clear() is called internally by changed_filename() on every non-merge file load, so it must
        # NOT wipe the accumulated INPUT csv file list (csv_files_list) -- doing so emptied the roll-through
        # dropdown the instant a file loaded. The roll list is cleared only on genuine 'Reset all'
        # (reset_all_values) and when the top 'Select INPUT CSV file' button starts a fresh list.
        csv_file_operations_var.set('')
        reset_csv_field_values()
        # single-row model: reset the operation dropdown + its mirrored one-hot IntVars + the shared '+'/OK
        options_var.set('')
        merge_var.set(0)
        concatenate_var.set(0)
        append_var.set(0)
        extract_var.set(0)
        drop_var.set(0)
        add_drop_field.configure(state='disabled')
        add_drop_file.configure(state='disabled')
        OK_operation_button.configure(state='disabled')
        select_csv_field_var.set('')
        select_csv_field_concatenate_var.set('')
        select_csv_field_merge_var.set('')
        character_separator_entry_var.set('')
        comparator_var.set('')
        where_entry_var.set('')
        and_or_var.set('')
        GUI_util.clear("Escape")

    window.bind("<Escape>", clear)


    def reset_all_values():
        clear("<Escape>")
        # genuine start-over: empty the accumulated INPUT csv file roll list + its dropdown
        csv_files_list.clear()
        _refresh_csv_file_dropdown()
        reset_csv_field_values()
        operation_results_text_list.clear()
        # file_number_var.set(1)
        selected_csv_fields_var.set(0)
        selectedCsvFile_var.set(GUI_util.inputFilename.get())
        operation_name_var.set('')

        # a text widget is read only when disabled
        operation_results_text.configure(state='normal')
        operation_results_text.delete(0.1, tk.END)
        operation_results_text.configure(state='disabled')

        character_separator_entry_var.set("")

        comparator_menu.configure(state="disabled")
        where_entry.configure(state="disabled")
        and_or_menu.configure(state="disabled")

        where_entry_var.set("")
        comparator_var.set("")
        and_or_var.set("")

        merge_var.set(0)
        concatenate_var.set(0)
        append_var.set(0)
        extract_var.set(0)


    def reset_csv_field_values():
        selected_csv_fields_var.set('')

    file_number_var = tk.IntVar()
    file_number_var.set(1)

    if GUI_util.inputFilename.get() != '' and (os.path.basename(GUI_util.inputFilename.get())[-4:] == ".csv"):
        # if selectedCsvFile_var.get() == '':
        #     selectedCsvFile_var.set(GUI_util.inputFilename.get())

        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(GUI_util.inputFilename.get())
        if IO_csv_util.csvFile_has_header(GUI_util.inputFilename.get()) == False:
            menu_values = range(1, nColumns + 1)
        else:
            data, headers = IO_csv_util.get_csv_data(GUI_util.inputFilename.get(), True)
            menu_values = headers
    else:
        nColumns = 0
        menu_values = " "
    if nColumns == -1:
        pass
    # return



    # operation is a string with values "merge", "concatenate", "append", "extract", "drop"
    # menu_choice is the menu value of the specific csv field selected  (e.g., select_csv_field_concatenate_var.get())
    # it returns a list to be passed to data_handling.py for processing

    # visualizeBuildString after clicking OK
    def build_string_for_processing(operation, csv_field_menu_choice, comingFrom_Plus, comingFrom_OK):
        # skip empty values and csv fields already selected
        if not append_var and not concatenate_var and not extract_var and not drop_var and not merge_var.set:
            return False # no error

        # buildString = csv_fileName + "," + csv_field_menu_choice
        if ((not comingFrom_Plus) and (not comingFrom_OK)) and (csv_field_menu_choice!='' and (csv_field_menu_choice in selected_csv_fields_var.get())):
            mb.showwarning(title='Warning',
                           message='You have already selected the field ' + csv_field_menu_choice + '\n\nPlease, select a different field.')
            # select_csv_field_merge_menu.configure(state='normal', width=12)
            return True # error

        buildString = selectedCsvFile_var.get() + "," + csv_field_menu_choice
        if selected_csv_fields_var.get() == '':
            selected_csv_fields_var.set(csv_field_menu_choice)
        if (selected_csv_fields_var.get() != '') and (csv_field_menu_choice not in selected_csv_fields_var.get()):
            selected_csv_fields_var.set(selected_csv_fields_var.get() + "," + str(csv_field_menu_choice))

        if not comingFrom_Plus and not comingFrom_OK:
            return False # no error

        if operation == "concatenate":
            character_separator_entry.get()
            if select_csv_field_var.get() != '' and character_separator_entry.get() != '':
                buildString = buildString + "," + character_separator_entry.get()
            else:
                buildString = ''

        if operation == "split":
            if character_separator_entry.get() == '':
                mb.showwarning(title='Missing separator',
                               message='The SPLIT operation requires a character separator.\n\nPlease, enter it in the Character separator box and try again.')
                return True  # error
            buildString = buildString + "," + character_separator_entry.get()

        if operation == "rename":
            if character_separator_entry.get() == '':
                mb.showwarning(title='Missing new name',
                               message='The RENAME operation requires a new field name.\n\nPlease, type it in the Character separator box and try again.')
                return True  # error
            buildString = buildString + "," + character_separator_entry.get()

        if operation == 'extract' or operation == 'drop':
            if comparator_var.get() != '' and where_entry_var.get() == '':
                mb.showwarning(title='Warning',
                               message='You have selected the comparator value ' + comparator_var.get() + '\n\nYou MUST enter a WHERE value or press ESC to cancel.')
                return True # error
            # always enter the value even if empty to ensure a similarly formatted string
            if comparator_var.get() != '':
                buildString = buildString + "," + comparator_var.get()
            else:
                buildString = buildString + "," + "''"
            if where_entry_var.get() != '':
                buildString = buildString + "," + where_entry_var.get()
            else:
                buildString = buildString + "," + "''"
            if and_or_var.get() != '':
                buildString = buildString + "," + and_or_var.get()
            else:
                buildString = buildString + "," + "''"

        operation_results_text_list.append(buildString)
        # when clicking the OK button for the Concatenate and Extract operations
        if comingFrom_OK == True:
            operation_name_var.set(str(operation).upper())  # + " list"
            # a text widget is read only when disabled
            operation_results_text.configure(state='normal')
            operation_results_text.insert("end", str(operation_results_text_list))
            operation_results_text.configure(state='disabled')
        return False # no error

    # after clicking on the merge checkbox
    def merge_reminder1():
        reminders_util.checkReminder(scriptName,
                                     reminders_util.title_options_data_manager_merge,
                                     reminders_util.message_data_manager_merge1,
                                     True)
        activate_all_options()
        build_merge_string(False, False)
        # mergeSelection(False, False)


    def build_append_string(comingFrom_Plus, comingFrom_OK):
        errorFound = build_string_for_processing("append", select_csv_field_var.get(), comingFrom_Plus, comingFrom_OK)
        if not errorFound:
            activate_csv_fields_selection('append', append_var.get(), comingFrom_Plus, comingFrom_OK)

    def operation_OK():
        # single-row OK: record the current selection for whichever operation is chosen (options_var), then
        # display the accumulated arguments in the read-only box. The per-operation extra parameters
        # (separator / new name / WHERE) are added inside build_string_for_processing.
        op = options_var.get()
        if op == '':
            mb.showwarning(title='No operation',
                           message='Please, select an operation from the dropdown menu before clicking OK.')
            return
        build_string_for_processing(op.lower(), select_csv_field_var.get(), False, True)

    def operation_plus_field():
        # single-row '+field': record the current field and re-open the field menu so another can be added
        # (CONCATENATE, MERGE, SORT, DEDUPLICATE).
        op = options_var.get()
        if op == '':
            return
        errorFound = build_string_for_processing(op.lower(), select_csv_field_var.get(), True, False)
        if not errorFound:
            select_csv_field_menu.configure(state='normal')
            select_csv_field_var.set('')



# ALL OPTIONS: New layout -----------------------------------------------------------------------------------

    operation_options = ['Append', 'Concatenate', 'Deduplicate', 'Drop', 'Extract', 'Merge',
                         'Rename', 'Sort', 'Split']
    options_var = tk.StringVar()
    options_menu = tk.OptionMenu(window, options_var, *operation_options)
    options_menu.configure(state='disabled')
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                                   y_multiplier_integer,
                                                   options_menu,
                                                   True, False, False, False, 90,
                                                   GUI_IO_util.labels_x_coordinate,
                                                   "Use the dropdown menu to select an available option: Append, Concatenate, Deduplicate, Drop, Extract, Merge, Rename, Sort, Split.\nRow widgets become available depending upon the operation selected.")

    select_csv_field_lb = tk.Label(window, text='Select field')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                                   select_csv_field_lb, True)

    select_csv_field_var = tk.StringVar()
    select_csv_field_menu = tk.OptionMenu(window, select_csv_field_var, *menu_values)
    select_csv_field_menu.configure(state='disabled')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 100, y_multiplier_integer,
                                                   select_csv_field_menu,
                                                   True, False, False, False, 90,
                                                   GUI_IO_util.IO_configuration_menu,
                                                   "Use the dropdown menu to select the csv field the selected operation acts on: the field to concatenate, split, sort by, deduplicate by, drop by, extract, or rename - or the overlapping key field for merge.")

    character_separator_entry_var = tk.StringVar()
    character_separator_entry = tk.Entry(window, width=10, textvariable=character_separator_entry_var)
    character_separator_entry.config(state='disabled')
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_setup_x_coordinate+120,
                                                   y_multiplier_integer,
                                                   character_separator_entry,
                                                   True, False, False, False, 90,
                                                   GUI_IO_util.open_setup_x_coordinate,
                                                   "This box serves the operation you selected:\n\nFor CONCATENATE and SPLIT, enter the character(s) separator (CONCATENATE joins the selected fields with it; SPLIT cuts a field apart on it).\n\nFor RENAME, type the NEW field name here.")
    # 'WHERE widget'
    WHERE_drop_extract_button = tk.Button(window, text='WHERE clause', command=lambda: activate_where_clause())
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.run_button_x_coordinate,
                                                   y_multiplier_integer,
                                                   WHERE_drop_extract_button,
                                                   True, False, False, False, 90,
                                                   GUI_IO_util.open_setup_x_coordinate,
                                                   "Click the button to activate the WHERE clause on top of this GUI")

    add_drop_field = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1, state='disabled', command=lambda: operation_plus_field())
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 950,
                                                   y_multiplier_integer,
                                                   add_drop_field,
                                                   True, False, False, False, 90,
                                                   GUI_IO_util.labels_x_coordinate + 760,
                                                   "Click the + button to add another csv field")

    # add another file
    add_drop_file = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1, state='disabled',
                         command=lambda: add_csvFile(window, 'Select INPUT csv file',
                                                                [("csv files", "*.csv")]))
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 1000,
                                                   y_multiplier_integer,
                                                   add_drop_file, True, False, False, False, 90,
                                                   GUI_IO_util.labels_x_coordinate + 800,
                                                   "Click the + button to add another csv file")

    OK_operation_button = tk.Button(window, text='OK', width=GUI_IO_util.OK_button_width, height=1, state='disabled',
                                command=lambda: operation_OK())
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 1050,
                                                   y_multiplier_integer,
                                                   OK_operation_button,
                                                   False, False, False, False, 90,
                                                   GUI_IO_util.open_reminders_x_coordinate,
                                                   "Click the 'OK' button to approve the selections made and display the selected option in the display widget")


# Claude we should export results to both csv and txt files

# WHERE clause 2 rows

    where_lb = tk.Label(window, text='WHERE clause')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                                   where_lb, True)

    # A Combobox rather than an Entry: it occupies the same slot and is still free to type into, but it
    # can also DROP DOWN the values actually present in the selected field. Typing the value blind, case
    # sensitively, meant a user had to know the column's contents by heart, and a single typo matched
    # nothing at all while looking like a legitimate result.
    where_entry = ttk.Combobox(window, width=27, textvariable=where_entry_var, values=[])
    where_entry.configure(state="disabled")
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate + 100, y_multiplier_integer,
                                                   where_entry,
                                                   True, False, False, False, 90,
                                                   GUI_IO_util.labels_x_indented_coordinate,
                                                   "Enter the value to test the selected field against in the WHERE clause (CASE SENSITIVE), or click the arrow to pick from the values found in that field.\n\nExample: to keep only the rows where Year >= 1997, select the >= comparator and enter 1997 here.\n\nThe list shows the distinct values of the field selected above, so you do not have to remember how they are spelled or capitalised. Long lists are cut at 500 values; you can always type a value that is not shown.\n\nAvailable for the DROP and EXTRACT operations only; the box is disabled until you select a comparator.")

    def _refresh_where_values(*args):
        """Fill the WHERE dropdown with the distinct values of the currently selected field."""
        try:
            values = data_manipulation_util.distinct_values(selectedCsvFile_var.get(),
                                                            select_csv_field_var.get())
        except Exception:
            values = []   # a convenience list must never stop the user typing a value by hand
        where_entry.configure(values=values)

    # refresh when either the field or the csv file changes; both determine what the values are
    select_csv_field_var.trace('w', _refresh_where_values)
    selectedCsvFile_var.trace('w', _refresh_where_values)

    comp_menu_values=['<>', '=', '>', '>=', '<', '<=']
    comparator_menu = tk.OptionMenu(window, comparator_var, *comp_menu_values) #, command=lambda:extractSelection()
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate + 340, y_multiplier_integer,
                                                   comparator_menu,
                                                   True, False, False, False, 90,
                                                   GUI_IO_util.labels_x_indented_coordinate + 340,
                                                   "Select the comparator for the WHERE clause:\n\n   <>   not equal to\n   =    equal to\n   >    greater than\n   >=   greater than or equal to\n   <    less than\n   <=   less than or equal to")

    and_or_lb = tk.Label(window, text='and/or')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate + 460, y_multiplier_integer,
                                                   and_or_lb, True)

    and_or_menu = tk.OptionMenu(window, and_or_var, 'and', 'or')
    and_or_menu.configure(state="disabled", width=3)
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate + 910, y_multiplier_integer,
                                                   and_or_menu,
                                                   True, False, False, False, 90,
                                                   GUI_IO_util.labels_x_indented_coordinate + 910,
                                                   "Select 'and' or 'or' to combine this WHERE condition with a further condition, then press the + button to add the next condition.")

    ##
    add_extract_options_var = tk.IntVar()
    add_extract_options = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1, state='disabled',
                                    command=lambda: activate_extract_options())
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 1000,
                                                   y_multiplier_integer,
                                                   add_extract_options,
                                                   True, False, False, False, 90,
                                                   GUI_IO_util.labels_x_coordinate + 760,
                                                   "Click the + button to add another WHERE option")

    OK_WHERE_button = tk.Button(window, text='OK', width=GUI_IO_util.OK_button_width, height=1, state='disabled',
                                        command=lambda: build_extract_string(False, True))
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 1050,
                                                   y_multiplier_integer,
                                                   OK_WHERE_button,
                                                   False, False, False, False, 90,
                                                   GUI_IO_util.open_reminders_x_coordinate,
                                                   "Click the 'OK' button to approve the selections made and display the selected option in the display widget")

    reset_all_button = tk.Button(window, width=15, text='Reset all', state='normal', command=lambda: reset_all_values())
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                                   reset_all_button,
                                                   True, False, False, False, 90,
                                                   GUI_IO_util.labels_x_indented_coordinate,
                                                   "Click 'Reset all' to clear every selection - the operation, csv field(s), the WHERE clause, and the accumulated csv file list - and start fresh.")

    # a text widget is read only when disabled
    operation_results_text = tk.Text(window, width=100, height=3, state="disabled")
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                                   operation_results_text)

    def activate_where_clause():
        where_entry.configure(state="normal")

    def build_extract_string(comingFrom_Plus, comingFrom_OK):
        errorFound = build_string_for_processing("extract", select_csv_field_var.get(), comingFrom_Plus, comingFrom_OK)
        if not errorFound:
            ##
            activate_extract_fields(comingFrom_Plus, comingFrom_OK)

    # after selecting a csv field
    def merge_reminder2(*args):
        if not merge_var.get():
            return
        if select_csv_field_var.get()!='':
            reminders_util.checkReminder(scriptName,
                                         reminders_util.title_options_data_manager_merge,
                                         reminders_util.message_data_manager_merge2,
                                         True)
        build_merge_string(False, False)
        # mergeSelection(False, False)

    # single shared field menu drives all operations; merge_reminder2 self-guards on merge_var
    select_csv_field_var.trace('w', merge_reminder2)

    def build_merge_string(comingFrom_Plus, comingFrom_OK):
        if not merge_var.get():
            return
        errorFound = build_string_for_processing("merge", select_csv_field_var.get(), comingFrom_Plus, comingFrom_OK)
        if not errorFound:
            activate_csv_fields_selection('merge', merge_var.get(), comingFrom_Plus, comingFrom_OK)

    # after clicking OK
    def merge_reminder_OK():
        if not merge_var.get():
            return
        if file_number_var.get()>1:
            reminders_util.checkReminder(scriptName,
                                         reminders_util.title_options_data_manager_merge,
                                         reminders_util.message_data_manager_merge7,
                                         True)
        else:
            reminders_util.checkReminder(scriptName,
                                         reminders_util.title_options_data_manager_merge,
                                         reminders_util.message_data_manager_merge4,
                                         True)
        build_merge_string(False,True)


    # after clicking + to add another csv field
    def merge_reminder_plus():
        if not merge_var.get():
            return
        reminders_util.checkReminder(scriptName,
                                     reminders_util.title_options_data_manager_merge,
                                     reminders_util.message_data_manager_merge3,
                                     True)
        build_merge_string(True, False)

    def add_csvFile(window, title, fileType):
        global y_multiplier_integer
        initialFolder, initialFile = _default_open_dir_and_file()
        filePath = tk.filedialog.askopenfilename(title=title, initialdir=initialFolder, initialfile=initialFile, filetypes=fileType)
        if len(filePath) > 0:
            select_csv_field_merge_var.set('')
            selected_csv_fields_var.set('')

            selectedCsvFile_var.set(filePath)   # trace -> changed_filename records it in the roll dropdown

            reminders_util.checkReminder(scriptName,
                                         reminders_util.title_options_data_manager_merge,
                                         reminders_util.message_data_manager_merge5,
                                         True)

    #
    def changed_filename(tracedInputFile):
        global error
        if tracedInputFile[-4:] != '.csv':
            mb.showerror(title='Input file error',
                         message="The Data manipulation functions expect in input a csv file.\n\nPlease, select a csv file for your Default or GUI-specific I/O configuration and try again.\n\nThe RUN button is disabled until the required Input/Output option is entered.")
            error = True
        else:
            error = False

        activate_all_options()

        menu_values = []
        if tracedInputFile != '':
            nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(tracedInputFile)
            if nColumns == 0 or nColumns == None:
                return False
            if IO_csv_util.csvFile_has_header(tracedInputFile) == False:
                menu_values = range(1, nColumns + 1)
            else:
                data, headers = IO_csv_util.get_csv_data(tracedInputFile, True)
                menu_values = headers
        else:
            menu_values.clear()
            return

        # SINGLE source of truth for the roll-through dropdown: every file that reaches changed_filename as a
        # valid, non-empty csv -- the I/O config INPUT file (GUI_util.inputFilename trace), the top 'Select
        # INPUT CSV file' button, AND the per-operation '+' buttons (add_csvFile) all funnel here -- is
        # recorded (dedup). Cleared only on 'Reset all' or a fresh top-button selection.
        if tracedInputFile not in csv_files_list:
            csv_files_list.append(tracedInputFile)
        _refresh_csv_file_dropdown()

        # ONE shared field menu now (was four per-operation menus): populate it once.
        m1 = select_csv_field_menu["menu"]
        m1.delete(0, "end")
        for s in menu_values:
            m1.add_command(label=s, command=lambda value=s: select_csv_field_var.set(value))

        if tracedInputFile != GUI_util.inputFilename.get():
            selectedCsvFile_var.set(selectedCsvFile_var.get())
        else:
            selectedCsvFile_var.set(GUI_util.inputFilename.get())
        reset_csv_field_values()
        if not merge_var.get():
            clear("<Escape>")

    selectedCsvFile_var.trace('w', lambda x, y, z: changed_filename(selectedCsvFile_var.get()))
    GUI_util.inputFilename.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))


    def activate_WHERE_options(*args):
        # DEAD in the single-row redesign (no callers; the WHERE-clause enabling now lives in
        # activate_extract_fields / activate_all_options). Kept as a stub to avoid dangling references.
        pass

    def activate_all_options(*args):
        # SINGLE-ROW enable matrix. The operation is chosen in options_var (mirrored into the *_var IntVars
        # by select_operation); here we reset every operation-specific widget in the shared row, then enable
        # only the ones the selected operation needs. Shared widgets: select_csv_field_menu (field),
        # character_separator_entry (separator), WHERE_drop_extract_button (WHERE), add_drop_field ('+field'),
        # add_drop_file ('+file'), OK_drop_button (OK), output_to_csv_checkbox (csv/txt out for EXTRACT).
        select_csv_field_menu.config(state='disabled')
        character_separator_entry.config(state='disabled')
        WHERE_drop_extract_button.configure(state='disabled')
        # output_to_csv_checkbox.config(state='disabled')
        add_drop_field.configure(state='disabled')
        add_drop_file.configure(state='disabled')
        OK_operation_button.configure(state='disabled')

        # EXTRA GUIs dropdown ('GUIs available for more analyses'): clickable only while its checkbox is ticked
        extra_GUIs_menu.configure(state='normal' if extra_GUIs_var.get() else 'disabled')

        options_menu.configure(state='normal')
        if error:
            options_menu.configure(state='disabled')
            return

        if append_var.get():          # APPEND rows: add file(s), no field
            add_drop_file.configure(state='normal')
            OK_operation_button.configure(state='normal')
        elif concatenate_var.get():   # CONCATENATE fields: field + separator + add field
            select_csv_field_menu.config(state='normal')
            character_separator_entry.config(state='normal')
            add_drop_field.configure(state='normal')
            OK_operation_button.configure(state='normal')
        elif drop_var.get():          # DROP rows: field + WHERE + add field/file
            select_csv_field_menu.config(state='normal')
            WHERE_drop_extract_button.configure(state='normal')
            add_drop_field.configure(state='normal')
            add_drop_file.configure(state='normal')
            OK_operation_button.configure(state='normal')
        elif extract_var.get():       # EXTRACT field(s): field + WHERE + csv/txt output
            select_csv_field_menu.config(state='normal')
            WHERE_drop_extract_button.configure(state='normal')
            # output_to_csv_checkbox.config(state='normal')
            OK_operation_button.configure(state='normal')
        elif merge_var.get():         # MERGE files: field (join key) + add field/file
            select_csv_field_menu.config(state='normal')
            add_drop_field.configure(state='normal')
            add_drop_file.configure(state='normal')
            OK_operation_button.configure(state='normal')
        elif split_var.get():         # SPLIT field: field + separator (the inverse of CONCATENATE)
            select_csv_field_menu.config(state='normal')
            character_separator_entry.config(state='normal')
            OK_operation_button.configure(state='normal')
        elif sort_var.get():          # SORT rows: field(s), ascending (+field for multiple sort keys)
            select_csv_field_menu.config(state='normal')
            add_drop_field.configure(state='normal')
            OK_operation_button.configure(state='normal')
        elif deduplicate_var.get():   # DEDUPLICATE rows: key field(s), or whole row if none (+field for multi-key)
            select_csv_field_menu.config(state='normal')
            add_drop_field.configure(state='normal')
            OK_operation_button.configure(state='normal')
        elif rename_var.get():        # RENAME field: field + new name (typed in the Character separator box)
            select_csv_field_menu.config(state='normal')
            character_separator_entry.config(state='normal')
            OK_operation_button.configure(state='normal')

    def select_operation(*args):
        # single dropdown -> mirror the choice into the one-hot IntVars that run()/build_* branch on, then
        # re-evaluate the enable matrix.
        op = options_var.get()
        append_var.set(1 if op == 'Append' else 0)
        concatenate_var.set(1 if op == 'Concatenate' else 0)
        drop_var.set(1 if op == 'Drop' else 0)
        extract_var.set(1 if op == 'Extract' else 0)
        merge_var.set(1 if op == 'Merge' else 0)
        split_var.set(1 if op == 'Split' else 0)
        sort_var.set(1 if op == 'Sort' else 0)
        deduplicate_var.set(1 if op == 'Deduplicate' else 0)
        rename_var.set(1 if op == 'Rename' else 0)
        activate_all_options()

    options_var.trace("w", select_operation)
    select_csv_field_var.trace("w", activate_all_options)
    character_separator_entry_var.trace("w", activate_all_options)

    ##
    def activate_csv_fields_selection(operation, checkButton, comingFrom_Plus, comingFrom_OK):
        # checkButton whether the specific operation has been selected
        # if checkButton == False:
        #     merge_checkbox.config(state='normal')
        # else:
        reset_all_button.config(state='normal')

        # if operation == "append":
        if append_var.get():
            if checkButton == True:
                # merge_checkbox.config(state='disabled')
                # concatenate_split_menu.config(state='disabled')
                select_csv_field_menu.config(state='disabled')

            else:
                # OK_append_button.config(state='disabled')
                # merge_checkbox.config(state='normal')
                # concatenate_split_menu.config(state='normal')
                select_csv_field_menu.config(state='normal')
        elif concatenate_var.get():
            if checkButton == True:
                select_csv_field_menu.config(state='disabled')
                if select_csv_field_var.get() != '':
                    character_separator_entry.config(state='normal')
                if character_separator_entry_var.get() != '':
                    OK_operation_button.config(state='normal')
                    if comingFrom_Plus == True or comingFrom_OK == True:
                        character_separator_entry.config(state='disabled')
            else:
                character_separator_entry.config(state='disabled')
                character_separator_entry_var.set('')
        # DROP / EXTRACT: per-operation widget enabling is owned by activate_all_options in the single-row
        # model; only the shared OK bookkeeping below still applies.
        elif drop_var.get():
            pass
        elif extract_var.get():
            pass
        elif merge_var.get():
            if checkButton == True:
                select_csv_field_menu.config(state='normal')
                if select_csv_field_var.get() != '':
                    select_csv_field_menu.config(state='disabled')
                    OK_operation_button.config(state='normal')
                    if comingFrom_Plus == True:
                        select_csv_field_menu.configure(state='normal')
                    if comingFrom_OK == True:
                        select_csv_field_menu.configure(state='disabled')
                        OK_operation_button.config(state='disabled')
                else:
                    OK_operation_button.config(state='disabled')
            else:
                select_csv_field_menu.config(state='disabled')
                OK_operation_button.config(state='disabled')

        # clear content of current variables when selecting a different main option
        if (operation_name_var.get() != '') and (operation_name_var.get() != str(operation).upper()):
            operation_results_text_list.clear()
            if operation_name_var.get()=='MERGE':
                return
            reset_csv_field_values()
            file_number_var.set(1)
            operation_name_var.set('')
            operation_results_text.configure(state='normal')
            operation_results_text.delete(0.1, tk.END)
            operation_results_text.configure(state='disabled')

    videos_lookup = {'No videos available': ''}
    videos_options = 'No videos available'

    TIPS_lookup = {'Data manipulation GUI': 'TIPS_NLP_Data manipulation.pdf',
                   'csv files - Problems & solutions': 'TIPS_NLP_csv files - Problems & solutions.pdf',
                   'Statistical tools in the NLP Suite': 'TIPS_NLP_Statistical tools.pdf',
                   'Statistical descriptive measures': "TIPS_NLP_Statistical measures.pdf",
                   'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
                   'DB SQL GUI (what input it needs; where the database is saved)': 'TIPS_NLP_DB SQL GUI.pdf',
                   'SQL template queries': 'TIPS_NLP_SQL Template Queries.pdf',
               'Filtering data (thresholds, values, stop words)':'TIPS_NLP_Filtering Function.pdf'}
    TIPS_options = 'Data manipulation GUI', 'csv files - Problems & solutions', 'Statistical tools in the NLP Suite', 'Statistical descriptive measures', 'DB SQL GUI (what input it needs; where the database is saved)', 'SQL template queries', 'Excel smoothing data series','Filtering data (thresholds, values, stop words)'


    # add all the lines to the end to every special GUI
    # change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
    # any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
    def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
        # , while the MERGE option takes 2 or more csv files
        # input_output="In INPUT,\n\n   the APPEND, CONCATENATE, and drop options take 1 csv file." \
        #         "\n\nIn OUTPUT," \
        #         "\n\n   the APPEND option creates a csv file containing all the same input fields but with more rows (the appended rows)." \
        #         "\n\n   the CONCATENATE option creates a csv file containing all the same fields as in the input file plus an extra field for the concatenated values." \
        #         "\n\n   the drop option creates a csv file containing all the same input fields but with fewer rows (the purged rows)."
        resetAll = "\n\nPress the RESET ALL button to clear all values, including csv files and fields, and start fresh."
        # plusButton = "\n\nPress the + buttons, when available, to add either a new field from the same csv file (the + button at the end of this line) or a new csv file (the + button next to File at the top of this GUI). Multiple csv files can be used with any of the operations."
        # OKButton = "\n\nPress the OK button, when available, to accept the selections made, then press the RUN button to process the query."
        if not IO_setup_display_brief:
            y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_csvFile)
            y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                          GUI_IO_util.msg_outputDirectory)
        else:
            y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                          GUI_IO_util.msg_IO_setup)

        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Select and display the csv file in your file list. Click the Open button to open the selected csv file.")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                             "NLP Suite Help",
                                                             'Tick the \'GUIs available for more analyses\' checkbox, then use the dropdown menu to open a related tool for further csv analysis:\n\n   CSV data manipulation with SQL: manipulate csv files using SQL queries;\n   CSV data visualization: visualize your data in a variety of ways;\n   Statistics on csv files: compute frequencies, cross-tabulations, and statistics on csv data.\n\nThe selected GUI will open as soon as you pick it from the menu, without having to press the RUN button.')

        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Use the operation dropdown menu to choose what to do with your csv file(s). The widgets on this row become active according to the operation you select:\n\n"
                                      "   APPEND rows: stack the rows of two or more csv files that share the same fields into a single file. Use the '+' file button to add files.\n\n"
                                      "   CONCATENATE fields: join two or more fields into a new field, separated by the character(s) you type in the Character separator box. Use the '+' field button to add fields.\n\n"
                                      "   SPLIT field: the inverse of CONCATENATE - split one field into several new fields at the Character separator.\n\n"
                                      "   DROP rows: delete the rows that meet a WHERE condition (see the WHERE clause row below).\n\n"
                                      "   EXTRACT field(s): save selected field(s) to a new csv or txt file, optionally filtered by a WHERE condition. Tick 'csv output' for csv, untick for txt.\n\n"
                                      "   MERGE files: join two or more csv files on one or more overlapping key field(s) - the equivalent of an SQL JOIN. Use the '+' file button to add a file and select its key field.\n\n"
                                      "   SORT rows: sort the file (ascending) by the selected field(s); use the '+' field button to add more sort keys.\n\n"
                                      "   DEDUPLICATE rows: remove duplicate rows - judged on the selected key field(s), or on the whole row if no field is selected.\n\n"
                                      "   RENAME field: rename the selected field; type the NEW name in the Character separator box.\n\n"
                                      "Select the field to operate on from the 'Select field' dropdown. Press the '+' buttons, when active, to add another field or another csv file. Press OK to register your selections (they appear in the display box), then press RUN.")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "The WHERE clause filters rows by field value. It is available for the DROP and EXTRACT operations only.\n\n"
                                      "After selecting a field, click the 'WHERE clause' button to activate the widgets, then:\n\n"
                                      "   select a comparator (e.g., =, <>, >, >=, <, <=);\n"
                                      "   type the value to compare against in the WHERE box (CASE SENSITIVE!);\n"
                                      "   choose and/or to combine with a further condition, then press the '+' button to add it.\n\n"
                                      "Examples: EXTRACT only the rows where Year >= 1997; DROP the rows where Stopword = the.\n\n"
                                      "Leave the WHERE clause empty to operate on all rows.")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      resetAll + "\n\nThe read-only widget after the 'RESET all' button displays the arguments that will be processed when pressing the RUN button for the selected operation:\n\n   csv filename\n   csv column/field.\n   For the Concatenate option the character separator will also be displayed.\n   For the Drop and Extract options, the comparator value (e.g., =, >), the WHERE value, and the selected add/or option will be displayed.")
        # empty line to account for the height of the text widget
        y_multiplier_integer = y_multiplier_integer + 1
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                             "NLP Suite Help", GUI_IO_util.msg_openOutputFiles)
        return y_multiplier_integer -1

    y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

    # change the value of the readMe_message
    readMe_message = "The Python 3 scripts provide several ways of handling data from csv files.\n\nIn INPUT, the script takes one or more csv files depending upon the selected operation.\n\nIn OUTPUT, the script creates a new csv file.\n\nThe following operation are possible.\n\n   1. MERGE different csv files using one or more overlapping common field(s) as a way to JOIN the files together;\n   2. CONCATENATE into a single field the values of different fields from one csv file;\n   3. APPEND the content of different fields from one csv file after the content of a selected target field;\n   4. EXTRACT fields from one csv file, perhaps by specific field values (the equivalent of an SQL WHERE clause);\n   4. DROP dulicate rows from one csv file."
    readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
    GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief,scriptName,True)

    # TODO must uncomment
    # GUI_util.inputFilename.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))
    # changed_filename(inputFilename.get())

    if (GUI_util.input_main_dir_path.get() != '') or (os.path.basename(GUI_util.inputFilename.get())[-4:] != ".csv"):
        GUI_util.run_button.configure(state='disabled')
        mb.showwarning(title='Input file',
                       message="The Data manipulation scripts require in input a csv file.\n\nAll options and RUN button are disabled until the expected csv file is seleted in input.\n\nPlease, select in input a csv file and try again.")
        error = True
    else:
        error = False
        GUI_util.run_button.configure(state='normal')

    activate_all_options()

    # CLI argument: --inputfile to pre-load a CSV file (e.g., from DB_SQL_main)
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

    # GUI_util.window.attributes("-topmost", True)
    # GUI_util.window.focus_force()
    GUI_util.window.mainloop()
