# Created on Thu Nov 21 09:45:47 2019
# rewritten by Roberto Franzosi April 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"annotator_gender_main.py",['os','tkinter','datetime'])==False:
    sys.exit(0)

import tkinter as tk
import tkinter.messagebox as mb
from datetime import datetime

import GUI_util
import GUI_IO_util
import IO_files_util
import reminders_util
import Stanford_CoreNLP_annotator_util
import annotator_dictionary_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,input_main_dir_path,output_dir_path, openOutputFiles, createExcelCharts,
		CoreNLP_gender_annotator_var, memory_var, CoreNLP_download_gender_file_var, CoreNLP_upload_gender_file_var,
		annotator_dictionary_var, annotator_dictionary_file_var,personal_pronouns_var,plot_var, year_state_var, firstName_entry_var, new_SS_folders):

	filesToOpen=[]
	# select dict_var with no file_var
	if annotator_dictionary_var==True and annotator_dictionary_file_var=='':
		if annotator_dictionary_file_var=='':
			mb.showwarning(title='Warning', message='You have selected to annotate your corpus using dictionary entries, but you have not provided the required .csv dictionary file.\n\nPlease, select a .csv dictionary file and try again.')
			return
	# missing required select option
	if CoreNLP_gender_annotator_var==False and annotator_dictionary_var==False and plot_var==False:
		mb.showwarning(title='Warning', message='There are no options selected.\n\nPlease, select one of the available options and try again.')
		return
	#CoreNLP annotate
	if CoreNLP_gender_annotator_var==True:
		output = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(inputFilename, input_main_dir_path,
															   output_dir_path, openOutputFiles, createExcelCharts, 'gender', False, memory_var)
		# annotator returns a list and not a string
		# the gender annotator returns 2 Excel charts in addition to the csv file
		if len(output)>0:
			# output=output[0]
			filesToOpen.extend(output)

	#dict annotate
	elif annotator_dictionary_var==True:
		if IO_libraries_util.inputProgramFileCheck('annotator_gender_dictionary_util.py')==False:
			return
		import annotator_gender_dictionary_util
		# csvValue_color_list, bold_var, tagAnnotations, '.txt'
		filesToOpen= [annotator_gender_dictionary_util.dictionary_annotate(inputFilename, input_main_dir_path, output_dir_path, annotator_dictionary_file_var,personal_pronouns_var)]

	#plot annotate
	elif plot_var==True:
		import annotator_gender_dictionary_util
		if len(new_SS_folders)>0:
			print(new_SS_folders)
			try:
				annotator_gender_dictionary_util.build_dictionary_state_year(new_SS_folders[0])
				annotator_gender_dictionary_util.build_dictionary_yob(new_SS_folders[1])
			except:
				annotator_gender_dictionary_util.build_dictionary_state_year(new_SS_folders[1])
				annotator_gender_dictionary_util.build_dictionary_yob(new_SS_folders[0])
		if (year_state_var=='' or firstName_entry_var==''):
			mb.showwarning(title='Warning', message="The plot option requires both 'By year/state' value and first name(s) in the 'Enter firt name(s)' widget.\n\nPlease, enter the required information and try again.")
			return
		else:
			filesToOpen = annotator_gender_dictionary_util.SSA_annotate(year_state_var,firstName_entry_var,output_dir_path)

	if openOutputFiles==True:
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
                CoreNLP_gender_annotator_var.get(),
				memory_var.get(),
				CoreNLP_download_gender_file_var.get(),
				CoreNLP_upload_gender_file_var.get(),
				annotator_dictionary_var.get(),
				annotator_dictionary_file_var.get(),
				personal_pronouns_var.get(),
				plot_var.get(),
				year_state_var.get(),
				firstName_entry_var.get(),
				new_SS_folders)

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

GUI_size='1150x640'
GUI_label='Graphical User Interface (GUI) for Annotating First Names & Pronouns in Documents for Gender (Male/Female)'
config_filename='annotator-gender-config.txt'
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
# +3 is the number of lines starting at 1 of IO widgets
y_multiplier_integer=GUI_util.y_multiplier_integer+2
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_options,config_filename)


def clear(e):
	GUI_util.clear("Escape")
	year_state_var.set('')
	firstName_entry_var.set('')
window.bind("<Escape>", clear)

