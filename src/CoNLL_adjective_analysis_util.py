
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

def compute_stats(data):
    global postag_list, postag_counter, deprel_list, deprel_counter, ner_list, ner_counter
    postag_list = [i[3] for i in data]
    ner_list = [i[4] for i in data]
    deprel_list = [i[6] for i in data]
    postag_counter = Counter(postag_list)
    deprel_counter = Counter(deprel_list)
    ner_counter = Counter(ner_list)
    return postag_list, postag_counter, deprel_list, deprel_counter, ner_list, ner_counter



def adjective_POSTAG_NER_DEPREL_compute_lists_frequencies(data, data_divided_sents):
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

    list_adjectives_postag = data_preparation(data, ['JJ', 'JJR', 'JJS'],
                                              ['Adjective (JJ)', 'Comparative Adjective (JJR)',
                                               'Superlative Adjective (JJS)'], 3)

    adjective_postag_stats = [['Adjective POS Tags', 'Frequencies'],
                              ['Adjective (JJ)', postag_counter['JJ']],
                              ['Comparative Adjective (JJR)', postag_counter['JJR']],
                              ['Superlative Adjective (JJS)', postag_counter['JJS']]]

    list_adjectives_deprel = data_preparation(data, ['amod'], ['Adjective Modifier (amod)'], 6)

    adjective_deprel_stats = [['Adjective DEPREL Tags', 'Frequencies'],
                              ['Adjective Modifier (amod)', deprel_counter['amod']]]

    included_tags = ['JJ', 'JJR', 'JJS']
    #df = pd.DataFrame(data, columns=["ID", "Form", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document"])
    filtered_df = df[df['POS'].isin(included_tags)]
    possible_items = list(filtered_df['NER'].value_counts().keys())
    list_adjectives_ner = data_preparation(data, possible_items, possible_items, 4)

    adjective_ner_stats = [['Adjective NERs', 'Frequencies']] + [[item, ner_counter[item]] for item in possible_items]

    return list_adjectives_postag, list_adjectives_deprel, list_adjectives_ner, adjective_postag_stats, adjective_deprel_stats, adjective_ner_stats


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



def adjective_stats(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, chartPackage, dataTransformation):
    filesToOpen = []  # Store all files that are to be opened once finished

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running ADJECTIVE ANALYSES at',
                                                   True, '', True, '', True)


    adjective_postag_list, adjective_postag_stats, adjective_deprel_list, adjective_deprel_stats, adjective_ner_list, adjective_ner_stats = compute_stats(data)

    adjective_postag_list, adjective_deprel_list, adjective_ner_list, adjective_postag_stats, adjective_deprel_stats, adjective_ner_stats = adjective_POSTAG_NER_DEPREL_compute_lists_frequencies(data, data_divided_sents)

    ###debugging
    df = pd.DataFrame(adjective_postag_list)
    #debugging

    df, headers = process_df_headers(df, "Adjective POS Tags")
    # Output file names
    adjective_list_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adjective-ALL', 'list')
    adjective_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adjective', 'stats')

    adjective_postag_list_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adjective', 'POSTAG_list')
    adjective_ner_list_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adjective', 'NER_list')
    adjective_deprel_list_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adjective', 'DEPREL_list')
    adjective_postag_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adjective', 'POSTAG_stats')
    adjective_ner_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adjective', 'NER_stats')
    adjective_deprel_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'AVA', 'Adjective', 'DEPREL_stats')




    df = pd.DataFrame(adjective_postag_list)



    df1 = df.iloc[:, 1:4]
    df1.columns = ['Form', 'Lemma', 'POS']

    IO_csv_util.df_to_csv(GUI_util.window, df1, adjective_list_file_name, headers=['Form', 'Lemma', 'POS'], index=False, language_encoding='utf-8')



    df = pd.DataFrame(adjective_postag_list)
    df, headers = process_df_headers(df, "Adjective POS Tags")
    headers = list(headers) if not isinstance(headers, list) else headers



    IO_csv_util.df_to_csv(GUI_util.window, df, adjective_postag_list_file_name, headers=headers, index=False, language_encoding='utf-8')

    df = pd.DataFrame(adjective_ner_list)
    df, headers = process_df_headers(df, "Adjective NER Tags")
    headers = list(headers) if not isinstance(headers, list) else headers

    IO_csv_util.df_to_csv(GUI_util.window, df, adjective_ner_list_file_name, headers=headers, index=False, language_encoding='utf-8')

    df = pd.DataFrame(adjective_deprel_list)
    df, headers = process_df_headers(df, "Adjective DEPREL Tags")
    headers = list(headers) if not isinstance(headers, list) else headers

    IO_csv_util.df_to_csv(GUI_util.window, df, adjective_deprel_list_file_name, headers=headers, index=False, language_encoding='utf-8')

    if chartPackage != 'No charts':

        # Bar charts for Adjective Forms
        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = [[0, 0]]
        count_var = 1
        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, adjective_list_file_name, outputDir,
                                          outputFileLabel='Adjectives_Form',
                                          chartPackage=chartPackage,
                                          dataTransformation=dataTransformation,
                                          chart_type_list=['bar'],
                                          chart_title="Frequency Distribution of Adjectives (Form)",
                                          column_xAxis_label_var='Adjective',
                                          hover_info_column_list=[],
                                          count_var=count_var,
                                          complete_sid=False)

        if outputFiles:
            filesToOpen.extend(outputFiles if isinstance(outputFiles, list) else [outputFiles])

        # Bar charts for Adjective Lemmas
        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = [[0, 1]]
        count_var = 1
        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, adjective_list_file_name, outputDir,
                                          outputFileLabel='Adjectives_Lemma',
                                          chartPackage=chartPackage,
                                          dataTransformation=dataTransformation,
                                          chart_type_list=['bar'],
                                          chart_title="Frequency Distribution of Adjectives (Lemma)",
                                          column_xAxis_label_var='Adjective',
                                          hover_info_column_list=[],
                                          count_var=count_var,
                                          complete_sid=False)

        if outputFiles:
            filesToOpen.extend(outputFiles if isinstance(outputFiles, list) else [outputFiles])

        # Adjective POS Tags Frequency Chart
        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = ['Adjective POS Tags']
        count_var = 1

        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                  adjective_postag_list_file_name, outputDir,
                                                  columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                  chart_title="Frequency Distribution of Adjective POS Tags",
                                                  outputFileNameType='adjective_POS',
                                                  column_xAxis_label='Adjective POS tag',
                                                  count_var=count_var,
                                                  hover_label=[],
                                                  groupByList=['Document'],
                                                  plotList=[],
                                                  chart_title_label='')

        if outputFiles:
            filesToOpen.extend(outputFiles if isinstance(outputFiles, list) else [outputFiles])

        # Adjective NER Tags Frequency Chart
        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = ['Adjective NER Tags']
        count_var = 1

        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                  adjective_ner_list_file_name, outputDir,
                                                  columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                  chart_title="Frequency Distribution of Adjective NER Tags",
                                                  outputFileNameType='adjective_NER',
                                                  column_xAxis_label='Adjective NER tag',
                                                  count_var=count_var,
                                                  hover_label=[],
                                                  groupByList=['Document'],
                                                  plotList=[],
                                                  chart_title_label='')

        if outputFiles:
            filesToOpen.extend(outputFiles if isinstance(outputFiles, list) else [outputFiles])

        # Adjective DEPREL Tags Frequency Chart
        columns_to_be_plotted_xAxis = []
        columns_to_be_plotted_yAxis = ['Adjective DEPREL Tags']
        count_var = 1

        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation,
                                                  adjective_deprel_list_file_name, outputDir,
                                                  columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                                                  chart_title="Frequency Distribution of Adjective DEPREL Tags",
                                                  outputFileNameType='adjective_DEPREL',
                                                  column_xAxis_label='Adjective DEPREL tag',
                                                  count_var=count_var,
                                                  hover_label=[],
                                                  groupByList=['Document'],
                                                  plotList=[],
                                                  chart_title_label='')

        if outputFiles:
            filesToOpen.extend(outputFiles if isinstance(outputFiles, list) else [outputFiles])

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running ADJECTIVE ANALYSES at',
                                       True, '', True, startTime, True)

    return filesToOpen



