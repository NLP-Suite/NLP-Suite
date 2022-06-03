#written by Roberto Franzosi August 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"what\'s in your corpus",['os','tkinter'])==False:
    sys.exit(1)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_user_interface_util
import IO_files_util
import statistics_txt_util
import knowledge_graphs_WordNet_util
import Stanford_CoreNLP_annotator_util
import topic_modeling_gensim_util
import topic_modeling_mallet_util
import reminders_util
import file_checker_util
import file_cleaner_util

# RUN section ______________________________________________________________________________________________________________________________________________________

run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_Excel_chart_output_checkbox.get(),
                            GUI_util.charts_dropdown_field.get(),
                            utf8_var.get(),
                            ASCII_var.get(),
                            corpus_statistics_var.get(),
                            corpus_options_menu_var.get(),
                            topics_var.get(),
                            topics_Mallet_var.get(),
                            topics_Gensim_var.get(),
                            open_GUI_var.get(),
                            what_else_var.get(),
                            what_else_menu_var.get(),
                            quote_var.get(),
                            memory_var.get())

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
def run(inputFilename,inputDir, outputDir,
        openOutputFiles,
        createExcelCharts,
        chartPackage,
        utf8_var,
        ASCII_var,
        corpus_statistics_var,
        corpus_options_menu_var,
        topics_var,
        topics_Mallet_var,
        topics_Gensim_var,
        open_GUI_var,
        what_else_var,
        what_else_menu_var,
        single_quote,
        memory_var):

    filesToOpen=[]

    # if inputFilename=='': # only corpus in dir used
    #     mb.showwarning(title='The scripts behind the What\'s in your corpus scripts expect in input a directory containing a sett of txt files.\n\nPlease, select a directory and try again.)
    #     return

    if (corpus_statistics_var==False and \
        corpus_options_menu_var==False and \
        topics_Mallet_var==False and \
        topics_Gensim_var==False and \
        what_else_var==False and \
        what_else_var == False):
            mb.showwarning(title='No options selected', message='No options have been selected.\n\nPlease, select an option and try again.')
            return

    if utf8_var==True:
        file_checker_util.check_utf8_compliance(GUI_util.window, inputFilename, inputDir, outputDir,openOutputFiles)

    if ASCII_var==True:
        result=file_cleaner_util.convert_quotes(GUI_util.window,inputFilename, inputDir)
        if result==False:
            return

    if corpus_statistics_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('statistics_txt_util.py')==False:
            return

        lemmatize = False
        stopwords = False

        if '*' or 'stopwords' in corpus_options_menu_var:
            stopwords = True
        if '*' or 'Lemmatize' in corpus_options_menu_var:
            lemmatize=True

        if '*' in corpus_options_menu_var or 'stopwords' in corpus_options_menu_var or 'Lemmatize' in corpus_options_menu_var:
            output = statistics_txt_util.compute_corpus_statistics(window, inputFilename, inputDir, outputDir, False, createExcelCharts, chartPackage,
                                  stopwords, lemmatize)
            if output!=None:
                filesToOpen.extend(output)

        if IO_libraries_util.check_inputPythonJavaProgramFile('statistics_txt_util.py') == False:
            return

        # inputFilename = ''  # for now we only process a whole directory
        excludePunctuation=True
        n_grams_size=3
        bySentenceIndex_word_var=False
        normalize=False

        statistics_txt_util.compute_character_word_ngrams(GUI_util.window, inputFilename, inputDir,
                                                          outputDir, n_grams_size, normalize, excludePunctuation, 1, openOutputFiles, createExcelCharts, chartPackage,
                                                          bySentenceIndex_word_var)

        if 'lines' in corpus_options_menu_var:
            output = statistics_txt_util.read_line(window, inputFilename, inputDir, outputDir, False, createExcelCharts, chartPackage)
            if output!=None:
                filesToOpen.extend(output)

    if topics_var==True:
        if topics_Gensim_var==True:
            if IO_libraries_util.check_inputPythonJavaProgramFile('topic_modeling_gensim_main.py')==False:
                return
            routine_options = reminders_util.getReminders_list(config_filename)
            reminders_util.checkReminder(config_filename,
                                         reminders_util.title_options_topic_modeling_gensim,
                                         reminders_util.message_topic_modeling_gensim,
                                         True)
            routine_options = reminders_util.getReminders_list(config_filename)

            if open_GUI_var == True:
                call("python topic_modeling_gensim_main.py", shell=True)
            else:
                # run with all default values; do not run MALLET
                output = topic_modeling_gensim_util.run_Gensim(GUI_util.window, inputDir, outputDir, num_topics=20,
                                                      remove_stopwords_var=1, lemmatize=1, nounsOnly=0, run_Mallet=False, openOutputFiles=openOutputFiles,createExcelCharts=createExcelCharts)
                if output!=None:
                    filesToOpen.extend(output)

            if topics_Mallet_var==True:
                if open_GUI_var == True:
                    call("python topic_modeling_mallet_main.py", shell=True)
                else:
                    # running with default values
                    output = topic_modeling_mallet_util.run(inputDir, outputDir, openOutputFiles=openOutputFiles, createExcelCharts=createExcelCharts, chartPackage=chartPackage, OptimizeInterval=True, numTopics=20)
                    if output != None:
                        filesToOpen.extend(output)

    nouns_var=False
    verbs_var=False
    dialogues_var = False
    people_organizations_var = False
    gender_var = False
    times_var = False
    locations_var = False
    nature_var = False

    if what_else_var and what_else_menu_var == '*':
        nouns_var = True
        verbs_var = True

    if 'noun' in what_else_menu_var.lower():
        nouns_var = True
    if 'verb' in what_else_menu_var.lower():
        verbs_var = True
    if 'dialogue' in what_else_menu_var.lower():
        dialogues_var = True
    if 'people' in what_else_menu_var.lower():
        people_organizations_var = True
    if 'male' in what_else_menu_var.lower():
        gender_var = True
    if 'time' in what_else_menu_var.lower():
        times_var = True
    if 'location' in what_else_menu_var.lower():
        locations_var=True
    if 'nature' in what_else_menu_var.lower():
        nature_var=True

    inputFilenameSV=inputFilename #inputFilename value is changed in the WordNet function

    if (what_else_var and what_else_menu_var == '*') or nouns_var==True or verbs_var==True or people_organizations_var==True or gender_var==True or dialogues_var==True or times_var==True or locations_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('Stanford_CoreNLP_annotator_util.py')==False:
            return

        if nouns_var or verbs_var:

            if nouns_var or verbs_var or what_else_menu_var == '*':
                WordNetDir, missing_external_software = IO_libraries_util.get_external_software_dir('whats_in_your_corpus', 'WordNet')
                if WordNetDir == None:
                    return

                annotator = ['POS']
                files = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                            outputDir, openOutputFiles, createExcelCharts, chartPackage,
                                            annotator, False, memory_var)
                if len(files) > 0:
                    noun_verb=''
                    if verbs_var == True:
                        inputFilename = files[0] # Verbs but... double check
                        if "verbs" in inputFilename.lower():
                            noun_verb='VERB'
                        else:
                            return
                        output = knowledge_graphs_WordNet_util.aggregate_GoingUP(WordNetDir,inputFilename, outputDir, config_filename, noun_verb,
                                                                    openOutputFiles, createExcelCharts)
                        if output!=None:
                            filesToOpen.extend(output)

                    if nouns_var == True:
                        inputFilename = files[1]  # Nouns but... double check
                        if "nouns" in inputFilename.lower():
                            noun_verb='NOUN'
                        else:
                            return
                        output = knowledge_graphs_WordNet_util.aggregate_GoingUP(WordNetDir,inputFilename, outputDir, config_filename, noun_verb,
                                                                    openOutputFiles, createExcelCharts)
                        if output!=None:
                            filesToOpen.extend(output)
            else:
                if (what_else_var and what_else_menu_var == '*'):
                    IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Missing WordNet',
                                                       'The analysis of \'What else is in your corpus\' will skip the nouns and verbs classification requiring WordNet and will continue with all other CoreNLP annotators')

        if what_else_var and what_else_menu_var == '*':
            inputFilename=inputFilenameSV

            annotator_list = ['NER', 'gender', 'quote', 'normalized-date']
            NER_list=['PERSON','ORGANIZATION', 'CITY', 'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION']
            output = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir, openOutputFiles, createExcelCharts, chartPackage,
                                                                      annotator_list, False, memory_var,
                                                                      NERs=NER_list)
            if output != None and output!=[]:
                filesToOpen.extend(output)

        if people_organizations_var == True:
            annotator = 'NER'
            NER_list=['PERSON','ORGANIZATION']

            output = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir, openOutputFiles, createExcelCharts, chartPackage,
                                                                      annotator, False, memory_var,
                                                                      NERs=NER_list)
            if output != None:
                filesToOpen.extend(output)

        if gender_var == True:
            annotator = 'gender'
            output = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir, openOutputFiles, createExcelCharts, chartPackage,
                                                                      annotator, False, memory_var)
            if output != None:
                filesToOpen.extend(output)

        if dialogues_var==True:
            annotator = 'quote'
            output = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir, openOutputFiles, createExcelCharts, chartPackage,
                                                                      annotator, False, memory_var, single_quote_var = single_quote)
            if output != None:
                filesToOpen.extend(output)

        if times_var==True:
            annotator='normalized-date'
            output = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir, outputDir,
                        openOutputFiles, createExcelCharts, chartPackage,
                        annotator, False, memory_var)
            if output != None:
                filesToOpen.extend(output)

        if locations_var == True:
            annotator = 'NER'
            NER_list = ['CITY', 'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION']

            output = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir, openOutputFiles, createExcelCharts, chartPackage,
                                                                      annotator, False, memory_var,
                                                                      NERs=NER_list)
            if output != None:
                filesToOpen.extend(output)

    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=430, # height at brief display
                             GUI_height_full=470, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=1, # to be added for full display
                             increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for a Sweeping View of Your Corpus (Single/Multiple Document(s)) - A Pipeline'
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
config_input_output_numeric_options=[0,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)

