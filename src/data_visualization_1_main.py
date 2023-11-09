# written by Roberto Franzosi November 2019
# rewritten by Roberto January 2023

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"data_visualization__main.py",['os','tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_csv_util
import IO_files_util
import charts_util

def runGephi(inputFilename, outputDir, csv_file_relational_field_list, dynamic_network_field_var):
    import Gephi_util

    fileBase = os.path.basename(inputFilename)[0:-4]
    # csv_file_relational_field_list contains the column header of node1, edge, node2 (e.g., SVO), and, possibly, the field for dynamic network
    return Gephi_util.create_gexf(GUI_util.window, fileBase, outputDir, inputFilename,
                                  csv_file_relational_field_list[0], csv_file_relational_field_list[1],
                                  csv_file_relational_field_list[2], dynamic_network_field_var, 'abnormal')


def run(inputFilename, inputDir, outputDir, openOutputFiles,
        relations_var,
        relations_menu_var,
        csv_field_relational_var,
        csv_file_relational_field_list,
        dynamic_network_field_var,
        Sankey_limit1_var, Sankey_limit2_var, Sankey_limit3_var,
        categorical_var,
        csv_file_categorical_field_list,
        filter_options_var,
        fixed_param_var,
        rate_param_var,
        base_param_var,
        max_rows_var,
        color_1_style_var,
        color_2_style_var,
        normalize_var,
        # K_sent_begin_var,
        # K_sent_end_var,
        # split_var,
        # do_not_split_var,
        use_numerical_variable_var,
        csv_field_treemap_var):


    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    else:
        config_filename = scriptName.replace('main.py', 'config.csv')

    filesToOpen = []
    # int_K_sent_begin_var=None
    # int_K_sent_end_var=None

    if relations_var==False and categorical_var == False:
        mb.showwarning("Warning",
                       "No options have been selected.\n\nPlease, select an option to run and try again.")
        return
    else:
        # check if input file is csv
        if inputDir!='' or os.path.basename(inputFilename)[-4:] != ".csv":
            mb.showwarning("Warning",
                           "The visualization options requires in input a csv file.\n\nPlease, select a csv file and try again.")
            return

    if relations_var:
        output_label=relations_menu_var
    elif categorical_var:
        output_label = categorical_menu_var.get()
    else:
        output_label = ''

    outputFiles = ''
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                             '.html', output_label)

# Visualize relations: Gephi, Sankey  --------------------------------------------------------------------------------

    if relations_var:
        if relations_menu_var == '':
            mb.showwarning("Warning",
                           "Please, use the dropdown menu to select one of the options for for visualizing relations: Gephi, Sankey and try again.")
            return

# Gephi  --------------------------------------------------------------------------------

        if relations_menu_var=='Gephi':
            if len(csv_file_relational_field_list)!=3:
                mb.showwarning("Warning",
                               "You must select three csv fields to be used in the computation of the network graph, in the order of node, edge, node (e.g., Subject, Verb, Object).\n\nIf you wish to create a dynamic network graph you can select a fourth field to be used as the dynamic index (e.g., Sentence ID or Date).")
                return
            outputFiles = runGephi(inputFilename, outputDir, csv_file_relational_field_list, dynamic_network_field_var)

            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

# Sankey  --------------------------------------------------------------------------------

        if relations_menu_var=='Sankey':
            if len(csv_file_relational_field_list)!=2 and len(csv_file_relational_field_list)!=3:
                mb.showwarning("Warning",
                               "You must select 2 or 3 csv fields to be used in the computation of a Sankey chart (e.g., Subject, Verb, Object or Subject, Object).\n\nMAKE SURE TO CLICK ON THE + BUTTON AFTER THE LAST SELECTION. CLICK ON THE SHOW BUTTON TO SEE THE CURRENT SELECTION.")
                return
            if len(csv_file_relational_field_list)==3:
                three_way_Sankey=True
                var3=csv_file_relational_field_list[2]
                # Sankey_limit3_var
            else:
                three_way_Sankey = False
                var3=None
                Sankey_limit3_var=None
            outputFiles = charts_util.Sankey(inputFilename, outputFilename,
                                csv_file_relational_field_list[0], Sankey_limit1_var, csv_file_relational_field_list[1],
                                             Sankey_limit2_var, three_way_Sankey, var3, Sankey_limit3_var)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)


# Categorical data (sunburst or treemap) --------------------------------------------------------------------------------

    if categorical_var:
        if len(csv_file_categorical_field_list)<2:
            mb.showwarning("Warning",
                           "You must have at least 2 sets of csv file field and search values to produce meaningful " + categorical_menu_var.get() + " charts.\n\nPlease, select another combination of csv file field and search values and try again.")
            return

        if categorical_menu_var.get() == '':
            mb.showwarning("Warning",
                           "Please, use the dropdown menu to select one of the options for categorical data: Sunburst, treemap and try again.")
            return
        if csv_field_categorical_var == '':
            mb.showwarning("Warning",
                           "The categorical data visualization functions require a set of comma-separated entries to be used in the search (could be parts of a filenames, if the Document field is selected).\n\nPlease, enter value(s) and try again.")
            return

        # interest pass a list [] of labels embedded in the filename, e.g. Book1, Book2, ... or Chinese, Arabian,...
        interest = []
        # temp_interest=[]
        # interest = search_values_categorical_var.split(',')
        # for i in range(len(interest)):
        #     temp_interest.append(interest[i].lstrip())
        # label is a string that has the header field in the csv file to be used for display
        label=csv_field_categorical_var


# Sunburst & Treemap

        if 'Sunburst' in categorical_menu_var.get() or 'Treemap' in categorical_menu_var.get():
            if csv_field_categorical_var.get()!='' and not csv_field_categorical_var.get() in str(csv_file_categorical_field_list):
                result = mb.askyesno(title="Warning",message="There is a search value '" + str(csv_field_categorical_var.get()) + "' that has not been added (using the + button) to the csv file fields to be processed.\n\nAre you sure you want to continue?")
                if result == False: # No
                    return

        # Categorical data: colormap  --------------------------------------------------------------------------------

        if 'Colormap' in categorical_menu_var.get():
            if csv_field_categorical_var == '':
                mb.showwarning("Warning",
                               "The colormap algorithm requires a value for 'csv file field.'\n\nPlease, select a value and try again.")
                return
            params = [max_rows_var, color_1_style_var, color_2_style_var, normalize_var]
            outputFiles = charts_util.main_colormap(inputFilename, outputDir, csv_file_categorical_field_list, params)

            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

