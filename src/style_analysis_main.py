# written by Roberto Franzosi (Spring/summer 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"style_analysis_main.py",['os','csv','tkinter','ntpath','collections','subprocess'])==False:
    sys.exit(0)

import os
import tkinter.messagebox as mb
import tkinter as tk
from subprocess import call

import GUI_IO_util
import IO_files_util
import file_spell_checker_util
import statistics_txt_util
import abstract_concreteness_analysis_util
import Stanza_util
import reminders_util
import config_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir, openOutputFiles,createCharts,chartPackage,
    ngrams_analysis_var,
    ngrams_menu_var,
    ngrams_options_menu_var,
    corpus_statistics_var,
    corpus_statistics_options_menu_var,
    corpus_text_options_menu_var,
    complexity_readability_analysis_var,
    complexity_readability_analysis_menu_var,
    vocabulary_analysis_var,
    vocabulary_analysis_menu_var,
    gender_guesser_var):

    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    else:
        config_filename = scriptName.replace('_main.py', '_config.csv')

    filesToOpen = []  # Store all files that are to be opened once finished

    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]

    # get the date options from filename
    filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = config_util.get_date_options(
        config_filename, config_input_output_numeric_options)
    extract_date_from_text_var = 0

    if package_display_area_value == '':
        mb.showwarning(title='No setup for NLP package and language',
                       message="The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again.")
        return

    openOutputFilesSV=openOutputFiles
    outputDir_style=outputDir

    if (corpus_statistics_var==False and
        ngrams_analysis_var == False and
        complexity_readability_analysis_var == False and
        vocabulary_analysis_var == False and
        gender_guesser_var==False):
        mb.showwarning('Warning','No options have been selected.\n\nPlease, select an option and try again.')
        return

    # COMPUTE Ngrams ______________________________________________________________________________

    if ngrams_analysis_var:
        ngrams_word_var = False
        ngrams_character_var = False
        normalize = False
        case_sensitive = False
        ngrams_size = 3  # default number of ngrams
        excludePunctuation = False
        excludeDeterminants = False
        excludeStopwords = False
        bySentenceIndex_word_var = False
        bySentenceIndex_character_var = False
        if ngrams_menu_var == "Word":
            ngrams_word_var = True
        else:
            ngrams_character_var = True
        bySentenceIndex_character_var = False
        if 'Hapax' in str(ngrams_list):
            ngrams_size = 1
            frequency = 1
        else:
            frequency = None
        if 'punctuation' in str(ngrams_list):
            excludePunctuation = True
        if 'determinants' in str(ngrams_list):
            excludeDeterminants = True
        if 'stopwords' in str(ngrams_list):
            excludeStopwords = True
        if 'sentence index' in str(ngrams_list):
            if ngrams_menu_var == "Word":
                bySentenceIndex_word_var = True
            else:
                bySentenceIndex_character_var = True

        if '*' in str(ngrams_list) or 'POSTAG' in ngrams_menu_var or 'DEPREL' in str(ngrams_list) or 'NER' in str(ngrams_list):
            mb.showwarning('Warning', 'The selected option is not available yet.\n\nSorry!')
            if 'Repetition' in ngrams_menu_var:
                mb.showwarning('Warning',
                               'Do check out the repetition finder algorithm in the CoNLL Table Analyzer GUI.')
            return

        if ngrams_word_var or ngrams_character_var or bySentenceIndex_word_var or bySentenceIndex_character_var:
            if IO_libraries_util.check_inputPythonJavaProgramFile('statistics_txt_util.py') == False:
                return

        # word n-grams
        if ngrams_word_var or bySentenceIndex_word_var:
            outputFiles = statistics_txt_util.compute_character_word_ngrams(GUI_util.window, inputFilename, inputDir,
                                                              outputDir, config_filename,
                                                              ngrams_size, normalize,
                                                              excludePunctuation, excludeDeterminants, excludeStopwords, 1, 0, openOutputFiles,
                                                              createCharts, chartPackage,

                                                              bySentenceIndex_word_var)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        # character n-grams
        if ngrams_character_var or bySentenceIndex_character_var:
            statistics_txt_util.compute_character_word_ngrams(GUI_util.window, inputFilename, inputDir,
                                                              outputDir, config_filename,
                                                              ngrams_size, normalize,
                                                              excludePunctuation, 0, 0, openOutputFiles,
                                                              createCharts, chartPackage,
                                                              bySentenceIndex_character_var)

