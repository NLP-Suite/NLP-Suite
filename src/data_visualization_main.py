# Combined visualization GUI with tabbed interface
# Merges data_visualization_1_main.py (relational, categorical, temporal)
# and data_visualization_2_main.py (numeric/statistical)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"data_visualization_main.py",['os','tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_csv_util
import IO_files_util
import charts_util
import run_script_util

# ── Run functions ──────────────────────────────────────────────────────────────

def runGephi(inputFilename, outputDir, csv_file_relational_field_list, dynamic_network_field_var):
    import Gephi_util
    fileBase = os.path.basename(inputFilename)[0:-4]
    return Gephi_util.create_gexf(GUI_util.window, fileBase, outputDir, inputFilename,
                                  csv_file_relational_field_list[0], csv_file_relational_field_list[1],
                                  csv_file_relational_field_list[2], dynamic_network_field_var, 'abnormal')

def run_relational(inputFilename, outputDir, openOutputFiles,
                   relations_menu_var, csv_field_relational_var,
                   csv_file_relational_field_list, dynamic_network_field_var,
                   Sankey_limit1_var, Sankey_limit2_var, Sankey_limit3_var):
    filesToOpen = []
    if inputFilename == '' or os.path.basename(inputFilename)[-4:] != ".csv":
        mb.showwarning("Warning", "The visualization options require a csv file in input.\n\nPlease, select a csv file and try again.")
        return
    if relations_menu_var == '':
        mb.showwarning("Warning", "Please, use the dropdown menu to select one of the options for visualizing relations: Gephi, Network graph (vis.js), Sankey and try again.")
        return

    outputFilename = ''

    # Gephi
    if relations_menu_var=='*' or relations_menu_var=='Gephi':
        if len(csv_file_relational_field_list)!=3:
            if relations_menu_var=='Gephi':
                mb.showwarning("Warning", "You must select three csv fields to be used in the computation of the network graph, in the order of node, edge, node (e.g., Subject, Verb, Object).\n\nIf you wish to create a dynamic network graph you can select a fourth field to be used as the dynamic index (e.g., Sentence ID or Date).")
                return
        else:
            try:
                outputFiles = runGephi(inputFilename, outputDir, csv_file_relational_field_list, dynamic_network_field_var)
                if outputFiles != None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)
            except Exception as e:
                if relations_menu_var=='*':
                    print(f"  Gephi skipped (not installed or error): {e}")
                else:
                    mb.showwarning("Warning", f"Gephi error: {e}")
                    return

    # Network graph (vis.js)
    if relations_menu_var=='*' or relations_menu_var=='Network graph (vis.js)':
        if len(csv_file_relational_field_list)!=3:
            if relations_menu_var=='Network graph (vis.js)':
                mb.showwarning("Warning", "You must select three csv fields to be used in the computation of the network graph, in the order of node, edge, node (e.g., Subject, Verb, Object).\n\nIf you wish to create a dynamic temporal network you can select a fourth field to be used as the dynamic index (e.g., Date).")
                return
        else:
            date_field = dynamic_network_field_var if dynamic_network_field_var else None
            outputFiles = charts_util.network_graph_visjs(
                inputFilename, outputDir,
                csv_file_relational_field_list[0],
                csv_file_relational_field_list[1],
                csv_file_relational_field_list[2],
                date_col=date_field)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    # Sankey
    if relations_menu_var=='*' or relations_menu_var=='Sankey':
        if len(csv_file_relational_field_list)!=2 and len(csv_file_relational_field_list)!=3:
            if relations_menu_var=='Sankey':
                mb.showwarning("Warning", "You must select 2 or 3 csv fields to be used in the computation of a Sankey chart (e.g., Subject, Verb, Object or Subject, Object).\n\nMAKE SURE TO CLICK ON THE + BUTTON AFTER THE LAST SELECTION. CLICK ON THE SHOW BUTTON TO SEE THE CURRENT SELECTION.")
                return
        else:
            if len(csv_file_relational_field_list)==3:
                three_way_Sankey=True
                var3=csv_file_relational_field_list[2]
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

    if openOutputFiles and len(filesToOpen) > 0:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)


def run_categorical(inputFilename, outputDir, openOutputFiles,
                    categorical_menu_var, csv_field_categorical_var,
                    case_sensitive_var, csv_file_categorical_field_list,
                    filter_options_var, fixed_param_var, rate_param_var, base_param_var,
                    max_rows_var, color_1_style_var, color_2_style_var, data_transformation_var,
                    csv_files_list, csv_field_visualization_var):
    filesToOpen = []
    if inputFilename == '' or os.path.basename(inputFilename)[-4:] != ".csv":
        mb.showwarning("Warning", "The visualization options require a csv file in input.\n\nPlease, select a csv file and try again.")
        return

    if categorical_menu_var == '':
        mb.showwarning("Warning", "Please, use the dropdown menu to select one of the options for categorical data and try again.")
        return

    # Comparative bar charts have their own validation
    if 'Comparative' in categorical_menu_var:
        if len(csv_files_list) < 2:
            mb.showwarning("Warning", "The 'Comparative bar charts' option requires at least two csv files in input.\n\nPlease, select at least 2 csv files and try again.")
            return
        if csv_field_visualization_var == '':
            mb.showwarning("Warning", "No Y-axis variable has been selected.\n\nPlease, select a Y-axis variable and try again.")
            return
        outputFiles = charts_util.comparative_bar_charts(csv_files_list, outputDir, csv_field_visualization_var)
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)
        if openOutputFiles and len(filesToOpen) > 0:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)
        return

    if len(csv_file_categorical_field_list)<2:
        mb.showwarning("Warning", "You must have at least 2 sets of csv file search field and search values to produce meaningful " + categorical_menu_var + " charts.\n\nPlease, select another combination of csv file field and search values and try again.")
        return
    if csv_field_categorical_var == '':
        mb.showwarning("Warning", "The categorical data visualization functions require a set of comma-separated entries to be used in the search (could be parts of a filenames, if the Document field is selected).\n\nPlease, enter value(s) and try again.")
        return

    label = csv_field_categorical_var
    outputFilename = ''

    # Colormap
    if '*' in categorical_menu_var or 'Colormap' in categorical_menu_var:
        all_fields = []
        intermediate_fields = []
        for i in range(len(csv_file_categorical_field_list)):
            if i > 0 and i < len(csv_file_categorical_field_list)-1:
                intermediate_fields.append(csv_file_categorical_field_list[i][0].split('|')[0])
            all_fields.append(csv_file_categorical_field_list[i][0].split('|')[0])
        all_fields_str = ', '.join(all_fields)
        intermediate_fields_str = ', '.join(intermediate_fields)
        mb.showwarning(title='Search values',
                       message='You have entered ' + str(len(csv_file_categorical_field_list)) +
                               ' different search fields: "' + all_fields_str + '".' +
                               '\n\nThe first selected field "' + csv_file_categorical_field_list[0][0].split('|')[0] + '" will be used as the GroupBy field.' +
                               '\n\nThe last field "' + csv_file_categorical_field_list[len(csv_file_categorical_field_list)-1][0].split('|')[0] + '" will be used as the field whose values will be displayed.' +
                               '\n\nAll other intermediate fields "' + intermediate_fields_str + '" will be used as the conditional WHERE CLAUSE.')
        params = [max_rows_var, color_1_style_var, color_2_style_var, data_transformation_var]
        outputFiles = charts_util.colormap(inputFilename, outputDir, csv_file_categorical_field_list, params)
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    if filter_options_var=='No filtering':
        fixed_param_var_val=None
        rate_param_var_val=None
        base_param_var_val=None
    elif filter_options_var=='Fixed parameter':
        fixed_param_var_val=fixed_param_var
        rate_param_var_val=None
        base_param_var_val=None
    else:
        fixed_param_var_val=None
        rate_param_var_val=rate_param_var
        base_param_var_val=base_param_var

    # Sunburst
    if '*' in categorical_menu_var:
        chart_type = 3
    if '*' in categorical_menu_var or 'Sunburst' in categorical_menu_var:
        chart_type = 1
        outputFiles = charts_util.Sunburst_Treemap(inputFilename, outputFilename, outputDir, csv_file_categorical_field_list, chart_type, fixed_param_var_val, rate_param_var_val, base_param_var_val, filter_options_var, case_sensitive_var)
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # Stacked bar
    if '*' in categorical_menu_var or 'Stacked bar' in categorical_menu_var:
        if len(csv_file_categorical_field_list) < 2:
            mb.showwarning("Warning", "The stacked bar chart requires at least 2 csv file fields: one for the groups (rows) and one for the segments (stacked colors).\n\nPlease, select at least 2 fields and try again.")
        else:
            group_field = csv_file_categorical_field_list[0][0].split('|')[0]
            segment_field = csv_file_categorical_field_list[1][0].split('|')[0]
            outputFile = charts_util.stacked_bar_from_csv(inputFilename, outputDir, group_field, segment_field)
            if outputFile:
                filesToOpen.append(outputFile)

    # Treemap
    if 'Treemap' in categorical_menu_var:
        chart_type = 0
        outputFiles = charts_util.Sunburst_Treemap(inputFilename, outputFilename, outputDir,
                                                   csv_file_categorical_field_list, chart_type,
                                                   fixed_param_var_val, rate_param_var_val, base_param_var_val, filter_options_var, case_sensitive_var)
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    if openOutputFiles and len(filesToOpen) > 0:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)


