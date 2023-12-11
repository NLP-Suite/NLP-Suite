# Created on Thu Nov 21 09:45:47 2019
# rewritten by Roberto Franzosi April 2020, May 2022

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"annotator_gender_main.py",['os','tkinter','datetime'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
from datetime import datetime

import GUI_util
import GUI_IO_util
import IO_files_util
import reminders_util
import Stanford_CoreNLP_util
import html_annotator_dictionary_util
import html_annotator_gender_dictionary_util
import config_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,input_main_dir_path,outputDir, openOutputFiles, chartPackage, dataTransformation,
        CoreNLP_gender_annotator_var, CoreNLP_download_gender_file_var, CoreNLP_upload_gender_file_var,
        annotator_dictionary_var, annotator_dictionary_file_var,personal_pronouns_var,plot_var, year_state_var, firstName_entry_var, new_SS_folders):


    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    else:
        config_filename = scriptName.replace('_main.py', '_config.csv')

    filesToOpen=[]

    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]
    if package_display_area_value == '':
        mb.showwarning(title='No setup for NLP package and language',
                       message="The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again.")
        return

    # select dict_var with no file_var
    if annotator_dictionary_var==True and annotator_dictionary_file_var=='':
        if annotator_dictionary_file_var=='':
            mb.showwarning(title='Warning', message='You have selected to annotate your corpus using dictionary entries, but you have not provided the required .csv dictionary file.\n\nPlease, select a .csv dictionary file and try again.')
            return
    # missing required select option
    if CoreNLP_gender_annotator_var==False and annotator_dictionary_var==False and plot_var==False:
        mb.showwarning(title='Warning', message='There are no options selected.\n\nPlease, select one of the available options and try again.')
        return

    # if plot_var and year_state_var!= 'Year of birth':
    #     mb.showwarning('Warning',
    #                    message='The selected option "' + year_state_var + '" is not available yet.\n\nThe only currently available option is "Year of birth".\n\nSorry!')
    #     return

    #CoreNLP annotate
    if CoreNLP_gender_annotator_var==True:
        output = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, input_main_dir_path,
                                        outputDir, openOutputFiles,
                                        chartPackage, dataTransformation,'gender', False, language, export_json_var, memory_var)

        # annotator returns a list and not a string
        # the gender annotator returns 2 Excel charts in addition to the csv file
        if len(output)>0:
            filesToOpen.append(output)

    #dict annotate
    elif annotator_dictionary_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('html_annotator_gender_dictionary_util.py')==False:
            return
        # csvValue_color_list, bold_var, tagAnnotations, '.txt'
        if 'CMU' in annotator_dictionary_file_var:  # CMU column name for Name is Names
            csv_field1_var=['Names']
        else:
            csv_field1_var = ['Name']
        if 'SS' in annotator_dictionary_file_var: # US SS classify gender names as F M rather than Female or Male
            csvValue_color_list = ['Gender', '|', 'F', 'red', '|', 'M', 'blue', '|']
        else:
            csvValue_color_list = ['Gender', '|', 'Female', 'red', '|', 'Male', 'blue', '|']
        tagAnnotations = ['<span style="color: blue; font-weight: bold">', '</span>']
        fileSubsc='gender'
        output= html_annotator_dictionary_util.dictionary_annotate(inputFilename, input_main_dir_path, outputDir, config_filename, annotator_dictionary_file_var,
                                                                   csv_field1_var, csvValue_color_list, True, tagAnnotations, '.txt', fileSubsc)
        if len(output)>0:
            # output=output[0]
            filesToOpen.append(output)

    #plot annotate
    elif plot_var==True:
        if len(new_SS_folders)>0:
            print(new_SS_folders)
            try:
                html_annotator_gender_dictionary_util.build_dictionary_state_year(new_SS_folders[0])
                html_annotator_gender_dictionary_util.build_dictionary_yob(new_SS_folders[1])
            except:
                html_annotator_gender_dictionary_util.build_dictionary_state_year(new_SS_folders[1])
                html_annotator_gender_dictionary_util.build_dictionary_yob(new_SS_folders[0])
        if (year_state_var=='' or firstName_entry_var==''):
            mb.showwarning(title='Warning', message="The plot option requires both 'By year/state' value and first name(s) in the 'Enter firt name(s)' widget.\n\nPlease, enter the required information and try again.")
            return
        else:
            outputFiles = html_annotator_gender_dictionary_util.SSA_annotate(year_state_var,firstName_entry_var,outputDir)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    if openOutputFiles==True:
        nFile=len(filesToOpen)
        if nFile > 5:
            mb.showwarning(title='Warning', message='There are too many output files (' + str(nFile) + ') to be opened automatically.\n\nPlease, do not forget to check the html files in your selected output directory.')
            return
        else:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
