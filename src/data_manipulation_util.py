import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"data_manipulation_util.py", ['os', 'tkinter', 'pandas', 'functools'])==False:
    sys.exit(0)

import csv
import pandas as pd
import tkinter.messagebox as mb
import os.path

import IO_files_util

def distinct_values(csv_path, column, limit=500):
    """The distinct values of ONE column, sorted, as strings -- for offering in a pick-list.

    The WHERE clause required the user to TYPE the value to test against, case-sensitively, so you had
    to know already what the column held and a single typo silently matched nothing. Reading the values
    lets the GUI offer them instead.

    Returns [] rather than raising on every failure -- no file, no such column, unreadable csv -- because
    this only fills a convenience list: a file that cannot be read here must still be typed against by
    hand, not bring the GUI down.

    Numeric-looking values sort numerically, so a Year column reads 1892, 1893, ... and not 1892, 18930,
    19. *limit* caps the list, since a free-text column can hold tens of thousands of distinct values
    that no dropdown can usefully show.
    """
    if not csv_path or not column or not os.path.isfile(csv_path):
        return []

    # the stdlib csv module rather than pandas: only one column is wanted, the file is streamed instead
    # of loaded whole, and it sidesteps encoding_errors, which needs pandas >= 1.3 while this environment
    # runs 1.2.4. It also keeps the helper testable, since the test suite stubs pandas out.
    values = set()
    try:
        with open(csv_path, 'r', encoding='utf-8', errors='ignore', newline='') as fin:
            reader = csv.reader(fin)
            try:
                headers = next(reader)
            except StopIteration:
                return []                      # empty file
            if column not in headers:
                return []
            idx = headers.index(column)
            for row in reader:
                if idx < len(row):             # short rows are skipped, not fatal
                    text = row[idx].strip()
                    if text:
                        values.add(text)
                        if len(values) > limit * 4:
                            break              # stop reading a huge free-text column early
    except Exception:
        return []

    def sort_key(text):
        # the raw text is the final tiebreaker: without it 'COBB' and 'Cobb' share a key, and since the
        # values come out of a set their order would vary from run to run
        try:
            return (0, float(text), '', text)
        except ValueError:
            return (1, 0.0, text.lower(), text)

    return sorted(values, key=sort_key)[:limit]


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

def check_fields_selected(headers, operation):
    """False, with an explanation, when any record carries no field name.

    A record is 'path,field'; with no field chosen it is 'path,' and the field parses as an empty
    string. That empty string reached get_cols as df[''] and raised KeyError: '' -- a traceback in a
    terminal the user never sees, instead of a message naming the selection that is missing.
    """
    if any(str(h).strip() == '' for h in headers):
        mb.showwarning(title='Field not selected', message='The ' + operation + ' operation needs a field selected for EVERY csv file listed.\n\nAt least one of the files listed has no field.\n\nPlease, select a field for each file -- click the + button to add a file, then pick its field from the dropdown -- then click OK and RUN again.')
        return False
    return True

def select_csv(files,cols=None):
    df = []
    for file in files:
        try:
            if cols==None:
                df = pd.read_csv(file, encoding='utf-8', on_bad_lines='skip') # gives error on CoNLL table ,on_bad_lines='error')
            else:
                df = pd.read_csv(file,usecols=cols, encoding='utf-8', on_bad_lines='skip')
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

# operation_results_text_list -----------------------------------------------------------------------

# filePath = [s.split(',')[0] for s in operation_results_text_list]  # file filePath
# data_files = [file for file in data_manipulation_util.select_csv(filePath)]  # dataframes
# headers = [s.split(',')[1] for s in operation_results_text_list]  # headers
# data_cols = [file for file in data_manipulation_util.get_cols(data_files, headers)]  # selected cols


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

    if not check_fields_selected(headers, 'APPEND'):
        return ''

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
    df_append.to_csv(outputFilename, encoding='utf-8', header=[listToString(headers, sep)],index=False)
    return outputFilename

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
        # tolerant parse: a record is 'path,field,separator', but a record missing its field or its
        # separator used to raise IndexError here -- a traceback, before the check below could report
        # which selection was missing
        parts = s.split(',')
        files = files + [parts[0]]
        headers = headers + [parts[1] if len(parts) > 1 else '']
        tempHeaders=str(headers[i])
        i = i + 1
        if ' ' in tempHeaders: # avoid a query error later for a multi-word header
            tempHeaders = "`" + tempHeaders + "`"
            headers = [tempHeaders]
        if i == 1:
            sep = parts[2] if len(parts) > 2 else ''

    if not check_fields_selected(headers, 'CONCATENATE'):
        return ''

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
    df_concat.to_csv(outputFilename, header=[listToString(headers, sep)],encoding='utf-8', index=False)
    return outputFilename

