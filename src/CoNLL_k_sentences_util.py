#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 23:05:52 2022

@author: claude
edited by Naman Sahni 9/23.2022
"""
from pydoc import Doc
import pandas as pd
import string
# from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza

import IO_files_util
import charts_util
import statistics_txt_util

def k_sent(inputFilename, outputDir, createCharts, chartPackage, Begin_K_sent_var, End_K_sent_var):
    filesToOpen=[]

    label='CoNLL_' + str(Begin_K_sent_var) + '-' + str(End_K_sent_var) + '-sent'
    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, '', outputDir, label=label,
                                                       silent=True)
    if outputDir == '':
        return outputDir, filesToOpen

    conll = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    head = ["First/Last Sentences", "K value", "Words Count","Nouns Count","Nouns Proportion", "Verbs Count", "Verbs Proportion", "Adjectives Count","Adjectives Proportion","Proper-Nouns Count","Proper-Nouns Proportion", "Document ID", "Document"]
    result = []

    head_rep_words = ["Firs/Last Sentences", "K value", "Word", "Word ID", "Sentence ID", "Sentence", "Document ID", "Document"]
    result_rep_words = []
    result_rep_words_temp = []

    rep_words_first = []
    rep_words_last = []


    #print(filtered_lemmas)


    txt = ""

    for i in range(1, max(conll["Document ID"])+1):
        txt = ""
        doc_conll = conll.loc[conll["Document ID"] == i]
        outputFilename_rep_words = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv',
                                                                 'CoNLL_K_sent_rep_words'+str(Begin_K_sent_var),
                                                                 '', '', '', '',
                                                                 False,
                                                                 True)
        for l in doc_conll["Form"]:
            if l in string.punctuation:
                txt += l + " "
            else:
                txt += " " + l

        #txt.replace("  ", " ")
        #print(txt)
        from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza
        sent = sentences = sent_tokenize_stanza(stanzaPipeLine(txt))
        sentenceID = 0

        for doc in doc_conll["Document"]:
            DOC = doc
            break

        for s in sent:

            sentenceID = sentenceID + 1

            words = word_tokenize_stanza(stanzaPipeLine(s))

            words = statistics_txt_util.excludeStopWords_list(words)

            filtered_words = [word for word in words if word.isalpha()]

            for wrdID, wrd in enumerate(filtered_words):
                if sentenceID <= Begin_K_sent_var:
                    result_rep_words_temp.append(["First", Begin_K_sent_var, wrd, wrdID+1, sentenceID, s, i, DOC])
                    rep_words_first.append(wrd)

                elif sentenceID > len(sentences) - End_K_sent_var:
                    result_rep_words_temp.append(["Last", End_K_sent_var, wrd, wrdID+1, sentenceID, s, i, DOC])
                    rep_words_last.append(wrd)

        result_rep_words.extend([sublist for sublist in result_rep_words_temp if sublist[2] in rep_words_first and sublist[2] in rep_words_last])

        df_rep_words = pd.DataFrame(result_rep_words, columns=head_rep_words)
        if df_rep_words.empty:
            outputFilename_rep_words = None
        else:
            df_rep_words.to_csv(outputFilename_rep_words, encoding='utf-8', index=False)
            filesToOpen.append(outputFilename_rep_words)

            columns_to_be_plotted_xAxis=[]
            columns_to_be_plotted_yAxis=['Word']
            count_var=1
            outputFiles = charts_util.visualize_chart(createCharts, chartPackage,
                                                            outputFilename_rep_words, outputDir,
                                                            columns_to_be_plotted_xAxis,columns_to_be_plotted_yAxis,
                                                            chart_title="Frequency Distribution of Repeated Words in first and last K (" + str(Begin_K_sent_var)+'-'+str(End_K_sent_var) +") sentences",
                                                            outputFileNameType=str(Begin_K_sent_var)+'-'+str(End_K_sent_var)+'-sent_rep_words',
                                                            column_xAxis_label='Words',
                                                            count_var=count_var,
                                                            hover_label=[],
                                                            groupByList=[], # ['Document ID', 'Document'],
                                                            plotList=[], #['Concreteness (Mean score)'],
                                                            chart_title_label='') #'Concreteness Statistics')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)












    for i in range(1, max(conll["Document ID"])+1):
        doc_conll = conll.loc[conll["Document ID"] == i]
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv',
                                                                 label,
                                                                 '', '', '', '',
                                                                 False,
                                                                 True)
        if max(doc_conll['Sentence ID']) <= 2 * Begin_K_sent_var:
            if(doc_conll["Sentence ID"]<=Begin_K_sent_var):
                ksentences_first = doc_conll.loc[doc_conll["Sentence ID"]]



            else:
                ksentences_last = doc_conll.loc[doc_conll["Sentence ID"]]

        else:
            ksentences_first = doc_conll.loc[(doc_conll["Sentence ID"] <= Begin_K_sent_var)]
            ksentences_last = doc_conll.loc[(doc_conll["Sentence ID"] > max(doc_conll['Sentence ID']) - End_K_sent_var)]

        #ksentences = ksentences_first + ksentences_last
        word_count_first = len(ksentences_first['POS']) - ksentences_first['DepRel'].value_counts()["punct"]
        verb_count_first = 0
        noun_count_first = 0
        adj_count_first = 0
        pp_count_first = 0#proper nouns

        word_count_last = len(ksentences_last['POS']) - ksentences_last['DepRel'].value_counts()["punct"]
        verb_count_last = 0
        noun_count_last = 0
        adj_count_last = 0
        pp_count_last = 0#proper nouns
        for pos in ksentences_first['POS']:
            if "NN" in pos: # nouns
                noun_count_first +=1
                if "NNP" in pos: # proper nouns
                    pp_count_first += 1
            elif "VB" in pos: # verbs
                verb_count_first +=1
            elif "JJ" in pos: # adjectives
                adj_count_first +=1
        # print("dataframe: ")
        # print(ksentences)
        for doc in ksentences_first['Document']:
            DOC = doc # as doc is in CoNLL table, doc already as the hyperlink
            break

        for pos in ksentences_last['POS']:
            if "NN" in pos: # nouns
                noun_count_last +=1
                if "NNP" in pos: # proper nouns
                    pp_count_last += 1
            elif "VB" in pos: # verbs
                verb_count_last +=1
            elif "JJ" in pos: # adjectives
                adj_count_last +=1
        # print("dataframe: ")
        # print(ksentences)
        for doc in ksentences_last['Document']:
            DOC = doc # as doc is in CoNLL table, doc already as the hyperlink
            break

        temp_first =["First", Begin_K_sent_var, word_count_first, noun_count_first, noun_count_first / word_count_first,
                      verb_count_first, verb_count_first / word_count_first, adj_count_first, adj_count_first / word_count_first,pp_count_first, pp_count_first / word_count_first, i, DOC]

        temp_last = ["Last", End_K_sent_var, word_count_last, noun_count_last, noun_count_last / word_count_last,
                      verb_count_last, verb_count_last / word_count_last, adj_count_last, adj_count_last / word_count_last,pp_count_last, pp_count_last / word_count_last, i, DOC]
        result.append(temp_first)
        result.append(temp_last)
        df = pd.DataFrame(result, columns=head)
        if df.empty:
            outputFilename = None
        else:
            df.to_csv(outputFilename, encoding='utf-8', index=False)
            filesToOpen.append(outputFilename)

            columns_to_be_plotted_xAxis=[]
            columns_to_be_plotted_yAxis=['Nouns Proportion','Verbs Proportion','Adjectives Proportion','Proper-Nouns Proportion']
            count_var=0
            outputFiles = charts_util.visualize_chart(createCharts, chartPackage,
                                                            outputFilename, outputDir,
                                                            columns_to_be_plotted_xAxis,columns_to_be_plotted_yAxis,
                                                            chart_title="Frequency Distribution of Different Proportions in First and Last K (" + str(Begin_K_sent_var)+'-'+str(End_K_sent_var) + ") Sentences",
                                                            outputFileNameType='k_sent',
                                                            column_xAxis_label='Tags',
                                                            count_var=count_var,
                                                            hover_label=[],
                                                            groupByList=[], # ['Document ID', 'Document'],
                                                            plotList=[], #['Concreteness (Mean score)'],
                                                            chart_title_label='') #'Concreteness Statistics')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    return outputDir, filesToOpen


