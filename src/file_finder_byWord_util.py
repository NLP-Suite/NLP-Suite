#!/usr/bin/env Python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 21:37:40 2020

@author: claude
"""

#source: https://www.nltk.org/_modules/nltk/tokenize.html
import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_splitter_ByKeyword_txt",['os','tkinter','nltk','mlconjug'])==False:
    sys.exit(0)

import os
import csv
import pandas as pd
from nltk.data import load
# from nltk import tokenize
from nltk.tokenize import sent_tokenize, word_tokenize

from nltk.corpus import wordnet #lemmatization
#https://wordnet.princeton.edu/documentation/morphy7wn
#https://stackoverflow.com/questions/31016540/lemmatize-plural-nouns-using-nltk-and-wordnet

import mlconjug #conjugation of verbs
#https://readthedocs.org/projects/mlconjug/downloads/pdf/latest/
#https://pypi.org/project/mlconjug/

# import pattern.en
#https://stackoverflow.com/questions/18902608/generating-the-plural-form-of-a-noun/19018986#comment27903114_18902608

import IO_user_interface_util
import IO_files_util

def run(inputFilename,input_main_dir_path, outputPath, search_by_dictionary_var, search_by_keyword_var, keyword, lemmatization, within_sentence):

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', "Started running the file search script at", True)

    if input_main_dir_path=='' and inputFilename!='':
        inputDir=os.path.dirname(inputFilename)
        files=[inputFilename]
    elif input_main_dir_path!='':
        inputDir=input_main_dir_path
        files= IO_files_util.getFileList(inputFilename, inputDir, 'txt')
    if len(files) == 0:
        return

    #print("files",files)
    for file in files:
        #print("file",file)
        if search_by_dictionary_var:
            break
        if search_by_keyword_var:
            output_dir_path = inputDir + os.sep + "search_result_csv"
            if not os.path.exists(output_dir_path):
                os.mkdir(output_dir_path)
            if file[-4:]!='.txt':
                continue

        kwtokens = word_tokenize(keyword)
        kwlist = []#list of list which includes conjugated forms of each token in keyword phrase
        default_conjugator = mlconjug.Conjugator(language='en')

        for token in kwtokens:
            conjus = default_conjugator.conjugate(token)
            formlist = conjus.iterate()
            forms = []
            for form in formlist:
                forms.append(form[-1])
            kwlist.append(list(dict.fromkeys(forms)))#reduce repetitions
        csvtitle = outputPath+'/'+os.path.split(os.path.split(outputPath)[0])[1]+"_"+keyword+'.csv'
        if lemmatization:
            csvtitle = outputPath+'/'+os.path.split(os.path.split(outputPath)[0])[1]+"_"+keyword+'_lemma.csv'
        csvExist = os.path.exists(csvtitle)
        with open(csvtitle, "a",newline = "", encoding='utf-8',errors='ignore') as csvFile:
            writer = csv.writer(csvFile)

            if csvExist == False:
                writer.writerow(["Document ID", "Document", "Sentence ID","SENTENCE", "SEARCH_WORD", "LEMMATIZED", "Sentence ID of FIRST_OCCURRENCE", "RELATIVE_POSITION", "FREQUENCY of OCCURRENCE"])
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
            f = open(file, "r",encoding='utf-8',errors='ignore')
            docText = f.read()
            f.close()
            sentences_ = sent_tokenize(docText)#the list of sentences in corpus
            sentence_index = 1

            for sent in sentences_:
                tokens_ = word_tokenize(sent)
                kwindex = 0
                kw = False
                form = ''
                for token in tokens_:
                    t = token.lower()
                    if kwindex == len(kwlist):
                        break
                    if t == kwtokens[kwindex] or (lemmatization and (t in kwlist[kwindex] or kwtokens[kwindex] == wordnet.morphy(t))):#two ways to recognize the keyword
                            #(1) the form in corpus match item in the conjugation list(verbs)
                            #(2) the lemmatized form in corpus match the keyword token(for nouns or adjectives)
                        kw = True
                        kwindex += 1
                        form += t + " "
                    else:
                        kw = False
                        kwindex = 0
                        form = ''
                if len(form) > 0:
                    form = form[:-1]
                if kw == True:#if keyword is detected, generate the next subfile
                    frequency += 1
                    if frequency == 1:
                        first_occurrence_index = sentence_index
                    if lemmatization:
                        writer.writerow([docIndex, file, sentence_index, sent, keyword, form,  first_occurrence_index, sentence_index / len(sentences_), frequency])
                    else:
                        writer.writerow([docIndex, file, sentence_index, sent,  keyword, '', first_occurrence_index, sentence_index / len(sentences_), frequency])
                    # writer.writerow([docIndex, inputFilename, presubfile, keyword, sent, first_occurrence_index, sentence_index / len(sentences_), frequency])
                else:
                     writer.writerow([docIndex, file, sentence_index, sent,  '', '', '', '', ''])
                sentence_index += 1

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, "Analysis end", "Finished running the file search script at", True)
