"""
Python 3 script
author: Jian Chen, January 2019, based on original vba code by Roberto Franzosi
modified by Jack Hester and Roberto Franzosi, February, June 2019, November 2021
modified by Tony Apr 2022
"""

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "CoNLL Table Analyzer",
                                          ['csv', 'os', 'collections']) == False:
    sys.exit(0)

from collections import Counter
import pandas as pd

import IO_files_util
import IO_csv_util
import IO_user_interface_util
import CoNLL_util
import charts_util
import statistics_csv_util
import Stanford_CoreNLP_tags_util

dict_POSTAG, dict_DEPREL = Stanford_CoreNLP_tags_util.dict_POSTAG, Stanford_CoreNLP_tags_util.dict_DEPREL

recordID_position = 9 # NEW CoNLL_U
sentenceID_position = 10 # NEW CoNLL_U
documentID_position = 11 # NEW CoNLL_U

# Following are used if running all analyses to prevent redundancy
inputFilename = ''
outputDir = ''
cla_open_csv = False  # if run from command line, will check if they want to open the CSV

"""
    SUPPORTING COMMANDS FOR MAIN FUNCTIONS
"""

# Written by Tony Apr 2022
# prepare data in a given way
# in the tag_pos position of the data, find if it is in a given list of tags
# add a column in the end describing the tag the extract the row from data
def data_preparation(data, tag_list, name_list, tag_pos):
    dat = []
    for tok in data:
        if tok[tag_pos] in tag_list:
            try:
                dat.append(tok+[name_list[tag_list.index(tok[tag_pos])]])
            except:
                print("???")
    dat = sorted(dat, key=lambda x: int(x[recordID_position]))
    return dat

# to avoid key value error

# Take in file name, output is a list of rows each with columns 1->11 in the conll table
# Used to divide sentences etc.

def compute_stats(data):
    global postag_list, postag_counter, deprel_list, deprel_counter, ner_list, ner_counter
    postag_list = [i[3] for i in data]
    ner_list = [i[4] for i in data]
    deprel_list = [i[6] for i in data]
    postag_counter = Counter(postag_list)
    deprel_counter = Counter(deprel_list)
    ner_counter = Counter(ner_list)
    return postag_list, postag_counter, deprel_list, deprel_counter, ner_list, ner_counter

# noun analysis; compute frequencies

