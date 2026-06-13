import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "SVO_compare_util",
        ['os', 'pandas', 'tkinter']) == False:
    sys.exit(0)

import os
import pandas as pd
import tkinter.messagebox as mb

import IO_files_util
import IO_user_interface_util


def _normalize(val):
    if pd.isna(val):
        return ''
    return str(val).strip().lower()


def _load_svo(filepath):
    df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip')
    for col in ['Subject (S)', 'Verb (V)', 'Object (O)']:
        if col not in df.columns:
            mb.showerror(title='Missing column',
                         message=f'Column "{col}" not found in\n{filepath}')
            return None
    df['_s'] = df['Subject (S)'].apply(_normalize)
    df['_v'] = df['Verb (V)'].apply(_normalize)
    df['_o'] = df['Object (O)'].apply(_normalize)
    df['_triple'] = df['_s'] + ' | ' + df['_v'] + ' | ' + df['_o']
    return df


def compare(file_a, file_b, outputDir):
    filesToOpen = []

    df_a = _load_svo(file_a)
    df_b = _load_svo(file_b)
    if df_a is None or df_b is None:
        return filesToOpen

    name_a = os.path.basename(file_a)[:-4]
    name_b = os.path.basename(file_b)[:-4]

    triples_a = set(df_a['_triple'])
    triples_b = set(df_b['_triple'])

    shared = triples_a & triples_b
    only_a = triples_a - triples_b
    only_b = triples_b - triples_a

    total_union = len(triples_a | triples_b)
    overlap_pct = round(100 * len(shared) / total_union, 1) if total_union > 0 else 0
    recall_a = round(100 * len(shared) / len(triples_a), 1) if len(triples_a) > 0 else 0
    recall_b = round(100 * len(shared) / len(triples_b), 1) if len(triples_b) > 0 else 0

    rows = []

    rows.append({'Metric': 'Unique triples in ' + name_a, 'Value': len(triples_a)})
    rows.append({'Metric': 'Unique triples in ' + name_b, 'Value': len(triples_b)})
    rows.append({'Metric': 'Shared triples', 'Value': len(shared)})
    rows.append({'Metric': 'Only in ' + name_a, 'Value': len(only_a)})
    rows.append({'Metric': 'Only in ' + name_b, 'Value': len(only_b)})
    rows.append({'Metric': 'Overlap % (Jaccard)', 'Value': overlap_pct})
    rows.append({'Metric': f'% of {name_a} triples found in {name_b}', 'Value': recall_a})
    rows.append({'Metric': f'% of {name_b} triples found in {name_a}', 'Value': recall_b})

    summary_df = pd.DataFrame(rows)
    summary_file = IO_files_util.generate_output_file_name('', '', outputDir,
                                                            '.csv', 'SVO_comparison_summary',
                                                            '', '', '', '', False, True)
    summary_df.to_csv(summary_file, index=False, encoding='utf-8')
    filesToOpen.append(summary_file)

    diff_rows = []
    for t in sorted(only_a):
        s, v, o = t.split(' | ', 2)
        diff_rows.append({'Subject (S)': s, 'Verb (V)': v, 'Object (O)': o, 'Source': name_a})
    for t in sorted(only_b):
        s, v, o = t.split(' | ', 2)
        diff_rows.append({'Subject (S)': s, 'Verb (V)': v, 'Object (O)': o, 'Source': name_b})

    if diff_rows:
        diff_df = pd.DataFrame(diff_rows)
        diff_file = IO_files_util.generate_output_file_name('', '', outputDir,
                                                              '.csv', 'SVO_comparison_differences',
                                                              '', '', '', '', False, True)
        diff_df.to_csv(diff_file, index=False, encoding='utf-8')
        filesToOpen.append(diff_file)

    if shared:
        shared_rows = []
        for t in sorted(shared):
            s, v, o = t.split(' | ', 2)
            shared_rows.append({'Subject (S)': s, 'Verb (V)': v, 'Object (O)': o})
        shared_df = pd.DataFrame(shared_rows)
        shared_file = IO_files_util.generate_output_file_name('', '', outputDir,
                                                                '.csv', 'SVO_comparison_shared',
                                                                '', '', '', '', False, True)
        shared_df.to_csv(shared_file, index=False, encoding='utf-8')
        filesToOpen.append(shared_file)

    return filesToOpen
