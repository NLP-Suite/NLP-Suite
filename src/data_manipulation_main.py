import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"data_manipulation_main.py", ['os', 'tkinter', 'pandas', 'functools'])==False:
    sys.exit(0)

import os
import tkinter as tk
from subprocess import call
import tkinter.messagebox as mb

import IO_files_util
import GUI_util
import GUI_IO_util
import IO_csv_util
import data_manipulation_util
import reminders_util

# RUN section ________________________________________________________________________________________________________

def run(inputFilename,
        selectedCsvFile,
        operation_results_text_list,
        operation,
        append_var, concatenate_var, drop_var, extract_var, merge_var,
        output_to_csv_var, openOutputFiles, outputDir):

    filesToOpen = []  # Store all files that are to be opened once finished

    # data_files = [file for file in data_manipulation_util.select_csv(filePath)]  # dataframes
    # headers = [s.split(',')[1] for s in operation_results_text_list]  # headers
    # data_cols = [file for file in data_manipulation_util.get_cols(data_files, headers)]  # selected cols

# APPEND https://www.geeksforgeeks.org/how-to-append-a-new-row-to-an-existing-csv-file/

    if (operation=='CONCATENATE') and n_concatenate_fields<2:
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
        outputFilename = data_manipulation_util.merge(outputDir, operation_results_text_list)
        if outputFilename != None:
            filesToOpen.append(outputFilename)

# drop ______________________________________________________________________________

    if drop_var:
        mb.showwarning(title='Warning',message='The option is not available yet.\n\nSorry!\n\nCheck back soon!')

    # EXTRACT ______________________________________________________________________________

    if extract_var:
        if output_to_csv_var:
            export_type = '.csv'
        else:
            export_type = '.txt'
        outputFilename = data_manipulation_util.export_csv_to_csv_txt(outputDir,operation_results_text_list,export_type)
        if outputFilename != None:
            filesToOpen.append(outputFilename)


    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)


# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated

if __name__ == '__main__':
    run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                     selectedCsvFile.get(),
                                     operation_results_text_list,
                                     operation_name_var.get(),
                                     append_var.get(), concatenate_var.get(),
                                     drop_var.get(), extract_var.get(), merge_var.get(),
                                     output_to_csv_var.get(),
                                     GUI_util.open_csv_output_checkbox.get(), GUI_util.output_dir_path.get()
                                     )

    GUI_util.run_button.configure(command=run_script_command)

    # GUI section ______________________________________________________________________________________________________________________________________________________

    IO_setup_display_brief=True
    GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                     GUI_width=GUI_IO_util.get_GUI_width(3),
                                                     GUI_height_brief=680,
                                                     # height at brief display
                                                     GUI_height_full=720,  # height at full display
                                                     y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                     y_multiplier_integer_add=1,
                                                     # to be added for full display
                                                     increment=1)  # to be added for full display

    GUI_label = 'Graphical User Interface (GUI) for csv Data Manipulation'
    head, scriptName = os.path.split(os.path.basename(__file__))
    config_filename = 'data-manager_config.csv'
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

    GUI_util.GUI_top(config_input_output_numeric_options, config_filename,IO_setup_display_brief,'data_manager_main.py',True)

    # GUI CHANGES cut/paste special GUI widgets from GUI_util
    operation_results_text_list = []
    merge_var = tk.IntVar()
    concatenate_var = tk.IntVar()
    character_separator_var = tk.StringVar()
    append_var = tk.IntVar()
    extract_var = tk.IntVar()
    output_to_csv_var = tk.IntVar()
    drop_var = tk.IntVar()

    selectedCsvFile_var = tk.StringVar()

    selected_csv_files_var = tk.StringVar()

    where_entry_var = tk.StringVar()
    and_or_var = tk.StringVar()

    comparator_var = tk.StringVar()

    selected_csv_fields_var = tk.StringVar()
    operation_name_var = tk.StringVar()
    csv_file_operations_var = tk.StringVar()
    select_csv_field_var = tk.StringVar()
    select_csv_field_concatenate_var = tk.StringVar()
    selectedCsvFile_var = tk.StringVar()
    select_csv_field_merge_var = tk.StringVar()

    add_field_var = tk.IntVar()
    add_merge_options_var = tk.IntVar()
    add_file_var = tk.IntVar()

    select_csv_file_lb = tk.Label(window, text='Select csv file')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   select_csv_file_lb, True)


    menu_values=[]
    menu_values = " "
    n_concatenate_fields=0

    # menu_values=inputFilename
    select_csv_file_menu = tk.OptionMenu(window, select_csv_field_var, *menu_values)
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate + 100, y_multiplier_integer,
                                                   select_csv_file_menu,
                                                   True, False, True, False, 90,
                                                   GUI_IO_util.labels_x_coordinate + 100,
                                                   "The APPEND and MERGE options require multiple csv files in input.\nUse the dropdown menu to select a specific file that you can then open for inspection.")

    selectedCsvFile = tk.Entry(window, width=GUI_IO_util.widget_width_long, textvariable=selectedCsvFile_var)
    selectedCsvFile.config(state='disabled')
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.setup_pop_up_text_widget, y_multiplier_integer,
                                                   selectedCsvFile,True)

    # setup a button to open Windows Explorer on the selected input directory
    openInputFile_button = tk.Button(window, width=3, text='',
                                     command=lambda: IO_files_util.openFile(window,
                                                                            selectedCsvFile_var.get()))
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu+GUI_IO_util.open_config_file_button_brief, y_multiplier_integer,
                                                   openInputFile_button,False, False, True, False, 90,
                                                   GUI_IO_util.close_button_x_coordinate, "Open displayed file")

