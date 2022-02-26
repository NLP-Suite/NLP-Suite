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
import IO_user_interface_util
import GUI_util
import Stanford_CoreNLP_coreference_util
import file_splitter_merged_util

# RUN section ______________________________________________________________________________________________________________________________________________________


lemmalib = {}
voLib = {}
notSure = set()
added = set()
file_open = []

caps = "([A-HJ-Z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"


def run(inputFilename, inputDir, outputDir,
        memory_var,
        document_length_var,
        limit_sentence_length_var,
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

    inputFileBase = ""
    inputDirBase = ""


    if  Coref==False and split_coreferenced_files_var==False and continue_manual_Coref_var==False:
        mb.showerror(title='Missing required information', message="No options have been selected.\n\nPlease, tick one of the available options and try again.")
        return False

    # CoRef _____________________________________________________

    if Coref:
        if inputFilename!='':
            inputFileBase = os.path.basename(inputFilename)[0:-4]  # without .txt
            outputCorefedDir = os.path.join(outputDir, "coref_" + inputFileBase)  # + "_CoRefed_files")
            inputDir = ''
        else:
            # processing a directory
            inputFilename = ''
            inputDirBase = os.path.basename(inputDir)
            outputCorefedDir = os.path.join(outputDir, "coref_Dir_" + inputDirBase)

        if not IO_files_util.make_directory(outputCorefedDir):
            return

        # inputFilename and inputDir are the original txt files to be coreferenced
        # 2 items are returned: filename string and true/False for error
        file_open, error_indicator = Stanford_CoreNLP_coreference_util.run(config_filename, inputFilename, inputDir, outputCorefedDir,
                                       True, True,
                                       memory_var,
                                       Manual_Coref_var)
        if error_indicator != 0:
            return

        if inputFilename!='':
            inputFilename = str(file_open)
            inputDir = ''
        else:
            # processing a directory
            inputFilename = ''
            inputDir = outputCorefedDir

        if len(file_open) > 0:
            filesToOpen.extend(file_open)

    # split merged coreferenced file  --------------------------------------------------------------------------------------------------------
    # split <@# #@> --------------------------------------------------------------------------------------

    if split_coreferenced_files_var:
        subDir = ''
        nFiles = 0
        subDir, nFiles = file_splitter_merged_util.run(corefed_txt_file_var.get(),
                                                       '<@#',
                                                       '#@>',
                                                       outputDir)
        mb.showwarning(title='Exported files',
                       message=str(nFiles) + ' split files were created in the subdirectory of the output directory\n\n' + subDir)
        return

    # continue manual resolution --------------------------------------------------------------------------------------------------------

    if continue_manual_Coref_var:
            error = Stanford_CoreNLP_coreference_util.manualCoref(inputFilename, corefed_txt_file, corefed_txt_file)

# the values of the GUI widgets MUST be entered in the command as widget.get() otherwise they will not be updated
run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                 GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 memory_var.get(),
                                 document_length_var.get(),
                                 limit_sentence_length_var.get(),
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
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename,IO_setup_display_brief)


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

CoRef_var = tk.IntVar()
# CoRef_menu_var = tk.StringVar()
memory_var = tk.StringVar()
manual_Coref_var = tk.IntVar()
split_coreferenced_files_var = tk.IntVar()
continue_manual_Coref_var = tk.IntVar()
corefed_txt_file_var= tk.StringVar()

def open_GUI():
    call("python file_checker_converter_cleaner_main.py", shell=True)

pre_processing_button = tk.Button(window, text='Pre-processing tools (file checking & cleaning GUI)',command=open_GUI)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               pre_processing_button)
# memory options
memory_var_lb = tk.Label(window, text='Memory ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               memory_var_lb, True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(6)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 100, y_multiplier_integer,
                                               memory_var, True)

document_length_var_lb = tk.Label(window, text='Document length')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               document_length_var_lb, True)

document_length_var = tk.Scale(window, from_=40000, to=90000, orient=tk.HORIZONTAL)
document_length_var.pack()
document_length_var.set(90000)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+150, y_multiplier_integer,
                                               document_length_var,True)

limit_sentence_length_var_lb = tk.Label(window, text='Limit sentence length')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate() + 370, y_multiplier_integer,
                                               limit_sentence_length_var_lb,True)

limit_sentence_length_var = tk.Scale(window, from_=70, to=400, orient=tk.HORIZONTAL)
limit_sentence_length_var.pack()
limit_sentence_length_var.set(100)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate() + 550, y_multiplier_integer,
                                               limit_sentence_length_var)

