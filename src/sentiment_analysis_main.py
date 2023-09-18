# written by Roberto Franzosi October 2019

import sys
import GUI_util
import IO_libraries_util

if not IO_libraries_util.install_all_Python_packages(GUI_util.window,"sentiment_analysis_main.py",['os','tkinter','subprocess']):
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import IO_files_util
import IO_user_interface_util
import lib_util
import GUI_IO_util
import reminders_util
import sentiment_analysis_hedonometer_util
import sentiment_analysis_SentiWordNet_util
import sentiment_analysis_VADER_util
import sentiment_analysis_ANEW_util
import config_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,inputDir,outputDir,
        openOutputFiles,
        createCharts,
        chartPackage,
        mean_var,
        median_var,
        SA_algorithm_var,
        sentence_index_var,
        shape_of_stories_var):

    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    else:
        config_filename = scriptName.replace('_main.py', '_config.csv')

    usefile = False
    usedir = False
    flag="" #used by CoreNLP
    filesToOpen = []  # Store all files that are to be opened once finished


    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]
    if package_display_area_value == '':
        mb.showwarning(title='No setup for NLP package and language',
                       message="The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again.")
        return

    if SA_algorithm_var=='':
        mb.showwarning('Warning',"No option has been selected.\n\nPlease, select a Sentiment analysis option and try again.")
        return

    if len(inputFilename)>3:
        usefile = True
        usedir = False

    if len(inputDir)>3:
        usefile = False
        usedir = True

    mode = "both"
    if mean_var==False and median_var==False:
        mode = "mean"
    elif mean_var==True and median_var==False:
        mode = "mean"
    elif mean_var==False and median_var==True:
        mode = "median"
    elif mean_var==True and median_var==True:
        mode = "both"

    BERT_var = 0
    SentiWordNet_var=0
    CoreNLP_var=0
    Stanza_var=0
    spaCy_var=0
    hedonometer_var=0
    vader_var=0
    anew_var=0

    if SA_algorithm_var=='*':
        BERT_var=1
        CoreNLP_var=1
        spaCy_var=1
        Stanza_var=1
        anew_var=1
        hedonometer_var=1
        SentiWordNet_var=1
        vader_var=1
    elif 'BERT' in SA_algorithm_var:
        BERT_var = 1
    elif 'spaCy' in SA_algorithm_var:
        spaCy_var = 1
    elif 'Stanford CoreNLP' in SA_algorithm_var:
        CoreNLP_var = 1
    elif 'Stanza' in SA_algorithm_var:
        Stanza_var=1
    elif 'SentiWordNet' in SA_algorithm_var:
        SentiWordNet_var=1
    elif 'ANEW' in SA_algorithm_var:
        anew_var=1
    elif 'hedonometer' in SA_algorithm_var:
        hedonometer_var=1
    elif 'VADER' in SA_algorithm_var:
        vader_var=1
    else:
        mb.showwarning('Warning',
                SA_algorithm_var.lstrip() + " is not available yet. Sorry!\n\nPlease, select another option and try again.")
        return

# NEURAL NETWORK APPROACHES -------------------------------------------------------------------

    # BERT ---------------------------------------------------------

    if BERT_var==1:
        import BERT_util
        if 'Multilingual' in SA_algorithm_var:
            model_path = "cardiffnlp/twitter-xlm-roberta-base-sentiment" # multilingual model
        else:
            model_path = "cardiffnlp/twitter-roberta-base-sentiment-latest" # English language model
        outputFiles = BERT_util.sentiment_main(inputFilename, inputDir, outputDir, config_filename, mode, createCharts, chartPackage, model_path)
        if outputFiles == None:
            return
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
            outputFilename = outputFiles
        else:
            filesToOpen.extend(outputFiles)
            outputFilename = outputFiles[0]

    # spaCy  _______________________________________________________

    if SA_algorithm_var == '*' or spaCy_var == 1 and (mean_var or median_var):
        # check internet connection
        import IO_internet_util
        if not IO_internet_util.check_internet_availability_warning('spaCy Sentiment Analysis'):
            return
        #     flag="true" do NOT produce individual output files when processing a directory; only merged file produced
        #     flag="false" or flag="" ONLY produce individual output files when processing a directory; NO  merged file produced

        annotator = ['sentiment']
        document_length_var = 1
        limit_sentence_length_var = 1000
        import spaCy_util
        outputFiles = spaCy_util.spaCy_annotate(config_filename, inputFilename, inputDir,
                                                    outputDir,
                                                    openOutputFiles,
                                                    createCharts, chartPackage,
                                                    annotator, False,
                                                    language_var,
                                                    memory_var, document_length_var, limit_sentence_length_var,
                                                    filename_embeds_date_var=0,
                                                    date_format='',
                                                    items_separator_var='',
                                                    date_position_var=0)

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
                outputFilename = outputFiles
            else:
                filesToOpen.extend(outputFiles)
                outputFilename = outputFiles[0]

