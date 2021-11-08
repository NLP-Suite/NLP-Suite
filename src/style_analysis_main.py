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
import CoNLL_clause_analysis_util
import CoNLL_noun_analysis_util
import CoNLL_verb_analysis_util
import IO_csv_util
import IO_CoNLL_util
import sentence_analysis_util
import concreteness_analysis_util
import lib_util
import Excel_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir,openOutputFiles,createExcelCharts,
    CoNLL_table_analysis_var,
    complexity_readability_analysis_var,
    vocabulary_analysis_var,
    ngrams_analysis_var,
    CoNLL_table_analysis_menu_var,
    complexity_readability_analysis_menu_var,
    vocabulary_analysis_menu_var,
    ngrams_analysis_menu_var,
    gender_guesser_var):

    filesToOpen = []  # Store all files that are to be opened once finished

    if (CoNLL_table_analysis_var==False and
        complexity_readability_analysis_var == False and
        vocabulary_analysis_var == False and
        ngrams_analysis_var==False and
        gender_guesser_var==False):
        mb.showwarning('Warning','No options have been selected.\n\nPlease, select an option and try again.')
        return

    if CoNLL_table_analysis_var == True:
        withHeader = True
        recordID_position = 8
        documentId_position = 10
        data, header = IO_csv_util.get_csv_data(inputFilename, withHeader)
        if len(data) == 0:
            return
        data_divided_sents = IO_CoNLL_util.sentence_division(data)
        if data_divided_sents == None:
            return
        if len(data_divided_sents) == 0:
            return

        if 'Clauses' in CoNLL_table_analysis_menu_var or '*' in CoNLL_table_analysis_menu_var:
            tempfilesToOpen = CoNLL_clause_analysis_util.clause_stats(inputFilename, inputDir, outputDir, data,
                                                                      data_divided_sents, openOutputFiles,
                                                                      createExcelCharts)
            # only open the chart files
            # add line plots eventually
            filesToOpen.append(tempfilesToOpen[1])
            filesToOpen.append(tempfilesToOpen[2])

        if 'Nouns' in CoNLL_table_analysis_menu_var or '*' in CoNLL_table_analysis_menu_var:
            tempfilesToOpen = CoNLL_noun_analysis_util.noun_stats(inputFilename, outputDir, data, data_divided_sents,
                                                                  openOutputFiles, createExcelCharts)
            # only open the chart files
            # add line plots eventually
            filesToOpen.append(tempfilesToOpen[6])
            filesToOpen.append(tempfilesToOpen[7])
            filesToOpen.append(tempfilesToOpen[8])

        if 'Verbs' in CoNLL_table_analysis_menu_var or '*' in CoNLL_table_analysis_menu_var:
            tempfilesToOpen = CoNLL_verb_analysis_util.verb_voice_stats(inputFilename, outputDir, data,
                                                                        data_divided_sents, openOutputFiles,
                                                                        createExcelCharts)
            # only open the chart files
            # add line plots eventually
            filesToOpen.append(tempfilesToOpen[2])
            tempfilesToOpen = CoNLL_verb_analysis_util.verb_modality_stats(inputFilename, outputDir, data,
                                                                           data_divided_sents, openOutputFiles,
                                                                           createExcelCharts)
            filesToOpen.append(tempfilesToOpen[2])
            tempfilesToOpen = CoNLL_verb_analysis_util.verb_tense_stats(inputFilename, outputDir, data,
                                                                        data_divided_sents, openOutputFiles,
                                                                        createExcelCharts)
            filesToOpen.append(tempfilesToOpen[1])

        if 'Function' in CoNLL_table_analysis_menu_var or '*' in CoNLL_table_analysis_menu_var:
            # only open the chart files
            # add line plots eventually
            import CoNLL_function_words_analysis_util
            tempfilesToOpen = CoNLL_function_words_analysis_util.article_stats(inputFilename, outputDir, data,
                                                                               data_divided_sents, openOutputFiles,
                                                                               createExcelCharts)
            filesToOpen.append(tempfilesToOpen[2])
            tempfilesToOpen = CoNLL_function_words_analysis_util.auxiliary_stats(inputFilename, outputDir, data,
                                                                                 data_divided_sents, openOutputFiles,
                                                                                 createExcelCharts)
            filesToOpen.append(tempfilesToOpen[2])
            tempfilesToOpen = CoNLL_function_words_analysis_util.conjunction_stats(inputFilename, outputDir, data,
                                                                                   data_divided_sents, openOutputFiles,
                                                                                   createExcelCharts)
            filesToOpen.append(tempfilesToOpen[2])
            tempfilesToOpen = CoNLL_function_words_analysis_util.preposition_stats(inputFilename, outputDir, data,
                                                                                   data_divided_sents, openOutputFiles,
                                                                                   createExcelCharts)
            filesToOpen.append(tempfilesToOpen[2])
            tempfilesToOpen = CoNLL_function_words_analysis_util.pronoun_stats(inputFilename, outputDir, data,
                                                                               data_divided_sents, openOutputFiles,
                                                                               createExcelCharts)
            filesToOpen.append(tempfilesToOpen[2])

        if 'POSTAG' in CoNLL_table_analysis_menu_var or 'DEPREL' in CoNLL_table_analysis_menu_var or 'NER' in CoNLL_table_analysis_menu_var:
            mb.showwarning('Warning','The selected option is not available yet.\n\nSorry!')
            return

        if CoNLL_table_analysis_menu_var=='':
            mb.showwarning('Warning', 'No option has been selected for CoNLL table analysis.\n\nPlease, select an option and try again.')
            return

        mb.showwarning(title='Output files',
                       message="The analysis of the CoNLL table for clauses, nouns, verbs, and function words opens only the Excel chart files. But the script produces in output many more csv files.\n\nPlease, check your output directory for more file output.")

    if complexity_readability_analysis_var == True:
        if 'Sentence' in complexity_readability_analysis_menu_var:
            if IO_libraries_util.inputProgramFileCheck('statistics_txt_util.py') == False:
                return
            filesToOpen = sentence_analysis_util.sentence_complexity(GUI_util.window, inputFilename,
                                                                     inputDir, outputDir,
                                                                     openOutputFiles, createExcelCharts)
            if filesToOpen == None:
                return

        elif 'Text' in complexity_readability_analysis_menu_var:
            if IO_libraries_util.inputProgramFileCheck('statistics_txt_util.py') == False:
                return
            sentence_analysis_util.sentence_text_readability(GUI_util.window, inputFilename, inputDir,
                                                             outputDir, openOutputFiles, createExcelCharts)
        elif 'tree' in complexity_readability_analysis_menu_var:
            # if inputFilename == '' and inputFilename.strip()[-4:] != '.txt':
            #     mb.showwarning(title='Input file error',
            #                    message='The Sentence tree viewer script requires a single txt file in input.\n\nPlease, select a txt file and try again.')
            #     return
            # IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
            #                                    'Started running Sentence visualization: Dependency tree viewer (png graphs) at',
            #                                    True, '\n\nYou can follow Sentence Complexity in command line.')
            # subprocess.call(['java', '-jar', 'DependenSee.Jar', inputFilename, outputDir])

            sentence_analysis_util.sentence_structure_tree(inputFilename, outputDir)
        else:
            mb.showwarning('Warning', 'No option has been selected for Complex/readability analysis.\n\nPlease, select an option and try again.')
            return

    if vocabulary_analysis_var == True:
        if vocabulary_analysis_menu_var=='':
            mb.showwarning('Warning', 'No option has been selected for Vocabulary analysis.\n\nPlease, select an option and try again.')
            return
        if 'Repetition' in vocabulary_analysis_menu_var:
            mb.showwarning('Warning', 'The selected option is not available yet.\n\nSorry!')
            return
        if '*' == vocabulary_analysis_menu_var:
            filesToOpen = file_spell_checker_util.language_detection(window, inputFilename, inputDir, outputDir,
                                                                   openOutputFiles, createExcelCharts)
        if '*' == vocabulary_analysis_menu_var:
            filesToOpen = statistics_txt_util.process_words(window, inputFilename, inputDir, outputDir,
                                                                   openOutputFiles, createExcelCharts)
            # if len(tempOutputfile)>0:
            #     filesToOpen.extend(tempOutputfile)
        elif 'detection' in vocabulary_analysis_menu_var:
                filesToOpen = file_spell_checker_util.language_detection(window, inputFilename, inputDir, outputDir,
                                                                         openOutputFiles, createExcelCharts)
        elif 'capital' in vocabulary_analysis_menu_var:
            filesToOpen = statistics_txt_util.process_words(window, inputFilename, inputDir, outputDir,
                                                                   openOutputFiles, createExcelCharts,'capital')
        elif 'Short' in vocabulary_analysis_menu_var:
            filesToOpen=statistics_txt_util.process_words(window,inputFilename,inputDir, outputDir, openOutputFiles, createExcelCharts,'short')
        elif 'Vowel' in vocabulary_analysis_menu_var:
            filesToOpen = statistics_txt_util.process_words(window, inputFilename, inputDir, outputDir, openOutputFiles, createExcelCharts,'vowel')
        elif 'Punctuation' in vocabulary_analysis_menu_var:
            filesToOpen=statistics_txt_util.process_words(window,inputFilename, inputDir, outputDir, openOutputFiles, createExcelCharts,'punctuation')
        if '*' == vocabulary_analysis_menu_var or 'Yule' in vocabulary_analysis_menu_var:
            statistics_txt_util.yule(window, inputFilename, inputDir, outputDir)
        if '*' == vocabulary_analysis_menu_var or '*' == vocabulary_analysis_menu_var or 'Unusual' in vocabulary_analysis_menu_var:
            tempFiles=file_spell_checker_util.nltk_unusual_words(window, inputFilename, inputDir, outputDir, False, createExcelCharts)
            if len(tempFiles)>0:
                filesToOpen.extend(tempFiles)
        if '*' == vocabulary_analysis_menu_var or 'Abstract' in vocabulary_analysis_menu_var:
            # ABSTRACT/CONCRETENESS _______________________________________________________
            mode = "both" # mean, median, both (calculates both mean and median)
            if lib_util.checklibFile(
                    GUI_IO_util.concreteness_libPath + os.sep + 'Concreteness_ratings_Brysbaert_et_al_BRM.csv',
                    'concreteness_analysis_util.py') == False:
                return
            if IO_libraries_util.inputProgramFileCheck('concreteness_analysis_util.py') == False:
                return
            IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start',
                                               'Started running CONCRETENESS Analysis at', True)
            if len(inputFilename) > 0:
                outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir,outputDir, '.csv', 'SC',
                                                                         'Concreteness', '', '', '', False, True)
            else:
                outputFilename = IO_files_util.generate_output_file_name(inputDir, inputDir, outputDir, '.csv', 'SC_dir',
                                                                         'Concreteness', '', '', '', False, True)

            concreteness_analysis_util.main(inputFilename, inputDir, outputDir, outputFilename, mode)

            filesToOpen.append(outputFilename)
            if createExcelCharts == True:
                inputFilename=outputFilename
                if mode == "both":
                    columns_to_be_plotted = [[2, 4], [2, 5]]
                    hover_label = ['Sentence', 'Sentence']
                else:
                    columns_to_be_plotted = [[2, 4]]
                    hover_label = ['Sentence']
                Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                          outputFileLabel='Concret',
                                                          chart_type_list=["line"],
                                                          chart_title='Concreteness Scores by Sentence Index',
                                                          column_xAxis_label_var='Sentence index',
                                                          hover_info_column_list=hover_label,
                                                          count_var=0,
                                                          column_yAxis_label_var='Scores')
                if Excel_outputFilename != "":
                    filesToOpen.append(Excel_outputFilename)

                # outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                #                                     outputFilename, chart_type_list=["line"],
                #                                     chart_title="Concreteness Scores by Sentence Index",
                #                                     column_xAxis_label_var='Sentence index',
                #                                     column_yAxis_label_var='Frequency of concreteness scores',
                #                                     outputExtension='.xlsm', label1='SC', label2='Concreteness',
                #                                     label3='line', label4='chart', label5='', useTime=False,
                #                                     disable_suffix=True,
                #                                     count_var=0, column_yAxis_field_list=[],
                #                                     reverse_column_position_for_series_label=False,
                #                                     series_label_list=[''], second_y_var=0,
                #                                     second_yAxis_label='', hover_var=1,
                #                                     hover_info_column_list=hover_label)
                # if outputFilename != "":
                #     filesToOpen.append(outputFilename)

            IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
                                                   'Finished running CONCRETENESS Analysis at', True, '', True, startTime)

    if ngrams_analysis_var == True:
        if 'Character' in ngrams_analysis_menu_var or 'Word' in ngrams_analysis_menu_var:
            if 'Character' in ngrams_analysis_menu_var:
                ngramType=0
            else:
                ngramType = 1
            IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'N-Grams analysis start',
                                               'Started running Word/Characters N-Grams at',
                                               True, '', True, '', True)
            # (inputFilename = ''  # for now we only process a whole directory
            if IO_libraries_util.inputProgramFileCheck('statistics_txt_util.py') == False:
                return
            ngramsNumber=4
            normalize = False
            excludePunctuation = False

            statistics_txt_util.compute_character_word_ngrams(GUI_util.window, inputFilename, inputDir,
                                                              outputDir, ngramsNumber, normalize, excludePunctuation, ngramType, openOutputFiles,
                                                              createExcelCharts,
                                                              bySentenceIndex_var)
            IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'N-Grams analysis end',
                                               'Finished running Word/Characters N-Grams at', True, '', True, startTime, True)
        elif 'Hapax' in ngrams_analysis_menu_var:
            ngramsNumber=1
            ngramType = 1
            normalize = False
            excludePunctuation = False

            statistics_txt_util.compute_character_word_ngrams(GUI_util.window, inputFilename, inputDir,
                                                              outputDir, ngramsNumber, normalize, excludePunctuation, ngramType, openOutputFiles,
                                                              createExcelCharts,
                                                              bySentenceIndex_var)
        elif 'POSTAG' in ngrams_analysis_menu_var:
            mb.showwarning('Warning','The selected option is not available yet.\n\nSorry!')
            return
        elif 'DEPREL' in ngrams_analysis_menu_var:
            mb.showwarning('Warning','The selected option is not available yet.\n\nSorry!')
            return
        elif 'NER' in ngrams_analysis_menu_var:
            mb.showwarning('Warning','The selected option is not available yet.\n\nSorry!')
            return
        else:
            mb.showwarning('Warning', 'No option has been selected for N-grams analysis.\n\nPlease, select an option and try again.')
            return

    if gender_guesser_var==True:
        IO_files_util.runScript_fromMenu_option('Gender guesser', 0, inputFilename, inputDir, outputDir,
                                  openOutputFiles, createExcelCharts)
        return

    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_Excel_chart_output_checkbox.get(),
                                CoNLL_table_analysis_var.get(),
                                complexity_readability_analysis_var.get(),
                                vocabulary_analysis_var.get(),
                                ngrams_analysis_var.get(),
                                CoNLL_table_analysis_menu_var.get(),
                                complexity_readability_analysis_menu_var.get(),
                                vocabulary_analysis_menu_var.get(),
                                ngrams_analysis_menu_var.get(),
                                gender_guesser_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_width=GUI_IO_util.get_GUI_width(3)
