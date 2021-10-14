# Roberto Franzosi September 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Stanford_CoreNLP_NER_extractor",['os','pandas','tkinter'])==False:
    sys.exit(0)

import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import Stanford_CoreNLP_annotator_util
import IO_files_util
import IO_user_interface_util

# RUN section ______________________________________________________________________________________________________________________________________________________

# def run(CoreNLPdir,inputFilename,inputDir,outputDir,openOutputFiles,createExcelCharts,encoding_var,memory_var,extract_date_from_text_var,extract_date_from_filename_var,date_format,date_separator_var,date_position_var,NER_list,NER_split_prefix_values_entry_var,NER_split_suffix_values_entry_var,NER_sentence_var):
def run(inputFilename, inputDir, outputDir, openOutputFiles, createExcelCharts,
        encoding_var,
        memory_var, document_length_var, limit_sentence_length_var,
        extract_date_from_text_var, extract_date_from_filename_var, date_format, date_separator_var,
        date_position_var, NER_list, NER_sentence_var):

    filesToOpen = []  # Store all files that are to be opened once finished

    if len(NER_list)==0:
        mb.showwarning(title='No NER tag selected', message='No NER tag has been selected.\n\nPlease, select an NER tag and try again.')
        return

    tempOutputFiles = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir, outputDir,
                                                        openOutputFiles, createExcelCharts,
                                                        'NER',
                                                        NERs=NER_list,
                                                        DoCleanXML=False,
                                                        memory_var=memory_var,
                                                        document_length=document_length_var,
                                                        sentence_length=limit_sentence_length_var,
                                                        dateExtractedFromFileContent=extract_date_from_text_var,
                                                        filename_embeds_date_var=extract_date_from_filename_var,
                                                        date_format=date_format,
                                                        date_separator_var=date_separator_var,
                                                        date_position_var=date_position_var)

    if len(tempOutputFiles)>0:
        filesToOpen.extend(tempOutputFiles)

    # TODO Excel charts

    # # TODO date
    # if extract_date_from_text_var or extract_date_from_filename_var:
    # 	df = pd.DataFrame(data, columns=['Word', 'NER', 'Sentence ID', 'Sentence', 'Document ID', 'Document', 'Date'])
    # else:
    # 	df = pd.DataFrame(data, columns=['Word', 'NER', 'Sentence ID', 'Sentence', 'Document ID', 'Document'])
    # if NER_sentence_var == 1:
    # 	df = Excel_util.add_missing_IDs(df)

    # if inputDir!='':
    # 	output_filename = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'NER_extractor_dir')
    # else:
    # 	output_filename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NER_extractor')
    # df.to_csv(output_filename,index=False)
    # filesToOpen.append(output_filename)

    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running NER extraction at', True)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(
                            GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_Excel_chart_output_checkbox.get(),
                            encoding_var.get(),
                            memory_var.get(),
                            document_length_var.get(),
                            limit_sentence_length_var.get(),
                            extract_date_from_text_var.get(),
                            extract_date_from_filename_var.get(),
                            date_format.get(),
                            date_separator_var.get(),
                            date_position_var.get(),
                            NER_list,
                            NER_sentence_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_width=1200
GUI_height=550 # height of GUI with full I/O display

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

GUI_label='Graphical User Interface (GUI) for NER (Named Entity Recognition) Extraction'
config_filename='NER_config.txt'
# The 6 values of config_option refer to:
#   software directory
#   input file 1 for CoNLL file 2 for TXT file 3 for csv file 4 for any type of file
#   input dir
#   input secondary dir
#   output file
#   output dir
config_option=[0,4,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_options,config_filename,IO_setup_display_brief)

NER_list=[]

encoding_var=tk.StringVar()

memory_var = tk.IntVar()

extract_date_from_text_var= tk.IntVar()
extract_date_from_filename_var= tk.IntVar()

date_format = tk.StringVar()
date_separator_var = tk.StringVar()
date_position_var = tk.IntVar()

NER_tag_var = tk.StringVar()
NER_sentence_var = tk.StringVar()
NER_entry_var = tk.StringVar()
# NER_split_values_prefix_entry_var = tk.StringVar()
# NER_split_values_suffix_entry_var = tk.StringVar()

encoding_var.set('utf-8')
encodingValue = tk.OptionMenu(window,encoding_var,'utf-8','utf-16-le','utf-32-le','latin-1','ISO-8859-1')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,encodingValue,True)
encoding_lb = tk.Label(window, text='Select the encoding type (utf-8 default)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,encoding_lb)

def open_GUI():
    call("python file_checker_converter_cleaner_main.py", shell=True)

pre_processing_button = tk.Button(window, text='Pre-processing tools (file checking & cleaning GUI)',command=open_GUI)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               pre_processing_button)
# memory options