# EXTRACT/EXPORT csv/txt ---------------------------------------------------------------------------------------------

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
        df_extract.to_csv(outputFilename, encoding='utf-8', index=False)
    else: # .txt
        text = df_extract.to_csv(encoding='utf-8', index=False)
        text = text.replace(",", " ")
        with open(outputFilename, "w", encoding='utf-8', errors='ignore', newline='') as text_file:
            text_file.write(text)
    return outputFilename


# MERGE ------------------------------------------------------------------------------------------

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


def MERGE(outputDir, operation_results_text_list):
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
        df1 = pd.read_csv(csv_lst[0], encoding='utf-8', on_bad_lines='skip')
        df2 = pd.read_csv(csv_lst[1], encoding='utf-8', on_bad_lines='skip')
        df = pd.merge(df1, df2, on=param_lst, how='inner', suffixes=('', '_'))
        df = drop_suffixCol(df)
        if (size > 2):
            for i in range(2, size):
                tdf = pd.read_csv(csv_lst[i], encoding='utf-8', on_bad_lines='skip')
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

    df.to_csv(outputFilename, encoding='utf-8', index=False)

    return outputFilename

# DROP rows ------------------------------------------------------------------------------------------
# https://www.geeksforgeeks.org/drop-rows-from-the-dataframe-based-on-certain-condition-applied-on-a-column/

# each entry: filepath,field,comparator,where_value,and_or  (same record format as EXTRACT).
# DROP removes the rows that MATCH the WHERE condition(s), keeping all columns.
def drop(outputDir, operation_results_text_list):
    if len(operation_results_text_list) == 0:
        mb.showwarning(title='Missing field(s)',
                       message='No field/condition has been selected for the DROP operation.\n\nPlease, select a field, a comparator, and a WHERE value, then try again.')
        return
    filepath = operation_results_text_list[0].split(',')[0]
    df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip')
    queryStr = ''
    prev_and_or = 'and'
    for s in operation_results_text_list:
        parts = s.split(',')
        header = parts[1]
        sign = parts[2] if len(parts) > 2 else "''"
        value = parts[3] if len(parts) > 3 else "''"
        and_or = parts[4] if len(parts) > 4 else "''"
        if sign == "''" or value == "''":
            continue
        if sign == '=':
            sign = '=='
        if sign == '<>':
            sign = '!='
        if ' ' in header:
            header = '`' + header + '`'
        if "'" not in value and not value.isdigit():
            value = "'" + value + "'"
        cond = header + sign + value
        if queryStr == '':
            queryStr = cond
        else:
            conj = prev_and_or if prev_and_or in ('and', 'or') else 'and'
            queryStr = queryStr + ' ' + conj + ' ' + cond
        prev_and_or = and_or
    if queryStr == '':
        mb.showwarning(title='Missing condition',
                       message='The DROP operation requires a WHERE condition (a field, a comparator, and a value).\n\nPlease, enter a condition and try again.')
        return
    matching = df.query(queryStr, engine='python')
    df_result = df.drop(matching.index)
    outputFilename = IO_files_util.generate_output_file_name(filepath, os.path.dirname(filepath),
                                                             outputDir, '.csv', 'drop',
                                                             '', '', '', '', False, True)
    df_result.to_csv(outputFilename, encoding='utf-8', index=False)
    return outputFilename


# SPLIT field ------------------------------------------------------------------------------------------
# the inverse of CONCATENATE. entry: filepath,field,separator.
# Splits one field into several new columns (field_1, field_2, ...) at the separator; keeps the original.
def split_field(outputDir, operation_results_text_list):
    if len(operation_results_text_list) == 0:
        mb.showwarning(title='Missing field',
                       message='No field has been selected for the SPLIT operation.\n\nPlease, select a field and a character separator, then try again.')
        return
    parts = operation_results_text_list[0].split(',')
    filepath = parts[0]
    field = parts[1]
    separator = parts[2] if len(parts) > 2 else ''
    if separator == '':
        mb.showwarning(title='Missing separator',
                       message='The SPLIT operation requires a character separator.\n\nPlease, enter the separator and try again.')
        return
    df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip')
    if field not in df.columns:
        mb.showwarning(title='Field error', message='Field "' + field + '" was not found in the input file.')
        return
    pieces = df[field].astype(str).apply(lambda x: x.split(separator))
    max_parts = int(pieces.map(len).max()) if len(pieces) else 0
    for k in range(max_parts):
        df[field + '_' + str(k + 1)] = pieces.map(lambda p, k=k: p[k] if k < len(p) else '')
    outputFilename = IO_files_util.generate_output_file_name(filepath, os.path.dirname(filepath),
                                                             outputDir, '.csv', 'split',
                                                             '', '', '', '', False, True)
    df.to_csv(outputFilename, encoding='utf-8', index=False)
    return outputFilename


