#written by Catherine Xiao, Apr 2018
#edited by Elaine Dong, Dec 04 2019
#edited by Roberto Franzosi, Nov 2019, October 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Nominalization",['tkinter','nltk','pywsd','csv','re','os','collections'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
import nltk

# check averaged_perceptron_tagger
IO_libraries_util.import_nltk_resource(GUI_util.window,'taggers/averaged_perceptron_tagger','averaged_perceptron_tagger')
# check punkt
IO_libraries_util.import_nltk_resource(GUI_util.window,'tokenizers/punkt','punkt')
# check WordNet
IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/WordNet','WordNet')

from nltk import tokenize
# MUST use this  version or code will break pywsd~=1.2.4 pip install pywsd~=1.2.4; even try pip install pywsd=1.2.2
#   or this version pip install pywsd==1.0.2
# https://github.com/alvations/pywsd/issues/65
# pywsd depends upon wn below; if the code breaks reinstall wn
# pywsd Python word sense disambiguation
#   https://pypi.org/project/pywsd/
from pywsd import disambiguate
from nltk.corpus import wordnet as wn
# pip install wn==0.0.23
import string
import re
from collections import Counter


import IO_files_util
import IO_csv_util
import IO_user_interface_util
import Excel_util
import GUI_IO_util

# RUN section ______________________________________________________________________________________________________________________________________________________

#first_section is to extract the word from "syns". 
# syns.name() of "intention" is "purpose.n.01". So "first_section" gets everything before the first period: "purpose"

#params: sent > string
#result #includes word='NO NOMINALIZATION'
#count #includes word='NO NOMINALIZATION'
#count1 #excludes word='NO NOMINALIZATION'
def nominalized_verb_detection(docID,doc,sent):
    sentences = tokenize.sent_tokenize(sent)
    result = []
    result1 = []
    true_word = []
    false_word = []
    # word count for the sentence
    word_count = []
    # number of nominalization in the sentence
    nomi_count = []
    sen_id = -1
    # to print the sentence in output
    sentence = []
    # to print the nominalizations in each sentence
    nomi_sen = []
    nomi_sen_ = ""
    def is_pos(s, pos):
        # print(s)
        return s.split('.')[1] == pos
    for each_sen in sentences:
        sen_id += 1
        nomi_count.append(0)
        word_count.append(0)
        sentence.append(each_sen)
        words_with_tags = disambiguate(each_sen)
        for tup in words_with_tags:
            word, syns = tup
            if (word in string.punctuation) or (word == "\"") or (word[0] == "\'") or (word[0] == "`"):
                continue
            word_count[sen_id] += 1
            derivationals = []
            word = word.lower()
            if word in true_word:
                nomi_count[sen_id] += 1
                if nomi_sen_ == "":
                    nomi_sen_ = word
                else:
                    nomi_sen_ = nomi_sen_ + "; " + word
                noun_cnt[word] += 1
                nominalized_cnt[word] += 1
                continue
            if word in false_word:
                noun_cnt[word] += 1
                continue
            if syns:
                #look at only nouns
                if not is_pos(syns.name(), 'n'):
                    result.append([word, False])
                    false_word.append(word)
                    noun_cnt[word] += 1
                    continue
                if wn.lemmas(word):
                    for lemma in wn.lemmas(word): 
                        derive = lemma.derivationally_related_forms()
                        if derive not in derivationals and derive:
                            derivationals.append(derive)
                else:
                    try:
                        derivationals = syns.lemmas()[0].derivationally_related_forms()
                    except:
                        pass
                stem = first_section.match(str(syns.name())).group(1)
                found = False
                for deriv in derivationals:
                    if is_pos(str(deriv), 'v'):
                        deriv_str = str(deriv)[7:-3].split('.')[3]
                        if len(word) <= len(deriv_str):
                            continue
                        result.append([word, True])
                        true_word.append(word)
                        noun_cnt[word] += 1
                        if nomi_sen_ == "":
                            nomi_sen_ = word
                        else:
                            nomi_sen_ = nomi_sen_ + "; " + word
                        nominalized_cnt[word] += 1
                        found = True
                        break
                if found:
                    nomi_count[sen_id] += 1
                    continue
                else:
                    result.append([word, False]) #includes word='NO NOMINALIZATION'
                    noun_cnt[word] += 1
        nomi_sen.append(nomi_sen_)
        nomi_sen_ = ""
    for i in range(sen_id+1):
        #['Document ID', 'Document', 'Sentence ID', 'Sentence', 'Number of words in sentence', 'Nominalized verbs','Number of nominalizations in sentence', 'Percentage of nominalizations in sentence'])
        if word_count[i]>0:
            result1.append([docID, IO_csv_util.dressFilenameForCSVHyperlink(doc), i+1, sentence[i], word_count[i], nomi_sen[i], nomi_count[i],
                             100.0*nomi_count[i]/word_count[i]])
        else:
            result1.append([docID, IO_csv_util.dressFilenameForCSVHyperlink(doc), i+1, sentence[i], word_count[i], nomi_sen[i], nomi_count[i]])
    # print(result1)
    # result contains a list of each word TRUE/FALSE values for nominalization
    # result1 contains a list of docID, docName, sentence...
    return result, result1