#def run(inputFilename,input_main_dir_path,outputDir, dictionary_var, annotator_dictionary, DBpedia_var, annotator_extractor, openOutputFiles):
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                GUI_util.input_main_dir_path.get(),
                GUI_util.output_dir_path.get(),
                GUI_util.open_csv_output_checkbox.get(),
                GUI_util.charts_package_options_widget.get(),
                GUI_util.data_transformation_options_widget.get(),
                CoreNLP_gender_annotator_var.get(),
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


GUI_label='Graphical User Interface (GUI) for Annotating First Names & Pronouns in Documents for Gender (Male/Female)'
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
config_input_output_numeric_options=[5,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)


def clear(e):
    GUI_util.clear("Escape")
    CoreNLP_gender_annotator_var.set(0)
    annotator_dictionary_var.set(0)
    annotator_dictionary_file_var.set('')
    plot_var.set(0)
    year_state_var.set('')
    firstName_entry_var.set('')
window.bind("<Escape>", clear)

CoreNLP_gender_annotator_var=tk.IntVar()

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

CoreNLP_gender_annotator_checkbox = tk.Checkbutton(window, text='Annotate nouns & pronouns gender (via CoreNLP Gender annotator - Neural Network)', variable=CoreNLP_gender_annotator_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,CoreNLP_gender_annotator_checkbox)

# TODO list of male/female names https://nlp.stanford.edu/projects/gender.shtml
CoreNLP_download_gender_file_checkbox = tk.Checkbutton(window, text='Download CoreNLP gender file', variable=CoreNLP_download_gender_file_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,CoreNLP_download_gender_file_checkbox,True)

CoreNLP_upload_gender_file_checkbox = tk.Checkbutton(window, text='Upload CoreNLP gender file', variable=CoreNLP_upload_gender_file_var, onvalue=1, offvalue=0)
# html_annotator_gender_select_dictionary_file_annotator
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate,y_multiplier_integer,CoreNLP_upload_gender_file_checkbox)

annotator_dictionary_var.set(0)
annotator_dictionary_checkbox = tk.Checkbutton(window, text='Annotate first names by gender (via selected dictionary file)', variable=annotator_dictionary_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,annotator_dictionary_checkbox)

annotator_dictionary_button=tk.Button(window, text='Select dictionary file ',command=lambda: get_dictionary_file(window,'Select INPUT dictionary file', [("dictionary files", "*.csv")]))
annotator_dictionary_button.config(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   annotator_dictionary_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "The lib/nameGender subdirectory contains several US names files (Carnegie Mellon list, US Social Security list, US census, NLTK)\nBut... you can also selected a file of names of your own chosing")

#setup a button to open Windows Explorer on the selected input directory
openInputFile_button  = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, state='disabled', text='', command=lambda: IO_files_util.openFile(window, annotator_dictionary_file_var.get()))
# the button widget has hover-over effects (no_hover_over_widget=False) and the info displayed is in text_info
# the two x-coordinate and x-coordinate_hover_over must have the same values
y_multiplier_integer = GUI_IO_util.placeWidget(window,
    GUI_IO_util.html_annotator_gender_select_dictionary_file_button, y_multiplier_integer,
    openInputFile_button, True, False, True, False, 90, GUI_IO_util.html_annotator_gender_select_dictionary_file_button, "Open csv dictionary file")

annotator_dictionary_file=tk.Entry(window, width=GUI_IO_util.html_annotator_gender_annotator_dictionary_file_width,textvariable=annotator_dictionary_file_var)
annotator_dictionary_file.config(state='disabled')
# html_annotator_gender_select_dictionary_file_annotator
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,annotator_dictionary_file)

def get_dictionary_file(window,title,fileType):
    #annotator_dictionary_var.set('')
    filePath = tk.filedialog.askopenfilename(title = title, initialdir =GUI_IO_util.namesGender_libPath, filetypes = fileType)
    if len(filePath)>0:
        # annotator_dictionary_file.config(state='normal')
        annotator_dictionary_file_var.set(filePath)

