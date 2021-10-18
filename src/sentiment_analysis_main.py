# written by Roberto Franzosi October 2019

import sys
import GUI_util
import IO_libraries_util

if not IO_libraries_util.install_all_packages(GUI_util.window,"sentiment_analysis.py",['os','tkinter','subprocess']):
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
import subprocess
from subprocess import call

import IO_files_util
import IO_user_interface_util
import Excel_util
import lib_util
import GUI_IO_util
import reminders_util
import Stanford_CoreNLP_annotator_util
import sentiment_analysis_hedonometer_util
import sentiment_analysis_SentiWordNet_util
import sentiment_analysis_VADER_util
import sentiment_analysis_ANEW_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(CoreNLPdir,inputFilename,inputDir,outputDir,
        openOutputFiles,
        createExcelCharts,
        mean_var,
        median_var,
        SA_algorithm_var,
        memory_var,
        sentence_index_var,
        shape_of_stories_var):

    #if GUI_util.check_missingIO()==True:
    #    return
    usefile = False
    usedir = False
    flag="" #used by CoreNLP
    filesToOpen = []  # Store all files that are to be opened once finished

    if shape_of_stories_var:
        if IO_libraries_util.inputProgramFileCheck('shape_of_stories_main.py') == False:
            return
        call("python shape_of_stories_main.py", shell=True)

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

    SentiWordNet_var=0
    CoreNLP_var=0
    hedonometer_var=0
    vader_var=0
    anew_var=0

    if SA_algorithm_var=='*':
        SentiWordNet_var=1
        CoreNLP_var=1
        hedonometer_var=1
        vader_var=1
        anew_var=1
    elif SA_algorithm_var=='Stanford CoreNLP':
        CoreNLP_var=1
    elif SA_algorithm_var=='SentiWordNet':
        SentiWordNet_var=1
    elif SA_algorithm_var=='ANEW':
        anew_var=1
    elif SA_algorithm_var=='hedonometer':
        hedonometer_var=1
    elif SA_algorithm_var=='VADER':
        vader_var=1

    #CORENLP  _______________________________________________________
    if CoreNLP_var==1:
        #check internet connection
        import IO_internet_util
        if not IO_internet_util.check_internet_availability_warning('Stanford CoreNLP Sentiment Analysis'):
            return
        #     flag="true" do NOT produce individual output files when processing a directory; only merged file produced
        #     flag="false" or flag="" ONLY produce individual output files when processing a directory; NO  merged file produced

        flag = "false" # the true option does not seem to work

        if IO_libraries_util.inputProgramFileCheck('Stanford_CoreNLP_annotator_util.py') == False:
            return
        # IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Stanford CoreNLP Sentiment Analysis',
        #                                    'Started running Stanford CoreNLP Sentiment Analysis at', True,
        #                                    'You can follow CoreNLP in command line.')
        
        #@ need an additional variable CoreNLP dir and memory_var @
        # set memory_var if not there
        if memory_var==0:
            memory_var=4
        outputFilename = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                          outputDir, openOutputFiles, createExcelCharts,'sentiment', False,
                                                                          memory_var)
        outputFilename=outputFilename[0] # annotators return a list and not a string
        if len(outputFilename)>0:
            filesToOpen.append(outputFilename)
        #@ not longer need to call java subprocess @
        # subprocess.call(['java', '-jar', 'Stanford_CoreNLP_sentiment_analysis.jar', inputDir, inputFilename, outputDir, flag])
        if not usedir:
            if createExcelCharts==True:
                # CoreNLP only computes mean values
                columns_to_be_plotted = [[2,4]]
                hover_label=['Sentence']
                # inputFilename = outputFilename
                Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                          outputFileLabel='CoreNLP_sent',
                                                          chart_type_list=["line"],
                                                          chart_title='Stanford CoreNLP - Sentiment Scores by Sentence Index',
                                                          column_xAxis_label_var='Sentence index',
                                                          hover_info_column_list=hover_label,
                                                          count_var=0,
                                                          column_yAxis_label_var='Scores')
                if Excel_outputFilename != "":
                    filesToOpen.append(Excel_outputFilename)

                columns_to_be_plotted = [[5,5]]
                hover_label=[]
                # inputFilename = inputFilename
                Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                          outputFileLabel='CoreNLP_SA',
                                                          chart_type_list=["bar"],
                                                          chart_title='Stanford CoreNLP - Sentiment Scores',
                                                          column_xAxis_label_var='Sentiment score',
                                                          hover_info_column_list=hover_label,
                                                          count_var=1,
                                                          column_yAxis_label_var='Scores')

                if Excel_outputFilename != "":
                    filesToOpen.append(Excel_outputFilename)

                # outputFilenameXlsm1 = Excel_util.run_all(columns_to_be_plotted,inputFilename,outputDir, outputQuotefilePath, chart_type_list = ["bar"], chart_title=
                # "Stanford CoreNLP (Sentiment Value)", column_xAxis_label_var = 'Sentiment value',
                # column_yAxis_label_var = 'Frequency of sentiment value',outputExtension = '.xlsm',
                # label1='SC',label2='CoreNLP_Sentiment',label3='bar',label4='chart',label5='',
                # useTime=False,disable_suffix=True,  count_var=1, column_yAxis_field_list = [], reverse_column_position_for_series_label=False , series_label_list=[''], second_y_var=0, second_yAxis_label='', hover_info_column_list=hover_label)

        # else:
        #     #open only the merged file
        #     lastPart=os.path.basename(os.path.normpath(inputDir))
        #     outputFilename = IO_files_util.generate_output_file_name(lastPart, outputDir, '.csv', 'SC', 'Sentiment CoreNLP', '', '', '', False, True)
        #     filesToOpen.append(outputFilename)

        # IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running CoreNLP Sentiment Analysis at', True)

    #HEDONOMETER _______________________________________________________
    if hedonometer_var==1:
        if lib_util.checklibFile(GUI_IO_util.sentiment_libPath + os.sep + 'hedonometer.json', 'sentiment_analysis_hedonometer_util.py')==False:
            return
        if IO_libraries_util.inputProgramFileCheck('sentiment_analysis_hedonometer_util.py')==False:
            return
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running HEDONOMETER Sentiment Analysis at', True)
        if len(inputFilename)>0:
            fileNamesToPass = []  # LINE ADDED
            outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'SC', 'Hedonometer', '', '', '', False, True)
        else:
            outputFilename = IO_files_util.generate_output_file_name(inputDir, inputDir,  outputDir, '.csv', 'SC_dir', 'Hedonometer', '', '', '', False, True)

        sentiment_analysis_hedonometer_util.main(inputFilename, inputDir, outputDir, outputFilename, mode)

        #tkinter filedialog.askdirectory ALWAYS returns forward slashes / if you use os.sep you end up mixing the slashes
        # subprocess.call(['python', 'sentiment_analysis_hedonometer_util.py', '--file', inputFilename, "--out", outputDir+os.sep
        #                  , "--mode", mode])
        filesToOpen.append(outputFilename)

        if createExcelCharts==True:
            if mode == "both":
                columns_to_be_plotted = [[2,4],[2,6]]
                hover_label=['Sentence','Sentence']
            else:
                columns_to_be_plotted = [[2,4]]
                hover_label=['Sentence']
            # inputFilename = outputFilename
            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                      outputFileLabel='Hedo_sent',
                                                      chart_type_list=["line"],
                                                      chart_title='Hedonometer - Sentiment Scores by Sentence Index',
                                                      column_xAxis_label_var='Sentence index',
                                                      hover_info_column_list=hover_label,
                                                      count_var=0,
                                                      column_yAxis_label_var='Scores')
            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

            columns_to_be_plotted = [[5,5]]
            hover_label=[]
            # inputFilename = outputFilename
            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                      outputFileLabel='Hedo_sent',
                                                      chart_type_list=["bar"],
                                                      chart_title='Hedonometer - Sentiment Scores',
                                                      column_xAxis_label_var='Sentiment score',
                                                      hover_info_column_list=hover_label,
                                                      count_var=1,
                                                      column_yAxis_label_var='Scores')

            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running HEDONOMETER Sentiment Analysis at', True)

    #SentiWordNet _______________________________________________________
    if SentiWordNet_var==1:
        if IO_libraries_util.inputProgramFileCheck('sentiment_analysis_SentiWordNet_util.py')==False:
            return
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running SentiWordNet Sentiment Analysis at', True)

        if len(inputFilename)>0:
            outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'SC', 'SentiWordNet', '', '', '', False, True)
        else:
            outputFilename = IO_files_util.generate_output_file_name(inputDir, inputDir, outputDir, '.csv', 'SC_dir', 'SentiWordNet', '', '', '', False, True)

        sentiment_analysis_SentiWordNet_util.main(inputFilename, inputDir, outputDir, outputFilename, mode)

        filesToOpen.append(outputFilename)
        if createExcelCharts==True:
            # sentiWordNet compute a single sentiment score
            columns_to_be_plotted = [[2,4]]
            hover_label=['Sentence']

            # inputFilename = outputFilename
            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                      outputFileLabel='SentiWordNet_sent',
                                                      chart_type_list=["line"],
                                                      chart_title='SentiWordNet - Sentiment Scores by Sentence Index',
                                                      column_xAxis_label_var='Sentence index',
                                                      hover_info_column_list=hover_label,
                                                      count_var=0,
                                                      column_yAxis_label_var='Scores')
            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

            columns_to_be_plotted = [[5,5]]
            hover_label=[]
            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                      outputFileLabel='SentiWordNet_sent',
                                                      chart_type_list=["bar"],
                                                      chart_title='SentiWordNet - Sentiment Scores',
                                                      column_xAxis_label_var='Sentiment score',
                                                      hover_info_column_list=hover_label,
                                                      count_var=1,
                                                      column_yAxis_label_var='Scores')

            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running SentiWordNet Sentiment Analysis at', True)

    #VADER _______________________________________________________
    if vader_var==1:
        if lib_util.checklibFile(GUI_IO_util.sentiment_libPath + os.sep + 'vader_lexicon.txt', 'sentiment_analysis_VADER_util.py')==False:
            return
        if IO_libraries_util.inputProgramFileCheck('sentiment_analysis_VADER_util.py')==False:
            return
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running VADER Sentiment Analysis at', True)
        if len(inputFilename)>0:
            outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir,  outputDir, '.csv', 'SC', 'VADER', '', '', '', False, True)
        else:
            outputFilename = IO_files_util.generate_output_file_name(inputDir, inputDir, outputDir, '.csv', 'SC_dir', 'VADER', '', '', '', False, True)

        sentiment_analysis_VADER_util.main(inputFilename, inputDir, outputDir, outputFilename, mode)

        filesToOpen.append(outputFilename)
        if createExcelCharts==True:
            # VADER does not compute separate mean and median values
            columns_to_be_plotted = [[2,4]]
            hover_label=['Sentence']
            # inputFilename = outputFilename

            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                      outputFileLabel='VADER_sent',
                                                      chart_type_list=["line"],
                                                      chart_title='VADER - Sentiment Scores by Sentence Index',
                                                      column_xAxis_label_var='Sentence index',
                                                      hover_info_column_list=hover_label,
                                                      count_var=0,
                                                      column_yAxis_label_var='Scores')
            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

            columns_to_be_plotted = [[5,5]]
            hover_label=[]
            # inputFilename = outputFilename
            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                      outputFileLabel='VADER_sent',
                                                      chart_type_list=["bar"],
                                                      chart_title='VADER - Sentiment Scores',
                                                      column_xAxis_label_var='Sentiment score',
                                                      hover_info_column_list=hover_label,
                                                      count_var=1,
                                                      column_yAxis_label_var='Scores')

            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running VADER Sentiment Analysis at', True)

    #ANEW _______________________________________________________
    if anew_var==1:
        if lib_util.checklibFile(GUI_IO_util.sentiment_libPath + os.sep + 'EnglishShortenedANEW.csv', 'sentiment_analysis_ANEW')==False:
            return
        if IO_libraries_util.inputProgramFileCheck('sentiment_analysis_ANEW_util.py')==False:
            return
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running ANEW Sentiment Analysis at', True)
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'SC', 'ANEW', '', '', '', False, True)

        sentiment_analysis_ANEW_util.main(inputFilename, inputDir, outputDir, outputFilename, mode)
        if createExcelCharts==True:
            # # sentiment by sentence index
            if mode == "both":
                columns_to_be_plotted = [[2,4],[2,6],[2,8],[2,10],[2,12],[2,14]]
                hover_label=['Sentence','Sentence','Sentence','Sentence','Sentence','Sentence']
            else:
                columns_to_be_plotted = [[2,4],[2,6],[2,8]]
                hover_label=['Sentence','Sentence','Sentence']

            # inputFilename = outputFilename
            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                      outputFileLabel='ANEW_sent',
                                                      chart_type_list=["line"],
                                                      chart_title='ANEW - Sentiment Scores by Sentence Index',
                                                      column_xAxis_label_var='Sentence index',
                                                      hover_info_column_list=hover_label,
                                                      count_var=0,
                                                      column_yAxis_label_var='Scores')
            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

            # sentiment bar chart
            if mode == "both":
                columns_to_be_plotted = [[5,5],[7,7]]
            else:
                columns_to_be_plotted = [[5,5]]
            hover_label=[]
            # inputFilename = outputFilename
            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                      outputFileLabel='ANEW_sent',
                                                      chart_type_list=["bar"],
                                                      chart_title='ANEW - Sentiment Scores',
                                                      column_xAxis_label_var='Sentiment score',
                                                      hover_info_column_list=hover_label,
                                                      count_var=1,
                                                      column_yAxis_label_var='Scores')

            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

            # arousal
            if mode == "both":
                columns_to_be_plotted = [[9,9],[11,11]]
            else:
                columns_to_be_plotted = [[7,7]]
            hover_label=[]
            # inputFilename = outputFilename
            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                      outputFileLabel='ANEW_arous',
                                                      chart_type_list=["bar"],
                                                      chart_title='ANEW - Arousal Scores',
                                                      column_xAxis_label_var='Arousal score',
                                                      hover_info_column_list=hover_label,
                                                      count_var=1,
                                                      column_yAxis_label_var='Scores')

            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

            # dominance
            if mode == "both":
                columns_to_be_plotted = [[13,13],[15,15]]
            else:
                columns_to_be_plotted = [[9,9]]
            hover_label=[]
            # inputFilename = outputFilename
            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                      outputFileLabel='ANEW_dom',
                                                      chart_type_list=["bar"],
                                                      chart_title='ANEW - Dominance Scores',
                                                      column_xAxis_label_var='Dominance score',
                                                      hover_info_column_list=hover_label,
                                                      count_var=1,
                                                      column_yAxis_label_var='Scores')

            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running ANEW Sentiment Analysis at', True)

    if openOutputFiles==True:
        # IO_user_interface_util.timed_alert(GUI_util.window, 5000, 'Warning', 'All csv output files have been saved to ' + outputDir)
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.softwareDir.get(),
                               GUI_util.inputFilename.get(),
                               GUI_util.input_main_dir_path.get(),
                               GUI_util.output_dir_path.get(),
                               GUI_util.open_csv_output_checkbox.get(),
                               GUI_util.create_Excel_chart_output_checkbox.get(),
                               mean_var.get(),
                               median_var.get(),
                               SA_algorithm_var.get(),
                               memory_var.get(),
                               sentence_index_var.get(),
                               shape_of_stories_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=False