# Categorical data: Sunburst  --------------------------------------------------------------------------------

        if 'Sunburst' in categorical_menu_var.get():
            if csv_field_categorical_var=='':
                mb.showwarning("Warning",
                               "The sunburst algorithm requires a value for 'csv file field.'\n\nPlease, select a value and try again.")
                return

            outputFiles = charts_util.Sunburst_Treemap(inputFilename, outputFilename, outputDir, csv_file_categorical_field_list, 1,  fixed_param_var, rate_param_var, base_param_var, filter_options_var)

            #### USED
        #    outputFiles = charts_util.Sunburst(inputFilename, outputFilename, outputDir, case_sensitive_var, temp_interest, label,
        #                                    do_not_split_var, int_K_sent_begin_var, int_K_sent_end_var, split_var)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

# Categorical data: treemap --------------------------------------------------------------------------------

        if 'Treemap' in categorical_menu_var.get():
            if label=='':
                mb.showwarning("Warning",
                               "You have not entered a 'csv file field' required by the treemap algorithm.\n\nPlease, use the dropdown menu to select the csv file field containing categorical data and try again.")
                return
            if use_numerical_variable_var and csv_field_categorical_var=='':
                mb.showwarning("Warning",
                               "The selected treemap option with the use of numerical data requires a variable containing the numerical data.\n\nPlease, select the csv file field containing the numerical data and try again.")
                return
            #def Treemap(data,outputFilename,interest,var,extra_dimension_average,average_variable=None):

            outputFiles = charts_util.Sunburst_Treemap(inputFilename, outputFilename, outputDir,
                                                       csv_file_categorical_field_list, 0)
            # 0 - Treemap, 1 - Sunburst, lazy boolean for shortening the code in charts_util

            # outputFiles = charts_util.Treemap(inputFilename, outputFilename,
          #                                                         temp_interest, label, use_numerical_variable_var,csv_field_categorical_var)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    if openOutputFiles and len(filesToOpen) > 0:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            relations_var.get(),
                            relations_menu_var.get(),
                            csv_field_relational_var.get(),
                            csv_file_relational_field_list,
                            dynamic_network_field_var.get(),
                            Sankey_limit1_var.get(), Sankey_limit2_var.get(), Sankey_limit3_var.get(),
                            categorical_var.get(),
                            csv_file_categorical_field_list,
                            filter_options_var.get(),
                            fixed_param_var.get(),
                            rate_param_var.get(),
                            base_param_var.get(),
                            max_rows_var.get(),
                            color_1_style_var.get(),
                            color_2_style_var.get(),
                            normalize_var.get(),
                            # K_sent_begin_var.get(),
                            # K_sent_end_var.get(),
                            # split_var.get(),
                            # do_not_split_var.get(),
                            use_numerical_variable_var.get(),
                            csv_field_treemap_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=640, # height at brief display
                             GUI_height_full=720, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Visualization Tools'
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
window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

def clear(e):
    extra_GUIs_var.set(0)
    extra_GUIs_menu_var.set('')
    relations_menu_var.set('Gephi')
    categorical_menu_var.set('Sunburst')

    relations_var.set(0)
    categorical_var.set(0)

    selected_csv_file_fields.set('')
    
    relations_checkbox.configure(state='normal')
    categorical_checkbox.configure(state='normal')

    case_sensitive_var.set(1)
    # for now always set to disabled
    case_sensitive_checkbox.configure(state='disabled')
    csv_field_categorical_var.set('')
    csv_field_categorical_menu.configure(state='disabled')
    search_values_categorical_var.set('')
    # K_sent_begin_var.set('')
    # K_sent_end_var.set('')
    # K_sent_begin.configure(state='disabled')
    # K_sent_end.configure(state='disabled')
    # split_var.set(0)
    # split_checkbox.configure(state='disabled')
    # do_not_split_var.set(0)
    # do_not_split_checkbox.configure(state='disabled')
    csv_field_treemap_var.set('')

    reset_relational()
    reset_categorical()

    fixed_param_var.set(50)
    rate_param_var.set(3)
    base_param_var.set(40)
    activate_filtering_options()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

extra_GUIs_var = tk.IntVar()
extra_GUIs_menu_var = tk.StringVar()

# open_GUI_var = tk.StringVar()
relations_var = tk.IntVar()
relations_menu_var = tk.StringVar()
Gephi_var = tk.IntVar()
Sankey_var = tk.IntVar()
selected_csv_file_fields_var = tk.StringVar()

csv_field_relational_var = tk.StringVar()
dynamic_network_field_var = tk.StringVar()

csv_field_categorical_var = tk.StringVar()
categorical_var = tk.IntVar()
categorical_menu_var = tk.StringVar()
search_values_categorical_var = tk.StringVar()
case_sensitive_var = tk.IntVar()
csv_field_categorical_var = tk.StringVar()
search_values_categorical_var = tk.StringVar()
filter_options_var = tk.StringVar()
fixed_param_var = tk.StringVar()
rate_param_var = tk.StringVar()
base_param_var = tk.StringVar()

selected_csv_file_fields = tk.StringVar()

max_rows_var = tk.IntVar()
color_1_var = tk.IntVar()
color_2_var = tk.IntVar()
color_1_style_var = tk.StringVar()
color_2_style_var = tk.StringVar()

# K_sent_begin_var = tk.StringVar()
# K_sent_end_var = tk.StringVar()
# split_var = tk.IntVar()
# do_not_split_var = tk.IntVar()

use_numerical_variable_var = tk.IntVar()
csv_field_treemap_var = tk.StringVar()

csv_file_categorical_field_string = ''
csv_file_relational_field_list = []
csv_file_categorical_field_list = []
menu_values = []
color_1_style_var_list=[]
color_2_style_var_list=[]
color_1_var_list=[]
color_2_var_list=[]
error = False


# open_GUI_lb = tk.Label(window, text='Open special visualization options GUI')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
#                                                open_GUI_lb, True)
#
# open_GUI_menu = tk.OptionMenu(window, open_GUI_var, 'Excel charts (Open GUI)','Geographic maps: From texts to maps (Open GUI)',"Geographic maps: Google Earth Pro (Open GUI)", 'HTML annotator (Open GUI)','Wordclouds (Open GUI)')
# # open_GUI_menu.configure(state='disabled')
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
#                                    open_GUI_menu,
#                                    False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
#                                    "Open a GUI for special visualization options: Excel charts, geographic maps (from texts to maps), geographic maps (Google Earth Pro), HTML, wordclouds")

