"""
Python 3 script
author: Jian Chen, January 2019, based on original vba code by Roberto Franzosi
modified by Jack Hester and Roberto Franzosi, February, June 2019, November 2021
modified by Siyan Pu November 2021
"""

import sys
import GUI_util
import IO_libraries_util
import pandas as pd

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "Verb Analysis",
                                          ['csv', 'os', 'collections', 'tkinter']) == False:
    sys.exit(0)

from collections import Counter
from tkinter import filedialog
import tkinter.messagebox as mb
import tkinter as tk

import CoNLL_util
import IO_files_util
import IO_csv_util
import IO_user_interface_util
import charts_util
import statistics_csv_util
import Stanford_CoreNLP_tags_util
import reminders_util

dict_POSTAG, dict_DEPREL = Stanford_CoreNLP_tags_util.dict_POSTAG, Stanford_CoreNLP_tags_util.dict_DEPREL

# global recordID_position, documentID_position #, data, data_divided_sents
recordID_position = 9  # NEW CoNLL_U
sentenceID_position = 10  # NEW CoNLL_U
documentID_position = 11  # NEW CoNLL_U

# Following are used if running all analyses to prevent redundancy
# filesToOpen = []  # Store all files that are to be opened once finished
inputFilename = ''
outputDir = ''
cla_open_csv = False  # if run from command line, will check if they want to open the CSV

"""
    SUPPORTING COMMANDS FOR MAIN FUNCTIONS
"""


# to avoid key value error

# Take in file name, output is a list of rows each with columns 1->11 in the conll table
# Used to divide sentences etc.


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

def compute_stats(data):
    global form_list, postag_list, postag_counter, deprel_list, deprel_counter

    # IMPERATIVES ARE MORE DIFFICULT TO COMPUTE AND ARE CURRENTLY NOT COMPUTED IN THIS SCRIPT;
    # SEE THE FOLLOWING LINKS, ESPECIALLY THE FIRST ONE FOR SUGGESTIONS

    # https://aclanthology.org/2020.lrec-1.805.pdf EXCELLENT
    # https://stackoverflow.com/questions/29473169/approach-for-identifying-whether-a-sentence-includes-an-imperative-within-it
    # https://nlp.stanford.edu/software/lex-parser.shtml
    # https://iconix.github.io/portfolio%20building/2017/09/25/nlp-for-tasks
    # https://web.stanford.edu/~jurafsky/slp3/old_oct19/ed3book.pdf

    # VBG gerund, VBD past, VBN Past Principle/Passive,
    # VBP present (non-3rd person singular), VBZ present (3rd person singular)
    # VB future, VB infinitive, depending on MD modal

    # verb_postags = ['VB', 'VBN', 'VBD', 'VBG', 'VBP', 'VBZ', 'MD'] # all verb types
    verb_postags = ['VB', 'VBN', 'VBD', 'VBG', 'VBP', 'VBZ'] # exclude modals, 'MD'] # all verb types
    data = [tok for tok in data if (tok[3] in verb_postags)]
    form_list = [i[1] for i in data]
    lemma_list = [i[2] for i in data]
    postag_list = [i[3] for i in data]
    deprel_list = [i[6] for i in data]

    form_counter = Counter(form_list)
    lemma_counter = Counter(lemma_list)
    postag_counter = Counter(postag_list)
    deprel_counter = Counter(deprel_list)
    return form_list, form_counter, lemma_list, lemma_counter, postag_list, postag_counter, deprel_list, deprel_counter


# VERB VOICE ----------------------------------------------------------------------------------------------

