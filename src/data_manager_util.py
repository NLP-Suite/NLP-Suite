import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"data_manager_util.py", ['os', 'tkinter', 'pandas', 'functools'])==False:
    sys.exit(0)

import pandas as pd
import tkinter.messagebox as mb
import os.path

def listToString(s, sep):
    str1 = ""
    for ele in s:
        str1 = str1 + ele + sep
    return str1[:-1]


def get_comparator(phrase: str) -> str:
    if phrase == 'not equals':
        return '!='
    elif phrase == 'equals':
        return '=='
    elif phrase == 'greater than':
        return '>'
    elif phrase == 'greater than or equals':
        return '>='
    elif phrase == 'less than':
        return '<'
    elif phrase == 'less than or equals':
        return '<='
    else:
        return ''
        # assert False, "Invalid comparator phrase"


def select_csv(files):
    for file in files:
        df = pd.read_csv(file)
        yield df

# not used
def select_columns(dfs: list, columns: list):
    for df in get_cols(dfs, columns):
        yield df


def concat(dfs: list, separator: str):
    s = pd.DataFrame
    for i in range(len(dfs)):
        if i == 0:
            s = dfs[i].astype(str) + separator
        else:
            if i != len(dfs) - 1:
                s = s + dfs[i].astype(str) + separator
            else:
                s = s + dfs[i].astype(str)
    return s


# helper method
def get_cols(dfs: list, headers: list):
    if len(headers) != len(dfs):
        return 'Unmatching number of dataframes and headers'
    else:
        for i in range(len(dfs)):
            yield (dfs[i])[headers[i]]

# extract ---------------------------------------------------------------------------------------------

def extract_from_csv(filePath, outputDir, outputFilename, data_files, csv_file_field_list):
    headers = [s.split(',')[1] for s in csv_file_field_list]
    sign_var = [s.split(',')[2] for s in csv_file_field_list]
    value_var = [s.split(',')[3] for s in csv_file_field_list]
    if len(data_files) <= 1:
        data_files = data_files * len(headers)
    df_list = []
    value: str
    header: str
    if len(csv_file_field_list)==0:
        mb.showwarning(title='Missing field(s)',
                       message="No field(s) to be extracted have been selected.\n\nPlease, select field(s) and try again.")
        return
    for (sign, value, header, df) in zip(sign_var, value_var, headers, data_files):
        if ' ' in header:
            header = "`" + header + "`"
        if sign == "''" and value == "''":
            df_list.append(df[[header]])
        else:
            sign = get_comparator(sign)
            if sign=='':
                mb.showwarning(title='Missing sign condition',
                               message="No condition has been entered for the \'WHERE\' value entered.\n\nPlease, include a condition for the \'WHERE\' value and try again.")
                return
            if '\'' not in value and not value.isdigit():
                value = '\'' + value + '\''
            query = header + sign + value
            result = df.query(query, engine='python')
            df_list.append(result)
    df_extract = df_list[0]
    for index, df_ex in enumerate(df_list):

        if csv_file_field_list[index].split(',')[4] in ['and', "''"]:
            if index == len(df_list) - 1:
                continue
            df_extract = df_extract.merge(df_list[index + 1], how='inner',
                                          right_index=True,
                                          left_index=True)
        elif csv_file_field_list[index].split(',')[4] == 'or':
            if index == len(df_list) - 1:
                continue
            df_extract = df_extract.merge(df_list[index + 1], how='outer',
                                          right_index=True,
                                          left_index=True)
        elif csv_file_field_list[index].split(',')[4] == '' and index != len(df_list) - 1:
            mb.showwarning(title='Missing and/or condition',
                           message="Please include an and/or condition between each WHERE condition on the column you want to extract!")
        else:
            pass
    df_extract.to_csv(outputFilename,index=False)
    return outputFilename


