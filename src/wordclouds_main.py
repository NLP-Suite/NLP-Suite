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

import GUI_IO_util
import IO_csv_util
import IO_internet_util
import wordclouds_util


os.environ['KMP_DUPLICATE_LIB_OK']='True'#for mac users to solve one error: https://stackoverflow.com/questions/53014306/error-15-initializing-libiomp5-dylib-but-found-libiomp5-dylib-already-initial
# RUN section ______________________________________________________________________________________________________________________________________________________

def transform_format(val):
    if val == 0:
        return 255
    else:
        return val

def run(inputFilename, inputDir, outputDir, visualization_tools,differentPOS_differentColors_checkbox,selectedImage,
        differentWords_differentColors_var, csvField_color_list, openOutputFiles, doNotCreateIntermediateFiles):
    if len(visualization_tools)==0:
        mb.showerror(title='Word cloud service', message='No word cloud service has been entered.\n\nPlease, select a word cloud service and try again.')
        mb.showerror(title='Word cloud service', message='No word cloud service has been entered.\n\nPlease, select a word cloud service and try again.')
        return

    if visualization_tools!='Python WordCloud' and differentWords_differentColors_var==True:
        mb.showerror(title='Word cloud service', message='The option of using different colors for different words is only available for the Python WordCloud package.\n\nPlease, select the Python WordCloud service (or diselect the different colors option) and try again.')
        return

    if differentWords_differentColors_var==True and len(csvField_color_list)==0:
        mb.showerror(title='Warning', message='You have selected the option of using different colors for different words. But...you have not selected the combination of fields and colors.\n\nPlease, complete your selections and try again.')
        return
  
    if visualization_tools=="TagCrowd" or visualization_tools=="Tagul" or visualization_tools=="Tagxedo" or visualization_tools=="Wordclouds" or visualization_tools=="Wordle":
        #check internet connection
        if not IO_internet_util.check_internet_availability_warning(visualization_tools):
            return

        if visualization_tools=="TagCrowd":
            webPage="https://tagcrowd.com/"
        if visualization_tools=="Tagul":
            webPage="https://wordart.com/"
        if visualization_tools=="Tagxedo":
            webPage="http://www.tagxedo.com/"
        if visualization_tools=="Wordclouds":
            webPage="https://www.wordclouds.com/"
        if visualization_tools=="Wordle":
            webPage="http://www.wordle.net/"
        webbrowser.open_new(webPage)
    elif visualization_tools=="Python WordCloud":
             wordclouds_util.python_wordCloud(inputFilename, inputDir, outputDir, selectedImage, differentPOS_differentColors_checkbox, csvField_color_list,doNotCreateIntermediateFiles,openOutputFiles)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            wordclouds_var.get(),
                            differentPOS_differentColors_var.get(),
                            selectedImage_var.get(),
                            differentWords_differentColors_var.get(),
                            csvField_color_list,
                            GUI_util.open_csv_output_checkbox.get(),
                            doNotCreateIntermediateFiles_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUUI section ______________________________________________________________________________________________________________________________________________________

GUI_size='1100x520'
GUI_label='Graphical User Interface (GUI) for Word Clouds'
config_filename='wordclouds-config.txt'
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
config_option=[0,4,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)
# GUI CHANGES add following lines to every special GUI
# +2 is the number of lines starting at 1 of IO widgets
y_multiplier_integer=GUI_util.y_multiplier_integer+2
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_options,config_filename)

differentPOS_differentColors_var=tk.IntVar()
csv_field_var=tk.StringVar()
differentWords_differentColors_var = tk.IntVar()
doNotCreateIntermediateFiles_var = tk.IntVar() #when an entire directory is processed; could lead to an enourmus number of output files
wordclouds_var=tk.StringVar()
selectedImage_var=tk.StringVar()
color_var = tk.IntVar()
color_style_var=tk.StringVar()

csvField_color_list=[]


def clear(e):
    wordclouds_var.set('')
    selectedImage_var.set('')
    color_style_var.set('')
    csvField_color_list.clear()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

def clear_field_color_list():
    csv_field_var.set('')
    color_var.set(0)
    color_style_var.set('')
    csvField_color_list.clear()

