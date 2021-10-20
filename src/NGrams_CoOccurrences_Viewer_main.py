import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "Ngrams-CoOccurrence_Viewer",
                                ['subprocess', 'os', 'tkinter', 'datetime','pandas','glob']) == False:
    sys.exit(0)

import os
import subprocess
import tkinter as tk
import tkinter.messagebox as mb
import glob
import datetime
import pandas as pd

import IO_user_interface_util
import GUI_IO_util
import IO_files_util
import Excel_util
import statistics_txt_util
import reminders_util
import IO_csv_util
import NGrams_CoOccurrences_Viewer_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def processSearchWords(inputStr):
    word_list = []
    if inputStr.find("\"") == -1:
        # no quotation mark
        word_list += inputStr.split(",")
    else:
        # contains quotation mark
        curWord = ""
        i = 0
        while i < len(inputStr):
            if inputStr[i] == " ":
                if curWord != "":
                    word_list.append(curWord)
                curWord = ""
            elif inputStr[i] == "\"":
                endIndex = inputStr.index("\"", i + 1)
                word_list.append(inputStr[i + 1: endIndex])
                i = endIndex
            else:
                curWord = curWord + inputStr[i]
            i += 1
    return word_list


def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def run(inputFilename, inputDir, outputDir, openOutputFiles, createExcelCharts,
        n_grams_var,
        n_grams_menu_var,
        n_grams_list,
        n_grams_viewer_var,
        CoOcc_Viewer_var,
        search_words,
        date_options,
        temporal_aggregation,
        date_format,
        date_separator_var,
        date_position_var,
        viewer_list):
    # print(date_options, temporal_aggregation, date_format, date_separator_var, date_position_var)
    filesToOpen = []


    total_file_number = 0
    error_file_number = 0
    error_filenames = []
    error_flag = False

    if n_grams_var==False and n_grams_viewer_var==False and CoOcc_Viewer_var==False:
        mb.showwarning(title='Warning',
                       message='There are no options selected.\n\nPlease, select one of the available options and try again.')
        return
    if inputDir=='' and (n_grams_viewer_var==True or CoOcc_Viewer_var==True):
        mb.showwarning(title='Warning',
                       message='You have selected to run the Viewer option but... this option requires a directory of txt files in input. Your configuration specifies a single txt file in input.\n\nPlease, select a directory in input or deselect the Viewer option and try again.')
        return

    if date_options:
        new_date_format = date_format.replace('yyyy', '%Y').replace('mm', '%m').replace('dd', '%d')
        for folder, subs, files in os.walk(inputDir):
            for filename in files:
                if not filename.endswith('.txt'):
                    continue
                filename = filename.replace('.txt', '')
                total_file_number = total_file_number + 1
                try:
                    date_text = ''
                    date_text = filename.split(date_separator_var)[date_position_var - 1]
                except: # if a file in the folder has no date it will break the code
                    pass
                try:
                    datetime.datetime.strptime(date_text, new_date_format)
                except ValueError:
                    error_file_number = error_file_number + 1
                    error_filenames.append(IO_csv_util.dressFilenameForCSVHyperlink(os.path.join(folder, filename+'.txt')))
                    error_flag = True

    if error_flag:
        df = pd.DataFrame(error_filenames, columns=['File with date not in position ' + str(date_position_var)])
        error_output = IO_files_util.generate_output_file_name('',inputDir, outputDir, '.csv',
                                                         'Date_position_errors_file')
        df.to_csv(error_output, index=False)
        mb.showwarning(title='Warning',
                       message='There are ' + str(error_file_number) + ' files out of ' + str(
                           total_file_number) + ' processed in the selected input directory with errors in either the date format or the date position. \n\nThe selected date format is '+ str(date_format)+' and the selected date position is ' + str(date_position_var) + '.\n\nClick OK to open a csv file with a list of files with erroneous dates. Check carefully, both date format and date position. Any erroneous file will need to be fixed or removed from the input directory before processing. You may also simply need to select a different date format and/or date position.')
        filesToOpen.append(error_output)
        if openOutputFiles == True:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
        return



