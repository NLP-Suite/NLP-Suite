#Written by Roberto Franzosi
#Modified by Cynthia Dong (Fall 2019-Spring 2020)
#Wordnet_bySentenceID and get_case_initial_row written by Yi Wang (April 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"WordNet",['os','csv','tkinter','subprocess','nltk','pandas'])==False:
    sys.exit(0)

import os
import subprocess
from nltk.corpus import wordnet as wn
import pandas as pd
import csv

import reminders_util
import charts_util
import IO_files_util
import IO_user_interface_util
import data_manager_util
import IO_csv_util
import statistics_csv_util

filesToOpen=[]

def process_keyword(wordNet_keyword_list, noun_verb):
    for keyword in wordNet_keyword_list:
        if noun_verb == "VERB":
            synset = wn.synsets(keyword, pos = wn.VERB)
            if len(synset) == 0:
                continue
            else:
                synset = synset[0]# get the synset of word with its most frequent meaning
        else:
            synset = wn.synsets(keyword, pos = wn.NOUN)
            if len(synset) == 0:
                continue
            else:
                synset = synset[0]# get the synset of word with its most frequent meaning
        hyponynms = synset.hyponyms()
        print ("=======sub groups are: ======")
        # find the direct hyponynms
        for each in hyponynms:
            print (each.lemmas()[0].name())

def disaggregate_GoingDOWN(WordNetDir,outputDir, wordNet_keyword_list, noun_verb):
    filesToOpen=[]
    if IO_libraries_util.check_inputPythonJavaProgramFile('WordNet_Search_DOWN.jar') == False:
        return
    errorFound, error_code, system_output = IO_libraries_util.check_java_installation('WordNet downward search')
    if errorFound:
        return
    process_keyword(wordNet_keyword_list, noun_verb)
    if len(wordNet_keyword_list) > 1:
        fileName = wordNet_keyword_list[0] + "-plus-list"
    else:
        fileName = wordNet_keyword_list[0] + "-list"
    call_list = ['java', '-jar', 'WordNet_Search_DOWN.jar', outputDir, os.path.join(WordNetDir, "dict"), fileName, noun_verb]
    for each in wordNet_keyword_list:
        call_list.append(each)
    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Analysis start', 'Started running WordNet (Zoom IN/DOWN) at', True, 'Running WordNet with the ' + noun_verb + ' option with following keywords:\n\n' + str(wordNet_keyword_list))
    warning = subprocess.call(call_list)
    if warning == 1:
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Invalid Input',
                                           'All keyword(s) in your search list do not exist in Wordnet for " + noun_verb + ".\n\nPlease, edit your keyword list and try again.')
        # mb.showwarning(title = "Invalid Input", message = "All keyword(s) in your search list do not exist in Wordnet for " + noun_verb + ".\n\nPlease, edit your keyword list and try again.")
        return
    elif warning == 2:
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Invalid Input',
                                           'Some keyword(s) in your search list do not exist in Wordnet for " + noun_verb + ".\n\nPlease, edit your keyword list and try again.\n\nPlease, check the terminal/command line prompt to see the details.')
        # mb.showwarning(title="Invalid Input",
                       # message="Some keyword(s) in your search list do not exist in Wordnet for " + noun_verb + ".\n\nPlease, edit your keyword list and try again.\n\nPlease, check the terminal/command line prompt to see the details.")
    filesToOpen.append(os.path.join(outputDir, "NLP_WordNet_DOWN_" + fileName + ".csv"))
    filesToOpen.append(os.path.join(outputDir, "NLP_WordNet_DOWN_" + fileName + "-verbose.csv"))
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running WordNet (Zoom IN/DOWN) at', True, '', True, startTime)
    return filesToOpen

