#Written by Roberto Franzosi
#Modified by Cynthia Dong (Fall 2019-Spring 2020)
#Wordnet_bySentenceID and get_case_initial_row written by Yi Wang (April 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"knowledge_graphs_WordNet_main",['os','tkinter','pandas'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
import pandas as pd

import GUI_IO_util
import config_util
import IO_files_util
import CoNLL_util
import knowledge_graphs_WordNet_util
import sentence_analysis_util
import Stanford_CoreNLP_util
import reminders_util
import html_annotator_dictionary_util

# RUN section ______________________________________________________________________________________________________________________________________________________

pd.set_option('display.max_columns', 500)
# DocumentID    DocumentName    SenetenceID     (FullSentence)
# written by Yi Wang April 2020

def run(inputFilename, inputDir, outputDir,openOutputFiles,
        createCharts,
        chartPackage,
        csv_file,
        aggregate_POS_var,
        noun_verb,
        disaggregate_var,
        wordNet_keyword_list,
        annotate_file_var,
        extract_proper_nouns,
        extract_improper_nouns,
        aggregate_lemmatized_var,
        extract_nouns_verbs_from_CoNLL_var,
        aggregate_bySentenceID_var,
        dict_WordNet_filename_var):

    filesToOpen = []  # Store all files that are to be opened once finished

    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()

    language_var='English' # WordNet works only for English language

    # check that the GEP has been setup
    WordNetDir, existing_software_config = IO_libraries_util.external_software_install('knowledge_graphs_WordNet_util',
                                                                                         'WordNet',
                                                                                         '',
                                                                                         silent=False)

    if WordNetDir == None:
        return

    # print("noun_verb",noun_verb)

    if aggregate_POS_var==False and disaggregate_var==False and annotate_file_var== False and aggregate_lemmatized_var==False and aggregate_bySentenceID_var==False and extract_nouns_verbs_from_CoNLL_var==False and extract_proper_nouns==False and extract_improper_nouns==False:
        mb.showerror(title='Missing required information', message="No options have been selected.\n\nPlease, tick one of the available options and try again.")
        return False

    if disaggregate_var==True and len(wordNet_keyword_list)==0:
        mb.showerror(title='Missing required information', message="You have selected to run the option 'Zoom IN/DOWN to find related words', but you have not entered any keywords required to run the script.\n\nPlease, enter the keywords and try again.")
        return False

    if disaggregate_var==True:
        filesToOpen= knowledge_graphs_WordNet_util.disaggregate_GoingDOWN(WordNetDir,outputDir, wordNet_keyword_list, noun_verb)
        if len(filesToOpen)>0:
            csv_file_var.set(str(filesToOpen[0]))

    if annotate_file_var:
        if IO_libraries_util.check_inputPythonJavaProgramFile('html_annotator_dictionary_util.py') == False:
            return
        csvValue_color_list = []
        bold_var=True
        color_palette_dict_var = 'red'  # default color, if forgotten

        tagAnnotations = ['<span style=\"color: ' + color_palette_dict_var + '; font-weight: bold\">', '</span>']

        filesToOpen = html_annotator_dictionary_util.dictionary_annotate(inputFilename, inputDir, outputDir,
                                                                    csv_file, 'Term', csvValue_color_list,
                                                                    bold_var, tagAnnotations, '.txt','WordNet_'+noun_verb)

    if extract_proper_nouns==1 or extract_improper_nouns==1:
        if noun_verb!='NOUN':
            mb.showerror(title='Option not available', message="You have selected to run the option 'Extract PROPER/IMPROPER nouns' with VERB.\n\nPlease, select NOUN and try again.")
            return
        if len(csv_file)==0:
            mb.showerror(title='Missing input file', message="You have selected to run the option 'Extract PROPER/IMPROPER nouns'. The function expects in input a WordNet dictionary file previously exported with the 'Zoom IN/DOWN' function for nouns.\n\nPlease, select an input WordNet dictionary file and try again.")
            return
        check_column=0
        if extract_proper_nouns:
            filesToOpen=knowledge_graphs_WordNet_util.get_case_initial_row(csv_file, outputDir,'Term', True)
        if extract_improper_nouns:
            filesToOpen=knowledge_graphs_WordNet_util.get_case_initial_row(csv_file, outputDir,'Term', False)

    if aggregate_lemmatized_var==True:

        if len(csv_file)==0:
            mb.showerror(title='Missing required information', message="You have selected to run the option 'Zoom OUT/UP to find higher-level aggregates', but you have not selected the Input csv file for " + noun_verb + " required to run the script.\n\nPlease, select the Input file and try again.")
            return False
        if noun_verb=='NOUN' and 'nouns_lemma' not in csv_file:
            if hidden_noun_lemma_csv.get() != '':
                csv_file_var.set(hidden_noun_lemma_csv.get())
            else:
                result=mb.askokcancel(title='Missing required information',
                             message="You have selected to run the option 'Zoom OUT/UP to find higher-level aggregates' with the 'NOUN' option but the csv file currently selected does not contain the expected subscript 'nouns_lemma'.\n\nIf this an overshigth, click on the Select INPUT CSV file button to select a different csv file and try again.")
                if result == False:
                    return
        if noun_verb=='VERB' and 'verbs_lemma' not in csv_file:
            if hidden_verb_lemma_csv.get()!='':
                csv_file_var.set(hidden_verb_lemma_csv.get())
            else:
                result=mb.askokcancel(title='Missing required information', message="You have selected to run the option 'Zoom OUT/UP to find higher-level aggregates' with the 'VERB' option but the csv file currently selected does not contain the expected subscript 'verbs_lemma'.\n\nIf this an overshigth, click on the Select INPUT CSV file button to select a different csv file and try again.")
                if result==False:
                    return
        filesToOpen = knowledge_graphs_WordNet_util.aggregate_GoingUP(WordNetDir, csv_file, outputDir, config_filename, noun_verb, openOutputFiles,
                                                     createCharts, chartPackage, language_var)

    if extract_nouns_verbs_from_CoNLL_var==True:
        # check that input file is a CoNLL table
        if not CoNLL_util.check_CoNLL(csv_file):
            return
        noun_form_csv,noun_lemma_csv,verb_form_csv,verb_lemma_csv = CoNLL_util.get_nouns_verbs_CoNLL(csv_file, outputDir)
        filesToOpen.append(noun_form_csv)
        filesToOpen.append(noun_lemma_csv)
        filesToOpen.append(verb_form_csv)
        filesToOpen.append(verb_lemma_csv)

        if noun_verb_menu_var.get() == 'NOUN':
            csv_file_var.set(noun_lemma_csv)
        if noun_verb_menu_var.get() == 'VERB':
            csv_file_var.set(verb_lemma_csv)
        hidden_verb_lemma_csv.set(verb_lemma_csv)
        hidden_noun_lemma_csv.set(noun_lemma_csv)

    if aggregate_POS_var == True:
        annotator = ['POS']
        nouns_var = True
        verbs_var = True
        # uses a txt fie in input
        language_var='English'
        files = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                 outputDir, openOutputFiles, createCharts, chartPackage,
                                                                 annotator, False, language_var, export_json_var, memory_var)
        if len(files) > 0:
            noun_verb = ''
            if verbs_var == True:
                temp_csv_file = files[0]  # Verbs but... double check
                if "verbs" in temp_csv_file.lower():
                    noun_verb = 'VERB'
                else:
                    return
                output = knowledge_graphs_WordNet_util.aggregate_GoingUP(WordNetDir, temp_csv_file, outputDir, config_filename, noun_verb,
                                                        openOutputFiles, createCharts, chartPackage, language_var)
                if output != None:
                    filesToOpen.append(output)

            if nouns_var == True:
                temp_csv_file = files[1]  # Nouns but... double check
                if "nouns" in temp_csv_file.lower():
                    noun_verb = 'NOUN'
                else:
                    return
                output = knowledge_graphs_WordNet_util.aggregate_GoingUP(WordNetDir, temp_csv_file, outputDir, config_filename, noun_verb,
                                                        openOutputFiles, createCharts, chartPackage, language_var)
                if output != None:
                    filesToOpen.append(output)

    if aggregate_bySentenceID_var==1:
        # check that input file is a CoNLL table
        if not CoNLL_util.check_CoNLL(csv_file):
            return
        outputFilename=IO_files_util.generate_output_file_name(csv_file, outputDir, '.csv', 'WordNet', 'conll')
        filesToOpen.append(outputFilename)
        temp_outputfiles = knowledge_graphs_WordNet_util.Wordnet_bySentenceID(csv_file,dict_WordNet_filename_var,outputFilename,outputDir,noun_verb,openOutputFiles,createCharts, chartPackage)
        if temp_outputfiles!=None:
            filesToOpen.append(temp_outputfiles)

    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

