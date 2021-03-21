import os.path
import sys
import IO_files_util
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"data_manager.py", ['os', 'tkinter', 'pandas', 'functools'])==False:
    sys.exit(0)

import tkinter as tk
import pandas as pd
from functools import reduce
import tkinter.messagebox as mb

import GUI_IO_util
import IO_csv_util

# RUN section ______________________________________________________________________________________________________________________________________________________


def listToString(s, sep):
    str1 = ""
    for ele in s:
        str1 = str1 + ele + sep
    return str1[:-1]


def get_comparator(phrase: str) -> str:
    if phrase == 'not equals':
        return '!='
    elif phrase == 'equals':
        return '=='
    elif phrase == 'greater than':
        return '>'
    elif phrase == 'greater than or equals':
        return '>='
    elif phrase == 'less than':
        return '<'
    elif phrase == 'less than or equals':
        return '<='
    else:
        return ''
        # assert False, "Invalid comparator phrase"


def select_csv(files):
    for file in files:
        df = pd.read_csv(file)
        yield df


def select_columns(dfs: list, columns: list):
    for df in get_cols(dfs, columns):
        yield df


def concat(dfs: list, separator: str):
    s = pd.DataFrame
    for i in range(len(dfs)):
        if i == 0:
            s = dfs[i].astype(str) + separator
        else:
            if i != len(dfs) - 1:
                s = s + dfs[i].astype(str) + separator
            else:
                s = s + dfs[i].astype(str)
    return s


# helper method
def get_cols(dfs: list, headers: list):
    if len(headers) != len(dfs):
        return 'Unmatching number of dataframes and headers'
    else:
        for i in range(len(dfs)):
            yield (dfs[i])[headers[i]]


filesToOpen = []  # Store all files that are to be opened once finished


def extract_from_csv(path, output_path, data_files, csv_file_field_list):
    outputFilename = IO_files_util.generate_output_file_name(path[0], os.path.dirname(path[0]), output_path, '.csv',
                                                             'extract',
                                                             'stats', '', '', '', False, True)
    sign_var = [s.split(',')[2] for s in csv_file_field_list]
    value_var = [s.split(',')[3] for s in csv_file_field_list]
    headers = [s.split(',')[1] for s in csv_file_field_list]
    if len(data_files) <= 1:
        data_files = data_files * len(headers)
    df_list = []
    value: str
    header: str
    if len(csv_file_field_list)==0:
        mb.showwarning(title='Missing field(s)',
                       message="No field(s) to be extracted have been selected.\n\nPlease, select field(s) and try again.")
        return
    for (sign, value, header, df) in zip(sign_var, value_var, headers, data_files):
        if ' ' in header:
            header = "`" + header + "`"
        if sign == "''" and value == "''":
            df_list.append(df[[header]])
        else:
            sign = get_comparator(sign)
            if sign=='':
                mb.showwarning(title='Missing sign condition',
                               message="No condition has been entered for the \'WHERE\' value entered.\n\nPlease, include a condition for the \'WHERE\' value and try again.")
                return
            if '\'' not in value and not value.isdigit():
                value = '\'' + value + '\''
            query = header + sign + value
            result = df.query(query, engine='python')
            df_list.append(result)
    df_extract = df_list[0]
    for index, df_ex in enumerate(df_list):

        if csv_file_field_list[index].split(',')[4] in ['and', "''"]:
            if index == len(df_list) - 1:
                continue
            df_extract = df_extract.merge(df_list[index + 1], how='inner',
                                          right_index=True,
                                          left_index=True)
        elif csv_file_field_list[index].split(',')[4] == 'or':
            if index == len(df_list) - 1:
                continue
            df_extract = df_extract.merge(df_list[index + 1], how='outer',
                                          right_index=True,
                                          left_index=True)
        elif csv_file_field_list[index].split(',')[4] == '' and index != len(df_list) - 1:
            mb.showwarning(title='Missing and/or condition',
                           message="Please include an and/or condition between each WHERE condition on the column you want to extract!")
        else:
            pass
    df_extract.to_csv(outputFilename,index=False)
    filesToOpen.append(outputFilename)
    return filesToOpen


def run(inputFilename,
        csv_file_field_list,
        merge_var, concatenate_var,
        append_var, extract_var,
        purge_row_var, select_csv_field_purge_var, keep_most_recent_var, keep_most_fields_var, select_csv_field2_purge_var,
        openOutputFiles, output_path):

    path = [s.split(',')[0] for s in csv_file_field_list]  # file path
    data_files = [file for file in select_csv(path)]  # dataframes
    headers = [s.split(',')[1] for s in csv_file_field_list]  # headers
    data_cols = [file for file in get_cols(data_files, headers)]  # selected cols

    if merge_var:
        outputFilename = IO_files_util.generate_output_file_name(path[0], os.path.dirname(path[0]), output_path, '.csv', 'merge',
                                                           'stats', '', '', '', False, True)
        df_merged = reduce(lambda left, right: pd.merge(left, right, on=headers[0], how='inner'), data_files)
        df_merged.to_csv(outputFilename)
        filesToOpen.append(outputFilename)
    if concatenate_var:
        outputFilename = IO_files_util.generate_output_file_name(path[0], os.path.dirname(path[0]), output_path, '.csv', 'concatenate',
                                                           'stats', '', '', '', False, True)
        for s in csv_file_field_list:
            if s[-1] == ',':
                sep = ','
            else:
                temp = s.split(',')
                if len(temp) >= 3:
                    sep = temp[2]
                    break
        df_concat = concat(data_cols, sep)  # TODO: Could sep potentially be null?
        df_concat.to_csv(outputFilename, header=[listToString(headers, sep)])
        filesToOpen.append(outputFilename)
    if append_var:
        outputFilename = IO_files_util.generate_output_file_name(path[0], os.path.dirname(path[0]), output_path, '.csv', 'append',
                                                           'stats', '', '', '', False, True)
        sep = ','
        df_append = pd.concat(data_cols, axis=0)
        df_append.to_csv(outputFilename, header=[listToString(headers, sep)])
        filesToOpen.append(outputFilename)
    if extract_var:
        extract_from_csv(path=path, output_path=output_path,
                         data_files=data_files, csv_file_field_list=csv_file_field_list)
    if purge_row_var:
        import file_filename_util
        if keep_most_recent_var:
            file_filename_util.purge_duplicate_rows_byFilename(GUI_util.window,inputFilename, output_path, openOutputFiles, select_csv_field_purge_var)
        if keep_most_fields_var:
            file_filename_util.purge_partial_matches(GUI_util.window,inputFilename, output_path, openOutputFiles, select_csv_field_purge_var, select_csv_field2_purge_var)


    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)


# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated

if __name__ == '__main__':
    run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                     csv_file_field_list,
                                     merge_var.get(), concatenate_var.get(),
                                     append_var.get(), extract_var.get(),
                                     purge_row_var.get(), select_csv_field_purge_var.get(), keep_most_recent_var.get(),
                                     keep_most_fields_var.get(), select_csv_field2_purge_var.get(),
                                     GUI_util.open_csv_output_checkbox.get(), GUI_util.output_dir_path.get()
                                     )

    GUI_util.run_button.configure(command=run_script_command)

    # GUI section ______________________________________________________________________________________________________________________________________________________

    GUI_size = '1250x680'
    GUI_label = 'Graphical User Interface (GUI) for Data Manager'
    config_filename = 'data-manager-config.txt'
    # The 6 values of config_option refer to:
    #   software directory
    #   input file
            # 1 for CoNLL file
            # 2 for TXT file
            # 3 for csv file
            # 4 for any type of file
            # 5 for txt or html
            # 6 for txt or csv
    #   input dir
    #   input secondary dir
    #   output file
    #   output dir
    config_option = [0, 3, 0, 0, 0, 1]

    GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

    # in csv_file_field_list, the script returns a list of comma-separated csv filename + csv field
    # when using the extract option, csv_file_field_list will also list the where and and/or values
    # repeated csv fields will be skipped
    # for instance
    # ['C:/Program Files (x86)/NLP_backup/Output/EnglishANEW.csv,A.SD.F', 'C:/Program Files (x86)/NLP_backup/Output/EnglishANEW.csv,D.Mean.M']

    # GUI CHANGES search for GUI CHANGES

    # GUI CHANGES add following lines to every special GUI
    # +1 is the number of lines starting at 1 of IO widgets
    y_multiplier_integer = GUI_util.y_multiplier_integer + 1
    window = GUI_util.window
    config_input_output_options = GUI_util.config_input_output_options
    config_filename = GUI_util.config_filename
    inputFilename = GUI_util.inputFilename

    GUI_util.GUI_top(config_input_output_options, config_filename)

    # GUI CHANGES cut/paste special GUI widgets from GUI_util
    csv_file_field_list = []
    merge_var = tk.IntVar()
    concatenate_var = tk.IntVar()
    character_separator_var = tk.StringVar()
    append_var = tk.IntVar()
    extract_var = tk.IntVar()
    purge_row_var = tk.IntVar()

    keep_most_recent_var = tk.IntVar()

    keep_most_fields_var = tk.IntVar()
    select_csv_field2_purge_var = tk.StringVar()

    # de-indent all commands

    current_pair_file_field_var = tk.Label(text="Current matched pair of csv filename and fields",
                                           font="Helvetica 10 italic")
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                                                   current_pair_file_field_var)

    avoidLoop = False


    def clear(e):
        select_csv_field_merge_var.set('')
        select_csv_field_concatenate_var.set('')
        select_csv_field_append_var.set('')
        select_csv_field_extract_var.set('')
        character_separator_entry_var.set("")
        comparator_var.set('')
        where_entry_var.set('')
        and_or_var.set('')
        GUI_util.clear("Escape")

    window.bind("<Escape>", clear)


    def reset_all_values():
        clear("<Escape>")
        reset_csv_field_values()
        csv_file_field_list.clear()
        file_number_var.set(1)
        selected_fields_var.set('')
        selectedCsvFile_var.set(GUI_util.inputFilename.get())
        operation_text_var.set('')

        add_file_button.config(state='disabled')
        merge_checkbox.config(state='normal')
        concatenate_checkbox.config(state='normal')
        append_checkbox.config(state='normal')
        extract_checkbox.config(state='normal')
        purge_row_checkbox.config(state='normal')

        # a text widget is read only when disabled
        csv_file_field.configure(state='normal')
        csv_file_field.delete(0.1, tk.END)
        csv_file_field.configure(state='disabled')

        character_separator_entry_var.set("")

        comparator_menu.configure(state="disabled")
        where_entry.configure(state="disabled")
        and_or_menu.configure(state="disabled")

        where_entry_var.set("")
        comparator_var.set("")
        and_or_var.set("")

        select_csv_field_merge_menu.config(state='disabled')
        select_csv_field_concatenate_menu.config(state='disabled')
        select_csv_field_append_menu.config(state='disabled')
        select_csv_field_extract_menu.config(state='disabled')
        select_csv_field_purge_menu.config(state='disabled')
        select_csv_field2_purge_menu.config(state='disabled')

        merge_var.set(0)
        concatenate_var.set(0)
        append_var.set(0)
        extract_var.set(0)


    def reset_csv_field_values():
        selected_fields_var.set('')


    file_number_var = tk.IntVar()
    file_number_var.set(1)
    file_lb = tk.Label(window, text='File ')
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer, file_lb,
                                                   True)
    file_number = tk.Entry(window, width=3, textvariable=file_number_var)
    file_number.config(state="disabled")
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 50, y_multiplier_integer,
                                                   file_number, True)

    add_file_button = tk.Button(window, text='+', width=2, height=1, state='disabled',
                                command=lambda: get_additional_csvFile(window, 'Select INPUT csv file',
                                                                       [("csv files", "*.csv")]))
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 100, y_multiplier_integer,
                                                   add_file_button, True)

    # setup a button to open Windows Explorer on the selected input directory
    openInputFile_button = tk.Button(window, width=3, text='',
                                     command=lambda: IO_files_util.openFile(window,
                                                                            selectedCsvFile_var.get()))
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.open_file_directory_coordinate, y_multiplier_integer,
                                                   openInputFile_button,True)

    # openInputFile_button.place(x=GUI_IO_util.get_open_file_directory_coordinate,
    #                            y=y_multiplier_integer,True)

    selectedCsvFile_var = tk.StringVar()
    selectedCsvFile = tk.Entry(window, width=100, textvariable=selectedCsvFile_var)
    selectedCsvFile.config(state='disabled')
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                                                   selectedCsvFile)


    def get_additional_csvFile(window, title, fileType):
        import os
        initialFolder = os.path.dirname(os.path.abspath(__file__))
        filePath = tk.filedialog.askopenfilename(title=title, initialdir=initialFolder, filetypes=fileType)
        if len(filePath) > 0:
            select_csv_field_merge_var.set('')
            select_csv_field_concatenate_var.set('')
            select_csv_field_append_var.set('')
            select_csv_field_extract_var.set('')
            selected_fields_var.set('')

            selectedCsvFile_var.set(filePath)
            file_number_var.set(file_number_var.get() + 1)

            changed_filename(selectedCsvFile_var.get())


    if GUI_util.inputFilename.get() != '':
        if selectedCsvFile_var.get() == '':
            selectedCsvFile_var.set(GUI_util.inputFilename.get())
        numColumns = IO_csv_util.get_csvfile_numberofColumns(GUI_util.inputFilename.get())
        if IO_csv_util.csvFile_has_header(GUI_util.inputFilename.get()) == False:
            menu_values = range(1, numColumns + 1)
        else:
            data, headers = IO_csv_util.get_csv_data(GUI_util.inputFilename.get(), True)
            menu_values = headers
    else:
        numColumns = 0
        menu_values = " "
    if numColumns == -1:
        pass
    # eturn

    reset_field_button = tk.Button(window, width=15, text='Reset csv field(s)', state='disabled',
                                   command=lambda: reset_csv_field_values())
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                                   reset_field_button, True)

    selected_fields_var = tk.StringVar()
    selected_fields_var.set('')
    selected_fields = tk.Entry(window, width=100, textvariable=selected_fields_var)
    selected_fields.configure(state="disabled")
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                                                   selected_fields)

    reset_all_button = tk.Button(window, width=15, text='Reset all', state='normal', command=lambda: reset_all_values())
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                                   reset_all_button, True)

    # a text widget is read only when disabled
    csv_file_field = tk.Text(window, width=100, height=3, state="disabled")
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer, csv_file_field,
                                                   True)

    operation_text_var = tk.StringVar()
    operation_text_var.set('')
    operation_text = tk.Entry(window, width=20, textvariable=operation_text_var)
    operation_text.configure(state="disabled")
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 140, y_multiplier_integer,
                                                   operation_text, True)


    # operation is a string with values "merge", "concatenate", "append", "extract"
    # menu_choice is the menu value of the spcecific csv field selected  (e.g., select_csv_field_concatenate_var.get())
    # it returns a list to be passed to data_handling.py for processing

    def add_field_to_list(operation, menu_choice, visualizeBuildString=True):
        # skip empty values and csv fields already selected
        if select_csv_field_merge_var.get() == '' and select_csv_field_concatenate_var.get() == '' and select_csv_field_append_var.get() == '' and select_csv_field_extract_var.get() == '':
            return

        buildString = selectedCsvFile_var.get() + "," + menu_choice

        if selected_fields_var.get() != '' and menu_choice not in selected_fields_var.get():
            selected_fields_var.set(selected_fields_var.get() + "," + str(menu_choice))
        else:
            selected_fields_var.set(menu_choice)

        if operation == "concatenate":
            character_separator_entry.get()
            if select_csv_field_concatenate_var.get() != '' and character_separator_entry.get() != '':
                buildString = buildString + "," + character_separator_entry.get()
            else:
                buildString = ''

        if operation == 'extract':
            if comparator_var.get() != '' and where_entry_var.get() == '':
                mb.showwarning(title='Warning',
                               message='You have selected the comparator value ' + comparator_var.get() + '\n\nYou MUST enter a WHERE value or press ESC to cancel.')
                return
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

        csv_file_field_list.append(buildString)
        # visualizeBuildString is True when clicking the OK button for the Concatenate and Extract operations
        if visualizeBuildString == True:
            operation_text_var.set(str(operation).upper())  # + " list"
            # a text widget is read only when disabled
            csv_file_field.configure(state='normal')
            csv_file_field.insert("end", str(csv_file_field_list))
            csv_file_field.configure(state='disabled')
            reset_field_button.config(state="normal")


    y_multiplier_integer = y_multiplier_integer + 2

    # _____________________________________________________________________________


    merge_var.set(0)
    merge_checkbox = tk.Checkbutton(window, text='Merge files (Join)', variable=merge_var, onvalue=1, offvalue=0)
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                                   merge_checkbox, True)

    select_csv_field_lb = tk.Label(window, text='Select field')
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 200, y_multiplier_integer,
                                                   select_csv_field_lb, True)

    select_csv_field_merge_var = tk.StringVar()
    select_csv_field_merge_menu = tk.OptionMenu(window, select_csv_field_merge_var, *menu_values)
    select_csv_field_merge_menu.configure(state='disabled', width=12)
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 300, y_multiplier_integer,
                                                   select_csv_field_merge_menu, True)


    def build_merge_string(comingFrom_Plus, comingFrom_OK):
        add_field_to_list("merge", select_csv_field_merge_var.get(), comingFrom_OK)
        # if comingFrom_Plus == True:
        #     mb.showwarning(title='Warning',
        #                    message='With the MERGE option you cannot select another csv column/field. You can only add another file and a field from that file to serve as match with the already selected field(s).\n\nYou will be redirected to selecting a new csv file.')
        #     get_additional_csvFile(window, 'Select INPUT csv file', [("csv files", "*.csv")])
        activate_csv_fields_selection('merge', merge_var.get(), comingFrom_Plus, comingFrom_OK)


    add_merge_options_var = tk.IntVar()
    add_merge_options = tk.Button(window, text='+', width=2, height=1, state='disabled',
                                  command=lambda: build_merge_string(True, False))
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 1000, y_multiplier_integer,
                                                   add_merge_options, True)

    OK_merge_button = tk.Button(window, text='OK', width=3, height=1, state='disabled',
                                command=lambda: build_merge_string(False, True))
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 1050, y_multiplier_integer,
                                                   OK_merge_button)

    # _____________________________________________________________________________

    concatenate_var.set(0)
    concatenate_checkbox = tk.Checkbutton(window, text='Concatenate field values', variable=concatenate_var, onvalue=1,
                                          offvalue=0)
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                                   concatenate_checkbox, True)

    select_csv_field_lb = tk.Label(window, text='Select field')
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 200, y_multiplier_integer,
                                                   select_csv_field_lb, True)

    select_csv_field_concatenate_var = tk.StringVar()
    select_csv_field_concatenate_menu = tk.OptionMenu(window, select_csv_field_concatenate_var, *menu_values)
    select_csv_field_concatenate_menu.configure(state='disabled', width=12)
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 300, y_multiplier_integer,
                                                   select_csv_field_concatenate_menu, True)

    character_separator_lb = tk.Label(window, text='Character(s) separator')
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 450, y_multiplier_integer,
                                                   character_separator_lb, True)

    character_separator_entry_var = tk.StringVar()
    character_separator_entry = tk.Entry(window, width=5, textvariable=character_separator_entry_var)
    character_separator_entry.config(state='disabled')
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 600, y_multiplier_integer,
                                                   character_separator_entry, True)


    def build_concatenate_string(comingFrom_Plus, comingFrom_OK):
        add_field_to_list("concatenate", select_csv_field_concatenate_var.get(), comingFrom_OK)
        activate_csv_fields_selection('concatenate', concatenate_var.get(), comingFrom_Plus, comingFrom_OK)


    add_concatenate_options_var = tk.IntVar()
    add_concatenate_options = tk.Button(window, text='+', width=2, height=1, state='disabled',
                                        command=lambda: build_concatenate_string(True, False))
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 1000, y_multiplier_integer,
                                                   add_concatenate_options, True)

    OK_concatenate_button = tk.Button(window, text='OK', width=3, height=1, state='disabled',
                                      command=lambda: build_concatenate_string(False, True))
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 1050, y_multiplier_integer,
                                                   OK_concatenate_button)

    # _____________________________________________________________________________

    append_var.set(0)
    append_checkbox = tk.Checkbutton(window, text='Append field values', variable=append_var, onvalue=1, offvalue=0)
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                                   append_checkbox, True)

    select_csv_field_lb = tk.Label(window, text='Select field')
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 200, y_multiplier_integer,
                                                   select_csv_field_lb, True)

    select_csv_field_append_var = tk.StringVar()
    select_csv_field_append_menu = tk.OptionMenu(window, select_csv_field_append_var, *menu_values)
    select_csv_field_append_menu.configure(state='disabled', width=12)
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 300, y_multiplier_integer,
                                                   select_csv_field_append_menu, True)


    def build_append_string(comingFrom_Plus, comingFrom_OK):
        add_field_to_list("append", select_csv_field_append_var.get(), comingFrom_OK)
        activate_csv_fields_selection('append', append_var.get(), comingFrom_Plus, comingFrom_OK)


    add_append_options_var = tk.IntVar()
    add_append_options = tk.Button(window, text='+', width=2, height=1, state='disabled',
                                   command=lambda: build_append_string(True, False))
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 1000, y_multiplier_integer,
                                                   add_append_options, True)

    OK_append_button = tk.Button(window, text='OK', width=3, height=1, state='disabled',
                                 command=lambda: build_append_string(False, True))
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 1050, y_multiplier_integer,
                                                   OK_append_button)

    # _____________________________________________________________________________


    extract_var.set(0)
    extract_checkbox = tk.Checkbutton(window, text='Extract field(s) from csv file', variable=extract_var, onvalue=1,
                                      offvalue=0)
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                                   extract_checkbox, True)

    # extract_var.trace('w',)

    select_csv_field_lb = tk.Label(window, text='Select field')
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 200, y_multiplier_integer,
                                                   select_csv_field_lb, True)

    select_csv_field_extract_var = tk.StringVar()
    select_csv_field_extract_menu = tk.OptionMenu(window, select_csv_field_extract_var, *menu_values)
    select_csv_field_extract_menu.configure(state='disabled', width=12)
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 300, y_multiplier_integer,
                                                   select_csv_field_extract_menu, True)

    # TODO from a GUI, how can you select a specific value of selected field,
    # rather than entering the value?

    comparator_var = tk.StringVar()
    comparator_menu = tk.OptionMenu(window, comparator_var, 'not equals', 'equals', 'greater than',
                                    'greater than or equals', 'less than', 'less than or equals')
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 450, y_multiplier_integer,
                                                   comparator_menu, True)

    where_lb = tk.Label(window, text='WHERE')
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 590, y_multiplier_integer,
                                                   where_lb, True)

    where_entry_var = tk.StringVar()
    where_entry = tk.Entry(window, width=30, textvariable=where_entry_var)
    where_entry.configure(state="disabled")
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 670, y_multiplier_integer,
                                                   where_entry, True)

    and_or_lb = tk.Label(window, text='and/or')
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 860, y_multiplier_integer,
                                                   and_or_lb, True)

    and_or_var = tk.StringVar()
    and_or_menu = tk.OptionMenu(window, and_or_var, 'and', 'or')
    and_or_menu.configure(state="disabled", width=3)
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 910, y_multiplier_integer,
                                                   and_or_menu, True)


    def build_extract_string(comingFrom_Plus, comingFrom_OK):
        add_field_to_list("extract", select_csv_field_extract_var.get(), comingFrom_OK)
        activate_csv_fields_selection('extract', extract_var.get(), comingFrom_Plus, comingFrom_OK)


    add_extract_options_var = tk.IntVar()
    add_extract_options = tk.Button(window, text='+', width=2, height=1, state='disabled',
                                    command=lambda: build_extract_string(True, False))
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 1000, y_multiplier_integer,
                                                   add_extract_options, True)

    OK_extract_button = tk.Button(window, text='OK', width=3, height=1, state='disabled',
                                  command=lambda: build_extract_string(False, True))
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 1050, y_multiplier_integer,
                                                   OK_extract_button)

    # _____________________________________________________________________________

    purge_row_var.set(0)
    purge_row_checkbox = tk.Checkbutton(window, text='Purge duplicate rows', variable=purge_row_var, onvalue=1, offvalue=0)
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                                   purge_row_checkbox, True)

    # purge_row_var

    select_csv_field_lb = tk.Label(window, text='Select field')
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 200, y_multiplier_integer,
                                                   select_csv_field_lb, True)

    select_csv_field_purge_var = tk.StringVar()
    select_csv_field_purge_menu = tk.OptionMenu(window, select_csv_field_purge_var, *menu_values)
    select_csv_field_purge_menu.configure(state='disabled', width=12)
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 300, y_multiplier_integer,
                                                   select_csv_field_purge_menu, True)

    keep_most_recent_checkbox = tk.Checkbutton(window, text='Keep row with most recent file', variable=keep_most_recent_var,
                                               onvalue=1, offvalue=0)
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 450, y_multiplier_integer,
                                                   keep_most_recent_checkbox, True)

    keep_most_fields_checkbox = tk.Checkbutton(window, text='Keep row with most items', variable=keep_most_fields_var,
                                               onvalue=1, offvalue=0)
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 670, y_multiplier_integer,
                                                   keep_most_fields_checkbox, True)

    select_csv_field2_lb = tk.Label(window, text='Select second field')
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 850, y_multiplier_integer,
                                                   select_csv_field2_lb, True)

    select_csv_field2_purge_var = tk.StringVar()
    select_csv_field2_purge_menu = tk.OptionMenu(window, select_csv_field2_purge_var, *menu_values)
    select_csv_field2_purge_menu.configure(state='disabled', width=12)
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 1000, y_multiplier_integer,
                                                   select_csv_field2_purge_menu)


    def activate_purge_fields(*args):
        keep_most_recent_checkbox.configure(state='normal')
        keep_most_fields_checkbox.configure(state='normal')
        if keep_most_recent_var.get():
            # keep_most_fields_var.set(0)
            keep_most_fields_checkbox.configure(state='disabled')
            select_csv_field2_purge_menu.configure(state='disabled', width=12)
        else:
            keep_most_fields_checkbox.configure(state='normal')
            select_csv_field2_purge_menu.configure(state='normal', width=12)
        if keep_most_fields_var.get():
            # keep_most_recent_var.set(0)
            keep_most_recent_checkbox.configure(state='disabled')
        else:
            keep_most_recent_checkbox.configure(state='normal')


    keep_most_recent_var.trace('w', activate_purge_fields)
    keep_most_fields_var.trace('w', activate_purge_fields)


    def activateResetFields(*args):
        if selected_fields_var.get() != '':
            reset_field_button.config(state='normal')
        else:
            reset_field_button.config(state='disabled')


    selected_fields_var.trace('w', activateResetFields)


    # _____________________________________________________________________________


    def changed_filename(tracedInputFile):
        menu_values = []
        if tracedInputFile != '':
            numColumns = IO_csv_util.get_csvfile_numberofColumns(tracedInputFile)
            if numColumns == 0 or numColumns == None:
                return False
            if IO_csv_util.csvFile_has_header(tracedInputFile) == False:
                menu_values = range(1, numColumns + 1)
            else:
                data, headers = IO_csv_util.get_csv_data(tracedInputFile, True)
                menu_values = headers
        else:
            menu_values.clear()
            return
        m1 = select_csv_field_merge_menu["menu"]
        m1.delete(0, "end")
        m2 = select_csv_field_concatenate_menu["menu"]
        m2.delete(0, "end")
        m3 = select_csv_field_append_menu["menu"]
        m3.delete(0, "end")
        m4 = select_csv_field_extract_menu["menu"]
        m4.delete(0, "end")
        m5 = select_csv_field_purge_menu["menu"]
        m5.delete(0, "end")
        m6 = select_csv_field2_purge_menu["menu"]
        m6.delete(0, "end")

        for s in menu_values:
            m1.add_command(label=s, command=lambda value=s: select_csv_field_merge_var.set(value))
            m2.add_command(label=s, command=lambda value=s: select_csv_field_concatenate_var.set(value))
            m3.add_command(label=s, command=lambda value=s: select_csv_field_append_var.set(value))
            m4.add_command(label=s, command=lambda value=s: select_csv_field_extract_var.set(value))
            m5.add_command(label=s, command=lambda value=s: select_csv_field_purge_var.set(value))
            m6.add_command(label=s, command=lambda value=s: select_csv_field2_purge_var.set(value))

        if tracedInputFile != GUI_util.inputFilename.get():
            selectedCsvFile_var.set(selectedCsvFile_var.get())
        else:
            selectedCsvFile_var.set(GUI_util.inputFilename.get())
        reset_csv_field_values()
        clear("<Escape>")


    GUI_util.inputFilename.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))

    changed_filename(GUI_util.inputFilename.get())

    selectedCsvFile_var.trace('w', lambda x, y, z: changed_filename(selectedCsvFile_var.get()))

    changed_filename(selectedCsvFile_var.get())


    def activate_csv_fields_selection(operation, checkButton, comingFrom_Plus, comingFrom_OK):
        keep_most_recent_checkbox.config(state='disabled')
        keep_most_fields_checkbox.config(state='disabled')
        if checkButton == False:
            add_file_button.config(state='disabled')
            merge_checkbox.config(state='normal')
            concatenate_checkbox.config(state='normal')
            append_checkbox.config(state='normal')
            extract_checkbox.config(state='normal')
            purge_row_checkbox.config(state='normal')
        else:
            reset_all_button.config(state='normal')

        if operation == "merge":
            if checkButton == True:
                select_csv_field_merge_menu.config(state='normal')
                concatenate_checkbox.config(state='disabled')
                append_checkbox.config(state='disabled')
                extract_checkbox.config(state='disabled')
                if select_csv_field_merge_var.get() != '':
                    select_csv_field_merge_menu.config(state='disabled')
                    # you cannot add another field from the same file in merge;
                    # should always be disabled, but having it enabled allows to display a warning
                    add_file_button.config(state='normal')
                    add_merge_options.config(state='normal')
                    OK_merge_button.config(state='normal')
                    if comingFrom_Plus == True:
                        select_csv_field_merge_menu.configure(state='normal')
                    if comingFrom_OK == True:
                        select_csv_field_merge_menu.configure(state='disabled')
                        add_file_button.config(state='disabled')
                        add_merge_options.config(state='disabled')
                        OK_merge_button.config(state='disabled')
                else:
                    # you cannot add another field from the same file in merge
                    add_merge_options.config(state='disabled')
                    OK_merge_button.config(state='disabled')

            else:
                select_csv_field_merge_var.set("")
                select_csv_field_merge_menu.config(state='disabled')
                add_merge_options.config(state='disabled')
                OK_merge_button.config(state='disabled')
                concatenate_checkbox.config(state='normal')
                append_checkbox.config(state='normal')
                extract_checkbox.config(state='normal')
                purge_row_checkbox.config(state='normal')

        elif operation == "concatenate":
            if checkButton == True:
                select_csv_field_concatenate_menu.config(state='normal')

                merge_checkbox.config(state='disabled')
                append_checkbox.config(state='disabled')
                extract_checkbox.config(state='disabled')
                purge_row_checkbox.config(state='disabled')

                if select_csv_field_concatenate_var.get() != '':
                    select_csv_field_concatenate_menu.config(state='disabled')
                    if character_separator_entry_var.get() != '':
                        character_separator_entry.config(state='disabled')
                    else:
                        character_separator_entry.config(state='normal')
                else:
                    select_csv_field_concatenate_menu.config(state='normal')
                    character_separator_entry.config(state='disabled')
                if character_separator_entry_var.get() != '':
                    add_file_button.config(state='normal')
                    add_concatenate_options.config(state='normal')
                    OK_concatenate_button.config(state='normal')

                    if comingFrom_Plus == True:
                        select_csv_field_concatenate_menu.configure(state='normal')
                        character_separator_entry.config(state='disabled')
                    if comingFrom_OK == True:
                        select_csv_field_concatenate_menu.configure(state='disabled')
                        character_separator_entry.config(state='disabled')
                        add_file_button.config(state='disabled')
                        add_concatenate_options.config(state='disabled')
                        OK_concatenate_button.config(state='disabled')
            else:
                select_csv_field_concatenate_var.set("")
                select_csv_field_concatenate_menu.config(state='disabled')
                character_separator_entry.config(state='disabled')
                character_separator_entry_var.set('')
                add_concatenate_options.config(state='disabled')
                OK_concatenate_button.config(state='disabled')

                merge_checkbox.config(state='normal')
                append_checkbox.config(state='normal')
                extract_checkbox.config(state='normal')
                purge_row_checkbox.config(state='normal')

        elif operation == "append":
            if checkButton == True:
                select_csv_field_append_menu.config(state='normal')
                merge_checkbox.config(state='disabled')
                concatenate_checkbox.config(state='disabled')
                extract_checkbox.config(state='disabled')
                purge_row_checkbox.config(state='disabled')

                if select_csv_field_append_var.get() != '':
                    select_csv_field_append_menu.configure(state='disabled')
                    add_file_button.config(state='normal')
                    add_append_options.config(state='normal')
                    OK_append_button.config(state='normal')
                    if comingFrom_Plus == True:
                        select_csv_field_append_menu.configure(state='normal')
                    if comingFrom_OK == True:
                        select_csv_field_append_menu.configure(state='disabled')
                        add_file_button.config(state='disabled')
                        add_append_options.config(state='disabled')
                        OK_append_button.config(state='disabled')
                else:
                    add_file_button.config(state='disabled')
                    add_append_options.config(state='disabled')
                    OK_append_button.config(state='disabled')
            else:
                select_csv_field_append_var.set('')
                select_csv_field_append_menu.config(state='disabled')
                add_append_options.config(state='disabled')
                OK_append_button.config(state='disabled')
                merge_checkbox.config(state='normal')
                concatenate_checkbox.config(state='normal')
                extract_checkbox.config(state='normal')
                purge_row_checkbox.config(state='normal')

        elif operation == "extract":
            if checkButton == True:

                if select_csv_field_extract_var.get() != '':
                    if comingFrom_Plus == True:
                        select_csv_field_extract_menu.configure(state='normal')
                    else:
                        select_csv_field_extract_menu.configure(state='disabled')

                    if where_entry_var.get() != '':
                        and_or_menu.configure(state='normal')
                    else:
                        and_or_menu.configure(state='disabled')

                    if comingFrom_OK == True:
                        comparator_menu.configure(state="disabled")
                        where_entry.configure(state="disabled")
                        and_or_menu.configure(state='disabled')
                        add_file_button.config(state='disabled')
                        add_extract_options.config(state='disabled')
                        OK_extract_button.config(state='disabled')
                    else:
                        add_file_button.config(state='normal')
                        add_extract_options.config(state='normal')
                        OK_extract_button.config(state='normal')
                        comparator_menu.configure(state="normal")
                        where_entry.configure(state="normal")
                else:
                    select_csv_field_extract_menu.configure(state='normal')
                    add_file_button.config(state='disabled')
                    add_append_options.config(state='disabled')
                    add_file_button.config(state='disabled')
                    OK_append_button.config(state='disabled')

                merge_checkbox.config(state='disabled')
                concatenate_checkbox.config(state='disabled')
                append_checkbox.config(state='disabled')
                purge_row_checkbox.config(state='disabled')
            else:
                select_csv_field_extract_var.set('')
                select_csv_field_extract_menu.config(state='disabled')

                merge_checkbox.config(state='normal')
                concatenate_checkbox.config(state='normal')
                append_checkbox.config(state='normal')
                purge_row_checkbox.config(state='normal')

                comparator_menu.configure(state="disabled")
                where_entry.configure(state="disabled")
                and_or_menu.configure(state="disabled")
                add_append_options.config(state='disabled')
                OK_extract_button.config(state='disabled')

                where_entry_var.set("")
                comparator_var.set("")
                and_or_var.set("")

        elif operation == "purge":
            if checkButton == True:

                if select_csv_field_purge_var.get() != '':
                    select_csv_field_purge_menu.configure(state='disabled')
                    select_csv_field2_purge_menu.configure(state='disabled')

                else:
                    select_csv_field_purge_menu.configure(state='normal')
                    select_csv_field2_purge_menu.configure(state='normal')

                keep_most_recent_checkbox.config(state='normal')
                keep_most_fields_checkbox.config(state='normal')

                merge_checkbox.config(state='disabled')
                concatenate_checkbox.config(state='disabled')
                append_checkbox.config(state='disabled')
                extract_checkbox.config(state='disabled')

            else:
                select_csv_field_purge_var.set('')
                select_csv_field2_purge_var.set('')
                select_csv_field_purge_menu.config(state='disabled')
                select_csv_field2_purge_menu.configure(state='disabled')

                merge_checkbox.config(state='normal')
                concatenate_checkbox.config(state='normal')
                append_checkbox.config(state='normal')
                extract_checkbox.config(state='normal')

        # clear content of current variables when selecting a different main option
        if (operation_text_var.get() != '') and (operation_text_var.get() != str(operation).upper()):
            csv_file_field_list.clear()
            reset_csv_field_values()
            file_number_var.set(1)
            operation_text_var.set('')
            csv_file_field.configure(state='normal')
            csv_file_field.delete(0.1, tk.END)
            csv_file_field.configure(state='disabled')


    def mergeSelection(*args):
        activate_csv_fields_selection('merge', merge_var.get(), False, False)


    merge_var.trace('w', mergeSelection)
    select_csv_field_merge_var.trace('w', mergeSelection)


    def concatenateSelection(*args):
        activate_csv_fields_selection('concatenate', concatenate_var.get(), False, False)


    concatenate_var.trace('w', concatenateSelection)
    select_csv_field_concatenate_var.trace('w', concatenateSelection)
    character_separator_entry_var.trace('w', concatenateSelection)


    def appendSelection(*args):
        activate_csv_fields_selection('append', append_var.get(), False, False)


    append_var.trace('w', appendSelection)
    select_csv_field_append_var.trace('w', appendSelection)


    def extractSelection(*args):
        activate_csv_fields_selection('extract', extract_var.get(), False, False)


    extract_var.trace('w', extractSelection)
    select_csv_field_extract_var.trace('w', extractSelection)
    comparator_var.trace('w', extractSelection)
    where_entry_var.trace("w", extractSelection)


    def purgeSelection(*args):
        activate_csv_fields_selection('purge', purge_row_var.get(), False, False)


    purge_row_var.trace('w', purgeSelection)

    TIPS_lookup = {'No TIPS available': ''}
    TIPS_options = 'No TIPS available'


    # add all the lines lines to the end to every special GUI
    # change the last item (message displayed) of each line of the function help_buttons
    # any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
    def help_buttons(window, help_button_x_coordinate, basic_y_coordinate, y_step):
        resetAll = "\n\nPress the RESET ALL button to clear all values, including csv files and fields, and start fresh."
        plusButton = "\n\nPress the + buttons, when available, to add either a new field from the same csv file (the + button at the end of this line) or a new csv file (the + button next to File at the top of this GUI). Multiple csv files can be used with any of the operations."
        OKButton = "\n\nPress the OK button, when available, to accept the selections made, then press the RUN button to process the query."

        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help", GUI_IO_util.msg_csvFile)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step, "Help",
                                      GUI_IO_util.msg_outputDirectory)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 2, "Help",
                                      "The label groups together the next two widgets that display the currently selected csv filename and fields.")
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 3, "Help",
                                      "Press the + button to add a new csv file.\n\nThe currently selected csv file is displayed in the next(read-only) widget.")
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 4, "Help",
                                      "Press the RESET CSV FIELD(S) button to clear all selected csv fields and start fresh.\n\nThe currently selected csv fields are displayed in the second (read-only) widget.")
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 5, "Help",
                                      resetAll + "\n\nThe next two (read-only) widgets display the arguments that will be processed when pressing the RUN button for the selected operation.\n\nThe first (read-only) widget displays the currently selected type of operation.\n\nThe second (read-only) widget displays a list of items:\n   csv filename\n   csv column/field.\n   For the Concatenate option the character separator will also be displayed.\n   For the Extract option, the comparator value (e.g., =, >), the WHERE value, and the selected add/or option will be displayed.")
        # empty line to account for the height of the text widget
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 7, "Help",
                                      "The MERGE option allows you to select several files, merge them together in a single file using the key of overlapping fields (the equivalent of an SQL JOIN operation), and save the output as a new file.\n\nAfter selecting the 'Merge files (Join)' option, press the + button either to add a new csv field or a new csv file (you can add repeatedly more fields and/or files)." + plusButton + OKButton + GUI_IO_util.msg_Esc + resetAll)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 8, "Help",
                                      "The CONCATENATE option allows you to select specific fields from one or more csv files, concatenate them together in a new field, and save the output as a new file.\n\nThe character(s) separator must be entered for every new csv field selected.\n\nTo select concatenate fields from different csv files, after selecting the first field and the character(s) separator, press the + button to add a new csv file and the RESET button to clear all values and start fresh." + plusButton + OKButton + GUI_IO_util.msg_Esc + resetAll)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 9, "Help",
                                      "The APPEND option allows you to select a specific field from a csv file and append its values at the bottom of the values of another field, and save the output as a new file." + plusButton + OKButton + GUI_IO_util.msg_Esc + resetAll)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 10, "Help",
                                      "The EXTRACT option allows you to select specific fields, even by specific values, from one or more csv files and save the output as a new file.\n\nStart by ticking the Extract checkbox, then selecting the csv field from the current csv file. To filter the field by specific values, select the comparator character to be used (e.g., =), enter the desired value, and select and/or if you want to add another filter.\n\nOptions become available in succession.\n\nPress the + button to register your choices (these will be displayed in command line in the form: filename and path, field, comparator, WHERE value, and/or selection; empty values will be recorded as ''. ). PRESSING THE + BUTTON TWICE WITH NO NEW CHOICES WILL CLEAR THE CURRENT CHOICES. PRESS + AGAIN TO RE-INSERT THE CHOICES. WATCH THIS IN COMMAND LINE.\n\nIF YOU DO NOT WISH TO FILTER FIELDS, PRESS THE + BUTTON AFTER SELECTING THE FIELD." + plusButton + OKButton + GUI_IO_util.msg_Esc + resetAll)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 11, "Help",
                                      "The PURGE DUPLICATE ROWS option allows you to delete duplicate records in a csv file.\n\n" + GUI_IO_util.msg_Esc)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 12, "Help",
                                      GUI_IO_util.msg_openOutputFiles)


    help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), GUI_IO_util.get_basic_y_coordinate(),
                 GUI_IO_util.get_y_step())

    # change the value of the readMe_message
    readMe_message = "The Python 3 scripts provide several ways of handling data from csv files.\n\nIn INPUT, the script takes one or more csv files depending upon the selected operation.\n\nIn OUTPUT, the script creates a new csv file.\n\nThe following operation are possible.\n\n   1. MERGE different csv files using one overalpping common field as a way to JOIN the files together, with the option of selecting only certain fields for the output file;\n   2. CONCATENATE into a single field the values of different fields from one or more csv files;\n   3. APPEND the content of different fields from one or more csv files after the content of the target field;\n   4. EXTRACT fields from one or more csv files, perhaps by specific field values (the equivalent of an SQL WHERE clause)."
    readMe_command = lambda: GUI_IO_util.readme_button(window, GUI_IO_util.get_help_button_x_coordinate(),
                                                       GUI_IO_util.get_basic_y_coordinate(), "Help", readMe_message)
    GUI_util.GUI_bottom(config_input_output_options, y_multiplier_integer, readMe_command, TIPS_lookup, TIPS_options)

    GUI_util.window.mainloop()
