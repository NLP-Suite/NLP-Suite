import sys
import GUI_util
import IO_libraries_util
from collections import Counter
import pandas as pd

import IO_files_util
import IO_csv_util
import IO_user_interface_util
import CoNLL_util
import charts_util
import statistics_csv_util
import Stanford_CoreNLP_tags_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "CoNLL Table Analyzer",
                                          ['csv', 'os', 'collections']) == False:
    sys.exit(0)


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

# Written by Julian Lucio P 2025
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

def compute_stats(data):
    global postag_list, postag_counter, deprel_list, deprel_counter
    postag_list = [i[3] for i in data]
    deprel_list = [i[6] for i in data]
    postag_counter = Counter(postag_list)
    deprel_counter = Counter(deprel_list)
    return postag_list, postag_counter, deprel_list, deprel_counter



def adverb_POSTAG_DEPREL_compute_lists_frequencies(data, data_divided_sents):
    column_count = len(data[0])  # Get number of columns from first row

    # Define column names dynamically based on detected column count
    if column_count == 14:
        column_names = ["ID", "Form", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag",
                        "Record ID", "Sentence ID", "Document ID", "Document", "Year"]
    elif column_count == 13:
        column_names = ["ID", "Form", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag",
                        "Record ID", "Sentence ID", "Document ID", "Document"]
    else:
        raise ValueError(f"❌ Unexpected number of columns: {column_count}")

    df = pd.DataFrame(data, columns=column_names)

    list_adverbs_postag = data_preparation(data, ['RB', 'RBR', 'RBS'],
                                           ['Adverb (RB)', 'Comparative Adverb (RBR)',
                                            'Superlative Adverb (RBS)'], 3)

    adverbs_postag_stats = [['Adverb POS Tags', 'Frequencies'],
                            ['Adverb (RB)', postag_counter['RB']],
                            ['Comparative Adverb (RBR)', postag_counter['RBR']],
                            ['Superlative Adverb (RBS)', postag_counter['RBS']]]

    list_adverbs_deprel = data_preparation(data, ['advmod'], ['Adverbial Modifier (advmod)'], 6)

    adverbs_deprel_stats = [['Adverb DEPREL Tags', 'Frequencies'],
                           ['Adverbial Modifier (advmod)', deprel_counter['advmod']]]

    included_tags = ['RB', 'RBR', 'RBS']  # Adverb POS tags

    #df = pd.DataFrame(data, columns=["ID", "Form", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document"])
    filtered_df = df[df['POS'].isin(included_tags)]


    return list_adverbs_postag, list_adverbs_deprel, adverbs_postag_stats, adverbs_deprel_stats


def process_df_headers(df, word_type):
    num_columns = len(df.columns)

    if num_columns == 15:  # Includes a Date column
        df.columns = ["ID", "FORM", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID",
                      "Sentence ID", "Document ID", "Document", "Date", word_type]
    elif num_columns == 14:  # Standard CoNLL format
        df.columns = ["ID", "FORM", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID",
                      "Sentence ID", "Document ID", "Document", word_type]
    else:
        raise ValueError(f"Unexpected number of columns: {num_columns}")

    return df, df.columns