memory_var_lb = tk.Label(window, text='Memory ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               memory_var_lb, True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(4)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+100, y_multiplier_integer,
                                               memory_var,True)

document_length_var_lb = tk.Label(window, text='Document length')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               document_length_var_lb, True)

document_length_var = tk.Scale(window, from_=40000, to=90000, orient=tk.HORIZONTAL)
document_length_var.pack()
document_length_var.set(90000)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+150, y_multiplier_integer,
                                               document_length_var,True)

limit_sentence_length_var_lb = tk.Label(window, text='Limit sentence length')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate() + 370, y_multiplier_integer,
                                               limit_sentence_length_var_lb,True)

limit_sentence_length_var = tk.Scale(window, from_=70, to=400, orient=tk.HORIZONTAL)
limit_sentence_length_var.pack()
limit_sentence_length_var.set(100)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate() + 550, y_multiplier_integer,
                                               limit_sentence_length_var)

extract_date_lb = tk.Label(window, text='Extract date (for dynamic GIS)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,extract_date_lb,True)

extract_date_from_text_var.set(0)
extract_date_from_text_checkbox = tk.Checkbutton(window, variable=extract_date_from_text_var, onvalue=1, offvalue=0)
extract_date_from_text_checkbox.config(text="From document content")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),
                                               y_multiplier_integer, extract_date_from_text_checkbox, True)

extract_date_from_filename_var.set(0)
extract_date_from_filename_checkbox = tk.Checkbutton(window, variable=extract_date_from_filename_var, onvalue=1, offvalue=0)
extract_date_from_filename_checkbox.config(text="From filename")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 190,
                                               y_multiplier_integer, extract_date_from_filename_checkbox, True)

date_format_lb = tk.Label(window,text='Format ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 320,
                                               y_multiplier_integer, date_format_lb, True)
date_format.set('mm-dd-yyyy')
date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy','yyyy-mm-dd','yyyy-dd-mm','yyyy-mm','yyyy')
date_format_menu.configure(width=10,state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 380,
                                               y_multiplier_integer, date_format_menu, True)
date_separator_var.set('_')
date_separator_lb = tk.Label(window, text='Character separator ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 510,
                                               y_multiplier_integer, date_separator_lb, True)
date_separator = tk.Entry(window, textvariable=date_separator_var)
date_separator.configure(width=2,state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 640,
                                               y_multiplier_integer, date_separator, True)
date_position_var.set(2)
date_position_menu_lb = tk.Label(window, text='Position ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 670,
                                               y_multiplier_integer, date_position_menu_lb, True)
date_position_menu = tk.OptionMenu(window,date_position_var,1,2,3,4,5)
date_position_menu.configure(width=1,state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 740,
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

tk.Label(window, text='NER tag').place(x=GUI_IO_util.get_labels_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)
# NER tag
NER_tag_var.set('')
NER_menu_lb = tk.Label(window, text='NER tags')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,NER_menu_lb,True)

NER_menu = tk.OptionMenu(window,NER_tag_var,'--- All NER tags', '--- All quantitative expressions','NUMBER', 'ORDINAL', 'PERCENT', '--- All social actors', 'PERSON', 'ORGANIZATION', '--- All spatial expressions', 'CITY', 'STATE_OR_PROVINCE', 'COUNTRY', '--- All temporal expressions', 'DATE', 'TIME', 'DURATION', 'SET',  '--- All other expressions', 'MISC', 'CAUSE_OF_DEATH', 'CRIMINAL_CHARGE', 'EMAIL',  'IDEOLOGY', 'LOCATION', 'MONEY',  'NATIONALITY', 'RELIGION', 'TITLE','URL')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+70,y_multiplier_integer,NER_menu,True)

add_NER_button = tk.Button(window, text='+', width=2,height=1,state='disabled',command=lambda: activate_NER_Options())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+40,y_multiplier_integer,add_NER_button, True)

reset_NER_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: clear_NER_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+70,y_multiplier_integer,reset_NER_button,True)

NER_entry_lb = tk.Label(window, text='NER list')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 140,y_multiplier_integer,NER_entry_lb,True)

NER_entry = tk.Entry(window,width=70,textvariable=NER_entry_var)
NER_entry.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+ 200,y_multiplier_integer,NER_entry)

# openFile_button = tk.Button(window, width=3, text='',command=lambda: IO_files_util.openFile(window, os.path.join(GUI_IO_util.wordLists_libPath,'NER_prefix_suffix.csv')))
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,openFile_button,True)

