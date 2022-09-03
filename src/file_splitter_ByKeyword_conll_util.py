#!/usr/bin/env Python
# -*- coding: utf-8 -*-
"""
Created on Thu May 28 23:08:58 2020

@author: claude
"""

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_splitter_ByKeyword_conll",['os','tkinter','pandas','stanza'])==False:
    sys.exit(0)

import csv
import os
import pandas as pd

from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza



def run(inputCoNLL, outputPath, keyword, first_occurrence):

    head, table_name = os.path.split(inputCoNLL)
    table_title = table_name.partition('.')[0]
    directory_name = table_title
   
    if "NLP_SCNLP_" in directory_name:     
        directory_name = directory_name.replace('NLP_SCNLP_', '')
    if '_mergedCoNLL' in directory_name:      
        directory_name = directory_name.replace('_mergedCoNLL', '')
    outputPath = head+os.sep+directory_name+"_subfiles&csv"#a directory will be built in the path of input conll table no matter what input outputPath is 
    os.mkdir(outputPath)
    df = pd.read_csv(inputCoNLL, encoding = "ISO-8859-1")#problem of utf-8 enconding when read csv file: 
    #https://stackoverflow.com/questions/18171739/unicodedecodeerror-when-reading-csv-file-in-pandas-with-python
    subfileindex = 1#record the number of subfles generated
    # kwtoken = word_tokenize(keyword)
    kwtoken = word_tokenize_stanza(stanzaPipeLine(keyword))
    keyword_size = len(kwtoken)
    head, output_name = os.path.split(df.iloc[0][11])
    name = output_name.partition('.')[0]
     #record the index of sentence being processed
    subfilePath = outputPath+os.sep+name+"_"+str(subfileindex)+'.txt'
    subfile = open(subfilePath, 'w')
    first_occurrence_id = 0
    frequency = 0
    i = 0#index of token in the conll
    with open(outputPath+'/'+keyword+'.csv', "w",newline = "", encoding='utf-8',errors='ignore') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(["Document ID", "Document", "SEARCH_WORD", "SENTENCE", "Sentence ID of FIRST_OCCURRENCE", "RELATIVE_POSITION", "FREQUENCY of OCCURRENCE"])
        while i < len(df):
            sentenceindex = df.iloc[i][9]
            sameFile = True
            if df.iloc[i][10]!= df.iloc[i-1][10] or i == 0:
                frequency = 0
                subfileindex = 1
                head, output_name = os.path.split(df.iloc[i][11])
                name = output_name.partition('.')[0]
                sameFile = False
                subfilePath = outputPath+os.sep+name+"_"+str(subfileindex)+'.txt'
                s = i+1
                total_length = 1
                while s < len(df) and df.iloc[i][10] == df.iloc[s][10]:
                    s += 1
                    total_length += 1
            sentence_str = ''
            j = i
            while j < len(df) and df.iloc[j][9] == sentenceindex: #build sentence string
                if df.iloc[j][6] == "punct":
                    sentence_str = sentence_str + str(df.iloc[j][1])
                else:
                    sentence_str = sentence_str + " " + str(df.iloc[j][1])
                j = j + 1
            sentence_range = j
            k = i
            while k < sentence_range:
                if sentence_range - k <= keyword_size: #the rest tokens are less than number of tokens in key word
                    subfile.write(sentence_str+" ")
                    k = sentence_range
                else: 
                    kw = False
                    if df.iloc[k][2] == kwtoken[0] and k + keyword_size < sentence_range:#detected first token of the keyword
                        kw = True
                        l = k + 1
                        while l < k+keyword_size:
                            if df.iloc[l][2] != kwtoken[l - k]:#following tokens do not match
                                kw = False
                                pointer = l
                                l = k+keyword_size 
                            else: 
                                l = l + 1#keep tracking
                        if kw: #if the keyword is detected, build a new subfile
                            frequency += 1
                            if frequency == 1:
                                first_occurrence_id = df.iloc[i][9]
                            if first_occurrence == False or sameFile == False:
                                subfileindex += 1
                                subfilePath = outputPath+os.sep+name+"_"+str(subfileindex)+'.txt'
                                subfile = open(subfilePath, 'w')
                                subfile.write(sentence_str+" ")
                            k = sentence_range
                            writer.writerow([df.iloc[i][10], df.iloc[i][11], keyword, sentence_str, first_occurrence_id, df.iloc[i][9] / total_length, frequency])
                        else: 
                            k = l
                    else: k = k+1
            i = k
