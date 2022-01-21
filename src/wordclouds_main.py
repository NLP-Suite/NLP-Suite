#written by Roberto Franzosi November 2019

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Wordclouds",['os','tkinter','webbrowser'])==False:
    sys.exit(0)

import os
import webbrowser
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import requests

import IO_internet_util
import IO_files_util
import GUI_IO_util
import IO_csv_util
import reminders_util

os.environ['KMP_DUPLICATE_LIB_OK']='True'#for mac users to solve one error: https://stackoverflow.com/questions/53014306/error-15-initializing-libiomp5-dylib-but-found-libiomp5-dylib-already-initial
# RUN section ______________________________________________________________________________________________________________________________________________________

def transform_format(val):
    if val == 0:
        return 255
    else:
        return val

def run(inputFilename, inputDir, outputDir, visualization_tools, prefer_horizontal, lemmatize, stopwords, punctuation, lowercase, collocation, differentPOS_differentColors,prepare_image_var,selectedImage,
        differentColumns_differentColors, csvField_color_list, openOutputFiles, doNotCreateIntermediateFiles):
    if len(visualization_tools)==0 and differentColumns_differentColors==False:
        mb.showwarning("Warning",
                       "No options have been selected.\n\nPlease, select an option to run and try again.")
        return

    if (differentColumns_differentColors==True) and ((len(inputFilename)==0) or (inputFilename[-3:]!='csv')):
        mb.showerror(title='Warning', message='You have selected the option of using different colors for different columns of a single csv file. But...you have not selected in input a csv file.\n\nPlease, select an appropriate csv file in input and try again.')
        return

    if differentColumns_differentColors==True and len(csvField_color_list)==0:
        mb.showerror(title='Warning', message='You have selected the option of using different colors for different columns of a csv file. But...you have not selected the combination of fields and colors.\n\nPlease, complete your selections and try again.')
        return

    if differentColumns_differentColors == True:
        visualization_tools = 'Python WordCloud'

    if 'Python' in visualization_tools:
        if prepare_image_var:
            #check internet connection
            if not IO_internet_util.check_internet_availability_warning(visualization_tools):
                return
            webbrowser.open_new('https://www.remove.bg/')
            return

    if visualization_tools=="TagCrowd" or visualization_tools=="Tagul" or visualization_tools=="Tagxedo" or visualization_tools=="Wordclouds" or visualization_tools=="Wordle":
        #check internet connection
        if not IO_internet_util.check_internet_availability_warning(visualization_tools):
            return
        if visualization_tools=="TagCrowd":
            url="https://tagcrowd.com/"
        if visualization_tools=="Tagul":
            url="https://wordart.com/"
        if visualization_tools=="Tagxedo":
            url="http://www.tagxedo.com/"
        if visualization_tools=="Wordclouds":
            url="https://www.wordclouds.com/"
        if visualization_tools=="Wordle":
            url="http://www.wordle.net/"
        status_code = requests.get(url).status_code
        if status_code != 200:
            mb.showwarning(title='Warning',
                           message='Oops! It appears that the website www.wordle.net that traditionally hosted Wordle is no longer available.\n\nWordle was the fiirst wordclouds algorithm developed by Jonathan Feinberg at IBM Research in 2005, 2008 and subsequently followed by several other applications.\n\nPlease, use one of these freeware applications hosted by the NLP Suite, including the Python package WordCloud.')
        else:
            reminders_util.checkReminder(config_filename, reminders_util.title_options_wordclouds,
                                         reminders_util.message_wordclouds, True)
            webbrowser.open_new(url)
    elif visualization_tools=="Python WordCloud":
        import wordclouds_util
        if not IO_internet_util.check_internet_availability_warning("wordclouds_main.py"):
            return
        wordclouds_util.python_wordCloud(inputFilename, inputDir, outputDir, selectedImage, prefer_horizontal, lemmatize, stopwords, punctuation, lowercase, differentPOS_differentColors,differentColumns_differentColors, csvField_color_list,doNotCreateIntermediateFiles,openOutputFiles, collocation)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            wordclouds_var.get(),
                            prefer_horizontal_var.get(),
                            lemmatize_var.get(),
                            stopwords_var.get(),
                            punctuation_var.get(),
                            lowercase_var.get(),
                            collocation_var.get(),
                            differentPOS_differentColors_var.get(),
                            prepare_image_var.get(),
                            selectedImage_var.get(),
                            differentColumns_differentColors_var.get(),
                            csvField_color_list,
                            GUI_util.open_csv_output_checkbox.get(),
                            doNotCreateIntermediateFiles_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=520, # height at brief display
                             GUI_height_full=600, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Word Clouds'
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
config_input_output_numeric_options=[6,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)
window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)

