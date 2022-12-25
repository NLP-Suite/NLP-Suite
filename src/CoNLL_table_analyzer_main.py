import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "CoNLL table_analyzer", ['os', 'tkinter','pandas']) == False:
    sys.exit(0)

import os
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import CoNLL_util
import CoNLL_table_search_util
import statistics_csv_util
import charts_util
import IO_files_util
import IO_csv_util
import IO_user_interface_util
import Stanford_CoreNLP_tags_util
import CoNLL_k_sentences_util
import reminders_util

# from data_manager_main import extract_from_csv

# more imports (e.g., import CoNLL_clause_analysis_util) are called below under separate if statements

# RUN section ______________________________________________________________________________________________________________________________________________________

# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
def run(inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage,
        searchedCoNLLField, searchField_kw, postag, deprel, co_postag, co_deprel, Begin_K_sent_var, End_K_sent_var):

    global recordID_position, documentId_position, data, all_CoNLL_records
    recordID_position = 9 # NEW CoNLL_U
    documentId_position = 11 # NEW CoNLL_U

    noResults = "No results found matching your search criteria for your input CoNLL file. Please, try different search criteria.\n\nTypical reasons for this warning are:\n   1.  You are searching for a token/word not found in the FORM or LEMMA fields (e.g., 'child' in FORM when in fact FORM contains 'children', or 'children' in LEMMA when in fact LEMMA contains 'child'; the same would be true for the verbs 'running' in LEMMA instead of 'run');\n   2. you are searching for a token that is a noun (e.g., 'children'), but you select the POS value 'VB', i.e., verb, for the POSTAG of searched token."
    filesToOpen = []  # Store all files that are to be opened once finished
    outputFiles = []

    if all_analyses_var.get() == False and\
        search_token_var.get() == False and\
        compute_sentence_var.get() == False and \
        k_sentences_var.get() == False:
            mb.showwarning(title='No option selected',
                       message="No option has been selected.\n\nPlease, select an option by ticking a checkbox and try again.")
            return

    if search_token_var.get() and searchField_kw=='e.g.: father':
        mb.showwarning(title='Search error',
                       message="The 'Searched token' field must be different from 'e.g.: father'. Please, enter a CoNLL table token/word and try again.")
        return

    withHeader = True
    # TODO Chen we are reading inputFilename twice, once here then again as a dataframe
    data, header = IO_csv_util.get_csv_data(inputFilename, withHeader)
    if len(data) == 0:
        return
    all_CoNLL_records = CoNLL_util.CoNLL_record_division(data)
    if all_CoNLL_records == None:
        return
    if len(all_CoNLL_records) == 0:
        return

    if all_analyses_var.get():
        # create a subdirectory of the output directory; should create a subdir with increasing number to avoid writing ver
        outputDir_temp = IO_files_util.make_output_subdirectory(inputFilename, '', outputDir, label='CoNLL_analyses',
                                                           silent=True)
        if outputDir_temp == '':
            return

        outputDir=outputDir_temp

        if all_analyses.get() == '*':
            label = "Clause, noun, verb, function words"
        else:
            label = all_analyses.get()
        startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running CoNLL table ' + label + ' analyses at',
                                                     True, '', True, '', False)
        if all_analyses.get() == '*' or all_analyses.get() == 'Clause analysis':
            import CoNLL_clause_analysis_util
            outputFiles = CoNLL_clause_analysis_util.clause_stats(inputFilename, '', outputDir,
                                                                  data,
                                                                  all_CoNLL_records,
                                                                  openOutputFiles, createCharts, chartPackage)
            if outputFiles != None:
                filesToOpen.extend(outputFiles)

        if all_analyses.get() =='*' or all_analyses.get() =='Noun analysis':
            import CoNLL_noun_analysis_util
            outputFiles = CoNLL_noun_analysis_util.noun_stats(inputFilename, outputDir, data, all_CoNLL_records,
                                                              openOutputFiles, createCharts, chartPackage)
            if outputFiles != None:
                filesToOpen.extend(outputFiles)
        if all_analyses.get() =='*' or all_analyses.get() =='Verb analysis':
            import CoNLL_verb_analysis_util
            outputFiles = CoNLL_verb_analysis_util.verb_stats(config_filename, inputFilename, outputDir, data, all_CoNLL_records,
                                                              openOutputFiles, createCharts, chartPackage)

            if outputFiles != None:
                filesToOpen.extend(outputFiles)

        if all_analyses.get() =='*' or all_analyses.get() =='Function (junk/stop) words analysis':
            import CoNLL_function_words_analysis_util
            outputFiles = CoNLL_function_words_analysis_util.function_words_stats(inputFilename, outputDir, data,
                                                                                  all_CoNLL_records, openOutputFiles,
                                                                                  createCharts, chartPackage)
            if outputFiles != None:
                filesToOpen.extend(outputFiles)

        IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                                           'Finished running CoNLL table ' + label + ' analyses at',
                                           True, '', True, startTime, False)

    if search_token_var.get() and searchField_kw != 'e.g.: father':
        # # create a subdirectory of the output directory
        # outputDir = IO_files_util.make_output_subdirectory(inputFilename, '', outputDir, label='CoNLL_search',
        #                                                    silent=True)

        if ' ' in searchField_kw:
            mb.showwarning(title='Search error',
                           message="The CoNLL table search can only contain one token/word since the table has one record for each token/word.\n\nPlease, enter a different word and try again.\n\nIf you need to search your corpus for collocations, i.e., multi-word expressions, you need to use the 'N-grams/Co-occurrence searches' or the 'Words/collocations searches' in the ALL searches GUI.")
            return
        if searchedCoNLLField.lower() not in ['lemma', 'form']:
            searchedCoNLLField_var.set('FORM')
        if postag_var.get() != '*':
            postag = str(postag_var.get()).split(' - ')[0]
            postag = postag.strip()
        else:
            postag = '*'
        if deprel != '*':
            deprel = str(deprel).split(' - ')[0]
            deprel = deprel.strip()
        else:
            deprel = '*'
        if co_postag != '*':
            co_postag = str(co_postag).split(' - ')[0]
            co_postag = co_postag.strip()
        else:
            co_postag = '*'
        if co_deprel != '*':
            co_deprel = str(co_deprel).split(' - ')[0]
            co_deprel = co_deprel.strip()
        else:
            co_deprel = '*'

        if (not os.path.isfile(inputFilename.strip())) and \
                ('CoNLL' not in inputFilename) and \
                (not inputFilename.strip()[-4:] == '.csv'):
            mb.showwarning(title='INPUT File Path Error',
                           message='Please, check INPUT FILE PATH and try again. The file must be a CoNLL table (extension .conll with Stanford CoreNLP no clausal tags, extension .csv with Stanford CoreNLP with clausal tags)')
            return
        if 'e.g.: father' in searchField_kw:
            msg = "Please, check the \'Searched token\' field and try again.\n\nThe value entered must be different from the default value (e.g.: father)."
            mb.showwarning(title='Searched Token Input Error', message=msg)
            return  # breaks loop
        if len(searchField_kw) == 0:
            msg = "Please, check the \'Searched token\' field and try again.\n\nThe value entered must be different from blank."
            mb.showwarning(title='Searched Token Input Error', message=msg)
            return  # breaks loop

        startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running CoNLL search at',
                                                     True, '', True, '', True)

        withHeader = True
        data, header = IO_csv_util.get_csv_data(inputFilename, withHeader)

        if len(data) <= 1000000:
            try:
                data = sorted(data, key=lambda x: int(x[recordID_position]))
            except:
                mb.showwarning(title="CoNLLL table ill formed",
                               message="The CoNLL table is ill formed. You may have tinkered with it. Please, rerun the Stanford CoreNLP parser since many scripts rely on the CoNLL table.")
                return

        temp_outputDir, filesToOpen = CoNLL_table_search_util.search_CoNLL_table(inputFilename, outputDir,
                                          createCharts, chartPackage,
                                          all_CoNLL_records, searchField_kw, searchedCoNLLField,
                                          related_token_POSTAG=co_postag,
                                          related_token_DEPREL=co_deprel, _tok_postag_=postag,
                                          _tok_deprel_=deprel)

        if len(filesToOpen)>0:
            outputDir = temp_outputDir

    if compute_sentence_var.get():
        tempOutputFile = CoNLL_util.compute_sentence_table(inputFilename, outputDir)
        filesToOpen.append(tempOutputFile)

    if k_sentences_var.get():
        if Begin_K_sent_var==0 or End_K_sent_var==0:
            mb.showwarning(title='Warning',
                           message="The Repetion finder algorithm needs beginning and end K sentences.\n\nPlease, enter valid K number(s) of sentences and try again.")
            return
        startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                       'Started running the CoNLL table K-sentences analyzer at',
                                                       True, '', True, '', False)
        temp_outputDir, outputFiles = CoNLL_k_sentences_util.k_sent(inputFilename, outputDir, createCharts, chartPackage, Begin_K_sent_var, End_K_sent_var)
        if outputFiles != None:
            outputDir = temp_outputDir
            filesToOpen.extend(outputFiles)
        IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                                           'Finished running the CoNLL table K-sentences analyzer at',
                                           True, '', True, startTime, False)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                 GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.create_chart_output_checkbox.get(),
                                 GUI_util.charts_package_options_widget.get(),
                                 searchedCoNLLField_var.get(),
                                 searchField_kw_var.get(),
                                 postag_var.get(),
                                 deprel_var.get(),
                                 co_postag_var.get(),
                                 co_deprel_var.get(),
                                 Begin_K_sent_var.get(),
                                 End_K_sent_var.get())

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

