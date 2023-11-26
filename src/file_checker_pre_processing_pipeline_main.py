#written by Roberto Franzosi November 2023

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"file_checker_pre_processing_pipeline_main",['os','tkinter','subprocess'])==False:
    sys.exit(1)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call
import pandas as pd

import GUI_IO_util
import IO_files_util
import config_util
import statistics_txt_util

import file_checker_util
import file_cleaner_util
import file_spell_checker_util

# RUN section ______________________________________________________________________________________________________________________________________________________

run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_chart_output_checkbox.get(),
                            GUI_util.charts_package_options_widget.get(),
                            utf8_var.get(),
                            ASCII_var.get())

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
def run(inputFilename,inputDir, outputDir,
        openOutputFiles,
        createCharts,
        chartPackage,
        utf8_var,
        ASCII_var):

    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    else:
        config_filename = scriptName.replace('_main.py', '_config.csv')

    filesToOpen=[]
    openOutputFiles=False # to make sure files are only opened at the end of this multi-tool script


    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]

    # # get the date options from filename
    # filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = config_util.get_date_options(
    #     config_filename, config_input_output_numeric_options)
    # extract_date_from_text_var = 0

    if package_display_area_value == '':
        mb.showwarning(title='No setup for NLP package and language',
                       message="The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again.")
        return


    if (utf8_var==False and \
        ASCII_var == False and \
        language_detect_var.get()==False and \
        spelling_var.get() == False and \
        NLTK_unusual_var.get() == False and \
        word_length_var.get() == False and \
        sentence_length_var.get() == False):
            mb.showwarning(title='No options selected', message='No options have been selected.\n\nPlease, select an option and try again.')
            return

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                       label='data_quality', silent=True)
    if outputDir == '':
        return

# utf-8 compliance ---------------------------------------------------------------------

    if utf8_var==True:
        file_checker_util.check_utf8_compliance(GUI_util.window, inputFilename, inputDir, outputDir,openOutputFiles,True)

    if ASCII_var==True:
        result=file_cleaner_util.convert_2_ASCII(GUI_util.window,inputFilename, inputDir, outputDir, config_filename)
        if result==False:
            return


# detect language  ----------------------------------------------------

    if language_detect_var.get():
        output = file_spell_checker_util.language_detection(window, inputFilename, inputDir, outputDir, config_filename,
                                                               openOutputFiles, createCharts, chartPackage)
        if output != None:
            if isinstance(output, str):
                filesToOpen.append(output)
            else:
                filesToOpen.extend(output)

    # if 'capital' in corpus_statistics_options_menu_var:
    #     output = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir, config_filename,
    #                                                            openOutputFiles, createCharts, chartPackage,corpus_statistics_options_menu_var)
    #     if output != None:
    #         if isinstance(output, str):
    #             filesToOpen.append(output)
    #         else:
    #             filesToOpen.extend(output)

# spelling checker --------------------------------------------------------------------------

    if spelling_var.get():
        pyspellchecker_file_name = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'spell_pyspellchecker')
        # import BERT_util
        # BERT_output = BERT_util.spell_checker_bert(window, inputFilename, inputDir, outputDir, '', createCharts, chartPackage)
        # filesToOpen.append(BERT_output)

        autocorrect_df = pd.DataFrame({'Original': [],
                                       'Corrected': [],
                                       "Document ID": [],
                                       "Document": []})

        pyspellchecker_df = autocorrect_df.copy()
        textblob_df = autocorrect_df.copy()

        pyspellchecker_file_name = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'spell_pyspellchecker')
        pyspellchecker_df.to_csv(pyspellchecker_file_name,encoding='utf-8', index=False)
        filesToOpen.append(pyspellchecker_file_name)

        textblob_file_name = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'spell_textblob')
        textblob_df.to_csv(textblob_file_name,encoding='utf-8', index=False)
        filesToOpen.append(textblob_file_name)

# NLTK unusual words -----------------------------------------------------------------

    if NLTK_unusual_var.get():
        output=file_spell_checker_util.nltk_unusual_words(window, inputFilename, inputDir, outputDir, config_filename, False, createCharts, chartPackage)
        if output != None:
            if isinstance(output, str):
                filesToOpen.append(output)
            else:
                filesToOpen.extend(output)

