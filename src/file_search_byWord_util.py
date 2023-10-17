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
                                          ['os', 'tkinter','stanza']) == False:
    sys.exit(0)

import os
import shutil # for copy of files
import csv
import tkinter.messagebox as mb
import stanza
# from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza
import collections

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

def search_sentences_documents(inputFilename, inputDir, outputDir, configFileName,
        search_by_dictionary, search_by_search_keywords, search_keywords_list,
        create_subcorpus_var, search_options_list, lang, createCharts, chartPackage):

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                       "Started running the Word search function at",
                                        True, '', True, '', False)

    result = mb.askyesno('Warning',
                         'The search algorithm will write over any output file created by previous searches. You may wish to rename those files in the output directory and, if you checked the option of creating a subcorpus of files, rename the directory inside the input files directory.\n\nAre you sure you want to continue?')
    if not result:
        return

    filesToOpen=[]
    # each occurrence of a search keyword, it's file path will be stored in a set
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
        # for search_option in search_keywords_list:
        #     # Tony search_keywords_list is not a list but a string and every single character in the string is processed separately
        #     #   we should test
        #     #   if isinstance(search_keywords_list, str) convert to list
        #     search_list = search_list + ' ' + search_option

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
    search_within_sentence = False
    for search_option in search_options_list:
        if search_option == 'Case sensitive (default)':
            case_sensitive = True
        if search_option == 'Case insensitive':
                case_sensitive = False
        elif search_option == "Search within sentence (default)":
            search_within_sentence = True
        elif search_option == "Lemmatize":  # not available yet
            lemmatize = True

    nlp = stanza.Pipeline(lang=lang, processors='tokenize, lemma')
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'search')
    docIndex = 0
    first_occurrence_index = -1
    csvExist = os.path.exists(outputFilename)
    with open(outputFilename, "a", newline="", encoding='utf-8', errors='ignore') as csvFile:
        writer = csv.writer(csvFile)
        if csvExist:
            csvFile.truncate(0)
            writer.writerow(["Search word(s)", "Lemma", "Sentence ID of first occurrence", "Number of sentences", "Relative position in document",
                             "Frequency of occurrence", "Sentence ID", "Sentence", "Document ID", "Document"])
        else:
            writer.writerow(["Search word(s)", "Lemma", "Sentence ID of first occurrence", "Number of sentences", "Relative position in document",
                             "Frequency of occurrence", "Sentence ID", "Sentence", "Document ID", "Document"])
        for file in files:
            isFirstOcc = True
            docIndex += 1
            _, tail = os.path.split(file)
            print("Processing file " + str(docIndex) + "/" + str(nFile) + ' ' + tail)
            if search_by_dictionary:
                break
            if search_by_search_keywords:
                output_dir_path = inputDir + os.sep + "search_result_csv"
                # if not os.path.exists(output_dir_path):
                #     os.mkdir(output_dir_path)
                if file[-4:] != '.txt':
                    continue
            f = open(file, "r", encoding='utf-8', errors='ignore')
            docText = f.read()
            f.close()

    # search in sentence  -----------------------------------------------
            if search_within_sentence:
                chart_title = 'Frequency Distribution of Search Words'
                # the next clause takes long time to process even for small documents
                sentences_ = nlp(docText).sentences
                sentences = [sentence.text for sentence in sentences_]
                sentence_index = 0
                for sent in sentences:
                    if len(sent) == 0:
                        sentence_index += 1
                        continue
                    sentence_index += 1
                    if not case_sensitive:
                        sent = sent.lower()
                    #     tokens_ = [token.text.lower() for token in sentences_[sentence_index-1].tokens]
                    # else:
                    #     tokens_ = [token.text for token in sentences_[sentence_index-1].tokens]

                    frequency = 0
                    for keyword in search_keywords_list:
                        if keyword in sent:
                            if isFirstOcc:
                                first_occurrence_index = sentence_index
                                isFirstOcc = False
                            frequency += 1

                            if frequency == 0:
                                        document_percent_position = 0
                                        continue
                            else:
                                search_keywords_found = True
                                corpus_to_copy.add(file)
                                document_percent_position = round((sentence_index / len(sentences_)), 2)
                                if lemmatize:
                                    form = search_keywords_list
                                    writer.writerow(
                                        [keyword, form, first_occurrence_index, len(sentences_), document_percent_position, frequency,
                                        sentence_index, sent,
                                        docIndex,
                                        IO_csv_util.dressFilenameForCSVHyperlink(file)])
                                else:
                                    writer.writerow(
                                        [keyword, '', first_occurrence_index, len(sentences_), document_percent_position, frequency,
                                        sentence_index, sent,
                                        docIndex,
                                        IO_csv_util.dressFilenameForCSVHyperlink(file)])
                        else:
                            continue

    # search in document, regardless of sentence -----------------------------------------------

            else: # search in document, regardless of sentence
                chart_title = 'Frequency Distribution of Documents with Search Words'
                if not case_sensitive:
                    docText = docText.lower()
                # words_ = word_tokenize(docText)  # the list of sentences in corpus
                words_ = word_tokenize_stanza(stanzaPipeLine(docText))
                wordCounter = collections.Counter(words_)
                # TODO should check that a single word is processed rather than a collocation
                #   when a single word is processed should tokenize
                #       or the keyword "rent" would be found in rental, renting, etc.
                #       unless a partial match is selected
                for keyword in search_keywords_list:
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
                                # count the number of documents, not of searched word occurrences
                                corpus_to_copy.add(file)
                                frequency += 1
                        if frequency > 0:
                            if lemmatize:
                                form = search_keywords_list
                                writer.writerow(
                                    [keyword, form, "N/A", "N/A", "N/A", frequency,
                                    "N/A", "N/A",
                                     docIndex,
                                     IO_csv_util.dressFilenameForCSVHyperlink(file)])
                            else:
                                writer.writerow(
                                    [keyword, '', "N/A", "N/A", "N/A", frequency,
                                     "N/A", "N/A",
                                     docIndex,
                                     IO_csv_util.dressFilenameForCSVHyperlink(file)])
                        else:
                            if lemmatize:
                                form = search_keywords_list
                                writer.writerow(
                                    [keyword, form, "N/A", "N/A", "N/A", "NOT FOUND",
                                     "N/A", "N/A",
                                     docIndex,
                                     IO_csv_util.dressFilenameForCSVHyperlink(file)])
                            else:
                                writer.writerow(
                                    [keyword, '', "N/A", "N/A", "N/A", "NOT FOUND",
                                     "N/A", "N/A",
                                     docIndex,
                                     IO_csv_util.dressFilenameForCSVHyperlink(file)])
                    elif keyword in list(wordCounter.keys()):
                        search_keywords_found = True
                        corpus_to_copy.add(file)
                        if lemmatize:
                            form = search_keywords_list
                            writer.writerow(
                                [keyword, form, "N/A", "N/A", "N/A", wordCounter[keyword],
                                "N/A", "N/A",
                                 docIndex,
                                 IO_csv_util.dressFilenameForCSVHyperlink(file)])
                        else:
                            writer.writerow(
                                [keyword, '', "N/A", "N/A", "N/A", wordCounter[keyword],
                                 "N/A", "N/A",
                                 docIndex,
                                 IO_csv_util.dressFilenameForCSVHyperlink(file)])
                    else:
                        if lemmatize:
                            form = search_keywords_list
                            writer.writerow(
                                [keyword, form, "N/A", "N/A", "N/A", "NOT FOUND",
                                 "N/A", "N/A",
                                 docIndex,
                                 IO_csv_util.dressFilenameForCSVHyperlink(file)])
                        else:
                            writer.writerow(
                                [keyword, '', "N/A", "N/A", "N/A", "NOT FOUND",
                                "N/A", "N/A",
                                 docIndex,
                                 IO_csv_util.dressFilenameForCSVHyperlink(file)])
    csvFile.close()
    if search_keywords_found == False:
        mb.showwarning(title='Search string(s) not found',
                       message='The search keywords:\n\n   ' + search_keywords_str + '\n\nwere not found in your input document(s) with the following set of search options:\n\n  '+ str('\n  '.join(search_options_list)))
        outputFilename = ''
    else:
        filesToOpen.append(outputFilename)

        outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Search word(s)'],
                                                           chart_title=chart_title,
                                                           count_var=1,  # 1 for alphabetic fields that need to be coounted;  1 for numeric fields (e.g., frequencies, scorers)
                                                           hover_label=[],
                                                           outputFileNameType='',
                                                           column_xAxis_label='Search word',
                                                           groupByList=[],
                                                           plotList=[],
                                                           chart_title_label='')
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # when creating a subcorpus copy all the files in the set to the output directory
    if create_subcorpus_var and len(corpus_to_copy) > 0:
        for file in corpus_to_copy:
            shutil.copy(file, subCorpusDir)
        mb.showwarning(title='Warning',message='The search function has created a subcorpus of the files containing the search word(s) "'
                        + search_keywords_list + '" as a subdirectory called "subcorpus_search" of the input directory:\n\n'
                        + subCorpusDir + '\n\nA set of csv files have also been exported to the same directory.')

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running the Search word function at',
                                       True, '', True, startTime,  False)

    return filesToOpen

