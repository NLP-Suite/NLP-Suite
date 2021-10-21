import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"sentence_analysis_util",['nltk','csv','tkinter','os','collections','subprocess','textstat','itertools','ast'])==False:
    sys.exit(0)

import tkinter as tk
import tkinter.messagebox as mb
import collections
from collections import Counter
import os
import csv
import nltk
from nltk import tokenize
from nltk import word_tokenize
# from gensim.utils import lemmatize
from itertools import groupby
import pandas as pd
import ast
import textstat
import subprocess

import Excel_util
import IO_csv_util
import IO_files_util
import IO_user_interface_util
import Excel_util
import statistics_csv_util
import TIPS_util

def Extract(lst):
    return [item[0] for item in lst]

def dictionary_items_bySentenceID(window,inputFilename,inputDir, outputDir,createExcelCharts,openOutputFiles=True,input_dictionary_file='',chartTitle=''):
    filesToOpen=[]
    DictionaryList=[]
    file_list = IO_files_util.getFileList(inputFilename, inputDir, '.txt')
    nFile=len(file_list)
    if nFile==0:
        return
    # when running the function w/o a GUI, as currently is mostly the case,
    #   we would not be able to pass a dictionary file to the function
    if input_dictionary_file=='':
        initialFolder = os.path.dirname(os.path.abspath(__file__))
        input_dictionary_file = tk.filedialog.askopenfilename(title = "Select dictionary csv file", initialdir = initialFolder, filetypes = [("csv files", "*.csv")])
        if len(input_dictionary_file)==0:
            return

    if IO_csv_util.get_csvfile_numberofColumns(input_dictionary_file) == 2:
        dic = pd.read_csv(input_dictionary_file)
        dic_value = dic.iloc[:,0].tolist()
        dic_sec_value = dic.iloc[:,1].tolist()
        dic =[(dic_value[i],dic_sec_value[i])for i in range(len(dic_value))]
        if chartTitle=='':
            chartTitle="Dictionary value"
        documentID = 0
        container = []
        for file in file_list:
            documentID+=1
            head, tail = os.path.split(file)
            print("Processing file ", str(documentID),"\\",str(nFile),tail)
            text = (open(file, "r", encoding="utf-8",errors='ignore').read())
            #Process each word in txt
            Sentence_ID = 0
            sentences = tokenize.sent_tokenize(text)
            # word  frequency sentenceID DocumentID FileName
            for each_sentence in sentences:
                In = []
                Sentence_ID += 1
                token=nltk.word_tokenize(each_sentence)
                for word in token:
                    for dict_word in dic:
                        if word == dict_word[0].rstrip():
                            In.append([word,dict_word[1],Sentence_ID,each_sentence,documentID,file])
                            break
                        else:
                            continue
                container.extend(In)

            ctr = collections.Counter(Extract(container))
            for word in container:
                word.insert(2,ctr.get(word[0]))
            for word in container:
                if word[0] not in Extract(DictionaryList):
                    DictionaryList.append(word)

            DictionaryList.insert(0, ['Dict_value','Dict_second_value', 'Frequency', 'SentenceID','Sentence','documentID','fileName'])
    else:
        dic = pd.read_csv(input_dictionary_file)
        dic_value = dic.iloc[:, 0].tolist()
        if chartTitle == '':
            chartTitle = "Dictionary value"
        documentID = 0
        container = []
        for file in file_list:
            documentID += 1
            head, tail = os.path.split(file)
            print("Processing file ", str(documentID), "\\", str(nFile), tail)
            text = (open(file, "r", encoding="utf-8", errors='ignore').read())
            # Process each word in txt
            Sentence_ID = 0
            sentences = tokenize.sent_tokenize(text)
            # word  frequency sentenceID DocumentID FileName
            for each_sentence in sentences:
                In = []
                Sentence_ID += 1
                token = nltk.word_tokenize(each_sentence)
                for word in token:
                    for dict_word in dic_value:
                        if word == dict_word.rstrip():
                            In.append([word, Sentence_ID, each_sentence, documentID, file])
                            break
                        else:
                            continue
                container.extend(In)

            ctr = collections.Counter(Extract(container))
            for word in container:
                word.insert(1, ctr.get(word[0]))
            for word in container:
                if word[0] not in Extract(DictionaryList):
                    DictionaryList.append(word)

            DictionaryList.insert(0, ['Dict_value', 'Frequency', 'SentenceID', 'Sentence',
                                      'documentID', 'fileName'])

        outputFilename=IO_files_util.generate_output_file_name(file, inputDir, outputDir, '.csv', str(Sentence_ID) + '-Dict_value', 'stats', '', '', '', False, True)
        filesToOpen.append(outputFilename)
        IO_csv_util.list_to_csv(window,DictionaryList,outputFilename)
        outputFilename=IO_files_util.generate_output_file_name(file, inputDir, outputDir, '.xlsx', str(Sentence_ID) + '-Dict_value', 'chart', '', '', '', False, True)
        filesToOpen.append(outputFilename)
        Excel_util.create_excel_chart(GUI_util.window,[DictionaryList],outputFilename,chartTitle,["bar"])

    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

