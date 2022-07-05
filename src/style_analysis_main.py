# written by Roberto Franzosi (Spring/summer 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"style_analysis_main.py",['os','csv','tkinter','ntpath','collections','subprocess'])==False:
    sys.exit(0)

import os
import tkinter.messagebox as mb
import tkinter as tk
import subprocess
from subprocess import call

import IO_user_interface_util
import GUI_IO_util
import IO_files_util
import file_spell_checker_util
import statistics_txt_util
import abstract_concreteness_analysis_util
import lib_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir,openOutputFiles,createCharts,chartPackage,
    CoNLL_table_analysis_var,
    nominalization_var,
    complexity_readability_analysis_var,
    vocabulary_analysis_var,
    ngrams_analysis_var,
    # CoNLL_table_analysis_menu_var,
    complexity_readability_analysis_menu_var,
    vocabulary_analysis_menu_var,
    ngrams_analysis_menu_var,
    gender_guesser_var):

    filesToOpen = []  # Store all files that are to be opened once finished
    openOutputFilesSV=openOutputFiles
    outputDir_style=outputDir

    if (CoNLL_table_analysis_var==False and
        nominalization_var==False and
        complexity_readability_analysis_var == False and
        vocabulary_analysis_var == False and
        ngrams_analysis_var==False and
        gender_guesser_var==False):
        mb.showwarning('Warning','No options have been selected.\n\nPlease, select an option and try again.')
        return

    if CoNLL_table_analysis_var == True:
        call("python CoNLL_table_analyzer_main.py", shell=True)
        return

    if nominalization_var == True:
        call("python nominalization_main.py", shell=True)
        return

    if complexity_readability_analysis_var == True:
        if '*' in complexity_readability_analysis_menu_var or 'Sentence' in complexity_readability_analysis_menu_var:
            if IO_libraries_util.check_inputPythonJavaProgramFile('statistics_txt_util.py') == False:
                return
            filesToOpen = statistics_txt_util.compute_sentence_complexity(GUI_util.window, inputFilename,
                                                                     inputDir, outputDir,
                                                                     openOutputFiles, createCharts, chartPackage)
        if '*' in complexity_readability_analysis_menu_var or 'Text' in complexity_readability_analysis_menu_var:
            if IO_libraries_util.check_inputPythonJavaProgramFile('statistics_txt_util.py') == False:
                return
            statistics_txt_util.compute_sentence_text_readability(GUI_util.window, inputFilename, inputDir,
                                                             outputDir, openOutputFiles, createCharts, chartPackage)

        if complexity_readability_analysis_menu_var=='':
            mb.showwarning('Warning', 'No option has been selected for Complexity/readability analysis.\n\nPlease, select an option from the dropdown menu and try again.')
            return

    if vocabulary_analysis_var == True:
        openOutputFilesSV=openOutputFiles
        openOutputFiles = False  # to make sure files are only opened at the end of this multi-tool script
        if vocabulary_analysis_menu_var=='':
            mb.showwarning('Warning', 'No option has been selected for Vocabulary analysis.\n\nPlease, select an option and try again.')
            return
        if 'Repetition' in vocabulary_analysis_menu_var:
            mb.showwarning('Warning', 'The selected option is not available yet.\n\nSorry!\n\nDo check out the repetition finder algorithm in the CoNLL Table Analyzer GUI.')
            return
        if '*' == vocabulary_analysis_menu_var:
            outputDir_style = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                                   label='style',
                                                                   silent=True)
            if outputDir_style == '':
                return
        else:
            outputDir_style=outputDir

        if '*' in vocabulary_analysis_menu_var or 'unigrams' in vocabulary_analysis_menu_var:
            output = statistics_txt_util.process_words(window, inputFilename, inputDir, outputDir_style,
                                                                   openOutputFiles, createCharts, chartPackage,'unigrams')
            if output != None:
                filesToOpen.extend(output)
        if '*' in vocabulary_analysis_menu_var or 'capital' in vocabulary_analysis_menu_var:
            output = statistics_txt_util.process_words(window, inputFilename, inputDir, outputDir_style,
                                                                   openOutputFiles, createCharts, chartPackage,'capital')
            if output != None:
                filesToOpen.extend(output)
        if '*' in vocabulary_analysis_menu_var or 'Short' in vocabulary_analysis_menu_var:
            output =statistics_txt_util.process_words(window,inputFilename,inputDir, outputDir_style, openOutputFiles, createCharts, chartPackage,'Short')
            if output != None:
                filesToOpen.extend(output)
        if '*' in vocabulary_analysis_menu_var or 'Vowel' in vocabulary_analysis_menu_var:
            output = statistics_txt_util.process_words(window, inputFilename, inputDir, outputDir_style, openOutputFiles, createCharts, chartPackage,'Vowel')
            if output != None:
                filesToOpen.extend(output)
        if '*' in vocabulary_analysis_menu_var or 'Punctuation' in vocabulary_analysis_menu_var:
            output =statistics_txt_util.process_words(window,inputFilename, inputDir, outputDir_style, openOutputFiles, createCharts, chartPackage,'Punctuation')
            if output != None:
                filesToOpen.extend(output)

        if '*' == vocabulary_analysis_menu_var or 'Unusual' in vocabulary_analysis_menu_var:
            output =file_spell_checker_util.nltk_unusual_words(window, inputFilename, inputDir, outputDir_style, False, createCharts, chartPackage)
            if output != None:
                filesToOpen.extend(output)
        if '*' == vocabulary_analysis_menu_var or 'Abstract' in vocabulary_analysis_menu_var:
            mode = "both" # mean, median, both (calculates both mean and median)
            output = abstract_concreteness_analysis_util.main(GUI_util.window, inputFilename, inputDir, outputDir_style, openOutputFiles, createCharts, chartPackage, processType='')
            if output != None:
                filesToOpen.extend(output)
        if '*' == vocabulary_analysis_menu_var or 'Yule' in vocabulary_analysis_menu_var:
            output =statistics_txt_util.yule(window, inputFilename, inputDir, outputDir)
            if output != None:
                filesToOpen.extend(output)
        if '*' in vocabulary_analysis_menu_var or 'detection' in vocabulary_analysis_menu_var:
                output = file_spell_checker_util.language_detection(window, inputFilename, inputDir, outputDir_style,
                                                                         openOutputFiles, createCharts, chartPackage)
                if output != None:
                    filesToOpen.extend(output)

    if ngrams_analysis_var == True:
        if '*' in ngrams_analysis_menu_var or 'Character' in ngrams_analysis_menu_var or 'Word' in ngrams_analysis_menu_var:
            if 'Character' in ngrams_analysis_menu_var:
                ngramType=0
            else:
                ngramType = 1
            if IO_libraries_util.check_inputPythonJavaProgramFile('statistics_txt_util.py') == False:
                return
            ngramsNumber=4
            normalize = False
            excludePunctuation = False
            frequency=0

            statistics_txt_util.compute_character_word_ngrams(GUI_util.window, inputFilename, inputDir,
                                                              outputDir, ngramsNumber, normalize,
                                                              excludePunctuation, ngramType, frequency,
                                                              openOutputFiles, createCharts, chartPackage,
                                                              bySentenceIndex_var)

        if '*' in ngrams_analysis_menu_var or 'Hapax' in ngrams_analysis_menu_var:
            ngramsNumber=1
            ngramType = 1
            normalize = False
            excludePunctuation = False
            if 'Hapax' in ngrams_analysis_menu_var:
                frequency = 1
            else:
                frequency = None

            statistics_txt_util.compute_character_word_ngrams(GUI_util.window, inputFilename, inputDir,
                                                              outputDir, ngramsNumber, normalize,
                                                              excludePunctuation, ngramType, frequency,
                                                              openOutputFiles, createCharts, chartPackage,
                                                              bySentenceIndex_var)
        if '*' in ngrams_analysis_menu_var or 'Repetition' in ngrams_analysis_menu_var or 'POSTAG' in ngrams_analysis_menu_var or 'DEPREL' in ngrams_analysis_menu_var or 'NER' in ngrams_analysis_menu_var:
            mb.showwarning('Warning','The selected option is not available yet.\n\nSorry!')
            if 'Repetition' in ngrams_analysis_menu_var:
                mb.showwarning('Warning','Do check out the repetition finder algorithm in the CoNLL Table Analyzer GUI.')
            return
        if ngrams_analysis_menu_var=='':
            mb.showwarning('Warning', 'No option has been selected for N-grams analysis.\n\nPlease, select an option and try again.')
            return

    if gender_guesser_var==True:
        mb.showwarning('Warning',
                       'When the Gender Guesser (Hacker Factor) webpage opens, make sure to read carefully the page content in order to understand:\n1. how this sophisticated neural network Java tool can guess the gender identity of a text writer (male or female);\n2. the difference between formal and informal text genre;\n3. the meaning of the gender estimate as "Weak emphasis could indicate European";\n4. the limits of the algorithms (about 60-70% accuraracy).\n\nYou can also read Argamon, Shlomo, Moshe Koppel, Jonathan Fine, and Anat Rachel Shimoni. 2003. "Gender, Genre, and Writing Style in Formal Written Texts," Text, Vol. 23, No. 3, pp. 321–346.')
        IO_files_util.runScript_fromMenu_option('Gender guesser', 0, inputFilename, inputDir, outputDir,
                                  openOutputFiles, createCharts, chartPackage)
        return

    openOutputFiles=openOutputFilesSV
    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir_style)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_chart_output_checkbox.get(),
                                GUI_util.charts_dropdown_field.get(),
                                CoNLL_table_analysis_var.get(),
                                nominalization_var.get(),
                                complexity_readability_analysis_var.get(),
                                vocabulary_analysis_var.get(),
                                ngrams_analysis_var.get(),
                                # CoNLL_table_analysis_menu_var.get(),
                                complexity_readability_analysis_menu_var.get(),
                                vocabulary_analysis_menu_var.get(),
                                ngrams_analysis_menu_var.get(),
                                gender_guesser_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=480, # height at brief display
                             GUI_height_full=520, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=1, # to be added for full display
                             increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Style Analysis'
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
config_input_output_numeric_options=[6,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename,config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)