def open_GUI(*args):
    if 'Boxplot' in extra_GUIs_menu_var.get() or 'Time' in extra_GUIs_menu_var.get() or 'Multiple' in extra_GUIs_menu_var.get():
        call("python data_visualization_1_main.py", shell=True)
    if 'Excel' in extra_GUIs_menu_var.get():
        call("python charts_Excel_main.py", shell=True)
    elif 'texts to maps' in extra_GUIs_menu_var.get():
        call("python GIS_main.py", shell=True)
    elif 'Google Earth' in extra_GUIs_menu_var.get():
        call("python GIS_Google_Earth_main.py", shell=True)
    elif 'HTML' in extra_GUIs_menu_var.get():
        call("python html_annotator_main.py", shell = True)
    elif 'Wordclouds' in extra_GUIs_menu_var.get():
        call("python wordclouds_main.py", shell=True)
extra_GUIs_menu_var.trace('w',open_GUI)


extra_GUIs_var.set(0)
extra_GUIs_checkbox = tk.Checkbutton(window, text='GUIs available for more analyses ', variable=extra_GUIs_var, onvalue=1, offvalue=0, command=lambda: activate_all_options())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,extra_GUIs_checkbox,True)

extra_GUIs_menu_var.set('')
extra_GUIs_menu = tk.OptionMenu(window,extra_GUIs_menu_var,'Boxplot', 'Time mapper', 'Multiple bar charts', 'Excel', 'texts to maps', 'Google Earth', 'HTML', 'Wordclouds')
extra_GUIs_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   extra_GUIs_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select other related types of analysis you wish to perform")

relations_checkbox = tk.Checkbutton(window, text='Visualize relations', variable=relations_var,
                                    onvalue=1, command=lambda:activate_all_options(()))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   relations_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox if you wish to visualize relational data in interactive Gephi network graphs or Sankey charts")

relations_menu_var.set('Gephi')
relations_menu = tk.OptionMenu(window, relations_menu_var, 'Gephi','Sankey')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                   relations_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_filename_label_lb_pos,
                                   "Visualize relations (network graphs via Gephi or Sankey chart via Plotly)")

def get_csv_file_menu_vales():
    global menu_values
    if GUI_util.inputFilename.get() != '' and GUI_util.inputFilename.get()[-4:] == ".csv":
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
    return menu_values
get_csv_file_menu_vales()

csv_field_lb = tk.Label(window, text='csv file field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               csv_field_lb, True)

csv_field_relational_menu = tk.OptionMenu(window, csv_field_relational_var, *menu_values) # relational
csv_field_relational_menu.configure(state='disabled')
# place widget with hover-over info
# visualization_csv_field_menu_pos
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                   csv_field_relational_menu,
                                   True, False, True, False, 90, GUI_IO_util.visualization_filename_label_lb_pos,
                                   "Select the three fields to be used for the network graph in the order node1, edge, node2 (e.g., SVO)")

selected_csv_fields_area = tk.Entry(width=GUI_IO_util.widget_width_medium, state='disabled', textvariable=selected_csv_file_fields)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                               selected_csv_fields_area, True, False, True, False, 90,
                                               GUI_IO_util.open_reminders_x_coordinate, "The widget, always disabled, displays all the  selected csv file fields.")

def display_selected_csv_fields():
    if csv_field_relational_var.get() != '' and not csv_field_relational_var.get() in csv_file_relational_field_list:
        csv_file_relational_field_list.append(csv_field_relational_var.get())
        new_missing_software_string=', '.join(csv_file_relational_field_list)
        selected_csv_file_fields.set(new_missing_software_string.lstrip())
    else:
        mb.showwarning(title='Warning',
                       message='The option "' + csv_field_relational_var.get() + '" has already been selected. Selection ignored.\n\nYou can see your current selections by clicking the Show button.')
        csv_field_relational_menu.configure(state='normal')
    selected_csv_file_fields_var.set(str(csv_file_relational_field_list))
    activate_csv_fields_relational_selection(True)


def reset_relational():
    csv_file_relational_field_list.clear()
    csv_field_relational_var.set('')
    selected_csv_file_fields.set('')
    dynamic_network_field_var.set('')
    selected_csv_file_fields_var.set('')

add_button_relational_var = tk.IntVar()
add_button_relational = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1,
                                command=lambda: display_selected_csv_fields())
add_button_relational.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.close_button_x_coordinate+20, y_multiplier_integer,
                                   add_button_relational,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Click on the + button to add a selected csv field to the list of Gephy parameters (edge1, node, edge2)")

reset_button_relational = tk.Button(window, text='Reset ', width=GUI_IO_util.reset_button_width,height=1,state='disabled',command=lambda: reset_relational())
reset_button_relational.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.close_button_x_coordinate+55, y_multiplier_integer,
                                   reset_button_relational,
                                   False, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Click on the reset_relational button to clear the list of selected fields and start again")
def show_Gephi_options_list():
    if len(csv_file_relational_field_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected Gephi options.')
    else:
        mb.showwarning(title='Warning', message='The currently selected Gephi options are:\n\n  ' + '\n  '.join(csv_file_relational_field_list) + '\n\nPlease, press the Reset button (or ESCape) to start fresh.')

def activate_csv_fields_relational_selection(comingFromPlus=False):
    if csv_field_relational_var.get() != '':
        if comingFromPlus:
            csv_field_relational_menu.config(state='normal')
        else:
            csv_field_relational_menu.config(state='disabled')
        add_button_relational.config(state='normal')
        reset_button_relational.config(state='normal')
        # show_button.config(state='normal')
        if len(csv_file_relational_field_list) == 3:
            csv_field_relational_menu.configure(state='disabled')
            dynamic_network_field_menu.config(state='normal')
            if dynamic_network_field_var.get()=='':
                mb.showwarning(title='Warning', message='You have selected the maximum number of fields (3) to visualize relations.\n\nPress the "Show" button to display your selection. Press the "reset_relational" button to clear your selection and start again.')
    else:
        csv_field_relational_menu.config(state='normal')
        dynamic_network_field_menu.config(state='normal')
        reset_button_relational.config(state='disabled')
        # show_button.config(state='disabled')
csv_field_relational_var.trace('w', callback = lambda x,y,z: activate_csv_fields_relational_selection())
dynamic_network_field_var.trace('w', callback = lambda x,y,z: activate_csv_fields_relational_selection())

GUI_util.inputFilename.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))
# GUI_util.input_main_dir_path.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))

Gephi_lb = tk.Label(window, text='Gephi parameters', foreground="red",font=("Courier", 12, "bold"))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   Gephi_lb,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The widgets on this line refer to the Gephi option only")