# personal_pronouns_var.set(1)
# personal_pronouns_checkbox = tk.Checkbutton(window, text='Process personal pronouns', variable=personal_pronouns_var, onvalue=1, offvalue=0)
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,personal_pronouns_checkbox)
#
plot_var.set(0)
plot_checkbox = tk.Checkbutton(window, text='Process names via US SS', variable=plot_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,
    GUI_IO_util.labels_x_coordinate,
    y_multiplier_integer,
    plot_checkbox, True, False, True, False, 90,
    GUI_IO_util.labels_x_coordinate, "Tick the checkbox to search for use of first names by state/year of birth using the US Social Security first names databases")

year_state_lb = tk.Label(window, text='By US state/year')
# html_annotator_gender_select_dictionary_file_annotator
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate,y_multiplier_integer,year_state_lb,True)

year_state_menu = tk.OptionMenu(window,year_state_var, 'State', 'Year of birth', 'State & Year of birth')
year_state_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,
    GUI_IO_util.html_annotator_gender_by_type_dropdown,
    y_multiplier_integer,
    year_state_menu, True, False, True, False, 90,
    GUI_IO_util.html_annotator_gender_by_type_dropdown, "Use the dropdown menu to select the desired first name search")

firstName_entry_lb = tk.Label(window, text='Enter name(s)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,firstName_entry_lb,True)

firstName_entry = tk.Entry(window,width=GUI_IO_util.widget_width_short,textvariable=firstName_entry_var)
firstName_entry.configure(state="disabled")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,
    GUI_IO_util.html_annotator_gender_firstName_entry_pos+100,
    y_multiplier_integer,
    firstName_entry, False, False, True, False, 90,
    GUI_IO_util.html_annotator_gender_firstName_entry_pos, "Enter the comma-separated first names whose use by state/year of birth you wish to process")

open_SS_website_button=tk.Button(window, text='Open US SS website ',command=lambda: open_SS_website())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,
    GUI_IO_util.labels_x_indented_coordinate,
    y_multiplier_integer,
    open_SS_website_button, True, False, True, False, 90,
    GUI_IO_util.labels_x_indented_coordinate, "Open the US Social Security website where you can download first name databases: National data and State-specific data\nYou must be connected to the internet")
#
# https://www.ssa.gov/oact/babynames/limits.html
new_SS_folders_var.set(0)
new_SS_folders_checkbox = tk.Checkbutton(window, text='Generate new US Social Security files (by US State, Year of birth, US State & Year of birth)', variable=new_SS_folders_var, onvalue=1, offvalue=0, command=lambda: get_new_SS_folders(window))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,
    GUI_IO_util.open_TIPS_x_coordinate,
    y_multiplier_integer,
    new_SS_folders_checkbox, False, False, True, False, 90,
    GUI_IO_util.open_TIPS_x_coordinate, "After downloading the US SS Nation data and State-specific data, tick the checkbox to prepare the data for NLP Suite algorithms")

def open_SS_website():
    url = 'https://www.ssa.gov/oact/babynames/limits.html'
    from urllib.request import urlopen  # used to call Google website to display a selected pin
    message_title=''
    message=''
    website_name='US Social Security'
    IO_libraries_util.open_url(website_name, url, ask_to_open=False, message_title=message_title, message=message)

def get_new_SS_folders(window):
    new_SS_folders.clear()
    new_SS_folder_var.set('')
    mb.showwarning(title='Warning', message='You are about to select the two folders where you downloaded and unzipped the most up-to-date gender names databases \'National data\' and \'State-specific data\' from the US Social Security website\n\nhttps://www.ssa.gov/oact/babynames/limits.html\n\nYOU WILL LOOP TWICE TO SELECT BOTH FOLDERS.')
    for i in range(2):
        if len(new_SS_folders)==0:
            title="Select INPUT new SS folder for the 'National data' database (downloaded folder 'names')"
        else:
            title="Select INPUT new SS folder for the 'State-specific data' database (downloaded folder 'namesbystate')"
        folderPath = tk.filedialog.askdirectory(initialdir=GUI_IO_util.namesGender_libPath, title = title)
        if len(folderPath)>0:
            if folderPath in new_SS_folders:
                mb.showwarning(title='Warning', message='You have selected the same SS folder twice. The two folders are expected to be different.\n\nPlease, try again.')
                return
            new_SS_folders.append(folderPath)
    new_SS_folder_var.set(new_SS_folders)
    if len(new_SS_folders)!=2:
        mb.showwarning(title='Warning', message='You were expected to select two folders (downloaded names & namesbystate).\n\nPlease, try again if you wish to update your SS gender names databases.')
        new_SS_folder_var.set('')
        new_SS_folders.clear()

    a1 = new_SS_folders[0]
    a2 = new_SS_folders[1]
    process_names_folder(a1,GUI_IO_util.namesGender_libPath+os.sep+"SS_yearOfBirth.csv")
    process_namesbystate_folder(a2, GUI_IO_util.namesGender_libPath + os.sep+"SS_state_yearOfBirth.csv")
    if os.path.isfile(GUI_IO_util.namesGender_libPath+os.sep+"SS_yearOfBirth.csv") and os.path.isfile(GUI_IO_util.namesGender_libPath+os.sep+"SS_state_yearOfBirth.csv"):
        mb.showwarning(title='Warning',message='The new Social Security files by year of birth and state were successfully created in the directory ' + GUI_IO_util.namesGender_libPath)
    else:
        mb.showwarning(title='Warning',message="The new Social Security files by year of birth and state files failed to be created.\n\nPlease, check your input 'names' and 'namesbystate' directories and your output directory " + GUI_IO_util.namesGender_libPath + " and try again.")