def clear(e):
    CoNLL_table_analysis_checkbox.configure(state='normal')
    nominalization_checkbox.configure(state='normal')
    complexity_readability_analysis_checkbox.configure(state='normal')
    vocabulary_analysis_checkbox.configure(state='normal')
    ngrams_analysis_checkbox.configure(state='normal')

    CoNLL_table_analysis_var.set(0)
    nominalization_var.set(0)
    complexity_readability_analysis_var.set(0)
    vocabulary_analysis_var.set(0)
    ngrams_analysis_var.set(0)

    # CoNLL_table_analysis_menu_var.set('')
    complexity_readability_analysis_menu_var.set('')
    vocabulary_analysis_menu_var.set('')
    ngrams_analysis_menu_var.set('')

    # nominalization_checkbox.configure(state='disabled')
    # complexity_readability_analysis_menu.configure(state='disabled')
    # vocabulary_analysis_menu.configure(state='disabled')
    # ngrams_analysis_menu.configure(state='disabled')

    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

# GUI CHANGES cut/paste special GUI widgets from GUI_util

bySentenceIndex_var=tk.IntVar()

CoNLL_table_analysis_var=tk.IntVar()
nominalization_var=tk.IntVar()
complexity_readability_analysis_var=tk.IntVar()
vocabulary_analysis_var=tk.IntVar()
ngrams_analysis_var=tk.IntVar()
gender_guesser_var=tk.IntVar()

