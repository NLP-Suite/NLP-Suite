import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"html_annotator_main.py",['os','tkinter','subprocess'])==False:
    sys.exit(0)

import os
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_files_util
import IO_csv_util
import reminders_util
import constants_util
import html_annotator_dictionary_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,input_main_dir_path,outputDir, openOutputFiles, createCharts, chartPackage,
        knowledge_graphs_DBpedia_YAGO_var,
        knowledge_graphs_WordNet_var,
        html_gender_annotator_var,
        html_annotator_dictionary_var,
        html_annotator_add_dictionary_var,
        html_dictionary_file,
        csv_field1_var,
        csv_field2_var,
        color_palette_dict_var,
        bold_var,
        csvValue_color_list,
        html_annotator_extractor):

    filesToOpen=[]

    if knowledge_graphs_DBpedia_YAGO_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('knowledge_graphs_DBpedia_YAGO_main.py') == False:
            return
        call("python knowledge_graphs_DBpedia_YAGO_main.py", shell=True)

    if knowledge_graphs_WordNet_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('knowledge_graphs_WordNet_main.py') == False:
            return
        call("python knowledge_graphs_WordNet_main.py", shell=True)

    if html_annotator_add_dictionary_var==True or html_annotator_extractor==True:
        if inputFilename!='' and inputFilename[-5:]!='.html':
            mb.showwarning(title='Warning', message='You have selected to run an option that requires an input file of type .html.\n\nPlease, select an .html file (or a directory) and try again.')
            return

    if html_annotator_dictionary_var==True or html_annotator_add_dictionary_var==True and html_dictionary_file=='':
        if html_dictionary_file=='':
            mb.showwarning(title='Warning', message='You have selected to annotate your corpus using dictionary entries, but you have not provided the required .csv dictionary file.\n\nPlease, select a .csv dictionary file and try again.')
            return

    if color_palette_dict_var=='':
        color_palette_dict_var='red' # default color, if forgotten

    if bold_var==True:
        tagAnnotations = ['<span style=\"color: ' + color_palette_dict_var + '; font-weight: bold\">','</span>']
    else:
        tagAnnotations = ['<span style=\"color: ' + color_palette_dict_var + '\">','</span>']

    if html_annotator_dictionary_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('html_annotator_dictionary_util.py')==False:
            return
        if csv_field2_var=='':
            csvValue_color_list=[]
        filesToOpen = html_annotator_dictionary_util.dictionary_annotate(inputFilename, input_main_dir_path, outputDir, config_filename, html_dictionary_file, csv_field1_var, csvValue_color_list, bold_var, tagAnnotations, '.txt','')
    elif html_annotator_add_dictionary_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('html_annotator_dictionary_util.py')==False:
            return
        filesToOpen = html_annotator_dictionary_util.dictionary_annotate(inputFilename, input_main_dir_path, outputDir, config_filename, html_dictionary_file, csv_field1_var, csvValue_color_list, bold_var, tagAnnotations, '.html','')
    elif html_annotator_extractor==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('html_annotator_extractor_util.py')==False:
            return
        import html_annotator_extractor_util
        html_annotator_extractor_util.buildcsv(inputFilename, input_main_dir_path, outputDir,openOutputFiles,createCharts, chartPackage, config_filename)
    elif html_gender_annotator_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('html_annotator_gender_main.py')==False:
            return
        call("python html_annotator_gender_main.py", shell=True)
    else:
        mb.showwarning(title='Warning', message='There are no options selected.\n\nPlease, select one of the available options and try again.')
        return

    if openOutputFiles==True:
        if filesToOpen!=None:
            nFile=len(filesToOpen)
            if nFile > 5:
                mb.showwarning(title='Warning', message='There are too many output files (' + str(nFile) + ') to be opened automatically.\n\nPlease, do not forget to check the HTML files in your selected output directory.')
                return
            else:
                IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
