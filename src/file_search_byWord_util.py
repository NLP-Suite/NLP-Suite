#!/usr/bin/env Python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 21:37:40 2020

@author: claude
rewritten by Roberto October 2021
appended by Austin Cai October 2021
appended by Mino Cha April 2022
rewritten entirely by Roberto June 2024
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
import collections
import re

import IO_user_interface_util
import IO_files_util
import IO_csv_util
import charts_util
import constants_util

# sentences is a list of all sentences
# search_sentence is a string containing the sentence around which we want to get -K +K sentences
def find_k_adjacent_sentences(sentences, search_sentence, kminus, kplus):
    n = len(sentences)
    idx = sentences.index(search_sentence)
    prior_k = sentences[max(0, idx-kminus):idx]
    after_k = sentences[idx+1:min(n, idx+kplus+1)]
    # return a list of -K + K sentences before and after the search_sentence []
    # adjacent_sentences = prior_k + [search_sentence] + after_k
    # return ONLY adjacent sentence, excluding the search sentence that contains a search word
    adjacent_sentences = prior_k + after_k
    return adjacent_sentences

# s is a list of individual tokens; so "pretty girl" would not be found
# search_word is a string of an individual search word or multi-word expression
def find_k_adjacent_tokens(tokenized_sentence, search_word, exact_word_match, kminus, kplus):
    #minus_K_var, plus_K_var
    n = len(tokenized_sentence)
    left = []
    mid = []
    right = []
    process_before_after = False
    # convert search_word string to list
    search_word_list = search_word.split(' ')
    len_search_word=len(search_word_list)
    for idx, current_word in enumerate(tokenized_sentence): # e.g., good man
        process_before_after = False
        if len_search_word>1:
            # @@@ need to complete partial matching
            search_word_left=search_word_list[0]
            search_word_right = search_word_list[len_search_word - 1]
            if tokenized_sentence[idx] == search_word_left:
                prior_k = tokenized_sentence[max(0, idx - kminus):idx]
                # after_k = s[idx + 1:min(n, idx + kplus + 1)]
                left.append(' '.join(prior_k))
            if tokenized_sentence[idx] == search_word_right:
                # prior_k = s[max(0, idx - kminus):idx]
                after_k = tokenized_sentence[idx + 1:min(n, idx + kplus + 1)]
                right.append(' '.join(after_k))
            if (left != [] or right != []) and mid==[]:
                mid.append(search_word)
        else:
            if not exact_word_match:
                # if search_word in tokenized_sentence[idx]:
                if search_word in current_word:
                    process_before_after = True
            else:
                # if tokenized_sentence[idx]==search_word:
                if search_word == current_word:
                    process_before_after = True
            if process_before_after:
                left.append(' '.join(tokenized_sentence[max(0, idx-kminus):idx]))
                right.append(' '.join(tokenized_sentence[idx+1:min(n, idx+kplus+1)]))
                # prior_k = tokenized_sentence[max(0, idx-kminus):idx]
                # after_k = tokenized_sentence[idx+1:min(n, idx+kplus+1)]
                # left.append(' '.join(prior_k))
                # right.append(' '.join(after_k))
                mid.append(search_word)
    return left, mid, right


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


def get_words_minus_K_plus_K(docText, search_keyword, exact_word_match,
                             minus_K_words_var, plus_K_words_var,
                             lemmatize, form_lemma_pair, lang):

    # convert string to list
    if isinstance(docText, str):
        from Stanza_functions_util import stanzaPipeLine, tokenize_stanza_text
        words_ = tokenize_stanza_text(stanzaPipeLine(docText))
    # hashmap[hashfile.calculate_checksum(file)] = words_
    # hashfile.writehash(hashmap,hashOutputDir)
    # print("   Building cache...")
    a=[]
    # for keyword in search_keywords_list: the calling function now loops through the search_keywords_list
    left, mid, right = find_k_adjacent_tokens(words_, search_keyword, exact_word_match, minus_K_words_var, plus_K_words_var)
    for i in range(len(mid)):
        try:
            a = [left[i], right[i]]  # If you would like to retain, just follow the 4 lines above and you can do that.
        except:
            a = ['','']
            # print('error')
    # a is the word list used for a wordcloud of the set of -K and +K words
    return a

