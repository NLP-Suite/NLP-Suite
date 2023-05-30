# Created on Thu Nov 21 09:45:47 2019
# @author: jack hester
# rewritten by Roberto Franzosi April 2020, Fall 2022

import sys
import GUI_util
import IO_libraries_util
if IO_libraries_util.install_all_Python_packages(GUI_util.window,"knowledge_graphs_DBpedia_YAGO_main.py",['os','tkinter','subprocess'])==False:
    sys.exit(0)

import os
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

import GUI_IO_util
import IO_files_util
import reminders_util
import constants_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,inputDir,outputDir, openOutputFiles, createCharts, chartPackage,
        knowledge_graphs_var,
        confidence_level,
        databases_var,
        sub_class_entry,
        ontology_list,
        create_HTML_files_var,
        ontology_color_list,
        bold_DBpedia_YAGO_var):

    if ontology_class_var.get()=='':
        msg = 'The "Ontology class" widget is empty.\n\nPlease, use the dropdown menu to select an Ontology class and try again.'
        if 'DBpedia' in knowledge_graphs_var:
            msg = msg + '\n\nFor DBpedia, select the "Thing" class to tag all classes.'
        mb.showwarning(title='Warning',
            message=msg)
        return

    # check file number, if too many file pop the warning.
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False, configFileName=config_filename)
    fileNum = len(inputDocs)
    if fileNum > 10:
        res = mb.askokcancel("File Number Warning",
                             "Your input directory contains more than 10 files. The annotation will take a significantly longer time (especially for YAGO), and the output will contain " +
                             str(fileNum) + " html files.\n\n Do you want to proceed? ")
        # stop the process if user click cancel
        if not res:
            return

    if knowledge_graphs_var!='':
        import IO_internet_util
        if not IO_internet_util.check_internet_availability_warning(knowledge_graphs_var):
            return

    if knowledge_graphs_var!='':
        if inputFilename!='' and inputFilename[-4:]!='.txt':
            mb.showwarning(title='Warning', message='You have selected to annotate your corpus, but the input file is not of type .txt as required by the selected annotator.\n\nPlease, select a .txt file (or a directory) and try again.')
            return

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label=knowledge_graphs_var,
                                                       silent=True)
    if outputDir == '':
        return

    # accept_DBpedia_YAGO_list performs a final check to make sure that any selected ontology classes/sub-classes have not been left dangling
    #   the same check is carried out when clicking on the button SHOW

    accept_DBpedia_YAGO_list()
    colorlist = list(color_map.values())

    if 'DBpedia' in knowledge_graphs_var:
        import knowledge_graphs_DBpedia_util
        # for a complete list of annotator types:
        #http://mappings.DBpedia.org/server/ontology/classes/
        filesToOpen = knowledge_graphs_DBpedia_util.DBpedia_annotate(inputFilename, inputDir,
                                                                     outputDir,config_filename, 0,
                                                                     ontology_list, colorlist, confidence_level)

    elif 'YAGO' in knowledge_graphs_var:
        import knowledge_graphs_YAGO_util
        # for a complete list of annotator types:
        #http://mappings.DBpedia.org/server/ontology/classes/
        color1='black'
        filesToOpen = knowledge_graphs_YAGO_util.YAGO_annotate(inputFilename, inputDir, outputDir,
                                                               config_filename,
                                                               ontology_list, color1, colorlist)

    else:
        mb.showwarning(title='Warning', message='There are no options selected.\n\nPlease, select one of the available options and try again.')
        return

    if openOutputFiles==True:
        if filesToOpen==None:
            if knowledge_graphs_var:
                print("\n" + knowledge_graphs_var + " exited with error")
            return
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
#def run(inputFilename,input_main_dir_path,outputDir, dictionary_var, annotator_dictionary, DBpedia_var, annotator_extractor, openOutputFiles):
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                GUI_util.input_main_dir_path.get(),
                GUI_util.output_dir_path.get(),
                GUI_util.open_csv_output_checkbox.get(),
                                                GUI_util.create_chart_output_checkbox.get(),
                                GUI_util.charts_package_options_widget.get(),

                knowledge_graphs_var.get(),
                confidence_level_entry.get(),
                databases_var.get(),
                sub_class_entry_var.get(),
                ontology_list,
                create_HTML_files_var.get(),
                ontology_color_list,
                bold_DBpedia_YAGO_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(3),
                                                 GUI_height_brief=480, # height at brief display
                                                 GUI_height_full=560, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=2, # to be added for full display
                                                 increment=2) # to be added for full display

