# written by Roberto Franzosi (Spring/summer 2020)
import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"sentence_analysis_main.py",['tkinter','subprocess','ast'])==False:
    sys.exit(0)

import tkinter as tk
import tkinter.messagebox as mb
import subprocess

import GUI_IO_util
import IO_files_util
import sentence_analysis_util
import IO_user_interface_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, input_main_dir_path, output_dir_path,openOutputFiles,createExcelCharts,
    visualize_bySentenceIndex_var,
    script_to_run,
    IO_values,
    sentence_complexity_var,
    text_readability_var,
    visualize_sentence_structure_var,
    extract_sentences_var,
    search_words_var):

    filesToOpen = []  # Store all files that are to be opened once finished

    if (visualize_bySentenceIndex_var==False and
        sentence_complexity_var==False and
        text_readability_var==False and
        visualize_sentence_structure_var==False and
        extract_sentences_var==False):
            mb.showwarning(title='No options selected', message='No options have been selected.\n\nPlease, select an option and try again.')
            return

    if visualize_bySentenceIndex_var:
        IO_files_util.runScript_fromMenu_option(script_to_run, IO_values,
                                                inputFilename, input_main_dir_path,output_dir_path,
                                                openOutputFiles, createExcelCharts)
        return

    if sentence_complexity_var==True:
        if IO_libraries_util.inputProgramFileCheck('statistics_txt_util.py')==False:
            return
        filesToOpen=sentence_analysis_util.sentence_complexity(GUI_util.window,inputFilename, input_main_dir_path, output_dir_path,openOutputFiles,createExcelCharts)
        if filesToOpen==None:
            return

    if text_readability_var==True:
        if IO_libraries_util.inputProgramFileCheck('statistics_txt_util.py')==False:
            return
        sentence_analysis_util.sentence_text_readability(GUI_util.window,inputFilename, input_main_dir_path, output_dir_path,openOutputFiles,createExcelCharts)

    if visualize_sentence_structure_var==True:
        if IO_libraries_util.inputProgramFileCheck('DependenSee.Jar')==False:
            return
        errorFound, error_code, system_output = IO_libraries_util.check_java_installation('Sentence structure visualization')
        if errorFound:
            return
        if inputFilename=='' and inputFilename.strip()[-4:]!='.txt':
            mb.showwarning(title='Input file error', message='The Sentence tree viewer script requires a single txt file in input.\n\nPlease, select a txt file and try again.')
            return
        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running Sentence visualization: Dependency tree viewer (png graphs) at', True, '\n\nYou can follow Sentence Complexity in command line.')
        subprocess.call(['java', '-jar', 'DependenSee.Jar', inputFilename, output_dir_path])
        mb.showwarning(title='Analysis end',message='Finished running the Dependency tree viewer (png graphs).\n\nMake sure to open the png files in output, one graph for each sentence.')

    if extract_sentences_var:
        if search_words_var=='':
            mb.showwarning(title='No search words entered', message='You have selected to extract sentences from input file(s). You MUST enter specific words to be used to extract the sentences from input.\n\nPlease enter the word(s) and try again.')
            return

        sentence_analysis_util.extract_sentences(inputFilename, input_main_dir_path, output_dir_path, search_words_var)

    IO_files_util.runScript_fromMenu_option(script_to_run,IO_values,inputFilename,input_main_dir_path, output_dir_path, openOutputFiles,createExcelCharts)

    if openOutputFiles == 1:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_Excel_chart_output_checkbox.get(),
                                visualize_bySentenceIndex_var.get(),
                                script_to_run,
                                IO_values,
                                sentence_complexity_var.get(),
                                text_readability_var.get(),
                                visualize_sentence_structure_var.get(),
                                extract_sentences_var.get(),
                                search_words_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_width=1100
GUI_height=520 # height of GUI with full I/O display

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

GUI_label='Graphical User Interface (GUI) for Sentence Analysis'
config_filename='sentence-analysis-config.txt'
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
# config_option=[0,4,0,0,0,1]
config_option=[0,6,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename,config_option)