# NER_split_values_prefix_entry_lb = tk.Label(window, text='NER split values (Prefix)')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 40,y_multiplier_integer,NER_split_values_prefix_entry_lb,True)
#
# NER_split_values_prefix_entry = tk.Entry(window,width=70,textvariable=NER_split_values_prefix_entry_var)
# NER_split_values_prefix_entry.configure(state="disabled")
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+ 200,y_multiplier_integer,NER_split_values_prefix_entry)
#
# NER_split_values_suffix_entry_lb = tk.Label(window, text='NER split values (Suffix)')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 40,y_multiplier_integer,NER_split_values_suffix_entry_lb,True)
#
# NER_split_values_suffix_entry = tk.Entry(window,width=70,textvariable=NER_split_values_suffix_entry_var)
# NER_split_values_suffix_entry.configure(state="disabled")
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+ 200,y_multiplier_integer,NER_split_values_suffix_entry)

def clear(e):
    clear_NER_list()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

def changed_input_filename(*args):
    # display the date widgets
    if inputFilename.get().endswith('.txt') or len(input_main_dir_path.get()) > 0:
        extract_date_from_text_checkbox.config(state='normal')
        extract_date_from_filename_checkbox.config(state='normal')
    else:
        extract_date_from_text_checkbox.config(state='disabled')
        extract_date_from_filename_checkbox.config(state='disabled')
inputFilename.trace('w', changed_input_filename)
input_main_dir_path.trace('w', changed_input_filename)

def add_NER_tag(*args):
    global NER_list

    # if '---' in str(NER_list):
    #     mb.showwarning(title='Warning', message='You cannot add any other NER tags once you have selected an NER set ---\n\nPlease, press ESCape or RESET or RUN.')
    #     window.focus_force()
    #     return

    if NER_tag_var.get() == '--- All NER tags':
        NER_list = ['PERSON', 'ORGANIZATION', 'MISC', 'MONEY', 'NUMBER', 'ORDINAL',
                    'PERCENT', 'DATE', 'TIME', 'DURATION', 'SET', 'EMAIL', 'URL', 'LOCATION', 'CITY',
                    'STATE_OR_PROVINCE', 'COUNTRY', 'NATIONALITY', 'RELIGION', 'TITLE', 'IDEOLOGY', 'CRIMINAL_CHARGE',
                    'CAUSE_OF_DEATH']
        NER_entry_var.set('PERSON, ORGANIZATION, MISC, MONEY, NUMBER, ORDINAL, PERCENT, DATE, TIME, DURATION, SET, EMAIL, URL, LOCATION, CITY,STATE_OR_PROVINCE, COUNTRY, NATIONALITY, RELIGION, TITLE, IDEOLOGY, CRIMINAL_CHARGE,CAUSE_OF_DEATH')
    elif NER_tag_var.get() == '--- All quantitative expressions':
        NER_list = ['NUMBER', 'ORDINAL', 'PERCENT']
        NER_entry_var.set('NUMBER, ORDINAL, PERCENT')
    elif NER_tag_var.get() == '--- All social actors':
        NER_list = ['PERSON', 'ORGANIZATION']
        NER_entry_var.set('PERSON, ORGANIZATION')
    elif NER_tag_var.get() == '--- All spatial expressions':
        NER_list = ['CITY', 'STATE_OR_PROVINCE', 'COUNTRY']
        NER_entry_var.set('CITY, STATE_OR_PROVINCE, COUNTRY')
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
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,NER_sentence_checkbox)

