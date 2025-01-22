#!/usr/bin/env Python

# -*- coding: utf-8 -*-

#The Python 3 routine was written by Jian Chen, 12.12.2018
# modified by Jian Chen (January 2019)
# modified by Jack Hester (February 2019)
# modified by Roberto Franzosi (February 2019), November 2021
#Function words (or junk words) are: pronouns prepositions articles conjunctions auxiliaries

# Command promp commands
# cd C:\Program Files (x86)\PC-ACE\NLP\Miscellaneous
# python Function_Words_GUI.py


import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"function_words_analysis_main",['csv','os','collections','tkinter','ntpath'])==False:
    sys.exit(0)

import os
from collections import Counter
import tkinter.messagebox as mb
import pandas as pd

import CoNLL_util
import charts_util
import statistics_csv_util
import IO_files_util
import IO_csv_util
import IO_user_interface_util
import Stanford_CoreNLP_tags_util

dict_POSTAG, dict_DEPREL = Stanford_CoreNLP_tags_util.dict_POSTAG, Stanford_CoreNLP_tags_util.dict_DEPREL

sentenceID_position = 10 # NEW CoNLL_U
documentID_position = 11 # NEW CoNLL_U

def compute_stats(data):
    global postag_list, postag_counter, deprel_list, deprel_counter
    postag_list = [i[3] for i in data]
    deprel_list = [i[6] for i in data]
    postag_counter = Counter(postag_list)
    deprel_counter = Counter(deprel_list)
    return postag_list, postag_counter, deprel_list, deprel_counter


def process_df_headers(df, word_type):
    if len(df.columns)==15: #date column present
        df.columns = ["ID", "FORM", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID",
                      "Sentence ID", "Document ID", "Document", 'Date', word_type]
        headers = ["ID", "FORM", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID",
                   "Sentence ID",
                   "Document ID", "Document", 'Date', word_type]
    else:
        df.columns = ["ID", "FORM", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID",
                      "Sentence ID", "Document ID", "Document", word_type]
        headers = ["ID", "FORM", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID",
                   "Sentence ID",
                   "Document ID", "Document", word_type]
    return df, headers

def pronoun_stats(inputFilename,outputDir, data, data_divided_sents, openOutputFiles,chartPackage, dataTransformation):
    # create pronoun subdir
    outputDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                            label='FW_pron',
                                                            silent=True)
    if outputDir == '':
        return

    filesToOpen = []  # Store all files that are to be opened once finished

    #output file names
    pronouns_list_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Pronouns', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename,'',  outputDir, '.csv', 'FW', 'Pronouns')
    # filesToOpen.append(function_words_list_file_name)
    # not necessary to open stats since these stats are included in the pie chart
    # filesToOpen.append(function_words_stats_file_name)

    #obtain data
    #data  = get_data(inputFilename)
    #data_divided_sents = CoNLL_util.sentence_division(data)

    if 0:
        stats_pronouns(data)
    else:
        if not os.path.isdir(outputDir):
            mb.showwarning(title='output file path error', message='Please check OUTPUT DIRECTORY PATH and try again')
            return filesToOpen

        pronouns_list,pronouns_stats, pronouns_data = stats_pronouns_output(data,data_divided_sents)
        pronouns_list = pronouns_data

        # convert list to dataframe and save
        df = pd.DataFrame(pronouns_list)
        df, headers = process_df_headers(df, "PRONOUNS")

        IO_csv_util.df_to_csv(GUI_util.window, df, pronouns_list_file_name, headers=headers, index=False,
                              language_encoding='utf-8')

        if chartPackage!='No charts':

            columns_to_be_plotted_xAxis = []
            columns_to_be_plotted_yAxis = ['FORM']
            count_var = 1

            outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                      pronouns_list_file_name, outputDir,
                                                      columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                      chart_title="Frequency Distribution of Pronouns",
                                                      outputFileNameType='FW_pron',
                                                      column_xAxis_label='Pronoun',
                                                      count_var=count_var,
                                                      hover_label=[],
                                                      groupByList=['Document'],
                                                      plotList=[],
                                                      chart_title_label='')

            # run_all returns a string; must use append
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            columns_to_be_plotted_xAxis = []
            columns_to_be_plotted_yAxis = ['PRONOUNS']
            count_var = 1

            outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                      pronouns_list_file_name, outputDir,
                                                      columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                      chart_title="Frequency Distribution of Types of Pronouns",
                                                      outputFileNameType='FW_pron_type',
                                                      column_xAxis_label='Pronoun type',
                                                      count_var=count_var,
                                                      hover_label=[],
                                                      groupByList=['Document'],
                                                      plotList=[],
                                                      chart_title_label='')

            # run_all returns a string; must use append
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    # IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running PRONOUN Analysis at', True, '', True, startTime, True)
    return filesToOpen