def process_names_folder(input_folder, output_file):
    file_list = os.listdir(input_folder)
    output_data = []
    for file in file_list:
        if file.upper().endswith('.TXT'):
            year = file[3:7]  # Extract the year from the file name, e.g., yob1918.txt -> 1918
            with open(os.path.join(input_folder, file)) as f:
                content = f.readlines()
            for line in content:
                name, gender, frequency = line.strip().split(',')
                output_data.append(f'{name},{gender},{frequency},{year}')
    output_data = '\n'.join(output_data)
    with open(output_file, 'w') as f:
        f.write('Name,Gender,Frequency,Year of birth\n' + output_data)
def process_namesbystate_folder(input_folder, output_file):
    file_list = os.listdir(input_folder)
    output_data = []
    for file in file_list:
        if file.upper().endswith('.TXT'):
            with open(os.path.join(input_folder, file)) as f:
                content = f.readlines()
            output_data.extend(content)
    output_data = ''.join(output_data)
    with open(output_file, 'w') as f:
        f.write('State,Gender,Year of birth,Name,Frequency\n' + output_data)

# new_SS_select_button=tk.Button(window, width=20, text='Select new SS folders',command=lambda: get_new_SS_folders(window))
# new_SS_select_button.config(state='disabled')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,new_SS_select_button,True)
#
# #setup a button to open Windows Explorer on the selected input directory
# open_new_SS_folder_button = tk.Button(window, width=3, text='', command=lambda: IO_files_util.openExplorer(window, new_SS_folder_var.get()))
# # the button widget has hover-over effects (no_hover_over_widget=False) and the info displayed is in text_info
# # the two x-coordinate and x-coordinate_hover_over must have the same values
# y_multiplier_integer = GUI_IO_util.placeWidget(window,
#     GUI_IO_util.html_annotator_gender_select_dictionary_file_button,
#     y_multiplier_integer,
#     open_new_SS_folder_button, True, False, True, False, 90, GUI_IO_util.html_annotator_gender_select_dictionary_file_button, "Open SS file directory")
#
# new_SS_folder=tk.Entry(window, width=GUI_IO_util.html_annotator_gender_SS_folder_width,textvariable=new_SS_folder_var)
# new_SS_folder.config(state='disabled')
# # html_annotator_gender_select_dictionary_file_annotator
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,new_SS_folder,True)

# last_SS_year_var.set(2021)
# last_SS_year=tk.Entry(window, width=6,textvariable=last_SS_year_var)
# last_SS_year.config(state='disabled')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.html_annotator_gender_select_SS_folder, y_multiplier_integer,last_SS_year)

# def checkUSSSUpdate():
#     if annotator_dictionary_var.get()==True or plot_var.get() == True:
#         currentYear = datetime.now().year
#         yearDiff = currentYear - last_SS_year_var.get()
#         if yearDiff >= 2:
#             reminders_util.checkReminder(
#                     config_filename,
#                     reminders_util.title_options_SSdata,
#                     reminders_util.message_SSdata,
#                     True)