GUI_height=550 # height of GUI with full I/O display

if IO_setup_display_brief:
    GUI_height = GUI_height - 80
    y_multiplier_integer = GUI_util.y_multiplier_integer  # IO BRIEF display
    increment=0 # used in the display of HELP messages
else: # full display
    # GUI CHANGES add following lines to every special GUI
    # +3 is the number of lines starting at 1 of IO widgets
    # y_multiplier_integer=GUI_util.y_multiplier_integer+2
    y_multiplier_integer = GUI_util.y_multiplier_integer + 2  # IO FULL display
    increment=2

GUI_size = str(GUI_width) + 'x' + str(GUI_height)

GUI_label='Graphical User Interface (GUI) for Style Analysis'
config_filename='style-analysis-config.txt'
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
config_option=[0,6,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename,config_option)

window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_options,config_filename,IO_setup_display_brief)

def clear(e):
    CoNLL_table_analysis_checkbox.configure(state='normal')
    complexity_readability_analysis_checkbox.configure(state='normal')
    vocabulary_analysis_checkbox.configure(state='normal')
    ngrams_analysis_checkbox.configure(state='normal')

    CoNLL_table_analysis_var.set(0)
    complexity_readability_analysis_var.set(0)
    vocabulary_analysis_var.set(0)
    ngrams_analysis_var.set(0)

    CoNLL_table_analysis_menu_var.set('')
    complexity_readability_analysis_menu_var.set('')
    vocabulary_analysis_menu_var.set('')
    ngrams_analysis_menu_var.set('')

    CoNLL_table_analysis_menu.configure(state='disabled')
    complexity_readability_analysis_menu.configure(state='disabled')
    vocabulary_analysis_menu.configure(state='disabled')
    ngrams_analysis_menu.configure(state='disabled')

    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