# the header does not matter, it can be NUN or VERB or anything else
# what matters is the first column; and there can be multiple columns tha will not be processed
def aggregate_GoingUP(WordNetDir, inputFile, outputDir, config_filename, noun_verb,openOutputFiles,createCharts, chartPackage, language_var=''):
    filesToOpen=[]
    if language_var=='' and language_var!='English':
        reminders_util.checkReminder(
            config_filename,
            reminders_util.title_options_English_language_WordNet,
            reminders_util.message_English_language_WordNet,
            True)
        return filesToOpen
    if noun_verb == 'VERB':
        reminders_util.checkReminder(
            config_filename,
            reminders_util.title_options_WordNet_verb_aggregation,
            reminders_util.message_WordNet_verb_aggregation,
            True)

    # for noun_verb == 'VERB' we should provide the user with two different outputs; with and without be, have
    # the aggregated 'stative' category includes the auxiliary 'be' probably making up the vast majority of stative verbs. Similarly, the category 'possession' include the auxiliary 'have' (and 'get')

    if IO_libraries_util.check_inputPythonJavaProgramFile('WordNet_Search_UP.jar') == False:
        return filesToOpen
    errorFound, error_code, system_output = IO_libraries_util.check_java_installation('WordNet upward search')
    if errorFound:
        return filesToOpen
    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Analysis start', 'Started running WordNet (Zoom OUT/UP) with the ' + noun_verb + ' option at', True, '',True,'',True)

    # the java script produces two files: a file containing the intermediate synsets and with _output in the filename and a frequency file
    warning = subprocess.call(['java', '-jar', 'WordNet_Search_UP.jar', '-wordNetPath', os.path.join(WordNetDir, "dict"), '-wordList', inputFile, "-pos" , noun_verb, '-outputDir', outputDir])
    if warning == 1:
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Invalid Input',
                                           "Wordnet cannot find any word in the input csv file for " + noun_verb + ".\n\nThis error can also occur if any of the files previously generated by WordNet are open. Please, check your files, close them, and try again.")
        return filesToOpen
    elif warning == 2:
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Invalid Input',
                                           "WordNet " + noun_verb + " aggregation.\n\nSome words in the list to be aggregated do not exist in Wordnet for " + noun_verb + ".\n\nPlease, check in command line the list of words not found in WordNet.")
    # the Java script returns the filenames without VERB or NOUN in the filename
    # the next two lines reconstruct the filename as exported by the JAVA script
    fileName = os.path.basename(inputFile).split(".")[0]
    outputFilenameCSV1=os.path.join(outputDir, "NLP_WordNet_UP_" + fileName+"_output.csv")
    outputFilenameCSV2=os.path.join(outputDir, "NLP_WordNet_UP_" + fileName+"_frequency.csv")
    # remove _output from the Java output
    outputFilenameCSV1_new = outputFilenameCSV1.replace("_output", "")
    # the Java script returns the filenames without VERB or NOUN in the filename
    #   one for # intermediate synsets, the other of frequencies
    if (not 'VERB' in outputFilenameCSV1_new) and (not 'NOUN' in outputFilenameCSV1_new):
        outputFilenameCSV1_new = outputFilenameCSV1_new.replace("NLP_WordNet_UP_","NLP_WordNet_UP_"+noun_verb+"_")
        outputFilenameCSV2_new = outputFilenameCSV2.replace("NLP_WordNet_UP_","NLP_WordNet_UP_"+noun_verb+"_")
        # the synsets file already exists and must be removed
        if os.path.isfile(outputFilenameCSV1_new):
            os.remove(outputFilenameCSV1_new)
        # the frequency file already exists and must be removed
        if os.path.isfile(outputFilenameCSV2_new):
            os.remove(outputFilenameCSV2_new)
        # rename the output file of synsets values created by JAVA script (outputFilenameCSV1) to the new filename (outputFilenameCSV1_new)
        os.rename(outputFilenameCSV1, outputFilenameCSV1_new)
        # rename the output file of frequency values created by JAVA script (outputFilenameCSV2) to the new filename (outputFilenameCSV2_new)
        os.rename(outputFilenameCSV2, outputFilenameCSV2_new)
    else:
        outputFilenameCSV1_new = outputFilenameCSV1 # intermediate synsets
        outputFilenameCSV2_new = outputFilenameCSV2 # frequency
    filesToOpen.append(outputFilenameCSV1_new)
    complete_csv_header(outputFilenameCSV1_new,"Intermediate synset")
    # outputFilenameCSV2 - with frequency in the filename - is the file with the handful of WordNett aggregated synsets and their frequency
    outputFilenameCSV2 = os.path.join(outputDir, "NLP_WordNet_UP_" + noun_verb + '_' + fileName + "_frequency.csv")
    # Since the original output file returned by the JAVA script WordNet_Search_UP.jar contains
    #   the header Intermediate Synsets, this must be renamed to Intermediate synset 1
    IO_csv_util.rename_header(outputFilenameCSV1_new, "Intermediate Synsets","Intermediate synset 1")
    if (not 'VERB' in outputFilenameCSV2) and (not 'NOUN' in outputFilenameCSV2):
        outputFilenameCSV2_new = outputFilenameCSV1.replace("NLP_WordNet_UP_","NLP_WordNet_UP_"+noun_verb+"_")
        # the file already exists and must be removed
        if os.path.isfile(outputFilenameCSV2_new):
            os.remove(outputFilenameCSV2_new)
        os.rename(outputFilenameCSV2, outputFilenameCSV2_new)
    else:
        outputFilenameCSV2_new = outputFilenameCSV2
    filesToOpen.append(outputFilenameCSV2_new)

    chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilenameCSV1_new, outputDir,
                                                       columns_to_be_plotted=[[1, 1]],
                                                       chartTitle='Frequency of WordNet Aggregate Categories for ' + noun_verb,
                                                       count_var=1,  # to be used for byDoc, 0 for numeric field
                                                       hover_label=[],
                                                       outputFileNameType='',
                                                       column_xAxis_label='WordNet ' + noun_verb + ' category',
                                                       groupByList=[],
                                                       plotList=[],
                                                       chart_title_label='')
    if chart_outputFilename != None:
        if len(chart_outputFilename) > 0:
            filesToOpen.extend(chart_outputFilename)

    if noun_verb == 'VERB':
        operation_results_text_list=[]
        outputFilenameCSV3_new = inputFile.replace("VERB","VERB_no_auxil")
        # outputFilenameCSV3_new = outputFilenameCSV3_new.replace("_output", "")
        # # the file already exists and must be removed
        # if os.path.isfile(outputFilenameCSV3_new):
        #     os.remove(outputFilenameCSV3_new)
        # os.rename(outputFilenameCSV1_new, outputFilenameCSV3_new)
        # Word is the header from the _output file created by the Java WordNet script
        operation_results_text_list.append(str(outputFilenameCSV1_new) + ',Word,<>,be,and')
        operation_results_text_list.append(str(outputFilenameCSV1_new) + ',Word,<>,have,and')
        # outputFilenameCSV3_new = data_manager_util.export_csv_to_csv_txt(outputFilenameCSV3_new, operation_results_text_list,'.csv',[0,1])
        outputFilenameCSV3_new = data_manager_util.export_csv_to_csv_txt(outputDir,operation_results_text_list,'.csv',[0,1])

        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilenameCSV3_new,
                                                           outputDir,
                                                           columns_to_be_plotted=[[1, 1]],
                                                           chartTitle='Frequency of WordNet Aggregate Categories for ' + noun_verb + ' (No Auxiliaries)',
                                                           count_var=1,  # to be used for byDoc, 0 for numeric field
                                                           hover_label=[],
                                                           outputFileNameType='',
                                                           column_xAxis_label='WordNet ' + noun_verb + ' category',
                                                           groupByList=[],
                                                           plotList=[],
                                                           chart_title_label='')
        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        if outputFilenameCSV3_new != "":
            os.remove(outputFilenameCSV3_new)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running WordNet (Zoom OUT/UP) at', True, '', True, startTime, True)

    return filesToOpen

