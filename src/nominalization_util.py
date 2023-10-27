#written by Catherine Xiao, Apr 2018
#edited by Elaine Dong, Dec 04 2019
#edited by Roberto Franzosi, Nov 2019, October 2020

# https://stackoverflow.com/questions/2836959/adjective-nominalization-in-python-nltk
# https://stackoverflow.com/questions/45109767/get-verb-from-noun-wordnet-python

# https://github.com/topics/nominalization
# https://pypi.org/project/qanom/0.0.1/

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"Nominalization",['tkinter','nltk','pywsd','wn','csv','re','os','collections'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb

# check averaged_perceptron_tagger
IO_libraries_util.import_nltk_resource(GUI_util.window,'taggers/averaged_perceptron_tagger','averaged_perceptron_tagger')
# check punkt
IO_libraries_util.import_nltk_resource(GUI_util.window,'tokenizers/punkt','punkt')
# check WordNet
IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/WordNet','WordNet')
from nltk.corpus import wordnet as wn

# from Stanza_functions_util import stanzaPipeLine, sent_tokenize_stanza
# MUST use this version or code will break no longer true; pywsd~=1.2.4 pip install pywsd~=1.2.4; even try pip install pywsd=1.2.2
#   or this version pip install pywsd==1.0.2
# https://github.com/alvations/pywsd/issues/65
# pywsd depends upon wn below; if the code breaks reinstall wn
# pywsd Python word sense disambiguation
#   https://pypi.org/project/pywsd/
from pywsd import disambiguate
# pip install wn==0.0.23
import string
import re
from collections import Counter
import nltk
import pandas as pd


import IO_files_util
import IO_csv_util
import IO_user_interface_util
import charts_util
import GUI_IO_util
import config_util


# RUN section ______________________________________________________________________________________________________________________________________________________

#first_section is to extract the word from "syns".
# syns.name() of "intention" is "purpose.n.01". So "first_section" gets everything before the first period: "purpose"

#params: sent > string
#result_true_false_each_noun #includes word='NO NOMINALIZATION'
#count #includes word='NO NOMINALIZATION'
#count1 #excludes word='NO NOMINALIZATION'

def check_word_for_nominalization(word,nominalized_verbs_list):
    skip_record = False
    if not 'ent' in word[-3:] and not 'ing' in word[-3:] and not 'ion' in word[-3:] and \
            not 'ance' in word[-4:] and not 'ence' in word[-4:]:
        skip_record = True
    # check against a dictionary of nominalized verbs non ending in the standard nominalized verbs
    for index, row in nominalized_verbs_list.iterrows():
        if row[0] == word:
            skip_record = False
            break
    return skip_record
def nominalized_verb_detection(docID,doc,dateStr, sent,check_ending,nominalized_verbs_list):

    first_section = re.compile("^(.+?)\.")
    noun_cnt = Counter()
    nominalized_cnt = Counter()

    # sentences = tokenize.sent_tokenize(sent)
    from Stanza_functions_util import stanzaPipeLine, sent_tokenize_stanza
    sentences = sent_tokenize_stanza(stanzaPipeLine(sent))

    result_true_false_each_noun = []
    result_specific_document = []
    verbs = []
    true_word = []
    false_word = []
    # word count for the sentence
    word_count = []
    # number of nominalization in the sentence
    nomi_count = []
    sen_id = -1
    # to print the sentence in output
    sentence = []
    # to print the nominalizations in each sentence
    nomi_sen = []
    nomi_sen_ = ""
    def is_pos(s, pos):
        # print(s)
        return s.split('.')[1] == pos
    for each_sen in sentences:
        sen_id += 1
        nomi_count.append(0)
        word_count.append(0)
        sentence.append(each_sen)
        words_with_tags = disambiguate(each_sen)
        for tup in words_with_tags:
            word, syns = tup
            if (word in string.punctuation) or (word == "\"") or (word[0] == "\'") or (word[0] == "`"):
                continue
            word_count[sen_id] += 1
            derivationals = []
            word = word.lower()
            if word in true_word:
                nomi_count[sen_id] += 1
                if nomi_sen_ == "":
                    nomi_sen_ = word
                else:
                    nomi_sen_ = nomi_sen_ + "; " + word
                noun_cnt[word] += 1
                nominalized_cnt[word] += 1
                continue
            if word in false_word:
                noun_cnt[word] += 1
                continue
            if syns:
                #look at only nouns
                if not is_pos(syns.name(), 'n'):
                    # TODO do not save; leads to huge file
                    # result_true_false_each_noun.append([word, '', False])
                    # false_word.append(word)
                    # noun_cnt[word] += 1
                    continue
                if wn.lemmas(word):
                    for lemma in wn.lemmas(word):
                        derive = lemma.derivationally_related_forms()
                        if derive not in derivationals and derive:
                            derivationals.append(derive)
                else:
                    try:
                        derivationals = syns.lemmas()[0].derivationally_related_forms()
                    except:
                        pass
                stem = first_section.match(str(syns.name())).group(1)
                found = False
                for deriv in derivationals:
                    if is_pos(str(deriv), 'v'):
                        # original deriv_str = str(deriv)[7:-3].split('.')[3]
                        # deriv is a list with typically one item
                        #   [Lemma('construct.v.01.construct)
                        # sometimes the list can have multiple items
                        #   deriv [Lemma('dramatize.v.02.dramatize), Lemma('dramatize.v.02.dramatise')]
                        #   when multiple items are given taken the first in the list
                        #   deriv[0]
                        try:
                            deriv_str = str(deriv[0])[7:-2].split('.')[3]
                        except:
                            deriv_str = str([deriv][0])[7:-2].split('.')[3]
                        if word=='lights':
                            print('wrong')
                        print('   NOUN:', word, ' VERB:',deriv_str)
                        try:
                            deriv_str = str(deriv[0])[7:-2].split('.')[3]
                        except:
                            continue
                        # deriv_str is now the verb that is being lemmatized
                        if check_ending:
                            skip_record = check_word_for_nominalization(word,nominalized_verbs_list)
                            if skip_record:
                                continue
                        if dateStr != '':
                            result_true_false_each_noun.append([word, deriv_str, docID, IO_csv_util.dressFilenameForCSVHyperlink(doc), dateStr])
                        else:
                            result_true_false_each_noun.append([word, deriv_str, docID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])
                        verbs.append(deriv_str)
                        true_word.append(word)
                        noun_cnt[word] += 1
                        if nomi_sen_ == "":
                            nomi_sen_ = word
                        else:
                            nomi_sen_ = nomi_sen_ + "; " + word
                        nominalized_cnt[word] += 1
                        found = True
                        break
                if found:
                    nomi_count[sen_id] += 1
                    continue
                # else: # TODO do not save; leads to a huge unnecessary file
                #     result_true_false_each_noun.append([word, '', False]) #includes word='NO NOMINALIZATION'
                #     noun_cnt[word] += 1
        nomi_sen.append(nomi_sen_)
        nomi_sen_ = ""
    for i in range(sen_id+1):
        if word_count[i]>0:

            if nomi_count[i]>0:
                if dateStr!='':
                    result_specific_document.append([word_count[i], nomi_sen[i], nomi_count[i], 100.0 * nomi_count[i] / word_count[i],
                               i + 1, sentence[i], docID, IO_csv_util.dressFilenameForCSVHyperlink(doc), dateStr])
                else:
                    result_specific_document.append(
                        [word_count[i], nomi_sen[i], nomi_count[i], 100.0 * nomi_count[i] / word_count[i],
                         i + 1, sentence[i], docID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])
        else:
            # result_specific_document.append([docID, IO_csv_util.dressFilenameForCSVHyperlink(doc), i+1, sentence[i], word_count[i], nomi_sen[i], nomi_count[i]])
            if nomi_count[i]>0:
                if dateStr!='':
                    result_specific_document.append(
                        [word_count[i], nomi_sen[i], nomi_count[i], sentence[i], docID, IO_csv_util.dressFilenameForCSVHyperlink(doc), dateStr])
                else:
                    result_specific_document.append(
                        [word_count[i], nomi_sen[i], nomi_count[i], sentence[i], docID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])
    # print(result_specific_document)
    # result_true_false_each_noun contains a list of each word TRUE/FALSE values for nominalization for the document processed
    # result_specific_document contains a list of docID, docName, sentence... for the document processed
    return result_true_false_each_noun, result_specific_document, noun_cnt, nominalized_cnt

def nominalization(inputFilename,inputDir, outputDir, config_filename, config_input_output_numeric_options, openOutputFiles,createCharts,chartPackage,doNotListIndividualFiles, check_ending):

    filesToOpen = []  # Store all files that are to be opened once finished

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='NOM',
                                                       silent=False)
    if outputDir == '':
        return

    # first_section is to extract the word from "syns".
    # syns.name() of "intention" is "purpose.n.01". So "first_section" gets everything before the first period: "purpose"

    # #params: sent > string
    # #result_true_false_each_noun #includes word='NO NOMINALIZATION'
    # #count #includes word='NO NOMINALIZATION'
    # #count1 #excludes word='NO NOMINALIZATION'

    nltk.data.path.append('./nltk_data')

    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False,
                                          configFileName=config_filename)
    nDocs = len(inputDocs)
    if nDocs == 0:
        return filesToOpen

    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running Nominalization at',
                                       True, '', True, '', False)

    #add all into a sum
    result_dir = []
    docID=0
    result_all_documents = []
    result_true_false_each_noun_all_documents=[]
    counter_nominalized_list = []
    counter_nominalized_list.append(['Nominalized verb', 'Frequency'])
    counter_noun_list = []
    counter_noun_list.append(['Noun', 'Frequency'])

    # build dictionary of nominalized verbs not ending with the standard ending (e.g., attack, assault)
    if check_ending:
        nominalized_verbs_list = pd.read_csv(os.path.join(GUI_IO_util.wordLists_libPath, "nominalized-verbs-list.csv"))

    for doc in inputDocs:

        dateStr = ''
        # get the date options from filename
        filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = config_util.get_date_options(
            config_filename, config_input_output_numeric_options)
        if filename_embeds_date_var:
            date, dateStr, month, day, year = IO_files_util.getDateFromFileName(doc, date_format_var, items_separator_var,
                                                     date_position_var, errMsg=True)

        docID=docID+1
        head, tail = os.path.split(doc)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)
        #open the doc and create the list of result_true_false_each_noun (words, T/F)
        fin = open(doc, 'r',encoding='utf-8',errors='ignore')
        # result_true_false_each_noun contains for each word the False/True nominalization boolean
        # result_specific_document contains the sentence and nominalized values for a specific document
        result_true_false_each_noun, result_specific_document, noun_cnt, nominalized_cnt = nominalized_verb_detection(docID,doc,dateStr, fin.read(),check_ending, nominalized_verbs_list)
        # result_all_documents contains the sentence and nominalized values for all documents
        result_all_documents.extend(result_specific_document)
        result_true_false_each_noun_all_documents.extend(result_true_false_each_noun)
        fin.close()

        if len(inputDir) > 0:
            fname = os.path.basename(os.path.normpath(inputDir))+"_dir"
        else:
            fname=doc


        if len(inputDir) == 0 or doNotListIndividualFiles == False:
            counter_nominalized_list = []
            counter_noun_list = []

            outputFilename_bySentenceIndex = IO_files_util.generate_output_file_name(fname, '', outputDir,
                                                                                  '.csv', 'NOM', 'sent')

            # refresh the headers
            counter_nominalized_list.insert(0,['Nominalized verb', 'Frequency'])
            counter_noun_list.insert(0,['Noun', 'Frequency'])

            if dateStr!='':
                result_specific_document.insert(0, ['Number of words in sentence', 'Nominalized verbs',
                                   'Number of nominalizations in sentence',
                                   'Percentage of nominalizations in sentence',
                                   'Sentence ID', 'Sentence', 'Document ID', 'Document', 'Date'])
            else:
                result_specific_document.insert(0, ['Number of words in sentence', 'Nominalized verbs',
                                                    'Number of nominalizations in sentence',
                                                    'Percentage of nominalizations in sentence',
                                                    'Sentence ID', 'Sentence', 'Document ID', 'Document'])

            # compute frequency of most common nominalized verbs
            for word, freq in nominalized_cnt.most_common():
                counter_nominalized_list.append([word, freq])

            # compute frequency of most common nouns
            for word, freq in noun_cnt.most_common():
                counter_noun_list.append([word, freq])

            head, fname=os.path.split(doc)
            fname=fname[:-4]

            outputFilename_noun_frequencies = IO_files_util.generate_output_file_name(fname, inputDir, outputDir, '.csv', 'NOM',
                                                                            'noun_freq')
            filesToOpen.append(outputFilename_noun_frequencies)
            outputFilename_nominalized_frequencies = IO_files_util.generate_output_file_name(fname,
                                                                            inputDir, outputDir, '.csv', 'NOM',
                                                                             'verb_nom__freq')


            filesToOpen.append(outputFilename_nominalized_frequencies)

            # export nominalized verbs frequencies
            IO_csv_util.list_to_csv(GUI_util.window,counter_nominalized_list,outputFilename_nominalized_frequencies)

            # export nouns
            IO_csv_util.list_to_csv(GUI_util.window,counter_noun_list, outputFilename_noun_frequencies)

            outputFilename_TRUE_FALSE = IO_files_util.generate_output_file_name(fname + '_TRUE_FALSE', '', outputDir,
                                                                           '.csv', 'NOM')

            # TODO this leads to a huge file when processing a directory; comment for now
            filesToOpen.append(outputFilename_TRUE_FALSE)
            # this will export both True and False
            # list_to_csv(outputFilename_TRUE_FALSE, result_true_false_each_noun)
            if dateStr!='':
                result_true_false_each_noun_all_documents.insert(0, ["Noun/Nominalized Verb", "Verb", "Document ID", "Document", "Date"])
            else:
                result_true_false_each_noun_all_documents.insert(0, ["Noun/Nominalized Verb", "Verb", "Document ID", "Document"])

            IO_csv_util.list_to_csv(GUI_util.window,result_true_false_each_noun_all_documents, outputFilename_TRUE_FALSE)

            IO_csv_util.list_to_csv(GUI_util.window,result_specific_document,outputFilename_bySentenceIndex)
            filesToOpen.append(outputFilename_bySentenceIndex)

    if len(inputDir)>0 and doNotListIndividualFiles == True:
        outputFilename_byDocument = IO_files_util.generate_output_file_name(fname, '', outputDir,
                                                                            '.csv', 'NOM', 'verbs_byDoc')

        outputFilename_bySentenceIndex = IO_files_util.generate_output_file_name(fname, '', outputDir,
                                                                                 '.csv', 'NOM', 'sent')
        outputFilename_TRUE_FALSE_dir = IO_files_util.generate_output_file_name(fname + '_TRUE_FALSE', '', outputDir, '.csv', 'NOM')
        outputFilename_dir_noun_frequencies=IO_files_util.generate_output_file_name(fname, '', outputDir, '.csv', 'NOM', 'noun_freq', '', '', '', False, True)
        # outputFilename_dir_nominalized_frequencies=IO_files_util.generate_output_file_name(fname, '', outputDir, '.csv', 'NOM', 'nominal_freq', '', '', '', False, True)
        outputFilename_dir_nominalized_frequencies=IO_files_util.generate_output_file_name(fname, '', outputDir, '.csv', 'NOM', 'nominal_freq')

        if dateStr != '':
            result_all_documents.insert(0, ['Number of words in sentence', 'Nominalized verbs',
                               'Number of nominalizations in sentence', 'Percentage of nominalizations in sentence','Sentence ID', 'Sentence', 'Document ID', 'Document', "Date"])
        else:
            result_all_documents.insert(0, ['Number of words in sentence', 'Nominalized verbs',
                               'Number of nominalizations in sentence', 'Percentage of nominalizations in sentence','Sentence ID', 'Sentence', 'Document ID', 'Document'])
        IO_csv_util.list_to_csv(GUI_util.window,result_all_documents, outputFilename_bySentenceIndex)
        filesToOpen.append(outputFilename_bySentenceIndex)

        # list all verbs as TRUE/FALSE if nominalized
        # TODO  this leads to a huge file when processing a directory; comment for now
        if dateStr!='':
            result_true_false_each_noun_all_documents.insert(0, ["Noun/Nominalized Verb", "Verb", "Document ID", "Document", "Date"])
        else:
            result_true_false_each_noun_all_documents.insert(0, ["Noun/Nominalized Verb", "Verb", "Document ID", "Document"])
        IO_csv_util.list_to_csv(GUI_util.window,result_true_false_each_noun_all_documents, outputFilename_TRUE_FALSE_dir)
        filesToOpen.append(outputFilename_TRUE_FALSE_dir)

        counter_noun_list = []
        counter_noun_list.append(['Noun','Frequency'])
        for word, freq in noun_cnt.most_common():
            counter_noun_list.append([word, freq])
        IO_csv_util.list_to_csv(GUI_util.window,counter_noun_list, outputFilename_dir_noun_frequencies)
        filesToOpen.append(outputFilename_dir_noun_frequencies)

        counter_nominalized_list = []
        counter_nominalized_list.append(['Nominalized verb','Frequency'])
        for word, freq in nominalized_cnt.most_common():
            counter_nominalized_list.append([word, freq])
        IO_csv_util.list_to_csv(GUI_util.window, counter_nominalized_list,outputFilename_dir_nominalized_frequencies)
        filesToOpen.append(outputFilename_dir_nominalized_frequencies)

        if createCharts == True:
            # bar chart of nominalized verbs

            inputFilename = outputFilename_dir_nominalized_frequencies
            columns_to_be_plotted_xAxis=[]
            columns_to_be_plotted_yAxis=[[0, 1]]

            outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, inputFilename, outputDir,
                                                             outputFileLabel='NOM_verb',
                                                             chartPackage=chartPackage,
                                                             chart_type_list=['bar'],
                                                             chart_title='Frequency Distribution of Nominalized Verbs',
                                                             column_xAxis_label_var='Nominalized verb',
                                                             hover_info_column_list=[],
                                                             count_var=0)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

