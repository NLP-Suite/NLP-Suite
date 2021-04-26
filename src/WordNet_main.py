#Written by Roberto Franzosi
#Modified by Cynthia Dong (Fall 2019-Spring 2020)
#Wordnet_bySentenceID and get_case_initial_row written by Yi Wang (April 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"WordNet",['os','tkinter','pandas'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
import pandas as pd

import GUI_IO_util
import IO_files_util
import IO_CoNLL_util
import WordNet_util
import annotator_dictionary_util
import sentence_analysis_util
import Stanford_CoreNLP_annotator_util

# RUN section ______________________________________________________________________________________________________________________________________________________

pd.set_option('display.max_columns', 500)
# DocumentID    DocumentName    SenetenceID     (FullSentence)
# written by Yi Wang April 2020

def run(inputFilename, inputDir, outputDir,openOutputFiles,
        createExcelCharts,
        classify_var,
        noun_verb,
        character_var,
        wordNet_keyword_list,
        ancestor_var,
        extract_nouns_verbs_var,
        ancestor_bySentenceID_var,
        dict_WordNet_filename_var, 
        annotator_dictionary_var,
        annotator_dictionary_file,
        aggregate_dictionary_file,
        extract_proper_nouns,
        extract_improper_nouns):

    WordNetDir = IO_libraries_util.get_external_software_dir('WordNet_main', 'WordNet')
    if WordNetDir == None:
        return

    global filesToOpen
    filesToOpen = []  # Store all files that are to be opened once finished

    # print("noun_verb",noun_verb)

    if classify_var==False and character_var==False and ancestor_var==False and annotator_dictionary_var==False and ancestor_bySentenceID_var==False and extract_nouns_verbs_var==False and extract_proper_nouns==False and extract_improper_nouns==False:
        mb.showerror(title='Missing required information', message="No options have been selected.\n\nPlease, tick one of the available options and try again.")
        return False

    if character_var==True and len(wordNet_keyword_list)==0:
        mb.showerror(title='Missing required information', message="You have selected to run the option 'Zoom IN/DOWN to find related words', but you have not entered any keywords required to run the script.\n\nPlease, enter the keywords and try again.")
        return False

    if ancestor_var==True and len(inputFilename)==0:
        mb.showerror(title='Missing required information', message="You have selected to run the option 'Zoom OUT/UP to find higher-level aggregates', but you have not selected the Input csv file for " + noun_verb + " required to run the script.\n\nPlease, select the Input file and try again.")
        return False

    if classify_var==True:
        annotator = ['POS']
        memory_var=4
        nouns_var = True
        verbs_var = True
        files = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(inputFilename, inputDir,
                                                                 outputDir, openOutputFiles, createExcelCharts,
                                                                 annotator, False, memory_var)
        if len(files) > 0:
            noun_verb = ''
            if verbs_var == True:
                inputFilename = files[0]  # Verbs but... double check
                if "verbs" in inputFilename.lower():
                    noun_verb = 'VERB'
                else:
                    return
                output = WordNet_util.ancestor_GoingUP(WordNetDir, inputFilename, outputDir, noun_verb,
                                                       openOutputFiles, createExcelCharts)
                if output != None:
                    filesToOpen.extend(output)

            if nouns_var == True:
                inputFilename = files[1]  # Nouns but... double check
                if "nouns" in inputFilename.lower():
                    noun_verb = 'NOUN'
                else:
                    return
                output = WordNet_util.ancestor_GoingUP(WordNetDir, inputFilename, outputDir, noun_verb,
                                                       openOutputFiles, createExcelCharts)
                if output != None:
                    filesToOpen.extend(output)

    if character_var==True:
        filesToOpen= WordNet_util.character_GoingDOWN(WordNetDir,outputDir, wordNet_keyword_list, noun_verb)
    elif ancestor_var==True:
        filesToOpen= WordNet_util.ancestor_GoingUP(WordNetDir, inputFilename, outputDir, noun_verb, openOutputFiles,createExcelCharts)

    if ancestor_bySentenceID_var==1:
        # check that input file is a CoNLL table
        if not IO_CoNLL_util.check_CoNLL(inputFilename):
            return
        outputFilename=IO_files_util.generate_output_file_name(inputFilename, outputDir, '.csv', 'WordNet', 'conll')
        filesToOpen.append(outputFilename)
        sentence_analysis_util.Wordnet_bySentenceID(inputFilename,dict_WordNet_filename_var,outputFilename,outputDir,noun_verb,openOutputFiles,createExcelCharts)

    if extract_nouns_verbs_var==True:
        # check that input file is a CoNLL table
        if not IO_CoNLL_util.check_CoNLL(inputFilename):
            return
        noun_form_csv,noun_lemma_csv,verb_form_csv,verb_lemma_csv = IO_CoNLL_util.get_nouns_verbs_CoNLL(inputFilename, outputDir)
        filesToOpen.append(noun_form_csv)
        filesToOpen.append(noun_lemma_csv)
        filesToOpen.append(verb_form_csv)
        filesToOpen.append(verb_lemma_csv)

    if annotator_dictionary_var:
        if IO_libraries_util.inputProgramFileCheck('annotator_dictionary_util.py') == False:
            return
        csvValue_color_list = []
        bold_var=True
        color_palette_dict_var = 'red'  # default color, if forgotten

        tagAnnotations = ['<span style=\"color: ' + color_palette_dict_var + '; font-weight: bold\">', '</span>']

        filesToOpen = annotator_dictionary_util.dictionary_annotate(inputFilename, inputDir, outputDir,
                                                                    annotator_dictionary_file, 'Term', csvValue_color_list,
                                                                    bold_var, tagAnnotations, '.txt')

    if extract_proper_nouns==1 or extract_improper_nouns==1:
        if noun_verb!='NOUN':
            mb.showerror(title='Option not available', message="You have selected to run the option 'Extract PROPER/IMPROPER nouns' with VERB.\n\nPlease, select NOUN and try again.")
            return
        if len(inputFilename)==0:
            mb.showerror(title='Missing input file', message="You have selected to run the option 'Extract PROPER/IMPROPER nouns'. The function expects in input a WordNet dictionary file previously exported with the 'Zoom IN/DOWN' function for nouns.\n\nPlease, select an input WordNet dictionary file and try again.")
            return
        check_column=0
        WordNet_util.get_case_initial_row(inputFilename, outputDir,'Term', extract_proper_nouns)

    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