def preposition_stats(inputFilename,outputDir,data, data_divided_sents, openOutputFiles,chartPackage, dataTransformation):
    # create preposition subdir
    outputDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                            label='FW_prep',
                                                            silent=True)
    if outputDir == '':
        return

    filesToOpen = []  # Store all files that are to be opened once finished

    #output file names
    function_words_prepositions_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Prepositions', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Prepositions')
    # filesToOpen.append(function_words_list_file_name)
    # not necessary to open stats since these stats are included in the pie chart
    # filesToOpen.append(function_words_stats_file_name)

    #data  = get_data(inputFilename)
    #data_divided_sents = CoNLL_util.sentence_division(data)


    if 0:
        stats_prepositions(data)
    else:
        if not os.path.isdir(outputDir):
            mb.showwarning(title='output file path error', message='Please check OUTPUT DIRECTORY PATH and try again')
            return filesToOpen

        prepositions_list,prepositions_stats, prepositions_data = stats_prepositions_output(data,data_divided_sents)
        prepositions_list = prepositions_data

        # convert list to dataframe and save
        df = pd.DataFrame(prepositions_list)
        df, headers = process_df_headers(df, "PREPOSITIONS")

        IO_csv_util.df_to_csv(GUI_util.window, df, function_words_prepositions_file_name, headers=headers, index=False,
                              language_encoding='utf-8')

        if chartPackage!='No charts':

            columns_to_be_plotted_xAxis = []
            columns_to_be_plotted_yAxis = ['PREPOSITIONS']
            count_var = 1

            outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                      function_words_prepositions_file_name, outputDir,
                                                      columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                      chart_title="Frequency Distribution of Prepositions",
                                                      outputFileNameType='FW_prep',
                                                      column_xAxis_label='Preposition',
                                                      count_var=count_var,
                                                      hover_label=[],
                                                      groupByList=['Document'],
                                                      plotList=[],
                                                      chart_title_label='')

            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    return filesToOpen

def article_stats(inputFilename,outputDir,data, data_divided_sents, openOutputFiles,chartPackage, dataTransformation):
    # create article/determinant subdir
    outputDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                            label='FW_det',
                                                            silent=True)
    if outputDir == '':
        return

    filesToOpen = []  # Store all files that are to be opened once finished

    #output file names
    function_words_articles_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Articles', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Articles')
    # filesToOpen.append(function_words_list_file_name)
    # not necessary to open stats since these stats are included in the pie chart
    # filesToOpen.append(function_words_stats_file_name)

    #data  = get_data(inputFilename)
    #data_divided_sents = CoNLL_util.sentence_division(data)


    if 0:
        stats_articles(data)
        return filesToOpen
    else:
        if not os.path.isdir(outputDir):
            mb.showwarning(title='output file path error', message='Please check OUTPUT DIRECTORY PATH and try again')
            return filesToOpen

        # output files
        article_list,article_stats,article_data =  stats_determiners_articles_output(data,data_divided_sents)
        article_list = article_data

        # convert list to dataframe and save
        df = pd.DataFrame(article_list)
        df, headers = process_df_headers(df, "ARTICLES")

        IO_csv_util.df_to_csv(GUI_util.window, df, function_words_articles_file_name, headers=headers, index=False,
                              language_encoding='utf-8')

        if chartPackage!='No charts':

            columns_to_be_plotted_xAxis = []
            columns_to_be_plotted_yAxis = ['ARTICLES']
            count_var = 1

            outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                      function_words_articles_file_name, outputDir,
                                                      columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                      chart_title="Frequency Distribution of Articles",
                                                      outputFileNameType='FW_art',
                                                      column_xAxis_label='Article',
                                                      count_var=count_var,
                                                      hover_label=[],
                                                      groupByList=['Document'],
                                                      plotList=[],
                                                      chart_title_label='')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    return filesToOpen

