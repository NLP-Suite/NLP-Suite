import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "Ngrams-CoOccurrence_Viewer",
                                ['subprocess', 'os', 'tkinter', 'datetime','pandas','csv','glob','numpy']) == False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
import glob
import datetime
import pandas as pd
from subprocess import call

import IO_user_interface_util
import GUI_IO_util
import IO_files_util
import charts_util
import config_util
import reminders_util
import IO_csv_util
import NGrams_CoOccurrences_Viewer_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage,
        n_grams_list,
        n_grams_viewer_var,
        CoOcc_Viewer_var,
        search_words,
        # language_list,
        date_options,
        temporal_aggregation_var,
        viewer_options_list):

    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    else:
        config_filename = scriptName.replace('main.py', 'config.csv')

    # print(date_options, temporal_aggregation_var, date_format, items_separator_var, date_position_var)
    filesToOpen = []

    print("language_list",language_list)

    total_file_number = 0
    error_file_number = 0
    error_filenames = []
    error_flag = False

    # get the date options from filename
    filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = config_util.get_date_options(
        config_filename, config_input_output_numeric_options)
    extract_date_from_text_var = 0

    if n_grams_var==False and n_grams_viewer_var==False and CoOcc_Viewer_var==False:
        mb.showwarning(title='Warning',
                       message='There are no options selected.\n\nPlease, select one of the available options and try again.')
        return
    if inputDir=='' and (n_grams_viewer_var==True or CoOcc_Viewer_var==True):
        mb.showwarning(title='Warning',
                       message='You have selected to run the Viewer option but... this option requires a directory of txt files in input. Your configuration specifies a single txt file in input.\n\nPlease, select a directory in input or deselect the Viewer option and try again.')
        return

    if date_options:
        new_date_format = date_format_var.replace('yyyy', '%Y').replace('mm', '%m').replace('dd', '%d')
        for folder, subs, files in os.walk(inputDir):
            for filename in files:
                if not filename.endswith('.txt'):
                    continue
                filename = filename.replace('.txt', '')
                total_file_number = total_file_number + 1
                try:
                    date_text = ''
                    date_text = filename.split(items_separator_var)[date_position_var - 1]
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
        df.to_csv(error_output, encoding='utf-8', index=False)
        mb.showwarning(title='Warning',
                       message='There are ' + str(error_file_number) + ' files out of ' + str(
                           total_file_number) + ' processed in the selected input directory with errors in either the date format or the date position. \n\nThe selected date format is '+
                               str(date_format_var)+' and the selected date position is ' +
                               str(date_position_var) + '.\n\nClick OK to open a csv file with a list of files with erroneous dates. Check carefully, both date format and date position. Any erroneous file will need to be fixed or removed from the input directory before processing. You may also simply need to select a different date format and/or date position.')
        filesToOpen.append(error_output)
        if openOutputFiles == True:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)
        return


    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='nGrams-VIEWER',
                                                       silent=True)
    if outputDir == '':
        return

# VIEWER ____________________________________________________________________________________________

    if (n_grams_viewer_var == False and CoOcc_Viewer_var == False):
        return

    if (n_grams_viewer_var ==True or CoOcc_Viewer_var==True) and (createCharts==False):
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

    case_sensitive = False
    normalize=False
    scaleData=False
    useLemma=False
    fullInfo=False
    if 'sensitive' in str(viewer_options_list):
        case_sensitive = True
    if 'insensitive' in str(viewer_options_list):
        case_sensitive = False
    if 'Normalize' in str(viewer_options_list):
        normalize = True
    if 'Scale' in str(viewer_options_list):
        scaleData = True
    if 'Lemmatize' in str(viewer_options_list):
        useLemma = True

    if n_grams_viewer_var == 1 and len(search_words) > 0:
        if date_options == 0:
            mb.showwarning(title='Warning',
                           message='No Date options selected. The N-Grams routine requires date metadata (i.e., date information embedded in the document filenames, e.g., The New York Times_12-18-1899).\n\nPlease, tick the Date options checkbox, enter the appropariate date options and try again.')
            return

    reminders_util.checkReminder(scriptName,
                                 reminders_util.title_options_NGrams,
                                 reminders_util.message_NGrams,
                                 True)

    # run VIEWER ------------------------------------------------------------------------------------
    filesToOpen = NGrams_CoOccurrences_Viewer_util.run(
            inputDir,
            outputDir,
            config_filename,
            createCharts, chartPackage,
            n_grams_viewer_var,
            CoOcc_Viewer_var,
            search_words,
            language_list,
            useLemma,
            date_options,
            temporal_aggregation_var,
            number_of_years,
            date_format_var,
            items_separator_var,
            date_position_var,
            viewer_options_list)

    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)


# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command = lambda: run(GUI_util.inputFilename.get(), GUI_util.input_main_dir_path.get(), GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.create_chart_output_checkbox.get(),
                                 GUI_util.charts_package_options_widget.get(),
                                 n_grams_list,
                                 n_grams_viewer_var.get(),
                                 CoOcc_Viewer_var.get(),
                                 search_words_var.get(),
                                 date_options.get(),
                                 temporal_aggregation_var.get(),
                                 viewer_options_list)

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(3),
                                                 GUI_height_brief=480, # height at brief display
                                                 GUI_height_full=530, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=1, # to be added for full display
                                                 increment=1) # to be added for full display

GUI_label = 'Graphical User Interface (GUI) for N-Grams and Word Co-Occurrences Viewer'
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
config_input_output_numeric_options=[0,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)
window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

n_grams_list=[]
viewer_options_list=[]

n_grams_var= tk.IntVar()
n_grams_menu_var= tk.StringVar()
n_grams_options_menu_var= tk.StringVar()

n_grams_viewer_var = tk.IntVar()
CoOcc_Viewer_var = tk.IntVar()

search_words_var=tk.StringVar()

# date_format_var=tk.StringVar()
# items_separator_var=tk.StringVar()
# date_position_var=tk.IntVar()

date_options = tk.IntVar()
fileName_embeds_date = tk.IntVar()

temporal_aggregation_var=tk.StringVar()

viewer_options_menu_var=tk.StringVar()

normalize = tk.IntVar()
scaleData = tk.IntVar()
useLemma = tk.IntVar()
fullInfo = tk.IntVar()

n_grams_viewer_var.set(0)
Ngrams_checkbox = tk.Checkbutton(window, text='N-grams VIEWER', variable=n_grams_viewer_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   Ngrams_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "The N-grams VIEWER option requires in input file(s) with a date embedded in the filename")

CoOcc_Viewer_var.set(0)
CoOcc_checkbox = tk.Checkbutton(window, text='Co-Occurrences VIEWER', variable=CoOcc_Viewer_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NGrams_Co_occurrences_Viewer_CoOcc_Viewer_pos,y_multiplier_integer,CoOcc_checkbox)

search_words_var.set('')
search_words_lb = tk.Label(window, text='Search word(s)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,search_words_lb,True)
search_words_entry = tk.Entry(window, textvariable=search_words_var)
search_words_entry.configure(width=GUI_IO_util.widget_width_extra_long)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.NGrams_Co_occurrences_Viewer_search_words_entry_pos, y_multiplier_integer,
                                   search_words_entry,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Enter the comma-separated words/collocations to be searched;\nfor N-grams each item in the list will be plotted separately; for Co-occurrences all items will be plotted together ")
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NGrams_Co_occurrences_Viewer_search_words_entry_pos,y_multiplier_integer,search_words_entry)

date_options.set(0)
date_options_checkbox = tk.Checkbutton(window, text='Date options', variable=date_options, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,date_options_checkbox,True)

# date_options_checkbox.configure(state='disabled')

date_options_msg= tk.Label(window)
date_options_msg.config(text="Date option OFF")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NGrams_Co_occurrences_Viewer_date_options_pos,y_multiplier_integer,date_options_msg,True)

temporal_aggregation_var.set('year')
temporal_aggregation_lb = tk.Label(window,text='Aggregate by ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NGrams_Co_occurrences_Viewer_temporal_aggregation_lb_pos,y_multiplier_integer,temporal_aggregation_lb,True)

temporal_aggregation_menu = tk.OptionMenu(window, temporal_aggregation_var, 'group of years', 'year', 'quarter','month') #,'day'
temporal_aggregation_menu.configure(state="disabled")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NGrams_Co_occurrences_Viewer_temporal_aggregation_menu_pos,y_multiplier_integer,temporal_aggregation_menu)

number_of_years=0