#the values of the GUI widgets MUST be entered in the command as widget.get() otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(), 
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_Excel_chart_output_checkbox.get(),
                            classify_var.get(),
                            noun_verb_menu_var.get(), 
                            character_var.get(), 
                            wordNet_keyword_list,
                            ancestor_var.get(),
                            extract_nouns_verbs_var.get(),
                            ancestor_bySentenceID_var.get(),
                            dict_WordNet_filename_var.get(),
                            annotator_dictionary_var.get(),
                            annotator_dictionary_file_var.get(),
                            aggregate_dictionary_file_var.get(),
                            extract_proper_nouns_var.get(),
                            extract_improper_nouns_var.get())


GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

GUI_size='1300x630'
GUI_label='Graphical User Interface (GUI) for WordNet tools'
config_filename='WordNet-config.txt'
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
config_option=[0,2,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

# GUI CHANGES add following lines to every special GUI
y_multiplier_integer = GUI_util.y_multiplier_integer + 2
window = GUI_util.window
config_input_output_options = GUI_util.config_input_output_options
config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path
outputDir = GUI_util.output_dir_path

openOutputFiles = GUI_util.open_csv_output_checkbox.get()
createExcelCharts = GUI_util.create_Excel_chart_output_checkbox.get()

GUI_util.GUI_top(config_input_output_options, config_filename)

wordNet_keyword_list = []

classify_var = tk.IntVar()
noun_verb_menu_var = tk.StringVar()
noun_verb_menu_var.set('NOUN')
character_var = tk.IntVar()
keyWord_var = tk.StringVar()
keyWord_entry_var = tk.StringVar()
ancestor_var = tk.IntVar()
extract_nouns_verbs_var = tk.IntVar()
ancestor_bySentenceID_var = tk.IntVar()
dict_WordNet_filename_var = tk.StringVar()
extract_proper_nouns_var = tk.IntVar()
extract_improper_nouns_var = tk.IntVar()
annotator_dictionary_var = tk.IntVar()
annotator_dictionary_file_var = tk.StringVar()
aggregate_dictionary_var = tk.IntVar()
aggregate_dictionary_file_var= tk.StringVar()

WordNet_category_lb = tk.Label(window, text='WordNet category (synset)')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               WordNet_category_lb, True)

noun_verb_menu = tk.OptionMenu(window, noun_verb_menu_var, 'NOUN', 'VERB')
noun_verb_menu.configure(width=9, state="normal")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 170, y_multiplier_integer,
                                               noun_verb_menu)

character_var.set(0)
character_checkbox = tk.Checkbutton(window, text='Zoom IN/DOWN to find related words', variable=character_var,
                                    onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               character_checkbox, True)

def activate_keyword_menu():
    if keyWord_var.get() != '':
        keyWord_menu.configure(state="normal")