#the values of the GUI widgets MUST be entered in the command as widget.get() otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_chart_output_checkbox.get(),
                            GUI_util.charts_package_options_widget.get(),
                            csv_file_var.get(),
                            aggregate_POS_var.get(),
                            noun_verb_menu_var.get(),
                            disaggregate_var.get(),
                            wordNet_keyword_list,
                            annotate_file_var.get(),
                            extract_proper_nouns_var.get(),
                            extract_improper_nouns_var.get(),
                            aggregate_lemmatized_var.get(),
                            extract_nouns_verbs_from_CoNLL_var.get(),
                            aggregate_bySentenceID_var.get(),
                            dict_WordNet_filename_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=640, # height at brief display
                             GUI_height_full=720, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for WordNet tools'
head, scriptName = os.path.split(os.path.basename(__file__))
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
config_input_output_numeric_options=[2,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window = GUI_util.window
# config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
# config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path
outputDir = GUI_util.output_dir_path

openOutputFiles = GUI_util.open_csv_output_checkbox.get()
createCharts = GUI_util.create_chart_output_checkbox.get()

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

wordNet_keyword_list = []
hidden_noun_lemma_csv = tk.StringVar()
hidden_verb_lemma_csv = tk.StringVar()


aggregate_POS_var = tk.IntVar()
noun_verb_menu_var = tk.StringVar()
noun_verb_menu_var.set('NOUN')
disaggregate_var = tk.IntVar()
keyWord_var = tk.StringVar()
keyWord_entry_var = tk.StringVar()
aggregate_lemmatized_var = tk.IntVar()
extract_nouns_verbs_from_CoNLL_var = tk.IntVar()
annotate_file_var = tk.IntVar()
aggregate_bySentenceID_var = tk.IntVar()
dict_WordNet_filename_var = tk.StringVar()
extract_proper_nouns_var = tk.IntVar()
extract_improper_nouns_var = tk.IntVar()
csv_file_var= tk.StringVar()

def get_csv_file(window,title,fileType,annotate):
    #csv_file_var.set('')
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)
    if len(filePath)>0:
        csv_file_var.set(filePath)
    return filePath

