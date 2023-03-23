# written by Roberto Franzosi November 2019
# rewritten by Roberto January 2023

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"data_visualization.py",['os','tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_csv_util
import IO_files_util


def runGephi(inputFilename, outputDir, csv_file_field_list, dynamic_network_field_var):
    import Gephi_util

    fileBase = os.path.basename(inputFilename)[0:-4]
    # csv_file_field_list contains the column header of node1, edge, node2 (e.g., SVO), and, possibly, the field for dynamic network
    return Gephi_util.create_gexf(GUI_util.window, fileBase, outputDir, inputFilename,
                                  csv_file_field_list[0], csv_file_field_list[1],
                                  csv_file_field_list[2], dynamic_network_field_var)


def run(inputFilename, inputDir, outputDir, openOutputFiles,
        relations_var,
        relations_menu_var,
        csv_field_var,
        csv_file_field_list,
        dynamic_network_field_var,
        Sankey_limit1_var, Sankey_limit2_var, Sankey_limit3_var,
        categorical_var,
        filename_label_var,
        csv_field2_var,
        K_sent_begin_var,
        K_sent_end_var,
        split_var,
        do_not_split_var,
        time_mapper_var,
        date_format_var,
        time_var,
        cumulative_var,
        csv_field3_var):

    filesToOpen = []
    int_K_sent_begin_var=None
    int_K_sent_end_var=None

    if relations_var==False and categorical_var == False and time_mapper_var==False:
        mb.showwarning("Warning",
                       "No options have been selected.\n\nPlease, select an option to run and try again.")
        return
    else:
        # check if input file is csv
        if inputDir!='' or os.path.basename(inputFilename)[-4:] != ".csv":
            mb.showwarning("Warning",
                           "The visualization options requires in input a csv file.\n\nPlease, select a csv file and try again.")
            return

    if relations_menu_var!='':
        output_label=relations_menu_var
    elif categorical_menu_var.get()!='':
        output_label = categorical_menu_var.get()
    else:
        output_label = ''

    chart_outputFilename = ''
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
            if len(csv_file_field_list)!=3:
                mb.showwarning("Warning",
                               "You must select three csv fields to be used in the computation of the network graph, in the order of node, edge, node (e.g., Subject, Verb, Object).\n\nIf you wish to create a dynamic network graph you can select a fourth field to be used as the dynamic index (e.g., Sentence ID).")
                return
            chart_outputFilename = runGephi(inputFilename, outputDir, csv_file_field_list, dynamic_network_field_var)

# Sankey  --------------------------------------------------------------------------------

        if relations_menu_var=='Sankey':
            if len(csv_file_field_list)!=2 and len(csv_file_field_list)!=3:
                mb.showwarning("Warning",
                               "You must select 2 or 3 csv fields to be used in the computation of a Sankey plot (e.g., Subject, Verb, Object or Subject, Object).")
                return
            import charts_Sankey_util
            if len(csv_file_field_list)==3:
                three_way_Sankey=True
                var3=csv_file_field_list[2]
                # Sankey_limit3_var
            else:
                three_way_Sankey = None
                var3=None
                Sankey_limit3_var=None
            chart_outputFilename = charts_Sankey_util.Sankey(inputFilename, outputFilename,
                                csv_file_field_list[0], Sankey_limit1_var, csv_file_field_list[1], Sankey_limit2_var, three_way_Sankey, var3, Sankey_limit3_var)
            # Function takes a csv file as data input,

# Categorical data (sunburst or treemap) --------------------------------------------------------------------------------

    if categorical_var:
        if categorical_menu_var.get() == '':
            mb.showwarning("Warning",
                           "Please, use the dropdown menu to select one of the options for categorical data: Sunburst, treemap and try again.")
            return
        if filename_label_var == '':
            mb.showwarning("Warning",
                           "The categorical data visualization functions require a set of comma-separated entries in the 'Label/part in the filename to be used for visualization' widget.\n\nPlease, enter value(s) and try again.")
            return

        # interest pass a list [] of labels embedded in the filename, e.g. Book1, Book2, ... or Chinese, Arabian,...
        interest = []
        temp_interest=[]
        interest = filename_label_var.split(',')
        for i in range(len(interest)):
            temp_interest.append(interest[i].lstrip())
        # label is a string that has the header field in the csv file to be used for display
        label=csv_field2_var

# Categorical data: Sunburst  --------------------------------------------------------------------------------

        if 'Sunburst' in categorical_menu_var.get():
            if csv_field2_var=='':
                mb.showwarning("Warning",
                               "The sunburst visualization function requires a value for 'csv file field.'\n\nPlease, select a value and try again.")
                return

            if K_sent_begin_var=='' and K_sent_end_var=='' and split_var==False and do_not_split_var==False:
                mb.showwarning("Warning",
                               "The sunburst function requires a selection of Begin/End K sentences or Split documents in equal halves or Do not split documents.\n\nPlease, make a selection and try again.")
                return
            # check that K_sent_begin_var and K_sent_end_var values are numeric
            if split_var==False and do_not_split_var==False:
                try:
                    if type(int(K_sent_begin_var))!= int:
                        int_K_sent_begin_var = int(K_sent_begin_var)
                        pass
                except:
                    mb.showwarning("Warning",
                                   "The value entered for Begin K sentences MUST be a numeric integer.\n\nPlease, enter a numeric value and try again.")
                    return
                try:
                    if type(int(K_sent_end_var))!= int:
                        int_K_sent_end_var = int(K_sent_end_var)
                        pass
                except:
                    mb.showwarning("Warning",
                                   "The value entered for End K sentences MUST be a numeric integer.\n\nPlease, enter a numeric value and try again.")
                    return
            else:
                int_K_sent_begin_var=None
                int_K_sent_end_var=None

            # # interest pass a list [] of labels embedded in the filename, e.g. Book1, Book2, ... or Chinese, Arabian,...
            # interest = []
            # temp_interest=[]
            # interest = filename_label_var.split(',')
            # for i in range(len(interest)):
            #     temp_interest.append(interest[i].lstrip())
            # # label is a string that has the header field in the csv file to be used for display
            # label=csv_field2_var
            import charts_sunburst_util
            chart_outputFilename = charts_sunburst_util.Sunburster(inputFilename, outputFilename, outputDir, case_sensitive_var, temp_interest, label,
                                            do_not_split_var, int_K_sent_begin_var, int_K_sent_end_var, split_var)

# Categorical data: treemap --------------------------------------------------------------------------------

    if 'Treemap' in categorical_menu_var.get():
        if use_numerical_variable_var and csv_field2_var=='':
            mb.showwarning("Warning",
                           "The selected treemap option with the use of numerical data requires a variable containing the numertical data.\n\nPlease, select the csv file field containing the numertical data and try again.")
            return
        import charts_treemaper_util
        #def treemaper(data,outputFilename,interest,var,extra_dimension_average,average_variable=None):
        chart_outputFilename = charts_treemaper_util.treemaper(inputFilename, outputFilename,
                                                               temp_interest, label, use_numerical_variable_var.get(),csv_field2_var)

# time_mapper --------------------------------------------------------------------------------
    if time_mapper_var:
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                                 '.html', 'timeMapper')

        if csv_field3_var.get()=='':
            mb.showwarning("Warning",
                           "The csv file field is blank. The Plotly timeline algorithm expects in input a valid csv file field.\n\nPlease, select a csv file field and try again.")
            return
        monthly = False
        yearly = False
        if time_var=='Monthly':
            monthly=True
        elif time_var=='Yearly':
            yearly=True

        import charts_timeline_util
        chart_outputFilename = charts_timeline_util.timeline(inputFilename, outputFilename, csv_field3_var.get(), date_format_var, cumulative_var, monthly, yearly)

    if chart_outputFilename != '':
        filesToOpen.append(chart_outputFilename)

    if openOutputFiles and len(filesToOpen) > 0:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            relations_var.get(),
                            relations_menu_var.get(),
                            csv_field_var.get(),
                            csv_file_field_list,
                            dynamic_network_field_var.get(),
                            Sankey_limit1_var.get(), Sankey_limit2_var.get(), Sankey_limit3_var.get(),
                            categorical_var.get(),
                            filename_label_var.get(),
                            csv_field2_var.get(),
                            K_sent_begin_var.get(),
                            K_sent_end_var.get(),
                            split_var.get(),
                            do_not_split_var.get(),
                            time_mapper_var.get(),
                            date_format_var.get(),
                            time_var.get(),
                            cumulative_var.get(),
                            csv_field3_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=680, # height at brief display
                             GUI_height_full=760, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Visualization Tools'
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = scriptName.replace('main.py', 'config.csv')

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
    reset()
    open_GUI_var.set('')
    relations_menu_var.set('Gephi')
    categorical_menu_var.set('Sunburst')

    relations_var.set(0)
    categorical_var.set(0)
    time_mapper_var.set(0)

    relations_checkbox.configure(state='normal')
    categorical_checkbox.configure(state='normal')
    time_mapper_checkbox.configure(state='normal')

    case_sensitive_var.set(1)
    # for now always set to disabled
    case_sensitive_checkbox.configure(state='disabled',text="Case sensitive")
    filename_label.configure(state='disabled')
    filename_label_var.set('')
    csv_field2_var.set('')
    K_sent_begin_var.set('')
    K_sent_end_var.set('')
    K_sent_begin.configure(state='disabled')
    K_sent_end.configure(state='disabled')
    split_var.set(0)
    split_checkbox.configure(state='disabled')
    do_not_split_var.set(0)
    do_not_split_checkbox.configure(state='disabled')
    date_format_menu.configure(state='disabled')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)