#def run(inputFilename,input_main_dir_path,outputDir, dictionary_var, annotator_dictionary, DBpedia_var, annotator_extractor, openOutputFiles):
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                GUI_util.input_main_dir_path.get(),
                GUI_util.output_dir_path.get(),
                GUI_util.open_csv_output_checkbox.get(),
                GUI_util.create_chart_output_checkbox.get(),
                GUI_util.charts_package_options_widget.get(),
                knowledge_graphs_DBpedia_YAGO_var.get(),
                knowledge_graphs_WordNet_var.get(),
                html_gender_annotator_var.get(),
                html_annotator_dictionary_var.get(),
                html_annotator_add_dictionary_var.get(),
                html_annotator_dictionary_file_var.get(),
                csv_field1_var.get(),
                csv_field2_var.get(),
                color_palette_dict_var.get(),
                bold_dict_var.get(),
                csvValue_color_list,
                html_annotator_extractor_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(3),
                                                 GUI_height_brief=520, # height at brief display
                                                 GUI_height_full=600, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=2, # to be added for full display
                                                 increment=2) # to be added for full display

GUI_label='Graphical User Interface (GUI) for Annotating Documents in HTML Format'
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
config_input_output_numeric_options=[5,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

def clear(e):
    clear_dictionary_list()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

csvValue_color_list=[]

knowledge_graphs_DBpedia_YAGO_var=tk.IntVar() # to annotate a document using DBpedia
knowledge_graphs_WordNet_var=tk.IntVar() # to annotate a document using DBpedia
html_gender_annotator_var=tk.IntVar()

html_annotator_dictionary_var=tk.IntVar() # to annotate a document using a dictionary
csv_field1_var=tk.StringVar()
csv_field2_var=tk.StringVar()
csv_field_value_var=tk.StringVar()
color_palette_DBpedia_YAGO_var= tk.StringVar() # the color selected for DBpedia/YAGO annotation
bold_DBpedia_YAGO_var= tk.IntVar() # display in bod the selected color selected for DBpedia/YAGO annotation
color_palette_dict_var= tk.StringVar() # the color selected for dictionary annotation
bold_dict_var= tk.IntVar() # display in bod the selected color selected for dictionary annotation
html_annotator_add_dictionary_var=tk.IntVar() # to add new annotations via dictionary to an already annotated document
html_annotator_dictionary_file_var=tk.StringVar() # dictionary file used to annotate
html_annotator_extractor_var=tk.IntVar() # to extract annotations in csv format from an annotated file

knowledge_graphs_DBpedia_YAGO_button = tk.Button(window, width=GUI_IO_util.widget_width_long, text='HTML annotate corpus using the DBpedia & YAGO knowledge graphs (Open GUI)', command=lambda: call("python knowledge_graphs_DBpedia_YAGO_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   knowledge_graphs_DBpedia_YAGO_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

knowledge_graphs_WordNet_button = tk.Button(window, width=GUI_IO_util.widget_width_long, text='HTML annotate corpus using the WordNet knowledge graphs (Open GUI)', command=lambda: call("python knowledge_graphs_WordNet_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   knowledge_graphs_WordNet_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

# http://yago.r2.enst.fr/
# http://yago.r2.enst.fr/downloads/yago-4

def clear_dictionary_list():
    csv_field1_var.set('')
    csv_field2_var.set('')
    csv_field1_menu.configure(state="normal")
    csv_field2_menu.configure(state="normal")
    csv_field_value_var.set('')
    csv_field_value_menu.configure(state='normal')
    csvValue_color_list.clear()

html_gender_annotator_button = tk.Button(window, width=GUI_IO_util.widget_width_long, text='HTML gender annotator (Open GUI)',  command=lambda: call("python html_annotator_gender_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   html_gender_annotator_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

html_dictionary_annotator_checkbox = tk.Checkbutton(window, text='HTML annotate corpus using csv dictionary',  variable=html_annotator_dictionary_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,html_dictionary_annotator_checkbox,True)

html_annotator_add_dictionary_var.set(0)
html_annotator_add_dictionary_checkbox = tk.Checkbutton(window, text='Add annotations to a previously annotated HTML file using csv dictionary', variable=html_annotator_add_dictionary_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.html_annotator_add_dictionary_description,y_multiplier_integer,html_annotator_add_dictionary_checkbox)

annotator_dictionary_button=tk.Button(window, width=20, text='Select csv dictionary file',command=lambda: get_dictionary_file(window,'Select INPUT csv dictionary file', [("dictionary files", "*.csv")]))
annotator_dictionary_button.config(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   annotator_dictionary_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Click on the button to select the dictionary file")

#setup a button to open Windows Explorer on the selected input directory
current_y_multiplier_integer=y_multiplier_integer-1
openInputFile_button  = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, state='disabled', text='', command=lambda: IO_files_util.openFile(window, html_annotator_dictionary_file.get()))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,
    GUI_IO_util.html_annotator_openInputFile_button, y_multiplier_integer,
    openInputFile_button, True, False, True, False, 90, GUI_IO_util.html_annotator_openInputFile_button, "Open displayed csv dictionary file")

html_annotator_dictionary_file=tk.Entry(window, width=GUI_IO_util.html_annotator_dictionary_width,textvariable=html_annotator_dictionary_file_var)
html_annotator_dictionary_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.html_annotator_dictionary_file_button, y_multiplier_integer,html_annotator_dictionary_file)

menu_values=''
if os.path.isfile(html_annotator_dictionary_file.get()):
    if html_annotator_dictionary_file.get().endswith('csv'):
        menu_values=IO_csv_util.get_csvfile_headers(html_annotator_dictionary_file.get())

field_lb = tk.Label(window, text='Select csv field 1')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,field_lb,True)
if menu_values!='':
    csv_field1_menu = tk.OptionMenu(window, csv_field1_var, *menu_values)
else:
    csv_field1_menu = tk.OptionMenu(window, csv_field1_var, menu_values)
csv_field1_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.html_annotator_csv_field1_menu,y_multiplier_integer,csv_field1_menu,True)

add_dictValue_button = tk.Button(window, text='+', width=2,height=1,state='disabled',command=lambda: csv_field_value_menu.configure(state="normal"))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.html_annotator_add_dictValue_button,y_multiplier_integer,add_dictValue_button, True)

reset_dictValue_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: clear_dictionary_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.html_annotator_reset_dictValue_button,y_multiplier_integer,reset_dictValue_button,True)

def showKeywordList():
    if len(csvValue_color_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected combinations of csv field values and colors.')
    else:
        mb.showwarning(title='Warning', message='The currently selected combination of csv field values and colors are:\n\n' + ','.join(csvValue_color_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

show_keywords_button = tk.Button(window, text='Show', width=5,height=1,state='disabled',command=lambda: showKeywordList())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.html_annotator_show_keywords_button,y_multiplier_integer,show_keywords_button,True)

# OK_button = tk.Button(window, text='OK', width=3,height=1,state='disabled',command=lambda: accept_keyword_list())
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+330,y_multiplier_integer,OK_button,True)

field2_lb = tk.Label(window, text='Select csv field 2')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.html_annotator_csv_field2_lb,y_multiplier_integer,field2_lb,True)
if menu_values!='':
    csv_field2_menu = tk.OptionMenu(window, csv_field2_var, *menu_values)
else:
    csv_field2_menu = tk.OptionMenu(window, csv_field2_var, menu_values)
csv_field2_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.html_annotator_csv_field2_menu,y_multiplier_integer,csv_field2_menu,True)