GUI_width=1100
GUI_height=480 # height of GUI with full I/O display

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

GUI_label='Graphical User Interface (GUI) for Sentiment Analysis'
config_filename='sentiment-analysis-config.txt'
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
config_option=[0,2,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_options,config_filename,IO_setup_display_brief)

# if GUI_util.softwareDir.get()=='':
#     GUI_util.select_softwareDir_button.config(state='disabled')

mean_var = tk.IntVar()
median_var = tk.IntVar()
SA_algorithm_var = tk.StringVar()
memory_var = tk.IntVar()
memory_var_lb = tk.Label(window, text='Memory ')

sentence_index_var = tk.IntVar()
shape_of_stories_var = tk.IntVar()

# doNotCreateIntermediateFiles_var = tk.IntVar() #when an entire directory is processed; could lead to an enourmus number of output files

mean_var.set(1)
median_var.set(1)

def clear(e):
    SA_algorithm_var.set('')
    memory_var_lb.place_forget()  # invisible
    memory_var.place_forget()  # invisible
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

mean_checkbox = tk.Checkbutton(window, text='Calculate sentence mean', variable=mean_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,mean_checkbox,True)

median_checkbox = tk.Checkbutton(window, text='Calculate sentence median', variable=median_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+200,y_multiplier_integer,median_checkbox)

