#written by Roberto Franzosi November 2019

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"Wordclouds",['os','tkinter','webbrowser'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mb
from subprocess import call


import IO_internet_util
import IO_files_util
import GUI_IO_util
import IO_csv_util
import reminders_util
import config_util

os.environ['KMP_DUPLICATE_LIB_OK']='True'#for mac users to solve one error: https://stackoverflow.com/questions/53014306/error-15-initializing-libiomp5-dylib-but-found-libiomp5-dylib-already-initial
# RUN section ______________________________________________________________________________________________________________________________________________________

def transform_format(val):
    if val == 0:
        return 255
    else:
        return val

def run(inputFilename, inputDir, outputDir, visualization_tools, prefer_horizontal, font,
        max_words, lemmatize, exclude_stopwords, exclude_punctuation, lowercase, collocation, differentPOS_differentColor,
        prepare_image_var,selectedImage, use_contour_only,
        differentColumns_differentColors, csvField_color_list, openOutputFiles, doNotCreateIntermediateFiles):

    filesToOpen=[]

    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    else:
        config_filename = scriptName.replace('_main.py', '_config.csv')

    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]

    if len(visualization_tools)==0 and differentColumns_differentColors==False:
        mb.showwarning("Warning",
                       "No options have been selected.\n\nPlease, select an option to run and try again.")
        return

    if (differentColumns_differentColors==True) and ((len(inputFilename)==0) or (inputFilename[-3:]!='csv')):
        mb.showerror(title='Warning', message='You have selected the option of using different colors for different columns of a single csv file. But... you have not selected in input a csv file.\n\nPlease, select an appropriate csv file in input and try again.')
        return

    if (differentColumns_differentColors==True) and len(csvField_color_list)==0:
        mb.showerror(title='Warning', message='You have selected the option of using different colors for different columns of a single csv file. But... you have not selected in input the csv file field.\n\nPlease, select an appropriate csv file field and try again.')
        return

    if differentColumns_differentColors==True and not "|" in str(csvField_color_list):
        mb.showerror(title='Warning', message='You have selected the option of using different colors for different columns of a csv file. But... you have not selected the colors to be used.\n\nPlease, select a color by ticking the Color checkbox, select your preferred color and try again.')
        return

    if inputFilename[-4:] == '.csv':
        import CoNLL_util
        if not CoNLL_util.check_CoNLL(inputFilename,True):
            if not differentColumns_differentColors:
                mb.showwarning("Warning",
                               "You have selected to use wordclouds with a csv file that is not a CoNLL table.\n\nYou must select the fields you want to use for wordclouds visualization by ticking the checkbox 'Use different colors...' and then selecting the csv field(s).\n\nPlease, select those options and try again.")
                return

    if differentColumns_differentColors == True:
        visualization_tools = 'Python WordCloud'

    if 'Python' in visualization_tools:
        if prepare_image_var:
            #check internet connection
            # if not IO_internet_util.check_internet_availability_warning(visualization_tools):
            #     return
            # webbrowser.open_new_tab('https://www.remove.bg/')
            # https://www.adobe.com/express/feature/image/remove-background
            # https://express.adobe.com/tools/remove-background
            # https://www.slazzer.com/upload
            url = 'https://www.remove.bg/'
            if not IO_libraries_util.open_url('remove.bg', url):
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

        if not IO_libraries_util.open_url(visualization_tools, url, message_title='', message='', config_filename='',
                     reminder_title='', reminder_message='', scriptName=scriptName):
            return
    elif visualization_tools=="Python WordCloud":
        import wordclouds_util
        if not IO_internet_util.check_internet_availability_warning("wordclouds_main.py"):
            return
        if differentPOS_differentColor or differentColumns_differentColors: # should not process stopwords when useing a csv file in input or POS values
            exclude_stopwords = True
        outputFiles = wordclouds_util.python_wordCloud(inputFilename, inputDir, outputDir, config_filename,  selectedImage,
                                use_contour_only, prefer_horizontal, font,
                                int(max_words), lemmatize, exclude_stopwords, exclude_punctuation,
                                lowercase, differentPOS_differentColor, differentColumns_differentColors,
                                csvField_color_list,doNotCreateIntermediateFiles,openOutputFiles, collocation)

        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        if openOutputFiles == True:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)
        return


