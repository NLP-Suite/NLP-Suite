# Created on Thu Nov 21 09:45:47 2019
# @author: jack hester
# rewritten by Roberto Franzosi April 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"annotator_main.py",['os','tkinter','subprocess'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_files_util
import IO_csv_util
import reminders_util
import annotator_dictionary_util


# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,input_main_dir_path,output_dir_path, openOutputFiles, createExcelCharts,
		annotator_DBpedia_var, 
		annotator_YAGO_var, 
		confidence_level, 
		databases_var,
		sub_class_entry, 
		DBpedia_YAGO_class_list,
		DBpedia_YAGO_color_list,
		bold_DBpedia_YAGO_var,
		annotator_dictionary_var, 
		annotator_add_dictionary_var, 
		dictionary_file,
		csv_field1_var,
		csv_field2_var,
		color_palette_dict_var,
		bold_var,
		csvValue_color_list, 
		annotator_extractor,
		CoreNLP_gender_annotator_var):

	filesToOpen=[]

	if annotator_DBpedia_var==True or annotator_YAGO_var==True:
		import IO_internet_util
		if annotator_DBpedia_var:
			IO_internet_util.check_internet_availability_warning('DBpedia')
		else:
			IO_internet_util.check_internet_availability_warning('YAGO')

	if annotator_DBpedia_var==True or annotator_YAGO_var==True or annotator_dictionary_var==True:
		if inputFilename!='' and inputFilename[-4:]!='.txt':
			mb.showwarning(title='Warning', message='You have selected to annotate your corpus, but the input file is not of type .txt as required by the selected annotator.\n\nPlease, select a .txt file (or a directory) and try again.')
			return
		if sub_class_entry!='' and DBpedia_YAGO_class_list==[]:
			mb.showwarning(title='Warning', message='You have selected to annotate your corpus using the keywords ' + sub_class_entry + ' but it looks like you have forgotten to press OK.\n\nPlease, press OK and try again (or delete YOUR keyword(s) by pressing ESCape)')
			return

	if annotator_add_dictionary_var==True or annotator_extractor==True:
		if inputFilename!='' and inputFilename[-5:]!='.html':
			mb.showwarning(title='Warning', message='You have selected to run an option that requires an input file of type .html.\n\nPlease, select an .html file (or a directory) and try again.')
			return

	if annotator_dictionary_var==True or annotator_add_dictionary_var==True and dictionary_file=='':
		if dictionary_file=='':
			mb.showwarning(title='Warning', message='You have selected to annotate your corpus using dictionary entries, but you have not provided the required .csv dictionary file.\n\nPlease, select a .csv dictionary file and try again.')
			return

	if color_palette_dict_var=='':
		color_palette_dict_var='red' # default color, if forgotten

	if bold_var==True:
		tagAnnotations = ['<span style=\"color: ' + color_palette_dict_var + '; font-weight: bold\">','</span>']
	else:
		tagAnnotations = ['<span style=\"color: ' + color_palette_dict_var + '\">','</span>']

	if annotator_DBpedia_var==True:
		if IO_libraries_util.inputProgramFileCheck('annotator_DBpedia_util.py')==False:
			return
		import annotator_DBpedia_util
		# for a complete list of annotator types:
		#http://mappings.DBpedia.org/server/ontology/classes/
		filesToOpen = annotator_DBpedia_util.DBpedia_annotate(inputFilename, input_main_dir_path, output_dir_path, openOutputFiles, DBpedia_YAGO_class_list, confidence_level)
	elif annotator_YAGO_var==True:
		import annotator_YAGO_util
		if IO_libraries_util.inputProgramFileCheck('annotator_YAGO_util.py')==False:
			return
		# for a complete list of annotator types:
		#http://mappings.DBpedia.org/server/ontology/classes/
		# def YAGO_annotate(inputFile, inputDir, outputDir, annotationTypes, color1, colorls):

		if len(DBpedia_YAGO_color_list) == 0:  # no colors entered; use blue as default
			DBpedia_YAGO_color_list = ['', '|', 'blue', '|']
		temp = [a for a in DBpedia_YAGO_color_list if a is not "|"]
		colorls = []
		for i in range(len(temp)):
			if (i % 2 == 1):
				colorls.append(temp[i])
		color1 = 'black'

		filesToOpen = annotator_YAGO_util.YAGO_annotate(inputFilename, input_main_dir_path, output_dir_path,
																DBpedia_YAGO_class_list, color1, colorls)

	elif annotator_dictionary_var==True:
		if IO_libraries_util.inputProgramFileCheck('annotator_dictionary_util.py')==False:
			return
		if csv_field2_var=='' and color_palette_dict_var!='':
			csvValue_color_list=[]
		filesToOpen = annotator_dictionary_util.dictionary_annotate(inputFilename, input_main_dir_path, output_dir_path, dictionary_file, csvValue_color_list, bold_var, tagAnnotations, '.txt')
	elif annotator_add_dictionary_var==True:
		if IO_libraries_util.inputProgramFileCheck('annotator_dictionary_util.py')==False:
			return
		filesToOpen = annotator_dictionary_util.dictionary_annotate(inputFilename, input_main_dir_path, output_dir_path, dictionary_file, csvValue_color_list, bold_var, tagAnnotations, '.html')
	elif annotator_extractor==True: 
		if IO_libraries_util.inputProgramFileCheck('annotator_html_extractor_util.py')==False:
			return
		import annotator_html_extractor_util
		annotator_html_extractor_util.buildcsv(inputFilename, input_main_dir_path, output_dir_path,openOutputFiles,createExcelCharts)
	elif CoreNLP_gender_annotator_var==True: 
		if IO_libraries_util.inputProgramFileCheck('annotator_gender_main.py')==False:
			return
		call("python annotator_gender_main.py", shell=True)
	else:
		mb.showwarning(title='Warning', message='There are no options selected.\n\nPlease, select one of the available options and try again.')
		return

	if openOutputFiles==True:
		if filesToOpen==None:
			print("\nYAGO exited with error")
			return
		nFile=len(filesToOpen)
		if nFile > 5:
			mb.showwarning(title='Warning', message='There are too many output files (' + str(nFile) + ') to be opened automatically.\n\nPlease, do not forget to check the html files in your selected output directory.')
			return
		else:
			IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