# Stanford CORENLP  _______________________________________________________

    if SA_algorithm_var=='*' or CoreNLP_var==1 and (mean_var or median_var):
        #check internet connection
        import IO_internet_util
        if not IO_internet_util.check_internet_availability_warning('Stanford CoreNLP Sentiment Analysis'):
            return
        #     flag="true" do NOT produce individual output files when processing a directory; only merged file produced
        #     flag="false" or flag="" ONLY produce individual output files when processing a directory; NO  merged file produced

        flag = "false" # the true option does not seem to work

        if IO_libraries_util.check_inputPythonJavaProgramFile('Stanford_CoreNLP_util.py') == False:
            return
        import Stanford_CoreNLP_util
        outputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                          outputDir, openOutputFiles, createCharts, chartPackage,'sentiment', False,
                                                                          language_var, export_json_var,
                                                                          memory_var)
        # outputFilename=outputFilename[0] # annotators return a list and not a string
        if SA_algorithm_var!='*' and outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
                outputFilename = outputFiles
            else:
                filesToOpen.extend(outputFiles)
                outputFilename = outputFiles[0]

# Stanza  _______________________________________________________

    if SA_algorithm_var == '*' or Stanza_var == 1 and (mean_var or median_var):
        # check internet connection
        import IO_internet_util
        if not IO_internet_util.check_internet_availability_warning('Stanza Sentiment Analysis'):
            return

        annotator = 'sentiment'
        document_length_var = 1
        limit_sentence_length_var = 1000
        import Stanza_util
        outputFiles = Stanza_util.Stanza_annotate(config_filename, inputFilename, inputDir,
                                                      outputDir,
                                                      openOutputFiles,
                                                      createCharts, chartPackage,
                                                      annotator, False,
                                                      [language_var], # Stanza_util takes language_var as a list
                                                      memory_var, document_length_var, limit_sentence_length_var,
                                                      filename_embeds_date_var=0,
                                                      date_format='',
                                                      items_separator_var='',
                                                      date_position_var=0)

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
                outputFilename = outputFiles
            else:
                filesToOpen.extend(outputFiles)
                outputFilename = outputFiles[0]

# shape of stories ------------------------------------------------------------------------
#   only for neural network approaches

    if (BERT_var or spaCy_var or CoreNLP_var or Stanza_var) and shape_of_stories_var:
        if IO_libraries_util.check_inputPythonJavaProgramFile('shape_of_stories_main.py') == False:
            return

        # open the shape of stories GUI having saved the new SA output in config so that it opens the right input file
        config_filename_temp = 'shape_of_stories_config.csv'
        config_input_output_numeric_options_temp = [3, 0, 0, 1]

        # config_input_output_alphabetic_options is a double list with no headers
        #   with one sublist for each of the four types of IO configurations: filename, input main dir, input secondary dir, output dir
        # each sublist has four items: path, date format, date separator, date position
        # e.g., [['C:/Users/rfranzo/Desktop/NLP-Suite/lib/sampleData/The Three Little Pigs.txt', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['C:\\Program Files (x86)\\NLP_backup\\Output', '', '', '']]
        config_input_output_alphabetic_options_temp, missing_IO, config_file_exists = config_util.read_config_file(config_filename_temp, config_input_output_numeric_options_temp)
        # add the sentiment csv file to the config file 'shape_of_stories_config.csv'
        config_input_output_alphabetic_options_temp[0][1]=outputFilename
        # add the output directory to the config file 'shape_of_stories_config.csv'
        config_input_output_alphabetic_options_temp[3][1] = outputDir

        # config_input_output_alphabetic_options = [['', outputFilename, '','',outputDir]]
        config_util.write_IO_config_file(GUI_util.window, config_filename_temp, config_input_output_numeric_options, config_input_output_alphabetic_options_temp, True)

        reminders_util.checkReminder(scriptName,
                                     reminders_util.title_options_shape_of_stories,
                                     reminders_util.message_shape_of_stories,
                                     True)
        call("python shape_of_stories_main.py", shell=True)

