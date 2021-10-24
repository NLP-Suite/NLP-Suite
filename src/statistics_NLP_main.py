import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Statistics_NLP",['tkinter'])==False:
    sys.exit(0)

import tkinter as tk
import tkinter.messagebox as mb

import GUI_IO_util
import IO_csv_util
import IO_user_interface_util
import IO_files_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,input_main_dir_path,outputDir,openOutputFiles,createExcelCharts,
        corpus_stats, corpus_options_menu_var, n_grams, n_grams_menu_var, n_grams_list, all_csv_stats,csv_field_stats,
        csv_list,hover_over_list, groupBy_list, script_to_run):

    filesToOpen=[]

    window=GUI_util.window
    if input_main_dir_path=='' and corpus_stats:
        mb.showwarning(title='Input error', message='The selected option - ' + script_to_run + ' - requires a directory in input.\n\nPlease, select a directory and try again.')
        return

    if inputFilename!='' and (all_csv_stats or csv_field_stats):
        if inputFilename[-4:]!='.csv':
            mb.showwarning(title='Input error', message='The selected option - ' + script_to_run + ' - requires an input file of type csv.\n\nPlease, select a csv input file and try again.')
            return

    if inputFilename!='' and (n_grams):
        if inputFilename[-4:]!='.txt':
            mb.showwarning(title='Input error', message='The selected option - ' + script_to_run + ' - requires an input file of type txt (or an input directory).\n\nPlease, select a txt input file (or an input directory) and try again.')
            return

    if corpus_stats == False and n_grams == False and all_csv_stats == False and  csv_field_stats == False:
        mb.showwarning(title='Warning', message='There are no options selected.\n\nPlease, select one of the available options and try again.')
        return

    if corpus_stats or n_grams:
        if IO_libraries_util.inputProgramFileCheck('statistics_txt_util.py')==False:
            return
        else:
            import statistics_txt_util

    if all_csv_stats or csv_field_stats:
        if IO_libraries_util.inputProgramFileCheck('statistics_csv_util.py')==False:
            return
        else:
            import statistics_csv_util
        if csv_field_stats and len(csv_list) == 0:
            mb.showwarning(title='Warning', message='You have selected to compute the frequency of a csv file field but no field has been selected.\n\nPlease, select a csv file field and try again.')
            return

    if corpus_stats:
        stopwords_var = False
        lemmatize_var = False
        if corpus_options_menu_var=='*':
            stopwords_var=True
            lemmatize_var=True
        if 'Lemmatize' in corpus_options_menu_var:
            lemmatize_var=True
        if 'stopwords' in corpus_options_menu_var:
            stopwords_var=True
        if "*" in corpus_options_menu_var or lemmatize_var==True or stopwords_var==True:
            tempOutputFiles=statistics_txt_util.compute_corpus_statistics(window,inputFilename,input_main_dir_path,outputDir,False,createExcelCharts,stopwords_var, lemmatize_var)
            if tempOutputFiles!=None:
                filesToOpen.extend(tempOutputFiles)

        if "Compute lines length" or "*" in corpus_options_menu_var:
            tempOutputFiles=statistics_txt_util.read_line(window, inputFilename, input_main_dir_path, outputDir,
                                                          False, createExcelCharts)
            if tempOutputFiles!=None:
                filesToOpen.extend(tempOutputFiles)

    elif all_csv_stats:
        tempOutputFiles=statistics_csv_util.compute_field_statistics_NoGroupBy(window,inputFilename,outputDir,openOutputFiles,createExcelCharts)
    elif csv_field_stats:
        if len(csv_list) == 0:
            mb.showwarning(title='Warning', message='You have selected to compute the frequency of a csv file field but no field has been selected.\n\nPlease, select a csv file field and try again.')
            return
        columns_to_be_plotted=[] # field not used
        tempOutputFiles=statistics_csv_util.compute_stats_NLP_main(window,
                                                           inputFilename,
                                                           '',
                                                           outputDir,
                                                           openOutputFiles, createExcelCharts,
                                                           columns_to_be_plotted,
                                                           csv_list,hover_over_list,groupBy_list,
                                                           'CSV')
    elif n_grams:
        n_grams_word_var = False
        n_grams_character_var = False
        normalize = False
        n_grams_size = 4  # default number of n_grams
        excludePunctuation = False
        bySentenceIndex_word_var = False
        bySentenceIndex_character_var = False
        if n_grams_menu_var == "Word":
            n_grams_word_var = True
        else:
            n_grams_character_var = True
        bySentenceIndex_character_var = False
        if 'Hapax' in str(n_grams_list):
            n_grams_size = 1
        if 'punctuation' in str(n_grams_list):
            excludePunctuation = True
        if 'sentence index' in str(n_grams_list):
            if n_grams_menu_var == "Word":
                bySentenceIndex_word_var = True
            else:
                bySentenceIndex_character_var = True

        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'N-Grams start',
                                           'Started running ' + n_grams_menu_var + ' n-grams at', True,
                                           'You can follow the script in command line.')

        if n_grams_word_var or n_grams_character_var or bySentenceIndex_word_var or bySentenceIndex_character_var:
            inputFilename = ''  # for now we only process a whole directory
            if IO_libraries_util.inputProgramFileCheck('statistics_txt_util.py') == False:
                return

        if n_grams_word_var or bySentenceIndex_word_var:
            tempOutputFiles=statistics_txt_util.compute_character_word_ngrams(window,inputFilename,input_main_dir_path,outputDir,n_grams_size, normalize, excludePunctuation, 1, openOutputFiles, createExcelCharts,
                                                              bySentenceIndex_word_var)
        if n_grams_character_var or bySentenceIndex_character_var:
            tempOutputFiles=statistics_txt_util.compute_character_word_ngrams(window,inputFilename,input_main_dir_path,outputDir,n_grams_size, normalize, excludePunctuation,  0, openOutputFiles, createExcelCharts,
                                                              bySentenceIndex_character_var)
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'N-Grams end',
                                           'Finished running ' + n_grams_menu_var + ' n-grams at', True, '', True, startTime)

        # statistics_txt_util.compute_character_word_ngrams(window,inputFilename,input_mai
    if openOutputFiles == 1:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
