# written by Roberto Franzosi (Spring/summer 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"statistics_txt_main.py",['os','csv','tkinter','ntpath','collections','subprocess'])==False:
    sys.exit(0)

import os
import tkinter.messagebox as mb
import tkinter as tk
from subprocess import call

import GUI_IO_util


extra_GUIs_var = tk.IntVar()
extra_GUIs_menu_var = tk.StringVar()

corpus_statistics_var = tk.IntVar()
corpus_statistics_options_menu_var = tk.StringVar()
corpus_text_options_menu_var = tk.StringVar()

corpus_statistics_byPOS_var = tk.IntVar()

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir,
        corpus_statistics_options_menu_var,
        corpus_text_options_menu_var,
        openOutputFiles,createCharts,chartPackage,
        corpus_statistics_var,
        corpus_statistics_byPOS_var):

    filesToOpen = []  # Store all files that are to be opened once finished

    if not corpus_statistics_var and not corpus_statistics_byPOS_var:
        mb.showwarning('Warning',
                       'No option has been selected.\n\nPlease, select an option and try again.')
        return

    # corpus statistics --------------------------------------------------------------------

    if corpus_statistics_var:
        stopwords_var = False
        lemmatize_var = False
        if corpus_text_options_menu_var == '*':
            stopwords_var = True
            lemmatize_var = True
        if 'Lemmatize' in corpus_text_options_menu_var:
            lemmatize_var = True
        if 'stopwords' in corpus_text_options_menu_var:
            stopwords_var = True
        if "*" in corpus_statistics_options_menu_var or 'frequencies' in corpus_statistics_options_menu_var:

            import statistics_txt_util
            outputFiles = statistics_txt_util.compute_corpus_statistics(window, inputFilename, inputDir, outputDir,
                                                                        config_filename, False, createCharts,
                                                                        chartPackage, stopwords_var, lemmatize_var)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)
        if "Compute sentence length" in corpus_statistics_options_menu_var or "*" in corpus_statistics_options_menu_var:
            outputFiles = statistics_txt_util.compute_sentence_length(inputFilename, inputDir, outputDir,
                                                                      config_filename, createCharts, chartPackage)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if "Compute line length" in corpus_statistics_options_menu_var or "*" in corpus_statistics_options_menu_var:
            outputFiles = statistics_txt_util.compute_line_length(window, config_filename, inputFilename, inputDir,
                                                                  outputDir,
                                                                  False, createCharts, chartPackage)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    if corpus_statistics_byPOS_var:
        import Stanza_util
        import config_util
        # get the NLP package and language options
        error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = \
            config_util.read_NLP_package_language_config()
        # get the date options from filename
        filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = \
            config_util.get_date_options(config_filename, config_input_output_numeric_options)
        language_var = language
        language_list = [language]

        document_length_var = 1
        limit_sentence_length_var = 1000
        memory_var = 6
        annotator='POS'
        outputFiles = Stanza_util.Stanza_annotate(config_filename, inputFilename, inputDir,
                                                      outputDir,
                                                      openOutputFiles,
                                                      createCharts, chartPackage,
                                                      annotator, False,
                                                      language_list,
                                                      memory_var, document_length_var, limit_sentence_length_var,
                                                      filename_embeds_date_var=filename_embeds_date_var,
                                                      date_format=date_format_var,
                                                      items_separator_var=items_separator_var,
                                                      date_position_var=date_position_var)

        if outputFiles == None:
            return
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    if openOutputFiles == True:
        import IO_files_util
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)


#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                corpus_statistics_options_menu_var.get(),
                                corpus_text_options_menu_var.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_chart_output_checkbox.get(),
                                GUI_util.charts_package_options_widget.get(),
                                corpus_statistics_var.get(),
                                corpus_statistics_byPOS_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=360, # height at brief display
                             GUI_height_full=400, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=1, # to be added for full display
                             increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Statistical Analyses of txt Files'
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = scriptName.replace('_main.py', '_config.csv')

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
    extra_GUIs_var.set(0)
    extra_GUIs_menu_var.set('')

    corpus_statistics_checkbox.configure(state='normal')

    corpus_statistics_var.set(0)
    corpus_statistics_options_menu_var.set('')
    corpus_text_options_menu_var.set('')

    corpus_statistics_byPOS_var.set(0)

    activate_all_options()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)


extra_GUIs_var.set(0)
extra_GUIs_checkbox = tk.Checkbutton(window, text='GUIs available for pre-processing', variable=extra_GUIs_var, onvalue=1, offvalue=0, command=lambda: activate_all_options())
# extra_GUIs_checkbox.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,extra_GUIs_checkbox,True)