def get_year_group(*args):
    global number_of_years
    if 'group' in temporal_aggregation_var.get():
        # "Enter the FIND & REPLACE strings (CASE SENSITIVE)", 'Find', 2, '', 'Replace', '' , numberOfWidgets=1, defaultValue='', textCaption2='', defaultValue2=''
        result = GUI_IO_util.enter_value_widget("Enter the number of years to aggregate by (e.g., 10, 23)","Enter value",1)
        try:
            number_of_years=int(result[0])
            # if not isinstance(result[0], int):
        except:
            mb.showwarning(title='Warning', message='You must enter an integer value. The value ' + str(result[0]) + ' is not an integer.')
            get_year_group()
        return number_of_years
temporal_aggregation_var.trace('w',get_year_group)


def check_dateFields(*args):
    if date_options.get() == 1:
        date_options_msg.config(text="Date option ON")
        temporal_aggregation_menu.config(state="normal")
    else:
        date_options_msg.config(text="Date option OFF")
        temporal_aggregation_menu.config(state="disabled")
date_options.trace('w',check_dateFields)

add_viewer_button = tk.Button(window, text='+', width=2,height=1,state='disabled',command=lambda: activate_viewer_var())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NGrams_Co_occurrences_Viewer_add_viewer_button_pos,y_multiplier_integer,add_viewer_button, True)

reset_viewer_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: reset_viewer_options_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NGrams_Co_occurrences_Viewer_reset_viewer_button_pos,y_multiplier_integer,reset_viewer_button,True)

show_viewer_button = tk.Button(window, text='Show', width=5,height=1,state='disabled',command=lambda: show_viewer_options_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NGrams_Co_occurrences_Viewer_show_viewer_button_pos,y_multiplier_integer,show_viewer_button,True)

viewer_menu_lb = tk.Label(window, text='VIEWER options')
viewer_options_menu_var.set('Case sensitive (default)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,viewer_menu_lb,True)
viewer_options_menu = tk.OptionMenu(window, viewer_options_menu_var, 'Case sensitive (default)', 'Case insensitive', 'Exact match (default)','Partial match','Normalize results','Scale results', 'Lemmatize words')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NGrams_Co_occurrences_Viewer_viewer_options_menu_pos,y_multiplier_integer,viewer_options_menu)

def reset_viewer_options_list():
    viewer_options_list.clear()
    viewer_options_menu_var.set('Case sensitive')
    viewer_options_menu.configure(state='normal')