GUI_label='Graphical User Interface (GUI) for HTML Annotating Documents Using the Knowledge Graphs (KG) DBpedia & YAGO'
head, scriptName = os.path.split(os.path.basename(__file__))
if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
    config_filename = 'NLP_default_IO_config.csv'
else:
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
config_input_output_numeric_options=[5,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

def clear(e):
    knowledge_graphs_var.set('')
    ontology_class_var.set('')
    sub_class_entry_var.set('')
    ontology_class.configure(state='disabled')
    sub_class_entry.configure(state='disabled')
    clear_ontology_list()
    ontology_color_list.clear()
    add_class_button.configure(state='disabled')
    show_class_color_button.configure(state='disabled')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

ontology_list=[]
ontology_color_list=[]
color_map = {}

# knowledge_graphs_DBpedia_var=tk.IntVar() # to annotate a document using DBpedia
# knowledge_graphs_YAGO_var=tk.IntVar() # to annotate a document using YAGO
confidence_level_var=tk.StringVar()
databases_var=tk.StringVar()
ontology_class_var = tk.StringVar()
sub_class_entry_var = tk.StringVar()
create_HTML_files_var = tk.IntVar()
color_palette_var= tk.StringVar() # the color selected for DBpedia/YAGO annotation
bold_DBpedia_YAGO_var= tk.IntVar() # display in bod the selected color selected for DBpedia/YAGO annotation

# http://mappings.dbpedia.org/server/ontology/classes/
# DBpedia_menu_options=(
#         'Thing',
#         'Activity',
#         'Agent',
#         'Algorithm'
#         'Altitude',
#         'AnatomicalStructure',
#         'Area',
#         'Award',
#         'Biomolecule',
#         'Blazon',
#         'Browser',
#         'ChartsPlacements',
#         'ChemicalSubstance',
#         'Cipher',
#         'Colour',
#         'Currency',
#         'Demographics',
#         'Depth',
#         'Device',
#         'Diploma',
#         'Disease',
#         'ElectionDiagram',
#         'ElectricalSubstation',
#         'EthnicGroup',
#         'Event',
#         'FileSystem',
#         'Flag',
#         'Food',
#         'GeneLocation',
#         'GrossDomesticProduct',
#         'GrossDomesticProductPerCapita',
#         'Holiday',
#         'Identifier',
#         'Language',
#         'List',
#         'MeanOfTransportation',
#         'Media',
#         'MedicalSpecialty',
#         'Medicine',
#         'Name',
#         'Person',
#         'Place',
#         'Population',
#         'Protocol',
#         'PublicService',
#         'Relationship',
#         'Species',
#         'SportCompetitionResult',
#         'SportsSeason',
#         'Spreadsheet',
#         'StarCluster',
#         'Statistic',
#         'Tank',
#         'TimePeriod',
#         'TopicalConcept',
#         'UnitOfWork',
#         'Unknown',
#         'Work')

# These are schema.org classes https://schema.org/docs/full.html
# YAGO_menu_options=(
#         'BioChemEntity', 	# bioschemas
#         'Gene',				# bioschemas
#         'MolecularEntity',	# bioschemas
#         'Taxon',			# bioschemas
#         'Brand',			# schema
#         'BroadcastChannel',	# schema
#         'CreativeWork',		# schema
#         'Emotion',			# yago
#         'MedicalEntity',	# schema
#         'Organization',		# schema
#         'Person',			# schema
#         'Place',			# schema
#         'Product')			# schema

# temporarily set DBpedia_YAGO_menu_options to avoid
#	is not defined error
# DBpedia_YAGO_menu_options=DBpedia_menu_options

y_multiplier_integerSV= y_multiplier_integer

knowledge_graphs_menu_lb = tk.Label(window, text='Knowledge bases (Knowledge graphs)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,knowledge_graphs_menu_lb,True)

knowledge_graphs_var=tk.StringVar()
knowledge_graphs_var.set('')
# knowledge_graphs_menu_options=('DBpedia','YAGO','Wikipedia') #, 'Wikidata'
knowledge_graphs_menu = tk.OptionMenu(window,knowledge_graphs_var,'DBpedia','YAGO','Wikipedia')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu,
                                               y_multiplier_integer,
                                               knowledge_graphs_menu, False, False, False, False, 90,
                                               GUI_IO_util.open_TIPS_x_coordinate,
                                               "Select the knowledge base/graph you wish to use")

# http://yago.r2.enst.fr/
# http://yago.r2.enst.fr/downloads/yago-4
# knowledge_graphs_YAGO_var.set(0)
# knowledge_graphs_YAGO_checkbox = tk.Checkbutton(window, text='HTML annotate corpus via YAGO',variable=knowledge_graphs_YAGO_var, onvalue=1, offvalue=0,command=lambda: activate_DBpedia_YAGO_menu())
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.setup_pop_up_text_widget,y_multiplier_integer,knowledge_graphs_YAGO_checkbox,True)

