#written by Roberto Franzosi November 2019

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Wordclouds",['os','tkinter','webbrowser'])==False:
    sys.exit(0)

import os
import webbrowser
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_csv_util
import Gephi_util
import charts_Sunburster_util
import IO_files_util

def runGephi(inputFilename, outputDir, csv_file_field_list, dynamic_network_field_var):

    fileBase = os.path.basename(inputFilename)[0:-4]
    # csv_file_field_list contains the column header of node1, edge, node2 (e.g., SVO), and, possibly, the field for dynamic network
    return Gephi_util.create_gexf(GUI_util.window, fileBase, outputDir, inputFilename,
                                  csv_file_field_list[0], csv_file_field_list[1],
                                  csv_file_field_list[2], dynamic_network_field_var)


def run(inputFilename, inputDir, outputDir, openOutputFiles,
        Gephi_var,
        csv_file_field_list,
        dynamic_network_field_var,
        interactive_Sunburster_var,
        filename_label_var,
        csv_field2_var,
        K_sent_begin_var,
        K_sent_end_var,
        split_var,
        interactive_time_mapper_var):

    filesToOpen = []
    int_K_sent_begin_var=None
    int_K_sent_end_var=None

    if Gephi_var==False and interactive_Sunburster_var == False and interactive_time_mapper_var==False:
        mb.showwarning("Warning",
                       "No options have been selected.\n\nPlease, select an option to run and try again.")
        # Gephi_var.set(0)
        return
    else:
        # check if input file is csv
        if inputDir!='' or os.path.basename(inputFilename)[-4:] != ".csv":
            mb.showwarning("Warning",
                           "The visualization options requires in input a csv file.\n\nPlease, select a csv file and try again.")
            return
        else:
            if Gephi_var and len(csv_file_field_list)<3:
                mb.showwarning("Warning",
                               "You must select at least three csv fields to be used in the computation of the network graph, in the order of node, edge, node (e.g., Subject, Verb, Object).\n\nIf you wish to create a dynamic network graph you can select a fourth field to be used as the dynamic index (e.g., Sentence ID).")
                return
        if Gephi_var:
            gexf_file = runGephi(inputFilename, outputDir, csv_file_field_list, dynamic_network_field_var)
            filesToOpen.append(gexf_file)

        if interactive_Sunburster_var:
            if K_sent_begin_var=='' and K_sent_end_var=='' and split_var==False:
                mb.showwarning("Warning",
                               "The Sunburster function requires a selection of either Begin/End K sentences or Split documents in equal halves.\n\nPlease, make a selection and try again.")
                return
            # check that K_sent_begin_var and K_sent_end_var values are numeric
            if split_var==False:
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

            if filename_label_var=='':
                mb.showwarning("Warning",
                               "The Sunburster visualization function requires a set of comma-separated entries in the 'Label/part in the filename to be used for visualization' widget.\n\nPlease, enter value(s) and try again.")
                return
            if csv_field2_var=='':
                mb.showwarning("Warning",
                               "The Sunburster visualization function requires a value for 'Select csv file field.'\n\nPlease, select a value and try again.")
                return
            # interest pass a list [] of labels embedded in the filename, e.g. Book1, Book2, ... or Chinese, Arabian,...
            interest = []
            temp_interest=[]
            interest = filename_label_var.split(', ')
            for i in range(len(interest)):
                temp_interest.append(interest[i].lstrip())
            # label is a string that has the header field in the csv file to be used for display
            label=csv_field2_var
            charts_Sunburster_util.Sunburster(inputFilename, case_sensitive_var, temp_interest, label, int_K_sent_begin_var, int_K_sent_end_var, split_var)

        if openOutputFiles and len(filesToOpen) > 0:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            Gephi_var.get(),
                            csv_file_field_list,
                            dynamic_network_field_var.get(),
                            interactive_Sunburster_var.get(),
                            filename_label_var.get(),
                            csv_field2_var.get(),
                            K_sent_begin_var.get(),
                            K_sent_end_var.get(),
                            split_var.get(),
                            interactive_time_mapper_var.get())

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
config_input_output_numeric_options=[3,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)
window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

def clear(e):
    reset()
    Gephi_var.set(0)
    interactive_Sunburster_var.set(0)
    case_sensitive_var.set(0)
    case_sensitive_checkbox.configure(text="Case sensitive")
    filename_label_var.set('')
    csv_field2_var.set('')
    K_sent_begin_var.set('')
    K_sent_end_var.set('')
    K_sent_begin.configure(state='disabled')
    K_sent_end.configure(state='disabled')
    split_var.set(0)
    split_checkbox.configure(state='disabled')
    interactive_time_mapper_var.set(0)
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)