value_lb = tk.Label(window, text='Select csv field value ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.html_annotator_value_lb,y_multiplier_integer,value_lb,True)
if menu_values!='':
    csv_field_value_menu = tk.OptionMenu(window, csv_field_value_var, *menu_values)
else:
    csv_field_value_menu = tk.OptionMenu(window, csv_field_value_var, menu_values)
csv_field_value_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.html_annotator_csv_field_value_menu,y_multiplier_integer,csv_field_value_menu,True)

def changed_dictionary_filename(*args):
    csvValue_color_list.clear()
    csv_field1_var.set('')
    csv_field2_var.set('')
    csv_field_value_var.set('')
    color_palette_dict_var.set('')
    # menu_values is the number of headers in the csv dictionary file
    menu_values = ''
    if os.path.isfile(html_annotator_dictionary_file.get()):
        if html_annotator_dictionary_file.get().endswith('csv'):
            menu_values=IO_csv_util.get_csvfile_headers(html_annotator_dictionary_file.get())
        else:
            return
    m = csv_field1_menu["menu"]
    m.delete(0,"end")
    for s in menu_values:
        m.add_command(label=s,command=lambda value=s:csv_field1_var.set(value))

    if len(menu_values)>1:
        m1 = csv_field2_menu["menu"]
        m1.delete(0,"end")
        for s in menu_values:
            m1.add_command(label=s,command=lambda value=s:csv_field2_var.set(value))

    # set default value of csv_field1_var to
    #	first column of csv file
    if len(menu_values)>0:
        csv_field1_var.set(menu_values[0])
        if len(menu_values)>1:
            csv_field2_menu.configure(state='normal')
        else:
            csv_field2_menu.configure(state='disabled')