def run_temporal(inputFilename, outputDir, openOutputFiles,
                 csv_field_relational_var, time_mapper_field_var,
                 date_format_var, time_var, cumulative_var):
    filesToOpen = []
    if inputFilename == '' or os.path.basename(inputFilename)[-4:] != ".csv":
        mb.showwarning("Warning", "The visualization options require a csv file in input.\n\nPlease, select a csv file and try again.")
        return

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.html', 'timeMapper')
    monthly = False
    yearly = False
    if time_var == 'Monthly':
        monthly = True
    elif time_var == 'Yearly':
        yearly = True

    date_col = time_mapper_field_var if time_mapper_field_var else None
    outputFiles = charts_util.TimeMapper(inputFilename, outputFilename, csv_field_relational_var, date_format_var,
                                        cumulative_var, monthly, yearly, date_col=date_col)
    if outputFiles != None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    if openOutputFiles and len(filesToOpen) > 0:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)


def run_numeric(inputFilename, outputDir, openOutputFiles,
                visualizations_menu_var, csv_field_visualization_var,
                X_axis_var, csv_file_field_Y_axis_list, points_var,
                split_data_byCategory_var, csv_field_boxplot_var,
                csv_field_boxplot_color_var, X_axis_bubble_var,
                color_1_style_var):
    filesToOpen = []
    if inputFilename == '' or os.path.basename(inputFilename)[-4:] != ".csv":
        mb.showwarning("Warning", "The visualization options require a csv file in input.\n\nPlease, select a csv file and try again.")
        return

    config_filename = GUI_util.config_filename_selected_config.get()

    if 'Boxplot' in visualizations_menu_var:
        if csv_field_visualization_var == '':
            mb.showwarning("Warning", "No Y-axis variable has been selected.\n\nPlease, select a Y-axis variable and try again.")
            return
        outputFiles = charts_util.boxplot(inputFilename, outputDir, csv_field_visualization_var,
                                          complete_sid=False, csv_field_Y_axis_list=csv_file_field_Y_axis_list,
                                          X_axis_var = X_axis_var)
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    elif 'Bubble' in visualizations_menu_var:
        if csv_field_visualization_var == '':
            mb.showwarning("Warning", "No Y-axis variable has been selected.\n\nPlease, select a Y-axis variable and try again.")
            return
        outputFiles = charts_util.bubble_chart(inputFilename, outputDir, csv_field_visualization_var,
                                               X_axis_var=X_axis_bubble_var)
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    elif 'Excel' in visualizations_menu_var or 'Plotly' in visualizations_menu_var:
        if X_axis_var=='' and len(csv_file_field_Y_axis_list) < 1:
            mb.showwarning("Warning", "No X-axis or Y-axis variable has been selected.\n\nPlease, select a variable and try again.")
            return
        if len(csv_file_field_Y_axis_list) < 1:
            mb.showwarning("Warning", "No Y-axis variable has been selected.\n\nPlease, select at least one Y-axis variable and try again.")
            return
        if len(csv_file_field_Y_axis_list) < 3:
            outputFiles = charts_util.visualize_chart(GUI_util.window, inputFilename, outputDir,
                                                      complete_sid=False, csv_field_Y_axis_list=csv_file_field_Y_axis_list, X_axis_var = X_axis_var)
        else:
            outputFiles = charts_util.visualize_chart(GUI_util.window, inputFilename, outputDir,
                                                      complete_sid=False, csv_field_Y_axis_list=csv_file_field_Y_axis_list, X_axis_var = X_axis_var)
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    if openOutputFiles and len(filesToOpen) > 0:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)


# ── GUI setup ──────────────────────────────────────────────────────────────────

IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=600,
                             GUI_height_full=680,
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2,
                             increment=2)

GUI_label='Graphical User Interface (GUI) for Data Visualization'
config_filename = 'NLP_default_IO_config.csv'
head, scriptName = os.path.split(os.path.basename(__file__))

config_input_output_numeric_options=[3,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)
window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

# ── Shared variables ──────────────────────────────────────────────────────────

extra_GUIs_var = tk.IntVar()
extra_GUIs_menu_var = tk.StringVar()
input_csv_file_var = tk.StringVar()

# Relational tab variables
relations_menu_var = tk.StringVar()
Gephi_var = tk.IntVar()
Sankey_var = tk.IntVar()
selected_csv_file_fields_var = tk.StringVar()
csv_field_relational_var = tk.StringVar()
dynamic_network_field_var = tk.StringVar()
selected_csv_file_fields = tk.StringVar()

# Categorical tab variables
categorical_menu_var = tk.StringVar()
csv_field_categorical_var = tk.StringVar()
search_values_categorical_var = tk.StringVar()
case_sensitive_var = tk.IntVar()
filter_options_var = tk.StringVar()
fixed_param_var = tk.StringVar()
rate_param_var = tk.StringVar()
base_param_var = tk.StringVar()
max_rows_var = tk.IntVar()
color_1_var = tk.IntVar()
color_2_var = tk.IntVar()
color_1_style_var = tk.StringVar()
color_2_style_var = tk.StringVar()
data_transformation_var = tk.StringVar()

# Temporal tab variables
time_mapper_field_var = tk.StringVar()
date_format_var = tk.StringVar()
date_format_var.set('mm-dd-yyyy')
time_var = tk.StringVar()
time_var.set('Daily')
cumulative_var = tk.IntVar()