# written by Yi Wang April 2020
# ConnlTable is the inputFilename
def Wordnet_bySentenceID(ConnlTable, wordnetDict,outputFilename,outputDir,noun_verb,openOutputFiles,createExcelCharts):
    filesToOpen=[]
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running WordNet charts by sentence index at', True)
    if noun_verb=='NOUN':
        checklist = ['NN','NNP','NNPS','NNS']
    else:
        checklist = ['VB','VBD','VBG','VBN','VBP','VBZ']
    # read in the CoreNLP CoNLL table
    connl = pd.read_csv(ConnlTable)
    # read in the dictionary file to be used to filter CoNLL values
    # The file is expected to have 2 columns with headers: Word, WordNet Category
    try:
        dict = pd.read_csv(wordnetDict)
    except:
        mb.showwarning("Warning", "The file \n\n" + wordnetDict + "\n\ndoes not have the expected 2 columns: Word, WordNet Category. You may have selected the wrong input file.\n\nPlease, select the right input file and try again.")
        return
    # set up the double list conll from the conll data
    try:
        connl = connl[['Form','Lemma','POStag','Sentence ID','Document ID','Document']]
    except:
        mb.showwarning("Warning",
                       "The file \n\n" + ConnlTable + "\n\ndoes not appear to be a CoNLL table with expected column names: Form,Lemma,Postag, SentenceID, DocumentID, Document.\n\nPlease, select the right input file and try again.")
        return
    # filter the list by noun or verb
    connl = connl[connl['Postag'].isin(checklist)]
    # eliminate any duplicate value in Word (Form))
    dict = dict.drop_duplicates().rename(columns = {'Word':'Lemma', 'WordNet Category':'Category'})
    # ?
    connl = connl.merge(dict,how = 'left', on = 'Lemma')
    # the CoNLL table value is not found in the dictionary Word value
    connl.fillna('Not in INPUT dictionary for ' + noun_verb, inplace = True)
    # add the WordNet category to the conll list
    connl = connl[['Form','Lemma','POStag','Category','Sentence ID','Document ID','Document']]
    # put headers on conll list
    connl.columns = ['Form','Lemma','POStag','Category','Sentence ID','Document ID','Document']

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
    df = pd.DataFrame(Row_list,index=['Form','Lemma','POStag','WordNet Category','Sentence ID','Document ID','Document'])
    df = Excel_util.add_missing_IDs(df)
    df.to_csv(outputFilename,index=False)

    if createExcelCharts:
        outputFiles=Excel_util.compute_csv_column_frequencies(GUI_util.window,
                                                 ConnlTable,
                                                 df,
                                                 outputDir,
                                                 openOutputFiles,
                                                 createExcelCharts,
                                                 [[4,5]],
                                                 ['WordNet Category'],['Form'], ['Document ID','Sentence ID','Document'],
                                                )
        if len(outputFiles) > 0:
            filesToOpen.extend(outputFiles)
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running WordNet charts by sentence index at', True)

    return filesToOpen

def extract_sentence_length(inputFilename, inputDir, outputDir):
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    Ndocs = len(inputDocs)
    if Ndocs==0:
        return
    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                       'Started running sentence length computation at', True, 'You can follow Geocoder in command line.')

    fileID=0
    long_sentences = 0
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                     'sentence_length')
    csv_headers=['Document ID','Sentence ID','Sentence length (in words)','Sentence','Document']

    with open(outputFilename, 'w', newline = "", encoding='utf-8', errors='ignore') as csvOut:
        writer = csv.writer(csvOut)
        writer.writerow(csv_headers)
        for doc in inputDocs:
            sentenceID = 0
            fileID = fileID + 1
            head, tail = os.path.split(doc)
            print("Processing file " + str(fileID) + "/" + str(Ndocs) + ' ' + tail)
            with open(doc, 'r', encoding='utf-8', errors='ignore') as inputFile:
                text = inputFile.read().replace("\n", " ")
                sentences = tokenize.sent_tokenize(text)
                for sentence in sentences:
                    tokens = nltk.word_tokenize(sentence)
                    if len(tokens)>100:
                        long_sentences=long_sentences+1
                    sentenceID=sentenceID+1
                    writer.writerow([fileID,sentenceID,len(tokens),sentence,IO_csv_util.dressFilenameForCSVHyperlink(doc)])
        csvOut.close()
        answer = tk.messagebox.askyesno("TIPS file on memory issues",str(Ndocs) + " file(s) processed in input.\n\n"+
                    "Output csv file written to the output directory "+outputDir + "\n\n"+
                   str(long_sentences) + " SENTENCES WERE LONGER THAN 100 WORDS (the average sentence length in modern English is 20 words).\n\nMore to the point... Stanford CoreNLP would heavily tax memory resources with such long sentences.\n\nYou should consider editing these sentences if Stanford CoreNLP takes too long to process the file or runs out of memory.\n\nPlease, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.\n\nDo you want to open the TIPS file now?")
        if answer:
            TIPS_util.open_TIPS('TIPS_NLP_Stanford CoreNLP memory issues.pdf')
    return [outputFilename]

