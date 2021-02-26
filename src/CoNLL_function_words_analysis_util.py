#!/usr/bin/env Python

# -*- coding: utf-8 -*-

#The Python 3 routine was written by Jian Chen, 12.12.2018
# modified by Jian Chen (January 2019)
# modified by Jack Hester (February 2019)
# modified by Roberto Franzosi (February 2019)
#Function words (or junk words) are: pronouns prepositions articles conjunctions auxiliaries

# Command promp commands
# cd C:\Program Files (x86)\PC-ACE\NLP\Miscellaneous
# python Function_Words_GUI.py 


import sys

import GUI_IO_util
import IO_files_util
import GUI_util
import IO_libraries_util
import IO_csv_util
import IO_user_interface_util

if IO_libraries_util.install_all_packages(GUI_util.window,"function_words_analysis_main",['csv','os','collections','tkinter','ntpath'])==False:
    sys.exit(0)

import csv
import os
from collections import Counter
import tkinter.messagebox as mb
import tkinter as tk
import ntpath

import IO_CoNLL_util
import Excel_util
import statistics_csv_util


import Stanford_CoreNLP_tags_util

dict_POSTAG, dict_DEPREL = Stanford_CoreNLP_tags_util.dict_POSTAG, Stanford_CoreNLP_tags_util.dict_DEPREL

global recordID_position, documentId_position  # , data, data_divided_sents
recordID_position = 8
documentId_position = 10


def compute_stats(data):
    global postag_list, postag_counter, deprel_list, deprel_counter
    postag_list = [i[3] for i in data]
    deprel_list = [i[6] for i in data]
    postag_counter = Counter(postag_list)
    deprel_counter = Counter(deprel_list)
    return postag_list, postag_counter, deprel_list, deprel_counter

def pronoun_stats(inputFilename,outputDir, data, data_divided_sents, openOutputFiles,createExcelCharts):
    filesToOpen = []  # Store all files that are to be opened once finished
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running Pronoun Analysis at', True)
    
    #output file names
    function_words_list_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Pronouns', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename,'',  outputDir, '.csv', 'FW', 'Pronouns', 'stats')
    # filesToOpen.append(function_words_list_file_name)
    # not necessary to open stats since these stats are included in the pie chart
    # filesToOpen.append(function_words_stats_file_name)
    
    #obtain data
    #data  = get_data(inputFilename)
    #data_divided_sents = IO_CoNLL_util.sentence_division(data)
    
    if 0:
        stats_pronouns(data)
    else:
        if not os.path.isdir(outputDir):
            mb.showwarning(title='output file path error', message='Please check OUTPUT DIRECTORY PATH and try again')
            return filesToOpen
        
        pronouns_list,pronouns_stats= stats_pronouns_output(data,data_divided_sents)
        errorFound=IO_csv_util.list_to_csv(GUI_util.window,IO_CoNLL_util.sort_output_list('PRONOUNS',pronouns_list,documentId_position), function_words_list_file_name)
        if errorFound==True:
            return filesToOpen

        errorFound=IO_csv_util.list_to_csv(GUI_util.window,pronouns_stats,function_words_stats_file_name)
        if errorFound==True:
            return filesToOpen
        if createExcelCharts==True:
            Excel_outputFilename= Excel_util.create_excel_chart(GUI_util.window,
                                          data_to_be_plotted=[pronouns_stats],
                                          inputFilename=function_words_stats_file_name,
                                          outputDir=outputDir,
                                          scriptType='FuncWords_pron',
                                          chartTitle="Pronoun Analysis",
                                          chart_type_list=["pie"])

            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

            # line plot by sentence index
            outputFiles=Excel_util.compute_csv_column_frequencies(GUI_util.window,
                                                                         function_words_list_file_name,
                                                                         '',
                                                                         outputDir,
                                                                         openOutputFiles, createExcelCharts,
                                                                         [[1,4]],
                                                                         ['PRONOUNS'],['FORM','Sentence'], ['Document ID','Sentence ID','Document'],
                                                                         'FW','line')
            if len(outputFiles) > 0:
                filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running Pronoun Analysis at', True)
    return filesToOpen