utf8_var= tk.IntVar()
ASCII_var= tk.IntVar()
corpus_statistics_var= tk.IntVar()
corpus_options_menu_var= tk.StringVar()
topics_var= tk.IntVar()
topics_Mallet_var= tk.IntVar()
topics_Gensim_var= tk.IntVar()
open_GUI_var= tk.IntVar()

memory_var = tk.IntVar()
nouns_var= tk.IntVar()
verbs_var= tk.IntVar()

what_else_var= tk.IntVar()
what_else_menu_var= tk.StringVar()
people_organizations_var= tk.IntVar()
locations_var= tk.IntVar()
times_var= tk.IntVar()
dialogues_var= tk.IntVar()
nature_var= tk.IntVar()

quote_var = tk.IntVar()
y_multiplier_integer_SV=0 # used to set the quote_var widget on the proper GUI line

def clear(e):
    corpus_statistics_var.set(1)
    corpus_options_menu_var.set('*')
    what_else_var.set(1)
    what_else_menu_var.set('*')
    quote_checkbox.place_forget()  # invisible
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

utf8_var.set(1)
utf8_checkbox = tk.Checkbutton(window, text='Check input document(s) for utf-8 encoding', variable=utf8_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,utf8_checkbox)

ASCII_var.set(1)
ASCII_checkbox = tk.Checkbutton(window, text='Convert non-ASCII apostrophes & quotes and % to percent', variable=ASCII_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,ASCII_checkbox)

