#written by Catherine Xiao, Apr 2018
#edited by Elaine Dong, Dec 04 2019
#edited by Roberto Franzosi, Nov 2019, October 2020

# https://stackoverflow.com/questions/2836959/adjective-nominalization-in-python-nltk
# https://stackoverflow.com/questions/45109767/get-verb-from-noun-wordnet-python

# https://github.com/topics/nominalization
# https://pypi.org/project/qanom/0.0.1/

import sys
import GUI_util
import IO_libraries_util
import tkinter.messagebox as mb

import os
import tkinter as tk
import IO_files_util
import GUI_IO_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run():
    # widget values read here at RUN time (was: run_script_command lambda + run() params)
    inputFilename = GUI_util.inputFilename.get()
    inputDir = GUI_util.input_main_dir_path.get()
    outputDir = GUI_util.output_dir_path.get()
    openOutputFiles = GUI_util.open_csv_output_checkbox.get()
    chartPackage = GUI_util.charts_package_options_widget.get()
    dataTransformation = GUI_util.data_transformation_options_widget.get()
    check_ending = check_nom_verb_ending_var.get()

    config_filename = GUI_util.config_filename_selected_config.get()
    filesToOpen = []

    import nominalization_util
    outputFiles = nominalization_util.nominalization(inputFilename,inputDir, outputDir, config_filename, config_input_output_numeric_options, openOutputFiles,chartPackage,dataTransformation,check_ending)

    if outputFiles!=None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    if openOutputFiles == 1:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)


#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
GUI_util.run_button.configure(command=run)


# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=360, # height at brief display
                             GUI_height_full=440, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Nominalization'
head, scriptName = os.path.split(os.path.basename(__file__))
# hardcode the default config here (as every other GUI does): at module-init time
# GUI_util.config_filename_selected_config is not yet populated and .get() returns '', which makes
# the startup I/O check read an empty config and falsely report the INPUT/OUTPUT fields as missing
config_filename = 'NLP_default_IO_config.csv'

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

csv_file_var = tk.StringVar()

extra_GUIs_var = tk.IntVar()
extra_GUIs_menu_var = tk.StringVar()

check_nom_verb_ending_var = tk.IntVar()



csv_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT CSV file',command=lambda: IO_files_util.get_corpus_CoNLL_csv(window, csv_file_var,'Select INPUT csv CoNLL table file', [("csv files", "*.csv")],True))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               csv_file_button, True)

#setup a button to open Windows Explorer on the selected input directory
openInputFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, csv_file_var.get()))
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,openInputFile_button,
                    True, False, True,False, 90, GUI_IO_util.IO_configuration_menu, "Open INPUT csv CoNLL table file")

csv_file=tk.Entry(window, width=GUI_IO_util.csv_file_width,textvariable=csv_file_var)
csv_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,csv_file)


extra_GUIs_var.set(0)
extra_GUIs_checkbox = tk.Checkbutton(window, text='GUIs available for more analyses ', variable=extra_GUIs_var, onvalue=1, offvalue=0, command=lambda: open_GUI())
# extra_GUIs_checkbox.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,extra_GUIs_checkbox,True)

extra_GUIs_menu_var.set('')
extra_GUIs_menu = tk.OptionMenu(window,extra_GUIs_menu_var,'Semantic analysis (Open GUI)','Parsers & annotators (Open GUI)','N-grams & Co-Occurrences (Open GUI)','CoNLL table analyzer (Open GUI)','WordNet (Open GUI)','What\'s in Your Corpus (Open GUI)')
extra_GUIs_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   extra_GUIs_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select other related types of analysis you wish to perform" \
                                    "\nThe selected GUI will open without having to press RUN")

def open_GUI(*args):
    import run_script_util
    if extra_GUIs_var.get():
        extra_GUIs_menu.configure(state='normal')
    if extra_GUIs_menu_var.get():
        if 'Semantic' in extra_GUIs_menu_var.get():
            run_script_util.run_script("semantic_analysis_main.py")
        elif 'Parser' in extra_GUIs_menu_var.get():
            run_script_util.run_script("parsers_annotators_main.py")
        elif 'CoNLL' in extra_GUIs_menu_var.get():
            run_script_util.run_script("CoNLL_table_analyzer_main.py")
        else:
            mb.showwarning(title='Warning',
                           message="The selected option is not available.\n\nPlease, select a different option and try again.")