# def run_clouds(window,y_multiplier_integer, wordclouds_var,selectedImage_var,
# 	doNotCreateIntermediateFiles_var,input_main_dir_path):

wordclouds_var.set('')
selectedImage_var.set('')
wordclouds = tk.OptionMenu(window,wordclouds_var,'Python WordCloud','TagCrowd','Tagul','Tagxedo','Wordclouds','Wordle')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,wordclouds,True)
wordclouds_lb = tk.Label(window, text='Select the word cloud service you wish to use')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,wordclouds_lb)

y_multiplier_integer_SV=y_multiplier_integer

differentPOS_differentColors_var.set(0)
differentPOS_differentColors_checkbox = tk.Checkbutton(window, variable=differentPOS_differentColors_var,
                                                       onvalue=1, offvalue=0)

# for Python Wordcloud use different colors for different POSTAGs (red for noun, blue for verb, green for adjectives, black fro edverbs"
def activate_POSTAG_option(*args):
    if 'Python' in wordclouds_var.get():
        y_multiplier_integer = y_multiplier_integer_SV - 1
        differentPOS_differentColors_checkbox.config(text="Use different colors for different POS tag values (nouns, verbs, adjectives)")
        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 520,
                                                       y_multiplier_integer, differentPOS_differentColors_checkbox)
    else:
        differentPOS_differentColors_checkbox.place_forget()  # invisibleGoogle_API_geocode_lb.place_forget() #invisibleGoogle_API_geocode_lb.place_forget() #invisible
wordclouds_var.trace('w',activate_POSTAG_option)

menu_values=IO_csv_util.get_csvfile_headers(inputFilename.get())

select_image_file_button=tk.Button(window, width=20, text='Select png image file',command=lambda: get_image(window,'Select INPUT png file', [("png files", "*.png")]))
select_image_file_button.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,select_image_file_button,True)

selectedImage=tk.Entry(window, width=80,textvariable=selectedImage_var)
selectedImage.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+200, y_multiplier_integer,selectedImage)

def get_image(window,title,fileType):
    selectedImage_var.set('')
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)
    if len(filePath)>0:
        selectedImage.config(state='normal')
        selectedImage_var.set(filePath)

def imageSelection(*args):
    if wordclouds_var.get()=='Python WordCloud':
        select_image_file_button.config(state='normal')
    else:
        selectedImage_var.set('')
        select_image_file_button.config(state='disabled')
        selectedImage.config(state='disabled')
wordclouds_var.trace('w',imageSelection)

# labeling each group of words with separate colors"
differentWords_differentColors_var.set(0)
differentWords_differentColors_checkbox = tk.Checkbutton(window, variable=differentWords_differentColors_var, onvalue=1, offvalue=0)
differentWords_differentColors_checkbox.config(text="Use different colors for different words (csv file)")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,differentWords_differentColors_checkbox)

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
    if differentWords_differentColors_var.get()==True:
        if inputFilename.get()[-4:]!='.csv':
            mb.showwarning(title='Input file error', message='The Python 3 wordclouds algorithm expects in input a csv type file.\n\nPlease, select a csv input file and try again.')
            return
        csv_field_menu.configure(state='normal')
    else:
        csv_field_menu.configure(state='disabled')
differentWords_differentColors_var.trace('w',activateCsvOptions)

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

add_button = tk.Button(window, text='+', width=2,height=1,state='disabled',command=lambda: csv_field_menu.configure(state="normal"))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+650,y_multiplier_integer,add_button, True)

reset_button = tk.Button(window, text='Reset', width=5,height=1,state='disabled',command=lambda: clear_field_color_list())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+680,y_multiplier_integer,reset_button,True)