confidence_level_lb = tk.Label(window, text='DBpedia confidence level')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.knowledge_graphs_YAGO_checkbox_pos,y_multiplier_integerSV,confidence_level_lb,True)

confidence_level_entry = tk.Scale(window, from_=0.0, to=1.0, resolution = 0.1, orient=tk.HORIZONTAL)
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate+520,y_multiplier_integer,confidence_level_entry)
confidence_level_entry.set(.5)

y_multiplier_integer=y_multiplier_integerSV+1

def clear_ontology_list():
    ontology_class_var.set('')
    sub_class_entry_var.set('')
    ontology_list.clear()
    ontology_color_list.clear()
    color_map.clear()
    color_palette_var.set('')
    confidence_level_var.set('.5')
    reset_class_button.configure(state='disabled')
    activate_DBpedia_YAGO_Options(y_multiplier_integerSV,confidence_level_lb,confidence_level_entry)

def accept_DBpedia_YAGO_list():
    global ontology_list
    color = color_palette_var.get()
    if not color:
        color = 'blue'
    if sub_class_entry_var.get()!='':
        for token in sub_class_entry_var.get().split(' '):
            if token:
                if token not in str(ontology_list):
                    ontology_list.append(token)
                    color_map[token] = color
        # print(color_map)

        ontology_color_list.append(color)
        # ontology_list=[str(x) for x in sub_class_entry_var.get().split(',') if x]
    elif ontology_class_var.get() != '':
        color_map[ontology_class_var.get()] = color
        if ontology_class_var.get() not in str(ontology_list):
            ontology_list.append(ontology_class_var.get())
            ontology_color_list.append(color)

def add_DBpedia_YAGO_sub_class(*args):
    if sub_class_entry_var.get()!='':
        activate_DBpedia_YAGO_Options(y_multiplier_integerSV,confidence_level_lb,confidence_level_entry)
sub_class_entry_var.trace ('w',add_DBpedia_YAGO_sub_class)

