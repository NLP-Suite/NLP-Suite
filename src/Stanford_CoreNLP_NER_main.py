# Roberto Franzosi September 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Stanford_CoreNLP_NER_extractor",['os','pandas','tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import Stanford_CoreNLP_annotator_util
import IO_files_util
import IO_user_interface_util

# RUN section ______________________________________________________________________________________________________________________________________________________

# def run(CoreNLPdir,inputFilename,inputDir,outputDir,openOutputFiles,createCharts,chartPackage,encoding_var,memory_var,extract_date_from_text_var,extract_date_from_filename_var,date_format,date_separator_var,date_position_var,NER_list,NER_split_prefix_values_entry_var,NER_split_suffix_values_entry_var,NER_sentence_var):
def run(inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage,
        encoding_var,
        memory_var, document_length_var, limit_sentence_length_var,
        extract_date_from_text_var, extract_date_from_filename_var, date_format, date_separator_var,
        date_position_var, language_var, NER_list, NER_sentence_var):

    filesToOpen = []  # Store all files that are to be opened once finished

    if len(NER_list)==0:
        mb.showwarning(title='No NER tag selected', message='No NER tag has been selected.\n\nPlease, select an NER tag and try again.')
        return

    if language_var == 'Arabic':
        mb.showwarning(title='Language',
                       message='The Stanford CoreNLP NER annotator is not available for Arabic.')
        return

    tempOutputFiles = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir, outputDir,
                                                        openOutputFiles, createCharts, chartPackage,
                                                        'NER',
                                                        language=language_var,
                                                        NERs=NER_list,
                                                        DoCleanXML=False,
                                                        memory_var=memory_var,
                                                        document_length=document_length_var,
                                                        sentence_length=limit_sentence_length_var,
                                                        extract_date_from_text_var=extract_date_from_text_var,
                                                        extract_date_from_filename_var=extract_date_from_filename_var,
                                                        date_format=date_format,
                                                        date_separator_var=date_separator_var,
                                                        date_position_var=date_position_var)

    if len(tempOutputFiles)>0:
        filesToOpen.extend(tempOutputFiles)

    # TODO Excel charts; the basic bar charts are carried out in the _annotator_util

    # # TODO date
    # if extract_date_from_text_var or extract_date_from_filename_var:
    # 	df = pd.DataFrame(data, columns=['Word', 'NER', 'Sentence ID', 'Sentence', 'Document ID', 'Document', 'Date'])
    # else:
    # 	df = pd.DataFrame(data, columns=['Word', 'NER', 'Sentence ID', 'Sentence', 'Document ID', 'Document'])
    # if NER_sentence_var == 1:
    # 	df = charts_Excel_util.add_missing_IDs(df)

    # if inputDir!='':
    # 	output_filename = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'NER_extractor_dir')
    # else:
    # 	output_filename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NER_extractor')
    # df.to_csv(output_filename,index=False)
    # filesToOpen.append(output_filename)

    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(
                            GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_chart_output_checkbox.get(),
                            GUI_util.charts_dropdown_field.get(),
                            encoding_var.get(),
                            memory_var.get(),
                            document_length_var.get(),
                            limit_sentence_length_var.get(),
                            extract_date_from_text_var.get(),
                            extract_date_from_filename_var.get(),
                            date_format.get(),
                            date_separator_var.get(),
                            date_position_var.get(),
                            language_var.get(),
                            NER_list,
                            NER_sentence_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=520, # height at brief display
                             GUI_height_full=590, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for NER (Named Entity Recognition) Extraction'
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
config_input_output_numeric_options=[2,1,0,1]

head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = scriptName.replace('main.py', 'config.csv')

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
inputFilename=GUI_util.inputFilename

input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)

NER_list=[]

encoding_var=tk.StringVar()

memory_var = tk.IntVar()

extract_date_from_text_var= tk.IntVar()
extract_date_from_filename_var= tk.IntVar()