# Numeric tab variables
visualizations_menu_var = tk.StringVar()
csv_field_visualization_var = tk.StringVar()
Y_axis_var = tk.StringVar()
X_axis_var = tk.StringVar()
split_data_byCategory_var = tk.IntVar()
csv_field_boxplot_var = tk.StringVar()
csv_field_boxplot_color_var = tk.StringVar()
X_axis_bubble_var = tk.StringVar()
points_var = tk.StringVar()
csv_file_var = tk.StringVar()

# Shared lists
csv_file_categorical_field_string = ''
csv_file_relational_field_list = []
csv_file_categorical_field_list = []
csv_file_field_Y_axis_list = []
csv_files_list = []
file_menu_values = []
menu_values = []
color_1_style_var_list = []
color_2_style_var_list = []
color_1_var_list = []
color_2_var_list = []
error = False
csv_field_visualization_var_SV = ''

# ── Shared widgets on window (GUIs available + csv file display) ──────────────

def open_GUI(*args):
    if 'manipulation' in extra_GUIs_menu_var.get():
        run_script_util.run_script("data_manipulation_main.py")
    elif 'Texts to maps' in extra_GUIs_menu_var.get():
        run_script_util.run_script("GIS_main.py")
    elif 'Google Earth' in extra_GUIs_menu_var.get():
        run_script_util.run_script("GIS_Google_Earth_main.py")
    elif 'Proportional' in extra_GUIs_menu_var.get():
        run_script_util.run_script("GIS_main.py")
    elif 'HTML' in extra_GUIs_menu_var.get():
        run_script_util.run_script("html_annotator_main.py")
    elif 'Wordclouds' in extra_GUIs_menu_var.get():
        run_script_util.run_script("wordclouds_main.py")
extra_GUIs_menu_var.trace('w', open_GUI)

extra_GUIs_var.set(0)
extra_GUIs_checkbox = tk.Checkbutton(window, text='GUIs available for more analyses ', variable=extra_GUIs_var, onvalue=1, offvalue=0, command=lambda: activate_all_options())
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer, extra_GUIs_checkbox, True)

extra_GUIs_menu_var.set('')
extra_GUIs_menu = tk.OptionMenu(window, extra_GUIs_menu_var, 'Data manipulation', 'Texts to maps (Open GUI)', 'Google Earth Pro (Open GUI)', 'Proportional circle map (Open GUI)', 'HTML annotator (Open GUI)', 'Wordclouds (Open GUI)')
extra_GUIs_menu.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   extra_GUIs_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select other related types of analysis you wish to perform\nThe selected GUI will open without having to press RUN")

# CSV file display row
def get_input_csv_file(window_ref, title, fileType):
    if input_csv_file_var.get() != '':
        initialFolder = os.path.dirname(os.path.abspath(input_csv_file_var.get()))
    else:
        initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title=title, initialdir=initialFolder, filetypes=fileType)
    if len(filePath) > 0:
        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(filePath, 'utf-8')
        if nRecords == 0:
            mb.showwarning(title='Warning', message="The selected input csv file is empty.\n\nPlease, select a different file and try again.")
            filePath = ''
        else:
            input_csv_file_var.set(filePath)
            changed_filename(filePath)
    return filePath

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

# ── Read initial csv headers ──────────────────────────────────────────────────

def get_csv_file_menu_values():
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
get_csv_file_menu_values()

if GUI_util.inputFilename.get() != '' and GUI_util.inputFilename.get()[-4:] == ".csv":
    file_menu_values = [inputFilename.get()]
else:
    file_menu_values = " "

# ── Notebook ──────────────────────────────────────────────────────────────────

# Style the notebook tabs: bold red text, extra padding
nb_style = ttk.Style()
nb_style.configure('Viz.TNotebook.Tab', font=('Courier', 11, 'bold'), foreground='red', padding=[12, 4])

# Save the current y position for the notebook
notebook_y = 90 + 40 * y_multiplier_integer

notebook = ttk.Notebook(window, style='Viz.TNotebook')
notebook.place(x=GUI_IO_util.labels_x_coordinate, y=notebook_y,
               width=GUI_IO_util.get_GUI_width(3) - GUI_IO_util.labels_x_coordinate - 20, height=280)

tab_relational = ttk.Frame(notebook)
tab_categorical = ttk.Frame(notebook)
tab_temporal = ttk.Frame(notebook)
tab_numeric = ttk.Frame(notebook)

notebook.add(tab_relational, text=' Relational ')
notebook.add(tab_categorical, text=' Categorical ')
notebook.add(tab_temporal, text=' Temporal ')
notebook.add(tab_numeric, text=' Numeric ')

# Advance y_multiplier_integer past the notebook area (280px / 40px per row = 7 rows)
y_multiplier_integer = y_multiplier_integer + 7

# ── Tab 1: Relational ────────────────────────────────────────────────────────

r_y = 0  # each tab starts at y=0

relations_lb = tk.Label(tab_relational, text='Visualize relations')
relations_lb.place(x=10, y=10)

relations_menu_var.set('Gephi')
relations_menu = tk.OptionMenu(tab_relational, relations_menu_var, '*', 'Gephi', 'Network graph (vis.js)', 'Sankey')
relations_menu.place(x=160, y=7)

csv_field_lb = tk.Label(tab_relational, text='csv file field')
csv_field_lb.place(x=10, y=45)

csv_field_relational_menu = tk.OptionMenu(tab_relational, csv_field_relational_var, *menu_values)
csv_field_relational_menu.place(x=120, y=42)

selected_csv_fields_area = tk.Entry(tab_relational, width=30, state='disabled', textvariable=selected_csv_file_fields)
selected_csv_fields_area.place(x=350, y=45)

def display_selected_csv_fields():
    if csv_field_relational_var.get() != '' and not csv_field_relational_var.get() in csv_file_relational_field_list:
        csv_file_relational_field_list.append(csv_field_relational_var.get())
        new_string = ', '.join(csv_file_relational_field_list)
        selected_csv_file_fields.set(new_string.lstrip())
    else:
        mb.showwarning(title='Warning', message='The option "' + csv_field_relational_var.get() + '" has already been selected. Selection ignored.\n\nYou can see your current selections by clicking the Show button.')
        csv_field_relational_menu.configure(state='normal')
    selected_csv_file_fields_var.set(str(csv_file_relational_field_list))
    activate_csv_fields_relational_selection(True)

def reset_relational():
    csv_file_relational_field_list.clear()
    csv_field_relational_var.set('')
    selected_csv_file_fields.set('')
    dynamic_network_field_var.set('')
    selected_csv_file_fields_var.set('')

add_button_relational = tk.Button(tab_relational, text='+', width=2, height=1, command=lambda: display_selected_csv_fields())
add_button_relational.place(x=580, y=42)

reset_button_relational = tk.Button(tab_relational, text='Reset', width=4, height=1, state='disabled', command=lambda: reset_relational())
reset_button_relational.place(x=620, y=42)