# CoNLL_table_analysis_menu_var=tk.StringVar()
complexity_readability_analysis_menu_var=tk.StringVar()
vocabulary_analysis_menu_var=tk.StringVar()
ngrams_analysis_menu_var=tk.StringVar()

CoNLL_table_analysis_var.set(0)
CoNLL_table_analysis_checkbox = tk.Checkbutton(window, text='CoNLL table analysis (GUI)', variable=CoNLL_table_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,CoNLL_table_analysis_checkbox)

nominalization_var.set(0)
nominalization_checkbox = tk.Checkbutton(window, text='Nominalization (GUI)', variable=nominalization_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,nominalization_checkbox)

# CoNLL_table_analysis_lb = tk.Label(window, text='Select the CoNLL table analysis you wish to perform')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(),y_multiplier_integer,CoNLL_table_analysis_lb,True)
# CoNLL_table_analysis_menu = tk.OptionMenu(window,CoNLL_table_analysis_menu_var,'*','Clauses','Nouns','Verbs','Function words','DEPREL','POSTAG','NER')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate()+400, y_multiplier_integer,CoNLL_table_analysis_menu)

complexity_readability_analysis_var.set(0)
complexity_readability_analysis_checkbox = tk.Checkbutton(window, text='Complexity/readability analysis', variable=complexity_readability_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,complexity_readability_analysis_checkbox,True)

