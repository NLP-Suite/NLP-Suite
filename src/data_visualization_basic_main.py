# written by Roberto April 2023

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"data_visualization_basic_main.py",['os','tkinter'])==False:
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
        csv_field_var,
        points_var,
        split_data_byCategory_var,
        csv_field2_var,
        csv_field3_var,
        csv_files_list):

    filesToOpen = []

    chart_outputFilename = ''

    if csv_field_var == '':
        mb.showwarning(title='Warning',
                       message='The visualization algorithms require a "csv file field for visualization" variable.\n\nPlease, use the dropdown menu to select a field for anylysis and try again.')
        return

    if 'Boxplots' in visualizations_menu_var:
        if points_var == '':
            mb.showwarning(title='Warning', message='The "Boxplots" option requires a "Data points" variable.\n\nPlease, use the dropdown menu to select a "Data points" option and try again.')
            return

        outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir,
                                                                 '.html', 'boxplot')
        outputfilename = charts_util.boxplot(inputFilename, outputFilename, csv_field_var,
                                    points_var, split_data_byCategory_var, csv_field2_var, csv_field3_var) #, points_var, color=None)
        if outputfilename!='':
            filesToOpen.append(outputfilename)

    if 'Comparative' in visualizations_menu_var:
        if len(csv_files_list) < 2:
            mb.showwarning(title='Warning', message='The "Comparative bar charts" option requires a list of at least two csv files in input.\n\nPlease, use the + button to add multiple csv files and try again.')
            return
        # datalist list of csv files used
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir,
                                                                 '.html', 'multiplebar')
        ntopchoices = 20 # Must add to GUI
        outputfilename = charts_util.multiple_barchart(csv_files_list,outputFilename,csv_field_var,ntopchoices)
        if outputfilename!='':
            filesToOpen.append(outputfilename)


    if openOutputFiles and len(filesToOpen) > 0:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            visualizations_menu_var.get(),
                            csv_field_var.get(),
                            points_var.get(),
                            split_data_byCategory_var.get(),
                            csv_field2_var.get(),
                            csv_field3_var.get(),
                            csv_files_list)

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
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = scriptName.replace('_main.py', '_config.csv')

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
    reset_all_values()
window.bind("<Escape>", clear)

open_GUI_var = tk.StringVar()
visualizations_menu_var = tk.StringVar()

csv_field_var = tk.StringVar()

use_numerical_variable_var = tk.IntVar()
csv_field2_var = tk.StringVar()

csv_files_list = []
file_menu_values = []
menu_values = []
error = False

open_GUI_lb = tk.Label(window, text='Open special visualization options GUI')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               open_GUI_lb, True)

open_GUI_menu = tk.OptionMenu(window, open_GUI_var, 'Excel charts (Open GUI)','Geographic maps (Open GUI)','HTML annotator (Open GUI)', 'Visualize categorical, network, temporal data', 'Wordclouds (Open GUI)')
# open_GUI_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_pop_up_text_widget, y_multiplier_integer,
                                   open_GUI_menu,
                                   False, False, True, False, 90, GUI_IO_util.open_TIPS_x_coordinate,
                                   'Open a GUI for special visualization options: Excel charts, geographic maps, HTML, wordclouds')

def open_GUI(*args):
    if 'Excel' in open_GUI_var.get():
        call("python charts_Excel_main.py", shell=True)
    elif 'Geographic' in open_GUI_var.get():
        call("python GIS_main.py", shell=True)
    elif 'HTML' in open_GUI_var.get():
        call("python html_annotator_main.py", shell = True)
    elif 'Visualize categorical, network, temporal data' in open_GUI_var.get():
        call("python data_visualization_main.py", shell=True)
    elif 'Wordclouds' in open_GUI_var.get():
        call("python wordclouds_main.py", shell=True)
open_GUI_var.trace('w',open_GUI)

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

csv_field_lb = tk.Label(window, text='csv file field for visualization')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               csv_field_lb, True)