def display_reminder(*args):
    if SA_algorithm_var.get()=='Stanford CoreNLP':
        reminders_util.checkReminder(config_filename,
                                     reminders_util.title_options_SA_CoreNLP_system_requirements,
                                     reminders_util.message_SA_CoreNLP_system_requirements,
                                     True)
    elif SA_algorithm_var.get()=='VADER':
        reminders_util.checkReminder(config_filename,
                                     reminders_util.title_options_SA_VADER,
                                     reminders_util.message_SA_VADER,
                                     True)
        if mean_var.get() or median_var.get()==True:
            reminders_util.checkReminder(config_filename,
                                         reminders_util.title_options_VADER_MeanMedian,
                                         reminders_util.message_VADER_MeanMedian,
                                         True)
    elif SA_algorithm_var.get() == 'SentiWordNet':
        reminders_util.checkReminder(config_filename,
                                    reminders_util.title_options_SA_SentiWordNet,
                                    reminders_util.message_SA_SentiWordNet,
                                    True)
    else:
        return
SA_algorithm_var.trace('w',display_reminder)

SA_algorithms=['*','Stanford CoreNLP','ANEW','hedonometer','SentiWordNet','VADER']

SA_algorithm_var.set('*')
SA_algorithm_lb = tk.Label(window, text='Select sentiment analysis algorithm')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,SA_algorithm_lb,True)
SA_algorithm_menu = tk.OptionMenu(window,SA_algorithm_var,*SA_algorithms)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,SA_algorithm_menu)