open_GUI_var = tk.StringVar()
relations_var = tk.IntVar()
relations_menu_var = tk.StringVar()
Gephi_var = tk.IntVar()
Sankey_var = tk.IntVar()
selected_csv_file_fields_var = tk.StringVar()

csv_field_var = tk.StringVar()
dynamic_network_field_var = tk.StringVar()
categorical_var = tk.IntVar()
categorical_menu_var = tk.StringVar()
case_sensitive_var = tk.IntVar()
filename_label_var = tk.StringVar()
csv_field2_var = tk.StringVar()
K_sent_begin_var = tk.StringVar()
K_sent_end_var = tk.StringVar()
split_var = tk.IntVar()
do_not_split_var = tk.IntVar()

use_numerical_variable_var = tk.IntVar()
csv_field2_var = tk.StringVar()

time_mapper_var = tk.IntVar()
date_format_var = tk.StringVar()
csv_field3_var = tk.StringVar()
time_var = tk.StringVar()
cumulative_var = tk.IntVar()

csv_file_field_list = []
menu_values = []
error = False

open_GUI_lb = tk.Label(window, text='Open special visualization options GUI')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               open_GUI_lb, True)

open_GUI_menu = tk.OptionMenu(window, open_GUI_var, 'Excel charts (Open GUI)','Geographic maps (Open GUI)','HTML annotator (Open GUI)','Wordclouds (Open GUI)')
# open_GUI_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                   open_GUI_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Open a GUI for special visualization options: Excel charts, geographic maps, HTML, wordclouds")

