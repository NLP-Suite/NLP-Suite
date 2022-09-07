# written by Roberto Franzosi October 2019, edited Spring 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_splitter_main.py",['os','tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb

import GUI_IO_util
import IO_files_util
import IO_user_interface_util
import file_checker_util
import file_cleaner_util
import reminders_util
import config_util

# import several splitter util scripts under various if statements under Run

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,inputDir, outputDir,
    openOutputFiles,
    createCharts,
    chartPackage,
    utf8_var,
    ASCII_var,
    split_mergedFile,
    split_mergedFile_separator_entry_begin,
    split_mergedFile_separator_entry_end,
    splitByTOC,
    TOC_filename,
    splitByFileLength,
    split_docLength,
    splitByKeyword,
    keyword_value_var,
    lemmatize_var,
    first_occurrence_var,
    extract_sentences_var,
    extract_sentences_search_words_var,
    splitByString,
    string_value_var,
    blankLine_var,
    number_var,
    post_num_string_value_var,
    split_csv_by_documentID_var,
    menu_option):

    if utf8_var==True:
        startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                            'Started running utf8 compliance test at', True)
        file_checker_util.check_utf8_compliance(GUI_util.window, inputFilename, inputDir, outputDir,openOutputFiles)

    if ASCII_var==True:
        startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                            'Started running characters conversion at', True)
        file_cleaner_util.convert_quotes(GUI_util.window,inputFilename, inputDir)

    if extract_sentences_var:
        import sentence_analysis_util
        sentence_analysis_util.extract_sentences(window, inputFilename, inputDir, outputDir, extract_sentences_search_words_var)
        return

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                      "Started running " + menu_option + " at", True)

    if inputDir=='' and inputFilename!='':
        files=[inputFilename]
    elif inputDir!='':
        files= IO_files_util.getFileList(inputFilename, inputDir, 'txt')
    if len(files) == 0:
        return

    for file in files:
        #print("file",file)
        docname = os.path.split(file)[1]
        title = docname.partition('.')[0]
        keyword_value_var=keyword_value_var.strip()

        # split TOC --------------------------------------------------------------------------------------
        if splitByTOC:
            if TOC_filename == '':
                mb.showwarning(title='Input error',
                               message='The selected option - ' + menu_option + ' - requires a Table of Content file in input.\n\nPlease, select the file and try again.')
                return
            import file_splitter_ByTOC_util
            file_splitter_ByTOC_util.splitDocument_byTOC(GUI_util.window,file,TOC_filename, outputDir,openOutputFiles)
        # split <@# #@> --------------------------------------------------------------------------------------
        elif split_mergedFile:
            subDir=''
            nFiles=0
            import file_splitter_merged_txt_util
            subDir, nFiles=file_splitter_merged_txt_util.run(file,
                                          split_mergedFile_separator_entry_begin,
                                          split_mergedFile_separator_entry_end,
                                          outputDir)
            mb.showwarning(title='Exported files',
                           message=str(nFiles) + ' split files were created in the subdirectory of the output directory\n\n' + subDir)
            return
        # split file length --------------------------------------------------------------------------------------
        elif splitByFileLength:
            specialOutputPath = inputDir + os.sep +"split_files_"+split_docLength+"_"+title
            # no matter what the input of outputfile is, it will always generate a subfile that includes all output
            if not os.path.exists(specialOutputPath):
                os.mkdir(specialOutputPath)
            if splitByFileLength and split_docLength=='':
                mb.showwarning(title='Input error', message='The selected option - ' + menu_option + ' - requires a valid number of words for splitting the document.\n\nPlease, enter a value and try again.')
                return
            import file_splitter_ByLength_util
            file_splitter_ByLength_util.split_byLength(GUI_util.window,inputDir,file,specialOutputPath,maxLength=int(split_docLength), inSentence=True)
        # split keyword --------------------------------------------------------------------------------------
        elif splitByKeyword:
            # The following reserved characters for Windows filenames and directory names:
            # < (less than)
            # > (greater than)
            # : (colon)
            # " (double quote)
            # / (forward slash)
            # \ (backslash)
            # | (vertical bar or pipe)
            # ? (question mark)
            # * (asterisk)
            # if '<' or '>' or ':' or '"' or '/' or '\\' or '|' or '?' or '*' in keyword_value_var:
            # Strip the keyword_value_var of any character that would leaad to an illegal folder name
            title_var = keyword_value_var
            for letter in title_var:
                if letter == '<' or letter == '>' or letter ==':' or letter =='"' or letter =='/' or letter =='\\' or letter =='|' or letter =='?' or letter =='*':
                    title_var = title_var.replace(letter,"")
            specialOutputPath = inputDir + os.sep + "split_files_"+title_var+"_"+title
            # no matter what the input of outputfile is, it will always generate a subfile that includes all output
            if not os.path.exists(specialOutputPath):
                os.mkdir(specialOutputPath)
            if file[-4:]=='.txt':
                import file_splitter_ByKeyword_txt_util
                file_splitter_ByKeyword_txt_util.run(file, specialOutputPath, keyword_value_var, first_occurrence_var, lemmatize_var)
            elif file[-4:]=='.csv':
                import file_splitter_ByKeyword_conll_util
                file_splitter_ByKeyword_conll_util.run(file, specialOutputPath, keyword_value_var, first_occurrence_var, generateForm = False)

        elif splitByString: # created for MLK comments
            import file_splitter_ByString_util
            target='pp.'
            spot_one=-7
            spot_two=-5
            file_splitter_ByString_util.splitDocument_byStrings(file, outputDir, target, spot_one, spot_two, True)
        elif blankLine_var:
            import file_splitter_ByString_util
            file_splitter_ByString_util.split_by_blanks(file, outputDir)
        elif number_var:
            import file_splitter_ByNumber_util
            file_splitter_ByNumber_util.run(file, outputDir, post_num_string_value_var)
        elif split_csv_by_documentID_var:
            if file[-4:]!='.csv':
                mb.showwarning(title='Warning',message="The 'split by Document ID' function expects in input a csv file with at least one field labeled 'Document ID'.\n\nPlerase, select a csv file and try again.")
                return
            else:
                import file_splitter_ByDocumentID_csv_util
                file_splitter_ByDocumentID_csv_util.split_NLP_Suite_csv_output_by_document_id(file,outputDir)
    # IO_user_interface_util.timed_alert(GUI_util.window, 2000, "Analysis end", "Finished running '" + menu_option + "' at", True)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_chart_output_checkbox.get(),
                            GUI_util.charts_dropdown_field.get(),
                            utf8_var.get(),
                            ASCII_var.get(),
                            split_mergedFile_var.get(),
                            split_mergedFile_separator_entry_begin_var.get(),
                            split_mergedFile_separator_entry_end_var.get(),
                            TOC_var.get(),
                            TOC_filename_var.get(),
                            docLength_var.get(),
                            split_docLength_var.get(),
                            keyword_var.get(),
                            keyword_value_var.get(),
                            lemmatize_var.get(),
                            first_occurrence_var.get(),
                            extract_sentences_var.get(),
                            extract_sentences_search_words_var.get(),
                            string_var.get(),
                            string_value_var.get(),
                            blankLine_var.get(),
                            number_var.get(),
                            post_num_string_value_var.get(),
                            split_csv_by_documentID_var.get(),
                            menu_option)

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# GUI section ______________________________________________________________________________________________________________________________________________________
# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=640, # height at brief display
                             GUI_height_full=720, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display