# GUI CHANGES cut/paste special GUI widgets from GUI_util

bySentenceIndex_var=tk.IntVar()

CoNLL_table_analysis_var=tk.IntVar()
complexity_readability_analysis_var=tk.IntVar()
vocabulary_analysis_var=tk.IntVar()
ngrams_analysis_var=tk.IntVar()
gender_guesser_var=tk.IntVar()

CoNLL_table_analysis_menu_var=tk.StringVar()
complexity_readability_analysis_menu_var=tk.StringVar()
vocabulary_analysis_menu_var=tk.StringVar()
ngrams_analysis_menu_var=tk.StringVar()

bySentenceIndex_var.set(0)
bySentenceIndex_checkbox = tk.Checkbutton(window, text='By sentence index', variable=bySentenceIndex_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,bySentenceIndex_checkbox)

CoNLL_table_analysis_var.set(0)
CoNLL_table_analysis_checkbox = tk.Checkbutton(window, text='CoNLL table analysis', variable=CoNLL_table_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,CoNLL_table_analysis_checkbox,True)

CoNLL_table_analysis_lb = tk.Label(window, text='Select the CoNLL table analysis you wish to perform')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(),y_multiplier_integer,CoNLL_table_analysis_lb,True)
CoNLL_table_analysis_menu = tk.OptionMenu(window,CoNLL_table_analysis_menu_var,'*','Clauses','Nouns','Verbs','Function words','DEPREL','POSTAG','NER')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+400, y_multiplier_integer,CoNLL_table_analysis_menu)