def open_GUI(*args):
    if 'Excel' in open_GUI_var.get():
        call("python charts_Excel_main.py", shell=True)
    elif 'Geographic' in open_GUI_var.get():
        call("python GIS_main.py", shell=True)
    elif 'HTML' in open_GUI_var.get():
        call("python html_annotator_main.py", shell = True)
    elif 'Wordclouds' in open_GUI_var.get():
        call("python wordclouds_main.py", shell=True)
open_GUI_var.trace('w',open_GUI)

relations_checkbox = tk.Checkbutton(window, text='Visualize relations', variable=relations_var,
                                    onvalue=1, command=lambda:activate_visualization_options(()))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   relations_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox if you wish to visualize relational data in interactive Gephi network graphs or Sankey plots")

relations_menu_var.set('Gephi')
relations_menu = tk.OptionMenu(window, relations_menu_var, 'Gephi','Sankey')
# select_time_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   relations_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_filename_label_lb_pos,
                                   "Visualize relations (network graphs via Gephi or Sankey graphs via Plotly)")

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

csv_field_lb = tk.Label(window, text='csv file field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               csv_field_lb, True)

csv_field_menu = tk.OptionMenu(window, csv_field_var, *menu_values)
csv_field_menu.configure(state='disabled')
# place widget with hover-over info
# visualization_csv_field_menu_pos
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   csv_field_menu,
                                   True, False, True, False, 90, GUI_IO_util.visualization_filename_label_lb_pos,
                                   "Select the three fields to be used for the network graph in the order node1, edge, node2 (e.g., SVO)")

def display_selected_csv_fields():
    if csv_field_var.get() != '' and not csv_field_var.get() in csv_file_field_list:
        csv_file_field_list.append(csv_field_var.get())
        # csv_field_menu.configure(state='disabled')
    else:
        mb.showwarning(title='Warning',
                       message='The option "' + csv_field_var.get() + '" has already been selected. Selection ignored.\n\nYou can see your current selections by clicking the Show button.')
        csv_field_menu.configure(state='normal')
    selected_csv_file_fields_var.set(str(csv_file_field_list))
    activate_csv_fields_selection(True)