date_format = tk.StringVar()
date_separator_var = tk.StringVar()
date_position_var = tk.IntVar()

language_var = tk.StringVar()
NER_tag_var = tk.StringVar()
NER_sentence_var = tk.StringVar()
NER_entry_var = tk.StringVar()
# NER_split_values_prefix_entry_var = tk.StringVar()
# NER_split_values_suffix_entry_var = tk.StringVar()

encoding_var.set('utf-8')
encodingValue = tk.OptionMenu(window,encoding_var,'utf-8','utf-16-le','utf-32-le','latin-1','ISO-8859-1')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,encodingValue,True)
encoding_lb = tk.Label(window, text='Select the encoding type (utf-8 default)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,encoding_lb)

GUI=''

def open_GUI1():
    call("python file_checker_converter_cleaner_main.py", shell=True)

pre_processing_button = tk.Button(window, text='Pre-processing tools (file checking & cleaning GUI)',command=open_GUI1)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               pre_processing_button)

# language options
language_var_lb = tk.Label(window, text='Language ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               language_var_lb, True)

language_var.set('English')
language_menu = tk.OptionMenu(window, language_var, 'Arabic','Chinese', 'English', 'German','Hungarian','Italian','Spanish')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+70,
                                               y_multiplier_integer, language_menu, True)
# memory options
memory_var_lb = tk.Label(window, text='Memory ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+210, y_multiplier_integer,
                                               memory_var_lb, True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(6)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate() + 280, y_multiplier_integer,
                                               memory_var, True)

document_length_var_lb = tk.Label(window, text='Document length')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate()+210, y_multiplier_integer,
                                               document_length_var_lb, True)

document_length_var = tk.Scale(window, from_=40000, to=90000, orient=tk.HORIZONTAL)
document_length_var.pack()
document_length_var.set(90000)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate()+330, y_multiplier_integer,
                                               document_length_var,True)

limit_sentence_length_var_lb = tk.Label(window, text='Limit sentence length')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 530, y_multiplier_integer,
                                               limit_sentence_length_var_lb,True)

limit_sentence_length_var = tk.Scale(window, from_=70, to=400, orient=tk.HORIZONTAL)
limit_sentence_length_var.pack()
limit_sentence_length_var.set(100)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 680, y_multiplier_integer,
                                               limit_sentence_length_var)

extract_date_lb = tk.Label(window, text='Extract date (for dynamic GIS)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,extract_date_lb,True)

extract_date_from_text_var.set(0)
extract_date_from_text_checkbox = tk.Checkbutton(window, variable=extract_date_from_text_var, onvalue=1, offvalue=0)
extract_date_from_text_checkbox.config(text="From document content")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate(),
                                               y_multiplier_integer, extract_date_from_text_checkbox, True)

extract_date_from_filename_var.set(0)
extract_date_from_filename_checkbox = tk.Checkbutton(window, variable=extract_date_from_filename_var, onvalue=1, offvalue=0)
extract_date_from_filename_checkbox.config(text="From filename")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 190,
                                               y_multiplier_integer, extract_date_from_filename_checkbox, True)

date_format_lb = tk.Label(window,text='Format ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 320,
                                               y_multiplier_integer, date_format_lb, True)
date_format.set('mm-dd-yyyy')
date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy','yyyy-mm-dd','yyyy-dd-mm','yyyy-mm','yyyy')
date_format_menu.configure(width=10,state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 380,
                                               y_multiplier_integer, date_format_menu, True)
date_separator_var.set('_')
date_separator_lb = tk.Label(window, text='Character separator ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 510,
                                               y_multiplier_integer, date_separator_lb, True)
date_separator = tk.Entry(window, textvariable=date_separator_var)
date_separator.configure(width=2,state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 640,
                                               y_multiplier_integer, date_separator, True)