# written by Yi Wang April 2020
# ConnlTable is the inputFilename
# TODO TONY do we need this now? Don't we have more general ways of dealing with this?
def Wordnet_bySentenceID(ConnlTable, wordnetDict, outputFilename, outputDir, noun_verb, openOutputFiles,
                         createCharts, chartPackage):
    filesToOpen = []
    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start',
                                                   'Started running WordNet charts by sentence index at',
                                                   True, '', True, '', False)

    if noun_verb == 'NOUN':
        checklist = ['NN', 'NNP', 'NNPS', 'NNS']
    else:
        checklist = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    # read in the CoreNLP CoNLL table
    connl = pd.read_csv(ConnlTable)
    # read in the dictionary file to be used to filter CoNLL values
    # The file is expected to have 2 columns with headers: Word, WordNet Category
    try:
        dict = pd.read_csv(wordnetDict)
    except:
        mb.showwarning("Warning",
                       "The file \n\n" + wordnetDict + "\n\ndoes not have the expected 2 columns: Word, WordNet Category. You may have selected the wrong input file.\n\nPlease, select the right input file and try again.")
        return
    # set up the double list conll from the conll data
    try:
        connl = connl[['Form', 'Lemma', 'POStag', 'Sentence ID', 'Document ID', 'Document']]
    except:
        mb.showwarning("Warning",
                       "The file \n\n" + ConnlTable + "\n\ndoes not appear to be a CoNLL table with expected column names: Form,Lemma,Postag, SentenceID, DocumentID, Document.\n\nPlease, select the right input file and try again.")
        return
    # filter the list by noun or verb
    connl = connl[connl['Postag'].isin(checklist)]
    # eliminate any duplicate value in Word (Form))
    dict = dict.drop_duplicates().rename(columns={'Word': 'Lemma', 'WordNet Category': 'Category'})
    # ?
    connl = connl.merge(dict, how='left', on='Lemma')
    # the CoNLL table value is not found in the dictionary Word value
    connl.fillna('Not in INPUT dictionary for ' + noun_verb, inplace=True)
    # add the WordNet category to the conll list
    connl = connl[['Form', 'Lemma', 'POStag', 'Category', 'Sentence ID', 'Document ID', 'Document']]
    # put headers on conll list
    connl.columns = ['Form', 'Lemma', 'POStag', 'Category', 'Sentence ID', 'Document ID', 'Document']

    Row_list = []
    # Iterate over each row
    for index, rows in connl.iterrows():
        # Create list for the current row
        my_list = [rows.word, rows.lemma, rows.postag, rows.Category, rows.SentenceID, rows.DocumentID, rows.Document]
        # append the list to the final list
        Row_list.append(my_list)
    for index, row in enumerate(Row_list):
        if index == 0 and Row_list[index][4] != 1:
            for i in range(Row_list[index][4] - 1, 0, -1):
                Row_list.insert(0, ['', '', '', '', i, Row_list[index][5], Row_list[index][6]])
        else:
            if index < len(Row_list) - 1 and Row_list[index + 1][4] - Row_list[index][4] > 1:
                for i in range(Row_list[index + 1][4] - 1, Row_list[index][4], -1):
                    Row_list.insert(index + 1, ['', '', '', '', i, Row_list[index][5], Row_list[index][6]])
    df = pd.DataFrame(Row_list,
                      index=['Form', 'Lemma', 'POStag', 'WordNet Category', 'Sentence ID', 'Document ID', 'Document'])
    df = statistics_csv_util.add_missing_IDs(df)
    df.to_csv(outputFilename, index=False)

    if createCharts:
        outputFiles = statistics_csv_util.compute_csv_column_frequencies(GUI_util.window,
                                                                       ConnlTable,
                                                                       df,
                                                                       outputDir,
                                                                       openOutputFiles,
                                                                       createCharts,
                                                                       chartPackage,
                                                                       [[4, 5]],
                                                                       ['WordNet Category'], ['Form'],
                                                                       ['Sentence ID', 'Document ID', 'Document'],
                                                                       )
        if len(outputFiles) > 0:
            filesToOpen.extend(outputFiles)
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
                                       'Finished running WordNet charts by sentence index at', True, '', True,
                                       startTime)

    return filesToOpen