# COMPUTE Ngrams ______________________________________________________________________________

    if n_grams_var:
        n_grams_word_var = False
        n_grams_character_var = False
        normalize = False
        n_grams_size = 3  # default number of n_grams
        excludePunctuation = False
        bySentenceIndex_word_var = False
        bySentenceIndex_character_var = False
        if n_grams_menu_var=="Word":
            n_grams_word_var=True
        else:
            n_grams_character_var=True
        bySentenceIndex_character_var = False
        if 'Hapax' in str(n_grams_list):
            n_grams_size = 1
        if 'punctuation' in str(n_grams_list):
            excludePunctuation=True
        if 'sentence index' in str(n_grams_list):
            if n_grams_menu_var == "Word":
                bySentenceIndex_word_var=True
            else:
                bySentenceIndex_character_var=True

        if n_grams_word_var or n_grams_character_var or bySentenceIndex_word_var or bySentenceIndex_character_var:
            if IO_libraries_util.inputProgramFileCheck('statistics_txt_util.py') == False:
                return

        if n_grams_word_var or bySentenceIndex_word_var:
            statistics_txt_util.compute_character_word_ngrams(GUI_util.window, inputFilename, inputDir,
                                                              outputDir, n_grams_size, normalize, excludePunctuation, 1, openOutputFiles, createExcelCharts,
                                                              bySentenceIndex_word_var)
        if n_grams_character_var or bySentenceIndex_character_var:
            statistics_txt_util.compute_character_word_ngrams(GUI_util.window, inputFilename, inputDir,
                                                              outputDir, n_grams_size, normalize, excludePunctuation, 0, openOutputFiles, createExcelCharts,
                                                              bySentenceIndex_character_var)