window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_options,config_filename,IO_setup_display_brief)

# GUI CHANGES cut/paste special GUI widgets from GUI_util

script_to_run=''
IO_values=''

pydict = {}

#if you want to get the value, just call val=pydict[input] where the input is the
#input from the table
#val[0] will be the py file you want and val[1] will be the availability with 1 to be available and 0 to be unexisting
#There are FIVE values in the dictionary:
#	1. the label displayed in any of the menus (the key to be used)
#	2. the name of the python script (to be passed to NLP.py) LEAVE BLANK IF OPTION NOT AVAILABLE
#	3. 0 False 1 True whether the script has a GUI that will check IO items or we need to check IO items here
#	4. 1, 2, 3 (to be chcked when the script has no GUI )
#		1 requires input Dir
#		2 requires input file
#		3 requires either Dir or file
#	5. file extension
# FOR CONVENIENCE, THE DIC ENTRIES ARE IN KEY ALPHABETICAL ORDER

# set all values to null when using a web-based program, as in:
#	pydict["Gender guesser"] = ["Gender guesser", 0, 0,'']

# set 2 values to null when option is not available:
#	pydict["Male & female names"] = ["", 0]

# when not available
# pydict["Sentence visualization: Dynamic sentence network viewer (Gephi graphs)"] = ["", 0] # not available

# when using a function within a script
# pydict["Dictionary items by sentence index"] = ["dictionary_items_sentenceID_util.dictionary_items_bySentenceID", 0, 3, 'txt']

pydict["Clause analysis by sentence index (via CoNLL)"] = ["CoNLL_table_analyzer_main.py", 1]
pydict["Noun analysis by sentence index (via CoNLL)"] = ["CoNLL_table_analyzer_main.py", 1]
pydict["Verb analysis by sentence index (via CoNLL)"] = ["CoNLL_table_analyzer_main.py", 1]
pydict["Function words analysis by sentence index (via CoNLL)"] = ["CoNLL_table_analyzer_main.py", 1]
pydict["Concreteness analysis by sentence index"] = ["sentiment_concreteness_analysis_main.py", 1]
pydict["Dictionary items by sentence index"] = ["dictionary_items_sentenceID_util.dictionary_items_bySentenceID", 0, 3, 'txt']
pydict["N-grams (word & character) by sentence index"] = ["NGrams_CoOccurrences_Viewer_main.py", 1]
pydict["Search words/collocations by sentence index"] = ["file_finder_byWord_main.py",1]
pydict["Sentence complexity by sentence index"] = ["sentence_analysis_util.sentence_complexity", 0, 3, 'txt']
pydict["Sentence/text readability by sentence index (via textstat)"] = ["sentence_analysis_util.sentence_text_readability", 0, 3, 'txt']
pydict["Sentiment analysis by sentence index"] = ["sentiment_concreteness_analysis_main.py", 1]
pydict["Words/collocations by sentence index"] = ["", 0]
pydict["WordNet categories by sentence index"] = ["WordNet_main.py", 1]

visualize_bySentenceIndex_var=tk.IntVar()
visualize_bySentenceIndex_options_var=tk.StringVar()
visualize_sentence_structure_var=tk.IntVar()
sentence_complexity_var=tk.IntVar()
text_readability_var=tk.IntVar()
extract_sentences_var=tk.IntVar()
search_words_var=tk.StringVar()

def clear(e):
	visualize_bySentenceIndex_var.set(0)
	visualize_sentence_structure_var.set(0)
	extract_sentences_var.set(0)
	visualize_bySentenceIndex_options_var.set('')
	search_words_var.set('')
	GUI_util.clear("Escape")
window.bind("<Escape>", clear)