Gephi_var = tk.IntVar()
selected_csv_file_fields_var = tk.StringVar()

csv_field_var = tk.StringVar()
dynamic_network_field_var = tk.StringVar()
interactive_Sunburster_var = tk.IntVar()
case_sensitive_var = tk.IntVar()
filename_label_var = tk.StringVar()
csv_field2_var = tk.StringVar()
K_sent_begin_var = tk.StringVar()
K_sent_end_var = tk.StringVar()
split_var = tk.IntVar()
interactive_time_mapper_var = tk.IntVar()

csv_file_field_list = []
menu_values = []

Excel_button = tk.Button(window, text='Open Excel GUI', width=GUI_IO_util.select_file_directory_button_width, height=1,
                               command=lambda: call("python charts_Excel_main.py", shell=True))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               Excel_button)

GIS_button = tk.Button(window, text='Open GIS GUI', width=GUI_IO_util.select_file_directory_button_width, height=1,
                               command=lambda: call("python GIS_main.py", shell=True))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               GIS_button)

HTML_button = tk.Button(window, text='Open HTML annotator GUI', width=GUI_IO_util.select_file_directory_button_width, height=1,
                               command=lambda: call("python html_annotator_main.py", shell=True))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               HTML_button)

wordcloud_button = tk.Button(window, text='Open wordcloud GUI', width=GUI_IO_util.select_file_directory_button_width, height=1,
                               command=lambda: call("python wordclouds_main.py", shell=True))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               wordcloud_button)
Gephi_var.set(0)
Gephi_checkbox = tk.Checkbutton(window, text='Visualize relations in a Gephi network graph', variable=Gephi_var,
                                    onvalue=1)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               Gephi_checkbox)

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

# def changed_filename(tracedInputFile):
#     menu_values = []
#     if tracedInputFile != '':
#         nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(tracedInputFile)
#         if nColumns == 0 or nColumns == None:
#             return False
#         if IO_csv_util.csvFile_has_header(tracedInputFile) == False:
#             menu_values = range(1, nColumns + 1)
#         else:
#             data, headers = IO_csv_util.get_csv_data(tracedInputFile, True)
#             menu_values = headers
#     else:
#         menu_values.clear()
#         return
#     m1 = select_csv_field_menu["menu"]
#     m2 = dynamic_network_field_menu["menu"]
#     m1.delete(0, "end")
#     m2.delete(0, "end")
#
#     for s in menu_values:
#         m1.add_command(label=s, command=lambda value=s: csv_field_var.set(value))
#         m2.add_command(label=s, command=lambda value=s: dynamic_network_field_var.set(value))
#
#     m3 = select_csv_field2_menu["menu"]
#     m3.delete(0, "end")
#
#     for s in menu_values:
#         m3.add_command(label=s, command=lambda value=s: csv_field2_var.set(value))
#
#     clear("<Escape>")
#
select_csv_field_lb = tk.Label(window, text='Select csv file field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               select_csv_field_lb, True)

select_csv_field_menu = tk.OptionMenu(window, csv_field_var, *menu_values)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_select_csv_field_menu_pos, y_multiplier_integer,
                                   select_csv_field_menu,
                                   True, False, True, False, 90, GUI_IO_util.visualization_select_csv_field_menu_pos,
                                   "Select the three fields to be used for the network graph in the order node1, edge, node2 (e.g., SVO)")

GUI_util.inputFilename.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))

select_csv_field_dynamic_network_lb = tk.Label(window, text='Select csv file field for dynamic network graph')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_select_csv_field_dynamic_network_lb_pos, y_multiplier_integer,
                                               select_csv_field_dynamic_network_lb, True)

dynamic_network_field_menu = tk.OptionMenu(window, dynamic_network_field_var, *menu_values)
dynamic_network_field_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_dynamic_network_field_pos, y_multiplier_integer,
                                   dynamic_network_field_menu,
                                   True, False, True, False, 90, GUI_IO_util.visualization_select_csv_field_dynamic_network_lb_pos,
                                   "Select the field to be used for a dynamic network graph (e.g., Sentence ID) if you wish to compute a dynamic network graph")