GUI_label='Graphical User Interface (GUI) for File Splitter'
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

window = GUI_util.window
# config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
# config_filename = GUI_util.config_filename
inputDir = GUI_util.input_main_dir_path
outputDir = GUI_util.output_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename,IO_setup_display_brief)

menu_option = ''

utf8_var = tk.IntVar()
ASCII_var = tk.IntVar()
split_mergedFile_var = tk.IntVar()
split_mergedFile_separator_entry_begin_var = tk.StringVar()
split_mergedFile_separator_entry_end_var = tk.StringVar()
TOC_var = tk.IntVar()
TOC_filename_var = tk.StringVar()
split_docLength_var = tk.StringVar()
docLength_var = tk.IntVar()
current_docLength_var = tk.StringVar()
keyword_var = tk.IntVar()
keyword_value_var = tk.StringVar()
lemmatize_var = tk.IntVar()
first_occurrence_var = tk.IntVar()
string_var = tk.IntVar()
string_value_var = tk.StringVar()
extract_sentences_var = tk.IntVar()
extract_sentences_search_words_var = tk.StringVar()
blankLine_var = tk.IntVar()
number_var = tk.IntVar()
post_num_string_value_var = tk.StringVar()
split_csv_by_documentID_var = tk.IntVar()

def clear(e):
    GUI_util.clear("Escape")

