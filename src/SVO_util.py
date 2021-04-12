import pandas as pd

import IO_files_util


def count_frequency_two_svo(open_ie_csv, senna_csv, inputFilename, inputDir, outputDir) -> list:
    """
    Only triggered when both Senna and OpenIE options are chosen.
    Counts the frequency of same and different SVOs and SVs in the Senna and OpenIE results and lists them
    :param open_ie_csv: the path of the stanford core Open IE csv file
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
    openIE_df = pd.read_csv(open_ie_csv)
    senna_df = pd.read_csv(senna_csv)
    open_ie_svo, open_ie_sv, senna_svo, senna_sv = set(), set(), set(), set()

    # Adding each row of SVO into the corresponding sets
    for i in range(len(openIE_df)):
        if pd.notnull(openIE_df.iloc[i, 4]):
            if not pd.isnull(openIE_df.iloc[i, 5]) and not pd.isnull(openIE_df.iloc[i, 3]):
                open_ie_svo.add(generate_key(S=openIE_df.iloc[i, 3], V=openIE_df.iloc[i, 4], O=openIE_df.iloc[i, 5]))
            elif not pd.isnull(openIE_df.iloc[i, 3]):
                open_ie_sv.add(generate_key(S=openIE_df.iloc[i, 3], V=openIE_df.iloc[i, 4], O=''))
            # elif not pd.isnull(openIE_df.iloc[i, 5]):
            #     open_ie_sv.add(generate_key(S='', V=openIE_df.iloc[i, 4], O=openIE_df.iloc[i, 5]))
            # else:
            #     open_ie_sv.add(generate_key(S='', V=openIE_df.iloc[i, 4], O=''))

    for i in range(len(senna_df)):
        if pd.notnull(senna_df.iloc[i, 4]):
            if not pd.isnull(senna_df.iloc[i, 3]) and not pd.isnull(senna_df.iloc[i, 5]):  # Has S, V, O
                senna_svo.add(generate_key(S=senna_df.iloc[i, 3], V=senna_df.iloc[i, 4], O=senna_df.iloc[i, 5]))
            elif not pd.isnull(senna_df.iloc[i, 3]):  # Has S, V
                senna_sv.add(generate_key(S=senna_df.iloc[i, 3], V=senna_df.iloc[i, 4], O=''))
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
                                                               'SENNA_OPENIE_SVO_FREQ')
    df.to_csv(freq_output_name, index=False)

    # Listing all same and diff SV and SVOs
    compare_df = pd.DataFrame(columns=['Same', 'S', 'V', 'O', 'Different', 'S', 'V', 'O'])

    same_svo.update(same_sv)
    diff_svo.update(diff_sv)
    same, diff = [], []

    for svo in same_svo:
        splitted_svo = svo.split(',')
        s, v = splitted_svo[0], splitted_svo[1]
        o = splitted_svo[2] if len(splitted_svo) >= 3 else ''
        same.append((s, v, o))

    for svo in diff_svo:
        splitted_svo = svo.split(',')
        s, v = splitted_svo[0], splitted_svo[1]
        o = splitted_svo[2] if len(splitted_svo) >= 3 else ''
        tool = 'Senna' if svo in senna_svo or svo in senna_sv else 'OpenIE'
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
                                                                  'SENNA_OPENIE_SVO_COMPARE')
    compare_df.to_csv(compare_outout_name, index=False)

    return [freq_output_name, compare_outout_name]


def combine_two_svo(open_ie_svo, senna_svo, inputFilename, inputDir, outputDir) -> str:
    """
    Combine the OpenIE results and Senna SVO results into one table; sorted by document ID then sentence ID
    :param open_ie_svo: the path of the stanford core Open IE csv file
    :param senna_svo: the path of the Senna csv file
    :param inputFilename: the input file name; used for generating output file name
    :param inputDir: the input directory name; used for generating output file name
    :param outputDir: the output directory name; used for generating output file name
    :return: the name of the output csv file
    """
    columns = ['Tool', 'Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O/A', 'LOCATION', 'TIME', 'Sentence']
    combined_df = pd.DataFrame(columns=columns)
    dfs = [(pd.read_csv(open_ie_svo), 'Open IE'), (pd.read_csv(senna_svo), 'Senna')]

    for df, df_name in dfs:
        for i in range(len(df)):
            new_row = [df_name, df.loc[i, 'Document ID'], df.loc[i, 'Sentence ID'], df.loc[i, 'Document'],
                       df.loc[i, 'S'],
                       df.loc[i, 'V'], df.loc[i, 'O/A'], df.loc[i, 'LOCATION'],
                       df.loc[i, 'TIME'], df.loc[i, 'Sentence']]
            combined_df = combined_df.append(pd.DataFrame([new_row], columns=columns), ignore_index=True)

    combined_df.sort_values(by=['Document ID', 'Sentence ID'], inplace=True)
    output_name = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                          'SENNA_OPENIE_SVO_COMBINE')
    combined_df.to_csv(output_name, index=False)

    return output_name


def filter_svo(svo_file_name, filter_s, filter_v, filter_o):
    """
    Filters a svo csv file based on the dictionaries given, and replaces the original output csv file
    :param svo_file_name: the name of the svo csv file
    :param filter_s: the subject dict file path
    :param filter_v: the verb dict file path
    :param filter_o: the object dict file path
    """
    df = pd.read_csv(svo_file_name)
    filtered_df = pd.DataFrame(columns=df.columns)

    # Generating filter dicts
    if filter_s:
        s_dict = open(filter_s, 'r', encoding='utf-8-sig', errors='ignore').read().split('\n')
        s_dict = set(s_dict)
    if filter_v:
        v_dict = open(filter_v, 'r', encoding='utf-8-sig', errors='ignore').read().split('\n')
        v_dict = set(v_dict)
    if filter_o:
        o_dict = open(filter_o, 'r', encoding='utf-8-sig', errors='ignore').read().split('\n')
        o_dict = set(o_dict)

    # Adding rows to filtered df
    for i in range(len(df)):
        if filter_s and df.loc[i, 'S'] not in s_dict or filter_v and df.loc[i, 'V'] not in v_dict or filter_o and \
                df.loc[i, 'O/A'] not in o_dict:
            continue
        filtered_df.append(df.loc[i, :], ignore_index=True)

    # Replacing the original csv file
    filtered_df.to_csv(svo_file_name, index=False)


if __name__ == '__main__':
    senna_csv = '/Users/admin/Desktop/EMORY/Academics/Spring_2021/SOC497R/test_output/SVO_Result/NLP_SENNA_SVO_Dir_test.csv'
    openIE_csv = '/Users/admin/Desktop/EMORY/Academics/Spring_2021/SOC497R/test_output/SVO_Result/test-merge-svo.csv'
    count_frequency_two_svo(openIE_csv, senna_csv)
    # combine_two_svo(open_ie_svo=openIE_csv, senna_svo=senna_csv)