prefer_horizontal_var=tk.IntVar()
lemmatize_var=tk.IntVar()
punctuation_var=tk.IntVar()
stopwords_var=tk.IntVar()
lowercase_var=tk.IntVar()
collocation_var=tk.IntVar()

differentPOS_differentColors_var=tk.IntVar()
csv_field_var=tk.StringVar()
differentColumns_differentColors_var = tk.IntVar()
doNotCreateIntermediateFiles_var = tk.IntVar() #when an entire directory is processed; could lead to an enourmus number of output files
wordclouds_var=tk.StringVar()
prepare_image_var = tk.IntVar()
selectedImage_var=tk.StringVar()
color_var = tk.IntVar()
color_style_var=tk.StringVar()

csvField_color_list=[]

def clear(e):
    wordclouds_var.set('')
    differentColumns_differentColors_var.set(0)
    differentColumns_differentColors_checkbox.config(state='normal')
    selectedImage_var.set('')
    prefer_horizontal_var.set(0)
    lemmatize_var.set(0)
    stopwords_var.set(0)
    punctuation_var.set(0)
    lowercase_var.set(0)
    collocation_var.set(0)
    differentPOS_differentColors_var.set(0)
    color_var.set(0)
    color_style_var.set('')
    csvField_color_list.clear()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

def clear_field_color_list():
    csv_field_var.set('')
    csv_field_menu.configure(state='normal')
    color_var.set(0)
    color_style_var.set('')
    csvField_color_list.clear()

# def run_clouds(window,y_multiplier_integer, wordclouds_var,selectedImage_var,
# 	doNotCreateIntermediateFiles_var,input_main_dir_path):

wordclouds_var.set('')
selectedImage_var.set('')
wordclouds = tk.OptionMenu(window,wordclouds_var,'Python WordCloud','TagCrowd','Tagul','Tagxedo','Wordclouds','Wordle')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+120, y_multiplier_integer,wordclouds,True)
wordclouds_lb = tk.Label(window, text='Select the word cloud service you wish to use (txt file(s)/CoNLL table)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,wordclouds_lb)

y_multiplier_integer_SV=y_multiplier_integer

differentPOS_differentColors_var.set(0)
differentPOS_differentColors_checkbox = tk.Checkbutton(window, variable=differentPOS_differentColors_var,
                                                       onvalue=1, offvalue=0)

prefer_horizontal_checkbox = tk.Checkbutton(window, variable=prefer_horizontal_var,
                                                       onvalue=1, offvalue=0)

prefer_horizontal_checkbox.config(text="Horizontal")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,
                                               y_multiplier_integer, prefer_horizontal_checkbox, True)
def warnUser(*args):
    if prefer_horizontal_var.get()==True:
        mb.showwarning(title='Warning',
                       message='You have selected to visualize words only horizontally in the wordcloud image. Some of the lower-frequency words may need to be dropped from the wordclouds image since there may not be enough room for their display.\n\nCombining horizontal and vertical displays maximizes the number of words visualized in the wordcloud image.')
prefer_horizontal_var.trace('w',warnUser)

lemmatize_checkbox = tk.Checkbutton(window, variable=lemmatize_var,
                                                       onvalue=1, offvalue=0)

lemmatize_checkbox.config(text="Lemmas")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+140,
                                               y_multiplier_integer, lemmatize_checkbox, True)

stopwords_checkbox = tk.Checkbutton(window, variable=stopwords_var,
                                                       onvalue=1, offvalue=0)

stopwords_checkbox.config(text="Stopwords")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+230,
                                               y_multiplier_integer, stopwords_checkbox, True)

