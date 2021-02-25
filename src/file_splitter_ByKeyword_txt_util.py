#!/usr/bin/env Python
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 21:45:41 2020

@author: claude
"""

#source: https://www.nltk.org/_modules/nltk/tokenize.html
import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_splitter_ByKeyword_txt",['os','tkinter','nltk','mlconjug'])==False:
    sys.exit(0)

import os
import pandas as pd
import csv
from nltk.data import load
# from nltk import tokenize
from nltk.tokenize import sent_tokenize, word_tokenize

from nltk.corpus import wordnet#lemmatization
#https://wordnet.princeton.edu/documentation/morphy7wn
#https://stackoverflow.com/questions/31016540/lemmatize-plural-nouns-using-nltk-and-wordnet


import mlconjug #conjugation of verbs
#https://readthedocs.org/projects/mlconjug/downloads/pdf/latest/
#https://pypi.org/project/mlconjug/


# import pattern.en
#https://stackoverflow.com/questions/18902608/generating-the-plural-form-of-a-noun/19018986#comment27903114_18902608

def run(inputFilename, outputPath, keyword, first_occurrence, lemmatization = True):
    title_keyword = keyword
    for letter in keyword:
        if letter == '<' or letter == '>' or letter ==':' or letter =='"' or letter =='/' or letter =='\\' or letter =='|' or letter =='?' or letter =='*':
            title_keyword = keyword.replace(letter,"")
    kwtokens = word_tokenize(keyword.lower())
    kwlist = []#list of list which includes conjugated forms of each token in keyword phrase
    default_conjugator = mlconjug.Conjugator(language='en')
    if first_occurrence == True:
        outputPathone = outputPath + "/subfile_1"
        outputPathtwo = outputPath + "/subfile_2"
        if not os.path.exists(outputPathone) and not os.path.exists(outputPathtwo):
            os.mkdir(outputPathone)
            os.mkdir(outputPathtwo)
            
    for token in kwtokens:
        if token.isalpha():
            conjus = default_conjugator.conjugate(token.lower())
            formlist = conjus.iterate()
            forms = []
            for form in formlist:
                forms.append(form[-1])
            kwlist.append(list(dict.fromkeys(forms)))#reduce repetitions
        else: #mlconjug can't conjugate punctuation(if that's a part of the keyword)
            kwlist.append([token])
    csvtitle = outputPath+'/'+os.path.split(inputFilename)[1].split(".")[0]+"_"+title_keyword+'.csv'
    csvExist = os.path.exists(csvtitle)
    with open(csvtitle, "a",newline = "", encoding='utf-8',errors='ignore') as csvFile:
        writer = csv.writer(csvFile)
        if csvExist == False: 
            writer.writerow(["Document ID", "Document", 'SPLIT_Document', "SEARCH_WORD", "SENTENCE", "Sentence ID of FIRST_OCCURRENCE", "RELATIVE_POSITION", "FREQUENCY of OCCURRENCE"])
            docIndex = 1
        else: 
             df = pd.read_csv(csvtitle, encoding = "ISO-8859-1")
             if len(df) == 0:
                 docIndex = 1
             else:
                 docIndex = df.iloc[-1][0] +1
        first_occurrence_index = 0
        frequency = 0
        contents = []
        head, docname = os.path.split(inputFilename)
        title = docname.partition('.')[0]
        f = open(inputFilename, "r",encoding='utf-8',errors='ignore')
        docText = f.read()
        f.close()
        sentences_ = sent_tokenize(docText)#the list of sentneces in corpus
        subfileindex = 1
        subfilePath = outputPath+os.sep+title+"_"+str(subfileindex)+'.txt'
        if first_occurrence == True:
            subfilePath = outputPathone+os.sep+title+"_"+str(subfileindex)+'.txt'
            
        subfile = open(subfilePath, 'w',encoding='utf-8',errors='ignore')
        sentence_index = 1

        for sent in sentences_: 
            tokens_ = word_tokenize(sent)
            kwindex = 0
            kw = False
            for token in tokens_: 
                t = token.lower()
                if kwindex == len(kwlist):
                    break
                if t.lower() == kwtokens[kwindex] or (lemmatization and (t.lower() in kwlist[kwindex] or kwtokens[kwindex] == wordnet.morphy(t))):#two ways to recognize the keyword
                        #(1) the form in corpus match item in the conjugation list(verbs)
                        #(2) the lemmatized form in corpus match the keyword token(for nouns or adjectives)
                    kw = True
                    kwindex += 1
                else: 
                    kw = False
                    kwindex = 0
            if kw == True:#if keyword is detected, generate the next subfile
                frequency += 1
                presubfile = subfilePath
                if frequency == 1:
                    first_occurrence_index = sentence_index
                if first_occurrence == False or frequency <= 1: 
                    subfileindex += 1
                    subfilePath = outputPath+os.sep+title+"_"+str(subfileindex)+'.txt'
                    if first_occurrence == True and subfileindex == 1:
                        subfilePath = outputPathone+os.sep+title+"_"+str(subfileindex)+'.txt'
                    if first_occurrence == True and subfileindex == 2:
                        subfilePath = outputPathtwo+os.sep+title+"_"+str(subfileindex)+'.txt'
                    subfile = open(subfilePath, 'w',encoding='utf-8',errors='ignore')
                    
                contents.append([docIndex, inputFilename, presubfile, keyword, sent, first_occurrence_index, sentence_index / len(sentences_), frequency])
                # writer.writerow([docIndex, inputFilename, presubfile, keyword, sent, first_occurrence_index, sentence_index / len(sentences_), frequency])
            subfile.write(sent+" ")
            sentence_index += 1
        # print(contents)
        l = len(contents)
        # print("length:",l)
        if l != 0 and first_occurrence: 
            f = contents[-1][-1] 
            if f > 1: f -= 1
            # print(f)
            subpath = contents[-1][2]
            for i in reversed(range(l)):
                # print(contents[i][2])
                if contents[i][2] == subpath:
                    contents[i][-1] = f
                # elif l > 1:                 
                #     f = contents[i][-1] - 1
                #     contents[i][-1] = f
                #     subpath = contents[i][2]
        writer.writerows(contents)

                    

        
        