def show_Gephi_options_list():
    if len(csv_file_relational_field_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected Gephi options.')
    else:
        mb.showwarning(title='Warning', message='The currently selected Gephi options are:\n\n  ' + '\n  '.join(csv_file_relational_field_list) + '\n\nPlease, press the Reset button (or ESCape) to start fresh.')

# Gephi/vis.js row
Gephi_lb = tk.Label(tab_relational, text='Gephi/vis.js', foreground="red", font=("Courier", 12, "bold"))
Gephi_lb.place(x=10, y=80)

csv_field_dynamic_network_lb = tk.Label(tab_relational, text='csv file field for dynamic graph')
csv_field_dynamic_network_lb.place(x=140, y=83)

dynamic_network_field_menu = tk.OptionMenu(tab_relational, dynamic_network_field_var, *menu_values)
dynamic_network_field_menu.configure(state='disabled')
dynamic_network_field_menu.place(x=360, y=80)

# Sankey row
Sankey_lb = tk.Label(tab_relational, text='Sankey', foreground="red", font=("Courier", 12, "bold"))
Sankey_lb.place(x=10, y=115)

Sankey_limit1_lb = tk.Label(tab_relational, text='Variable 1 max')
Sankey_limit1_lb.place(x=140, y=118)

Sankey_limit1_var = tk.IntVar()
Sankey_limit1_var.set(5)
Sankey_limit1_menu = tk.OptionMenu(tab_relational, Sankey_limit1_var, 5, 10)
Sankey_limit1_menu.place(x=260, y=115)

Sankey_limit2_lb = tk.Label(tab_relational, text='Variable 2 max')
Sankey_limit2_lb.place(x=340, y=118)

Sankey_limit2_var = tk.IntVar()
Sankey_limit2_var.set(10)
Sankey_limit2_menu = tk.OptionMenu(tab_relational, Sankey_limit2_var, 5, 10, 20)
Sankey_limit2_menu.place(x=460, y=115)

Sankey_limit3_lb = tk.Label(tab_relational, text='Variable 3 max')
Sankey_limit3_lb.place(x=540, y=118)

Sankey_limit3_var = tk.IntVar()
Sankey_limit3_var.set(20)
Sankey_limit3_menu = tk.OptionMenu(tab_relational, Sankey_limit3_var, 5, 10, 20, 30)
Sankey_limit3_menu.place(x=660, y=115)

def activate_csv_fields_relational_selection(comingFromPlus=False):
    if csv_field_relational_var.get() != '':
        if comingFromPlus:
            csv_field_relational_menu.config(state='normal')
        else:
            csv_field_relational_menu.config(state='disabled')
        add_button_relational.config(state='normal')
        reset_button_relational.config(state='normal')
        if len(csv_file_relational_field_list) == 3:
            csv_field_relational_menu.configure(state='disabled')
            dynamic_network_field_menu.config(state='normal')
            if dynamic_network_field_var.get()=='':
                mb.showwarning(title='Warning', message='You have selected the maximum number of fields (3) to visualize relations.\n\nPress the "Show" button to display your selection. Press the "Reset" button to clear your selection and start again.')
    else:
        csv_field_relational_menu.config(state='normal')
        dynamic_network_field_menu.config(state='normal')
        reset_button_relational.config(state='disabled')
csv_field_relational_var.trace('w', callback=lambda x,y,z: activate_csv_fields_relational_selection())
dynamic_network_field_var.trace('w', callback=lambda x,y,z: activate_csv_fields_relational_selection())


# ── Tab 2: Categorical ───────────────────────────────────────────────────────

categorical_lb = tk.Label(tab_categorical, text='Visualize categorical data')
categorical_lb.place(x=10, y=10)

categorical_menu_var.set('Sunburst')
categorical_menu = tk.OptionMenu(tab_categorical, categorical_menu_var, '*', 'Colormap/heatmap', 'Comparative bar charts', 'Stacked bar', 'Sunburst', 'Treemap')
categorical_menu.place(x=200, y=7)

csv_field_categorical_lb = tk.Label(tab_categorical, text='Search field')
csv_field_categorical_lb.place(x=10, y=45)

csv_field_categorical_menu = tk.OptionMenu(tab_categorical, csv_field_categorical_var, *menu_values)
csv_field_categorical_menu.place(x=120, y=42)

case_sensitive_var.set(1)
case_sensitive_checkbox = tk.Checkbutton(tab_categorical, variable=case_sensitive_var, onvalue=1, offvalue=0)
case_sensitive_checkbox.place(x=340, y=45)

search_values_categorical_label_lb = tk.Label(tab_categorical, text='Search values')
search_values_categorical_label_lb.place(x=370, y=48)

search_values_categorical_var.set('')
search_values_categorical = tk.Entry(tab_categorical, state='disabled', textvariable=search_values_categorical_var, width=20)
search_values_categorical.place(x=460, y=48)

def add_combination_csvField_searchValues():
    global csv_file_categorical_field_string
    if (not search_values_categorical_var.get()=='') and (search_values_categorical_var.get() in csv_file_categorical_field_string):
        result = mb.askyesno('Warning', 'You have already entered the search value(s) "' + search_values_categorical_var.get() + '"\n\nAre you sure you want to use the same search values?')
        if not result:
            return
    csv_file_categorical_field_string = csv_field_categorical_var.get()+'|'+search_values_categorical_var.get()
    csv_file_categorical_field_list.append([csv_file_categorical_field_string])
    search_values_categorical_var.set('')
    csv_field_categorical_menu.focus_set()
    activate_all_options()

add_button_categorical = tk.Button(tab_categorical, text='+', width=2, height=1, command=lambda: add_combination_csvField_searchValues())
add_button_categorical.place(x=640, y=42)

def reset_categorical():
    csv_file_categorical_field_list.clear()
    csv_field_categorical_var.set('')
    search_values_categorical_var.set('')
    csv_field_categorical_menu.config(state='normal')
    if csv_field_categorical_var.get() == '' and 'Document' in menu_values:
        csv_field_categorical_var.set('Document')

reset_button_categorical = tk.Button(tab_categorical, text='Reset', width=4, height=1, command=lambda: reset_categorical())
reset_button_categorical.place(x=680, y=42)

def show_categorical_list():
    if len(csv_file_categorical_field_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected combinations of csv file field and search words.')
    else:
        mb.showwarning(title='Warning', message='The currently selected combination of csv file field and search word are:\n\n' + str(csv_file_categorical_field_list) + '\n\nPlease, press the Reset button (or ESCape) to start fresh.')

show_button_categorical = tk.Button(tab_categorical, text='Show', width=4, height=1, command=lambda: show_categorical_list())
show_button_categorical.place(x=730, y=42)

# Filtering row
filter_lb = tk.Label(tab_categorical, text='Filtering options')
filter_lb.place(x=10, y=80)

filter_options_var.set('No filtering')
filter_options_menu = tk.OptionMenu(tab_categorical, filter_options_var, 'No filtering', 'Fixed parameter', 'Propagating parameter')
filter_options_menu.place(x=140, y=77)

fixed_param_lb = tk.Label(tab_categorical, text='Fixed')
fixed_param_lb.place(x=320, y=80)

fixed_param_var.set(15)
fixed_param = tk.Entry(tab_categorical, state='disabled', textvariable=fixed_param_var, width=3)
fixed_param.place(x=365, y=80)

rate_param_lb = tk.Label(tab_categorical, text='Rate')
rate_param_lb.place(x=400, y=80)

rate_param_var.set(3)
rate_param = tk.Entry(tab_categorical, state='disabled', textvariable=rate_param_var, width=3)
rate_param.place(x=440, y=80)

base_param_lb = tk.Label(tab_categorical, text='Base')
base_param_lb.place(x=475, y=80)

base_param_var.set(15)
base_param = tk.Entry(tab_categorical, state='disabled', textvariable=base_param_var, width=3)
base_param.place(x=515, y=80)

def activate_filtering_options(*args):
    fixed_param.configure(state='disabled')
    rate_param.configure(state='disabled')
    base_param.configure(state='disabled')
    if 'Fixed' in filter_options_var.get():
        fixed_param.configure(state='normal')
    if 'Propagating' in filter_options_var.get():
        rate_param.configure(state='normal')
        base_param.configure(state='normal')
filter_options_var.trace('w', activate_filtering_options)

# Colormap row
colormap_lb = tk.Label(tab_categorical, text='Colormap/heatmap', foreground="red", font=("Courier", 12, "bold"))
colormap_lb.place(x=10, y=115)

max_rows_lb = tk.Label(tab_categorical, text='Max rows')
max_rows_lb.place(x=200, y=118)

max_rows_var.set(20)
max_rows = tk.Entry(tab_categorical, state='disabled', textvariable=max_rows_var, width=3)
max_rows.place(x=265, y=118)

color_1_var.set(0)
color_1_style_var_list.append("")
color_1_var_list.append(0)
color_1_checkbox = tk.Checkbutton(tab_categorical, text='Color ', variable=color_1_var, onvalue=1, offvalue=0)
color_1_checkbox.place(x=300, y=115)

color_1_style_var.set("135, 207, 236")
color_1_entry = tk.Entry(tab_categorical, width=10, textvariable=color_1_style_var)
color_1_entry.configure(state='disabled')
color_1_entry.place(x=370, y=118)

def activate_color_1_palette(*args):
    try:
        from tkcolorpicker import askcolor
        if color_1_var.get() == 1:
            style = ttk.Style(window)
            style.theme_use('clam')
            color_1_list = askcolor((135, 207, 236), window)
            color_1_style = color_1_list[0]
            color_1_style_var.set(color_1_style)
    except ImportError:
        pass
color_1_var.trace('w', activate_color_1_palette)

color_2_var.set(0)
color_2_style_var_list.append("")
color_2_var_list.append(0)
color_2_checkbox = tk.Checkbutton(tab_categorical, text='Color ', variable=color_2_var, onvalue=1, offvalue=0)
color_2_checkbox.place(x=470, y=115)

color_2_style_var.set("0, 0, 255")
color_2_entry = tk.Entry(tab_categorical, width=10, textvariable=color_2_style_var)
color_2_entry.configure(state='disabled')
color_2_entry.place(x=540, y=118)

def activate_color_2_palette(*args):
    try:
        from tkcolorpicker import askcolor
        if color_2_var.get() == 1:
            style = ttk.Style(window)
            style.theme_use('clam')
            color_2_list = askcolor((0, 0, 255), window)
            color_2_style = color_2_list[0]
            color_2_style_var.set(color_2_style)
    except ImportError:
        pass
color_2_var.trace('w', activate_color_2_palette)

data_transformation_lb = tk.Label(tab_categorical, text='Normalize')
data_transformation_lb.place(x=640, y=118)

data_transformation_var.set('No transform')
data_transformation_menu = tk.OptionMenu(tab_categorical, data_transformation_var, 'No transform', 'Min-Max', 'Z-score', 'Square root', 'Log', 'Ln')
data_transformation_menu.place(x=710, y=115)

# Comparative bar charts row
comparative_bar_lb = tk.Label(tab_categorical, text='Comparative bar charts', foreground="red", font=("Courier", 12, "bold"))
comparative_bar_lb.place(x=10, y=150)

def add_csvFile_comparative(window_ref, title, fileType):
    initialFolder = GUI_util.output_dir_path.get()
    filePath = tk.filedialog.askopenfilename(title=title, initialdir=initialFolder, filetypes=fileType)
    if len(filePath) > 0:
        if filePath not in csv_files_list:
            csv_files_list.append(filePath)
            process_csv_file_menu_comparative(filePath)
        else:
            mb.showwarning(title='Warning', message='The file has already been selected. Selection ignored.')

def process_csv_file_menu_comparative(InputFile):
    m = csv_file_menu_comparative["menu"]
    m.delete(0, "end")
    for s in csv_files_list:
        m.add_command(label=s, command=lambda value=s: csv_file_var.set(value))

add_file = tk.Button(tab_categorical, text='+', width=2, height=1, command=lambda: add_csvFile_comparative(window, 'Select csv file', [("csv files", "*.csv")]))
add_file.place(x=230, y=150)

def reset_files():
    csv_files_list.clear()
    csv_file_var.set('')
    if GUI_util.inputFilename.get().endswith('.csv'):
        csv_files_list.append(GUI_util.inputFilename.get())
        process_csv_file_menu_comparative(GUI_util.inputFilename.get())

reset_file_button = tk.Button(tab_categorical, text='Reset', width=4, height=1, command=lambda: reset_files())
reset_file_button.place(x=270, y=150)

openInputFile_button_comparative = tk.Button(tab_categorical, width=1, text='', command=lambda: IO_files_util.openFile(window, csv_file_var.get()))
openInputFile_button_comparative.place(x=330, y=150)

select_csv_file_lb = tk.Label(tab_categorical, text='Select csv file')
select_csv_file_lb.place(x=360, y=153)

csv_file_menu_comparative = tk.OptionMenu(tab_categorical, csv_file_var, *file_menu_values)
csv_file_menu_comparative.place(x=460, y=150)

def activate_csv_fields_categorical_selection(comingFromPlus=True):
    global csv_file_categorical_field_string
    if csv_field_categorical_var.get() != '':
        if csv_field_categorical_var.get() in csv_file_categorical_field_list:
            mb.showwarning(title='Warning', message='The option has already been selected. Selection ignored.\n\nYou can see your current selections by clicking the Show button.')
            return
        else:
            csv_file_categorical_field_string = csv_file_categorical_field_string + '|' + csv_field_categorical_var.get()
    if csv_field_categorical_var.get() != '':
        search_values_categorical.configure(state='normal')
        if comingFromPlus:
            csv_field_categorical_menu.config(state='normal')
        else:
            csv_field_categorical_menu.config(state='disabled')
        add_button_categorical.config(state='normal')
        reset_button_categorical.config(state='normal')
    else:
        search_values_categorical.configure(state='disabled')
        csv_field_categorical_menu.config(state='normal')
    activate_all_options()
categorical_menu_var.trace('w', callback=lambda x,y,z: activate_csv_fields_categorical_selection())


# ── Tab 3: Temporal ───────────────────────────────────────────────────────────

temporal_lb = tk.Label(tab_temporal, text='Time mapper', foreground="red", font=("Courier", 12, "bold"))
temporal_lb.place(x=10, y=10)

csv_field_time_mapper_lb = tk.Label(tab_temporal, text='Y-axis field')
csv_field_time_mapper_lb.place(x=130, y=13)

# Reuse relational field menu for Y-axis in temporal tab
csv_field_temporal_menu = tk.OptionMenu(tab_temporal, csv_field_relational_var, *menu_values)
csv_field_temporal_menu.place(x=220, y=10)

date_field_lb = tk.Label(tab_temporal, text='Date field')
date_field_lb.place(x=10, y=50)

time_mapper_field_menu = tk.OptionMenu(tab_temporal, time_mapper_field_var, *menu_values)
time_mapper_field_menu.place(x=100, y=47)

date_format_lb = tk.Label(tab_temporal, text='Format')
date_format_lb.place(x=320, y=50)

date_format_var.set('mm-dd-yyyy')
date_format_menu = tk.OptionMenu(tab_temporal, date_format_var, 'mm-dd-yyyy', 'dd-mm-yyyy', 'yyyy-mm-dd', 'yyyy-dd-mm', 'yyyy-mm', 'yyyy')
date_format_menu.place(x=380, y=47)

select_time_lb = tk.Label(tab_temporal, text='Timeline')
select_time_lb.place(x=520, y=50)

time_var.set('Daily')
select_time_menu = tk.OptionMenu(tab_temporal, time_var, 'Daily', 'Monthly', 'Yearly')
select_time_menu.place(x=585, y=47)

cumulative_var.set(0)
cumulative_checkbox = tk.Checkbutton(tab_temporal, text='Cumulative', variable=cumulative_var, onvalue=1, offvalue=0)
cumulative_checkbox.place(x=680, y=50)


# ── Tab 4: Numeric ────────────────────────────────────────────────────────────

visualization_basic_options_lb = tk.Label(tab_numeric, text='Visualization options')
visualization_basic_options_lb.place(x=10, y=10)

visualizations_menu_var.set('Excel/Plotly charts')
visualizations_menu = tk.OptionMenu(tab_numeric, visualizations_menu_var, 'Boxplots', 'Bubble chart', 'Excel/Plotly charts')
visualizations_menu.place(x=170, y=7)

csv_field_visualization_lb = tk.Label(tab_numeric, text='csv file field for visualization (Y-axis)')
csv_field_visualization_lb.place(x=10, y=45)

csv_field_visualization_menu = tk.OptionMenu(tab_numeric, csv_field_visualization_var, *menu_values)
csv_field_visualization_menu.place(x=280, y=42)

def check_selected_csv_file_field_Y_axis_list(main_Y_axis):
    global csv_field_visualization_var_SV
    if not 'Excel' in visualizations_menu_var.get():
        return
    if csv_field_visualization_var.get() != '':
        if csv_field_visualization_var_SV == '':
            csv_field_visualization_var_SV = csv_field_visualization_var.get()
        else:
            if main_Y_axis:
                if csv_field_visualization_var_SV in str(', '.join(csv_file_field_Y_axis_list)):
                    csv_file_field_Y_axis_list.remove(csv_field_visualization_var_SV)
                csv_field_visualization_var_SV = ''
    if main_Y_axis:
        field_value = csv_field_visualization_var.get()
    else:
        field_value = Y_axis_var.get()
    if field_value == '':
        return
    if field_value in str(', '.join(csv_file_field_Y_axis_list)):
        mb.showwarning(title='Warning', message='The option "' + field_value + '" has already been selected. Selection ignored.\n\nYou can see your current selections by using the dropdown menu.')
    else:
        csv_file_field_Y_axis_list.append(field_value)
csv_field_visualization_var.trace('w', lambda x, y, z: check_selected_csv_file_field_Y_axis_list(True))

# Excel/Plotly row
Excel_Plotly_lb = tk.Label(tab_numeric, text='Excel/Plotly', foreground="red", font=("Courier", 12, "bold"))
Excel_Plotly_lb.place(x=10, y=80)

X_axis_lb = tk.Label(tab_numeric, text='X-axis')
X_axis_lb.place(x=130, y=83)

X_axis_menu = tk.OptionMenu(tab_numeric, X_axis_var, *file_menu_values)
X_axis_menu.place(x=180, y=80)

Y_axis_lb = tk.Label(tab_numeric, text='Additional Y-axis')
Y_axis_lb.place(x=380, y=83)

Y_axis_menu = tk.OptionMenu(tab_numeric, Y_axis_var, *file_menu_values)
Y_axis_menu.place(x=500, y=80)

add_Y_axis = tk.Button(tab_numeric, text='+', width=2, height=1, command=lambda: check_selected_csv_file_field_Y_axis_list(False))
add_Y_axis.place(x=640, y=80)

def reset_csv_field_Y_axis_values():
    csv_file_field_Y_axis_list.clear()
    csv_field_visualization_menu.configure(state='normal')
    csv_field_visualization_var.set('')
    Y_axis_var.set('')

reset_Y_axis_button = tk.Button(tab_numeric, text='Reset', width=4, height=1, state='normal', command=lambda: reset_csv_field_Y_axis_values())
reset_Y_axis_button.place(x=680, y=80)

def show_Y_axis_list():
    if len(csv_file_field_Y_axis_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected additional Y-axis variables.')
    else:
        mb.showwarning(title='Warning', message='The currently selected Y-axis variables are:\n\n' + ', '.join(csv_file_field_Y_axis_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

show_Y_axis_button = tk.Button(tab_numeric, text='Show', width=4, height=1, command=lambda: show_Y_axis_list())
show_Y_axis_button.place(x=730, y=80)

# Boxplot row
boxplot_lb = tk.Label(tab_numeric, text='Boxplot', foreground="red", font=("Courier", 12, "bold"))
boxplot_lb.place(x=10, y=115)

points_lb = tk.Label(tab_numeric, text='Data')
points_lb.place(x=130, y=118)

points_menu = tk.OptionMenu(tab_numeric, points_var, 'all', 'None', 'outliers')
points_menu.place(x=170, y=115)

split_data_byCategory_checkbox = tk.Checkbutton(tab_numeric, variable=split_data_byCategory_var, text='Split data by category',
                                onvalue=1, offvalue=0, command=lambda: activate_split_options())
split_data_byCategory_checkbox.place(x=290, y=115)

csv_field2_lb = tk.Label(tab_numeric, text='csv file field')
csv_field2_lb.place(x=460, y=118)

csv_field_boxplot_menu = tk.OptionMenu(tab_numeric, csv_field_boxplot_var, *menu_values)
csv_field_boxplot_menu.configure(state='disabled')
csv_field_boxplot_menu.place(x=550, y=115)

csv_field_boxplot_color_lb = tk.Label(tab_numeric, text='Color field')
csv_field_boxplot_color_lb.place(x=680, y=118)

csv_field_boxplot_color_menu = tk.OptionMenu(tab_numeric, csv_field_boxplot_color_var, *menu_values)
csv_field_boxplot_color_menu.configure(state='disabled')
csv_field_boxplot_color_menu.place(x=750, y=115)

def activate_split_options(*args):
    if split_data_byCategory_var.get():
        csv_field_boxplot_menu.configure(state='normal')
        csv_field_boxplot_color_menu.configure(state='normal')
    else:
        csv_field_boxplot_var.set('')
        csv_field_boxplot_color_var.set('')
        csv_field_boxplot_menu.configure(state='disabled')
        csv_field_boxplot_color_menu.configure(state='disabled')
split_data_byCategory_var.trace('w', activate_split_options)

# Bubble chart row
bubble_chart_lb = tk.Label(tab_numeric, text='Bubble chart', foreground="red", font=("Courier", 12, "bold"))
bubble_chart_lb.place(x=10, y=150)

X_axis_bubble_lb = tk.Label(tab_numeric, text='X-axis')
X_axis_bubble_lb.place(x=130, y=153)

X_axis_bubble_menu = tk.OptionMenu(tab_numeric, X_axis_bubble_var, *file_menu_values)
X_axis_bubble_menu.place(x=180, y=150)

num_color_1_var = tk.IntVar()
num_color_1_style_var = tk.StringVar()
num_color_1_checkbox = tk.Checkbutton(tab_numeric, text='Color', variable=num_color_1_var, onvalue=1, offvalue=0)
num_color_1_checkbox.place(x=380, y=150)

num_color_1_style_var.set("135, 207, 236")
num_color_1_entry = tk.Entry(tab_numeric, width=10, textvariable=num_color_1_style_var)
num_color_1_entry.configure(state='disabled')
num_color_1_entry.place(x=440, y=153)



# ── changed_filename (populates all menus across all tabs) ────────────────────

def changed_filename(tracedInputFile):
    global error
    if tracedInputFile.endswith('.csv'):
        error = False
    else:
        error = True

    menu_values_local = []
    if tracedInputFile != '' and os.path.basename(tracedInputFile)[-4:] == ".csv":
        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(tracedInputFile)
        if nColumns == 0 or nColumns == None:
            return False
        if IO_csv_util.csvFile_has_header(tracedInputFile) == False:
            menu_values_local = list(range(1, nColumns + 1))
        else:
            data, headers = IO_csv_util.get_csv_data(tracedInputFile, True)
            menu_values_local = headers

        # Initialize csv_files_list for comparative bar charts
        if tracedInputFile not in csv_files_list:
            csv_files_list.clear()
            csv_files_list.append(tracedInputFile)
            process_csv_file_menu_comparative(tracedInputFile)
    else:
        menu_values_local = []

    # Relational tab menus
    m1 = csv_field_relational_menu["menu"]
    m1.delete(0, "end")
    for s in menu_values_local:
        m1.add_command(label=s, command=lambda value=s: csv_field_relational_var.set(value))

    m2 = dynamic_network_field_menu["menu"]
    m2.delete(0, "end")
    for s in menu_values_local:
        m2.add_command(label=s, command=lambda value=s: dynamic_network_field_var.set(value))

    # Categorical tab menus
    m3 = csv_field_categorical_menu["menu"]
    m3.delete(0, "end")
    for s in menu_values_local:
        m3.add_command(label=s, command=lambda value=s: csv_field_categorical_var.set(value))

    # Temporal tab menus
    m_tm = time_mapper_field_menu["menu"]
    m_tm.delete(0, "end")
    for s in menu_values_local:
        m_tm.add_command(label=s, command=lambda value=s: time_mapper_field_var.set(value))

    m_tc = csv_field_temporal_menu["menu"]
    m_tc.delete(0, "end")
    for s in menu_values_local:
        m_tc.add_command(label=s, command=lambda value=s: csv_field_relational_var.set(value))

    # Numeric tab menus
    m4 = csv_field_visualization_menu["menu"]
    m4.delete(0, "end")
    for s in menu_values_local:
        m4.add_command(label=s, command=lambda value=s: csv_field_visualization_var.set(value))

    m5 = X_axis_menu["menu"]
    m5.delete(0, "end")
    for s in menu_values_local:
        m5.add_command(label=s, command=lambda value=s: X_axis_var.set(value))

    m6 = Y_axis_menu["menu"]
    m6.delete(0, "end")
    for s in menu_values_local:
        m6.add_command(label=s, command=lambda value=s: Y_axis_var.set(value))

    m7 = csv_field_boxplot_menu["menu"]
    m7.delete(0, "end")
    for s in menu_values_local:
        m7.add_command(label=s, command=lambda value=s: csv_field_boxplot_var.set(value))

    m8 = csv_field_boxplot_color_menu["menu"]
    m8.delete(0, "end")
    for s in menu_values_local:
        m8.add_command(label=s, command=lambda value=s: csv_field_boxplot_color_var.set(value))

    m9 = X_axis_bubble_menu["menu"]
    m9.delete(0, "end")
    for s in menu_values_local:
        m9.add_command(label=s, command=lambda value=s: X_axis_bubble_var.set(value))

    clear("<Escape>")

def on_inputFilename_change(*args):
    f = GUI_util.inputFilename.get()
    if f.endswith('.csv'):
        input_csv_file_var.set(f)
    changed_filename(f)
GUI_util.inputFilename.trace('w', lambda x, y, z: on_inputFilename_change())


# ── activate_all_options ──────────────────────────────────────────────────────

def activate_all_options(*args):
    if error:
        return

    extra_GUIs_menu.configure(state='disabled')

    if extra_GUIs_var.get():
        extra_GUIs_menu.configure(state='normal')

    # Relational tab state based on relations_menu_var
    current_rel = relations_menu_var.get()
    dynamic_network_field_menu.configure(state='disabled')
    Sankey_limit1_menu.configure(state='disabled')
    Sankey_limit2_menu.configure(state='disabled')
    Sankey_limit3_menu.configure(state='disabled')

    if current_rel == '*':
        dynamic_network_field_menu.configure(state='normal')
        Sankey_limit1_menu.configure(state='normal')
        Sankey_limit2_menu.configure(state='normal')
        Sankey_limit3_menu.configure(state='normal')
        try:
            GephiDir, _, errorFound = IO_libraries_util.external_software_install('Gephi_util', 'Gephi', '', silent=True, errorFound=False)
            if GephiDir is None or GephiDir == '':
                mb.showwarning("Warning", "Gephi is not installed on this machine.\n\nThe '*' option will run Network graph (vis.js) and Sankey but will skip Gephi.\n\nYou can install Gephi from the Setup menu.")
        except Exception:
            mb.showwarning("Warning", "Gephi is not installed on this machine.\n\nThe '*' option will run Network graph (vis.js) and Sankey but will skip Gephi.\n\nYou can install Gephi from the Setup menu.")
    elif current_rel == 'Gephi' or current_rel == 'Network graph (vis.js)':
        dynamic_network_field_menu.configure(state='normal')
    elif current_rel == 'Sankey':
        Sankey_limit1_menu.configure(state='normal')
        Sankey_limit2_menu.configure(state='normal')
        Sankey_limit3_menu.configure(state='normal')

    # Categorical tab state
    add_file.configure(state='disabled')
    reset_file_button.configure(state='disabled')
    openInputFile_button_comparative.configure(state='disabled')
    csv_file_menu_comparative.configure(state='disabled')

    if categorical_menu_var.get() == 'Colormap/heatmap':
        max_rows.configure(state='normal')
        color_1_checkbox.configure(state='normal')
        color_2_checkbox.configure(state='normal')
        data_transformation_menu.configure(state='normal')
    else:
        max_rows.configure(state='disabled')
        color_1_checkbox.configure(state='disabled')
        color_2_checkbox.configure(state='disabled')
        data_transformation_menu.configure(state='disabled')

    if 'Comparative' in categorical_menu_var.get() or '*' in categorical_menu_var.get():
        add_file.configure(state='normal')
        reset_file_button.configure(state='normal')
        openInputFile_button_comparative.configure(state='normal')
        csv_file_menu_comparative.configure(state='normal')

    # Numeric tab state
    X_axis_menu.configure(state='disabled')
    Y_axis_menu.configure(state='disabled')
    add_Y_axis.configure(state='disabled')
    reset_Y_axis_button.configure(state='disabled')
    show_Y_axis_button.configure(state='disabled')
    points_menu.configure(state='disabled')
    split_data_byCategory_checkbox.configure(state='disabled')
    csv_field_boxplot_menu.configure(state='disabled')
    csv_field_boxplot_color_menu.configure(state='disabled')
    X_axis_bubble_menu.configure(state='disabled')

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
    if 'bubble' in visualizations_menu_var.get().lower():
        X_axis_bubble_menu.configure(state='normal')

activate_all_options()

relations_menu_var.trace('w', activate_all_options)
visualizations_menu_var.trace('w', activate_all_options)
categorical_menu_var.trace('w', activate_all_options)


# ── Run command (tab-aware) ───────────────────────────────────────────────────

def run_command():
    active_tab = notebook.index(notebook.select())
    inputFile = input_csv_file_var.get() if input_csv_file_var.get() else GUI_util.inputFilename.get()
    outputDir = GUI_util.output_dir_path.get()
    openOutputFiles = GUI_util.open_csv_output_checkbox.get()

    if active_tab == 0:  # Relational
        run_relational(inputFile, outputDir, openOutputFiles,
                       relations_menu_var.get(), csv_field_relational_var.get(),
                       csv_file_relational_field_list, dynamic_network_field_var.get(),
                       Sankey_limit1_var.get(), Sankey_limit2_var.get(), Sankey_limit3_var.get())
    elif active_tab == 1:  # Categorical
        run_categorical(inputFile, outputDir, openOutputFiles,
                        categorical_menu_var.get(), csv_field_categorical_var.get(),
                        case_sensitive_var.get(), csv_file_categorical_field_list,
                        filter_options_var.get(), fixed_param_var.get(), rate_param_var.get(), base_param_var.get(),
                        max_rows_var.get(), color_1_style_var.get(), color_2_style_var.get(), data_transformation_var.get(),
                        csv_files_list, csv_field_visualization_var.get())
    elif active_tab == 2:  # Temporal
        run_temporal(inputFile, outputDir, openOutputFiles,
                     csv_field_relational_var.get(), time_mapper_field_var.get(),
                     date_format_var.get(), time_var.get(), cumulative_var.get())
    elif active_tab == 3:  # Numeric
        run_numeric(inputFile, outputDir, openOutputFiles,
                    visualizations_menu_var.get(), csv_field_visualization_var.get(),
                    X_axis_var.get(), csv_file_field_Y_axis_list, points_var.get(),
                    split_data_byCategory_var.get(), csv_field_boxplot_var.get(),
                    csv_field_boxplot_color_var.get(), X_axis_bubble_var.get(),
                    color_1_style_var.get())

run_script_command = lambda: run_command()
GUI_util.run_button.configure(command=run_script_command)


# ── Clear ─────────────────────────────────────────────────────────────────────

def clear(e):
    extra_GUIs_var.set(0)
    extra_GUIs_menu_var.set('')
    input_csv_file_var.set('')
    relations_menu_var.set('Gephi')
    categorical_menu_var.set('Sunburst')
    csv_field_relational_var.set('')
    dynamic_network_field_var.set('')
    selected_csv_file_fields.set('')
    selected_csv_file_fields_var.set('')
    csv_file_relational_field_list.clear()
    csv_field_categorical_var.set('')
    search_values_categorical_var.set('')
    csv_file_categorical_field_list.clear()
    case_sensitive_var.set(1)
    fixed_param_var.set(15)
    rate_param_var.set(3)
    base_param_var.set(15)
    time_mapper_field_var.set('')
    date_format_var.set('mm-dd-yyyy')
    time_var.set('Daily')
    cumulative_var.set(0)
    visualizations_menu_var.set('Excel/Plotly charts')
    X_axis_var.set('')
    Y_axis_var.set('')
    csv_field_visualization_var.set('')
    csv_field_boxplot_var.set('')
    points_var.set('')
    split_data_byCategory_var.set(0)
    csv_field_boxplot_color_var.set('')
    csv_files_list.clear()
    csv_file_field_Y_axis_list.clear()
    activate_filtering_options()
    activate_all_options()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)


# ── TIPS, Videos, Help ────────────────────────────────────────────────────────

videos_lookup = {'Data visualization': 'https://youtu.be/EDKdurWa56g'}
videos_options = 'Data visualization'

TIPS_lookup = {
    "Network Graphs (via Gephi)": "TIPS_NLP_Gephi network graphs.pdf",
    "Network graph (vis.js)": "TIPS_NLP_Gephi network graphs.pdf",
    "Sankey chart": "TIPS_NLP_Charts - Sankey chart.pdf",
    "Stacked bar chart": "TIPS_NLP_Charts - Multiple bar charts.pdf",
    "Sunburst pie chart": "TIPS_NLP_Charts - Sunburst pie chart.pdf",
    "Colormap/heatmap chart": "TIPS_NLP_Charts - Colormap-heatmap.pdf",
    "Treemap chart": "TIPS_NLP_Charts - Treemap chart.pdf",
    "Boxplots": "TIPS_NLP_Charts - Boxplots.pdf",
    "Bubble chart": "TIPS_NLP_Charts - Bubble chart.pdf",
    "Multiple bar charts": "TIPS_NLP_Charts - Multiple bar charts.pdf",
    "Time mapper": "TIPS_NLP_Charts - Time mapper.pdf",
    "Word clouds": "TIPS_NLP_Wordclouds Visualizing word clouds.pdf",
    'Excel charts': 'TIPS_NLP_Excel Charts.pdf',
    'csv files - Problems & solutions': 'TIPS_NLP_csv files - Problems & solutions.pdf',
    'Statistical measures': 'TIPS_NLP_Statistical measures.pdf'
}

TIPS_options = ('Network Graphs (via Gephi)', 'Network graph (vis.js)', 'Sankey chart', 'Stacked bar chart',
                'Sunburst pie chart', 'Colormap/heatmap chart', 'Treemap chart', 'Boxplots', 'Bubble chart',
                'Multiple bar charts', 'Time mapper', 'Word clouds', 'Excel charts',
                'csv files - Problems & solutions', 'Statistical measures')

def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_CoNLL)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                                         'Please, tick the \'GUIs available\' checkbox if you wish to see and select the range of other available tools suitable for data visualization.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                                         'Please, click the \'Select INPUT CSV file\' button to select a csv file to visualize.\n\nThe csv file headers will be used to populate the dropdown menus for selecting the fields to be used for visualization.')
    # One help button at the top of the notebook area, then skip the rest
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                                         "Select a tab to choose the type of visualization you wish to produce.\n\n"
                                                         "RELATIONAL tab: Network graphs (Gephi, vis.js) and Sankey charts to visualize relationships between entities (e.g., Subject-Verb-Object).\n\n"
                                                         "CATEGORICAL tab: Colormap/heatmap, Comparative bar charts, Stacked bar, Sunburst, and Treemap charts to visualize categorical data.\n\n"
                                                         "TEMPORAL tab: Time mapper to visualize temporal data along a timeline.\n\n"
                                                         "NUMERIC tab: Excel/Plotly charts, Boxplots, and Bubble charts to visualize numeric/statistical data.")
    y_multiplier_integer += 6
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer - 1

y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

readMe_message = "The Python 3 script provides access to different types of data visualization: network graphs (Gephi, vis.js), Sankey charts, sunburst, treemap, colormap/heatmap, stacked bar charts, time mapper, boxplots, bubble charts, comparative bar charts, and Excel/Plotly charts.\n\nIn INPUT the algorithms expect a csv file.\n\nIn OUTPUT the algorithms produce different types of interactive html charts."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

activate_all_options()

GUI_util.window.mainloop()