add_keyword_button = tk.Button(window, text='+', width=2, height=1, state='disabled',
                               command=lambda: activate_keyword_menu())
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               add_keyword_button, True)

reset_keywords_button = tk.Button(window, text='Reset', width=5, height=1, state='disabled',
                                  command=lambda: clear_keyword_list())
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 50, y_multiplier_integer,
                                               reset_keywords_button, True)


def showKeywordList():
    mb.showwarning(title='Warning', message='The currently selected keywords are:\n\n' + ','.join(
        wordNet_keyword_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')


show_keywords_button = tk.Button(window, text='Show', width=5, height=1, state='disabled',
                                 command=lambda: showKeywordList())
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 100, y_multiplier_integer,
                                               show_keywords_button, True)

noun_verb_menu_options = []
keyWord_var.set('')
keyWord_menu_lb = tk.Label(window, text='Keyword (synset)')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 170, y_multiplier_integer,
                                               keyWord_menu_lb, True)
keyWord_menu = tk.OptionMenu(window, keyWord_var, noun_verb_menu_options)
# keyWord_menu.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 290, y_multiplier_integer,
                                               keyWord_menu, True)

keyWord_entry_lb = tk.Label(window, text='YOUR keyword(s) ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 430, y_multiplier_integer,
                                               keyWord_entry_lb, True)

keyWord_entry = tk.Entry(window, width=40, textvariable=keyWord_entry_var)
keyWord_entry.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 550, y_multiplier_integer,
                                               keyWord_entry, True)

OK_button = tk.Button(window, text='OK', width=3, height=1, state='disabled', command=lambda: accept_WordNet_list())
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 830, y_multiplier_integer,
                                               OK_button)


def clear(e):
    keyWord_var.set('')
    keyWord_entry_var.set('')
    dict_WordNet_filename_var.set('')
    # activate_allOptions(noun_verb_menu_var.get())
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


def getDictFile():
    # if ancestor_var.get()==True or ancestor_bySentenceID_var.get()==True or extract_proper_nouns_var.get()==True or extract_improper_nouns_var.get()==True:
    if ancestor_bySentenceID_var.get() == False:
        dict_WordNet_filename_var.set('')
        # GUI_util.select_input_file_button.configure(state='disabled')
    else:
        mb.showwarning(title="Warning",
                       message="The Zoom OUT/UP by Sentence Index option requires in input 2 csv files:\n  1. a csv CoNLL file to get the sentence index (you select this csv file in the IO widgets at the top of the GUI);\n  2. a csv dictionary file containing the WordNet classification of LEMMATIZED words into higher-level aggregates and for which you want to see where in the text they are used (you will be prompted next to select this csv file; the file will have been generated by widget 'Zoom OUT/UP to higher-level aggregates'). \n\nAs a reminder, you are searching in the CoNLL table for " + noun_verb_menu_var.get() + ". The selected dictionary file of WordNet aggregated words must also contain " + noun_verb_menu_var.get() + " values - values to be found in the input CoNLL file " + inputFilename.get() + "\n\nIf this is not the case, select a different NOUN/VERB option, and/or different input/output file options.")
        initialFolder = os.path.dirname(os.path.abspath(__file__))
        filePath = tk.filedialog.askopenfilename(title='Select INPUT csv file of words classified/aggregated into WordNet synsets', initialdir=initialFolder,
                                                 filetypes=[("csv files", "*.csv")])
        if len(filePath) > 0:
            dict_WordNet_filename_var.set(filePath)
            GUI_util.select_input_file_button.configure(state='normal')
        else:
            dict_WordNet_filename_var.set('')
            ancestor_bySentenceID_var.set(0)
            # GUI_util.select_input_file_button.configure(state='disabled')

def get_dictionary_file(window,title,fileType,annotate):
    #annotator_dictionary_var.set('')
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)
    if len(filePath)>0:
        if annotate:
            annotator_dictionary_file.config(state='normal')
            annotator_dictionary_file_var.set(filePath)
        else:
            aggregate_dictionary_file.config(state='normal')
            aggregate_dictionary_file_var.set(filePath)


annotator_dictionary_var.set(0)
annotator_dictionary_checkbox = tk.Checkbutton(window, text='Annotate corpus (using WordNet dictionary from Zoom IN/DOWN)', variable=annotator_dictionary_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,annotator_dictionary_checkbox,True)