# for voice analysis
def verb_voice_compute_frequencies(list_all_tok):
    # print ("\n------- VERB VOICE ANALYSIS -------")
    # print ("\n############### VERB VOICE ANALYSIS ##############")
    rootAuxiliary = False
    rootPassive = False
    InsertData = False
    aux_helper = ''
    _aux_VBN = []
    _auxp_VBN = []
    _active_ = []
    num_passive = 0
    num_active = 0

    for ind, tok in enumerate(list_all_tok):
        if tok[6] == 'aux':
            rootAuxiliary = True
            rootPassive = False
            aux_helper = tok
        elif tok[6] == 'aux:pass':
            rootAuxiliary = False
            rootPassive = True
            aux_helper = tok
        else:
            if tok[3] == 'VBN':
                if rootPassive:
                    num_passive += 1
                    _auxp_VBN.append([aux_helper, tok])
                    voiceType = 'Passive'
                elif rootAuxiliary:
                    voiceType = 'Active'
                    num_active += 1
                    _aux_VBN.append([aux_helper, tok])
                else:
                    num_active += 1
                    _active_.append(tok)
            else:
                voiceType = 'Active'
                rootAuxiliary = False
                rootPassive = False
                num_active += 1
                _active_.append(tok)

    auxp_VBN_organize = []
    aux_VBN_organize = []
    for pair in _auxp_VBN:
        auxp_form = pair[0][1]
        vbn_form = pair[1][1]
        pair[1][1] = auxp_form + " " + vbn_form
        pair[1] = pair[1] + ['Passive']
        auxp_VBN_organize.append(pair[1])
    for pair in _aux_VBN:
        pair[1][1] = pair[0][1] + " " + pair[1][1]
        pair[1] = pair[1] + ['Active']
        aux_VBN_organize.append(pair[1])
    _active_ = [i + ['Active'] for i in _active_]

    verb_voice_stats = [['Verb Voice', 'Frequencies'],
                  ['Passive', len(auxp_VBN_organize)],
                  ['Active', len(aux_VBN_organize) + len(_active_)]]
    return auxp_VBN_organize, aux_VBN_organize, _active_, verb_voice_stats


# verb voice; compute frequencies
def verb_voice_data_preparation(data):
    try:
        verb_postags = ['VB', 'VBN', 'VBD', 'VBG', 'VBP', 'VBZ'] # all verb types excluding modals
        verb_deprel = ['aux:pass', 'aux']
        data_2 = [tok for tok in data if (tok[3] in verb_postags or tok[6] in verb_deprel)]
        return data_2
    except:
        print("ERROR: INPUT MUST BE THE CoNLL TABLE CONTAINING THE SENTENCE ID. Program will exit.")
        mb.showinfo("ERROR",
                    "INPUT MUST BE THE MERGED CoNLL TABLE CONTAINING THE SENTENCE ID. Please use the merge option when generating your CoNLL table in the StanfordCoreNLP.py routine. Program will exit.")
        return


def voice_output(voice_word_list, data_divided_sents):
    voice_pass, voice_act_aux, voice_act, voice_stats = verb_voice_compute_frequencies(
        voice_word_list)  # passive active analysis
    voice = voice_pass + voice_act_aux + voice_act  # join
    # voice = [i + [IO_CoNLL_util.Sentence_searcher(data_divided_sents, i[documentID_position], i[sentenceID_position])] for i in
    # 		 voice]  # get full sentence
    voice_sorted = sorted(voice, key=lambda x: int(x[recordID_position]))  # sort in ascending record id order
    voice_pass = sorted(voice_pass, key=lambda x: int(x[recordID_position]))  # sort in ascending record id order
    voice_act_aux = sorted(voice_act_aux, key=lambda x: int(x[recordID_position]))  # sort in ascending record id order
    voice_act = sorted(voice_act, key=lambda x: int(x[recordID_position]))  # sort in ascending record id order
    return voice_sorted, voice_stats, voice_pass, voice_act_aux, voice_act

def verb_voice_stats(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, chartPackage, dataTransformation):
    filesToOpen = []  # Store all files that are to be opened once finished
    # print ("\nRun verb voice analysis")
    data_prep = verb_voice_data_preparation(data)

    verb_voice_list, voice_stats, voice_pass, voice_aux, voice_act = voice_output(data_prep, data_divided_sents)
    # output file names
    # NVA Noun Verb Analysis
    verb_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Verb Voice',
                                                                'list')
    verb_voice_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA',
                                                                    'Verb Voice')

    # convert list to dataframe and save
    df = pd.DataFrame(verb_voice_list)
    df, headers = process_df_headers(df, "Verb Voice")

    IO_csv_util.df_to_csv(GUI_util.window, df, verb_voice_file_name, headers=headers, index=False,
                          language_encoding='utf-8')

    if chartPackage!='No charts':

        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = ['Verb Voice']
        count_var = 1

        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                  verb_voice_file_name, outputDir,
                                                  columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                  chart_title="Frequency Distribution of Verb Voice",
                                                  outputFileNameType='verb_voice',
                                                  column_xAxis_label='Verb voice',
                                                  count_var=count_var,
                                                  hover_label=[],
                                                  groupByList=[], # 'Document' not exported
                                                  plotList=[],
                                                  chart_title_label='')

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    return filesToOpen