date_position_var.set(2)
date_position_menu_lb = tk.Label(window, text='Position ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 670,
                                               y_multiplier_integer, date_position_menu_lb, True)
date_position_menu = tk.OptionMenu(window,date_position_var,1,2,3,4,5)
date_position_menu.configure(width=1,state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 740,
                                               y_multiplier_integer, date_position_menu)


def check_dateFields(*args):
    if extract_date_from_text_var.get() == 1:
        extract_date_from_filename_checkbox.config(state="disabled")
    else:
        extract_date_from_text_checkbox.config(state="normal")
        extract_date_from_filename_checkbox.config(state="normal")
    if extract_date_from_filename_var.get() == 1:
        extract_date_from_text_checkbox.config(state="disabled")
        date_format_menu.config(state="normal")
        date_separator.config(state='normal')
        date_position_menu.config(state='normal')
    else:
        date_format_menu.config(state="disabled")
        date_separator.config(state='disabled')
        date_position_menu.config(state="disabled")
extract_date_from_text_var.trace('w',check_dateFields)
extract_date_from_filename_var.trace('w',check_dateFields)

NER_tag_lb = tk.Label(window, text='NER tags')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,NER_tag_lb,True)

# NER tags menu
NER_tag_var.set('')
NER_menu = tk.OptionMenu(window,NER_tag_var,'--- All NER tags', '--- All quantitative expressions','NUMBER', 'ORDINAL', 'PERCENT', '--- All social actors', 'PERSON', 'ORGANIZATION', '--- All spatial expressions', 'CITY', 'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION', '--- All temporal expressions', 'DATE', 'TIME', 'DURATION', 'SET',  '--- All other expressions', 'MISC', 'CAUSE_OF_DEATH', 'CRIMINAL_CHARGE', 'EMAIL',  'IDEOLOGY', 'MONEY',  'NATIONALITY', 'RELIGION', 'TITLE','URL')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+100,y_multiplier_integer,NER_menu,True)

add_NER_button = tk.Button(window, text='+', width=2,height=1,state='disabled',command=lambda: activate_NER_Options())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate()+40,y_multiplier_integer,add_NER_button, True)

reset_NER_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: clear_NER_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate()+70,y_multiplier_integer,reset_NER_button,True)

NER_entry_lb = tk.Label(window, text='NER list')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 140,y_multiplier_integer,NER_entry_lb,True)

NER_entry = tk.Entry(window,width=70,textvariable=NER_entry_var)
NER_entry.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate()+ 200,y_multiplier_integer,NER_entry)

# openFile_button = tk.Button(window, width=3, text='',command=lambda: IO_files_util.openFile(window, os.path.join(GUI_IO_util.wordLists_libPath,'NER_prefix_suffix.csv')))
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,openFile_button,True)

# NER_split_values_prefix_entry_lb = tk.Label(window, text='NER split values (Prefix)')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 40,y_multiplier_integer,NER_split_values_prefix_entry_lb,True)
#
# NER_split_values_prefix_entry = tk.Entry(window,width=70,textvariable=NER_split_values_prefix_entry_var)
# NER_split_values_prefix_entry.configure(state="disabled")
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate()+ 200,y_multiplier_integer,NER_split_values_prefix_entry)
#
# NER_split_values_suffix_entry_lb = tk.Label(window, text='NER split values (Suffix)')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 40,y_multiplier_integer,NER_split_values_suffix_entry_lb,True)
#
# NER_split_values_suffix_entry = tk.Entry(window,width=70,textvariable=NER_split_values_suffix_entry_var)
# NER_split_values_suffix_entry.configure(state="disabled")
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate()+ 200,y_multiplier_integer,NER_split_values_suffix_entry)

def clear(e):
    clear_NER_list()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

def changed_inputFilenamename(*args):
    # display the date widgets
    if inputFilename.get().endswith('.txt') or len(input_main_dir_path.get()) > 0:
        extract_date_from_text_checkbox.config(state='normal')
        extract_date_from_filename_checkbox.config(state='normal')
    else:
        extract_date_from_text_checkbox.config(state='disabled')
        extract_date_from_filename_checkbox.config(state='disabled')