GUI_label = 'Graphical User Interface (GUI) for CoNLL Table Analyzer'
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
config_input_output_numeric_options=[1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window = GUI_util.window
# config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
# config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

all_analyses = tk.StringVar()
searchField_kw_var = tk.StringVar()
searchedCoNLLField_var = tk.StringVar()
postag_var = tk.StringVar()
deprel_var = tk.StringVar()
co_postag_var = tk.StringVar()
co_postag_var = tk.StringVar()
co_deprel_var = tk.StringVar()
k_sentences_var = tk.IntVar()
Begin_K_sent_var = tk.IntVar()
End_K_sent_var = tk.IntVar()
csv_file_field_list = []

clausal_analysis_var = tk.IntVar()

compute_sentence_var = tk.IntVar()

all_analyses_var = tk.IntVar()

buildString = ''
menu_values = []
error = False

postag_menu = '*', 'JJ* - Any adjective', 'NN* - Any noun', 'VB* - Any verb', *sorted([k + " - " + v for k, v in Stanford_CoreNLP_tags_util.dict_POSTAG.items()])
deprel_menu = '*', *sorted([k + " - " + v for k, v in Stanford_CoreNLP_tags_util.dict_DEPREL.items()])

def clear(e):
    all_analyses_var.set(0)
    all_analyses_checkbox.configure(state='normal')
    all_analyses_menu.configure(state='disabled')
    all_analyses.set('*')
    search_token_var.set(0)
    searchField_kw_var.set('e.g.: father')
    postag_var.set('*')
    deprel_var.set('*')
    co_postag_var.set('*')
    co_postag_var.set('*')
    co_deprel_var.set('*')
    activate_all_options()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)


