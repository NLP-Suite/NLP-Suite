# written by Roberto April 2023

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"data_visualization_2_main.py",['os','tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_csv_util
import IO_files_util
import charts_util

def run(inputFilename, outputDir, openOutputFiles,
        visualizations_menu_var,
        csv_field_visualization_var,
        X_axis_var,
        csv_file_field_Y_axis_list,
        points_var,
        split_data_byCategory_var,
        csv_field_boxplot_var,
        csv_field_boxplot_color_var,
        csv_files_list,
        date_format_var,
        time_var,
        cumulative_var):

    # print(inputFilename, outputDir, openOutputFiles,
    #     visualizations_menu_var,
    #     csv_field_visualization_var,
    #     X_axis_var,
    #     csv_field_Y_axis_list,
    #     points_var,
    #     split_data_byCategory_var,
    #     csv_field_boxplot_var,
    #     csv_field_boxplot_color_var,
    #     csv_files_list,
    #     date_format_var,
    #     time_var,
    #     cumulative_var)

    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    else:
        config_filename = scriptName.replace('main.py', 'config.csv')

    filesToOpen = []

    outputFiles = ''

    if not inputFilename.endswith('csv'):
        mb.showwarning(title='Warning',
                       message='The visualization algorithms require a "csv file field for visualization" variable.\n\nPlease, use the dropdown menu to select a field for anylysis and try again.')
        return

    if extra_GUIs_var==False and csv_field_visualization_var == '':
        mb.showwarning("Warning",
                       "No csv file field to be used for visualization has been selected.\n\nPlease, use the dropdown menu of the 'csv file field for visualization' widget to select the desired field and try again.")
        return

    if extra_GUIs_var==False and visualizations_menu_var=='':
        mb.showwarning(title="Warning",
                       message="No visualization option has been selected.\n\nPlease, use the dropdown menu of the 'Visualization options' widget to select the desired option and try again.")
        return

# Excel/Plotly charts --------------------------------------------------------------------------------
    if 'Excel' in visualizations_menu_var or 'Plotly' in visualizations_menu_var:

        if 'bar' in GUI_util.charts_type_options_widget.get().lower() or 'line' in GUI_util.charts_type_options_widget.get().lower():
            if X_axis_var=='' and len(csv_file_field_Y_axis_list) < 1:
                mb.showwarning(title='Warning',message='A '+str(GUI_util.charts_type_options_widget.get().lower()+' chart requires ONE X-axis variable and AT LEAST ONE Y-axis variable.\n\nPlease, select the expected number of variables and try again.'))
                return
        if 'scatter' in GUI_util.charts_type_options_widget.get().lower():
            if len(csv_file_field_Y_axis_list) < 1:
                mb.showwarning(title='Warning',message='A '+str(GUI_util.charts_type_options_widget.get().lower()+' chart requires at least TWO Y-axis variables.\n\nPlease, select the expected number of variables and try again.'))
                return
        if 'bubble' in GUI_util.charts_type_options_widget.get().lower() or 'radar' in GUI_util.charts_type_options_widget.get().lower():
            if len(csv_file_field_Y_axis_list) < 3:
                mb.showwarning(title='Warning',message='A '+str(GUI_util.charts_type_options_widget.get().lower()+' chart requires at least THREE Y-axis variables.\n\nPlease, select the expected number of variables and try again.'))
                return

        columns_to_be_plotted_xAxis=[]
        headers = IO_csv_util.get_csvfile_headers(inputFilename)
        col_num = IO_csv_util.get_columnNumber_from_headerValue(headers, csv_field_visualization_var, inputFilename)

        columns_to_be_plotted_yAxis=[[col_num,col_num]]
        count_var=1
        chart_type_list = [GUI_util.charts_type_options_widget.get().split(' ')[0]]
        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, inputFilename, outputDir,
                                                        outputFileLabel='',
                                                        chartPackage=GUI_util.charts_package_options_widget.get(),
                                                        dataTransformation=GUI_util.data_transformation_options_widget.get(),
                                                        chart_type_list=chart_type_list,
                                                        chart_title="Frequency Distribution of " + csv_field_visualization_var,
                                                        column_xAxis_label_var=csv_field_visualization_var,
                                                        hover_info_column_list=[],
                                                        count_var=count_var,
                                                        complete_sid=False, csv_field_Y_axis_list=csv_file_field_Y_axis_list, X_axis_var = X_axis_var)  # TODO to be changed
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)