# compute word length ----------------------------------------------------

    if word_length_var.get():
        output = statistics_txt_util.process_words(GUI_util.window, config_filename, inputFilename, inputDir, outputDir, openOutputFiles, createCharts,
                          chartPackage,
                          processType='word length', language='English', excludeStopWords=True, word_length=3,
                          excludePunctuation=True, excludeArticles=True,
                          wordgram=1, lemmatize=False)
        if output != None:
            if isinstance(output, str):
                filesToOpen.append(output)
            else:
                filesToOpen.extend(output)

# compute sentence length ----------------------------------------------------

    if sentence_length_var.get():
        output = statistics_txt_util.compute_sentence_length(inputFilename, inputDir, outputDir,
                            config_filename, createCharts, chartPackage)
        if output != None:
            if isinstance(output, str):
                filesToOpen.append(output)
            else:
                filesToOpen.extend(output)


    openOutputFiles=True
    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=600, # height at brief display
                             GUI_height_full=640, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=1, # to be added for full display
                             increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for a pre-processing set of tools for data checking and data cleaning - A Pipeline'
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
config_input_output_numeric_options=[2,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

utf8_var= tk.IntVar()
ASCII_var= tk.IntVar()
extra_GUIs_var = tk.IntVar()
extra_GUIs_menu_var = tk.StringVar()
language_detect_var = tk.IntVar()
spelling_var = tk.IntVar()
spelling_auto_correct_var = tk.IntVar()
NLTK_unusual_var = tk.IntVar()
lower_case_words_var = tk.IntVar()
word_length_var = tk.IntVar()
sentence_length_var = tk.IntVar()

def clear(e):
    extra_GUIs_var.set(0)
    extra_GUIs_menu_var.set('')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

def open_GUI(*args):
    if 'checker/converter/cleaner' in extra_GUIs_menu_var.get():
        call("python file_checker_converter_cleaner_main.py", shell=True)
    if 'spell' in extra_GUIs_menu_var.get():
        call("python file_spell_checker_main.py", shell=True)
    elif 'splitter' in extra_GUIs_menu_var.get():
        call("python file_splitter_main.py", shell=True)
    elif 'search' in extra_GUIs_menu_var.get():
        call("python file_search_byWord_main.py", shell=True)
extra_GUIs_menu_var.trace('w',open_GUI)


extra_GUIs_var.set(0)
extra_GUIs_checkbox = tk.Checkbutton(window, text='GUIs available for more analyses ', variable=extra_GUIs_var, onvalue=1, offvalue=0) #, command=lambda: activate_all_options())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,extra_GUIs_checkbox,True)

extra_GUIs_menu_var.set('')
extra_GUIs_menu = tk.OptionMenu(window,extra_GUIs_menu_var,'File checker/converter/cleaner','Spell checker','File splitter','File word search')
# extra_GUIs_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   extra_GUIs_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select other related types of analysis you wish to perform")

utf8_var.set(1)
utf8_checkbox = tk.Checkbutton(window, text='Check input document(s) for utf-8 encoding', variable=utf8_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,utf8_checkbox)

ASCII_var.set(1)
ASCII_checkbox = tk.Checkbutton(window, text='Convert non-ASCII apostrophes & quotes and % to percent', variable=ASCII_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,ASCII_checkbox)

language_detect_var.set(1)
language_detect_checkbox = tk.Checkbutton(window,text="Language detection", variable=language_detect_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                    language_detect_checkbox, False, False, True,False, 90,
                    GUI_IO_util.labels_x_coordinate,
                    "Tick the checkbox to run different language detection algorithms: LANGDETECT, LANGID, spaCY, Stanza")



spelling_var.set(1)
spelling_checkbox = tk.Checkbutton(window,text="Spelling checker", variable=spelling_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                    spelling_checkbox, True, False, True,False, 90,
                    GUI_IO_util.labels_x_coordinate,
                    "Tick the checkbox to run different spelling checker algorithms: Pyspellchecker, Textblob, NLP Suite Typo checking")

spelling_auto_correct_var.set(0)
spelling_auto_correct_checkbox = tk.Checkbutton(window,text="Spelling auto-correct", variable=spelling_auto_correct_var, onvalue=1, offvalue=0)
spelling_auto_correct_checkbox.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                    spelling_auto_correct_checkbox, False, False, True,False, 90,
                    GUI_IO_util.open_TIPS_x_coordinate,
                    "Tick the checkbox to run the spelling auto-correct algorithm: AUTOCORRECT\nPLEASE, be sure to check auto-corrections very carefully")

