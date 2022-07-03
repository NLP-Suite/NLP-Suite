# written by Roberto Franzosi October 2019, edited Spring 2020
# the script checks the CONTENT of txt files with various options:
#   utf-compliance
#   spelling
# the script also converts files types (pdf-->txt; docx-->txt)  

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_checker_converter_cleaner_main.py",['tkinter','importlib'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
import importlib

import GUI_IO_util
import IO_files_util

# RUN section ______________________________________________________________________________________________________________________________________________________


def run(inputFilename,inputDir, outputDir,
    openOutputFiles,
    createCharts,
    chartPackage,
    check_tools,
    convert_tools,
    clean_tools,
    menu_option,
    script_to_run,
    function_to_run):

    filesToOpen=[]

    if (check_tools=='') and (convert_tools=='') and (clean_tools==""):
        mb.showwarning(title='No options selected', message='No options have been selected.\n\nPlease, select one of the available options and try again.')
        return

    if menu_option=='Document converter (rtf --> txt)':
        mb.showwarning(title='rtf --> txt converter (Mac OS)', message='In a Mac OS, there is a simple way to batch convert a set of rtf files to txt. THIS ONLY APPLIES TO MAC OS!\n\nOpen the command prompt and change directory to where the rtf files are stored, then type:\n\nfind . -name \*.rtf -print0 | xargs -0 textutil -convert txt\n\nHit return. All txt converted files will be found in the same input directory as the original rtf files.\n\nFor more information, see the post by Alexander Refsum Jensenius at:\nhttps://www.arj.no/2013/01/08/batch-convert-rtf-files-to-txt/.')
        # return

    if ((check_tools!='') and (clean_tools!='')) and ((inputDir=="") and (inputFilename=="")):
        mb.showwarning(title='Input error', message='The selected option - ' + menu_option + ' - requires either a txt file or a directory in input.\n\nPlease, select a txt file or directory and try again.')
        return

    if check_tools!='' or convert_tools!='' or clean_tools!='':
        if 'check_for_typo' in function_to_run:
            mb.showwarning(title='Option not available', message='The Levenshtein\'s distance option is not available from this GUI.\n\nPlease, run the script from the spell_checker_main.')
            return

        # if 'Vocabulary richness' in function_to_run or 'Short words' in function_to_run or 'Vowel words' in function_to_run:
        #     mb.showwarning(title='Option not available',
        #                    message='The option is not available from this GUI.\n\nPlease, run the script from the style_analysis_main.')
        #     return

        pythonFile = importlib.import_module(script_to_run)
        func = getattr(pythonFile, function_to_run)
        if IO_libraries_util.check_inputPythonJavaProgramFile(script_to_run + ".py") == False:
            return
        outputFile=[]

        if 'predict_encoding' in function_to_run or 'empty_file' in function_to_run:
            # use default first 20 lines
            func(inputFilename,inputDir)
        elif 'sentence_length' in function_to_run:
            outputFile=func(inputFilename,inputDir,outputDir)
        else:
            func(GUI_util.window,inputFilename,inputDir, outputDir,openOutputFiles,createCharts,chartPackage)

        if len(outputFile)>0:
            filesToOpen.extend(outputFile)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

    # IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
    #                                        'Started running ' + menu_option + ' at', True,
    #                                        'You can follow ' + menu_option + ' in command line.')
    #
    # IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running ' + menu_option + ' at', True)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_chart_output_checkbox.get(),
                            GUI_util.charts_dropdown_field.get(),
                            check_tools_var.get(),
                            convert_tools_var.get(),
                            clean_tools_var.get(),
                            menu_option,
                            script_to_run,
                            function_to_run)

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                     GUI_width=GUI_IO_util.get_GUI_width(3),
                                                     GUI_height_brief=360,
                                                     # height at brief display
                                                     GUI_height_full=440,  # height at full display
                                                     y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                     y_multiplier_integer_add=2,
                                                     # to be added for full display
                                                     increment=2)  # to be added for full display


GUI_label='Graphical User Interface (GUI) for File Content Checker & File Type Converter & File Content Cleaner'
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
config_input_output_numeric_options=[4,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputDir =GUI_util.input_main_dir_path
outputDir =GUI_util.output_dir_path

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)

script_to_run=''
function_to_run=''
menu_option=''