# DICTIONARY APPROACHES -------------------------------------------------------------------

# ANEW _______________________________________________________

    if anew_var == 1 and (mean_var or median_var):
        if language == 'English':
            if lib_util.checklibFile(GUI_IO_util.sentiment_libPath + os.sep + 'EnglishShortenedANEW.csv',
                                     'sentiment_analysis_ANEW') == False:
                return
            if IO_libraries_util.check_inputPythonJavaProgramFile('sentiment_analysis_ANEW_util.py') == False:
                return
            startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                           'Started running ANEW Sentiment Analysis at',
                                                           True, '', True, '', False)

            outputFiles = sentiment_analysis_ANEW_util.main(inputFilename, inputDir, outputDir, mode, createCharts,
                                                            chartPackage)

            if SA_algorithm_var!='*' and outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                               'Finished running ANEW Sentiment Analysis at', True, '', True,
                                               startTime)
        else:
            IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Warning',
                                               'The ANEW algorithm is available only for the English language.\n\nYour currently selected language is ' + language + '.\n\nYou can change the language using the Setup dropdownmenu at the bottom of this GUI and selecting "Setup NLP package and corpus language."')

# HEDONOMETER _______________________________________________________

    if SA_algorithm_var=='*' or hedonometer_var==1 and (mean_var or median_var):
        if lib_util.checklibFile(GUI_IO_util.sentiment_libPath + os.sep + 'hedonometer.json', 'sentiment_analysis_hedonometer_util.py')==False:
            return
        if IO_libraries_util.check_inputPythonJavaProgramFile('sentiment_analysis_hedonometer_util.py')==False:
            return
        if language=='English':

            startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running HEDONOMETER Sentiment Analysis at',
                                                         True, '', True, '', False)

            outputFiles = sentiment_analysis_hedonometer_util.main(inputFilename, inputDir, outputDir, mode, createCharts, chartPackage)

            if SA_algorithm_var!='*' and outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running HEDONOMETER Sentiment Analysis at', True, '', True, startTime)
        else:
            IO_user_interface_util.timed_alert(GUI_util.window,4000,'Warning','The HEDONOMETER algorithm is available only for the English language.\n\nYour currently selected language is '+language+'.\n\nYou can change the language using the Setup dropdownmenu at the bottom of this GUI and selecting "Setup NLP package and corpus language."')

#SentiWordNet _______________________________________________________

    if SA_algorithm_var=='*' or SentiWordNet_var==1 and (mean_var or median_var):
        if language=='English':
            if IO_libraries_util.check_inputPythonJavaProgramFile('sentiment_analysis_SentiWordNet_util.py')==False:
                return
            startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running SentiWordNet Sentiment Analysis at',
                                                         True, '', True, '', False)

            outputFiles = sentiment_analysis_SentiWordNet_util.main(inputFilename, inputDir, outputDir, config_filename, mode, createCharts, chartPackage)

            if SA_algorithm_var!='*' and outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)


            IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running SentiWordNet Sentiment Analysis at', True, '', True, startTime)
        else:
            IO_user_interface_util.timed_alert(GUI_util.window,4000,'Warning','The SentiWordNet algorithm is available only for the English language.\n\nYour currently selected language is '+language+'.\n\nYou can change the language using the Setup dropdownmenu at the bottom of this GUI and selecting "Setup NLP package and corpus language."')