#def run(inputFilename,input_main_dir_path,outputDir, dictionary_var, annotator_dictionary, DBpedia_var, annotator_extractor, openOutputFiles):
run_script_command=lambda: run(
                GUI_util.inputFilename.get(),
                GUI_util.input_main_dir_path.get(),
                GUI_util.output_dir_path.get(),
                GUI_util.open_csv_output_checkbox.get(),
                GUI_util.create_Excel_chart_output_checkbox.get(),
                corpus_stats_var.get(),
                corpus_options_menu_var.get(),
                # stopwords_var.get(),
                # lemmatize_var.get(),
                n_grams_var.get(),
                n_grams_menu_var.get(),
                n_grams_list,
                all_csv_stats_var.get(),
                csv_field_stats_var.get(),
                csv_list,
                hover_over_list,
                groupBy_list,
                script_to_run)

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_width=1220
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

GUI_label='Graphical User Interface (GUI) for Statistical Analyses'
config_filename='statistics-config.txt'
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

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

window = GUI_util.window
config_input_output_options = GUI_util.config_input_output_options
config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_options, config_filename,IO_setup_display_brief)

n_grams_list=[]
csv_list = []
hover_over_list = []
groupBy_list = []

corpus_stats_var = tk.IntVar()
corpus_options_menu_var = tk.StringVar()
# stopwords_var = tk.IntVar()
# lemmatize_var = tk.IntVar()

all_csv_stats_var = tk.IntVar()
csv_field_stats_var = tk.IntVar()
csv_field_var = tk.StringVar()
csv_hover_over_field_var = tk.StringVar()
csv_groupBy_field_var = tk.StringVar()
n_grams_var = tk.IntVar()
n_grams_menu_var = tk.StringVar()
csv_options_menu_var = tk.StringVar()
n_grams_options_menu_var = tk.StringVar()

script_to_run = ''


def get_script_to_run(text):
    global script_to_run
    script_to_run = text


def clear(e):
    corpus_stats_var.set(0)
    corpus_options_menu_var.set('*')
    all_csv_stats_var.set(0)
    csv_field_stats_var.set(0)
    n_grams_menu_var.set('Word')
    reset_n_grams_list()
    reset_csv_list()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)


corpus_stats_var.set(0)
corpus_field_checkbox = tk.Checkbutton(window, text='Compute corpus statistics', variable=corpus_stats_var, onvalue=1,
                                       offvalue=0, command=lambda: get_script_to_run('Compute corpus statistics'))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               corpus_field_checkbox, True)

