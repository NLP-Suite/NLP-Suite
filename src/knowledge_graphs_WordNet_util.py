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
import tkinter.messagebox as mb
from nltk.corpus import wordnet as wn
import pandas as pd
import csv

import reminders_util
import charts_Excel_util
import IO_files_util
import IO_user_interface_util
import data_manager_util

filesToOpen=[]

# written by Yi Wang April 2020
# ConnlTable is the inputFilename
def Wordnet_bySentenceID(ConnlTable, wordnetDict,outputFilename,outputDir,noun_verb,openOutputFiles,createExcelCharts):
    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running WordNet charts by sentence index at',
                                                 True, '', True, '', True)

    if noun_verb=='NOUN':
        checklist = ['NN','NNP','NNPS','NNS']
    else:
        checklist = ['VB','VBD','VBG','VBN','VBP','VBZ']
    # read in the CoreNLP CoNLL table
    connl = pd.read_csv(ConnlTable)
    # read in the dictionary file to be used to filter CoNLL values
    # The file is expected to have 2 columns with headers: Word, WordNet Category
    dict = pd.read_csv(wordnetDict)
    # set up the double list conll from the conll data 
    connl = connl[['word','lemma','postag','Sentence ID','Document ID','Document']]
    # filter the list by noun or verb
    connl = connl[connl['postag'].isin(checklist)]
    # eliminate any duplicate value in Word    
    dict = dict.drop_duplicates().rename(columns = {'Word':'lemma', 'WordNet Category':'Category'})
    # ?
    connl = connl.merge(dict,how = 'left', on = 'lemma')
    # the CoNLL table value is not found in the dictionary Word value
    connl.fillna('Not in INPUT dictionary for ' + noun_verb, inplace = True)
    # add the WordNet Catgegory to the conll list 
    connl = connl[['word','lemma','postag','Category','Sentence ID','Document ID','Document']]
    # put headers on conll list
    connl.columns = ['word','lemma','postag','Category','Sentence ID','Document ID','Document']

    Row_list = []
    # Iterate over each row
    for index, rows in connl.iterrows():
        # Create list for the current row
        my_list = [rows.word, rows.lemma, rows.postag, rows.Category, rows.SentenceID,rows.DocumentID, rows.Document]
        # append the list to the final list
        Row_list.append(my_list)
    for index,row in enumerate(Row_list):
        if index == 0 and Row_list[index][4] != 1:
            for i in range(Row_list[index][4]-1,0,-1):
                Row_list.insert(0,['','','','',i,Row_list[index][5],Row_list[index][6]])
        else:
            if index < len(Row_list)-1 and Row_list[index+1][4] - Row_list[index][4] > 1:
                for i in range(Row_list[index+1][4]-1,Row_list[index][4],-1):
                    Row_list.insert(index+1,['','','','',i,Row_list[index][5],Row_list[index][6]])
    df = pd.DataFrame(Row_list,index=['word','lemma','postag','WordNet Category','Sentence ID','Document ID','Document'])
    df = charts_Excel_util.add_missing_IDs(df)
    # Row_list.insert(0, ['word','lemma','postag','WordNet Category','SentenceID','DocumentID','Document'])
    #IO_util.list_to_csv('',Row_list,outputFilename)
    df.to_csv(outputFilename,index=False)

    if createExcelCharts:
        outputFiles=charts_Excel_util.compute_csv_column_frequencies(GUI_util.window,
                                    ConnlTable,
                                    df,
                                    outputDir,
                                    openOutputFiles,
                                    createExcelCharts,
                                    [[4,5]],
                                    ['WordNet Category'],['word'], ['Document ID','Sentence ID','Document'],
                                    'WordNet', 'line')
        if len(outputFiles) > 0:
            filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running WordNet charts by sentence index at', True, '', True, startTime)

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
def aggregate_GoingUP(WordNetDir, inputFile, outputDir, config_filename, noun_verb,openOutputFiles,createExcelCharts):

    if noun_verb == 'VERB':
        reminders_util.checkReminder(
            config_filename,
            reminders_util.title_options_WordNet_verb_aggregation,
            reminders_util.message_WordNet_verb_aggregation,
            True)

    # for noun_verb == 'VERB' we should provide the user with two different outputs; with and without be, have
    # the aggregated 'stative' category includes the auxiliary 'be' probably making up the vast majority of stative verbs. Similarly, the category 'possession' include the auxiliary 'have' (and 'get')

    filesToOpen=[]
    if IO_libraries_util.check_inputPythonJavaProgramFile('WordNet_Search_UP.jar') == False:
        return
    errorFound, error_code, system_output = IO_libraries_util.check_java_installation('WordNet upward search')
    if errorFound:
        return
    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Analysis start', 'Started running WordNet (Zoom OUT/UP) with the ' + noun_verb + ' option at', True, '',True,'',True)

    # the java script produces two files:a list and a frequency
    warning = subprocess.call(['java', '-jar', 'WordNet_Search_UP.jar', '-wordNetPath', os.path.join(WordNetDir, "dict"), '-wordList', inputFile, "-pos" , noun_verb, '-outputDir', outputDir])
    if warning == 1:
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Invalid Input',
                                           "Wordnet cannot find any word in the input csv file for " + noun_verb + ".\n\nThis error can also occur if any of the files previously generated by WordNet are open. Please, check your files, close them, and try again.")
        #
        # mb.showwarning(title = "Warning", message = "Wordnet cannot find any word in the input csv file for " + noun_verb + ".\n\nThis error can also occur if any of the files previously generated by WordNet are open. Please, check your files, close them, and try again.")
        return
    elif warning == 2:
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Invalid Input',
                                           "WordNet " + noun_verb + " aggregation.\n\nSome words in the list to be aggregated do not exist in Wordnet for " + noun_verb + ".\n\nPlease, check in command line the list of words not found in WordNet.")
        # mb.showwarning(title = "Warning", message = "WordNet " + noun_verb + " aggregation.\n\nSome words in the list to be aggregated do not exist in Wordnet for " + noun_verb + ".\n\nPlease, check in command line the list of words not found in WordNet.")
    fileName = os.path.basename(inputFile).split(".")[0]
    outputFilenameCSV1=os.path.join(outputDir, "NLP_WordNet_UP_" + fileName+"_output.csv")
    outputFilenameCSV1_new = outputFilenameCSV1.replace("_output", "")
    if (not 'VERB' in outputFilenameCSV1_new) and (not 'NOUN' in outputFilenameCSV1_new):
        # outputFilenameCSV1_new - with output in the filename - is the file with three columns: Word, WordNet Category, Intermediate Synsets
        outputFilenameCSV1_new = outputFilenameCSV1_new.replace("NLP_WordNet_UP_","NLP_WordNet_UP_"+noun_verb+"_")
        # outputFilenameCSV1_new = outputFilenameCSV1_new.replace("_output","")
        # the file already exists and must be removed
        if os.path.isfile(outputFilenameCSV1_new):
            os.remove(outputFilenameCSV1_new)
        os.rename(outputFilenameCSV1, outputFilenameCSV1_new)
    else:
        outputFilenameCSV1_new = outputFilenameCSV1
    filesToOpen.append(outputFilenameCSV1_new)

    # outputFilenameCSV2 - with frequency in the filename - is the file with the handful of WordNett aggregated synsets and their frequency
    outputFilenameCSV2 = os.path.join(outputDir, "NLP_WordNet_UP_" + fileName + "_frequency.csv")
    if (not 'VERB' in outputFilenameCSV2) and (not 'NOUN' in outputFilenameCSV2):
        outputFilenameCSV2_new = outputFilenameCSV1.replace("NLP_WordNet_UP_","NLP_WordNet_UP_"+noun_verb+"_")
        # the file already exists and must be removed
        if os.path.isfile(outputFilenameCSV2_new):
            os.remove(outputFilenameCSV2_new)
        os.rename(outputFilenameCSV2, outputFilenameCSV2_new)
    else:
        outputFilenameCSV2_new = outputFilenameCSV2
    filesToOpen.append(outputFilenameCSV2_new)

    if createExcelCharts:
        columns_to_be_plotted = [[1, 1]]
        chart_title='Frequency of WordNet Aggregate Categories for ' + noun_verb
        hover_label=['Word']
        inputFilename = outputFilenameCSV1_new
        Excel_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                  outputFileLabel='',
                                                  chart_type_list=["bar"],
                                                  chart_title=chart_title,
                                                  column_xAxis_label_var='WordNet ' + noun_verb + ' category',
                                                  hover_info_column_list=hover_label,
                                                  count_var=1)

        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)

    # from outputFilenameCSV1_new exclude the auxiliary verbs be and have not to bias
    #   the aggregate categories STATIVE and POSSESSION that include these verbs respectively

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

        if outputFilenameCSV3_new != "":
            filesToOpen.append(outputFilenameCSV3_new)

        if createExcelCharts:
            columns_to_be_plotted = [[1, 1]]
            chart_title='Frequency of WordNet Aggregate Categories for ' + noun_verb + ' (No Auxiliaries)'
            hover_label=[]
            inputFilename = outputFilenameCSV3_new
            Excel_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                      outputFileLabel='',
                                                      chart_type_list=["bar"],
                                                      chart_title=chart_title,
                                                      column_xAxis_label_var='WordNet ' + noun_verb + ' category',
                                                      hover_info_column_list=hover_label,
                                                      count_var=1)

            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running WordNet (Zoom OUT/UP) at', True, '', True, startTime, True)

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
