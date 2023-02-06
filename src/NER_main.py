# Roberto Franzosi September 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"Stanford_CoreNLP_NER_extractor",['os','pandas','tkinter'])==False:
    sys.exit(0)
# IBM https://ibm.github.io/zshot/ "pip install zshot"

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_files_util
import reminders_util
import config_util
import spaCy_util
import Stanford_CoreNLP_util
import Stanza_util

# RUN section ______________________________________________________________________________________________________________________________________________________

# def run(CoreNLPdir,inputFilename,inputDir,outputDir,openOutputFiles,createCharts,chartPackage,encoding_var,memory_var,extract_date_from_text_var,extract_date_from_filename_var,date_format,date_separator_var,date_position_var,NER_list,NER_split_prefix_values_entry_var,NER_split_suffix_values_entry_var,NER_sentence_var):
def run(inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage, config_filename,
        NER_package, NER_list):

    filesToOpen = []  # Store all files that are to be opened once finished

    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]

    # get the date options from filename
    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    extract_date_from_filename_var, date_format_var, date_separator_var, date_position_var = config_util.get_date_options(
        config_filename, config_input_output_numeric_options)
    extract_date_from_text_var = 0

    if package_display_area_value == '':
        mb.showwarning(title='No setup for NLP package and language',
                       message="The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again.")
        return

    if len(NER_list)==0 and 'CoreNLP' in NER_packages_var.get():
        mb.showwarning(title='No NER tag selected', message='No NER tag has been selected.\n\nPlease, select an NER tag and try again.')
        return

    if language_var == 'Arabic':
        mb.showwarning(title='Language',
                       message='The Stanford CoreNLP NER annotator is not available for Arabic.')
        return

    if 'BERT' in NER_package:
        import BERT_util
        tempOutputFiles = BERT_util.NER_tags_BERT(window,inputFilename, inputDir, outputDir, '', createCharts, chartPackage)
        if tempOutputFiles != '':
            filesToOpen.append(tempOutputFiles)

    if 'spaCy' in NER_package:
        document_length_var = 1
        limit_sentence_length_var = 1000
        tempOutputFiles = spaCy_util.spaCy_annotate(config_filename, inputFilename, inputDir,
                                                    outputDir,
                                                    openOutputFiles,
                                                    createCharts, chartPackage,
                                                    'NER', False,
                                                    language,
                                                    memory_var, document_length_var, limit_sentence_length_var,
                                                    extract_date_from_filename_var=extract_date_from_filename_var,
                                                    date_format=date_format_var,
                                                    date_separator_var=date_separator_var,
                                                    date_position_var=date_position_var)

        if tempOutputFiles == None:
            return
        else:
            filesToOpen.append(tempOutputFiles)

    if 'Stanza' in NER_package:
        document_length_var = 1
        limit_sentence_length_var = 1000
        tempOutputFiles = Stanza_util.Stanza_annotate(config_filename, inputFilename, inputDir,
                                                      outputDir,
                                                      openOutputFiles,
                                                      createCharts, chartPackage,
                                                      'NER', False,
                                                      language_list,
                                                      memory_var, document_length_var, limit_sentence_length_var,
                                                      extract_date_from_filename_var=extract_date_from_filename_var,
                                                      date_format=date_format_var,
                                                      date_separator_var=date_separator_var,
                                                      date_position_var=date_position_var)

        if tempOutputFiles == None:
            return
        else:
            filesToOpen.append(tempOutputFiles)

    if 'CoreNLP' in NER_package:
        tempOutputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir, outputDir,
                                                            openOutputFiles, createCharts, chartPackage,
                                                            'NER',
                                                            language=language_var,
                                                            NERs=NER_list,
                                                            DoCleanXML=False,
                                                            export_json_var= export_json_var,
                                                            memory_var=memory_var,
                                                            document_length=document_length_var,
                                                            sentence_length=limit_sentence_length_var,
                                                            extract_date_from_text_var=extract_date_from_text_var,
                                                            extract_date_from_filename_var=extract_date_from_filename_var,
                                                            date_format=date_format_var,
                                                            date_separator_var=date_separator_var,
                                                            date_position_var=date_position_var)

        if len(tempOutputFiles)>0:
            filesToOpen.append(tempOutputFiles)

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
                            GUI_util.charts_package_options_widget.get(),
                            config_filename,
                            NER_packages_var.get(),
                            NER_list)

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=360, # height at brief display
                             GUI_height_full=430, # height at full display
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

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

NER_list=[]

encoding_var=tk.StringVar()

NER_tag_var = tk.StringVar()
NER_entry_var = tk.StringVar()
# NER_split_values_prefix_entry_var = tk.StringVar()
# NER_split_values_suffix_entry_var = tk.StringVar()

GUI=''

def open_GUI1():
    call("python file_checker_converter_cleaner_main.py", shell=True)

pre_processing_button = tk.Button(window, text='Pre-processing tools (file checking & cleaning GUI)',command=open_GUI1)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               pre_processing_button)

NER_entry_lb = tk.Label(window, text='NER packages')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,NER_entry_lb,True)

NER_packages_var = tk.StringVar()
NER_packages_var.set('BERT (English language model)')
# IBM https://ibm.github.io/zshot/ "pip install zshot"
NER_packages_menu = tk.OptionMenu(window,NER_packages_var,'BERT (English language model)','IBM','spaCy','Stanford CoreNLP','Stanza')
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NER_NER_packages_menu_pos, y_multiplier_integer,
                    NER_packages_menu, False, False, True, False,
                    90, GUI_IO_util.labels_x_coordinate,
                    "Select the NER package you wish to use as NER annotator")