# not used
def get_lemma(form_lemma_pair, lang, keyword):
    if keyword not in form_lemma_pair:
        nlp = stanza.Pipeline(lang=lang, processors='tokenize, lemma')
        doc = nlp(keyword)
        lemma_value = doc.sentences[0].words[0].lemma
        form_lemma_pair[keyword] = lemma_value
    else:
        lemma_value = form_lemma_pair[keyword]
    return form_lemma_pair, lemma_value

def search_in_document(file, create_subcorpus_var, corpus_to_copy, docText, docIndex,
            search_keywords_list, search_keywords_str,
            case_sensitive, lemmatize, exact_word_match):
    # SIMON cache
    # cache not working properly
    # import hashfile
    # if hashfile.calculate_checksum(file)+"case"+str(case_sensitive) in hashmap:
    #     words_ = hashmap[hashfile.calculate_checksum(file)]
    #     print('   Using cache...')
    # else:

    all_found_csv_sentences_records_oneDoc = []
    all_found_csv_words_records_oneDoc = []
    all_found_csv_words_minusK_plusK_records_oneDoc = []

    from Stanza_functions_util import stanzaPipeLine, tokenize_stanza_text
    # SIMON cache
    # import hashfile

    search_keywords_NOT_found = []
    search_keywords_found=False

    words_ = tokenize_stanza_text(stanzaPipeLine(docText))
    # hashmap[hashfile.calculate_checksum(file)+"case"+str(case_sensitive)] = words_
    # hashfile.writehash(hashmap, hashOutputDir)
    # print("   Building cache...")

    # wordCounter = collections.Counter(words_)

    #@@@@@
    # if exact_word_match:
    #     docText = re.findall(r'\b\w+\b', docText)
    # else:
    #     docText = docText

    for keyword in search_keywords_list:
        import NGrams_CoOccurrences_util
        frequency_keyword = NGrams_CoOccurrences_util.get_search_word_from_text(docText, keyword, lemmatize, case_sensitive, exact_word_match)
        if (not search_keywords_found) and frequency_keyword>0:
            search_keywords_found=True

        if frequency_keyword == 0:
            # document search
            search_keywords_NOT_found.append([keyword, docIndex, IO_csv_util.dressFilenameForCSVHyperlink(file)])

            document_percent_position = 0

        if create_subcorpus_var and frequency_keyword>0:
            corpus_to_copy.add(file)

        temp_csv_record_oneSentence = [keyword, \
                                       str(frequency_keyword), \
                                       str(docIndex), \
                                       IO_csv_util.dressFilenameForCSVHyperlink(file)]
        all_found_csv_sentences_records_oneDoc.append(temp_csv_record_oneSentence)

    return search_keywords_found, search_keywords_NOT_found, corpus_to_copy, all_found_csv_sentences_records_oneDoc