punctuation_checkbox = tk.Checkbutton(window, variable=punctuation_var,
                                                       onvalue=1, offvalue=0)

punctuation_checkbox.config(text="Punctuation")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+340,
                                               y_multiplier_integer, punctuation_checkbox, True)

lowercase_checkbox = tk.Checkbutton(window, variable=lowercase_var,
                                                       onvalue=1, offvalue=0)

lowercase_checkbox.config(text="Lowercase")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+460,
                                               y_multiplier_integer, lowercase_checkbox, True)

collocation_checkbox = tk.Checkbutton(window, variable=collocation_var,
                                                       onvalue=1, offvalue=0)

collocation_checkbox.config(text="Collocation")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+580,
                                               y_multiplier_integer, collocation_checkbox, True)

differentPOS_differentColors_checkbox.config(text="Different colors by POS tags (nouns, verbs, adverbs, adjectives)")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+680,
                                               y_multiplier_integer, differentPOS_differentColors_checkbox)

menu_values=IO_csv_util.get_csvfile_headers(inputFilename.get())

prepare_image_checkbox = tk.Checkbutton(window, variable=prepare_image_var,
                                                       onvalue=1, offvalue=0)

prepare_image_checkbox.config(text="Prepare image")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate(),
                                               y_multiplier_integer, prepare_image_checkbox)

# width=20,
select_image_file_button=tk.Button(window, text='Select png image file',command=lambda: get_image(window,'Select INPUT png file', [("png files", "*.png")]))
#select_image_file_button.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate(), y_multiplier_integer,select_image_file_button,True)

# setup a button to open Windows Explorer on open the png image file
openImage_button = tk.Button(window, width=3, text='', state='disabled',
                                 command=lambda: IO_files_util.openFile(window,
                                                                        selectedImage_var.get()))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate()+150, y_multiplier_integer,
                                               openImage_button, True)

selectedImage=tk.Entry(window, width=100,textvariable=selectedImage_var)
selectedImage.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate()+220, y_multiplier_integer,selectedImage)

def get_image(window,title,fileType):
    selectedImage_var.set('')
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)
    if len(filePath)>0:
        selectedImage_var.set(filePath)
        prepare_image_var.set(0)

# labeling each group of words with separate colors"
differentColumns_differentColors_var.set(0)
differentColumns_differentColors_checkbox = tk.Checkbutton(window, variable=differentColumns_differentColors_var, onvalue=1, offvalue=0)
differentColumns_differentColors_checkbox.config(text="Use different colors for different columns (csv file)")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,differentColumns_differentColors_checkbox)

def displayWarning(*args):
    if collocation_var.get()==True and differentPOS_differentColors_var.get()==True:
        mb.showwarning(title='Warning',
                       message='The joint use of the flter options "Collocation" and "Different colors by POS tags" is likely to distort the default color scheme of POS tags, since the individual words in the collocations would not be recognized by the color scheme function.\n\nThus, for the collocation "huff puff," the individual verbs - huff, puff - would not be displayed in the expected color blue.')

collocation_var.trace('w', displayWarning)
differentPOS_differentColors_var.trace('w',displayWarning)

menu_values=IO_csv_util.get_csvfile_headers(inputFilename.get())

field_lb = tk.Label(window, text='Select csv field')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,field_lb,True)
if menu_values!='':
    csv_field_menu = tk.OptionMenu(window, csv_field_var, *menu_values)
else:
    csv_field_menu = tk.OptionMenu(window, csv_field_var, menu_values)
csv_field_menu.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+120,y_multiplier_integer,csv_field_menu,True)

def activateCsvOptions(*args):
    csv_field_var.set('')
    if differentColumns_differentColors_var.get()==True:
        if inputFilename.get()[-4:]!='.csv':
            mb.showwarning(title='Input file error', message='The Python 3 wordclouds algorithm expects in input a csv type file.\n\nPlease, select a csv input file and try again.')
            # differentColumns_differentColors_var.set(0)
            return
        csv_field_menu.configure(state='normal')

    else:
        csv_field_menu.configure(state='disabled')
differentColumns_differentColors_var.trace('w',activateCsvOptions)

activateCsvOptions()