NER_tag_lb = tk.Label(window, text='NER tags')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,NER_tag_lb,True)

# NER tags menu
NER_tag_var.set('All NER tags') #--- All NER tags
NER_menu = tk.OptionMenu(window,NER_tag_var,'--- All NER tags', '--- All quantitative expressions','NUMBER', 'ORDINAL', 'PERCENT', '--- All social actors', 'PERSON', 'ORGANIZATION', '--- All spatial expressions', 'CITY', 'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION', '--- All temporal expressions', 'DATE', 'TIME', 'DURATION', 'SET',  '--- All other expressions', 'MISC', 'CAUSE_OF_DEATH', 'CRIMINAL_CHARGE', 'EMAIL',  'IDEOLOGY', 'MONEY',  'NATIONALITY', 'RELIGION', 'TITLE','URL')
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NER_NER_menu_pos, y_multiplier_integer,
                    NER_menu, True, False, True, False,
                    90, GUI_IO_util.labels_x_coordinate,
                    "Options currently available only for Stanford CoreNLP.\nSelect the NER tag(s) you wish to search for. Click on the + or Reset buttons when the widget is disabled to add new NER tags or to start fresh.")

add_NER_button = tk.Button(window, text='+', width=2,height=1,state='disabled',command=lambda: activate_NER_Options())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.setup_pop_up_text_widget,y_multiplier_integer,add_NER_button, True)

reset_NER_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: clear_NER_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NER_reset_NER_button_pos,y_multiplier_integer,reset_NER_button,True)

NER_entry_lb = tk.Label(window, text='NER list')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NER_NER_entry_lb_pos,y_multiplier_integer,NER_entry_lb,True)

NER_entry = tk.Entry(window,width=GUI_IO_util.widget_width_long,textvariable=NER_entry_var)
NER_entry.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NER_NER_entry_pos,y_multiplier_integer,NER_entry)

def clear(e):
    clear_NER_list()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

def add_NER_tag(*args):
    global NER_list

    # if '---' in str(NER_list):
    #     mb.showwarning(title='Warning', message='You cannot add any other NER tags once you have selected an NER set ---\n\nPlease, press ESCape or RESET or RUN.')
    #     window.focus_force()
    #     return

    if not 'CoreNLP' in NER_packages_var.get():
        return
    if 'All NER tags' in NER_tag_var.get(): # == '--- All NER tags':
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

def activate_NER_Options(*args):
    add_NER_button.configure(state="disabled")
    if 'CoreNLP' in NER_packages_var.get():
        NER_menu.configure(state='normal')
        reset_NER_button.configure(state='normal')
        NER_tag_var.set('All NER tags')  # --- All NER tags
    else:
        NER_menu.configure(state='disabled')
        reset_NER_button.configure(state='disabled')
        NER_tag_var.set('')
        NER_entry_var.set('')
    if 'IBM' in NER_packages_var.get():
        mb.showwarning("Option not available",
                       "The selected " + NER_packages_var.get() + " option is not available yet.\n\nSorry! Please, check back soon...")

activate_NER_Options()

NER_packages_var.trace('w',activate_NER_Options)

def clear_NER_list():
    NER_list.clear()
    NER_tag_var.set('')
    NER_entry_var.set('')
    # NER_split_values_prefix_entry_var.set('')
    # NER_split_values_suffix_entry_var.set('')
    activate_NER_Options()

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


# add all the lines to the end to every special GUI
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

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, click on the 'Pre-processing tools' button to open the GUI where you will be able to perform a variety of\n   file checking options (e.g., utf-8 encoding compliance of your corpus or sentence length);\n   file cleaning options (e.g., convert non-ASCII apostrophes & quotes and % to percent).\n\nNon utf-8 compliant texts are likely to lead to code breakdown in various algorithms.\n\nASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n\n% signs will lead to code breakdon of Stanford CoreNLP.\n\nSentences without an end-of-sentence marker (. ! ?) in Stanford CoreNLP will be processed together with the next sentence, potentially leading to very long sentences.\n\nSentences longer than 70 or 100 words may pose problems to Stanford CoreNLP (the average sentence length of modern English is 20 words). Please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the 23 NER tags that you would like to extract.\n\nFor English, the Stanford CoreNLP, by default through the NERClassifierCombiner annotator, recognizes the following NER values:\n  named (PERSON, LOCATION, ORGANIZATION, MISC);\n  numerical (MONEY, NUMBER, ORDINAL, PERCENT);\n  temporal (DATE, TIME, DURATION, SET).\n  In addition, via regexner, the following entity classes are tagged: EMAIL, URL, CITY, STATE_OR_PROVINCE, COUNTRY, NATIONALITY, RELIGION, (job) TITLE, IDEOLOGY, CRIMINAL_CHARGE, CAUSE_OF_DEATH.\n\nClick on the + button to add more NER tags.\nClick on the Reset button (or ESCape) to cancel all selected options and start over."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","If you have run a Stanford CoreNLP parser and you have a CoNLL table containing NER values, click on the 'Open table analyzer (GUI)' to have access to any desired CoNLL table."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="This Python 3 script will extract NER tags from either tetxt file(s) using the Stanford CoreNLP NER annotator.\n\nIn INPUT the algorith expects a single txt file or a set of txt files in a directory.\n\nIn OUTPUT the algorithm exports a csv file of extracted NER values and 2 Excel bar charts (if the checkbox 'Automatically compute Excel chart(s)' is not ticked off)."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

reminders_util.checkReminder(config_filename, reminders_util.title_options_only_CoreNLP_NER,
                             reminders_util.message_only_CoreNLP_NER, True)

GUI_util.window.mainloop()