CoRef_var.set(0)
CoRef_checkbox = tk.Checkbutton(window, text='Coreference Resolution, PRONOMINAL (via Stanford CoreNLP - Neural Network)',
                                variable=CoRef_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               CoRef_checkbox)

# CoRef_menu_var.set("Neural Network")
# CoRef_menu = tk.OptionMenu(window, CoRef_menu_var, 'Deterministic', 'Statistical', 'Neural Network')
# y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.SVO_2nd_column, y_multiplier_integer, CoRef_menu)
#

manual_Coref_var.set(0)
manual_Coref_checkbox = tk.Checkbutton(window, text='Manually edit coreferenced document ', variable=manual_Coref_var,
                                       onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate(), y_multiplier_integer,
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
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,corefed_txt_file_button,True)

#setup a button to open Windows Explorer on the selected input directory
# current_y_multiplier_integer2=y_multiplier_integer-1
# openInputFile_button  = tk.Button(window, width=3, state='disabled', text='', command=lambda: IO_files_util.openFile(window, csv_file_var.get()))
openInputFile_button  = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, corefed_txt_file_var.get()))
openInputFile_button.place(x=GUI_IO_util.get_open_file_directory_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

corefed_txt_file=tk.Entry(window, width=130,textvariable=corefed_txt_file_var)
corefed_txt_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,corefed_txt_file)

split_coreferenced_files_var.set(0)
split_coreferenced_files_checkbox = tk.Checkbutton(window, text='Split merged coreferenced file (with filenames embedded in <@# #@>) for manual editing to fit memory', variable=split_coreferenced_files_var,
                                       onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate(), y_multiplier_integer,
                                               split_coreferenced_files_checkbox)
split_coreferenced_files_checkbox.config(state='disabled')

continue_manual_Coref_var.set(0)
continue_manual_Coref_var_checkbox = tk.Checkbutton(window, text='Continue manual coreferencing of previously coreferenced document', variable=continue_manual_Coref_var,
                                       onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate(), y_multiplier_integer,
                                               continue_manual_Coref_var_checkbox)

continue_manual_Coref_var_checkbox.configure(state='disabled')


def activateCoRefOptions(*args):
    if CoRef_var.get() == 1:
        memory_var.configure(state='normal')
        if input_main_dir_path.get()!='':
            manual_Coref_checkbox.configure(state='disabled')
            manual_Coref_var.set(0)
        else:
            manual_Coref_checkbox.configure(state='normal')
            manual_Coref_var.set(1)
    else:
        manual_Coref_checkbox.configure(state='disabled')
        manual_Coref_var.set(0)
CoRef_var.trace('w', activateCoRefOptions)

activateCoRefOptions()


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

TIPS_lookup = {'Stanford CoreNLP coreference resolution': "TIPS_NLP_Stanford CoreNLP coreference resolution.pdf",
               'utf-8 encoding': 'TIPS_NLP_Text encoding.pdf',
               'Stanford CoreNLP memory issues':'TIPS_NLP_Stanford CoreNLP memory issues.pdf'}
TIPS_options = 'Stanford CoreNLP coreference resolution', 'utf-8 encoding', 'Stanford CoreNLP memory issues'


# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, basic_y_coordinate, y_step):
    if IO_setup_display_brief==False:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      "Please, select either a txt file to be analyzed and extract SVO triplets from it, or a csv file of previously extracted SVOs if all you want to do is to visualize the previously computed results." + GUI_IO_util.msg_openFile)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step, "Help",
                                      GUI_IO_util.msg_corpusData)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 2, "Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