# VIEWER ____________________________________________________________________________________________

    if (n_grams_viewer_var == False and CoOcc_Viewer_var == False):
        return

    if (n_grams_viewer_var ==True or CoOcc_Viewer_var==True) and (createExcelCharts==False):
        mb.showwarning(title='Warning',
                       message='The checkbox to compute Excel charts is unticked. Since the VIEWER produces Excel charts as output, the script will abort.\n\nPlease, tick the checkbox to produce Excel charts and try again.')
        return

    txtCounter = len(glob.glob1(inputDir, "*.txt"))
    if txtCounter == 0:
        mb.showwarning(title='Warning',
                       message='There are no files with txt extension in the selected directory.\n\nPlease, select a different directory and try again.')
        return

    if txtCounter == 1:
        mb.showwarning(title='Warning',
                       message='There is only one file with txt extension in the selected directory. The script requires at least two files.\n\nPlease, select a different directory and try again.')
        return

    if (n_grams_viewer_var or CoOcc_Viewer_var):
        if IO_libraries_util.inputProgramFileCheck('NGrams_CoOccurrences_Viewer.jar') == False:
            return
        # errorFound, error_code, system_output=IO_libraries_util.check_java_installation('Ngram/CoOccurrence Viewer')
        # if errorFound:
        #     return

    # if ' ' in search_words and not "\"" in search_words:
    #     mb.showwarning(title='Warning',
    #                    message='Values entered in the search bar should be comma-separated, not blank-separated (e.g., woman, man, and not woman man).\n\nPlease, check your search bar values and try again.')
    #     return

    if search_words != '' and n_grams_viewer_var == False and CoOcc_Viewer_var == False:
        mb.showwarning(title='Warning',
                       message="You have entered the string '" + search_words + "' in the Search widget but you have not selected which Viewer you wish to use, Ngram or Co-Occurrence.\n\nPlease, select an option and try again.")
        return

    if search_words == '' and (n_grams_viewer_var == True or CoOcc_Viewer_var == True):
        mb.showwarning(title='Warning',
                       message="You have selected to run a Viewer but you have not entered any search strings in the Search widget.\n\nPlease, enter search values  and try again.")
        return

    normalize=False
    scaleData=False
    useLemma=False
    fullInfo=False
    if 'Normalize' in str(viewer_list):
        normalize = True
    if 'Scale' in str(viewer_list):
        scaleData = True
    if 'Lemmatize' in str(viewer_list):
        useLemma = True
    if 'full information' in str(viewer_list):
        fullInfo = True

    # cmd = ['java', '-jar', 'NGrams_CoOccurrences_Viewer.jar', '-inputFolder', inputDir, '-outputFolder',
    #        outputDir]
    #
    # if (n_grams_viewer_var == 1 or CoOcc_Viewer_var == 1) and len(search_words) == 0:
    #     mb.showwarning(title='Warning',
    #                    message='No search words have been entered for either N-Grams or words co-occurrences.\n\nPlease, enter the search words and try again.')
    #     return

    if n_grams_viewer_var == 1 and len(search_words) > 0:
        if date_options == 0:
            mb.showwarning(title='Warning',
                           message='No Date options selected. The N-Grams routine requires date metadata (i.e., date information embedded in the document filenames, e.g., The New York Times_12-18-1899).\n\nPlease, tick the Date options checkbox, enter the appropariate date options and try again.')
            return
        ngram_list = processSearchWords(search_words)
        ngram_list = ['-checkNGrams'] + ngram_list
        # cmd.extend(ngram_list)

    # if date_options == 1:
    #     cmd.extend(
    #         ['-AggregateBy', temporal_aggregation, '-dateFormat', date_format, '-datePos', str(date_position_var),
    #          '-itemsDelim', date_separator_var])

    # if CoOcc_Viewer_var == 1 and len(search_words) > 0:
    #     co_occurrences_list = processSearchWords(search_words)
    #     co_occurrences_list = ["-checkCoOccurrences"] + co_occurrences_list
    #     cmd.extend(co_occurrences_list)

    # if normalize == 1 and n_grams_viewer_var == 1 and len(search_words) > 0: cmd.append(
    #     '-normalize')  # only available for Ngrams
    # if scaleData == 1: cmd.append('-scaledata')
    # if useLemma == 1: cmd.append('-lemma')
    # if fullInfo == 1: cmd.append('-fullInfo')

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'N-Grams Word Co-Occurrences start',
                        'Started running N-Grams Word Co-Occurrences Viewer at', True,
                        'Please, be patient. Depending upon the number of documents processed this may take a few minutes.\n\nYou can follow the script in command line.')

    reminders_util.checkReminder(config_filename,
                                 reminders_util.title_options_NGrams,
                                 reminders_util.message_NGrams,
                                 True)

    # search_words,
    # date_options,
    # temporal_aggregation,
    # date_format,
    # date_separator_var,
    # date_position_var,
    # viewer_list):

    # run VIEWER ------------------------------------------------------------------------------------
    n_grams_outputFile = NGrams_CoOccurrences_Viewer_util.run(inputDir,
            outputDir,
            n_grams_viewer_var,
            CoOcc_Viewer_var,
            search_words,
            date_options,
            date_position_var,
            date_format,
            date_separator_var,
            temporal_aggregation,
            # docPCIDCouplesFilePath,
            scaleData,
            useLemma,
            fullInfo,
            # considerAsSeparateGroups,
            normalize)

    return


    # plot co-occurrences
    if createExcelCharts == True and CoOcc_Viewer_var == 1 and len(search_words) > 0:
        xlsxFilename = co_occurrences_outputFile
        filesToOpen.append(co_occurrences_outputFile)
        chartTitle = 'Co-Occurrences Viewer'
        if date_options == 0:
            xAxis = 'Document'
        else:
            xAxis = temporal_aggregation
        hover_label = ['More information']
        if xAxis == 'Document':
            columns_to_be_plotted = [[1, 1]]
            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, xlsxFilename, outputDir,
                                                      'Co-Occ_viewer',
                                                      chart_type_list=["pie"],
                                                      chart_title=chartTitle, column_xAxis_label_var=xAxis,
                                                      hover_info_column_list=hover_label,
                                                      count_var=1)
        else:
            columns_to_be_plotted = [[0, 1]]
            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, xlsxFilename, outputDir,
                                                      'Co-Occ_viewer',
                                                      chart_type_list=["line"],
                                                      chart_title=chartTitle, column_xAxis_label_var=xAxis,
                                                      hover_info_column_list=hover_label)
        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)

    # plot Ngrams
    if createExcelCharts == True and n_grams_viewer_var == 1 and len(search_words) > 0:
        xlsxFilename = n_grams_outputFile
        filesToOpen.append(n_grams_outputFile)
        xAxis = temporal_aggregation
        chartTitle = 'N-Grams Viewer'
        columns_to_be_plotted = []
        for i in range(len(ngram_list) - 1):  # it will iterate through i = 0, 1, 2, …., n-1
            columns_to_be_plotted.append([0, i + 1])
        hover_label = ['Total Word Count of This Group', 'Total Word Count of This Group',
                       'Total Word Count of This Group']
        Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, xlsxFilename, outputDir,
                                                  'n-grams_viewer',
                                                  chart_type_list=["line"],
                                                  chart_title=chartTitle, column_xAxis_label_var=xAxis,
                                                  hover_info_column_list=hover_label)
        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)

    # with both Ngrams and co-occurrences
    if n_grams_viewer_var == 1 and CoOcc_Viewer_var == 1 and CoOcc_Viewer_var == 1 and len(search_words) > 0:
        n_grams_co_occurrences_outputFile = os.path.join(outputDir, 'N-Grams_CoOccurrences_Statistics.csv')
        filesToOpen.append(n_grams_co_occurrences_outputFile)
        chartTitle = ''

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'N-Grams Word Co-Occurrences end',
                        'Finished running N-Grams Word Co-Occurrences Viewer at', True)

    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)


# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command = lambda: run(GUI_util.inputFilename.get(), GUI_util.input_main_dir_path.get(), GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.create_Excel_chart_output_checkbox.get(),
                                 n_grams_var.get(),
                                 n_grams_menu_var.get(),
                                 n_grams_list,
                                 n_grams_viewer_var.get(),
                                 CoOcc_Viewer_var.get(),
                                 search_words_var.get(),
                                 date_options.get(),
                                 temporal_aggregation.get(),
                                 date_format.get(),
                                 date_separator_var.get(),
                                 date_position_var.get(),
                                 viewer_list)

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

IO_setup_display_brief=True
GUI_width=1100
GUI_height=530 # height of GUI with full I/O display

if IO_setup_display_brief:
    GUI_height = GUI_height - 40
    y_multiplier_integer = GUI_util.y_multiplier_integer  # IO BRIEF display
    increment=0 # used in the display of HELP messages
else: # full display
    # GUI CHANGES add following lines to every special GUI
    # +3 is the number of lines starting at 1 of IO widgets
    # y_multiplier_integer=GUI_util.y_multiplier_integer+2
    y_multiplier_integer = GUI_util.y_multiplier_integer + 1  # IO FULL display
    increment=1

GUI_size = str(GUI_width) + 'x' + str(GUI_height)
GUI_label = 'Graphical User Interface (GUI) for N-Grams and Word Co-Occurrences Viewer'
config_filename = 'n-grams-co-occurrences-viewer-config.txt'

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
config_option = [0, 2, 1, 0, 0, 1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_options,config_filename,IO_setup_display_brief)

n_grams_list=[]
viewer_list=[]

n_grams_var= tk.IntVar()
n_grams_menu_var= tk.StringVar()
# bySentenceIndex_var = tk.IntVar()
# normalize_var= tk.IntVar()
n_grams_options_menu_var= tk.StringVar()

n_grams_viewer_var = tk.IntVar()
CoOcc_Viewer_var = tk.IntVar()

search_words_var=tk.StringVar()

date_options = tk.IntVar()
fileName_embeds_date = tk.IntVar()

