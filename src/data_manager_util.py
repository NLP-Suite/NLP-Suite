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


# merge ------------------------------------------------------------------------------------------

def merge(filePath, outputDir, outputFilename, csv_file_field_list):
    # processed_params: [(field1, field2..., dataframe1), (field1', field2'..., dataframe2)]
    processed_params = []
    csv_file_field_list = list(dict.fromkeys(csv_file_field_list))
    param_str: str
    for param_str in csv_file_field_list:
        params = list(param_str.split(','))
        csv_path = params[0]
        df = pd.read_csv(csv_path)
        params.pop(0)
        params.append(df)
        processed_params.append(params)
    indexes = processed_params[0][:-1]
    data_files_for_merge = [processed_params[0][-1]]
    for row in processed_params[1:]:
        # rename different field names to the field name on the first document.
        # They will be merged anyway so this doesn't change much.
        column_mapping = dict()
        for index_int, field in enumerate(indexes):
            # {original_index1: new_index1, original_index2: new_index2...}
            column_mapping[row[index_int]] = field
        df: DataFrame = row[-1]
        df.rename(columns=column_mapping)
        data_files_for_merge.append(df)

    df_merged: DataFrame = data_files_for_merge[0]
    for df in data_files_for_merge[1:]:
        df_merged = pd.concat([df_merged, df], join='inner', ignore_index=False)
    df_merged.to_csv(outputFilename)

    return outputFilename

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