window.bind("<Escape>", clear)

# setup GUI widgets

utf8_var.set(0)
utf8_checkbox = tk.Checkbutton(window, text='Check input corpus for utf-8 encoding', variable=utf8_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,utf8_checkbox,True)

ASCII_var.set(0)
ASCII_checkbox = tk.Checkbutton(window, text='Convert non-ASCII apostrophes & quotes and % to percent', variable=ASCII_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+440,y_multiplier_integer,ASCII_checkbox)

split_mergedFile_separator_entry_begin = tk.Entry(window, width=10,
                                                  textvariable=split_mergedFile_separator_entry_begin_var)
split_mergedFile_separator_entry_end = tk.Entry(window, width=10, textvariable=split_mergedFile_separator_entry_end_var)

split_mergedFile_var.set(0)
split_mergedFile_checkbox = tk.Checkbutton(window,
                                           text='Split a merged file with filename embedded in separator strings',
                                           state='normal', variable=split_mergedFile_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               split_mergedFile_checkbox, True)


def display_split_mergedFile_separator(y_multiplier_integer):
    split_mergedFile_separator_entry_begin_var.set("<#@")
    split_mergedFile_separator_entry_begin.configure(state="disabled")
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate() + 440, y_multiplier_integer,
                                                   split_mergedFile_separator_entry_begin, True)

    split_mergedFile_separator_entry_end_var.set("#@>")
    split_mergedFile_separator_entry_end.configure(state="disabled")
    y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate() + 520, y_multiplier_integer,
                                                   split_mergedFile_separator_entry_end)


display_split_mergedFile_separator(y_multiplier_integer)
y_multiplier_integer = y_multiplier_integer + 1


def getTOCFile():
    if TOC_var.get() == True:
        filePath = tk.filedialog.askopenfilename(title='Select INPUT txt file', initialdir=GUI_util.inputFilename.get(),
                                                 filetypes=[("txt files", "*.txt")])
        if len(filePath) > 0:
            TOC_filename_var.set(filePath)
    else:
        TOC_filename_var.set('')


TOC_var.set(0)
TOC_checkbox = tk.Checkbutton(window, text='Split using Table of Contents (TOC)', variable=TOC_var, onvalue=1,
                              offvalue=0, command=lambda: getTOCFile())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               TOC_checkbox, True)

TOC_filename = tk.Entry(window, width=80, textvariable=TOC_filename_var)
TOC_filename.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               TOC_filename)

docLength_var.set(0)
docLength_checkbox = tk.Checkbutton(window, text='Split by number of words', variable=docLength_var, onvalue=1,
                                    offvalue=0, command=lambda: getDocLength())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               docLength_checkbox, True)

current_docLength_lb = tk.Label(window, text='Word count in selected file')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               current_docLength_lb, True)

current_docLength = tk.Entry(window, width=10, state="disabled", textvariable=current_docLength_var)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 180, y_multiplier_integer,
                                               current_docLength, True)

split_docLength_lb = tk.Label(window, text='Max word count in split files')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 270, y_multiplier_integer,
                                               split_docLength_lb, True)

split_docLength = tk.Entry(window, width=10, textvariable=split_docLength_var)
split_docLength.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 480, y_multiplier_integer,
                                               split_docLength)


def getDocLength():
    if GUI_util.inputFilename.get() == '' or GUI_util.inputFilename.get()[-4:] != '.txt':
        current_docLength_var.set('')
        return
    with open(GUI_util.inputFilename.get(), 'r', encoding='utf-8', errors='ignore') as F:
        text = F.read()
        length = len(text.split())
    F.close()
    current_docLength_var.set(length)