def conjunction_stats(inputFilename,outputDir, data, data_divided_sents,openOutputFiles,chartPackage, dataTransformation):

    # create conjunction subdir
    outputDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                            label='FW_conj',
                                                            silent=True)
    if outputDir == '':
        return

    filesToOpen = []  # Store all files that are to be opened once finished

    #output file names
    #output file names
    function_words_conjunctions_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Conjunctions', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Conjunctions')
    # not necessary to open stats since these stats are included in the pie chart
    # filesToOpen.append(function_words_stats_file_name)

    #data  = get_data(inputFilename)
    #data_divided_sents = CoNLL_util.sentence_division(data)

    if 0:
        stats_conjunctions(data)
        return filesToOpen
    else:
        if not os.path.isdir(outputDir):
            mb.showwarning(title='output file path error', message='Please check OUTPUT DIRECTORY PATH and try again')
            return filesToOpen

        conjunction_list,conjunction_stats,conjunction_data = stats_conjunctions_output(data,data_divided_sents)
        conjunction_list = conjunction_data


        # convert list to dataframe and save
        df = pd.DataFrame(conjunction_list)
        df, headers = process_df_headers(df, "CONJUNCTIONS")
        IO_csv_util.df_to_csv(GUI_util.window, df, function_words_conjunctions_file_name, headers=headers, index=False,
                              language_encoding='utf-8')

        if chartPackage!='No charts':

            columns_to_be_plotted_xAxis = []
            columns_to_be_plotted_yAxis = ['CONJUNCTIONS']
            count_var = 1

            outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                  function_words_conjunctions_file_name, outputDir,
                                  columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                  chart_title="Frequency Distribution of Conjunctions",
                                  outputFileNameType='FW_conj',
                                  column_xAxis_label='Conjunction',
                                  count_var=count_var,
                                  hover_label=[],
                                  groupByList=['Document'],
                                  plotList=[],
                                  chart_title_label='')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            columns_to_be_plotted_xAxis = []
            columns_to_be_plotted_yAxis = ['Lemma']
            count_var = 1

            outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                  function_words_conjunctions_file_name, outputDir,
                                  columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                  chart_title="Frequency Distribution of Conjunction Words",
                                  outputFileNameType='FW_conj_words',
                                  column_xAxis_label='Conjunction word',
                                  count_var=count_var,
                                  hover_label=[],
                                  groupByList=['Document'],
                                  plotList=[],
                                  chart_title_label='')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    return filesToOpen

def auxiliary_stats(inputFilename,outputDir,data, data_divided_sents, openOutputFiles,chartPackage, dataTransformation):
    # create auxiliary subdir
    outputDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                            label='FW_aux',
                                                            silent=True)
    if outputDir == '':
        return
    filesToOpen = []  # Store all files that are to be opened once finished

    #output file names
    function_words_auxiliaries_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Auxiliaries', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Auxiliaries')
    # filesToOpen.append(function_words_list_file_name)
    # not necessary to open stats since these stats are included in the pie chart
    # filesToOpen.append(function_words_stats_file_name)

    #data  = get_data(inputFilename)
    #data_divided_sents = CoNLL_util.sentence_division(data)

    if 0:
        stats_auxiliaries(data)
        return filesToOpen
    else:
        if not os.path.isdir(outputDir):
            mb.showwarning(title='output file path error', message='Please check OUTPUT DIRECTORY PATH and try again')
            return filesToOpen
        auxiliary_list,auxiliary_stats,auxiliary_data = stats_auxiliaries_output(data,data_divided_sents)
        auxiliary_list = auxiliary_data

        # convert list to dataframe and save
        df = pd.DataFrame(auxiliary_list)
        df, headers = process_df_headers(df, "AUXILIARIES")

        IO_csv_util.df_to_csv(GUI_util.window, df, function_words_auxiliaries_file_name, headers=headers, index=False,
                              language_encoding='utf-8')

        if chartPackage!='No charts':

            columns_to_be_plotted_xAxis = []
            # columns_to_be_plotted_yAxis = ['AUXILIARIES']
            columns_to_be_plotted_yAxis = ['Lemma']
            count_var = 1

            outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                      function_words_auxiliaries_file_name, outputDir,
                                                      columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                      chart_title="Frequency Distribution of Auxiliaries",
                                                      outputFileNameType='FW_aux',
                                                      column_xAxis_label='Auxiliary verb',
                                                      count_var=count_var,
                                                      hover_label=[],
                                                      groupByList=['Document'],
                                                      plotList=[],
                                                      chart_title_label='')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            return filesToOpen