# VADER _______________________________________________________

    if SA_algorithm_var=='*' or vader_var==1 and (mean_var or median_var):
        if language=='English':
            if lib_util.checklibFile(GUI_IO_util.sentiment_libPath + os.sep + 'vader_lexicon.txt', 'sentiment_analysis_VADER_util.py')==False:
                return
            if IO_libraries_util.check_inputPythonJavaProgramFile('sentiment_analysis_VADER_util.py')==False:
                return
            startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running VADER Sentiment Analysis at',
                                                         True, '', True, '', False)
            outputFiles = sentiment_analysis_VADER_util.main(inputFilename, inputDir, outputDir, mode, createCharts, chartPackage)

            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running VADER Sentiment Analysis at', True, '', True, startTime)
        else:
            IO_user_interface_util.timed_alert(GUI_util.window,4000,'Warning','The VADER algorithm is available only for the English language.\n\nYour currently selected language is '+language+'.\n\nYou can change the language using the Setup dropdownmenu at the bottom of this GUI and selecting "Setup NLP package and corpus language."')

    if len(filesToOpen)>0:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                               GUI_util.input_main_dir_path.get(),
                               GUI_util.output_dir_path.get(),
                               GUI_util.open_csv_output_checkbox.get(),
                               GUI_util.create_chart_output_checkbox.get(),
                               GUI_util.charts_package_options_widget.get(),
                               mean_var.get(),
                               median_var.get(),
                               SA_algorithm_var.get(),
                               sentence_index_var.get(),
                               shape_of_stories_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=440, # height at brief display
                             GUI_height_full=520, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Sentiment Analysis'
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
# GUI_util.set_window(GUI_size, GUI_label)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

mean_var = tk.IntVar()
median_var = tk.IntVar()
SA_algorithm_var = tk.StringVar()

sentence_index_var = tk.IntVar()
shape_of_stories_var = tk.IntVar()

# doNotCreateIntermediateFiles_var = tk.IntVar() #when an entire directory is processed; could lead to an enourmus number of output files

mean_var.set(1)
median_var.set(1)

def clear(e):
    SA_algorithm_var.set('*')
    activate_SOS()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

mean_checkbox = tk.Checkbutton(window, text='Calculate sentence mean', variable=mean_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,mean_checkbox,True)

median_checkbox = tk.Checkbutton(window, text='Calculate sentence median', variable=median_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.sentiment_analysis_median_checkbox_pos,y_multiplier_integer,median_checkbox)

def display_reminder(*args):
    if 'Neural network' in SA_algorithm_var.get() or 'Dictionar' in SA_algorithm_var.get():
        mb.showwarning('Warning', SA_algorithm_var.get() + " is only a label. Please, select one of the indented sentiment analysis options and try again.")
        return
    if SA_algorithm_var.get()=='':
        mb.showwarning('Warning',"The selected option is only a spacer. Please, select one of the indented sentiment analysis options and try again.")
        return
    if 'Stanford CoreNLP' in SA_algorithm_var.get():
        reminders_util.checkReminder(scriptName,
                                     reminders_util.title_options_SA_CoreNLP_system_requirements,
                                     reminders_util.message_SA_CoreNLP_system_requirements,
                                     True)
    elif 'VADER' in SA_algorithm_var.get():
        reminders_util.checkReminder(scriptName,
                                     reminders_util.title_options_SA_VADER,
                                     reminders_util.message_SA_VADER,
                                     True)
        if mean_var.get() or median_var.get()==True:
            reminders_util.checkReminder(scriptName,
                                         reminders_util.title_options_VADER_MeanMedian,
                                         reminders_util.message_VADER_MeanMedian,
                                         True)
    elif 'SentiWordNet' in SA_algorithm_var.get():
        reminders_util.checkReminder(scriptName,
                                    reminders_util.title_options_SA_SentiWordNet,
                                    reminders_util.message_SA_SentiWordNet,
                                    True)

    else:
        return
SA_algorithm_var.trace('w',display_reminder)

SA_algorithms=['*','Neural network approaches:','   BERT (English model)','   BERT (Multilingual model)','   spaCy','   Stanford CoreNLP','   Stanza','','Dictionary approaches:','   ANEW','   hedonometer','   SentiWordNet','   VADER']

SA_algorithm_var.set('*')
SA_algorithm_lb = tk.Label(window, text='Select sentiment analysis algorithm')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,SA_algorithm_lb,True)

SA_algorithm_menu = tk.OptionMenu(window,SA_algorithm_var,*SA_algorithms)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.sentiment_analysis_SA_algorithm_menu_pos, y_multiplier_integer,SA_algorithm_menu)

y_multiplier_integerSV=y_multiplier_integer-1

sentence_index_var.set(0)
sentence_index_checkbox = tk.Checkbutton(window, state='disabled', text='Do sentiments fluctuate across a document (Sentiment scores by sentence index)', variable=sentence_index_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,sentence_index_checkbox)

