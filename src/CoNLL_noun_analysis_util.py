"""
Python 3 script
author: Jian Chen, January 2019, based on original vba code by Roberto Franzosi
modified by Jack Hester and Roberto Franzosi, February, June 2019, November 2021
"""

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "CoNLL Table Analyzer",
                                          ['csv', 'os', 'collections']) == False:
    sys.exit(0)

from collections import Counter

import IO_files_util
import IO_csv_util
import IO_user_interface_util
import CoNLL_util
import charts_Excel_util
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

def noun_POSTAG_DEPREL_compute_frequencies(data, data_divided_sents):
    # print("\n\n################# NOUN ANALYSIS ################")
    list_nouns_postag = []
    list_nouns_deprel = []
    list_nouns_ner = []

    # must all be sorted in descending order

    noun_postag_stats = [['Noun POS Tags', 'Frequencies'],
                         ['Proper noun singular (NNP)', postag_counter['NNP']],
                         ['Proper noun plural (NNPS)', postag_counter['NNPS']],
                         ['Noun singular/mass (NN)', postag_counter['NN']],
                         ['Noun plural (NNS)', postag_counter['NNS']]]

    noun_deprel_stats = [['Noun DEPREL Tags', 'Frequencies'],
                         ['Object (obj)', deprel_counter['obj']],
                         ['Indirect object (iobj)', deprel_counter['iobj']],
                         ['Nominal subject (nsubj', deprel_counter['nsubj']],
                         ['Nominal passive subject (nsubj:pass)', deprel_counter['nsubj:pass']],
                         ['Clausal subject (csubj)', deprel_counter['csubj']],
                         ['Clausal passive subject (csubj:pass)', deprel_counter['csubj:pass']]]

    noun_ner_stats = [['Noun NER Tags', 'Frequencies'],
        ['COUNTRY', ner_counter['COUNTRY']],
        ['CITY', ner_counter['CITY']],
        ['LOCATION', ner_counter['LOCATION']],
        ['PERSON', ner_counter['PERSON']],
        ['ORGANIZATION', ner_counter['ORGANIZATION']],
        ['STATE_OR_PROVINCE', ner_counter['STATE_OR_PROVINCE']]]

    return list_nouns_postag, list_nouns_deprel, list_nouns_ner, noun_postag_stats, noun_deprel_stats, noun_ner_stats


