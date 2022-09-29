#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 23:05:52 2022

@author: claude
edited by Naman Sahni 9/23.2022
"""
from pydoc import Doc
import pandas as pd
import os

import GUI_IO_util
import IO_files_util
import charts_util
import IO_csv_util

def k_sent(inputFilename, outputDir, createCharts, chartPackage):
    filesToOpen=[]

    k_str, useless = GUI_IO_util.enter_value_widget("Enter the number of sentences, K, to be analyzed", 'K',
                                                    1, '', '', '')
    k = int(k_str)
    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, '', outputDir, label='CoNLL_K-sent-' + k_str,
                                                       silent=False)
    if outputDir == '':
        return

    conll = pd.read_csv(inputFilename, encoding='utf-8', error_bad_lines=False)
    head = ["First/Last Sentences", "K value", "Words Count","Nouns Count","Nouns Proportion", "Verbs Count", "Verbs Proportion", "Adjectives Count","Adjectives Proportion","Proper-Nouns Count","Proper-Nouns Proportion", "Document ID", "Document"]
    result = []

    for i in range(1, max(conll["Document ID"])+1):
        doc_conll = conll.loc[conll["Document ID"] == i]
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv',
                                                                 'CoNLL_K_sent',
                                                                 '', '', '', '',
                                                                 False,
                                                                 True)
        if max(doc_conll['Sentence ID']) <= 2 * k:
            if(doc_conll["Sentence ID"]<=k):
                ksentences_first = doc_conll.loc[doc_conll["Sentence ID"]]
            else:
                ksentences_last = doc_conll.loc[doc_conll["Sentence ID"]]
        else:
            ksentences_first = doc_conll.loc[(doc_conll["Sentence ID"] <= k)]
            ksentences_last = doc_conll.loc[(doc_conll["Sentence ID"] > max(doc_conll['Sentence ID']) - k)]
        #ksentences = ksentences_first + ksentences_last
        word_count_first = len(ksentences_first['POStag']) - ksentences_first['DepRel'].value_counts()["punct"]
        verb_count_first = 0
        noun_count_first = 0
        adj_count_first = 0
        pp_count_first = 0#proper nouns

        word_count_last = len(ksentences_last['POStag']) - ksentences_last['DepRel'].value_counts()["punct"]
        verb_count_last = 0
        noun_count_last = 0
        adj_count_last = 0
        pp_count_last = 0#proper nouns
        for pos in ksentences_first['POStag']:
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

        for pos in ksentences_last['POStag']:
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

        temp_first =["First", k, word_count_first, noun_count_first, noun_count_first / word_count_first,
                      verb_count_first, verb_count_first / word_count_first, adj_count_first, adj_count_first / word_count_first,pp_count_first, pp_count_first / word_count_first, i, DOC]

        temp_last = ["Last", k, word_count_last, noun_count_last, noun_count_last / word_count_last,
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
            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage,
                                                            outputFilename, outputDir,
                                                            columns_to_be_plotted_xAxis,columns_to_be_plotted_yAxis,
                                                            chartTitle="Frequency Distribution of Different Proportions in First and Last K (" + str(k) + ") Sentences",
                                                            outputFileNameType='k_sent',
                                                            column_xAxis_label='Tags',
                                                            count_var=count_var,
                                                            hover_label=[],
                                                            groupByList=[], # ['Document ID', 'Document'],
                                                            plotList=[], #['Concreteness (Mean score)'],
                                                            chart_title_label='') #'Concreteness Statistics')
            if chart_outputFilename != None:
                filesToOpen.extend(chart_outputFilename)

    return filesToOpen