visualize_bySentenceIndex_var.set(0)
visualize_bySentenceIndex_options_var.set('')
visualize_bySentenceIndex_checkbox = tk.Checkbutton(window, text='Visualize text features by sentence index (Excel line plots)', variable=visualize_bySentenceIndex_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,visualize_bySentenceIndex_checkbox,True)
visualize_bySentenceIndex_lb = tk.Label(window, text='Select visualization option')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+350,y_multiplier_integer,visualize_bySentenceIndex_lb,True)
visualize_bySentenceIndex_menu = tk.OptionMenu(window,visualize_bySentenceIndex_options_var,'*','Clause analysis by sentence index (via CoNLL)','Noun analysis by sentence index (via CoNLL)','Verb analysis by sentence index (via CoNLL)','Function words analysis by sentence index (via CoNLL)','Sentence complexity by sentence index','Sentence/text readability by sentence index (via textstat)','N-grams (word & character) by sentence index','Hapax legomena (once-occurring words) by sentence index','Unusual words (via NLTK) by sentence index','Short words by sentence index','Vowel words by sentence index','Annotated gender names by sentence index', 'Annotated words (DBpedia, YAGO, dictionary) by sentence index','Sentiment analysis by sentence index','Concreteness analysis by sentence index', 'Words/collocations by sentence index','WordNet categories by sentence index','Time by sentence index','Location by sentence index')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+500, y_multiplier_integer,visualize_bySentenceIndex_menu)

sentence_complexity_var.set(0)
sentence_complexity_checkbox = tk.Checkbutton(window, text='Sentence complexity', variable=sentence_complexity_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,sentence_complexity_checkbox)

text_readability_var.set(0)
text_readability_checkbox = tk.Checkbutton(window, text='Sentence/text readability (via textstat)', variable=text_readability_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,text_readability_checkbox)

def getScript(script):
	global script_to_run, IO_values
	script_to_run = ''
	IO_values = ''
	script_to_run, IO_values=IO_files_util.getScript(pydict,script)

visualize_bySentenceIndex_options_var.trace('w', lambda x,y,z: getScript(visualize_bySentenceIndex_options_var.get()))

visualize_sentence_structure_var.set(0)
visualize_sentence_structure_checkbox = tk.Checkbutton(window, text='Visualize sentence structure (via dependency tree)', variable=visualize_sentence_structure_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,visualize_sentence_structure_checkbox)

extract_sentences_var.set(0)
extract_sentences_checkbox = tk.Checkbutton(window, text='Extract sentences from corpus', variable=extract_sentences_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,extract_sentences_checkbox,True)

search_words_var.set('')
search_words_lb = tk.Label(window, text='Word(s) in sentence')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+200,y_multiplier_integer,search_words_lb,True)
search_words_entry = tk.Entry(window, textvariable=search_words_var)
search_words_entry.configure(width=100)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+340,y_multiplier_integer,search_words_entry)

def activate_visualize_bySentenceIndex_options(*args):
    if visualize_bySentenceIndex_var.get()==False:
        visualize_bySentenceIndex_menu.configure(state='disabled')
    else:
        visualize_bySentenceIndex_menu.configure(state='normal')
visualize_bySentenceIndex_var.trace('w',activate_visualize_bySentenceIndex_options)

activate_visualize_bySentenceIndex_options()

def activate_extract_sentences(*args):
    if extract_sentences_var.get()==False:
        search_words_entry.configure(state='disabled')
    else:
        search_words_entry.configure(state='normal')
extract_sentences_var.trace('w',activate_extract_sentences)

activate_extract_sentences()