csv_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT CSV file',command=lambda: get_csv_file(window,'Select INPUT csv file', [("dictionary files", "*.csv")],True))
# csv_file_button.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,csv_file_button,True)

#setup a button to open Windows Explorer on the selected input directory
openInputFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, csv_file_var.get()))
# the button widget has hover-over effects (no_hover_over_widget=False) and the info displayed is in text_info
# the two x-coordinate and x-coordinate_hover_over must have the same values
y_multiplier_integer = GUI_IO_util.placeWidget(window,
    GUI_IO_util.IO_configuration_menu,
    y_multiplier_integer,
    openInputFile_button, True, False, True, False, 90, GUI_IO_util.IO_configuration_menu, "Open INPUT csv file")

csv_file=tk.Entry(window, width=GUI_IO_util.WordNet_csv_file_width,textvariable=csv_file_var)
csv_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,csv_file)

WordNet_category_lb = tk.Label(window, text='WordNet category (synset)')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               WordNet_category_lb,True)

noun_verb_menu = tk.OptionMenu(window, noun_verb_menu_var, 'NOUN', 'VERB')
noun_verb_menu.configure(width=9, state="normal")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                                               noun_verb_menu)

disaggregate_var.set(0)
disaggregate_checkbox = tk.Checkbutton(window, text='Zoom IN/DOWN to find related words', variable=disaggregate_var,
                                    onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               disaggregate_checkbox, True)

def activate_keyword_menu():
    if keyWord_var.get() != '':
        keyWord_menu.configure(state="normal")

add_keyword_button = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1, state='disabled',
                               command=lambda: activate_keyword_menu())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                                               add_keyword_button, True)

reset_keywords_button = tk.Button(window, text='Reset', width=GUI_IO_util.reset_button_width, height=1, state='disabled',
                                  command=lambda: clear_keyword_list())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.WordNet_reset_pos, y_multiplier_integer,
                                               reset_keywords_button, True)

def showKeywordList():
    mb.showwarning(title='Warning', message='The currently selected keywords are:\n\n' + ','.join(
        wordNet_keyword_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')


show_keywords_button = tk.Button(window, text='Show', width=GUI_IO_util.show_button_width, height=1, state='disabled',
                                 command=lambda: showKeywordList())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.WordNet_show_pos, y_multiplier_integer,
                                               show_keywords_button, True)

noun_verb_menu_options = []
keyWord_var.set('')
keyWord_menu_lb = tk.Label(window, text='Keyword (synset)')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.WordNet_noun_verb_menu_pos, y_multiplier_integer,
                                               keyWord_menu_lb, True)

keyWord_menu = tk.OptionMenu(window, keyWord_var, noun_verb_menu_options)
# keyWord_menu.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.WordNet_keyWord_menu_pos, y_multiplier_integer,
                                               keyWord_menu)

keyWord_entry_lb = tk.Label(window, text='YOUR keyword(s) ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.WordNet_noun_verb_menu_pos, y_multiplier_integer,
                                               keyWord_entry_lb, True)

keyWord_entry = tk.Entry(window, width=GUI_IO_util.WordNet_keyWord_entry_width, textvariable=keyWord_entry_var)
keyWord_entry.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.WordNet_keyWord_menu_pos, y_multiplier_integer,
                                               keyWord_entry, True)

OK_button = tk.Button(window, text='OK', width=GUI_IO_util.OK_button_width, height=1, state='disabled', command=lambda: accept_WordNet_list())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.WordNet_OK_button_pos, y_multiplier_integer,
                                               OK_button)
def clear(e):
    if aggregate_lemmatized_var.get():
        aggregate_lemmatized_var.set(0)
    keyWord_var.set('')
    keyWord_entry_var.set('')
    dict_WordNet_filename_var.set('')
    csv_file_var.set('')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)


# activated when pressing the RESET button
def clear_keyword_list():
    wordNet_keyword_list.clear()
    keyWord_var.set('')
    keyWord_entry_var.set('')
    activate_allOptions(noun_verb_menu_var.get())

def accept_WordNet_list():
    global wordNet_keyword_list
    if keyWord_entry_var.get() != '':
        # TODO CYNTHIA
        # what if user enter , followed by a space? most likely event...
        wordNet_keyword_list = [str(x) for x in keyWord_entry_var.get().split(',') if x]
        show_keywords_button.configure(state="normal")
    else:
        mb.showwarning(title='Warning',
                       message='You have pressed the OK button, but you must first enter your keyword(s).\n\nPlease, enter the keyword(s) and try again.')


