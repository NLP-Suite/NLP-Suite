import pandas as pd
import IO_libraries_util
import GUI_util
from stanza_functions import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza

# import stanza
# stanza.download('en')
# stannlp = stanza.Pipeline(lang='en', processors='tokenize,ner,mwt,pos,lemma')

import IO_files_util
import IO_user_interface_util
import charts_util
import IO_csv_util
import reminders_util

def count_frequency_two_svo(CoreNLP_csv, senna_csv, inputFilename, inputDir, outputDir) -> list:
    """
    Only triggered when both SENNA and CoreNLP ++ options are chosen.
    Counts the frequency of same and different SVOs and SVs in the SENNA and CoreNLP ++ results and lists them
    :param CoreNLP_csv: the path of the stanford core CoreNLP ++ csv file
    :param senna_csv: the path of the Senna csv file
    :param inputFilename: the input file name; used for generating output file name
    :param inputDir: the input directory name; used for generating output file name
    :param outputDir: the output directory name; used for generating output file name
    :return: [Freq table, Comparison table], where Freq table counts the frequency of same/different SVOs, and
        Comparison table lists all the same/different SVOs
    """

    def generate_key(S, V, O):
        """
        Converts strings S, V, O to a key with the format "{S}, {V}, {O}".
        If it is a S-V combination, the key would be "{S}, {V}"
        If it is a V-O combination, the key would be "{V}, {O}"
        :return:
        """
        key = ''
        if S:
            key += S.strip().lower() + ','

        key += V.strip().lower()

        if O:
            key += ',' + O.strip().lower()

        return key

    df = pd.DataFrame(columns=['Same SVO', 'Same SV', 'Different SVO', 'Different SV', 'Total SVO', 'Total SV'])
    CoreNLP_df = pd.read_csv(CoreNLP_csv)
    senna_df = pd.read_csv(senna_csv)
    open_ie_svo, open_ie_sv, senna_svo, senna_sv = set(), set(), set(), set()

    # S, V, O are in loc 0, 1, 2

    # Adding each row of SVO into the corresponding sets
    for i in range(len(CoreNLP_df)):
        # if pd.notnull(CoreNLP_df.iloc[i, 4]):
        #     if not pd.isnull(CoreNLP_df.iloc[i, 5]) and not pd.isnull(CoreNLP_df.iloc[i, 3]):
        #         open_ie_svo.add(generate_key(S=CoreNLP_df.iloc[i, 3], V=CoreNLP_df.iloc[i, 4], O=CoreNLP_df.iloc[i, 5]))
        #     elif not pd.isnull(CoreNLP_df.iloc[i, 3]):
        #         open_ie_sv.add(generate_key(S=CoreNLP_df.iloc[i, 3], V=CoreNLP_df.iloc[i, 4], O=''))
        if pd.notnull(CoreNLP_df.iloc[i, 1]):
            if not pd.isnull(CoreNLP_df.iloc[i, 2]) and not pd.isnull(CoreNLP_df.iloc[i, 1]):
                open_ie_svo.add(
                    generate_key(S=CoreNLP_df.iloc[i, 0], V=CoreNLP_df.iloc[i, 1], O=CoreNLP_df.iloc[i, 2]))
            elif not pd.isnull(CoreNLP_df.iloc[i, 0]):
                open_ie_sv.add(generate_key(S=CoreNLP_df.iloc[i, 0], V=CoreNLP_df.iloc[i, 1], O=''))

            # elif not pd.isnull(CoreNLP_df.iloc[i, 5]):
            #     open_ie_sv.add(generate_key(S='', V=CoreNLP_df.iloc[i, 4], O=CoreNLP_df.iloc[i, 5]))
            # else:
            #     open_ie_sv.add(generate_key(S='', V=CoreNLP_df.iloc[i, 4], O=''))

    for i in range(len(senna_df)):
        # if pd.notnull(senna_df.iloc[i, 4]):
        #     if not pd.isnull(senna_df.iloc[i, 3]) and not pd.isnull(senna_df.iloc[i, 5]):  # Has S, V, O
        #         senna_svo.add(generate_key(S=senna_df.iloc[i, 3], V=senna_df.iloc[i, 4], O=senna_df.iloc[i, 5]))
        #     elif not pd.isnull(senna_df.iloc[i, 3]):  # Has S, V
        #         senna_sv.add(generate_key(S=senna_df.iloc[i, 3], V=senna_df.iloc[i, 4], O=''))
        if pd.notnull(senna_df.iloc[i, 1]): # VERB
            if not pd.isnull(senna_df.iloc[i, 0]) and not pd.isnull(senna_df.iloc[i, 2]):  # Has S and O
                senna_svo.add(generate_key(S=senna_df.iloc[i, 0], V=senna_df.iloc[i, 1], O=senna_df.iloc[i, 2]))
            elif not pd.isnull(senna_df.iloc[i, 0]):  # Has S, V NO O
                senna_sv.add(generate_key(S=senna_df.iloc[i, 0], V=senna_df.iloc[i, 1], O=''))

            # elif not pd.isnull(senna_df.iloc[i, 5]):  # Has V, O
            #     senna_sv.add(generate_key(S='', V=senna_df.iloc[i, 4], O=senna_df.iloc[i, 5]))
            # else:  # Has V
            #     senna_sv.add(generate_key(S='', V=senna_df.iloc[i, 4], O=''))

    # Generating the stats
    same_svo = open_ie_svo.intersection(senna_svo)
    same_sv = open_ie_sv.intersection(senna_sv)
    diff_svo = open_ie_svo.symmetric_difference(senna_svo)
    diff_sv = open_ie_sv.symmetric_difference(senna_sv)
    total_svo = len(same_svo) + len(diff_svo)
    total_sv = len(same_sv) + len(diff_sv)

    df = df.append(pd.DataFrame([[len(same_svo), len(same_sv), len(diff_svo), len(diff_sv), total_svo, total_sv]],
                                columns=['Same SVO', 'Same SV', 'Different SVO', 'Different SV', 'Total SVO',
                                         'Total SV']), ignore_index=True)
    freq_output_name = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                               'SENNA_CoreNLP_SVO_FREQ')
    df.to_csv(freq_output_name, index=False)

    # Listing all same and diff SV and SVOs
    compare_df = pd.DataFrame(columns=['Same', 'S', 'V', 'O', 'Different', 'S', 'V', 'O'])

    same_svo.update(same_sv)
    diff_svo.update(diff_sv)
    same, diff = [], []

    for svo in same_svo:
        split_svo = svo.split(',')
        s, v = split_svo[0], split_svo[1]
        o = split_svo[2] if len(split_svo) >= 3 else ''
        same.append((s, v, o))

    for svo in diff_svo:
        split_svo = svo.split(',')
        s, v = split_svo[0], split_svo[1]
        o = split_svo[2] if len(split_svo) >= 3 else ''
        tool = 'SENNA' if svo in senna_svo or svo in senna_sv else 'CoreNLP ++'
        diff.append((s, v, o, tool))

    if len(same) < max(len(same), len(diff)):
        same.extend([('', '', '')] * (len(diff) - len(same)))
    elif len(diff) < max(len(same), len(diff)):
        diff.extend([('', '', '')] * (len(same) - len(diff)))

    for svo1, svo2 in zip(same, diff):
        compare_df = compare_df.append(pd.DataFrame([['', svo1[0], svo1[1], svo1[2], svo2[3], svo2[0], svo2[1], svo2[2]]],
                                                    columns=['Same', 'S', 'V', 'O', 'Different', 'S', 'V', 'O']), ignore_index=True)

    # Outputting the file
    compare_outout_name = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                  'SENNA_CoreNLP_SVO_COMPARE')
    compare_df.to_csv(compare_outout_name, index=False)

    return [freq_output_name, compare_outout_name]


