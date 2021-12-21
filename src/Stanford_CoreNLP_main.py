# Written by Roberto Franzosi

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "Stanford_CoreNLP.py", ['tkinter', 'subprocess']) == False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_files_util
import IO_user_interface_util
import config_util
import reminders_util
import IO_internet_util
import Stanford_CoreNLP_annotator_util
import Stanford_CoreNLP_coreference_util
import IO_CoNLL_util
import file_checker_util
import file_cleaner_util
import sentence_analysis_util

# RUN section ______________________________________________________________________________________________________________________________________________________

# https://stackoverflow.com/questions/45886128/unable-to-set-up-my-own-stanford-corenlp-server-with-error-could-not-delete-shu
# for the Error [Thread-0] INFO CoreNLP - CoreNLP Server is shutting down
# sometimes the error appears but processing actually continues; but rebooting should do the trick if processing does not continue

# dateInclude indicates whether there is date embedded in the file name. 
# 1: included 0: not included
# def run(inputFilename, inputDir, outputDir, openOutputFiles, createExcelCharts, memory_var, date_extractor, split_files, quote_extractor, CoreNLP_gender_annotator, CoReference, manual_Coref, parser, parser_menu_var, dateInclude, sep, date_field_position, dateFormat, compute_sentence, CoNLL_table_analyzer_var):

