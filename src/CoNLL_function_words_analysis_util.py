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

def pronoun_stats(inputFilename,outputDir, data, data_divided_sents, openOutputFiles,createCharts, chartPackage):
    filesToOpen = []  # Store all files that are to be opened once finished

    #output file names
    function_words_list_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Pronouns', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename,'',  outputDir, '.csv', 'FW', 'Pronouns', 'stats')
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

        # convert list to dataframe
        df = pd.DataFrame(pronouns_stats)
        IO_csv_util.df_to_csv(GUI_util.window, df, function_words_stats_file_name, headers=None, index=False,
                              language_encoding='utf-8')
        # filesToOpen.append(function_words_stats_file_name)

          # header=["ID", "FORM", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document",
          #     "PRONOUNS"])

        if createCharts==True:
            columns_to_be_plotted_xAxis=[]
            columns_to_be_plotted_yAxis=[[0,1]]
            count_var=0
            outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, function_words_stats_file_name, outputDir,
                                                            outputFileLabel='FuncWords_pron',
                                                            chartPackage=chartPackage,
                                                            chart_type_list=['bar'],
                                                            chart_title="Frequency Distribution of Pronouns",
                                                            column_xAxis_label_var='Pronoun',
                                                            hover_info_column_list=[],
                                                            count_var=count_var,
                                                            complete_sid=False)  # TODO to be changed

            # run_all returns a string; must use append
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    # IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running PRONOUN Analysis at', True, '', True, startTime, True)
    return filesToOpen

def preposition_stats(inputFilename,outputDir,data, data_divided_sents, openOutputFiles,createCharts, chartPackage):
    filesToOpen = []  # Store all files that are to be opened once finished

    #output file names
    function_words_list_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Prepositions', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Prepositions', 'stats')
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

        prepositions_list,prepositions_stats, preposition_data = stats_prepositions_output(data,data_divided_sents)
        prepositions_list = preposition_data

        # convert list to dataframe
        df = pd.DataFrame(prepositions_stats)
        IO_csv_util.df_to_csv(GUI_util.window, df, function_words_stats_file_name, headers=None, index=False,
                              language_encoding='utf-8')

          # header=["ID", "FORM", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document",
          #     "PREPOSITIONS"])

        if createCharts==True:
            columns_to_be_plotted_xAxis=[]
            columns_to_be_plotted_yAxis=[[0,1]]
            count_var=0
            outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, function_words_stats_file_name, outputDir,
                                                            outputFileLabel='FuncWords_prep',
                                                            chartPackage=chartPackage,
                                                            chart_type_list=['bar'],
                                                            chart_title="Frequency Distribution of Prepositions",
                                                            column_xAxis_label_var='Preposition',
                                                            hover_info_column_list=[],
                                                            count_var=count_var,
                                                            complete_sid=False)  # TODO to be changed

            # run_all returns a string; must use append
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    return filesToOpen

def article_stats(inputFilename,outputDir,data, data_divided_sents, openOutputFiles,createCharts, chartPackage):
    filesToOpen = []  # Store all files that are to be opened once finished

    #output file names
    function_words_list_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Articles', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Articles', 'stats')
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
        article_list,article_stats,article_data =  stats_articles_output(data,data_divided_sents)
        article_list = article_data
          # header=["ID", "FORM", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document",
          #     "ARTICLES"])

        # convert list to dataframe
        df = pd.DataFrame(article_stats)
        IO_csv_util.df_to_csv(GUI_util.window, df, function_words_stats_file_name, headers=None, index=False,
                              language_encoding='utf-8')

        if createCharts==True:
            columns_to_be_plotted_xAxis=[]
            columns_to_be_plotted_yAxis=[[0,1]]
            count_var=0
            outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, function_words_stats_file_name, outputDir,
                                                            outputFileLabel='FuncWords_article',
                                                            chartPackage=chartPackage,
                                                            chart_type_list=['bar'],
                                                            chart_title="Frequency Distribution of Articles/Determiners",
                                                            column_xAxis_label_var='Article/Determiner',
                                                            hover_info_column_list=[],
                                                            count_var=count_var,
                                                            complete_sid=False)  # TODO to be changed
            # run_all returns a string; must use append
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)
    return filesToOpen

def conjunction_stats(inputFilename,outputDir, data, data_divided_sents,openOutputFiles,createCharts, chartPackage):
    filesToOpen = []  # Store all files that are to be opened once finished

    #output file names
    function_words_list_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Conjunctions', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Conjunctions', 'stats')
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

        conjunction_list,conjunction_stats,conjunction_data =  stats_conjunctions_output(data,data_divided_sents)
        conjunction_list = conjunction_data

        # convert list to dataframe
        df = pd.DataFrame(conjunction_stats)
        IO_csv_util.df_to_csv(GUI_util.window, df, function_words_stats_file_name, headers=None, index=False,
                              language_encoding='utf-8')
        # header=["ID", "FORM", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document",
          #     "CONJUNCTIONS"])

        if createCharts==True:
            columns_to_be_plotted_xAxis=[]
            columns_to_be_plotted_yAxis=[[0,1]]
            count_var=0
            outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, function_words_stats_file_name, outputDir,
                                                            outputFileLabel='FuncWords_conjunction',
                                                            chartPackage=chartPackage,
                                                            chart_type_list=['bar'],
                                                            chart_title="Frequency Distribution of Conjunctions",
                                                            column_xAxis_label_var='Conjunctions',
                                                            hover_info_column_list=[],
                                                            count_var=count_var,
                                                            complete_sid=False)  # TODO to be changed

            # run_all returns a string; must use append
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

            # function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, outputDir, '.xlsx', 'FW', 'Conjunctions', 'stats_pie_chart')
            # filesToOpen.append(function_words_stats_file_name)
            # outputFiles =charts_Excel_util.create_excel_chart(GUI_util.window,[conjunction_stats],function_words_stats_file_name,"Conjunction Analysis",["pie"])

    return filesToOpen