# boxplots --------------------------------------------------------------------------------

    if 'Boxplots' in visualizations_menu_var:
        if points_var == '':
            mb.showwarning(title='Warning', message='The "Boxplots" option requires a "Data points" variable.\n\nPlease, use the dropdown menu to select a "Data points" option and try again.')
            return

        if split_data_byCategory_var and csv_field_boxplot_var=='':
            mb.showwarning(title='Warning',
                           message='The "Split data by category" Boxplots option requires a second CATEGORICAL csv file field for processing.\n\nPlease, use the dropdown menu to select the csv file field and try again.')
            return

        outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir,
                                                                 '.html', 'boxplot')
        # You cannot keep it as float inside the csv. The csv will treat everything as strings.
        # https://stackoverflow.com/questions/65393774/writing-floats-into-a-csv-file-but-floats-become-a-string
        outputfilename = charts_util.boxplot(inputFilename, outputFilename, csv_field_visualization_var,
                                    points_var, split_data_byCategory_var, csv_field_boxplot_var, csv_field_boxplot_color_var) #, points_var, color=None)
        if outputfilename!='':
            filesToOpen.append(outputfilename)

# comparative bar charts --------------------------------------------------------------------------------

    if 'Comparative' in visualizations_menu_var:
        if len(csv_files_list) < 2:
            mb.showwarning(title='Warning', message='The "Comparative bar charts" option requires a list of at least two csv files in input.\n\nPlease, use the + button to add multiple csv files and try again.')
            return
        # datalist list of csv files used
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir,
                                                                 '.html', 'multiplebar')
        ntopchoices = 20 # Must add to GUI
        outputfilename = charts_util.multiple_barchart(csv_files_list,outputFilename,csv_field_visualization_var,ntopchoices)
        if outputfilename!='':
            filesToOpen.append(outputfilename)

# time_mapper --------------------------------------------------------------------------------

    if 'Time' in visualizations_menu_var:
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir,
                                                                 '.html', 'timeMapper')
        monthly = False
        yearly = False
        if time_var == 'Monthly':
            monthly = True
        elif time_var == 'Yearly':
            yearly = True

        # import timechart_util
        # outputFiles = charts_util.timeline(inputFilename, outputFilename, csv_field_boxplot_color_var, date_format_var, cumulative_var, monthly, yearly)
        outputFiles = charts_util.timechart(inputFilename, outputFilename, csv_field_visualization_var, date_format_var,
                                            cumulative_var, monthly, yearly)

        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    if openOutputFiles and len(filesToOpen) > 0:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            visualizations_menu_var.get(),
                            csv_field_visualization_var.get(),
                            X_axis_var.get(),
                            csv_file_field_Y_axis_list,
                            points_var.get(),
                            split_data_byCategory_var.get(),
                            csv_field_boxplot_var.get(),
                            csv_field_boxplot_color_var.get(),
                            csv_files_list,
                            date_format_var.get(),
                            time_var.get(),
                            cumulative_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=520, # height at brief display
                             GUI_height_full=560, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Basic Visualization Tools: Boxplots, Comparative Bar Charts'
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

extra_GUIs_var = tk.IntVar()
extra_GUIs_menu_var = tk.StringVar()

visualizations_menu_var = tk.StringVar()

Y_axis_var = tk.StringVar()

csv_field_visualization_var = tk.StringVar()

split_data_byCategory_var = tk.IntVar()
use_numerical_variable_var = tk.IntVar()
csv_field_boxplot_var = tk.StringVar()

date_format_var = tk.StringVar()
time_var = tk.StringVar()
cumulative_var = tk.IntVar()

csv_file_field_Y_axis_list=[]
csv_files_list = []
file_menu_values = []
menu_values = []
error = False
csv_field_visualization_var_SV = ''