# wordList is a string
def extract_sentences(input_file, input_dir, output_dir, inputString):
    inputDocs = IO_files_util.getFileList(input_file, input_dir, fileType='.txt')
    Ndocs = len(inputDocs)
    if Ndocs==0:
        return

    # Win/Mac may use different quotation, we replace any directional quotes to straight ones
    right_double = u"\u201C"  # “
    left_double = u"\u201D"  # ”
    straight_double = u"\u0022"  # "
    if (right_double in inputString) or (left_double in inputString):
        inputString = inputString.replace(right_double, straight_double)
        inputString = inputString.replace(left_double, straight_double)
    if inputString.count(straight_double) == 2:
        # Append ', ' to the end of search_words_var so that literal_eval creates a list
        inputString += ', '
    # convert the string inputString to a list []
    wordList=ast.literal_eval(inputString)
    caseSensitive = mb.askyesno("Python", "Do you want to process your search word(s) as case sensitive?")

    fileID=0
    file_extract_written = False
    file_extract_minus_written = False
    nDocsExtractOutput = 0
    nDocsExtractMinusOutput = 0
    for doc in inputDocs:
        outputFilename_extract=doc[:-4]+"_extract.txt"
        outputFilename_extract_minus=doc[:-4]+"_extract_minus.txt"
        wordFound = False
        fileID = fileID + 1
        head, tail = os.path.split(doc)
        print("Processing file " + str(fileID) + "/" + str(Ndocs) + ' ' + tail)
        with open(doc, 'r', encoding='utf-8', errors='ignore') as inputFile:
            text = inputFile.read().replace("\n", " ")
        with open(outputFilename_extract, 'w', encoding='utf-8', errors='ignore') as outputFile_extract, open(outputFilename_extract_minus, 'w', encoding='utf-8', errors='ignore') as outputFile_extract_minus:
            sentences = tokenize.sent_tokenize(text)
            for sentence in sentences:
                sentenceSV = sentence
                nextSentence = False
                for word in wordList:
                    if nextSentence == True:
                        # go to next sentence; do not write the same sentence several times if it contains several words in wordList
                        break
                    if caseSensitive == False:
                        sentenceSV=sentence
                        sentence = sentence.lower()
                        word = word.lower()
                    if word in sentence:
                        outputFile_extract.write(sentenceSV+" ") #write out original sentence
                        file_extract_written = True
                        wordFound=True
                        nextSentence = True
                    # if none of the words in wordList are found in a sentence write the sentence to the extract_minus file
                    if wordFound == False:
                        outputFile_extract_minus.write(sentenceSV + " ")  # write out original sentence
                        file_extract_minus_written = True
        if file_extract_written == True:
            filesToOpen.append(outputFilename_extract)
            nDocsExtractOutput += 1
            file_extract_written = False
        outputFile_extract.close()
        if file_extract_minus_written:
            filesToOpen.append(outputFilename_extract_minus)
            nDocsExtractMinusOutput += 1
            file_extract_minus_written = False
        outputFile_extract_minus.close()
    if Ndocs==1:
        msg1=str(Ndocs) + " file was"
    else:
        msg1=str(Ndocs) + " files were"
    if nDocsExtractOutput == 1:
        msg2=str(nDocsExtractOutput) + " file was"
    else:
        msg2 = str(nDocsExtractOutput) + " files were"
    if nDocsExtractMinusOutput == 1:
        msg3=str(nDocsExtractMinusOutput) + " file was"
    else:
        msg3 = str(nDocsExtractMinusOutput) + " files were"
    mb.showwarning("Warning",msg1+ " processed in input.\n\n"+
                    msg2 + " written with _extract in the filename.\n\n" +
                    msg3 + " written with _extract_minus in the filename.\n\n" +
                    "Files were written to the output directory "+output_dir+
                   "\n\nPlease, check the output directory for filenames ending with _extract.txt and _extract_minus.txt.")