'''
functions for debugging:


def adjective_POSTAG_NER_DEPREL_compute_lists_frequencies(data, data_divided_sents):
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
    for i, row in enumerate(data[:5]):
        print(f"🔹 Row {i + 1}: {row} (Columns: {len(row)})")
    # Create DataFrame with correct column names
    df = pd.DataFrame(data, columns=column_names)
    print(f"✅ DataFrame successfully created with {column_count} columns!")
    print(f"🔹 DataFrame shape: {df.shape}")
    print(f"🔹 Column names: {df.columns.tolist()}")


    print("🔹 Entered adjective_POSTAG_NER_DEPREL_compute_lists_frequencies")  # Debugging Step 1

    if not data or len(data) == 0:
        print("❌ Error: Data is empty!")
        return [], [], [], [], [], []

    print(f"🔹 First row of data: {data[0]}")  # Debugging Step 2

    try:
        list_adjectives_postag = data_preparation(data, ['JJ', 'JJR', 'JJS'],
                                                  ['Adjective (JJ)', 'Comparative Adjective (JJR)',
                                                   'Superlative Adjective (JJS)'], 3)
    except Exception as e:
        print(f"❌ Error in data_preparation for POS tags: {e}")
        return [], [], [], [], [], []

    print("🔹 Successfully processed POS tags")  # Debugging Step 3

    try:
        list_adjectives_deprel = data_preparation(data, ['amod'], ['Adjective Modifier (amod)'], 6)
    except Exception as e:
        print(f"❌ Error in data_preparation for DEPREL: {e}")
        return [], [], [], [], [], []

    print("🔹 Successfully processed DEPREL")  # Debugging Step 4

    try:
        included_tags = ['JJ', 'JJR', 'JJS']
        #df = pd.DataFrame(data, columns=['ID', 'Form', 'Lemma', 'POS', 'NER', 'Head', 'DepRel', 'Deps', 'Clause Tag', 'Record ID', 'Sentence ID', 'Document ID', 'Document'])
        print(f"🔹 DataFrame created. Shape: {df.shape}")  # Debugging Step 5

        filtered_df = df[df['POS'].isin(included_tags)]
        possible_items = list(filtered_df['NER'].value_counts().keys())
    except Exception as e:
        print(f"❌ Error processing DataFrame: {e}")
        return [], [], [], [], [], []

    print("🔹 Successfully filtered adjectives")  # Debugging Step 6

    try:
        list_adjectives_ner = data_preparation(data, possible_items, possible_items, 4)
    except Exception as e:
        print(f"❌ Error in data_preparation for NER: {e}")
        return [], [], [], [], [], []

    print("🔹 Successfully processed NER")  # Debugging Step 7

    return list_adjectives_postag, list_adjectives_deprel, list_adjectives_ner, \
        [['Adjective POS Tags', 'Frequencies']], [['Adjective DEPREL Tags', 'Frequencies']], [
        ['Adjective NERs', 'Frequencies']]
'''