def reset():
    csv_file_field_list.clear()
    csv_field_var.set('')
    dynamic_network_field_var.set('')
    selected_csv_file_fields_var.set('')

add_button_var = tk.IntVar()
add_button = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1, state='disabled',
                                command=lambda: display_selected_csv_fields())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_add_button_pos, y_multiplier_integer,
                                   add_button,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Click on the + button to add a selected csv field to the list of Gephy parameters (edge1, node, edge2)")

reset_button = tk.Button(window, text='Reset', width=GUI_IO_util.reset_button_width,height=1,state='disabled',command=lambda: reset())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_reset_button_pos, y_multiplier_integer,
                                   reset_button,
                                   True, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Click on the Reset button to clear the list of selected fields and start again")
def show_Gephi_options_list():
    if len(csv_file_field_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected Gephi options.')
    else:
        mb.showwarning(title='Warning', message='The currently selected Gephi options are:\n\n  ' + '\n  '.join(csv_file_field_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

show_button = tk.Button(window, text='Show', width=GUI_IO_util.show_button_width,height=1,state='disabled',command=lambda: show_Gephi_options_list())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_show_button_pos, y_multiplier_integer,
                                   show_button,
                                   False, False, True, False, 90, GUI_IO_util.open_setup_x_coordinate,
                                   "Click on the Show button to display the list of currently selected csv fields")

def activate_csv_fields_selection(comingFromPlus=False):
    if csv_field_var.get() != '':
        if comingFromPlus:
            csv_field_menu.config(state='normal')
        else:
            csv_field_menu.config(state='disabled')
        add_button.config(state='normal')
        reset_button.config(state='normal')
        show_button.config(state='normal')
        if len(csv_file_field_list) == 3:
            csv_field_menu.configure(state='disabled')
            dynamic_network_field_menu.config(state='normal')
            mb.showwarning(title='Warning', message='You have selected the maximum number of fields (3) to visualize relations.\n\nPress the "Show" button to display your selection. Press the "Reset" button to clear your selection and start again.')
    else:
        csv_field_menu.config(state='normal')
        dynamic_network_field_menu.config(state='normal')
        reset_button.config(state='disabled')
        show_button.config(state='disabled')
csv_field_var.trace('w', callback = lambda x,y,z: activate_csv_fields_selection())
dynamic_network_field_var.trace('w', callback = lambda x,y,z: activate_csv_fields_selection())

GUI_util.inputFilename.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))
# GUI_util.input_main_dir_path.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))

Gephi_lb = tk.Label(window, text='Gephi parameters')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   Gephi_lb,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The widgets on this line refer to the Gephi option only")

csv_field_dynamic_network_lb = tk.Label(window, text='csv file field for dynamic graph')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               csv_field_dynamic_network_lb, True)

dynamic_network_field_menu = tk.OptionMenu(window, dynamic_network_field_var, *menu_values)
dynamic_network_field_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu+200, y_multiplier_integer,
                                   dynamic_network_field_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_csv_field_dynamic_network_lb_pos,
                                   "Select the field to be used for a dynamic network graph (e.g., Sentence ID) if you wish to compute a dynamic network graph")

Sankey_lb = tk.Label(window, text='Sankey parameters')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   Sankey_lb,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The widgets on this line refer to the Sankey option only")

Sankey_limit1_lb = tk.Label(window, text='Variable 1 max')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
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


# activate_csv_fields_selection()

# split
categorical_checkbox = tk.Checkbutton(window, text='Visualize categorical data', variable=categorical_var,
                                    onvalue=1, command=lambda:activate_visualization_options(()))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   categorical_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox if you wish to visualize categorical data in interactive sunburst or treemap plots")

categorical_menu_var.set('Sunburst')
categorical_menu = tk.OptionMenu(window, categorical_menu_var, 'Sunburst','Treemap')
# select_time_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   categorical_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_filename_label_lb_pos,
                                   "Visualize categorical data as sunbust plot or treemap plot via Plotly)")