# the function search_in_sentence will loop through every sentence of a specific document
def search_in_all_sentences_oneDoc(file,
    create_subcorpus_var, corpus_to_copy, docText, docIndex,
    form_lemma_pair, lang,
    search_keywords_list,
    case_sensitive, lemmatize, exact_word_match, search_keywords_found,
    minus_K_var, plus_K_var):
    # the next clause takes long time to process even for small documents

    isFirstOcc=True
    textToProcess = ''
    fileID = 0
    file_extract_written = False
    file_extract_wo_searchword_written = False
    nDocsExtractOutput = 0
    nDocsExtractMinusOutput = 0

    from Stanza_functions_util import stanzaPipeLine, sentence_split_stanza_text
    sentences = sentence_split_stanza_text(stanzaPipeLine(docText))
    num_sentences=len(sentences)
    search_keywords_NOT_found = []
    all_adjacent_words_oneDoc = []
    all_adjacent_sentences_oneDoc = ''
    all_found_sentences_oneDoc = ''
    adjacent_sentences = ''
    all_found_csv_sentences_records_oneDoc = []
    all_found_csv_words_records_oneDoc = []
    all_found_csv_words_minusK_plusK_records_oneDoc = []

    for sentence_index, sentence in enumerate(sentences):
        sentencecopy = sentence
        wordFound = False
        sentenceSV = sentence
        nextSentence = False
        n_sentences_extract = 0
        n_sentences_extract_wo_searchword = 0
        sentence_index+=1 # to avoid having a sentence_index as 0
        import NGrams_CoOccurrences_util

        if isinstance(search_keywords_list,str):
            # convert string to list
            search_keywords_list = search_keywords_list.split('')

        for search_word in search_keywords_list:
            search_word_frequency = NGrams_CoOccurrences_util.get_search_word_from_text(sentence, search_word,
                                                                                        lemmatize, case_sensitive,
                                                                                        exact_word_match)
            if search_word_frequency == 0:
                # sentence search
                search_keywords_NOT_found.append([search_word, sentence_index, sentence, docIndex, IO_csv_util.dressFilenameForCSVHyperlink(file)])
                document_percent_position = 0
            elif search_word_frequency>0:
                if isFirstOcc:
                    first_occurrence_index = sentence_index
                    isFirstOcc = False
                search_keywords_found = True
                if create_subcorpus_var:
                    corpus_to_copy.add(file)
                document_percent_position = round((sentence_index / num_sentences), 2)
                if minus_K_var > 0 or plus_K_var > 0:
                    minus_plus_K_words = get_words_minus_K_plus_K(sentence,
                        search_word, exact_word_match, minus_K_var, plus_K_var,
                        lemmatize, form_lemma_pair, lang)
                    if minus_plus_K_words==[]:
                        continue
                    all_adjacent_words_oneDoc.extend(minus_plus_K_words)
                    try:
                        left_words=minus_plus_K_words[0]
                    except:
                        left_words=''
                    try:
                        right_words=minus_plus_K_words[1]
                    except:
                        right_words=''
                    temp_csv_record_oneSentence = [left_words, search_word, right_words, str(num_sentences), str(sentences.index(sentence)), \
                        str(document_percent_position), \
                        str(search_word_frequency), \
                        str(sentence_index), \
                        sentence, \
                        str(docIndex), \
                        IO_csv_util.dressFilenameForCSVHyperlink(file)]
                    all_found_csv_words_minusK_plusK_records_oneDoc.append(temp_csv_record_oneSentence)
                if (minus_K_var == 0 and plus_K_var == 0):
                    temp_csv_record_oneSentence = [search_word, str(num_sentences), str(sentences.index(sentence)), \
                        str(document_percent_position), \
                        str(search_word_frequency), \
                        str(sentence_index), \
                        sentence, \
                        str(docIndex), \
                        IO_csv_util.dressFilenameForCSVHyperlink(file)]
                    all_found_csv_sentences_records_oneDoc.append(temp_csv_record_oneSentence)

                sentencecopy = sentence
                all_found_sentences_oneDoc = all_found_sentences_oneDoc + '\n' + sentence
                adjacent_sentences = find_k_adjacent_sentences(sentences, sentence, minus_K_var, plus_K_var)
                # Search word(s)	Sentence ID	 Relative position in document	 Sentence	 Document ID	 Document

                # create a string containing all the searched sentences so that they can be displayed ina wordcloud
                all_adjacent_sentences_oneDoc = all_adjacent_sentences_oneDoc + ' '.join(adjacent_sentences) + "\n"


    # convert list to string for wordcloud
    all_adjacent_words_oneDoc=' '.join(all_adjacent_words_oneDoc)
    # end of search_in_sentence function
    return search_keywords_found, search_keywords_NOT_found, corpus_to_copy, all_adjacent_words_oneDoc, all_adjacent_sentences_oneDoc, all_found_sentences_oneDoc, all_found_csv_words_minusK_plusK_records_oneDoc, all_found_csv_sentences_records_oneDoc