#setup a button to open Windows Explorer on the selected input directory
current_y_multiplier_integer2=y_multiplier_integer-1
# openInputFile_button  = tk.Button(window, width=3, state='disabled', text='', command=lambda: IO_files_util.openFile(window, annotator_dictionary_file_var.get()))
openInputFile_button  = tk.Button(window, width=3, text='', command=lambda: IO_files_util.openFile(window, annotator_dictionary_file_var.get()))
openInputFile_button.place(x=GUI_IO_util.get_labels_x_coordinate()+420, y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

annotator_dictionary_button=tk.Button(window, width=20, text='Select dictionary file',command=lambda: get_dictionary_file(window,'Select INPUT csv dictionary file', [("dictionary files", "*.csv")],True))
# annotator_dictionary_button.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+460, y_multiplier_integer,annotator_dictionary_button,True)

annotator_dictionary_file=tk.Entry(window, width=80,textvariable=annotator_dictionary_file_var)
annotator_dictionary_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+640, y_multiplier_integer,annotator_dictionary_file)

extract_proper_nouns_var.set(0)
extract_proper_nouns_checkbox = tk.Checkbutton(window, text='Extract WordNet PROPER nouns',
                                               variable=extract_proper_nouns_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               extract_proper_nouns_checkbox, True)
extract_proper_nouns_checkbox.config(text="Extract PROPER nouns")

extract_improper_nouns_var.set(0)
extract_improper_nouns_checkbox = tk.Checkbutton(window, text='Extract WordNet IMPROPER nouns',
                                                 variable=extract_improper_nouns_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               extract_improper_nouns_checkbox)
extract_improper_nouns_checkbox.config(text="Extract IMPROPER nouns")

ancestor_var.set(0)
ancestor_checkbox = tk.Checkbutton(window, text='Zoom OUT/UP (classify/aggregate lemmatized words in csv file)', variable=ancestor_var,
                                   onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               ancestor_checkbox, True)

# aggregate_dictionary_var.set(0)
# aggregate_dictionary_checkbox = tk.Checkbutton(window, text='CHE E?', variable=aggregate_dictionary_var, onvalue=1, offvalue=0)
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,aggregate_dictionary_checkbox,True)

#setup a button to open Windows Explorer on the selected input directory
current_y_multiplier_integer2=y_multiplier_integer-1
# openInputFile_button  = tk.Button(window, width=3, state='disabled', text='', command=lambda: IO_files_util.openFile(window, annotator_dictionary_file_var.get()))
openInputFile_button  = tk.Button(window, width=3, text='', command=lambda: IO_files_util.openFile(window, aggregate_dictionary_file_var.get()))
openInputFile_button.place(x=GUI_IO_util.get_labels_x_coordinate()+420, y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

aggregate_dictionary_button=tk.Button(window, width=20, text='Select dictionary file',command=lambda: get_dictionary_file(window,'Select INPUT csv dictionary file', [("dictionary files", "*.csv")],False))
# annotator_dictionary_button.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+460, y_multiplier_integer,aggregate_dictionary_button,True)

aggregate_dictionary_file=tk.Entry(window, width=80,textvariable=aggregate_dictionary_file_var)
aggregate_dictionary_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+640, y_multiplier_integer,aggregate_dictionary_file)

extract_nouns_verbs_var.set(0)
extract_nouns_verbs_checkbox = tk.Checkbutton(window, text='Extract nouns & verbs from CoNLL table (for Zoom OUT/UP)',
                                              variable=extract_nouns_verbs_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               extract_nouns_verbs_checkbox)

classify_var.set(0)
classify_checkbox = tk.Checkbutton(window, text='Zoom OUT/UP (classify/aggregate input text document(s) by CoreNLP NOUN & VERB POS tags and WordNet NOUN & VERB synsets)', variable=classify_var,
                                    onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               classify_checkbox)

ancestor_bySentenceID_var.set(0)
ancestor_bySentenceID_checkbox = tk.Checkbutton(window, text='Zoom OUT/UP by Sentence Index',
                                                variable=ancestor_bySentenceID_var, onvalue=1, offvalue=0,
                                                command=lambda: getDictFile())
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               ancestor_bySentenceID_checkbox, True)

dict_WordNet_filename_lb = tk.Label(window, text='csv file of WordNet classified/aggregated words (from ZOOM OUT/UP)')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               dict_WordNet_filename_lb, True)

dict_WordNet_filename = tk.Entry(window, width=80, textvariable=dict_WordNet_filename_var)
dict_WordNet_filename.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 400, y_multiplier_integer,
                                               dict_WordNet_filename)