def add_wordNet_keyword(*args):
    if keyWord_var.get() in wordNet_keyword_list:
        mb.showwarning(title='Warning',
                       message='The keyword "' + keyWord_var.get() + '" is already in your selection list: ' + str(
                           wordNet_keyword_list) + '.\n\nPlease, select another keyword.')
        window.focus_force()
        return
    if keyWord_var.get() != '':
        wordNet_keyword_list.append(noun_verb_menu_var.get().lower() + "." + keyWord_var.get())
        keyWord_menu.configure(state="disabled")
        # keyWord_entry.configure(state="disabled")
        # wordNet_keyword_list.append(keyWord_var.get())
        activate_allOptions(noun_verb_menu_var.get())
keyWord_var.trace('w', add_wordNet_keyword)
keyWord_entry_var.trace('w', add_wordNet_keyword)

annotate_file_var.set(0)
annotate_file_checkbox = tk.Checkbutton(window, text='Annotate corpus (using WordNet csv output file from Zoom IN/DOWN)', variable=annotate_file_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,annotate_file_checkbox)

extract_proper_nouns_var.set(0)
extract_proper_nouns_checkbox = tk.Checkbutton(window, text='Extract WordNet PROPER nouns  (using WordNet csv output file from Zoom IN/DOWN)',
                                               variable=extract_proper_nouns_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               extract_proper_nouns_checkbox, True)
extract_proper_nouns_checkbox.config(text="Extract PROPER nouns  (using WordNet csv output file from Zoom IN/DOWN)")

extract_improper_nouns_var.set(0)
extract_improper_nouns_checkbox = tk.Checkbutton(window, text='Extract WordNet IMPROPER nouns  (using WordNet csv output file from Zoom IN/DOWN)',
                                                 variable=extract_improper_nouns_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.WordNet_extract_improper_nouns_pos, y_multiplier_integer,
                                               extract_improper_nouns_checkbox)
extract_improper_nouns_checkbox.config(text="Extract IMPROPER nouns  (using WordNet csv output file from Zoom IN/DOWN)")

aggregate_lemmatized_var.set(0)
aggregate_lemmatized_checkbox = tk.Checkbutton(window, text='Zoom OUT/UP (classify/aggregate lemmatized words in csv file)', variable=aggregate_lemmatized_var,
                                   onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               aggregate_lemmatized_checkbox)

extract_nouns_verbs_from_CoNLL_var.set(0)
extract_nouns_verbs_from_CoNLL_checkbox = tk.Checkbutton(window, text='Extract nouns & verbs from CoNLL table (for Zoom OUT/UP)',
                                              variable=extract_nouns_verbs_from_CoNLL_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               extract_nouns_verbs_from_CoNLL_checkbox)

aggregate_POS_var.set(0)
aggregate_POS_checkbox = tk.Checkbutton(window, text='Zoom OUT/UP (classify/aggregate input text document(s) by CoreNLP NOUN & VERB POS tags and WordNet NOUN & VERB synsets)', variable=aggregate_POS_var,
                                    onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               aggregate_POS_checkbox)

aggregate_bySentenceID_var.set(0)
# aggregate_bySentenceID_checkbox = tk.Checkbutton(window, text='Zoom OUT/UP by Sentence Index',
#                                                 variable=aggregate_bySentenceID_var, onvalue=1, offvalue=0,
#                                                 command=lambda: getDictFile())
aggregate_bySentenceID_checkbox = tk.Checkbutton(window, text='Zoom OUT/UP by Sentence ID',
                                                variable=aggregate_bySentenceID_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               aggregate_bySentenceID_checkbox, True)

dict_WordNet_filename_lb = tk.Label(window, text='csv file of WordNet classified/aggregated words')
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.WordNet_dict_WordNet_filename_lb_pos, y_multiplier_integer,
                    dict_WordNet_filename_lb, True, False, True, False,
                    90, GUI_IO_util.WordNet_dict_WordNet_filename_lb_pos,
                    "The csv file is obtained by running the ZOOM OUT/UP checkbox widget, above")

dict_WordNet_filename = tk.Entry(window, width=GUI_IO_util.WordNet_dict_WordNet_filename_width, textvariable=dict_WordNet_filename_var)
dict_WordNet_filename.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.WordNet_dict_WordNet_filename_pos, y_multiplier_integer,
                                               dict_WordNet_filename)

asked = False