# custom sorter to place non alpha strings later while custom sorting
def custom_sort(s):
    if s:
        if s[0].isalpha():
            return 0
        else:
            return 10
    else:
        return 10


all_analyses_var = tk.IntVar()
all_analyses_checkbox = tk.Checkbutton(window, state='disabled', variable = all_analyses_var, text='Clause, noun, verb, function word',
                                onvalue=1, offvalue=0, command = lambda: activate_all_options())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                                    y_multiplier_integer, all_analyses_checkbox,True)

all_analyses.set('*')
all_analyses_menu = tk.OptionMenu(window, all_analyses, '*', 'Clause analysis', 'Noun analysis', 'Verb analysis', 'Function (junk/stop) words analysis')
all_analyses_menu.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               all_analyses_menu)

search_token_var = tk.IntVar()
searchToken_checkbox = tk.Checkbutton(window, state='disabled', variable=search_token_var,  text='Search token/word', onvalue=1,
                                  offvalue=0, command = lambda:  activate_all_options())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                                    y_multiplier_integer, searchToken_checkbox,True)

searchField_kw_var.set('e.g.: father')

# used to place noun/verb checkboxes starting at the top level
y_multiplier_integer_top = y_multiplier_integer

entry_searchField_kw = tk.Entry(window, width=GUI_IO_util.combobox_width, state='disabled', textvariable=searchField_kw_var)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,
    y_multiplier_integer,
    entry_searchField_kw,
    False, False, False, False, 90, GUI_IO_util.IO_configuration_menu,
    "Enter the CASE SENSITIVE word (ONE WORD ONLY) that you would like to search (* for any word). All searches are done WITHIN EACH SENTENCE for the EXACT word.")