# corpus statistics --------------------------------------------------------------------

    if corpus_statistics_var:
        stopwords_var = False
        lemmatize_var = False
        if corpus_text_options_menu_var=='*':
            stopwords_var=True
            lemmatize_var=True
        if 'Lemmatize' in corpus_text_options_menu_var:
            lemmatize_var=True
        if 'stopwords' in corpus_text_options_menu_var:
            stopwords_var=True
        if "*" in corpus_statistics_options_menu_var or 'frequencies' in corpus_statistics_options_menu_var:
            outputFiles=statistics_txt_util.compute_corpus_statistics(window,inputFilename,inputDir,outputDir,config_filename,False,createCharts, chartPackage, stopwords_var, lemmatize_var)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)
        if "Compute sentence length" in corpus_statistics_options_menu_var or "*" in corpus_statistics_options_menu_var:
            outputFiles = statistics_txt_util.compute_sentence_length(inputFilename, inputDir, outputDir, config_filename, createCharts, chartPackage)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if "Compute line length" in corpus_statistics_options_menu_var or "*" in corpus_statistics_options_menu_var:
            outputFiles=statistics_txt_util.compute_line_length(window, config_filename, inputFilename, inputDir, outputDir,
                                                          False, createCharts, chartPackage)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

# complexity_readability    ---------------------------------------------------------------------

    if complexity_readability_analysis_var == True:
        if '*' in complexity_readability_analysis_menu_var or 'Sentence' in complexity_readability_analysis_menu_var:
            if IO_libraries_util.check_inputPythonJavaProgramFile('statistics_txt_util.py') == False:
                return
            filesToOpen = statistics_txt_util.compute_sentence_complexity(GUI_util.window, inputFilename,
                                                                     inputDir, outputDir, config_filename,
                                                                     openOutputFiles, createCharts, chartPackage)
        if '*' in complexity_readability_analysis_menu_var or 'Text' in complexity_readability_analysis_menu_var:
            if IO_libraries_util.check_inputPythonJavaProgramFile('statistics_txt_util.py') == False:
                return
            statistics_txt_util.compute_sentence_text_readability(GUI_util.window, inputFilename, inputDir,
                                                             outputDir, config_filename,
                                                             openOutputFiles, createCharts, chartPackage)

        if complexity_readability_analysis_menu_var=='':
            mb.showwarning('Warning', 'No option has been selected for Complexity/readability analysis.\n\nPlease, select an option from the dropdown menu and try again.')
            return