# WHERE clause

    where_lb = tk.Label(window, text='WHERE clause')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   where_lb, True)

    where_entry = tk.Entry(window, width=30, textvariable=where_entry_var)
    where_entry.configure(state="disabled")
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate + 100, y_multiplier_integer,
                                                   where_entry, True)

    comp_menu_values=['<>', '=', '>', '>=', '<', '<=']
    ##
    # select_csv_field_extract_menu = tk.OptionMenu(window, select_csv_field_extract_var, *menu_values, command=lambda:activate_csv_fields_selection('extract', extract_var.get(), False, False))
    comparator_menu = tk.OptionMenu(window, comparator_var, *comp_menu_values) #, command=lambda:extractSelection()
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate + 340, y_multiplier_integer,
                                                   comparator_menu,True)


    and_or_lb = tk.Label(window, text='and/or')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate + 460, y_multiplier_integer,
                                                   and_or_lb, True)

    and_or_menu = tk.OptionMenu(window, and_or_var, 'and', 'or')
    and_or_menu.configure(state="disabled", width=3)
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate + 910, y_multiplier_integer,
                                                   and_or_menu, True)


    def activate_where_clause():
        where_entry.configure(state="normal")


    def build_extract_string(comingFrom_Plus, comingFrom_OK):
        errorFound = build_string_for_processing("extract", select_csv_field_extract_var.get(), comingFrom_Plus, comingFrom_OK)
        if not errorFound:
            ##
            activate_extract_fields(comingFrom_Plus, comingFrom_OK)

    ##
    add_extract_options_var = tk.IntVar()
    add_extract_options = tk.Button(window, text='+', width=2, height=1, state='disabled',
                                    command=lambda: activate_extract_options())
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 1000,
                                                   y_multiplier_integer,
                                                   add_extract_options,
                                                   True, False, False, False, 90,
                                                   GUI_IO_util.labels_x_coordinate + 760,
                                                   "Click the + button to add another WHERE option")

    OK_WHERE_extract_button = tk.Button(window, text='OK', width=3, height=1, state='disabled',
                                  command=lambda: build_extract_string(False, True))
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 1050,
                                                   y_multiplier_integer,
                                                   OK_WHERE_extract_button,
                                                   False, False, False, False, 90,
                                                   GUI_IO_util.open_reminders_x_coordinate,
                                                   "Click the 'OK' button to approve the selections made and display the selected option in the display widget")

    pressedPlus = False

    def activate_extract_options():
        global pressedPlus
        pressedPlus = True
        activate_extract_fields(True, False)
        pressedPlus = False

    def activate_extract_fields(comingFrom_Plus, comingFrom_OK):
        global pressedPlus
        merge_checkbox.config(state='disabled')
        if extract_var.get() == True:
            if select_csv_field_extract_var.get() != '':
                if comingFrom_Plus == True:
                    select_csv_field_extract_menu.configure(state='normal')
                    where_entry_var.set('')
                    and_or_var.set('')
                else:
                    try:
                        if pressedPlus==False:
                            select_csv_field_extract_menu.configure(state='disabled')
                    except:
                        pass
                    comparator_menu.configure(state="disabled")

                if select_csv_field_extract_var.get() != '':
                    comparator_menu.configure(state="normal")
                    add_extract_options.config(state='normal')
                    OK_WHERE_button.config(state='normal')
                else:
                    comparator_menu.configure(state="disabled")
                    add_extract_options.config(state='disabled')
                    OK_WHERE_button.config(state='disabled')
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
                    WHERE_button.config(state='disabled')
                else:
                    # add_file_button.config(state='normal')
                    add_extract_options.config(state='normal')
                    OK_WHERE_button.config(state='normal')
                    comparator_menu.configure(state="normal")
                    where_entry.configure(state="normal")
            else:
                select_csv_field_extract_menu.configure(state='normal')
                # add_file_button.config(state='disabled')
                comparator_menu.configure(state="disabled")

        else:
            # select_csv_field_extract_var.set('')
            select_csv_field_extract_menu.config(state='disabled')

            merge_checkbox.config(state='normal')
            comparator_menu.configure(state="disabled")
            where_entry.configure(state="disabled")
            and_or_menu.configure(state="disabled")
            OK_WHERE_button.config(state='disabled')

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


    # de-indent all commands

    # current_pair_file_field_var = tk.Label(text="Current matched pair of csv filename and fields",
    #                                        font="Helvetica 10 italic")
    # y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate +300, y_multiplier_integer,
    #                                                current_pair_file_field_var)

    avoidLoop = False
    error = False

    def clear(e):
        csv_file_operations_var.set('')
        reset_csv_field_values()
        merge_var.set(0)
        concatenate_var.set(0)
        append_var.set(0)
        extract_var.set(0)
        drop_var.set(0)
        select_csv_field_concatenate_var.set('')
        select_csv_field_drop_var.set('')
        select_csv_field_extract_var.set('')
        select_csv_field_merge_var.set('')
        character_separator_entry_var.set('')
        comparator_var.set('')
        where_entry_var.set('')
        and_or_var.set('')
        GUI_util.clear("Escape")

    window.bind("<Escape>", clear)


    def reset_all_values():
        clear("<Escape>")
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
    # file_lb = tk.Label(window, text='File ')
    # y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer, file_lb,
    #                                                True)
    # file_number = tk.Entry(window, width=3, textvariable=file_number_var)
    # file_number.config(state="disabled")
    # y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate + 50, y_multiplier_integer,
    #                                                file_number, True)
    #
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

    # reset_field_button = tk.Button(window, width=15, text='Reset csv field(s)', state='disabled',
    #                                command=lambda: reset_csv_field_values())
    # y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
    #                                                reset_field_button, True)

    # selected_csv_fields_var.set('')
    # selected_fields = tk.Entry(window, width=100, textvariable=selected_csv_fields_var)
    # selected_fields.configure(state="disabled")
    # y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+ 300, y_multiplier_integer,
    #                                                selected_fields)

    reset_all_button = tk.Button(window, width=15, text='Reset all', state='normal', command=lambda: reset_all_values())
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   reset_all_button, True)

    # a text widget is read only when disabled
    operation_results_text = tk.Text(window, width=100, height=3, state="disabled")
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer, operation_results_text)

    # operation is a string with values "merge", "concatenate", "append", "extract", "drop"
    # menu_choice is the menu value of the specific csv field selected  (e.g., select_csv_field_concatenate_var.get())
    # it returns a list to be passed to data_handling.py for processing

    # visualizeBuildString after clicking OK
    def build_string_for_processing(operation, csv_field_menu_choice, comingFrom_Plus, comingFrom_OK):
        # skip empty values and csv fields already selected
        if not append_var and not concatenate_var and not extract_var and not drop_var and not merge_var.set:
            return False # no error

        # if select_csv_field_merge_var.get() == '' and select_csv_field_concatenate_var.get() == '' and select_csv_field_append_var.get() == '' and select_csv_field_extract_var.get() == '':
        # # if select_csv_field_concatenate_var.get() == '' and select_csv_field_append_var.get() == '' and select_csv_field_extract_var.get() == '':
        #         return False  # no error

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
            if select_csv_field_concatenate_var.get() != '' and character_separator_entry.get() != '':
                buildString = buildString + "," + character_separator_entry.get()
            else:
                buildString = ''

        if operation == 'extract':
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

    y_multiplier_integer = y_multiplier_integer + 1

    # _____________________________________________________________________________

    # after clicking on the merge checkbox
    def merge_reminder1():
        reminders_util.checkReminder(scriptName,
                                     reminders_util.title_options_data_manager_merge,
                                     reminders_util.message_data_manager_merge1,
                                     True)
        activate_all_options()
        build_merge_string(False, False)
        # mergeSelection(False, False)