# VERB MODALITY ----------------------------------------------------------------------------------------------
# written by Tony Chen Gu Mar 2022
# add an extra column describing verb modality
def verb_modality_data_preparation(data):
    modals_row = []
    obl_row = []
    will_row = []
    can_row = []
    # the modal value is taken from Halliday, An Introduction to Functional Grammar, Second Edition, London: Arnold. p. 362.
    high_value_row = []
    median_value_row = []
    low_value_row = []
    verb_postags = ['MD'] # verb modals
    high_value_keywords = ['must', 'ought to', 'need', 'have to', 'be to']
    median_value_keywords = ['will', 'would', 'shall', 'should']
    low_value_keywords = ['may', 'might', 'can', 'could']
    obligation_keywords = ['must', 'need', 'form', 'should', 'ought', 'shall']
    will_would_keywords = ['will', 'would', 'll', '\'d']
    can_may_keywords = ['can', 'could', 'may', 'might']

    # i includes all the CoNLL table data, much useless for modality but easier to export; so be it, for now
    for i in data:
        # modal verbs MD
        if(i[3] in verb_postags):
            modals_row.append(i+["Modals"])

        # Halliday's modality value
        if(i[1] in high_value_keywords and i[3] in verb_postags):
            high_value_row.append(i+["High-value modals"])
        if(i[1] in median_value_keywords and i[3] in verb_postags):
            median_value_row.append(i+["Median-value modals"])
        if(i[1] in low_value_keywords and i[3] in verb_postags):
            low_value_row.append(i+["Low-value modals"])

        # modality type
        if(i[1] in obligation_keywords and i[3] in verb_postags):
            obl_row.append(i+["Obligation"])
        elif(i[1] in will_would_keywords and i[3] in verb_postags):
            will_row.append(i+["Will/Would"])
        elif(i[1] in can_may_keywords and i[3] in verb_postags):
            can_row.append(i+["Can/May"])

    verb_modals_list = modals_row
    verb_modals_stats = [['Verb Modals (POS tag MD)', 'Frequencies'], ['MD', len(modals_row)]]
    verb_modality_value_list = high_value_row + median_value_row + low_value_row
    verb_modality_list = obl_row + will_row + can_row
    verb_modality_stats = [['Verb Modality', 'Frequencies'],
                  ['Obligation', len(obl_row)],
                  ['Will/Would', len(will_row)],
                  ['Can/May', len(can_row)]]
    verb_modality_value_stats = [['Verb Modality Value', 'Frequencies'],
                  ['High-value Modals', len(high_value_row)],
                  ['Median-value Modals', len(median_value_row)],
                  ['Low-value Modals', len(low_value_row)]]

    verb_modals_list  = sorted(verb_modals_list, key=lambda x: int(x[recordID_position]))
    verb_modality_list = sorted(verb_modality_list, key=lambda x: int(x[recordID_position]))
    verb_modality_value_list = sorted(verb_modality_value_list, key=lambda x: int(x[recordID_position]))
    return verb_modals_list, verb_modals_stats, verb_modality_list, verb_modality_stats, verb_modality_value_list, verb_modality_value_stats

# modality compute frequencies of modality categories
# def verb_modality_compute_categories(data, data_divided_sents):
# 	num_obligation_mod = 0
# 	num_will_would_mod = 0
# 	num_can_may_mod = 0
# 	num_unclassified = 0
# 	verb_modality_list = []
# 	obligation_keywords = ['must', 'need', 'form', 'should', 'ought', 'shall']
# 	will_would_keywords = ['will', 'would', 'll', '\'d']
# 	can_may_keywords = ['can', 'could', 'may', 'might']

# 	try:
# 		verb_postags = ['MD']
# 		verb_modality_list = [tok[1] for tok in data if (tok[3] in verb_postags and tok[1] in obligation_keywords)]
# 		will_would_list = [tok[1] for tok in data if (tok[3] in verb_postags and tok[1] in will_would_keywords)]
# 		can_may_list = [tok[1] for tok in data if (tok[3] in verb_postags and tok[1] in can_may_keywords)]