case_sensitive_var.set(1)
case_sensitive_checkbox = tk.Checkbutton(window, state='disabled',text='Case sensitive', variable=case_sensitive_var,
                                    onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   case_sensitive_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Tick/untick the checkbox if you wish to process filename labels/parts as case sensitive or insensitive")

def activate_case_label(*args):
    if case_sensitive_var.get():
        case_sensitive_checkbox.configure(text="Case sensitive")
    else:
        case_sensitive_checkbox.configure(text="Case insensitive")
case_sensitive_var.trace('w',activate_case_label)

filename_label_lb = tk.Label(window, text='Filename label/part')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,
                                               y_multiplier_integer, filename_label_lb, True)

filename_label_var.set('')
filename_label = tk.Entry(window, state='disabled', textvariable=filename_label_var, width=GUI_IO_util.widget_width_short)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                   filename_label,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Enter the comma-separated label/part of a filename to be used to sample the corpus for visualization (e.g., Book1, Book2 in Harry Potter_Book1_1, Harry Potter_Book2_3, ...)")


csv_field2_lb = tk.Label(window, text='csv file field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_csv_field2_lb_pos, y_multiplier_integer,
                                               csv_field2_lb, True)

csv_field2_menu = tk.OptionMenu(window, csv_field2_var, *menu_values)
csv_field2_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_csv_field2_menu_pos, y_multiplier_integer,
                                   csv_field2_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_K_sent_end_pos,
                                   "Select the csv file field to be used to visualize specific data (e.g., 'Sentiment label' in a sentiment analysis csv output file")

sunburst_lb = tk.Label(window, text='Sunburst parameters')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   sunburst_lb,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The widgets on this line refer to the sunburst option only")


K_sent_begin_var.set('')
K_sent_begin_lb = tk.Label(window, text='First K')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_K_sent_begin_lb,
                                               y_multiplier_integer, K_sent_begin_lb, True)

K_sent_begin = tk.Entry(window, state='disabled', textvariable=K_sent_begin_var, width=3)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   K_sent_begin,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Enter the number of sentences at the beginning of each document to be used to visualize differences in the data")

K_sent_end_var.set('')
K_sent_end_lb = tk.Label(window, text='Last K')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_K_sent_end_pos,
                                               y_multiplier_integer, K_sent_end_lb, True)
K_sent_end = tk.Entry(window, state='disabled',textvariable=K_sent_end_var, width=3)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                   K_sent_end,
                                   True, False, True, False, 90, GUI_IO_util.visualization_K_sent_end_lb_pos,
                                   "Enter the number of sentences at the end of each document to be used to visualize differences in the data")

split_var.set(0)
split_checkbox = tk.Checkbutton(window, state='disabled',text='Split documents in equal halves', variable=split_var,
                                    onvalue=1, command=lambda: activate_visualization_options())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_split_pos, y_multiplier_integer,
                                   split_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Tick the checkbox if you wish to visualize differences in the data by splitting each document in two halves")

do_not_split_var.set(0)
do_not_split_checkbox = tk.Checkbutton(window, state='disabled', text='Do NOT split documents', variable=do_not_split_var,
                 onvalue=1, command=lambda: activate_visualization_options())
do_not_split_checkbox.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_do_not_split_pos, y_multiplier_integer,
                                   do_not_split_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.visualization_split_pos,
                                   "Tick the checkbox if you wish to visualize the entire data")

treemap_lb = tk.Label(window, text='Treemap parameters')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   treemap_lb,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The widgets on this line refer to the treemap option only")

use_numerical_variable_var.set(0)
use_numerical_variable_checkbox = tk.Checkbutton(window, state='disabled', text='Use numerical variable', variable=use_numerical_variable_var,
                 onvalue=1)
use_numerical_variable_checkbox.configure(state='disabled')

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_K_sent_begin_pos, y_multiplier_integer,
                                   use_numerical_variable_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.visualization_K_sent_begin_pos,
                                   "Tick the checkbox if you wish to use a numerical variable to improve the treemap plot")


csv_field2_lb = tk.Label(window, text='csv file field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_K_sent_end_pos, y_multiplier_integer,
                                               csv_field2_lb, True)

csv_field2_menu = tk.OptionMenu(window, csv_field2_var, *menu_values)
csv_field2_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                   csv_field2_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Select the csv file field to be used to visualize specific data\nThe field must be categorical rather than numeric (e.g., 'Sentiment label', rather than 'Sentiment score', in a sentiment analysis csv output file)")

time_mapper_var.set(0)
time_mapper_checkbox = tk.Checkbutton(window, text='Visualize temporal data', variable=time_mapper_var,
                                    onvalue=1, command=lambda: activate_visualization_options())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   time_mapper_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox if you wish to visualize data in a dynamic time mapper\nIn input the filenames under Document must contain date values")