def clear(e):
    extra_GUIs_var.set(0)
    extra_GUIs_menu_var.set('')
    visualizations_menu_var.set('Excel/Plotly charts')
    X_axis_var.set('')
    Y_axis_var.set('')
    csv_files_list.clear()
    csv_field_visualization_var.set('')
    csv_field_boxplot_var.set('')
    points_var.set('')
    split_data_byCategory_var.set(0)
    # activate_split_options()
    csv_field_boxplot_color_var.set('')
    process_csv_file_menu(inputFilename.get())
    date_format_menu.configure(state='disabled')
    csv_file_field_Y_axis_list.clear()
window.bind("<Escape>", clear)


extra_GUIs_var.set(0)
extra_GUIs_checkbox = tk.Checkbutton(window, text='GUIs available for more analyses ', variable=extra_GUIs_var, onvalue=1, offvalue=0, command=lambda: open_GUI())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,extra_GUIs_checkbox,True)

extra_GUIs_menu_var.set('')
extra_GUIs_menu = tk.OptionMenu(window,extra_GUIs_menu_var,'Visualize categorical and network data: Gephi, Sankey, Colormap, Sunburst, Treemap (Open GUI)', 'Texts to maps (Open GUI)', 'Google Earth Pro (Open GUI)', 'HTML annotator (Open GUI)', 'Wordclouds (Open GUI)')
extra_GUIs_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   extra_GUIs_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select other related types of analysis you wish to perform" \
                                    "\nThe selected GUI will open without having to press RUN")



def open_GUI(*args):
    if extra_GUIs_var:
        extra_GUIs_menu.configure(state='normal')
    if 'Excel' in extra_GUIs_menu_var.get():
        call("python charts_Excel_main.py", shell=True)
    elif 'Google' in extra_GUIs_menu_var.get():
        call("python GIS_main.py", shell=True)
    elif 'Texts to maps' in extra_GUIs_menu_var.get():
        call("python GIS_main.py", shell=True)
    elif 'HTML' in extra_GUIs_menu_var.get():
        call("python html_annotator_main.py", shell = True)
    elif 'Visualize categorical' in extra_GUIs_menu_var.get():
        call("python data_visualization_1_main.py", shell=True)
    elif 'Wordclouds' in extra_GUIs_menu_var.get():
        call("python wordclouds_main.py", shell=True)
extra_GUIs_menu_var.trace('w',open_GUI)

if GUI_util.inputFilename.get() != '' and GUI_util.inputFilename.get()[-4:] == ".csv":
    nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(GUI_util.inputFilename.get())
    file_menu_values = [inputFilename.get()]
    if IO_csv_util.csvFile_has_header(GUI_util.inputFilename.get()) == False:
        menu_values = range(1, nColumns + 1)
    else:
        data, headers = IO_csv_util.get_csv_data(GUI_util.inputFilename.get(), True)
        menu_values = headers
else:
    nColumns = 0
    file_menu_values = " "
    menu_values = " "
if nColumns == -1:
    pass

csv_field_visualization_lb = tk.Label(window, text='csv file field for visualization (Y-axis)')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               csv_field_visualization_lb, True)

csv_field_visualization_menu = tk.OptionMenu(window, csv_field_visualization_var, *menu_values)
# csv_field_visualization_menu.configure(state='disabled')
# place widget with hover-over info
# visualization_csv_field_visualization_menu_pos
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   csv_field_visualization_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_filename_label_lb_pos,
                                   "Select the csv file field to be used for visualizing the chart\nBoxplots require a NUMERIC field; Comparative bar charts require a CATEGORICAL field")

#@@@
def check_selected_csv_file_field_Y_axis_list(main_Y_axis):
    global csv_field_visualization_var_SV
    if not 'Excel' in visualizations_menu_var.get():
        # csv_file_field_Y_axis_list.clear()
        return
    if csv_field_visualization_var.get()!='':
        # the next line does not work on Mac,
        #   so must take a convoluted way of making sure the same value is not added several times to csv_file_field_Y_axis_list
        # csv_field_visualization_menu.configure(state='disabled')
        if csv_field_visualization_var_SV=='':
            csv_field_visualization_var_SV=csv_field_visualization_var.get()
        else:
            if main_Y_axis:
                # remove the previously selected field from csv_file_field_Y_axis_list ONLY if coming from main Y-axis
                if csv_field_visualization_var_SV in str(', '.join(csv_file_field_Y_axis_list)):
                    csv_file_field_Y_axis_list.remove(csv_field_visualization_var_SV)
                csv_field_visualization_var_SV=''
    if main_Y_axis:
        field_value = csv_field_visualization_var.get() # main Y-axis, used for boxplots, comparative bar chhrts, time mapper
    else:
        field_value = Y_axis_var.get() # additional Y-axis used for Excel and Plotly
    if field_value =='':
        return
    if field_value in str(', '.join(csv_file_field_Y_axis_list)):
        mb.showwarning(title='Warning',
                       message='The option "' + field_value + '" has already been selected. Selection ignored.\n\nYou can see your current selections by using the dropdown menu.')
    else:
        csv_file_field_Y_axis_list.append(field_value)