#    top.title("Comparing result from {0} (Edit text on the right hand side and Save) - in BLUE pronouns not done; in YELLOW & RED pronouns done".format('Neural Network'))

    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+1), "Help",
                                  "Please, click on the 'Pre-processing tools' button to open the GUI where you will be able to perform a variety of\n   file checking options (e.g., utf-8 encoding compliance of your corpus or sentence length);\n   file cleaning options (e.g., convert non-ASCII apostrophes & quotes and % to percent).\n\nNon utf-8 compliant texts are likely to lead to code breakdown in various algorithms.\n\nASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n\n% signs will lead to code breakdon of Stanford CoreNLP.\n\nSentences without an end-of-sentence marker (. ! ?) in Stanford CoreNLP will be processed together with the next sentence, potentially leading to very long sentences.\n\nSentences longer than 70 or 100 words may pose problems to Stanford CoreNLP (the average sentence length of modern English is 20 words). Please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf."+ GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+2), "Help",
                                  "The Stanford CoreNLP performance is affected by various issues: memory size of your computer, document size, sentence length\n\nPlease, select the memory size Stanford CoreNLP will use. Default = 4. Lower this value if CoreNLP runs out of resources.\n   For CoreNLP co-reference resolution you may wish to increase the value when processing larger files (compatibly with the memory size of your machine).\n\nLonger documents affect performace. Stanford CoreNLP has a limit of 100,000 characters processed (the NLP Suite limits this to 90,000 as default). If you run into performance issues you may wish to further reduce the document size.\n\nSentence length also affect performance. The Stanford CoreNLP recommendation is to limit sentence length to 70 or 100 words.\n   You may wish to compute the sentence length of your document(s) so that perhaps you can edit the longer sentences.\n\nOn these issues, please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf."+ GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+3), "Help",
                                  "Please, tick the checkbox if you wish to run the Stanford CoreNLP neural network annotator for pronominal coreference resolution.\n\nPlease, BE PATIENT. Depending upon number and size of processed files, the algorithm can be very slow.\n\nIn INPUT the algorithm expects a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithm will produce txt-format copies of the same input txt files but co-referenced." + GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+4), "Help",
                                  "Please, tick the checkbox if you wish to resolve manually cases of unresolved or wrongly resolved coreferences.\n\nThe option is not available with a directory in input.\n\nMANUAL EDITING REQUIRES A LOT OF MEMORY SINCE BOTH ORIGINAL AND CO-REFERENCED FILE ARE BROUGHT IN MEMORY. DEPENDING UPON FILE SIZES, YOU MAY NOT HAVE ENOUGH MEMORY FOR THIS STEP.\n\nIn output, the manual coreference algorithm will display the original text on the left, highlighting in BLUE the pronouns not coreferenced by CoreNLP, and in YELLOW the coreferenced pronouns, and the coreferenced text on the right, highlighting in the RED the coreferenced pronoun." + GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+5), "Help",
                                  "Please, use the 'Select INPUT corefed TXT file' button to select a previosuly coreferenced file for further manual coreference.\n\nYou can use the little square widget to the right of the button to open the selected input coref txt file for inspection."+ GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+6), "Help",
                                  "Please, tick the checkbox if you wish to automatically split files that may be too long to bring in memory for original vs. coreferenced files.\n\nIn INPUT the algorithm expects the coreferenced merged file (selected via the button 'Select INPUT corefed txt file').\n\nIn OUTPUT the algorithm will save the split individual files into a subfolder of the the output directory."+ GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+7), "Help",
                                  "Please, tick the checkboxes if you wish to run manually corefence a previously coreferenced file.\n\nIn INPUT the algorithm expects the original txt file(s) (selected in either the 'Default I/O configuration' or the 'Alternative I/O configuration') and the previously coreferenced file (selected via the button 'Select INPUT corefed txt file').\n\nIn OUTPUT the algorithm will save the same newly manually coreferenced file."+ GUI_IO_util.msg_Esc)

help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), GUI_IO_util.get_basic_y_coordinate(),
             GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message = "This set of Python 3 scripts implement a Stanford CoreNLP neural network approach to coreference resolution for three different types of PRONOUNS:\n   nominative: I, you, he/she, it, we, they;\n   possessive: my, mine, our(s), his/her(s), their, its, yours;\n   objective: me, you, him, her, it, them.\n\nThe NLP Suite implements only PRONOMINAL coreference but NOT NOMINAL.\n\nIn INPUT the scripts expect either a single txt file or a set of txt files in a directory.\n\nIn OUTPUT, the scripts will produce a coreferenced txt file. If manual edit is selected, the script will also display a split-screen file for manual editing. On the left-hand side, pronouns cross-referenced by CoreNLP are tagged in YELLOW; pronouns NOT cross-referenced by CoreNLP are tagged in BLUE. On the right-hand side, pronouns cross-referenced by CoreNLP are tagged in RED, with the pronouns replaced by the referenced nouns.\n\nThe user can edit any unresolved or wrongly resolved pronominal cases directly on the right panel, as if it were any text editor and then save the changes."
readMe_command = lambda: GUI_IO_util.readme_button(window, GUI_IO_util.get_help_button_x_coordinate(),
                                                   GUI_IO_util.get_basic_y_coordinate(), "Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief,'Stanford_CoreNLP_coreference_main')

GUI_util.window.mainloop()
