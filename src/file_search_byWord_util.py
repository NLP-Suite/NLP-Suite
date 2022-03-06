#!/usr/bin/env Python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 21:37:40 2020

@author: claude
rewritten by Roberto October 2021
complted by Austin Cai October 2021

"""

import sys
import GUI_util
import IO_libraries_util
import collections

if IO_libraries_util.install_all_packages(GUI_util.window, "file_search_byWord_util.py",
                                          ['os', 'tkinter','stanza']) == False:
    sys.exit(0)

import os
import csv
import tkinter.messagebox as mb
from stanza_functions import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza

import IO_user_interface_util
import IO_files_util
import IO_csv_util


def run(inputFilename, inputDir, outputDir, search_by_dictionary, search_by_search_keywords, search_keywords_list,
        search_options_list):
    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                       "Started running the file search script at", True)

    # loop through every txt file and annotate via request to YAGO
    files = IO_files_util.getFileList(inputFilename, inputDir, '.txt')
    nFile = len(files)
    if nFile == 0:
        return

    case_sensitive = False
    lemmatize = False
    search_keywords_found = False
    search_within_sentence = False
    for search_option in search_options_list:
        if search_option == 'Case sensitive':
            case_sensitive = True
        if search_option == 'Case insensitive':
                case_sensitive = False
        elif search_option == "Search within sentence":
            search_within_sentence = True
        elif search_option == "Lemmatize":  # not available yet
            lemmatize = True
    outputFileName = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'search')
    docIndex = 0
    first_occurrence_index = -1
    csvExist = os.path.exists(outputFileName)
    with open(outputFileName, "a", newline="", encoding='utf-8', errors='ignore') as csvFile:
        writer = csv.writer(csvFile)
        if csvExist:
            csvFile.truncate(0)
            writer.writerow(["Search word(s)", "Lemma", "Sentence ID of first occurrence", "Number of sentences", "Relative position",
                             "Frequency of occurrence", "Sentence ID", "Sentence", "Document ID", "Document"])
        else:
            writer.writerow(["Search word(s)", "Lemma", "Sentence ID of first occurrence", "Number of sentences", "Relative position",
                             "Frequency of occurrence", "Sentence ID", "Sentence", "Document ID", "Document"])
        csvFile.close()
    for file in files:
        isFirstOcc = True
        docIndex += 1
        print("Processing file " + str(docIndex) + "/" + str(nFile) + " " + file)
        # print("file",file)
        if search_by_dictionary:
            break
        if search_by_search_keywords:
            output_dir_path = inputDir + os.sep + "search_result_csv"
            if not os.path.exists(output_dir_path):
                os.mkdir(output_dir_path)
            if file[-4:] != '.txt':
                continue
        if not case_sensitive:
            search_keywords_list = search_keywords_list.lower()
        search_keyword = search_keywords_list.split(',')  # word_tokenize(search_keywords_list)
        for w in range(len(search_keyword)):
            search_keyword[w] = search_keyword[w].lstrip()

        # csvtitle = outputDir+'/'+os.path.split(os.path.split(outputDir)[0])[1]+"_"+search_keywords_list+'.csv'
        # if lemmatize:
        #     csvtitle = outputDir+'/'+os.path.split(os.path.split(outputDir)[0])[1]+"_"+search_keywords_list+'_lemma.csv'

        with open(outputFileName, "a", newline="", encoding='utf-8', errors='ignore') as csvFile:
            writer = csv.writer(csvFile)
            f = open(file, "r", encoding='utf-8', errors='ignore')
            docText = f.read()
            f.close()
            if search_within_sentence:
                # sentences_ = sent_tokenize(docText)  # the list of sentences in corpus
                sentences_ = sent_tokenize_stanza(stanzaPipeLine(docText))
                sentence_index = 0
                for sent in sentences_:
                    if len(sent) == 0:
                        sentence_index += 1
                        continue
                    sentence_index += 1
                    if not case_sensitive:
                        sent = sent.lower()
                    # tokens_ = word_tokenize(sent)
                    tokens_ = word_tokenize_stanza(stanzaPipeLine(sent))
                    for keyword in search_keyword:
                        if keyword in sent:
                            if isFirstOcc:
                                first_occurrence_index = sentence_index
                                isFirstOcc = False
                            iterations = keyword.count(' ')
                            tokenIndex = 0
                            frequency = 0
                            for token in tokens_:
                                tokenIndex += 1
                                checker = False
                                if iterations > 0:
                                    partsOfWord = keyword.split(' ')
                                    for i in range(iterations + 1):
                                        if i == 0:
                                            if partsOfWord[i] == token:
                                                # print("yes")
                                                checker = True
                                        else:
                                            if checker and (tokenIndex - 1 + i) < len(tokens_):
                                                if partsOfWord[i] == tokens_[tokenIndex - 1 + i]:
                                                    # print("yes")
                                                    checker = True
                                                else:
                                                    checker = False
                                    if checker:
                                        frequency += 1
                                else:
                                    if keyword == token:
                                        frequency += 1

                            if frequency == 0:
                                percent_position = 0
                                continue
                            else:
                                search_keywords_found = True
                                percent_position = round((sentence_index / len(sentences_)), 2)
                                if lemmatize:
                                    form = search_keywords_list
                                    writer.writerow(
                                        [keyword, form, first_occurrence_index, len(sentences_), percent_position, frequency,
                                         docIndex,
                                         IO_csv_util.dressFilenameForCSVHyperlink(file), sentence_index, len(sentences_), sent])
                                else:
                                    writer.writerow(
                                        [keyword, '', first_occurrence_index, len(sentences_), percent_position, frequency,
                                         docIndex,
                                         IO_csv_util.dressFilenameForCSVHyperlink(file), sentence_index, len(sentences_), sent])
                        else:
                            continue
            else:
                if not case_sensitive:
                    docText = docText.lower()
                # words_ = word_tokenize(docText)  # the list of sentences in corpus
                words_ = word_tokenize_stanza(stanzaPipeLine(docText))
                wordCounter = collections.Counter(words_)
                # print("this is word counter!!!! \n", wordCounter)
                for keyword in search_keyword:
                    # print("this is the key word", keyword)

                    iterations = keyword.count(' ')
                    tokenIndex = 0
                    frequency = 0
                    if iterations > 0:
                        wordIndex = 0
                        for word in words_:
                            wordIndex += 1
                            checker = False
                            partsOfWord = keyword.split(' ')
                            for i in range(iterations + 1):
                                if i == 0:
                                    if partsOfWord[i] == word:
                                        checker = True
                                else:
                                    if checker and (wordIndex - 1 + i) < len(words_):
                                        if partsOfWord[i] == words_[wordIndex - 1 + i]:
                                            # print("yes")
                                            checker = True
                                        else:
                                            checker = False
                            if checker:
                                search_keywords_found = True
                                frequency += 1
                        if frequency > 0:
                            if lemmatize:
                                form = search_keywords_list
                                writer.writerow(
                                    [keyword, form, "N/A", "N/A", "N/A", frequency,
                                     docIndex,
                                     IO_csv_util.dressFilenameForCSVHyperlink(file), "N/A", "N/A"])
                            else:
                                writer.writerow(
                                    [keyword, '', "N/A", "N/A", "N/A", frequency,
                                     docIndex,
                                     IO_csv_util.dressFilenameForCSVHyperlink(file), "N/A", "N/A"])
                        else:
                            if lemmatize:
                                form = search_keywords_list
                                writer.writerow(
                                    [keyword, form, "N/A", "N/A", "N/A", "NOT FOUND",
                                     docIndex,
                                     IO_csv_util.dressFilenameForCSVHyperlink(file), "N/A", "N/A"])
                            else:
                                writer.writerow(
                                    [keyword, '', "N/A", "N/A", "N/A", "NOT FOUND",
                                     docIndex,
                                     IO_csv_util.dressFilenameForCSVHyperlink(file), "N/A", "N/A"])
                    elif keyword in list(wordCounter.keys()):
                        search_keywords_found = True
                        if lemmatize:
                            form = search_keywords_list
                            writer.writerow(
                                [keyword, form, "N/A", "N/A", "N/A", wordCounter[keyword],
                                 docIndex,
                                 IO_csv_util.dressFilenameForCSVHyperlink(file), "N/A", "N/A"])
                        else:
                            writer.writerow(
                                [keyword, '', "N/A", "N/A", "N/A", wordCounter[keyword],
                                 docIndex,
                                 IO_csv_util.dressFilenameForCSVHyperlink(file), "N/A", "N/A"])
                    else:
                        if lemmatize:
                            form = search_keywords_list
                            writer.writerow(
                                [keyword, form, "N/A", "N/A", "N/A", "NOT FOUND",
                                 docIndex,
                                 IO_csv_util.dressFilenameForCSVHyperlink(file), "N/A", "N/A"])
                        else:
                            writer.writerow(
                                [keyword, '', "N/A", "N/A", "N/A", "NOT FOUND",
                                 docIndex,
                                 IO_csv_util.dressFilenameForCSVHyperlink(file), "N/A", "N/A"])

    if search_keywords_found == False:
        mb.showwarning(title='Search string(s) not found',
                       message='The search keywords:\n\n   ' + search_keywords_list + '\n\nwere not found in your input document(s).')
        outputFileName = ''

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, "Analysis end",
                                       "Finished running the file search script at", True)
    return outputFileName