#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated

run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            wordclouds_var.get(),
                            prefer_horizontal_var.get(),
                            font_var.get(),
                            max_words_var.get(),
                            lemmatize_var.get(),
                            exclude_stopwords_var.get(),
                            exclude_punctuation_var.get(),
                            lowercase_var.get(),
                            collocation_var.get(),
                            differentPOS_differentColor_var.get(),
                            prepare_image_var.get(),
                            selectedImage_var.get(),
                            use_contour_only_var.get(),
                            differentColumns_differentColor_var.get(),
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
                             GUI_height_brief=560, # height at brief display
                             GUI_height_full=640, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Word Clouds'
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
config_input_output_numeric_options=[6,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)
window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

prefer_horizontal_var=tk.IntVar()
lemmatize_var=tk.IntVar()
exclude_punctuation_var=tk.IntVar()
exclude_stopwords_var=tk.IntVar()
lowercase_var=tk.IntVar()
collocation_var=tk.IntVar()

differentPOS_differentColor_var=tk.IntVar()
csv_field_var=tk.StringVar()
differentColumns_differentColor_var = tk.IntVar()
doNotCreateIntermediateFiles_var = tk.IntVar() #when an entire directory is processed; could lead to an enourmus number of output files
wordclouds_var=tk.StringVar()
font_var=tk.StringVar()
prepare_image_var = tk.IntVar()
selectedImage_var=tk.StringVar()
use_contour_only_var = tk.IntVar()
color_var = tk.IntVar()
color_style_var=tk.StringVar()

csvField_color_list=[]

def clear(e):
    wordclouds_var.set('Python WordCloud')
    font_var.set('Default')
    differentColumns_differentColor_var.set(0)
    differentColumns_differentColor_checkbox.config(state='normal')
    selectedImage_var.set('')
    use_contour_only_var.set(1)
    prefer_horizontal_var.set(0)
    lemmatize_var.set(1)
    exclude_stopwords_var.set(1)
    exclude_punctuation_var.set(1)
    lowercase_var.set(0)
    collocation_var.set(0)
    differentPOS_differentColor_var.set(0)
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

wordclouds_var.set('Python WordCloud')
selectedImage_var.set('')
use_contour_only_var.set(1)
wordclouds = tk.OptionMenu(window,wordclouds_var,'Python WordCloud','TagCrowd','Tagul','Tagxedo','Wordclouds','Wordle')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate+120, y_multiplier_integer,wordclouds,True)
wordclouds_lb = tk.Label(window, text='Select the word cloud service you wish to use (txt file(s)/CoNLL table)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,wordclouds_lb)

y_multiplier_integer_SV=y_multiplier_integer

differentPOS_differentColor_var.set(0)
differentPOS_differentColor_checkbox = tk.Checkbutton(window, variable=differentPOS_differentColor_var,
                                                       onvalue=1, offvalue=0)

prefer_horizontal_checkbox = tk.Checkbutton(window, variable=prefer_horizontal_var,
                                                       onvalue=1, offvalue=0)

prefer_horizontal_checkbox.config(text="Horizontal")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                   prefer_horizontal_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Tick the checkbox to visualize words horizontally.\nHorizontal layout may be more readable but low-frequency words may need to be dropped.\nUntick the checkbox to displays words both horizontally and vertically to maximize space and number of words displayed.")

def warnUser(*args):
    if prefer_horizontal_var.get()==True:
        reminders_util.checkReminder(scriptName, reminders_util.title_options_python_wordclouds_horizontal,
                                     reminders_util.message_python_wordclouds_horizontal, True)
prefer_horizontal_var.trace('w',warnUser)

## import wordclouds_util
# font_list = wordclouds_util.get_font_list()

font_var.set('Default')
font_lb = tk.Label(window, text='Font')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_font_lb, y_multiplier_integer,
                                   font_lb,
                                   True, False, True, False, 90, GUI_IO_util.wordclouds_font_lb,
                                   "Select the font you want to use in the wordclouds visualization; default font is the Adobe Droid Sans Mono font.")