#def run(inputFilename,input_main_dir_path,output_dir_path, dictionary_var, annotator_dictionary, DBpedia_var, annotator_extractor, openOutputFiles):
run_script_command=lambda: run(GUI_util.inputFilename.get(),
				GUI_util.input_main_dir_path.get(),
				GUI_util.output_dir_path.get(),
                GUI_util.open_csv_output_checkbox.get(),
                GUI_util.create_Excel_chart_output_checkbox.get(),
				annotator_DBpedia_var.get(),
				annotator_YAGO_var.get(),
				confidence_level_entry.get(),
				databases_var.get(),
				sub_class_entry_var.get(),
				DBpedia_YAGO_class_list,
				DBpedia_YAGO_color_list,
				bold_DBpedia_YAGO_var.get(),
				annotator_dictionary_var.get(),
				annotator_add_dictionary_var.get(),
				annotator_dictionary_file_var.get(),
				csv_field1_var.get(),
				csv_field2_var.get(),
				color_palette_dict_var.get(),
				bold_dict_var.get(),
				csvValue_color_list,
				annotator_extractor_var.get(),
				CoreNLP_gender_annotator_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

GUI_size='1400x640'
GUI_label='Graphical User Interface (GUI) for annotating documents using DBpedia, YAGO, and/or dictionaries'
config_filename='annotator-config.txt'
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
config_option=[0,5,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

# GUI CHANGES add following lines to every special GUI
# +2 is the number of lines starting at 1 of IO widgets
y_multiplier_integer=GUI_util.y_multiplier_integer+2
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_options,config_filename)

def clear(e):
	clear_DBpedia_YAGO_class_list()
	clear_dictionary_list()
	DBpedia_YAGO_color_list.clear()
	CoreNLP_gender_annotator_var.set(0)
	GUI_util.clear("Escape")
window.bind("<Escape>", clear)

DBpedia_YAGO_class_list=[]
DBpedia_YAGO_color_list=[]
csvValue_color_list=[]

annotator_DBpedia_var=tk.IntVar() # to annotate a document using DBpedia
annotator_YAGO_var=tk.IntVar() # to annotate a document using YAGO
confidence_level_var=tk.StringVar()
databases_var=tk.StringVar()
class_var = tk.StringVar()
sub_class_entry_var = tk.StringVar()
annotator_dictionary_var=tk.IntVar() # to annotate a document using a dictionary
csv_field1_var=tk.StringVar()
csv_field2_var=tk.StringVar()
csv_field_value_var=tk.StringVar()
color_palette_DBpedia_YAGO_var= tk.StringVar() # the color selected for DBpedia/YAGO annotation
bold_DBpedia_YAGO_var= tk.IntVar() # display in bod the selected color selected for DBpedia/YAGO annotation
color_palette_dict_var= tk.StringVar() # the color selected for dictionary annotation
bold_dict_var= tk.IntVar() # display in bod the selected color selected for dictionary annotation
annotator_add_dictionary_var=tk.IntVar() # to add new annotations via dictionary to an already annotated document
annotator_dictionary_file_var=tk.StringVar() # dictionary file used to annotate 
annotator_extractor_var=tk.IntVar() # to extract annotations in csv format from an annotated file
CoreNLP_gender_annotator_var=tk.IntVar() 

# http://mappings.dbpedia.org/server/ontology/classes/
DBpedia_menu_options=(
		'Thing',
		'Activity',
		'Agent',
		'Algorithm'
		'Altitude',
		'AnatomicalStructure',
		'Area',
		'Award',
		'Biomolecule',
		'Blazon',
		'Browser',
		'ChartsPlacements',
		'ChemicalSubstance',
		'Cipher',
		'Colour',
		'Currency',
		'Demographics',
		'Depth',
		'Device',
		'Diploma',
		'Disease',
		'ElectionDiagram',
		'ElectricalSubstation',
		'EthnicGroup',
		'Event',
		'FileSystem',
		'Flag',
		'Food',
		'GeneLocation',
		'GrossDomesticProduct',
		'GrossDomesticProductPerCapita',
		'Holiday',
		'Identifier',
		'Language',
		'List',
		'MeanOfTransportation',
		'Media',
		'MedicalSpecialty',
		'Medicine',
		'Name',
		'PersonFunction',
		'Place',
		'Population',
		'Protocol',
		'PublicService',
		'Relationship',
		'Species',
		'SportCompetitionResult',
		'SportsSeason',
		'Spreadsheet',
		'StarCluster',
		'Statistic',
		'Tank',
		'TimePeriod',
		'TopicalConcept',
		'UnitOfWork',
		'Unknown',
		'Work')

# These are schema.org classes https://schema.org/docs/full.html
YAGO_menu_options=(
		'BioChemEntity', 	# bioschemas
		'Gene',				# bioschemas
		'MolecularEntity',	# bioschemas
		'Taxon',			# bioschemas
		'Brand',			# schema
		'BroadcastChannel',	# schema
		'CreativeWork',		# schema
		'Emotion',			# yago
		'MedicalEntity',	# schema
		'Organization',		# schema
		'Person',			# schema
		'Place',			# schema
		'Product')			# schema

# temporarily set DBpedia_YAGO_menu_options to avoid
#	is not defined error
DBpedia_YAGO_menu_options=DBpedia_menu_options

def activate_DBpedia_YAGO_menu():
	global DBpedia_YAGO_menu_options
	if annotator_DBpedia_var.get():
		DBpedia_YAGO_menu_options=DBpedia_menu_options
	if annotator_YAGO_var.get():
		DBpedia_YAGO_menu_options=YAGO_menu_options
	m = class_menu["menu"]
	m.delete(0,"end")
	for s in DBpedia_YAGO_menu_options:
		m.add_command(label=s,command=lambda value=s:class_var.set(value))

y_multiplier_integerSV= y_multiplier_integer

annotator_DBpedia_var.set(0)
annotator_DBpedia_checkbox = tk.Checkbutton(window, text='Annotate corpus (using DBpedia)', variable=annotator_DBpedia_var, onvalue=1, offvalue=0,command=lambda: activate_DBpedia_YAGO_menu())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,annotator_DBpedia_checkbox,True)