complexity_readability_analysis_menu_var.set('*')
complexity_readability_analysis_lb = tk.Label(window, text='Select the complexity/readability analysis you wish to perform')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(),y_multiplier_integer,complexity_readability_analysis_lb,True)
complexity_readability_analysis_menu = tk.OptionMenu(window,complexity_readability_analysis_menu_var,'*','Sentence complexity','Text readability')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate()+400, y_multiplier_integer,complexity_readability_analysis_menu)

vocabulary_analysis_var.set(0)
vocabulary_analysis_checkbox = tk.Checkbutton(window, text='Vocabulary analysis', variable=vocabulary_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,vocabulary_analysis_checkbox,True)

vocabulary_analysis_menu_var.set('*')
vocabulary_analysis_lb = tk.Label(window, text='Select the vocabulary analysis you wish to perform')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(),y_multiplier_integer,vocabulary_analysis_lb,True)
vocabulary_analysis_menu = tk.OptionMenu(window,vocabulary_analysis_menu_var,'*',
                                         'Vocabulary (via unigrams) - List of all words/tokens in input document(s)',
                                         'Vocabulary (via Stanza multilanguage lemmatizer) - List of all words/tokens in input document(s)',
                                         'Vocabulary richness (word type/token ratio or Yule’s K)',
                                         'Abstract/concrete vocabulary',
                                         'Punctuation as figures of pathos (? !)',
                                         'Short words (<4 characters)',
                                         'Vowel words',
                                         'Words with capital initial (proper nouns)',
                                         'Unusual words (via NLTK)',
                                         'Language detection',
                                         'Repetition: Last N words of a sentence/First N words of next sentence',
                                         'Repetition across sentences (special ngrams)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate()+400, y_multiplier_integer,vocabulary_analysis_menu)

ngrams_analysis_var.set(0)
ngrams_analysis_checkbox = tk.Checkbutton(window, text='N-grams analysis', variable=ngrams_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,ngrams_analysis_checkbox,True)

ngrams_analysis_menu_var.set('*')
ngrams_lb = tk.Label(window, text='Select the n-grams analysis you wish to perform')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate(),y_multiplier_integer,ngrams_lb,True)
ngrams_analysis_menu = tk.OptionMenu(window,ngrams_analysis_menu_var,'*','Characters','Words','Hapax legomena (once-occurring words)','DEPREL','POSTAG','NER','Repetition of words (last N words of a sentence/first N words of next sentence)','Repetition of words across sentences (special ngrams)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate()+400, y_multiplier_integer,ngrams_analysis_menu)

gender_guesser_var.set(0)
gender_guesser_checkbox = tk.Checkbutton(window, text='Who wrote the text - Gender guesser', variable=gender_guesser_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,gender_guesser_checkbox)
gender_guesser_checkbox.configure(state='normal')

def activate_options(*args):
    if CoNLL_table_analysis_var.get()==True:
        # CoNLL_table_analysis_menu.configure(state='normal')
        nominalization_checkbox.configure(state='disabled')
        complexity_readability_analysis_checkbox.configure(state='disabled')
        vocabulary_analysis_checkbox.configure(state='disabled')
        ngrams_analysis_checkbox.configure(state='disabled')
        complexity_readability_analysis_menu.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
        ngrams_analysis_menu.configure(state='disabled')
        gender_guesser_checkbox.configure(state='disabled')
    elif nominalization_var.get()==True:
        CoNLL_table_analysis_checkbox.configure(state='disabled')
        complexity_readability_analysis_checkbox.configure(state='disabled')
        vocabulary_analysis_checkbox.configure(state='disabled')
        ngrams_analysis_checkbox.configure(state='disabled')
        complexity_readability_analysis_menu.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
        ngrams_analysis_menu.configure(state='disabled')
        gender_guesser_checkbox.configure(state='disabled')
    elif complexity_readability_analysis_var.get()==True:
        complexity_readability_analysis_menu.configure(state='normal')
        CoNLL_table_analysis_checkbox.configure(state='disabled')
        nominalization_checkbox.configure(state='disabled')
        vocabulary_analysis_checkbox.configure(state='disabled')
        ngrams_analysis_checkbox.configure(state='disabled')
        # CoNLL_table_analysis_menu.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
        ngrams_analysis_menu.configure(state='disabled')
        gender_guesser_checkbox.configure(state='disabled')
    elif vocabulary_analysis_var.get()==True:
        vocabulary_analysis_menu.configure(state='normal')
        CoNLL_table_analysis_checkbox.configure(state='disabled')
        nominalization_checkbox.configure(state='disabled')
        complexity_readability_analysis_checkbox.configure(state='disabled')
        ngrams_analysis_checkbox.configure(state='disabled')
        # CoNLL_table_analysis_menu.configure(state='disabled')
        complexity_readability_analysis_menu.configure(state='disabled')
        ngrams_analysis_menu.configure(state='disabled')
        gender_guesser_checkbox.configure(state='disabled')
    elif ngrams_analysis_var.get() == True:
        ngrams_analysis_menu.configure(state='normal')
        CoNLL_table_analysis_checkbox.configure(state='disabled')
        nominalization_checkbox.configure(state='disabled')
        complexity_readability_analysis_checkbox.configure(state='disabled')
        vocabulary_analysis_checkbox.configure(state='disabled')
        # CoNLL_table_analysis_menu.configure(state='disabled')
        complexity_readability_analysis_menu.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
        gender_guesser_checkbox.configure(state='disabled')
    elif gender_guesser_var.get() == True:
        ngrams_analysis_checkbox.configure(state='disabled')
        ngrams_analysis_menu.configure(state='disabled')
        CoNLL_table_analysis_checkbox.configure(state='disabled')
        nominalization_checkbox.configure(state='disabled')
        complexity_readability_analysis_checkbox.configure(state='disabled')
        vocabulary_analysis_checkbox.configure(state='disabled')
        # CoNLL_table_analysis_menu.configure(state='disabled')
        complexity_readability_analysis_menu.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
    else:
        CoNLL_table_analysis_checkbox.configure(state='normal')
        nominalization_checkbox.configure(state='normal')
        complexity_readability_analysis_checkbox.configure(state='normal')
        vocabulary_analysis_checkbox.configure(state='normal')
        ngrams_analysis_checkbox.configure(state='normal')
        gender_guesser_checkbox.configure(state='normal')

        # CoNLL_table_analysis_menu.configure(state='disabled')
        complexity_readability_analysis_menu.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
        ngrams_analysis_menu.configure(state='disabled')

CoNLL_table_analysis_var.trace('w',activate_options)
nominalization_var.trace('w',activate_options)
complexity_readability_analysis_var.trace('w',activate_options)
vocabulary_analysis_var.trace('w',activate_options)
ngrams_analysis_var.trace('w',activate_options)
gender_guesser_var.trace('w',activate_options)

activate_options()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Style analysis':'TIPS_NLP_Style analysis.pdf',
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',
               'Clause analysis':'TIPS_NLP_Clause analysis.pdf',
               'Sentence complexity':'TIPS_NLP_Sentence complexity.pdf',
               'Text readability':'TIPS_NLP_Text readability.pdf',
               'Nominalization':'TIPS_NLP_Nominalization.pdf',
               'CoNLL Table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",
               'POSTAG (Part of Speech Tags)': "TIPS_NLP_POSTAG (Part of Speech Tags) Stanford CoreNLP.pdf",
               'DEPREL (Stanford Dependency Relations)': "TIPS_NLP_DEPREL (Dependency Relations) Stanford CoreNLP.pdf",
               'NLP Searches': "TIPS_NLP_NLP Searches.pdf",
               'N-Grams (word & character)':"TIPS_NLP_Ngrams (word & character).pdf",
               'NLP Ngram and Word Co-Occurrence VIEWER':"TIPS_NLP_Ngram and Word Co-Occurrence VIEWER.pdf",
               'Google Ngram Viewer':'TIPS_NLP_Ngram Google Ngram Viewer.pdf',
               'Language concreteness':'TIPS_NLP_Language concreteness analysis.pdf',
               'Yule measures of vocabulary richness':'TIPS_NLP_Yule - Measures of vocabulary richness.pdf',
               'The world of emotions and sentiments':'TIPS_NLP_The world of emotions and sentiments.pdf',
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf'}

TIPS_options='Style analysis', 'English Language Benchmarks', 'Clause analysis', 'Sentence complexity', 'Text readability','Nominalization','CoNLL Table', 'POSTAG (Part of Speech Tags)', 'DEPREL (Stanford Dependency Relations)','NLP Searches','N-Grams (word & character)','NLP Ngram and Word Co-Occurrence VIEWER','Google Ngram Viewer','Language concreteness','Yule measures of vocabulary richness','The world of emotions and sentiments','Excel smoothing data series', 'csv files - Problems & solutions', 'Statistical measures'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_csv_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",'Please, tick the \'CoNLL table analysis\' checkbox if you wish to open the CoNLL table analyzer GUI to analyze various items in the CoNLL table, such as\n\n   1. Clause\n   2. Noun\n   3. Verb\n   4. Function words\n   5. DEPREL\n   6. POSTAG\n   7. NER\n\nYou will also be able to run specialized functions such as\n\n   1. CoNLL table searches\n   2. K sentences analyszer')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",'Please, tick the \'Nominalization\' checkbox if you wish to open the Nominalization GUI to analyze instances of nominalization (i.e., turning verbs into nouns - Latin nomen=noun).')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",'Please, tick the \'Complex\\readability analysis\' checkbox if you wish to analyze the complexity or readability of sentences and documents.\n\nUse the dropdown menu to select the type of analysis to run.\n\n   1. Sentence complexity to provide different measures of sentence complexity: Yngve Depth, Frazer Depth, and Frazer Sum. These measures are closely associated to the sentence clause structure. The Frazier and Yngve scores are very similar, with one key difference: while the Frazier score measures the depth of a syntactic tree, the Yngve score measures the breadth of the tree.\n\n   2. Text readability to compute various measures of text readability.\n 12 readability score requires HIGHSCHOOL education;\n 16 readability score requires COLLEGE education;\n 18 readability score requires MASTER education;\n 24 readability score requires DOCTORAL education;\n >24 readability score requires POSTDOC education.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",'Please, tick the \'Vocabulary analysis\' checkbox if you wish to analyze the vocabulary used in your corpus.\n\nUse the dropdown menu to select the type of analysis to run.\n\n   1. Abstract/concrete vocabulary, The script uses the concreteness ratings by Brysbaert, Warriner, Kuperman, Concreteness Ratings for 40 Thousand Generally Known English Word Lemmas, Behavioral Research (2014) 46:904–911.\nMean/median Concreteness values are calculated for each sentence on a 5-point scale going from abstract (0) to concrete (5).\n\n   2. Vocabulary richness (word type/token ratio or Yule’s K). C.U. Yule. 1944. The statistical study of literary vocabulary. Cambridge: Cambridge University Press.\n\n   3. Short words to compute the number of short words (<4 characters) and list them.\n\n   4. Vowel words to compute the number of words that start with a vowel (vowel words) and list them.\n\n   5. Unusual, or misspelled, words (via NLTK).\n\n   6. Language detection. Language detection is carried out via LANGDETECT, LANGID, SPACY. Languages are exported via the ISO 639 two-letter code. ISO 639 is a standardized nomenclature used to classify languages (check here for the list https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).\nAll language detection algorithms, except for Stanza, export the probability of detection of a specific detected language.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",'Please, tick the \'N-grams analysis\' checkbox if you wish to compute various types of n-grams.\n\nUse the dropdown menu to select the type of analysis to run.\n\n   1. Characters\n   2. Words\n   3. Hapax legomena (once-occurring words)\n   4. DEPREL\n   5. POSTAG\n   6. NER.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",'Please, tick the \'Who wrote the text\' checkbox if you wish to run the Gender Guesser algorithm to determine an author\'s gender based on the words used.\n\nYou will need to copy and paste a document content to the website http://www.hackerfactor.com/GenderGuesser.php#About\n\nYou need to be connected to the internet.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),0)

# change the value of the readMe_message
readMe_message="The Python 3 scripts analyze different aspects of style, from the analysis of CoNLL table tags (POSTAG, DEPREL, NER), to sentence complexity and readability, vocabulary analysis (short and vowel words, abstract/concrete words, unusual words, vocabulary richness (Yule\'s K)), N-grams." + GUI_IO_util.msg_multipleDocsCoNLL
readMe_command = lambda: GUI_IO_util.display_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()