def activate_all_options(*args):
    CoreNLP_gender_annotator_checkbox.configure(state="normal")
    annotator_dictionary_checkbox.configure(state="normal")
    plot_checkbox.configure(state="normal")
    CoreNLP_download_gender_file_checkbox.configure(state='disabled')
    CoreNLP_upload_gender_file_checkbox.configure(state='disabled')
    annotator_dictionary_button.config(state='disabled')
    openInputFile_button.config(state='disabled')
    annotator_dictionary_file.config(state='disabled')
    # personal_pronouns_checkbox.configure(state='disabled')
    # year_state_var.set('')
    year_state_menu.configure(state='disabled')
    firstName_entry.configure(state="disabled")
    # new_SS_folders_checkbox.configure(state="disabled")
    # new_SS_select_button.config(state='disabled')
    # open_new_SS_folder_button.config(state='disabled')
    # new_SS_folder_var.set("")
    # new_SS_folder.config(state='disabled')
    new_SS_folders.clear()
    if CoreNLP_gender_annotator_var.get()==True:
        annotator_dictionary_checkbox.configure(state="disabled")
        plot_checkbox.configure(state="disabled")
        # CoreNLP_download_gender_file_checkbox.configure(state='normal')
        # CoreNLP_upload_gender_file_checkbox.configure(state='normal')
    if annotator_dictionary_var.get()==True:
        # checkUSSSUpdate()
        CoreNLP_gender_annotator_checkbox.configure(state="normal")
        plot_checkbox.configure(state="disabled")
        annotator_dictionary_button.config(state='normal')
        openInputFile_button.config(state='normal')
        # annotator_dictionary_file.config(state='normal')
        # personal_pronouns_checkbox.configure(state='normal')
    if plot_var.get()==True:
        # checkUSSSUpdate()
        CoreNLP_gender_annotator_checkbox.configure(state="disabled")
        annotator_dictionary_checkbox.configure(state="disabled")
        new_SS_folders_checkbox.configure(state="normal")
        year_state_menu.configure(state='normal')
        # new_SS_select_button.config(state='normal')
        # open_new_SS_folder_button.config(state='normal')
        # new_SS_select_button.config(state='normal')
    else:
        year_state_menu.configure(state='disabled')
        firstName_entry.configure(state="disabled")
        year_state_var.set('')
        firstName_entry_var.set('')
    if year_state_var.get()!='':
        firstName_entry.configure(state="normal")
    # if new_SS_folders_checkbox:
    #     new_SS_select_button.config(state='normal')
    # else:
    #     new_SS_select_button.config(state='disabled')

CoreNLP_gender_annotator_var.trace('w',activate_all_options)
annotator_dictionary_var.trace('w',activate_all_options)
plot_var.trace('w',activate_all_options)
year_state_var.trace('w',activate_all_options)