date_format_lb = tk.Label(window,text='Date format ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,
                                               y_multiplier_integer, date_format_lb, True)
date_format_var.set('mm-dd-yyyy')
date_format_menu = tk.OptionMenu(window, date_format_var, 'mm-dd-yyyy', 'dd-mm-yyyy','yyyy-mm-dd','yyyy-dd-mm','yyyy-mm','yyyy')
date_format_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,
                                               GUI_IO_util.visualization_K_sent_begin_pos,
                                               y_multiplier_integer,
                                               date_format_menu,
                                               True, False, False, False, 90,
                                               GUI_IO_util.visualization_K_sent_begin_pos,
                                               'Select the date type embedded in your filename')

select_time_lb = tk.Label(window, text='Timeline')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_filename_label_pos, y_multiplier_integer,
                                               select_time_lb, True)

time_var.set('Daily')
select_time_menu = tk.OptionMenu(window, time_var, 'Daily','Monthly','Yearly')
select_time_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                   select_time_menu,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Select the time option")

cumulative_var.set(0)
cumulative_checkbox = tk.Checkbutton(window, text='Cumulative',
                                    onvalue=1)
cumulative_checkbox.configure(state='disabled')

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                   cumulative_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   "Tick the checkbox for a cumulative time chart showing the frequency of the chosen variable up until a current day rather than visualizing the frequency day by day")

csv_field3_lb = tk.Label(window, text='csv file field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_csv_field2_lb_pos, y_multiplier_integer,
                                               csv_field3_lb, True)

csv_field3_menu = tk.OptionMenu(window, csv_field3_var, *menu_values)
csv_field3_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_csv_field2_menu_pos, y_multiplier_integer,
                                   csv_field3_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_K_sent_end_pos,
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
    m1 = csv_field_menu["menu"]
    m2 = dynamic_network_field_menu["menu"]
    m1.delete(0, "end")
    m2.delete(0, "end")

    for s in menu_values:
        m1.add_command(label=s, command=lambda value=s: csv_field_var.set(value))
        m2.add_command(label=s, command=lambda value=s: dynamic_network_field_var.set(value))

    m3 = csv_field2_menu["menu"]
    m3.delete(0, "end")

    for s in menu_values:
        m3.add_command(label=s, command=lambda value=s: csv_field2_var.set(value))

    m4 = csv_field2_menu["menu"]
    m4.delete(0, "end")

    for s in menu_values:
        m4.add_command(label=s, command=lambda value=s: csv_field2_var.set(value))

    m5 = csv_field3_menu["menu"]
    m5.delete(0, "end")

    for s in menu_values:
        m5.add_command(label=s, command=lambda value=s: csv_field3_var.set(value))

    clear("<Escape>")

# changed_filename(GUI_util.inputFilename.get())