csv_field_dynamic_network_lb = tk.Label(window, text='csv file field for dynamic graph')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                               csv_field_dynamic_network_lb, True)

dynamic_network_field_menu = tk.OptionMenu(window, dynamic_network_field_var, *menu_values)
dynamic_network_field_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu+200, y_multiplier_integer,
                                   dynamic_network_field_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Select the field to be used for a dynamic network graph (e.g., Sentence ID, Date) if you wish to compute a dynamic network graph.\nTHE OPTION IS CURRENTLY DISABLED.")

Sankey_lb = tk.Label(window, text='Sankey parameters',foreground="red",font=("Courier", 12, "bold"))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   Sankey_lb,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The widgets on this line refer to the Sankey option only")

Sankey_limit1_lb = tk.Label(window, text='Variable 1 max')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                               Sankey_limit1_lb, True)

Sankey_limit1_var = tk.IntVar()
Sankey_limit1_var.set(5)
Sankey_limit1_menu = tk.OptionMenu(window, Sankey_limit1_var, 5, 10)
Sankey_limit1_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_filename_label_pos, y_multiplier_integer,
                                   Sankey_limit1_menu,
                                   True, False, True, False, 90, GUI_IO_util.visualization_csv_field_dynamic_network_lb_pos,
                                   "Select the maximum number of categories for variable 1")

Sankey_limit2_lb = tk.Label(window, text='Variable 2 max')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                               Sankey_limit2_lb, True)

Sankey_limit2_var = tk.IntVar()
Sankey_limit2_var.set(10)
Sankey_limit2_menu = tk.OptionMenu(window, Sankey_limit2_var, 5, 10, 20)
Sankey_limit1_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+110, y_multiplier_integer,
                                   Sankey_limit2_menu,
                                   True, False, True, False, 90, GUI_IO_util.visualization_csv_field_dynamic_network_lb_pos,
                                   "Select the maximum number of categories for variable 2")

Sankey_limit3_lb = tk.Label(window, text='Variable 3 max')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_dynamic_network_field_pos, y_multiplier_integer,
                                               Sankey_limit3_lb, True)

Sankey_limit3_var = tk.IntVar()
Sankey_limit3_var.set(20)
Sankey_limit3_menu = tk.OptionMenu(window, Sankey_limit3_var, 5, 10, 20, 30)
Sankey_limit1_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_dynamic_network_field_pos+110, y_multiplier_integer,
                                   Sankey_limit3_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_csv_field_dynamic_network_lb_pos,
                                   "Select the maximum number of categories for variable 3")


# activate_csv_fields_relational_selection()

# split
categorical_checkbox = tk.Checkbutton(window, text='Visualize categorical data', variable=categorical_var,
                                    onvalue=1, command=lambda:activate_all_options(()))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   categorical_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox if you wish to visualize categorical data in interactive sunburst or treemap charts")

csv_field_categorical_var.set('Sunburst')
csv_field_categorical_menu = tk.OptionMenu(window, categorical_menu_var, 'Colormap', 'Sunburst', 'Treemap')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                   csv_field_categorical_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_filename_label_lb_pos,
                                   "Visualize categorical data as colormap chart, sunburst chart, or treemap chart)")

# def activate_case_label(*args):
#     if case_sensitive_var.get():
#         case_sensitive_checkbox.configure(text="Case sensitive")
#     else:
#         case_sensitive_checkbox.configure(text="Case insensitive")
# case_sensitive_var.trace('w',activate_case_label)

def activate_csv_fields_categorical_selection(comingFromPlus = True):
    global csv_file_categorical_field_string, search_values_categorical, csv_field_categorical_menu
    if csv_field_categorical_var.get()!='':
        if csv_field_categorical_var.get() in csv_file_categorical_field_list:
            mb.showwarning(title='Warning', message='The option has already been selected. Selection ignored.\n\nYou can see your current selections by clicking the Show button.')
            return
        else:
            # csv_file_categorical_field_list.append(csv_field_categorical_var.get())
            csv_file_categorical_field_string=csv_file_categorical_field_string + '|' + csv_field_categorical_var.get()
    if csv_field_categorical_var.get() != '':
        search_values_categorical.configure(state='normal')
        if comingFromPlus:
            csv_field_categorical_menu.config(state='normal')
        else:
            csv_field_categorical_menu.config(state='disabled')
        add_button_categorical.config(state='normal')
        reset_button_categorical.config(state='normal')
        # show_button.config(state='normal')
    else:
        search_values_categorical.configure(state='disabled')
        csv_field_categorical_menu.config(state='normal')
        # reset_button_categorical.config(state='disabled')
        # show_button.config(state='disabled')
    activate_all_options()
categorical_menu_var.trace('w', callback = lambda x,y,z: activate_csv_fields_categorical_selection())

csv_field_categorical_lb = tk.Label(window, text='Search field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               csv_field_categorical_lb, True)

csv_field_categorical_menu = tk.OptionMenu(window, csv_field_categorical_var, *menu_values) # Sunburst
csv_field_categorical_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                   csv_field_categorical_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Select the csv file field to be used to visualize specific data (e.g., 'Sentiment label' in a sentiment analysis csv output file)")

case_sensitive_var.set(1)
# text='Case sensitive'
case_sensitive_checkbox = tk.Checkbutton(window, state='disabled', variable=case_sensitive_var,
                                    onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                   case_sensitive_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Tick/untick the checkbox if you wish to process the search values as case sensitive or insensitive")

# visualization_do_not_split_pos; visualization_csv_field2_lb_pos
search_values_categorical_label_lb = tk.Label(window, text='Search values')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+30,
                                               y_multiplier_integer, search_values_categorical_label_lb, True)

search_values_categorical_var.set('')
search_values_categorical = tk.Entry(window, state='disabled', textvariable=search_values_categorical_var, width=GUI_IO_util.widget_width_short)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                   search_values_categorical,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Enter the comma-separated search values to be used to sample the corpus for visualization.\nIf you select 'Document' as csv file field, you can enter specific parts of a filename (e.g., Book1, Book2 in Harry Potter_Book1_1, Harry Potter_Book2_3, ...).\nIf you select 'NER' as csv file field in an input CoNLL table, you can enter the tags 'PERSON' or 'LOCATION, COUNTRY, STATE_OR_PROVINCE, CITY'")
def add_combination_csvField_searchValues():
    comingFromPlus=True
    global csv_file_categorical_field_string
    if (not search_values_categorical_var.get()=='') and (search_values_categorical_var.get() in csv_file_categorical_field_string):
        result = mb.askyesno('Warning',
                                    'You have already entered the search value(s) "' + search_values_categorical_var.get() + '"\n\nAre you sure you want to use the same search values?')
        if not result:
            return

    csv_file_categorical_field_string=csv_field_categorical_var.get()+'|'+search_values_categorical_var.get()
    csv_file_categorical_field_list.append([csv_file_categorical_field_string])
    search_values_categorical_var.set('')
    csv_field_categorical_menu.focus_set()
    activate_all_options()
    comingFromPlus=False

add_button_categorical = tk.Button(window, text='+', width=GUI_IO_util.add_button_width,height=1,command=lambda: add_combination_csvField_searchValues())
add_button_categorical.configure(state='disabled')

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.close_button_x_coordinate+20,
                                               y_multiplier_integer,
                                               add_button_categorical, True, False, False, False, 90,
                                               GUI_IO_util.run_button_x_coordinate,
                                               "Click the + button to add another csv field")