NLTK_unusual_var.set(1)
NLTK_unusual_checkbox = tk.Checkbutton(window,text="NLTK unusual words", variable=NLTK_unusual_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                    NLTK_unusual_checkbox, False, False, True,False, 90,
                    GUI_IO_util.labels_x_coordinate,
                    "Tick the checkbox to obtain an NLTK list of unusual words as an indicator of possible misspellings")

lower_case_words_var.set(1)
lower_case_words_checkbox = tk.Checkbutton(window,text="Lower-case words after end-of-sentence punctuation (e.g., . ? !)", variable=lower_case_words_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                    lower_case_words_checkbox, False, False, True,False, 90,
                    GUI_IO_util.labels_x_coordinate,
                    "Tick the checkbox to check for lower-case words coming after a . as an indicator of possible break in sentence construction")


word_length_var.set(1)
word_length_checkbox = tk.Checkbutton(window,text="Word length", variable=word_length_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                    word_length_checkbox, False, False, True,False, 90,
                    GUI_IO_util.labels_x_coordinate,
                    "Tick the checkbox to check word length as an indicator of possible misspellings")

sentence_length_var.set(1)
sentence_length_checkbox = tk.Checkbutton(window,text="Sentence length", variable=sentence_length_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                    sentence_length_checkbox, False, False, True,False, 90,
                    GUI_IO_util.labels_x_coordinate,
                    "Tick the checkbox to check sentence length as an indicator of possible incorrect sentences")

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Word similarity (Levenshtein edit distance)': 'TIPS_NLP_Word similarity (Levenshtein edit distance).pdf',
               'File checker, converter, cleaner':'TIPS_NLP_File checker & converter & cleaner.pdf',
               'Filename checker':'TIPS_NLP_Filename checker.pdf',
               'Text encoding':'TIPS_NLP_Text encoding.pdf',
               'utf-8 text encoding':'TIPS_NLP_Text encoding (utf-8).pdf',
               'Spelling checker': 'TIPS_NLP_Spelling checker.pdf'}
TIPS_options = 'Text encoding', 'utf-8 text encoding', 'Spelling checker', 'Word similarity (Levenshtein edit distance)', 'File checker, converter, cleaner', 'Filename checker'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         'Please, tick the \'GUIs available\' checkbox if you wish to see and select the range of other available tools suitable for data checking.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, tick the checkbox to check your input corpus for utf-8 encoding.\n   Non utf-8 compliant texts are likely to lead to code breakdown.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, tick the checkbox to convert non-ASCII apostrophes & quotes and % to percent.\n   ASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n   % signs may lead to code breakdon of Stanford CoreNLP.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick checkbox to run various algorithms of language detection: LANGDETECT, LANGID, spaCY, Stanza.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick checkbox to run spell-checking algorithms: Pyspellchecker, textblob.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help","Please, tick the checkbox to run the NLTK unusual word algorithm. Not all unusual words are misspelled words but the list of NLTK unusual words can be used to find misspelled words.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help","Please, tick the checkbox to obtain a list of lower-case words that occur after an end-of-sentence marker. Such words can be taken as an indication, for instance, of an incorrect conversion to text of a pdf file. Parsers (e.g., Stanford CoreNLP, spaCy) will incorrectly parse sentences with end-of-sentence markers in the wrong position (e.g., 'Robert went to. Europe for vacation').")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to run the algorithm that computes word length. Unusually long words may be an indication that words have been run together (e.g., Abraham Lincoln, AbrahamLincoln).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to run the algorithm that computes sentence length.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The GUI brings together various Python 3 scripts to buil a pipeline for data quality checking of a corpus, automatically extracting all relevant data from texts and visualizing the results.\n\nEach tool performs all required computations then saves results as csv files and visualizes them."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
    config_filename = 'NLP_default_IO_config.csv'
filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = config_util.get_date_options(config_filename, config_input_output_numeric_options)
extract_date_from_text_var=0

mb.showwarning(title='Warning',message='The option is currently under development. Sorry!\n\nCheck back soon.')
GUI_util.window.mainloop()