def activate_visualization_options(*args):
    if error:
        relations_checkbox.configure(state='disabled')
        categorical_checkbox.configure(state='disabled')
        time_mapper_checkbox.configure(state='disabled')
        return

    relations_checkbox.configure(state='normal')
    categorical_checkbox.configure(state='normal')
    time_mapper_checkbox.configure(state='normal')

    # relations options
    relations_menu.configure(state='disabled')
    csv_field_menu.configure(state='disabled')
    dynamic_network_field_menu.configure(state='disabled')
    Sankey_limit1_menu.configure(state='disabled')
    Sankey_limit2_menu.configure(state='disabled')
    Sankey_limit3_menu.configure(state='disabled')

    # categorical options
    categorical_menu.configure(state='disabled')
    csv_field2_menu.configure(state='disabled')
    case_sensitive_checkbox.configure(state='disabled')
    filename_label.configure(state='disabled')
    K_sent_begin.configure(state='disabled')
    K_sent_end.configure(state='disabled')
    split_checkbox.configure(state='disabled')
    do_not_split_checkbox.configure(state='disabled')

    # time-line options
    date_format_menu.configure(state='disabled')
    select_time_menu.configure(state='disabled')
    cumulative_checkbox.configure(state='disabled')
    csv_field3_menu.configure(state='disabled')

    if relations_var.get():
        relations_menu.configure(state='normal')
        relations_checkbox.configure(state='normal')
        categorical_checkbox.configure(state='disabled')
        time_mapper_checkbox.configure(state='disabled')
        csv_field_menu.configure(state='normal')
        dynamic_network_field_menu.configure(state='normal')
        if relations_menu_var.get() == '':
            dynamic_network_field_menu.configure(state='disabled')
        elif relations_menu_var.get() == 'Gephi':
            dynamic_network_field_menu.configure(state='normal')
            Gephi_var.set(True)
            Sankey_var.set(False)
        elif relations_menu_var.get() == 'Sankey':
            dynamic_network_field_menu.configure(state='disabled')
            Gephi_var.set(False)
            Sankey_var.set(True)
            Sankey_limit1_menu.configure(state='normal')
            Sankey_limit2_menu.configure(state='normal')
            Sankey_limit3_menu.configure(state='normal')

    elif categorical_var.get():
        # case_sensitive_checkbox.configure(state='normal')
        # for now always set to disabled
        categorical_menu.configure(state='normal')
        categorical_checkbox.configure(state='normal')
        relations_checkbox.configure(state='disabled')
        time_mapper_checkbox.configure(state='disabled')
        case_sensitive_checkbox.configure(state='disabled')
        filename_label.configure(state='normal')
        csv_field2_menu.configure(state='normal')

        if categorical_menu_var.get()=='':
            K_sent_begin.configure(state='disabled')
            K_sent_end.configure(state='disabled')
            split_checkbox.configure(state='disabled')
            do_not_split_checkbox.configure(state='disabled')

            use_numerical_variable_checkbox.configure(state='disabled')
            csv_field2_menu.configure(state='disabled')
        elif categorical_menu_var.get()=='Sunburst':
            K_sent_begin.configure(state='normal')
            K_sent_end.configure(state='normal')
            split_checkbox.configure(state='normal')
            do_not_split_checkbox.configure(state='normal')
            if K_sent_begin_var.get() != '' or K_sent_end_var.get() != '':
                split_checkbox.configure(state='disabled')
                do_not_split_checkbox.configure(state='disabled')
            if do_not_split_var.get():
                K_sent_begin.configure(state='disabled')
                K_sent_end.configure(state='disabled')
                split_checkbox.configure(state='disabled')
            if split_var.get():
                K_sent_begin.configure(state='disabled')
                K_sent_end.configure(state='disabled')
                do_not_split_checkbox.configure(state='disabled')
        elif categorical_menu_var.get()=='Treemap':
            K_sent_begin.configure(state='disabled')
            K_sent_end.configure(state='disabled')
            split_checkbox.configure(state='disabled')
            do_not_split_checkbox.configure(state='disabled')

            use_numerical_variable_checkbox.configure(state='normal')
            csv_field2_menu.configure(state='normal')

        if split_var.get():
            K_sent_begin.configure(state='disabled')
            K_sent_end.configure(state='disabled')
            do_not_split_checkbox.configure(state='disabled')
    elif time_mapper_var.get():
        time_mapper_checkbox.configure(state='normal')
        relations_checkbox.configure(state='disabled')
        categorical_checkbox.configure(state='disabled')
        date_format_menu.configure(state='normal')
        select_time_menu.configure(state='normal')
        cumulative_checkbox.configure(state='normal')
        csv_field3_menu.configure(state='normal')

activate_visualization_options()

relations_menu_var.trace('w',activate_visualization_options)
categorical_menu_var.trace('w',activate_visualization_options)
K_sent_begin_var.trace('w',activate_visualization_options)
K_sent_end_var.trace('w',activate_visualization_options)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {"Lemmas & stopwords":"TIPS_NLP_NLP Basic Language.pdf",
               "Word clouds":"TIPS_NLP_Wordclouds Visualizing word clouds.pdf",
               "Wordle":"TIPS_NLP_Wordclouds Wordle.pdf",
               "Tagxedo":"TIPS_NLP_Wordclouds Tagxedo.pdf",
               "Tagcrowd":"TIPS_NLP_Wordclouds Tagcrowd.pdf",
               'Excel charts': 'TIPS_NLP_Excel Charts.pdf',
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
               'Network Graphs (via Gephi)': 'TIPS_NLP_Gephi network graphs.pdf',
               'csv files - Problems & solutions': 'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf'}

