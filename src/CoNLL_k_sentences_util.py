#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 23:05:52 2022

@author: claude
"""
import pandas as pd
import GUI_IO_util
import IO_files_util

def k_sent(inputFilename, outputDir):
    k_str, useless = GUI_IO_util.enter_value_widget("Enter the number of sentences, K, to be analyzed", 'K',
                                                           1, '', '', '')
    k = int(k_str)
    conll = pd.read_csv(inputFilename, encoding='utf-8', error_bad_lines=False)
    head = ["K value", "Words Count","Nouns Count","Nouns Proportion", "Verbs Count", "Verbs Proportion", "Adjectives Count","Adjectives Proportion","Proper-Nouns Count","Proper-Nouns Proportion", "Document ID", "Document"]
    result = []

    for i in range(1, max(conll["Document ID"])+1):
        doc_conll = conll.loc[conll["Document ID"] == i]
        if max(doc_conll['Sentence ID']) <= 2 * k:
            ksentences = doc_conll
        else:
            ksentences = doc_conll.loc[(doc_conll["Sentence ID"] <= k) | (doc_conll["Sentence ID"] > max(doc_conll['Sentence ID']) - k)]
        word_count = len(ksentences['POStag']) - ksentences['DepRel'].value_counts()["punct"]
        verb_count = 0
        noun_count = 0
        adj_count = 0
        pp_count = 0#proper nouns
        for pos in ksentences['POStag']:
            if "NN" in pos: # nouns
                noun_count +=1
                if "NNP" in pos: # proper nouns
                    pp_count += 1
            elif "VB" in pos: # verbs
                verb_count +=1
            elif "JJ" in pos: # adjectives
                adj_count +=1
        # print("dataframe: ")
        # print(ksentences)
        for doc in ksentences['Document']:
            DOC = doc # as doc is in CoNLL table, doc already as the hyperlink
            break

        temp =[k, word_count, noun_count, noun_count / word_count,
                      verb_count, verb_count / word_count, adj_count, adj_count / word_count,pp_count, pp_count / word_count, i, DOC]
        result.append(temp)
        df = pd.DataFrame(result, columns=head)
        if df.empty:
            outputFilename = None
        else:
            outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv',
                                                                                      'K_sent',
                                                                                      '', '', '', '',
                                                                                      False,
                                                                                      True)
            df.to_csv(outputFilename, index=False)
    return outputFilename


# inputFilename = '/Users/claude/Desktop/ClaudeCase/Emory/Trabajo/NLP_CoreNLP_Dir_ksent_CoNLL.csv'
# df = k_sent(inputFilename, 5)
# df.to_csv("/Users/claude/Desktop/ClaudeCase/Emory/Trabajo/k_sentTest.csv", index=False)

# # inputFilename = '/Users/claude/Desktop/ClaudeCase/Emory/Trabajo/NLP_CoreNLP_Dir_Date_embeds_CoNLL.csv'
# conll = pd.read_csv(inputFilename)

# # # conll[]
# # for i in range(1, 9):
# #     print(i)
# # print(conll)
# print(conll['Document'][0])
# doc_conll = conll.loc[conll["Document ID"] == 2]
# print(doc_conll.columns)
# print(doc_conll["Document"][3182])
# print(conll.columns)
# print(max(conll["Document ID"]))
# k = 3
# subset = conll.loc[conll["Document ID"] == 1]
# print(subset)
# head = ["Document", "Word Count","Nouns Count","Nouns Proportion", "Verbs Count", "Verbs Proportion", "Adjective Count","Adjective Proportion"]
# result = []
# for i in range(1, max(conll["Document ID"])+1):
#     doc_conll = conll.loc[conll["Document ID"] == i]
#     if max(doc_conll['Sentence ID']) <= 2 * k:
#         ksentences = doc_conll
#     else:
#         ksentences = doc_conll.loc[doc_conll["Sentence ID"] <= k or doc_conll["Sentence ID"] > max(doc_conll['Sentence ID']) - k]

#     word_count = len(ksentences['POStag']) - ksentences['DepRel'].count("punct")
#     verb_count = 0
#     noun_count = 0
#     adj_count = 0
#     for pos in ksentences['POStag']:
#         if "NN" in pos:
#             noun_count +=1
#         elif "VB" in pos:
#             verb_count +=1
#         elif "JJ" in pos:
#             adj_count +=1
#     result.append([ksentences['Document'][0]], word_count, noun_count, noun_count / word_count,
#                   verb_count, verb_count / word_count, adj_count, adj_count / word_count)
