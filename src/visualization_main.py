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

def run(inputFilename, inputDir, outputDir, openOutputFiles):
    if Gephi_var==False:
        mb.showwarning("Warning",
                       "No options have been selected.\n\nPlease, select an option to run and try again.")
        return

    inputFileBase = os.path.basename(inputFilename)[0:-4]  # without .csv

    gexf_file = Gephi_util.create_gexf(inputFileBase, outputDir, inputFilename)
    filesToOpen.append(gexf_file)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_width=1200
GUI_height=600 # height of GUI with full I/O display

if IO_setup_display_brief:
    GUI_height = GUI_height - 80
    y_multiplier_integer = GUI_util.y_multiplier_integer  # IO BRIEF display
    increment=0 # used in the display of HELP messages
else: # full display
    # GUI CHANGES add following lines to every special GUI
    # +3 is the number of lines starting at 1 of IO widgets
    # y_multiplier_integer=GUI_util.y_multiplier_integer+2
    y_multiplier_integer = GUI_util.y_multiplier_integer + 2  # IO FULL display
    increment=2

GUI_size = str(GUI_width) + 'x' + str(GUI_height)

GUI_label='Graphical User Interface (GUI) for Visualization Tools'
config_filename='visualization-config.txt'
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
config_option=[0,3,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_options,config_filename,IO_setup_display_brief)

def clear(e):
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)


Gephi_var = tk.IntVar()
selected_csv_file_fields_var = tk.StringVar()

csv_file_field_list = []
menu_values = []

Excel_button = tk.Button(window, text='Open Excel GUI', width=GUI_IO_util.select_file_directory_button_width, height=1,
                               command=lambda: call("python Excel_charts_main.py", shell=True))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               Excel_button)

GIS_button = tk.Button(window, text='Open GIS GUI', width=GUI_IO_util.select_file_directory_button_width, height=1,
                               command=lambda: call("python GIS_main.py", shell=True))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               GIS_button)

HTML_button = tk.Button(window, text='Open HTML annotator GUI', width=GUI_IO_util.select_file_directory_button_width, height=1,
                               command=lambda: call("python annotator_main.py", shell=True))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               HTML_button)

wordcloud_button = tk.Button(window, text='Open wordcloud GUI', width=GUI_IO_util.select_file_directory_button_width, height=1,
                               command=lambda: call("python wordclouds_main.py", shell=True))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               wordcloud_button)

Gephi_var.set(0)
Gephi_checkbox = tk.Checkbutton(window, text='Visualize relations in a Gephi network graph', variable=Gephi_var,
                                    onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               Gephi_checkbox)

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
    m1 = select_csv_field_menu["menu"]
    m1.delete(0, "end")

    for s in menu_values:
        m1.add_command(label=s, command=lambda value=s: csv_field_var.set(value))
    clear("<Escape>")

select_csv_field_lb = tk.Label(window, text='Select csv file field')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate(), y_multiplier_integer,
                                               select_csv_field_lb, True)

csv_field_var = tk.StringVar()
select_csv_field_menu = tk.OptionMenu(window, csv_field_var, *menu_values)
select_csv_field_menu.configure(state='disabled', width=12)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate()+150, y_multiplier_integer,
                                               select_csv_field_menu, True)

GUI_util.inputFilename.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))

changed_filename(GUI_util.inputFilename.get())

def activate_csv_fields_selection(comingFrom_Plus, comingFrom_OK):

    select_csv_field_menu.config(state='normal')
    if csv_field_var.get() != '':
        select_csv_field_menu.config(state='disabled')
        add_options.config(state='normal')
        OK_button.config(state='normal')
        reset_button.config(state='normal')
        if comingFrom_Plus == True:
            select_csv_field_menu.configure(state='normal')
        if comingFrom_OK == True:
            select_csv_field_menu.configure(state='disabled')
            add_options.config(state='disabled')
            OK_button.config(state='disabled')

    # clear content of current variables when selecting a different main option
    # csv_file_field_list.clear()