def preposition_stats(inputFilename,outputDir,data, data_divided_sents, openOutputFiles,createExcelCharts):
    filesToOpen = []  # Store all files that are to be opened once finished
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running Preposition Analysis at', True)

    #output file names
    function_words_list_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Prepositions', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Prepositions', 'stats')
    # filesToOpen.append(function_words_list_file_name)
    # not necessary to open stats since these stats are included in the pie chart
    # filesToOpen.append(function_words_stats_file_name)
    
    #data  = get_data(inputFilename)
    #data_divided_sents = IO_CoNLL_util.sentence_division(data)
    
    
    if 0:
        stats_prepositions(data)
        #IO_util.timed_alert(GUI_util.window,3000,'Analysis start','Started running Pronoun Analysis at',True)
    else:
        if not os.path.isdir(outputDir):
            mb.showwarning(title='output file path error', message='Please check OUTPUT DIRECTORY PATH and try again')
            return filesToOpen
       
        prepositions_list,prepositions_stats= stats_prepositions_output(data,data_divided_sents)
        errorFound=IO_csv_util.list_to_csv(GUI_util.window,IO_CoNLL_util.sort_output_list('PREPOSITIONS',prepositions_list,documentId_position), function_words_list_file_name)
        if errorFound==True:
            return filesToOpen

        errorFound=IO_csv_util.list_to_csv(GUI_util.window,prepositions_stats,function_words_stats_file_name)
        if errorFound==True:
            return filesToOpen
        if createExcelCharts==True:
            Excel_outputFilename= Excel_util.create_excel_chart(GUI_util.window,
                                          data_to_be_plotted=[prepositions_stats],
                                          inputFilename=function_words_stats_file_name,
                                          outputDir=outputDir,
                                          scriptType='FuncWords_prep',
                                          chartTitle="Preposition Analysis",
                                          chart_type_list=["pie"])

            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

            # line plot by sentence index
            outputFiles=Excel_util.compute_csv_column_frequencies(GUI_util.window,
                                                                         function_words_list_file_name,
                                                                         '',
                                                                         outputDir,
                                                                         openOutputFiles,createExcelCharts,
                                                                         [[1,4]],
                                                                         ['PREPOSITIONS'],['FORM','Sentence'], ['Document ID','Sentence ID','Document'],
                                                                         'FW','line')
            if len(outputFiles) > 0:
                filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running Preposition Analysis at', True)
    return filesToOpen

def article_stats(inputFilename,outputDir,data, data_divided_sents, openOutputFiles,createExcelCharts):
    filesToOpen = []  # Store all files that are to be opened once finished
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running Article Analysis at', True)
    
    #output file names
    function_words_list_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Articles', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Articles', 'stats')
    # filesToOpen.append(function_words_list_file_name)
    # not necessary to open stats since these stats are included in the pie chart
    # filesToOpen.append(function_words_stats_file_name)

    #data  = get_data(inputFilename)
    #data_divided_sents = IO_CoNLL_util.sentence_division(data)
    
    
    if 0:
        stats_articles(data)
        return filesToOpen
    else:
        if not os.path.isdir(outputDir):
            mb.showwarning(title='output file path error', message='Please check OUTPUT DIRECTORY PATH and try again')
            return filesToOpen

        # output files
        article_list,article_stats =  stats_articles_output(data,data_divided_sents)

        errorFound=IO_csv_util.list_to_csv(GUI_util.window,IO_CoNLL_util.sort_output_list('ARTICLES',article_list,documentId_position), function_words_list_file_name)
        if errorFound==True:
            return filesToOpen
        filesToOpen.append(function_words_list_file_name)

        errorFound=IO_csv_util.list_to_csv(GUI_util.window,article_stats,function_words_stats_file_name)
        if errorFound==True:
            return filesToOpen
        filesToOpen.append(function_words_stats_file_name)

        if createExcelCharts==True:
            Excel_outputFilename= Excel_util.create_excel_chart(GUI_util.window,
                                          data_to_be_plotted=[article_stats],
                                          inputFilename=function_words_stats_file_name,
                                          outputDir=outputDir,
                                          scriptType='CoreNLP_FuncWords',
                                          chartTitle="Article Analysis",
                                          chart_type_list=["pie"])

            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)


            # Excel_util.create_excel_chart(GUI_util.window,[article_stats],function_words_stats_file_name,
            # "Article Analysis",["pie"])

            # line plot by sentence index
            outputFiles=Excel_util.compute_csv_column_frequencies(GUI_util.window,
                                                                         function_words_list_file_name,
                                                                         '',
                                                                         outputDir,
                                                                         openOutputFiles, createExcelCharts,
                                                                         [[1,4]],['ARTICLES'],['FORM','Sentence'], ['Document ID','Sentence ID','Document'],
                                                                         'FW','line')
            if len(outputFiles) > 0:
                filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running Article Analysis at', True)
    return filesToOpen