extra_GUIs_menu_var.set('')
extra_GUIs_menu = tk.OptionMenu(window,extra_GUIs_menu_var,'N-grams & Co-occurrences', 'CoNLL Table Analyzer (Open GUI)','Style Analysis (Open GUI)')
extra_GUIs_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   extra_GUIs_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select other related types of analysis you wish to perform" \
                                    "\nThe selected GUI will open without having to press RUN")


def open_GUI(*args):
    extra_GUIs_menu.configure(state='disabled')
    if extra_GUIs_var.get():
        extra_GUIs_menu.configure(state='normal')
    else:
        return
    if extra_GUIs_var.get():
        if 'CoNLL' in extra_GUIs_menu_var.get():
            call("python CoNLL_table_analyzer_main.py", shell=True)
        if 'Style' in extra_GUIs_menu_var.get():
            call("python style_analysis_main.py", shell=True)
        if 'grams' in extra_GUIs_menu_var.get():
            call("python NGrams_CoOccurrences_main.py", shell=True)
extra_GUIs_menu_var.trace('w',open_GUI)

corpus_statistics_var.set(0)
corpus_statistics_checkbox = tk.Checkbutton(window,text="Compute document(s) statistics", variable=corpus_statistics_var, onvalue=1, offvalue=0, command=lambda: activate_all_options())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,corpus_statistics_checkbox,True)

corpus_statistics_options_menu_var.set('*')

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

corpus_statistics_byPOS_var.set(0)
corpus_statistics_byPOS_checkbox = tk.Checkbutton(window,text="Compute document(s) statistics by POS (Part of Speech) tag value", variable=corpus_statistics_byPOS_var, onvalue=1, offvalue=0, command=lambda: activate_all_options())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   corpus_statistics_byPOS_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick the checkbox if you wish to compute document statistics by POS (Part of Speech) tag (e.g., nouns, verbs, adjectives)\nThe algorith relies on Stanza POS annotator")

def activate_all_options():
    extra_GUIs_checkbox.configure(state='normal')
    corpus_statistics_checkbox.configure(state='normal')
    corpus_statistics_byPOS_checkbox.configure(state='normal')
    if extra_GUIs_var.get():
        extra_GUIs_menu.configure(state='normal')
        corpus_statistics_checkbox.configure(state='disabled')
        corpus_statistics_byPOS_checkbox.configure(state='disabled')
    if corpus_statistics_var.get():
        extra_GUIs_checkbox.configure(state='disabled')
        corpus_statistics_byPOS_checkbox.configure(state='disabled')
    if corpus_statistics_byPOS_var.get():
        extra_GUIs_checkbox.configure(state='disabled')
        corpus_statistics_checkbox.configure(state='disabled')

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Style analysis':'TIPS_NLP_Style analysis.pdf',
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',
               'N-Grams (word & character)':"TIPS_NLP_Ngrams (word & character).pdf",
               'NLP Ngram and Word Co-Occurrence VIEWER':"TIPS_NLP_Ngram and Word Co-Occurrence VIEWER.pdf",
               'Google Ngram Viewer':'TIPS_NLP_Ngram Google Ngram Viewer.pdf',
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf'}

TIPS_options='Style analysis', 'English Language Benchmarks', 'N-Grams (word & character)','NLP Ngram and Word Co-Occurrence VIEWER','Google Ngram Viewer','Excel smoothing data series', 'csv files - Problems & solutions', 'Statistical measures'

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
                                                         'Please, tick the \'GUIs available\' checkbox if you wish to see and select the range of other available tools suitable for searches and style analysis.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                'Please, tick the checkbox if you wish to compute basic statistics on your corpus.\n\nUse the dropdown menu to select the desired option. Use the Text options dropdown menu to lemmatize words or exclude stopwords/punctuation.\n\nIn INPUT the script expects a single txt file or a directory containing a set of txt files.\n\nIn OUTPUT, the script generates a set of csv files each containing word n-grams between 1 and 3.\n\nWhen n-grams are computed by sentence index, the sentence displayed in output is always the first occurring sentence.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                'Please, tick the checkbox if you wish to compute statistics on your corpus by POS (Part of Speech) tag (e.g., nouns, verbs, adjectives).\n\nThe scripts relies on the Stanza POS annotator to export all tokens in the corpus with their POS value.\n\nIn INPUT the script expects a single txt file or a directory containing a set of txt files.\n\nIn OUTPUT, the script generates a set of csv files each containing the words in our corpus by POS value and their frequencies. Charts will also be visualized.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 scripts provides a quick link to various NLP Suite GUIs for obtaining basic statistics about the corpus (e.g., n-grams, sentence lenght)."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()