def activate_allOptions(noun_verb, fromaggregate=False):
    global asked
    # all options FALSE
    # GUI_util.select_inputFilename_button.configure(state="disabled")
    # csv_file_var.set('')
    # csv_file_button.config(state='disabled')
    disaggregate_checkbox.configure(state='normal')
    annotate_file_checkbox.configure(state='normal')
    aggregate_lemmatized_checkbox.configure(state='normal')
    extract_proper_nouns_checkbox.configure(state='normal')
    extract_improper_nouns_checkbox.configure(state='normal')
    extract_nouns_verbs_from_CoNLL_checkbox.configure(state='normal')
    aggregate_POS_checkbox.configure(state='normal')
    aggregate_bySentenceID_checkbox.configure(state='normal')

    keyWord_menu.configure(state="disabled")
    keyWord_entry.configure(state="disabled")
    add_keyword_button.configure(width=GUI_IO_util.add_button_width, height=1, state="disabled")
    reset_keywords_button.configure(width=GUI_IO_util.reset_button_width, height=1, state="disabled")

    if len(wordNet_keyword_list) > 0:
        show_keywords_button.configure(state="normal")
    else:
        show_keywords_button.configure(state="disabled")

    if disaggregate_var.get() == True:
        aggregate_lemmatized_checkbox.configure(state='disabled')
        annotate_file_checkbox.configure(state='disabled')
        extract_proper_nouns_checkbox.configure(state='disabled')
        extract_improper_nouns_checkbox.configure(state='disabled')
        extract_nouns_verbs_from_CoNLL_checkbox.configure(state='disabled')
        aggregate_POS_checkbox.configure(state='disabled')
        aggregate_bySentenceID_checkbox.configure(state='disabled')
        if keyWord_var.get() != '':
            # + button
            add_keyword_button.configure(width=GUI_IO_util.add_button_width, height=1, state="normal")
            keyWord_entry.configure(state="disabled")
            OK_button.configure(state="disabled")
        else:
            add_keyword_button.configure(width=GUI_IO_util.add_button_width, height=1, state="disabled")
            keyWord_entry.configure(state="normal")
            if keyWord_entry_var.get() != '':
                keyWord_menu.configure(state="disabled")
                OK_button.configure(state="normal")
            else:
                OK_button.configure(state="disabled")
                keyWord_menu.configure(state="normal")

        # RESET button
        if keyWord_var.get() == '' and keyWord_entry_var.get() == '':
            reset_keywords_button.configure(width=GUI_IO_util.reset_button_width, height=1, state="disabled")
        else:
            reset_keywords_button.configure(width=GUI_IO_util.reset_button_width, height=1, state="normal")
    else:
        keyWord_var.set('')
        wordNet_keyword_list.clear()
        keyWord_entry_var.set('')
        dict_WordNet_filename_var.set('')

    # else:
    #     asked = False

    if annotate_file_var.get() == 1:
        if csv_file_var.get()=='' and asked==False:
            asked=True
            mb.showwarning("csv dictionary file",
                           "Please, select next the csv dictionary file you want to use to annotate your txt file(s) then click on the RUN button.")
            filePath=get_csv_file(window, 'Select INPUT csv dictionary file', [("dictionary files", "*.csv")], True)
            if filePath=='':
                return
        csv_file_button.config(state='normal')
    # else:
    #     asked = False

    if extract_proper_nouns_var.get() == True or extract_improper_nouns_var.get() == True:
        disaggregate_checkbox.configure(state='disabled')
        annotate_file_checkbox.configure(state='disabled')
        aggregate_lemmatized_checkbox.configure(state='disabled')
        extract_nouns_verbs_from_CoNLL_checkbox.configure(state='disabled')
        aggregate_POS_checkbox.configure(state='disabled')
        aggregate_bySentenceID_checkbox.configure(state='disabled')
        if csv_file_var.get() == '' and asked==False:
            asked=True
            mb.showwarning("csv WordNet dictionary",
                           "Please, select next the csv WordNet dictionary file (either verbose or simple) generated by the ZOOM IN/DOWN function then click on the RUN button.")
            filePath = get_csv_file(window, 'Select INPUT csv dictionary file', [("dictionary files", "*.csv")],
                                           False)
            if filePath == '':
                return
    # else:
    #     asked = False

    if aggregate_lemmatized_var.get() == 1: # aggregating UP
        if fromaggregate==False:
            if csv_file_var.get() == '' and asked==False:
                asked = True
                # mb.showwarning(title='csv WordNet dictionary',
                #                message="This is a reminder that you are searching WordNet for " + noun_verb_menu_var.get() + ".\n\nPlease, use the IO widget 'Select INPUT file' at the top of the GUI to select the csv file containing LEMMATIZED " + noun_verb_menu_var.get() + " values to be aggregated.\n\nThis file MUST contain LEMMATIZED " + noun_verb_menu_var.get() + " values, since WordNet only contains lemmatized values. If this is not the case, select a different NOUN/VERB option, and/or a different input file option.")
                mb.showwarning(title='Warning',
                               message='Please, select next the csv file with the LEMMATIZED words (noun or verb, since WordNet only contains lemmatized values) for which you need to find their aggregate (e.g., the verb walk as motion).\n\nPlease, select next the INPUT csv file to be used.')
                filePath =get_csv_file(window, 'Select INPUT csv dictionary file', [("dictionary files", "*.csv")], False)
                if filePath == '':
                    return
        csv_file_button.config(state='normal')
        GUI_util.select_inputFilename_button.configure(state="normal")
        disaggregate_checkbox.configure(state='disabled')
        annotate_file_checkbox.configure(state='disabled')
        extract_proper_nouns_checkbox.configure(state='disabled')
        extract_improper_nouns_checkbox.configure(state='disabled')
        extract_nouns_verbs_from_CoNLL_checkbox.configure(state='disabled')
        aggregate_POS_checkbox.configure(state='disabled')
        aggregate_bySentenceID_checkbox.configure(state='disabled')
    # else:
    #     asked = False

    if extract_nouns_verbs_from_CoNLL_var.get()==True:
        disaggregate_checkbox.configure(state='disabled')
        annotate_file_checkbox.configure(state='disabled')
        aggregate_lemmatized_checkbox.configure(state='disabled')
        extract_proper_nouns_checkbox.configure(state='disabled')
        extract_improper_nouns_checkbox.configure(state='disabled')
        aggregate_POS_checkbox.configure(state='disabled')
        aggregate_bySentenceID_checkbox.configure(state='disabled')
        if csv_file_var.get() == '' and asked==False:
            asked=True
            mb.showwarning("csv CoNLL table",
                           "Please, select next the csv CoNLL table from which you want to extract nouns and verbs then click on the RUN button.")
            filePath = get_csv_file(window, 'Select INPUT csv CoNLL file', [("CoNLL files", "*.csv")],
                                           False)
            if filePath == '':
                return
    # else:
    #     asked = False

    if aggregate_POS_var.get()==True:
        disaggregate_checkbox.configure(state='disabled')
        annotate_file_checkbox.configure(state='disabled')
        aggregate_lemmatized_checkbox.configure(state='disabled')
        extract_proper_nouns_checkbox.configure(state='disabled')
        extract_improper_nouns_checkbox.configure(state='disabled')
        extract_nouns_verbs_from_CoNLL_checkbox.configure(state='disabled')
        aggregate_bySentenceID_checkbox.configure(state='disabled')
    else:
        asked = False

    if aggregate_bySentenceID_var.get() == True:
        disaggregate_checkbox.configure(state='disabled')
        annotate_file_checkbox.configure(state='disabled')
        aggregate_lemmatized_checkbox.configure(state='disabled')
        extract_proper_nouns_checkbox.configure(state='disabled')
        extract_improper_nouns_checkbox.configure(state='disabled')
        extract_nouns_verbs_from_CoNLL_checkbox.configure(state='disabled')
        aggregate_POS_checkbox.configure(state='disabled')
        if csv_file_var.get() == '' and asked==False:
            asked=True
            mb.showwarning(title="Warning",
                           message="The Zoom OUT/UP by Sentence Index option requires in input 2 csv files:\n  1. a csv CoNLL file to get the sentence index;\n  2. a csv dictionary file containing the WordNet classification of LEMMATIZED words into higher-level aggregates and for which you want to see where in the text they are used (you will be prompted next to select this csv file; the file will have been generated by widget 'Zoom OUT/UP to higher-level aggregates'). \n\nAs a reminder, you are searching in the CoNLL table for " + noun_verb_menu_var.get() + ". The selected dictionary file of WordNet aggregated words must also contain " + noun_verb_menu_var.get() + " values - values to be found in the input CoNLL file " + inputFilename.get() + "\n\nIf this is not the case, select a different NOUN/VERB option, and/or different input/output file options.")

            filePath = get_csv_file(window, 'Select INPUT csv file of words classified/aggregated into WordNet synsets', [("csv files", "*.csv")],
                                           False)
            if filePath == '':
                return
            mb.showwarning("csv WordNet dictionary",
                           "Please, select next the csv WordNet dictionary file generated by the ZOOM IN/DOWN function then click on the RUN button.")
            filePath = get_csv_file(window, 'Select INPUT csv dictionary file', [("dictionary files", "*.csv")],
                                           False)
            if len(filePath) > 0:
                dict_WordNet_filename_var.set(filePath)
                GUI_util.select_inputFilename_button.configure(state='normal')
            else:
                # csv_file_var.set('')
                dict_WordNet_filename_var.set('')
                aggregate_bySentenceID_var.set(0)
        else:
            asked = False

