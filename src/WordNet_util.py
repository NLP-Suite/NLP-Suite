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

import Excel_util
import IO_files_util
import IO_user_interface_util

filesToOpen=[]

# written by Yi Wang April 2020
# ConnlTable is the inputFilename
def Wordnet_bySentenceID(ConnlTable, wordnetDict,outputFilename,outputDir,noun_verb,openOutputFiles,createExcelCharts):
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running WordNet charts by sentence index at', True)
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
    df = Excel_util.add_missing_IDs(df)
    # Row_list.insert(0, ['word','lemma','postag','WordNet Category','SentenceID','DocumentID','Document'])
    #IO_util.list_to_csv('',Row_list,outputFilename)
    df.to_csv(outputFilename,index=False)

    if createExcelCharts:
        outputFiles=Excel_util.compute_csv_column_frequencies(GUI_util.window,
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

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running WordNet charts by sentence index at', True)

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
    if IO_libraries_util.inputProgramFileCheck('WordNet_Search_DOWN.jar') == False:
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
    IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Analysis start', 'Started running WordNet (Zoom IN/DOWN) at', True, 'Running WordNet with the ' + noun_verb + ' option with following keywords:\n\n' + str(wordNet_keyword_list))
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
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running WordNet (Zoom IN/DOWN) at', True)
    return filesToOpen

# the header does not matter, it can be NUN or VERB or anything else
# what mattes is the first column; and there can be multiple columns tha will not be processed
def aggregate_GoingUP(WordNetDir, inputFile, outputDir, noun_verb,openOutputFiles,createExcelCharts):

    filesToOpen=[]
    if IO_libraries_util.inputProgramFileCheck('WordNet_Search_UP.jar') == False:
        return
    errorFound, error_code, system_output = IO_libraries_util.check_java_installation('WordNet upward search')
    if errorFound:
        return
    IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Analysis start', 'Started running WordNet (Zoom OUT/UP) at', True, '\n\nRunning WordNet with the ' + noun_verb + ' option.')
    # the java script produces two files:a list and a frequency
    warning = subprocess.call(['java', '-jar', 'WordNet_Search_UP.jar', '-wordNetPath', os.path.join(WordNetDir, "dict"), '-wordList', inputFile, "-pos" , noun_verb, '-outputDir', outputDir])
    if warning == 1:
        # IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Invalid Input',
        #                                    'Wordnet cannot find any word in the input csv file for " + noun_verb + ".\n\nThis error can also occur if any of the files previously generated by WordNet are open. Please, check your files, close them, and try again.')
        #
        mb.showwarning(title = "Warning", message = "Wordnet cannot find any word in the input csv file for " + noun_verb + ".\n\nThis error can also occur if any of the files previously generated by WordNet are open. Please, check your files, close them, and try again.")
        return
    elif warning == 2:
        # IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Invalid Input',
        #                                    'Some words in your list do not exist in Wordnet for " + noun_verb + ".\n\nPlease, check the list of words in command line.')
        mb.showwarning(title = "Warning", message = "WordNet " + noun_verb + " aggregation.\n\nSome words in the list to be aggregated do not exist in Wordnet for " + noun_verb + ".\n\nPlease, check in command line the list of words not found in WordNet.")
    fileName = os.path.basename(inputFile).split(".")[0]
    outputFilenameCSV1=os.path.join(outputDir, "NLP_WordNet_UP_"+fileName+"_output.csv")
    filesToOpen.append(outputFilenameCSV1)
    outputFilenameCSV2= os.path.join(outputDir, "NLP_WordNet_UP_" + fileName + "_frequency.csv")
    filesToOpen.append(outputFilenameCSV2)

    if createExcelCharts:
        columns_to_be_plotted = [[1, 1]]
        chart_title='Frequency of WordNet Aggregate Categories for ' + noun_verb
        hover_label=['Word']
        inputFilename = outputFilenameCSV1
        Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                  outputFileLabel='_bar_chart',
                                                  chart_type_list=["bar"],
                                                  chart_title=chart_title,
                                                  column_xAxis_label_var='WordNet ' + noun_verb + ' category',
                                                  hover_info_column_list=hover_label,
                                                  count_var=1)

        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)


    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running WordNet (Zoom OUT/UP) at', True)
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