# line chart of frequencies of nominalized verbs by document or date

            columns_to_be_plotted_xAxis=[]

            inputFilename=outputFilename_TRUE_FALSE_dir
            # inputFilename=outputFilename_byDocument
            # these variables are used in charts_util.visualize_chart
            headers = IO_csv_util.get_csvfile_headers (inputFilename)
            groupBy = []
            if 'Date' in headers:
                columns_to_be_plotted_yAxis = [[0, 4]]
                groupBy=['Date']
            else:
                if 'Document' in headers:
                    groupBy=['Document']
                    columns_to_be_plotted_yAxis = [[0, 3]]

            # column_xAxis_label='Nominalized verb'
            # columns_to_be_plotted_xAxis=[]
            # columns_to_be_plotted_yAxis=['Frequency']
            # count_var=1
            # outputFiles = charts_util.visualize_chart(createCharts, chartPackage,
            #                                                 inputFilename, outputDir,
            #                                                 columns_to_be_plotted_xAxis,columns_to_be_plotted_yAxis,
            #                                                 chart_title="Frequency Distribution of Nominalized Verbs]",
            #                                                 outputFileNameType='-verbs_nom',
            #                                                 column_xAxis_label=column_xAxis_label,
            #                                                 count_var=count_var,
            #                                                 hover_label=[],
            #                                                 groupByList=groupBy,
            #                                                 plotList=[],
            #                                                 chart_title_label='')

            outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, inputFilename, outputDir,
                                                             outputFileLabel='NOM_verb',
                                                             chartPackage=chartPackage,
                                                             chart_type_list=['line'],
                                                             chart_title='Frequency Distribution of Nominalized Verbs by Document',
                                                             hover_info_column_list=[],
                                                             column_xAxis_label_var='Document',
                                                             count_var=1)

            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            inputFilename = outputFilename_dir_noun_frequencies
            columns_to_be_plotted_xAxis=[]
            columns_to_be_plotted_yAxis=[[0, 1]]

            outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, inputFilename, outputDir,
                                                             outputFileLabel='NOM_noun',
                                                             chartPackage=chartPackage,
                                                             chart_type_list=['bar'],
                                                             chart_title='Frequency Distribution of Nouns',
                                                             column_xAxis_label_var='Noun',
                                                             hover_info_column_list=[],
                                                             count_var=0)

            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running Nominalization at', True, '', True, startTime)

    return filesToOpen