# to jump to an item in the list that starts with a specific letter (e.g., without) by pressing that letter (e.g., w)
# https://stackoverflow.com/questions/32747592/can-you-have-a-tkinter-drop-down-menu-that-can-jump-to-an-entry-by-typing
# autocomplete
# https://stackoverflow.com/questions/12298159/tkinter-how-to-create-a-combo-box-with-autocompletion
# for the code
#   https://mail.python.org/pipermail/tkinter-discuss/2012-January/003041.html

# ontology_class = GUI_IO_util.combobox_with_search_widget(constants_util.DBpedia_ontology_class_menu)
ontology_class_lb = tk.Label(window, text='Ontology class')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,ontology_class_lb,True)

ontology_class_var.set('')
ontology_class = ttk.Combobox(window, state='disabled', width = GUI_IO_util.widget_width_long, textvariable = ontology_class_var)
# ontology_class['values'] = constants_util.DBpedia_ontology_class_menu
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu,
                                               y_multiplier_integer,
                                               ontology_class, False, False, False, False, 90,
                                               GUI_IO_util.IO_configuration_menu,
                                               "Using the dropdown menu, single click to select an ontology class; double click to expand an ontology class to all its sub-classes for further selection.")
def search_items(search_value):
    if knowledge_graphs_var.get()=='DBpedia':
        item_names=constants_util.DBpedia_ontology_class_menu
    else:
        item_names = constants_util.YAGO_ontology_class_menu
    if search_value == "" or search_value == " ":
        ontology_class['values'] = item_names
    else:
        value_to_display = []
        for value in item_names:
            if search_value in value.lower():
                value_to_display.append(value)
        ontology_class['values'] = value_to_display
        if len(value_to_display)>0:
            ontology_class.set(ontology_class['values'][0])

# https://stackoverflow.com/questions/27262580/tkinter-binding-mouse-double-click
def mouse_click(event):
    '''  delay mouse action to allow for double click to occur
    '''
    ontology_class.after(300, mouse_action, event)

def double_click(event):
    '''  set the double click status flag
    '''
    global double_click_flag
    double_click_flag = True

def mouse_action(event):
    global double_click_flag
    if double_click_flag:
        print('double mouse click event')
        double_click_flag = False
    else:
        print('single mouse click event')

# https://stackoverflow.com/questions/27262580/tkinter-binding-mouse-double-click
double_click_flag = False
ontology_class.bind('<Button-1>', mouse_click) # bind left mouse click
ontology_class.bind('<Double-1>', double_click) # bind double left clicks

search_variable = tk.StringVar()
search_entry = tk.Entry(window, state='disabled', width=GUI_IO_util.widget_width_long, textvariable=search_variable)
# place widget with hover-over info
# " + knowledge_graphs_var.get() + "
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu+20,
                                               y_multiplier_integer,
                                               search_entry, True, False, False, False, 90,
                                               GUI_IO_util.IO_configuration_menu+20,
                                               "Enter a string to be used for searching the list of ontology class values for case-insensitive substring matches")

search_button = tk.Button(window, text="Search", command=lambda: search_items(search_entry.get()))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.close_button_x_coordinate,
                                               y_multiplier_integer,
                                               search_button, False, False, False, False, 90,
                                               GUI_IO_util.open_setup_x_coordinate,
                                               "Click the Search button to search the list of ontology class values for the string entered")
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.close_button_x_coordinate, y_multiplier_integer,search_button)

sub_class_entry_lb = tk.Label(window, text='Ontology sub-class')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,sub_class_entry_lb,True)

sub_class_entry = tk.Entry(window,width=GUI_IO_util.knowledge_sub_class_entry_width,textvariable=sub_class_entry_var)
sub_class_entry.configure(state="disabled")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu,
                                               y_multiplier_integer,
                                               sub_class_entry, False, False, False, False, 90,
                                               GUI_IO_util.labels_x_indented_coordinate,
                                               "Enter the comma-separated ontology sub-classes you wish to use; get the sub-classes from the TIPS_NLP_DBpedia ontology classes.pdf or TIPS_NLP_YAGO (schema.org) Ontology Classes.pdf.")