complexity_readability_analysis_var.set(0)
complexity_readability_analysis_checkbox = tk.Checkbutton(window, text='Complexity/readability analysis', variable=complexity_readability_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,complexity_readability_analysis_checkbox,True)

complexity_readability_analysis_lb = tk.Label(window, text='Select the complexity/readability analysis you wish to perform')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(),y_multiplier_integer,complexity_readability_analysis_lb,True)
complexity_readability_analysis_menu = tk.OptionMenu(window,complexity_readability_analysis_menu_var,'*','Sentence complexity','Text readability','Visualize sentence structure (via dependency tree)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+400, y_multiplier_integer,complexity_readability_analysis_menu)

vocabulary_analysis_var.set(0)
vocabulary_analysis_checkbox = tk.Checkbutton(window, text='Vocabulary analysis', variable=vocabulary_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,vocabulary_analysis_checkbox,True)

vocabulary_analysis_lb = tk.Label(window, text='Select the vocabulary analysis you wish to perform')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(),y_multiplier_integer,vocabulary_analysis_lb,True)
vocabulary_analysis_menu = tk.OptionMenu(window,vocabulary_analysis_menu_var,'*','Abstract/concrete vocabulary','Vocabulary richness (word type/token ratio or Yule’s K)','Punctuation as figures of pathos (? !)','Short words (<4 characters)','Vowel words','Words with capital initial (proper nouns)','Unusual words (via NLTK)','Language detection','Repetition: Last N words of a sentence/First N words of next sentence','Repetition across sentences (special ngrams)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+400, y_multiplier_integer,vocabulary_analysis_menu)

ngrams_analysis_var.set(0)
ngrams_analysis_checkbox = tk.Checkbutton(window, text='N-grams analysis', variable=ngrams_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,ngrams_analysis_checkbox,True)

ngrams_lb = tk.Label(window, text='Select the n-grams analysis you wish to perform')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(),y_multiplier_integer,ngrams_lb,True)
ngrams_analysis_menu = tk.OptionMenu(window,ngrams_analysis_menu_var,'*','Characters','Words','Hapax legomena (once-occurring words)','DEPREL','POSTAG','NER','Repetition of words (last N words of a sentence/first N words of next sentence)','Repetition of words across sentences (special ngrams)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+400, y_multiplier_integer,ngrams_analysis_menu)

gender_guesser_var.set(0)
gender_guesser_checkbox = tk.Checkbutton(window, text='Who wrote the text - Gender guesser', variable=gender_guesser_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,gender_guesser_checkbox)

def activate_options(*args):
    if CoNLL_table_analysis_var.get()==True:
        CoNLL_table_analysis_menu.configure(state='normal')
        complexity_readability_analysis_checkbox.configure(state='disabled')
        vocabulary_analysis_checkbox.configure(state='disabled')
        ngrams_analysis_checkbox.configure(state='disabled')
        complexity_readability_analysis_menu.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
        ngrams_analysis_menu.configure(state='disabled')
    elif complexity_readability_analysis_var.get()==True:
        complexity_readability_analysis_menu.configure(state='normal')
        CoNLL_table_analysis_checkbox.configure(state='disabled')
        vocabulary_analysis_checkbox.configure(state='disabled')
        ngrams_analysis_checkbox.configure(state='disabled')
        CoNLL_table_analysis_menu.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
        ngrams_analysis_menu.configure(state='disabled')
    elif vocabulary_analysis_var.get()==True:
        vocabulary_analysis_menu.configure(state='normal')
        CoNLL_table_analysis_checkbox.configure(state='disabled')
        complexity_readability_analysis_checkbox.configure(state='disabled')
        ngrams_analysis_checkbox.configure(state='disabled')
        CoNLL_table_analysis_menu.configure(state='disabled')
        complexity_readability_analysis_menu.configure(state='disabled')
        ngrams_analysis_menu.configure(state='disabled')
    elif ngrams_analysis_var.get() == True:
        ngrams_analysis_menu.configure(state='normal')
        CoNLL_table_analysis_checkbox.configure(state='disabled')
        complexity_readability_analysis_checkbox.configure(state='disabled')
        vocabulary_analysis_checkbox.configure(state='disabled')
        CoNLL_table_analysis_menu.configure(state='disabled')
        complexity_readability_analysis_menu.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
    else:
        CoNLL_table_analysis_checkbox.configure(state='normal')
        complexity_readability_analysis_checkbox.configure(state='normal')
        vocabulary_analysis_checkbox.configure(state='normal')
        ngrams_analysis_checkbox.configure(state='normal')

        CoNLL_table_analysis_menu.configure(state='disabled')
        complexity_readability_analysis_menu.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
        ngrams_analysis_menu.configure(state='disabled')

CoNLL_table_analysis_var.trace('w',activate_options)
complexity_readability_analysis_var.trace('w',activate_options)
vocabulary_analysis_var.trace('w',activate_options)
ngrams_analysis_var.trace('w',activate_options)

activate_options()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Style analysis':'TIPS_NLP_Style analysis.pdf','Clause analysis':'TIPS_NLP_Clause analysis.pdf','Sentence complexity':'TIPS_NLP_Sentence complexity.pdf','Text readability':'TIPS_NLP_Text readability.pdf','CoNLL Table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf", 'POSTAG (Part of Speech Tags)': "TIPS_NLP_POSTAG (Part of Speech Tags) Stanford CoreNLP.pdf", 'DEPREL (Stanford Dependency Relations)': "TIPS_NLP_DEPREL (Dependency Relations) Stanford CoreNLP.pdf", 'NLP Searches': "TIPS_NLP_NLP Searches.pdf",'N-Grams (word & character)':"TIPS_NLP_Ngrams (word & character).pdf",'NLP Ngram and Word Co-Occurrence VIEWER':"TIPS_NLP_Ngram and Word Co-Occurrence VIEWER.pdf",'Google Ngram Viewer':'TIPS_NLP_Ngram Google Ngram Viewer.pdf','Language concreteness':'TIPS_NLP_Language concreteness analysis.pdf','Yule measures of vocabulary richness':'TIPS_NLP_Yule - Measures of vocabulary richness.pdf'}
TIPS_options='Style analysis', 'Clause analysis', 'Sentence complexity', 'Text readability','CoNLL Table', 'POSTAG (Part of Speech Tags)', 'DEPREL (Stanford Dependency Relations)','NLP Searches','N-Grams (word & character)','NLP Ngram and Word Co-Occurrence VIEWER','Google Ngram Viewer','Language concreteness','Yule measures of vocabulary richness'
# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    if not IO_setup_display_brief:
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",GUI_IO_util.msg_csv_txtFile)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_corpusData)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help",GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+1),"Help",'Please, tick the \'By sentence index\' checkbox if you wish to analyze any selected option with sentence information.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+2),"Help",'Please, tick the \'CoNLL table analysis\' checkbox if you wish to analyze various items in the CoNLL table.\n\nUse the dropdown menu to select the type of analysis to run.\n\n   1. Clause\n   2. Noun\n   3. Verb\n   4. Function word\n   5. DEPREL\n   6. POSTAG\n   7. NER.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+3),"Help",'Please, tick the \'Complex\\readability analysis\' checkbox if you wish to analyze the complexity or readability of sentences and documents.\n\nUse the dropdown menu to select the type of analysis to run.\n\n   1. Sentence complexity to provide different measures of sentence complexity: Yngve Depth, Frazer Depth, and Frazer Sum. These measures are closely associated to the sentence clause structure. The Frazier and Yngve scores are very similar, with one key difference: while the Frazier score measures the depth of a syntactic tree, the Yngve score measures the breadth of the tree.\n\n   2. Text readability to compute various measures of text readability.\n 12 readability score requires HIGHSCHOOL education;\n 16 readability score requires COLLEGE education;\n 18 readability score requires MASTER education;\n 24 readability score requires DOCTORAL education;\n >24 readability score requires POSTDOC education.\n\n   3. Visualize the sentence tree as a png image, using spacy and nltk.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+4),"Help",'Please, tick the \'Vocabulary analysis\' checkbox if you wish to analyze the vocabulary used in your corpus.\n\nUse the dropdown menu to select the type of analysis to run.\n\n   1. Abstract/concrete vocabulary, The script uses the concreteness ratings by Brysbaert, Warriner, Kuperman, Concreteness Ratings for 40 Thousand Generally Known English Word Lemmas, Behavioral Research (2014) 46:904–911.\nMean/median Concreteness values are calculated for each sentence on a 5-point scale going from abstract (0) to concrete (5).\n\n   2. Vocabulary richness (word type/token ratio or Yule’s K). C.U. Yule. 1944. The statistical study of literary vocabulary. Cambridge: Cambridge University Press.\n\n   3. Short words to compute the number of short words (<4 characters) and list them.\n\n   4. Vowel words to compute the number of words that start with a vowel (vowel words) and list them.\n\n   5. Unusual, or misspelled, words (via NLTK).\n\n   6. Language detection. Language detection is carried out via LANGDETECT, LANGID, SPACY. Languages are exported via the ISO 639 two-letter code. ISO 639 is a standardized nomenclature used to classify languages (check here for the list https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+5),"Help",'Please, tick the \'N-grams analysis\' checkbox if you wish to compute various types of n-grams.\n\nUse the dropdown menu to select the type of analysis to run.\n\n   1. Characters\n   2. Words\n   3. Hapax legomena (once-occurring words)\n   4. DEPREL\n   5. POSTAG\n   6. NER.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+6),"Help",'Please, tick the \'Who wrote the text\' checkbox if you wish to run the Gender Guesser algorithm to determine an author\'s gender based on the words used.\n\nYou will need to copy and paste a document content to the website http://www.hackerfactor.com/GenderGuesser.php#About\n\nYou need to be connnected to the internet.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+7),"Help",GUI_IO_util.msg_openOutputFiles)
help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The Python 3 scripts analyze different aspects of style, from the analysis of CoNLL table tags (POSTAG, DEPREL, NER), to sentence complexity and readability, vocabulary analysis (short and vowel words, abstract/concrete words, unusual words, vocabulary richness (Yule\'s K)), N-grams." + GUI_IO_util.msg_multipleDocsCoNLL
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief)

GUI_util.window.mainloop()

