#written by Roberto Franzosi October 2021

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "Stanford_CoreNLP_coreference_main",
                                          ['subprocess', 'os', 'tkinter', 'csv']) == False:
    sys.exit(0)

from collections import defaultdict
import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

# to install stanfordnlp, first install
#   pip3 install torch===1.4.0 torchvision===0.5.0 -f https://download.pytorch.org/whl/torch_stable.html
#   pip3 install stanfordnlp
# import stanfordnlp


import GUI_IO_util
import IO_files_util
import GUI_util
import Stanford_CoreNLP_coreference_util
import file_splitter_merged_txt_util
import reminders_util
import config_util

# RUN section ______________________________________________________________________________________________________________________________________________________

files_to_open = []

def run(inputFilename, inputDir, outputDir,
        openOutputFiles, createCharts, chartPackage,
        Coref,
        Manual_Coref_var,
        split_coreferenced_files_var,
        continue_manual_Coref_var,
        corefed_txt_file):

    # pull the widget names from the GUI since the scripts change the IO values
    inputFilename = GUI_util.inputFilename.get()
    inputDir = GUI_util.input_main_dir_path.get()
    outputDir = GUI_util.output_dir_path.get()

    outputCorefedDir = ''

    filesToOpen = []

    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]

    # get the date options from filename
    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    extract_date_from_filename_var, date_format_var, date_separator_var, date_position_var = config_util.get_date_options(
        config_filename, config_input_output_numeric_options)
    extract_date_from_text_var = 0

    if package_display_area_value == '':
        mb.showwarning(title='No setup for NLP package and language',
                       message="The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again.")
        return

    inputFileBase = ""
    inputDirBase = ""


    if  Coref==False and split_coreferenced_files_var==False and continue_manual_Coref_var==False:
        mb.showerror(title='Missing required information', message="No options have been selected.\n\nPlease, tick one of the available options and try again.")
        return False

    # CoRef _____________________________________________________

    if Coref:
        if language_var!='English' and language_var!='Chinese':
            mb.showwarning(title='Language',message='The Stanford CoreNLP coreference resolution annotator is only available for English and Chinese.')
            return

        label = 'CoreNLP_coref'
        if inputFilename != '':
            inputBaseName = os.path.basename(inputFilename)[0:-4]  # without .txt
        else:
            inputBaseName = os.path.basename(inputDir)
        outputCorefDir = os.path.join(outputDir, label + "_" + inputBaseName)

        # create a subdirectory of the output directory
        outputCorefedDir = IO_files_util.make_output_subdirectory('', '', outputCorefDir, '',
                                                            silent=False)
        if outputCorefedDir == '':
            return

        # inputFilename and inputDir are the original txt files to be coreferenced
        # 2 items are returned: filename string and true/False for error
        files_to_open, error_indicator = Stanford_CoreNLP_coreference_util.run(config_filename, inputFilename, inputDir,
                                       outputCorefedDir,
                                       openOutputFiles, createCharts, chartPackage,
                                       language_var,
                                       memory_var,
                                       Manual_Coref_var)
        if error_indicator != 0:
            return

        if inputFilename!='':
            inputFilename = str(files_to_open)
            inputDir = ''
        else:
            # processing a directory
            inputFilename = ''
            inputDir = outputCorefedDir

        if len(files_to_open) > 0:
            # mb.showwarning("Output directory",
            #                "All output files have been saved to a subdirectory of the selected output directory at\n\n" + str(
            #                    outputCorefedDir))
            filesToOpen.append(files_to_open)

    # split merged coreferenced file  --------------------------------------------------------------------------------------------------------
    # split <@# #@> --------------------------------------------------------------------------------------

    if split_coreferenced_files_var:
        subDir = ''
        nFiles = 0
        subDir, nFiles = file_splitter_merged_txt_util.run(corefed_txt_file_var.get(),
                                                       '<@#',
                                                       '#@>',
                                                       outputDir)
        mb.showwarning(title='Exported files',
                       message=str(nFiles) + ' split files were created in the subdirectory of the output directory\n\n' + subDir)
        return

    # continue manual resolution --------------------------------------------------------------------------------------------------------

    if continue_manual_Coref_var:
            error = Stanford_CoreNLP_coreference_util.manualCoref(inputFilename, corefed_txt_file, corefed_txt_file)

    if openOutputFiles == True and len(filesToOpen) > 0:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