y_multiplier_integerSV=y_multiplier_integer-1

def activate_memory_var(*args):
    global memory_var
    if SA_algorithm_var.get()=='Stanford CoreNLP' or SA_algorithm_var.get()=='*':
        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+500, y_multiplier_integerSV,
                                                       memory_var_lb, True)

        memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
        memory_var.pack()
        memory_var.set(6)
        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+570,
                                                       y_multiplier_integer, memory_var)
    else:
        memory_var_lb.place_forget() #invisible
        try:
            memory_var.place_forget() #invisible
        except:
            return
SA_algorithm_var.trace('w',activate_memory_var)

sentence_index_var.set(0)
sentence_index_checkbox = tk.Checkbutton(window, state='disabled', text='Do sentiments fluctuate across a document (Sentiment scores by sentence index)', variable=sentence_index_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,sentence_index_checkbox)

shape_of_stories_var.set(0)
shape_of_stories_checkbox = tk.Checkbutton(window, text='Do sentiments fluctuate across documents (\'Shape of stories\')', variable=shape_of_stories_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,shape_of_stories_checkbox)

# doNotCreateIntermediateFiles_var.set(1)
# doNotCreateIntermediateFiles_checkbox = tk.Checkbutton(window, variable=doNotCreateIntermediateFiles_var, onvalue=1, offvalue=0)
# doNotCreateIntermediateFiles_checkbox.config(text="Do NOT produce intermediate csv files when processing all txt files in a directory")
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,doNotCreateIntermediateFiles_checkbox)

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