def conjunction_stats(inputFilename,outputDir, data, data_divided_sents,openOutputFiles,createExcelCharts):
    filesToOpen = []  # Store all files that are to be opened once finished
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running Conjunction Analysis at', True)

    #output file names
    function_words_list_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Conjunctions', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Conjunctions', 'stats')
    # not necessary to open stats since these stats are included in the pie chart
    # filesToOpen.append(function_words_stats_file_name)

    #data  = get_data(inputFilename)
    #data_divided_sents = IO_CoNLL_util.sentence_division(data)
    
    if 0:
        stats_conjunctions(data)
        return filesToOpen
    else:
        if not os.path.isdir(outputDir):
            mb.showwarning(title='output file path error', message='Please check OUTPUT DIRECTORY PATH and try again')
            return filesToOpen

        conjunction_list,conjunction_stats =  stats_conjunctions_output(data,data_divided_sents)
        errorFound=IO_csv_util.list_to_csv(GUI_util.window,IO_CoNLL_util.sort_output_list('CONJUNCTIONS',conjunction_list,documentId_position), function_words_list_file_name)
        if errorFound==True:
            return filesToOpen
        filesToOpen.append(function_words_list_file_name)

        errorFound=IO_csv_util.list_to_csv(GUI_util.window,conjunction_stats,function_words_stats_file_name)
        if errorFound==True:
            return filesToOpen
        filesToOpen.append(function_words_stats_file_name)

        if createExcelCharts==True:
            Excel_outputFilename = Excel_util.create_excel_chart(GUI_util.window,
                                                                 data_to_be_plotted=[conjunction_stats],
                                                                 inputFilename=function_words_stats_file_name,
                                                                 outputDir=outputDir,
                                                                 scriptType='Conjunctions',
                                                                 chartTitle="Frequency Distribution of Conjunctions",
                                                                 chart_type_list=["pie"])

            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

            # function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, outputDir, '.xlsx', 'FW', 'Conjunctions', 'stats_pie_chart')
            # filesToOpen.append(function_words_stats_file_name)
            # Excel_outputFilename =Excel_util.create_excel_chart(GUI_util.window,[conjunction_stats],function_words_stats_file_name,"Conjunction Analysis",["pie"])

            # line plot by sentence index
            outputFiles=Excel_util.compute_csv_column_frequencies(GUI_util.window,
                                                                         function_words_list_file_name,
                                                                         '',
                                                                         outputDir,
                                                                         openOutputFiles, createExcelCharts,
                                                                         [[1,4]],
                                                                         ['CONJUNCTIONS'],['FORM','Sentence'], ['Document ID','Sentence ID','Document'],
                                                                         'FW','line')
            if len(outputFiles) > 0:
                filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running Conjunction Analysis at', True)
    return filesToOpen