corpus_statistics_var.set(1)
corpus_statistics_checkbox = tk.Checkbutton(window,text="Compute document(s) statistics (word frequency & word n-grams by document)", variable=corpus_statistics_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,corpus_statistics_checkbox,True)

corpus_options_menu_var.set('*')
corpus_options_menu_lb = tk.Label(window, text='document(s) statistics options')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+440,y_multiplier_integer,corpus_options_menu_lb,True)
corpus_options_menu = tk.OptionMenu(window, corpus_options_menu_var, '*','Lemmatize words', 'Exclude stopwords & punctuation', 'Compute lines length')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+620,y_multiplier_integer,corpus_options_menu)

topics_checkbox = tk.Checkbutton(window,text="What are the topics? (Topic modeling)", variable=topics_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,topics_checkbox,True)

def changed_filename(*args):
    if inputFilename.get()!='':
        reminders_util.checkReminder(config_filename,
                                     reminders_util.title_options_topic_modeling,
                                     reminders_util.message_topic_modeling,
                                     True)
        topics_var.set(0)
        topics_checkbox.configure(state='disabled')
    else:
        topics_var.set(1)
        topics_checkbox.configure(state='normal')
inputFilename.trace('w',changed_filename)
# input_main_dir_path.trace('w',changed_filename)

topics_Mallet_var.set(0)
topics_Mallet_checkbox = tk.Checkbutton(window,text="via MALLET", variable=topics_Mallet_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+440,y_multiplier_integer,topics_Mallet_checkbox,True)

topics_Gensim_var.set(1)
topics_Gensim_checkbox = tk.Checkbutton(window,text="via Gensim", variable=topics_Gensim_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+570,y_multiplier_integer,topics_Gensim_checkbox,True)

open_GUI_var.set(0)
open_GUI_checkbox = tk.Checkbutton(window,text="open Gensim/MALLET GUI", variable=open_GUI_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+700,y_multiplier_integer,open_GUI_checkbox)