# APPEND --------------------------------------------------------------------------------------------

    append_var.set(0)
    append_checkbox = tk.Checkbutton(window, text='APPEND rows', variable=append_var, onvalue=1, offvalue=0, command=lambda: activate_all_options())
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   append_checkbox, True)

    # add another file
    add_append_file = tk.Button(window, text='+', width=2, height=1, state='disabled',
                         command=lambda: add_csvFile(window, 'Select INPUT csv file',
                                                                [("csv files", "*.csv")]))
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 1000,
                                                   y_multiplier_integer,
                                                   add_append_file, True, False, False, False, 90,
                                                   GUI_IO_util.labels_x_coordinate + 800,
                                                   "Click the + button to add another csv file")

    OK_append_button = tk.Button(window, text='OK', width=3, height=1, state='disabled',
                                 command=lambda: build_append_string(False, True))
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 1050,
                                                   y_multiplier_integer,
                                                   OK_append_button,
                                                   False, False, False, False, 90,
                                                   GUI_IO_util.open_reminders_x_coordinate,
                                                   "Click the 'OK' button to approve the selections made and display the selected option in the display widget")

    def build_append_string(comingFrom_Plus, comingFrom_OK):
        errorFound = build_string_for_processing("append", select_csv_field_append_var.get(), comingFrom_Plus, comingFrom_OK)
        if not errorFound:
            activate_csv_fields_selection('append', append_var.get(), comingFrom_Plus, comingFrom_OK)

# CONCATENATE -----------------------------------------------------------------------------------

    concatenate_var.set(0)
    concatenate_checkbox = tk.Checkbutton(window, text='CONCATENATE fields', variable=concatenate_var, onvalue=1, offvalue=0, command=lambda: activate_all_options())
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   concatenate_checkbox, True)

    select_csv_field_lb = tk.Label(window, text='Select field')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                                   select_csv_field_lb, True)

    select_csv_field_concatenate_menu = tk.OptionMenu(window, select_csv_field_concatenate_var, *menu_values)
    select_csv_field_concatenate_menu.configure(state='disabled')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 100, y_multiplier_integer,
                                                   select_csv_field_concatenate_menu, True)

    character_separator_lb = tk.Label(window, text='Character(s) separator')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                                   character_separator_lb, True)

    character_separator_entry_var = tk.StringVar()
    character_separator_entry = tk.Entry(window, width=5, textvariable=character_separator_entry_var)
    character_separator_entry.config(state='disabled')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+150, y_multiplier_integer,
                                                   character_separator_entry, True)

    # add another field
    add_concatenate_field = tk.Button(window, text='+', width=2, height=1, state='disabled', command=lambda: merge_reminder_plus())
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 950,
                                                   y_multiplier_integer,
                                                   add_concatenate_field,
                                                   True, False, False, False, 90,
                                                   GUI_IO_util.labels_x_coordinate + 760,
                                                   "Click the + button to add another csv field")


    OK_concatenate_button = tk.Button(window, text='OK', width=3, height=1, state='disabled',
                                      command=lambda: build_concatenate_string(False, True))
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 1050,
                                                   y_multiplier_integer,
                                                   OK_concatenate_button,
                                                   False, False, False, False, 90,
                                                   GUI_IO_util.open_reminders_x_coordinate,
                                                   "Click the 'OK' button to approve the selections made and display the selected option in the display widget")


    def build_concatenate_string(comingFrom_Plus, comingFrom_OK):
        errorFound = build_string_for_processing("concatenate", select_csv_field_concatenate_var.get(), comingFrom_Plus,
                                                 comingFrom_OK)
        if not errorFound:
            activate_csv_fields_selection('concatenate', concatenate_var.get(), comingFrom_Plus, comingFrom_OK)