shape_of_stories_var.set(0)
shape_of_stories_checkbox = tk.Checkbutton(window, text='Do sentiments fluctuate across documents (Open \'Shape of stories\' GUI)', variable=shape_of_stories_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,shape_of_stories_checkbox)

ALL_options_button = tk.Button(window, text='Sentiments/emotions (ALL options GUI)', command=lambda: call("python sentiments_emotions_ALL_main.py", shell=True))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,ALL_options_button)

def activate_SOS(*args):
    # the Shape of Stories is only available when processing a directory and using CoreNLP
    if input_main_dir_path.get()=='' or (not 'BERT' in SA_algorithm_var.get().strip() and SA_algorithm_var.get().strip()!='spaCy' and SA_algorithm_var.get().strip()!='Stanza' and SA_algorithm_var.get().strip()!='Stanford CoreNLP'):
        shape_of_stories_checkbox.config(state='disabled')
    else:
        shape_of_stories_checkbox.config(state='normal')
shape_of_stories_var.trace('w',activate_SOS)
inputFilename.trace('w',activate_SOS)
input_main_dir_path.trace('w',activate_SOS)
SA_algorithm_var.trace('w',activate_SOS)

activate_SOS()

# doNotCreateIntermediateFiles_var.set(1)
# doNotCreateIntermediateFiles_checkbox = tk.Checkbutton(window, variable=doNotCreateIntermediateFiles_var, onvalue=1, offvalue=0)
# doNotCreateIntermediateFiles_checkbox.config(text="Do NOT produce intermediate csv files when processing all txt files in a directory")
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,doNotCreateIntermediateFiles_checkbox)

# def changeLabel(*args):
# 	if doNotCreateIntermediateFiles_var.get()==1:
# 		doNotCreateIntermediateFiles_checkbox.config(text="Do NOT produce intermediate csv files when processing all txt files in a directory")
# 	else:
# 		doNotCreateIntermediateFiles_checkbox.config(text="Produce intermediate csv files when processing all txt files in a directory")
# doNotCreateIntermediateFiles_var.trace('w',changeLabel)
#
# def turnOff_doNotCreateIntermediateFiles_checkbox(*args):
# 	if len(input_main_dir_path.get())>0:
# 		doNotCreateIntermediateFiles_checkbox.config(state='normal')
# 	else:
# 		doNotCreateIntermediateFiles_checkbox.config(state='disabled')
# input_main_dir_path.trace('w',turnOff_doNotCreateIntermediateFiles_checkbox)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'The world of emotions and sentiments':'TIPS_NLP_The world of emotions and sentiments.pdf',
               'Sentiment Analysis':"TIPS_NLP_Sentiment Analysis.pdf",
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf',
               'BERT: A brief introduction':'TIPS_NLP_BERT Brief introduction.pdf',
               'BERT: Sentiment analysis':'TIPS_NLP_BERT Sentiment Analysis.pdf'}