corpus_options_menu_var.set('*')
corpus_options_menu_lb = tk.Label(window, text='Corpus statistics options')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+400,y_multiplier_integer,corpus_options_menu_lb,True)
corpus_options_menu = tk.OptionMenu(window, corpus_options_menu_var, '*','Lemmatize words', 'Exclude stopwords & punctuation', 'Compute lines length')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+560,y_multiplier_integer,corpus_options_menu)

def activate_corpus_options(*args):
    if corpus_stats_var.get()==True:
        corpus_options_menu.configure(state='normal')
    else:
        corpus_options_menu.configure(state='disabled')
corpus_stats_var.trace('w',activate_corpus_options)

n_grams_var.set(0)
n_grams_checkbox = tk.Checkbutton(window, text='Compute N-grams', variable=n_grams_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,n_grams_checkbox,True)

n_grams_menu_var.set('Word')
n_grams_menu_lb = tk.Label(window, text='N-grams type')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+140,y_multiplier_integer,n_grams_menu_lb,True)
n_grams_menu = tk.OptionMenu(window, n_grams_menu_var, 'Character', 'Word','DEPREL','POSTAG')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(),y_multiplier_integer,n_grams_menu)

n_grams_options_menu_lb = tk.Label(window, text='N-grams options')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,n_grams_options_menu_lb,True)
n_grams_options_menu = tk.OptionMenu(window, n_grams_options_menu_var, 'Hapax legomena (unigrams)','Normalize n-grams', 'Exclude punctuation (word n-grams only)','By sentence index','End sentence/Begin sentence (word n-grams only)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+140,y_multiplier_integer,n_grams_options_menu,True)

add_n_grams_button = tk.Button(window, text='+', width=2,height=1,state='disabled',command=lambda: activate_n_grams_var())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+500,y_multiplier_integer,add_n_grams_button, True)

reset_n_grams_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: reset_n_grams_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+540,y_multiplier_integer,reset_n_grams_button,True)

show_n_grams_button = tk.Button(window, text='Show', width=5,height=1,state='disabled',command=lambda: show_n_grams_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+600,y_multiplier_integer,show_n_grams_button)

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

all_csv_stats_var.set(0)
all_csv_field_checkbox = tk.Checkbutton(window, text='Compute statistics on all csv-file fields (numeric fields only)',
                                        variable=all_csv_stats_var, onvalue=1, offvalue=0,
                                        command=lambda: get_script_to_run(
                                            'Compute statistics on all csv-file fields (numeric fields only)'))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               all_csv_field_checkbox)

csv_field_stats_var.set(0)
csv_field_checkbox = tk.Checkbutton(window, text='Compute frequencies of specific csv-file field',
                                    variable=csv_field_stats_var, onvalue=1, offvalue=0,
                                    command=lambda: get_script_to_run('Compute frequencies of specific csv-file field'))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               csv_field_checkbox, True)

menu_values = ['']

reset_csv_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: reset_csv_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+300,y_multiplier_integer,reset_csv_button,True)

show_csv_button = tk.Button(window, text='Show', width=5,height=1,state='disabled',command=lambda: show_csv_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+360,y_multiplier_integer,show_csv_button,True)

csv_field_lb = tk.Label(window, text='csv field')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 430, y_multiplier_integer,
                                               csv_field_lb, True)
csv_field_menu = tk.OptionMenu(window, csv_field_var, *menu_values)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 500, y_multiplier_integer,
                                               csv_field_menu)

def reset_csv_list():
    csv_list.clear()
    hover_over_list.clear()
    groupBy_list.clear()
    csv_field_var.set('')
    csv_groupBy_field_var.set('')
    csv_hover_over_field_var.set('')
    csv_field_menu.configure(state='normal')