def sentence_complexity(window, inputFilename, inputDir, outputDir, openOutputFiles, createExcelCharts):
    filesToOpen = []

    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, '.txt')
    Ndocs = len(inputDocs)
    if Ndocs == 0:
        return
    if IO_libraries_util.inputProgramFileCheck('Sentence_Complexity.Jar') == False:
        mb.showwarning("Warning",
                       "The java algorithm for sentence cmplexity is no longer available. Taking up over 1.5 GB of disk space it was not easy to download.\n\nThe algorithms will be rewritten in Python as soon as possible. Sorry!\n\nPlease, check back soon.")
        return

    errorFound, error_code, system_output = IO_libraries_util.check_java_installation('Sentence complexity')
    if errorFound:
        return

    IO_user_interface_util.timed_alert(window, 2000, 'Analysis start', 'Started running Sentence Complexity at', True,
                                       '\n\nYou can follow Sentence Complexity in command line.')

    index = 0
    output_csv = []

    for doc in inputDocs:
        index += 1
        head, tail = os.path.split(doc)
        print("Processing file " + str(index) + "/" + str(Ndocs) + ' ' + tail)
        outputFilename = IO_files_util.generate_output_file_name(doc, '', outputDir, '.csv', 'SentComp', '', '')

        # the output filename passed to jar file MUST be a filename without path
        temp_outputFilename = os.path.basename(outputFilename)

        subprocess.call(['java', '-jar', 'Sentence_Complexity.Jar', doc, outputDir, temp_outputFilename])
        # Need to use the full path when modifying the now created CSV data
        output_csv.append(outputFilename)
        # Add document_ID to the csv file that was just created
        try:
            temp_csv = pd.read_csv(outputFilename, encoding='utf-8')
        except:
            try:
                temp_csv = pd.read_csv(outputFilename, encoding='latin')
            except:
                print(
                    "Warning! Could not find a proper encoding (utf-8 or latin) for the csv file " + temp_outputFilename + "\n\nFile not merged in output.")
                continue
        temp_csv.insert(loc=0, column='Document ID', value=index)
        temp_csv.to_csv(outputFilename, index=False)

    # Combine all CSV files when processing an input dir
    # https://github.com/ekapope/Combine-CSV-files-in-the-folder/blob/master/Combine_CSVs.py
    if inputDir != '':
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'SentComp',
                                                                        '', '')
        try:
            combined_data = pd.concat([pd.read_csv(f) for f in output_csv])
        except:
            mb.showwarning("Fatal error",
                           "An error was encountered in merging the " + str(Ndocs) + " individual csv files of sentence complexity. Please, use R to merge the csv files containing the sentence complexity scores for each sentence of each input txt file saved in the output directory " + outputDir)
            return
        combined_data.to_csv(outputFilename, index=False, encoding='utf-8')
        # Delete the individual CSV files
        for f in output_csv:
            os.unlink(f)
        # # Add to files to open
        filesToOpen.append(outputFilename)
        mb.showwarning(title='Warning',
                       message='The sentence complexity algorithm will NOT produce the 3 expected Excel line charts of sentence complexity scores by sentence index for the ' + str(
                           Ndocs) + ' files processed since this would produce too many files in output.')
        return filesToOpen

    IO_user_interface_util.timed_alert(window, 2000, 'Analysis end', 'Finished running Sentence Complexity at', True)

    if createExcelCharts:
        hover_label = ['Sentence']
        # sentence length
        columns_to_be_plotted = [[2, 4]]

        Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                  outputFileLabel='SentComp',
                                                  chart_type_list=["line"],
                                                  chart_title='Sentence Length (in Number of Words) by Sentence Index',
                                                  column_xAxis_label_var='Sentence index',
                                                  hover_info_column_list=hover_label,
                                                  count_var=0,
                                                  column_yAxis_label_var='Complexity (sentence length in number of words)')
        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)

        # outputFilenameXLSM_1 = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
        # outputFilename,
        #                                           chart_type_list=["line"],
        #                                           chart_title="Sentence Length (in Number of Words) by Sentence Index",
        #                                           column_xAxis_label_var='Sentence index',
        #                                           column_yAxis_label_var='Complexity (sentence length in number of words)',
        #                                           outputExtension='.xlsm', label1='SentComp', label2='SentLen',
        #                                           label3='line', label4='chart', label5='', useTime=False,
        #                                           disable_suffix=True,  count_var=0,
        #                                           column_yAxis_field_list=[],
        #                                           reverse_column_position_for_series_label=False,
        #                                           series_label_list=[''], second_y_var=0, second_yAxis_label='',
        #                                           hover_var=1, hover_info_column_list=hover_label)
        # if outputFilenameXLSM_1 != "":
        #     filesToOpen.append(outputFilenameXLSM_1)

        hover_label = ['Sentence', 'Sentence']
        # Yngve and Frazier scores
        columns_to_be_plotted = [[2, 5], [2, 7]]

        Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                  outputFileLabel='SentComp',
                                                  chart_type_list=["line"],
                                                  chart_title='"Sentence Complexity (Yngve and Frazier Scores by Sentence Index)',
                                                  column_xAxis_label_var='Sentence index',
                                                  hover_info_column_list=hover_label,
                                                  count_var=0,
                                                  column_yAxis_label_var='Complexity score')
        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)


        # outputFilenameXLSM_2 = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir, outputFilename,
        #                                           chart_type_list=["line"],
        #                                           chart_title="Sentence Complexity (Yngve and Frazier Scores by Sentence Index)",
        #                                           column_xAxis_label_var='Sentence index',
        #                                           column_yAxis_label_var='Complexity score', outputExtension='.xlsm',
        #                                           label1='SentComp', label2='scores', label3='line', label4='chart',
        #                                           label5='', useTime=False, disable_suffix=True,
        #                                            count_var=0,
        #                                           column_yAxis_field_list=[],
        #                                           reverse_column_position_for_series_label=False,
        #                                           series_label_list=[''], second_y_var=0, second_yAxis_label='',
        #                                           hover_var=1, hover_info_column_list=hover_label)
        # if outputFilenameXLSM_2 != "":
        #     filesToOpen.append(outputFilenameXLSM_2)
        # Yngve and Frazier sums
        columns_to_be_plotted = [[2, 6], [2, 8]]

        Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                  outputFileLabel='SentComp',
                                                  chart_type_list=["line"],
                                                  chart_title='"Sentence Complexity (Yngve and Frazier Sums by Sentence Index)',
                                                  column_xAxis_label_var='Sentence index',
                                                  hover_info_column_list=hover_label,
                                                  count_var=0,
                                                  column_yAxis_label_var='Complexity sum')
        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)

        # outputFilenameXLSM_3 = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir, outputFilename,
        #                                           chart_type_list=["line"],
        #                                           chart_title="Sentence Complexity (Yngve and Frazier Sums by Sentence Index)",
        #                                           column_xAxis_label_var='Sentence index',
        #                                           column_yAxis_label_var='Complexity sum', outputExtension='.xlsm',
        #                                           label1='SentComp', label2='sums', label3='line', label4='chart',
        #                                           label5='', useTime=False, disable_suffix=True,
        #                                            count_var=0,
        #                                           column_yAxis_field_list=[],
        #                                           reverse_column_position_for_series_label=False,
        #                                           series_label_list=[''], second_y_var=0, second_yAxis_label='',
        #                                           hover_var=1, hover_info_column_list=hover_label)
        # if outputFilenameXLSM_3 != "":
        #     filesToOpen.append(outputFilenameXLSM_3)

    if len(inputDir) != 0:
        mb.showwarning(title='Warning',
                       message='The output filenames generated by Textstat readability contain the name of the directory processed in input, rather than the name of any individual file in the directory.\n\nBoth txt & csv files include all ' + str(
                           nFile) + ' files in the input directory processed by Textstat.')
    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(window, openOutputFiles, filesToOpen)