# http://yago.r2.enst.fr/
# http://yago.r2.enst.fr/downloads/yago-4
annotator_YAGO_var.set(0)
annotator_YAGO_checkbox = tk.Checkbutton(window, text='Annotate corpus (using YAGO)',variable=annotator_YAGO_var, onvalue=1, offvalue=0,command=lambda: activate_DBpedia_YAGO_menu())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,annotator_YAGO_checkbox,True)

confidence_level_lb = tk.Label(window, text='DBpedia confidence level')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+270,y_multiplier_integer,confidence_level_lb,True)

confidence_level_entry = tk.Scale(window, from_=0.0, to=1.0, resolution = 0.1, orient=tk.HORIZONTAL)
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+420,y_multiplier_integer,confidence_level_entry)
confidence_level_entry.set(.5)

y_multiplier_integer=y_multiplier_integerSV+1

DB_menu_options=('*','Wikipedia', 'Wikidata')
databases_var.set('')
databases_menu_lb = tk.Label(window, text='Databases')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,databases_menu_lb,True)
databases_menu = tk.OptionMenu(window,databases_var,*DB_menu_options)
databases_menu.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+100,y_multiplier_integer,databases_menu,True)

def activate_class_var():
	# Disable the + after clicking on it and enable the class menu
	add_class_button.configure(state='disabled')
	class_menu.configure(state='normal')

add_class_button = tk.Button(window, text='+', width=2,height=1,state='disabled',command=lambda: activate_class_var())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.open_file_directory_coordinate,y_multiplier_integer,add_class_button, True)

reset_class_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: clear_DBpedia_YAGO_class_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.open_file_directory_coordinate+30,y_multiplier_integer,reset_class_button,True)