csv_field_visualization_var.trace('w', lambda x, y, z: check_selected_csv_file_field_Y_axis_list(True))

visualization_basic_options_lb = tk.Label(window, text='Visualization options')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               visualization_basic_options_lb, True)


visualizations_menu_var.set('Excel/Plotly charts')
visualizations_menu = tk.OptionMenu(window, visualizations_menu_var, 'Boxplots','Comparative bar charts','Excel/Plotly charts','Time mapper')
# select_time_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   visualizations_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_filename_label_lb_pos,
                                   "Use the dropdown menu to select a visualization option for your data: Boxplots, Comparative bar charts, Excel/Plotly charts, Time mapper\nBoxplots require a NUMERIC field; Comparative bar charts require a CATEGORICAL field")

def check_selected_csv_files(selected_filename):
    file_accepted = True
    if selected_filename in csv_files_list:
        mb.showwarning(title='Warning',
                       message='The option "' + selected_filename + '" has already been selected. Selection ignored.\n\nYou can see your current selections by using the dropdown menu.')
        file_accepted = False
    return file_accepted

GUI_util.inputFilename.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))
# GUI_util.input_main_dir_path.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))

Excel_Plotly_lb = tk.Label(window, text='Excel/Plotly',foreground="red",font=("Courier", 12, "bold"))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   Excel_Plotly_lb,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The widgets on this line refer to the Excel/Plotly option only")

X_axis_lb = tk.Label(window, text='X-axis')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                               X_axis_lb, True)

X_axis_var = tk.StringVar()
X_axis_menu = tk.OptionMenu(window, X_axis_var, *file_menu_values)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu+70, y_multiplier_integer,
                                               X_axis_menu,
                                               True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 100,
                                               "Select the csv file field to be used as X-axis")

Y_axis_lb = tk.Label(window, text='Additional Y-axis')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_pop_up_text_widget, y_multiplier_integer,
                                               Y_axis_lb, True)

Y_axis_menu = tk.OptionMenu(window, Y_axis_var, *file_menu_values)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                               Y_axis_menu,
                                               True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 100,
                                               "Select the csv file field to be used as additional Y-axis (e.g., for multiple line charts). You will need to click the + button after selection")

# add another Y-axis
add_Y_axis = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1, command = lambda: check_selected_csv_file_field_Y_axis_list(False))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_coordinate+850,
                                               y_multiplier_integer,
                                               add_Y_axis, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "Click the + button to add another Y-axis variable")


def reset_csv_field_Y_axis_values():
    csv_file_field_Y_axis_list.clear()
    csv_field_visualization_menu.configure(state='normal')
    csv_field_visualization_var.set('')
    Y_axis_var.set('')

reset_Y_axis_button = tk.Button(window, text='Reset ', width=GUI_IO_util.reset_button_width, height=1, state='normal',
                                command=lambda: reset_csv_field_Y_axis_values())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_coordinate+890,
                                               y_multiplier_integer,
                                               reset_Y_axis_button, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "Click the Reset button to clear all previously selected csv files and start fresh")

