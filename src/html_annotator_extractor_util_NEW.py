"""
    Read in html file with words previously annotated
    gather text between annotation tags
    output aggregate data to cvs table
    by Jack Hester, July 18, 2019
    rewritten by Roberto Franzosi, Zhangyi Pan, Spring 2020
"""

import sys

import GUI_IO_util
import IO_files_util
import charts_util
import IO_libraries_util
import IO_user_interface_util

if IO_libraries_util.install_all_packages("html_annotator_extractor_util",['os','tkinter','re','csv','ntpath'])==False:
    sys.exit(0)

import re
import os
import csv
import ntpath
from Stanza_functions import stanzaPipeLine, sent_tokenize_stanza

import GUI_util

# Optional routine to clean any places where a duplicate tag emerged on accident
# Takes in text to check and list of tags to check duplicates/triplicates, etc.
# Checks up to 10x occurring, allows occurring once
def cleanMultipleTags(text, tags):
    sorted_tags = sorted(tags, key=len)
    for tag in sorted_tags:
        for n in range(2, 11):
            text = text.replace(n*tag, '')
    return text

# Take in html files, find tagged words and extract them
# Tags require a list of two strings in the form ['openingTag','closingTag']
# mustInclude means that the tag must appear in the line (to avoid headers/extra paragraphs)
def gatherAnnotations(inputFile, tags, mustInclude='<p>', cleanMultiples=True):
    openingTag, closingTag = tags[0], tags[1]
    starts, ends, words = [], [], []

    # text = (open(inputFil, "r", encoding="utf-8", errors='ignore').read())
    text = (open(inputFile, "r", encoding="utf-8", errors='ignore').read())
    # split into sentences
    # sentences = nltk.sent_tokenize(text)
    sentences = sent_tokenize_stanza(stanzaPipeLine(text))
    #for each_sentence in sentences:
    Sentence_ID = 0
    sentence_cleaned=''
    for sentence in sentences:
        Sentence_ID += 1
        # TODO sentence should be cleaned, using cleanMultipleTags?
        # sentence_cleaned
    # with open(inputFile, 'r',encoding='utf-8',errors='ignore') as f:
    #     for line in f.readlines():
        if mustInclude in sentence:
            if cleanMultiples==True:
                print("sentence BEFORE CLEAN",sentence)                
                sentence = cleanMultipleTags(sentence, tags)
                print("sentence AFTER CLEAN",sentence)                
            for tag in re.finditer(openingTag, sentence):
                starts.append(tag.end())
                print("ends",tag.end())
            for tag in re.finditer(closingTag, sentence):
                ends.append(tag.start())
                print("starts",tag.start())
            for i in range(0, min(len(ends),len(starts))):
                #words.append(line[starts[i]:ends[i]])
                words.extend([Sentence_ID,sentence_cleaned, sentence[starts[i]:ends[i]]])
        starts, ends = [],[]
    words = [w for w in words if w!='']
    if openingTag!='">' and closingTag!='</a':
        result=[]
        for word in words:
            #result.append(word.split('>',1)[1])
            result.extend([Sentence_ID,sentence_cleaned,word.split('>',1)[1]])
            print('result',result)
    else:
        result=words,Sentence_ID,sentence_cleaned
        print('result ELSE',result)
    return result
        

def buildcsv(inputHTMLFile, inputHTMLFolder, outputDir,openOutputFiles,createCharts, chartPackage):
    filesToOpen=[]
    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running html annotator extractor at', True, "You can follow html annotation extractor in command line.")

    outputFilename=IO_files_util.generate_output_file_name('DBpedia annotations', outputDir, '.csv', 'html extractor', '', '')
    filesToOpen.append(outputFilename)
    annotatedHtmlFiles = []

    annotatedHtmlFiles=IO_files_util.getFileList(inputHTMLFile, inputHTMLFolder, '.html')
    nFile=len(annotatedHtmlFiles)

    if nFile==0:
        return
    i=0

    csvFile=os.path.join(outputDir, outputFilename)
    writeCSV = IO_files_util.openCSVFile(csvFile, 'w')
    if writeCSV=='':
        return
    writer = csv.writer(writeCSV)
    writer.writerow(['Word','Annotation Type','Sentence ID','Sentence','Document ID','Document'])
    # TODO Add document ID and sentence
    for file in annotatedHtmlFiles:
        # examples of how sentence is constructed are in def dataframe_byNER in Stanford_CoreNLP_NER_extractor_util.py
        # from nltk import tokenize
        # IO_libraries_util.import_nltk_resource(GUI_util.window, 'tokenizers/punkt', 'punkt')
        # with open(os.path.join(folder, filename), 'r', encoding='utf-8', errors='ignore') as src:
        #     text = src.read().replace("\n", " ")
        # sentences = tokenize.sent_tokenize(text)

        i=i+1
        print("Processing html annotated file " + str(i) + "/" + str(nFile), file)
        DBpediaWordList = gatherAnnotations(file, ['">',"</a"],'',False)
        dictionaryWordList = gatherAnnotations(file, ['<span',"</span>"],'',True)
        fileName = ntpath.basename(file)
        print("DBpediaWordList",DBpediaWordList)
        # for word in DBpediaWordList:
        # print("fileName, DBpediaWordList[0], DBpediaWordList[1], DBpediaWordList[2],'DBpedia'",fileName, DBpediaWordList[0], DBpediaWordList[1], DBpediaWordList[2],'DBpedia')
        writer.writerow([ y[1] for x in DBpediaWordList for y in x ])
        # for j in len(DBpediaWordList):
        #     writer.writerow([fileName, DBpediaWordList[0], DBpediaWordList[1], DBpediaWordList[2],'DBpedia'])
        #     #writer.writerow([fileName, word,'DBpedia'])
        for word in dictionaryWordList:
            writer.writerow([fileName, Sentence_ID, sentence, word,'Dictionary'])

        # combinedList=[]
        # for word in dictionaryWordList:
        #     if word in DBpediaWordList:
        #         combinedList.append(word)
        # for word in dictionaryWordList:
        #     if word not in combinedList:
        #         writer.writerow([fileName, word,'','X'])
        # for word in DBpediaWordList:
        #     if word not in combinedList:
        #         writer.writerow([fileName, word,'X',''])
        # for word in combinedList:
        #     writer.writerow([fileName, word,'X','X'])

    writeCSV.close()

    # if createCharts==True:
    #     chartTitle='HTML extractor'
    #     columns_to_be_plotted = [2,2]
    #     hover_label=['']
    #     chartType='bar'
    #     fileNameType='html_extr'
    #     chart_outputFilename_1 = charts_util.run_all(columns_to_be_plotted, csvFile, outputDir, csvFile, chart_type_list=[chartType], chart_title=chartTitle, column_xAxis_label_var='', column_yAxis_label_var='Frequencies', outputExtension = '.xlsm', label1=fileNameType,label2=chartType,label3='chart',label4='',label5='', useTime=False,disable_suffix=True,  count_var=1, column_yAxis_field_list = [], reverse_column_position_for_series_label=False , series_label_list=[], second_y_var=0, second_yAxis_label='', hover_info_column_list=hover_label)
    #     if chart_outputFilename_1 != "":
    #         filesToOpen.append(chart_outputFilename_1)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running html annotator extractor at', True, '', True, startTime, True)
    
    if openOutputFiles==True :
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

# Testing program
def main():
    buildcsv('test', 'test')

if __name__ == '__main__':
    main()