html_annotator_dictionary_file_var.trace('w',changed_dictionary_filename)

changed_dictionary_filename()

if csv_field2_var.get()!='':
    menu_field_values = IO_csv_util.get_csv_field_values(html_annotator_dictionary_file.get(), csv_field2_var.get())
else:
    menu_field_values = IO_csv_util.get_csv_field_values(html_annotator_dictionary_file.get(), csv_field1_var.get())

color_menu=['black','blue','green','pink','red','yellow']

color_palette_dict_lb = tk.Label(window, text='Select color')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.html_annotator_color_palette_dict_lb,y_multiplier_integer,color_palette_dict_lb,True)
color_palette_dict_menu = tk.OptionMenu(window, color_palette_dict_var,*color_menu)
color_palette_dict_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.html_annotator_color_palette_dict_menu, y_multiplier_integer,color_palette_dict_menu, True)

def get_csv_fieldValues(*args):
    csv_field_value_var.set('')
    color_palette_dict_menu.configure(state='normal')
    if os.path.isfile(html_annotator_dictionary_file.get()):
        if html_annotator_dictionary_file.get().endswith('csv'):
            menu_values = IO_csv_util.get_csvfile_headers(html_annotator_dictionary_file.get())
        else:
            return
    if csv_field2_var.get()!='':
        menu_field_values = IO_csv_util.get_csv_field_values(html_annotator_dictionary_file.get(), csv_field2_var.get())
    else:
        menu_field_values = IO_csv_util.get_csv_field_values(html_annotator_dictionary_file.get(), csv_field1_var.get())

    m2 = csv_field_value_menu["menu"]
    m2.delete(0,"end")
    for s in menu_field_values:
        m2.add_command(label=s,command=lambda value=s:csv_field_value_var.set(value))
    if csv_field1_var.get()!='' or csv_field2_var.get()!='':
        if csv_field_value_var.get()=='':
            csv_field_value_menu.configure(state="normal")
    else:
        csv_field_value_menu.configure(state="disabled")
    # if csv_field1_var.get()!='':
    # 	if color_palette_dict_var.get()=='':
    # 		color_palette_dict_var.set('red')
csv_field1_var.trace('w',get_csv_fieldValues)
csv_field2_var.trace('w',get_csv_fieldValues)

get_csv_fieldValues()

def activate_color_palette_dict_menu(*args):
    if color_palette_dict_var.get()!='':
        reset_dictValue_button.configure(state='normal')
        show_keywords_button.configure(state='normal')
        state = str(color_palette_dict_menu['state'])
        if state != 'disabled':
            if color_palette_dict_var.get() in csvValue_color_list:
                mb.showwarning(title='Warning', message='The selected color, ' + color_palette_dict_var.get() + ', has already been selected.\n\nPlease, select a different value. You can display all selected values by clicking on SHOW.')
                return
            if csv_field1_var.get()=='' and csv_field2_var.get()=='':
                csvValue_color_list.clear()
            else:
                if len(csvValue_color_list)==0:
                    csv_field1_menu.configure(state="disabled")
                    csv_field2_menu.configure(state="disabled")
                    csv_field_value_menu.configure(state="disabled")
                    csvValue_color_list.append(csv_field1_var.get())
                    csvValue_color_list.append("|")
                csvValue_color_list.append(color_palette_dict_var.get())
                csvValue_color_list.append("|")
            color_palette_dict_menu.configure(state='disabled')