def show_class_color_list():
	if len(DBpedia_YAGO_color_list)==0:
		mb.showwarning(title='Warning', message='There are no currently selected combinations of ontology class and color.')
	else:
		mb.showwarning(title='Warning', message='The currently selected combination of ontology classes and colors are:\n\n' + ','.join(DBpedia_YAGO_color_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

show_class_color_button = tk.Button(window, text='Show', width=5,height=1,state='disabled',command=lambda: show_class_color_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.open_file_directory_coordinate+80,y_multiplier_integer,show_class_color_button,True)

#activated when pressing the RESET button

def clear_DBpedia_YAGO_class_list():
	DBpedia_YAGO_class_list.clear()
	DBpedia_YAGO_color_list.clear()
	color_palette_DBpedia_YAGO_var.set('')
	confidence_level_var.set('.5')
	class_var.set('')
	sub_class_entry_var.set('')
	reset_class_button.configure(state='disabled')
	activate_DBpedia_YAGO_Options(y_multiplier_integerSV,confidence_level_lb,confidence_level_entry)

def accept_DBpedia_YAGO_list():
	global DBpedia_YAGO_class_list
	if sub_class_entry_var.get()!='':
		#TODO
		#what if user enter , followed by a space? most likely event...
		DBpedia_YAGO_class_list=[str(x) for x in sub_class_entry_var.get().split(',') if x]
	else:
		mb.showwarning(title='Warning', message='You have pressed the OK button, but you must first enter your class(s).\n\nPlease, enter the class(s) and try again.')


def add_DBpedia_sub_class(*args):
	if sub_class_entry_var.get()!='':
		activate_DBpedia_YAGO_Options(y_multiplier_integerSV,confidence_level_lb,confidence_level_entry)
sub_class_entry_var.trace ('w',add_DBpedia_sub_class)

class_var.set('')
class_menu_lb = tk.Label(window, text='Ontology class')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+85,y_multiplier_integer,class_menu_lb,True)
class_menu = tk.OptionMenu(window,class_var,*DBpedia_YAGO_menu_options)
class_menu.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+180,y_multiplier_integer,class_menu,True)

sub_class_entry_lb = tk.Label(window, text='Sub-class')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 300,y_multiplier_integer,sub_class_entry_lb,True)

sub_class_entry = tk.Entry(window,width=30,textvariable=sub_class_entry_var)
sub_class_entry.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+ 380,y_multiplier_integer,sub_class_entry,True)

OK_button = tk.Button(window, text='OK', width=3,height=1,state='disabled',command=lambda: accept_DBpedia_YAGO_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+600,y_multiplier_integer,OK_button,True)

color_palette_DBpedia_YAGO_lb = tk.Label(window, text='Select color')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+640,y_multiplier_integer,color_palette_DBpedia_YAGO_lb,True)
color_palette_DBpedia_YAGO_menu = tk.OptionMenu(window, color_palette_DBpedia_YAGO_var,'black','blue','green','pink','red','yellow')
color_palette_DBpedia_YAGO_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+730, y_multiplier_integer,color_palette_DBpedia_YAGO_menu,True)

bold_DBpedia_YAGO_var.set(1)
bold_DBpedia_YAGO_checkbox = tk.Checkbutton(window, text='Bold', state='disabled',variable=bold_DBpedia_YAGO_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+830,y_multiplier_integer,bold_DBpedia_YAGO_checkbox)

firstTime = False

# https://www.python.org/download/mac/tcltk/
# https://stackoverflow.com/questions/24207870/cant-reenable-menus-in-python-tkinter-on-mac
# In Mac, widgets are temporarily turned disabled but immediately return to normal. This is a bug in the Apple-supplied Tk 8.5. The Cocoa versions of Tk that Apple has been shipping since OS X 10.6 have had numerous problems many of which have been fixed in more recent versions of Tk 8.5. With the current ActiveTcl 8.5.15, your test appears to work correctly. Unfortunately, you can't easily change the version of Tcl/Tk that the Apple-supplied system Pythons use. One option is to install the current Python 2.7.7 from the python.org binary installer along with ActiveTcl 8.5.15. There is more information here:

# https://www.python.org/downloads/

def activate_DBpedia_YAGO_Options(y_multiplier_integerSV,confidence_level_lb,confidence_level_entry,*args):
	global firstTime
	if annotator_DBpedia_var.get()==False and annotator_YAGO_var.get()==False:
		DBpedia_YAGO_class_list.clear()
		DBpedia_YAGO_color_list.clear()
		class_var.set('') # DBpedia_YAGO_menu_options
		annotator_DBpedia_checkbox.configure(state="normal")
		annotator_YAGO_checkbox.configure(state="normal")
		y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integerSV,
												   annotator_YAGO_checkbox)
	if annotator_DBpedia_var.get()==True:
		y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integerSV,
													   annotator_YAGO_checkbox, True)
		y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 270,
													   y_multiplier_integerSV, confidence_level_lb,True)
		y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 420,
													   y_multiplier_integerSV, confidence_level_entry)
		annotator_YAGO_checkbox.configure(state="disabled")
	else:
		y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integerSV,
													   annotator_YAGO_checkbox)
		confidence_level_lb.place_forget()  # invisible
		confidence_level_entry.place_forget()  # invisible
	if annotator_DBpedia_var.get()==True:
		annotator_YAGO_checkbox.configure(state="disabled")
	if annotator_YAGO_var.get()==True:
		annotator_DBpedia_checkbox.configure(state="disabled")
	if annotator_DBpedia_var.get()==True or annotator_YAGO_var.get()==True:
		# display the reminder only once in the same GUI or the trace will display it many times
		if firstTime==False:
			title_options = ['DBpedia/YAGO options']
			message = "Please, using the dropdown menu, select an ontology class or enter a sub-class in the \'Sub-class\' widget (for sub-classes, consult the TIPS files on ontology classes). If you select an ontology class from the dropdown menu, the \'Select color\' widget will become available. You MUST select a color to be associated to the selected ontology class. After selecting a color, the + button will become available for multiple selections of class/color.\n\nYou can select the same color for different classes."
			reminders_util.checkReminder(config_filename,
										 title_options,
										 message,
										 True)
		firstTime=True
		databases_menu.configure(state="normal")
		class_menu.configure(state="normal")
		sub_class_entry.configure(state="normal")
	else:
		databases_menu.configure(state="disabled")
		class_menu.configure(state="disabled")
		sub_class_entry.configure(state="disabled")