# Search type var (FORM/LEMMA)
searchedCoNLLField_var.set('FORM')
searchedCoNLLdescription_csv_field_menu_lb = tk.Label(window, text='CoNLL search field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               searchedCoNLLdescription_csv_field_menu_lb,True)

searchedCoNLLdescription_csv_field_menu_lb = tk.OptionMenu(window, searchedCoNLLField_var, 'FORM', 'LEMMA')
searchedCoNLLdescription_csv_field_menu_lb.configure(width=GUI_IO_util.combobox_width, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               searchedCoNLLdescription_csv_field_menu_lb)

# POSTAG variable
postag_var.set('*')
POS_lb = tk.Label(window, text='POSTAG of searched token')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               POS_lb, True)

postag_menu_lb = ttk.Combobox(window, width = GUI_IO_util.combobox_width, textvariable = postag_var)
postag_menu_lb['values'] = postag_menu
postag_menu_lb.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               postag_menu_lb)

# DEPREL variable

deprel_var.set('*')
DEPREL_lb = tk.Label(window, text='DEPREL of searched token')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               DEPREL_lb, True)

deprel_menu_lb = ttk.Combobox(window, width = GUI_IO_util.combobox_width, textvariable = deprel_var)
deprel_menu_lb['values'] = deprel_menu
deprel_menu_lb.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               deprel_menu_lb)

# Co-Occurring POSTAG menu

co_postag_var.set('*')

POSTAG_CoOc_lb = tk.Label(window, text='POSTAG of co-occurring tokens')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               POSTAG_CoOc_lb, True)

co_postag_menu_lb = ttk.Combobox(window, width = GUI_IO_util.combobox_width, textvariable = co_postag_var)
co_postag_menu_lb['values'] = postag_menu
co_postag_menu_lb.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               co_postag_menu_lb)

co_deprel_menu = '*','acl - clausal modifier of noun (adjectival clause)', 'acl:relcl - relative clause modifier', 'acomp - adjectival complement', 'advcl - adverbial clause modifier', 'advmod - adverbial modifier', 'agent - agent', 'amod - adjectival modifier', 'appos - appositional modifier', 'arg - argument', 'aux - auxiliary', 'auxpass - passive auxiliary', 'case - case marking', 'cc - coordinating conjunction', 'ccomp - clausal complement with internal subject', 'cc:preconj - preconjunct','compound - compound','compound:prt - phrasal verb particle','conj - conjunct','cop - copula conjunction','csubj - clausal subject','csubjpass - clausal passive subject','dep - unspecified dependency','det - determiner','det:predet - predeterminer','discourse - discourse element','dislocated - dislocated element','dobj - direct object','expl - expletive','foreign - foreign words','goeswith - goes with','iobj - indirect object','list - list','mark - marker','mod - modifier','mwe - multi-word expression','name - name','neg - negation modifier','nn - noun compound modifier','nmod - nominal modifier','nmod:npmod - noun phrase as adverbial modifier','nmod:poss - possessive nominal modifier','nmod:tmod - temporal modifier','nummod - numeric modifier','npadvmod - noun phrase adverbial modifier','nsubj - nominal subject','nsubjpass - passive nominal subject','num - numeric modifier','number - element of compound number','parataxis - parataxis','pcomp - prepositional complement','pobj - object of a preposition','poss - possession modifier', 'possessive - possessive modifier','preconj - preconjunct','predet - predeterminer','prep - prepositional modifier','prepc - prepositional clausal modifier','prt - phrasal verb particle','punct - punctuation','quantmod - quantifier phrase modifier','rcmod - relative clause modifier','ref - referent','remnant - remnant in ellipsis','reparandum - overridden disfluency','ROOT - root','sdep - semantic dependent','subj - subject','tmod - temporal modifier','vmod - reduced non-finite verbal modifier','vocative - vocative','xcomp - clausal complement with external subject','xsubj - controlling subject','# - #'

