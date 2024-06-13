#!/usr/bin/env Python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 21:37:40 2020

@author: claude
rewritten by Roberto October 2021
appended by Austin Cai October 2021
appended by Mino Cha April 2022

"""

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "file_search_byWord_util.py",
                                          ['os', 'tkinter','stanza', 're']) == False:
    sys.exit(0)

import os
import shutil # for copy of files
import csv
import tkinter.messagebox as mb
import stanza
# from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza
import collections
import re

import IO_user_interface_util
import IO_files_util
import IO_csv_util
import charts_util
import constants_util
def find_k_adjacent_elements(s, sv, kplus,kminus):
    #plus_K_var,minus_K_var
    n = len(s)
    idx = s.index(sv)
    prior_k = s[max(0, idx-kminus):idx]
    after_k = s[idx+1:min(n, idx+kplus+1)]
    return prior_k + [sv] + after_k

def find_EVERY_k_adjacent_elements(s, sv, kminus, kplus):
    #minus_K_var, plus_K_var
    n = len(s)
    #idx = s.index(sv)
    lefti = []
    midi = []
    riight = []
    for idx in range(len(s)):
        if s[idx]==sv:
            prior_k = s[max(0, idx-kminus):idx]
            after_k = s[idx+1:min(n, idx+kplus+1)]
            lefti.append(' '.join(prior_k))
            riight.append(' '.join(after_k))
            midi.append(sv)
    return lefti,midi, riight


def csv_escape(input_string):
    # Check if the string contains a comma, newline, or double quote
    if ',' in input_string or '\n' in input_string or '"' in input_string:
        # Escape double quotes by replacing one double quote with two
        escaped_string = input_string.replace('"', '""')
        # Enclose the string in double quotes
        return f'"{escaped_string}"'
    else:
        # Return the string unchanged if it doesn't contain any special characters
        return input_string


def get_words_minus_K_plus_K(outputFilename, outputTxtFilename, outputDir, configFileName, hashOutputDir, writer, files, hashmap, search_keywords_list,
                    minus_K_words_var, plus_K_words_var,
                    lemmatize, form_lemma_pair, lang, chartPackage):

    from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza

    with open(outputTxtFilename, 'a', newline='') as f_txt:
        f_txt.write('') # just flushing it
        # Use my logic when we have +- k because the csv is complicated to modify
        # SIMON cache
        for index, file in enumerate(files):
            import hashfile
            # if hashfile.calculate_checksum(file) in hashmap:
            #     words_ = hashmap[hashfile.calculate_checksum(file)]
            #     print('   Using cache...')
            # else:
            f_doc = open(file, "r", encoding='utf-8', errors='ignore')
            docText = f_doc.read()
            f_doc.close()
            words_ = word_tokenize_stanza(stanzaPipeLine(docText))
            hashmap[hashfile.calculate_checksum(file)] = words_
            hashfile.writehash(hashmap,hashOutputDir)
            print("   Building cache...")
            for keyword in search_keywords_list:
                left, mid, right = find_EVERY_k_adjacent_elements(words_, keyword, minus_K_words_var, plus_K_words_var)
                for i in range(len(mid)):
                    str_filename = IO_csv_util.dressFilenameForCSVHyperlink(file)
                    form_lemma_pair, lemma_value = get_lemma(form_lemma_pair, lang, keyword)
                    writer.writerow([csv_escape(left[i]),csv_escape(mid[i]),csv_escape(right[i]), lemma_value, str(index+1), str_filename])
                    #f.write(','.join(a)+"\n")
                for i in range(len(mid)):
                    a = [left[i],right[i]] # If you would like to retain, just follow the 4 lines above and you can do that.
                    # this would be the basis for wordclouds
                    f_txt.write(' '.join(a) + "\n")
                outputFiles = [outputFilename,outputTxtFilename]
    f_txt.close()
    if chartPackage!='No charts':
        # create a wordcloud of the extracted -K +K words
        use_contour_only = False
        max_words = 100
        font = 'Default'
        prefer_horizontal = .9
        lemmatize = False
        exclude_stopwords = True
        exclude_punctuation = True
        lowercase = False
        differentPOS_differentColors = False
        differentColumns_differentColors = False
        csvField_color_list = []
        doNotListIndividualFiles = True
        collocation = False
        import wordclouds_util
        outputFiles2 = wordclouds_util.python_wordCloud(outputTxtFilename, '', outputDir, configFileName,
                                                       selectedImage="",
                                                       use_contour_only=use_contour_only,
                                                       prefer_horizontal=prefer_horizontal, font=font,
                                                       max_words=max_words,
                                                       lemmatize=lemmatize, exclude_stopwords=exclude_stopwords,
                                                       exclude_punctuation=exclude_punctuation, lowercase=lowercase,
                                                       differentPOS_differentColors=differentPOS_differentColors,
                                                       differentColumns_differentColors=differentColumns_differentColors,
                                                       csvField_color_list=csvField_color_list,
                                                       doNotListIndividualFiles=doNotListIndividualFiles,
                                                       openOutputFiles=False, collocation=collocation)
        outputFiles.extend(outputFiles2)
        return outputFiles
    else:
        return outputFiles


def get_lemma(form_lemma_pair, lang, keyword):
    if keyword not in form_lemma_pair:
        nlp = stanza.Pipeline(lang=lang, processors='tokenize, lemma')
        doc = nlp(keyword)
        lemma_value = doc.sentences[0].words[0].lemma
        form_lemma_pair[keyword] = lemma_value
    else:
        lemma_value = form_lemma_pair[keyword]
    return form_lemma_pair, lemma_value

def search_in_document(nlp, files, file, create_subcorpus_var, corpus_to_copy, docText, docIndex, form_lemma_pair, lang, writer,
            outputDir, configFileName, search_keywords_list,
            case_sensitive, lemmatize, exact_word_match, hashmap, hashOutputDir, search_keywords_found,
            minus_K_words_var, plus_K_words_var, outputFilename, outputTxtFilename, chartPackage):
    # SIMON cache
    # cache not working properly
    # import hashfile
    # if hashfile.calculate_checksum(file)+"case"+str(case_sensitive) in hashmap:
    #     words_ = hashmap[hashfile.calculate_checksum(file)]
    #     print('   Using cache...')
    # else:
    from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza
    # SIMON cache
    import hashfile

    words_ = word_tokenize_stanza(stanzaPipeLine(docText))
    hashmap[hashfile.calculate_checksum(file)+"case"+str(case_sensitive)] = words_
    hashfile.writehash(hashmap, hashOutputDir)
    print("   Building cache...")

    # wordCounter = collections.Counter(words_)

    if exact_word_match:
        docText = re.findall(r'\b\w+\b', docText)
    else:
        docText = docText

    for keyword in search_keywords_list:
        frequency_keyword = docText.count(keyword)
        if (not search_keywords_found) and frequency_keyword>0:
            search_keywords_found=True

        if create_subcorpus_var and frequency_keyword>0:
            corpus_to_copy.add(file)

        if lemmatize:
            form_lemma_pair, lemma_value = get_lemma(form_lemma_pair, lang, keyword)
            writer.writerow(
                [keyword, lemma_value, frequency_keyword, docIndex,
                 IO_csv_util.dressFilenameForCSVHyperlink(file)])
        else:
            writer.writerow(
                 [search_keywords_list, frequency, docIndex,
                 IO_csv_util.dressFilenameForCSVHyperlink(file)])

    return search_keywords_found, corpus_to_copy

def search_in_sentence(nlp, files, file,
    create_subcorpus_var, corpus_to_copy, docText, docIndex, isFirstOcc, form_lemma_pair, lang,
    outputDir, configFileName, writer, search_keywords_list,
    case_sensitive, lemmatize, exact_word_match, hashmap, hashOutputDir, search_keywords_found,
    minus_K_words_var, plus_K_words_var, outputFilename, outputTxtFilename, chartPackage):
    # the next clause takes long time to process even for small documents

    import hashfile
    import json
    import hashlib
    # SIMON cache
    if hashfile.calculate_checksum(file) + "Sentences" in hashmap:
        sentences = hashmap[hashfile.calculate_checksum(file) + "Sentences"]
        len_sentences_ = hashmap[hashfile.calculate_checksum(file) + "lenSentences"]
        print('   Using cache...')
    else:
        sentences_ = nlp(docText).sentences
        sentences = [sentence.text for sentence in sentences_]
        len_sentences_ = len(sentences_)
        hashmap[hashfile.calculate_checksum(file) + "Sentences"] = sentences
        hashmap[hashfile.calculate_checksum(file) + "lenSentences"] = len(sentences_)
        hashfile.writehash(hashmap, hashOutputDir)
        print("   Building cache...")

    sentences_ = nlp(docText).sentences

    sentence_index = 0

    for sentence in sentences:
        if len(sentence) == 0:
            sentence_index += 1
            continue
        sentence_index += 1
        if not case_sensitive:
            sentence = sentence.lower()
        for keyword in search_keywords_list:
            if exact_word_match:
                sent = re.findall(r'\b\w+\b', sentence)
            else:
                sent = sentence
            if keyword in sent:
                if isFirstOcc:
                    first_occurrence_index = sentence_index
                    isFirstOcc = False
                frequency = sent.count(keyword)

                if frequency == 0:
                    document_percent_position = 0
                    continue
                else:
                    search_keywords_found = True
                    if create_subcorpus_var:
                        corpus_to_copy.add(file)
                    document_percent_position = round((sentence_index / len_sentences_), 2)
                    if minus_K_words_var > 0 or plus_K_words_var > 0:
                        outputFiles = get_words_minus_K_plus_K(outputFilename, outputTxtFilename, outputDir, configFileName, hashOutputDir, writer, files, hashmap, search_keywords_list, minus_K_words_var, plus_K_words_var, lemmatize, form_lemma_pair, lang, chartPackage)
                    else:
                        if lemmatize:
                            form_lemma_pair, lemma_value = get_lemma(form_lemma_pair, lang, keyword)
                            writer.writerow(
                                [keyword, lemma_value, first_occurrence_index, len_sentences_, document_percent_position,
                                 frequency,
                                 sentence_index, sentence,
                                 docIndex,
                                 IO_csv_util.dressFilenameForCSVHyperlink(file)])
                        else: # no lemmatizing
                            writer.writerow(
                                [keyword, first_occurrence_index, len_sentences_, document_percent_position,
                                 frequency,
                                 sentence_index, sentence,
                                 docIndex,
                                 IO_csv_util.dressFilenameForCSVHyperlink(file)])


            else:
                # keyword not in sentence; move on
                continue
    return search_keywords_found, corpus_to_copy

def search_sentences_documents(inputFilename, inputDir, outputDir, configFileName,
        search_by_dictionary, search_by_search_keywords, search_keywords_list, minus_K_words_var, plus_K_words_var,
        create_subcorpus_var, search_options_list, lang, chartPackage, dataTransformation):

    hashOutputDir = outputDir
    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='search_word',
                                                       silent=False)
    if outputDir == '':
        return
    # SIMON cache
    import hashfile
    if hashfile.checkOut(hashOutputDir):
        hashmap = hashfile.getcache(hashOutputDir)
    else:
        hashmap = {}
    print("done loading hasmap")

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                       "Started running the Word search function at",
                                        True, '', True, '', False)

    filesToOpen=[]
    outputFiles = []

    # each occurrence of a search keyword, it's file path will be stored in a set
    form_lemma_pair = {}
    corpus_to_copy = set()
    from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza

    # loop through every txt file and annotate via request to YAGO
    files = IO_files_util.getFileList(inputFilename, inputDir, '.txt', silent=False, configFileName=configFileName)
    nFile = len(files)
    if nFile == 0:
        return

    import IO_string_util
    if 'insensitive' in str(search_options_list):
        case_sensitive=False
    else:
        case_sensitive = True
    search_keywords_str, search_keywords_list = IO_string_util.process_comma_separated_string_list(search_keywords_list, case_sensitive)

    if create_subcorpus_var:
        if inputFilename!='':
            head, tail = os.path.split(inputFilename)
            # remove the extension
            tail=tail[:-4]
        elif inputDir!='':
            head, tail = os.path.split(inputDir)
        search_list=''

        # txt subsample files are exported as a folder inside the input folder
        subCorpusDir = os.path.join(inputDir, 'subcorpus_search')
        if not os.path.exists(subCorpusDir):
            try:
                os.mkdir(subCorpusDir)
            except Exception:
                print(Exception)

    case_sensitive = False
    lemmatize = False
    search_keywords_found = False
    search_within_sentence = True
    exact_word_match = True
    for search_option in search_options_list:
        if search_option == 'Case sensitive (default)':
            case_sensitive = True
        if search_option == 'Case insensitive':
            case_sensitive = False
        if search_option == "Search within document":
            search_within_sentence = False
        if search_option == "Lemmatize":  # not available yet
            lemmatize = True
        if search_option == "Partial match":
            exact_word_match = False

    if search_within_sentence:
        search_word = 'Search Word in Sentence'
    else:
        search_word = 'Search Word in Document'

    docIndex = 0
    first_occurrence_index = -1

    nlp = stanza.Pipeline(lang=lang, processors='tokenize, lemma')
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'search')
    csvExist = os.path.exists(outputFilename)

    #     writer = csv.writer(csvFile)
    #     with open(outputFilename, 'w') as f:

    # write to text file textToProcess
    outputTxtFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.txt', 'search')
    with open(outputTxtFilename, 'w') as f:
        f.write('') # just flushing it

    form_lemma_pair = {}
    with open(outputFilename, 'a', newline='') as f_csv:
        writer = csv.writer(f_csv)
        with open(outputFilename, 'w') as f_csv:
            f_csv.write("")  # flushing

# write csv file headers -------------------------------------------------------------------
# search in sentence --------------------------------------------------------------------------------
            if search_within_sentence:
                if minus_K_words_var > 0 or plus_K_words_var > 0:
                    if lemmatize:
                        writer.writerow(["Minus K Value of Words (" + str(
                        minus_K_words_var) + ")", search_word, "Plus K Value of Words (" + str(
                        plus_K_words_var) + ")", "Lemma", "Sentence ID of first occurrence", "Number of sentences", "Relative position in document",
                                         "Frequency of occurrence", "Sentence ID", "Sentence", "Document ID", "Document"])
                    else:
                        writer.writerow(["Minus K Value of Words (" + str(
                            minus_K_words_var) + ")", search_word, "Plus K Value of Words (" + str(
                            plus_K_words_var) + ")", "Sentence ID of first occurrence", "Number of sentences",
                                    "Relative position in document",
                                    "Frequency of occurrence", "Sentence ID", "Sentence", "Document ID", "Document"])
                else:
                    if lemmatize:
                        writer.writerow([search_word, "Lemma", "Sentence ID of first occurrence",
                                    "Number of sentences", "Relative position in document",
                                    "Frequency of occurrence", "Sentence ID", "Sentence",
                                    "Document ID", "Document"])
                    else:
                        writer.writerow([search_word, "Sentence ID of first occurrence", "Number of sentences",
                                    "Relative position in document",
                                    "Frequency of occurrence", "Sentence ID", "Sentence", "Document ID", "Document"])

# search in document --------------------------------------------------------------------------------
            else: # search in document
                if lemmatize:
                    writer.writerow([search_word, "Lemma",
                                "Frequency of occurrence",
                                "Document ID", "Document"])
                else:
                    for keyword in search_keywords_list:
                        writer.writerow([search_word,
                                    "Frequency of occurrence of " + keyword, "Document ID", "Document"])

                # if csvExist:
                #         # csvFile.truncate(0)
                #     f_csv.truncate(0)
                # writer.writerow(["Lemma", "Sentence ID of first occurrence", "Number of sentences", "Relative position in document",
                #                      "Frequency of occurrence", "Sentence ID", "Sentence", "Document ID", "Document"])


    # processing corpus files

            for file in files:
                isFirstOcc = True
                docIndex += 1
                _, tail = os.path.split(file)
                print("Processing file " + str(docIndex) + "/" + str(nFile) + ' ' + tail)
                if search_by_dictionary:
                    break
                if search_by_search_keywords:
                    output_dir_path = inputDir + os.sep + "search_result_csv"
                    if file[-4:] != '.txt':
                        continue
                f_doc = open(file, "r", encoding='utf-8', errors='ignore')
                docText = f_doc.read()
                f_doc.close()


        # search in sentence  -----------------------------------------------
                if search_within_sentence:
                    search_keywords_found, corpus_to_copy = search_in_sentence (nlp, files, file, create_subcorpus_var, corpus_to_copy,
                                docText, docIndex, isFirstOcc,
                                form_lemma_pair, lang, outputDir, configFileName, writer,
                                search_keywords_list, case_sensitive, lemmatize,
                                exact_word_match, hashmap, hashOutputDir, search_keywords_found,
                                minus_K_words_var, plus_K_words_var, outputFilename, outputTxtFilename, chartPackage)
                    chart_title = 'Frequency Distribution of Search Words'
        # search in document, regardless of sentence -----------------------------------------------
                else: # search in document, regardless of sentence
                    search_keywords_found, corpus_to_copy = search_in_document (nlp, files, file, create_subcorpus_var, corpus_to_copy,
                            docText, docIndex, form_lemma_pair, lang, writer, outputDir, configFileName,
                            search_keywords_list, case_sensitive, lemmatize, exact_word_match, hashmap, hashOutputDir,
                            search_keywords_found,
                            minus_K_words_var, plus_K_words_var,
                            outputFilename, outputTxtFilename, chartPackage)
                    chart_title = 'Frequency Distribution of Documents with Search Words'

            f_csv.close()
            filesToOpen.append(outputFilename)

            # produce charts ---------------------------------------------------------------
            if not search_keywords_found:
                mb.showwarning(title='Search word(s) not found',
                               message='The search keywords:\n\n   ' + search_keywords_str + '\n\nwere not found in your input document(s) with the following set of search options:\n\n  '+ str('\n  '.join(search_options_list)))
                outputFilename = ''
            else:

                outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFilename, outputDir,
                                                                   columns_to_be_plotted_xAxis=[],
                                                                   columns_to_be_plotted_yAxis=[search_word],
                                                                   chart_title=chart_title,
                                                                   count_var=1,  # 1 for alphabetic fields that need to be coounted;  1 for numeric fields (e.g., frequencies, scorers)
                                                                   hover_label=[],
                                                                   outputFileNameType='',
                                                                   column_xAxis_label=search_word,
                                                                   groupByList=[],
                                                                   plotList=[],
                                                                   chart_title_label='')
                if outputFiles!=None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)

        # when creating a subcorpus copy all the files in the set to a subdirectory 'subcorpus_search' of the input directory
        if create_subcorpus_var and len(corpus_to_copy) > 0:
            for file in corpus_to_copy:
                shutil.copy(file, subCorpusDir)
            mb.showwarning(title='Warning',message='The search function has created a subcorpus of the files containing the search word(s) "'
                            + str(search_keywords_list) + '" as a subdirectory called "subcorpus_search" of the input directory:\n\n'
                            + subCorpusDir + '\n\nA set of csv files have also been exported to the output  directory.')

        IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running the Search word function at',
                                           True, '', True, startTime,  False)

    return filesToOpen

# inputString is the list of search words
# wordList is a string
def search_extract_sentences(window, inputFilename, inputDir, outputDir, configFileName, inputString, search_options_list,
                                                  minus_K_var, plus_K_var, chartPackage, dataTransformation):
    if not (isinstance(minus_K_var, int) and isinstance(plus_K_var, int) and minus_K_var >= 0 and plus_K_var >= 0):
        mb.showwarning(title="Warning",message="Invalid input for -K or +K widgets.\n\nThe values must be positive integer numbers.\n\nPlease, enter positive integers and try again.")
        return

    hashOutputDir = outputDir
    # SIMON cache
    import hashfile
    if hashfile.checkOut(hashOutputDir):
        hashmap = hashfile.getcache(hashOutputDir)
    else:
        hashmap = {}
    print("done loading hasmap")

    filesToOpen=[]
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False, configFileName=configFileName)
    Ndocs = len(inputDocs)
    if Ndocs == 0:
        return

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='search_sent_extract',
                                                       silent=False)
    if outputDir == '':
        return

    from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza

    case_sensitive = False
    exact_word_match = True
    lemmatize = False
    search_keywords_found = False
    search_within_sentence = False
    for search_option in search_options_list:
        if search_option == 'Case sensitive (default)':
            case_sensitive = True
        if search_option == 'Case insensitive':
                case_sensitive = False
        if search_option == "Search within sentence (default)":
            search_within_sentence = True
        if search_option == "Lemmatize":  # not available yet
            lemmatize = True
        if search_option == "Partial match":
            exact_word_match = False

    if search_within_sentence:
        search_word = 'Search Word in Sentence'
    else:
        search_word = 'Search Word in Document'

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
    def Convert(inputString):
        wordList = list(inputString.split(","))
        return wordList

    wordList = Convert(inputString)

    if inputFilename!='':
        inputFileBase = os.path.basename(inputFilename)[0:-4]  # without .txt
        outputDir_sentences = os.path.join(outputDir, "sentences_" + inputFileBase)
    else:
        # processing a directory
        inputDirBase = os.path.basename(inputDir)
        outputDir_sentences = os.path.join(outputDir, "sentences_Dir_" + inputDirBase)

    # create a subdirectory in the output directory
    # should be silent because the user has already agreed to overwrite an existing upper directory
    outputDir_sentences_extract = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='extract_with_searchword', silent=True)
    if outputDir_sentences_extract == '':
        return
    outputDir_sentences_extract_wo_searchword = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='extract_wo_searchword', silent=True)
    if outputDir_sentences_extract_wo_searchword == '':
        return

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                   'Started running the Word search with extraction function at',
                                                   True, '', True, '',  False)

    fileID = 0
    file_extract_written = False
    file_extract_wo_searchword_written = False
    nDocsExtractOutput = 0
    nDocsExtractMinusOutput = 0

    outputFilenameCSV = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                'search_sent_extract')

    print(inputDir, outputDir)

    with open(outputFilenameCSV, 'w', encoding='utf-8', errors='ignore') as f:
        f.write(search_word+',Sentence ID, Relative position in document, Sentence, Document ID, Document\n')

    textToProcess = ''
    for doc in inputDocs:
        wordFound = False
        fileID = fileID + 1
        head, tail = os.path.split(doc)
        print("Processing file " + str(fileID) + "/" + str(Ndocs) + ' ' + tail)
        with open(doc, 'r', encoding='utf-8', errors='ignore') as inputFile:
            text = inputFile.read().replace("\n", " ")
        outputFilename_extract = os.path.join(outputDir_sentences_extract,tail[:-4]) + "_extract_with_searchword.txt"
        outputFilename_extract_wo_searchword = os.path.join(outputDir_sentences_extract_wo_searchword,tail[:-4]) + "_extract_wo_searchword.txt"
        with open(outputFilename_extract, 'w', encoding='utf-8', errors='ignore') as outputFile_extract, open(
                outputFilename_extract_wo_searchword, 'w', encoding='utf-8', errors='ignore') as outputFile_extract_wo_searchword:
            # SIMON cache
            import hashfile
            if hashfile.calculate_checksum(doc) + "doc" in hashmap:
                sentences = hashmap[hashfile.calculate_checksum(doc)+"doc"]
                print('   Using cache...')
            else:
                sentences_tokens = sent_tokenize_stanza(stanzaPipeLine(text), False)
                sentences = [s.text for s in sentences_tokens]
                hashmap[hashfile.calculate_checksum(doc) + "doc"] = sentences
                hashfile.writehash(hashmap, hashOutputDir)
                print("   Building cache...")

            n_sentences_extract = 0
            n_sentences_extract_wo_searchword = 0
            sentence_index = 0

            for sentence in sentences:
                if len(sentence) == 0:
                    sentence_index += 1
                    continue
                sentence_index += 1
                wordFound = False
                sentenceSV = sentence
                nextSentence = False
                for keyword in wordList:
                    if nextSentence == True:
                        # go to next sentence; do not write the same sentence several times if it contains several words in wordList
                        break
                    if case_sensitive==False:
                        sentence = sentence.lower()
                        keyword = keyword.lower()

                    # TODO should check that a single word is processed rather than a collocation
                    #   when a single word is processed should tokenize
                    #       or the keyword "rent" would be found in rental, renting, etc.
                    #       unless a partial match is selected

                    # using Stanza would be more accurate but slower
                    # if keyword in word_tokenize_stanza(stanzaPipeLine(sentence.lower())):
                    if exact_word_match:
                        if type(sentence) == str:
                            sentencecopy = sentence
                            sentence = re.findall(r'\b\w+\b', sentence)
                    else:
                        sentencecopy = sentence
                    if keyword in sentence:
                        with open(outputFilenameCSV,'a',encoding='utf-8',errors='ignore') as f:
                            f.write(keyword+','+
                                    str(sentences.index(sentencecopy))+','+
                                    str(sentences.index(sentencecopy)/len(sentences))+','+
                                    str(csv_escape(''.join(sentencecopy)))+','+
                                    str(inputDocs.index(doc))+','+
                                    IO_csv_util.dressFilenameForCSVHyperlink(doc)+
                                    '\n')

                        wordFound = True
                        nextSentence = True
                        n_sentences_extract += 1
                        # TODO should process -K +K options for sentences
                        new_sentences = find_k_adjacent_elements(sentences,sentenceSV,plus_K_var,minus_K_var)
                        outputFile_extract.write(' '.join(new_sentences) + "\n")  # write out original sentence
                        file_extract_written = True
                        # create a string containing all the searched sentences so that they can be displayed ina wordcloud
                        textToProcess = textToProcess + ' '.join(new_sentences) + "\n"
                # if none of the words in wordList are found in a sentence
                #   write the sentence to the extract_wo_searchword file
                if wordFound == False:
                    n_sentences_extract_wo_searchword += 1
                    outputFile_extract_wo_searchword.write(sentenceSV + " ")  # write out original sentence
                    file_extract_wo_searchword_written = True
        if file_extract_written == True:
            # filesToOpen.append(outputFilename_extract)
            nDocsExtractOutput += 1
            file_extract_written = False
        outputFile_extract.close()
        if n_sentences_extract == 0: # remove empty file
            os.remove(outputFilename_extract)
        if file_extract_wo_searchword_written:
            # filesToOpen.append(outputFilename_extract_wo_searchword)
            nDocsExtractMinusOutput += 1
            file_extract_wo_searchword_written = False
        outputFile_extract_wo_searchword.close()
        if n_sentences_extract_wo_searchword == 0: # remove empty file
            os.remove(outputFilename_extract_wo_searchword)
    if Ndocs == 1:
        msg1 = str(Ndocs) + " file was"
    else:
        msg1 = str(Ndocs) + " files were"
    if nDocsExtractOutput == 1:
        msg2 = str(nDocsExtractOutput) + " file was"
    else:
        msg2 = str(nDocsExtractOutput) + " files were"
    if nDocsExtractMinusOutput == 1:
        msg3 = str(nDocsExtractMinusOutput) + " file was"
    else:
        msg3 = str(nDocsExtractMinusOutput) + " files were"
    mb.showwarning("Warning", msg1 + " processed in input.\n\n" +
                   msg2 + " written with _extract_with_searchword in the filename.\n\n" +
                   msg3 + " written with _extract_wo_searchword in the filename.\n\n" +
                   "Files were written to the subdirectories " + outputDir_sentences_extract + " and " + outputDir_sentences_extract_wo_searchword + " of the output directory." +
                   "\n\nPlease, check the output subdirectories for filenames ending with _extract_with_searchword.txt and _extract_wo_searchword.txt.")

    if textToProcess=='':
        mb.showwarning(title='Warning',message='There are no sentences in your input document(s) containing the selected search word(s).')
        return
    # write to text file textToProcess
    outputFilenameTxt = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.txt', 'search_single_text')
    filesToOpen.append(outputFilenameTxt)
    outputTxtFile = open(outputFilenameTxt, "w", encoding="utf-8", errors="ignore")
    outputTxtFile.write(textToProcess)
    outputTxtFile.close()

    import wordclouds_util

    # run with all default values;
    use_contour_only = False
    max_words = 100
    font = 'Default'
    prefer_horizontal = .9
    # lemmatize = False
    exclude_stopwords = True
    exclude_punctuation = True
    lowercase = False
    differentPOS_differentColors = False
    differentColumns_differentColors = False
    csvField_color_list = []
    doNotListIndividualFiles = True
    collocation = False
    import wordclouds_util
    outputFiles = wordclouds_util.python_wordCloud(outputFilenameTxt, '', outputDir, configFileName, selectedImage="",
                                              use_contour_only=use_contour_only,
                                              prefer_horizontal=prefer_horizontal, font=font, max_words=max_words,
                                              lemmatize=lemmatize, exclude_stopwords=exclude_stopwords,
                                              exclude_punctuation=exclude_punctuation, lowercase=lowercase,
                                              differentPOS_differentColors=differentPOS_differentColors,
                                              differentColumns_differentColors=differentColumns_differentColors,
                                              csvField_color_list=csvField_color_list,
                                              doNotListIndividualFiles=doNotListIndividualFiles,
                                              openOutputFiles=False, collocation=collocation)

    if outputFiles != None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)
    IO_files_util.openExplorer(window, outputDir_sentences_extract)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running the Word search with extraction function at',
                                       True, '', True, startTime,  False)

    return filesToOpen