disaggregate_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get()))
keyWord_entry_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get()))
annotate_file_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get(), True))
extract_proper_nouns_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get()))
extract_improper_nouns_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get()))
aggregate_lemmatized_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get()))
extract_nouns_verbs_from_CoNLL_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get()))
aggregate_POS_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get()))
aggregate_bySentenceID_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get()))

activate_allOptions(noun_verb_menu_var.get())

# set menu values
def setNounVerbMenu(*args):
    global noun_verb_menu_options
    noun_verb_menu_optionsSV = noun_verb_menu_options
    if noun_verb_menu_var.get() == 'NOUN':
        # 25 beginning nouns
        noun_verb_menu_options = 'act', 'animal', 'artifact', 'attribute', 'body', 'cognition', 'communication', 'event', 'feeling', 'food', 'group', 'location', 'motive', 'object', 'person', 'phenomenon', 'plant', 'possession', 'process', 'quantity', 'relation', 'shape', 'state', 'substance', 'time'
        if hidden_noun_lemma_csv.get() != '':
            csv_file_var.set(hidden_noun_lemma_csv.get())
    else:
        # 15 beginning verbs
        noun_verb_menu_options = 'body', 'change', 'cognition', 'communication', 'competition', 'consumption', 'contact', 'creation', 'emotion', 'motion', 'perception', 'possession', 'social', 'stative', 'weather'
        if hidden_verb_lemma_csv.get() != '':
            csv_file_var.set(hidden_verb_lemma_csv.get())
    m = keyWord_menu["menu"]
    m.delete(0, "end")
    for s in noun_verb_menu_options:
        m.add_command(label=s, command=lambda value=s: keyWord_var.set(value))
    if noun_verb_menu_optionsSV != noun_verb_menu_options:
        clear_keyword_list()

    #print('hidden_noun_lemma_csv, hidden_verb_lemma_csv',hidden_noun_lemma_csv.get(), hidden_verb_lemma_csv.get())