def reset_categorical():
    csv_file_categorical_field_list.clear()
    csv_field_categorical_var.set('')
    selected_csv_file_fields.set('')
    selected_csv_file_fields_var.set('')
    search_values_categorical_var.set('')
    if csv_field_categorical_var.get() == '' and 'Document' in menu_values:
        csv_field_categorical_var.set('Document')


reset_button_categorical = tk.Button(window, text='Reset ', width=GUI_IO_util.reset_button_width,height=1,command=lambda: reset_categorical())
reset_button_categorical.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.close_button_x_coordinate+55,
                                               y_multiplier_integer,
                                               reset_button_categorical, True, False, False, False, 90,
                                               GUI_IO_util.run_button_x_coordinate,
                                               "Click the reset_relational button to clear all selected values")

show_button_categorical = tk.Button(window, text='Show', width=GUI_IO_util.show_button_width,height=1,command=lambda: show_categorical_list())
show_button_categorical.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.close_button_x_coordinate+105,
                                               y_multiplier_integer,
                                               show_button_categorical, False, False, False, False, 90,
                                               GUI_IO_util.run_button_x_coordinate,
                                               "Click the Show button to see all selected options")

def show_categorical_list():
    if len(csv_file_categorical_field_list)==0:
        mb.showwarning(title='Warning',
                   message='There are no currently selected combinations of csv file field and search words.')
    else:
    #     class_color_1_string = ""
    #     for ont in color_1_map.keys():
    #         class_color_1_string = class_color_1_string + ont + ":" + color_1_map[ont] + "\n"
        mb.showwarning(title='Warning', message='The currently selected combination of csv file field and search word are:\n\n' + str(csv_file_categorical_field_list) + '\n\nPlease, press the Reset button (or ESCape) to start fresh.')


filter_lb = tk.Label(window, text='Filtering options')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,
                                               y_multiplier_integer, filter_lb, True)

filter_options_var.set('No filtering')
filter_options_menu = tk.OptionMenu(window, filter_options_var, 'No filtering', 'Fixed parameter', 'Propagating parameter')
filter_options_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                   filter_options_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Select the type of filtering to be used in processing larger volumes of data which would make the charts unreadable")


fixed_param_lb = tk.Label(window, text='Fixed')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate,
                                               y_multiplier_integer, fixed_param_lb, True)

fixed_param_var.set(50)
fixed_param = tk.Entry(window, state='disabled', textvariable=fixed_param_var, width=3)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+50, y_multiplier_integer,
                                   fixed_param,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Enter the FIXED parameter value in a typical range 50-100 (default = 50)\n"
                                    "Available only when selecting the 'Fixed parameter' filtering option")

rate_param_lb = tk.Label(window, text='Rate')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,
                                               y_multiplier_integer, rate_param_lb, True)

rate_param_var.set(3)
rate_param = tk.Entry(window, state='disabled', textvariable=rate_param_var, width=3)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+40, y_multiplier_integer,
                                   rate_param,
                                   True, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Enter the RATE parameter value in a typical range 3-20 (default = 3)\n"
                                    "Available only when selecting the 'Propagating parameter' filtering option")

# Option 2: Rate-Propagating Parameter Filtering: 2 values Rate filtering 3 value Base filtering value def = 40

base_param_lb = tk.Label(window, text='Base')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.run_button_x_coordinate,
                                               y_multiplier_integer, base_param_lb, True)

base_param_var.set(40)
base_param = tk.Entry(window, state='disabled', textvariable=base_param_var, width=3)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.run_button_x_coordinate+40, y_multiplier_integer,
                                   base_param,
                                   False, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Enter the BASE parameter value in a typical range 50-100 (default = 40)\n"
                                    "Available only when selecting the 'Propagating parameter' filtering option")

def activate_filtering_options(*args):
    fixed_param.configure(state='disabled')
    rate_param.configure(state='disabled')
    base_param.configure(state='disabled')
    if not categorical_var.get():
        return
    if 'Fixed' in filter_options_var.get():
        fixed_param.configure(state='normal')
    if 'Propagating' in filter_options_var.get():
        rate_param.configure(state='normal')
        base_param.configure(state='normal')

filter_options_var.trace('w',activate_filtering_options)

colormap_lb = tk.Label(window, text='Colormap parameters',foreground="red",font=("Courier", 12, "bold"))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   colormap_lb,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The widgets on this line refer to the colormap option only")

max_rows_lb = tk.Label(window, text='Max no. of rows')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate,
                                               y_multiplier_integer, max_rows_lb, True)

max_rows_var.set(20)
max_rows = tk.Entry(window, state='disabled', textvariable=max_rows_var, width=3)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_filename_label_pos, y_multiplier_integer,
                                   max_rows,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Enter the maximum number of rows to be shown in the chart (default = 20).\nEach row will be displayed on the Y-axis as the most-frequent csv field values.")

color_1_var.set(0)
color_1_style_var_list.append("")
color_1_var_list.append(0)
color_1_checkbox = tk.Checkbutton(window, text='Color ', variable=color_1_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                   color_1_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Tick the checkbox to select the LIGHTER color (left to right) for less frequent occurrences to be used for the cormap (default = light blue, RGB = 135 207 236)")

# color_1_lb = tk.Label(window, text='RGB color code ')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 400, y_multiplier_integer,
#                                                color_1_lb, True)

color_1_style_var.set("135, 207, 236")
color_1_entry = tk.Entry(window, width=10, textvariable=color_1_style_var)
color_1_entry.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+70, y_multiplier_integer,
                                               color_1_entry,True)