CoreNLP_gender_annotator_var=tk.IntVar()
memory_var = tk.IntVar()
CoreNLP_download_gender_file_var=tk.IntVar()
CoreNLP_upload_gender_file_var=tk.IntVar()
annotator_dictionary_var=tk.IntVar() # to annotate a document using a dictionary
annotator_dictionary_file_var=tk.StringVar() # dictionary file used to annotate
personal_pronouns_var=tk.IntVar()
plot_var=tk.IntVar()
year_state_var=tk.StringVar()
firstName_entry_var=tk.StringVar()
new_SS_folders_var=tk.IntVar()
new_SS_folder_var=tk.StringVar()
last_SS_year_var=tk.IntVar()
new_SS_folders=[]

CoreNLP_gender_annotator_checkbox = tk.Checkbutton(window, text='Annotate nouns & pronouns gender (via CoreNLP Coref)', variable=CoreNLP_gender_annotator_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,CoreNLP_gender_annotator_checkbox,True)

#memory options

memory_var_lb = tk.Label(window, text='Memory ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+400,y_multiplier_integer,memory_var_lb,True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(6)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+470,y_multiplier_integer,memory_var)

CoreNLP_download_gender_file_checkbox = tk.Checkbutton(window, text='Download CoreNLP gender file', variable=CoreNLP_download_gender_file_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,CoreNLP_download_gender_file_checkbox,True)

CoreNLP_upload_gender_file_checkbox = tk.Checkbutton(window, text='Upload CoreNLP gender file', variable=CoreNLP_upload_gender_file_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+400,y_multiplier_integer,CoreNLP_upload_gender_file_checkbox)

annotator_dictionary_var.set(0)
annotator_dictionary_checkbox = tk.Checkbutton(window, text='Annotate first names by gender (using dictionary)', variable=annotator_dictionary_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,annotator_dictionary_checkbox)

annotator_dictionary_button=tk.Button(window, width=20, text='Select dictionary file',command=lambda: get_dictionary_file(window,'Select INPUT dictionary file', [("dictionary files", "*.csv")]))
annotator_dictionary_button.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20, y_multiplier_integer,annotator_dictionary_button,True)

#setup a button to open Windows Explorer on the selected input directory
openInputFile_button  = tk.Button(window, width=3, state='disabled', text='', command=lambda: IO_files_util.openFile(window, annotator_dictionary_file_var.get()))
openInputFile_button.place(x=GUI_IO_util.get_labels_x_coordinate()+190, y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

annotator_dictionary_file=tk.Entry(window, width=100,textvariable=annotator_dictionary_file_var)
annotator_dictionary_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+250, y_multiplier_integer,annotator_dictionary_file)


def get_dictionary_file(window,title,fileType):
	#annotator_dictionary_var.set('')
	filePath = tk.filedialog.askopenfilename(title = title, initialdir =GUI_IO_util.namesGender_libPath, filetypes = fileType)
	if len(filePath)>0:
		annotator_dictionary_file.config(state='normal')
		annotator_dictionary_file_var.set(filePath)

personal_pronouns_var.set(1)
personal_pronouns_checkbox = tk.Checkbutton(window, text='Process personal pronouns', variable=personal_pronouns_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,personal_pronouns_checkbox)

plot_var.set(0)
plot_checkbox = tk.Checkbutton(window, text='Plot names via US Social Security', variable=plot_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,plot_checkbox,True)

year_state_lb = tk.Label(window, text='By US state/year')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 250,y_multiplier_integer,year_state_lb,True)

year_state_menu = tk.OptionMenu(window,year_state_var,'State','Year','Year of birth','State & Year','State & Year of birth')
year_state_menu.configure(width=20,state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+350,y_multiplier_integer,year_state_menu,True)

firstName_entry_lb = tk.Label(window, text='Enter first name(s)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 540,y_multiplier_integer,firstName_entry_lb,True)

firstName_entry = tk.Entry(window,width=50,textvariable=firstName_entry_var)
firstName_entry.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+ 670,y_multiplier_integer,firstName_entry)

# https://www.ssa.gov/oact/babynames/limits.html
new_SS_folders_var.set(0)
new_SS_folders_checkbox = tk.Checkbutton(window, text='Generate new US Social Security files (by US State, Year, Year of birth, US State & Year, US State & Year of birth)', variable=new_SS_folders_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,new_SS_folders_checkbox)