getDocLength()

keyword_var.set(0)
keyword_checkbox = tk.Checkbutton(window, text='Split by word(s)', variable=keyword_var, onvalue=1, offvalue=0,
                                  command=lambda: getDocLength())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               keyword_checkbox, True)

keyword_value_var.set('')
keyword_value = tk.Entry(window, width=50, textvariable=keyword_value_var)
keyword_value.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               keyword_value, True)

lemmatize_var.set(0)
lemmatize_checkbox = tk.Checkbutton(window, text='Lemmatize', variable=lemmatize_var, onvalue=1, offvalue=0)
lemmatize_checkbox.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 420, y_multiplier_integer,
                                               lemmatize_checkbox, True)

first_occurrence_var.set(0)
first_occurrence_checkbox = tk.Checkbutton(window, text='First occurrence', variable=first_occurrence_var, onvalue=1,
                                           offvalue=0)
first_occurrence_checkbox.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 550, y_multiplier_integer,
                                               first_occurrence_checkbox)

extract_sentences_var.set(0)
extract_sentences_checkbox = tk.Checkbutton(window, text='Split by word(s) (extract sentences)',
                                            variable=extract_sentences_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               extract_sentences_checkbox, True)

extract_sentences_search_words_var.set('')
search_words_entry = tk.Entry(window, textvariable=extract_sentences_search_words_var)
search_words_entry.configure(width=100, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               search_words_entry)

string_var.set(0)
string_checkbox = tk.Checkbutton(window, text='Split by string', variable=string_var, onvalue=1, offvalue=0,
                                 command=lambda: getDocLength())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               string_checkbox, True)

string_value_var.set('')
string_value = tk.Entry(window, width=100, textvariable=string_value_var)
string_value.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               string_value)

blankLine_var.set(0)
blankLine_checkbox = tk.Checkbutton(window, text='Split by an empty blank line', variable=blankLine_var, onvalue=1,
                                    offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               blankLine_checkbox)

number_var.set(0)
number_checkbox = tk.Checkbutton(window, text='Split by a line that starts with a number (like a bullet point)',
                                 variable=number_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               number_checkbox, True)
# post_num is the string behind each number
# (if the numbers in the txt are in the form of "1. ", "2. ", then the post_num should be ". ")

post_num_string_value_lb = tk.Label(window,
                                    text='Enter characters to be expected after a bullet-point number (e.g., . )')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 100, y_multiplier_integer,
                                               post_num_string_value_lb, True)

post_num_string_value_var.set('')
post_num_string_value = tk.Entry(window, width=10, textvariable=post_num_string_value_var)
post_num_string_value.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate() + 500, y_multiplier_integer,
                                               post_num_string_value)

split_csv_by_documentID_var.set(0)
split_csv_by_documentID_checkbox = tk.Checkbutton(window, text='Split csv merged file into separate files by Document ID',
                                 variable=split_csv_by_documentID_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               split_csv_by_documentID_checkbox)