def activate_IOButton():
    if extract_proper_nouns_var.get():
        extract_improper_nouns_var.set(0)
    if extract_improper_nouns_var.get():
        extract_proper_nouns_var.set(0)
    if extract_proper_nouns_var.get() or extract_improper_nouns_var.get():
        # GUI_util.select_input_file_button.configure(state='normal')
        if GUI_util.inputFilename.get() == '':
            mb.showwarning(title='Warning',
                           message='The Extract PROPER/IMPROPER nouns function requires in input a csv WordNet dictionary file (either verbose or simple); you select this csv file in the IO widgets at the top of the GUI.')
    # else:
    #     GUI_util.select_input_file_button.configure(state='disabled')

def activate_allOptions(noun_verb, fromAncestor=False):
    if len(wordNet_keyword_list) > 0:
        show_keywords_button.configure(state="normal")
    else:
        show_keywords_button.configure(state="disabled")

    if character_var.get() == True:
        ancestor_checkbox.configure(state='disabled')
        ancestor_bySentenceID_checkbox.configure(state='disabled')
        extract_proper_nouns_checkbox.configure(state='disabled')
        extract_improper_nouns_checkbox.configure(state='disabled')
        extract_nouns_verbs_checkbox.configure(state='disabled')
        if keyWord_var.get() != '':
            # + button
            add_keyword_button.configure(width=5, height=1, state="normal")
            keyWord_entry.configure(state="disabled")
            OK_button.configure(state="disabled")
        else:
            add_keyword_button.configure(width=5, height=1, state="disabled")
            keyWord_entry.configure(state="normal")
            if keyWord_entry_var.get() != '':
                keyWord_menu.configure(state="disabled")
                OK_button.configure(state="normal")
            else:
                OK_button.configure(state="disabled")
                keyWord_menu.configure(state="normal")

        # RESET button
        if keyWord_var.get() == '' and keyWord_entry_var.get() == '':
            reset_keywords_button.configure(width=5, height=1, state="disabled")
        else:
            reset_keywords_button.configure(width=5, height=1, state="normal")
    elif ancestor_var.get() == 1:
        if fromAncestor:
            mb.showwarning(title='csv WordNet dictionary',
                           message="This is a reminder that you are searching WordNet for " + noun_verb_menu_var.get() + ".\n\nPlease, use the IO widget 'Select INPUT file' at the top of the GUI to select the csv file containing LEMMATIZED " + noun_verb_menu_var.get() + " values to be aggregated.\n\nThis file MUST contain LEMMATIZED " + noun_verb_menu_var.get() + " values, since WordNet only contains lemmatized values. If this is not the case, select a different NOUN/VERB option, and/or a different input file option.")
        if GUI_util.inputFilename.get() == '':
            mb.showwarning(title='Warning',
                           message='The Zoom OUT/UP option requires in input a csv file with the LEMMATIZED words (noun or verb, since WordNet only contains lemmatized values) for which you need to find their aggregate (e.g., the verb walk as motion).\n\nPlease, select next the INPUT csv file to be used.')
        GUI_util.select_input_file_button.configure(state="normal")
        character_checkbox.configure(state='disabled')
        ancestor_bySentenceID_checkbox.configure(state='disabled')
        extract_proper_nouns_checkbox.configure(state='disabled')
        extract_improper_nouns_checkbox.configure(state='disabled')

    elif ancestor_bySentenceID_var.get() == True:
        character_checkbox.configure(state='disabled')
        ancestor_checkbox.configure(state='disabled')
        extract_proper_nouns_checkbox.configure(state='disabled')
        extract_improper_nouns_checkbox.configure(state='disabled')
        extract_nouns_verbs_checkbox.configure(state='disabled')
    elif extract_proper_nouns_var.get() == True or extract_improper_nouns_var.get() == True:
        character_checkbox.configure(state='disabled')
        ancestor_checkbox.configure(state='disabled')
        ancestor_bySentenceID_checkbox.configure(state='disabled')
        extract_nouns_verbs_checkbox.configure(state='disabled')
    elif extract_nouns_verbs_var.get()==True:
        character_checkbox.configure(state='disabled')
        ancestor_checkbox.configure(state='disabled')
        ancestor_bySentenceID_checkbox.configure(state='disabled')
        extract_proper_nouns_checkbox.configure(state='disabled')
        extract_improper_nouns_checkbox.configure(state='disabled')
    else:
        # all options FALSE
        # GUI_util.select_input_file_button.configure(state="disabled")
        character_checkbox.configure(state='normal')
        ancestor_checkbox.configure(state='normal')
        ancestor_bySentenceID_checkbox.configure(state='normal')
        extract_proper_nouns_checkbox.configure(state='normal')
        extract_improper_nouns_checkbox.configure(state='normal')
        extract_nouns_verbs_checkbox.configure(state='normal')

        wordNet_keyword_list.clear()
        keyWord_var.set('')
        keyWord_entry_var.set('')
        dict_WordNet_filename_var.set('')
        keyWord_menu.configure(state="disabled")
        keyWord_entry.configure(state="disabled")
        add_keyword_button.configure(width=5, height=1, state="disabled")
        reset_keywords_button.configure(width=5, height=1, state="disabled")