date_format = tk.StringVar()
date_separator_var = tk.StringVar()
date_position_var = tk.IntVar()

temporal_aggregation=tk.StringVar()

viewer_options_menu_var=tk.StringVar()

normalize = tk.IntVar()
scaleData = tk.IntVar()
useLemma = tk.IntVar()
fullInfo = tk.IntVar()

n_grams_var.set(0)
n_grams_checkbox = tk.Checkbutton(window, text='Compute n-grams', variable=n_grams_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,n_grams_checkbox,True)

n_grams_menu_var.set('Word')
n_grams_menu_lb = tk.Label(window, text='N-grams type')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+140,y_multiplier_integer,n_grams_menu_lb,True)
n_grams_menu = tk.OptionMenu(window, n_grams_menu_var, 'Character', 'Word','DEPREL','POSTAG')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(),y_multiplier_integer,n_grams_menu)

n_grams_options_menu_lb = tk.Label(window, text='N-grams options')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,n_grams_options_menu_lb,True)
n_grams_options_menu = tk.OptionMenu(window, n_grams_options_menu_var, 'Hapax legomena (once-occurring words/unigrams)','Normalize n-grams', 'Exclude punctuation (word n-grams only)','By sentence index','Repetition of words (last N words of a sentence/first N words of next sentence)','Repetition of words across sentences (special ngrams)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+140,y_multiplier_integer,n_grams_options_menu,True)

add_n_grams_button = tk.Button(window, text='+', width=2,height=1,state='disabled',command=lambda: activate_n_grams_var())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+300,y_multiplier_integer,add_n_grams_button, True)

reset_n_grams_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: reset_n_grams_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+340,y_multiplier_integer,reset_n_grams_button,True)

show_n_grams_button = tk.Button(window, text='Show', width=5,height=1,state='disabled',command=lambda: show_n_grams_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+400,y_multiplier_integer,show_n_grams_button)

def reset_n_grams_list():
    n_grams_list.clear()
    n_grams_options_menu_var.set('')
    n_grams_options_menu.configure(state='normal')

def show_n_grams_list():
    if len(n_grams_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected n-grams options.')
    else:
        mb.showwarning(title='Warning', message='The currently selected n-grams options are:\n\n' + ','.join(n_grams_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

def activate_n_grams_var():
    # Disable the + after clicking on it and enable the class menu
    add_n_grams_button.configure(state='disabled')
    n_grams_options_menu.configure(state='normal')

def activate_n_grams_options(*args):
    if n_grams_options_menu_var.get()!='':
        n_grams_list.append(n_grams_options_menu_var.get())
        n_grams_options_menu.configure(state="disabled")
        add_n_grams_button.configure(state='normal')
        reset_n_grams_button.configure(state='normal')
        show_n_grams_button.configure(state='normal')
    else:
        add_n_grams_button.configure(state='disabled')
        reset_n_grams_button.configure(state='disabled')
        show_n_grams_button.configure(state='disabled')
        n_grams_options_menu.configure(state="normal")
n_grams_options_menu_var.trace('w',activate_n_grams_options)

n_grams_viewer_var.set(0)
Ngrams_checkbox = tk.Checkbutton(window, text='N-grams VIEWER', variable=n_grams_viewer_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,Ngrams_checkbox,True)

CoOcc_Viewer_var.set(0)
CoOcc_checkbox = tk.Checkbutton(window, text='Co-Occurrences VIEWER', variable=CoOcc_Viewer_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+140,y_multiplier_integer,CoOcc_checkbox)

search_words_var.set('')
search_words_lb = tk.Label(window, text='Search words')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,search_words_lb,True)
search_words_entry = tk.Entry(window, textvariable=search_words_var)
search_words_entry.configure(width=100)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+140,y_multiplier_integer,search_words_entry)

date_options.set(0)
date_options_checkbox = tk.Checkbutton(window, text='Date options', variable=date_options, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,date_options_checkbox,True)

date_options_msg= tk.Label(window)
date_options_msg.config(text="Date option OFF")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+140,y_multiplier_integer,date_options_msg,True)