def show_viewer_options_list():
    if len(viewer_options_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected VIEWER options.')
    else:
        mb.showwarning(title='Warning', message='The currently selected VIEWER options are:\n\n  ' + '\n  '.join(viewer_options_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

def activate_viewer_var():
    # Disable the + after clicking on it and enable the menu
    add_viewer_button.configure(state='disabled')
    viewer_options_menu.configure(state='normal')
    activate_viewer_options()

def activate_viewer_options(*args):
    if viewer_options_menu_var.get()!='':
        if viewer_options_menu_var.get() in viewer_options_list:
            mb.showwarning(title='Warning', message='The option has already been selected. Selection ignored.\n\nYou can see your current selections by clicking the Show button.')
            return
        if 'Partial match' in viewer_options_menu_var.get() or \
                'Normalize' in viewer_options_menu_var.get() or \
                'Scale' in viewer_options_menu_var.get():
                mb.showwarning(title='Warning', message='The option is not available yet.\n\nSorry!')
                return
        # remove the case option, when a different one is selected
        if 'insensitive' in viewer_options_menu_var.get() and 'sensitive' in str(viewer_options_list):
            viewer_options_list.remove('Case sensitive (default)')
        if 'sensitive' in viewer_options_menu_var.get() and 'insensitive' in str(viewer_options_list):
            viewer_options_list.remove('Case insensitive')
        # if len(viewer_options_list) > 0:
        #     add_viewer_button.configure(state='normal')
        #     reset_viewer_button.configure(state='normal')
        #     show_viewer_button.configure(state='normal')
        #     return
        viewer_options_list.append(viewer_options_menu_var.get())
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

activate_viewer_options()

def clear_n_grams_list():
    n_grams_list.clear()

def clear(e):
    n_grams_list.clear()
    search_words_var.set('')
    viewer_options_list.clear()
    viewer_options_menu_var.set('Case sensitive')
    temporal_aggregation_var.set('year')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

n_grams_list=[]

def activate_allOptions():
    Ngrams_checkbox.configure(state='normal')
    CoOcc_checkbox.configure(state='normal')
    search_words_entry.configure(state='normal')
    date_options_checkbox.config(state='normal')
    if "INPUT FILE" in GUI_util.IO_setup_var.get():
        input_label= 'INPUT FILE'
    else:
        input_label = 'INPUT DIR'
    if n_grams_viewer_var.get() and ('(Date: ' not in GUI_util.IO_setup_var.get()):
        mb.showwarning(title='Warning',message='The N-grams VIEWER option requires file(s) with a date embedded in the filename.\n\nYour current ' + input_label + ' selection does not show the Date option (THE DATE OPTION IS SET IN THE I/O SETUP GUI; CLICK THE "Setup INPUT/OUTPUT configuration" BUTTON TO OPEN THE GUI).\n\nPlease, select a different Input configuration or run the Co-Occurrences VIEWER option instead that does not require a date embedded in filenames.')
        n_grams_viewer_var.set(0)
    if n_grams_viewer_var.get() or CoOcc_Viewer_var.get():
        search_words_entry.configure(state='normal')
        date_options_checkbox.config(state='normal')
        viewer_options_menu.config(state='normal')
    else:
        search_words_entry.configure(state='disabled')
        date_options_checkbox.config(state='disabled')
        viewer_options_menu.config(state='disabled')
n_grams_viewer_var.trace('w', lambda x, y, z: activate_allOptions())
CoOcc_Viewer_var.trace('w', lambda x, y, z: activate_allOptions())

activate_allOptions()

open_GUI_Ngrams_button = tk.Button(window, width=GUI_IO_util.widget_width_short, text='Compute N-grams (Open GUI)',command=lambda: call("python style_analysis_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_GUI_Ngrams_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

open_GUI_search_button = tk.Button(window, width=GUI_IO_util.widget_width_short, text='Search words/collocations (Open GUI)',command=lambda: call("python file_search_byWord_main.py", shell=True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   open_GUI_search_button,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to open the GUI")

videos_lookup = {'N grams Co Occurrences VIEWER':'https://www.youtube.com/watch?v=67YejULroIo'}
videos_options='N grams Co Occurrences VIEWER'

TIPS_lookup = {'N-Grams (word & character)':"TIPS_NLP_Ngram (word & character).pdf",
               'Google Ngram Viewer':'TIPS_NLP_Ngram Google Ngram Viewer.pdf',
               'NLP Suite Ngram and Word Co-Occurrence Viewer':"TIPS_NLP_Ngram and Word Co-Occurrence Viewer.pdf",
               'Style analysis':'TIPS_NLP_Style analysis.pdf',
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',
               'Things to do with words: Overall view': 'TIPS_NLP_Things to do with words Overall view.pdf',
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures':'TIPS_NLP_Statistical measures.pdf'}
TIPS_options='N-Grams (word & character)','Google Ngram Viewer','NLP Suite Ngram and Word Co-Occurrence Viewer','Style analysis','English Language Benchmarks', 'Things to do with words: Overall view','Excel smoothing data series','csv files - Problems & solutions','Statistical measures'

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
        'Please, tick the Ngram VIEWER checkbox if you wish to run the Ngram Viewer script.'\
        '\n\nTick the Co-Occurrence VIEWER checkbox if you wish to run the Co-Occurrene Viewer script.'\
        '\n\nYou can run both Viewers at the same time.'\
        '\n\nThe NGrams part of the algorithm requires date metadata, i.e., a date embedded in the filename (e.g., The New York Time_2-18-1872). '\
        'YOU CAN SETUP DATES EMBEDDED IN FILENAMES BY CLICKING THE "Setup INPUT/OUTPUT configuration" WIDGET AT THE TOP OF THIS GUI AND THEN TICKING THE CHECKBOXES "Filename embeds multiple items" AND "Filename embeds date" WHEN THE NLP_setup_IO_main GUI OPENS.'\
        '\n\nFor both viewers, results will be visualized in Excel line plots.'\
        '\n\nFor n-grams the routine will display the FREQUENCY OF NGRAMS (WORDS), NOT the frequency of documents where searched word(s) appear. '\
        'For Word Co-Occurrences the routine will display the FREQUENCY OF DOCUMENTS where searched word(s) appear.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
        'Please, enter the comma-separated list of single words or collocations (i.e., sets of words such as coming out, beautiful sunny day) for which you want to know N-Grams/Co-occurrences statistics (e.g., woman, man, job). Leave blank if you do not want NGrams data. Both NGrams and co-occurrences words can be entered.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
        'Please, tick the checkbox if the filenames embed a date (e.g., The New York Times_12-19-1899). The DATE OPTIONS are required for N-grams; optional for word co-occurrences. ' \
            'YOU CAN SETUP DATES EMBEDDED IN FILENAMES BY CLICKING THE "Setup INPUT/OUTPUT configuration" WIDGET AT THE TOP OF THIS GUI AND THEN TICKING THE CHECKBOXS "Filename embeds multiple items" AND "Filename embeds date" WHEN THE NLP_setup_IO_main GUI OPENS.'\
            '\n\nPlease, using the dropdown menu, select the level of temporal aggregation you want to apply to your documents: group of years, year, quarter, month.'\
            '\n\nFor both viewers, results will be visualized in Excel line plots.'\
            '\n\nFor n-grams the routine will display the FREQUENCY OF NGRAMS (WORDS), NOT the frequency of documents where searched word(s) appear. '\
            'For Word Co-Occurrences the routine will display the FREQUENCY OF DOCUMENTS where searched word(s) appear.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
        'Please, use the dropdown menu to select various options that can be applied to the VIEWER. Multiple criteria can be seleced by clicking on the + button. Currently selected criteria can be displayed by clicking on the Show button.\n\nYou can make your searches CASE SENSITIVE.\n\nYou can NORMALIZE results. Only works for N-Grams. Formula: search word frequency / total number of all words e.g: word "nurse" occurs once in year 1892, and year 1892 has a total of 1000 words. Then the normalized frequency will be 1/1000.\n\nYou can SCALE results. Only works for N-Grams. It applies the min-max normalization to frequency of search words. After the min-max normalization is done, each column of data (i.e., each search word) will fall in the same range.\n\nYou can LEMMATIZE words for your searches (e.g., be instead of being, is, was). The routine relies on the Stanford CoreNLP for lemmatizing words.\n\nFinally, you can select to display minimal information or full information.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
        'Please, click on the button to open the GUI where you can compute n-grams.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        'Please, click on the button to open a GUI with more options for word/collocation searches.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1

y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="""
The NGrams_CoOccurrences script allows searches for Ngrams or word co-occurrences, i.e., key words (e.g., “nursery school” (a 2-gram or bigram), “kindergarten” (a 1-gram or unigram) and “child care” (another bigram) that occur in a set of documents.
\n\nThe NGrams VIEWER requires date metadata, i.e., a date embedded in the filename (e.g., The New York Time_2-18-1872). It computes the number of words that appear in documents within a selected time period (e.g., month, year). It works similarly to Google Ngram Viewer except this routine works on documents supplied by the user rather than on the millions of Google books (see https://books.google.com/ngrams/info).
'\n\nYOU CAN SETUP DATES EMBEDDED IN FILENAMES BY CLICKING THE "Setup INPUT/OUTPUT configuration" WIDGET AT THE TOP OF THIS GUI AND THEN TICKING THE CHECKBOXS "Filename embeds multiple items" AND "Filename embeds date" WHEN THE NLP_setup_IO_main GUI OPENS.'
\n\nThe routine relies on Stanza for lemmatizing words.
\n\n   For NGRAMS, the routine will display the FREQUENCY OF NGRAMS (WORDS), NOT the FREQUENCY OF DOCUMENTS where searched word(s) appear.
\n\n   For CO-OCCURRING words, the routine will display the FREQUENCY OF DOCUMENTS where searched word(s) appear together in the same document, NOT the frequency of the searched word(s) as with NGrams.
\n\nNGRAMS and CO-OCCURRING words DO NOT MAKE MUCH SENSE WITH A SINGLE FILE!
"""

readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName, False)

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

state = str(GUI_util.run_button['state'])
if state == 'disabled':
    error = True
    # check to see if there is a GUI-specific config file, i.e., a CoNLL table file, and set it to the setup_IO_menu_var
    if os.path.isfile(os.path.join(GUI_IO_util.configPath, config_filename)):
        GUI_util.setup_IO_menu_var.set('GUI-specific I/O configuration')
        mb.showwarning(title='Warning',
               message="Since a GUI-specific " + config_filename + " file is available, the I/O configuration has been automatically set to GUI-specific I/O configuration.")
        error = False

GUI_util.window.mainloop()