Gephi_var.trace('w', callback = lambda x,y,z: activate_csv_fields_selection(False,False))
csv_field_var.trace('w', callback = lambda x,y,z: activate_csv_fields_selection(True,False))

add_options_var = tk.IntVar()
add_options = tk.Button(window, text='+', width=2, height=1, state='disabled',
                              command=lambda: add_field_to_list(selected_csv_file_fields_var.get()))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 500, y_multiplier_integer,
                                               add_options, True)

OK_button = tk.Button(window, text='OK', width=3, height=1, state='disabled',
                            command=lambda: display_selected_csv_fields())
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 550, y_multiplier_integer,
                                               OK_button,True)

reset_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: reset())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 600,y_multiplier_integer,reset_button)

csv_file_fields=tk.Entry(window, width=150,textvariable=selected_csv_file_fields_var)
csv_file_fields.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate(), y_multiplier_integer,csv_file_fields)

def add_field_to_list(m):
    if not csv_field_var.get() in csv_file_field_list:
        csv_file_field_list.append(csv_field_var.get())

def display_selected_csv_fields():
    if not csv_field_var.get() in csv_file_field_list:
        csv_file_field_list.append(csv_field_var.get())
    selected_csv_file_fields_var.set(str(csv_file_field_list))
    reset_button.config(state="normal")

def reset():
    csv_field_var.set('')
    csv_file_field_list.clear()
    selected_csv_file_fields_var.set('')

TIPS_lookup = {"Lemmas & stopwords":"TIPS_NLP_NLP Basic Language.pdf", "Word clouds":"TIPS_NLP_Wordclouds Visualizing word clouds.pdf","Wordle":"TIPS_NLP_Wordclouds Wordle.pdf","Tagxedo":"TIPS_NLP_Wordclouds Tagxedo.pdf","Tagcrowd":"TIPS_NLP_Wordclouds Tagcrowd.pdf"}
TIPS_options='Lemmas & stopwords', 'Word clouds', 'Tagcrowd', 'Tagxedo', 'Wordle'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    resetAll = "\n\nPress the RESET button to clear all selected values, and start fresh."
    plusButton = "\n\nPress the + buttons, when available, to add a new field."
    OKButton = "\n\nPress the OK button, when available, to accept the selections made, then press the RUN button to process the query."
    if not IO_setup_display_brief:
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",GUI_IO_util.msg_CoNLL)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_corpusData)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help",GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+1),"Help","Please, click on the button to open the Excel GUI.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+2),"Help","Please, click on the button to open the GIS GUI.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+3),"Help","Please, click on the button to open the HTML annotator GUI.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+4),"Help","Please, click on the button to open the wordcloud GUI.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+5),"Help","Please, tick the checkbox if you wish to visualize a network graph in Gephi.\n\nOptions become available in succession.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+6),"Help","\n\nOptions become available in succession." + plusButton + OKButton + resetAll)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+7),"Help","\n\nThe widget is always disabled; it is for display only. When pressing OK, the selected csv fields will be displayed." + plusButton + OKButton + resetAll)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+8),"Help",GUI_IO_util.msg_openOutputFiles)
help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The Python 3 script and online services display the content of text files as word cloud.\n\nA word cloud, also known as text cloud or tag cloud, is a collection of words depicted visually in different sizes (and colors). The bigger and bolder the word appears, the more often it’s mentioned within a given text and the more important it is.\n\nDifferent, freeware, word cloud applications are available: 'TagCrowd', 'Tagul', 'Tagxedo', 'Wordclouds', and 'Wordle'. These applications require internet connection.\n\nThe script also provides Python word clouds (via Andreas Mueller's Python package WordCloud https://amueller.github.io/word_cloud/) for which no internet connection is required."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup, TIPS_options, IO_setup_display_brief)

GUI_util.window.mainloop()
