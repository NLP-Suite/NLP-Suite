import pandas as pd

import IO_files_util


def count_frequency_two_svo(open_ie_csv, senna_csv, inputFilename, inputDir, outputDir):
    def generate_key(S, V, O):
        key = ''
        print(S, V, O)
        if S:
            key += S.strip().lower() + ','

        key += V.strip().lower()

        if O:
            key += ',' + O.strip().lower()

        return key

    df = pd.DataFrame(columns=['Same SVO', 'Same SV', 'Different SVO', 'Different SV'])
    openIE_df = pd.read_csv(open_ie_csv)
    senna_df = pd.read_csv(senna_csv)
    open_ie_svo, open_ie_sv, senna_svo, senna_sv = set(), set(), set(), set()

    for i in range(len(openIE_df)):
        if not pd.isnull(openIE_df.iloc[i, 5]) and not pd.isnull(openIE_df.iloc[i, 3]):
            open_ie_svo.add(generate_key(S=openIE_df.iloc[i, 3], V=openIE_df.iloc[i, 4], O=openIE_df.iloc[i, 5]))
        elif not pd.isnull(openIE_df.iloc[i, 3]):
            open_ie_sv.add(generate_key(S=openIE_df.iloc[i, 3], V=openIE_df.iloc[i, 4], O=''))
        elif not pd.isnull(openIE_df.iloc[i, 5]):
            open_ie_sv.add(generate_key(S='', V=openIE_df.iloc[i, 4], O=openIE_df.iloc[i, 5]))
        else:
            open_ie_sv.add(generate_key(S='', V=openIE_df.iloc[i, 4], O=''))

    for i in range(len(senna_df)):
        if not pd.isnull(senna_df.iloc[i, 3]) and not pd.isnull(senna_df.iloc[i, 5]):       # Has S, V, O
            senna_svo.add(generate_key(S=senna_df.iloc[i, 3], V=senna_df.iloc[i, 4], O=senna_df.iloc[i, 5]))
        elif not pd.isnull(senna_df.iloc[i, 3]):                                            # Has S, V
            senna_sv.add(generate_key(S=senna_df.iloc[i, 3], V=senna_df.iloc[i, 4], O=''))
        elif not pd.isnull(senna_df.iloc[i, 5]):                                            # Has V, O
            senna_sv.add(generate_key(S='', V=senna_df.iloc[i, 4], O=senna_df.iloc[i, 5]))
        else:                                                                               # Has V
            senna_sv.add(generate_key(S='', V=senna_df.iloc[i, 4], O=''))

    same_svo = open_ie_svo.intersection(senna_svo)
    same_sv = open_ie_sv.intersection(senna_sv)
    diff_svo = open_ie_svo.symmetric_difference(senna_svo)
    diff_sv = open_ie_sv.symmetric_difference(senna_sv)

    df = df.append(pd.DataFrame([[len(same_svo), len(same_sv), len(diff_svo), len(diff_sv)]],
                                columns=['Same SVO', 'Same SV', 'Different SVO', 'Different SV']), ignore_index=True)
    df.to_csv(IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                      'SENNA_OPENIE_SVO_COMBINE'), index=False)


def combine_two_svo(open_ie_svo, senna_svo, inputFilename, inputDir, outputDir):
    columns = ['Tool', 'Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O/A', 'LOCATION', 'TIME', 'Sentence']
    combined_df = pd.DataFrame(
        columns=columns)
    dfs = [(pd.read_csv(open_ie_svo), 'Open IE'), (pd.read_csv(senna_svo), 'Senna')]

    for df, df_name in dfs:
        for i in range(len(df)):
            new_row = [df_name, df.loc[i, 'Document ID'], df.loc[i, 'Sentence ID'], df.loc[i, 'Document'],
                       df.loc[i, 'S'],
                       df.loc[i, 'V'], df.loc[i, 'O/A'], df.loc[i, 'LOCATION'],
                       df.loc[i, 'TIME'], df.loc[i, 'Sentence']]
            combined_df = combined_df.append(pd.DataFrame([new_row], columns=columns), ignore_index=True)

    combined_df.sort_values(by=['Document ID', 'Sentence ID'], inplace=True)
    combined_df.to_csv(IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                               'SENNA_OPENIE_SVO_FREQ'), index=False)


if __name__ == '__main__':
    senna_csv = '/Users/admin/Desktop/EMORY/Academics/Spring_2021/SOC497R/test_output/SVO_Result/NLP_SENNA_SVO_Dir_test.csv'
    openIE_csv = '/Users/admin/Desktop/EMORY/Academics/Spring_2021/SOC497R/test_output/SVO_Result/test-merge-svo.csv'
    count_frequency_two_svo(openIE_csv, senna_csv)
    # combine_two_svo(open_ie_svo=openIE_csv, senna_svo=senna_csv)