def get_new_SS_folders(window):
	new_SS_folders.clear()
	new_SS_folder_var.set('')
	mb.showwarning(title='Warning', message='You are about to select the two folders where you downloaded and unzipped the most up-to-date gender names databases \'National data\' and \'State-specific data\' from the US Social Security website\n\nhttps://www.ssa.gov/oact/babynames/limits.html\n\nThe last updated year in your NLP Suite is displayed in the last widget of this GUI line.\n\nYOU WILL LOOP TWICE TO SELECT BOTH FOLDERS.')
	for i in range(2):
		if len(new_SS_folders)==0:
			title="Select INPUT new SS folder for the 'National data' database"
		else:
			title="Select INPUT new SS folder for the 'State-specific data' database"
		folderPath = tk.filedialog.askdirectory(title = title)
		if len(folderPath)>0:
			if folderPath in new_SS_folders:
				mb.showwarning(title='Warning', message='You have selected the same SS folder twice. The two folders are expected to be different.\n\nPlease, try again.')
				return
			new_SS_folders.append(folderPath)
	new_SS_folder_var.set(new_SS_folders)
	if len(new_SS_folders)!=2:
		mb.showwarning(title='Warning', message='You were expected to select two folders.\n\nPlease, try again if you wish to update your SS gender names databases.')
		new_SS_folder_var.set('')
		new_SS_folders.clear()

new_SS_select_button=tk.Button(window, width=20, text='Select new SS folders',command=lambda: get_new_SS_folders(window))
new_SS_select_button.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20, y_multiplier_integer,new_SS_select_button,True)

#setup a button to open Windows Explorer on the selected input directory
open_new_SS_folder_button  = tk.Button(window, width=3, text='', command=lambda: IO_files_util.openExplorer(window, new_SS_folder_var.get()))
open_new_SS_folder_button.place(x=GUI_IO_util.get_labels_x_coordinate()+190, y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

new_SS_folder=tk.Entry(window, width=110,textvariable=new_SS_folder_var)
new_SS_folder.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+250, y_multiplier_integer,new_SS_folder,True)

last_SS_year_var.set(2018)
last_SS_year=tk.Entry(window, width=6,textvariable=last_SS_year_var)
last_SS_year.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+950, y_multiplier_integer,last_SS_year)

def checkUSSSUpdate():
	if annotator_dictionary_var.get()==True or plot_var.get() == True:
		currentYear = datetime.now().year
		yearDiff = currentYear - last_SS_year_var.get()
		if yearDiff >= 2:
			reminders_util.checkReminder(
					config_filename,
					['Time to download new US SS data'],
					'It has been more than two years since the US Social Security gender data have been downloaded to your machine.\n\nCheck on the US Social Security website whether more current data are available at US Social Security website\n\nhttps://www.ssa.gov/oact/babynames/limits.html',
					True)

def activate_all_options(*args):
	CoreNLP_gender_annotator_checkbox.configure(state="normal")
	annotator_dictionary_checkbox.configure(state="normal")
	plot_checkbox.configure(state="normal")
	CoreNLP_download_gender_file_checkbox.configure(state='disabled')
	CoreNLP_upload_gender_file_checkbox.configure(state='disabled')
	annotator_dictionary_button.config(state='disabled')
	openInputFile_button.config(state='disabled')
	annotator_dictionary_file.config(state='disabled')
	personal_pronouns_checkbox.configure(state='disabled')
	# year_state_var.set('')
	year_state_menu.configure(state='disabled')
	firstName_entry.configure(state="disabled")
	new_SS_folders_checkbox.configure(state="disabled")
	new_SS_select_button.config(state='disabled')
	open_new_SS_folder_button.config(state='disabled')
	new_SS_folder_var.set("")
	new_SS_folder.config(state='disabled')
	new_SS_folders.clear()
	if CoreNLP_gender_annotator_var.get()==True:
		annotator_dictionary_checkbox.configure(state="disabled")
		plot_checkbox.configure(state="disabled")
		# CoreNLP_download_gender_file_checkbox.configure(state='normal')
		# CoreNLP_upload_gender_file_checkbox.configure(state='normal')
	if annotator_dictionary_var.get()==True:
		checkUSSSUpdate()
		CoreNLP_gender_annotator_checkbox.configure(state="normal")
		plot_checkbox.configure(state="disabled")
		annotator_dictionary_button.config(state='normal')
		openInputFile_button.config(state='normal')
		annotator_dictionary_file.config(state='normal')
		personal_pronouns_checkbox.configure(state='normal')
	if plot_var.get()==True:
		checkUSSSUpdate()
		CoreNLP_gender_annotator_checkbox.configure(state="disabled")
		annotator_dictionary_checkbox.configure(state="disabled")
		year_state_menu.configure(state='normal')
		new_SS_select_button.config(state='normal')
		open_new_SS_folder_button.config(state='normal')
	else:
		year_state_menu.configure(state='disabled')
		firstName_entry.configure(state="disabled")
		year_state_var.set('')
		firstName_entry_var.set('')
	if year_state_var.get()!='':
		firstName_entry.configure(state="normal")
CoreNLP_gender_annotator_var.trace('w',activate_all_options)
annotator_dictionary_var.trace('w',activate_all_options)
plot_var.trace('w',activate_all_options)
year_state_var.trace('w',activate_all_options)