def show_Y_axis_list():
    if len(csv_file_field_Y_axis_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected additional Y-axis variables.')
    else:
        mb.showwarning(title='Warning', message='The currently selected Y-axis variables are:\n\n' + ', '.join(csv_file_field_Y_axis_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

# , state='disabled'
show_Y_axis_button = tk.Button(window, text='Show', width=GUI_IO_util.show_button_width, height=1,
                                 command=lambda: show_Y_axis_list())
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+945, y_multiplier_integer,
                                             show_Y_axis_button,
                                             False, False, True, False,
                                             90, GUI_IO_util.WordNet_show_pos,
                                             "Click on the Show button to display the currently selected synsets")


boxplot_lb = tk.Label(window, text='Boxplot', foreground="red",font=("Courier", 12, "bold"))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   boxplot_lb,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The widgets on this line refer to the Boxplot option only")

points_lb = tk.Label(window, text='Data')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                               points_lb, True)

points_var = tk.StringVar()
points_menu = tk.OptionMenu(window, points_var, 'all', 'None', 'outliers')
# points_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu+70, y_multiplier_integer,
                                   points_menu,
                                   True, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select the amount of data points you want to visualize")


split_data_byCategory_checkbox = tk.Checkbutton(window, variable = split_data_byCategory_var, text='Split data by category',
                                onvalue=1, offvalue=0, command = lambda: activate_split_options()) #, command = lambda: activate_all_options())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_pop_up_text_widget, y_multiplier_integer,
                                   split_data_byCategory_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Tick the checkbox to visualize data split by selected csv file field values")

csv_field2_lb = tk.Label(window, text='csv file field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                               csv_field2_lb, True)

csv_field_boxplot_menu = tk.OptionMenu(window, csv_field_boxplot_var, *menu_values)
csv_field_boxplot_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+100, y_multiplier_integer,
                                   csv_field_boxplot_menu,
                                   True, False, True, False, 90, GUI_IO_util.visualization_K_sent_end_pos,
                                   "Select the csv file CATEGORICAL field along which to split the data\nrecommended, but not necessary; use field with few categories")

csv_field_boxplot_color_lb = tk.Label(window, text='csv file field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+850, y_multiplier_integer,
                                               csv_field_boxplot_color_lb, True)

csv_field_boxplot_color_var = tk.StringVar()
csv_field_boxplot_color_menu = tk.OptionMenu(window, csv_field_boxplot_color_var, *menu_values)
csv_field_boxplot_color_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+950, y_multiplier_integer,
                                   csv_field_boxplot_color_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_K_sent_end_pos,
                                   "Select the csv file CATEGORICAL field to be used for COLORING split categories\nrecommended, but not necessary; use field with few categories")

def activate_split_options(*args):
    if split_data_byCategory_var.get():
        csv_field_boxplot_menu.configure(state='normal')
        csv_field_boxplot_color_menu.configure(state='normal')
    else:
        csv_field_boxplot_var.set('')
        csv_field_boxplot_color_var.set('')
        csv_field_boxplot_menu.configure(state='disabled')
        csv_field_boxplot_color_menu.configure(state='disabled')
split_data_byCategory_var.trace('w',activate_split_options)
activate_split_options()

multiple_bar_lb = tk.Label(window, text='Bar charts',foreground="red",font=("Courier", 12, "bold"))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   multiple_bar_lb,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The widgets on this line refer to the comparative bar charts option only")

# add another file
add_file = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1,
                            command=lambda: add_csvFile(window, 'Select INPUT csv file',
                                                        [("csv files", "*.csv")]))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate,
                                               y_multiplier_integer,
                                               add_file, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "Click the + button to add another csv file (in addition to either the input csv file displayed in the I/O configuration or any other files already added)")

def reset_csv_files_values():
    csv_files_list.clear()
    process_csv_file_menu(inputFilename.get())

reset_file_button = tk.Button(window, text='Reset ', width=GUI_IO_util.reset_button_width, height=1, state='normal',
                                command=lambda: reset_csv_files_values())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate + 40,
                                               y_multiplier_integer,
                                               reset_file_button, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "Click the Reset button to clear all previously selected csv files and start fresh")


# setup a button to open Windows Explorer on the selected input directory
openInputFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                 command=lambda: IO_files_util.openFile(window,
                                                                        csv_file_var.get()))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,
                                               GUI_IO_util.open_TIPS_x_coordinate + 90,
                                               y_multiplier_integer,
                                               openInputFile_button, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_indented_indented_coordinate + 70, 'Open selected csv file')


