#written by Catherine Xiao, Apr 2018
#edited by Elaine Dong, Dec 04 2019
#edited by Roberto Franzosi, Nov 2019, October 2020


import sys
import GUI_util
import IO_libraries_util
import tkinter.messagebox as mb

import os
import tkinter as tk
import IO_files_util
import GUI_IO_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,inputDir, outputDir,openOutputFiles,chartPackage, dataTransformation):

    config_filename = GUI_util.config_filename_selected_config.get()
    filesToOpen = []
    if SRL_var.get() == 1:
        import SRL_util
        if inputFilename and inputFilename[-4:].lower() == '.csv':
            mb.showwarning(title='SRL input error',
                           message='Semantic Role Labeling needs txt input (a txt file or a folder '
                                   'of txt files), not a csv file.\n\nPlease select txt input and try again.')
            return
        srl_files = SRL_util.run_SRL(GUI_util.window, inputFilename, inputDir, outputDir,
                                     chartPackage, dataTransformation)
        if srl_files:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, srl_files, outputDir, scriptName)
        return


#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.charts_package_options_widget.get(),
                                GUI_util.data_transformation_options_widget.get())

GUI_util.run_button.configure(command=run_script_command)


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

GUI_label='Graphical User Interface (GUI) for Semantic Role Labelling (SRL)'

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

SRL_var = tk.IntVar()

def check_csv_file_headers(csv_file):
    import CoNLL_util
    import reminders_util
    cannotRun=False
    inputIsCoNLL = CoNLL_util.check_CoNLL(csv_file_var.get(), True)
    if inputIsCoNLL:
        reminders_util.checkReminder(scriptName, reminders_util.title_options_input_csv_file,
                                     reminders_util.message_input_csv_file, True)
    return cannotRun

def get_csv_file(window,title,fileType,annotate):
    #csv_file_var.set('')
    # First offer the CoNLL tables discovered for the current corpus (output/input/default dirs); only fall
    # back to a file dialog if none are found or the user chooses to browse.
    import CoNLL_util
    import IO_csv_util
    chosen = CoNLL_util.choose_corpus_CoNLL(window, GUI_util.output_dir_path.get(), GUI_util.inputFilename.get(), GUI_util.input_main_dir_path.get())
    if chosen is None:
        return ''
    if chosen != '__BROWSE__':
        filePath = chosen
    else:
        if csv_file!='':
            initialFolder=os.path.dirname(os.path.abspath(csv_file_var.get()))
        else:
            initialFolder = os.path.dirname(os.path.abspath(__file__))
        filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)

    if len(filePath)>0:
        nRecords, nColumns =IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(filePath, 'utf-8')
        if nRecords==0:
            mb.showwarning(title='Warning',
                           message="The selected input csv file is empty.\n\nPlease, select a different file and try again.")
            filePath=''
        else:
            csv_file_var.set(filePath)
            GUI_util.inputFilename.set(filePath)
    return filePath

csv_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT CSV file',command=lambda: get_csv_file(window,'Select INPUT csv CoNLL table file', [("csv files", "*.csv")],True))
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
extra_GUIs_menu = tk.OptionMenu(window,extra_GUIs_menu_var,'Subject-Verb-Object (SVO)','Semantic analysis (Open GUI)','Parsers & annotators (Open GUI)','N-grams & Co-Occurrences (Open GUI)','CoNLL table analyzer (Open GUI)','WordNet (Open GUI)','What\'s in Your Corpus (Open GUI)')
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
        elif 'SVO' in extra_GUIs_menu_var.get():
            run_script_util.run_script("SVO_main.py")
        elif 'CoNLL' in extra_GUIs_menu_var.get():
            run_script_util.run_script("CoNLL_table_analyzer_main.py")
        else:
            mb.showwarning(title='Warning',
                           message="The selected option is not available.\n\nPlease, select a different option and try again.")


extra_GUIs_menu_var.trace('w',open_GUI)