# 		verb_modality_list = [['Verb Modality', 'Frequencies'],
# 					  ['Obligation', len(verb_modality_list)],
# 					  ['Will/would', len(will_would_list)],
# 					  ['Can/may', len(can_may_list)]]

# 		obligation_counter = len(verb_modality_list)
# 		will_would_counter = len(will_would_list)
# 		can_may_counter = len(can_may_list)

# 		return obligation_counter, will_would_counter, can_may_counter, verb_modality_list, will_would_list
# 	except:
# 		print("ERROR: INPUT MUST BE THE CoNLL TABLE CONTAINING THE SENTENCE ID. Program will exit.")
# 		mb.showinfo("ERROR",
# 					"INPUT MUST BE THE MERGED CoNLL TABLE CONTAINING THE SENTENCE ID. Please use the merge option when generating your CoNLL table in the StanfordCoreNLP.py routine. Program will exit.")
# 		return

def verb_modality_stats(config_filename, inputFilename, outputDir, data, data_divided_sents, openOutputFiles,
                        chartPackage, dataTransformation):
    import os
    head, scriptName = os.path.split(os.path.basename(__file__))
    reminders_util.checkReminder(scriptName,
                                 reminders_util.title_options_CoNLL_table_verb_modality,
                                 reminders_util.message_CoNLL_table_verb_modality,
                                 True)

    filesToOpen = []  # Store all files that are to be opened once finished

    verb_modals_list, verb_modals_stats, verb_modality_list, verb_modality_stats, verb_modality_value_list, verb_modality_value_stats = verb_modality_data_preparation(data)
    # output file names
    # NVA Noun Verb Analysis
    verb_modals_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA',
                                                             'Verb Modals')
    verb_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA',
                                                             'Verb Modality list')
    verb_modality_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA',
                                                                   'Verb Modality')
    verb_modality_value_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA',
                                                                   'Verb Modality Value')

    # convert list to dataframe and save
    df = pd.DataFrame(verb_modals_list)
    df, headers = process_df_headers(df, "Verb Modals (POS tag MD)")

    IO_csv_util.df_to_csv(GUI_util.window, df, verb_modals_file_name, headers=headers, index=False,
                          language_encoding='utf-8')

    if chartPackage!='No charts':

        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = ['Verb Modals (POS tag MD)']
        count_var = 1

        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                  verb_modals_file_name, outputDir,
                                                  columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                  chart_title="Frequency Distribution of Verb Modals (POS tag MD)",
                                                  outputFileNameType='verb_modls',
                                                  column_xAxis_label='Verb Modals (POS tag MD)',
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

    # convert list to dataframe and save
    df = pd.DataFrame(verb_modality_list)
    df, headers = process_df_headers(df, "Verb Modality")

    IO_csv_util.df_to_csv(GUI_util.window, df, verb_modality_file_name, headers=headers, index=False,
                          language_encoding='utf-8')

    if chartPackage!='No charts':

        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = ['Verb Modality']
        count_var = 1

        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                  verb_modality_file_name, outputDir,
                                                  columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                  chart_title="Frequency Distribution of Verb Modality",
                                                  outputFileNameType='verb_mod',
                                                  column_xAxis_label='Verb Modality',
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

        # convert list to dataframe and save
        df = pd.DataFrame(verb_modality_value_list)
        df, headers = process_df_headers(df, "Modality Value")

        IO_csv_util.df_to_csv(GUI_util.window, df, verb_modality_value_stats_file_name, headers=headers, index=False,
                              language_encoding='utf-8')

        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = ['Modality Value']
        count_var = 1

        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                  verb_modality_value_stats_file_name, outputDir,
                                                  columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                  chart_title="Frequency Distribution of Modality Value",
                                                  outputFileNameType='verb_mod_value',
                                                  column_xAxis_label='Modality value',
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