def list_to_csv(output_filename, lists):
    """
    for list_ in lists:
        word, bool = tup_
        bool = str(bool)
        output_filename.write(word)
        output_filename.write(',')
        output_filename.write(bool)
        output_filename.write('\n')
        """
    IO_csv_util.list_to_csv(GUI_util.window,lists,output_filename,colnum=0)

def write_dir_csv(output_filename, lists, file_name):
    parts = file_name.split(os.path.sep) 
    file_name = parts[-1]
    for list_ in lists:
        list_.append(file_name)
    IO_csv_util.list_to_csv(GUI_util.window,lists,output_filename,colnum=0)

def run(inputFilename,inputDir, outputDir,openOutputFiles,createExcelCharts,doNotListIndividualFiles):
    global first_section, noun_cnt, nominalized_cnt

    first_section = re.compile("^(.+?)\.")
    noun_cnt = Counter()
    nominalized_cnt = Counter()
    filesToOpen = []  # Store all files that are to be opened once finished

    if __name__ == '__main__':
        nltk.data.path.append('./nltk_data')

        inputDocs = []
        if os.path.isdir(inputDir):
            for f in os.listdir(inputDir):
                if f[:2] != '~$' and f[-4:] == '.txt':
                    inputDocs.append(os.path.join(inputDir, f))
            if len(inputDocs) == 0:
                print("There are no txt files in the input path. The program will exit.")
                mb.showwarning(title='No txt files found',
                               message='There are no txt files in the selected input directory.\n\nPlease, select a different input directory and try again.')
                return
        else:
            inputDocs = [inputFilename]

        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running Nominalization at', True)

        #add all into a sum
        result_dir = []
        docID=0
        result2 = []
        result_dir2=[]
        counter_nominalized_list = []
        counter_nominalized_list.append(['Nominalized verb', 'Frequency'])
        counter_noun_list = []
        counter_noun_list.append(['Noun', 'Frequency'])

        for doc in inputDocs:

            docID=docID+1
            print("Processing document", doc, "\n")
            #open the doc and create the list of result (words, T/F)
            fin = open(doc, 'r',encoding='utf-8',errors='ignore')
            # result1 contains the sentence and nominalized values for a specific document
            result, result1 = nominalized_verb_detection(docID,doc,fin.read())
            # result2 contains the sentence and nominalized values for all documents
            result2.extend(result1)
            fin.close()

            # list all verbs as TRUE/FALSE if nominalized
            for word, boolean in result:
                result_dir.append([word, boolean, docID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])

            result_dir2.extend(result_dir)

            if len(inputDir) > 0:
                fname = os.path.basename(os.path.normpath(inputDir))+"_dir"
            else:
                fname=doc
            # used for both individual files and directories
            output_filename_bySentenceIndex = IO_files_util.generate_output_file_name(fname, '', outputDir,
                                                            '.csv','NOM', 'sent', '', '', '', False, True)


            if len(inputDir) == 0 or doNotListIndividualFiles == False:
                counter_nominalized_list = []
                counter_noun_list = []
                # refresh the headers
                counter_nominalized_list.insert(0,['Nominalized verb', 'Frequency'])
                counter_noun_list.insert(0,['Noun', 'Frequency'])

                result1.insert(0, ['Document ID', 'Document', 'Sentence ID', 'Sentence',
                                   'Number of words in sentence', 'Nominalized verbs',
                                   'Number of nominalizations in sentence',
                                   'Percentage of nominalizations in sentence'])

                # compute frequency of most common nominalized verbs
                for word, freq in nominalized_cnt.most_common():
                    counter_nominalized_list.append([word, freq])

                # compute frequency of most common nouns
                for word, freq in noun_cnt.most_common():
                    counter_noun_list.append([word, freq])

                head, fname=os.path.split(doc)
                fname=fname[:-4]

                output_filename_noun_frequencies = IO_files_util.generate_output_file_name(fname, '', outputDir, '.csv', 'NOM',
                                                                                'noun_freq', '', '', '', False,
                                                                                           True)
                filesToOpen.append(output_filename_noun_frequencies)
                output_filename_nominalized_frequencies = IO_files_util.generate_output_file_name(fname,
                                                                                '', outputDir, '.csv', 'NOM',
                                                                                 'nominal_freq', '', '', '', False,
                                                                                                  True)
                filesToOpen.append(output_filename_nominalized_frequencies)

                # export nominalized verbs
                list_to_csv(output_filename_nominalized_frequencies, counter_nominalized_list)

                # export nouns
                list_to_csv(output_filename_noun_frequencies, counter_noun_list)

                output_filename_TRUE_FALSE = IO_files_util.generate_output_file_name(fname + '_TRUE_FALSE', '', outputDir,
                                                                               '.csv', 'NOM', '', '', '', '', False,
                                                                                     True)

                filesToOpen.append(output_filename_TRUE_FALSE)
                list_to_csv(output_filename_TRUE_FALSE, result)

                filesToOpen.append(output_filename_bySentenceIndex)
                list_to_csv(output_filename_bySentenceIndex, result1)

                if createExcelCharts == True:
                    # line chart
                    columns_to_be_plotted = [[2,6]]
                    chartTitle='Nominalized verbs (by Sentence Index)'
                    xAxis='Sentence index'
                    yAxis='Number of nominalizations in sentence'
                    hover_label=''
                    Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, output_filename_bySentenceIndex, outputDir,
                                                              '',
                                                              chart_type_list=["line"],
                                                              chart_title=chartTitle,
                                                              column_xAxis_label_var=xAxis,
                                                              hover_info_column_list=hover_label,
                                                              column_yAxis_label_var=yAxis)
                    if len(Excel_outputFilename) > 0:
                        filesToOpen.append(Excel_outputFilename)

                    # pie chart of nominalized verbs
                    Excel_outputFilename=Excel_util.create_excel_chart(GUI_util.window,[counter_nominalized_list],fname,outputDir,'NOM_Verb',"Nominalized verbs",["pie"])
                    if len(Excel_outputFilename) > 0:
                        filesToOpen.append(Excel_outputFilename)

                    # pie chart of nouns
                    Excel_outputFilename=Excel_util.create_excel_chart(GUI_util.window,[counter_noun_list],fname,outputDir,'NOM_noun',"Nouns",["pie"])
                    if len(Excel_outputFilename) > 0:
                        filesToOpen.append(Excel_outputFilename)

        if len(inputDir)>0 and doNotListIndividualFiles == True:
            output_filename_TRUE_FALSE_dir = IO_files_util.generate_output_file_name(fname + '_TRUE_FALSE', '', outputDir, '.csv', 'NOM', '', '', '', '', False, True)
            filesToOpen.append(output_filename_TRUE_FALSE_dir)
            output_filename_dir_noun_frequencies=IO_files_util.generate_output_file_name(fname, '', outputDir, '.csv', 'NOM', 'noun_freq', '', '', '', False, True)
            filesToOpen.append(output_filename_dir_noun_frequencies)
            output_filename_dir_nominalized_frequencies=IO_files_util.generate_output_file_name(fname, '', outputDir, '.csv', 'NOM', 'nominal_freq', '', '', '', False, True)
            filesToOpen.append(output_filename_dir_nominalized_frequencies)

            result2.insert(0, ['Document ID', 'Document', 'Sentence ID', 'Sentence', 'Number of words in sentence', 'Nominalized verbs',
                               'Number of nominalizations in sentence', 'Percentage of nominalizations in sentence'])
            list_to_csv(output_filename_bySentenceIndex, result2)

            # list all verbs as TRUE/FALSE if nominalized
            result_dir2.insert(0, ["Word", "Is nominalized", "Document ID", "Document"])
            list_to_csv(output_filename_TRUE_FALSE_dir, result_dir2)


            counter_noun_list = []
            counter_noun_list.append(['Noun','Frequency'])
            for word, freq in noun_cnt.most_common():
                counter_noun_list.append([word, freq])
            list_to_csv(output_filename_dir_noun_frequencies, counter_noun_list)

            counter_nominalized_list = []
            counter_nominalized_list.append(['Nominalized verb','Frequency'])
            for word, freq in nominalized_cnt.most_common():
                counter_nominalized_list.append([word, freq])
            list_to_csv(output_filename_dir_nominalized_frequencies, counter_nominalized_list)

            if createExcelCharts == True:
                # pie chart of nominalized verbs
                Excel_outputFilename=Excel_util.create_excel_chart(GUI_util.window, [counter_nominalized_list], output_filename_dir_nominalized_frequencies,
                                            outputDir,'NOM_verb',
                                            "Nominalized verbs", ["pie"])
                if len(Excel_outputFilename) > 0:
                    filesToOpen.append(Excel_outputFilename)

                # pie chart of nouns
                Excel_outputFilename=Excel_util.create_excel_chart(GUI_util.window, [counter_noun_list], output_filename_dir_noun_frequencies,
                                            outputDir,'NOM_noun',
                                            "Nouns", ["pie"])
                if len(Excel_outputFilename) > 0:
                    filesToOpen.append(Excel_outputFilename)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running Nominalization at', True, '', True, startTime)

    if openOutputFiles == 1:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)