# 'Java download install run':'TIPS_NLP_Java download install run.pdf'
TIPS_options='The world of emotions and sentiments','Sentiment Analysis','Excel smoothing data series', 'csv files - Problems & solutions', 'Statistical measures','BERT: A brief introduction','BERT: Sentiment analysis'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkboxes for either Mean or Median in output csv files. BY DEFAULT, BOTH VALUES ARE COMPUTED.\n\nStanford CoreNLP Sentiment Analysis only computes mean values for each sentence.\n\nVADER only computes 'compound' values for each sentence.\n\nSentiWordNet as well does not provide sentence mean/median values.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, using the dropdown menu, select the algorithm to be used for computing sentiment analysis.\n\nSelect * to run ALL algorithms.\n\nspaCy, Stanford CoreNLP, Stanza neural network approach to Sentiment Analysis typically achieves better results than dictionary-based approaches.\n\nCoreNLP computes mean values only for each sentence on a scale 0-4 (minimum-maximum).\n\nANEW (Affective Norms for English Words) computes sentiment/arousal/dominance mean/median values for each sentence using the ANEW ratings for SENTIMENT (VALENCE), AROUSAL, and DOMINANCE (CONTROL) by Bradley, M.M. & Lang, P.J. (2017). Affective Norms for English Words (ANEW): Instruction manual and affective ratings. Technical Report C-3. Gainesville, FL:UF Center for the Study of Emotion and Attention.\n\nContrary to all other approaches, the ANEW script computes three different measures, for SENTIMENT, AROUSAL, and DOMINANCE:\nSENTIMENT or VALENCE measures how pleasant/unpleasant a word makes us feel;\nAROUSAL measures how calm/excited a word makes us feel;\nDOMINANCE or CONTROL measures how dominated/in control a word makes us feel.\n\nTHE SCRIPT EXPECTS TO FIND THE FILE EnglishShortenedANEW.csv IN A ""lib"" SUBFOLDER OF THE FOLDER WHERE THE Sentiment_Analysis_ANEW.py SCRIPT IS STORED.\n\nIn OUTPUT, the script creates a csv file containing the calculated mean/median sentiment values for each sentence, where each rating can have a total of maximum 9 points.\n\nValues for sentiment, arousal, and dominance are classified on a scale 0-9, grouped in 5 categories: <3, >=3 and < 5, 5 (neutral), >5 and <8, >=8 and <=9.\n\nThe hedonometer algorithm uses the hedonometer.org rated dictionary to compute sentiment mean/median values for each sentence.\n\nThe script has been shown to work best with social media texts (e.g., Twitter), New York Times editorials, movie reviews, and product reviews.\n\nTHE SCRIPT EXPECTS TO FIND THE FILE hedonometer.json IN A ""lib"" SUBFOLDER OF THE FOLDER WHERE THE Sentiment_Analysis_Hedonometer.py SCRIPT IS STORED.\n\nIn OUTPUT, the script creates a csv file containing the calculated mean/median sentiment values for each sentence.\n\nSentiment values are classified on a scale 0-10, grouped in 3 categories: negative (>=0 and <4), neutral (>=4 and <=6), and positive (>6 and <=10).\n\nThe NLTK VADER (VADER, Valence Aware Dictionary and sEntiment Reasoner) uses the NLTK rated dictionary to compute sentiment mean/median values for each sentence.\n\nThe script has been shown to work best with social media texts (e.g., Twitter).\n\nIn INPUT the script expects either a single text file or a set of text files stored in a directory. THE SCRIPT ALSO EXPECTS TO FIND THE VADER RATED DICTIONARY FILE vader_lexicon.txt IN A ""lib"" SUBFOLDER OF THE FOLDER WHERE THE Sentiment_Analysis_VADER.py SCRIPT IS STORED.\n\nIn OUTPUT, the script creates a csv file containing the calculated 'compound' sentiment values for each sentence.\n\nMean and Median calculations are not available for VADER; VADER computes 'compound' values for each sentence.\n\nSentiment values are classified on a scale -1 (most negative) to 1 as (most positive) grouped in 3 categories: negative (<-0.05), neutral (>=-0.05 and <=0.05), and positive (>0.05 and <=1).\n\nVADER heavily relies on a number of NLTK libraries. If VADER fails to run, make sure that in command line you run\n   python -m nltk.downloader all")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to display a line plot of sentiment scores by sentence index across a specific document.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to open the 'Shape of stories' GUI. The 'Shape of stories' algorithms will compute and visualize the \'shape of stories\' of a set of sentiment scores across different documents using different data reduction methods: Hiererchical Clustering, Singular Value Decomposition, Non-Negative Matrix Factorization.\n\nThe 'Shape of stories' GUI is only available when computing sentiment scores via BERT, spaCy, Stanford CoreNLP, or Stanza on a corpus of txt files in an input directory.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                              "Please, click on the button to open the GUI for ALL options to analyze emotions/sentiments available in the NLP Suite.")
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 Dictionary-based Analyses scripts calculate the mean/median values for various aspects of the language used in a text: sentiment, arousal, dominance.\n\nIn INPUT the scripts expect either a single text file or a set of text files stored in a directory. THE hedonometer, ANEW, AND VADER SCRIPTS ALSO EXPECT TO FIND DICTIONARY FILES IN A ""lib"" SUBFOLDER OF THE FOLDER WHERE THE PYTHON SCRIPTS ARE STORED.\n\nIn OUTPUT, the scripts create csv files containing the calculated mean/median values for each sentence."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

def activate_NLP_options(*args):
    global error, package_basics, package, language, language_var, language_list
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
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