select_csv_file_lb = tk.Label(window, text='Select csv file')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_pop_up_text_widget, y_multiplier_integer,
                                               select_csv_file_lb, True)

csv_file_var = tk.StringVar()
csv_file_menu = tk.OptionMenu(window, csv_file_var, *file_menu_values)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.setup_pop_up_text_widget+100, y_multiplier_integer,
                                               csv_file_menu,
                                               False, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 100,
                                               "The comparative bar charts visualization option requires multiple csv files in input.\nUse the dropdown menu to select a specific file that you can then open for inspection.")

# # setup a button to open Windows Explorer on the selected input directory
# openInputFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
#                                  command=lambda: IO_files_util.openFile(window,
#                                                                         csv_file_var.get()))
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,
#                                                GUI_IO_util.IO_configuration_menu,
#                                                y_multiplier_integer,
#                                                openInputFile_button, False, False, True, False, 90,
#                                                GUI_IO_util.IO_configuration_menu, 'Open selected csv file')
#


def add_csvFile(window, title, fileType):
    global y_multiplier_integer, outputDir
    initialFolder = GUI_util.output_dir_path.get()
    filePath = tk.filedialog.askopenfilename(title=title, initialdir=initialFolder, filetypes=fileType)
    if len(filePath) > 0:
        if check_selected_csv_files(filePath):
            process_csv_file_menu(filePath)

def process_csv_file_menu(InputFile):
    file_menu_values = []
    csv_files_list.append(InputFile)
    if len(csv_files_list) == 0:
        file_menu_values = ' '
    else:
        file_menu_values = csv_files_list

    m = csv_file_menu["menu"]
    m.delete(0, "end")

    for s in file_menu_values:
        m.add_command(label=s, command=lambda value=s: csv_file_var.set(value))

time_mapper_lb = tk.Label(window, text='Time mapper', foreground="red",font=("Courier", 12, "bold"))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   time_mapper_lb,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The widgets on this line refer to the time mapper option only")

# time_mapper_var.set(0)
# time_mapper_checkbox = tk.Checkbutton(window, text='Visualize temporal data', variable=time_mapper_var,
#                                     onvalue=1, command=lambda: activate_all_options())
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
#                                    time_mapper_checkbox,
#                                    False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
#                                    "Tick the checkbox if you wish to visualize data in a dynamic time mapper\nIn input the filenames under the 'Document' field in the csv file must contain date values\n"
#                                                "(e.g., /Users/me/Desktop/Janet Maslin_Living Centuries Apart_2014-12-12.txt)")

date_format_lb = tk.Label(window,text='Date format ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate,
                                               y_multiplier_integer, date_format_lb, True)
date_format_var.set('mm-dd-yyyy')
date_format_menu = tk.OptionMenu(window, date_format_var, 'mm-dd-yyyy', 'dd-mm-yyyy','yyyy-mm-dd','yyyy-dd-mm','yyyy-mm','yyyy')
date_format_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,
                                               GUI_IO_util.open_TIPS_x_coordinate+70,
                                               y_multiplier_integer,
                                               date_format_menu,
                                               True, False, False, False, 90,
                                               GUI_IO_util.visualization_K_sent_begin_pos,
                                               'Select the date type embedded in your filename')

select_time_lb = tk.Label(window, text='Timeline')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_pop_up_text_widget, y_multiplier_integer,
                                               select_time_lb, True)

time_var.set('Daily')
select_time_menu = tk.OptionMenu(window, time_var, 'Daily','Monthly','Yearly')
select_time_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_pop_up_text_widget+100, y_multiplier_integer,
                                   select_time_menu,
                                   True, False, True, False, 90, GUI_IO_util.setup_pop_up_text_widget+100,
                                   "Select the time option")

cumulative_var.set(0)
cumulative_checkbox = tk.Checkbutton(window, text='Cumulative', variable=cumulative_var,
                                    onvalue=1, offvalue=0)
cumulative_checkbox.configure(state='disabled')

# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.run_button_x_coordinate, y_multiplier_integer,
                                   cumulative_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox for a cumulative time chart showing the frequency of the chosen variable up until a current day/month/year rather than visualizing the frequency day/month/year by day/month/year")