def run(inputFilename, inputDir, outputDir, openOutputFiles, createExcelCharts,
        memory_var,
        document_length_var,
        limit_sentence_length_var,
        manual_Coref, open_GUI, parser, parser_menu_var, dateInclude, sep, date_field_position, dateFormat,
        CoNLL_table_analyzer_var, CoreNLP_annotators_var, CoreNLP_annotators_menu_var):

    filesToOpen = []
    outputCoNLLfilePath = ''

    if open_GUI:
        call("python Stanford_CoreNLP_coreference_main.py", shell=True)
        return

    # check internet connection
    if not IO_internet_util.check_internet_availability_warning("Stanford CoreNLP"):
        return

    if parser == 0 and CoNLL_table_analyzer_var == 0 and CoreNLP_annotators_var == 0:
        mb.showinfo("Warning", "No options have been selected.\n\nPlease, select an option and try again.")
        return

    if parser == 0 and CoNLL_table_analyzer_var == 1:
        mb.showinfo("Warning", "You have selected to open the CoNLL table analyser GUI. This option expects to run the parser first.\n\nPlease, tick the CoreNLP parser checkbox and try again.")
        return

    if CoreNLP_annotators_var == True and 'Coreference PRONOMINAL resolution' in CoreNLP_annotators_menu_var:
        if IO_libraries_util.inputProgramFileCheck("Stanford_CoreNLP_coReference_util.py") == False:
            return
        # if "Neural" in CoreNLP_annotators_menu_var:
        #     CoRef_Option = 'Neural Network'
        file_open, error_indicator = Stanford_CoreNLP_coreference_util.run(config_filename, inputFilename, inputDir,
                                                                           outputDir, openOutputFiles, createExcelCharts, memory_var,
                                                                           manual_Coref)

        if error_indicator == 0:
            IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Stanford CoreNLP Co-Reference Resolution',
                                               "Finished running Stanford CoreNLP Co-Reference Resolution using the 'Neural Network' approach at",
                                               True)
        else:
            mb.showinfo("Coreference Resolution Error",
                        "Since Stanford CoreNLP Co-Reference Resolution throws error, " +
                        "and you either didn't choose manual Co-Reference Resolution or manual Co-Referenece Resolution fails as well, the process ends now.")
        # filesToOpen = filesToOpen + file_open
        # print("Number of files to Open: ", len(file_open))
        filesToOpen.extend(file_open)


    if parser or (CoreNLP_annotators_var and CoreNLP_annotators_menu_var != ''):

        if IO_libraries_util.inputProgramFileCheck('Stanford_CoreNLP_annotator_util.py') == False:
            return

        if parser and parser_menu_var == 'Probabilistic Context Free Grammar (PCFG)':
            annotator='parser (pcfg)'
        elif parser_menu_var == 'Neural Network':
            annotator='parser (nn)'
        else:
            if CoreNLP_annotators_var and CoreNLP_annotators_menu_var != '':
                if 'NER (GUI)' in CoreNLP_annotators_menu_var: # NER annotator
                    if IO_libraries_util.inputProgramFileCheck('Stanford_CoreNLP_NER_main.py') == False:
                        return
                    call("python Stanford_CoreNLP_NER_main.py", shell=True)
                elif 'Sentence splitter (with sentence length)' in CoreNLP_annotators_menu_var:
                    annotator = 'Sentence'
                elif 'Lemma annotator' in CoreNLP_annotators_menu_var:
                    annotator = 'Lemma'
                elif 'POS annotator' in CoreNLP_annotators_menu_var:
                    annotator = 'All POS'
                elif 'Gender' in CoreNLP_annotators_menu_var:
                    annotator = 'gender'
                elif 'Quote' in CoreNLP_annotators_menu_var:
                    annotator = 'quote'
                elif 'Normalized' in CoreNLP_annotators_menu_var:
                    annotator = 'normalized-date'
                elif '*' in CoreNLP_annotators_menu_var:
                    annotator = ['gender','normalized-date','quote']
                elif 'Sentiment analysis' in CoreNLP_annotators_menu_var:
                    annotator = ['sentiment']
                elif 'SVO' in CoreNLP_annotators_menu_var:
                    annotator = ['SVO']
                elif 'OpenIE' in CoreNLP_annotators_menu_var:
                    annotator = ['OpenIE']
                else:
                    return

        tempOutputFiles = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                       outputDir,
                                                                       openOutputFiles, createExcelCharts,
                                                                       annotator, False, #'All POS',
                                                                       memory_var, document_length_var, limit_sentence_length_var,
                                                                       extract_date_from_filename_var=dateInclude,
                                                                       date_format=dateFormat,
                                                                       date_separator_var=sep,
                                                                       date_position_var=date_field_position)
        if len(tempOutputFiles)>0:
            filesToOpen.extend(tempOutputFiles)
            if 'parser' in annotator:
                reminders_util.checkReminder(config_filename,
                                             reminders_util.title_options_CoreNLP_NER_tags,
                                             reminders_util.message_CoreNLP_NER_tags,
                                             True)
                if CoNLL_table_analyzer_var:
                    if IO_libraries_util.inputProgramFileCheck('CoNLL_table_analyzer_main.py') == False:
                        return
                    # open the analyzer having saved the new parser output in config so that it opens the right input file
                    config_filename_temp = 'conll-table-analyzer_config.csv'
                    config_input_output_alphabetic_options = ['EMPTY LINE', str(tempOutputFiles[0]), 'EMPTY LINE', 'EMPTY LINE', 'EMPTY LINE', outputDir]
                    config_util.write_config_file(GUI_util.window, config_filename_temp, config_input_output_alphabetic_options, True)

                    reminders_util.checkReminder(config_filename,
                                                 reminders_util.title_options_CoNLL_analyzer,
                                                 reminders_util.message_CoNLL_analyzer,
                                                 True)

                    call("python CoNLL_table_analyzer_main.py", shell=True)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)


# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                 GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.create_Excel_chart_output_checkbox.get(),
                                 memory_var.get(),
                                 document_length_var.get(),
                                 limit_sentence_length_var.get(),
                                 manual_Coref_var.get(),
                                 open_GUI_var.get(),
                                 parser_var.get(),
                                 parser_menu_var.get(),
                                 fileName_embeds_date.get(),
                                 date_separator_var.get(),
                                 date_position_var.get(),
                                 date_format.get(),
                                 CoNLL_table_analyzer_var.get(),
                                 CoreNLP_annotators_var.get(),
                                 CoreNLP_annotators_menu_var.get())

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
                             increment=2)  # to be added for full display


GUI_label = 'Graphical User Interface (GUI) for Stanford CoreNLP'
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

window = GUI_util.window

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path