SRL_var.set(1)
SRL_checkbox = tk.Checkbutton(window, variable=SRL_var, onvalue=1, offvalue=0)
SRL_checkbox.config(text="Semantic Role Labelling (SRL)")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer,
                                               SRL_checkbox, False, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "The checkbox, when ticked, checks CLAUDE CODE ")

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

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Tick the SRL (Semantic Role Labeling) checkbox to identify, for every verb (predicate) in a sentence, WHO did WHAT to WHOM:\n"
                                  "   ARG0 = the Agent (the doer);\n"
                                  "   ARG1 = the Patient (the one acted upon/affected);\n"
                                  "   ARG2 = the Recipient or Beneficiary;\n"
                                  "   plus modifiers Where (ARGM-LOC), When (ARGM-TMP), How (ARGM-MNR), and Why (ARGM-CAU).\n\n"
                                  "SRL is the richer successor to Subject-Verb-Object (SVO) analysis. In INPUT it expects a txt file or a directory of txt files (ENGLISH ONLY). In OUTPUT it produces a csv file with one row per sentence-and-predicate (a sentence with several verbs yields several rows).\n\n"
                                  "Beyond the raw PropBank arguments, SRL enriches each predicate via SemLink (Palmer's PropBank-VerbNet-FrameNet linking):\n"
                                  "   Refined roles = fairly-accurate VerbNet thematic roles (Agent, Patient/Theme, Experiencer, Stimulus, Recipient, Goal, Result...), keeping the preposition cue alongside when it differs (e.g. 'Destination / Source');\n"
                                  "   VerbNet class = the sense-disambiguated VerbNet class of the predicate (e.g. murder.01 = murder-42.1) - a backbone for grouping verbs into categories such as 'violence';\n"
                                  "   FrameNet frame = the disambiguated FrameNet frame (Killing, Destroying, Execution, Attack, Cause_harm...) - interpretable action categories for content analysis (e.g. lynch = Killing).\n\n"
                                  "Visualizations include a 'who did what to whom' network and Sankey flow (both entity-level and VerbNet-role-level), plus frequency charts of the refined roles, VerbNet classes, and FrameNet frames.\n\n"
                                  "SRL runs in a separate, isolated Python 3.8 engine (it cannot share the Suite's packages) that is set up once per machine by running  python setup_SRL.py  - this creates the environment, downloads the BERT model, and fetches the SemLink maps. The VerbNet class and FrameNet frame columns need those maps; without them SRL still runs with heuristic refined roles.\n\n"
                                  "Note: lemmatization inside the SRL engine uses spaCy (already present in that isolated environment), not the Suite's default Stanza, which is not installed there.\n\n"
                                  "The first run loads the BERT-based model and may take 30-60 seconds; the GUI will appear frozen (Not Responding) while SRL runs. This is normal - please be patient."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer -1

y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="CLAUDE CODE These Python 3 scripts analyze a text file (or a directory of text files) for instances of nominalization, i.e., the use of a noun derived from a verb (a deverbal noun) instead of the verb itself, such as 'the lynching occurred' instead of 'they lynched'.\n\nNominalization, together with the passive voice, can be used to deny agency: in an expression such as 'the lynching occurred' there is no mention of an agent, of who did it.\n\nHOW IT WORKS. Each word is tagged for part of speech and lemmatized using the NLP Suite's configuration-aware basic NLP layer (spaCy or Stanza, according to your setup). Every noun is then tested against WordNet's derivational morphology (Fellbaum 1998): a noun is flagged as a nominalization when WordNet links it to a base VERB through a derivationally related form, with a derivation-direction (length) constraint so that only nouns DERIVED from verbs are kept (e.g., 'destruction' -> 'destroy'). The scripts no longer rely on pywsd. Optionally (checkbox) nominalized nouns are also filtered by their typical endings (-ing, -ion, -ent, -ance, -ence) and checked against an editable list, lib/wordLists/nominalized-verbs-list.csv, which you can extend with nominalizations that do not follow the standard endings.\n\nIN OUTPUT the scripts produce\n   1. a csv file listing each noun with its base verb and a TRUE/FALSE nominalization flag;\n   2. a csv file with the frequency distribution of the nominalized verbs;\n   3. a csv file with the frequency distribution of nominalizations by sentence index;\n   4. bar charts of these frequency distributions."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