# csv_field4_lb = tk.Label(window, text='csv file field')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_csv_field2_lb_pos, y_multiplier_integer,
#                                                csv_field4_lb, True)
#
# csv_field4_menu = tk.OptionMenu(window, csv_field_boxplot_color_var, *menu_values) # timemapper
# csv_field4_menu.configure(state='disabled')
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.visualization_csv_field2_menu_pos, y_multiplier_integer,
#                                    csv_field4_menu,
#                                    False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
#                                    "Select the csv file field to be used to visualize specific data\nThe field must be categorical rather than numeric (e.g., 'Sentiment label', rather than 'Sentiment score', in a sentiment analysis csv output file)")

def changed_filename(tracedInputFile):
    global error
    if tracedInputFile.endswith('.csv'):
        error = False
    else:
        error = True

    menu_values = []
    if tracedInputFile != '' and os.path.basename(tracedInputFile)[-4:] == ".csv":
        process_csv_file_menu(tracedInputFile)
        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(tracedInputFile)

        if nColumns == 0 or nColumns == None:
            return False
        if IO_csv_util.csvFile_has_header(tracedInputFile) == False:
            menu_values = range(1, nColumns + 1)
        else:
            data, headers = IO_csv_util.get_csv_data(tracedInputFile, True)
            menu_values = headers

# main Y-axis
        m1 = csv_field_visualization_menu["menu"]
        m1.delete(0, "end")

        for s in menu_values:
            m1.add_command(label=s, command=lambda value=s: csv_field_visualization_var.set(value))
# X-axis

        m2 = X_axis_menu["menu"]
        m2.delete(0, "end")

        for s in menu_values:
            m2.add_command(label=s, command=lambda value=s: X_axis_var.set(value))

# additional Y-axis

        m3 = Y_axis_menu["menu"]
        m3.delete(0, "end")

        for s in menu_values:
            m3.add_command(label=s, command=lambda value=s: Y_axis_var.set(value))

# boxplot
        m4 = csv_field_boxplot_menu["menu"]
        m4.delete(0, "end")

        for s in menu_values:
            m4.add_command(label=s, command=lambda value=s: csv_field_boxplot_var.set(value))

# boxplot color

        m5 = csv_field_boxplot_color_menu["menu"]
        m5.delete(0, "end")

        for s in menu_values:
            m5.add_command(label=s, command=lambda value=s: csv_field_boxplot_color_var.set(value))

    else:
        csv_files_list.clear()
        menu_values.clear()

def activate_all_options(*args):
    if error:
            return

    # Excel/Plotly
    X_axis_menu.configure(state='disabled')
    Y_axis_menu.configure(state='disabled')
    add_Y_axis.configure(state='disabled')
    reset_Y_axis_button.configure(state='disabled')
    show_Y_axis_button.configure(state='disabled')

    # boxplot
    points_menu.configure(state='disabled')
    split_data_byCategory_checkbox.configure(state='disabled')
    csv_field_boxplot_menu.configure(state='disabled')
    csv_field_boxplot_color_menu.configure(state='disabled')

    # comparative bar charts
    add_file.configure(state='disabled')
    reset_file_button.configure(state='disabled')
    openInputFile_button.configure(state='disabled')
    csv_file_menu.configure(state='disabled')

    # time mapper
    date_format_menu.configure(state='disabled')
    select_time_menu.configure(state='disabled')
    cumulative_checkbox.configure(state='disabled')

    if 'plotly' in visualizations_menu_var.get().lower():
        X_axis_menu.configure(state='normal')
        Y_axis_menu.configure(state='normal')
        add_Y_axis.configure(state='normal')
        reset_Y_axis_button.configure(state='normal')
        show_Y_axis_button.configure(state='normal')

    if 'boxplot' in visualizations_menu_var.get().lower():
        points_menu.configure(state='normal')
        split_data_byCategory_checkbox.configure(state='normal')
        csv_field_boxplot_menu.configure(state='normal')
        csv_field_boxplot_color_menu.configure(state='normal')

    if 'comparative' in visualizations_menu_var.get().lower():
        add_file.configure(state='normal')
        reset_file_button.configure(state='normal')
        openInputFile_button.configure(state='normal')
        csv_file_menu.configure(state='normal')

    if 'time' in visualizations_menu_var.get().lower():
        date_format_menu.configure(state='normal')
        select_time_menu.configure(state='normal')
        cumulative_checkbox.configure(state='normal')