annotator_DBpedia_var.trace('w',callback = lambda x,y,z: activate_DBpedia_YAGO_Options(y_multiplier_integerSV,confidence_level_lb,confidence_level_entry))
annotator_YAGO_var.trace('w',callback = lambda x,y,z: activate_DBpedia_YAGO_Options(y_multiplier_integerSV,confidence_level_lb,confidence_level_entry))

def activate_class_options(*args):
	if class_var.get() in DBpedia_YAGO_class_list:
		mb.showwarning(title='Warning', message='The class "'+ class_var.get() + '" is already in your selection list: '+ str(DBpedia_YAGO_class_list) + '.\n\nPlease, select another class.')
		window.focus_force()
		return
	state = str(class_menu['state'])
	if state != 'disabled':
		if class_var.get() != '':
			DBpedia_YAGO_class_list.append(class_var.get())
			class_menu.configure(state="disabled")
			sub_class_entry.configure(state="disabled")
			OK_button.configure(state="disabled")
			reset_class_button.configure(state='normal')
			# color palette ONLY available when selecting a major ontology class from the dropdown menu
			color_palette_DBpedia_YAGO_menu.configure(state='normal')
		else:
			color_palette_DBpedia_YAGO_menu.configure(state='disabled')
	else:
		if sub_class_entry_var.get() != '':
			class_menu.configure(state="disabled")
			OK_button.configure(state="normal")
		else:
			class_menu.configure(state="normal")
			OK_button.configure(state="disabled")
class_var.trace ('w',activate_class_options)

def activate_OK_buttton(*args):
	if sub_class_entry_var.get() != '':
		class_menu.configure(state="disabled")
		OK_button.configure(state="normal")
		color_palette_DBpedia_YAGO_menu.configure(state='normal')
		reset_class_button.configure(state='normal')
	else:
		class_menu.configure(state="normal")
		OK_button.configure(state="disabled")
		color_palette_DBpedia_YAGO_menu.configure(state='disabled')
		reset_class_button.configure(state='disabled')
sub_class_entry_var.trace('w',activate_OK_buttton)

def activate_class_color_combo(*args):
	if color_palette_DBpedia_YAGO_var.get()!='':
		state = str(color_palette_DBpedia_YAGO_menu['state'])
		# 'active' for mac; 'normal' for windows
		if state != 'disabled': # normal/active
			# you may wish to assign the same color to different ontology classes
			# if color_palette_DBpedia_YAGO_var.get() in DBpedia_YAGO_color_list:
			# 	mb.showwarning(title='Warning', message='The selected color, ' + color_palette_DBpedia_YAGO_var.get() + ', has already been selected.\n\nPlease, select a different value. You can display all selected values by clicking on SHOW.')
			# 	return
			DBpedia_YAGO_color_list.append(class_var.get())
			DBpedia_YAGO_color_list.append("|")
			DBpedia_YAGO_color_list.append(color_palette_DBpedia_YAGO_var.get())
			DBpedia_YAGO_color_list.append("|")
			# now disable the color palette and enable the + button (so that more combinations class/color can be added) and the Reset & Show buttons
			color_palette_DBpedia_YAGO_menu.configure(state='disabled')
			add_class_button.configure(state='normal')
			reset_class_button.configure(state='normal')
			show_class_color_button.configure(state='normal')
color_palette_DBpedia_YAGO_var.trace('w',activate_class_color_combo)

def clear_dictionary_list():
	csv_field1_var.set('')
	csv_field2_var.set('')
	csv_field1_menu.configure(state="normal")
	csv_field2_menu.configure(state="normal")
	csv_field_value_var.set('')
	csv_field_value_menu.configure(state='normal')
	color_palette_dict_var.set('')
	color_palette_DBpedia_YAGO_var.set('')
	bold_DBpedia_YAGO_var.set(1)
	bold_dict_var.set(1)
	csvValue_color_list.clear()

annotator_dictionary_var.set(0)
annotator_dictionary_checkbox = tk.Checkbutton(window, text='Annotate corpus (using dictionary)', variable=annotator_dictionary_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,annotator_dictionary_checkbox)

annotator_add_dictionary_var.set(0)
annotator_add_dictionary_checkbox = tk.Checkbutton(window, text='Add annotations to a previously annotated html file (using dictionary)', variable=annotator_add_dictionary_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,annotator_add_dictionary_checkbox)

annotator_dictionary_button=tk.Button(window, width=20, text='Select dictionary file',command=lambda: get_dictionary_file(window,'Select INPUT dictionary file', [("dictionary files", "*.csv")]))
annotator_dictionary_button.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,annotator_dictionary_button,True)