def noun_POSTAG_NER_DEPREL_compute_lists_frequencies(data, data_divided_sents):
    # print("\n\n################# NOUN ANALYSIS ################")
    list_nouns_postag = []
    list_nouns_deprel = []
    list_nouns_ner = []

    # must all be sorted in descending order
    list_nouns_postag = data_preparation(data, ['NN', 'NNS', 'NNP', 'NNPS'],
     ['Noun singular/mass (NN)', 'Noun plural (NNS)', 'Proper noun singular (NNP)', 'Proper noun plural (NNPS)'], 3)
    noun_postag_stats = [['Noun POS Tags', 'Frequencies'],
                         ['Proper noun singular (NNP)', postag_counter['NNP']],
                         ['Proper noun plural (NNPS)', postag_counter['NNPS']],
                         ['Noun singular/mass (NN)', postag_counter['NN']],
                         ['Noun plural (NNS)', postag_counter['NNS']]]

    list_nouns_deprel = data_preparation(data, ['obj','iobj','nsubj','nsubj:pass','csubj','csubj:pass'],
    ['Object (obj)','Indirect object (iobj)','Nominal subject (nsubj)','Nominal passive subject (nsubj:pass)',
    'Clausal subject (csubj)','Clausal passive subject (csubj:pass)'],6)

    noun_deprel_stats = [['Noun DEPREL Tags', 'Frequencies'],
                         ['Object (obj)', deprel_counter['obj']],
                         ['Indirect object (iobj)', deprel_counter['iobj']],
                         ['Nominal subject (nsubj)', deprel_counter['nsubj']],
                         ['Nominal passive subject (nsubj:pass)', deprel_counter['nsubj:pass']],
                         ['Clausal subject (csubj)', deprel_counter['csubj']],
                         ['Clausal passive subject (csubj:pass)', deprel_counter['csubj:pass']]]

    # list_nouns_ner = data_preparation(data, ['COUNTRY','CITY','LOCATION','PERSON','ORGANIZATION','STATE_OR_PROVINCE'],
    # ['COUNTRY','CITY','LOCATION','PERSON','ORGANIZATION','STATE_OR_PROVINCE'],4)
    # noun_ner_stats = [['Noun NERs', 'Frequencies'],
    #     ['COUNTRY', ner_counter['COUNTRY']],
    #     ['CITY', ner_counter['CITY']],
    #     ['LOCATION', ner_counter['LOCATION']],
    #     ['PERSON', ner_counter['PERSON']],
    #     ['ORGANIZATION', ner_counter['ORGANIZATION']],
    #     ['STATE_OR_PROVINCE', ner_counter['STATE_OR_PROVINCE']]]

    tl = ['ID', 'Form', 'Lemma', 'POS', 'NER', 'Head', 'DepRel', 'Deps', 'Clause Tag', 'Record ID', 'Sentence ID',
          'Document ID', 'Document']
    possible_items = list(pd.DataFrame(data, columns=tl)['NER'].value_counts().keys())
    list_nouns_ner = data_preparation(data,possible_items, possible_items, 4)
    strings = '''[['Noun NERs', 'Frequencies'],'''
    for index, item in enumerate(possible_items):
        if index != len(possible_items)-1:
            strings+= "['"+item+"',ner_counter['"+item+"']],"
        else:
            strings += "['" + item + "',ner_counter['" + item + "']]]"
    noun_ner_stats = eval(strings)
    print(noun_ner_stats[1],noun_ner_stats[1][1], "THIS IS THE O COUNTER!!!!!!!!")
    return list_nouns_postag, list_nouns_deprel, list_nouns_ner, noun_postag_stats, noun_deprel_stats, noun_ner_stats

    # return list_nouns_postag, list_nouns_deprel, list_nouns_ner, noun_postag_stats, noun_deprel_stats, noun_ner_stats