inputFilename.trace('w', changed_inputFilenamename)
input_main_dir_path.trace('w', changed_inputFilenamename)

def add_NER_tag(*args):
    global NER_list

    # if '---' in str(NER_list):
    #     mb.showwarning(title='Warning', message='You cannot add any other NER tags once you have selected an NER set ---\n\nPlease, press ESCape or RESET or RUN.')
    #     window.focus_force()
    #     return

    if NER_tag_var.get() == '--- All NER tags':
        NER_list = ['PERSON', 'ORGANIZATION', 'MISC', 'MONEY', 'NUMBER', 'ORDINAL',
                    'PERCENT', 'DATE', 'TIME', 'DURATION', 'SET', 'EMAIL', 'URL', 'CITY',
                    'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION', 'NATIONALITY', 'RELIGION', 'TITLE', 'IDEOLOGY', 'CRIMINAL_CHARGE',
                    'CAUSE_OF_DEATH']
        NER_entry_var.set('PERSON, ORGANIZATION, MISC, MONEY, NUMBER, ORDINAL, PERCENT, DATE, TIME, DURATION, SET, EMAIL, URL, CITY,STATE_OR_PROVINCE, COUNTRY, LOCATION, NATIONALITY, RELIGION, TITLE, IDEOLOGY, CRIMINAL_CHARGE,CAUSE_OF_DEATH')
    elif NER_tag_var.get() == '--- All quantitative expressions':
        NER_list = ['NUMBER', 'ORDINAL', 'PERCENT']
        NER_entry_var.set('NUMBER, ORDINAL, PERCENT')
    elif NER_tag_var.get() == '--- All social actors':
        NER_list = ['PERSON', 'ORGANIZATION']
        NER_entry_var.set('PERSON, ORGANIZATION')
    elif NER_tag_var.get() == '--- All spatial expressions':
        NER_list = ['CITY', 'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION']
        NER_entry_var.set('CITY, STATE_OR_PROVINCE, COUNTRY, LOCATION')
    elif NER_tag_var.get() == '--- All temporal expressions':
        NER_list = ['DATE', 'TIME', 'DURATION', 'SET']
        NER_entry_var.set('DATE, TIME, DURATION, SET')
    elif NER_tag_var.get()=='--- All other expressions':
        mb.showwarning(title='Warning', message='You cannot select the option --- All other expressions.\n\nPlease, select a different option and try again.')
        NER_tag_var.set('')
        window.focus_force()
        return
    if NER_tag_var.get() in NER_list and not('---' in NER_tag_var.get()):
        mb.showwarning(title='Warning', message='The NER tag "'+ NER_tag_var.get() + '" is already in your selection list: '+ str(NER_entry_var.get()) + '.\n\nPlease, select another NER tag.')
        window.focus_force()
        return
    if NER_tag_var.get()!='':
        # NER_split_values_prefix_entry.configure(state="normal")
        # NER_split_values_suffix_entry.configure(state="normal")
        if not('---' in NER_tag_var.get()):
            NER_list.append(NER_tag_var.get())
            if len(NER_list)==1:
                NER_entry_var.set(NER_tag_var.get())
            else:
                NER_entry_var.set(NER_entry_var.get()+', '+NER_tag_var.get())
        NER_menu.configure(state='disabled')
        add_NER_button.configure(state="normal")
        reset_NER_button.configure(state="normal")
        # if 'spatial' in NER_tag_var.get() or 'CITY' in NER_tag_var.get() or 'COUNTRY' in NER_tag_var.get() or 'STATE_OR_PROVINCE' in NER_tag_var.get():
        #     # GUI_IO_util.wordLists_libPath
        #     prefs = ''
        #     sufs = ''
        #     prefsuf_table = pd.read_csv(os.path.join(GUI_IO_util.wordLists_libPath,"NER_prefix_suffix.csv"))
        #     for p in prefsuf_table["Prefix"]:
        #         # Make sure the value is not null because we may have more values in prefix than suffix, vice versa.
        #         # When we have more vals in one column than the other, the result will be nulls in the shorter col
        #         # to fill the gaps. We need to skip these.
        #         if pd.notna(p):
        #             prefs += p + ", "
        #     for s in prefsuf_table["Suffix"]:
        #         if pd.notna(s):
        #             sufs += s + ", "
    #         # We use [:-2] to trim off the trailing comma and space characters
    #         NER_split_values_prefix_entry_var.set(prefs[:-2])
    #         NER_split_values_suffix_entry_var.set(sufs[:-2])
    # else:
    #     NER_split_values_prefix_entry.configure(state="disabled")
    #     NER_split_values_suffix_entry.configure(state="disabled")