# VERB TENSE ----------------------------------------------------------------------------------------------
# written by Tony Chen Gu Mar 2022
# add an extra column describing verb tense
def verb_tense_data_preparation(data):
    dat = []
    vbg_counter = 0 # gerund
    vbd_counter = 0 # past
    vbn_counter = 0 # Past Principle/Passive
    vbp_counter = 0 # present (non-3rd person singular)
    vbz_counter = 0 # present (3rd person singular)
    vb_counter_future = 0 # future
    vb_counter_infinitive = 0 # infintive
    # verb_tense_list = ['VBG', 'VBD', 'VB', 'VBN', 'VBP', 'VBZ', 'MD'] # MD modal verb
    verb_tense_list = ['VBG', 'VBD', 'VB', 'VBN', 'VBP', 'VBZ'] #, 'MD'] # MD modal verb


    aux = False
    # data is the CoNLL table
    for i in data:
        if(i[3] in verb_tense_list):
            tense = i[3]
            if(tense == 'VBG'):
                tense_col = 'Gerund'
                vbg_counter+=1
            elif(tense == 'VBD'):
                tense_col = 'Past'
                vbd_counter+=1
            elif (tense == 'MD' and (i[1]=='will' or i[1]=='shall')):
                aux = True #'aux' in i[6]
            elif (tense == 'VB'):
                if aux:
                    vb_counter_future += 1
                    tense_col = 'Future'
                    aux = False
                else:
                    vb_counter_infinitive += 1
                    tense_col = 'Infinitive'
            elif(tense == 'VBN'):
                tense_col = 'Past Principle/Passive'
                vbn_counter+=1
            elif(tense == 'VBP'):
                tense_col = 'Present (non-3rd person singular)'
                vbp_counter+=1
            elif(tense == 'VBZ'):
                tense_col = 'Present (3rd person singular)'
                vbp_counter+=1
            if not aux and tense != 'MD':
                dat.append(i+[tense_col])
    verb_tense_stats = [['Verb Tense', 'Frequencies'],
                    ['Gerund', vbg_counter],
                    ['Infinitive', vb_counter_infinitive],
                    ['Past', vbd_counter],
                    ['Past Principle/Passive', vbn_counter],
                    ['Present (non-3rd person singular)', vbp_counter],
                    ['Present (3rd person singular)', vbz_counter],
                    ['Future', vb_counter_future]]
    dat = sorted(dat, key=lambda x: int(x[recordID_position]))
    return dat, verb_tense_stats

def verb_compute_frequencies(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, chartPackage, dataTransformation):
    global postag_counter
    filesToOpen = []
    # must be sorted in descending order
    form_list, form_counter, lemma_list, lemma_counter, postag_list, postag_counter, deprel_list, deprel_counter = compute_stats(data)
    verb_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Verb_ALL',
                                                                'list')
    filesToOpen.append(verb_file_name)

    verb_POS_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Verb_POS',
                                                                'list')
    df = pd.DataFrame({'Verb POS tag': postag_list})
    IO_csv_util.df_to_csv(GUI_util.window, df, verb_POS_file_name, headers=['Verb POS tag'], index=False,
                          language_encoding='utf-8')

    filesToOpen.append(verb_POS_file_name)

    columns_to_be_plotted_xAxis = []
    columns_to_be_plotted_yAxis = ['Verb POS tag']
    count_var = 1

    outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                              verb_POS_file_name, outputDir,
                                              columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                              chart_title="Frequency Distribution of Verb POS Tags",
                                              outputFileNameType='verb_POS',
                                              column_xAxis_label='Verb POS tag',
                                              count_var=count_var,
                                              hover_label=[],
                                              groupByList=[], # 'Document' not exported in this output file
                                              plotList=[],
                                              chart_title_label='')

    if outputFiles!=None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    verb_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA',
                                                                   'Verb_ALL','stats')

    df = pd.DataFrame({'Form': form_list, 'Lemma': lemma_list})
    IO_csv_util.df_to_csv(GUI_util.window, df, verb_file_name, headers=['Form', 'Lemma'], index=False,
                          language_encoding='utf-8')

    form_df = pd.DataFrame(form_counter.items(), columns=['Form', 'Form Frequency'])
    lemma_df = pd.DataFrame(lemma_counter.items(), columns=['Lemma', 'Lemma Frequency'])

    merged_df = pd.concat([form_df, lemma_df], axis=1)
    IO_csv_util.df_to_csv(GUI_util.window, merged_df, verb_stats_file_name, headers=['Form', 'Form Frequency', 'Lemma', 'Lemma Frequency'], index=False,
                          language_encoding='utf-8')

    if chartPackage!='No charts':
        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = [[0, 0]]
        count_var = 1
        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, verb_file_name, outputDir,
                                          outputFileLabel='Verbs_Form',
                                          chartPackage=chartPackage,
                                          dataTransformation=dataTransformation,
                                          chart_type_list=['bar'],
                                          chart_title="Frequency Distribution of Verbs (Form)",
                                          column_xAxis_label_var='Verb',
                                          hover_info_column_list=[],
                                          count_var=count_var,
                                          complete_sid=False)  # TODO to be changed

        # run_all returns a string; must use append
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = [[0, 1]]
        count_var = 1
        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, verb_file_name, outputDir,
                                          outputFileLabel='Verbs_Lemma',
                                          chartPackage=chartPackage,
                                          dataTransformation=dataTransformation,
                                          chart_type_list=['bar'],
                                          chart_title="Frequency Distribution of Verbs (Lemma)",
                                          column_xAxis_label_var='Verb',
                                          hover_info_column_list=[],
                                          count_var=count_var,
                                          complete_sid=False)  # TODO to be changed

        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    return filesToOpen


