#The Python 3 routine was written by Jian Chen, 12.12.2018
# modified by Jian Chen (January 2019)
# modified by Jack Hester (February 2019)
# modified by Roberto Franzosi (February 2019-August 2020), November 2021

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"CoNLL_clause_analysis.py",['os','csv','tkinter','ntpath','collections','subprocess'])==False:
    sys.exit(0)

import os
from collections import Counter
import tkinter.messagebox as mb
import pandas as pd

import IO_files_util
import IO_csv_util
import IO_user_interface_util
import charts_util
#
clause_position = 8 # NEW CoNLL_U
recordID_position = 9 # NEW CoNLL_U
sentenceID_position = 10 # NEW CoNLL_U
documentID_position = 11 # NEW CoNLL_U

# Following are used if running all analyses to prevent redundancy
# filesToOpen = []  # Store all files that are to be opened once finished
inputFilename_name = ''
output_dir = ''

# if a Json file is present for pcfg output, the function extract each clause tag with the set of words that make it up
def process_Json(inputFilename, outputDir):
    head, tail = os.path.split(inputFilename)
    subtree_string_fileName = head + os.sep + 'clausal_tags.csv'
    if not os.path.exists(subtree_string_fileName):
        if os.path.exists(head):
            import Stanford_CoreNLP_clause_util
            sent_list_clause = []
            subtree_string = []
            # JsonDir = head+os.sep+"Json_"+ tail[:-4]
            for file in os.listdir(head):
                if 'Json_' in file:
                    JsonDir=file
            JsonDir = head+os.sep+JsonDir
            if not os.path.exists(JsonDir):
                return None
            inputDocs = IO_files_util.getFileList('', JsonDir, fileType='.txt',silent=True,configFileName='')

            Ndocs = len(inputDocs)
            if Ndocs==0:
                return None
            for JsonFile in inputDocs:
                json = open(JsonFile, 'r', encoding='utf-8', errors='ignore').read()
                for parsed_sent in json['sentences']:
                    sent_list, sent_examples = Stanford_CoreNLP_clause_util.clausal_info_extract_from_string(parsed_sent['parse'])
                    sent_list_clause.append(sent_list)
                    subtree_string.append(sent_examples)

            if len(subtree_string) > 0:
                IO_csv_util.list_to_csv(GUI_util.window, subtree_string, subtree_string_fileName, encoding=language_encoding)
                # filesToOpen.append(subtree_string_fileName)

    return subtree_string_fileName

def clause_data_preparation(data):
    dat = []
    sbar_counter = 0
    s_counter = 0
    sbarq_counter = 0
    sq_counter = 0
    sinv_counter = 0
    np_counter = 0
    vp_counter = 0
    adjp_counter = 0
    advp_counter = 0
    pp_counter = 0
    # should use dict_CLAUSALTAG from Stanford_CoreNLP_tags_util
    clause_list = ['S','SBAR', 'SBARQ', 'SQ', 'SINV', 'NP', 'VP', 'ADJP', 'ADVP', 'PP']

    for i in data:
        if(i[8] in clause_list):
            clause = i[8]
            if(clause == 'S'):
                clause_col = 'Sentence'
                s_counter+=1
            elif(clause == 'SBAR'):
                clause_col = 'Clause introduced by a (possibly empty) subordinating conjunction'
                sbar_counter+=1
            elif(clause == 'SBARQ'):
                clause_col = 'Direct question introduced by a wh-word or a wh-phrase'
                sbarq_counter+=1
            elif (clause == 'SQ'):
                clause_col = 'Inverted yes/no question, or main clause of a wh-question, following the wh-phrase in SBARQ'
                sq_counter += 1
            elif(clause == 'SINV'):
                clause_col = 'Inverted declarative sentence'
                sinv_counter+=1
            elif(clause == 'NP'):
                clause_col = 'Noun Phrase'
                np_counter+=1
            elif(clause == 'VP'):
                clause_col = 'Verb Phrase'
                vp_counter+=1
            elif(clause == 'ADJP'):
                clause_col = 'Adjective Phrase'
                adjp_counter+=1
            elif(clause == 'ADVP'):
                clause_col = 'Adverb Phrase'
                advp_counter+=1
            elif(clause == 'PP'):
                clause_col = 'Prepositional Phrase'
                pp_counter+=1
            dat.append(i+[clause_col])

    clause_stats = [['Clause Tags', 'Frequencies'],
                         ['Clause-level (S - Sentence)', s_counter],
                         ['Clause-level (SBAR - Clause introduced by a (possibly empty) subordinating conjunction)', sbar_counter],
                         ['Clause-level (SBARQ - Direct question introduced by a wh-word or a wh-phrase)', sbarq_counter],
                         ['Clause-level (SQ - Inverted yes/no question, or main clause of a wh-question, following the wh-phrase in SBARQ)', sq_counter],
                         ['Clause-level (SINV - Inverted declarative sentence, i.e. one in which the subject follows the tensed verb or modal)', sinv_counter],
                         ['Phrase-level (NP - Noun Phrase)', np_counter],
                         ['Phrase-level (VP - Verb Phrase)', vp_counter],
                         ['Phrase-level (ADJP - Adjective Phrase)', adjp_counter],
                         ['Phrase-level (ADVP - Adverb Phrase)', advp_counter],
                         ['Phrase-level (PP - Prepositional Phrase)', pp_counter]]
    dat = sorted(dat, key=lambda x: int(x[recordID_position]))
    return clause_stats, dat

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