# vocabulary analysis    ---------------------------------------------------------------------

    if vocabulary_analysis_var == True:
        openOutputFilesSV=openOutputFiles
        openOutputFiles = False  # to make sure files are only opened at the end of this multi-tool script
        if vocabulary_analysis_menu_var=='':
            mb.showwarning('Warning', 'No option has been selected for Vocabulary analysis.\n\nPlease, select an option and try again.')
            return
        if 'Repetition across' in vocabulary_analysis_menu_var:
            mb.showwarning('Warning', 'The selected option is not available yet.\n\nSorry!')
            return

        if '*' == vocabulary_analysis_menu_var:
            outputDir_style = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                                   label='style',
                                                                   silent=True)
            if outputDir_style == '':
                return
        else:
            outputDir_style=outputDir

        if '*' in vocabulary_analysis_menu_var or 'Vocabulary (via unigrams)' in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                                   openOutputFiles, createCharts, chartPackage,'unigrams',language)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Hapax legomena' in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                                   openOutputFiles, createCharts, chartPackage,'Hapax legomena', language)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        #Added this option to be able to test the subjectivity/objectivity output (Naman Sahni 10/01/2022)
        if '*' in vocabulary_analysis_menu_var or 'Objectivity/subjectivity (via spaCy)' in vocabulary_analysis_menu_var:
            if '*' in vocabulary_analysis_menu_var:
                silent=True
            else:
                silent=False
            import spaCy_util
            # annotator_available = spaCy_util.check_spaCy_annotator_availability(['Objectivity/subjectivity'], language,
            #                                                                     silent)
            annotator_available=True
            if annotator_available:
                outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                            openOutputFiles, createCharts,
                                                            chartPackage,'Objectivity/subjectivity (via spaCy)', language)
                if outputFiles!=None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Repetition: Words' in vocabulary_analysis_menu_var:
            if '*' in vocabulary_analysis_menu_var:
                # this will force a deafault setting of k_str = '4' to avoid stopping all algorithms
                process='*Repetition: Words in first K and last K sentences'
            else:
                process = 'Repetition: Words in first K and last K sentences'
            # a reminder about CoNLL table analyzer option is posted in process_words
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                       openOutputFiles, createCharts,
                                                       chartPackage,process,language)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Repetition: Last' in vocabulary_analysis_menu_var:
            if '*' in vocabulary_analysis_menu_var:
                # this will force a deafault setting of k_str = '4' to avoid stopping all algorithms
                process='*Repetition: Last K words of a sentence/First K words of next sentence'
            else:
                process = 'Repetition: Last K words of a sentence/First K words of next sentence'
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                       openOutputFiles, createCharts,
                                                       chartPackage, process, language)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Stanza' in vocabulary_analysis_menu_var:
            annotator = 'Lemma'
            language_list = ['English']
            memory_var = 8
            document_length_var = 1
            limit_sentence_length_var = 1000
            outputFiles = Stanza_util.Stanza_annotate(config_filename, inputFilename, inputDir,
                                                          outputDir,
                                                          openOutputFiles,
                                                          createCharts, chartPackage,
                                                          annotator, False,
                                                          language_list,
                                                          memory_var, document_length_var, limit_sentence_length_var)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'capital' in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                                   openOutputFiles, createCharts, chartPackage,'capital')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Word length' in vocabulary_analysis_menu_var:
            outputFiles =statistics_txt_util.process_words(window, config_filename, inputFilename,inputDir, outputDir_style,
                                                      openOutputFiles, createCharts, chartPackage,'Word length')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Vowel' in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                       openOutputFiles, createCharts, chartPackage,'Vowel')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Punctuation' in vocabulary_analysis_menu_var:
            outputFiles =statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                      openOutputFiles, createCharts, chartPackage,'Punctuation')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' == vocabulary_analysis_menu_var or 'Unusual' in vocabulary_analysis_menu_var:
            outputFiles =file_spell_checker_util.nltk_unusual_words(window, inputFilename, inputDir, outputDir_style, config_filename, False, createCharts, chartPackage)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' == vocabulary_analysis_menu_var or 'Abstract' in vocabulary_analysis_menu_var:
            if language == 'English':
                mode = "both" # mean, median, both (calculates both mean and median)
                outputFiles = abstract_concreteness_analysis_util.main(GUI_util.window, inputFilename, inputDir, outputDir_style, config_filename, openOutputFiles, createCharts, chartPackage, processType='')
                if outputFiles!=None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)
            else:
                if not '*' == vocabulary_analysis_menu_var:
                    mb.showwarning(title='Warning', message='The Abstract/concrete vocabulary algorithm is only available for the English language.')

        if '*' == vocabulary_analysis_menu_var or 'Yule' in vocabulary_analysis_menu_var:
            outputFiles =statistics_txt_util.yule(window, inputFilename, inputDir, outputDir, config_filename)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'detection' in vocabulary_analysis_menu_var:
                outputFiles = file_spell_checker_util.language_detection(window, inputFilename, inputDir, outputDir_style, config_filename,
                                                                         openOutputFiles, createCharts, chartPackage)
                if outputFiles!=None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)

    if gender_guesser_var==True:
        mb.showwarning('Warning',
                       'When the Gender Guesser (Hacker Factor) webpage opens, make sure to read carefully the page content in order to understand:\n1. how this sophisticated neural network Java tool can guess the gender identity of a text writer (male or female);\n2. the difference between formal and informal text genre;\n3. the meaning of the gender estimate as "Weak emphasis could indicate European";\n4. the limits of the algorithms (about 60-70% accuraracy).\n\nYou can also read Argamon, Shlomo, Moshe Koppel, Jonathan Fine, and Anat Rachel Shimoni. 2003. "Gender, Genre, and Writing Style in Formal Written Texts," Text, Vol. 23, No. 3, pp. 321–346.')
        IO_files_util.runScript_fromMenu_option('Gender guesser', 0, inputFilename, inputDir, outputDir,
                                  openOutputFiles, createCharts, chartPackage)
        return

    openOutputFiles=openOutputFilesSV
    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir_style, scriptName)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_chart_output_checkbox.get(),
                                GUI_util.charts_package_options_widget.get(),
                                ngrams_analysis_var.get(),
                                ngrams_menu_var.get(),
                                ngrams_options_menu_var.get(),
                                corpus_statistics_var.get(),
                                corpus_statistics_options_menu_var.get(),
                                corpus_text_options_menu_var.get(),
                                complexity_readability_analysis_var.get(),
                                complexity_readability_analysis_menu_var.get(),
                                vocabulary_analysis_var.get(),
                                vocabulary_analysis_menu_var.get(),
                                gender_guesser_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=640, # height at brief display
                             GUI_height_full=680, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=1, # to be added for full display
                             increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Style Analysis'
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
config_input_output_numeric_options=[6,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename,config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

def clear(e):
    ngrams_checkbox.configure(state='normal')
    corpus_statistics_checkbox.configure(state='normal')
    complexity_readability_analysis_checkbox.configure(state='normal')
    vocabulary_analysis_checkbox.configure(state='normal')

    ngrams_analysis_var.set(0)
    corpus_statistics_var.set(0)
    complexity_readability_analysis_var.set(0)
    vocabulary_analysis_var.set(0)

    ngrams_options_menu_var.set('')
    corpus_statistics_options_menu_var.set('')
    corpus_text_options_menu_var.set('')
    complexity_readability_analysis_menu_var.set('')
    vocabulary_analysis_menu_var.set('')

    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

# GUI CHANGES cut/paste special GUI widgets from GUI_util

ngrams_list=[]
ngrams_analysis_var= tk.IntVar()
ngrams_menu_var= tk.StringVar()
ngrams_options_menu_var= tk.StringVar()

bySentenceIndex_var=tk.IntVar()

complexity_readability_analysis_var=tk.IntVar()
vocabulary_analysis_var=tk.IntVar()
gender_guesser_var=tk.IntVar()

# CoNLL_table_analysis_menu_var=tk.StringVar()
complexity_readability_analysis_menu_var=tk.StringVar()
vocabulary_analysis_menu_var=tk.StringVar()
ngrams_menu_var=tk.StringVar()

corpus_statistics_var = tk.IntVar()
corpus_statistics_options_menu_var = tk.StringVar()
corpus_text_options_menu_var = tk.StringVar()

CoNLL_table_analysis_button = tk.Button(window, width=GUI_IO_util.widget_width_short, text='CoNLL table analysis (Open GUI)',command=lambda: call('python CoNLL_table_analyzer_main.py', shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   CoNLL_table_analysis_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

ngrams_button = tk.Button(window, width=GUI_IO_util.widget_width_short, text='N-Grams/Co-occurrences VIEWER (Open GUI)',command=lambda: call('python NGrams_CoOccurrences_Viewer_main.py', shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   ngrams_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

nominalization_button = tk.Button(window, width=GUI_IO_util.widget_width_short, text='Nominalization (Open GUI)',command=lambda: call('python nominalization_main.py', shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   nominalization_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

spell_checker_button = tk.Button(window, width=GUI_IO_util.widget_width_short, text='Spelling/grammar checker (Open GUI)',command=lambda: call('python file_spell_checker_main.py', shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   spell_checker_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

ngrams_analysis_var.set(0)
ngrams_checkbox = tk.Checkbutton(window, text='Compute n-grams', variable=ngrams_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,ngrams_checkbox,True)

ngrams_menu_var.set('Word')
# ngrams_menu_lb = tk.Label(window, text='N-grams type')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.style_ngrams_menu_pos,y_multiplier_integer,ngrams_menu_lb,True)
ngrams_menu = tk.OptionMenu(window, ngrams_menu_var, 'Character', 'Word') #,'DEPREL','POSTAG')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   ngrams_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select the N-grams type")

ngrams_options_menu_lb = tk.Label(window, text='N-grams options')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,ngrams_options_menu_lb,True)
ngrams_options_menu = tk.OptionMenu(window, ngrams_options_menu_var, 'Hapax legomena (once-occurring words/unigrams)','Normalize n-grams', 'Exclude punctuation (word n-grams only)','Exclude determinants/articles (word n-grams only)','Exclude ALL stopwords (word n-grams only)','By sentence index','Repetition of words (last K words of a sentence/first N words of next sentence)','Repetition of words across sentences (special ngrams)')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   ngrams_options_menu,
                                   True, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select the N-grams option; hit + button to add multiple options; Reset to start fresh; Show to display current selection.")

add_ngrams_button = tk.Button(window, text='+', width=GUI_IO_util.add_button_width,height=1,state='disabled',command=lambda: activate_ngrams_analysis_var())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.style_add_ngrams_button_pos,y_multiplier_integer,add_ngrams_button, True)

reset_ngrams_button = tk.Button(window, text='Reset ', width=GUI_IO_util.reset_button_width,height=1,state='disabled',command=lambda: reset_ngrams_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.style_reset_ngrams_button_pos,y_multiplier_integer,reset_ngrams_button,True)

show_ngrams_button = tk.Button(window, text='Show', width=GUI_IO_util.show_button_width,height=1,state='disabled',command=lambda: show_ngrams_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.style_show_ngrams_button_pos,y_multiplier_integer,show_ngrams_button)

def reset_ngrams_list():
    ngrams_list.clear()
    ngrams_options_menu_var.set('')
    ngrams_options_menu.configure(state='normal')

def show_ngrams_list():
    if len(ngrams_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected n-grams options.')
    else:
        mb.showwarning(title='Warning', message='The currently selected n-grams options are:\n\n' + ',\n'.join(ngrams_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

def activate_ngrams_analysis_var():
    # Disable the + after clicking on it and enable the class menu
    add_ngrams_button.configure(state='disabled')
    ngrams_options_menu.configure(state='normal')

def activate_ngrams_options(*args):
    if ngrams_options_menu_var.get()!='':
        if ngrams_options_menu_var.get() in ngrams_list:
            mb.showwarning(title='Warning', message='The option has already been selected. Selection ignored.\n\nYou can see your current selections by clicking the Show button.')
            return
        ngrams_list.append(ngrams_options_menu_var.get())
        ngrams_options_menu.configure(state="disabled")
        add_ngrams_button.configure(state='normal')
        reset_ngrams_button.configure(state='normal')
        show_ngrams_button.configure(state='normal')
    else:
        add_ngrams_button.configure(state='disabled')
        reset_ngrams_button.configure(state='disabled')
        show_ngrams_button.configure(state='disabled')
        ngrams_options_menu.configure(state="normal")
ngrams_options_menu_var.trace('w',activate_ngrams_options)

corpus_statistics_var.set(0)
corpus_statistics_checkbox = tk.Checkbutton(window,text="Compute document(s) statistics", variable=corpus_statistics_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,corpus_statistics_checkbox,True)

corpus_statistics_options_menu_var.set('*')
# corpus_statistics_options_menu_lb = tk.Label(window, text='Statistics options')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,y_multiplier_integer,corpus_statistics_options_menu_lb,True)

corpus_statistics_options_menu = tk.OptionMenu(window,corpus_statistics_options_menu_var,
                                                '*',
                                               'Compute frequencies of sentences, words, syllables, and top-20 words',
                                               'Compute sentence length',
                                               'Compute line length',
                                               )
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   corpus_statistics_options_menu,
                                   True, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select the statistics option for your document(s) (* for all); widget disabled until checkbox ticked.")

# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.style_corpus_statistics_options_menu_pos,y_multiplier_integer,corpus_statistics_options_menu, True)

corpus_text_options_menu_var.set('')
corpus_options_menu_lb = tk.Label(window, text='Text options')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.style_corpus_text_options_menu_lb_pos,y_multiplier_integer,corpus_options_menu_lb,True)
corpus_text_options_menu = tk.OptionMenu(window, corpus_text_options_menu_var, '*','Lemmatize words', 'Exclude stopwords & punctuation')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.style_corpus_options_menu_men_pos,y_multiplier_integer,corpus_text_options_menu)

def activate_corpus_options(*args):
    if corpus_statistics_var.get()==True:
        corpus_statistics_options_menu.configure(state='normal')
        corpus_text_options_menu.configure(state='normal')
    else:
        corpus_statistics_options_menu.configure(state='disabled')
        corpus_text_options_menu.configure(state='disabled')
corpus_statistics_var.trace('w',activate_corpus_options)

complexity_readability_analysis_var.set(0)
complexity_readability_analysis_checkbox = tk.Checkbutton(window, text='Complexity/readability analysis', variable=complexity_readability_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,complexity_readability_analysis_checkbox,True)

complexity_readability_analysis_menu_var.set('*')
# complexity_readability_analysis_lb = tk.Label(window, text='Select the complexity/readability analysis you wish to perform')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,y_multiplier_integer,complexity_readability_analysis_lb,True)
complexity_readability_analysis_menu = tk.OptionMenu(window,complexity_readability_analysis_menu_var,'*','Sentence complexity','Text readability')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   complexity_readability_analysis_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select the complexity/readability analysis you wish to perform (* for all); widget disabled until checkbox ticked.")
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.style_complexity_readability_analysis_menu_pos, y_multiplier_integer,complexity_readability_analysis_menu)

vocabulary_analysis_var.set(0)
vocabulary_analysis_checkbox = tk.Checkbutton(window, text='Vocabulary analysis', variable=vocabulary_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,vocabulary_analysis_checkbox,True)

# # vocabulary_analysis_menu_var.set('*')
# # vocabulary_analysis_lb = tk.Label(window, text='Select the vocabulary analysis you wish to perform')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,y_multiplier_integer,vocabulary_analysis_lb,True)
vocabulary_analysis_menu = tk.OptionMenu(window,vocabulary_analysis_menu_var,'*',
                                         'Vocabulary (via unigrams) - List of all words/tokens in input document(s)',
                                         'Vocabulary (via Stanza multilanguage lemmatizer) - List of all words/tokens in input document(s)',
                                         'Vocabulary richness (word type/token ratio or Yule’s K)',
                                         'Abstract/concrete vocabulary',
                                         'Objectivity/subjectivity (via spaCy)',
                                         'Punctuation as figures of pathos (? !)',
                                         'Word length',
                                         'Vowel words',
                                         'Words with capital initial (proper nouns)',
                                         'Unusual words (via NLTK)',
                                         'Hapax legomena (once-occurring words/unigrams)',
                                         'Language detection',
                                         'Repetition: Words in first K and last K sentences',
                                         'Repetition: Last K words of a sentence/First K words of next sentence',
                                         'Repetition across sentences (special ngrams)')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   vocabulary_analysis_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select the vocabulary analysis you wish to perform (* for all); widget disabled until checkbox ticked,")
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.style_vocabulary_analysis_menu_pos, y_multiplier_integer,vocabulary_analysis_menu)

gender_guesser_var.set(0)
gender_guesser_checkbox = tk.Checkbutton(window, text='Who wrote the text - Gender guesser', variable=gender_guesser_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,gender_guesser_checkbox)
gender_guesser_checkbox.configure(state='normal')

def activate_options(*args):
    if ngrams_analysis_var.get() == True:
        corpus_statistics_checkbox.configure(state='disabled')
        corpus_statistics_options_menu.configure(state='disabled')
        complexity_readability_analysis_checkbox.configure(state='disabled')
        vocabulary_analysis_checkbox.configure(state='disabled')
        complexity_readability_analysis_menu.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
        gender_guesser_checkbox.configure(state='disabled')
    elif corpus_statistics_var.get() == True:
        ngrams_checkbox.configure(state='disabled')
        corpus_statistics_options_menu.configure(state='normal')
        complexity_readability_analysis_checkbox.configure(state='disabled')
        vocabulary_analysis_checkbox.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
        gender_guesser_checkbox.configure(state='disabled')
    elif complexity_readability_analysis_var.get()==True:
        ngrams_checkbox.configure(state='disabled')
        corpus_statistics_checkbox.configure(state='disabled')
        corpus_statistics_options_menu.configure(state='disabled')
        complexity_readability_analysis_menu.configure(state='normal')
        vocabulary_analysis_checkbox.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
        gender_guesser_checkbox.configure(state='disabled')
    elif vocabulary_analysis_var.get()==True:
        ngrams_checkbox.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='normal')
        corpus_statistics_checkbox.configure(state='disabled')
        corpus_statistics_options_menu.configure(state='disabled')
        complexity_readability_analysis_checkbox.configure(state='disabled')
        complexity_readability_analysis_menu.configure(state='disabled')
        gender_guesser_checkbox.configure(state='disabled')
    elif gender_guesser_var.get() == True:
        ngrams_checkbox.configure(state='disabled')
        corpus_statistics_checkbox.configure(state='disabled')
        corpus_statistics_options_menu.configure(state='disabled')
        complexity_readability_analysis_checkbox.configure(state='disabled')
        vocabulary_analysis_checkbox.configure(state='disabled')
        complexity_readability_analysis_menu.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
    else:
        ngrams_checkbox.configure(state='normal')
        corpus_statistics_checkbox.configure(state='normal')
        corpus_statistics_options_menu.configure(state='disabled')
        complexity_readability_analysis_checkbox.configure(state='normal')
        vocabulary_analysis_checkbox.configure(state='normal')
        vocabulary_analysis_menu_var.set('*')
        gender_guesser_checkbox.configure(state='normal')
        complexity_readability_analysis_menu.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')

ngrams_analysis_var.trace('w',activate_options)
corpus_statistics_var.trace('w',activate_options)
complexity_readability_analysis_var.trace('w',activate_options)
vocabulary_analysis_var.trace('w',activate_options)
gender_guesser_var.trace('w',activate_options)

activate_options()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Style analysis':'TIPS_NLP_Style analysis.pdf',
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',
               'Things to do with words: Overall view': 'TIPS_NLP_Things to do with words Overall view.pdf',
               'Clause analysis':'TIPS_NLP_Clause analysis.pdf',
               'Sentence complexity':'TIPS_NLP_Sentence complexity.pdf',
               'Text readability':'TIPS_NLP_Text readability.pdf',
               'Objective/subjective writing':'TIPS_NLP_Objectivity_subjectivity (via spaCy and TextBlob).pdf',
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

TIPS_options='Style analysis', 'English Language Benchmarks','Things to do with words: Overall view', 'Clause analysis', 'Sentence complexity', 'Text readability', \
             'Objective/subjective writing','Nominalization','CoNLL Table', 'POSTAG (Part of Speech Tags)', 'DEPREL (Stanford Dependency Relations)','NLP Searches','N-Grams (word & character)','NLP Ngram and Word Co-Occurrence VIEWER','Google Ngram Viewer','Language concreteness','Yule measures of vocabulary richness','The world of emotions and sentiments','Excel smoothing data series', 'csv files - Problems & solutions', 'Statistical measures'

# add all the lines to the end to every special GUI
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

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         'Please, click the button \'CoNLL table analysis\' if you wish to open the CoNLL table analyzer GUI to analyze various items in the CoNLL table, such as\n\n   1. Clause\n   2. Noun\n   3. Verb\n   4. Function words\n   5. DEPREL\n   6. POSTAG\n   7. NER\n\nYou will also be able to run specialized functions such as\n\n   1. CoNLL table searches\n   2. K sentences analyzer')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         'Please, click the button \'N-Grams\' if you wish to open the N-Grams GUI to analyze n-grams (1, 2, 3) present in your corpus.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         'Please, click the button \'Nominalization\' if you wish to open the Nominalization GUI to analyze instances of nominalization (i.e., turning verbs into nouns - Latin nomen=noun).')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         'Please, click the button \'Spelling/grammar checker\' if you wish to open the Spelling/grammar checker GUI to check your corpus for spelling and/or grammar errors with several different NLP tools.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                'Please, tick the checkbox if you wish to compute N-grams.\n\nN-grams can be computed for character and word values. Use the dropdown menu to select the desired option.\n\nIn INPUT the script expects a single txt file or a directory containing a set of txt files.\n\nIn OUTPUT, the script generates a set of csv files each containing word n-grams between 1 and 3.\n\nWhen n-grams are computed by sentence index, the sentence displayed in output is always the first occurring sentence.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  'Please, use the dropdown menu to select different options for N-grams. Clisk the + button to select more options; the Reset button to start fresh; the Show button to visualize the options already selected.\n\nIn INPUT the script expects a single txt file or a directory containing a set of txt files.\n\nIn OUTPUT, the script generates the following three files:\n  1. csv file of frequencies of the twenty most frequent words;\n  2. csv file of the following statistics for each column in the previous csv file and for each document in the corpus: Count, Mean, Mode, Median, Standard deviation, Minimum, Maximum, Skewness, Kurtosis, 25% quantile, 50% quantile; 75% quantile;\n  3. Excel line chart of the number of sentences and words for each document.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                'Please, tick the checkbox if you wish to compute basic statistics on your corpus.\n\nUse the dropdown menu to select the desired option. Use the Text options dropdown menu to lemmatize words or exclude stopwords/punctuation.\n\nIn INPUT the script expects a single txt file or a directory containing a set of txt files.\n\nIn OUTPUT, the script generates a set of csv files each containing word n-grams between 1 and 3.\n\nWhen n-grams are computed by sentence index, the sentence displayed in output is always the first occurring sentence.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         'Please, tick the \'Complexlexity\readability analysis\' checkbox if you wish to analyze the complexity or readability of sentences and documents.\n\nUse the dropdown menu to select the type of analysis to run.\n\n   1. Sentence complexity to provide different measures of sentence complexity: Yngve Depth, Frazer Depth, and Frazer Sum. These measures are closely associated to the sentence clause structure. The Frazier and Yngve scores are very similar, with one key difference: while the Frazier score measures the depth of a syntactic tree, the Yngve score measures the breadth of the tree.\n\nTHE SENTENCE COMPLEXITY ALGORITHM IS BASED ON STANZA.\n\n   2. Text readability to compute various measures of text readability.\n 12 readability score requires HIGHSCHOOL education;\n 16 readability score requires COLLEGE education;\n 18 readability score requires MASTER education;\n 24 readability score requires DOCTORAL education;\n >24 readability score requires POSTDOC education.\n\nTHE TEXT READABILITY ALGORITHM IS BASED ON TEXSTAT.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         'Please, tick the \'Vocabulary analysis\' checkbox if you wish to analyze the vocabulary used in your corpus.\n\nUse the dropdown menu to select the type of analysis to run.\n\n   1. Abstract/concrete vocabulary, The script uses the concreteness ratings by Brysbaert, Warriner, Kuperman, Concreteness Ratings for 40 Thousand Generally Known English Word Lemmas, Behavioral Research (2014) 46:904–911.\nMean/median Concreteness values are calculated for each sentence on a 5-point scale going from abstract (0) to concrete (5).\n\n   2. Vocabulary richness (word type/token ratio or Yule’s K). C.U. Yule. 1944. The statistical study of literary vocabulary. Cambridge: Cambridge University Press. The larger Yule K, the smaller the diversity of the vocabulary (and thus, arguably, the easier the text).\n\n   3. Word length to compute the number of characters per word and list the words.\n\n   4. Vowel words to compute the number of words that start with a vowel (vowel words) and list them.\n\n   5. Unusual, or misspelled, words (via NLTK).\n\n   6. Language detection. Language detection is carried out via LANGDETECT, LANGID, SPACY. Languages are exported via the ISO 639 two-letter code. ISO 639 is a standardized nomenclature used to classify languages (check here for the list https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).\nAll language detection algorithms, except for Stanza, export the probability of detection of a specific detected language.')
    # y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",'Please, tick the \'N-grams analysis\' checkbox if you wish to compute various types of n-grams.\n\nUse the dropdown menu to select the type of analysis to run.\n\n   1. Characters\n   2. Words\n   3. Hapax legomena (once-occurring words)\n   4. DEPREL\n   5. POSTAG\n   6. NER.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",'Please, tick the \'Who wrote the text\' checkbox if you wish to run the Gender Guesser algorithm to determine an author\'s gender based on the words used.\n\nYou will need to copy and paste a document content to the website http://www.hackerfactor.com/GenderGuesser.php#About\n\nYou need to be connected to the internet.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 scripts analyze different aspects of style, from the analysis of CoNLL table tags (POSTAG, DEPREL, NER), to sentence complexity and readability, vocabulary analysis (word length and vowel words, abstract/concrete words, unusual words, vocabulary richness (Yule\'s K)), N-grams."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command,
                    videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

def activate_NLP_options(*args):
    global error, package_basics, package, language, language_var, language_list
    error, package, parsers, package_basics, language, package_display_area_value_new, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]
GUI_util.setup_menu.trace('w', activate_NLP_options)
activate_NLP_options()

if error:
    mb.showwarning(title='Warning',
               message="The config file 'NLP_default_package_language_config.csv' could not be found in the sub-directory 'config' of your main NLP Suite folder.\n\nPlease, setup next the default NLP package and language options.")
    call("python NLP_setup_package_language_main.py", shell=True)
    # this will display the correct hover-over info after the python call, in case options were changed
    error, package, parsers, package_basics, language, package_display_area_value_new, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()

title = ["NLP setup options"]
message = "Some of the algorithms behind this GUI rely on a specific NLP package to carry out basic NLP functions (e.g., sentence splitting, tokenizing, lemmatizing) for a specific language your corpus is written in.\n\nYour selected corpus language is " \
          + str(language) + ".\nYour selected NLP package for basic functions (e.g., sentence splitting, tokenizing, lemmatizing) is " \
          + str(package_basics) + ".\n\nYou can always view your default selection saved in the config file NLP_default_package_language_config.csv by hovering over the Setup widget at the bottom of this GUI and change your default options by selecting Setup NLP package and corpus language."
reminders_util.checkReminder(scriptName, title, message)

GUI_util.window.mainloop()