def search_sentences_documents(inputFilename, inputDir, outputDir, configFileName,
        search_by_dictionary, selectedCsvFile, search_by_search_keywords, search_keywords_list, minus_K_var, plus_K_var,
        extract_sentences, create_subcorpus_var, search_options_list, lang, chartPackage, dataTransformation):

    import pandas as pd

    filesToOpen=[]
    outputFiles = []

    # each occurrence of a search keyword, it's file path will be stored in a set
    form_lemma_pair = {}
    corpus_to_copy = set()

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
    # when processing an input csv file must create the search_keywords_list
    if search_by_dictionary:
        df = pd.read_csv(selectedCsvFile)
        colname = df.columns[0]
        search_keywords_list = df[colname].tolist()
        search_keywords_str = ', '.join(search_keywords_list)
    else:
        search_keywords_str, search_keywords_list = IO_string_util.process_comma_separated_string_list(search_keywords_list, case_sensitive)

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
        search_word_header = 'Search Word in Sentence'
        label='_sent'
    else:
        search_word_header = 'Search Word in Document'
        label='_doc'
    if search_by_dictionary:
        label=label+'_dict'
    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='search_word'+label,
                                                       silent=False)

    if outputDir == '':
        return

    subCorpusDir=''
    if create_subcorpus_var:
        # create a subcorpus subdirectory of the output sub directory
        outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                           label='search_word' + label,
                                                           silent=False)
        # create a subdirectory labeled subcorpus_search of the txt subsample files inside the input folder
        subCorpusDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, inputDir,
                                                           label='subcorpus_search',
                                                           silent=False)
    search_list = ''
    all_adjacent_words_allDocs = ''
    all_adjacent_sentences_allDocs = ''
    all_found_sentences_allDocs = ''
    all_search_keywords_NOT_found = []
    all_found_csv_sentences_records_allDocs = []
    all_found_csv_words_minusK_plusK_records_allDocs = []
    all_found_csv_words_minusK_plusK_records_oneDoc = []

    docIndex = 0
    first_occurrence_index = -1

    outputFilename_csv_sentence = ''
    # outputDir_sentences_extract = ''
    # outputDir_sentences_extract_wo_searchword = ''
    outputFilename_extract_w_searchword = ''
    outputFilename_extract_wo_searchword = ''
    nDocsExtractOutput = 0
    nDocsExtractMinusOutput = 0

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                       "Started running the Word search function at",
                                        True, '', True, '', False)


    # nlp = stanza.Pipeline(lang=lang, processors='tokenize, lemma')
    #
    # processing corpus files

    # when lemmatizing, the search words also need to be lemmatized
    if lemmatize:
        import NGrams_CoOccurrences_util
        # lemmatized_search_keywords_list, lemmatized_search_word_str = NGrams_CoOccurrences_util.lemmatize_search_words(search_keywords_list)
        lemmatized_search_keywords_list, lemmatized_search_word_str = NGrams_CoOccurrences_util.lemmatize_search_words(search_keywords_str)
        search_keywords_list=lemmatized_search_keywords_list

    for file in files:
        docIndex += 1
        _, tail = os.path.split(file)
        print("Processing file " + str(docIndex) + "/" + str(nFile) + ' ' + tail)
        # if search_by_dictionary:
        #     break
        if search_by_dictionary or search_by_search_keywords:
            output_dir_path = inputDir + os.sep + "search_result_csv"
            if file[-4:] != '.txt':
                continue
        f_doc = open(file, "r", encoding='utf-8', errors='ignore')
        docText = f_doc.read()
        f_doc.close()
        import NGrams_CoOccurrences_util
        docText = NGrams_CoOccurrences_util.prepare_text_with_options(docText, case_sensitive, exact_word_match, lemmatize, lang)

# search in document, regardless of sentence -----------------------------------------------
        if not search_within_sentence:
            search_keywords_found, search_keywords_NOT_found, corpus_to_copy, all_found_csv_sentences_records_oneDoc = \
                search_in_document (file, create_subcorpus_var, corpus_to_copy,
                    docText, docIndex,
                    search_keywords_list, search_keywords_str, case_sensitive, lemmatize, exact_word_match)

            if len(search_keywords_NOT_found)>0:
                #@@
                all_search_keywords_NOT_found.extend(search_keywords_NOT_found)
            if len(all_found_csv_sentences_records_oneDoc)>0:
                all_found_csv_sentences_records_allDocs.append(all_found_csv_sentences_records_oneDoc)

            chart_title = 'Frequency Distribution of Documents with Search Words\n' + search_keywords_str