def show_csv_list():
    if len(csv_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected csv field options.')
    else:
        mb.showwarning(title='Warning', message='The currently selected csv field options are:\n'
        '\n   CSV FIELD: ' + ', '.join(csv_list) +
        '\n   GROUP-BY FIELD(S): ' + ', ' .join(groupBy_list) +
        '\n   HOVER-OVER FIELD(S): ' + ', ' .join(hover_over_list) +
        '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

def activate_plus1(*args):
    # if csv_field_var.get() in csv_list:
    # 	mb.showwarning(title='Warning', message='The csv field "'+ csv_field_var.get() + '" is already in your selection list: '+ str(csv_list) + '.\n\nPlease, select another field.')
    # 	window.focus_force()
    # 	return
    if csv_field_var.get() != '':
        csv_list.clear()  # only 1 value is now allowed
        csv_list.append(csv_field_var.get())
        csv_hover_over_field_menu.configure(state='normal')
        csv_groupBy_field_menu.configure(state='normal')


# csv_field_menu.configure(state="disabled")
# add_field1_button.configure(state='normal')
csv_field_var.trace('w', activate_plus1)


def activate_hover_over_field_menu():
    if csv_hover_over_field_var.get() != '':
        csv_hover_over_field_menu.configure(state="normal")

# add extra group_by field
add_field3_button = tk.Button(window, text='+', width=2, height=1, state='disabled',
                              command=lambda: activate_groupBy_field_menu())
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 20, y_multiplier_integer,
                                               add_field3_button, True)

csv_groupBy_field_lb = tk.Label(window, text='Group-by field')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 60, y_multiplier_integer,
                                               csv_groupBy_field_lb, True)
csv_groupBy_field_menu = tk.OptionMenu(window, csv_groupBy_field_var, *menu_values)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 160, y_multiplier_integer,
                                               csv_groupBy_field_menu, True)

# add extra hover_over field
add_field2_button = tk.Button(window, text='+', width=2, height=1, state='disabled',
                              command=lambda: activate_hover_over_field_menu())
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 500, y_multiplier_integer,
                                               add_field2_button, True)

csv_hover_over_field_lb = tk.Label(window, text='Hover-over field')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 540, y_multiplier_integer,
                                               csv_hover_over_field_lb, True)
csv_hover_over_field_menu = tk.OptionMenu(window, csv_hover_over_field_var, *menu_values)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 640, y_multiplier_integer,
                                               csv_hover_over_field_menu)


# groupBy_list=[]
def activate_plus2(*args):
    if csv_hover_over_field_var.get() in hover_over_list:
        mb.showwarning(title='Warning',
                       message='The csv field "' + csv_hover_over_field_var.get() + '" is already in your selection list: ' + str(
                           hover_over_list) + '.\n\nPlease, select another field.')
        window.focus_force()
        return
    if csv_hover_over_field_var.get() != '':
        hover_over_list.append(csv_hover_over_field_var.get())
        csv_hover_over_field_menu.configure(state="disabled")
        add_field2_button.configure(state='normal')

csv_hover_over_field_var.trace('w', activate_plus2)


def activate_groupBy_field_menu():
    if csv_groupBy_field_var.get() != '':
        csv_groupBy_field_menu.configure(state="normal")


def activate_plus3(*args):
    if csv_groupBy_field_var.get() in groupBy_list:
        mb.showwarning(title='Warning',
                       message='The csv field "' + csv_groupBy_field_var.get() + '" is already in your selection list: ' + str(
                           groupBy_list) + '.\n\nPlease, select another field.')
        window.focus_force()
        return
    if csv_groupBy_field_var.get() != '':
        groupBy_list.append(csv_groupBy_field_var.get())
        csv_groupBy_field_menu.configure(state="disabled")
        add_field3_button.configure(state='normal')


csv_groupBy_field_var.trace('w', activate_plus3)