co_deprel_var.set('*')
DEPREL_CoOc_lb = tk.Label(window, text='DEPREL of co-occurring tokens')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               DEPREL_CoOc_lb, True)

co_deprel_menu_lb = ttk.Combobox(window, width = GUI_IO_util.combobox_width, textvariable = co_deprel_var)
co_deprel_menu_lb['values'] = deprel_menu
co_deprel_menu_lb.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,co_deprel_menu_lb)

def changed_filename(tracedInputFile):
    global error
    if os.path.isfile(tracedInputFile):
        if not CoNLL_util.check_CoNLL(tracedInputFile):
            error = True
            return
        else:
            error = False
    else:
        error = True
    activate_all_options()
    clear("<Escape>")
# GUI_util.inputFilename.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))

k_sentences_var.set(0)
k_sentences_checkbox = tk.Checkbutton(window, text="Beginning-End K sentences analyzer (repetition finder)",
                              variable=k_sentences_var, onvalue=1, offvalue=0, command = lambda: activate_all_options())
# k_sentences_checkbox.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               k_sentences_checkbox,True)

Begin_K_sent_entry_lb = tk.Label(window,
                                    text='Begin K-sentences')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                               Begin_K_sent_entry_lb, True)

Begin_K_sent_entry = tk.Entry(window, textvariable=Begin_K_sent_var)
Begin_K_sent_entry.configure(width=GUI_IO_util.widget_width_extra_short, state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate+120,
                                               y_multiplier_integer,
                                               Begin_K_sent_entry, True, False, False, False, 90,
                                               GUI_IO_util.file_splitter_split_mergedFile_separator_entry_begin_pos,
                                               "Enter the beginning number of sentences to be analyzed in the CoNLL table for repeated elements")

End_K_sent_entry_lb = tk.Label(window,
                                    text='End K-sentences')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                               End_K_sent_entry_lb, True)

End_K_sent_entry = tk.Entry(window, textvariable=End_K_sent_var)
End_K_sent_entry.configure(width=GUI_IO_util.widget_width_extra_short, state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_setup_x_coordinate+110,
                                               y_multiplier_integer,
                                               End_K_sent_entry, False, False, False, False, 90,
                                               GUI_IO_util.file_splitter_split_mergedFile_separator_entry_end_pos,
                                               "Enter the end number of sentences to be analyzed in the CoNLL table for repeated elements")

compute_sentence_var.set(0)
sentence_table_checkbox = tk.Checkbutton(window, text='Compute sentence table', variable=compute_sentence_var,
                                         onvalue=1, offvalue=0, command = lambda: activate_all_options())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               sentence_table_checkbox)