activate_all_options()

TIPS_lookup = {'Gender annotator':'TIPS_NLP_Gender annotator.pdf','NER (Named Entity Recognition)':'TIPS_NLP_NER (Named Entity Recognition) Stanford CoreNLP.pdf','CoreNLP Coref':'TIPS_NLP_Stanford CoreNLP coreference resolution.pdf'}
TIPS_options='Gender annotator', 'NER (Named Entity Recognition)', 'CoreNLP Coref'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help", GUI_IO_util.msg_txtFile)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help", GUI_IO_util.msg_corpusData)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help", GUI_IO_util.msg_outputDirectory)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*3,"Help", 'Please, tick the checkbox if you wish to run the Stanford CoreNLP gender annotator. The CoreNLP gender annotator is based on CoreNLP Coref annotator which, unfortunately, only has about 60\% accuracy. The algorithm annotates the gender of both first names and personal pronouns (he, him, his, she, her, hers).\n\nThe CoreNLP Coref annotator uses a neural network approach. This annotator requires a great deal of memory. Please, adjust the memory allowing as much memory as you can afford.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*4,"Help", 'Please, tick the DOWNLOAD checkbox to dowload the Stanford CoreNLP gender file for editing.\n\nTick the UPLOAD checkbox to upload the edited Stanford CoreNLP gender file.\n\nThe CoreNLP gender file has the format JOHN\\MALE with one NAME\\GENDER entry per line. The CoreNLP gender file is found in The default gender mappings file is in the stanford-corenlp-3.5.2-models.jar file. It is called tmp-stanford-models-expanded/edu/stanford/nlp/models/gender/first_name_map_small')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*5,"Help", 'Please, tick the checkbox if you wish to annotate the first names found in a text using an input dictionary list of gender annotated first names. As a caveat, keep in mind that some first names may be both male and female names (e.g., Jamie in the US) or male and female depending upon the country (e.g., Andrea is a male name in Italy, a female name in the US).\n\nThe algorithm uses the NER PERSON value from the Stanford CoreNLP NER annotator to annotate the gender of proper first names.\n\nThe algorithm also annotates the gender of personal pronouns (he, him, his, she, her, hers, as, respectively, male and female).')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*6,"Help", 'Please, click on the \'Select dictionary file\' to select the first name file to be used to annotate the first names found in the input text(s) by gender.\n\nSeveral files are available as default files in the lib subdirectory (e.g., the 1990 US census lists, the US Social Security list, Carnegie Mellon lists). But, users can also select any file of their choice.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*7,"Help", 'Please, tick the checkbox if you wish to annotate the gender of personal pronouns (he, him, his, she, her, hers as male and female, respectively).')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*8,"Help", 'Please, tick the checkbox if you wish to plot selected first name(s) by US State, by Year of use of the first name, by Year of birth of individuals bearing the first name, by US State & Year (combining both into one file), or State & Year of birth (combining both into one file) using United States Social Security lists.\n\nEnter comma-separated first names, including double names, e.g., Jo Ann.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*9,"Help", 'Please, tick the checkbox if you wish to generate new US Social Security files (by US State, Year, Year of birth, US State & Year, US State & Year of birth).\n\nTHIS IS ONLY NECESSARY WHEN THE US SOCIAL SECURITY ADMINISTRATION RELEASES NEW GENDER NAMES DATA.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*10,"Help", 'Please, click on the \'Select new SS folders\' to select the two folders where you downloaded and unzipped the most up-to-date gender names databases \'National data\' and \'State-specific data\' from the US Social Security website\n\nhttps://www.ssa.gov/oact/babynames/limits.html\n\nThe last updated year in your NLP Suite is displayed in the last widget of this GUI line.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*11,"Help",GUI_IO_util.msg_openOutputFiles)
help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The Python 3 scripts provide ways of annotating text files for the gender (female/male) of first names found in the text.\n\nTwo different types of gender annotation are applied.\n\n  1. Stanford CoreNLP gender annotator. This annotator requires Coref annotator which only has about 60% accuracy.\n\n  2. A second approach is based on a variety of first name lists (e.g., US Census name lists, Social Security lists, Carnegie Mellon lists). As a point of warning, it should be noted that many first names may be both male or female first names (e.g., Jamie in the US), sometimes depending upon the country (e.g., Andrea is a male name in Italy and a female name in the US).\n\nWhether using CoreNLP or dictionary lists, the algorithms also classify the gender of personal pronouns (he, him, his; she, her, hers as male and female, respectively)."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options)

GUI_util.window.mainloop()