def showList():
    if len(csvField_color_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected combinations of csv fields and colors.')
    else:
        mb.showwarning(title='Warning', message='The currently selected combination of csv fields and colors are:\n\n' + ','.join(csvField_color_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

show_columns_button = tk.Button(window, text='Show', width=5,height=1,state='disabled',command=lambda: showList())
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+730,y_multiplier_integer,show_columns_button)

def activateCsvField(*args):
    if csv_field_var.get()!='':
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
    color_checkbox.configure(state='normal')
csv_field_var.trace('w',activateCsvField)

def changed_filename(*args):
    clear_field_color_list()
    # menu_values is the number of headers in the csv dictionary file
    menu_values=IO_csv_util.get_csvfile_headers(inputFilename.get())
    m = csv_field_menu["menu"]
    m.delete(0,"end")
    for s in menu_values:
        m.add_command(label=s,command=lambda value=s:csv_field_var.set(value))
inputFilename.trace('w',changed_filename)

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

TIPS_lookup = {"Word clouds":"TIPS_NLP_Wordclouds Visualizing word clouds.pdf","Wordle":"TIPS_NLP_Wordclouds Wordle.pdf","Tagxedo":"TIPS_NLP_Wordclouds Tagxedo.pdf","Tagcrowd":"TIPS_NLP_Wordclouds Tagcrowd.pdf"}
TIPS_options='Word clouds', 'Tagcrowd', 'Tagxedo', 'Wordle',

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",GUI_IO_util.msg_CoNLL)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_corpusData)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help",GUI_IO_util.msg_outputDirectory)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*3,"Help","Please, using the dropdown menu, select the word cloud service you want to use to generate a worldcloud. For 'TagCrowd', 'Tagul', 'Tagxedo', 'Wordclouds', and 'Wordle' you must be connected to the internet.\n\nAndreas Mueller's Python package WordCloud (https://amueller.github.io/word_cloud/) can be run without internet connection.\n\nThe Python option allows users to display different POSTAG values (namely, nouns, verbs, and adjectives) in different colors (RED for NOUNS, BLUE for VERBS, GREEN for and ADJECTIVES).\n\nPOS tags are computed via Stanford CoreNLP and may be time consuming. For greater control over the use of different colors for different items, you can use the csv file option below with a CoNLL table as input. You will then be able to use NER or DEPREL and not just POSTAG (or more POSTAG values).\n\nIn INPUT the algorithm expects a txt file (single file or entire directory).\n\nIn OUTPUT the algorithm creates a word cloud image file.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*4,"Help","Please, select a png image file to be used to dislay the word cloud in the image.\n\nThe image must be a completely black image set in a white background.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*5,"Help","Please, tick the checkbox if you wish to run the Python 3 Andreas Mueller's package WordCloud (https://amueller.github.io/word_cloud/) and assign different colors to the values of different columns of a csv file.\n\nThus, if, from a file, you have extracted SVOs (Subjects, Verbs, Objects) or POSTAG values (nouns, verbs, and adjectives), saving these values in in different columns, this function will allow you to display the values in the different columns in different, user-selected colors (e.g., RED for NOUNS, BLUE for VERBS, GREEN for and ADJECTIVES).\n\nIn INPUT the algorithm expects a single csv file (e.g., a CoNLL table) rather than a text file.\n\nIn OUTPUT the algorithm creates a word cloud image file.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*6,"Help","Please, select the sets of csv file fields and colors.\n\nPress the + button to add more csv file fields.\n\nPress the RESET button (or simply ESCape) to delete all values entered and start fresh.\n\nPress SHOW to display all selected values.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*7,"Help","Please, untick the checkbox if you want to create intermediate image files for every txt file in a directory when processing all the txt files in a directory. These image files will be in addition to the final file which will include the words from all files in the directory (so, if there is 1 file in the directory, this will lead to 2 files, although in this case, the image utput will be exactly the same for each of he 2 files).\n\nWARNING! Unticking the checkbox may result in a very large number of intermediate files (1 word cloud image file for every txt file in the directory).")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*8,"Help",GUI_IO_util.msg_openOutputFiles)

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The Python 3 script and online services display the content of text files as word cloud.\n\nA word cloud, also known as text cloud or tag cloud, is a collection of words depicted visually in different sizes (and colors). The bigger and bolder the word appears, the more often it’s mentioned within a given text and the more important it is.\n\nDifferent, freeware, word cloud applications are available: 'TagCrowd', 'Tagul', 'Tagxedo', 'Wordclouds', and 'Wordle'. These applications require internet connection.\n\nThe script also provides Python word clouds (via Andreas Mueller's Python package WordCloud https://amueller.github.io/word_cloud/) for which no internet connection is required."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options)

GUI_util.window.mainloop()