def auxiliary_stats(inputFilename,outputDir,data, data_divided_sents, openOutputFiles,createExcelCharts):
    filesToOpen = []  # Store all files that are to be opened once finished
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running Auxiliary Analysis at', True)
    
    #output file names
    function_words_list_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Auxiliaries', 'list')
    function_words_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'FW', 'Auxiliaries', 'stats')
    # filesToOpen.append(function_words_list_file_name)
    # not necessary to open stats since these stats are included in the pie chart
    # filesToOpen.append(function_words_stats_file_name)

    #data  = get_data(inputFilename)
    #data_divided_sents = IO_CoNLL_util.sentence_division(data)
    
    if 0:
        stats_auxiliaries(data)
        return filesToOpen
    else:
        if not os.path.isdir(outputDir):
            mb.showwarning(title='output file path error', message='Please check OUTPUT DIRECTORY PATH and try again')
            return filesToOpen
        auxiliary_list,auxiliary_stats =  stats_auxiliaries_output(data,data_divided_sents)
        errorFound=IO_csv_util.list_to_csv(GUI_util.window,IO_CoNLL_util.sort_output_list('AUXILIARIES',auxiliary_list,documentId_position), function_words_list_file_name)
        if errorFound==True:
            return filesToOpen
        filesToOpen.append(function_words_list_file_name)

        errorFound=IO_csv_util.list_to_csv(GUI_util.window,auxiliary_stats,function_words_stats_file_name)
        if errorFound==True:
            return filesToOpen
        filesToOpen.append(function_words_stats_file_name)

        if createExcelCharts==True:
            Excel_outputFilename = Excel_util.create_excel_chart(GUI_util.window,
                                                                 data_to_be_plotted=[auxiliary_stats],
                                                                 inputFilename=function_words_stats_file_name,
                                                                 outputDir=outputDir,
                                                                 scriptType='Verb_Aux',
                                                                 chartTitle="Frequency Distribution of Auxiliary Verbs",
                                                                 chart_type_list=["pie"])

            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

            # line plots by sentence index

            outputFiles=Excel_util.compute_csv_column_frequencies(GUI_util.window,
                                                                         function_words_list_file_name,
                                                                         '',
                                                                         outputDir,
                                                                         openOutputFiles,createExcelCharts,
                                                                         [[1, 4]],
                                                                         ['AUXILIARIES'],['FORM','Sentence'], ['Document ID','Sentence ID','Document'],
                                                                         'FW','line')
            if len(outputFiles) > 0:
                filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running Auxiliary Analysis at', True)
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

#pronouns with output
def stats_pronouns_output(data,data_divided_sents):
    
    list_pronouns_postag = []
    
    for i in data:
        if i[3] in ['PRP']:
            list_pronouns_postag.append(i+['Personal pronoun',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[documentId_position],i[9])])
        if i[3] in ['PRP$']:
            list_pronouns_postag.append(i+['Possessive pronoun',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[documentId_position],i[9])])
        elif i[3] in ['WP']:
            list_pronouns_postag.append(i+['WH-pronoun',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[documentId_position],i[9])])
        elif i[3] in ['WP$']:
            list_pronouns_postag.append(i+['Possessive WH-pronoun',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[documentId_position],i[9])])
        
    #pronouns_postag_stats = [['PRONOUN ANALYSIS'],[],['PRONOUN ANALYSIS'],
    # pronouns_postag_stats = [['PRONOUN ANALYSIS','FREQUENCY'],
    #        ['PRP',postag_counter['PRP']],
    #        ['PRP$',postag_counter['PRP$']],
    #        ['WP',postag_counter['WP']],
    #        ['WP$',postag_counter['WP$']]]

    compute_stats(data)
    pronouns_postag_stats = [['PRONOUN ANALYSIS','FREQUENCY'],
           ['Personal pronoun (PRP)',postag_counter['PRP']],
           ['Possessive pronoun (PRP$)',postag_counter['PRP$']],
           ['WH-pronoun (WP)',postag_counter['WP']],
           ['Possessive WH-pronoun (WP$)',postag_counter['WP$']]]

    return list_pronouns_postag, pronouns_postag_stats