csv_field_menu = tk.OptionMenu(window, csv_field_var, *menu_values)
# csv_field_menu.configure(state='disabled')
# place widget with hover-over info
# visualization_csv_field_menu_pos
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   csv_field_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_filename_label_lb_pos,
                                   "Select the csv file field to be used for visualizing the chart\nBoxplots require a NUMERIC field; Comparative bar charts require a CATEGORICAL field")

visualization_basic_options_lb = tk.Label(window, text='Visualization options')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               visualization_basic_options_lb, True)


visualizations_menu_var.set('Boxplots')
visualizations_menu = tk.OptionMenu(window, visualizations_menu_var, 'Boxplots','Comparative bar charts')
# select_time_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   visualizations_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_filename_label_lb_pos,
                                   "Use the dropdown menu to select a visualization option for your data: Boxplots, Comparative bar charts\nBoxplots require a NUMERIC field; Comparative bar charts require a CATEGORICAL field")

def check_selected_csv_files(selected_filename):
    file_accepted = True
    if selected_filename in csv_files_list:
        mb.showwarning(title='Warning',
                       message='The option "' + selected_filename + '" has already been selected. Selection ignored.\n\nYou can see your current selections by using the dropdown menu.')
        file_accepted = False
    return file_accepted

GUI_util.inputFilename.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))
# GUI_util.input_main_dir_path.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))

boxplot_lb = tk.Label(window, text='Boxplot parameters')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   boxplot_lb,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The widgets on this line refer to the Boxplot option only")

points_lb = tk.Label(window, text='Data points')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_indented_coordinate, y_multiplier_integer,
                                               points_lb, True)

points_var = tk.StringVar()
points_menu = tk.OptionMenu(window, points_var, 'All points', 'no points', 'outliers only')
# points_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   points_menu,
                                   True, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select the amount of data points you want to visualize")


split_data_byCategory_var = tk.IntVar()
split_data_byCategory_checkbox = tk.Checkbutton(window, variable = split_data_byCategory_var, text='Split data by category',
                                onvalue=1, offvalue=0, command = lambda: activate_split_options()) #, command = lambda: activate_all_options())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+420, y_multiplier_integer,
                                   split_data_byCategory_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Tick the checkbox to visualize data split by selected csv file field values")

csv_field2_lb = tk.Label(window, text='csv file field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                               csv_field2_lb, True)

csv_field2_menu = tk.OptionMenu(window, csv_field2_var, *menu_values)
csv_field2_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+100, y_multiplier_integer,
                                   csv_field2_menu,
                                   True, False, True, False, 90, GUI_IO_util.visualization_K_sent_end_pos,
                                   "Select the csv file CATEGORICAL field along which to split the data\nrecommended, but not necessary; use field with few categories")

csv_field3_lb = tk.Label(window, text='csv file field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+850, y_multiplier_integer,
                                               csv_field3_lb, True)

csv_field3_var = tk.StringVar()
csv_field3_menu = tk.OptionMenu(window, csv_field3_var, *menu_values)
csv_field3_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+950, y_multiplier_integer,
                                   csv_field3_menu,
                                   False, False, True, False, 90, GUI_IO_util.visualization_K_sent_end_pos,
                                   "Select the csv file CATEGORICAL field to be used for COLORING split categories\nrecommended, but not necessary; use field with few categories")

def activate_split_options(*args):
    if split_data_byCategory_var.get():
        csv_field2_menu.configure(state='normal')
        csv_field3_menu.configure(state='normal')
    else:
        csv_field2_menu.configure(state='disabled')
        csv_field3_menu.configure(state='disabled')
split_data_byCategory_var.trace('w',activate_split_options())
activate_split_options()

multiple_bar_lb = tk.Label(window, text='Multiple bar charts parameters')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   multiple_bar_lb,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The widgets on this line refer to the multiple bar charts option only")

# add another file
add_file = tk.Button(window, text='+', width=2, height=1,
                            command=lambda: add_csvFile(window, 'Select INPUT csv file',
                                                        [("csv files", "*.csv")]))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_indented_coordinate,
                                               y_multiplier_integer,
                                               add_file, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "Click the + button to add another csv file")