font = ttk.Combobox(window, width = 15, textvariable = font_var)
# font['values'] = font_list
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_font_menu, y_multiplier_integer,font)
# font.config(state='disabled')

max_words_var=tk.StringVar()
max_words_var.set(100)

max_words_lb = tk.Label(window, text='Max no. of words')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,max_words_lb,True)
max_words=tk.Entry(window, width=4,textvariable=max_words_var)
max_words.config(state='normal')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_max_words_number, y_multiplier_integer,
                                   max_words,
                                   True, False, True, False, 90, GUI_IO_util.wordclouds_max_words_number,
                                   "Enter the maximum number of words to be displayed on the wordclouds image")

lemmatize_var.set(1)
lemmatize_checkbox = tk.Checkbutton(window, variable=lemmatize_var,
                                                       onvalue=1, offvalue=0)
lemmatize_checkbox.config(text="Lemmas")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_lemmas_pos, y_multiplier_integer,
                                   lemmatize_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.wordclouds_lemmas_pos,
                                   "Untick the checkbox to NOT lemmatize words; tick the checkbox to lemmatize words in the corpus."
                                   "\nLemmatization is based on Stanza.")

stopwords_checkbox = tk.Checkbutton(window, variable=exclude_stopwords_var,
                                                       onvalue=1, offvalue=0)

stopwords_checkbox.config(text="Stopwords")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_stopwords_pos, y_multiplier_integer,
                                   stopwords_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Untick the checkbox to INCLUDE stopwords; tick the checkbox to EXCLUDE stopwords."
                                   "\nStopwords are provided by the Wordclouds package and printed in command line/terminal when stopwords are included.")

punctuation_checkbox = tk.Checkbutton(window, variable=exclude_punctuation_var,
                                                       onvalue=1, offvalue=0)

punctuation_checkbox.config(text="Punctuation")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_punctuation_pos, y_multiplier_integer,
                                   punctuation_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.wordclouds_punctuation_pos,
                                   "Untick the checkbox to EXCLUDE punctuation; tick the checkbox to INCLUDE punctuation")

lowercase_checkbox = tk.Checkbutton(window, variable=lowercase_var,
                                                       onvalue=1, offvalue=0)

lowercase_checkbox.config(text="Lowercase")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_lowercase_pos, y_multiplier_integer,
                                   lowercase_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Untick the checkbox to NOT process corpus words in lowercase; tick the checkbox to process corpus words in lowercase")

collocation_checkbox = tk.Checkbutton(window, variable=collocation_var,
                                                       onvalue=1, offvalue=0)

collocation_checkbox.config(text="Collocation")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_collocation_pos, y_multiplier_integer,
                                   collocation_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.open_reminders_x_coordinate,
                                   "Untick the checkbox to NOT process multiple words together; tick the checkbox to process multiple words together (e.g., standing up)")

differentPOS_differentColor_checkbox.config(text="Different colors by POS tags")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_color_by_POS_tags, y_multiplier_integer,
                                   differentPOS_differentColor_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Untick the checkbox to NOT process words in different colors by their POS value; tick the checkbox to process in different colors words by their POS value: nouns, verbs, adjectives, and adverbs.\n"
                                   "POS values are computed by Stanza."
                                   "\nRED for NOUNS (including proper nouns), BLUE for VERBS, GREEN for ADJECTIVES, and GREY for ADVERBS.")

menu_values=''
if os.path.isfile(inputFilename.get()):
    if inputFilename.get().endswith('csv'):
        menu_values=IO_csv_util.get_csvfile_headers(inputFilename.get())

prepare_image_checkbox = tk.Checkbutton(window, variable=prepare_image_var,
                                                       onvalue=1, offvalue=0)