def combine_two_svo(CoreNLP_svo, senna_svo, inputFilename, inputDir, outputDir) -> str:
    """
    Combine the CoreNLP ++ results and Senna SVO results into one table; sorted by document ID then sentence ID
    :param CoreNLP ++_svo: the path of the stanford core CoreNLP ++ csv file
    :param senna_svo: the path of the Senna csv file
    :param inputFilename: the input file name; used for generating output file name
    :param inputDir: the input directory name; used for generating output file name
    :param outputDir: the output directory name; used for generating output file name
    :return: the name of the output csv file
    """
    columns = ['Tool', 'Subject (S)', 'Verb (V)', 'Object (O)', 'Negation', 'Location', 'Person', 'Time', 'Sentence ID', 'Sentence', 'Document ID', 'Document']
    combined_df = pd.DataFrame(columns=columns)
    dfs = [(pd.read_csv(CoreNLP_svo), 'CoreNLP ++'), (pd.read_csv(senna_svo), 'Senna')]

    for df, df_name in dfs:
        for i in range(len(df)):
            new_row = [df_name, df.loc[i, 'Subject (S)'],
                       df.loc[i, 'Verb (V)'], df.loc[i, 'Object (O)'], df.loc[i, 'Negation'], df.loc[i, 'Location'],
                       df.loc[i, 'Person'], df.loc[i, 'Time'], df.loc[i, 'Sentence ID'], df.loc[i, 'Sentence'], df.loc[i, 'Document ID'], df.loc[i, 'Document']]
            combined_df = combined_df.append(pd.DataFrame([new_row], columns=columns), ignore_index=True)

    combined_df.sort_values(by=['Document ID', 'Sentence ID'], inplace=True)
    output_name = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                          'SENNA_CoreNLP_SVO_COMBINE')
    combined_df.to_csv(output_name, index=False)

    return output_name