def activate_allOptions(menu_values, from_csv_field_stats_var=False):
    if inputFilename.get() == '' and input_main_dir_path.get() == '':
        clear('Escape')
        corpus_field_checkbox.configure(state='disabled')
        all_csv_field_checkbox.configure(state='disabled')
        csv_field_checkbox.configure(state='disabled')
        n_grams_menu.configure(state='disabled')
        n_grams_options_menu .configure(state='disabled')
    else:
        if inputFilename.get()[-4:] == '.txt':
            all_csv_field_checkbox.configure(state='disabled')
            csv_field_checkbox.configure(state='disabled')
            corpus_field_checkbox.configure(state='normal')
            n_grams_checkbox.configure(state='normal')
            n_grams_menu.configure(state='normal')
            n_grams_options_menu.configure(state='normal')
        elif inputFilename.get()[-4:] == '.csv':
            all_csv_field_checkbox.configure(state='normal')
            csv_field_checkbox.configure(state='normal')
            corpus_field_checkbox.configure(state='disabled')
            n_grams_checkbox.configure(state='disabled')
            n_grams_menu.configure(state='disabled')
            n_grams_options_menu .configure(state='disabled')

        if input_main_dir_path.get() != '':
            corpus_field_checkbox.configure(state='normal')
            all_csv_field_checkbox.configure(state='normal')
            csv_field_checkbox.configure(state='normal')
            n_grams_checkbox.configure(state='normal')
            n_grams_menu.configure(state='disabled')
            n_grams_options_menu.configure(state='disabled')

    if corpus_stats_var.get() == 1:
        all_csv_field_checkbox.configure(state='disabled')
        csv_field_checkbox.configure(state='disabled')
        n_grams_checkbox.configure(state='disabled')
        n_grams_menu.configure(state='disabled')
        n_grams_options_menu .configure(state='disabled')

    if all_csv_stats_var.get() == 1:
        corpus_field_checkbox.configure(state='disabled')
        csv_field_checkbox.configure(state='disabled')
        n_grams_checkbox.configure(state='disabled')
        n_grams_menu.configure(state='disabled')
        n_grams_options_menu.configure(state='disabled')

    if csv_field_stats_var.get() == 1:
        if from_csv_field_stats_var == True:
            if menu_values == ['']:  # first time through
                changed_filename()
        corpus_field_checkbox.configure(state='disabled')
        all_csv_field_checkbox.configure(state='disabled')
        n_grams_checkbox.configure(state='disabled')
        n_grams_menu.configure(state='disabled')
        n_grams_options_menu .configure(state='disabled')
        reset_csv_button.configure(state='normal')
        show_csv_button.configure(state='normal')
        csv_field_menu.configure(state='normal')
        csv_hover_over_field_menu.configure(state='disabled')
        csv_groupBy_field_menu.configure(state='disabled')
    else:
        csv_field_var.set('')
        reset_csv_button.configure(state='normal')
        show_csv_button.configure(state='normal')
        csv_hover_over_field_var.set('')
        csv_field_menu.configure(state='disabled')
        csv_hover_over_field_menu.configure(state='disabled')
        csv_groupBy_field_menu.configure(state='disabled')

    if n_grams_var.get() == 1:
        corpus_field_checkbox.configure(state='disabled')
        all_csv_field_checkbox.configure(state='disabled')
        csv_field_checkbox.configure(state='disabled')
        n_grams_menu.configure(state='normal')
        n_grams_options_menu.configure(state='normal')
    else:
        n_grams_menu.configure(state='disabled')
        n_grams_options_menu.configure(state='disabled')

corpus_stats_var.trace('w', lambda x, y, z: activate_allOptions(menu_values))
all_csv_stats_var.trace('w', lambda x, y, z: activate_allOptions(menu_values))
csv_field_stats_var.trace('w', lambda x, y, z: activate_allOptions(menu_values, True))
n_grams_var.trace('w', lambda x, y, z: activate_allOptions(menu_values))

activate_allOptions(menu_values)


# the first call is placed at the buttom of this script so that all widgets would have been dispayed
def changed_filename(*args):
    clear('Escape')
    global menu_values
    activate_allOptions(menu_values)
    if inputFilename.get() == '' or inputFilename.get()[-4:] != '.csv':
        activate_allOptions(menu_values)
        return
    menu_values = IO_csv_util.get_csvfile_headers(inputFilename.get(), True)
    m = csv_field_menu["menu"]
    m1 = csv_hover_over_field_menu["menu"]
    m2 = csv_groupBy_field_menu["menu"]
    m.delete(0, "end")
    m1.delete(0, "end")
    m2.delete(0, "end")
    for s in menu_values:
        m.add_command(label=s, command=lambda value=s: csv_field_var.set(value))
        m1.add_command(label=s, command=lambda value=s: csv_hover_over_field_var.set(value))
        m2.add_command(label=s, command=lambda value=s: csv_groupBy_field_var.set(value))
    activate_allOptions(menu_values)

# at the bottom of the script after laying out the GUI
# inputFilename.trace('w',changed_filename)
# changed_filename()

TIPS_lookup = {'Statistical tools in the NLP Suite': 'TIPS_NLP_Statistical tools.pdf',
               'Statistical descriptive measures': "TIPS_NLP_Statistical measures.pdf",
               'Lemmas & stopwords':'TIPS_NLP_NLP Basic Language.pdf',
               'Style measures': 'TIPS_NLP_Style measures.pdf',
               'N-Grams (word & character)': "TIPS_NLP_Ngrams (word & character).pdf",
               'NLP Ngram and Word Co-Occurrence Viewer': "TIPS_NLP_NLP Ngram and Co-Occurrence Viewer.pdf",
               'Google Ngram Viewer': 'TIPS_NLP_Ngram Google Ngram Viewer.pdf'}