def activate_topics(*args):
    if topics_var.get()==True:
        topics_Mallet_checkbox.configure(state='normal')
        topics_Gensim_checkbox.configure(state='normal')
        open_GUI_checkbox.configure(state='normal')
    else:
        topics_Mallet_checkbox.configure(state='disabled')
        topics_Gensim_checkbox.configure(state='disabled')
        open_GUI_checkbox.configure(state='disabled')
topics_var.trace('w',activate_topics)

def activate_Mallet(*args):
    if topics_var.get()==True:
        topics_Gensim_var.set(0)
        if topics_Mallet_var.get()==True:
            open_GUI_checkbox.configure(state='normal')
            topics_Gensim_checkbox.configure(state='disabled')
            open_GUI_checkbox.configure(state='normal')
        else:
            open_GUI_var.set(0)
            topics_Gensim_checkbox.configure(state='normal')
            open_GUI_checkbox.configure(state='disabled')
topics_Mallet_var.trace('w',activate_Mallet)

def activate_Gensim(*args):
    if topics_var.get()==True:
        if topics_Gensim_var.get()==True:
            open_GUI_checkbox.configure(state='normal')
            topics_Mallet_checkbox.configure(state='disabled')
            open_GUI_checkbox.configure(state='normal')
        else:
            open_GUI_checkbox.configure(state='disabled')
            topics_Mallet_checkbox.configure(state='normal')
            open_GUI_checkbox.configure(state='disabled')
topics_Gensim_var.trace('w',activate_Gensim)

def activate_allOptions(*args):
    if open_GUI_var.get()==True:
        corpus_statistics_var.set(0)
        corpus_statistics_checkbox.configure(state='disabled')
        what_else_var.set(0)
        topics_Mallet_checkbox.configure(state='disabled')
        topics_Gensim_checkbox.configure(state='disabled')
        what_else_checkbox.configure(state='disabled')
    else:
        corpus_statistics_var.set(1)
        corpus_statistics_checkbox.configure(state='normal')
        what_else_var.set(1)
        topics_Mallet_checkbox.configure(state='normal')
        topics_Gensim_checkbox.configure(state='normal')
        what_else_checkbox.configure(state='normal')
open_GUI_var.trace('w',activate_allOptions)


what_else_var.set(1)
what_else_checkbox = tk.Checkbutton(window,text="What else is in your document(s)? (via Stanford CoreNLP and WordNet)", variable=what_else_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,what_else_checkbox,True)
what_else_menu_var.set('*')
what_else_menu = tk.OptionMenu(window,  what_else_menu_var, '*', 'Dialogues (CoreNLP Neural Network)','Noun and verb classes (CoreNLP NER & WordNet)', 'People & organizations (CoreNLP NER)', 'Females & males (CoreNLP Neural Network)',
                               'References to date & time (CoreNLP normalized NER dates)',
                               'References to geographical locations (CoreNLP NER)',
                               'References to nature (CoreNLP & WordNet)')
what_else_menu.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate() + 440, y_multiplier_integer,
                                               what_else_menu, True)

quote_checkbox = tk.Checkbutton(window, text='Include single quotes',
                                       variable=quote_var,
                                       onvalue=1, offvalue=0)

def activate_what_else_menu(*args):
    global y_multiplier_integer, y_multiplier_integer_SV
    if what_else_var.get()==True:
        what_else_menu.config(state='normal')
        if "*" in what_else_menu_var.get() or "Dialogues" in what_else_menu_var.get():
            if y_multiplier_integer_SV!=0:
                y_multiplier_integer = y_multiplier_integer_SV - 1
            quote_var.set(0)
            y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 500,
                                                           y_multiplier_integer,
                                                           quote_checkbox, True)
            quote_checkbox.configure(state='normal')
        else:
            quote_checkbox.place_forget()  # invisible
    else:
        what_else_menu.config(state='disabled')
        quote_checkbox.place_forget()  # invisible

what_else_var.trace('w',activate_what_else_menu)
what_else_menu_var.trace('w',activate_what_else_menu)

activate_what_else_menu()

# memory options