activate_all_options()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf','Statistical measures':'TIPS_NLP_Statistical measures.pdf','Gender annotator':'TIPS_NLP_Gender annotator.pdf','NER (Named Entity Recognition)':'TIPS_NLP_NER (Named Entity Recognition) Stanford CoreNLP.pdf','CoreNLP Coref':'TIPS_NLP_Stanford CoreNLP coreference resolution.pdf'}
TIPS_options='csv files - Problems & solutions','Statistical measures','Gender annotator', 'NER (Named Entity Recognition)', 'CoreNLP Coref'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, tick the checkbox if you wish to run the Stanford CoreNLP gender annotator. The CoreNLP gender annotator is based on CoreNLP annotator which, unfortunately, only has about 60\% accuracy. The algorithm annotates the gender of both first names and personal pronouns (he, him, his, she, her, hers).\n\nThe CoreNLP annotator uses a neural network approach. This annotator requires a great deal of memory.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, tick the DOWNLOAD checkbox to dowload the Stanford CoreNLP gender file for editing.\n\nTick the UPLOAD checkbox to upload the edited Stanford CoreNLP gender file.\n\nThe CoreNLP gender file has the format JOHN\\MALE with one NAME\\GENDER entry per line. The CoreNLP gender file is found in The default gender mappings file is in the stanford-corenlp-3.5.2-models.jar file. It is called tmp-stanford-models-expanded/edu/stanford/nlp/models/gender/first_name_map_small')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox if you wish to annotate the first names found in a text using an input dictionary list of gender annotated first names. As a caveat, keep in mind that some first names may be both male and female names (e.g., Jamie in the US) or male and female depending upon the country (e.g., Andrea is a male name in Italy, a female name in the US).\n\nThe 'Select dictionary file' widget will become available when the 'Annotate first names by gender' checkbox is ticked off.\n\nIN INPUT THE ANNOTATOR ALGORITHM EXPECTS A CSV FILE WITH AT LEAST TWO COLUMNS LABELED 'Name' AND 'Gender' CONTAINING RESPECTIVELY THE FIRST NAMES AND GENDER TO BE TAGGED (GENDER VALUES ARE CASE-SENSITIVE 'Male' or 'Female').")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, click on the \'Select dictionary file\' to select the first name file to be used to annotate the first names found in the input text(s) by gender.\n\nSeveral files are available as default files in the lib subdirectory (e.g., the 1990 US census lists, the US Social Security list, Carnegie Mellon lists). But, users can also select any file of their choice.\n\nThe 'Select dictionary file' widget will become available when the 'Annotate first names by gender' checkbox is ticked off.\n\nIN INPUT THE ANNOTATOR ALGORITHM EXPECTS A CSV FILE WITH AT LEAST TWO COLUMNS LABELED 'Name' AND 'Gender' CONTAINING RESPECTIVELY THE FIRST NAMES AND GENDER TO BE TAGGED (GENDER VALUES ARE CASE-SENSITIVE 'Male' or 'Female').")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox if you wish to process selected first name(s) by US State, by Year of birth of individuals bearing the first name, or State & Year of birth, using United States Social Security lists.\n   Then, using the dropdown menu, select the desired display: by State, by Year of birth, by State & year of birth \n   Finally, enter comma-separated first names, including double names, e.g., Jo Ann.\n\nThe name database is downloadable from the US Social Security website\n\nhttps://www.ssa.gov/oact/babynames/limits.html\n\nAll names are from Social Security card applications for births that occurred in the United States after 1879. Note that many people born before 1937 never applied for a Social Security card, so their names are not included in our data. For others who did apply, our records may not show the place of birth, and again their names are not included in our data.\n\nNAMES FOR THE US ARE AVAILABLE SINCE 1879.\n\nNAMES BY STATE ARE AVAILABLE SINCE 1910.\n\nTHE ALGORITHM WILL PLOT BUT NOT ANNOTATE THE SELECTED NAMES. IF YOU WISH TO ANNOTATE YOUR CORPUS WITH US SOCIAL SECURITY NAMES, USE THE 'Annotate first names by gender' WIDGET INSTEAD.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, click on the \'Open US Social Security website\' button to download the Nation data and State-specific data from the US Social Security website.\n\nTick the checkbox if you wish to generate new US Social Security files (by US State, Year of birth,  US State & Year of birth) required by the NLP Suite algorithms.\n\nTHIS IS ONLY NECESSARY WHEN THE US SOCIAL SECURITY ADMINISTRATION RELEASES NEW GENDER NAMES DATA.\n\nThe name database is downloadable from the US Social Security website\n\nhttps://www.ssa.gov/oact/babynames/limits.html\n\nAll names are from Social Security card applications for births that occurred in the United States after 1879. Note that many people born before 1937 never applied for a Social Security card, so their names are not included in our data. For others who did apply, our records may not show the place of birth, and again their names are not included in our data.\n\nNAMES FOR THE US ARE AVAILABLE SINCE 1879.\n\nNAMES BY STATE ARE AVAILABLE SINCE 1910.')
    # y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, click on the \'Select new SS folders\' button to select the two folders where you downloaded and unzipped the most up-to-date gender names databases \'National data\' and \'State-specific data\' from the US Social Security website\n\nhttps://www.ssa.gov/oact/babynames/limits.html\n\nAll names are from Social Security card applications for births that occurred in the United States after 1879. Note that many people born before 1937 never applied for a Social Security card, so their names are not included in our data. For others who did apply, our records may not show the place of birth, and again their names are not included in our data.\n\nNAMES FOR THE US ARE AVAILABLE SINCE 1879.\n\nNAMES BY STATE ARE AVAILABLE SINCE 1910.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 scripts provide ways of annotating text files for the gender (female/male) of first names found in the text.\n\nTwo different types of gender annotation are applied.\n\n  1. Stanford CoreNLP gender annotator. This annotator requires Coref annotator which only has about 60% accuracy.\n\n  2. A second approach is based on a variety of first name lists (e.g., US Census name lists, Social Security lists, Carnegie Mellon lists). As a point of warning, it should be noted that many first names may be both male or female first names (e.g., Jamie in the US), sometimes depending upon the country (e.g., Andrea is a male name in Italy and a female name in the US)."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()