def activate_color_1_palette(*args):
    import tkinter.ttk as ttk
    from tkcolorpicker import askcolor
    if color_1_var.get() == 1:
        style = ttk.Style(window)
        style.theme_use('clam')
        color_1_list = askcolor((135, 207, 236), window)
        color_1_style = color_1_list[0]
        color_1_style_var.set(color_1_style)
color_1_var.trace('w', activate_color_1_palette)


def activate_color_2_palette(*args):
    import tkinter.ttk as ttk
    from tkcolorpicker import askcolor
    if color_2_var.get() == 1:
        style = ttk.Style(window)
        style.theme_use('clam')
        color_2_list = askcolor((0, 0, 255), window)
        color_2_style = color_2_list[0]
        color_2_style_var.set(color_2_style)
color_2_var.trace('w', activate_color_2_palette)

color_2_var.set(0)
color_2_style_var_list.append("")
color_2_var_list.append(0)
color_2_checkbox = tk.Checkbutton(window, text='Color ', variable=color_2_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                   color_2_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Tick the checkbox to select the DARKER color (left to right) for more frequent occurrences to be used for the cormap (default = dark blue, RGB = 0 0 255)")

# color_1_lb = tk.Label(window, text='RGB color code ')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 400, y_multiplier_integer,
#                                                color_1_lb, True)

color_2_style_var.set("0, 0, 255")
color_2_entry = tk.Entry(window, width=10, textvariable=color_2_style_var)
color_2_entry.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+70, y_multiplier_integer,
                                               color_2_entry, True)

normalize_lb = tk.Label(window, text='Normalize')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.run_button_x_coordinate, y_multiplier_integer,
                                               normalize_lb, True)

normalize_var=tk.StringVar()
normalize_var.set('No transform')
normalize_menu = tk.OptionMenu(window, normalize_var, 'No transform','Min-Max','Z-score','Square root','Log','Ln')
# normalize_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_do_not_split_pos, y_multiplier_integer,
                                   normalize_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Select the type of data normalization, if any, to be used in displaying the results, thus making them more comparable")

# sunburst_lb = tk.Label(window, text='Sunburst parameters')
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
#                                    sunburst_lb,
#                                    True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
#                                    "The widgets on this line refer to the sunburst option only")
#
# K_sent_begin_var.set('')
# K_sent_begin_lb = tk.Label(window, text='First K')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate,
#                                                y_multiplier_integer, K_sent_begin_lb, True)
#
# K_sent_begin = tk.Entry(window, state='disabled', textvariable=K_sent_begin_var, width=3)
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate+70, y_multiplier_integer,
#                                    K_sent_begin,
#                                    True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
#                                    "Enter the number of sentences at the beginning of each document to be used to visualize differences in the data\nThe option requires a Document ID and a Sentence ID field in the input file")
#
# K_sent_end_var.set('')
# K_sent_end_lb = tk.Label(window, text='Last K')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate,
#                                                y_multiplier_integer, K_sent_end_lb, True)
# K_sent_end = tk.Entry(window, state='disabled',textvariable=K_sent_end_var, width=3)
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+70, y_multiplier_integer,
#                                    K_sent_end,
#                                    True, False, True, False, 90, GUI_IO_util.visualization_K_sent_end_lb_pos,
#                                    "Enter the number of sentences at the end of each document to be used to visualize differences in the data\nThe option requires a Document ID and a Sentence ID field in the input file")
#
# split_var.set(0)
# split_checkbox = tk.Checkbutton(window, state='disabled',text='Split documents in equal halves', variable=split_var,
#                                     onvalue=1, command=lambda: activate_all_options())
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_split_pos, y_multiplier_integer,
#                                    split_checkbox,
#                                    True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
#                                    "Tick the checkbox if you wish to visualize differences in the data by splitting each document in two halves\nThe option requires a Document ID and a Sentence ID field in the input file")
#
# do_not_split_var.set(0)
# do_not_split_checkbox = tk.Checkbutton(window, state='disabled', text='Do NOT split documents', variable=do_not_split_var,
#                  onvalue=1, command=lambda: activate_all_options())
# do_not_split_checkbox.configure(state='disabled')
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_do_not_split_pos, y_multiplier_integer,
#                                    do_not_split_checkbox,
#                                    False, False, True, False, 90, GUI_IO_util.visualization_split_pos,
#                                    "Tick the checkbox if you wish to visualize the entire data")

treemap_lb = tk.Label(window, text='Treemap parameters',foreground="red",font=("Courier", 12, "bold"))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   treemap_lb,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The widgets on this line refer to the treemap option only")

use_numerical_variable_var.set(0)
use_numerical_variable_checkbox = tk.Checkbutton(window, state='disabled', text='Use numerical variable', variable=use_numerical_variable_var,
                 onvalue=1, offvalue=0)
use_numerical_variable_checkbox.configure(state='disabled')

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                   use_numerical_variable_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.visualization_K_sent_begin_pos,
                                   "Tick the checkbox if you wish to use a numerical variable to improve the treemap chart")