# the values of the GUI widgets MUST be entered in the command as widget.get() otherwise they will not be updated
run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                 GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.create_chart_output_checkbox.get(),
                                 GUI_util.charts_dropdown_field.get(),
                                 CoRef_var.get(),
                                 manual_Coref_var.get(),
                                 split_coreferenced_files_var.get(),
                                 continue_manual_Coref_var.get(),
                                 corefed_txt_file_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=470, # height at brief display
                             GUI_height_full=550, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display


GUI_label = 'Graphical User Interface (GUI) for Coreference PRONOMINAL Resolution (via CoreNLP) and Manual Editing'
config_filename = 'coref_config.csv'
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
config_input_output_numeric_options= [6,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

# location of this src python file
scriptPath = GUI_IO_util.scriptPath
# one folder UP, the NLP folder
NLPPath = GUI_IO_util.NLPPath
# subdirectory of script directory where config files are saved
# libPath = GUI_IO_util.libPath +os.sep+'wordLists'

window = GUI_util.window
# config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
# config_filename = GUI_util.config_filename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename,IO_setup_display_brief)

inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path

def clear(e):
    CoRef_var.set(0)
    CoRef_checkbox.configure(state='normal')
    manual_Coref_var.set(0)
    manual_Coref_checkbox.configure(state='disabled')
    corefed_txt_file_var.set('')
    continue_manual_Coref_var.set(0)
    split_coreferenced_files_var.set(0)
    continue_manual_Coref_var_checkbox.configure(state='disabled')
    split_coreferenced_files_checkbox.configure(state='disabled')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

language_var = tk.StringVar()
CoRef_var = tk.IntVar()
manual_Coref_var = tk.IntVar()
split_coreferenced_files_var = tk.IntVar()
continue_manual_Coref_var = tk.IntVar()
corefed_txt_file_var= tk.StringVar()

def open_GUI():
    call("python file_checker_converter_cleaner_main.py", shell=True)

pre_processing_button = tk.Button(window, text='Pre-processing tools (file checking & cleaning GUI)',command=open_GUI)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               pre_processing_button)

CoRef_var.set(1)
CoRef_checkbox = tk.Checkbutton(window, text='Coreference Resolution, PRONOMINAL (via Stanford CoreNLP - Neural Network)',
                                variable=CoRef_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               CoRef_checkbox)

# CoRef_menu_var.set("Neural Network")
# CoRef_menu = tk.OptionMenu(window, CoRef_menu_var, 'Deterministic', 'Statistical', 'Neural Network')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.SVO_2nd_column, y_multiplier_integer, CoRef_menu)
#

manual_Coref_var.set(0)
manual_Coref_checkbox = tk.Checkbutton(window, text='Manually edit coreferenced document ', variable=manual_Coref_var,
                                       onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_indented_coordinate(), y_multiplier_integer,
                                               manual_Coref_checkbox)

def get_corefed_txt_file(window,title,fileType,annotate):
    if corefed_txt_file!='':
        initialFolder=os.path.dirname(os.path.abspath(corefed_txt_file_var.get()))
    else:
        initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)

    if len(filePath)>0:
        corefed_txt_file_var.set(filePath)
        split_coreferenced_files_checkbox.configure(state='normal')
        continue_manual_Coref_var_checkbox.configure(state='normal')
    else:
        split_coreferenced_files_checkbox.configure(state='disabled')
        continue_manual_Coref_var_checkbox.configure(state='disabled')
    return filePath

corefed_txt_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT corefed TXT file',command=lambda: get_corefed_txt_file(window,'Select INPUT csv file', [("coreferenced file", "*.txt")],True))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                   corefed_txt_file_button,
                                   True, False, True, False, 90, GUI_IO_util.get_labels_x_coordinate(),
                                   "Click on the button to select a previosuly coreferenced txt file for further manual coreference")

#setup a button to open Windows Explorer on the selected input directory
openInputFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, corefed_txt_file_var.get()))
# the button widget has hover-over effects (no_hover_over_widget=False) and the info displayed is in text_info
# the two x-coordinate and x-coordinate_hover_over must have the same values
y_multiplier_integer = GUI_IO_util.placeWidget(window,
    GUI_IO_util.get_open_file_directory_coordinate(),
    y_multiplier_integer,
    openInputFile_button, True, False, True, False, 90, GUI_IO_util.get_open_file_directory_coordinate(), "Open coreferenced txt file")