#setup a button to open Windows Explorer on the selected input directory
current_y_multiplier_integer2=y_multiplier_integer-1
openInputFile_button  = tk.Button(window, width=3, state='disabled', text='', command=lambda: IO_files_util.openFile(window, annotator_dictionary_file_var.get()))
openInputFile_button.place(x=GUI_IO_util.get_labels_x_coordinate()+170, y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

annotator_dictionary_file=tk.Entry(window, width=100,textvariable=annotator_dictionary_file_var)
annotator_dictionary_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+230, y_multiplier_integer,annotator_dictionary_file)

menu_values=IO_csv_util.get_csvfile_headers(annotator_dictionary_file.get())

field_lb = tk.Label(window, text='Select csv field 1')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,field_lb,True)
if menu_values!='':
	csv_field1_menu = tk.OptionMenu(window, csv_field1_var, *menu_values)
else:
	csv_field1_menu = tk.OptionMenu(window, csv_field1_var, menu_values)
csv_field1_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+120,y_multiplier_integer,csv_field1_menu,True)

add_dictValue_button = tk.Button(window, text='+', width=2,height=1,state='disabled',command=lambda: csv_field_value_menu.configure(state="normal"))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+230,y_multiplier_integer,add_dictValue_button, True)

reset_dictValue_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: clear_dictionary_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+260,y_multiplier_integer,reset_dictValue_button,True)

def showKeywordList():
	if len(csvValue_color_list)==0:
		mb.showwarning(title='Warning', message='There are no currently selected combinations of csv field values and colors.')
	else:
		mb.showwarning(title='Warning', message='The currently selected combination of csv field values and colors are:\n\n' + ','.join(csvValue_color_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

show_keywords_button = tk.Button(window, text='Show', width=5,height=1,state='disabled',command=lambda: showKeywordList())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+310,y_multiplier_integer,show_keywords_button,True)

# OK_button = tk.Button(window, text='OK', width=3,height=1,state='disabled',command=lambda: accept_keyword_list())
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+330,y_multiplier_integer,OK_button,True)

field2_lb = tk.Label(window, text='Select csv field 2')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+380,y_multiplier_integer,field2_lb,True)
if menu_values!='':
	csv_field2_menu = tk.OptionMenu(window, csv_field2_var, *menu_values)
else:
	csv_field2_menu = tk.OptionMenu(window, csv_field2_var, menu_values)
csv_field2_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+480,y_multiplier_integer,csv_field2_menu,True)

value_lb = tk.Label(window, text='Select csv field value ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+620,y_multiplier_integer,value_lb,True)
if menu_values!='':
	csv_field_value_menu = tk.OptionMenu(window, csv_field_value_var, *menu_values)
else:
	csv_field_value_menu = tk.OptionMenu(window, csv_field_value_var, menu_values)
csv_field_value_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+750,y_multiplier_integer,csv_field_value_menu,True)

def changed_dictionary_filename(*args):
	csvValue_color_list.clear()
	csv_field1_var.set('')
	csv_field2_var.set('')
	csv_field_value_var.set('')
	color_palette_dict_var.set('')
	# menu_values is the number of headers in the csv dictionary file
	menu_values=IO_csv_util.get_csvfile_headers(annotator_dictionary_file.get())
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
annotator_dictionary_file_var.trace('w',changed_dictionary_filename)

changed_dictionary_filename()

if csv_field2_var.get()!='':
	menu_field_values = IO_csv_util.get_csv_field_values(annotator_dictionary_file.get(), csv_field2_var.get())
else:
	menu_field_values = IO_csv_util.get_csv_field_values(annotator_dictionary_file.get(), csv_field1_var.get())

color_menu=['black','blue','green','pink','red','yellow']

color_palette_dict_lb = tk.Label(window, text='Select color')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+640,y_multiplier_integer,color_palette_dict_lb,True)
color_palette_dict_menu = tk.OptionMenu(window, color_palette_dict_var,*color_menu)
color_palette_dict_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+730, y_multiplier_integer,color_palette_dict_menu, True)

def get_csv_fieldValues(*args):
	csv_field_value_var.set('')
	color_palette_dict_menu.configure(state='normal')
	menu_values = IO_csv_util.get_csvfile_headers(annotator_dictionary_file.get())
	if csv_field2_var.get()!='':
		menu_field_values = IO_csv_util.get_csv_field_values(annotator_dictionary_file.get(), csv_field2_var.get())
	else:
		menu_field_values = IO_csv_util.get_csv_field_values(annotator_dictionary_file.get(), csv_field1_var.get())

	m2 = csv_field_value_menu["menu"]
	m2.delete(0,"end")
	for s in menu_field_values:
		m2.add_command(label=s,command=lambda value=s:csv_field_value_var.set(value))
	if csv_field1_var.get()!='' or csv_field2_var.get()!='':
		if csv_field_value_var.get()=='':
			csv_field_value_menu.configure(state="normal")
	else:
		csv_field_value_menu.configure(state="disabled")
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
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+830,y_multiplier_integer,bold_checkbox)