# search in sentence  -----------------------------------------------
        else:
            # the function search_in_sentence will loop through every sentence in the corpus
            #   it will process the same sentences from different docs!!!
            search_keywords_found, search_keywords_NOT_found, corpus_to_copy, all_adjacent_words_oneDoc, \
                    all_adjacent_sentences_oneDoc, all_found_sentences_oneDoc, all_found_csv_words_minusK_plusK_records_oneDoc, all_found_csv_sentences_records_oneDoc = \
                search_in_all_sentences_oneDoc(file, create_subcorpus_var, corpus_to_copy,
                        docText, docIndex,
                        form_lemma_pair, lang,
                        search_keywords_list, case_sensitive, lemmatize,
                        exact_word_match, search_keywords_found,
                        minus_K_var, plus_K_var)

            # csv output files
            if len(search_keywords_NOT_found)>0:
                all_search_keywords_NOT_found.extend(search_keywords_NOT_found)
            if len(all_found_csv_words_minusK_plusK_records_oneDoc)>0:
                all_found_csv_words_minusK_plusK_records_allDocs.append(all_found_csv_words_minusK_plusK_records_oneDoc)
            if len(all_found_csv_sentences_records_oneDoc)>0:
                all_found_csv_sentences_records_allDocs.append(all_found_csv_sentences_records_oneDoc)

            # txt output files_
            all_adjacent_words_allDocs = all_adjacent_words_allDocs + ' ' + all_adjacent_words_oneDoc
            all_adjacent_sentences_allDocs = all_adjacent_sentences_allDocs + ' ' + all_adjacent_sentences_oneDoc
            all_found_sentences_allDocs = all_found_sentences_allDocs + ' ' + all_found_sentences_oneDoc

# write all output files -----------------------------------------------------------------
# write csv file headers -------------------------------------------------------------------
    if search_within_sentence:
        label = '_sent'
    else:
        label = '_doc'

    # both within documents and within sentences searches produce outputFilename_csv_word
    outputFilename_csv_word = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                                      '.csv',
                                                                      'search_word' + label)
    filesToOpen.append(outputFilename_csv_word)

    outputFilename_csv_word_NOT_found = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                                      '.csv',
                                                                      'search_word_NOT_found' + label)

    outputFilename_csv_distinct_word_NOT_found = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                                      '.csv',
                                                                      'distinct_search_word_NOT_found' + label)

# keywords NOT found applies to both documents and sentences searches
    # convert list to set to produce distinct values
    # all_search_keywords_NOT_found_set = set(all_search_keywords_NOT_found)
    # # convert set back to list
    # all_search_keywords_NOT_found=list(all_search_keywords_NOT_found_set)
    # sort the list of keywords not found
    all_search_keywords_NOT_found.sort()
    df = pd.DataFrame(all_search_keywords_NOT_found)
    # insert column names in dataframe
    # df.columns = ['Searched keyword NOT found', 'Document ID', 'Document']

    # 0 is the column 'Searched keyword NOT found'
    # group and compute the frequency of 'Searched keyword NOT found' (column 0) in dataframe
    df.groupby([0]).count()
    df['Frequency'] = df[0].map(df[0].value_counts())
    # keywords with a frequency equal to the number of files in corpus signals keywords not found anywhere in the corpus
    # nfile as criterion only works for document searches!!!
    df = df.loc[df['Frequency'] == nFile]
    series = df.iloc[:, 0]
    # convert series into a dataframe
    df = series.to_frame().reset_index()
    # drop the index column introduced by the conversion
    df = df.drop('index', axis=1)
    # drop any duplicate keywords; we just a list of distinct values
    df = df.drop_duplicates()
    distinct_keywords_not_found_list = df[0].to_list()
    distinct_keywords_not_found_list.insert(0, 'Searched keyword NOT found')
    IO_error = IO_csv_util.list_to_csv(GUI_util.window, distinct_keywords_not_found_list,
                                       outputFilename_csv_distinct_word_NOT_found)
    if not IO_error:
        filesToOpen.append(outputFilename_csv_distinct_word_NOT_found)