def clear(e):
    CoreNLP_annotators_var.set(0)
    CoreNLP_annotators_menu_var.set('')
    manual_Coref_checkbox.place_forget()  # invisible
    open_GUI_checkbox.place_forget()  # invisible
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

memory_var = tk.IntVar()
date_extractor_var = tk.IntVar()
CoreNLP_gender_annotator_var = tk.IntVar()
split_files_var = tk.IntVar()
quote_extractor_var = tk.IntVar()
manual_Coref_var = tk.IntVar()
open_GUI_var = tk.IntVar()
parser_var = tk.IntVar()
parser_menu_var = tk.StringVar()
fileName_embeds_date = tk.IntVar()

date_format = tk.StringVar()
date_separator_var = tk.StringVar()
date_position_var = tk.IntVar()

CoNLL_table_analyzer_var = tk.IntVar()

CoreNLP_annotators_var = tk.IntVar()
CoreNLP_annotators_menu_var = tk.StringVar()

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

date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy', 'yyyy-mm-dd', 'yyyy-dd-mm', 'yyyy-mm',
                                 'yyyy')

fileName_embeds_date_msg = tk.Label()
date_position_menu_lb = tk.Label()
date_position_menu = tk.OptionMenu(window, date_position_var, 1, 2, 3, 4, 5)
date_format_lb = tk.Label()
date_separator = tk.Entry(window, textvariable=date_separator_var)
date_separator_lb = tk.Label()

fileName_embeds_date_checkbox = tk.Checkbutton(window, text='Filename embeds date', variable=fileName_embeds_date,
                                               onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               fileName_embeds_date_checkbox, True)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               fileName_embeds_date_msg, True)

date_format.set('mm-dd-yyyy')
date_format_lb = tk.Label(window, text='Date format ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               date_format_lb, True)
date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy', 'yyyy-mm-dd', 'yyyy-dd-mm', 'yyyy-mm',
                                 'yyyy')
date_format_menu.configure()
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate() + 90, y_multiplier_integer,
                                               date_format_menu, True)

date_separator_lb = tk.Label(window, text='Date character separator ')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate(),y_multiplier_integer, date_separator_lb,True)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate() + 230, y_multiplier_integer,
                                               date_separator_lb, True)

date_separator_var.set('_')
date_separator = tk.Entry(window, textvariable=date_separator_var)
date_separator.configure(width=2)
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer, date_separator)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate() + 390, y_multiplier_integer,
                                               date_separator, True)

date_position_var.set(2)
date_position_menu_lb = tk.Label(window, text='Date position ')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate(),y_multiplier_integer, date_position_menu_lb,True)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate() + 440, y_multiplier_integer,
                                               date_position_menu_lb, True)
date_position_menu = tk.OptionMenu(window, date_position_var, 1, 2, 3, 4, 5)
date_position_menu.configure(width=2)
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer, date_position_menu)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate() + 530, y_multiplier_integer,
                                               date_position_menu)


def check_CoreNLP_dateFields(*args):
    if fileName_embeds_date.get() == 1:
        # fileName_embeds_date_msg.config(text="Date option ON")
        date_format_menu.config(state="normal")
        date_separator.config(state='normal')
        date_position_menu.config(state='normal')
    else:
        # fileName_embeds_date_msg.config(text="Date option OFF")
        date_format_menu.config(state="disabled")
        date_separator.config(state='disabled')
        date_position_menu.config(state="disabled")


fileName_embeds_date.trace('w', check_CoreNLP_dateFields)


parser_var.set(1)
parser_checkbox = tk.Checkbutton(window, text='CoreNLP parser', variable=parser_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               parser_checkbox, True)

parser_menu_var.set("Probabilistic Context Free Grammar (PCFG)")
parser_menu = tk.OptionMenu(window, parser_menu_var, 'Neural Network', 'Probabilistic Context Free Grammar (PCFG)')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               parser_menu)

