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

def select_csv(files,cols=None):
    for file in files:
        try:
            if cols==None:
                df = pd.read_csv(file,on_bad_lines='error')
            else:
                df = pd.read_csv(file,usecols=cols,on_bad_lines='error')
        except:
            # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
            print("raised error")
        yield df

# def select_csv(files):
#     for file in files:
#         df = pd.read_csv(file)
#         yield df

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

def merge(outputFilename, operation_results_text_list):
    # processed_params: [(field1, field2..., dataframe1), (field1', field2'..., dataframe2)]
    processed_params = []
    operation_results_text_list = list(operation_results_text_list)

    i = 0
    for text in operation_results_text_list:
        param_str: str
        for param_str in text:
            params = list(param_str.split(','))
            csv_path = params[0]
            df = pd.read_csv(csv_path)
            params.pop(0)
            params.append(df)
            processed_params.append(params)
        indexes = processed_params[i][:-1]
        data_files_for_merge = [processed_params[i][-1]]
        i = i + 1
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
            df_merged = df_merged.merge(df, how='left', on=indexes, suffixes=('', '_delme'))
        df_merged.to_csv(outputFilename, index=False)

    return outputFilename
# append ----------------------------------------------------------------------------------------------

def append(outputFilename, data_cols, headers, operation_results_text_list):
    sep = ','
    df_append = pd.concat(data_cols, axis=0)
    df_append.to_csv(outputFilename, header=[listToString(headers, sep)],index=False)
    return outputFilename

# concatenate ------------------------------------------------------------------------------------------

def concatenate(outputFilename, data_cols, headers, operation_results_text_list):
    for s in operation_results_text_list:
        if s[-1] == ',':
            sep = ','
        else:
            temp = s.split(',')
            if len(temp) >= 3:
                sep = temp[2]
                break
    df_concat = concat(data_cols, sep)
    df_concat.to_csv(outputFilename, header=[listToString(headers, sep)],index=False)
    return outputFilename

# extract/export csv/txt ---------------------------------------------------------------------------------------------

# the function can export field contents of a csv file for selected fields (and field values) to either a csv file or text file
def export_csv_to_csv_txt(outputFilename, operation_results_text_list,export_type='.csv', cols=[0]):
    files = []
    headers = []
    sign_var = []
    value_var = []
    and_or = []
    # operation_results_text_list: the various comma-separated items in the [] list cannot have spaces after each comma
    #       operation_results_text_list.append(str(outputFilenameCSV1_new) + ',VERB,<>,be,and')
    #       and not         operation_results_text_list.append(str(outputFilenameCSV1_new) + ', VERB, <>, be, and')
    i = 0
    for s in operation_results_text_list:
        files = files + [s.split(',')[0]]
        headers = headers + [s.split(',')[1]]
        tempHeaders=str(headers[i])
        i = i + 1
        if ' ' in tempHeaders: # avoid a query error later for a multi-word header
            tempHeaders = "`" + tempHeaders + "`"
            headers = headers + [tempHeaders]
        sign_var = sign_var + [s.split(',')[2]]
        value_var = value_var + [s.split(',')[3]]
        and_or = and_or + [s.split(',')[4]]

    # data_files = [file for file in select_csv(files,cols)] # dataframes
    data_files = [file for file in select_csv(files)] # dataframes

    queryStr = ''
    if len(data_files) <= 1:
        data_files = data_files * len(headers)
    df_list = []
    value: str
    header: str
    if len(operation_results_text_list) == 0:
        mb.showwarning(title='Missing field(s)',
                       message="No field(s) to be extracted have been selected.\n\nPlease, select field(s) and try again.")
        return
    for (sign, value, and_or, header, df) in zip(sign_var, value_var, and_or, headers, data_files):

        if sign == "''" and value == "''":
            df_list.append(df[[header]])
        else:
            if sign == '':
                mb.showwarning(title='Missing sign condition',
                               message="No condition has been entered for the \'WHERE\' value entered.\n\nPlease, include a condition for the \'WHERE\' value and try again.")
                return
            if '\'' not in value and not value.isdigit():
                value = '\'' + value + '\''
            if sign == '=':
                sign = '=='
            if sign == '<>': # different
                sign = '!='
            if queryStr == '':
                queryStr = header + sign + value
            else:
                queryStr = queryStr + ' ' + and_or + ' ' + header + sign + value
    result = df.query(queryStr, engine='python')
    df_list.append(result)
    df_extract = df_list[0]
    for index, df_ex in enumerate(df_list):

        if operation_results_text_list[index].split(',')[4] in ['and', "''"]:
            if index == len(df_list) - 1:
                continue
            df_extract = df_extract.merge(df_list[index + 1], how='inner',
                                          right_index=True,
                                          left_index=True)
        elif operation_results_text_list[index].split(',')[4] == 'or':
            if index == len(df_list) - 1:
                continue
            df_extract = df_extract.merge(df_list[index + 1], how='outer',
                                          right_index=True,
                                          left_index=True)
        elif operation_results_text_list[index].split(',')[4] == '' and index != len(df_list) - 1:
            mb.showwarning(title='Missing and/or condition',
                           message="Please include an and/or condition between each WHERE condition on the column you want to extract!")
        else:
            pass
    if export_type == '.csv':
        df_extract.to_csv(outputFilename, index=False)
    else: # .txt
        text = df_extract.to_csv(index=False)
        text = text.replace(",", " ")
        with open(outputFilename, "w", newline='') as text_file:
            text_file.write(text)
    return outputFilename