# https://pypi.org/project/textstat/
def sentence_text_readability(window, inputFilename, inputDir, outputDir, openOutputFiles, createExcelCharts):
    filesToOpen = []
    documentID = 0

    files = IO_files_util.getFileList(inputFilename, inputDir, '.txt')
    nFile = len(files)
    if nFile == 0:
        return

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running Text Readability at',
                                       True, '\n\nYou can follow Text Readability in command line.')

    if nFile > 1:
        outputFilenameTxt = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.txt', 'READ',
                                                                    'stats')
        outputFilenameCsv = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'READ',
                                                                    'stats')
    else:
        outputFilenameTxt = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.txt', 'READ',
                                                                    'stats')
        outputFilenameCsv = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'READ',
                                                                    'stats')
    filesToOpen.append(outputFilenameTxt)
    filesToOpen.append(outputFilenameCsv)

    fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence',
                  'Flesch Reading Ease formula',
                  'Flesch-Kincaid Grade Level',
                  'Fog Scale (Gunning FOG Formula)',
                  'SMOG (Simple Measure of Gobbledygook) Index',
                  'Automated Readability Index',
                  'Coleman-Liau Index',
                  'Linsear Write Formula',
                  'Dale-Chall Readability Score',
                  'Overall readability consensus',
                  'Grade level']

    with open(outputFilenameCsv, 'w', encoding='utf-8', errors='ignore', newline='') as outputCsvFile:
        writer = csv.DictWriter(outputCsvFile, fieldnames=fieldnames)
        writer.writeheader()

        # already shown in NLP.py
        # IO_util.timed_alert(GUI_util.window,3000,'Analysis start','Started running NLTK unusual words at',True,'You can follow NLTK unusual words in command line.')

        # open txt output file
        outputTxtFile = open(outputFilenameTxt, "w")
        documentID = 0
        for file in files:
            # read txt file
            text = (open(file, "r", encoding="utf-8", errors="ignore").read())

            documentID = documentID + 1
            head, tail = os.path.split(file)
            print("Processing file " + str(documentID) + "/" + str(nFile) + ' ' + tail)

            # write text files ____________________________________________

            outputTxtFile.write("TEXT READABILITY SCORES (by Python library textstat)" + "\n\n")
            outputTxtFile.write(file + "\n\n")

            # This legenda is now available as a TIPS file
            # outputTxtFile.write ("LEGENDA -----------------------------------------------------------------------------------------------------------------------------------------------\n\n")
            # outputTxtFile.write ("Text readability measures the understandability of a text.\n")
            # outputTxtFile.write ("The different measures of readability map on the U.S grade level (1 through 12) needed to comprehend a text.\n\n  12 readability score requires HIGHSCHOOL education;\n  16 readability score requires COLLEGE education;\n  18 readability score requires MASTER education;\n  24 readability score requires DOCTORAL education;\n  >24 readability score requires POSTDOC education.\n\n")

            # outputTxtFile.write ("Automated Readability Index (ARI) outputs a number that approximates the grade level needed to comprehend the text. For example if the ARI is 6.5, then the grade level to comprehend the text is 6th to 7th grade.\n\n")
            # outputTxtFile.write ("Coleman-Liau Index, Linsear Write Formula, Flesch-Kincaid Grade, SMOG index, Fog Scale (Gunning FOG Formula) are grade formula in that a score of 9.3 means that a ninth grader would be able to read the document.\n\n")

            # outputTxtFile.write ("The Flesch Reading Ease formula has the following range of values (the maximum score is 121.22; there is no limit on how low the score can be, with a negative score being valid):\n")
            # outputTxtFile.write ("  0-30 College\n")
            # outputTxtFile.write ("  50-60 High School\n")
            # outputTxtFile.write ("  90-100 Fourth Grade\n\n")

            # outputTxtFile.write ("The Dale-Chall index has the following range of values (different from other tests, since it uses a lookup table of the most commonly used 3000 English words and returns the grade level using the New Dale-Chall Formula):\n")
            # outputTxtFile.write ("  4.9 or lower    easily understood by an average 4th-grade student or lower\n")
            # outputTxtFile.write ("  5.0–5.9 easily understood by an average 5th or 6th-grade student\n")
            # outputTxtFile.write ("  6.0–6.9 easily understood by an average 7th or 8th-grade student\n")
            # outputTxtFile.write ("  7.0–7.9 easily understood by an average 9th or 10th-grade student\n")
            # outputTxtFile.write ("  8.0–8.9 easily understood by an average 11th or 12th-grade student\n")
            # outputTxtFile.write ("  9.0–9.9 easily understood by an average 13th to 15th-grade (college) student\n\n")

            outputTxtFile.write(
                "RESULTS -----------------------------------------------------------------------------------------------------------------------------------------------\n\n")
            # Syllable count
            str1 = "Syllable count " + str(textstat.syllable_count(text, lang='en_US'))
            outputTxtFile.write(str1 + "\n")
            # print("\n\nSyllable count ",textstat.syllable_count(text, lang='en_US'))
            # Lexicon count
            str1 = "Lexicon count " + str(textstat.lexicon_count(text, removepunct=True))
            outputTxtFile.write(str1 + "\n")
            # print("Lexicon count ",textstat.lexicon_count(text, removepunct=True))
            # Sentence count
            str1 = "Sentence count " + str(textstat.sentence_count(text))
            outputTxtFile.write(str1 + "\n\n")
            # print("Sentence count ",textstat.sentence_count(text))

            # The Flesch Reading Ease formula
            str1 = "Flesch Reading Ease formula " + str(textstat.flesch_reading_ease(text))
            outputTxtFile.write(str1 + "\n")
            # print("Flesch Reading Ease formula",textstat.flesch_reading_ease(text))
            # The Flesch-Kincaid Grade Level
            str1 = "Flesch-Kincaid Grade Level " + str(textstat.flesch_kincaid_grade(text))
            outputTxtFile.write(str1 + "\n")
            # print("Flesch-Kincaid Grade Level",textstat.flesch_kincaid_grade(text))
            # The Fog Scale (Gunning FOG Formula)
            str1 = "Fog Scale (Gunning FOG Formula) " + str(textstat.gunning_fog(text))
            outputTxtFile.write(str1 + "\n")
            # print("Fog Scale (Gunning FOG Formula)",textstat.gunning_fog(text))
            # The SMOG Index
            str1 = "SMOG (Simple Measure of Gobbledygook) Index " + str(textstat.smog_index(text))
            outputTxtFile.write(str1 + "\n")
            # print("SMOG (Simple Measure of Gobbledygook) Index",textstat.smog_index(text))
            # Automated Readability Index
            str1 = "Automated Readability Index " + str(textstat.automated_readability_index(text))
            outputTxtFile.write(str1 + "\n")
            # print("Automated Readability Index",textstat.automated_readability_index(text))
            # The Coleman-Liau Index
            str1 = "Coleman-Liau Index " + str(textstat.coleman_liau_index(text))
            outputTxtFile.write(str1 + "\n")
            # print("Coleman-Liau Index",textstat.coleman_liau_index(text))
            # Linsear Write Formula
            str1 = "Linsear Write Formula " + str(textstat.linsear_write_formula(text))
            outputTxtFile.write(str1 + "\n")
            # print("Linsear Write Formula",textstat.linsear_write_formula(text))
            # Dale-Chall Readability Score
            str1 = "Dale-Chall Readability Score " + str(textstat.dale_chall_readability_score(text))
            outputTxtFile.write(str1 + "\n")
            # print("Dale-Chall Readability Score",textstat.dale_chall_readability_score(text))
            # Readability Consensus based upon all the above tests
            str1 = "\n\nReadability Consensus Level based upon all the above tests: " + str(
                textstat.text_standard(text, float_output=False) + '\n\n')
            outputTxtFile.write(str1 + "\n")
            # print("\n\nReadability Consensus based upon all the above tests: ",textstat.text_standard(text, float_output=False))

            # write csv files ____________________________________________

            # split into sentences
            sentences = nltk.sent_tokenize(text)
            # analyze each sentence in text for readability
            sentenceID = 0  # to store sentence index
            for sent in sentences:
                sentenceID = sentenceID + 1
                # Flesch Reading Ease formula
                str1 = str(textstat.flesch_reading_ease(sent))
                # The Flesch-Kincaid Grade Level
                str2 = str(textstat.flesch_kincaid_grade(sent))
                # Th3 Fog Scale (Gunning FOG Formula)
                str3 = str(textstat.gunning_fog(sent))
                # The SMOG Index
                str4 = str(textstat.smog_index(sent))
                # Automated Readability Index
                str5 = str(textstat.automated_readability_index(sent))
                # The Coleman-Liau Index
                str6 = str(textstat.coleman_liau_index(sent))
                # Linsear Write Formula
                str7 = str(textstat.linsear_write_formula(sent))
                # Dale-Chall Readability Score
                str8 = str(textstat.dale_chall_readability_score(sent))
                # Overal summary measure
                str9 = str(textstat.text_standard(sent, float_output=False))
                if str9 == "-1th and 0th grade":
                    sortOrder = 0
                elif str9 == "0th and 1st grade":
                    sortOrder = 1
                elif str9 == "1st and 2nd grade":
                    sortOrder = 2
                elif str9 == "2nd and 3rd grade":
                    sortOrder = 3
                elif str9 == "3rd and 4th grade":
                    sortOrder = 4
                elif str9 == "4th and 5th grade":
                    sortOrder = 5
                elif str9 == "5th and 6th grade":
                    sortOrder = 6
                elif str9 == "6th and 7th grade":
                    sortOrder = 7
                elif str9 == "7th and 8th grade":
                    sortOrder = 8
                elif str9 == "8th and 9th grade":
                    sortOrder = 9
                elif str9 == "9th and 10th grade":
                    sortOrder = 10
                elif str9 == "10th and 11th grade":
                    sortOrder = 11
                elif str9 == "11st and 12th grade":
                    sortOrder = 12
                elif str9 == "12th and 13th grade":
                    sortOrder = 13
                elif str9 == "13th and 14th grade":
                    sortOrder = 14
                elif str9 == "14th and 15th grade":
                    sortOrder = 15
                elif str9 == "15th and 16th grade":
                    sortOrder = 16
                elif str9 == "16th and 17th grade":
                    sortOrder = 17
                elif str9 == "17th and 18th grade":
                    sortOrder = 18
                elif str9 == "18th and 19th grade":
                    sortOrder = 19
                elif str9 == "19th and 20th grade":
                    sortOrder = 20
                elif str9 == "20th and 21st grade":
                    sortOrder = 21
                elif str9 == "21st and 22nd grade":
                    sortOrder = 22
                elif str9 == "22nd and 23rd grade":
                    sortOrder = 23
                elif str9 == "23rd and 24th grade":
                    sortOrder = 24
                else:
                    sortOrder = 25
                # rowValue=[[documentID,file,sentenceID,sent,str1,str2,str3,str4,str5,str6,str7,str8,str9,sortOrder]]
                rowValue = [
                    [documentID, IO_csv_util.dressFilenameForCSVHyperlink(file), sentenceID, sent, str1, str2, str3,
                     str4, str5, str6, str7, str8, str9, sortOrder]]
                writer = csv.writer(outputCsvFile)
                writer.writerows(rowValue)
        # at least 12th grade level HIGH-SCHOOL EDUCATION
        # at least 16th grade level UNDERGRADUATE COLLEGE EDUCATION
        # at least 18th grade level MA EDUCATION
        # at least 24th grade level PhD EDUCATION
        # > 24th grade level PostDoc EDUCATION

        # TODO YI not sure what to pass to the sort function;
        # IO filenames should be computed here
        # outputFilename1=IO_util.generate_output_file_name(inputFilename,outputDir,'.csv','READ','stats1')
        # IO_util.sort_csvFile_by_columns(outputFilenameCsv, outputFilenameCsv, ['Document ID','Sort order'])
        outputTxtFile.close()
        outputCsvFile.close()
        result = True

        # readability
        if createExcelCharts == True:
            result = True
            # if nFile>10:
            #     result = mb.askyesno("Excel charts","You have " + str(nFile) + " files for which to compute Excel charts for each file.\n\nTHIS WILL TAKE A LONG TIME TO PRODUCE.\n\nAre you sure you want to do that?")
            if result == True:
                # 4 (Flesch Reading Ease) has a different scale and 8 (SMOG) is often 0
                columns_to_be_plotted = [[2, 5], [2, 6], [2, 7], [2, 9], [2, 10], [2, 11]]
                hover_label = ['Sentence', 'Sentence', 'Sentence', 'Sentence', 'Sentence', 'Sentence']

                Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilenameCsv, outputDir,
                                                          outputFileLabel='READ',
                                                          chart_type_list=["line"],
                                                          chart_title='Text Readability',
                                                          column_xAxis_label_var='Sentence index',
                                                          hover_info_column_list=hover_label,
                                                          count_var=0,
                                                          column_yAxis_label_var='Readability grade level')
                if Excel_outputFilename != "":
                    filesToOpen.append(Excel_outputFilename)

                # outputFilenameXLSM_1 = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                #                                           outputFilenameCsv, chart_type_list=["line"],
                #                                           chart_title="Text Readability",
                #                                           column_xAxis_label_var='Sentence Index',
                #                                           column_yAxis_label_var='Readability grade level',
                #                                           outputExtension='.xlsm', label1='READ', label2='line',
                #                                           label3='charts', label4='', label5='', useTime=False,
                #                                           disable_suffix=True,
                #                                           count_var=0, column_yAxis_field_list=[],
                #                                           reverse_column_position_for_series_label=False,
                #                                           series_label_list=[''], second_y_var=0, second_yAxis_label='',
                #                                           hover_var=1, hover_info_column_list=hover_label)
                # if outputFilenameXLSM_1 != "":
                #     filesToOpen.append(outputFilenameXLSM_1)

                columns_to_be_plotted = [[2, 13]]
                hover_label = ['Sentence']
                Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilenameCsv, outputDir,
                                                          outputFileLabel='READ',
                                                          chart_type_list=["line"],
                                                          chart_title='Text Readability',
                                                          column_xAxis_label_var='Sentence index',
                                                          hover_info_column_list=hover_label,
                                                          count_var=0,
                                                          column_yAxis_label_var='Readability grade level')
                if Excel_outputFilename != "":
                    filesToOpen.append(Excel_outputFilename)


                # outputFilenameXLSM_2 = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                #                                           outputFilenameCsv, chart_type_list=["line"],
                #                                           chart_title="Text Readability",
                #                                           column_xAxis_label_var='Sentence Index',
                #                                           column_yAxis_label_var='Readability grade level',
                #                                           outputExtension='.xlsm', label1='READ', label2='line',
                #                                           label3='chart', label4='', label5='', useTime=False,
                #                                           disable_suffix=True,
                #                                           count_var=0, column_yAxis_field_list=[],
                #                                           reverse_column_position_for_series_label=False,
                #                                           series_label_list=[''], second_y_var=0, second_yAxis_label='',
                #                                           hover_var=1, hover_info_column_list=hover_label)
                # if outputFilenameXLSM_2 != "":
                #     filesToOpen.append(outputFilenameXLSM_2)

            # bar chart of the frequency of sentences by grade levels
            columns_to_be_plotted = [[0, 12]]
            hover_label = []

            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, outputFilenameCsv, outputDir,
                                                      outputFileLabel='READ',
                                                      chart_type_list=["bar"],
                                                      chart_title='Frequency of Sentences by Readability Consensus of Grade Level',
                                                      column_xAxis_label_var='',
                                                      hover_info_column_list=hover_label,
                                                      count_var=1)
            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

            # outputFilenameXLSM_3 = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
            #                                           outputFilenameCsv, chart_type_list=["bar"],
            #                                           chart_title="Frequency of Sentences by Readability Consensus of Grade Level",
            #                                           column_xAxis_label_var='', column_yAxis_label_var='Frequency',
            #                                           outputExtension='.xlsm', label1='READ', label2='bar',
            #                                           label3='chart', label4='', label5='', useTime=False,
            #                                           disable_suffix=True,
            #                                           count_var=1, column_yAxis_field_list=[],
            #                                           reverse_column_position_for_series_label=False,
            #                                           series_label_list=[''], second_y_var=0, second_yAxis_label='',
            #                                           hover_var=1, hover_info_column_list=hover_label)
            # if outputFilenameXLSM_3 != "":
            #     filesToOpen.append(outputFilenameXLSM_3)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running Text Readability at',
                                       True)

    if len(inputDir) != 0:
        mb.showwarning(title='Warning',
                       message='The output filenames generated by Textstat readability contain the name of the directory processed in input, rather than the name of any individual file in the directory.\n\nBoth txt & csv files include all ' + str(
                           nFile) + ' files in the input directory processed by Textstat.')
    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(window, openOutputFiles, filesToOpen)