temporal_aggregation.set('year')
temporal_aggregation_lb = tk.Label(window,text='Aggregate by ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,temporal_aggregation_lb,True)
temporal_aggregation_menu = tk.OptionMenu(window, temporal_aggregation, 'year', 'quarter','month','day')
temporal_aggregation_menu.configure(width=5,state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+80,y_multiplier_integer,temporal_aggregation_menu,True)

date_format.set('mm-dd-yyyy')
date_format_lb = tk.Label(window,text='Format ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+170,y_multiplier_integer,date_format_lb,True)
date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy','yyyy-mm-dd','yyyy-dd-mm','yyyy-mm','yyyy')
date_format_menu.configure(width=10,state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+220,y_multiplier_integer,date_format_menu,True)

date_separator_var.set('_')
date_separator_lb = tk.Label(window, text='Character separator ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+340,y_multiplier_integer,date_separator_lb,True)
date_separator = tk.Entry(window, textvariable=date_separator_var)
date_separator.configure(width=2,state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+460,y_multiplier_integer,date_separator,True)

date_position_var.set(2)
date_position_menu_lb = tk.Label(window, text='Position ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+490,y_multiplier_integer,date_position_menu_lb,True)
date_position_menu = tk.OptionMenu(window,date_position_var,1,2,3,4,5)
date_position_menu.configure(width=1,state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+550,y_multiplier_integer,date_position_menu)

def check_dateFields(*args):
    if date_options.get() == 1:
        date_options_msg.config(text="Date option ON")
        temporal_aggregation_menu.config(state="normal")
        date_format_menu.config(state="normal")
        date_separator.config(state='normal')
        date_position_menu.config(state='normal')
    else:
        date_options_msg.config(text="Date option OFF")
        temporal_aggregation_menu.config(state="disabled")
        date_format_menu.config(state="disabled")
        date_separator.config(state='disabled')
        date_position_menu.config(state="disabled")
date_options.trace('w',check_dateFields)

add_viewer_button = tk.Button(window, text='+', width=2,height=1,state='disabled',command=lambda: activate_viewer_var())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+300,y_multiplier_integer,add_viewer_button, True)

reset_viewer_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: reset_viewer_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+340,y_multiplier_integer,reset_viewer_button,True)

show_viewer_button = tk.Button(window, text='Show', width=5,height=1,state='disabled',command=lambda: show_viewer_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+400,y_multiplier_integer,show_viewer_button,True)

viewer_menu_lb = tk.Label(window, text='VIEWER options')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,viewer_menu_lb,True)
viewer_options_menu = tk.OptionMenu(window, viewer_options_menu_var, 'Normalize results','Scale results', 'Lemmatize words','Display full information')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+140,y_multiplier_integer,viewer_options_menu)

def reset_viewer_list():
    viewer_list.clear()
    viewer_options_menu_var.set('')
    viewer_options_menu.configure(state='normal')