activate_all_options()

visualizations_menu_var.trace('w',activate_all_options)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {"Word clouds":"TIPS_NLP_Wordclouds Visualizing word clouds.pdf",
               "Wordle":"TIPS_NLP_Wordclouds Wordle.pdf",
               "Tagxedo":"TIPS_NLP_Wordclouds Tagxedo.pdf",
               "Tagcrowd":"TIPS_NLP_Wordclouds Tagcrowd.pdf",
               'Excel charts': 'TIPS_NLP_Excel Charts.pdf',
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
               'Network Graphs (via Gephi)': 'TIPS_NLP_Gephi network graphs.pdf',
               "Specialized visualization tools 1":"TIPS_NLP_Specialized visualization tools 1.pdf",
               "Specialized visualization tools 2":"TIPS_NLP_Specialized visualization tools 2.pdf",
               'csv files - Problems & solutions': 'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf'}

TIPS_options='Specialized visualization tools 1', 'Specialized visualization tools 2', 'Word clouds', 'Tagcrowd', 'Tagxedo', 'Wordle', 'Excel smoothing data series', 'Network Graphs (via Gephi)', 'csv files - Problems & solutions', 'Statistical measures'

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

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         'Please, tick the \'GUIs available\' checkbox if you wish to see and select the range of other available tools suitable for data visualization.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, select the csv file field to be used for visualization.\n\nA NUMERIC field is required for the 'Boxplot' option and a CATEGORICAL field for the 'Comparative bar charts' option.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select type of visual chart to be used for visualization.")
    # Excel/Plotly
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Use the widgets in this line to set the parameters required by The Excel/Plotly charts option." \
                        "\n\nThe Excel/Plotly charts require an X-axis field and, perhaps, additional Y-axis fields (e.g., for multiple series line charts or bar charts).")
    # boxplot
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Use the widgets in this line to set the parameters required by the 'Boxplot' option." \
                            "\n\nUse the dropdown menu to select the type of data points to be processed. Tick the 'Split data by category' checkbox if you want to use a file field to split and/or color the charts by the value of a csv file field.")
    # comparative bar charts
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Use the widgets in this line to set the parameters required by the 'Comparative bar charts' option." \
                            "\n\nAT LEAST TWO CSV FILES ARE REQUIRED FOR THE COMPARATIVE BAR CHARTS OPTION.\n\nClick on the + button to add a new csv file (in addition to either the input csv file displayed in the I/O configuration or any other files already added).\nClick on the Reset button to clear the current selection and start over.\nUse the dropdown menu to select a specific csv file that you can then open with the Open button.")
    # time mapper
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Use the widgets in this line to set the parameters required by the 'Time mapper' option.\n\nYou can use the Time mapper to analyze time-dependent data in an interactive bar chart." \
            "\n\nTHE TIME MAPPER ALGORITHM REQUIRES A DATE FIELD EMBEDDED IN THE FILENAME. YOU CAN SETUP DATES EMBEDDED IN FILENAMES BY CLICKING THE 'Setup INPUT/OUTPUT configuration' WIDGET AT THE TOP OF THE ALGORITHM GUI THAT HAS PRODUCED THE CSV FILE USED HERE IN INPUT AND THEN TICKING THE CHECKBOXS 'Filename embeds multiple items' AND 'Filename embeds date' WHEN THE NLP_setup_IO_main GUI OPENS." \
            "\n\nUse the dropdown menu to select the 'Date format' of the date embedded in the filenames (the filenames are listed in the csv file under the field 'Document').\nUse the dropdown menu to select the preferred 'Timeline' (daily, monthly, or yearly).\nClick on the 'Cumulative' checkbox to visualize data cumulatively.")
    # Cumulative, for a time chart showing the frequency of the chosen variable up until a current day rather than visualizing the frequency day by day" \
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 script provides access to different types of data visualization: boxplots and comparative bar charts.\n\nIn OUTPUT the algorithms produce different types of html charts."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

activate_all_options()

GUI_util.window.mainloop()