character_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get()))
ancestor_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get(), True))
keyWord_entry_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get()))
ancestor_bySentenceID_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get()))
extract_proper_nouns_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get()))
extract_improper_nouns_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get()))
extract_nouns_verbs_var.trace('w', lambda x, y, z: activate_allOptions(noun_verb_menu_var.get()))

def activate_CoNLL(*args):
    if extract_nouns_verbs_var.get() == True:
        GUI_util.select_input_file_button.configure(state="normal")
        mb.showwarning("csv CoNLL table",
                       "Please, use the IO widget 'Select INPUT file' at the top of the GUI to select the csv CoNLL table from which you want to extract nouns and verbs then click on the RUN button.")
    # else:
    #     GUI_util.select_input_file_button.configure(state="disabled")
extract_nouns_verbs_var.trace('w', activate_CoNLL)


def activate_WordNet(*args):
    if extract_proper_nouns_var.get() == True or extract_improper_nouns_var.get() == True:
        GUI_util.select_input_file_button.configure(state="normal")
        mb.showwarning("csv WordNet dictionary",
                       "Please, use the IO widget 'Select INPUT file' at the top of the GUI to select the WordNet dictionary file generated by the ZOOM IN/DOWN function then click on the RUN button.")
    # else:
    #     GUI_util.select_input_file_button.configure(state="disabled")

extract_proper_nouns_var.trace('w', activate_WordNet)
extract_improper_nouns_var.trace('w', activate_WordNet)

activate_allOptions(noun_verb_menu_var.get())
# set menu values
def setNounVerbMenu(*args):
    global noun_verb_menu_options
    noun_verb_menu_optionsSV = noun_verb_menu_options
    if noun_verb_menu_var.get() == 'NOUN':
        # 25 beginning nouns
        noun_verb_menu_options = 'act', 'animal', 'artifact', 'attribute', 'body', 'cognition', 'communication', 'event', 'feeling', 'food', 'group', 'location', 'motive', 'object', 'person', 'phenomenon', 'plant', 'possession', 'process', 'quantity', 'relation', 'shape', 'state', 'substance', 'time'
    else:
        # 15 beginning verbs
        noun_verb_menu_options = 'body', 'change', 'cognition', 'communication', 'competition', 'consumption', 'contact', 'creation', 'emotion', 'motion', 'perception', 'possession', 'social', 'stative', 'weather'
    m = keyWord_menu["menu"]
    m.delete(0, "end")
    for s in noun_verb_menu_options:
        m.add_command(label=s, command=lambda value=s: keyWord_var.set(value))
    if noun_verb_menu_optionsSV != noun_verb_menu_options:
        clear_keyword_list()


noun_verb_menu_var.trace("w", setNounVerbMenu)

setNounVerbMenu()

TIPS_lookup = {'WordNet': 'TIPS_NLP_WordNet.pdf', 'Java download install run': 'TIPS_NLP_Java download install run.pdf'}
TIPS_options = 'WordNet', 'Java download install run'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
webSearch = "\n\nYou can search terms directly on the WordNet website at http://wordnetweb.princeton.edu/perl/webwn?s=&sub=Search+WordNet."


