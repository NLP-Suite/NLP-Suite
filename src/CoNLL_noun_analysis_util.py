"""
Python 3 script
author: Jian Chen, January 2019, based on original vba code by Roberto Franzosi
modified by Jack Hester and Roberto Franzosi, February, June 2019
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
import IO_CoNLL_util
import Excel_util
import statistics_csv_util
import Stanford_CoreNLP_tags_util

dict_POSTAG, dict_DEPREL = Stanford_CoreNLP_tags_util.dict_POSTAG, Stanford_CoreNLP_tags_util.dict_DEPREL

global recordID_position, documentId_position  # , data, data_divided_sents
recordID_position = 8
documentId_position = 10

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

    for i in data:
        if i[3] in ['NN', 'NNS']:
            list_nouns_postag.append(i + ['Improper', IO_CoNLL_util.Sentence_searcher(data_divided_sents,
                                                                                           i[documentId_position],
                                                                                           i[9])])
        elif i[3] in ['NNP', 'NNPS']:
            list_nouns_postag.append(
                i + ['Proper', IO_CoNLL_util.Sentence_searcher(data_divided_sents, i[documentId_position], i[9])]
            )
        if i[6] in ['obj', 'iobj', 'nsubj', 'nsubj:pass', 'csubj', 'csubj:pass']:
            list_nouns_deprel.append(
                i + [i[6], IO_CoNLL_util.Sentence_searcher(data_divided_sents, i[documentId_position], i[9])]
            )
        if i[4] in ['ORGANIZATION', 'PERSON', 'COUNTRY', 'CITY', 'STATE_OR_PROVINCE']:
            list_nouns_ner.append(
                i + [i[4], IO_CoNLL_util.Sentence_searcher(data_divided_sents, i[documentId_position], i[9])]
            )

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

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running NOUN ANALYSES at',
                                       True)  # TODO: fix

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
                                         IO_CoNLL_util.sort_output_list('Noun POS Tags', noun_postag,
                                                                        documentId_position),
                                         noun_postag_file_name)
    if errorFound == True:
        return filesToOpen
    filesToOpen.append(noun_postag_file_name)

    errorFound = IO_csv_util.list_to_csv(GUI_util.window,
                                         IO_CoNLL_util.sort_output_list('Noun DEPREL Tags', noun_deprel,
                                                                        documentId_position),
                                         noun_deprel_file_name)
    if errorFound == True:
        return filesToOpen
    filesToOpen.append(noun_deprel_file_name)

    errorFound = IO_csv_util.list_to_csv(GUI_util.window,
                                         IO_CoNLL_util.sort_output_list('Noun NER Tags', noun_ner,
                                                                        documentId_position),
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

        Excel_outputFilename = Excel_util.create_excel_chart(GUI_util.window,
                                                             data_to_be_plotted=[noun_postag_stats],
                                                             inputFilename=noun_postag_stats_file_name,
                                                             outputDir=outputDir,
                                                             scriptType='Nouns_POS',
                                                             chartTitle="Noun POS Analysis",
                                                             chart_type_list=["pie"])

        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)

        Excel_outputFilename = Excel_util.create_excel_chart(GUI_util.window,
                                                             data_to_be_plotted=[noun_deprel_stats],
                                                             inputFilename=noun_deprel_stats_file_name,
                                                             outputDir=outputDir,
                                                             scriptType='Nouns_DEPREL',
                                                             chartTitle="Noun DEPREL Analysis",
                                                             chart_type_list=["pie"])

        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)

        Excel_outputFilename = Excel_util.create_excel_chart(GUI_util.window,
                                                             data_to_be_plotted=[noun_ner_stats],
                                                             inputFilename=noun_ner_stats_file_name,
                                                             outputDir=outputDir,
                                                             scriptType='Nouns_DEPREL',
                                                             chartTitle="Nouns (NER Tags)",
                                                             chart_type_list=["pie"])

        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)

        # line plots by sentence index -----------------------------------------------------------------------------------------------

        outputFiles = Excel_util.compute_csv_column_frequencies(GUI_util.window,
                                                                       noun_postag_file_name,
                                                                       '',
                                                                       outputDir,
                                                                       openOutputFiles,
                                                                       createExcelCharts,
                                                                       [[1, 4]],
                                                                       ['Noun POS Tags'], ['FORM', 'Sentence', 'Document ID', 'Sentence ID','Document'],
                                                                       'NVA', 'line')
        if len(outputFiles)>0:
            filesToOpen.extend(outputFiles)

        outputFiles = Excel_util.compute_csv_column_frequencies(GUI_util.window,
                                                                       noun_deprel_file_name,
                                                                       '',
                                                                       outputDir,
                                                                       openOutputFiles,
                                                                       createExcelCharts,
                                                                       [[1, 4]],
                                                                       ['Noun DEPREL Tags'],['FORM', 'Sentence'],['Document ID', 'Sentence ID','Document'],
                                                                       'NVA','line')

        if len(outputFiles)>0:
            filesToOpen.extend(outputFiles)

        outputFiles = Excel_util.compute_csv_column_frequencies(GUI_util.window,
                                                                       noun_ner_file_name,
                                                                       '',
                                                                       outputDir,
                                                                       openOutputFiles,
                                                                       createExcelCharts,
                                                                       [[1, 4]],
                                                                       ['Noun NER Tags'], ['FORM', 'Sentence'], ['Document ID', 'Sentence ID', 'Document'],
                                                                       'NVA','line')
        if len(outputFiles)>0:
            filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running NOUN ANALYSES at', True)

    return filesToOpen