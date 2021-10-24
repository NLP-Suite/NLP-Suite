#The Python 3 routine was written by Jian Chen, 12.12.2018
# modified by Jian Chen (January 2019)
# modified by Jack Hester (February 2019)
# modified by Roberto Franzosi (February 2019-August 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"CoNLL_clause_analysis.py",['os','csv','tkinter','ntpath','collections','subprocess'])==False:
    sys.exit(0)

import os
from collections import Counter
import tkinter.messagebox as mb

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
# filesToOpen = []  # Store all files that are to be opened once finished
input_file_name = ''
output_dir = ''

def compute_stats(CoNLL_table):
    global clausal_list, clausal_counter
    clausal_list = [i[7] for i in CoNLL_table]
    clausal_counter = Counter(clausal_list)
    return clausal_list, clausal_counter

def clause_stats(inputFilename,inputDir, outputDir,data, data_divided_sents,openOutputFiles,createExcelCharts):

    filesToOpen = []  # Store all files that are to be opened once finished

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running CLAUSE ANALYSES at', True)
    
    #output file names
    #clausal_analysis_file_name contains all the CoNLL table records that have a clausal tag
    clausal_analysis_file_name=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'CA', 'Clause tags', 'list')
    filesToOpen.append(clausal_analysis_file_name)
    #clausal_analysis_stats_file_name will contain a data sheet with the frequency distribution of all available clausal tags and a chart sheet with the pie chart visualization of the data
  
    
    if 0:
        stats_clauses(data)
    else:
        if not os.path.isdir(outputDir):
            mb.showwarning(title='Output file path error', message='Please check OUTPUT DIRECTORY PATH and try again')
            return
        clausal_list= stats_clauses_output(data,data_divided_sents)

        IO_csv_util.list_to_csv(GUI_util.window,IO_CoNLL_util.sort_output_list('CLAUSE TAGS',clausal_list,documentId_position), clausal_analysis_file_name)
        column_stats=statistics_csv_util.compute_stats_CoreNLP_tag(clausal_list,7,"Clause Tags, Frequency","CLAUSALTAG")

        clausal_analysis_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'CA', 'Clause tags', 'stats')
        errorFound=IO_csv_util.list_to_csv(GUI_util.window,column_stats,clausal_analysis_stats_file_name)
        if errorFound==True:
             return

        if createExcelCharts==True:
            Excel_outputFilename= Excel_util.create_excel_chart(GUI_util.window,
                                          data_to_be_plotted=[column_stats],
                                          inputFilename=clausal_analysis_stats_file_name,
                                          outputDir=outputDir,
                                          scriptType='CoNLL_Clause',
                                          chartTitle="Frequency Distribution of Clause Type",
                                          chart_type_list=["pie"],
                                          column_xAxis_label="Clause Tags",
                                          column_yAxis_label="Frequency")
            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

            # line plot by sentence index
            Excel_outputFilename=Excel_util.compute_csv_column_frequencies(GUI_util.window,
                                                                         clausal_analysis_file_name,
                                                                         '',
                                                                         outputDir,
                                                                         openOutputFiles,
                                                                         createExcelCharts,
                                                                         [[8,8]],
                                                                         ['CLAUSE TAGS'],
                                                                            ['FORM','Sentence'],
                                                                           ['Document ID','Sentence ID'],
                                                                         'CA','line')
            if len(Excel_outputFilename)>0:
                filesToOpen.extend(Excel_outputFilename)

            # output_df= Excel_util.add_missing_IDs(clausal_analysis_file_name)
            # # overwrite original file having added any missing document ID and sentence ID
            # output_df.to_csv(clausal_analysis_file_name,index=False)
            #
            columns_to_be_plotted = [[1, 8]]
            hover_label = ['CLAUSAL TAG-DESCRIPTION']
            inputFilename = clausal_analysis_file_name
            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted,
                                                      inputFilename, outputDir,
                                                      outputFileLabel='CoNLL_Clause',
                                                      chart_type_list=["line"],
                                                      chart_title='Frequency of Clause Tags',
                                                      column_xAxis_label_var='Sentence index',
                                                      hover_info_column_list=hover_label,
                                                      count_var=1)
            if Excel_outputFilename!='':
                filesToOpen.append(Excel_outputFilename)


    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running CLAUSE ANALYSES at', True, '', True, startTime)
    return filesToOpen

#stats_clauses_output contains a list of records 
#   from the CoNLL table that have valid clausal tags
def stats_clauses_output(data,data_divided_sents):
    
    #list_clauses looks like this in the end: [['1', '``', '``', '``', 'O', '0', 'ROOT'...
    list_clauses = []
    
    for i in data:
        # print('i[7]',i[7])
        if i[7] == 'VP':
            list_clauses.append(i+['Verb phrase',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[10],i[9])])
        elif i[7] == 'NP':
            list_clauses.append(i+['Noun phrase',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[10],i[9])])
        elif i[7] == 'ADJP':
            list_clauses.append(i+['Adjective phrase',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[10],i[9])])
        elif i[7] == 'AP':
            list_clauses.append(i+['Adverb phrase',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[10],i[9])])
        elif 'PP' in i[7]: # different types of PPs
            list_clauses.append(i+['Prepositional phrase',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[10],i[9])])
        elif i[7] == 'S':
            list_clauses.append(i+['Sentence',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[10],i[9])])
        elif i[7] == 'SBAR':
            list_clauses.append(i+['Subordinate clause',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[10],i[9])])
        elif i[7] == 'SBARQ':
            list_clauses.append(i+['Direct question (wh)',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[10],i[9])])
        else:
            list_clauses.append(i+['',IO_CoNLL_util.Sentence_searcher(data_divided_sents,i[10],i[9])])
    return list_clauses