extract_fromCoNLL = tk.Button(window, text='Extract other fields/data from CoNLL table (Open GUI)', command = lambda: call("python data_manipulation_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
    y_multiplier_integer,
    extract_fromCoNLL,
    False, False, False, False, 90, GUI_IO_util.read_button_x_coordinate,
    "Click on the button to open the Data manipulation GUI where you can use the function 'Extract field(s) from csv file' with several options for complex data queries of csv files (in this case, a CoNLL table).")

all_analyses_checkbox.configure(state='normal')
searchToken_checkbox.configure(state='normal')
sentence_table_checkbox.configure(state='normal')
k_sentences_checkbox.configure(state='normal')


def activate_all_options():
    # k sentences options
    Begin_K_sent_entry.configure(state='disabled')
    End_K_sent_entry.configure(state='disabled')

    if error:
        all_analyses_checkbox.configure(state='disabled')
        all_analyses_menu.configure(state='disabled')
        searchToken_checkbox.configure(state='disabled')
        sentence_table_checkbox.configure(state='disabled')
        sentence_table_checkbox.configure(state='disabled')
        k_sentences_checkbox.configure(state='disabled')
        return
    if all_analyses_var.get():
        all_analyses_menu.configure(state='normal')
        searchToken_checkbox.configure(state='disabled')
        sentence_table_checkbox.configure(state='disabled')
        sentence_table_checkbox.configure(state='disabled')
        k_sentences_checkbox.configure(state='disabled')
        reminders_util.checkReminder(config_filename,
                                     reminders_util.title_options_CoreNLP_nn_parser,
                                     reminders_util.message_CoreNLP_nn_parser,
                                     True)
    elif search_token_var.get()==True:
        all_analyses_checkbox.configure(state='disabled')
        sentence_table_checkbox.configure(state='disabled')
        k_sentences_checkbox.configure(state='disabled')

        entry_searchField_kw.configure(state='normal')
        searchedCoNLLdescription_csv_field_menu_lb.configure(state='normal')
        postag_menu_lb.configure(state='normal')
        deprel_menu_lb.configure(state='normal')
        co_postag_menu_lb.configure(state='normal')
        co_deprel_menu_lb.configure(state='normal')
    elif compute_sentence_var.get():
        all_analyses_checkbox.configure(state='disabled')
        searchToken_checkbox.configure(state='disabled')
        entry_searchField_kw.configure(state='disabled')
        searchedCoNLLdescription_csv_field_menu_lb.configure(state='disabled')
        postag_menu_lb.configure(state='disabled')
        deprel_menu_lb.configure(state='disabled')
        co_postag_menu_lb.configure(state='disabled')
        co_deprel_menu_lb.configure(state='disabled')
    elif k_sentences_var.get():
        all_analyses_checkbox.configure(state='disabled')
        searchToken_checkbox.configure(state='disabled')
        sentence_table_checkbox.configure(state='disabled')
        entry_searchField_kw.configure(state='disabled')
        searchedCoNLLdescription_csv_field_menu_lb.configure(state='disabled')
        postag_menu_lb.configure(state='disabled')
        deprel_menu_lb.configure(state='disabled')
        co_postag_menu_lb.configure(state='disabled')
        co_deprel_menu_lb.configure(state='disabled')
        sentence_table_checkbox.configure(state='disabled')
        Begin_K_sent_entry.configure(state='normal')
        End_K_sent_entry.configure(state='normal')
    else:
        all_analyses_checkbox.configure(state='normal')
        all_analyses_menu.configure(state='disabled')
        searchToken_checkbox.configure(state='normal')
        sentence_table_checkbox.configure(state='normal')
        k_sentences_checkbox.configure(state='normal')

activate_all_options()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'CoNLL Table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",
               'POSTAG (Part of Speech Tags)': "TIPS_NLP_POSTAG (Part of Speech Tags) Stanford CoreNLP.pdf",
               'DEPREL (Stanford Dependency Relations)': "TIPS_NLP_DEPREL (Dependency Relations) Stanford CoreNLP.pdf",
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',
               'Style Analysis': 'TIPS_NLP_Style Analysis.pdf', 'Clause Analysis': 'TIPS_NLP_Clause Analysis.pdf',
               'Noun Analysis': 'TIPS_NLP_Noun Analysis.pdf', 'Verb Analysis': 'TIPS_NLP_Verb Analysis.pdf',
               'Function Words Analysis': 'TIPS_NLP_Function Words Analysis.pdf',
               'Nominalization': 'TIPS_NLP_Nominalization.pdf', 'NLP Searches': "TIPS_NLP_NLP Searches.pdf",
               'Excel Charts': 'TIPS_NLP_Excel Charts.pdf',
               'Excel Enabling Macros': 'TIPS_NLP_Excel Enabling macros.pdf',
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
                'Statistical measures':'TIPS_NLP_Statistical measures.pdf',
               'Network Graphs (via Gephi)': 'TIPS_NLP_Gephi network graphs.pdf'}
TIPS_options = 'CoNLL Table', 'POSTAG (Part of Speech Tags)', 'DEPREL (Stanford Dependency Relations)', 'English Language Benchmarks', 'Style Analysis', 'Clause Analysis', 'Noun Analysis', 'Verb Analysis', 'Function Words Analysis', 'Nominalization', 'NLP Searches', 'Excel Charts', 'Excel Enabling Macros', 'Excel smoothing data series', 'Statistical measures', 'Network Graphs (via Gephi)'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.