def adverb_stats(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, chartPackage, dataTransformation):
    filesToOpen = []  # Store all files that are to be opened once finished

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running ADVERB ANALYSES at',
                                                   True, '', True, '', True)


    adverbs_postag_list, adverbs_postag_stats, adverbs_deprel_list, adverbs_deprel_stats = compute_stats(data)

    adverbs_postag_list, adverbs_deprel_list, adverbs_postag_stats, adverbs_deprel_stats  = adverb_POSTAG_DEPREL_compute_lists_frequencies(data, data_divided_sents)

    ###debugging
    df = pd.DataFrame(adverbs_postag_list)
    #debugging

    df, headers = process_df_headers(df, "Adverbs POS Tags")
    # Output file names
    adverbs_list_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adverbs-ALL', 'list')
    adverbs_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adverb', 'stats')

    adverbs_postag_list_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adverb', 'POSTAG_list')
    #adverbs_ner_list_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adverb', 'NER_list')
    adverbs_deprel_list_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adverb', 'DEPREL_list')
    adverbs_postag_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adverb', 'POSTAG_stats')
    #adverbs_ner_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adverb', 'NER_stats')
    adverbs_deprel_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adverb', 'DEPREL_stats')




    df = pd.DataFrame(adverbs_postag_list)



    df1 = df.iloc[:, 1:4]
    df1.columns = ['Form', 'Lemma', 'POS']

    IO_csv_util.df_to_csv(GUI_util.window, df1, adverbs_list_file_name, headers=['Form', 'Lemma', 'POS'], index=False, language_encoding='utf-8')



    df = pd.DataFrame(adverbs_postag_list)
    df, headers = process_df_headers(df, "Adverbs POS Tags")
    headers = list(headers) if not isinstance(headers, list) else headers



    IO_csv_util.df_to_csv(GUI_util.window, df, adverbs_postag_list_file_name, headers=headers, index=False, language_encoding='utf-8')




    df = pd.DataFrame(adverbs_deprel_list)
    df, headers = process_df_headers(df, "Adverb DEPREL Tags")
    headers = list(headers) if not isinstance(headers, list) else headers

    IO_csv_util.df_to_csv(GUI_util.window, df, adverbs_deprel_list_file_name, headers=headers, index=False, language_encoding='utf-8')

    if chartPackage != 'No charts':

        # Bar charts for Adverb Forms
        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = [[0, 0]]
        count_var = 1
        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, adverbs_list_file_name, outputDir,
                                          outputFileLabel='Adverbs_Form',
                                          chartPackage=chartPackage,
                                          dataTransformation=dataTransformation,
                                          chart_type_list=['bar'],
                                          chart_title="Frequency Distribution of Adverbs (Form)",
                                          column_xAxis_label_var='Adverb',
                                          hover_info_column_list=[],
                                          count_var=count_var,
                                          complete_sid=False)

        if outputFiles:
            filesToOpen.extend(outputFiles if isinstance(outputFiles, list) else [outputFiles])

        # Bar charts for Adverb Lemmas
        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = [[0, 1]]
        count_var = 1
        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, adverbs_list_file_name, outputDir,
                                          outputFileLabel='Adverbs_Lemma',
                                          chartPackage=chartPackage,
                                          dataTransformation=dataTransformation,
                                          chart_type_list=['bar'],
                                          chart_title="Frequency Distribution of Adverbs (Lemma)",
                                          column_xAxis_label_var='Adverb',
                                          hover_info_column_list=[],
                                          count_var=count_var,
                                          complete_sid=False)

        if outputFiles:
            filesToOpen.extend(outputFiles if isinstance(outputFiles, list) else [outputFiles])

        # Adverb POS Tags Frequency Chart
        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = ['Adverbs POS Tags']
        count_var = 1

        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                  adverbs_postag_list_file_name, outputDir,
                                                  columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                  chart_title="Frequency Distribution of Adverb POS Tags",
                                                  outputFileNameType='adverb_POS',
                                                  column_xAxis_label='Adverb POS tag',
                                                  count_var=count_var,
                                                  hover_label=[],
                                                  groupByList=['Document'],
                                                  plotList=[],
                                                  chart_title_label='')

        if outputFiles:
            filesToOpen.extend(outputFiles if isinstance(outputFiles, list) else [outputFiles])


        # Adverb DEPREL Tags Frequency Chart
        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = ['Adverbs DEPREL Tags']
        count_var = 1

        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                  adverbs_deprel_list_file_name, outputDir,
                                                  columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                  chart_title="Frequency Distribution of Adverbs DEPREL Tags",
                                                  outputFileNameType='adverb_DEPREL',
                                                  column_xAxis_label='Adverb DEPREL tag',
                                                  count_var=count_var,
                                                  hover_label=[],
                                                  groupByList=['Document'],
                                                  plotList=[],
                                                  chart_title_label='')

        if outputFiles:
            filesToOpen.extend(outputFiles if isinstance(outputFiles, list) else [outputFiles])

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running ADVERB ANALYSES at',
                                       True, '', True, startTime, True)

    return filesToOpen