def reset_all_values():
    open_GUI_var.set('')
    visualizations_menu_var.set('Boxplots')
    csv_files_list.clear()
    split_data_byCategory_var.set(0)
    activate_split_options()
    csv_field_var.set('')
    csv_field2_var.set('')
    csv_field3_var.set('')
    points_var.set('')
    process_csv_file_menu(inputFilename.get())

def reset_csv_files_values():
    csv_files_list.clear()
    process_csv_file_menu(inputFilename.get())

reset_button = tk.Button(window, text='Reset', width=5, height=1, state='normal',
                                command=lambda: reset_csv_files_values())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_indented_coordinate + 40,
                                               y_multiplier_integer,
                                               reset_button, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "Click the Reset button to clear all previously selected csv files and start fresh")

select_csv_file_lb = tk.Label(window, text='Select csv file')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu+80, y_multiplier_integer,
                                               select_csv_file_lb, True)

csv_file_var = tk.StringVar()
csv_file_menu = tk.OptionMenu(window, csv_file_var, *file_menu_values)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.setup_pop_up_text_widget, y_multiplier_integer,
                                               csv_file_menu,
                                               True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate + 100,
                                               "The multiple charts visualization option requires multiple csv files in input.\nUse the dropdown menu to select a specific file that you can then open for inspection.")

# setup a button to open Windows Explorer on the selected input directory
openInputFile_button = tk.Button(window, width=3, text='',
                                 command=lambda: IO_files_util.openFile(window,
                                                                        csv_file_var.get()))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,
                                               GUI_IO_util.IO_configuration_menu,
                                               y_multiplier_integer,
                                               openInputFile_button, False, False, True, False, 90,
                                               GUI_IO_util.IO_configuration_menu, 'Open selected csv file')



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

        m1 = csv_field_menu["menu"]
        m1.delete(0, "end")

        for s in menu_values:
            m1.add_command(label=s, command=lambda value=s: csv_field_var.set(value))

        m2 = csv_field2_menu["menu"]
        m2.delete(0, "end")

        for s in menu_values:
            m2.add_command(label=s, command=lambda value=s: csv_field2_var.set(value))

        m3 = csv_field3_menu["menu"]
        m3.delete(0, "end")

        for s in menu_values:
            m3.add_command(label=s, command=lambda value=s: csv_field3_var.set(value))
    else:
        csv_files_list.clear()
        menu_values.clear()

def activate_visualization_options(*args):
    if error:
        return

activate_visualization_options()

visualizations_menu_var.trace('w',activate_visualization_options)

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
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, select the csv file field to be used for visualization.\n\nA NUMERIC field is required for the 'Boxplot' option and a CATEGORICAL field for the 'Comparative bar charts' option.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select type of visual chart to be used for visualization.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","THE 'Boxplot' parameter widget is just a label. Use the widgets in the next line to set the parameters required by the 'Boxplot' option.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","THE WIDGETS ON THIS LINE REFER TO THE BOXPLOT OPTION ONLY.\n\nUse the dropdown menu to select the type of data points to be processed. Tick the 'Split data by category' checkbox if you want to use a file field to split and/or color the charts by the value of a csv file field.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","THE 'Multiple bar charts parameters' widget is just a label. Use the widgets in the next line to set the parameters required by the 'Comparative bar charts' option.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","THE WIDGETS ON THIS LINE REFER TO THE COMPARATIVE MULTIPLE BAR CHARTS OPTION ONLY.\n\nAT LEAST TWO CSV FILES ARE REQUIRED FOR THE MULTIPLE BAR CHARTS OPTION.\n\nClick on the + button to add a new csv file.\nClick on the Reset button to clear the current selection and start over.\nUse the dropdown menu to select a specific csv file that you can then open with the Open button.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 script provides access to different types of data visualization: boxplots and comparative bar charts.\n\nIn OUTPUT the algorithms produce different types of html charts."
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