def activate_SentenceTable(*args):
    if parser_var.get() == 0:
        parser_menu_var.set('')
        parser_menu.configure(state='disabled')
        # compute_sentence_var.set(0)
        CoNLL_table_analyzer_var.set(0)
    else:
        parser_menu_var.set('Probabilistic Context Free Grammar (PCFG)')
        parser_menu.configure(state='normal')
        # compute_sentence_var.set(1)
        CoNLL_table_analyzer_var.set(1)


# parser_var.trace('w', activate_SentenceTable)

# activate_SentenceTable()
#
# compute_sentence_var.set(0)
# sentence_table_checkbox = tk.Checkbutton(window, text='Compute sentence table', variable=compute_sentence_var,
#                                          onvalue=1, offvalue=0)
# y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
#                                                sentence_table_checkbox, True)
#
# sentence_table_checkbox_msg = tk.Label()
# sentence_table_checkbox_msg.config(text="Compute sentence table")
# y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
#                                                sentence_table_checkbox_msg)

# def check_sentence_table(*args):
#     if compute_sentence_var.get() == 1:
#         sentence_table_checkbox_msg.config(text="Compute sentence table")
#     else:
#         sentence_table_checkbox_msg.config(text="Do NOT compute sentence table")
# compute_sentence_var.trace('w', check_sentence_table)

CoNLL_table_analyzer_var.set(0)
CoNLL_table_analyzer_checkbox = tk.Checkbutton(window, text='CoNLL table analyzer', variable=CoNLL_table_analyzer_var,
                                               onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               CoNLL_table_analyzer_checkbox, True)
CoNLL_table_analyzer_checkbox_msg = tk.Label()
CoNLL_table_analyzer_checkbox_msg.config(text="Open the CoNLL table analyzer GUI")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               CoNLL_table_analyzer_checkbox_msg)

def check_CoNLL_table(*args):
    if CoNLL_table_analyzer_var.get() == 1:
        CoNLL_table_analyzer_checkbox_msg.config(text="Open CoNLL table analyzer GUI")
    else:
        CoNLL_table_analyzer_checkbox_msg.config(text="Do NOT open CoNLL table analyzer GUI")


CoNLL_table_analyzer_var.trace('w', check_CoNLL_table)

CoreNLP_annotators_checkbox = tk.Checkbutton(window, text='CoreNLP annotators', variable=CoreNLP_annotators_var,
                                             onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               CoreNLP_annotators_checkbox, True)

CoreNLP_annotators_menu_var.set("")
CoreNLP_annotators_menu = tk.OptionMenu(window, CoreNLP_annotators_menu_var,
        'Sentence splitter (with sentence length)',
        'Lemma annotator',
        'POS annotator',
        'NER (GUI)',
        'Coreference PRONOMINAL resolution (Neural Network)',
        'Sentiment analysis (Neural Network)',
        'OpenIE - Relation triples extractor (Neural Network)',
        'SVO extraction (Enhanced++ Dependencies; Neural Network)',
        '*',
        'Gender annotator (Neural Network)',
        'Normalized NER date',
        'Quote/dialogue annotator (Neural Network)')

y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               CoreNLP_annotators_menu)

manual_Coref_checkbox = tk.Checkbutton(window, text='Manual edit',
                                       variable=manual_Coref_var,
                                       onvalue=1, offvalue=0)

open_GUI_checkbox = tk.Checkbutton(window, text='Open coreference GUI',
                                       variable=open_GUI_var,
                                       onvalue=1, offvalue=0)