create_HTML_files_var.set(0)
create_HTML_files_checkbox = tk.Checkbutton(window, text='Create HTML output files', state='disabled',variable=create_HTML_files_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_indented_coordinate,
                                               y_multiplier_integer,
                                               create_HTML_files_checkbox, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_indented_coordinate,
                                               "Create in output separate HTML files for every input txt file in addition to the default csv file output. Keep in mind that the process is relatively slow...")

bold_DBpedia_YAGO_var.set(1)
bold_DBpedia_YAGO_checkbox = tk.Checkbutton(window, text='Bold', state='disabled',variable=bold_DBpedia_YAGO_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu,
                                               y_multiplier_integer,
                                               bold_DBpedia_YAGO_checkbox, True, False, False, False, 90,
                                               GUI_IO_util.IO_configuration_menu,
                                               "When creating output HTML files, you can choose to annotate in bold a selected ontology class/sub-class (bold is typically more visible...)")

color_palette_var.set('')
color_palette_DBpedia_YAGO_lb = tk.Label(window, text='Color')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate,y_multiplier_integer,color_palette_DBpedia_YAGO_lb,True)
color_palette_DBpedia_YAGO_menu = tk.OptionMenu(window, color_palette_var,'black','blue','green','pink','red','yellow')
color_palette_DBpedia_YAGO_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate+50,
                                               y_multiplier_integer,
                                               color_palette_DBpedia_YAGO_menu, False, False, False, False, 90,
                                               GUI_IO_util.open_reminders_x_coordinate+50,
                                               "When creating output HTML files, you can choose a specific color for a specific ontology class... Default color is blue.")

add_class_button = tk.Button(window, text='+', width=GUI_IO_util.add_button_width,height=1,state='disabled',command=lambda: activate_class_var())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.knowledge_plus_button,
                                               y_multiplier_integer,
                                               add_class_button, True, False, False, False, 90,
                                               GUI_IO_util.knowledge_plus_button,
                                               "Click the + button to add another ontology class")

def activate_class_var():
    ontology_class.configure(state='normal')
    if ontology_class_var.get()!='' or sub_class_entry_var.get()!='':
        accept_DBpedia_YAGO_list()  # get current value and store into the dict
        add_class_button.configure(state='normal')
        show_class_color_button.configure(state='normal')
    else:
        add_class_button.configure(state='disabled')

reset_class_button = tk.Button(window, text='Reset', width=GUI_IO_util.reset_button_width,height=1,state='disabled',command=lambda: clear_ontology_list())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.knowledge_reset_button,
                                               y_multiplier_integer,
                                               reset_class_button, True, False, False, False, 90,
                                               GUI_IO_util.knowledge_reset_button,
                                               "Click the Reset button to clear all selected values")

def show_class_color_list():
    # accept_DBpedia_YAGO_list performs a final check to make sure that any selected ontology classes/sub-classes have not been left dangling
    #   the same check is carried out in RUN

    accept_DBpedia_YAGO_list()

    if not color_map:
        if color_palette_var.get()!='':
            mb.showwarning(title='Warning',
                       message='You have selected the color ' + color_palette_var.get() + ' for the ontology class ' + ontology_class_var.get() + '\n\nYou must press the + button to OK your selection.')
        else:
            mb.showwarning(title='Warning',
                       message='There are no currently selected combinations of ontology class and color.')
    else:
        class_color_string = ""
        for ont in color_map.keys():
            class_color_string = class_color_string + ont + ":" + color_map[ont] + "\n"
        # mb.showwarning(title='Warning', message='The currently selected combination of ontology classes and colors are:\n\n' + ','.join(ontology_color_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')
        mb.showwarning(title='Warning', message='The currently selected combination of ontology classes and colors are:\n\n' + class_color_string + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

show_class_color_button = tk.Button(window, text='Show', width=GUI_IO_util.show_button_width,height=1,state='disabled',command=lambda: show_class_color_list())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.knowledge_show_button,
                                               y_multiplier_integer,
                                               show_class_color_button, False, False, False, False, 90,
                                               GUI_IO_util.knowledge_show_button,
                                               "Click the Show button to see all selected options")