TIPS_lookup = {'Clause analysis':'TIPS_NLP_Clause Analysis.pdf','Sentence complexity':'TIPS_NLP_Sentence complexity.pdf','Text readability':'TIPS_NLP_Text readability.pdf','CoNLL Table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf", 'POSTAG (Part of Speech Tags)': "TIPS_NLP_POSTAG (Part of Speech Tags) Stanford CoreNLP.pdf", 'DEPREL (Stanford Dependency Relations)': "TIPS_NLP_DEPREL (Dependency Relations) Stanford CoreNLP.pdf", 'NLP Searches': "TIPS_NLP_NLP Searches.pdf",'N-Grams (word & character)':"TIPS_NLP_Ngrams (word & character).pdf",'NLP Ngram and Word Co-Occurrence VIEWER':"TIPS_NLP_Ngram and Word Co-Occurrence VIEWER.pdf",'Google Ngram Viewer':'TIPS_NLP_Ngram Google Ngram Viewer.pdf'}
TIPS_options='Clause analysis', 'Sentence complexity', 'Text readability','CoNLL Table', 'POSTAG (Part of Speech Tags)', 'DEPREL (Stanford Dependency Relations)','NLP Searches','N-Grams (word & character)','NLP Ngram and Word Co-Occurrence VIEWER','Google Ngram Viewer'
# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    if not IO_setup_display_brief:
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",GUI_IO_util.msg_csv_txtFile)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_corpusData)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help",GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+1),"Help",'Please, tick the checkbox if you wish to visualize in an Excel line chart various text characteristics by sentence index.\n\nThe chart will give you a sense of the tempo of the text from one sentence to the next.\n\nOnce you have ticked the checkbox you will need to select one of the many visualization options available.\n\nIn INPUT, the script expects a CoNLL table generated by the Stanford_CoreNLP.py script (the parser option).'+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+2),"Help",'Please, tick the checkbox if you wish to run the Java Sentence_Complexity.jar script to provide different measures of sentence complexity: Yngve Depth, Frazer Depth, and Frazer Sum. These measures are closely associated to the sentence clause structure.\n\nThe Frazier and Yngve scores are very similar, with one key difference: while the Frazier score measures the depth of a syntactic tree, the Yngve score measures the breadth of the tree.\n\nIn INPUT, the script expects a txt file, rather than a CoNLL table.'+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+3),"Help",'Please, tick the checkbox if you wish to run the Python 3 sentence_text_readability function to compute various measures of text readability, also closely associated to the sentence clause structure.\n\n  12 readability score requires HIGHSCHOOL education;\n  16 readability score requires COLLEGE education;\n  18 readability score requires MASTER education;\n  24 readability score requires DOCTORAL education;\n  >24 readability score requires POSTDOC education.\n\nIn INPUT, the script expects a txt file, rather than a CoNLL table.\n\nIn OUTPUT, the script produces a txt file with readability scores for an entire text and a csv file with readability scores for each sentence in a text.'+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+4),"Help",'Please, tick the checkbox if you wish to visualize the sentence structure as a png image of the dependency tree.'+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+5),"Help","Please, tick the checkbox if you wish to extract all the sentences from your input txt file(s) that contain specific words (single words or collocations, i.e., sets of words).\n\nThe widget 'Words in sentence' will become available once you select the option. You will need to enter there the words/set of words that a sentence must contain in order to be extracted from input and saved in output. Words/set of words must be entered in DOUBLE QUOTES (e.g., \"The New York Times\") and comma separated (e.g., \"The New York Times\" , \"The Boston Globe\"). When running the script, the script will ask you if you want to process the search word(s) as case sensitive (thus, if you opt for case sensitive searches, a sentence containing the word 'King' will not be selected in output if in the widget 'Word(s) in sentence' you have entered 'king').\n\nIn INPUT, the script expects a single txt file or a directory.\n\nIn OUTPUT the script produces two types of files:\n1. files ending with _extract.txt and containing, for each input file, all the sentences that have the search word(s);\n2. files ending with _extract_minus.txt and containing, for each input file, the sentences that do NOT have the search word(s)."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+6),"Help",GUI_IO_util.msg_openOutputFiles)
help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The Python 3 scripts provide a variety of tools for fine-grained analyses of texts by sentence index, visualizing the ebb and flow of writing, the tempo of writing."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options, IO_setup_display_brief)

# GUI_IO_util.GUI_frontEnd('Sentence Analysis')

GUI_util.window.mainloop()