#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_Excel_chart_output_checkbox.get(),
                                doNotCreateIntermediateFiles_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_width=1220
GUI_height=360 # height of GUI with full I/O display

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

GUI_label='Graphical User Interface (GUI) for Nominalization'
config_filename='nominalization-config.txt'
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
config_option=[0,2,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_options,config_filename,IO_setup_display_brief)

doNotCreateIntermediateFiles_var = tk.IntVar() #when an entire directory is processed; could lead to an enourmus number of output files
doNotCreateIntermediateFiles_var.set(1)

doNotCreateIntermediateFiles_checkbox = tk.Checkbutton(window, variable=doNotCreateIntermediateFiles_var, onvalue=1, offvalue=0)
doNotCreateIntermediateFiles_checkbox.config(text="Do NOT produce intermediate csv files when processing all txt files in a directory")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,doNotCreateIntermediateFiles_checkbox)

def changeLabel_nomin(*args):
    if doNotCreateIntermediateFiles_var.get()==1:
        doNotCreateIntermediateFiles_checkbox.config(text="Do NOT produce intermediate csv files when processing all txt files in a directory")
    else:
        doNotCreateIntermediateFiles_checkbox.config(text="Produce intermediate csv files when processing all txt files in a directory")
doNotCreateIntermediateFiles_var.trace('w',changeLabel_nomin)