prepare_image_checkbox.config(text="Prepare image")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   prepare_image_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Tick/untick the checkbox to open the web service Removebg to prepare an image for use in the Python wordclouds algorithm")

# width=20,
select_image_file_button=tk.Button(window, text='Select png image file',command=lambda: get_image(window,'Select INPUT png file', [("png files", "*.png")]))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   select_image_file_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "Click on the button to select the png image file")

# setup a button to open Windows Explorer on open the png image file
openImage_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', state='disabled',
                                 command=lambda: IO_files_util.openFile(window,
                                                                        selectedImage_var.get()))
# the button widget has hover-over effects (no_hover_over_widget=False) and the info displayed is in text_info
# the two x-coordinate and x-coordinate_hover_over must have the same values
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_openImage_button, y_multiplier_integer,
                                               openImage_button, True, False, True,False, 90, GUI_IO_util.wordclouds_openImage_button, "Open png image file")

selectedImage=tk.Entry(window, width=GUI_IO_util.wordclouds_selectedImage_width,textvariable=selectedImage_var)
selectedImage.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_selectedImage_file_path, y_multiplier_integer,selectedImage, True)

use_contour_only_var.set(1)
use_contour_only_checkbox = tk.Checkbutton(window, variable=use_contour_only_var, onvalue=1, offvalue=0)
use_contour_only_checkbox.config(text="Use image contour only")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.contour_only_pos, y_multiplier_integer,
                                   use_contour_only_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.wordclouds_punctuation_pos,
                                   "Tick/untick the checkbox to use (or not use) only the image contour rather than the image itself")
def get_image(window,title,fileType):
    selectedImage_var.set('')
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)
    if len(filePath)>0:
        selectedImage_var.set(filePath)
        prepare_image_var.set(0)


# labeling each group of words with separate colors"
differentColumns_differentColor_var.set(0)
differentColumns_differentColor_checkbox = tk.Checkbutton(window, variable=differentColumns_differentColor_var, onvalue=1, offvalue=0)
differentColumns_differentColor_checkbox.config(text="Use different colors for different columns (csv file)")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                   differentColumns_differentColor_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "The option is available only when a non-CoNLL csv file is selected. CoNLL files are automatically processed for wordclouds visualization.")
def displayWarning(*args):
    if collocation_var.get()==True and differentPOS_differentColor_var.get()==True:
        mb.showwarning(title='Warning',
                       message='The joint use of the flter options "Collocation" and "Different colors by POS tags" is likely to distort the default color scheme of POS tags, since the individual words in the collocations would not be recognized by the color scheme function.\n\nThus, for the collocation "huff puff," the individual verbs - huff, puff - would not be displayed in the expected color blue.')

collocation_var.trace('w', displayWarning)
differentPOS_differentColor_var.trace('w',displayWarning)

menu_values=''

if os.path.isfile(inputFilename.get()):
    if inputFilename.get().endswith('csv'):
        menu_values=IO_csv_util.get_csvfile_headers(inputFilename.get())

field_lb = tk.Label(window, text='Select csv field')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,field_lb,True)

if menu_values!='':
    csv_field_menu = tk.OptionMenu(window, csv_field_var, *menu_values)
else:
    csv_field_menu = tk.OptionMenu(window, csv_field_var, menu_values)
csv_field_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_select_csv_field, y_multiplier_integer,
                                   csv_field_menu,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_coordinate,
                                   "The option is available only when a non-CoNLL csv file is selected. CoNLL files are automatically processed for wordclouds visualization.")
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_select_csv_field,y_multiplier_integer,csv_field_menu,True)

# def activateCsvOptions(*args):
#     csv_field_var.set('')
#     if differentColumns_differentColor_var.get()==True:
#         if os.path.isfile(inputFilename.get()):
#             if inputFilename.get()[-4:]!='.csv':
#                 mb.showwarning(title='Input file error', message='The Python 3 wordclouds algorithm expects in input a csv type file.\n\nPlease, select a csv input file and try again.')
#                 # differentColumns_differentColors_var.set(0)
#                 return
#             differentColumns_differentColor_checkbox.config(state='normal')
#             csv_field_menu.configure(state='normal')
#
#     else:
#         differentColumns_differentColor_checkbox.config(state='disabled')
#         csv_field_menu.configure(state='disabled')
# differentColumns_differentColor_var.trace('w',activateCsvOptions)
#
# activateCsvOptions()

