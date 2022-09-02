import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"data_manager_util.py", ['os', 'tkinter', 'pandas', 'functools'])==False:
    sys.exit(0)

import pandas as pd
import tkinter.messagebox as mb
import os.path

import IO_files_util

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
    df = []
    for file in files:
        try:
            if cols==None:
                df = pd.read_csv(file, encoding='utf-8', error_bad_lines=False) # gives error on CoNLL table ,on_bad_lines='error')
            else:
                df = pd.read_csv(file,usecols=cols, encoding='utf-8', error_bad_lines=False)
        except:
            # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
            mb.showwarning(title='Missing field(s)',
                           message="Processing the file\n\n" + file + "\n\ngenerated an error. Most likely, the file has more columns in some rows that the number of column headers.\n\nPlease, check your input file and try again.")
            yield df
        yield df

# not used
def select_columns(dfs: list, columns: list):
    for df in get_cols(dfs, columns):
        yield df

# helper method
def get_cols(dfs: list, headers: list):
    if len(headers) != len(dfs):
        return 'Unmatching number of dataframes and headers'
    else:
        for i in range(len(dfs)):
            yield (dfs[i])[headers[i]]


# merge ------------------------------------------------------------------------------------------

def put_csv(lst):
    new_lst = []
    for item in lst:
        if (item.endswith('.csv')):
            it = item
            it = it.strip()
            it = it.strip("[]''")
            new_lst.append(it)
    return new_lst


def put_param(lst):
    new_lst = []
    for item in lst:
        if (item.endswith('.csv') == False):
            it = item
            it = it.strip()
            it = it.strip("[]''")
            new_lst.append(it)
    return new_lst


def drop_suffixCol(df):
    for c in df.columns:
        if c.endswith('_'):
            df = df.drop(columns=[c])
    return df


def merge(outputDir, operation_results_text_list):
    df = pd.DataFrame()
    operation_results_text_list = str(operation_results_text_list)
    ip = operation_results_text_list.split("][")
    tp = []
    for item in ip:
        tmp = item.split(',')
        for t in tmp:
            tp.append(t)
    temp = put_csv(tp)
    temp2 = put_param(tp)
    csv_lst = list(dict.fromkeys(temp))
    param_lst = list(dict.fromkeys(temp2))

    size = len(csv_lst)
    try:
        df1 = pd.read_csv(csv_lst[0], encoding='utf-8', error_bad_lines=False)
        df2 = pd.read_csv(csv_lst[1], encoding='utf-8', error_bad_lines=False)
        df = pd.merge(df1, df2, on=param_lst, how='inner', suffixes=('', '_'))
        df = drop_suffixCol(df)
        if (size > 2):
            for i in range(2, size):
                tdf = pd.read_csv(csv_lst[i], encoding='utf-8', error_bad_lines=False)
                df = pd.merge(df, tdf, on=param_lst, how='inner', suffixes=('', '_'))
                df = drop_suffixCol(df)
    except (ValueError, TypeError) as err:
        mb.showwarning(title='Error',
                        message="An unexpected error occurred while merging the files.\n\nPlease, check the input files and try again.")
        print("Unexpected err", err)
        raise
    outputFilename = IO_files_util.generate_output_file_name(csv_lst[0], os.path.dirname(csv_lst[0]),
                                                             outputDir,
                                                             '.csv', 'merge',
                                                             '', '', '', '', False, True)

    df.to_csv(outputFilename, index=False)

    return outputFilename


# APPEND ----------------------------------------------------------------------------------------------

def append(outputDir, operation_results_text_list):
    files = []
    headers = []
    i = 0
    for s in operation_results_text_list:
        files = files + [s.split(',')[0]]
        headers = headers + [s.split(',')[1]]
        tempHeaders=str(headers[i])
        i = i + 1
        if ' ' in tempHeaders: # avoid a query error later for a multi-word header
            tempHeaders = "`" + tempHeaders + "`"

    outputFilename = IO_files_util.generate_output_file_name(files[0], os.path.dirname(files[0]),
                                                             outputDir,
                                                             '.csv','append',
                                                             '', '', '', '', False, True)

    data_files = [file for file in select_csv(files)] # dataframes
    if data_files == []:
        return ''
    data_cols = [file for file in get_cols(data_files, headers)]  # selected cols
    if data_files == []:
        return ''
    sep = ','
    df_append = pd.concat(data_cols, axis=0)
    df_append.to_csv(outputFilename, header=[listToString(headers, sep)],index=False)
    return outputFilename

# filePath = [s.split(',')[0] for s in operation_results_text_list]  # file filePath
# data_files = [file for file in data_manager_util.select_csv(filePath)]  # dataframes
# headers = [s.split(',')[1] for s in operation_results_text_list]  # headers
# data_cols = [file for file in data_manager_util.get_cols(data_files, headers)]  # selected cols

# CONCATENATE ------------------------------------------------------------------------------------------

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

def concatenate(outputDir,operation_results_text_list):
    files = []
    headers = []
    sep = []
    # data_cols, headers,
    i = 0
    for s in operation_results_text_list:
        files = files + [s.split(',')[0]]
        headers = headers + [s.split(',')[1]]
        tempHeaders=str(headers[i])
        i = i + 1
        if ' ' in tempHeaders: # avoid a query error later for a multi-word header
            tempHeaders = "`" + tempHeaders + "`"
            headers = [tempHeaders]
        if i == 1:
            sep = s.split(',')[2]

    outputFilename = IO_files_util.generate_output_file_name(files[0], os.path.dirname(files[0]),
                                                             outputDir,
                                                             '.csv','concatenate',
                                                             '', '', '', '', False, True)

    data_files = [file for file in select_csv(files)] # dataframes
    if data_files == []:
        return ''
    data_cols = [file for file in get_cols(data_files, headers)]  # selected cols
    if data_cols == []:
        return ''
    df_concat = concat(data_cols, sep)
    df_concat.to_csv(outputFilename, header=[listToString(headers, sep)],index=False)
    return outputFilename

# extract/export csv/txt ---------------------------------------------------------------------------------------------

# the function can export field contents of a csv file for selected fields (and field values) to either a csv file or text file
def export_csv_to_csv_txt(outputDir,operation_results_text_list,export_type='.csv', cols=None):
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

    # os.path.dirname(files[0])
    outputFilename = IO_files_util.generate_output_file_name(files[0], '',
                                                             outputDir,
                                                             export_type,
                                                             'extract',
                                                             '', '', '', '', False, True)

    # data_files = [file for file in select_csv(files,cols)] # dataframes
    data_files = [file for file in select_csv(files,cols)] # dataframes
    if data_files == []:
        return ''
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
            # queryStr = header + '==' + '\'' + '*' + '\''
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