def activateDictionary(*args):
	if annotator_dictionary_var.get()==1 or annotator_add_dictionary_var.get()==1:
		annotator_dictionary_button.config(state='normal')
		openInputFile_button.config(state='normal')
		annotator_dictionary_file.config(state='normal')
		csv_field1_menu.configure(state='normal')
		# csv_field2_menu.configure(state='normal')
		# csv_field_value_menu.configure(state='normal')
	else:
		annotator_dictionary_file_var.set('')
		annotator_dictionary_button.config(state='disabled')
		openInputFile_button.config(state='disabled')
		annotator_dictionary_file.config(state='disabled')
		csv_field1_menu.configure(state='disabled')
		# csv_field2_menu.configure(state='disabled')
		# csv_field_value_menu.configure(state='disabled')
annotator_dictionary_var.trace('w',activateDictionary)
annotator_add_dictionary_var.trace('w',activateDictionary)

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
		annotator_dictionary_file.config(state='normal')
		annotator_dictionary_file_var.set(filePath)

annotator_extractor_var.set(0)
annotator_extractor_checkbox = tk.Checkbutton(window, text='Extract html annotations', variable=annotator_extractor_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,annotator_extractor_checkbox)

CoreNLP_gender_annotator_var.set(0)
CoreNLP_gender_annotator_checkbox = tk.Checkbutton(window, text='CoreNLP gender annotator', variable=CoreNLP_gender_annotator_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,CoreNLP_gender_annotator_checkbox)