def help_buttons(window, help_button_x_coordinate, basic_y_coordinate, y_step):
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                  GUI_IO_util.msg_csv_txtFile)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step, "Help",
                                  GUI_IO_util.msg_corpusData)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 2, "Help",
                                  GUI_IO_util.msg_outputDirectory)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 3, "Help",
                                  "Please, using the dropdown menu, select the synset type (NOUN or VERB) that you want to use for your WordNet searches.\n\nLists of NOUNS and VERBS can be exported from a CoNLL table computed via the Stanford_CoreNLP.py script. Nouns would have POSTAG values NN* (* for any NN value) and verbs VB*. Tick the checkbox 'Extract nouns & verbs from CoNLL' to extract the lists." + webSearch)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 4, "Help",
                                  "Please, tick the checkbox if you wish to run the Python 3 script 'Zoom IN/DOWN'. The script uses the WordNet lexicon database to provide a list of terms associated to a starting keyword (synset) in a lexical hierarchy.\n\nThe IN/DOWN Java algorithm uses the MIT JWI (Java Wordnet Interface) (https://projects.csail.mit.edu/jwi/) to interface with WordNet.\n\nIt uses both hyponymy and meronymy to go DOWN the hierarchy.\n\nHyponym is the specific term used to designate a member of a class. X is a hyponym of Y if X is a (kind of) Y.\n\nMeronymy is the name of a constituent part of, the substance of, or a member of something. X is a meronym of Y if X is a part of Y.\n\nThus, you can construct a list of social actors (i.e., human characters, groups, or organizations) by selecting 'person' as starting point.\n\nPlease, using the dropdown menu, select the starting keyword(s) (synsets) that the script will use to traverse the database in order to provide the list.\n\nNOUNS have 25 top-level synsets and VERB have 15.\n\nMultiple starting words are allowed. If your research deals with fairy tales, animals may also be characters (e.g., a talking fox), so the starting keyword can be 'animal', with both 'person' and 'animal' as your combined keywords.\n\nPress the + button for multiple selections.\n\nPress RESET (or ESCape) to delete all values entered and start fresh.\n\nPress SHOW to display all selected values.\n\nYou can also enter one or more, comma separated, terms into the 'YOUR keyword(s)'field, ignoring the pre-selected keywords. This option is particularly helpful if you want to restrict your search at a lower level, e.g. 'ethnic group' instead of 'person' to obtain a much shorter list of terms.\n\nPress OK when finished entering YOUR own values.\n\nIn INPUT all is required is the starting keywords that you will have selected or entered.\n\nIn OUTPUT the script will create 2 csv files, a one-column file with a list of all the terms found in the synset, and a five-columns file marked as verbose: a list of terms found (column 1), the selected WordNet category (column 2), definitions of the category (column 3), frequency of senses of lemma that are ranked according to their frequency of occurrence in semantic concordance texts (column 4), examples of use (column 5)." + webSearch)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 5, "Help",
                                  "Please, tick the checkbox if you wish to annotate your input document(s) using a dictionary csv file generated by the \'Zoom IN\DOWN\' algorithm. Thus, you can extract all \'PERSON\' items from WordNet and annotate your corpus by those values." + webSearch)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 6, "Help",
                                  "Please, tick the checkbox if you wish to extract proper or improper nouns from a NOUN ZOOM IN/DOWN list. Nouns are classified as proper or improper depending on whether the first character is upper or lower case.\n\nIn INPUT the function expects a csv file of NOUNs generated by the ZOOM IN/DOWN function (whether simple or verbose).\n\nIn OUTPUT, the function saves a csv file with only either proper or improper nouns, as identified by a first letter upper/lower case.\n\nThe first column of the dictionary file, whether simple or verbose, will always be used for extracting values.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 7, "Help",
                                  "Please, tick the checkbox if you wish to run the Python 3 script 'Zoom OUT/UP'.\n\nThe script uses the WordNet lexicon database to aggregate LEMMATIZED NOUNS and VERBS (LEMMATIZED, since WordNet only contains lemmatized values) listed in a csv file (e.g., run, flee, walk, ... aggregated as verbs of motion).\n\nYou can aggregate any list of LEMMATIZED nouns and verbs however obtained. Most likely, you will want to aggregate LEMMATIZED nouns and verbs from the CoNLL table computed via Stanford_CoreNLP.py script. NOUNS WOULD HAVE POSTAG VALUES NN* AND VERBS VB*. Tick the checkbox 'Extract nouns & verbs from CoNLL' to extract the lists.\n\nThe OUT/UP Java algorithm uses the MIT JWI (Java Wordnet Interface) (https://projects.csail.mit.edu/jwi/) to interface with WordNet.\n\nThe algorithm uses both ypernymy and holonymy to go UP the hierarchy.\n\nHypernym is the generic term used to designate a whole class of specific instances. Y is a hypernym of X if X is a (kind of) Y.\n\nHolonym is the name of the whole of which the meronym names a part. Y is a holonym of X if X is a part of Y.\n\nIn INPUT, the script expects a one-column csv file containing a list of LEMMATIZED NOUNS or VERBS to be aggregated. You will be prompted to select the dictionary csv file when you tick the checkbox. Tick the checkbox 'Extract nouns & verbs from CoNLL' to extract the lists.\n\nNotice that you can process either a LEMMATIZED NOUN list or a LEMMATIZED VERB list at a time. You cannot process both at the same time.\n\nIn OUTPUT the script will create a csv file that contains the aggregate values of the various nouns and verbs.\n\nCAVEAT: For VERBS, the 'stative' category includes the auxiliary 'be' probably making up the vast majority of stative verbs. Similarly, the category 'possession' include the auxiliary 'have' (and 'get'). You may wish to exclude these auxialiary verbs from frequencies." + webSearch)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 8, "Help",
                                  "Please, tick the checkbox if you wish to run a Python 3 script to extract all LEMMATIZED nouns and verbs from a CoNLL table (LEMMATIZED, since WordNet only contains lemmatized values) - nouns and verbs to be used by the 'Zoom OUT/UP' algorithm to aggregate nouns and verbs into WorNet categories.\n\nFor convenience, the script will also export the original words for nouns and verbs as found in FORM.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 9, "Help",
                                  "Please, tick the checkbox if you wish to classify your document(s) by the main NOUN & VERB WordNet synsets.\n\nThe function uses the Stanford CoreNLP POS (Part of Speech) annotator to extract Nouns and Verbs to be then classified via WordNet.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*10,"Help", 'The widgets become available only when a csv dictionary file has been selected (via the widget above \'Select dictionary file\').\n\nSelect csv field 1 is the column that contains the values used to annotate the input txt file(s). The FIRST COLUMN of the dictionary file is taken as the default column. YOU CAN SELECT A DIFFERENT COLUMN FROM THE DROPDOWN MENU Select csv field 1.\n\nIf the dictionary file contains more columns, you can select a SECOND COLUMN using the dropdown menu in Select csv field 2 to be used if you wish to use different colors for different items listed in this column. YOU CAN SELECT A DIFFERENT COLUMN FROM THE DROPDOWN MENU Select csv field 2. For example, column 1 contains words to be annotated in different colors by specific categories of field 2 (e.g., \'he\' to be annotated by a \'Gender\' column with the value \'Male\').\n\nThe specific values will have to be selected together with the specific color to be used. YOU CAN ACHIEVE THE SAME RESULT BY ANNOTATING THE SAME HTML FILE MULTIPLE TIMES USING A DIFFERENT DICTIONARY FILE ASSOCIATED EACH TIME TO A DIFFERENT COLOR.\n\n\nPress + for multiple selections.\nPress RESET (or ESCape) to delete all values entered and start fresh.\nPress Show to display all selected values.')
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 11, "Help",
                                  "Please, tick the checkbox if you wish to run the Python 3 script 'Zoom OUT/UP by Sentence Index' to provide a csv file and an Excel line plot of the aggregate WordNet categories by sentence index for more in-grained linguistic analyses.\n\nIn INPUT, the script expects 2 csv files:\n  1. a csv CoNLL file; you select this file in the IO widgets at the top of the GUI (the 'Select INPUT file' IO widget will become available after selecting the dictionary file);\n  2. a csv dictionary file containing the WordNet classification of LEMMATIZED words into higher-level aggregates (LEMMATIZED, since WordNet only contains lemmatized values). This file is generated by the 'Zoom OUT/UP' widget. You will be prompted to select the dictionary csv file when you tick the checkbox.\n\nIn OUTPUT, the script produces a csv file and an Excel line plot of the aggregate WordNet categories by sentence index.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 12, "Help",
                                  GUI_IO_util.msg_openOutputFiles)