def turnOff_doNotCreateIntermediateFiles_checkbox(*args):
    if len(input_main_dir_path.get())>0:
        doNotCreateIntermediateFiles_checkbox.config(state='normal')
    else:
        doNotCreateIntermediateFiles_checkbox.config(state='disabled')
GUI_util.input_main_dir_path.trace('w',turnOff_doNotCreateIntermediateFiles_checkbox)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Nominalization':'TIPS_NLP_Nominalization.pdf'}
TIPS_options='Nominalization'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    if not IO_setup_display_brief:
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",GUI_IO_util.msg_txtFile)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_corpusData)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help",GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+1),"Help","Please, untick the checkbox if you want to create intermediate csv files for every txt file in a directory when processing all the txt files in a directory.\n\nWARNING! Unticking the checkbox may result in a very large number of intermediate files (3 csv/xlsx files for every txt file in the directory).")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+2),"Help",GUI_IO_util.msg_openOutputFiles)

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The Python 3 scripts analyzes a text file for instances of nominaliztion (i.e., the use of nouns instead of verbs, such as 'the lynching' occurred).\n\nNominalization, together with passive verb voices, can be used to deny agency. In fact, in an expression such as 'the lynching occurred' there is no mention of an agent, of who did it."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief)

GUI_util.window.mainloop()