color_var.set(0)
color_checkbox = tk.Checkbutton(window, text='Color ', state='disabled',variable=color_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+300,y_multiplier_integer,color_checkbox,True)

color_lb = tk.Label(window, text='RGB color code ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+400,y_multiplier_integer,color_lb,True)
color_entry = tk.Entry(window, width=10, textvariable=color_style_var)
color_entry.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+520,y_multiplier_integer,color_entry,True)

def activate_color_palette(*args):
    # tkcolorpicker requires tkinter and pillow to be installed (https://libraries.io/pypi/tkcolorpicker)
    # tkcolorpicker is both the package and module name
    # pillow is the Python 3 version of PIL which was an older Python 2 version
    # PIL being the commmon module for both packages, you need to check for PIL and trap PIL to tell the user to install pillow
    from tkcolorpicker import askcolor
    if color_var.get()==1:
        style = ttk.Style(window)
        style.theme_use('clam')
        color_list = askcolor((255, 255, 0), window)
        color_style = color_list[0]
        color_style_var.set(color_style)
        csvField_color_list.append(str(color_style))
        csvField_color_list.append("|")
color_var.trace('w',activate_color_palette)

def update_csvFields():
    csv_field_menu.configure(state="normal")
    color_var.set(0)

add_button = tk.Button(window, text='+', width=2,height=1,state='disabled',command=lambda: update_csvFields())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+650,y_multiplier_integer,add_button, True)

reset_button = tk.Button(window, text='Reset', height=1,state='disabled',command=lambda: clear_field_color_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+700,y_multiplier_integer,reset_button,True)