noun_verb_menu_var.trace("w", setNounVerbMenu)

setNounVerbMenu()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf','Statistical measures':'TIPS_NLP_Statistical measures.pdf','WordNet': 'TIPS_NLP_WordNet.pdf','The world of emotions and sentiments':'TIPS_NLP_The world of emotions and sentiments.pdf'}
#'Java download install run': 'TIPS_NLP_Java download install run.pdf'
TIPS_options = 'csv files - Problems & solutions','Statistical measures','WordNet','The world of emotions and sentiments' #, 'Java download install run'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
webSearch = "\n\nYou can search terms directly on the WordNet website at http://wordnetweb.princeton.edu/perl/webwn?s=&sub=Search+WordNet."


def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_csv_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "The INPUT csv file widget will display the csv file required by many algorithms in this GUI.\n\n   1. The algorithms that require a csv file in input will prompt you to select the appropriate csv file when you tick a checkbox.\n\n   2. Some algorithms, when you run them, will automatically write in the csv filename produced.\n\n   3. You can always click the Select INPUT CSV file button to change the selection.\n" + GUI_IO_util.msg_openFile)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the synset type (NOUN or VERB) that you want to use for your WordNet searches.\n\nLists of NOUNS and VERBS can be exported from a CoNLL table computed via the Stanford_CoreNLP.py script. Nouns would have POSTAG values NN* (* for any NN value) and verbs VB*. Tick the checkbox 'Extract nouns & verbs from CoNLL' to extract the lists." + webSearch)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to run the Python 3 script 'Zoom IN/DOWN'. The script uses the WordNet lexicon database to provide a list of terms associated to a starting keyword (synset) in a lexical hierarchy.\n\nThe IN/DOWN Java algorithm uses the MIT JWI (Java Wordnet Interface) (https://projects.csail.mit.edu/jwi/) to interface with WordNet.\n\nIt uses both hyponymy and meronymy to go DOWN the hierarchy.\n\nHyponym is the specific term used to designate a member of a class. X is a hyponym of Y if X is a (kind of) Y.\n\nMeronymy is the name of a constituent part of, the substance of, or a member of something. X is a meronym of Y if X is a part of Y.\n\nThus, you can construct a list of social actors (i.e., human disaggregates, groups, or organizations) by selecting 'person' as starting point.\n\nPlease, using the dropdown menu, select the starting keyword(s) (synsets) that the script will use to traverse the database in order to provide the list.\n\nNOUNS have 25 top-level synsets and VERB have 15.\n\nMultiple starting words are allowed. If your research deals with fairy tales, animals may also be disaggregates (e.g., a talking fox), so the starting keyword can be 'animal', with both 'person' and 'animal' as your combined keywords.\n\nPress the + button for multiple selections.\n\nPress RESET (or ESCape) to delete all values entered and start fresh.\n\nPress SHOW to display all selected values.\n\nIn INPUT all is required is the starting keywords that you will have selected or entered.\n\nIn OUTPUT the script will create 2 csv files, a one-column file with a list of all the terms found in the synset, and a five-columns file marked as verbose: a list of terms found (column 1), the selected WordNet category (column 2), definitions of the category (column 3), frequency of senses of lemma that are ranked according to their frequency of occurrence in semantic concordance texts (column 4), examples of use (column 5)." + webSearch)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "You can enter one or more, comma separated, terms into the 'YOUR keyword(s)'field, ignoring the pre-selected keywords. This option is particularly helpful if you want to restrict your search at a lower level, e.g. 'ethnic group' instead of 'person' to obtain a much shorter list of terms.\n\nPress OK when finished entering YOUR own values." + webSearch)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to annotate your input document(s) using a dictionary csv file generated by the \'Zoom IN\DOWN\' algorithm. Thus, you can extract all \'PERSON\' items from WordNet and annotate your corpus by those values.\n\nIn INPUT the function expects\n   1. either a single txt file or a directory of txt files to be annotated (txt file(s) are selected in the Setup INPUT/OUTPUT configuration widget);\n   2. a csv dictionary file generated by the ZOOM IN/DOWN widget and containing with the WordNet tags that will be used to annotate the text. You will be prompted to select the csv file when you tick the checkbox.\n\nIn OUTPUT the fnction produces an html file annotated according to the values found in the input csv dictionary file." + webSearch)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to extract proper or improper nouns from a NOUN ZOOM IN/DOWN list. Nouns are classified as proper or improper depending on whether the first character is upper or lower case.\n\nIn INPUT the function expects a csv file of NOUNs generated by the ZOOM IN/DOWN function (whether simple or verbose). You will be prompted to select the csv file when you tick the checkbox.\n\nIn OUTPUT, the function saves a csv file with only either proper or improper nouns, as identified by a first letter upper/lower case.\n\nThe first column of the dictionary file, whether simple or verbose, will always be used for extracting values.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to run the Python 3 script 'Zoom OUT/UP'.\n\nThe script uses the WordNet lexicon database to aggregate LEMMATIZED NOUNS and VERBS (LEMMATIZED, since WordNet only contains lemmatized values) listed in a csv file (e.g., run, flee, walk, ... aggregated as verbs of motion).\n\nYou can aggregate any list of LEMMATIZED nouns and verbs however obtained. Most likely, you will want to aggregate LEMMATIZED nouns and verbs from the CoNLL table computed via Stanford_CoreNLP.py script. NOUNS WOULD HAVE POSTAG VALUES NN* AND VERBS VB*. Tick the checkbox 'Extract nouns & verbs from CoNLL' to extract the lists.\n\nThe OUT/UP Java algorithm uses the MIT JWI (Java Wordnet Interface) (https://projects.csail.mit.edu/jwi/) to interface with WordNet.\n\nThe algorithm uses both ypernymy and holonymy to go UP the hierarchy.\n\nHypernym is the generic term used to designate a whole class of specific instances. Y is a hypernym of X if X is a (kind of) Y.\n\nHolonym is the name of the whole of which the meronym names a part. Y is a holonym of X if X is a part of Y.\n\nIn INPUT, the script expects a csv file where the first column contains a list of LEMMATIZED NOUNS or VERBS to be aggregated (the column headerr does not matter). You will be prompted to select the csv file when you tick the checkbox. Tick the checkbox 'Extract nouns & verbs from CoNLL' to extract the lists.\n\nNotice that you can process either a LEMMATIZED NOUN list or a LEMMATIZED VERB list at a time. You cannot process both at the same time.\n\nIn OUTPUT the script will create a csv file that contains the aggregate values of the various nouns and verbs.\n\nCAVEAT: For VERBS, the 'stative' category includes the auxiliary 'be' probably making up the vast majority of stative verbs. Similarly, the category 'possession' include the auxiliary 'have' (and 'get'). You may wish to exclude these auxiliary verbs from frequencies." + webSearch)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to run a Python 3 script to extract all LEMMATIZED nouns and verbs from a CoNLL table (LEMMATIZED, since WordNet only contains lemmatized values) - nouns and verbs to be used by the 'Zoom OUT/UP' algorithm to aggregate nouns and verbs into WorNet categories.\n\nFor convenience, the script will also export the original words for nouns and verbs as found in FORM.\n\nIn INPUT, the script expects 2 csv files:\n  1. a csv CoNLL file;\n  2. a csv dictionary file containing the WordNet classification of LEMMATIZED words into higher-level aggregates (LEMMATIZED, since WordNet only contains lemmatized values). This file is generated by the 'Zoom OUT/UP' widget.\n   You will be prompted to select these csv files when you tick the checkbox.\n\nIn OUTPUT, the script produces a csv file and an Excel line plot of the aggregate WordNet categories by sentence index.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to classify your document(s) by the main NOUN & VERB WordNet synsets.\n\nThe function uses the Stanford CoreNLP POS (Part of Speech) annotator to extract Nouns and Verbs to be then classified via WordNet.\n\nIn INPUT the function expects either a single txt file or a directory of txt files.\n\nIn OUTPUT the fnction produces a csv file of nouns and verbs classified by WordNet top synsets.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to run the Python 3 script 'Zoom OUT/UP by Sentence Index' to provide a csv file and an Excel line plot of the aggregate WordNet categories by sentence index for more in-grained linguistic analyses.\n\nIn INPUT, the script expects 2 csv files:\n  1. a csv CoNLL file;\n  2. a csv dictionary file containing the WordNet classification of LEMMATIZED words into higher-level aggregates generated by the 'Zoom OUT/UP' widget (LEMMATIZED, since WordNet only contains lemmatized values).\n   You will be prompted to select these csv files when you tick the checkbox.\n\nIn OUTPUT, the script produces a csv file and an Excel line plot of the aggregate WordNet categories by sentence index.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

# change the value of the readMe_message

# GUI_util.select_inputFilename_button.configure(state="disabled")
readMe_message = "The Python 3 and Java scripts interface with the lexical database WordNet to find word semantically related words.\n\nThe GUI widgets allow you to zoom IN, zoom OUT (or zoom DOWN and UP) in the WordNet database and to display WordNet categories by sentence index. The two IN/DOWN, OUT/UP Java algorithms use the MIT JWI (Java Wordnet Interface) (https://projects.csail.mit.edu/jwi/) to interface with WordNet.\n\nYou will need to download WordNet from https://wordnet.princeton.edu/download/current-version.\n\nWhen zooming IN/DOWN, you basically take a closer look at a term, going down the hierarchy (e.g., 'person' would give a list of words such as 'police', 'woman', ... or anyone who is a member of the group \'person\').\n\nWhen zooming OUT/UP, you find terms'higher-level aggregates (e.g., 'walk', 'run', 'flee'as verbs of a higher-level verb aggregate 'motion')" + webSearch
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

reminders_util.checkReminder(
        config_filename,
        reminders_util.title_options_English_language_WordNet,
        reminders_util.message_English_language_WordNet,
        True)

GUI_util.window.mainloop()