def activate_CoreNLP_annotators_menu(*args):
    global y_multiplier_integer
    if CoreNLP_annotators_var.get() == True:
        if parser_var.get():
            if 'POS' in CoreNLP_annotators_menu_var.get():
                mb.showinfo("Warning", "You have selected to run the CoreNLP parser AND the lemma/POS annotator. The parser already computes lemmas and POS tags.\n\nPlease, tick either the parser or the annotator checkbox.")
                CoreNLP_annotators_var.set(0)
                CoreNLP_annotators_menu_var.set('')
                return
        CoreNLP_annotators_menu.configure(state='normal')
        if 'Coreference' in CoreNLP_annotators_menu_var.get():
            y_multiplier_integer=y_multiplier_integer-1
            manual_Coref_var.set(0)
            y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate() + 400,
                                                           y_multiplier_integer,
                                                           manual_Coref_checkbox,True)

            open_GUI_var.set(0)
            y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate() + 550,
                                                           y_multiplier_integer,
                                                           open_GUI_checkbox)
            open_GUI_checkbox.configure(state='normal')
            if input_main_dir_path.get()!='':
                manual_Coref_checkbox.configure(state='disabled')
            else:
                manual_Coref_checkbox.configure(state='normal')
        else:
            manual_Coref_checkbox.place_forget()  # invisible
            open_GUI_checkbox.place_forget()  # invisible
    else:
        manual_Coref_checkbox.place_forget()  # invisible
        open_GUI_checkbox.place_forget()  # invisible
        CoreNLP_annotators_menu_var.set('')
        CoreNLP_annotators_menu.configure(state='disabled')

CoreNLP_annotators_var.trace('w', activate_CoreNLP_annotators_menu)
CoreNLP_annotators_menu_var.trace('w', activate_CoreNLP_annotators_menu)

activate_CoreNLP_annotators_menu()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Stanford CoreNLP download': 'TIPS_NLP_Stanford CoreNLP download install run.pdf',
               'Stanford CoreNLP parser': 'TIPS_NLP_Stanford CoreNLP parser.pdf',
               'Stanford CoreNLP memory issues': 'TIPS_NLP_Stanford CoreNLP memory issues.pdf',
               'NER (Named Entity Recognition)': 'TIPS_NLP_NER (Named Entity Recognition).pdf',
               'Stanford CoreNLP date extractor (NER normalized date)': 'TIPS_NLP_Stanford CoreNLP date extractor.pdf',
               'Stanford CoreNLP OpenIE': 'TIPS_NLP_Stanford CoreNLP OpenIE.pdf',
               'Stanford CoreNLP coreference resolution': 'TIPS_NLP_Stanford CoreNLP coreference resolution.pdf',
               'Java download install run': 'TIPS_NLP_Java download install run.pdf',
               'CoNLL Table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",
               'POSTAG (Part of Speech Tags)': "TIPS_NLP_POSTAG (Part of Speech Tags) Stanford CoreNLP.pdf",
               'Noun Analysis': "TIPS_NLP_Noun Analysis.pdf", 'Verb Analysis': "TIPS_NLP_Verb Analysis.pdf",
               'Function Words Analysis': 'TIPS_NLP_Function Words Analysis.pdf',
               'Clause Analysis': 'TIPS_NLP_Clause analysis.pdf'}
TIPS_options = 'Stanford CoreNLP download', 'Stanford CoreNLP parser', 'Stanford CoreNLP memory issues', 'Stanford CoreNLP date extractor (NER normalized date)', 'Stanford CoreNLP coreference resolution', 'Stanford CoreNLP OpenIE', 'Java download install run', 'CoNLL Table', 'POSTAG (Part of Speech Tags)', 'DEPREL (Stanford Dependency Relations)', 'NER (Named Entity Recognition)', 'Clause Analysis', 'Noun Analysis', 'Verb Analysis', 'Function Words Analysis'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.