memory_var_lb = tk.Label(window, text='Memory ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate() + 900, y_multiplier_integer,
                                               memory_var_lb, True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(4)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate() + 950, y_multiplier_integer,
                                               memory_var)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Excel - Enabling Macros': 'TIPS_NLP_Excel Enabling macros.pdf', 'Lemmas & stopwords':'TIPS_NLP_NLP Basic Language.pdf', 'Text encoding (utf-8)': 'TIPS_NLP_Text encoding (utf-8).pdf', 'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf', 'N-Grams (word & character)':'TIPS_NLP_Ngram (word & character).pdf','Google Ngram Viewer':'TIPS_NLP_Ngram Google Ngram Viewer.pdf','NLP Suite Ngram and Word Co-Occurrence Viewer':'TIPS_NLP_Ngram and Word Co-Occurrence Viewer.pdf','Statistical measures':'TIPS_NLP_Statistical measures.pdf','Topic modeling':'TIPS_NLP_Topic modeling.pdf','Topic modeling and corpus size':'TIPS_NLP_Topic modeling and corpus size.pdf','Topic modeling (Gensim)':'TIPS_NLP_Topic modeling Gensim.pdf','Topic modeling (Mallet)':'TIPS_NLP_Topic modeling Mallet.pdf','Mallet installation':'TIPS_NLP_Topic modeling Mallet installation.pdf','NER (Named Entity Recognition)':'TIPS_NLP_NER (Named Entity Recognition).pdf','WordNet':'TIPS_NLP_WordNet.pdf','Stanford CoreNLP date extractor (NER normalized date)':'TIPS_NLP_Stanford CoreNLP date extractor.pdf',"Gender annotator":"TIPS_NLP_Gender annotator.pdf"}
TIPS_options='Text encoding (utf-8)','Excel - Enabling Macros', 'csv files - Problems & solutions', 'Lemmas & stopwords', 'N-Grams (word & character)','Google Ngram Viewer','NLP Suite Ngram and Word Co-Occurrence Viewer','Statistical measures','Topic modeling','Topic modeling and corpus size','Topic modeling (Gensim)','Topic modeling (Mallet)','Mallet installation','NER (Named Entity Recognition)','Stanford CoreNLP date extractor (NER normalized date)','WordNet','Gender annotator'


# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, tick the checkbox to check your input corpus for utf-8 encoding.\n   Non utf-8 compliant texts are likely to lead to code breakdown.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, tick the checkbox to convert non-ASCII apostrophes & quotes and % to percent.\n   ASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n   % signs may lead to code breakdon of Stanford CoreNLP.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick checkbox to compute corpus statistics: number of documents, number of sentences and words, word n-grams by document.\n\nFOR N-GRAMS, THERE IS A SEPARATE SCRIPT WITH MORE GENERAL OPTIONS: NGrams_CoOccurrences_Viewer_main.\n\nThe * option will lemmatize words and exclude stopwords and punctuation. IT WILL COMPUTE BASIC WORD N-GRAMS. IT WILL NOT COMPUTE LINE LENGTH. YOU WOULD NEED TO RUN THE LINE LENGTH OPTION SEPARATELY.\n\nLine length in a typical document mostly depends upon typesetting formats. Only for poetry or music lyrics does the line-length measure make sense; in fact, you could use the option the detect those documents in your corpus characterized by different typesetting formats (.g., a poem document among narrative documents).\n\nRUN THE LINE-LENGTH OPTION ONLY IF IT MAKES SENSE FOR YOUR CORPUS.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick the Mallet or Gensim checkboxes to run run LDA Topic Modeling to find out the main topics of your corpus.\n\nTick the \'open GUI\' checkbox to open the specialized Gensim topic modeling GUI that offers more options. Mallet can only be run via its GUI")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help","Please, tick the checkbox to analyze your corpus for a variety of tools. Select the default \'*\' to run all options. Allternatively, select the specific option to run.\n\nThe NLP tools will allow you to answer questions such as:\n  1. Are there dialogues in your corpus? The CoreNLP QUOTE annotator extracts quotes from text and attributes the quote to the speaker. The default CoreNLP parameter is DOUBLE quotes. If you want to process both DOUBLE and SINGLE quotes, plase tick the checkbox 'Include single quotes.'\n  .2 Do nouns and verbs cluster in specific aggregates (e.g., communication, movement)?\n  3. Does the corpus contain references to people (by gender) and organizations?\n  4.  References to dates and times?\n  5. References to geographical locations that could be placed on a map?\n  6. References to nature (e.g., weather, seasons, animals, plants)?")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),0)

# change the value of the readMe_message
readMe_message="The GUI brings together various Python 3 scripts to buil a pipeline for the analysis of a corpus, automatically extracting all relevant data from texts and visualizing the results.\n\nEach tool performs all required computations then saves results as csv files and visualizes them in various ways (word clouds, Excel charts, and HTML files)."
readMe_command = lambda: GUI_IO_util.display_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

if y_multiplier_integer_SV == 0:
    y_multiplier_integer_SV = y_multiplier_integer

GUI_util.window.mainloop()