firstTime = False

# https://www.python.org/download/mac/tcltk/
# https://stackoverflow.com/questions/24207870/cant-reenable-menus-in-python-tkinter-on-mac
# In Mac, widgets are temporarily turned disabled but immediately return to normal. This is a bug in the Apple-supplied Tk 8.5. The Cocoa versions of Tk that Apple has been shipping since OS X 10.6 have had numerous problems many of which have been fixed in more recent versions of Tk 8.5. With the current ActiveTcl 8.5.15, your test appears to work correctly. Unfortunately, you can't easily change the version of Tcl/Tk that the Apple-supplied system Pythons use. One option is to install the current Python 2.7.7 from the python.org binary installer along with ActiveTcl 8.5.15. There is more information here:

# https://www.python.org/downloads/

def activate_class_options(*args):
    if ontology_class_var.get() in ontology_list:
        mb.showwarning(title='Warning', message='The class "'+ ontology_class_var.get() + '" is already in your selection list: '+ str(ontology_list) + '.\n\nPlease, select another class.')
        window.focus_force()
        return
    state = str(ontology_class['state'])
    if state != 'disabled':
        if ontology_class_var.get() != '':
            if ontology_class_var.get() not in str(ontology_list):
                ontology_list.append(ontology_class_var.get())
            add_class_button.configure(state='normal')
            reset_class_button.configure(state='normal')
            show_class_color_button.configure(state='normal')
            ontology_class.configure(state='disabled')
            # sub_class_entry.configure(state="disabled")
            color_palette_DBpedia_YAGO_menu.configure(state='normal')
            if color_palette_var.get() != '':
                add_class_button.configure(state='normal')
            # color palette ONLY available when selecting a major ontology class from the dropdown menu
            # color_palette_DBpedia_YAGO_menu.configure(state='normal')
        else:
            color_palette_DBpedia_YAGO_menu.configure(state='disabled')
    else:
        reset_class_button.configure(state='normal')
        if sub_class_entry_var.get() != '':
            ontology_class.configure(state='disabled')
        else:
            ontology_class.configure(state='normal')
ontology_class_var.trace ('w',activate_class_options)

def activate_class_color_combo(*args):
    accept_DBpedia_YAGO_list()  # get current value and store into the dict
    if color_palette_var.get()!='':
        # accept_DBpedia_YAGO_list()  # get current value and store into the dict
        state = str(color_palette_DBpedia_YAGO_menu['state'])
        # 'active' for mac; 'normal' for windows
        if state != 'disabled': # normal/active
            color_palette_DBpedia_YAGO_menu.configure(state='disabled')
            add_class_button.configure(state='normal')
            reset_class_button.configure(state='normal')
            show_class_color_button.configure(state='normal')
    # else:
    #     accept_DBpedia_YAGO_list()  # get current value and store into the dict
color_palette_var.trace('w',activate_class_color_combo)