def help_buttons(window, help_button_x_coordinate, basic_y_coordinate, y_step):
    if not IO_setup_display_brief:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_txtFile)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step, "Help",
                                      GUI_IO_util.msg_corpusData)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 2, "Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                  GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+1), "Help",
                                  "Please, click on the 'Pre-processing tools' button to open the GUI where you will be able to perform a variety of\n   file checking options (e.g., utf-8 encoding compliance of your corpus or sentence length);\n   file cleaning options (e.g., convert non-ASCII apostrophes & quotes and % to percent).\n\nNon utf-8 compliant texts are likely to lead to code breakdown in various algorithms.\n\nASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n\n% signs will lead to code breakdon of Stanford CoreNLP.\n\nSentences without an end-of-sentence marker (. ! ?) in Stanford CoreNLP will be processed together with the next sentence, potentially leading to very long sentences.\n\nSentences longer than 70 or 100 words may pose problems to Stanford CoreNLP (the average sentence length of modern English is 20 words). Please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+2), "Help",
                                  "The Stanford CoreNLP performance is affected by various issues: memory size of your computer, document size, sentence length\n\nPlease, select the memory size Stanford CoreNLP will use. Default = 4. Lower this value if CoreNLP runs out of resources.\n   For CoreNLP co-reference resolution you may wish to increase the value when processing larger files (compatibly with the memory size of your machine).\n\nLonger documents affect performace. Stanford CoreNLP has a limit of 100,000 characters processed (the NLP Suite limits this to 90,000 as default). If you run into performance issues you may wish to further reduce the document size.\n\nSentence length also affect performance. The Stanford CoreNLP recommendation is to limit sentence length to 70 or 100 words.\n   You may wish to compute the sentence length of your document(s) so that perhaps you can edit the longer sentences.\n\nOn these issues, please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+3), "Help",
                                  "Please, tick the checkbox if your filenames embed a date (e.g., The New York Times_12-23-1992).\n\nWhen the date option is ticked, the script will add a date field to the CoNLL table. The date field will be used by other NLP scripts (e.g., Ngrams).\n\nOnce you have ticked the 'Filename embeds date' option, you will need to provide the follwing information:\n   1. the date format of the date embedded in the filename (default mm-dd-yyyy); please, select.\n   2. the character used to separate the date field embedded in the filenames from the other fields (e.g., _ in the filename The New York Times_12-23-1992) (default _); please, enter.\n   3. the position of the date field in the filename (e.g., 2 in the filename The New York Times_12-23-1992; 4 in the filename The New York Times_1_3_12-23-1992 where perhaps fields 2 and 3 refer respectively to the page and column numbers); please, select.\n\nIF THE FILENAME EMBEDS A DATE AND THE DATE IS THE ONLY FIELD AVAILABLE IN THE FILENAME (e.g., 2000.txt), enter . in the 'Date character separator' field and enter 1 in the 'Date position' field.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+4), "Help",
                                  "Please, tick the checkbox if you wish to use the CoreNLP parser to obtain a CoNLL table.\n\nThe CoNLL table is the basis of many of the NLP analyses: noun & verb analysis, function words, clause analysis, query CoNLL.\n\nYou have a choice between two types of papers:\n   1. the recommended default Probabilistic Context Free Grammar (PCFG) parser;\n   2. a Neural-network dependency parser.\n\nThe neural network approach is more accurate but much slower.\n\nIn output the scripts produce a CoNLL table with the following 8 fields: ID, FORM, LEMMA, POSTAG, NER (23 classes), HEAD, DEPREL, CLAUSAL TAGS (the neural-network parser does not produce clausal tags).\n\nThe following fields will be automatically added to the standard 8 fields of a CoNLL table: RECORD NUMBER, DOCUMENT ID, SENTENCE ID, DOCUMENT (INPUT filename), DATE (if the filename embeds a date).\n\nIf you suspect that CoreNLP may have given faulty results for some sentences, you can test those sentences directly on the Stanford CoreNLP website at https://corenlp.run")
    # GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+6), "Help",
    #                               "Please, tick the checkbox if you wish to compute a sentence table with various sentence statistics.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+5), "Help",
                                  "Please, tick/untick the checkbox if you want to open (or not) the CoNLL table analyzer GUI to analyze the CoreNLP parser results contained in the CoNLL table.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+6), "Help",
                                  "Please, using the dropdown menu, select one of the many other annotators available through Stanford CoreNLP: Coreference pronominal resolution, DepRel, POS, NER (Named Entity Recognition), NER normalized date. gender, quote, and sentiment analysis.\n\nANNOTATORS MARKED AS NEURAL NETWORK ARE MORE ACCURATE, BUT SLOW AND REQUIRE A GREAT DEAL OF MEMORY.\n\n1.  PRONOMINAL co-reference resolution refers to such cases as 'John said that he would...'; 'he' would be substituted by 'John'. CoreNLP can resolve other cases but the algorithm here is restricted to pronominal resolution.\n\nThe co-reference resolution checkbox is disabled when selected an entire directory in input. The co-reference resolution algorithm is a memory hog. You may not have enough memory on your machine.\n\nTick the checkbox Manually edit coreferenced document if you wish to resolve manually cases of unresolved or wrongly resolved coreferences. MANUAL EDITING REQUIRES A LOT OF MEMORY SINCE BOTH ORIGINAL AND CO-REFERENCED FILE ARE BROUGHT IN MEMORY. DEPENDING UPON FILE SIZES, YOU MAY NOT HAVE ENOUGH MEMORY FOR THIS STEP.\n\nTick the Open GUI checkbox to open the specialized GUI for pronominal coreference resolution.\n\n2.  The CoreNLP NER annotator recognizes the following NER values:\n  named (PERSON, LOCATION, ORGANIZATION, MISC);\n  numerical (MONEY, NUMBER, ORDINAL, PERCENT);\n  temporal (DATE, TIME, DURATION, SET).\n  In addition, via regexner, the following entity classes are tagged: EMAIL, URL, CITY, STATE_OR_PROVINCE, COUNTRY, NATIONALITY, RELIGION, (job) TITLE, IDEOLOGY, CRIMINAL_CHARGE, CAUSE_OF_DEATH.\n\n3.  The NER NORMALIZED DATE annotator extracts standard dates from text in the yyyy-mm-dd format (e.g., 'the day before Christmas' extracted as 'xxxx-12-24').\n\n4.  The CoreNLP coref GENDER annotator extracts the gender of both first names and personal pronouns (he, him, his, she, her, hers) using a neural network approach. This annotator requires a great deal of memory. So, please, adjust the memory allowing as much memory as you can afford.\n\n5.  The CoreNLP QUOTE annotator extracts quotes from text and attributes the quote to the speaker.\n\n6.  The SENTIMENT ANALYSIS annotator computes the sentiment values (negative, neutral, positive) of each sentence in a text.\n\n6.  The OpenIE (Open Information Extraction) annotator extracts  open-domain relation triples, representing a subject, a relation, and the object of the relation.\n\n\n\nIn INPUT the algorithms expect a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithms will produce a number of csv files annd Excel charts. The Gender annotator will also produce an html file with male tags displayed in blue and female tags displayed in red. The Coreference annotator will produce txt-format copies of the same input txt files but co-referenced.\n\Select * to run Gender annotator (Neural Network), Normalized NER date, and Quote/dialogue annotator (Neural Network).")
    # GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+2), "Help",
    #                               "Please, using the dropdown menu, select the type of Stanford coreference you wish to use for coreference Resolution (Neural Network is slowest but most accurate; recommended!\n\nThe co-reference resolution algorithm is a memory hog. You may not have enough memory on your machine.\n\nWhile CoreNLP can resolve different coreference types (e.g., nominal, pronominal), the SVO script filters only pronominal types. Pronominal coreference refers to such cases as 'John said that he would...'; 'he' would be substituted by 'John'.\n\nPlease, select the memory size Stanford CoreNLP will use to resolve coreference. Default = 6. Lower this value if CoreNLP runs out of resources. Increase the value for larger files.\n\nIn INPUT the algorithm expects a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithm will produce txt-format copies of the same input txt files but co-referenced.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+7), "Help",
                                  GUI_IO_util.msg_openOutputFiles)

help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), GUI_IO_util.get_basic_y_coordinate(),
             GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message = "This Python 3 script will perform different types of textual operations using the Stanford CoreNLP. The main operation is text parsing.\n\nYOU MUST BE CONNETED TO THE INTERNET TO RUN THE SCRIPTS."
readMe_command = lambda: GUI_IO_util.readme_button(window, GUI_IO_util.get_help_button_x_coordinate(),
                                                   GUI_IO_util.get_basic_y_coordinate(), "Help", readMe_message)

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