# inputString is the list of search words
# wordList is a string
def search_extract_sentences(window, inputFilename, inputDir, outputDir, configFileName, inputString, search_options_list,
                                                  minus_K_var, plus_K_var, createCharts, chartPackage):
    if not (isinstance(minus_K_var, int) and isinstance(plus_K_var, int) and minus_K_var >= 0 and plus_K_var >= 0):
        mb.showwarning(title="Warning",message="Invalid input for -K or +K widgets.\n\nThe values must be positive integer numbers.\n\nPlease, enter positive integers and try again.")
    else:
        filesToOpen=[]
        inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False, configFileName=configFileName)
        Ndocs = len(inputDocs)
        if Ndocs == 0:
            return

        from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza

        case_sensitive = False
        lemmatize = False
        search_keywords_found = False
        search_within_sentence = False
        for search_option in search_options_list:
            if search_option == 'Case sensitive (default)':
                case_sensitive = True
            if search_option == 'Case insensitive':
                    case_sensitive = False
            elif search_option == "Search within sentence (default)":
                search_within_sentence = True
            elif search_option == "Lemmatize":  # not available yet
                lemmatize = True

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
                sentences_tokens = sent_tokenize_stanza(stanzaPipeLine(text), False)
                sentences = [s.text for s in sentences_tokens]
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
                        if keyword in sentence:
                            wordFound = True
                            nextSentence = True
                            n_sentences_extract += 1
                            # TODO should process -K +K options for sentences
                            new_sentences = find_k_adjacent_elements(sentences,sentenceSV,plus_K_var,minus_K_var)
                            #print(new_sentences)
                            outputFile_extract.write(' '.join(new_sentences) + "\n")  # write out original sentence
                            file_extract_written = True

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

        IO_files_util.openExplorer(window, outputDir_sentences_extract)


        IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running the Word search with extraction function at',
                                           True, '', True, startTime,  False)