# search in document, regardless of sentence -----------------------------------------------
    if not search_within_sentence:
        # the within document option does not produce wordclouds. There is no point since entire documents containing the seatrch words would be processed
        #   these documents can be exported and visualized separately for wordclouds
        # # keywords NOT found
        # all_search_keywords_NOT_found.sort()
        # df = pd.DataFrame(all_search_keywords_NOT_found)
        # # insert column names in dataframe
        # df.columns = ['Searched keyword NOT found', 'Document ID', 'Document']
        # # group and compute the frequency of 'Searched keyword NOT found' in dataframe
        # df.groupby('Searched keyword NOT found').count()
        # df['Frequency'] = df['Searched keyword NOT found'].map(df['Searched keyword NOT found'].value_counts())
        # df = df.loc[df['Frequency'] == nFile]
        # series = df.iloc[:,0]
        # df = series.to_frame().reset_index()
        # df = df.drop('index', axis=1)
        # df = df.drop_duplicates()
        # distinct_keywords_not_found_list = df['Searched keyword NOT found'].to_list()
        # distinct_keywords_not_found_list.insert(0,'Searched keyword NOT found')
        # IO_error = IO_csv_util.list_to_csv(GUI_util.window, distinct_keywords_not_found_list,
        #                                    outputFilename_csv_distinct_word_NOT_found)
        # if not IO_error:
        #     filesToOpen.append(outputFilename_csv_distinct_word_NOT_found)

        header = ['Searched keyword NOT found', 'Document ID', 'Document']
        all_search_keywords_NOT_found.insert(0, header)

        IO_error = IO_csv_util.list_to_csv(GUI_util.window, all_search_keywords_NOT_found,
                                           outputFilename_csv_word_NOT_found)
        if not IO_error:
            filesToOpen.append(outputFilename_csv_word_NOT_found)

        # keywords found
        header = [search_word_header, "Frequency of occurrence", "Document ID", "Document"]
        with open(outputFilename_csv_word, 'w', newline='') as f_csv:
            writer = csv.writer(f_csv)
            writer.writerow(header)  # write out all the csv file records found
            # for i in range(len(all_found_csv_sentences_records_allDocs)):
            for i in range(len(all_found_csv_sentences_records_allDocs)):
                for j in range(len(all_found_csv_sentences_records_allDocs[i])):
                    try:
                        writer.writerow(all_found_csv_sentences_records_allDocs[i][j])
                        # document search works for newspaper articles
                        # document search works for Jiang Li
                        # document search works for CGWR
                        # writer.writerow(all_found_csv_sentences_records_allDocs[i][0])
                    except:
                        continue
        f_csv.close()

# search in sentence
    else:
        header = ['Searched keyword NOT found', 'Sentence ID', 'Sentence', 'Document ID', 'Document']
        all_search_keywords_NOT_found.insert(0, header)
        IO_error = IO_csv_util.list_to_csv(GUI_util.window, all_search_keywords_NOT_found[2],
                                           outputFilename_csv_word_NOT_found)
        if not IO_error:
            filesToOpen.append(outputFilename_csv_word_NOT_found)

        # headers for csv file for word FOUND
        header = [search_word_header, "Number of sentences", "Sentence ID of first occurrence",
                  "Relative position in document",
                  "Frequency of occurrence", "Sentence ID", "Sentence", "Document ID", "Document"]

        header_minusK_plusK = ["Minus K Value of Words (" + str(
            minus_K_var) + ")", search_word_header, "Plus K Value of Words (" + str(
            plus_K_var) + ")", "Number of sentences", "Sentence ID of first occurrence",
                               "Relative position in document",
                               "Frequency of occurrence", "Sentence ID", "Sentence", "Document ID", "Document"]

        if extract_sentences:
            # setup output text files

            outputFilename_extract_w_searchword = os.path.join(outputDir) + \
                                                               "NLP_extract_with_searchwords.txt"
            outputFilename_extract_wo_searchword = os.path.join(outputDir) + \
                                                                "NLP_extract_wo_searchwords.txt"