TIPS_options='Lemmas & stopwords', 'Word clouds', 'Tagcrowd', 'Tagxedo', 'Wordle', 'Excel smoothing data series', 'Network Graphs (via Gephi)', 'csv files - Problems & solutions', 'Statistical measures'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    # resetAll = "\n\nPress the RESET button to clear all selected values, and start fresh."
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
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to visualize relations between a set of elements, 3 elements in a network graph in Gephi (e.g, SVO) or 2 or 3 elements in a Plotly Sankey graph (e.g., SVO or SO).\n\nOptions become available in succession.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the csv file field to be used to visualize relations.\n\nPress the + button to add another field until all 2 or 3 elements have been added (2 or 3 for Sankey, 3 for Gephi). For instance, in a Gephi graph, the first field selected is the first node; the second field selected is the edge; the third field selected is the second node.\n\nPress the 'Show' button to display the fields currently selected.\n\nPress the 'Reset' button to clear selected values and start fresh.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","THE WIDGETS ON THIS LINE REFER TO THE GEPHI PLOT ONLY.\n\nFor Gephi network graphs, once all three fields (node 1, edge, node 2) have been selected, the widget 'csv file field for dynamic graph' will become available. When available, select a field to be used for dynamic networks (e.g., the Sentence ID) or ignore the option if the network should not be dynamic.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","THE WIDGETS ON THIS LINE REFER TO THE SANKEY PLOT ONLY.\n\nPlease, using the dropdown menus, select the maximum number of values to be considered for each of the 2 or 3 elements in computing the interactive Sankey plot.\n\nWith too many values, Sankey plots become very messy.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to visualize data in an interactive sunburst or treemap plot.\n\nThe algorithm applies to categorical data rather than numerical data.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, enter the comma-separated labels/parts of a filename to be used to separate fields in the filename (e.g., in the filename, Harry Potter_Book1_1, Harry Potter_Book2_3, ..., Harry Potter_Book4_1... you could enter Book1, Book3 to sample the files to be used for visualization.\n\nThe number of distinct labels/parts of filename should be small (e.g., the 7 Harry Potter books).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","THE WIDGETS ON THIS LINE REFER TO THE SUNBUST PLOT ONLY.\n\nPlease, enter the number of sentences at the beginning and at the end of a document to be used to visualize specific sentences.\n\nTick the checkbox 'Split documents in equal halves' if you wish to visualize the data for the first and last half of the documents in your corpus, rather than for begin and end sentences.\n\nTick the checkbox 'Do NOT split documents' if you wish to visualize an entire document.\n\nThe three options are mutually exclusive.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","THE WIDGETS ON THIS LINE REFER TO THE TREEMAP PLOT ONLY.\n\nPlease, tick the checkbox if you wish to use the values of a numerical variable to improve the treemap plot.\n\nUse the dropdown menu to select the csv file numeric field to be used for plotting.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to analyze time-dependent data in an interactive bar chart.\n\nIn INPUT the scripts expects filenames in the 'Document' field that contain date values.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, select the options to be applied to the timeline chart:\n\n1. date format embedded in the filename\n2. Timeline (daily, monthly, yearly)\n3. Cumulative, for a time chart showing the frequency of the chosen variable up until a current day rather than visualizing the frequency day by day\n4. csv file variable to be used for plotting (the variable must contain CATEGORICAL data)." \
            "\n\nYOU CAN SETUP DATES EMBEDDED IN FILENAMES BY CLICKING THE 'Setup INPUT/OUTPUT configuration' WIDGET AT THE TOP OF THIS GUI AND THEN TICKING THE CHECKBOX 'Extract date from filename' WHEN THE NLP_setup_IO_main GUI OPENS.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 script provides access to different GUIs to be used to visualize data (e.g., wordclouds) and network graphs via Gephi and different interactive charts via sunburst and time mapper.\n\nIn INPUT the algorithms expect a csv file. The categorical and time-dependent algorithms also expect the csv file to have a 'Document' field header as created by various NLP Suite algoriths.\n\nIn OUTPUT the algorithms produce different types of charts."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

state = str(GUI_util.run_button['state'])
if state == 'disabled':
    error = True
else:
    error = False

activate_visualization_options()

state = str(GUI_util.run_button['state'])
if state == 'disabled':
    error = True
    # check to see if there is a GUI-specific config file, i.e., a CoNLL table file, and set it to the setup_IO_menu_var
    if os.path.isfile(os.path.join(GUI_IO_util.configPath, config_filename)):
        GUI_util.setup_IO_menu_var.set('GUI-specific I/O configuration')
        mb.showwarning(title='Warning',
               message="Since a GUI-specific " + config_filename + " file is available, the I/O configuration has been automatically set to GUI-specific I/O configuration.")
        error = False

GUI_util.window.mainloop()