pydict = {}
pydict["Document converter (csv --> txt)"] = ["file_type_converter_util.csv_converter"]
pydict["Document converter (docx --> txt)"] = ["file_type_converter_util.docx_converter"]
pydict["Document converter (pdf --> txt)"] = ["file_type_converter_util.pdf_converter"]
pydict["Document converter (rtf --> txt)"] = ["file_type_converter_util.rtf_converter"]
pydict["Check utf-8 encoding compliance"] = ["file_checker_util.check_utf8_compliance"]
pydict["Check empty file"] = ["file_checker_util.check_empty_file"]
pydict["Check sentence length (extracting sentences)"] = ["sentence_analysis_util.extract_sentence_length"]
pydict["Language detector"] = ["file_spell_checker_util.language_detection"]
pydict["Predict encoding (via chardet)"] = ["file_checker_util.predict_encoding"]
pydict["Spelling checker/Unusual words (via nltk)"] = ["file_spell_checker_util.nltk_unusual_words"]
pydict["Spelling checker (via SpellChecker)"] = ["file_spell_checker_util.check_for_typo"]
pydict["Change to ASCII non-ASCII apostrophes & quotes and % to percent"] = ["file_cleaner_util.convert_quotes"]
pydict["Remove all characters between a set of characters (e.g., []) from text file(s)"] = ["file_cleaner_util.remove_characters_between_characters"]
pydict["Remove blank lines from text file(s)"] = ["file_cleaner_util.remove_blank_lines"]
pydict["Find & Replace string"] = ["file_cleaner_util.find_replace_string"]
pydict["Find & Replace string (via csv file)"] = ["file_spell_checker_util.spelling_checker_cleaner"]
pydict["Separate titles from documents (newspaper articles)"] = ["file_cleaner_util.newspaper_titles"]
pydict["Add full stop (.) at the end of paragraphs without end-of-paragraph punctuation"] = ["file_cleaner_util.add_full_stop_to_paragraph"]
# pydict["Vocabulary richness (Yule\'s K)"] = ["style_analysis_main.Vocabulary richness"]
# pydict["Short words"] = ["style_analysis_main.Short words"]
# pydict["Vowel words"] = ["style_analysis_main.Vowel words"]

check_tools_var=tk.StringVar()
convert_tools_var=tk.StringVar()
clean_tools_var=tk.StringVar()

def clear(e):
    check_tools_var.set('')
    convert_tools_var.set('')
    clean_tools_var.set('')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)


#setup GUI widgets
# CHECK ________________________________________________________

# check_files_lb = tk.Label(window, text='Check files',font=("Courier", 12, "bold"))
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,check_files_lb)

check_tools_var.set('')
check_lb = tk.Label(window, text='Check Files')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,check_lb,True)
check_menu = tk.OptionMenu(window,check_tools_var,
                    'Check utf-8 encoding compliance',
                    'Check empty file',
                    'Check sentence length (extracting sentences)',
                    'Language detector',
                    'Predict encoding (via chardet)',
                    'Spelling checker/Unusual words (via nltk)',
                    'Spelling checker (via SpellChecker)')
                    # 'Vocabulary richness (Yule\'s K)',
                    # 'Short words',
                    # 'Vowel words')

check_menu.configure(width=70)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,check_menu)

#setup GUI widgets
# CONVERT ________________________________________________________

# convert_files_lb = tk.Label(window, text='Convert files',font=("Courier", 12, "bold"))
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,convert_files_lb)

convert_tools_var.set('')
convert_lb = tk.Label(window, text='Convert Files')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,convert_lb,True)
convert_menu = tk.OptionMenu(window,convert_tools_var,
                    'Document converter (csv --> txt)',
                    'Document converter (docx --> txt)',
                    'Document converter (pdf --> txt)',
                    'Document converter (rtf --> txt)')

convert_menu.configure(width=70)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,convert_menu)

clean_tools_var.set('')
clean_lb = tk.Label(window, text='Clean Files')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,clean_lb,True)
clean_menu = tk.OptionMenu(window,clean_tools_var,
                    'Change to ASCII non-ASCII apostrophes & quotes and % to percent',
                    'Find & Replace string',
                    'Remove all characters between a set of characters (e.g., []) from text file(s)',
                    'Find & Replace string (via csv file)',
                    'Remove blank lines from text file(s)',
                    'Add full stop (.) at the end of paragraphs without end-of-paragraph punctuation',
                    'Separate titles from documents (newspaper articles)')

clean_menu.configure(width=70)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,clean_menu)


def activate_allOptions(*args):
    global menu_option
    check_menu.configure(state='normal')
    convert_menu.configure(state='normal')
    clean_menu.configure(state='normal')