color_var.set(0)
color_checkbox = tk.Checkbutton(window, text='Color ', state='disabled',variable=color_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_color_checkbox_pos, y_multiplier_integer,
                                   color_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.wordclouds_color_checkbox_pos,
                                   "Tick the 'Color' checkbox to open the RGB color pallette to select the desired color for your selected csv field")

color_lb = tk.Label(window, text='RGB color code ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_RGB_lb,y_multiplier_integer,color_lb,True)
color_entry = tk.Entry(window, width=10, textvariable=color_style_var)
color_entry.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_RGB,y_multiplier_integer,color_entry,True)

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

add_button = tk.Button(window, text='+', width=GUI_IO_util.add_button_width,height=1,state='disabled',command=lambda: update_csvFields())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_add_button,y_multiplier_integer,add_button, True)

reset_button = tk.Button(window, text='Reset ', width=GUI_IO_util.reset_button_width, height=1,state='disabled',command=lambda: clear_field_color_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_reset_button,y_multiplier_integer,reset_button,True)

def showList():
    if len(csvField_color_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected combinations of csv fields and colors.')
    else:
        mb.showwarning(title='Warning', message='The currently selected combination of csv fields and colors is:\n\n' + ','.join(csvField_color_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

show_columns_button = tk.Button(window, text='Show',width=GUI_IO_util.show_button_width, height=1,state='disabled',command=lambda: showList())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.wordclouds_show_button,y_multiplier_integer,show_columns_button)

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
        use_contour_only_var.set(1)
        use_contour_only_checkbox.config(state='disabled')
        prepare_image_checkbox.config(state='disabled')
        select_image_file_button.config(state='disabled')
        openImage_button.config(state='disabled')
        differentColumns_differentColor_checkbox.config(state='disabled')
        prefer_horizontal_checkbox.config(state='disabled')
        font.config(state='disabled')
        max_words.config(state='disabled')
        lemmatize_checkbox.config(state='disabled')
        stopwords_checkbox.config(state='disabled')
        punctuation_checkbox.config(state='disabled')
        lowercase_checkbox.config(state='disabled')
        collocation_checkbox.config(state='disabled')
        differentPOS_differentColor_checkbox.config(state='disabled')
    else:
        differentColumns_differentColor_checkbox.config(state='normal')
        prefer_horizontal_checkbox.config(state='normal')
        font.config(state='normal')
        max_words.config(state='normal')
        lemmatize_checkbox.config(state='normal')
        stopwords_checkbox.config(state='normal')
        punctuation_checkbox.config(state='normal')
        lowercase_checkbox.config(state='normal')
        collocation_checkbox.config(state='normal')
        differentPOS_differentColor_checkbox.config(state='normal')
        exclude_stopwords_var.set(1)
        exclude_punctuation_var.set(1)
        lowercase_var.set(1)
        collocation_var.set(1)

        prepare_image_checkbox.config(state='normal')
        select_image_file_button.config(state='normal')
        openImage_button.config(state='normal')
        use_contour_only_checkbox.config(state='normal')

wordclouds_var.trace('w',activate_Python_options)
activate_Python_options()

def changed_filename(*args):
    # if differentColumns_differentColors_var.get()==True:
    clear_field_color_list()
    # menu_values is the number of headers in the csv dictionary file
    if os.path.isfile(inputFilename.get()):
        if not inputFilename.get().endswith('csv'):
            differentColumns_differentColor_var.set(0)
            differentColumns_differentColor_checkbox.config(state='disabled')
            csv_field_menu.configure(state='disabled')
            return
        else:
            differentColumns_differentColor_checkbox.config(state='normal')
            csv_field_menu.configure(state='normal')
            menu_values = IO_csv_util.get_csvfile_headers(inputFilename.get())
            m = csv_field_menu["menu"]
            m.delete(0, "end")
            for s in menu_values:
                m.add_command(label=s, command=lambda value=s: csv_field_var.set(value))
            # activateCsvOptions()
    else:
        differentColumns_differentColor_var.set(0)
        differentColumns_differentColor_checkbox.config(state='disabled')
        csv_field_menu.configure(state='disabled')
        return
inputFilename.trace('w',changed_filename)
input_main_dir_path.trace('w',changed_filename)

changed_filename()

doNotCreateIntermediateFiles_var.set(1)
doNotCreateIntermediateFiles_checkbox = tk.Checkbutton(window, variable=doNotCreateIntermediateFiles_var, onvalue=1, offvalue=0)
doNotCreateIntermediateFiles_checkbox.config(text="Do NOT produce intermediate word cloud files when processing all txt files in a directory")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,doNotCreateIntermediateFiles_checkbox)

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

videos_lookup = {'Wordcloud 1':'https://youtu.be/CfRV9V7-OCM', 'Wordcloud 2':'https://youtu.be/5Q-AvG45rHY'}
videos_options = 'Wordcloud 1', 'Wordcloud 2'

TIPS_lookup = {"Lemmas & stopwords":"TIPS_NLP_NLP Basic Language.pdf",
               "Word clouds":"TIPS_NLP_Wordclouds Visualizing word clouds.pdf",
               "Wordle":"TIPS_NLP_Wordclouds Wordle.pdf",
               "Tagxedo":"TIPS_NLP_Wordclouds Tagxedo.pdf",
               "Tagcrowd":"TIPS_NLP_Wordclouds Tagcrowd.pdf",
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf'}
TIPS_options='Lemmas & stopwords', 'Word clouds', 'Tagcrowd', 'Tagxedo', 'Wordle','csv files - Problems & solutions', 'Statistical measures',

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_CoNLL)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the word cloud service you want to use to generate a worldcloud.\n\nFor 'TagCrowd', 'Tagul', 'Tagxedo', 'Wordclouds', and 'Wordle' you must be connected to the internet. You will also need to copy/paste text or upload a text file, depending upon the word clouds service. If you wish to visualize the words in all the files in a directory, you would need to merge the files first via the file_merger_main, then use your merged file.\n\nThe Python algorithm uses Andreas Mueller's Python package wordclouds (https://amueller.github.io/word_cloud/) can be run without internet connection.\n\nIn INPUT the algorithm expects a single txt file or a directory of txt files or a csv CoNLL table file.\n\nIn OUTPUT the algorithm creates word cloud image file(s).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","\n\nThe filter options are only available when selecting Python as the wordclouds service to use. When available,\n\n   1. tick the 'Horizonal' checkbox if you wish to display words in the wordclouds horizonally only;\n   2. select the preferred font; default font is the Adobe Droid Sans Mono font.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","\n\nThe filter options are only available when selecting Python as the wordclouds service to use. When available,\n\n   1. enter the maximum number of words to be displayed;\n   2. tick the 'Stopwords' checkbox if you wish to exclude from processing stopwords present in the input file(s);\n   3. tick the 'Lemmas' checkbox if you wish to lemmatize the words in the input file(s);\n   4. tick the 'Punctuation' checkbox if you wish to exclude from processing punctuation symbols present in the input file(s);\n   5. tick the 'Lowercase' checkbox if you wish to convert all words to lowercase to avoid having some words capitalized simply because they are the first words in a sentence;\n   6. tick the 'Collocation' checkbox if you wish to keep together common combinations of words (South Carolina; White House);\n   7. tick the 'Different colors for different POS tags' checkbox if you wish to display different POSTAG values (namely, nouns, verbs, adjectives, and adverbs) in different colors (RED for NOUNS (including proper nouns), BLUE for VERBS, GREEN for ADJECTIVES, and GREY for ADVERBS). For greater control over the use of different colors for different items, you can use the csv file option below with a CoNLL table as input. You will then be able to use NER or DEPREL and not just POSTAG (or more POSTAG values).\n\nStanford CoreNLP STANZA will be used to tokenize sentences, lemmatize words, and compute POS tags. Depending upon the number of files processed and length of files, the process can be time consuming. Please, be patient.\n\nREGARDLESS OF OPTIONS SELECTED, THE S OF THE SAXON GENITIVE WILL NOT BE DISPLAYED.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox to open the web service Removebg (https://www.remove.bg/) that will prepare an image for use in the Python wordclouds algorithm, removing all image background and turning it into white.\n\nYou can then use the output png image file to create the wordclouds (see the widget 'Select png image' file).\n\nYOU MUST BE CONNECTED TO THE INTERNET.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, select a png image file to be used to display the word cloud in the image.\n\nThe image must have a white background.\n\nYou can use the image file created via removebg (see the widget 'Prepare image').\n\nClick on the button to the right of the widget 'Select png image file' to open the file.\n\nTick the checkbox 'Use image contour only' if you want to use the contour of the image rather than the full image.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you are using a csv file in input and you wish to run the Python 3 Andreas Mueller's package WordCloud (https://amueller.github.io/word_cloud/) assigning different colors to the values of different columns of the csv file.\n\nThus, if, from a file, you have extracted SVOs (Subjects, Verbs, Objects) or POSTAG values (nouns, verbs, and adjectives), saving these values in different columns, this function will allow you to display the values in the different columns in different, user-selected colors (e.g., RED for the column of NOUNS, BLUE for the column of VERBS).\n\nThe wordclouds algorithm can color all the values of a column differently from all the values of another column. The algorithm is NOT setup to color differently the different values within a column (to accomplish this goal, you would need to manipulate first the csv file; for instance, if the input file is a CoNLL table, you could extract all the NER values COUNTRY, CITY, and STATE_OR_PROVINCE and the NER tag PERSON and ORGANIZATION, save them as two separate columns, and then use this new csv file in the current wordclouds algorithm).\n\nIn INPUT the algorithm expects a single csv file rather than a text file or a directory.\n\nIn OUTPUT the algorithm creates a word cloud image file.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Pease, select the sets of csv file fields and colors.\n\nPress the + button to add more csv file fields.\n\nPress the RESET button (or simply ESCape) to delete all values entered and start fresh.\n\nPress SHOW to display all selected values.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, untick the checkbox if you want to create intermediate image files for every txt file in a directory when processing all the txt files in a directory. These image files will be in addition to the final file which will include the words from all files in the directory (so, if there is 1 file in the directory, this will lead to 2 files, although in this case, the image utput will be exactly the same for each of he 2 files).\n\nWARNING! Unticking the checkbox may result in a very large number of intermediate files (1 word cloud image file for every txt file in the directory).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 script and online services display the content of text files as word cloud.\n\nA word cloud, also known as text cloud or tag cloud, is a collection of words depicted visually in different sizes (and colors). The bigger and bolder the word appears, the more often it’s mentioned within a given text and the more important it is.\n\nDifferent, freeware, word cloud applications are available: 'TagCrowd', 'Tagul', 'Tagxedo', 'Wordclouds', and 'Wordle'. These applications require internet connection.\n\nThe script also provides Python word clouds (via Andreas Mueller's Python package WordCloud https://amueller.github.io/word_cloud/) for which no internet connection is required.\n\nIn INPUT the algorithm expects a single txt file or a directory of txt files or a csv file. When a csv CoNLL file is selected the algorithm processes automatically the wordclouds visualization. When a non-CoNLL csv file is selected, you must select the csv field to be used for wordclouds visualization.\n\nIn OUTPUT the algorithms create word cloud image file(s)."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)


def activate_NLP_options(*args):
    global error, package_basics, package, language, language_var, language_list
    error, package, parsers, package_basics, language, package_display_area_value_new, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
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

import wordclouds_util
font_list = wordclouds_util.get_font_list()
font['values'] = font_list

GUI_util.window.mainloop()