NER_tag_var.trace ('w',add_NER_tag)

add_NER_tag()

def activate_NER_Options():
    NER_menu.configure(state='normal')
    add_NER_button.configure(state="disabled")

def clear_NER_list():
    NER_list.clear()
    NER_tag_var.set('')
    NER_entry_var.set('')
    # NER_split_values_prefix_entry_var.set('')
    # NER_split_values_suffix_entry_var.set('')
    activate_NER_Options()

NER_sentence_var.set(0)
NER_sentence_checkbox = tk.Checkbutton(window, variable=NER_sentence_var, onvalue=1, offvalue=0)
NER_sentence_checkbox.config(text="NER tags by sentence index")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,NER_sentence_checkbox)

def open_GUI2():
    call("python CoNLL_table_analyzer_main.py", shell=True)

CoNLL_table_analyzer_button = tk.Button(window, text='Open the CoNLL table analyzer GUI',command=open_GUI2)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               CoNLL_table_analyzer_button)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Stanford CoreNLP supported languages':'TIPS_NLP_Stanford CoreNLP supported languages.pdf',
               'Stanford CoreNLP performance & accuracy':'TIPS_NLP_Stanford CoreNLP performance and accuracy.pdf',
               'Stanford CoreNLP memory issues': 'TIPS_NLP_Stanford CoreNLP memory issues.pdf',
               'NER (Named Entity Recognition)':'TIPS_NLP_NER (Named Entity Recognition).pdf',
               'CoNLL Table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",
               'POSTAG (Part of Speech Tags)':'TIPS_NLP_POSTAG (Part of Speech Tags) Stanford CoreNLP.pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf'}
TIPS_options='Stanford CoreNLP supported languages','Stanford CoreNLP performance & accuracy','Stanford CoreNLP memory issues','NER (Named Entity Recognition)','CoNLL Table','POSTAG (Part of Speech Tags)','csv files - Problems & solutions','Statistical measures'


# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the type of encoding you wish to use.\n\nLocations in different languages may require encodings (e.g., latin-1 for French or Italian) different from the standard (and default) utf-8 encoding.\n\nTick the 'Filename embeds date' checkbox if the filename embeds a date (e.g., The New York Times_12-05-1885). The date will then be used to construct dynamic GIS models."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, click on the 'Pre-processing tools' button to open the GUI where you will be able to perform a variety of\n   file checking options (e.g., utf-8 encoding compliance of your corpus or sentence length);\n   file cleaning options (e.g., convert non-ASCII apostrophes & quotes and % to percent).\n\nNon utf-8 compliant texts are likely to lead to code breakdown in various algorithms.\n\nASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n\n% signs will lead to code breakdon of Stanford CoreNLP.\n\nSentences without an end-of-sentence marker (. ! ?) in Stanford CoreNLP will be processed together with the next sentence, potentially leading to very long sentences.\n\nSentences longer than 70 or 100 words may pose problems to Stanford CoreNLP (the average sentence length of modern English is 20 words). Please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the language to be used: English, Arabic, Chinese, German, Hungarian, Italian, or Spanish.\n\nNot all annotators are available for all languages, in fact, most are not. Please, read the TIPS file TIPS_NLP_Stanford CoreNLP supported languages.pdf.\n\nThe Stanford CoreNLP performance is affected by various issues: memory size of your computer, document size, sentence length\n\nPlease, select the memory size Stanford CoreNLP will use. Default = 4. Lower this value if CoreNLP runs out of resources.\n   For CoreNLP co-reference resolution you may wish to increase the value when processing larger files (compatibly with the memory size of your machine).\n\nLonger documents affect performace. Stanford CoreNLP has a limit of 100,000 characters processed (the NLP Suite limits this to 90,000 as default). If you run into performance issues you may wish to further reduce the document size.\n\nSentence length also affect performance. The Stanford CoreNLP recommendation is to limit sentence length to 70 or 100 words.\n   You may wish to compute the sentence length of your document(s) so that perhaps you can edit the longer sentences.\n\nOn these issues, please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","The GIS algorithms allow you to extract a date to be used to build dynamic GIS maps. You can extract dates from the document content or from the filename if this embeds a date.\n\nPlease, the tick the checkbox 'From document content' if you wish to extract normalized NER dates from the text itself.\n\nPlease, tick the checkbox 'From filename' if filenames embed a date (e.g., The New York Times_12-05-1885).\n\nDATE WIDGETS ARE NOT VISIBLE WHEN SELECTING A CSV INPUT FILE.\n\nOnce you have ticked the 'Filename embeds date' option, you will need to provide the follwing information:\n   1. the date format of the date embedded in the filename (default mm-dd-yyyy); please, select.\n   2. the character used to separate the date field embedded in the filenames from the other fields (e.g., _ in the filename The New York Times_12-23-1992) (default _); please, enter.\n   3. the position of the date field in the filename (e.g., 2 in the filename The New York Times_12-23-1992; 4 in the filename The New York Times_1_3_12-23-1992 where perhaps fields 2 and 3 refer respectively to the page and column numbers); please, select.\n\nIF THE FILENAME EMBEDS A DATE AND THE DATE IS THE ONLY FIELD AVAILABLE IN THE FILENAME (e.g., 2000.txt), enter . in the 'Date character separator' field and enter 1 in the 'Date position' field."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the 23 NER tags that you would like to extract.\n\nFor English, the Stanford CoreNLP, by default through the NERClassifierCombiner annotator, recognizes the following NER values:\n  named (PERSON, LOCATION, ORGANIZATION, MISC);\n  numerical (MONEY, NUMBER, ORDINAL, PERCENT);\n  temporal (DATE, TIME, DURATION, SET).\n  In addition, via regexner, the following entity classes are tagged: EMAIL, URL, CITY, STATE_OR_PROVINCE, COUNTRY, NATIONALITY, RELIGION, (job) TITLE, IDEOLOGY, CRIMINAL_CHARGE, CAUSE_OF_DEATH.\n\nClick on the + button to add more NER tags.\nClick on the Reset button (or ESCape) to cancel all selected options and start over."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to plot the extracted NER tags by sentence index."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","If you have run a Stanford CoreNLP parser and you have a CoNLL table containing NER values, click on the 'Open table analyzer (GUI)' to have access to any desired CoNLL table."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),0)

# change the value of the readMe_message
readMe_message="This Python 3 script will extract NER tags from either tetxt file(s) using the Stanford CoreNLP NER annotator.\n\nIn INPUT the algorith expects a single txt file or a set of txt files in a directory.\n\nIn OUTPUT the algorithm exports a csv file of extracted NER values and 2 Excel bar charts (if the checkbox 'Automatically compute Excel chart(s)' is not ticked off)."
readMe_command = lambda: GUI_IO_util.display_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()