def auxiliary_stats(inputFilename,outputDir,data, data_divided_sents, openOutputFiles,createCharts, chartPackage):
    filesToOpen = []  # Store all files that are to be opened once finished

    #output file names
    function_words_list_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Auxiliaries', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Auxiliaries', 'stats')
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
        auxiliary_list,auxiliary_stats,auxiliary_data =  stats_auxiliaries_output(data,data_divided_sents)
        auxiliary_list = auxiliary_data
          # header=["ID", "FORM", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document",
          #     "AUXILIARIES"])

        # convert list to dataframe
        df = pd.DataFrame(auxiliary_stats)
        IO_csv_util.df_to_csv(GUI_util.window, df, function_words_stats_file_name, headers=None, index=False,
                              language_encoding='utf-8')

        if createCharts==True:
            columns_to_be_plotted_xAxis=[]
            columns_to_be_plotted_yAxis=[[0,1]]
            count_var=0
            outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, function_words_stats_file_name, outputDir,
                                                            outputFileLabel='FuncWords_auxiliary',
                                                            chartPackage=chartPackage,
                                                            chart_type_list=['bar'],
                                                            chart_title="Frequency Distribution of Auxiliary Verbs",
                                                            column_xAxis_label_var='Auxiliary Verbs',
                                                            hover_info_column_list=[],
                                                            count_var=count_var,
                                                            complete_sid=False)  # TODO to be changed

            # run_all returns a string; must use append
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
           ['Personal pronoun (PRP)',postag_counter['PRP']],
           ['Possessive pronoun (PRP$)',postag_counter['PRP$']],
           ['WH-pronoun (WP)',postag_counter['WP']],
           ['Possessive WH-pronoun (WP$)',postag_counter['WP$']]]

    pronouns_data = data_preperation(data, ['PRP','PRP$','WP','WP$'], ['Personal pronouns','Possessive pronouns','WH-pronouns','Possessive WH-pronouns'], 3)

    return list_pronouns_postag, pronouns_postag_stats, pronouns_data


#PREPOSITIONS with output
def stats_prepositions_output(data,data_divided_sents):

    list_prepositions_postag = []
    postag_list, postag_counter, deprel_list, deprel_counter = compute_stats(data)
    # must be sorted in descending order
    prepositions_postag_stats = [['PREPOSITION ANALYSIS','FREQUENCY'],
           ['Preposition/subordinating conjunction',postag_counter['IN']]]

    preposition_data = data_preperation(data, ["IN"], ['Preposition/subordinating conjunction'], 3)

    return list_prepositions_postag, prepositions_postag_stats, preposition_data


#ARTICLES with output
def stats_articles_output(data,data_divided_sents):

    list_articles_postag = []
    postag_list, postag_counter, deprel_list, deprel_counter = compute_stats(data)
    # must be sorted in descending order
    articles_postag_stats = [['ARTICLE ANALYSIS','FREQUENCY'],
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

def function_words_stats(inputFilename,outputDir,data, data_divided_sents, openOutputFiles,createCharts,chartPackage):

    filesToOpen = []  # Store all files that are to be opened once finished

    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running FUNCTION WORDS ANALYSES at',
                                                 True, '', True, '', True)


    outputFiles = article_stats(inputFilename, outputDir, data, data_divided_sents,
                                                                   openOutputFiles, createCharts, chartPackage)
    if outputFiles != None:
        filesToOpen.extend(outputFiles)

    outputFiles = auxiliary_stats(inputFilename, outputDir, data, data_divided_sents,
                                                                     openOutputFiles, createCharts, chartPackage)
    if outputFiles != None:
        filesToOpen.extend(outputFiles)

    outputFiles = conjunction_stats(inputFilename, outputDir, data,
                                                                       data_divided_sents, openOutputFiles,
                                                                       createCharts, chartPackage)
    if outputFiles != None:
        filesToOpen.extend(outputFiles)

    outputFiles = preposition_stats(inputFilename, outputDir, data,
                                                                       data_divided_sents, openOutputFiles,
                                                                       createCharts, chartPackage)
    if outputFiles != None:
        filesToOpen.extend(outputFiles)

    outputFiles = pronoun_stats(inputFilename, outputDir, data, data_divided_sents,
                                                                   openOutputFiles, createCharts, chartPackage)
    if outputFiles != None:
        filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running FUNCTION WORDS ANALYSES at', True, '', True, startTime, True)

    return filesToOpen

global data_divided_sents