extra_GUIs_menu_var.trace('w',open_GUI)

check_nom_verb_ending_var.set(1)
check_nom_verb_ending_checkbox = tk.Checkbutton(window, variable=check_nom_verb_ending_var, onvalue=1, offvalue=0)
check_nom_verb_ending_checkbox.config(text="Check the nominalized verb ending")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer,
                                               check_nom_verb_ending_checkbox, False, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "The checkbox, when ticked, checks nominalized verbs (i.e., nouns) for the typical ending of nominalized verbs (nment, ing, ion, ance, ence)\n" \
                                               "and for the values listed in the nominalized-verbs-list.csv in the lib/wordList subdirectory that users can edit")

# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,check_nom_verb_ending_checkbox)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Nominalization':'TIPS_NLP_Nominalization.pdf','Lexical databases (WordNet, VerbNet, FrameNet)': 'TIPS_NLP_Lexical databases (WordNet, VerbNet, FrameNet).pdf','Style analysis':'TIPS_NLP_Style analysis.pdf','CoNLL Table': 'TIPS_NLP_Stanford CoreNLP CoNLL table.pdf'}
TIPS_options='Nominalization','Lexical databases (WordNet, VerbNet, FrameNet)','Style analysis','CoNLL Table'

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
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                             "NLP Suite Help",
                                                             "Please, use the 'Select INPUT CSV file' button to choose the CoNLL table to analyze.\n\nThe button first LISTS all CoNLL tables found for your current corpus - searching the output directory, the input directory, and the default output directory - so you can pick one directly without hunting for the file (each is labelled by its parser/corpus subfolder, e.g. a Stanza dependency parse vs a CoreNLP parse). You can also choose 'Browse for another file' to select any other CoNLL csv. If no CoNLL table is found, a file dialog opens directly.\n\nA CoNLL table is a csv file produced by a parser (spaCy, Stanford CoreNLP, or Stanza) via the Parsers & annotators GUI, in which each token is labeled with a part-of-speech tag (POSTAG), a Dependency Relation tag (DEPREL), and other linguistic information.\n\nThe selected file is validated to ensure it is a properly formatted CoNLL table." + GUI_IO_util.msg_openFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                             "NLP Suite Help",
                                                             'Please, tick the \'GUIs available\' checkbox if you wish to see and select the range of other available tools suitable for stylistic analysis.')

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, untick the checkbox if you do not want to check nominalized verbs for their typical ending (e.g., ing, ion; see TIPS file).\n\nWhen the checkbox is ticked, nomanilized verbs will also be checked against the values listed in the nominalized-verbs-list.csv in the lib/wordLists subdirectory that users can edit.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer -1

y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="These Python 3 scripts analyze a text file (or a directory of text files) for instances of nominalization, i.e., the use of a noun derived from a verb (a deverbal noun) instead of the verb itself, such as 'the lynching occurred' instead of 'they lynched'.\n\nNominalization, together with the passive voice, can be used to deny agency: in an expression such as 'the lynching occurred' there is no mention of an agent, of who did it.\n\nHOW IT WORKS. Each word is tagged for part of speech and lemmatized using the NLP Suite's configuration-aware basic NLP layer (spaCy or Stanza, according to your setup). Every noun is then tested against WordNet's derivational morphology (Fellbaum 1998): a noun is flagged as a nominalization when WordNet links it to a base VERB through a derivationally related form, with a derivation-direction (length) constraint so that only nouns DERIVED from verbs are kept (e.g., 'destruction' -> 'destroy'). The scripts no longer rely on pywsd. Optionally (checkbox) nominalized nouns are also filtered by their typical endings (-ing, -ion, -ent, -ance, -ence) and checked against an editable list, lib/wordLists/nominalized-verbs-list.csv, which you can extend with nominalizations that do not follow the standard endings.\n\nIN OUTPUT the scripts produce\n   1. a csv file listing each noun with its base verb and a TRUE/FALSE nominalization flag;\n   2. a csv file with the frequency distribution of the nominalized verbs;\n   3. a csv file with the frequency distribution of nominalizations by sentence index;\n   4. bar charts of these frequency distributions."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