help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), GUI_IO_util.get_basic_y_coordinate(),
             GUI_IO_util.get_y_step())

# change the value of the readMe_message

# GUI_util.select_input_file_button.configure(state="disabled")
readMe_message = "The Python 3 and Java scripts interface with the lexical database WordNet to find word semantically related words.\n\nThe three GUI widgets allow you to zoom IN, zoom OUT (or zoom DOWN and UP) in the WordNet database and to display WordNet categories by sentence index. The two IN/DOWN, OUT/UP Java algorithms use the MIT JWI (Java Wordnet Interface) (https://projects.csail.mit.edu/jwi/) to interface with WordNet.\n\nYou will need to download WordNet from https://wordnet.princeton.edu/download/current-version.\n\nWhen zooming IN/DOWN, you basically take a closer look at a term, going down the hierarchy (e.g., 'person' would give a list of words such as 'police', 'woman', ... or anyone who is a member of the group \'person\').\n\nWhen zooming OUT/UP, you find terms'higher-level aggregates (e.g., 'walk', 'run', 'flee'as verbs of a higher-level verb aggregate 'motion')" + webSearch
readMe_command = lambda: GUI_IO_util.readme_button(window, GUI_IO_util.get_help_button_x_coordinate(),
                                                   GUI_IO_util.get_basic_y_coordinate(), "Help", readMe_message)
GUI_util.GUI_bottom(config_input_output_options, y_multiplier_integer, readMe_command, TIPS_lookup, TIPS_options)

# GUI_util.softwareDir.set(IO_libraries_util.get_software_path_if_available('WordNet'))

GUI_util.window.mainloop()