def verb_tense_stats(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, chartPackage, dataTransformation):
    global postag_counter
    filesToOpen = []  # Store all files that are to be opened once finished

    verb_tense_list, verb_tense_stats = verb_tense_data_preparation(data)

    # output file names
    # NVA Noun Verb Analysis
    # verb_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Verb Tense',
    # 														 'list')
    verb_tense_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA',
                                                                   'Verb Tense')

    # convert list to dataframe and save
    df = pd.DataFrame(verb_tense_list)
    df, headers = process_df_headers(df, "Verb Tense")

    IO_csv_util.df_to_csv(GUI_util.window, df, verb_tense_file_name, headers=headers, index=False,
                          language_encoding='utf-8')

    if chartPackage!='No charts':

        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = ['Verb Tense']
        count_var = 1

        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                  verb_tense_file_name, outputDir,
                                                  columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                  chart_title="Frequency Distribution of Verb Tense Value",
                                                  outputFileNameType='verb_tense',
                                                  column_xAxis_label='Verb tense',
                                                  count_var=count_var,
                                                  hover_label=[],
                                                  groupByList=[], # 'Document' not exported in this output file
                                                  plotList=[],
                                                  chart_title_label='')

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # # temporary headers added, not sure why the verb_voice_list doesn't have headers
        # df = pd.read_csv(verb_file_name, header=None, encoding='utf-8', on_bad_lines='skip')
        # df.to_csv(verb_file_name,
        # 		  header=["ID", "FORM", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document",
        # 			  "Verb Tense"])
        #
    return filesToOpen

# calls functions that compute voice, modality, tense
def verb_stats(config_filename, inputFilename, outputDir, data, data_divided_sents, openOutputFiles, chartPackage, dataTransformation):
    filesToOpen = []  # Store all files that are to be opened once finished

    startTime = IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                                   'Started running VERB ANALYSES at',
                                                   True, '', True, '', True)

    outputFiles = verb_compute_frequencies(inputFilename, outputDir, data, data_divided_sents,
                                   openOutputFiles, chartPackage, dataTransformation)

    outputFiles = verb_voice_stats(inputFilename, outputDir, data, data_divided_sents,
                                   openOutputFiles, chartPackage, dataTransformation)

    if outputFiles!=None:
        filesToOpen.extend(outputFiles)

    outputFiles = verb_modality_stats(config_filename, inputFilename, outputDir, data, data_divided_sents,
                                      openOutputFiles, chartPackage, dataTransformation)
    if outputFiles!=None:
        filesToOpen.extend(outputFiles)

    outputFiles = verb_tense_stats(inputFilename, outputDir, data, data_divided_sents,
                                   openOutputFiles, chartPackage, dataTransformation)
    if outputFiles!=None:
        filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running VERB ANALYSES at', True,
                                       '', True, startTime, True)

    return filesToOpen

#=======================================================================================================================
#Debug use
#=======================================================================================================================
# def main():
# 	file = "C:/Users/Tony Chen/Desktop/NLP_working/Test Input/conll_chn.csv"
# 	# debug use
# 	data, header = IO_csv_util.get_csv_data(file, True)
# 	# end debug use
# 	a,b = verb_modality_data_preparation(data)

# if __name__ == "__main__":
# 	main()