# write csv output files -----------------------------------------------------------------
        with open(outputFilename_csv_word, 'w', newline='') as f_csv:
            writer = csv.writer(f_csv)

            if minus_K_var > 0 or plus_K_var > 0:
                writer.writerow(header_minusK_plusK)  # write out all the csv file records found
                # [i][j] sentence search works for Jiang Li (len 1, 13) -K + K 2 2
                # [i][j] sentence search works for newspaper articles (2, 1) -K + K 2 2
                # [i][j] sentence search works for CGWR (50, 19) -K + K 2 2
                for i in range(len(all_found_csv_words_minusK_plusK_records_allDocs)):
                    for j in range(len(all_found_csv_words_minusK_plusK_records_allDocs[i])):
                        try:
                            writer.writerow(all_found_csv_words_minusK_plusK_records_allDocs[i][j])
                        except:
                            continue
            else:
                writer.writerow(header)  # write out all the csv file records found
                for i in range(len(all_found_csv_sentences_records_allDocs)): # news 2; Jiang 1
                    for j in range(len(all_found_csv_sentences_records_allDocs[i])):
                        try:
                            # [i][j] works for Jiang Li (len 1, 13), newspaper articles (2, 1), CGWR (50, 19)
                            writer.writerow(all_found_csv_sentences_records_allDocs[i][j])
                        except:
                            continue
            f_csv.close()

            if extract_sentences:

# write txt output files -----------------------------------------------------------------

                with open(outputFilename_extract_w_searchword, 'w', encoding='utf-8',
                          errors='ignore') as outputFile_extract_w_searchword:
                    outputFile_extract_w_searchword.write(
                        all_found_sentences_allDocs)  # write out all the sentences containing the search word
                outputFile_extract_w_searchword.close()
                with open(outputFilename_extract_wo_searchword, 'w', encoding='utf-8',
                          errors='ignore') as outputFile_extract_wo_searchword:
                    outputFile_extract_wo_searchword.write(
                        all_adjacent_sentences_allDocs)  # write out all the sentences NOT containing the search word
                outputFile_extract_wo_searchword.close()

    # when creating a subcorpus copy all the files in the set to a subdirectory 'subcorpus_search' of the input directory
    if create_subcorpus_var and len(corpus_to_copy) > 0:
        for file in corpus_to_copy:
            shutil.copy(file, subCorpusDir)
        mb.showwarning(title='Warning',message='The search function has created a subcorpus of the files containing the search word(s) "'
                        + str(search_keywords_list) + '" as a subdirectory called "subcorpus_search" of the input directory:\n\n'
                        + subCorpusDir + '\n\nA set of csv files have also been exported to the output  directory.')


# visualize results for document searches ---------------------------------------------------------------

    if not search_within_sentence:
        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFilename_csv_word, outputDir,
                                                  columns_to_be_plotted_xAxis=[],
                                                  columns_to_be_plotted_yAxis=['Frequency of occurrence'],
                                                  chart_title=chart_title,
                                                  count_var=1,
                                                  # 1 for alphabetic fields that need to be coounted;  1 for numeric fields (e.g., frequencies, scorers)
                                                  hover_label=[],
                                                  outputFileNameType='',
                                                  column_xAxis_label=search_keywords_str,
                                                  groupByList=['Document'],
                                                  plotList=[],
                                                  chart_title_label='')
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