# SORT rows ------------------------------------------------------------------------------------------
# entries: filepath,field (one per sort key). Sorts ascending by the selected field(s).
def sort_rows(outputDir, operation_results_text_list):
    if len(operation_results_text_list) == 0:
        mb.showwarning(title='Missing field',
                       message='No field has been selected for the SORT operation.\n\nPlease, select at least one field and try again.')
        return
    filepath = operation_results_text_list[0].split(',')[0]
    fields = [s.split(',')[1] for s in operation_results_text_list if s.split(',')[1] != '']
    if not fields:
        mb.showwarning(title='Missing field', message='The SORT operation requires at least one field.')
        return
    df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip')
    missing = [f for f in fields if f not in df.columns]
    if missing:
        mb.showwarning(title='Field error', message='Field(s) not found in the input file: ' + ', '.join(missing))
        return
    df = df.sort_values(by=fields, ascending=True, kind='stable')
    outputFilename = IO_files_util.generate_output_file_name(filepath, os.path.dirname(filepath),
                                                             outputDir, '.csv', 'sort',
                                                             '', '', '', '', False, True)
    df.to_csv(outputFilename, encoding='utf-8', index=False)
    return outputFilename


# DEDUPLICATE rows -----------------------------------------------------------------------------------
# entries: filepath,field (0+ key fields). With key field(s), duplicates are judged on those; with none, on the whole row.
def deduplicate(outputDir, operation_results_text_list):
    if len(operation_results_text_list) == 0:
        mb.showwarning(title='Missing input',
                       message='Nothing has been selected for the DEDUPLICATE operation.\n\nPlease, click OK (optionally after selecting one or more key fields) and try again.')
        return
    filepath = operation_results_text_list[0].split(',')[0]
    fields = [s.split(',')[1] for s in operation_results_text_list if s.split(',')[1] != '']
    df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip')
    if fields:
        missing = [f for f in fields if f not in df.columns]
        if missing:
            mb.showwarning(title='Field error', message='Field(s) not found in the input file: ' + ', '.join(missing))
            return
        df = df.drop_duplicates(subset=fields)
    else:
        df = df.drop_duplicates()
    outputFilename = IO_files_util.generate_output_file_name(filepath, os.path.dirname(filepath),
                                                             outputDir, '.csv', 'deduplicate',
                                                             '', '', '', '', False, True)
    df.to_csv(outputFilename, encoding='utf-8', index=False)
    return outputFilename


# RENAME field ---------------------------------------------------------------------------------------
# entry: filepath,field,new_name  (the new name is taken from the Character separator box in the GUI).
def rename_field(outputDir, operation_results_text_list):
    if len(operation_results_text_list) == 0:
        mb.showwarning(title='Missing field',
                       message='No field has been selected for the RENAME operation.\n\nPlease, select a field, enter the new name in the separator box, and try again.')
        return
    parts = operation_results_text_list[0].split(',')
    filepath = parts[0]
    field = parts[1]
    new_name = parts[2] if len(parts) > 2 else ''
    if new_name == '':
        mb.showwarning(title='Missing new name',
                       message='The RENAME operation requires a new field name.\n\nPlease, type the new name in the Character separator box and try again.')
        return
    df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip')
    if field not in df.columns:
        mb.showwarning(title='Field error', message='Field "' + field + '" was not found in the input file.')
        return
    df = df.rename(columns={field: new_name})
    outputFilename = IO_files_util.generate_output_file_name(filepath, os.path.dirname(filepath),
                                                             outputDir, '.csv', 'rename',
                                                             '', '', '', '', False, True)
    df.to_csv(outputFilename, encoding='utf-8', index=False)
    return outputFilename