corefed_txt_file=tk.Entry(window, width=130,textvariable=corefed_txt_file_var)
corefed_txt_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,corefed_txt_file)

split_coreferenced_files_var.set(0)
split_coreferenced_files_checkbox = tk.Checkbutton(window, text='Split merged coreferenced file (with filenames embedded in <@# #@>) for manual editing to fit memory', variable=split_coreferenced_files_var,
                                       onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_indented_coordinate(), y_multiplier_integer,
                                               split_coreferenced_files_checkbox)
split_coreferenced_files_checkbox.config(state='disabled')

continue_manual_Coref_var.set(0)
continue_manual_Coref_var_checkbox = tk.Checkbutton(window, text='Continue manual coreferencing of previously coreferenced document', variable=continue_manual_Coref_var,
                                       onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_indented_coordinate(), y_multiplier_integer,
                                               continue_manual_Coref_var_checkbox)

continue_manual_Coref_var_checkbox.configure(state='disabled')


def activateCoRefOptions(*args):

    if CoRef_var.get() == 1:
        if input_main_dir_path.get()!='':
            reminders_util.checkReminder(config_filename, reminders_util.title_options_CoreNLP_coref,
                                         reminders_util.message_CoreNLP_coref, True)
            manual_Coref_checkbox.configure(state='disabled')
            manual_Coref_var.set(0)
        else:
            manual_Coref_checkbox.configure(state='normal')
            manual_Coref_var.set(1)
    else:
        manual_Coref_checkbox.configure(state='disabled')
        manual_Coref_var.set(0)
CoRef_var.trace('w', activateCoRefOptions)

def changed_filename(tracedInputFile):
    activateCoRefOptions()
GUI_util.input_main_dir_path.trace('w', lambda x, y, z: changed_filename(GUI_util.input_main_dir_path.get()))
# must trace on input_main_dir_path, rather than inputFilename,
#   because inputFilename is set BEFORE input_main_dir_path in GUI_util and it is not up-to-date

# activateCoRefOptions()


# def activateTxtFileOptions(*args):
#     if corefed_txt_file.get()!='':
#         split_coreferenced_files_checkbox.configure(state='normal')
#         continue_manual_Coref_var_checkbox.configure(state='normal')
#     else:
#         split_coreferenced_files_checkbox.configure(state='disabled')
#         continue_manual_Coref_var_checkbox.configure(state='disabled')
# corefed_txt_file_var.trace('w', activateTxtFileOptions)
#
# activateTxtFileOptions()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Stanford CoreNLP supported languages': 'TIPS_NLP_Stanford CoreNLP supported languages.pdf',
               'Stanford CoreNLP performance & accuracy': 'TIPS_NLP_Stanford CoreNLP performance and accuracy.pdf',
               'Stanford CoreNLP coreference resolution': "TIPS_NLP_Stanford CoreNLP coreference resolution.pdf",
               'utf-8 encoding': 'TIPS_NLP_Text encoding.pdf',
               'Stanford CoreNLP memory issues':'TIPS_NLP_Stanford CoreNLP memory issues.pdf',
               'csv files - Problems & solutions': 'TIPS_NLP_csv files - Problems & solutions.pdf'}

TIPS_options = 'Stanford CoreNLP coreference resolution','Stanford CoreNLP supported languages','Stanford CoreNLP performance & accuracy', 'utf-8 encoding', 'Stanford CoreNLP memory issues', 'csv files - Problems & solutions'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate,y_multiplier_integer):
    if IO_setup_display_brief==False:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      "Please, select either a txt file to be analyzed and extract SVO triplets from it, or a csv file of previously extracted SVOs if all you want to do is to visualize the previously computed results." + GUI_IO_util.msg_openFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