def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_CoNLL)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox to analyze the CoNLL table for different types of clauses (e.g., noun-phrase, NP, verb phrase, VP), nouns (singular, plural, proper nouns, subject and object), verbs (modality, tense, voice), and functions words (or junk/stop words) (e.g., articles/determnants, auxiliaries, conjunctions, prepositions, pronouns)." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checbox to search the CoNLL table for a specific token/word. Enter the CASE SENSITIVE token (i.e., word) to be searched (enter * for any word). ENTER * TO SEARCH FOR ANY TOKEN/WORD. The EXACT word will be searched (e.g., if you enter 'American', any instances of 'America' will not be found).\n\nDO NOT USE QUOTES WHEN ENTERING A SEARCH TOKEN. n\nThe algorithm will search all the tokens related to this token in the CoNLL table. For example, if the the token wife is entered, the algorithm will search in each dependency tree (i.e., each sentence).\n\nIn OUTPUT the algorithm will produce several charts and a Gephi network graphs of the relationship between searched and co-occurring words." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, select the CoNLL field to be used for the search (FORM or LEMMA).\n\nFor example, if brother is entered as the searched token, and FORM is entered as search field, the algorithm will first search all occurrences of the FORM brother. Note that in this case brothers will NOT be considered. Otherwise, if LEMMA is entered as search field, the algorithm will search all occurences of the LEMMA brother. In this case, tokens with form brother and brothers will all be considered." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, select POSTAG value for searched token (e.g., NN for noun; RETURN for ANY POSTAG value)." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, select DEPREL value for searched token (e.g., nsubjpass for passive nouns that are subjects; RETURN for ANY DEPREL value)." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, select POSTAG value for token co-occurring in the same sentence (e.g., NN for noun; RETURN for ANY POSTAG value)." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, select DEPREL value for token co-occurring in the same sentence (e.g., DEPREL nsubjpass for passive nouns that are subjects; RETURN for ANY DEPREL value)." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to run the repetition finder to compute counts and proportions of nouns, verbs, adjectives, and proper nouns across selected K beginnning and ending sentences." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to compute a sentence table with various sentence statistics.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Click the button to open the Data manager GUI for more options on querying the CoNLL table." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, increment)

# change the value of the readMe_message
readMe_message = "This Python 3 script will allow you to analyze in depth the contents of the CoNLL table (CoNLL U format), the table produced by Stanford CoreNLP parser. You can do several things in this GUI.\n\nYou can get frequency distributions of various types of linguistic objects: clauses, nouns, verbs, and function words.\n\nYou can search all the tokens (i.e., words) related to a user-supplied keyword, found in either FORM or LEMMA of a user-supplied CoNLL table. You can filter your search by specific POSTAG and DEPREL values for both searched and co-occurring tokens (e.g., POSTAG ‘NN for nouns, DEPREL nsubjpass for passive nouns that are subjects.)\n\nYou can get frequency distributions of words and nouns, verbs, adjectives, and proper nouns in the first and last K sentences.\n\nIn INPUT the script expects a CoNLL table generated by the python script StanfordCoreNLP.py. \n\nIn OUTPUT the script creates a tab-separated csv file with a user-supplied filename and path.\n\nThe script also displays the same infomation in the command line." + GUI_IO_util.msg_multipleDocsCoNLL
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
scriptName=os.path.basename(__file__)

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief,scriptName,True)

if GUI_util.input_main_dir_path.get()!='' or (os.path.basename(GUI_util.inputFilename.get())[-4:] != ".csv"):
    GUI_util.run_button.configure(state='disabled')
    mb.showwarning(title='Input file',
                   message="The CoNLL Table Analyzer scripts require in input a csv CoNLL table created by the Stanford CoreNLP parser (not the spaCy and Stanza parsers).\n\nAll options and RUN button are disabled until the expected CoNLL file is seleted in input.\n\nPlease, select in input a CoNLL file created by the Stanford CoreNLP parser.")
    error = True
    activate_all_options()
else:
    GUI_util.run_button.configure(state='normal')
    if inputFilename.get()!='':
        if not CoNLL_util.check_CoNLL(inputFilename.get()):
            error = True
            activate_all_options()
GUI_util.inputFilename.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))

GUI_util.window.mainloop()