csv_field_treemap_lb = tk.Label(window, text='Search field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                               csv_field_treemap_lb, True)

csv_field_treemap_menu = tk.OptionMenu(window, csv_field_treemap_var, *menu_values) # treemap
csv_field_treemap_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+100, y_multiplier_integer,
                                   csv_field_treemap_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Select the csv file field to be used to visualize specific data\nThe field must be categorical rather than numeric (e.g., 'Sentiment label', rather than 'Sentiment score', in a sentiment analysis csv output file)")


def changed_filename(tracedInputFile):
    global error
    if tracedInputFile.endswith('.csv'):
        error = False
    else:
        error = True

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
        # mb.showwarning("Warning",
        #                "The selected input option is not a csv file.\n\nThe visualization algorithms behind this GUI expect in input a csv file.\n\nPlease, select a csv file in input and try again.")
    m1 = csv_field_relational_menu["menu"] # relational
    m2 = dynamic_network_field_menu["menu"]
    m1.delete(0, "end")
    m2.delete(0, "end")

    for s in menu_values:
        m1.add_command(label=s, command=lambda value=s: csv_field_relational_var.set(value))
        m2.add_command(label=s, command=lambda value=s: dynamic_network_field_var.set(value))

    m3 = csv_field_categorical_menu["menu"] # Sunburst
    m3.delete(0, "end")

    for s in menu_values:
        m3.add_command(label=s, command=lambda value=s: csv_field_categorical_var.set(value))
    m3 = csv_field_categorical_menu["menu"]
    # if 'Document' in menu_values:
    #     csv_field_categorical_var.set('Document')

    m4 = csv_field_treemap_menu["menu"] # treemap
    m4.delete(0, "end")

    for s in menu_values:
        m4.add_command(label=s, command=lambda value=s: csv_field_treemap_var.set(value))

    clear("<Escape>")

# changed_filename(GUI_util.inputFilename.get())

def activate_all_options(*args):
    if error:
        relations_checkbox.configure(state='disabled')
        categorical_checkbox.configure(state='disabled')
        return

    extra_GUIs_checkbox.configure(state='normal')
    relations_checkbox.configure(state='normal')
    categorical_checkbox.configure(state='normal')

    extra_GUIs_menu.configure(state='disabled')
    # relations options
    relations_menu.configure(state='disabled')
    csv_field_relational_menu.configure(state='disabled')
    dynamic_network_field_menu.configure(state='disabled')
    Sankey_limit1_menu.configure(state='disabled')
    Sankey_limit2_menu.configure(state='disabled')
    Sankey_limit3_menu.configure(state='disabled')

    # categorical options
    csv_field_categorical_menu.configure(state='disabled')
    case_sensitive_checkbox.configure(state='disabled')
    filter_options_menu.configure(state='disabled')
    max_rows.configure(state='disabled')
    color_1_checkbox.configure(state='disabled')
    color_2_checkbox.configure(state='disabled')
    normalize_menu.configure(state='disabled')
    # K_sent_begin.configure(state='disabled')
    # K_sent_end.configure(state='disabled')
    # split_checkbox.configure(state='disabled')
    # do_not_split_checkbox.configure(state='disabled')
    search_values_categorical.configure(state='disabled')

    if extra_GUIs_var.get():
        extra_GUIs_menu.configure(state='normal')
        relations_checkbox.configure(state='disabled')
        categorical_checkbox.configure(state='disabled')
    elif relations_var.get():
        extra_GUIs_checkbox.configure(state='disabled')
        relations_menu.configure(state='normal')
        relations_checkbox.configure(state='normal')
        categorical_checkbox.configure(state='disabled')
        csv_field_relational_menu.configure(state='normal')
        dynamic_network_field_menu.configure(state='normal')
        dynamic_network_field_menu.configure(state='disabled') # delete this line when date issue solved

        if extra_GUIs_var:
            extra_GUIs_menu.configure(state='normal')

        elif relations_menu_var.get() == '':
            dynamic_network_field_menu.configure(state='disabled')
        elif relations_menu_var.get() == 'Gephi':
            dynamic_network_field_menu.configure(state='normal')
            dynamic_network_field_menu.configure(state='disabled')  # delete this line when date issue solved
            Gephi_var.set(True)
            Sankey_var.set(False)
        elif relations_menu_var.get() == 'Sankey':
            dynamic_network_field_menu.configure(state='disabled')
            Gephi_var.set(False)
            Sankey_var.set(True)
            Sankey_limit1_menu.configure(state='normal')
            Sankey_limit2_menu.configure(state='normal')
            Sankey_limit3_menu.configure(state='normal')

    elif categorical_var.get(): # sunburst, treemap
        search_values_categorical.configure(state='normal')
        extra_GUIs_checkbox.configure(state='disabled')
        menu_values = get_csv_file_menu_vales()
        if csv_field_categorical_var.get()=='' and 'Document' in menu_values:
            csv_field_categorical_var.set('Document')

        # case_sensitive_checkbox.configure(state='normal')
        # for now always set to disabled

        csv_field_categorical_menu.configure(state='normal')
        # categorical_menu.configure(state='disabled') #for now only Document can be selected
        categorical_checkbox.configure(state='normal')
        # csv_field_categorical_menu.configure(state='disabled') #for now only Document can be selected
        relations_checkbox.configure(state='disabled')
        case_sensitive_checkbox.configure(state='disabled')

        if csv_field_categorical_var.get()=='':
            # search_values_categorical.configure(state='disabled')
            add_button_categorical.configure(state='normal')
            reset_button_categorical.configure(state='normal')
            show_button_categorical.configure(state='normal')
            # add_button_categorical.configure(state='disabled')
            # reset_button_categorical.configure(state='disabled')
            # show_button_categorical.configure(state='disabled')
        else:
            show_button_categorical.configure(state='normal')
            #     search_values_categorical.configure(state='normal')
            #     if search_values_categorical_var.get()!='':
        #         add_button_categorical.configure(state='normal')
        #         reset_button_categorical.configure(state='normal')
        #         show_button_categorical.configure(state='normal')

            search_values_categorical.configure(state='normal')
            filter_options_menu.configure(state='normal')

        if categorical_menu_var.get()=='':
            # K_sent_begin.configure(state='disabled')
            # K_sent_end.configure(state='disabled')
            # split_checkbox.configure(state='disabled')
            # do_not_split_checkbox.configure(state='disabled')
            use_numerical_variable_checkbox.configure(state='disabled')

        elif categorical_menu_var.get() == 'Colormap':
            max_rows.configure(state='normal')
            color_1_checkbox.configure(state='normal')
            color_2_checkbox.configure(state='normal')
            normalize_menu.configure(state='normal')
        elif categorical_menu_var.get()=='Sunburst':
            csv_field_categorical_menu.configure(state='normal')
            # K_sent_begin.configure(state='normal')
            # K_sent_end.configure(state='normal')
            # split_checkbox.configure(state='normal')
            # do_not_split_checkbox.configure(state='normal')
            # if K_sent_begin_var.get() != '' or K_sent_end_var.get() != '':
            #     split_checkbox.configure(state='disabled')
            #     do_not_split_checkbox.configure(state='disabled')
            # if do_not_split_var.get():
            #     K_sent_begin.configure(state='disabled')
            #     K_sent_end.configure(state='disabled')
            #     split_checkbox.configure(state='disabled')
            # if split_var.get():
            #     K_sent_begin.configure(state='disabled')
            #     K_sent_end.configure(state='disabled')
            #     do_not_split_checkbox.configure(state='disabled')
            csv_field_treemap_var.set('')
            csv_field_treemap_menu.configure(state='disabled')

        elif categorical_menu_var.get()=='Treemap':
            # K_sent_begin.configure(state='disabled')
            # K_sent_end.configure(state='disabled')
            # split_checkbox.configure(state='disabled')
            # do_not_split_checkbox.configure(state='disabled')

            use_numerical_variable_checkbox.configure(state='normal')
            csv_field_treemap_menu.configure(state='normal')

        # if split_var.get():
        #     K_sent_begin.configure(state='disabled')
        #     K_sent_end.configure(state='disabled')
        #     do_not_split_checkbox.configure(state='disabled')

activate_all_options()

relations_menu_var.trace('w',activate_all_options)
csv_field_relational_var.trace('w',activate_all_options)
# csv_field_categorical_var.trace('w',activate_all_options)
# K_sent_begin_var.trace('w',activate_all_options)
# K_sent_end_var.trace('w',activate_all_options)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {
               "Network Graphs (via Gephi)": "TIPS_NLP_Gephi network graphs.pdf",
               "Specialized visualization tools 1":"TIPS_NLP_Specialized visualization tools 1.pdf",
               "Specialized visualization tools 2":"TIPS_NLP_Specialized visualization tools 2.pdf",
               "Word clouds":"TIPS_NLP_Wordclouds Visualizing word clouds.pdf",
               'Excel charts': 'TIPS_NLP_Excel Charts.pdf',
               'csv files - Problems & solutions': 'TIPS_NLP_csv files - Problems & solutions.pdf'}