#for verb auxiliaries analysis
def verb_data_preparation_auxiliary(data):
    try:
        verb_postags = ['VB','VBN','VBD','VBG','VBP','VBZ']
        verb_deprel = ['auxpass','aux']
        data_2 = [tok for tok in data if (tok[3] in verb_postags or tok[6] in verb_deprel)]
        return data_2
    except:
        print("ERROR: INPUT MUST BE THE MERGED CoNLL TABLE CONTAINING THE SENTENCE ID. Please use the merge option when generating your CoNLL table in the StanfordCoreNLP.py routine. Program will exit.")
        mb.showinfo("ERROR", "INPUT MUST BE THE MERGED CoNLL TABLE CONTAINING THE SENTENCE ID. Please use the merge option when generating your CoNLL table in the StanfordCoreNLP.py routine. Program will exit.")
        sys.exit(0)

# Written by Tony Apr 2022
# prepare data in a given way
# in the tag_pos position of the data, find if it is in a given list of tags
# add a column in the end describing the tag the extract the row from data
def data_preperation(data, tag_list, name_list, tag_pos):
    dat = []
    for tok in data:
        if tok[tag_pos] in tag_list:
            dat.append(tok+[name_list[tag_list.index(tok[tag_pos])]])
    dat = sorted(dat, key=lambda x: int(x[9]))
    return dat

#pronouns with output
def stats_pronouns_output(data,data_divided_sents):

    list_pronouns_postag = []
    postag_list, postag_counter, deprel_list, deprel_counter = compute_stats(data)
    # must be sorted in descending order
    pronouns_postag_stats = [['PRONOUN ANALYSIS','FREQUENCY'],
           ['Personal pronoun (PRP)',postag_counter['PRP']], # I, you, she, he, it, we, they (as subjects of the sentence); me, you, her, him, it, us, them (as objects of the sentence)
           ['Possessive pronoun (PRP$)',postag_counter['PRP$']], # mine, ours, yours, his, hers, theirs
           ['WH-pronoun (WP)',postag_counter['WP']], # what, who, whom, whoever (which for CoreNLP is WDT Wh-determiner, not a WP Wh-pronoun
           ['Possessive WH-pronoun (WP$)',postag_counter['WP$']]] # whose

    pronouns_data = data_preperation(data, ['PRP','PRP$','WP','WP$'], ['Personal pronouns','Possessive pronouns','WH-pronouns','Possessive WH-pronouns'], 3)

    return list_pronouns_postag, pronouns_postag_stats, pronouns_data


#PREPOSITIONS with output
def stats_prepositions_output(data,data_divided_sents):

    list_prepositions_postag = []
    postag_list, postag_counter, deprel_list, deprel_counter = compute_stats(data)
    # must be sorted in descending order
    prepositions_postag_stats = [['PREPOSITION ANALYSIS','FREQUENCY'],
           ['Preposition/subordinating conjunction',postag_counter['IN']]]

    prepositions_data = data_preperation(data, ["IN"], ['Preposition/subordinating conjunction'], 3)

    return list_prepositions_postag, prepositions_postag_stats, prepositions_data


#ARTICLES with output
def stats_determiners_articles_output(data,data_divided_sents):

# Common kinds of determiners include:
#   definite and indefinite articles (the, a),
#   demonstratives (this, that),
#   possessive determiners (my, their),
#   cardinal numerals (one, two),
#   quantifiers (many, both),
#   distributive determiners (each, every)
#   interrogative determiners (which, what)