def clause_stats(inputFilename,inputDir, outputDir,data, data_divided_sents,openOutputFiles,chartPackage, dataTransformation):

    filesToOpen = []  # Store all files that are to be opened once finished

    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running CLAUSE ANALYSES at',
                                                 True, '', True, '', True)

    #output file names
    #clausal_analysis_file_name contains all the CoNLL table records that have a clausal tag
    clausal_analysis_file_name=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'CA', 'Clause tags', 'list')
    # filesToOpen.append(clausal_analysis_file_name)
    #clausal_analysis_stats_file_name will contain a data sheet with the frequency distribution of all available clausal tags and a chart sheet with the pie chart visualization of the data


    # if 0:
    #    stats_clauses(data)
    #else:
    if not os.path.isdir(outputDir):
        mb.showwarning(title='Output file path error', message='Please check OUTPUT DIRECTORY PATH and try again')
        return

    # process the Json file for clause tags
    outputFiles = process_Json(inputFilename, outputDir)
    if outputFiles != None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    #clausal_list, clausal_counter = compute_stats(data)
    #clausal_stats = clause_compute_frequencies(data,data_divided_sents)

    clausal_stats, clausal_list = clause_data_preparation(data)
    if len(clausal_list)==0:
        mb.showwarning(title='Input file error',
                           message='The CLAUSE analysis algorithm expects in input a CoNLL table generated by the Stanford CoreNLP PCFG parser, rather than the nn, neural network parser.\n\nOnly the PCFG parser exports clause tags.\n\nPlease check your input file and try again.')
        print('The CLAUSE analysis algorithm expects in input a CoNLL table generated by the Stanford CoreNLP PCFG parser, rather than the nn, neural network parser. Only the PCFG parser exports clause tags. Please check your input file and try again.')
        return filesToOpen

    clausal_analysis_stats_file_name=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'CA', 'Clause tags', 'stats')
    clause_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'CA', 'Clause tags', 'list')
    # convert list to dataframe and save
    # headers=['Clause Tags','Frequencies']
    df = pd.DataFrame(clausal_list)
    df, headers = process_df_headers(df, "Clause Tag")

    IO_csv_util.df_to_csv(GUI_util.window, df, clausal_analysis_stats_file_name, headers=headers, index=False, language_encoding='utf-8')

    if chartPackage!='No charts':
        columns_to_be_plotted_xAxis=[]
        columns_to_be_plotted_yAxis=['Clause Tag']
        count_var=1

        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                  clausal_analysis_stats_file_name, outputDir,
                                                  columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                  chart_title="Frequency Distribution of Clause Types",
                                                  outputFileNameType='clausal_stats',
                                                  column_xAxis_label='Clause Type',
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

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running CLAUSE ANALYSES at', True, '', True, startTime, True)
    return filesToOpen