def show_viewer_list():
    if len(viewer_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected VIEWER options.')
    else:
        mb.showwarning(title='Warning', message='The currently selected VIEWER options are:\n\n' + ','.join(viewer_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

def activate_viewer_var():
    # Disable the + after clicking on it and enable the menu
    add_viewer_button.configure(state='disabled')
    viewer_options_menu.configure(state='normal')

def activate_viewer_options(*args):
    if viewer_options_menu_var.get()!='':
        viewer_list.append(viewer_options_menu_var.get())
        viewer_options_menu.configure(state="disabled")
        add_viewer_button.configure(state='normal')
        reset_viewer_button.configure(state='normal')
        show_viewer_button.configure(state='normal')
    else:
        add_viewer_button.configure(state='disabled')
        reset_viewer_button.configure(state='disabled')
        show_viewer_button.configure(state='disabled')
        viewer_options_menu.configure(state="normal")
viewer_options_menu_var.trace('w',activate_viewer_options)


def clear_n_grams_list():
    n_grams_list.clear()

def clear(e):
    n_grams_list.clear()
    n_grams_menu_var.set('Word')
    n_grams_options_menu_var.set('')
    search_words_var.set('')
    viewer_options_menu_var.set('')
    temporal_aggregation.set('year')
    date_format.set('mm-dd-yyyy')
    date_separator_var.set('_')
    date_position_var.set(2)
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

n_grams_list=[]

def activate_allOptions():
    if n_grams_var.get() == 1:
        n_grams_menu.configure(state='normal')
        n_grams_options_menu.configure(state='normal')
        Ngrams_checkbox.configure(state='disabled')
        CoOcc_checkbox.configure(state='disabled')
        search_words_entry.configure(state='disabled')
        date_options_checkbox.config(state='disabled')
    else:
        n_grams_menu.configure(state='disabled')
        n_grams_options_menu.configure(state='disabled')
        Ngrams_checkbox.configure(state='normal')
        CoOcc_checkbox.configure(state='normal')
        search_words_entry.configure(state='normal')
        date_options_checkbox.config(state='normal')
    if n_grams_viewer_var.get() or CoOcc_Viewer_var.get():
        n_grams_checkbox.configure(state='disabled')
        search_words_entry.configure(state='normal')
        date_options_checkbox.config(state='normal')
        viewer_options_menu.config(state='normal')
    else:
        n_grams_checkbox.configure(state='normal')
        search_words_entry.configure(state='disabled')
        date_options_checkbox.config(state='disabled')
        viewer_options_menu.config(state='disabled')
n_grams_var.trace('w', lambda x, y, z: activate_allOptions())
n_grams_viewer_var.trace('w', lambda x, y, z: activate_allOptions())
CoOcc_Viewer_var.trace('w', lambda x, y, z: activate_allOptions())

activate_allOptions()

TIPS_lookup = {'N-Grams (word & character)':"TIPS_NLP_Ngram (word & character).pdf",'Google Ngram Viewer':'TIPS_NLP_Ngram Google Ngram Viewer.pdf','NLP Suite Ngram and Word Co-Occurrence Viewer':"TIPS_NLP_Ngram and Word Co-Occurrence Viewer.pdf",'Style analysis':'TIPS_NLP_Style analysis.pdf','Java download install run':'TIPS_NLP_Java download install run.pdf'}
TIPS_options='N-Grams (word & character)','Google Ngram Viewer','NLP Suite Ngram and Word Co-Occurrence Viewer','Style analysis','Java download install run'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    if not IO_setup_display_brief:
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",GUI_IO_util.msg_corpusData)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment + 1),"Help", 'Please, tick the \'Compute n-grams\' checkbox if you wish to compute n-grams.\n\nN-grams can be computed for characters, words, POSTAG and DEPREL values. Use the dropdown menu to select the desired option.\n\nIn INPUT the script expects a single txt file or a directory containing a set of txt files.\n\nIn OUTPUT, the script generates a set of csv files each containing word n-grams between 1 and 3.\n\nWhen n-grams are computed by sentence index, the sentence displayed in output is always the first occurring sentence.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment + 2),"Help", 'Please, use the dropdown menu to select various options that can be applied to n-grams. You can make multiple selections by clicking on the + button.\n\nThe default number of n-grams computed is 3, unless you select the Hapax legomena option for unigrams (and then select once-occurring words).\n\nN-grams can be normalized, i.e., their frequency values are divided by the number of words or POSTAG-DEPREL values in a document.\n\nPunctuation can be excluded when computing n-grams (Google, for instance, exclude punctuation from its Ngram Viewer (https://books.google.com/ngrams).\n\nN-grams can be computed by sentence index.\n\nFinally, you can run a special type of n-grams that computes the last 2 words in a sentence and the first 2 words of the next sentence, a rhetorical figure of repetition for the analysis of style.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment + 3),"Help", 'Please, tick the Ngram VIEWER checkbox if you wish to run the Ngram Viewer Java script.\n\nTick the Co-Occurrence VIEWER checkbox if you wish to run the Co-Occurrene Viewer Java script.\n\nYou can run both Viewers at the same time.\n\nThe NGrams part of the NGrams_CoOccurrences.jar routine requires date metadata, i.e., a date embedded in the filename (e.g., The New York Time_2-18-1872).\n\nFor both viewers, results will be visualized in Excel line plots.\n\nFor n-grams the routine will display the FREQUENCY OF NGRAMS (WORDS), NOT the frequency of documents where searched word(s) appear. For Word Co-Occurrences the routine will display the FREQUENCY OF DOCUMENTS where searched word(s) appear.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment + 4),"Help", 'Please, enter the comma-separated list of words for which you want to know N-Gram statistics (e.g., woman, man, job). Leave blank if you do not want NGrams data. Both NGrams and co-occurrences words can be entered.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment + 5),"Help", 'Please, tick the checkbox if the filenames embed a date (e.g., The New York Times_12-19-1899). The DATE OPTIONS are required for N-grams; optional for word co-occurrences.\n\nPlease, using the dropdown menu, select the level of temporal aggregation you want to apply to your documents: year, quarter, month, day.\n\nPlease, using the dropdown menu, select the date format of the date embedded in the filename (default mm-dd-yyyy).\n\nPlease, enter the character used to separate the date field embedded in the filenames from the other fields (e.g., _ in the filename The New York Times_12-23-1992) (default _).\n\nPlease, using the dropdown menu, select the position of the date field in the filename (e.g., 2 in the filename The New York Times_12-23-1992; 4 in the filename The New York Times_1_3_12-23-1992 where perhaps fields 2 and 3 refer respectively to the page and column numbers) (default 2).')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment + 6),"Help", 'Please, use the dropdown menu to select various options that can be applied to the VIEWER. You can make multiple selections by clicking on the + button.\n\nYou can NORMALIZE results. Only works for N-Grams. Formula: search word frequency / total number of all words e.g: word "nurse" occurs once in year 1892, and year 1892 has a total of 1000 words. Then the normalized frequency will be 1/1000.\n\nYou can SCALE results. Only works for N-Grams. It applies the min-max normalization to frequency of search words. After the min-max normalization is done, each column of data (i.e., each search word) will fall in the same range.\n\nYou can LEMMATIZE words for your searches (e.g., be instead of being, is, was). The routine relies on the Stanford CoreNLP for lemmatizing words.\n\nFinally, you can select to display minimal information or full information.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment + 7),"Help",GUI_IO_util.msg_openOutputFiles)

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="""
The NGrams_CoOccurrences.jar is a Java routine that allows searches for Ngrams or word co-occurrences, i.e., key words (e.g., “nursery school” (a 2-gram or bigram), “kindergarten” (a 1-gram or unigram) and “child care” (another bigram) that occur in a set of documents.
\n\nThe NGrams part of the NGrams_CoOccurrences.jar routine requires date metadata, i.e., a date embedded in the filename (e.g., The New York Time_2-18-1872). It computes the number of words that appear in documents within a selected time period (e.g., month, year). It works similarly to Google Ngram Viewer except this routine works on documents supplied by the user rather than on the millions of Google books (see https://books.google.com/ngrams/info).
\n\nThe routine relies on the Stanford CoreNLP for lemmatizing words.
\n\n   For NGRAMS, the routine will display the FREQUENCY OF NGRAMS (WORDS), NOT the FREQUENCY OF DOCUMENTS where searched word(s) appear.
\n\n   For CO-OCCURRING words, the routine will display the FREQUENCY OF DOCUMENTS where searched word(s) appear together in the same document, NOT the frequency of the searched word(s) as with NGrams.
\n\nNGRAMS and CO-OCCURRING words DO NOT MAKE MUCH SENSE WITH A SINGLE FILE!
"""

readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options,IO_setup_display_brief)

GUI_util.window.mainloop()