def activate_allOptions(*args):
    global menu_option
    split_mergedFile_separator_entry_begin.configure(state="disabled")
    split_mergedFile_separator_entry_end.configure(state="disabled")
    TOC_checkbox.configure(state='disabled')
    TOC_filename_var.set('')
    string_value_var.set('')
    split_docLength_var.set('')
    split_docLength.configure(state="disabled")
    keyword_value.configure(state='disabled')
    keyword_value_var.set('')
    lemmatize_checkbox.configure(state='disabled')
    first_occurrence_checkbox.configure(state='disabled')
    lemmatize_var.set(0)
    first_occurrence_var.set(0)
    extract_sentences_checkbox.configure(state='disabled')
    search_words_entry.configure(state='disabled')

    string_value.configure(state='disabled')
    post_num_string_value.configure(state='disabled')
    post_num_string_value_var.set('')

    split_mergedFile_checkbox.configure(state="normal")
    TOC_checkbox.configure(state='normal')
    docLength_checkbox.configure(state="normal")
    keyword_checkbox.configure(state="normal")
    string_checkbox.configure(state='normal')
    extract_sentences_checkbox.configure(state='normal')
    blankLine_checkbox.configure(state='normal')
    number_checkbox.configure(state='normal')

    if split_mergedFile_var.get() == True:
        menu_option = 'Split merged file'
        split_mergedFile_separator_entry_begin.configure(state="normal")
        split_mergedFile_separator_entry_end.configure(state="normal")
        TOC_checkbox.configure(state='disabled')
        docLength_checkbox.configure(state="disabled")
        keyword_checkbox.configure(state='disabled')
        string_checkbox.configure(state='disabled')
        extract_sentences_checkbox.configure(state='disabled')
        blankLine_checkbox.configure(state='disabled')
        number_checkbox.configure(state='disabled')

    if TOC_var.get() == True:
        menu_option = 'Split file by TOC'
        split_mergedFile_checkbox.configure(state="disabled")
        docLength_checkbox.configure(state="disabled")
        keyword_checkbox.configure(state="disabled")
        extract_sentences_checkbox.configure(state='disabled')
        string_checkbox.configure(state='disabled')
        blankLine_checkbox.configure(state='disabled')
        number_checkbox.configure(state='disabled')

    if docLength_var.get() == True:
        menu_option = 'Split file by number of words'
        split_docLength.configure(state="normal")
        TOC_checkbox.configure(state="disabled")
        split_mergedFile_checkbox.configure(state="disabled")
        keyword_checkbox.configure(state="disabled")
        extract_sentences_checkbox.configure(state='disabled')
        string_checkbox.configure(state='disabled')
        blankLine_checkbox.configure(state='disabled')
        number_checkbox.configure(state='disabled')

    if keyword_var.get() == True:
        menu_option = 'Split by word(s)'
        keyword_value.configure(state='normal')
        lemmatize_checkbox.configure(state='normal')
        first_occurrence_checkbox.configure(state='normal')
        split_mergedFile_checkbox.configure(state="disabled")
        TOC_checkbox.configure(state='disabled')
        docLength_checkbox.configure(state="disabled")
        extract_sentences_checkbox.configure(state='disabled')
        string_checkbox.configure(state='disabled')
        blankLine_checkbox.configure(state='disabled')
        number_checkbox.configure(state='disabled')

    if extract_sentences_var.get() == True:
        menu_option = 'Split by word(s) (extract sentences)'
        search_words_entry.configure(state='normal')
        keyword_value.configure(state='disabled')
        lemmatize_checkbox.configure(state='disabled')
        first_occurrence_checkbox.configure(state='disabled')
        split_mergedFile_checkbox.configure(state="disabled")
        TOC_checkbox.configure(state='disabled')
        docLength_checkbox.configure(state="disabled")
        string_checkbox.configure(state='disabled')
        blankLine_checkbox.configure(state='disabled')
        number_checkbox.configure(state='disabled')

    if string_var.get() == True:
        menu_option = 'Split file by string'
        string_value.configure(state='normal')
        split_mergedFile_checkbox.configure(state="disabled")
        TOC_checkbox.configure(state='disabled')
        docLength_checkbox.configure(state="disabled")
        keyword_checkbox.configure(state='disabled')
        extract_sentences_checkbox.configure(state='disabled')
        blankLine_checkbox.configure(state='disabled')
        number_checkbox.configure(state='disabled')

    if blankLine_var.get() == True:
        menu_option = 'Split file by blank line'
        split_mergedFile_checkbox.configure(state="disabled")
        TOC_checkbox.configure(state='disabled')
        docLength_checkbox.configure(state="disabled")
        keyword_checkbox.configure(state='disabled')
        extract_sentences_checkbox.configure(state='disabled')
        string_checkbox.configure(state='disabled')
        number_checkbox.configure(state='disabled')

    if number_var.get() == True:
        menu_option = 'Split file by number (bullet point)'
        post_num_string_value.configure(state='normal')
        split_mergedFile_checkbox.configure(state="disabled")
        TOC_checkbox.configure(state='disabled')
        docLength_checkbox.configure(state="disabled")
        keyword_checkbox.configure(state='disabled')
        extract_sentences_checkbox.configure(state='disabled')
        string_checkbox.configure(state='disabled')
        blankLine_checkbox.configure(state='disabled')