activate_allOptions()

def getScript(script):
    global menu_option, script_to_run, function_to_run
    script_to_run=''
    function_to_run=''
    if script=='':
        return
    menu_option=script

    #There are TWO values in the dictionary:
    #	1. KEY the label displayed in any of the menus (the key to be used)
    #	val[0] the name of the python script (to be passed to NLP.py) LEAVE BLANK IF OPTION NOT AVAILABLE

    try:
        val=pydict[script]
    except:
        # entry not in dic; programming error; must be added!
        mb.showwarning(title='Warning', message='The selected option ' + script + ' was not found in the Python dictionary in NLP_GUI.py.\n\nPlease, inform the NLP Suite developers of the problem.\n\nSorry!')
        return
    # name of the python script
    if val[0]=='':
        mb.showwarning(title='Warning', message='The selected option ' + script + ' is not available yet.\n\nSorry!')
        return
    script_to_run, function_to_run=val[0].split(".", 1)

    activate_allOptions()
check_tools_var.trace('w',lambda x,y,z: getScript(check_tools_var.get()))
convert_tools_var.trace('w',lambda x,y,z: getScript(convert_tools_var.get()))
clean_tools_var.trace('w',lambda x,y,z: getScript(clean_tools_var.get()))

activate_allOptions()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'File manager':'TIPS_NLP_File manager.pdf','File handling in NLP Suite': "TIPS_NLP_File handling in NLP Suite.pdf",'Filename checker':'TIPS_NLP_Filename checker.pdf','Filename matcher':'TIPS_NLP_Filename matcher.pdf','File classifier (By date)':'TIPS_NLP_File classifier (By date).pdf','File classifier (By NER)':'TIPS_NLP_File classifier (By NER).pdf','File content checker & converter & cleaner':'TIPS_NLP_File checker & converter & cleaner.pdf','Text encoding (utf-8)':'TIPS_NLP_Text encoding (utf-8).pdf','Spelling checker':'TIPS_NLP_Spelling checker.pdf','File merger':'TIPS_NLP_File merger.pdf','File splitter':'TIPS_NLP_File splitter.pdf'}
TIPS_options= 'File content checker & converter & cleaner','File handling in NLP Suite', 'File manager', 'Filename checker', 'Filename matcher', 'File classifier (By date)','File classifier (By NER)','Text encoding (utf-8)','Spelling checker','File merger','File splitter'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_anyFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_anyData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select one of the options available for checking txt files.\n\nWhen a directory is selected as the input option, all files in a directory and its subdirectories can be checked. The script will ask users whether they want to check files in subdirectories." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select one of the options available for converting the file type: from pdf to txt, docx (NOT doc) to txt, or rtf to txt.\n\nThe pdf convert (via the pdfminer package) can also convert column-based pdf files. MAKE SURE TO OCR THE PDF DOCUMENT(S) BEFORE CONVERTING FOR BETTER QUALITY RESULTS.\n\nIn INPUT, when a directory is selected, all files in a directory and its subdirectories can be converted. The script will ask users whether they want to convert files in subdirectories.\n\nIn OUTPUT, the converted file(s) will be placed in the same directory as the input file(s)." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select one of the options available for cleaning a text file:\n\n   find & replace, via a single expression or a set of expressions in a csv file (will replace EXACT expressions - even multiple words but cannot include punctuation);\n   removing blank lines;\n   removing titles in documents (e.g., newspaper articles) and putting them in separate documents (titles and body text).\n\nOf particular IMPORTANTCE is the function that converts non-ASCII apostrophes and quotes and the % symbol.\n   The Windows Word non-ASCII slanted apostrophes and quotes will NOT break any NLP Suite code but will display as weird characters in a csv file (in a Windows machine; not on Mac).\n   The presence in your corpus of % signs is more fatal and will break the Stanford CoreNLP parser since % is interpreted as the start of a special escaped sequence.\n   Slanted apostrophes and quotes will be converted to straight apostrophes and quotes.\n   % signs will be converted to the word \'percent\'." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),increment)

# change the value of the readMe_message
readMe_message="This Python 3 script can check the CONTENT of txt files for\n  utf-8 compliace;\n  spelling.\n\nThe script can also convert a file type from\n  pdf to txt;\n  docx to txt;\n  rtf to txt.\nThe txt type is the only file type NLP tools can process.\n\nIn INPUT the script can take either a single txt file or a directory, processing all txt fles in the directory."
readMe_command = lambda: GUI_IO_util.display_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()