# DROP rows/purge -----------------------------------------------------------------------------------------------

    drop_var.set(0)
    drop_checkbox = tk.Checkbutton(window, text='DROP rows', variable=drop_var, onvalue=1, offvalue=0, command=lambda: activate_all_options())
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   drop_checkbox, True)

    select_csv_field_lb = tk.Label(window, text='Select field')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                                   select_csv_field_lb, True)

    select_csv_field_drop_var = tk.StringVar()
    select_csv_field_drop_menu = tk.OptionMenu(window, select_csv_field_drop_var, *menu_values)
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 100, y_multiplier_integer,
                                                   select_csv_field_drop_menu,True)

    # 'WHERE clause'
    WHERE_drop_button = tk.Button(window, text='WHERE clause', command=lambda: activate_where_clause())
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.run_button_x_coordinate,
                                                   y_multiplier_integer,
                                                   WHERE_drop_button,
                                                   False, False, False, False, 90,
                                                   GUI_IO_util.open_setup_x_coordinate,
                                                   "Click the button to activate the WHERE clause on top of this GUI")

# EXTRACT fields --------------------------------------------------------------------------------------
    extract_var.set(0)
    extract_checkbox = tk.Checkbutton(window, text='EXTRACT field(s) from csv file', variable=extract_var, onvalue=1,
                                      offvalue=0,command=lambda:extractSelection(False))
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   extract_checkbox, True)

    select_csv_field_lb = tk.Label(window, text='Select field')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                                   select_csv_field_lb, True)

    ##
    select_csv_field_extract_var = tk.StringVar()
    select_csv_field_extract_menu = tk.OptionMenu(window, select_csv_field_extract_var, *menu_values) #, command=lambda:select_csv_field_extract_var.trace('w', extractSelection)
    select_csv_field_extract_menu.configure(state='disabled')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 100, y_multiplier_integer,
                                                   select_csv_field_extract_menu, True)

    select_csv_field_extract_var.trace('w', lambda x, y, z: extractSelection(False))

    def change_label():
        if output_to_csv_var.get() == False:
            output_to_csv_checkbox.configure(text='txt output')
        else:
            output_to_csv_checkbox.configure(text='csv output')
    output_to_csv_var.set(1)
    output_to_csv_checkbox = tk.Checkbutton(window, text='csv output', variable=output_to_csv_var, onvalue=1,
                                      offvalue=0,command=lambda:change_label())
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_setup_x_coordinate,
                                                   y_multiplier_integer,
                                                   output_to_csv_checkbox,
                                                   True, False, False, False, 90,
                                                   GUI_IO_util.open_setup_x_coordinate,
                                                   "Tick the checkbox to export output to csv file or txt file")


    # 'WHERE clause'
    WHERE_extract_button = tk.Button(window, text='WHERE clause', command=lambda: activate_where_clause())
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.run_button_x_coordinate,
                                                   y_multiplier_integer,
                                                   WHERE_extract_button,
                                                   False, False, False, False, 90,
                                                   GUI_IO_util.open_setup_x_coordinate,
                                                   "Click the button to activate the WHERE clause on top of this GUI")

    def build_extract_string(comingFrom_Plus, comingFrom_OK):
        errorFound = build_string_for_processing("extract", select_csv_field_extract_var.get(), comingFrom_Plus, comingFrom_OK)
        if not errorFound:
            ##
            activate_extract_fields(comingFrom_Plus, comingFrom_OK)