#PREPOSITIONS with output
def stats_prepositions_output(data,data_divided_sents):
        
    list_prepositions_postag = []
    
    for i in data:
        if i[3] in ['IN']:
            list_prepositions_postag.append(i+['Preposition/subordinating conjunction',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[documentId_position],i[9])])
        
    #prepositions_postag_stats = [['PREPOSITION ANALYSIS'],[],['PREPOSITION ANALYSIS'],
    # prepositions_postag_stats = [['PREPOSITION ANALYSIS','FREQUENCY'],
    #        ['IN',postag_counter['IN']]]

    compute_stats(data)
    prepositions_postag_stats = [['PREPOSITION ANALYSIS','FREQUENCY'],
           ['Preposition/subordinating conjunction',postag_counter['IN']]]

    return list_prepositions_postag, prepositions_postag_stats


#ARTICLES with output
def stats_articles_output(data,data_divided_sents):
        
    list_articles_postag = []
    
    for i in data:
        if i[3] in ['DT']:
            list_articles_postag.append(i+['Articles/determinants',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[documentId_position],i[9])])
        

    #articles_postag_stats = [['ARTICLE ANALYSIS'],[],['ARTICLE ANALYSIS'],
    # articles_postag_stats = [['ARTICLE ANALYSIS','FREQUENCY'],
    #        ['DT',postag_counter['DT']]]

    compute_stats(data)
    articles_postag_stats = [['ARTICLE ANALYSIS','FREQUENCY'],
           ['Determiner/article (DT)',postag_counter['DT']]]

    return list_articles_postag, articles_postag_stats


#CONJUNCTIONS with output
def stats_conjunctions_output(data,data_divided_sents):
        
    list_conjunctions_postag = []
    
    for i in data:
        if i[3] in ['CC','IN']:
            list_conjunctions_postag.append(i+['Conjunctions',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[documentId_position],i[9])])

    #conjunctions_postag_stats = [['CONJUNCTION ANALYSIS'],[],['CONJUNCTION ANALYSIS'],
    # conjunctions_postag_stats = [['CONJUNCTION ANALYSIS','FREQUENCY'],
    #        ['CC',postag_counter['CC']],
    #        ['IN',postag_counter['IN']]]

    compute_stats(data)
    conjunctions_postag_stats = [['CONJUNCTION ANALYSIS','FREQUENCY'],
           ['Coordinating conjunction (CC)',postag_counter['CC']],
           ['Preposition/subordinating conjunction (IN)',postag_counter['IN']]]

    return list_conjunctions_postag, conjunctions_postag_stats


#"DEPREL = ""AUX"",""Auxiliary"", DEPREL = ""AUXPASS"", ""Passive auxiliary"", " & _
#auxiliaries no output

#AUXILIARIES with output
def stats_auxiliaries_output(data,data_divided_sents):
        
    list_auxiliaries_deprel = []
    

    for i in data:

        if i[6] in ['aux','auxpass']:

            list_auxiliaries_deprel.append(i+['Auxiliaries',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[documentId_position],i[9])])

    # auxiliaries_deprel_stats = [['AUXILIARY ANALYSIS','FREQUENCY'],
    #        ['AUX',deprel_counter['aux']],
    #        ['AUXPASS',deprel_counter['auxpass']]]

    compute_stats(data)
    auxiliaries_deprel_stats = [['AUXILIARY ANALYSIS','FREQUENCY'],
           ['Auxiliary (AUX)',deprel_counter['aux']],
           ['Passive auxiliary (AUXPASS)',deprel_counter['auxpass']]]

    return list_auxiliaries_deprel, auxiliaries_deprel_stats

global data_divided_sents