# Stanford CoreNLP does not include all these classes of determinerrs.
# POS 'det' includes only articles, distributive, demonstartives (but that is typically tagged as IN) etc.
# possessive are tagged as PRP$
# numerals are tagged as NUMBER
# interrogative are tagged as WDT

    list_articles_postag = []
    postag_list, postag_counter, deprel_list, deprel_counter = compute_stats(data)
    # must be sorted in descending order
    articles_postag_stats = [['DETERMINER/ARTICLE ANALYSIS','FREQUENCY'],
           ['Determiner/article (DT)',postag_counter['DT']]]

    article_data = data_preperation(data, ["DT"], ['Determiner/article (DT)'], 3)

    return list_articles_postag, articles_postag_stats, article_data


#CONJUNCTIONS with output
def stats_conjunctions_output(data,data_divided_sents):

    list_conjunctions_postag = []
    postag_list, postag_counter, deprel_list, deprel_counter = compute_stats(data)
    # must be sorted in descending order
    conjunctions_postag_stats = [['CONJUNCTION ANALYSIS','FREQUENCY'],
           ['Coordinating conjunction (CC)',postag_counter['CC']],
           ['Preposition/subordinating conjunction (IN)',postag_counter['IN']]]

    conjunction_data = data_preperation(data, ['CC', 'IN'], ['Coordinating conjunction (CC)','Preposition/subordinating conjunction (IN)'], 3)

    return list_conjunctions_postag, conjunctions_postag_stats, conjunction_data


#"DEPREL = ""AUX"",""Auxiliary"", DEPREL = ""AUXPASS"", ""Passive auxiliary"", " & _
#auxiliaries no output

#AUXILIARIES with output
def stats_auxiliaries_output(data,data_divided_sents):

    list_auxiliaries_deprel = []
    postag_list, postag_counter, deprel_list, deprel_counter = compute_stats(data)
    # must be sorted in descending order
    auxiliaries_deprel_stats = [['AUXILIARY ANALYSIS','FREQUENCY'],
           ['Auxiliary (AUX)',deprel_counter['aux']],
           ['Passive auxiliary (AUXPASS)',deprel_counter['auxpass']]]

    auxiliaries_data = data_preperation(data, ['aux', 'auxpass'], ['Auxiliary (AUX)','Passive auxiliary (AUXPASS)'], 6)

    return list_auxiliaries_deprel, auxiliaries_deprel_stats, auxiliaries_data

def function_words_stats(inputFilename,outputDir,data, data_divided_sents, openOutputFiles,chartPackage, dataTransformation):

    filesToOpen = []  # Store all files that are to be opened once finished

    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running FUNCTION WORDS ANALYSES at',
                                                 True, '', True, '', True)

# articles  ---------------------------------------------------
    outputFiles = article_stats(inputFilename, outputDir, data, data_divided_sents,
                                                                   openOutputFiles, chartPackage, dataTransformation)
    if outputFiles!=None:
        filesToOpen.extend(outputFiles)

# auxiliaries ---------------------------------------------------
    outputFiles = auxiliary_stats(inputFilename, outputDir, data, data_divided_sents,openOutputFiles,
                                                        chartPackage, dataTransformation)
    if outputFiles!=None:
        filesToOpen.extend(outputFiles)

# conjunctions ---------------------------------------------------
    outputFiles = conjunction_stats(inputFilename, outputDir, data,
                                                                       data_divided_sents, openOutputFiles,
                                                                       chartPackage, dataTransformation)
    if outputFiles!=None:
        filesToOpen.extend(outputFiles)

# prepositions  ---------------------------------------------------
    outputFiles = preposition_stats(inputFilename, outputDir, data,
                                                                       data_divided_sents, openOutputFiles,
                                                                       chartPackage, dataTransformation)
    if outputFiles!=None:
        filesToOpen.extend(outputFiles)

# pronouns  ---------------------------------------------------
    outputFiles = pronoun_stats(inputFilename, outputDir, data, data_divided_sents,openOutputFiles,
                                chartPackage, dataTransformation)
    if outputFiles!=None:
        filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running FUNCTION WORDS ANALYSES at', True, '', True, startTime, True)

    return filesToOpen

global data_divided_sents