def display_selected_csv_fields():
    if csv_field_var.get() != '' and not csv_field_var.get() in csv_file_field_list:
        csv_file_field_list.append(csv_field_var.get())
        # select_csv_field_menu.configure(state='disabled')
    else:
        mb.showwarning(title='Warning',
                       message='The option "' + csv_field_var.get() + '" has already been selected. Selection ignored.\n\nYou can see your current selections by clicking the Show button.')
        select_csv_field_menu.configure(state='normal')
    # if dynamic_network_field_var.get() != '' and not dynamic_network_field_var.get() in csv_file_field_list:
    #     csv_file_field_list.append(dynamic_network_field_var.get())
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
                                   True, False, True, False, 90, GUI_IO_util.visualization_select_csv_field_dynamic_network_lb_pos,
                                   "Click on the + button to add a selected csv field to the list of Gephy parameters (edge1, node, edge2)")

reset_button = tk.Button(window, text='Reset', width=GUI_IO_util.reset_button_width,height=1,state='disabled',command=lambda: reset())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_reset_button_pos, y_multiplier_integer,
                                   reset_button,
                                   True, False, True, False, 90, GUI_IO_util.visualization_select_csv_field_dynamic_network_lb_pos,
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
                                   False, False, True, False, 90, GUI_IO_util.visualization_select_csv_field_dynamic_network_lb_pos,
                                   "Click on the Show button to display the list of currently selected csv fields")

def activate_csv_fields_selection(comingFromPlus=False):
    if csv_field_var.get() != '':
        if comingFromPlus:
            select_csv_field_menu.config(state='normal')
        else:
            select_csv_field_menu.config(state='disabled')
        add_button.config(state='normal')
        reset_button.config(state='normal')
        show_button.config(state='normal')
        if len(csv_file_field_list) == 3:
            select_csv_field_menu.configure(state='disabled')
            dynamic_network_field_menu.config(state='normal')
            mb.showwarning(title='Warning', message='The "Select csv file field" has been disabled. You have selected the 3 fields required by Gephi for node1, edge, node2.\n\nPress the "Show" button to display your selection. Press the "Reset" button to clear your selection and start again.')
    else:
        select_csv_field_menu.config(state='normal')
        dynamic_network_field_menu.config(state='normal')
        reset_button.config(state='disabled')
        show_button.config(state='disabled')
csv_field_var.trace('w', callback = lambda x,y,z: activate_csv_fields_selection())
dynamic_network_field_var.trace('w', callback = lambda x,y,z: activate_csv_fields_selection())

# activate_csv_fields_selection()

interactive_Sunburster_checkbox = tk.Checkbutton(window, text='Visualize data in interactive Sunburster graph', variable=interactive_Sunburster_var,
                                    onvalue=1)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               interactive_Sunburster_checkbox)

case_sensitive_var.set(0)
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
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_filename_label_lb_pos,
                                               y_multiplier_integer, filename_label_lb, True)

filename_label_var.set('')
filename_label = tk.Entry(window, state='disabled', textvariable=filename_label_var, width=GUI_IO_util.widget_width_medium)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_filename_label_pos, y_multiplier_integer,
                                   filename_label,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Enter the comma-separated label/part of a filename to be used to sample the corpus for visualization (e.g., Book1, Book2 in Harry Potter_Book1_1, Harry Potter_Book2_3, ...)")


select_csv_field2_lb = tk.Label(window, text='Select csv file field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_csv_field2_lb_pos, y_multiplier_integer,
                                               select_csv_field2_lb, True)

select_csv_field2_menu = tk.OptionMenu(window, csv_field2_var, *menu_values)
select_csv_field2_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_select_csv_field2_menu_pos, y_multiplier_integer,
                                   select_csv_field2_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_K_sent_end_pos,
                                   "Select the csv file field to be used to visualize specific data (e.g., 'Sentiment score' in a sentiment analysis csv output file")

K_sent_begin_var.set('')
K_sent_begin_lb = tk.Label(window, text='Begin K sentences')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,
                                               y_multiplier_integer, K_sent_begin_lb, True)

K_sent_begin = tk.Entry(window, state='disabled', textvariable=K_sent_begin_var, width=3)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_K_sent_begin_pos, y_multiplier_integer,
                                   K_sent_begin,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Enter the number of sentences at the beginning of each document to be used to visualize differences in the data")

K_sent_end_var.set('')
K_sent_end_lb = tk.Label(window, text='End K sentences')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_K_sent_end_lb_pos,
                                               y_multiplier_integer, K_sent_end_lb, True)
K_sent_end = tk.Entry(window, state='disabled',textvariable=K_sent_end_var, width=3)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_K_sent_end_pos, y_multiplier_integer,
                                   K_sent_end,
                                   True, False, True, False, 90, GUI_IO_util.visualization_K_sent_end_lb_pos,
                                   "Enter the number of sentences at the end of each document to be used to visualize differences in the data")