def activate_DBpedia_YAGO_Options(y_multiplier_integerSV,confidence_level_lb,confidence_level_entry,*args):
    global firstTime, knowledge_graphs_YAGO_checkbox
    if not 'DBpedia' in knowledge_graphs_var.get() and not 'YAGO' in knowledge_graphs_var.get() and not 'Wiki' in knowledge_graphs_var.get():
        ontology_list.clear()
        ontology_color_list.clear()
        ontology_class_var.set('') # DBpedia_YAGO_menu_options
    else:
        ontology_class.configure(state='normal')
    if 'DBpedia' in knowledge_graphs_var.get():
        ontology_class['values'] = constants_util.DBpedia_ontology_class_menu
        y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate,
                                                       y_multiplier_integerSV, confidence_level_lb,True)
        # place widget with hover-over info
        y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.confidence_level_entry_pos,
                                                       y_multiplier_integerSV,
                                                       confidence_level_entry, False, False, False, False, 90,
                                                       GUI_IO_util.open_TIPS_x_coordinate,
                                                       "DBpedia allows you to set confidence levels for your annotation (.5 is the recommended default value in a range between 0 and 1).\nThe higher the confidence level the less likely you are to find DBpedia entries; the lower the level and the more likely you are to find extraneous entries")

    else:
        confidence_level_lb.place_forget()  # invisible
        confidence_level_entry.place_forget()  # invisible
    if 'YAGO' in knowledge_graphs_var.get():
        ontology_class['values'] = constants_util.YAGO_ontology_class_menu
    if 'DBpedia' in knowledge_graphs_var.get() or 'YAGO' in knowledge_graphs_var.get():
        # display the reminder only once in the same GUI or the trace will display it many times
        if firstTime==False:
            reminders_util.checkReminder(scriptName,
                                         reminders_util.title_options_DBpedia_YAGO,
                                         reminders_util.message_DBpedia_YAGO,
                                         True)
        firstTime=True
        ontology_class.configure(state='normal')
        search_entry.configure(state="normal")
        # sub_class_entry.configure(state="normal")
    else:
        ontology_class.configure(state='disabled')
        search_entry.configure(state="disabled")
        # sub_class_entry.configure(state="disabled")