TIPS_options='Network Graphs (via Gephi)', 'Specialized visualization tools 1', 'Specialized visualization tools 2','Word clouds', 'Excel charts', 'csv files - Problems & solutions'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    # reset_relationalAll = "\n\nPress the reset_relational button to clear all selected values, and start fresh."
    # plusButton = "\n\nPress the + buttons, when available, to add a new field."
    # OKButton = "\n\nPress the OK button, when available, to accept the selections made, then press the RUN button to process the query."
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_CoNLL)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the GUI you wish to open for specialized data visualization options: Excel charts, geographic maps in Google Earth Pro, HTML file, wordclouds.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to visualize relations between a set of elements, 3 elements in a network graph in Gephi (e.g, SVO) or 2 or 3 elements in a Plotly Sankey chart (e.g., SVO or SO).\n\n\n\nOptions become available in succession.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the csv file fields to be used to visualize relations.\n\nPress the + button to add successive fields until all 2 or 3 elements have been added (2 or 3 for Sankey, 3 for Gephi). For instance, in a Gephi graph, the first field selected is the first node; the second field selected is the edge; the third field selected is the second node (the selected fields will be displayed in the grayed out widget; make sure to press the + sign after the last selection).\n\nPress the 'reset_relational ' button to clear selected values and start fresh.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","THE WIDGETS ON THIS LINE REFER TO THE GEPHI CHART ONLY.\n\nFor Gephi network graphs, once all three fields (node 1, edge, node 2) have been selected, the widget 'csv file field for dynamic graph' will become available. When available, select a field to be used for dynamic networks (e.g., the Sentence ID or Date) or ignore the option if the network should not be dynamic.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","THE WIDGETS ON THIS LINE REFER TO THE SANKEY CHART ONLY.\n\nPlease, using the dropdown menus, select the maximum number of values to be considered for each of the 2 or 3 elements in computing the interactive Sankey chart.\n\nWith to many values, Sankey charts become very messy.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to visualize data in interactive charts (e.g., sunburst or treemap).\n\nThe algorithm applies to categorical data rather than numerical data.")
    # search line
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","The widgets in this line are REQUIRED to run either the Sunburst or Treemap algorithms.\n\nPlease, enter at least two sets of combinations of csv file field and search values.\n\n   First, select the csv file field using the dropdown menu.\n\n   Second, enter the comma-separated search values to be used from that field to construct the chart.\n   For instance, if you select 'Document' as csv file field, you can enter specific parts of a filename (e.g., Book1, Book2 in Harry Potter_Book1_1, Harry Potter_Book2_3, ...).\n   If you select 'NER' as csv file field in an input CoNLL table, you can enter the tags 'PERSON' or 'LOCATION', 'COUNTRY', 'STATE_OR_PROVINCE', 'CITY'.\n\n   Finally, click on + symbol to accept the current combination of csv field and values (at least two combinations are required) (you can also press the Reset button to clear all selected values and start fresh, or the Show button to visualize the currently selected options). After clicking + you can enter another combination or click on RUN to obtain the chart.\n\nALWAYS CLICK THE + SYMBOL AFTER HAVING ENTERED THE LAST COMBINATION.")
    # filtering line
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","The widgets in this line refer to the Sunburst or Treemap algorithms.\n\nThe options allow you to filter data when too many data values would simply make the charts unreadable.\n\n"
                        "'No filtering' is the default option. Start with this option, then, if necessary, try filtering."
                        "\n   Select the 'Fixed parameter' option and see whether the chart improves, perhaps varying the parameter value."
                        "\n   Select the 'Propagating parameter' option to use different filters for each layer of seletected csv file field, and see whether the chart improves, perhaps varying the parameter values.")
    # colormap line
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","THE WIDGETS ON THIS LINE REFER TO THE COLORMAP OPTION ONLY.\n\nPlease, enter the maximum number of rows to be displayed in the chart (default = 20).\n\nTick the 'Color' checkbox to select from the color palette the RGB color to be used for the chart (default color orange, RGB 255 166 0).")
    # OLD line
    # y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","THE WIDGETS ON THIS LINE REFER TO THE SUNBURST OPTION ONLY.\n\nPlease, enter the number of sentences at the beginning and at the end of a document to be used to visualize specific sentences.\n\nTick the checkbox 'Split documents in equal halves' if you wish to visualize the data for the first and last half of the documents in your corpus, rather than for begin and end sentences.\n\nTick the checkbox 'Do NOT split documents' if you wish to visualize an entire document.\n\nThe three options are mutually exclusive.\n\nThe Sunburst algorithm uses the values in Document ID and Sentence ID to process First K and Last K sentences or to split a document in halves.")
    # treemap line
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","THE WIDGETS ON THIS LINE REFER TO THE TREEMAP OPTION ONLY. THE FIELDS ARE OPTIONAL (i.e., not required to run the treemap algorithm). \n\nPlease, tick the checkbox if you wish to use the values of a numerical variable to improve the treemap chart.\n\nUse the dropdown menu to select the csv file numeric field to be used for plotting.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 script provides access to different GUIs to be used to visualize data (e.g., wordclouds) and network graphs via Gephi and Sankey different interactive charts via Sankey, sunburst, and treemap.\n\nIn INPUT the algorithms expect a csv file. The categorical and time-dependent algorithms also expect the csv file to have a 'Document' field header as created by various NLP Suite algoriths.\n\nIn OUTPUT the algorithms produce different types of charts."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

activate_all_options()

GUI_util.window.mainloop()