TIPS_lookup = {'Annotator':'TIPS_NLP_Annotator.pdf','Annotator DBpedia':'TIPS_NLP_Annotator DBpedia.pdf','DBpedia ontology classes':'TIPS_NLP_Annotator DBpedia ontology classes.pdf','YAGO (schema.org) ontology classes':'TIPS_NLP_Annotator YAGO (schema.org) ontology classes.pdf','YAGO (REDUCED schema.org) ontology classes':'TIPS_NLP_Annotator YAGO (schema reduced).pdf','W3C, OWL, RDF, SPARQL':'TIPS_NLP_W3C OWL RDF SPARQL.pdf','Annotator dictionary':'TIPS_NLP_Annotator dictionary.pdf','Annotator extractor':'TIPS_NLP_Annotator extractor.pdf','Gender annotator':'TIPS_NLP_Gender annotator.pdf'}
TIPS_options='Annotator','Annotator DBpedia','DBpedia ontology classes','YAGO (schema.org) ontology classes','YAGO (REDUCED schema.org) ontology classes','W3C, OWL, RDF, SPARQL', 'Annotator dictionary','Annotator extractor','Gender annotator'
# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util. 
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help", GUI_IO_util.msg_txtFile)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help", GUI_IO_util.msg_corpusData)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help", GUI_IO_util.msg_outputDirectory)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*3,"Help", 'Please, tick the appropriate checkbox if you wish to run the Python 3 annotator_DBpedia script or annotator_YAGO script to annotate the input corpus by terms found in either DBpedia or YAGO.\n\nDBpedia will allow you to set confidence levels for your annotation (.5 is the recommended default value in a range between 0 and 1). THE HIGHER THE CONFIDENCE LEVEL THE LESS LIKELY YOU ARE TO FIND DBpedia ENTRIES; THE LOWER THE LEVEL AND THE MORE LIKELY YOU ARE TO FIND EXTRANEOUS ENTRIES.\n\nDBpedia and YAGO are enormous databases (DB for database) designed to extract structured content from the information created in Wikipedia, Wikidata and other knowledge bases. DBpedia and YAGO allow users to semantically query relationships and properties of Wikipedia data (including links to other related datasets) via a large ontology of search values (for a complete listing, see the TIPS files TIPS_NLP_DBpedia Ontology Classes.pdf or TIPS_NLP_YAGO (schema.org) Ontology Classes.pdf).\n\nFor more information, see https://wiki.DBpedia.org/ and https://yago-knowledge.org/.\n\nIn INPUT the scripts expect one or more txt files.\n\nIn OUTPUT the scripts generate as many annotated html files as selected in input.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*4,"Help", 'Once you tick the DBpedia checkbox, the options on this line will become available.\n\nUsing the class dropdown menu, also select the DPpedia or YAGO ontology class you wish to use. IF NO CLASS IS SELECTED, ALL CLASSES WILL BE PROCESSED, WITH \'THING\' AS THE DEFAULT CLASS.\n\nThe class dropdown menu only includes the main classes in the DBpedia or YAGO ontology. For specific sub-classes, please, get the values from the TIPS_NLP_DBpedia ontology classes.pdf or TIPS_NLP_YAGO (schema.org) Ontology Classes.pdf and enter them, comma-separated, in Ontology sub-class field.\n\nYAGO DOES NOT USE THE COMPLETE SCHEMA CLASSES AND SUB-CLASSES. PLEASE, REFER TO THE REDUCED LIST FOR ALL THE SCHEMA CLASSES USED.\n\nYou can test the resulting annotations directly on DBpedia Spotlight at https://www.dbpedia-spotlight.org/demo/\n\nYou can select a specific color for a specific ontology class (Press the \'Show\' widget to display the seleted values. The choice of colors is available only when selecting main ontology classes from the dropdown menu and not for sub-classes.\n\nPress + for multiple selections.\nPress RESET (or ESCape) to delete all values entered and start fresh.\nPress Show to display all selected values.\n\nThe + Reset and Show widgets become available only after selecting both an ontology class and its associated color.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*5,"Help", 'Please, tick the checkbox if you wish to run the Python 3 annotator_dictionary script to annotate the input corpus by terms found in a dictionary file.\n\nThe script allows you to select the color to be used for annotating.\n\nIn INPUT, the script expects .txt file(s) to be annotated and a .csv dictionary file with a list of single- or multiple-word terms to be used for annotation (e.g., "love", "in love").\n\ncsv dictionary files can be constructed, for instance, by exporting specific tokens from the CoNLL table (e.g., FORM values of NER PERSON or all past verbs). If ouu use a csv dictionary file generated by WordNet, remember those Nouns or Verbs WorNet dictionaries contain lemmatized words. You are unlikely to tag all terms in a text using lemmatized values (e.g., \'being\', \'was\', \'is\' would not be tagged using the lemmatized \'be\').\n\nIn OUTPUT the script generates as many annotated html files as selected in input.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*6,"Help", 'Please, tick the checkbox if you wish to run the Python 3 annotator_html script to add new annotations to a previously annotated html file. A selected dictionary file will be used for annotating.\n\nThe script allows you to select the color to be used for annotating. By using a color different from the previous annotation color, you can visualize different annotations (e.g., black for fascists and red for socialists in a study of Italian fascism using, the first-time around, a dictionary file of terms for fascists, and, the second-time around, a dictionary file of terms for socialists).\n\nIn INPUT, the script expects .html file(s) and a .csv dictionary file with a list of single- or multiple-word terms to be used for annotation (e.g., "love", "in love").\n\nIn OUTPUT the script generates an annotaded html file (even when using the files directory option, the script generates a single output file). Each filename processed is added before each tagged text.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*7,"Help", 'Please, click on the \'Select dictionary file\' button to select the csv file that contains dictionary values.\n\nThe button becomes available only when using the dictionary as an annotator (see the widget above \'Annotate corpus (using dictionary)\'.\n\nOnce selected, you can open the dictionary file by clicking on the little square widget.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*8,"Help", 'The widgets become available only when a csv dictionary file has been selected (via the widget above \'Select dictionary file\').\n\nSelect csv field 1 is the column that contains the values used to annotate the input txt file(s). The FIRST COLUMN of the dictionary file is taken as the default column. YOU CAN SELECT A DIFFERENT COLUMN FROM THE DROPDOWN MENU Select csv field 1.\n\nIf the dictionary file contains more columns, you can select a SECOND COLUMN using the dropdown menu in Select csv field 2 to be used if you wish to use different colors for different items listed in this column. YOU CAN SELECT A DIFFERENT COLUMN FROM THE DROPDOWN MENU Select csv field 2. For example, column 1 contains words to be annotated in different colors by specific categories of field 2 (e.g., \'he\' to be annotated by a \'Gender\' column with the value \'Male\'\n\nThe specific values will have to be selected together with the specific color to be used. YOU CAN ACHIEVE THE SAME RESULT BY ANNOTATING THE SAME HTML FILE MULTIPLE TIMES USING A DIFFERENT DICTIONARY FILE ASSOCIATED EACH TIME TO A DIFFERENT COLOR.\n\n\nPress + for multiple selections.\nPress RESET (or ESCape) to delete all values entered and start fresh.\nPress Show to display all selected values.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*9,"Help", 'Please, tick the checkbox if you wish to run the Python 3 annotator_html_extractor script to extract all matched terms in your corpus as tagged in the html file(s).\n\nIn INPUT, the script expects previously annotated .html file(s) via DBpedia or dictionary.\n\nIn OUTPUT the script generates a csv file with the filename and term annotated, and whether it was annotated using DBpedia or dictionary.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*10,"Help", 'Please, tick the checkbox if you wish to open the gender annotator GUI for annotating text by gender (male/female), either via Stanford CoreNLP gender annotator or various gender databases (US Census, US Social Security, Carnegie Mellon).')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*11,"Help",GUI_IO_util.msg_openOutputFiles)

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The Python 3 scripts provide ways of annotating text files for matching terms found in a user-supplied dictionary file and/or in DBpedia or YAGO.\n\ncsv dictionary files can be constructed, for instance, by exporting specific tokens from the CoNLL table (e.g., FORM values of NER PERSON or all past verbs).\n\nDBpedia and YAGO tags can be selected from the class dropdown menu containing the DBpedia and YAGO ontology. The menu only includes the main classes in the ontology. For specific sub-classes, please, get the values from the TIPS_NLP_DBpedia ontology classes.pdf or TIPS_NLP_YAGO (schema.org) ontology classes.pdf and enter them in the Ontology sub-class field."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options)

GUI_util.window.mainloop()