# MERGE -----------------------------------------------------------------------------------

    merge_var.set(0)
    merge_checkbox = tk.Checkbutton(window, text='MERGE files (Join)', variable=merge_var, onvalue=1, offvalue=0, command=lambda: merge_reminder1())
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   merge_checkbox, True)

    select_csv_field_lb = tk.Label(window, text='Select field')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                                   select_csv_field_lb, True)

    select_csv_field_merge_menu = tk.OptionMenu(window, select_csv_field_merge_var, *menu_values)
    select_csv_field_merge_menu.configure(state='disabled')
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 100, y_multiplier_integer,
                                                   select_csv_field_merge_menu, True)

    add_merge_field = tk.Button(window, text='+', width=2, height=1, state='disabled', command=lambda: merge_reminder_plus())
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 950,
                                                   y_multiplier_integer,
                                                   add_merge_field,
                                                   True, False, False, False, 90,
                                                   GUI_IO_util.labels_x_coordinate + 760,
                                                   "Click the + button to add another csv field")

    # add another file
    add_merge_file = tk.Button(window, text='+', width=2, height=1, state='disabled',
                         command=lambda: add_csvFile(window, 'Select INPUT csv file',
                                                                [("csv files", "*.csv")]))
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 1000,
                                                   y_multiplier_integer,
                                                   add_merge_file, True, False, False, False, 90,
                                                   GUI_IO_util.labels_x_coordinate + 800,
                                                   "Click the + button to add another csv file")

    OK_merge_button = tk.Button(window, text='OK', width=3, height=1, state='disabled',
                                command=lambda: merge_reminder_OK())
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate + 1050,
                                                   y_multiplier_integer,
                                                   OK_merge_button,
                                                   False, False, False, False, 90,
                                                   GUI_IO_util.open_reminders_x_coordinate,
                                                   "Click the 'OK' button to approve the selections made and display the selected option in the display widget")

    # after selecting a csv field
    def merge_reminder2(*args):
        if not merge_var.get():
            return
        if select_csv_field_merge_var.get()!='':
            reminders_util.checkReminder(scriptName,
                                         reminders_util.title_options_data_manager_merge,
                                         reminders_util.message_data_manager_merge2,
                                         True)
        build_merge_string(False, False)
        mergeSelection(False, False)

    select_csv_field_merge_var.trace('w',merge_reminder2)

    def build_merge_string(comingFrom_Plus, comingFrom_OK):
        if not merge_var.get():
            return
        errorFound = build_string_for_processing("merge", select_csv_field_merge_var.get(), comingFrom_Plus, comingFrom_OK)
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
        # activate_csv_fields_selection('merge', merge_var.get(), True, False)

    def add_csvFile(window, title, fileType):
        global y_multiplier_integer
        import os
        initialFolder = os.path.dirname(os.path.abspath(__file__))
        filePath = tk.filedialog.askopenfilename(title=title, initialdir=initialFolder, filetypes=fileType)
        if len(filePath) > 0:
            select_csv_field_merge_var.set('')
            selected_csv_fields_var.set('')

            selectedCsvFile_var.set(filePath)
            # file_number_var.set(file_number_var.get() + 1)
            #
            # changed_filename(selectedCsvFile_var.get())

            reminders_util.checkReminder(scriptName,
                                         reminders_util.title_options_data_manager_merge,
                                         reminders_util.message_data_manager_merge5,
                                         True)

    #
    def changed_filename(tracedInputFile):
        global error
        if tracedInputFile[-4:] != '.csv':
            mb.showerror(title='Input file error',
                         message="The Data manipulation functions expect in input a csv file.\n\nPlease, select a csv file for your Default orGUI-specific I/O configuration and try again.\n\nThe RUN button is disabled until the required Input/Output option is entered.")
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
        m1 = select_csv_field_concatenate_menu["menu"]
        m1.delete(0, "end")
        m2 = select_csv_field_drop_menu["menu"]
        m2.delete(0, "end")
        m3 = select_csv_field_extract_menu["menu"]
        m3.delete(0, "end")
        m4 = select_csv_field_merge_menu["menu"]
        m4.delete(0, "end")
        # m6 = select_csv_field2_drop_menu["menu"]
        # m6.delete(0, "end")

        for s in menu_values:
            # m3.add_command(label=s, command=lambda value=s: select_csv_field_append_var.set(value))
            # concatenate
            m1.add_command(label=s, command=lambda value=s: select_csv_field_concatenate_var.set(value))
            # drop
            m2.add_command(label=s, command=lambda value=s: select_csv_field_drop_var.set(value))
            # extract
            m3.add_command(label=s, command=lambda value=s: select_csv_field_extract_var.set(value))
            # merge
            m4.add_command(label=s, command=lambda value=s: select_csv_field_merge_var.set(value))
            # m6.add_command(label=s, command=lambda value=s: select_csv_field2_drop_var.set(value))

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
        select_csv_field_extract_menu.configure(state='normal')
        comparator_menu.configure(state="disabled")
        if select_csv_field_extract_var.get() != '':
            if comingFrom_Plus == True:
                select_csv_field_extract_menu.configure(state='normal')
                where_entry_var.set('')
                and_or_var.set('')
            else:
                try:
                    if pressedPlus == False:
                        select_csv_field_extract_menu.configure(state='disabled')
                except:
                    pass
                comparator_menu.configure(state="disabled")

            if select_csv_field_extract_var.get() != '':
                comparator_menu.configure(state="normal")
                add_extract_options.config(state='normal')
                WHERE_extract_button.config(state='normal')
            else:
                comparator_menu.configure(state="disabled")
                add_extract_options.config(state='disabled')
                WHERE_extract_button.config(state='disabled')
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
                WHERE_extract_button.config(state='disabled')
            else:
                # add_file_button.config(state='normal')
                add_extract_options.config(state='normal')
                WHERE_extract_button.config(state='normal')
                comparator_menu.configure(state="normal")
                where_entry.configure(state="normal")

    def activate_all_options(*args):
        global comingFrom_Plus, comingFrom_OK, n_concatenate_fields
        select_csv_field_concatenate_menu.config(state='disabled')
        select_csv_field_drop_menu.config(state='disabled')
        select_csv_field_extract_menu.config(state='disabled')
        output_to_csv_checkbox.config(state='disabled')
        select_csv_field_merge_menu.config(state='disabled')
        WHERE_drop_button.configure(state='disabled')
        WHERE_extract_button.configure(state='disabled')

        if error:
            append_checkbox.configure(state='disabled')
            concatenate_checkbox.configure(state='disabled')
            extract_checkbox.configure(state='disabled')
            merge_checkbox.configure(state='disabled')
            drop_checkbox.configure(state='disabled')
            return

        # select_csv_field2_drop_menu.config(state='disabled')

        append_checkbox.configure(state='normal')
        concatenate_checkbox.configure(state='normal')
        extract_checkbox.configure(state='normal')
        merge_checkbox.configure(state='normal')
        drop_checkbox.configure(state='normal')

        if append_var.get():
            concatenate_checkbox.configure(state='disabled')
            extract_checkbox.configure(state='disabled')
            merge_checkbox.configure(state='disabled')
            drop_checkbox.configure(state='disabled')

            add_append_file.configure(state='normal')
            OK_append_button.configure(state='normal')

        elif concatenate_var.get():
            append_checkbox.configure(state='disabled')
            extract_checkbox.configure(state='disabled')
            merge_checkbox.configure(state='disabled')
            drop_checkbox.configure(state='disabled')

            select_csv_field_concatenate_menu.config(state='normal')
            if select_csv_field_concatenate_var.get()!='':
                character_separator_entry.config(state='normal')
                if character_separator_entry_var.get()!='':
                    add_concatenate_field.config(state='normal')
                    n_concatenate_fields=n_concatenate_fields+1
                    print(selected_csv_fields_var.get().count(','))
                    OK_concatenate_button.config(state='normal')

        elif drop_var.get():
            append_checkbox.configure(state='disabled')
            concatenate_checkbox.configure(state='disabled')
            extract_checkbox.configure(state='disabled')
            merge_checkbox.configure(state='disabled')
            select_csv_field_drop_menu.config(state='normal')

            if select_csv_field_drop_var.get()!='':
                WHERE_drop_button.configure(state='normal')

        elif extract_var.get():
            append_checkbox.configure(state='disabled')
            concatenate_checkbox.configure(state='disabled')
            merge_checkbox.configure(state='disabled')
            drop_checkbox.configure(state='disabled')

            if select_csv_field_extract_var.get()!='':
                output_to_csv_checkbox.configure(state='normal')
                WHERE_extract_button.configure(state='normal')

        elif merge_var.get():
            append_checkbox.configure(state='disabled')
            concatenate_checkbox.configure(state='disabled')
            extract_checkbox.configure(state='disabled')
            drop_checkbox.configure(state='disabled')

            if select_csv_field_merge_var.get()!='':
                add_merge_field.configure(state='normal')
                add_merge_file.configure(state='normal')
                OK_merge_button.configure(state='normal')

    select_csv_field_concatenate_var.trace("w", activate_all_options)
    select_csv_field_drop_var.trace("w", activate_all_options)
    select_csv_field_extract_var.trace("w", activate_all_options)
    select_csv_field_merge_var.trace("w", activate_all_options)
    character_separator_entry_var.trace("w", activate_all_options)

    ##
    def activate_csv_fields_selection(operation, checkButton, comingFrom_Plus, comingFrom_OK):
        # checkButton whether the specific operation has been selected
        if checkButton == False:
            merge_checkbox.config(state='normal')
        else:
            reset_all_button.config(state='normal')

        # if operation == "append":
        if append_var.get():
            if checkButton == True:
                merge_checkbox.config(state='disabled')
                concatenate_checkbox.config(state='disabled')
                extract_checkbox.config(state='disabled')
                drop_checkbox.config(state='disabled')

            else:
                OK_append_button.config(state='disabled')
                merge_checkbox.config(state='normal')
                concatenate_checkbox.config(state='normal')
                extract_checkbox.config(state='normal')
                drop_checkbox.config(state='normal')
        elif concatenate_var.get():
            if checkButton == True:

                merge_checkbox.config(state='disabled')
                extract_checkbox.config(state='disabled')

                if select_csv_field_concatenate_var.get() != '':
                    select_csv_field_concatenate_menu.config(state='disabled')
                    character_separator_entry.config(state='normal')
                if character_separator_entry_var.get() != '':
                    # add_file_button.config(state='normal')
                    OK_concatenate_button.config(state='normal')

                    if comingFrom_Plus == True:
                        select_csv_field_concatenate_menu.configure(state='normal')
                        character_separator_entry.config(state='disabled')
                    if comingFrom_OK == True:
                        # add_file_button.config(state='normal')
                        select_csv_field_concatenate_menu.configure(state='disabled')
                        # character_separator_entry_var.set('')
                        character_separator_entry.config(state='disabled')
                        # add_file_button.config(state='disabled')
                        OK_concatenate_button.config(state='disabled')
            else:
                select_csv_field_concatenate_var.set("")
                select_csv_field_concatenate_menu.config(state='disabled')
                character_separator_entry.config(state='disabled')
                character_separator_entry_var.set('')
                OK_concatenate_button.config(state='disabled')

                merge_checkbox.config(state='normal')
                append_checkbox.config(state='normal')
                extract_checkbox.config(state='normal')
                drop_checkbox.config(state='normal')
        elif drop_var.get():
            WHERE_drop_button.configure(state='disabled')
            if select_csv_field_drop_var.get() != '':
                WHERE_drop_button.configure(state='normal')
            if checkButton == True:

                if select_csv_field_drop_var.get() != '':
                    select_csv_field_drop_menu.configure(state='disabled')
                    # select_csv_field2_drop_menu.configure(state='disabled')

                else:
                    select_csv_field_drop_menu.configure(state='normal')
                    # select_csv_field2_drop_menu.configure(state='normal')

                merge_checkbox.config(state='disabled')
                concatenate_checkbox.config(state='disabled')
                append_checkbox.config(state='disabled')
                extract_checkbox.config(state='disabled')

            else:
                select_csv_field_drop_var.set('')
                # select_csv_field2_drop_var.set('')
                select_csv_field_drop_menu.config(state='disabled')
                # select_csv_field2_drop_menu.configure(state='disabled')

                merge_checkbox.config(state='normal')
                concatenate_checkbox.config(state='normal')
                append_checkbox.config(state='normal')
                extract_checkbox.config(state='normal')
        elif extract_var.get():
            WHERE_extract_button.configure(state='disabled')
            if select_csv_field_drop_var.get() != '':
                WHERE_extract_button.configure(state='normal')
            extract_checkbox.config(state='disabled')
        elif merge_var.get():
            if checkButton == True:
                select_csv_field_merge_menu.config(state='normal')
                extract_checkbox.config(state='disabled')
                if select_csv_field_merge_var.get() != '':
                    select_csv_field_merge_menu.config(state='disabled')
                    # you cannot add another field from the same file in merge;
                    # should always be disabled, but having it enabled allows to display a warning
                    # add_file_button.config(state='normal')
                    OK_merge_button.config(state='normal')
                    if comingFrom_Plus == True:
                        select_csv_field_merge_menu.configure(state='normal')
                    if comingFrom_OK == True:
                        select_csv_field_merge_menu.configure(state='disabled')
                        OK_merge_button.config(state='disabled')
                else:
                    # you cannot add another field from the same file in merge
                    OK_merge_button.config(state='disabled')

            else:
                select_csv_field_merge_var.set("")
                select_csv_field_merge_menu.config(state='disabled')
                OK_merge_button.config(state='disabled')
                extract_checkbox.config(state='normal')

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

    # def mergeSelection(*args):
    #     activate_csv_fields_selection('merge', merge_var.get(), False, False)


    # select_csv_field_merge_var.trace('w', mergeSelection)


    def concatenateSelection(*args):
        activate_csv_fields_selection('concatenate', concatenate_var.get(), False, False)


    # def purgeSelection(*args):
    #     activate_csv_fields_selection('drop', drop_var.get(), False, False)
    # drop_var.trace('w', purgeSelection)

    SQL_GUI_button = tk.Button(window,
                                            text='Manipulate csv data with SQL (Open GUI)',
                                            width=GUI_IO_util.widget_width_medium,
                                            command=lambda: call("python DB_SQL_main.py", shell=True))
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   SQL_GUI_button,
                                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                                   "Click the button to open the GUI to manipulate csv data via SQL")

    visualize_csv_data_GUI_button = tk.Button(window,
                                            text='Visualize csv data (Open GUI)',
                                            width=GUI_IO_util.widget_width_medium,
                                            command=lambda: call("python data_visualization_main.py", shell=True))
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                                   visualize_csv_data_GUI_button,
                                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                                   "Click the button to open the GUI to visualize csv data with various Python Plotly options")

    videos_lookup = {'No videos available': ''}
    videos_options = 'No videos available'

    TIPS_lookup = {'No TIPS available': ''}
    TIPS_options = 'No TIPS available'


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
        plusButton = "\n\nPress the + buttons, when available, to add either a new field from the same csv file (the + button at the end of this line) or a new csv file (the + button next to File at the top of this GUI). Multiple csv files can be used with any of the operations."
        OKButton = "\n\nPress the OK button, when available, to accept the selections made, then press the RUN button to process the query."
        if not IO_setup_display_brief:
            y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_csvFile)
            y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                          GUI_IO_util.msg_outputDirectory)
        else:
            y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                          GUI_IO_util.msg_IO_setup)

        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Select and display the csv file in your file list. Click the Open button to open the selected csv file.")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "When widgets are active, enter the values of the WHERE clause.\n\nThe options are available for the DROP and EXTRACT options only.")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      resetAll + "\n\nThe read-only widget after the 'RESET all' button displays the arguments that will be processed when pressing the RUN button for the selected operation:\n\n   csv filename\n   csv column/field.\n   For the Concatenate option the character separator will also be displayed.\n   For the Drop and Extract options, the comparator value (e.g., =, >), the WHERE value, and the selected add/or option will be displayed.")
        # empty line to account for the height of the text widget
        y_multiplier_integer = y_multiplier_integer + 1
        # APPEND
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "The APPEND option allows you to add multiple csv files for as long as they have the same number and type of fields.\n\nIn INPUT, the option takes at least 2 csv files.\n\nIn OUTPUT, the option creates a single csv file that combines all selected input files. "+resetAll)
        # CONCATENATE
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "The CONCATENATE option allows you to join together 2 or more fields of a csv file, separated by a user-selected sttring.\n\nIn INPUT, the option takes a single csv file.\n\nIn OUTPUT, the option creates a single csv file with all the original fields plus the concatenated fields. "+resetAll)
        # "The DROP and EXTRACT options allow you to select specific fields, even by specific values, from one or more csv files and save the output as a new file.\n\nStart by ticking the Extract checkbox, then selecting the csv field from the current csv file. To filter the field by specific values, select the comparator character to be used (e.g., =), enter the desired value in the \'WHERE\' widget (case sensitive!), and select and/or if you want to add another filter.\n\nOptions become available in succession.\n\nPress the + button to register your choices (these will be displayed in command line in the form: filename and path, field, comparator, WHERE value, and/or selection; empty values will be recorded as ''. ). PRESSING THE + BUTTON TWICE WITH NO NEW CHOICES WILL CLEAR THE CURRENT CHOICES. PRESS + AGAIN TO RE-INSERT THE CHOICES. WATCH THIS IN COMMAND LINE.\n\nIF YOU DO NOT WISH TO FILTER FIELDS, PRESS THE + BUTTON AFTER SELECTING THE FIELD." + plusButton + OKButton + GUI_IO_util.msg_Esc + resetAll)
        # DROP
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "The DROP option allows you to select several files, merge them together in a single file using the key of overlapping fields (the equivalent of an SQL JOIN operation), and save the output as a new file.\n\nAfter selecting the 'Merge files (Join)' option, press the + button either to add a new csv field or a new csv file (you can add repeatedly more fields and/or files).\n\nIn INPUT the MERGE option takes 2 or more csv files.\n\nIn OUTPUT, the MERGE option creates a csv file containing all the fields from all input files matched on the basis of the same selected overlapping field(s) (e.g., Document ID, Sentence ID)."+ GUI_IO_util.msg_Esc + resetAll)
        # EXTRACT
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "The EXTRACT option allows you to select specific fields, even by specific values, from a csv file and save the output as a new csv or txt file.\n\nYOU CAN SAVE THE OUTPUT TO CSV FILE OR TO A TEXT FILE. Just tick the Output csv checkbox as desired.\n\nStart by ticking the Extract checkbox, then selecting the csv field from the current csv file. To filter the field by specific values, select the comparator character to be used (e.g., =), enter the desired value, and select and/or if you want to add another filter.\n\nOptions become available in succession.\n\nPress the + button to register your choices (these will be displayed in command line in the form: filename and path, field, comparator, WHERE value, and/or selection; empty values will be recorded as ''. ). PRESSING THE + BUTTON TWICE WITH NO NEW CHOICES WILL CLEAR THE CURRENT CHOICES. PRESS + AGAIN TO RE-INSERT THE CHOICES. WATCH THIS IN COMMAND LINE.\n\nIF YOU DO NOT WISH TO FILTER FIELDS, PRESS THE + BUTTON AFTER SELECTING THE FIELD." + plusButton + OKButton + GUI_IO_util.msg_Esc + resetAll + "\n\nIn INPUT, the EXTRACT option takes 1 csv file.\n\nIn OUTPUT, the EXTRACT option creates either a csv or a text file containing only the fields selected for extraction from the input file."+ GUI_IO_util.msg_Esc + resetAll)
        # MERGE
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "The MERGE option allows you to select several files, merge them together in a single file using the key of overlapping fields (the equivalent of an SQL JOIN operation), and save the output as a new file.\n\nAfter selecting the 'Merge files (Join)' option, press the + button either to add a new csv field or a new csv file (you can add repeatedly more fields and/or files).\n\nIn INPUT the MERGE option takes 2 or more csv files.\n\nIn OUTPUT, the MERGE option creates a csv file containing all the fields from all input files matched on the basis of the same selected overlapping field(s) (e.g., Document ID, Sentence ID)."+ GUI_IO_util.msg_Esc + resetAll)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Click the button to open the GUI that will allow you to manipulate csv files using SQL.")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Click the button to open the GUI that will allow you to visualize data in a variety of ways.")
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                             "NLP Suite Help", GUI_IO_util.msg_openOutputFiles)
        return y_multiplier_integer -1

    y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

    # change the value of the readMe_message
    readMe_message = "The Python 3 scripts provide several ways of handling data from csv files.\n\nIn INPUT, the script takes one or more csv files depending upon the selected operation.\n\nIn OUTPUT, the script creates a new csv file.\n\nThe following operation are possible.\n\n   1. MERGE different csv files using one or more overlapping common field(s) as a way to JOIN the files together;\n   2. CONCATENATE into a single field the values of different fields from one csv file;\n   3. APPEND the content of different fields from one csv file after the content of a selected target field;\n   4. EXTRACT fields from one csv file, perhaps by specific field values (the equivalent of an SQL WHERE clause);\n   4. DROP dulicate rows from one csv file."
    readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
    GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief,scriptName,True)

    mb.showwarning(title='Warning',
                   message="The csv Data manipulation GUI is currently under redesign. It is not usable.\n\nSorry!\n\nCheck back soon.")

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

    state = str(GUI_util.run_button['state'])
    if state == 'disabled':
        error = True
        # check to see if there is a GUI-specific config file, i.e., a CoNLL table file, and set it to the setup_IO_menu_var
        if os.path.isfile(os.path.join(GUI_IO_util.configPath, config_filename)):
            GUI_util.setup_IO_menu_var.set('GUI-specific I/O configuration')
            mb.showwarning(title='Warning',
                           message="Since a GUI-specific " + config_filename + " file is available, the I/O configuration has been automatically set to GUI-specific I/O configuration.")
            error = False

    activate_all_options()

    GUI_util.window.mainloop()