split_mergedFile_var.trace('w', activate_allOptions)
TOC_var.trace('w', activate_allOptions)
docLength_var.trace('w', activate_allOptions)
keyword_var.trace('w', activate_allOptions)
extract_sentences_var.trace('w', activate_allOptions)
string_var.trace('w', activate_allOptions)
blankLine_var.trace('w', activate_allOptions)
number_var.trace('w', activate_allOptions)
extract_sentences_var.trace('w', activate_allOptions)

activate_allOptions()


def changed_filename(*args):
    getDocLength()


GUI_util.inputFilename.trace('w', changed_filename)

changed_filename()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'File manager': 'TIPS_NLP_File manager.pdf',
               'File handling in NLP Suite': "TIPS_NLP_File handling in NLP Suite.pdf",
               'Filename checker': 'TIPS_NLP_Filename checker.pdf', 'Filename matcher': 'TIPS_NLP_Filename matcher.pdf',
               'File classifier (By date)': 'TIPS_NLP_File classifier (By date).pdf',
               'File classifier (By NER)': 'TIPS_NLP_File classifier (By NER).pdf',
               'File content checker & converter': 'TIPS_NLP_File checker & converter.pdf',
               'Text encoding (utf-8)': 'TIPS_NLP_Text encoding (utf-8).pdf',
               'Spelling checker': 'TIPS_NLP_Spelling checker.pdf', 'File merger': 'TIPS_NLP_File merger.pdf',
               'File splitter': 'TIPS_NLP_File splitter.pdf'}
TIPS_options = 'File splitter', 'File merger', 'File handling in NLP Suite', 'File manager', 'Filename checker', 'Filename matcher', 'File classifier (By date)', 'File classifier (By NER)', 'File content checker & converter', 'Text encoding (utf-8)', 'Spelling checker'


# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    clearOptions = "\n\nTo clear a previously selected option for any of the tools, click on the appropriate dropdown menu and press ESCape twice."
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_anyFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_anyData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox to check your input corpus for utf-8 encoding.\n   Non utf-8 compliant texts are likely to lead to code breakdown.\n\nTick the checkbox to convert non-ASCII apostrophes & quotes and % to percent.\n   ASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n   % signs may lead to code breakdon of Stanford CoreNLP.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if the file to be split is a merged file with filenames embedded in start/end strings (e.g., <@#The New York Times_11-02-1992_4_1#@>).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox to split a txt file into separate files using a Table of Contents as the criterion for splitting. Once you tick the checkbox you will be asked to select the txt file containing the Table of Contents to be used.\n\nIn INPUT the Document splitter script expects two types of txt-type files:\n   1. a main txt file (e.g., The Philosopher’s Stone.txt) with the body of a text and section headings (e.g., chapter titles of the Harry Potter book);\n   2. a txt TOC file (Table of Content) that contains all the section headings of the main document (one section heading per line).\n\nSECTION HEADINGS IN THE TOC MUST MATCH EXACTLY THE SECTION HEADINGS IN THE MAIN DOCUMENT.\n   CASE WILL BE IGNORED IN MATCHING SECTION TITLE IN TOC AND MAIN DOCUMENT.\n   REMOVE TABLE OF CONTENTS FROM THE MAIN DOCUMENT TO BE SPLIT.\n\nIn OUTPUT, the script will split the main file into sub-documents, one document for each of the headings listed in the TOC file. The output documents will be placed in a new subdirectory where the main input file is stored. ANY TOC HEADINGS NOT FOUND IN THE MAIN DOCUMENT WILL BE LISTED IN A csv ERROR FILE.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox to split a txt file into separate files using a maximum number of words as the criterion for splitting.\n\nThe number of words in the selected file is displayed in the second widget, Word count in selected file. You will need to enter to desired maximum number of words in each split file in the third widget, Max word count in split files.\n\nIn INPUT, the script can either take a single txt file or a directory.\n\nIn OUTPUT, the script will generate the split files in a subdirectory, named split_files, of the directory of the input file or directory.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox to split a txt file into separate files using single words or collocations, i.e., combinations of words such as 'coming out,' 'standing in line,' as the criterion for splitting.\n\nThe widget where you can enter your words/collocations will become available once you select the option. Enter there the comma-separated words/set of words to be used for splitting the input file(s) (e.g, coming out, standing in line, boyfriend).\n\nYou have the option to LEMMATIZE the expression you entered (thus, the expression 'coming out', when the 'Lemmatize' checkbox is ticked, would be checked for 'coming out', 'come out', 'came out', 'comes out').\n\nYou also have the option to split a file by the FIRST OCCURRENCE of the expression entered (which would always result in two txt output files) or of splitting the file at every occurrence of the expression entered (thus leading to multiple output txt files, one for each occurrence of the expression).\n\nIn INPUT, the script can either take a single file or a directory. THE SCRIPT CAN EITHER SEARCH IN A CONLL TABLE OR IN TEXT FILE.\n\nIn OUTPUT, the script will generate the split files in a subdirectory, named split_files, of the directory of the input file or directory.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to extract all the sentences from your input txt file(s) that contain specific words (single words or collocations, i.e., sets of words, such as coming out, falling in love).\n\nThe widget where you can enter your words/collocations will become available once you select the option. Enter there the comma-separated words/set of words that a sentence must contain in order to be extracted from input and saved in output (e.g, coming out, standing in line, boyfriend).\n\nIn INPUT, the script expects a single txt file or a directory of txt files.\n\nIn OUTPUT the script produces two types of files:\n1. files ending with _extract.txt and containing, for each input file, all the sentences that have the search word(s);\n2. files ending with _extract_minus.txt and containing, for each input file, the sentences that do NOT have the search word(s)." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick then checkbox to split a txt file into separate files using string values as the criterion for splitting.\n\nIn INPUT, the script can either take a single file or a directory. \n\nIn OUTPUT, the script will generate the split files in a subdirectory, named split_files, of the directory of the input file or directory.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox to split a txt file into separate files using a blank line in the text as the criterion for splitting.\n\nIn INPUT, the script can either take a single file or a directory. \n\nIn OUTPUT, the script will generate the split files in a subdirectory, named split_files, of the directory of the input file or directory.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox to split a txt file into separate files using a number at the start of the line (like a bullet point) as the criterion for splitting.\n\nIn INPUT, the script can either take a single file or a directory. \n\nIn OUTPUT, the script will generate the split files in a subdirectory, named split_files, of the directory of the input file or directory.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox to split a merged csv file containing several different 'Document ID' and 'Document' into separate csv files one for each 'Document ID' and 'Document'.\n\nIn INPUT, the function expects a single merged csv file containing the fields 'Document ID' and 'Document'.\n\nIn OUTPUT, the function will create multiple csv files (as many as 'Document ID's in the INPUT merged csv file).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1

y_multiplier_integer = help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), 0)

# change the value of the readMe_message
readMe_message = "These Python 3 scripts split txt files into separate txt files with a number of processing options."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

def activate_NLP_options(*args):
    global error, package_basics, package, language_list
    error, package, parsers, package_basics, language, package_display_area_value = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]
GUI_util.setup_menu.trace('w', activate_NLP_options)
activate_NLP_options()

if error:
    mb.showwarning(title='Warning',
               message="The config file 'NLP_default_package_language_config.csv' could not be found in the sub-directory 'config' of your main NLP Suite folder.\n\nPlease, setup the default NLP package and language options using the Setup widget at the bottom of this GUI.")

title=["NLP setup options"]
message="Some of the algorithms behind this GUI rely on a specific NLP package to carry out basic NLP functions (e.g., sentence splitting, tokenizing, lemmatizing) for a specific language your corpus is written in.\n\nYour selected corpus language is " + ', '.join(language_list) + ".\nYour selected NLP package for basic functions (e.g., sentence splitting, tokenizing, lemmatizing) is " + package_basics + ".\n\nYou can always view your default selection saved in the config file NLP_default_package_language_config.csv by hovering over the Setup widget at the bottom of this GUI and change your default options by selecting Setup NLP package and corpus language."
reminders_util.checkReminder(config_filename, title, message)

GUI_util.window.mainloop()