#    top.title("Comparing result from {0} (Edit text on the right hand side and Save) - in BLUE pronouns not done; in YELLOW & RED pronouns done".format('Neural Network'))

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, click on the 'Pre-processing tools' button to open the GUI where you will be able to perform a variety of\n   file checking options (e.g., utf-8 encoding compliance of your corpus or sentence length);\n   file cleaning options (e.g., convert non-ASCII apostrophes & quotes and % to percent).\n\nNon utf-8 compliant texts are likely to lead to code breakdown in various algorithms.\n\nASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n\n% signs will lead to code breakdon of Stanford CoreNLP.\n\nSentences without an end-of-sentence marker (. ! ?) in Stanford CoreNLP will be processed together with the next sentence, potentially leading to very long sentences.\n\nSentences longer than 70 or 100 words may pose problems to Stanford CoreNLP (the average sentence length of modern English is 20 words). Please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf."+ GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox to run the Stanford CoreNLP coreference resolution annotator using the Neural Network approach.\n\nOnly pronominal, and not nominal, coreference resolution is implemented for four different types of PRONOUNS:\n   nominative: I, you, he/she, it, we, they;\n   possessive: my, mine, our(s), his/her(s), their, its, yours;\n   objective: me, you, him, her, it, them;\n   reflexive: myself, yourself, himself, herself, oneself, itself, ourselves, yourselves, themselves.\n\nPlease, BE PATIENT. Depending upon size and number of documents to be coreferenced the algorithm may take a long a time.\n\nIn INPUT the algorithm expects a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithm will produce txt-format copies of the same input txt files but co-referenced.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to resolve manually cases of unresolved or wrongly resolved coreferences.\n\nThe option is not available with a directory in input.\n\nMANUAL EDITING REQUIRES A LOT OF MEMORY SINCE BOTH ORIGINAL AND CO-REFERENCED FILE ARE BROUGHT IN MEMORY. DEPENDING UPON FILE SIZES, YOU MAY NOT HAVE ENOUGH MEMORY FOR THIS STEP.\n\nIn output, the manual coreference algorithm will display the original text on the left, highlighting in BLUE the pronouns not coreferenced by CoreNLP, and in YELLOW the coreferenced pronouns, and the coreferenced text on the right, highlighting in the RED the coreferenced pronoun." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, use the 'Select INPUT corefed TXT file' button to select a previosuly coreferenced file for further manual coreference.\n\nYou can use the little square widget to the right of the button to open the selected input coref txt file for inspection."+ GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to automatically split files that may be too long to bring in memory for original vs. coreferenced files.\n\nIn INPUT the algorithm expects the coreferenced merged file (selected via the button 'Select INPUT corefed txt file').\n\nIn OUTPUT the algorithm will save the split individual files into a subfolder of the the output directory."+ GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkboxes if you wish to run manually corefence a previously coreferenced file.\n\nIn INPUT the algorithm expects the original txt file(s) (selected in either the 'Default I/O configuration' or the 'Alternative I/O configuration') and the previously coreferenced file (selected via the button 'Select INPUT corefed txt file').\n\nIn OUTPUT the algorithm will save the same newly manually coreferenced file."+ GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), 0)

# change the value of the readMe_message
readMe_message = "This set of Python 3 scripts implement a Stanford CoreNLP neural network approach to coreference resolution for four different types of PRONOUNS:\n   nominative: I, you, he/she, it, we, they;\n   possessive: my, mine, our(s), his/her(s), their, its, yours;\n   objective: me, you, him, her, it, them;\n   reflexive: myself, yourself, himself, herself, oneself, itself, ourselves, yourselves, themselves.\n\nThe NLP Suite implements only PRONOMINAL coreference but NOT NOMINAL.\n\nIn INPUT the scripts expect either a single txt file or a set of txt files in a directory.\n\nIn OUTPUT, the scripts will produce a coreferenced txt file. If manual edit is selected, the script will also display a split-screen file for manual editing. On the left-hand side, pronouns cross-referenced by CoreNLP are tagged in YELLOW; pronouns NOT cross-referenced by CoreNLP are tagged in BLUE. On the right-hand side, pronouns cross-referenced by CoreNLP are tagged in RED, with the pronouns replaced by the referenced nouns.\n\nThe user can edit any unresolved or wrongly resolved pronominal cases directly on the right panel, as if it were any text editor and then save the changes."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief,'Stanford_CoreNLP_coreference_main')

if input_main_dir_path.get()!='':
    reminders_util.checkReminder(config_filename, reminders_util.title_options_CoreNLP_coref,
                                 reminders_util.message_CoreNLP_coref, True)
reminders_util.checkReminder(config_filename, reminders_util.title_options_only_CoreNLP_coref,
                             reminders_util.message_only_CoreNLP_coref, True)

activateCoRefOptions()

GUI_util.window.mainloop()