knowledge_graphs_var.trace('w',callback = lambda x,y,z: activate_DBpedia_YAGO_Options(y_multiplier_integerSV,confidence_level_lb,confidence_level_entry))

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf','Statistical measures':'TIPS_NLP_Statistical measures.pdf','Annotator':'TIPS_NLP_Annotator.pdf','Annotator DBpedia':'TIPS_NLP_Annotator DBpedia.pdf','DBpedia ontology classes':'TIPS_NLP_Annotator DBpedia ontology classes.pdf','YAGO (schema.org) ontology classes':'TIPS_NLP_Annotator YAGO (schema.org) ontology classes.pdf','YAGO (REDUCED schema.org) ontology classes':'TIPS_NLP_Annotator YAGO (schema reduced).pdf','The world of emotions and sentiments':'TIPS_NLP_The world of emotions and sentiments.pdf','W3C, OWL, RDF, SPARQL':'TIPS_NLP_W3C OWL RDF SPARQL.pdf','Annotator dictionary':'TIPS_NLP_Annotator dictionary.pdf','Annotator extractor':'TIPS_NLP_Annotator extractor.pdf','Gender annotator':'TIPS_NLP_Gender annotator.pdf'}
TIPS_options='csv files - Problems & solutions','Statistical measures','Annotator','Annotator DBpedia','DBpedia ontology classes','YAGO (schema.org) ontology classes','YAGO (REDUCED schema.org) ontology classes','The world of emotions and sentiments','W3C, OWL, RDF, SPARQL', 'Annotator dictionary','Annotator extractor','Gender annotator'
# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, using the dropdown menu, select the knowledge base/graph, DBpedia, YAGO, or Wikipedia, you wish to use to annotate the input corpus by terms found in either DBpedia or YAGO.\n\nDBpedia will allow you to set confidence levels for your annotation (.5 is the recommended default value in a range between 0 and 1). THE HIGHER THE CONFIDENCE LEVEL THE LESS LIKELY YOU ARE TO FIND DBpedia ENTRIES; THE LOWER THE LEVEL AND THE MORE LIKELY YOU ARE TO FIND EXTRANEOUS ENTRIES.\n\nDBpedia and YAGO are enormous databases (DB for database) designed to extract structured content from the information created in Wikipedia, Wikidata and other knowledge bases. DBpedia and YAGO allow users to semantically query relationships and properties of Wikipedia data (including links to other related datasets) via a large ontology of search values (for a complete listing, see the TIPS files TIPS_NLP_DBpedia Ontology Classes.pdf or TIPS_NLP_YAGO (schema.org) Ontology Classes.pdf).\n\nFor more information, see https://wiki.DBpedia.org/ and https://yago-knowledge.org/.\n\nIn INPUT the scripts expect one or more txt files.\n\nIn OUTPUT the scripts generate as many annotated html files as selected in input.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Once you select DBpedia or YAGO, the "Ontology class" options will become available.\n\nUsing the class dropdown menu, select the DPpedia or YAGO ontology class you wish to use.\n\nYou can add multiple ontology classes by pressing the + button.\n\nIF NO CLASS IS SELECTED, ALL CLASSES WILL BE PROCESSED, WITH \'THING\' AS THE DEFAULT CLASS.\n\nThe class dropdown menu only includes the main classes in the DBpedia or YAGO ontology. For specific sub-classes, please, get the values from the TIPS_NLP_DBpedia ontology classes.pdf or TIPS_NLP_YAGO (schema.org) Ontology Classes.pdf and enter them, comma-separated, in Ontology sub-class field. CLICK + AFTER ENTERING CLASS AND/OR SUB-CLASS VALUES.\n\nYAGO DOES NOT USE THE COMPLETE SCHEMA CLASSES AND SUB-CLASSES. PLEASE, REFER TO THE REDUCED LIST FOR ALL THE SCHEMA CLASSES USED.\n\nYou can test the resulting annotations directly on DBpedia Spotlight at https://www.dbpedia-spotlight.org/demo/\n\nYou can select a specific color for a specific ontology class; default color is blue (Press the \'Show\' widget to display the combination of selected values).\n\nPress RESET (or ESCape) to delete all values entered and start fresh.\nPress SHOW to display all selected values.\n\nThe +, RESET, and SHOW widgets become available only after selecting an ontology class or sub-class.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Enter a string to be used for searching the list of DBpedia or YAGO ontology classes, then click on the Search button.\n\nWhen the search item is found, the list in the Ontology class dropdown menu will be updated to a new list of found items.\n\nThe class list will be searched case insensitive.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Once you select DBpedia or YAGO, the "Ontology sub-class" widget will become available.\n\nSince the ontology class dropdown menu only includes the main classes in the DBpedia or YAGO ontology, enter in the "Ontology sub-class" widget more specific, comma-separated, sub-classes. You obtain these sub-classes from the TIPS_NLP_DBpedia ontology classes.pdf or TIPS_NLP_YAGO (schema.org).')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, tick the checkbox to create separate annotated HTML files in output in addition to a csv file.\n\nKeep in mind that the process of annotating files is slow and that the algorithm will create in output as many HTML annotated files as there are txt files in input.\n\nWhen creating HTML files, you can select to tag in bold and in a selected color a specific ontology class (default color is blue).\n\nThe options in this line become available only after selecting a specific ontology class.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Press the + button to add another ontology class.\n\nPress RESET (or ESCape) to delete all values entered and start fresh.\n\nPress SHOW to display all selected values.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1

y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 scripts provide ways of annotating text files for matching terms found in the knowledge graphs DBpedia or YAGO.\n\nDBpedia and YAGO tags can be selected from the class dropdown menu containing the DBpedia and YAGO ontology. The menu only includes the main classes in the ontology. For specific sub-classes, please, get the values from the TIPS_NLP_DBpedia ontology classes.pdf or TIPS_NLP_YAGO (schema.org) ontology classes.pdf and enter them in the Ontology sub-class field.\n\nIn INPUT the algorithms expect a txt file or a set of txt files in a directory.\n\nIn OUTPUT, the algorithms produce a csv file with a list of words annottate for a specific ontology class and document."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()