def noun_stats(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, createCharts, chartPackage):
    # print("\nRun noun analysis")

    filesToOpen = []  # Store all files that are to be opened once finished

    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running NOUN ANALYSES at',
                                                 True, '', True, '', True)

    # the following line is needed by the next line as it computes variables defined as general
    noun_postag_list, noun_postag_stats, noun_deprel_list, noun_deprel_stats, noun_ner_list, noun_ner_stats = compute_stats(data)

    noun_postag_list, noun_deprel_list, noun_ner_list, noun_postag_stats, noun_deprel_stats, noun_ner_stats = noun_POSTAG_NER_DEPREL_compute_lists_frequencies(data,
                                                                                                  data_divided_sents)

    # output file names
    noun_list_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Noun-ALL',
                                                                    'list')
    noun_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Noun',
                                                                 'stats')

    noun_postag_list_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Noun',
                                                                    'POSTAG_list')
    noun_ner_list_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Noun',
                                                                 'NER_list')
    noun_deprel_list_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Noun',
                                                                    'DEPREL_list')
    noun_postag_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Noun',
                                                                     'POSTAG_stats')
    noun_ner_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA','Noun',
                                                                  'NER_stats')
    noun_deprel_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA','Noun',
                                                                     'DEPREL_stats')

    # header=["ID", "FORM", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document",
    #       "Noun POS Tags"])


    # save csv files -------------------------------------------------------------------------------------------------
    # ALL nouns

    df = pd.DataFrame(noun_postag_list)
    df1 = df.iloc[:, 1:4]
    df1.columns = ['Form', 'Lemma', 'POS']
    IO_csv_util.df_to_csv(GUI_util.window, df1, noun_list_file_name, headers=['Form', 'Lemma', 'POS'], index=False,
                          language_encoding='utf-8')

    # df = pd.DataFrame(noun_postag_stats)
    # IO_csv_util.df_to_csv(GUI_util.window, df, noun_stats_file_name, headers=None, index=False,
    #                       language_encoding='utf-8')


    # POS tags

    df = pd.DataFrame(noun_postag_list)
    IO_csv_util.df_to_csv(GUI_util.window, df, noun_postag_list_file_name, headers=None, index=False,
                          language_encoding='utf-8')

    df = pd.DataFrame(noun_postag_stats)
    IO_csv_util.df_to_csv(GUI_util.window, df, noun_postag_stats_file_name, headers=None, index=False,
                          language_encoding='utf-8')

    # NER

    df = pd.DataFrame(noun_ner_list)
    IO_csv_util.df_to_csv(GUI_util.window, df, noun_ner_list_file_name, headers=None, index=False,
                          language_encoding='utf-8')

    df = pd.DataFrame(noun_ner_stats)
    IO_csv_util.df_to_csv(GUI_util.window, df, noun_ner_stats_file_name, headers=None, index=False,
                          language_encoding='utf-8')

    # DepRel

    df = pd.DataFrame(noun_deprel_list)
    IO_csv_util.df_to_csv(GUI_util.window, df, noun_deprel_list_file_name, headers=None, index=False,
                          language_encoding='utf-8')

    df = pd.DataFrame(noun_deprel_stats)
    IO_csv_util.df_to_csv(GUI_util.window, df, noun_deprel_stats_file_name, headers=None, index=False,
                          language_encoding='utf-8')


    # header=["ID", "FORM", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document",
    #   "Noun DEPREL Tags"])

    if createCharts == True:

        # bar charts -----------------------------------------------------------------------------------------------

        columns_to_be_plotted_xAxis=[]
        columns_to_be_plotted_yAxis=[[0,0]]
        count_var=1
        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, noun_list_file_name, outputDir,
                                     outputFileLabel='Nouns_Form',
                                     chartPackage=chartPackage,
                                     chart_type_list=['bar'],
                                     chart_title="Frequency Distribution of Nouns (Form)",
                                     column_xAxis_label_var='Noun',
                                     hover_info_column_list=[],
                                     count_var=count_var,
                                     complete_sid=False)  # TODO to be changed

        # run_all returns a string; must use append
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        columns_to_be_plotted_xAxis=[]
        columns_to_be_plotted_yAxis=[[0,1]]
        count_var=1
        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, noun_list_file_name, outputDir,
                                     outputFileLabel='Nouns_Lemma',
                                     chartPackage=chartPackage,
                                     chart_type_list=['bar'],
                                     chart_title="Frequency Distribution of Nouns (Lemma)",
                                     column_xAxis_label_var='Noun',
                                     hover_info_column_list=[],
                                     count_var=count_var,
                                     complete_sid=False)  # TODO to be changed

        # run_all returns a string; must use append
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        columns_to_be_plotted_xAxis=[]
        columns_to_be_plotted_yAxis=[[0,1]]
        count_var=0
        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, noun_postag_stats_file_name, outputDir,
                                     outputFileLabel='Nouns_POS',
                                     chartPackage=chartPackage,
                                     chart_type_list=['bar'],
                                     chart_title="Frequency Distribution of Nouns POS Tags",
                                     column_xAxis_label_var='Nouns POS Tag',
                                     hover_info_column_list=[],
                                     count_var=count_var,
                                     complete_sid=False)  # TODO to be changed

        # run_all returns a string; must use append
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, noun_deprel_stats_file_name, outputDir,
														 outputFileLabel='Nouns_DEPREL',
														 chartPackage=chartPackage,
														 chart_type_list=['bar'],
														 chart_title="Frequency Distribution of Nouns DEPREL Tags",
														 column_xAxis_label_var='Nouns DEPREL Tag',
														 hover_info_column_list=[],
														 count_var=count_var,
                                                         complete_sid=False)  # TODO to be changed

        # run_all returns a string; must use append
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, noun_ner_stats_file_name, outputDir,
                                     outputFileLabel='Nouns_NER',
                                     chartPackage=chartPackage,
                                     chart_type_list=['bar'],
                                     chart_title="Frequency Distribution of Nouns NERs",
                                     column_xAxis_label_var='Nouns NER',
                                     hover_info_column_list=[],
                                     count_var=count_var,
                                     complete_sid=False)  # TODO to be changed

        # run_all returns a string; must use append
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running NOUN ANALYSES at', True, '', True, startTime, True)

    return filesToOpen