def showList():
    if len(csvField_color_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected combinations of csv fields and colors.')
    else:
        mb.showwarning(title='Warning', message='The currently selected combination of csv fields and colors is:\n\n' + ','.join(csvField_color_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

show_columns_button = tk.Button(window, text='Show',height=1,state='disabled',command=lambda: showList())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+760,y_multiplier_integer,show_columns_button)

def activateCsvField(*args):
    if csv_field_var.get()!='':
        color_checkbox.configure(state='normal')
        state = str(csv_field_menu['state'])
        if state != 'disabled':
            if csv_field_var.get() in csvField_color_list:
                mb.showwarning(title='Warning', message='The selected csv field value, ' + csv_field_var.get() + ', has already been selected.\n\nPlease, select a different value. You can display all selected values by clicking on SHOW.')
                return
            add_button.configure(state="normal")
            reset_button.configure(state="normal")
            show_columns_button.configure(state='normal')
            csvField_color_list.append(csv_field_var.get())
            csv_field_menu.configure(state='disabled')
        else:
            add_button.configure(state="normal")
            reset_button.configure(state="normal")
            show_columns_button.configure(state='normal')
            csv_field_menu.configure(state='normal')
    else:
        add_button.configure(state="disabled")
        reset_button.configure(state="disabled")
        show_columns_button.configure(state='disabled')
        color_checkbox.configure(state='disabled')
csv_field_var.trace('w',activateCsvField)

def activate_Python_options(*args):

    if not 'Python' in wordclouds_var.get():
        selectedImage_var.set('')
        prepare_image_checkbox.config(state='disabled')
        select_image_file_button.config(state='disabled')
        openImage_button.config(state='disabled')
        differentColumns_differentColors_checkbox.config(state='disabled')
        prefer_horizontal_checkbox.config(state='disabled')
        lemmatize_checkbox.config(state='disabled')
        stopwords_checkbox.config(state='disabled')
        punctuation_checkbox.config(state='disabled')
        lowercase_checkbox.config(state='disabled')
        collocation_checkbox.config(state='disabled')
        differentPOS_differentColors_checkbox.config(state='disabled')
    else:
        differentColumns_differentColors_checkbox.config(state='normal')

        prefer_horizontal_checkbox.config(state='normal')
        lemmatize_checkbox.config(state='normal')
        stopwords_checkbox.config(state='normal')
        punctuation_checkbox.config(state='normal')
        lowercase_checkbox.config(state='normal')
        collocation_checkbox.config(state='normal')
        differentPOS_differentColors_checkbox.config(state='normal')
        stopwords_var.set(1)
        punctuation_var.set(1)
        lowercase_var.set(1)
        collocation_var.set(1)

        prepare_image_checkbox.config(state='normal')
        select_image_file_button.config(state='normal')
        openImage_button.config(state='normal')

wordclouds_var.trace('w',activate_Python_options)
activate_Python_options()

def changed_filename(*args):
    # if differentColumns_differentColors_var.get()==True:

    clear_field_color_list()
    # menu_values is the number of headers in the csv dictionary file
    menu_values=IO_csv_util.get_csvfile_headers(inputFilename.get())
    m = csv_field_menu["menu"]
    m.delete(0,"end")
    for s in menu_values:
        m.add_command(label=s,command=lambda value=s:csv_field_var.set(value))
inputFilename.trace('w',changed_filename)
input_main_dir_path.trace('w',changed_filename)

changed_filename()

doNotCreateIntermediateFiles_var.set(1)
doNotCreateIntermediateFiles_checkbox = tk.Checkbutton(window, variable=doNotCreateIntermediateFiles_var, onvalue=1, offvalue=0)
doNotCreateIntermediateFiles_checkbox.config(text="Do NOT produce intermediate word cloud files when processing all txt files in a directory")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,doNotCreateIntermediateFiles_checkbox)

def changeLabel_nomin(*args):
    if doNotCreateIntermediateFiles_var.get()==1:
        doNotCreateIntermediateFiles_checkbox.config(text="Do NOT produce intermediate word cloud files when processing all txt files in a directory")
    else:
        doNotCreateIntermediateFiles_checkbox.config(text="Produce intermediate word cloud files when processing all txt files in a directory")
doNotCreateIntermediateFiles_var.trace('w',changeLabel_nomin)

def turnOff_doNotCreateIntermediateFiles_checkbox(*args):
    if len(input_main_dir_path.get())>0:
        doNotCreateIntermediateFiles_checkbox.config(state='normal')
    else:
        doNotCreateIntermediateFiles_checkbox.config(state='disabled')
input_main_dir_path.trace('w',turnOff_doNotCreateIntermediateFiles_checkbox)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {"Lemmas & stopwords":"TIPS_NLP_NLP Basic Language.pdf", "Word clouds":"TIPS_NLP_Wordclouds Visualizing word clouds.pdf","Wordle":"TIPS_NLP_Wordclouds Wordle.pdf","Tagxedo":"TIPS_NLP_Wordclouds Tagxedo.pdf","Tagcrowd":"TIPS_NLP_Wordclouds Tagcrowd.pdf"}
TIPS_options='Lemmas & stopwords', 'Word clouds', 'Tagcrowd', 'Tagxedo', 'Wordle'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    if not IO_setup_display_brief:
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",GUI_IO_util.msg_CoNLL)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_corpusData)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help",GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+1),"Help","Please, using the dropdown menu, select the word cloud service you want to use to generate a worldcloud.\n\nFor 'TagCrowd', 'Tagul', 'Tagxedo', 'Wordclouds', and 'Wordle' you must be connected to the internet. You will also need to copy/paste text or upload a text file, depending upon the word clouds service. If you wish to visualize the words in all the files in a directory, you would need to merge the files first via the file_merger_main, then use your merged file.\n\nThe Python algorithm uses Andreas Mueller's Python package WordCloud (https://amueller.github.io/word_cloud/) can be run without internet connection.\n\nIn INPUT the algorithm expects a single txt file or a directory of txt files or a csv CoNLL table file.\n\nIn OUTPUT the algorithm creates word cloud image file(s).")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+2),"Help","\n\nThe filter options are only available when selecting Python as the wordcloud service to use. When available,\n\n   1. tick the 'Horizonal' checkbox if you wish to display words in the wordcloud horizonally only;\n   2. tick the 'Lemmas' checkbox if you wish to lemmatize the words in the input file(s);\n   3. tick the 'Stopwords' checkbox if you wish to exclude from processing stopwords present in the input file(s);\n   4. tick the 'Punctuation' checkbox if you wish to exclude from processing punctuation symbols present in the input file(s);\n   5. tick the 'Lowercase' checkbox if you wish to convert all words to lowercase to avoid having some words capitalized simly because they are the first words in a sentence;\n   6. tick the 'Collocation' checkbox if you wish to keep together common combinations of words (South Carolina; White House);\n   7. tick the 'Different colors for different POS tags' checkbox if you wish to display different POSTAG values (namely, nouns, verbs, adjectives, and adverbs) in different colors (RED for NOUNS, BLUE for VERBS, GREEN for ADJECTIVES, and GREY for ADVERBS; YELLOW for any other POS tags). For greater control over the use of different colors for different items, you can use the csv file option below with a CoNLL table as input. You will then be able to use NER or DEPREL and not just POSTAG (or more POSTAG values).\n\nStanford CoreNLP STANZA will be used to tokenize sentences, lemmatize words, and compute POS tags. Depending upon the number of files processed and length of files, the process can be time consuming. Please, be patient.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+3),"Help","Please, tick the checkbox to open the web service Removebg (https://www.remove.bg/) that will prepare an image for use in the Python wordcloud algorithm, removing all image background and turning it into white.\n\nYou can then use the output png image file to create the wordcloud (see the widget 'Select png image' file).\n\nYOU MUST BE CONNECTED TO THE INTERNET.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+4),"Help","Please, select a png image file to be used to dislay the word cloud in the image.\n\nThe image must have a white background.\n\nYou can use the image file created via removebg (see the widget 'Prepare image').\n\nClick on the button to the right of the widget 'Select png image file' to open the file.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+5),"Help","Please, tick the checkbox if you wish to run the Python 3 Andreas Mueller's package WordCloud (https://amueller.github.io/word_cloud/) and assign different colors to the values of different columns of a csv file.\n\nThus, if, from a file, you have extracted SVOs (Subjects, Verbs, Objects) or POSTAG values (nouns, verbs, and adjectives), saving these values in in different columns, this function will allow you to display the values in the different columns in different, user-selected colors (e.g., RED for the column of NOUNS, BLUE for the column of VERBS).\n\nThe wordcloud algorithm can color all the values of a column differently from all the values of another column. The algorithm is NOT setup to color differently the different values within a column (to accomplish this goal, you would need to manipulate first the csv file; for instance, if the input file is a CoNLL table, you could extract all the NER values COUNTRY, CITY, and STATE_OR_PROVINCE and the NER value PERSON and ORGANIZATION, save them as two separate columns, and then use this new csv file in the current wordcloud algorithm).\n\nIn INPUT the algorithm expects a single csv file (e.g., a CoNLL table) rather than a text file or a directory.\n\nIn OUTPUT the algorithm creates a word cloud image file.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+6),"Help","Pease, select the sets of csv file fields and colors.\n\nPress the + button to add more csv file fields.\n\nPress the RESET button (or simply ESCape) to delete all values entered and start fresh.\n\nPress SHOW to display all selected values.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+7),"Help","Please, untick the checkbox if you want to create intermediate image files for every txt file in a directory when processing all the txt files in a directory. These image files will be in addition to the final file which will include the words from all files in the directory (so, if there is 1 file in the directory, this will lead to 2 files, although in this case, the image utput will be exactly the same for each of he 2 files).\n\nWARNING! Unticking the checkbox may result in a very large number of intermediate files (1 word cloud image file for every txt file in the directory).")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+8),"Help",GUI_IO_util.msg_openOutputFiles)

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The Python 3 script and online services display the content of text files as word cloud.\n\nA word cloud, also known as text cloud or tag cloud, is a collection of words depicted visually in different sizes (and colors). The bigger and bolder the word appears, the more often it’s mentioned within a given text and the more important it is.\n\nDifferent, freeware, word cloud applications are available: 'TagCrowd', 'Tagul', 'Tagxedo', 'Wordclouds', and 'Wordle'. These applications require internet connection.\n\nThe script also provides Python word clouds (via Andreas Mueller's Python package WordCloud https://amueller.github.io/word_cloud/) for which no internet connection is required.\n\nIn INPUT the algorithm expects a single txt file or a directory of txt files or a csv file (e.g., a CoNLL table).\n\nIn OUTPUT the algorithms create word cloud image file(s)."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