TIPS_lookup = {'Stanford CoreNLP memory issues': 'TIPS_NLP_Stanford CoreNLP memory issues.pdf','NER (Named Entity Recognition)':'TIPS_NLP_NER (Named Entity Recognition).pdf', 'CoNLL Table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",'POSTAG (Part of Speech Tags)':'TIPS_NLP_POSTAG (Part of Speech Tags) Stanford CoreNLP.pdf'}
TIPS_options='Stanford CoreNLP memory issues','NER (Named Entity Recognition)','CoNLL Table','POSTAG (Part of Speech Tags)'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    if not IO_setup_display_brief:
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",GUI_IO_util.msg_txtFile)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_corpusData)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help",GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+1),"Help","Please, using the dropdown menu, select the type of encoding you wish to use.\n\nLocations in different languages may require encodings (e.g., latin-1 for French or Italian) different from the standard (and default) utf-8 encoding.\n\nTick the 'Filename embeds date' checkbox if the filename embeds a date (e.g., The New York Times_12-05-1885). The date will then be used to construct dynamic GIS models."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+2), "Help",
                                  "Please, click on the 'Pre-processing tools' button to open the GUI where you will be able to perform a variety of\n   file checking options (e.g., utf-8 encoding compliance of your corpus or sentence length);\n   file cleaning options (e.g., convert non-ASCII apostrophes & quotes and % to percent).\n\nNon utf-8 compliant texts are likely to lead to code breakdown in various algorithms.\n\nASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n\n% signs will lead to code breakdon of Stanford CoreNLP.\n\nSentences without an end-of-sentence marker (. ! ?) in Stanford CoreNLP will be processed together with the next sentence, potentially leading to very long sentences.\n\nSentences longer than 70 or 100 words may pose problems to Stanford CoreNLP (the average sentence length of modern English is 20 words). Please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+3), "Help",
                                  "The Stanford CoreNLP performance is affected by various issues: memory size of your computer, document size, sentence length\n\nPlease, select the memory size Stanford CoreNLP will use. Default = 4. Lower this value if CoreNLP runs out of resources.\n   For CoreNLP co-reference resolution you may wish to increase the value when processing larger files (compatibly with the memory size of your machine).\n\nLonger documents affect performace. Stanford CoreNLP has a limit of 100,000 characters processed (the NLP Suite limits this to 90,000 as default). If you run into performance issues you may wish to further reduce the document size.\n\nSentence length also affect performance. The Stanford CoreNLP recommendation is to limit sentence length to 70 or 100 words.\n   You may wish to compute the sentence length of your document(s) so that perhaps you can edit the longer sentences.\n\nOn these issues, please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+4),"Help","The GIS algorithms allow you to extract a date to be used to build dynamic GIS maps. You can extract dates from the document content or from the filename if this embeds a date.\n\nPlease, the tick the checkbox 'From document content' if you wish to extract normalized NER dates from the text itself.\n\nPlease, tick the checkbox 'From filename' if filenames embed a date (e.g., The New York Times_12-05-1885).\n\nDATE WIDGETS ARE NOT VISIBLE WHEN SELECTING A CSV INPUT FILE."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+5),"Help","Please, using the dropdown menu, select the 23 NER tags that you would like to extract.\n\nFor English, the Stanford CoreNLP, by default through the NERClassifierCombiner annotator, recognizes the following NER values:\n  named (PERSON, LOCATION, ORGANIZATION, MISC);\n  numerical (MONEY, NUMBER, ORDINAL, PERCENT);\n  temporal (DATE, TIME, DURATION, SET).\n  In addition, via regexner, the following entity classes are tagged: EMAIL, URL, CITY, STATE_OR_PROVINCE, COUNTRY, NATIONALITY, RELIGION, (job) TITLE, IDEOLOGY, CRIMINAL_CHARGE, CAUSE_OF_DEATH.\n\nClick on the + button to add more NER tags.\nClick on the Reset button (or ESCape) to cancel all selected options and start over."+GUI_IO_util.msg_Esc)
    # GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*8,"Help","Please, edit the list of split names, entering only the FIRST part - prefix - of the name.\n\nYOU HAVE 2 OPTIONS:\n  1. You can click on the little button to the left of the label 'NER split values (Prefix)' to open a csv file where you can enter any prefix (and suffix) values of your choice (these are the values used to populate the \'NER split values\' widgets);\n  2. You can enter comma separated values directly in the \'NER split values\' (this, however, will only be a temporary solution).\n\nEntering prefix and suffix values is particularly useful for geographic locations (e.g., hong for Hong Kong), but could be used to group together peoples' names (e.g. Mary for Mary Ann, de for de Witt)."+GUI_IO_util.msg_Esc)
    # GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*9,"Help","Please, edit the list of split names, entering only the LAST part - suffix - of the name.\n\nYOU HAVE 2 OPTIONS:\n  1. You can click on the little button to the left of the label 'NER split values (Prefix)' to open a csv file where you can enter any suffix (or prefix) values of your choice (these are the values used to populate the \'NER split values\' widgets);\n  2. You can enter comma separated values directly in the \'NER split values\' (this, however, will only be a temporary solution).\n\nEntering prefix and suffix values is particularly useful for geographic locations (e.g., city for Atlantic City), but could be used to group together peoples' names (e.g. Ann for Mary Ann or Jo Ann)."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+6),"Help","Please, tick the checkbox if you wish to plot the extracted NER tags by sentence index."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+7),"Help",GUI_IO_util.msg_openOutputFiles)

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="This Python 3 script will extract NER tags from either a CoNLL table obtained from the Stanford CoreNLP parser or from a text file."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options,IO_setup_display_brief)

GUI_util.window.mainloop()