def filter_svo(window,svo_file_name, filter_s_fileName, filter_v_fileName, filter_o_fileName, lemmatize_s, lemmatize_v,lemmatize_o, outputDir, createCharts=True, chartPackage='Excel'):
    """
    Filters a svo csv file based on the dictionaries given, and replaces the original output csv file
    :param svo_file_name: the name of the svo csv file
    :param filter_s_fileName: the subject dict file path
    :param filter_v_fileName: the verb dict file path
    :param filter_o_fileName: the object dict file path
    """

    startTime = IO_user_interface_util.timed_alert(window, 2000, 'Analysis start',
                                                   'Started running the SVO filter algorithm at',
                                                   True, '', True)

    df = pd.read_csv(svo_file_name)
    unfiltered_svo = df.to_dict('index')
    filtered_svo = {}
    num_rows = df.shape[0]

    # Generating filter dicts
    if filter_s_fileName:
        s_set = open(filter_s_fileName, 'r', encoding='utf-8-sig', errors='ignore').read().split('\n')
        s_set = set(s_set)
    if filter_v_fileName:
        v_set = open(filter_v_fileName, 'r', encoding='utf-8-sig', errors='ignore').read().split('\n')
        v_set = set(v_set)
    if filter_o_fileName:
        o_set = open(filter_o_fileName, 'r', encoding='utf-8-sig', errors='ignore').read().split('\n')
        o_set = set(o_set)

    # Adding rows to filtered df
    for i in range(num_rows):
        subject, verb, object = '', '', ''
        if not pd.isna(unfiltered_svo[i]['Subject (S)']):
            # words = stannlp(df.loc[i, 'S'])
            # ((word.pos == "VERB") or (word.pos == "NN") or (word.pos == "NNS")):
            # subject = words.lemma
            subject = lemmatize_stanza(stanzaPipeLine(unfiltered_svo[i]['Subject (S)']))
        if not pd.isna(unfiltered_svo[i]['Verb (V)']):
            verb = lemmatize_stanza(stanzaPipeLine(unfiltered_svo[i]['Verb (V)']))
        if not pd.isna(unfiltered_svo[i]['Object (O)']):
            object = lemmatize_stanza(stanzaPipeLine(unfiltered_svo[i]['Object (O)']))

        # The s_set, v_set, and o_set are sets. The “in” in set is equivalent to “==” in string.
        if subject and filter_s_fileName and subject not in s_set:
            continue
        if verb and filter_v_fileName and verb not in v_set:
            continue
        if object and filter_o_fileName and object not in o_set:
            continue

        # the next line does NOT replace the original SVO;
        #   must replace SVO with the values computed above: subject, verb, object
        if lemmatize_s:
            unfiltered_svo[i]['Subject (S)'] = subject
        if lemmatize_v:
            unfiltered_svo[i]['Verb (V)'] = verb
        if lemmatize_o:
            unfiltered_svo[i]['Object (O)'] = object

        filtered_svo[i] = unfiltered_svo[i]

    IO_user_interface_util.timed_alert(window, 3000, 'Analysis end', 'Finished running SVO filter algorithm at', True, '', True,
                                       startTime, True)

    # Replacing the original csv file
    pd.DataFrame.from_dict(filtered_svo, orient='index').to_csv(svo_file_name, index=False)

    filesToOpen = []

    if IO_csv_util.GetNumberOfRecordInCSVFile(svo_file_name,encodingValue='utf-8')>1:

        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, svo_file_name,
                                                           outputDir,
                                                           columns_to_be_plotted_bar=[[0, 0]],
                                                           chartTitle='Frequency Distribution of Subjects (filtered)',
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='',  # 'POS_bar',
                                                           column_xAxis_label='Subjects (filtered)',
                                                           groupByList=[],
                                                           plotList=[],
                                                           chart_title_label='')
        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, svo_file_name,
                                                           outputDir,
                                                           columns_to_be_plotted_bar=[[1, 1]],
                                                           chartTitle='Frequency Distribution of Verbs (filtered)',
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='',  # 'POS_bar',
                                                           column_xAxis_label='Verbs (filtered)',
                                                           groupByList=[],
                                                           plotList=[],
                                                           chart_title_label='')
        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, svo_file_name,
                                                           outputDir,
                                                           columns_to_be_plotted_bar=[[2, 2]],
                                                           chartTitle='Frequency Distribution of Objects (filtered)',
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='',  # 'POS_bar',
                                                           column_xAxis_label='Objects (filtered)',
                                                           groupByList=[],
                                                           plotList=[],
                                                           chart_title_label='')
        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

    return filesToOpen

if __name__ == '__main__':
    senna_csv = '/Users/admin/Desktop/EMORY/Academics/Spring_2021/SOC497R/test_output/SVO_Result/NLP_SENNA_SVO_Dir_test.csv'
    CoreNLP_csv = '/Users/admin/Desktop/EMORY/Academics/Spring_2021/SOC497R/test_output/SVO_Result/test-merge-svo.csv'
    count_frequency_two_svo(CoreNLP_csv, senna_csv)