TIPS_options = 'Statistical tools in the NLP Suite', 'Statistical descriptive measures', 'Lemmas & stopwords','Style measures', 'N-Grams (word & character)', 'NLP Ngram and Word Co-Occurrence VIEWER', 'Google Ngram Viewer'


# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, basic_y_coordinate, y_step):
    if not IO_setup_display_brief:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help", GUI_IO_util.msg_txtFile)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step, "Help",
                                      GUI_IO_util.msg_corpusData)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 2, "Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+1), "Help",
                                  'Please, tick the checkbox if you wish to compute basic statistics on your corpus. Users have the option to lemmatize words and exclude stopwords from word counts.\n\nIn INPUT the script expects a set of txt files.\n\nIn OUTPUT, the script generates the following three files:\n  1. csv file of frequencies of the twenty most frequent words;\n  2. csv file of the following statistics for each column in the previous csv file and for each document in the corpus: Count, Mean, Mode, Median, Standard deviation, Minimum, Maximum, Skewness, Kurtosis, 25% quantile, 50% quantile; 75% quantile;\n  3. Excel line chart of the number of sentences and words for each document.')
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+2), "Help",
                                  'Please, tick the \'Compute n-grams\' checkbox if you wish to compute n-grams.\n\nN-grams can be computed for characters, words, POSTAG and DEPREL values. Use the dropdown menu to select the desired option.\n\nIn INPUT the script expects a single txt file or a directory containing a set of txt files.\n\nIn OUTPUT, the script generates a set of csv files each containing word n-grams between 1 and 4.\n\nWhen n-grams are computed by sentence index, the sentence displayed in output is always the first occurring sentence.')
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+3), "Help",
                                  'Please, use the dropdown menu to select various options that can be applied to n-grams. You can make multiple selections by clicking on the + button.\n\nThe default number of n-grams computed is 4, unless you select the Hapax legomena option for unigrams.\n\nN-grams can be normalized, i.e., their frequency values are divided by the number of words or POSTAG-DEPREL values in a document.\n\nPunctuation can be excluded when computing n-grams (Google, for instance, exclude punctuation from its Ngram Viewer (https://books.google.com/ngrams).\n\nN-grams can be computed by sentence index.\n\nFinally, you can run a special type of n-grams that computes the last 2 words in a sentence and the first 2 words of the next sentence, a rhetorical figure of repetition for the analysis of style.')
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+4), "Help",
                                  'Please, tick the checkbox if you wish to compute basic statistics on all the numeric fields of a csv file.\n\nIn INPUT the script expects a csv file.\n\nIn OUTPUT, the script generates a csv file of statistics for each numeric field in the input csv file: Count, Mean, Mode, Median, Standard deviation, Minimum, Maximum, Skewness, Kurtosis, 25% quantile, 50% quantile; 75% quantile.')
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+5), "Help",
                                  'Please, tick the checkbox if you wish to compute the frequency of a specific field of a csv file. ONLY ONE FIELD CAN BE CURRENTLY SELECTED. But multiple group-by fields and hover-over fields can be selected.\n\nYou can select to group the frequencies by specific field(s) and/or have hover-over field(s) if you wish to display information in an Excel chart.\n\nIn INPUT the script expects a csv file.\n\nIn OUTPUT, the script generates a csv file of frequencies for the selected field.')
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+6), "Help",
                                  'Please, using the dropdown menu, for the selected csv field, selected  one or more group-by fields (e.g., compute the frequencies of POSTAG values by DocumentID in a CoNLL table displaying both words and lemmas in hover over.) \n\nMultiple fields can be selected by pressing the + button.')
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+7), "Help",
                                  GUI_IO_util.msg_openOutputFiles)

help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), GUI_IO_util.get_basic_y_coordinate(),
             GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message = "The Python 3 scripts provide ways of building ditionaries and of using these dictionary entries to annotate documents for matching terms found in a dictionary file and in DBpedia."
readMe_command = lambda: GUI_IO_util.readme_button(window, GUI_IO_util.get_help_button_x_coordinate(),
                                                   GUI_IO_util.get_basic_y_coordinate(), "Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_options, y_multiplier_integer, readMe_command, TIPS_lookup, TIPS_options, IO_setup_display_brief)

changed_filename()
inputFilename.trace('w', changed_filename)

GUI_util.window.mainloop()