split_var.set(0)
split_checkbox = tk.Checkbutton(window, state='disabled',text='Split documents in equal halves', variable=split_var,
                                    onvalue=1)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_split_pos, y_multiplier_integer,
                                   split_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.visualization_split_pos,
                                   "Tick the checkbox if you wish to visualize differences in the data by splitting each document in two halves")


def activate_options(*args):
    if interactive_Sunburster_var.get():
        case_sensitive_checkbox.configure(state='normal')
        filename_label.configure(state='normal')
        K_sent_begin.configure(state='normal')
        K_sent_end.configure(state='normal')
        select_csv_field2_menu.configure(state='normal')
        split_checkbox.configure(state='normal')
    else:
        case_sensitive_checkbox.configure(state='disabled')
        filename_label.configure(state='disabled')
        K_sent_begin.configure(state='disabled')
        K_sent_end.configure(state='disabled')
        select_csv_field2_menu.configure(state='disabled')
        split_checkbox.configure(state='disabled')
interactive_Sunburster_var.trace('w',activate_options)

def activate_visualization_options(*args):
    if (interactive_Sunburster_var.get()==False) or split_var.get():
        K_sent_begin_var.set('')
        K_sent_end_var.set('')
        K_sent_begin.configure(state='disabled')
        K_sent_end.configure(state='disabled')
    else:
        K_sent_begin.configure(state='normal')
        K_sent_end.configure(state='normal')
        if K_sent_begin_var.get() != '' or K_sent_end_var.get()  != '':
            split_checkbox.configure(state='disabled')
        else:
            split_checkbox.configure(state='normal')
split_var.trace('w',activate_visualization_options)
K_sent_begin_var.trace('w',activate_visualization_options)
K_sent_end_var.trace('w',activate_visualization_options)

interactive_time_mapper_var.set(0)
interactive_time_mapper_checkbox = tk.Checkbutton(window, text='Visualize time-dependent data in interactive graph', variable=interactive_time_mapper_var,
                                    onvalue=1)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               interactive_time_mapper_checkbox)

def changed_filename(tracedInputFile):
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
    m1 = select_csv_field_menu["menu"]
    m2 = dynamic_network_field_menu["menu"]
    m1.delete(0, "end")
    m2.delete(0, "end")

    for s in menu_values:
        m1.add_command(label=s, command=lambda value=s: csv_field_var.set(value))
        m2.add_command(label=s, command=lambda value=s: dynamic_network_field_var.set(value))

    m3 = select_csv_field2_menu["menu"]
    m3.delete(0, "end")

    for s in menu_values:
        m3.add_command(label=s, command=lambda value=s: csv_field2_var.set(value))

    clear("<Escape>")

changed_filename(GUI_util.inputFilename.get())

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
    resetAll = "\n\nPress the RESET button to clear all selected values, and start fresh."
    plusButton = "\n\nPress the + buttons, when available, to add a new field."
    # OKButton = "\n\nPress the OK button, when available, to accept the selections made, then press the RUN button to process the query."
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_CoNLL)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, click on the button to open the Excel GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, click on the button to open the GIS GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, click on the button to open the HTML annotator GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, click on the button to open the wordcloud GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to visualize a network graph in Gephi.\n\nOptions become available in succession.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Options become available in succession after the Gephi option is selected.\n\nThe first field selected is the first node; the second field selected is the edge; the third field selected is the second node.\n\nOnce all three fields have been selected, the widget 'Field to be used for dynamic network graphs' will become available. When available, select a field to be used for dynamic networks (e.g., the Sentence ID) or ignore the option if the network should not be dynamic." + resetAll)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to visualize data in an interactive Sunburster visual display.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, enter the comma-separated labels/parts of a filename to be used to separate fields in the filename (e.g., in the filename, Harry Potter_Book1_1, Harry Potter_Book2_3, ..., Harry Potter_Book4_1... you could enter Book1, Book3 to sample the files to be used for visualization.\n\nThe number of distinct labels/parts of filename should be small (e.g., the 7 Harry Potter books).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, enter the the number of sentences at the beginning and at the end of a document to be used to visualize specific sentences.\n\nTick the 'Split documents in equal halves' if you wish to visualize the data for the first and last half of the documents in your corpus, rather than for begin and end sentences.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to analyze time-dependent data in an interactive bar chart.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 script provides access to different GUIs to be used to visualize data (e.g., wordclouds) and network graphs via Gephi and different interactive charts via Sunburster and time mapper."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

mb.showwarning(title='Warning',
               message='The interactive visualization options for Sunburster and time mapper are under construction.\n\nPlease, check back soon for these great options.')

GUI_util.window.mainloop()