# visualize results for within sentence searches ---------------------------------------------------------------

    else:
        if not search_keywords_found:
            mb.showwarning(title='Search word(s) not found',
                           message='The search keywords:\n\n   ' + search_keywords_str + '\n\nwere not found in your input document(s) with the following set of search options:\n\n  '+ str('\n  '.join(search_options_list)))
            outputFilename_csv_word = ''
        else:
            try:
                df = pd.read_csv(outputFilename_csv_word)
            except UnicodeEncodeError:
                # mb.showwarning(title='Output file error', message="Could not write the file " + outputFilename + "\n\nA file with the same name is already open. Please, close the Excel file and then click OK to resume.")
                mb.showwarning(title='Input file error', message="Could not read the file " +
                                    outputFilename_csv_word + "\n\nThe file is not utf-8")
                df = pd.read_csv(outputFilename_csv_word, encoding="ISO-8859-1")
            # except UnicodeEncodeError:
            #     print('   Filename ' + outputFilename_csv_word + ' is not utf-8')
            unique_words = df["Search Word in Sentence"].unique()
            # Save separate CSVs for each unique search word
            file_paths = []
            for word in unique_words:
                filtered_df = df[df["Search Word in Sentence"] == word]
                output_filename = f"outputFilename_csv_word_{word}.csv"
                output_path = os.path.join(outputDir, output_filename)
                filtered_df.to_csv(output_path, index=False)
                file_paths.append(output_path)
            for outputFilename_csv_word in file_paths:
            # bar charts ----------------------------------------------------------------------
                chart_title = 'Frequency Distribution of Search Words\n' + search_keywords_str
                outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFilename_csv_word, outputDir,
                                                                           columns_to_be_plotted_xAxis=['Search Word in Sentence'],
                                                                           columns_to_be_plotted_yAxis=['Frequency of occurrence'],
                                                                           chart_title=chart_title,
                                                                           count_var=1,  # 1 for alphabetic fields that need to be coounted;  1 for numeric fields (e.g., frequencies, scorers)
                                                                           hover_label=[],
                                                                           outputFileNameType='',
                                                                           column_xAxis_label=search_keywords_str,
                                                                           groupByList=['Document'],
                                                                           plotList=[],
                                                                           chart_title_label='')
                if outputFiles!=None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)

    # wordclouds ----------------------------------------------------------------------------

            outputFiles = visualize_wordcloud(all_found_sentences_allDocs, search_keywords_str, 'all_sents_with_searchwords',
                                              inputFilename, inputDir, outputDir,
                                              configFileName, filesToOpen, lemmatize)

            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            if minus_K_var > 0 and plus_K_var > 0:
                outputFiles = visualize_wordcloud(all_adjacent_sentences_allDocs, search_keywords_str, 'K+K_sents_around_searchwords',
                                                  inputFilename, inputDir, outputDir,
                                                  configFileName, filesToOpen, lemmatize)

                if outputFiles != None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)

                outputFiles = visualize_wordcloud(all_adjacent_words_allDocs, search_keywords_str, '-K+K_words_around_searchwords',
                                                  inputFilename, inputDir, outputDir,
                                                  configFileName, filesToOpen, lemmatize)

                if outputFiles != None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running the Search word function at',
                                       True, '', True, startTime,  False)

    # end of function search_sentences_documents
    return filesToOpen

def visualize_wordcloud(textToProcess, search_keywords_str, label, inputFilename, inputDir, outputDir, configFileName, filesToOpen, lemmatize):
    if len(textToProcess)<15:
        mb.showwarning(title='Warning',message='The text required to produce a wordcloud is too short.\n"'
                        + textToProcess + '\n\nWordcloud exits.')
        return
    # write to text file textToProcess for wordcloud
    outputFilenameTxt = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.txt', label)
    filesToOpen.append(outputFilenameTxt)
    outputTxtFile = open(outputFilenameTxt, "w", encoding="utf-8", errors="ignore")
    outputTxtFile.write(textToProcess)
    outputTxtFile.close()

    # run with all default values;
    use_contour_only = False
    max_words = 100
    font = 'Default'
    prefer_horizontal = .9
    exclude_stopwords = False
    exclude_punctuation = False
    lowercase = False
    differentPOS_differentColors = False
    differentColumns_differentColors = False
    csvField_color_list = []
    doNotListIndividualFiles = True
    collocation = False
    import wordclouds_util
    wordcloud_title='Wordcloud for word search in file(s) ('+search_keywords_str+')'
    outputFiles = wordclouds_util.python_wordCloud(outputFilenameTxt, '', outputDir, configFileName, selectedImage="",
                                              use_contour_only=use_contour_only,
                                              wordcloud_title=wordcloud_title,
                                              prefer_horizontal=prefer_horizontal, font=font, max_words=max_words,
                                              lemmatize=lemmatize, exclude_stopwords=exclude_stopwords,
                                              exclude_punctuation=exclude_punctuation, lowercase=lowercase,
                                              differentPOS_differentColors=differentPOS_differentColors,
                                              differentColumns_differentColors=differentColumns_differentColors,
                                              csvField_color_list=csvField_color_list,
                                              doNotListIndividualFiles=doNotListIndividualFiles,
                                              openOutputFiles=False, collocation=collocation)

    # end of function search_sentences_documents
    return outputFiles