TIPS_lookup = {'Sentiment Analysis':"TIPS_NLP_Sentiment Analysis.pdf",'Java download install run':'TIPS_NLP_Java download install run.pdf'}
TIPS_options='Sentiment Analysis','Java download install run'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    if not IO_setup_display_brief:
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help", GUI_IO_util.msg_txtFile)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help", GUI_IO_util.msg_corpusData)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help", GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+1),"Help", "Please, tick the checkboxes for either Mean or Median in output csv files. BY DEFAULT, BOTH VALUES ARE COMPUTED.\n\nStanford CoreNLP Sentiment Analysis only computes mean values for each sentence.\n\nVADER only computes 'compound' values for each sentence.\n\nSentiWordNet as well does not provide sentence mean/median values.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+2),"Help", "Please, using the dropdown menu, select the algorithm to be used for computing sentiment analysis.\n\nSelect * to run ALL algorithms.\n\nStanford CoreNLP neural network approach to Sentiment Analysis typically achieves better results than dictionary-based approaches.\n\nCoreNLP computes mean values only for each sentence on a scale 0-4 (minimum-maximum).\n\nANEW (Affective Norms for English Words) computes sentiment/arousal/dominance mean/median values for each sentence using the ANEW ratings for SENTIMENT (VALENCE), AROUSAL, and DOMINANCE (CONTROL) by Bradley, M.M. & Lang, P.J. (2017). Affective Norms for English Words (ANEW): Instruction manual and affective ratings. Technical Report C-3. Gainesville, FL:UF Center for the Study of Emotion and Attention.\n\nContrary to all other approaches, the ANEW script computes three different measures, for SENTIMENT, AROUSAL, and DOMINANCE:\nSENTIMENT or VALENCE measures how pleasant/unpleasant a word makes us feel;\nAROUSAL measures how calm/excited a word makes us feel;\nDOMINANCE or CONTROL measures how dominated/in control a word makes us feel.\n\nTHE SCRIPT EXPECTS TO FIND THE FILE EnglishShortenedANEW.csv IN A ""lib"" SUBFOLDER OF THE FOLDER WHERE THE Sentiment_Analysis_ANEW.py SCRIPT IS STORED.\n\nIn OUTPUT, the script creates a csv file containing the calculated mean/median sentiment values for each sentence, where each rating can have a total of maximum 9 points.\n\nValues for sentiment, arousal, and dominance are classified on a scale 0-9, grouped in 5 categories: <3, >=3 and < 5, 5 (neutral), >5 and <8, >=8 and <=9.\n\nThe hedonometer algorithm uses the hedonometer.org rated dictionary to compute sentiment mean/median values for each sentence.\n\nThe script has been shown to work best with social media texts (e.g., Twitter), New York Times editorials, movie reviews, and product reviews.\n\nTHE SCRIPT EXPECTS TO FIND THE FILE hedonometer.json IN A ""lib"" SUBFOLDER OF THE FOLDER WHERE THE Sentiment_Analysis_Hedonometer.py SCRIPT IS STORED.\n\nIn OUTPUT, the script creates a csv file containing the calculated mean/median sentiment values for each sentence.\n\nSentiment values are classified on a scale 0-10, grouped in 3 categories: negative (>=0 and <4), neutral (>=4 and <=6), and positive (>6 and <=10).\n\nThe NLTK VADER (VADER, Valence Aware Dictionary and sEntiment Reasoner) uses the NLTK rated dictionary to compute sentiment mean/median values for each sentence.\n\nThe script has been shown to work best with social media texts (e.g., Twitter).\n\nIn INPUT the script expects either a single text file or a set of text files stored in a directory. THE SCRIPT ALSO EXPECTS TO FIND THE VADER RATED DICTIONARY FILE vader_lexicon.txt IN A ""lib"" SUBFOLDER OF THE FOLDER WHERE THE Sentiment_Analysis_VADER.py SCRIPT IS STORED.\n\nIn OUTPUT, the script creates a csv file containing the calculated 'compound' sentiment values for each sentence.\n\nMean and Median calculations are not available for VADER; VADER computes 'compound' values for each sentence.\n\nSentiment values are classified on a scale -1 (most negative) to 1 as (most positive) grouped in 3 categories: negative (<-0.05), neutral (>=-0.05 and <=0.05), and positive (>0.05 and <=1).\n\nVADER heavily relies on a number of NLTK libraries. If VADER fails to run, make sure that in command line you run\n   python -m nltk.downloader all")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+3),"Help", "Please, tick the checkboxes to display a line plot of sentiment scores by sentence index across a specific document.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+4),"Help", "Please, tick the checkboxes to open a specific GUI to compute the \'shape of stories\' of a set of sentiment scores across different documents.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+5),"Help",GUI_IO_util.msg_openOutputFiles)
help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The Python 3 Dictionary-based Analyses scripts calculate the mean/median values for various aspects of the language used in a text: sentiment, arousal, dominance.\n\nIn INPUT the scripts expect either a single text file or a set of text files stored in a directory. THE hedonometer, ANEW, AND VADER SCRIPTS ALSO EXPECT TO FIND DICTIONARY FILES IN A ""lib"" SUBFOLDER OF THE FOLDER WHERE THE PYTHON SCRIPTS ARE STORED.\n\nIn OUTPUT, the scripts create csv files containing the calculated mean/median values for each sentence."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options, IO_setup_display_brief)


GUI_util.window.mainloop()