color_palette_dict_var.trace('w',activate_color_palette_dict_menu)

bold_dict_var.set(1)
bold_checkbox = tk.Checkbutton(window, text='Bold', state='disabled',variable=bold_dict_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.html_annotator_bold_checkbox,y_multiplier_integer,bold_checkbox)

def activateDictionary(*args):
    if html_annotator_dictionary_var.get()==1 or html_annotator_add_dictionary_var.get()==1:
        annotator_dictionary_button.config(state='normal')
        openInputFile_button.config(state='normal')
        html_annotator_dictionary_file.config(state='normal')
        csv_field1_menu.configure(state='normal')
        # csv_field2_menu.configure(state='normal')
        # csv_field_value_menu.configure(state='normal')
    else:
        html_annotator_dictionary_file_var.set('')
        annotator_dictionary_button.config(state='disabled')
        openInputFile_button.config(state='disabled')
        html_annotator_dictionary_file.config(state='disabled')
        csv_field1_menu.configure(state='disabled')
        # csv_field2_menu.configure(state='disabled')
        # csv_field_value_menu.configure(state='disabled')
html_annotator_dictionary_var.trace('w',activateDictionary)
html_annotator_add_dictionary_var.trace('w',activateDictionary)

activateDictionary()

def di_activateCsvFieldValue(*args):
    if csv_field_value_var.get()!='':
        state = str(csv_field_value_menu['state'])
        if state != 'disabled':
            if csv_field_value_var.get() in csvValue_color_list:
                mb.showwarning(title='Warning', message='The selected csv field value, ' + csv_field_value_var.get() + ', has already been selected.\n\nPlease, select a different value. You can display all selected values by clicking on SHOW.')
                return
            add_dictValue_button.configure(state="normal")
            reset_dictValue_button.configure(state="normal")
            show_keywords_button.configure(state='normal')
            if len(csvValue_color_list)==0:
                csv_field1_menu.configure(state="disabled")
                csv_field2_menu.configure(state="disabled")
                if csv_field2_var.get()!='':
                    csvValue_color_list.append(csv_field2_var.get())
                else:
                    csvValue_color_list.append(csv_field1_var.get())
                csvValue_color_list.append("|")
            csvValue_color_list.append(csv_field_value_var.get())
            csv_field_value_menu.configure(state="disabled")
        else:
            add_dictValue_button.configure(state="normal")
            reset_dictValue_button.configure(state="normal")
            show_keywords_button.configure(state='normal')
    else:
        add_dictValue_button.configure(state="disabled")
        reset_dictValue_button.configure(state="disabled")
        show_keywords_button.configure(state='disabled')
    color_palette_dict_menu.configure(state='normal')
csv_field_value_var.trace('w',di_activateCsvFieldValue)

di_activateCsvFieldValue()

def get_dictionary_file(window,title,fileType):
    #annotator_dictionary_var.set('')
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)
    if len(filePath)>0:
        html_annotator_dictionary_file.config(state='normal')
        html_annotator_dictionary_file_var.set(filePath)