def noun_stats(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, createExcelCharts):
    # print("\nRun noun analysis")

    filesToOpen = []  # Store all files that are to be opened once finished

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running NOUN ANALYSES at',
                                                 True, '', True, '', True)

    postag_list, postag_counter, deprel_list, deprel_counter, ner_list, ner_counter = compute_stats(data)

    noun_postag, noun_deprel, noun_ner, \
    noun_postag_stats, noun_deprel_stats, noun_ner_stats = noun_POSTAG_DEPREL_compute_frequencies(data,
                                                                                                  data_divided_sents)
    # output file names
    noun_postag_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Noun',
                                                                    'POSTAG_list')
    noun_deprel_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Noun',
                                                                    'DEPREL_list')
    noun_ner_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Noun',
                                                                 'NER_list')
    noun_postag_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Noun',
                                                                     'POSTAG_stats')
    noun_deprel_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA','Noun',
                                                                     'DEPREL_stats')
    noun_ner_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA','Noun',
                                                                  'NER_stats')

    # save csv files -------------------------------------------------------------------------------------------------

    errorFound = IO_csv_util.list_to_csv(GUI_util.window,
                                         CoNLL_util.sort_output_list('Noun POS Tags', noun_postag),
                                         noun_postag_file_name)
    if errorFound == True:
        return filesToOpen
    filesToOpen.append(noun_postag_file_name)

    errorFound = IO_csv_util.list_to_csv(GUI_util.window,
                                         CoNLL_util.sort_output_list('Noun DEPREL Tags', noun_deprel),
                                         noun_deprel_file_name)
    if errorFound == True:
        return filesToOpen
    filesToOpen.append(noun_deprel_file_name)

    errorFound = IO_csv_util.list_to_csv(GUI_util.window,
                                         CoNLL_util.sort_output_list('Noun NER Tags', noun_ner),
                                         noun_ner_file_name)
    if errorFound == True:
        return filesToOpen
    filesToOpen.append(noun_ner_file_name)

    # save csv frequency files ----------------------------------------------------------------------------------------

    errorFound = IO_csv_util.list_to_csv(GUI_util.window, noun_postag_stats,noun_postag_stats_file_name)
    if errorFound == True:
        return filesToOpen
    filesToOpen.append(noun_postag_stats_file_name)

    errorFound = IO_csv_util.list_to_csv(GUI_util.window, noun_deprel_stats, noun_deprel_stats_file_name)
    if errorFound == True:
        return filesToOpen
    filesToOpen.append(noun_deprel_stats_file_name)

    errorFound = IO_csv_util.list_to_csv(GUI_util.window, noun_ner_stats, noun_ner_stats_file_name)
    if errorFound == True:
        return filesToOpen
    filesToOpen.append(noun_ner_stats_file_name)

    if createExcelCharts == True:

        # pie charts -----------------------------------------------------------------------------------------------

        Excel_outputFilename = charts_Excel_util.create_excel_chart(GUI_util.window,
                                                             data_to_be_plotted=[noun_postag_stats],
                                                             inputFilename=noun_postag_stats_file_name,
                                                             outputDir=outputDir,
                                                             scriptType='Nouns_POS',
                                                             chartTitle="Noun POS Analysis",
                                                             chart_type_list=["pie"])

        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)

        Excel_outputFilename = charts_Excel_util.create_excel_chart(GUI_util.window,
                                                             data_to_be_plotted=[noun_deprel_stats],
                                                             inputFilename=noun_deprel_stats_file_name,
                                                             outputDir=outputDir,
                                                             scriptType='Nouns_DEPREL',
                                                             chartTitle="Noun DEPREL Analysis",
                                                             chart_type_list=["pie"])

        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)

        Excel_outputFilename = charts_Excel_util.create_excel_chart(GUI_util.window,
                                                             data_to_be_plotted=[noun_ner_stats],
                                                             inputFilename=noun_ner_stats_file_name,
                                                             outputDir=outputDir,
                                                             scriptType='Nouns_DEPREL',
                                                             chartTitle="Nouns (NER Tags)",
                                                             chart_type_list=["pie"])

        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)

        return filesToOpen # to avoid code breaking in plot by sentence index

        # line plots by sentence index -----------------------------------------------------------------------------------------------

        outputFiles = charts_Excel_util.compute_csv_column_frequencies(GUI_util.window,
                                                                       noun_postag_file_name,
                                                                       '',
                                                                       outputDir,
                                                                       openOutputFiles,
                                                                       createExcelCharts,
                                                                       [[1, 4]],
                                                                       ['Noun POS Tags'], ['FORM', 'Sentence ID','Sentence', 'Document ID','Document'],
                                                                       'NVA', 'line')
        if len(outputFiles)>0:
            filesToOpen.extend(outputFiles)

        outputFiles = charts_Excel_util.compute_csv_column_frequencies(GUI_util.window,
                                                                       noun_deprel_file_name,
                                                                       '',
                                                                       outputDir,
                                                                       openOutputFiles,
                                                                       createExcelCharts,
                                                                       [[1, 4]],
                                                                       ['Noun DEPREL Tags'],['FORM', 'Sentence'],['Sentence ID','Document ID', 'Document'],
                                                                       'NVA','line')

        if len(outputFiles)>0:
            filesToOpen.extend(outputFiles)

        outputFiles = charts_Excel_util.compute_csv_column_frequencies(GUI_util.window,
                                                                       noun_ner_file_name,
                                                                       '',
                                                                       outputDir,
                                                                       openOutputFiles,
                                                                       createExcelCharts,
                                                                       [[1, 4]],
                                                                       ['Noun NER Tags'], ['FORM', 'Sentence'], ['Sentence ID', 'Document ID', 'Document'],
                                                                       'NVA','line')
        if len(outputFiles)>0:
            filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running NOUN ANALYSES at', True, '', True, startTime, True)

    return filesToOpen