def get_case_initial_row(inputFilename,outputDir,check_column, firstLetterCapitalized=True):
    if firstLetterCapitalized:
        str='Upper'
    else:
        str='Lower'
    outputFilename=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'filter_' + str)
    filesToOpen.append(outputFilename)
    data = pd.read_csv(inputFilename)
    if firstLetterCapitalized:
        regex = '^[A-Z].*'
    else:
        regex = '^[a-z].*'
    data = data[data[check_column].str.contains(regex, regex= True, na=False)] # select by regular expression
    data.to_csv(outputFilename,index=False)
    return filesToOpen

# The output file returned by the JAVA script WordNet_Search_UP.jar contains
#   several intermediate synsets under the same column header Intermediate Synsets
#   causing problems to pandas
#   The list of Intermediate Synsets mustt be separated and ut under separate headings

def complete_csv_header(inputFilename, padding_base_name):
    max_length = 0
    new_header = []
    # find the longest row
    with open(inputFilename, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if max_length < len(row):
                max_length = len(row)
    with open(inputFilename, newline='') as f:
        reader = csv.reader(f)
        # only read the first line
        for row in reader:
            max_length = max_length - len(row)
            new_header = row
            for i in range(1, max_length+1):
                new_header.append(padding_base_name + " " + str(i+1))
            break
    tempFile = os.path.splitext(inputFilename)[0] + "_modified.csv"
    os.rename(inputFilename, tempFile)
    with open(tempFile, newline='') as fr, open(inputFilename,"w", newline='') as fw:
        r = csv.reader(fr)
        w = csv.writer(fw)
        w.writerow(new_header)
        next(r, None)
        for row in r:
            w.writerow(row)
    os.remove(tempFile)
    return