html_annotator_extractor_var.set(0)
html_annotator_extractor_checkbox = tk.Checkbutton(window, text='Extract HTML annotations', variable=html_annotator_extractor_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,html_annotator_extractor_checkbox)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf','Statistical measures':'TIPS_NLP_Statistical measures.pdf','Annotator':'TIPS_NLP_Annotator.pdf','Annotator DBpedia':'TIPS_NLP_Annotator DBpedia.pdf','DBpedia ontology classes':'TIPS_NLP_Annotator DBpedia ontology classes.pdf','YAGO (schema.org) ontology classes':'TIPS_NLP_Annotator YAGO (schema.org) ontology classes.pdf','YAGO (REDUCED schema.org) ontology classes':'TIPS_NLP_Annotator YAGO (schema reduced).pdf','W3C, OWL, RDF, SPARQL':'TIPS_NLP_W3C OWL RDF SPARQL.pdf','Annotator dictionary':'TIPS_NLP_Annotator dictionary.pdf','Annotator extractor':'TIPS_NLP_Annotator extractor.pdf','Gender annotator':'TIPS_NLP_Gender annotator.pdf'}
TIPS_options='csv files - Problems & solutions','Statistical measures','Annotator','Annotator DBpedia','DBpedia ontology classes','YAGO (schema.org) ontology classes','YAGO (REDUCED schema.org) ontology classes','W3C, OWL, RDF, SPARQL', 'Annotator dictionary','Annotator extractor','Gender annotator'
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

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, click on the button to open the GUI to run the DBpedia and/or YAGO knowledge graphs.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, click on the button to open the GUI to run the WordNet knowledge graphs.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, click on the button to open the gender annotator GUI for annotating text by gender (male/female), either via Stanford CoreNLP gender annotator or various gender databases (US Census, US Social Security, Carnegie Mellon).')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, tick the checkbox \'HTML annotate corpus using csv dictionary\' if you wish to annotate txt file(s) using a csv dictionary (i.e., a list of words to be annotated).\n\nYou can also tick the checkbox \'Add annotations to a previously annotated HTML file using csv dictionary\' if you wish to annotate a previously annotated file using a csv dictionary.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, click on the \'Select dictionary file\' button to select the csv file that contains dictionary values.\n\nThe button becomes available only when using the dictionary as an annotator (see the widget above \'Annotate corpus (using dictionary)\'.\n\nOnce selected, you can open the dictionary file by clicking on the little square widget.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'The widgets become available only when a csv dictionary file has been selected (via the widget above \'Select dictionary file\').\n\nSelect csv field 1 is the column that contains the values used to annotate the input txt file(s). The FIRST COLUMN of the dictionary file is taken as the default column. YOU CAN SELECT A DIFFERENT COLUMN FROM THE DROPDOWN MENU Select csv field 1.\n\nIf the dictionary file contains more columns, you can select a SECOND COLUMN using the dropdown menu in Select csv field 2 to be used if you wish to use different colors for different items listed in this column. YOU CAN SELECT A DIFFERENT COLUMN FROM THE DROPDOWN MENU Select csv field 2. For example, column 1 contains words to be annotated in different colors by specific categories of field 2 (e.g., \'he\' to be annotated by a \'Gender\' column with the value \'Male\').\n\nThe specific values will have to be selected together with the specific color to be used. YOU CAN ACHIEVE THE SAME RESULT BY ANNOTATING THE SAME HTML FILE MULTIPLE TIMES USING A DIFFERENT DICTIONARY FILE ASSOCIATED EACH TIME TO A DIFFERENT COLOR.\n\n\nPress + for multiple selections.\nPress RESET (or ESCape) to delete all values entered and start fresh.\nPress Show to display all selected values.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, tick the checkbox if you wish to run the Python 3 HTML_annotator_extractor script to extract all matched terms in your corpus as tagged in the HTML file(s).\n\nIn INPUT, the script expects previously annotated .html file(s) via DBpedia or dictionary.\n\nIn OUTPUT the script generates a csv file with the filename and term annotated, and whether it was annotated using DBpedia or dictionary.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 scripts provide different ways of annotating text files in HTML for matching terms found in a user-supplied dictionary file, in knowledge graphs such as DBpedia, YAGO, or WordNet, or in the Stanford CorenNLP gender annotator.\n\ncsv dictionary files can be constructed, for instance, by exporting specific tokens from the CoNLL table (e.g., FORM values of NER PERSON or all past verbs).\n\nThe selection of the knowledge graphs DBpedia, YAGO, WordNet and the Stanford CoreNLP gender annotator will open specialized GUIs."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()

