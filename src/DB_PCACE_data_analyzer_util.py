# Anna (Qinchen) Ruan originally wrote the code
# Taeeun Kim Fall 2025 heavily edited the code generalizing functions and moving away from hard coded setup values so as to use the code across different databases
# Aiden Summer 2025 improved loading of different databases using pickle files, fixed SVO extractor, and continued to generalize the code across different databases
# RF added all visuals

import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "DB_PC-ACE_data_analyzer_main.py", ['os', 'tkinter','pandas','numpy'])==False:
    sys.exit(0)

# NEVER USED
def safe_pandas_call(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            # Handle error as needed
    return wrapper

import pandas as pd
import os
import tkinter.messagebox as mb

import IO_files_util

# RUN section ______________________________________________________________________________________________________________________________________________________

## OK Pass test of import PCACE
def import_PCACE_tables(inputDir, outputDir):
    dirSearch = os.listdir(inputDir)
    tableList = []

    # for file in dirSearch:
    for file in dirSearch:
        # Only include .xlsx files from the input dir
        if (file.startswith('data_') or file.startswith('setup_') or file.startswith('utility_')) and (file.endswith('.xlsx')):
            # Strip off the .xlsx extension
            # tableList.append(file[:len(file) - 4])
            if not file in str(tableList):
                if file=='data_Complex.xlsx':
                    print('')
                print(file)
                tableList.append(file)
    # if len(tableList) == 0:
    #     mb.showwarning(title='Warning',
    #                    message='There are no xlsx files in the input directory.\n\nThe script expects a set of xlsx files with overlapping ID fields across files in order to construct an SQLite relational database.\n\nPlease, select an input directory that contains 18 xlsx PC-ACE tables and try again.')
    if not "data_Document.xlsx" in str(tableList) and not "data_Complex.xlsx" in str(tableList):
        # mb.showwarning(title='Warning',
        #                message='Although the input directory does contain xlsx files, these files do not have the expected PC-ACE filename (e.g., data_Document, data_Complex).\n\nPlease, select an input directory that contains xlsx PC-ACE tables and try again.')
        tableList=[]
    else:
        # load_lib(inputDir)
        build_libraries(inputDir, outputDir)
    return tableList


reading_list = [
    ('setup_Complex.xlsx', {'ID':'ID_setup_complex'}),
    ('setup_Simplex.xlsx', {'ID':'ID_setup_simplex'}),
    ('setup_xref_Complex-Complex.xlsx', {'ID':'ID_setup_xref_complex-complex'}),
    ('setup_xref_Simplex-Complex.xlsx', {'ID':'ID_setup_xref_complex-complex', 'Complex':'ID_setup_complex', 'Simplex':'ID_setup_simplex'}),
    ('data_Complex.xlsx', {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"}),
    ('data_Simplex.xlsx', {"ID":"ID_data_simplex", "SimplexType":"ID_setup_simplex", "refValue":"ID_data_date_number_text"}),
    ('data_SimplexText.xlsx', {"ID":"ID_data_date_number_text"}),
    ('data_SimplexNumber.xlsx', {"ID":"ID_data_date_number_text"}),
    ('data_SimplexDate.xlsx', {"ID":"ID_data_date_number_text"}),
    ('data_xref_Simplex-Complex.xlsx', {'ID':'ID_data_xref_simplex_complex', 'xrefID':'ID_setup_xref_simplex_complex', 'Simplex':'ID_data_simplex', 'Complex':'ID_data_complex'}),
    ('data_xref_Complex-Complex.xlsx', {'ID':'ID_data_xref_complex-complex', 'HigherComplex':'ID_data_complex', 'xrefID':'ID_setup_xref_complex_complex', 'LowerComplex':'ID_data_complex.1'}),
    ('data_xref_Complex-Document.xlsx', {}),
    ('data_xref_comment-complex.xlsx', {}),
    ('data_xref_Comment-Document.xlsx', {}),
    ('data_xref_VComment.xlsx', {}),
    ('data_xref_VComment-Document.xlsx', {}),
    ('utility_Security.xlsx', {})
]

library = {}

def check_missing(fileName):
    if os.path.isfile(fileName):
        # fileName_lib = pd.DataFrame(pd.read_excel(fileName))
        fileName_lib = pd.read_excel(fileName)
        return fileName_lib
    else:
        mb.showwarning(title='Warning',
                    message='The table ' + fileName + ' is missing.\n\nPlease, make sure to export this table from PC-ACE data backend and try again.')
        # create an empty dataframe
        return pd.DataFrame()

def create_pkl_file(inputDir, filename):
    df = check_missing(os.path.join(inputDir, filename+'.xlsx'))
    if df.empty:
        library[filename] = {}
    else:
        library[filename] = df
        save = f"{filename}.pkl"
        df.to_pickle(str(inputDir) + "/" + str(save))
    return df
def load_lib(inputDir):

    import IO_user_interface_util
    inputDocs = IO_files_util.getFileList('',inputDir, fileType='.xlsx', silent=True)
    nDocs = len(inputDocs)

    head, tail = os.path.split(inputDir)

    if os.path.exists(f"{inputDir}/{'setup_Complex'}.pkl"):
        timing = 2000
        IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Loading PC-ACE database...', 'Loading ' + str(
            nDocs) + ' pkl files from PC-ACE database ' + tail + '\n\nPlease, be patient.',
                                           False, '', True, '', False)
    else:
        timing = 5000
        IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Loading PC-ACE database...', 'Loading ' + str(
            nDocs) + ' xlsx files from PC-ACE database ' + tail + '\n\nPlease, be patient. Depending on database size this may take several minutes.\n\nThe algorithm will create a set of pkl files that will make loading MUCH faster in the future.',
                                           False, '', True, '', False)

    print('InputDir', inputDir)
    i = 0
    NumTables = len(reading_list)
    # current_path = os.getcwd()
    for filename, rename_columns in reading_list:
        parts = filename.split(".")
        name = parts[0]

        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[filename] = df
            print(library[filename])
            i = i+1
            print('  Filename ' + str(i) + '/' + str(NumTables), filename)
        else:
            i = i + 1
            print('  Filename ' + str(i) + '/' + str(NumTables), filename)
            df = check_missing(os.path.join(inputDir, filename))
            if df.empty:
                library[filename] = {}
            else:
                if rename_columns:
                    df.rename(columns=rename_columns, inplace=True)
                library[filename] = df
                save = f"{name}.pkl"
                df.to_pickle(str(inputDir) + "/" + str(save))

    return


def export_df_to_csv(df, inputDir, outputDir, label):
    output_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                               label)
    df.to_csv(output_file_name, encoding='utf-8', index=False)


def build_libraries(inputDir, outputDir):
    global setup_Complex_lib, setup_Simplex_lib, setup_xref_Complex_Complex_lib, crossref, setup_xref_Simplex_Complex_lib, data_Simplex_lib, data_SimplexText_lib, data_SimplexNumber_lib, data_SimplexDate_lib, data_Complex_lib, data_xref_Complex_Complex_lib, data_xref_Simplex_Complex_lib, data_xref_Document_lib, data_xref_Complex_Document_lib, data_xref_comment_complex_lib, data_xref_Comment_Document_lib, data_xref_VComment_lib, data_xref_VComment_Document_lib, utility_Security_lib, xref_simplex_complex_ALL

    if os.path.exists(f"{inputDir}/{'setup_Complex'}.pkl"):
        name='setup_Complex'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library['setup_Complex.xlsx'] = df
            setup_Complex_lib = library['setup_Complex.xlsx']
        else:
            setup_Complex_lib = create_pkl_file(inputDir, name)

        name='setup_Simplex'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            setup_Simplex_lib = library['setup_Simplex.xlsx']
        else:
            setup_Simplex_lib = create_pkl_file(inputDir, name)

        name='setup_xref_Complex-Complex'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            setup_xref_Complex_Complex_lib = library['setup_xref_Complex-Complex.xlsx']
        else:
            setup_xref_Complex_Complex_lib = create_pkl_file(inputDir, name)
        # only keep required complex objects
        crossref = setup_xref_Complex_Complex_lib[['Required', 'Name']]

        name='setup_xref_Simplex-Complex'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            setup_xref_Simplex_Complex_lib = library['setup_xref_Simplex-Complex.xlsx']
        else:
            setup_xref_Simplex_Complex_lib = create_pkl_file(inputDir, name)

        name='data_Simplex'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            data_Simplex_lib = library['data_Simplex.xlsx']
        else:
            data_Simplex_lib = create_pkl_file(inputDir, name)


        name='data_SimplexText'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            data_SimplexText_lib = library['data_SimplexText.xlsx']
        else:
            data_SimplexText_lib = create_pkl_file(inputDir, name)


        name='data_SimplexNumber'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            data_SimplexNumber_lib = library['data_SimplexNumber.xlsx']
        else:
            data_SimplexNumber_lib = create_pkl_file(inputDir, name)

        name='data_SimplexDate'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            data_SimplexDate_lib = library['data_SimplexDate.xlsx']
        else:
            data_SimplexDate_lib = create_pkl_file(inputDir, name)

        name='data_Complex'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            data_Complex_lib = library['data_Complex.xlsx']
        else:
            data_Complex_lib = create_pkl_file(inputDir, name)

        name='data_xref_Complex-Complex'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            data_xref_Complex_Complex_lib = library['data_xref_Complex-Complex.xlsx']
        else:
            data_xref_Complex_Complex_lib = create_pkl_file(inputDir, name)

        name='data_xref_Simplex-Complex'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            data_xref_Simplex_Complex_lib = library['data_xref_Simplex-Complex.xlsx']
        else:
            data_xref_Simplex_Complex_lib = create_pkl_file(inputDir, name)

        name='data_xref_Complex-Document'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            data_xref_Complex_Document_lib = library['data_xref_Complex-Document.xlsx']
        else:
            data_xref_Complex_Document_lib = create_pkl_file(inputDir, name)

        name='data_xref_comment-complex'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            data_xref_comment_complex_lib = library['data_xref_comment-complex.xlsx']
        else:
            data_xref_comment_complex_lib = create_pkl_file(inputDir, name)

        name='data_xref_Comment-Document'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            data_xref_Comment_Document_lib = library['data_xref_Comment-Document.xlsx']
        else:
            data_xref_Comment_Document_lib = create_pkl_file(inputDir, name)

        name='data_xref_VComment'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            data_xref_VComment_lib = library['data_xref_VComment.xlsx']
        else:
            data_xref_VComment_lib = create_pkl_file(inputDir, name)

        name='data_xref_VComment-Document'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            data_xref_VComment_Document_lib = library['data_xref_VComment-Document.xlsx']
        else:
            data_xref_VComment_Document_lib = create_pkl_file(inputDir, name)

        name='utility_Security'
        if os.path.exists(f"{inputDir}/{name}.pkl"):
            df = pd.read_pickle(f"{inputDir}/{name}.pkl")
            library[name+'.xlsx'] = df
            utility_Security_lib = library['utility_Security.xlsx']
        else:
            utility_Security_lib = create_pkl_file(inputDir, name)

        xref_simplex_complex_ALL = get_xref_simplex_complex_data_setup_IDs_simplex_values(inputDir, outputDir)

        export_df_to_csv(xref_simplex_complex_ALL, inputDir, outputDir, "complex")
        print('Done importing libraries...')

# check if a required document can be found.
# OK pass checks and returns a dataframe or a boolean set to False if the file is not found.

def view_grammar(excel_file, column_name, output_file):
    """
    exports the contents from a specific excel file to a txt
    - excel_file (str): grammar_path to the Excel file.
    - column_name (str): Name of the column to read.
    - output_file (str): grammar_path to the output text file.
    """
    try:
        df = pd.read_excel(excel_file)

        column_data = df[column_name].dropna().astype(str)

        #replacing extra '_x00D_' strings that appear
        column_data = column_data.str.replace('_x000D_', '', regex=False)

        with open(output_file, 'w', encoding='utf-8') as f:
            for i,row in enumerate(column_data, start=1):
                f.write(f"{i}.    {row}\n")

        IO_files_util.openFile('', output_file)
    except Exception as e:
         print(f"An error occurred: {e}")

def get_complex_simplex_names():
    try:
        if setup_Complex_lib is not None and setup_Simplex_lib is not None:
            return setup_Complex_lib["Name"].dropna().sort_values().tolist(), setup_Simplex_lib["Name"].dropna().sort_values().tolist()
    except:
        return [], []


# helper method for get_Simplex_text_date_number
# convert the column named 'Value' into list type
def get_all_Simplex(data):
    return data['Value'].dropna().tolist()

# depend on users' choice, get a list of all value in data_SimplexText, data_SimplexDate or data_SimplexNumber
# Pass test 2023 / 09 / 22
def get_Simplex_text_date_number(simplex_type):
    if simplex_type=='':
        return []
    data_files = {
        'text': data_SimplexText_lib,
        'date': data_SimplexDate_lib,
        'number': data_SimplexNumber_lib
    }
    if simplex_type not in data_files:
        return []
    file_path = data_files[simplex_type]
    # if not(isinstance(file_path, str) and os.path.isfile(file_path)):
    #     return []

    data_lib = library.get(f'data_Simplex{simplex_type.capitalize()}.xlsx')
    if data_lib is None:
        return []

    list_simplex_data = data_lib[data_lib['Value'].notna()]['Value'].tolist()
    if simplex_type == 'number':
        list_simplex_data = [int(num) if isinstance(num, float) and num.is_integer() else num for num in list_simplex_data]
    if list_simplex_data and all(isinstance(item, type(list_simplex_data[0])) for item in list_simplex_data):
        list_simplex_data.sort()

    return list_simplex_data

# get data for the input simplex name
# parameter: name: simplex name in str type
# return: dataframe: name, value, frequency
def get_simplex_frequencies(name, inputDir, outputDir, compute_frequencies=True):
    if any(df is None or df.empty for df in [setup_Simplex_lib, data_Simplex_lib, data_xref_Simplex_Complex_lib]):
        return None

    # name must be a list
    if isinstance(name, str):
        name = [name]

    simplex_id = get_simplex_setup_id(name)
    id, name = simplex_id.iloc[0]

    merged_data = pd.merge(data_xref_Simplex_Complex_lib, data_Simplex_lib, how = 'left', on = 'ID_data_simplex')
    # filter the dataframe by the selected simplex
    filtered_simplex = merged_data[merged_data['ID_setup_simplex']==id][['ID_data_simplex', 'ID_data_complex']]

    simplex_data_combined = pd.merge(data_Simplex_lib, data_SimplexText_lib, how='left', on='ID_data_date_number_text')[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    if compute_frequencies:
        count = filtered_simplex.groupby(['ID_data_simplex']).size().reset_index(name='Frequency')
        result = pd.merge(count, simplex_data_combined, how = 'left', on = 'ID_data_simplex')
        result = result.rename(columns={'Value': name}).sort_values(by='Frequency', ascending=False)
        # TODO Anna: The first column should have a header "Name of Simplex Object"
        simplex_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                           name+'_simplex_freq')
    else:
        #list all simplex values
        result = pd.merge(filtered_simplex, simplex_data_combined, how = 'left', on = 'ID_data_simplex')
        simplex_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                           name+'_simplex_list')
    result.to_csv(simplex_file_name, encoding='utf-8', index=False)
    return simplex_file_name # this can be a file of simplex frequencies or simplex list


# Creates csv file with frequencies of complex associations for each simplex.
# return: grammar_path to generated csv or None if data is missing
def get_simplex_frequencies_all(inputDir, outputDir):
    if any(df is None or df.empty for df in [setup_Simplex_lib, data_Simplex_lib, data_xref_Simplex_Complex_lib]):
        return None

    list_simplex_name = setup_Simplex_lib['Name'].dropna().tolist()
    merged_data = pd.merge(data_xref_Simplex_Complex_lib, data_Simplex_lib, how='left', on='ID_data_simplex')

    all_rows=[]
    for name in list_simplex_name:
        simplex_info = get_simplex_setup_id([name])
        simplex_id = simplex_info.iloc[0,0]

        filtered_data = merged_data[merged_data['ID_setup_simplex'] == simplex_id]
        all_rows.append([name, len(filtered_data)])

    count_lib = pd.DataFrame(all_rows, columns=['name', 'frequency'])

    output_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'all_simplex_freq')
    count_lib.to_csv(output_file_name, encoding='utf-8', index=False)

    return output_file_name


# @@@
# given a complex name selected in _main, the function returns an output file containing a set of information about the complex
#   e.g., identifier, simplex values
def get_complex(complex_name, comment_info, document_info, inputDir, outputDir):
    global dfs_df
    dfs_df = pd.DataFrame()
    append_rows = dfs(complex_name)
    new_rows_df = pd.DataFrame(append_rows)
    dfs_df = pd.concat([dfs_df, new_rows_df], ignore_index=True)

    # @@@@@ Aiden question temporarily disconnected
    dfs_df = add_path_info_to_complex_object(complex_name, dfs_df)

    if document_info:
        dfs_df = add_document_info(dfs_df)

    if comment_info!='':
        dfs_df = add_comment_info(dfs_df, complex_name, comment_info)

    complex_object_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'Complex object')
    dfs_df.to_csv(complex_object_file_name, encoding='utf-8', index=False)

    return complex_object_file_name

def get_complex_frequencies(name, inputDir, outputDir):

    if any(df is None or df.empty for df in [setup_Complex_lib, data_Complex_lib, data_xref_Complex_Complex_lib]):
        return None

    if isinstance(name, str):
            name = [name]

    # Find the complex ID and name
    complex_info = get_complex_setup_id(name)
    complex_id, name = complex_info.iloc[0]

    # Merge DataFrames to get the relevant data
    merged_data = pd.merge(data_xref_Complex_Complex_lib, data_Complex_lib, how = 'left', on = 'ID_data_complex')
    select = merged_data[merged_data['ID_setup_complex'] == complex_id]

    # Group and count the frequencies
    count = select.groupby('ID_data_complex.1').size().reset_index(name='Frequency')
    result = pd.merge(count, data_Complex_lib, how = 'left', left_on = 'ID_data_complex.1', right_on = 'ID_data_complex')

    result = result[['Identifier', 'Frequency']].rename(columns={'Identifier': name}).sort_values(by='Frequency', ascending=False)
    complex_frequency_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'complex_freq')
    result.to_csv(complex_frequency_file_name, encoding='utf-8', index=False)

    return complex_frequency_file_name

# pass test, Sep 22, 2023
def get_complex_frequencies_all(inputDir, outputDir):

    if any(df is None or df.empty for df in [setup_Complex_lib, data_xref_Complex_Complex_lib, data_Complex_lib]):
        return None

    list_complex_name = setup_Complex_lib['Name'].dropna().tolist()
    merged_data = pd.merge(data_xref_Complex_Complex_lib, data_Complex_lib, how='left', on='ID_data_complex')

    all_rows = []
    for name in list_complex_name:
        complex_info = get_complex_setup_id([name])
        complex_id = complex_info.iat[0,0]

        select = merged_data[merged_data['ID_setup_complex'] == complex_id]
        all_rows.append([name, len(select)])

    count = pd.DataFrame(all_rows, columns=['name', 'frequency'])

    all_complex_frequency_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'all_complex_freq')
    count.to_csv(all_complex_frequency_file_name, encoding='utf-8', index=False)

    return all_complex_frequency_file_name


# find the id of the input complex (name)
# parameter: name of a complex in list type (e.g., [, dataframe of setup_Complex
# return: a dataframe: id, name of the input complex
def get_complex_setup_id(complex_name):
    if isinstance(complex_name, str):
        complex_name = [complex_name]
    data = setup_Complex_lib[setup_Complex_lib['Name'].isin(complex_name)]
    data = data[['ID_setup_complex', 'Name']]
    data['ID_setup_complex'] = [int(x) for x in data['ID_setup_complex']]
    return data

def get_complex_data_id(complex_name):
    if isinstance(complex_name, str):
        complex_name = [complex_name]
    data = setup_Complex_lib[setup_Complex_lib['Name'].isin(complex_name)]
    data = data[['ID_setup_complex', 'Name']]
    data['ID_setup_complex'] = [int(x) for x in data['ID_setup_complex']]
    return data

# @@@@@@ Useful function
# given a complex data ID value, returns its setup ID and name
def get_complex_setup_id_from_data_id(complex_data_id):
    ID_setup_complex = data_Complex_lib[data_Complex_lib['ID_data_complex'] == complex_data_id]['ID_setup_complex'].iloc[0]
    complex_name = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'] == ID_setup_complex]['Name'].iloc[0]
    return ID_setup_complex, complex_name

# @@@@@
# given a df with a column of IDs of data complex (ID_data_complex), returns a df of all complex setup IDs and names

# @@@@@@ Useful function

# def get_complex_setup_id_from_data_id_ALL(df):
#     # get setup IDs from data complex IDs
#     df = pd.merge(df, data_Complex_lib, how='left', left_on='ID_data_complex', right_on='ID_data_complex')
#     # get the setup complex name
#     df = pd.merge(df, setup_Complex_lib, how='left', left_on='ID_setup_complex', right_on='ID_setup_complex')
#     df = df.rename(columns={'Name': "Complex name"})
#     # drop the grammar column which creates a very messy output csv file
#     df = df.drop("GrammarRule_Text", axis=1)
#
#     return df

def get_complex_setup_id_from_data_id_ALL(inputDir, outputDir):
    # get setup IDs from data complex IDs
    df = pd.merge(data_Complex_lib, data_xref_Complex_Complex_lib, how='left', left_on='ID_data_complex', right_on='HigherComplex')
    # get the setup complex name
    df = pd.merge(df, setup_xref_Complex_Complex_lib, how='left', left_on='ID_setup_complex', right_on='ID_setup_xref_complex-complex')
    df = df.rename(columns={'Name': "Complex name"})
    # drop the grammar column which creates a very messy output csv file
    # df = df.drop("GrammarRule_Text", axis=1)

    export_df_to_csv(df, inputDir, outputDir, "ALL")

    return df

def get_simplex_setup_id(simplex_name):
    if isinstance(simplex_name, str):
        complex_name = [simplex_name]
    data = setup_Simplex_lib[setup_Simplex_lib['Name'].isin(simplex_name)]
    data = data[['ID_setup_simplex', 'Name']]
    data['ID_setup_simplex'] = [int(x) for x in data['ID_setup_simplex']]
    return data

# find the related names of simplexes to the input complex(es)
# parameter:
#   complexes: names of complexes in list type
#   setup_Complex, setup_xref_Simplex_Complex
# return: related names of simplexes and required simplexes in nested list type

# get_simplex_names_for_complex
def get_simplex_names_for_complex(complexes):
    simplexes = []
    simplexes_required = []
    if isinstance(complexes, str):
        complexes = [complexes]

    for c in complexes:
        complex_id = get_complex_setup_id([c])
        if complex_id.empty:
            continue
        complex_id = complex_id.iat[0, 0]
        simplex_children = setup_xref_Simplex_Complex_lib[setup_xref_Simplex_Complex_lib['ID_setup_complex'] == complex_id]
        data1 = simplex_children['Name'].values.tolist()
        print('List of ALL simplex', data1)
        simplexes.append(data1)
        # MUST keep only required simplex
        data2 = simplex_children.loc[simplex_children['Required'] == True, 'Name'].tolist()
        print('List of REQUIRED simplex', data2)
        simplexes_required.append(data2)
    return simplexes, simplexes_required

# find the one level lower complex of the input complex
# parameter: name of complex in string type, inputDir
# return: a list of child complex
def get_child_complex(complex):
    lower_level_complex = []
    has_files = True

    if isinstance(complex, str):
        complex = [complex]

    if setup_Complex_lib.empty or setup_xref_Complex_Complex_lib.empty:
        has_files = False

    if(has_files):
        complex_id = get_complex_setup_id(complex)
        complex_id = complex_id['ID_setup_complex'].values.tolist()
        lower_level_complex = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['HigherComplex'].isin(complex_id)]
        lower_level_complex = lower_level_complex[['LowerComplex', 'Name']]
        lower_level_complex = lower_level_complex['Name'].values.tolist()

    return lower_level_complex


# find the one level higher complex of the input complex
# parameter: name of complex in string type, inputDir
# return: a list of parent complex

# @@ what is the difference with the function get_higher_complex?
def get_parent_complex(complex):

    higher_level_complex = []
    has_files = True

    if isinstance(complex, str):
        complex = [complex]

    if setup_Complex_lib.empty or setup_xref_Complex_Complex_lib.empty:
        has_files = False

    if(has_files):
        complex_id = get_complex_setup_id(complex)
        complex_id = complex_id['ID_setup_complex'].values.tolist()

        higher_level_complex = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['LowerComplex'].isin(complex_id)]
        higher_level_complex = higher_level_complex['HigherComplex'].values.tolist()
        # higher_level_complex = [str(x) for x in higher_level_complex]

        higher_level_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'].isin(higher_level_complex)]
        higher_level_complex = higher_level_complex[['ID_setup_complex', 'Name']]
        higher_level_complex = higher_level_complex.rename(columns={'ID_setup_complex': 'HigherComplex', 'Name': 'Name'})

        higher_level_complex = higher_level_complex['Name'].values.tolist()

    return higher_level_complex

# find the one level upper complex of the input complex
# parameter: name(s) of complex in list type, dataframe of setup_Complex and setup_xref_Complex_Complex
# return: a dataframe: id, name of one level higher complex of the input complex

# @@@ what is the difference with the function get_parent_complex?

def get_higher_complex(complex):
    complex_id = get_complex_setup_id(complex)
    complex_id = complex_id['ID_setup_complex'].values.tolist()

    higher_level_complex = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['LowerComplex'].isin(complex_id)]
    higher_level_complex = higher_level_complex['HigherComplex'].values.tolist()
    higher_level_complex = [str(x) for x in higher_level_complex]

    higher_level_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'].isin(higher_level_complex)]
    higher_level_complex = higher_level_complex[['ID_setup_complex', 'Name']]
    higher_level_complex = higher_level_complex.rename(columns={'ID_setup_complex': 'HigherComplex', 'Name': 'Name'})

    return higher_level_complex



# find the parent of the chosen simplex (corresponding complex)
# parameter: name of simplex in string type, inputDir
# return: a list of parent complex

# NEVER USED
def get_parent_simplex(name):
    higher_level_complex = []
    has_files = True

    if isinstance(name, str):
        name = [name]

    # @@@ Aiden question why not recognized???
    global setup_Complex_lib
    if setup_Complex_lib.empty or setup_Simplex_lib.empty or setup_xref_Simplex_Complex_lib.empty:
        has_files = False

    if(has_files):
        simplex_id = get_simplex_setup_id(name)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

        complex_id = setup_xref_Simplex_Complex_lib[setup_xref_Simplex_Complex_lib['ID_setup_simplex'].isin(simplex_id)]
        complex_id = complex_id['ID_setup_complex'].values.tolist()

        # reset type of 'ID_setup_complex' in setup_Complex.xlsx
        setup_Complex_lib = setup_Complex_lib[setup_Complex_lib['Name'].notna()]
        setup_Complex_lib[['ID_setup_complex']] = setup_Complex_lib[['ID_setup_complex']].astype(int)
        setup_Complex_lib = setup_Complex_lib[['ID_setup_complex', 'Name']]

        higher_level_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'].isin(complex_id)]
        higher_level_complex = higher_level_complex['Name'].values.tolist()

    return higher_level_complex

def get_parent_simplex_util(name):
    simplex_id = get_simplex_setup_id(name)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

    complex_id = setup_xref_Simplex_Complex_lib[setup_xref_Simplex_Complex_lib['ID_setup_simplex'].isin(simplex_id)]
    complex_id = complex_id['ID_setup_complex'].values.tolist()

    # reset type of 'ID_setup_complex' in setup_Complex.xlsx
    setup_Complex = setup_Complex_lib[setup_Complex_lib['Name'].notna()]
    setup_Complex[['ID_setup_complex']] = setup_Complex[['ID_setup_complex']].astype(int)
    setup_Complex = setup_Complex[['ID_setup_complex', 'Name']]

    higher_level_complex = setup_Complex[setup_Complex['ID_setup_complex'].isin(complex_id)]
    higher_level_complex = higher_level_complex['Name'].values.tolist()

    return higher_level_complex


# find the one level lower complex of the input complex
# parameter: name(s) of complex in list type, dataframe of setup_Complex and setup_xref_Complex_Complex
# return: a dataframe: id, name of one level lower complex of the input complex
def get_lower_complex(complex):
    complex_id = get_complex_setup_id(complex)
    complex_id = complex_id['ID_setup_complex'].values.tolist()

    lower_level_complex = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['HigherComplex'].isin(complex_id)]
    lower_level_complex = lower_level_complex[['LowerComplex', 'Name']]

    return lower_level_complex



# give the lowest complex of the give complex
# parameter: name of complex in list type, dataframe of setup_Complex and setup_xref_Complex_Complex
# return: the lowest complex in list type

# NOT USED
def get_lowest_complex(complex_name):
    start = get_lower_complex(complex_name)
    checked_complex = complex_name
    lowest_complex_list = []
    lower(start, lowest_complex_list, checked_complex)
    return lowest_complex_list


# helper method for get_lowest_complex
# to fill lowest_complex_list with the names of complex at the lowest level
# parameter: dataframe returned by get_lower_complex function containing id and name of complex,
#            dataframe of setup_Complex and setup_xref_Complex_Complex
def lower(start, lowest_complex_list, checked_complex):
    start = start['Name'].values.tolist()
    for each in start:
        if each not in checked_complex:
            checked_complex.append(each)
            temp = get_lower_complex([each])
            if len(temp) == 0:
                lowest_complex_list.append(each)
            else:
                lower(temp, lowest_complex_list, checked_complex)

# find the grammar_path between complex objects in the setup grammar
# parameter: name of complex1 at higher level, name of complex2 at lower level
#            dataframe of setup_Complex and setup_xref_Complex_Complex
# return: the list of two complex and the complex in the grammar_path
def get_grammar_path(complex1, complex2):
    all_paths = []
    get_connections(complex1, complex2, [complex1], all_paths, set())
    return all_paths


def get_connections(complex1, complex2, current_path, all_paths, visited, depth_limit=10):
    if complex1 == complex2:
        all_paths.append(list(current_path))
        return
    if len(current_path) > depth_limit:  # Prevent overly deep recursion
        return

    visited.add(complex1)
    lower_complexes = get_lower_complex([complex1])
    next_complexes = lower_complexes['Name'].values.tolist()

    for next_complex in next_complexes:
        if next_complex not in visited:
            current_path.append(next_complex)
            get_connections(next_complex, complex2, current_path, all_paths, visited, depth_limit)
            current_path.pop()

    visited.remove(complex1)



# get the data IDs of the highest complex and lowest complex in the grammar_path
# parameter: return of grammar_path function
#            setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex
# return: 2 columns of data IDs of the highest complex and lowest complex in the given grammar_path with xref
#   e.g., if grammar_path contains the values Participant-S, Actor, Individual, it will return the data IDs for Participant-S and Individual

# get complex_data_IDs_in_grammar_path
def complex_data_IDs_in_grammar_path(grammar_path):
    highest_name = grammar_path[0]
    lowest_name = grammar_path[len(grammar_path) - 1]

    higher = highest_name
    higher = get_complex_setup_id([higher])
    higher = higher.iat[0, 0]
    grammar_path = grammar_path[1:]
    xrefs = []
    #3 ->47->49

    #3->49-79
    for each in grammar_path:
        lower = get_complex_setup_id([each])
        lower = lower.iat[0, 0]
        xref = setup_xref_Complex_Complex_lib[(setup_xref_Complex_Complex_lib['HigherComplex'] == higher) & (
                    setup_xref_Complex_Complex_lib['LowerComplex'] == lower)]

        if xref.empty:
            continue
        xref = xref.iat[0, 0]
        higher = lower
        xrefs.append(xref)

    if len(xrefs) == 0:
        print("Returning empty dataframe for :", grammar_path)
        return pd.DataFrame()

    xref = xrefs.pop()
    data = data_xref_Complex_Complex_lib[data_xref_Complex_Complex_lib['ID_setup_xref_complex_complex'] == xref]
    data = data[['ID_data_complex', 'ID_data_complex.1']]
    for each in reversed(xrefs):
        filter = data_xref_Complex_Complex_lib[data_xref_Complex_Complex_lib['ID_setup_xref_complex_complex'] == each]
        filter = filter[['ID_data_complex', 'ID_data_complex.1']]
        data = pd.merge(filter, data, how='right', right_on='ID_data_complex', left_on='ID_data_complex.1')
        data = data[['ID_data_complex_x', 'ID_data_complex.1_y']]
        data = data.rename(columns={'ID_data_complex_x': 'ID_data_complex', 'ID_data_complex.1_y': 'ID_data_complex.1'})

    data = data.rename(columns={'ID_data_complex': highest_name, 'ID_data_complex.1': lowest_name})

    return data


# give identifiers corresponding to the complex data ids
# parameter:
#            data: dataframe with column names = names of complexes and data = complex data id
#            cols: names of complexes that are part of column names of data
#            data_Complex
# return: dataframe of complex data id and identifier
def get_identifier(data, cols):
    for col in cols:
        data = pd.merge(data, data_Complex_lib, how='left', left_on=col, right_on='ID_data_complex')
        data = data.drop('ID_data_complex', axis=1)
        data = data.drop('ID_setup_complex', axis=1)
        index = data.columns.get_loc(col)
        temp = data.pop('Identifier')
        data.insert(index + 1, col + ' Identifier', temp)
        data = data.rename(columns={'Value': col + ' Identifier'})
        print(data)
    return data


# give simplex to the return of the complex data ids
# parameter:
#           data: data: dataframe with column names = names of complexes and data = complex data id
#           cols: names of complexes that are part of column names of data
#           data_xref_Simplex_Complex, data_Simplex, data_SimplexText
# return: adding corresponding simplex to input data dataframe

# NOT USED
def get_simplex_data(data, cols):
    xref_s_c = data_xref_Simplex_Complex_lib[['ID_data_simplex', 'ID_data_complex']]
    data_Simplex_temp = pd.merge(data_Simplex_lib, data_SimplexText_lib, how='left', left_on='ID_data_date_number_text',
                                 right_on='ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'Value']]

    for col in cols:
        data = pd.merge(data, xref_s_c, how='left', left_on=col, right_on='ID_data_complex')
        data = data.drop('ID_data_complex', axis=1)
        data = pd.merge(data, data_Simplex_temp, how='left', left_on='ID_data_simplex', right_on='ID_data_simplex')
        data = data.drop('ID_data_simplex', axis=1)
        index = data.columns.get_loc(col)
        temp = data.pop('Value')
        data.insert(index + 1, col + ' Simplex', temp)
        data = data.rename(columns={'Value': col + ' Simplex'})

    return data


# find related data (simplex & identifier) of the input complex name from the given dataset
# parameter:
#           complex_name: name of complex in list type
#           data_Simplex, data_SimplexText, setup_Complex, data_Complex, data_xref_Simplex_Complex
# return: dataframe containing individual data id, simplex, identifier

# NOT USED
def get_simplex_identifier_one_complextype(complex_name):
    data_Simplex_temp = pd.merge(data_Simplex_lib, data_SimplexText_lib, how='left', left_on='ID_data_date_number_text',
                                 right_on='ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'Value']]

    complex_id = get_complex_setup_id(complex_name).iat[0, 0]
    complex_id = data_Complex_lib[data_Complex_lib['ID_setup_complex'].isin([complex_id])]
    complex_id = complex_id[['ID_data_complex']]
    complex_id = complex_id.rename(columns={'ID_data_complex': complex_name[0]})

    complexes = get_identifier(complex_id, complex_name)
    complexes = get_simplex_data(complexes, complex_name)

    return complexes


# give distribution frequency for the input simplex name
# parameter: name: simplex name in list type
# return: dataframe: name, value, frequency
# duplicate function name

# NOT USED

def dist_1(name):
    simplex_id = get_simplex_setup_id(name)
    id = simplex_id.iat[0,0]
    xref_id = setup_xref_Simplex_Complex_lib[setup_xref_Simplex_Complex_lib['ID_setup_simplex']==id].iat[0,0]
    xref_data = data_xref_Simplex_Complex_lib[data_xref_Simplex_Complex_lib['ID_setup_xref_simplex_complex']==xref_id]
    xref_data = xref_data[['ID_data_simplex', 'ID_data_complex']]
    count = xref_data.groupby(['ID_data_simplex']).count()

    data_Simplex_temp = pd.merge(data_Simplex_lib, data_SimplexText_lib, how = 'left', on = 'ID_data_date_number_text')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]
    count = pd.merge(count, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    count = count[['ID_data_simplex', 'Value', 'ID_data_complex']]

    count = count.rename(columns = {'ID_data_simplex':name[0], 'ID_data_complex':'Frequency'})

    return count


# get identifier version of semantic triplet
# return: dataframe: Semantic triplet data id, S data id, S Identifier, V data id, V Identifier, O data id, O Identifier
def semantic_triplet_complex(semantic_triplet, subject, verb, object):
    if isinstance(semantic_triplet, list):
        semantic_triplet = str(semantic_triplet[0])

    # Semantic triplet ID here @@@
    id = get_complex_setup_id([semantic_triplet]).iat[0,0]

    save = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['HigherComplex'] == id]
    save = save['ID_setup_xref_complex-complex'].values.tolist()
    save = save[:3]

    triplet = data_xref_Complex_Complex_lib[data_xref_Complex_Complex_lib['ID_setup_xref_complex_complex'].isin(save)]
    triplet = triplet.pivot_table(
        index = ['ID_data_complex'],
        columns = 'ID_setup_xref_complex_complex',
        values = 'ID_data_complex.1'
    ).reset_index()
    print('=============================================================================')
    print(triplet.head())
    subject_id = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['Name'] == subject]['ID_setup_xref_complex-complex'].values[0]
    verb_id = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['Name'] == verb]['ID_setup_xref_complex-complex'].values[0]
    object_id = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['Name'] == object]['ID_setup_xref_complex-complex'].values[0]

    triplet = triplet.rename(columns = {'ID_data_complex': semantic_triplet ,subject_id: 'S', verb_id: 'V', object_id: 'O'})

    complexes = ['S', 'V', 'O']

    for i in range(3):
        complex = complexes[i]
        triplet = pd.merge(triplet, data_Complex_lib, how = 'left', left_on = complex, right_on = 'ID_data_complex')
        pop = triplet.pop('Identifier')
        name = complex + ' Identifier'
        triplet.insert((i+1)*2, name, pop)
        triplet = triplet.drop('ID_data_complex', axis = 1)
        triplet = triplet.drop('ID_setup_complex', axis = 1)

    return triplet

# NOT USED
def get_simplex_value(simplex_name, complex_name, xref_simplex_complex_value):
    simplexes_combined = pd.DataFrame()
    simplex_id = get_simplex_setup_id([simplex_name])
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
    xref_simplex_complex_value_new = xref_simplex_complex_value[
        xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_id)]
    simplexes_combined = xref_simplex_complex_value_new
    simplexes_combined = simplexes_combined.rename(columns={'ID_data_complex': complex_name})
    simplexes_combined['Type'] = complex_name
    return simplexes_combined

dfs_df = pd.DataFrame()

def dfs(parent, inputDir='', outputDir=''):
    global dfs_df

    required = crossref.loc[crossref['Name'] == parent, 'Required'].any()
    if not required:
        return []

    simplex_names, simplex_required_names = get_simplex_names_for_complex([parent])
    # @@@@@ Aiden Question, despite being global xref_simplex_complex_ALL is not recognized here
    #   although it is recognized further down
    global xref_simplex_complex_ALL
    if xref_simplex_complex_ALL.empty:
        xref_simplex_complex_ALL = get_xref_simplex_complex_data_setup_IDs_simplex_values(inputDir, outputDir)
    # xref_simplex_complex_ALL = get_xref_simplex_complex_data_setup_IDs_simplex_values()
    parent_id = xref_simplex_complex_ALL.loc[(xref_simplex_complex_ALL["Complex name"] == parent), "ID_data_complex"]
    parent_id = parent_id.reset_index(drop=True)

    try:
        parent_id = parent_id.loc[0]
    except:
        parent_id = "NO_ID_FOUND"
    # check setup_xref_Simplex-Complex.xlsx to see if the simplex is Required and only use the required simplex
    NSimplex = len(simplex_required_names[0])
    if NSimplex >1:
        mb.showwarning(title='Warning',
                       message="The complex object '" + str(parent) + "' contains " + str(NSimplex) + " required simplex objects (" + str(', '.join(simplex_required_names[0])) + "). Only the first simplex object (" + str(simplex_required_names[0][0]) + ") will be used to construct the triplet. Required simplex objects will have priority over any complex object children.\n\nTO CHANGE THE REQUIRED STATE OF ANY OF THESE SIMPLEX OBJECTS, OPEN THE FILE setup_xref_Simplex-Complex.xlsx AND SET THE VALUE OF REQUIRED TO FALSE FOR SELECTED SIMPLEX.")

    if simplex_required_names and len(simplex_required_names[0]) > 0:
        simplex = simplex_required_names[0][0]
        simplex_id = get_simplex_setup_id([simplex])
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

        data_Simplex_temp = pd.merge(
            data_Simplex_lib, data_SimplexText_lib,
            how='left', on='ID_data_date_number_text'
        )[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

        xref_simplex_complex_value = pd.merge(
            data_xref_Simplex_Complex_lib, data_Simplex_temp,
            how='left', on='ID_data_simplex'
        )[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

        simplex_children_values = xref_simplex_complex_value[
            xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_id)
        ]

        if simplex_children_values.empty:
            return []

        # add column headers
        simplex_values = simplex_children_values['Value'].tolist()
        child_rows = []

        # type_id = get_([parent]).iat[0, 0]
        for simplex_value in simplex_values:
            complex_id = xref_simplex_complex_ALL.loc[(xref_simplex_complex_ALL["Complex name"] == parent), "ID_data_complex"]
            complex_id = complex_id.reset_index(drop=True)
            simplex_name = xref_simplex_complex_ALL.loc[(xref_simplex_complex_ALL["Complex name"] == parent) & (xref_simplex_complex_ALL["Value"] == simplex_value), "Simplex name"].values

            try:
                complex_id = complex_id.loc[0]
            except:
                complex_id = "NO_ID_FOUND"
            child_rows.append({
                parent + " ID": complex_id,
                "Complex name": parent,
                "Simplex name": simplex_name,
                "Value": simplex_value,
            })

        return child_rows

    else:
        complex_children = get_lower_complex(parent)
        children = complex_children['Name'].tolist()

        if not children:
            return []

        append_rows = []
        # add column headers
        for child in children:
            child_rows = (dfs(child))
            if child_rows:
                append_rows.extend(child_rows)

        if append_rows:
            append_rows = [{parent + " ID": parent_id, parent: parent, **row} for row in append_rows]

        return append_rows

# @@@@@@
# the function builds a complete dataframe of complex & simplex setup and data IDs & simplex values
# return a complete dataframe (which is always invariant for any database);
#   so there is no need to recompute it once it is computed
def get_xref_simplex_complex_data_setup_IDs_simplex_values(inputDir, outputDir):
    # get ALL simplex text values
    # Aiden these merge only produce DATE values, i.e., the last of the three merges
    data_SimplexText_allValues = pd.merge(data_Simplex_lib, data_SimplexText_lib, how='left',
                                          on='ID_data_date_number_text')

    # data_SimplexText_allValues = pd.merge(data_SimplexText_allValues, data_SimplexNumber_lib, how='left',
    #                                       on='ID_data_date_number_text')
    #
    # data_SimplexText_allValues = pd.merge(data_SimplexText_allValues, data_SimplexDate_lib, how='left',
    #                                       on='ID_data_date_number_text')

    # add the data xref simplex-complex IDs, setup xref simplex-complex IDs, data complex IDs, data simplex IDs, setup simplex IDs, simplex values
    xref_simplex_complex_value = pd.merge(data_xref_Simplex_Complex_lib, data_SimplexText_allValues, how='left',
                                          left_on='ID_data_simplex', right_on='ID_data_simplex')
    # add the simplex setup name
    xref_simplex_complex_value = pd.merge(setup_Simplex_lib, xref_simplex_complex_value, how='left',
                                          left_on='ID_setup_simplex', right_on='ID_setup_simplex')
    # remove the decimals
    # xref_simplex_complex_value["ID_data_xref_simplex-complex"] = xref_simplex_complex_value["ID_data_xref_simplex-complex"].fillna(-1).astype(int)
    # xref_simplex_complex_value["ID_setup_xref_simplex_complex"] = xref_simplex_complex_value["ID_setup_xref_simplex_complex"].fillna(-1).astype(int)
    # xref_simplex_complex_value["ID_data_simplex"] = xref_simplex_complex_value["ID_data_simplex"].fillna(-1).astype(int)
    # xref_simplex_complex_value["ID_data_complex"] = xref_simplex_complex_value["ID_data_complex"].fillna(-1).astype(int)
    # xref_simplex_complex_value["Order"] = xref_simplex_complex_value["Order"].fillna(-1).astype(int)
    # xref_simplex_complex_value["ID_data_date_number_text"] = xref_simplex_complex_value["ID_data_date_number_text"].fillna(-1).astype(int)

    xref_simplex_complex_value = xref_simplex_complex_value.rename(columns={'Name': "Simplex name"})

    # select columns
    xref_simplex_complex_value = xref_simplex_complex_value[
        ['ID_data_complex', 'ID_setup_xref_simplex_complex', 'ID_setup_simplex', 'Simplex name', 'ID_data_simplex', 'Value']]

    export_df_to_csv(xref_simplex_complex_value, inputDir, outputDir, "simplex")

    # add complex setup IDs and Names
    xref_complex_complex_value = get_complex_setup_id_from_data_id_ALL(inputDir, outputDir)
    # select columns
    xref_complex_complex_value = xref_complex_complex_value[
        ['ID_data_complex', 'ID_setup_complex','Complex name', 'Identifier']]

    # merge xref_simplex_complex_value & xref_complex_complex_value
    xref_simplex_complex = pd.merge(xref_complex_complex_value, xref_simplex_complex_value, how='left',
                                          left_on='ID_data_complex', right_on='ID_data_complex')

    # select columns
    xref_simplex_complex = xref_simplex_complex[
        ['ID_setup_complex','Complex name', 'ID_setup_simplex','Simplex name', 'ID_data_complex', 'ID_data_simplex', 'Value']]

    # Aiden export_df_to_csv will have woman as simplex value for Name of individual actor but the complex name is Actor and NOT individual
    #   the last merge above must merge on the wrong values?
    export_df_to_csv(xref_simplex_complex, inputDir, outputDir, "simplex-complex")

    return xref_simplex_complex


def get_simplex_value_for_complex(complex_name, is_verb):

    # check whether Group is 0 or 1a, 1b, 1c,... i.e., whether the complex objects are mutually exclusive
    mutually_exclusive = setup_xref_Complex_Complex_lib[['Group', 'Name']]

    # initialize empty dataframe simplexes_combined
    simplexes_combined = pd.DataFrame()

    # # get a list of all the simplex and complex data IDs, setup IDs, and simplex TEXT values
    if xref_simplex_complex_ALL.empty:
        xref_simplex_complex_value = get_xref_simplex_complex_data_setup_IDs_simplex_values()

    simplex_names, simplex_required_names = get_simplex_names_for_complex([complex_name])

    # check setup_xref_Simplex-Complex.xlsx to see if the simplex is Required and only use the required simplex
    NSimplex = len(simplex_required_names[0])
    if NSimplex >1:
        mb.showwarning(title='Warning',
                       message="The complex object '" + str(complex_name) + "' contains " + str(NSimplex) + " required simplex objects (" + str(', '.join(simplex_required_names[0])) + "). Only the first simplex object (" + str(simplex_required_names[0][0]) + ") will be used to construct the triplet. Required simplex objects will have priority over any complex object children.\n\nTO CHANGE THE REQUIRED STATE OF ANY OF THESE SIMPLEX OBJECTS, OPEN THE FILE setup_xref_Simplex-Complex.xlsx AND SET THE VALUE OF REQUIRED TO FALSE FOR SELECTED SIMPLEX.")

    # for simplex_name in simplex_names[0]:
    #     simplex_id = get_simplex_setup_id([simplex_name], setup_Simplex_lib)
    #     simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
    #     xref_simplex_complex_value_new = xref_simplex_complex_value[
    #     xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_id)]
    #     xref_simplex_complex_value_new = xref_simplex_complex_value_new.rename(columns={'ID_data_complex': subject})
    if len(simplex_required_names[0])>0:
        simplex_id = get_simplex_setup_id([simplex_required_names[0][0]])
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_simplex_complex_value_new = xref_simplex_complex_value[xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_id)]
        simplexes_combined = xref_simplex_complex_value_new
        simplexes_combined = simplexes_combined.rename(columns={'ID_data_complex': complex_name})
        simplexes_combined['Type'] = complex_name
        # @@
    else:
        # get a list of all the simplex names, children of the complex object complex_name
        # get a list of all the simplex values
        if xref_simplex_complex_ALL.empty:
            xref_simplex_complex_value = get_xref_simplex_complex_data_setup_IDs_simplex_values()

        # global dfs_lib
        # dfs_lib = pd.DataFrame(columns=['Parent', 'Children'])
        # dfs(complex_name, crossref)
        # return dfs_lib

        # get as list all the complex children of the initial complex_name
        # @@@
        complex_children = get_lower_complex([complex_name])['Name'].values.tolist()
        # get as dataframe the names of all the complex children of the initial complex_name
        for lower in complex_children:
            simplex_names, simplex_required_names = get_simplex_names_for_complex([lower])
            if len(simplex_required_names[0]) > 0:
                simplex = simplex_required_names[0][0]

                simplex_id = get_simplex_setup_id([simplex])
                simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

                simplex_children_values = xref_simplex_complex_value[
                    xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_id)]
            else:
                complex_children_children = get_lower_complex(lower)
                # mutually_exclusive = setup_xref_Complex_Complex.loc[
                #     setup_xref_Complex_Complex['Name'] == lower, 'Group'].any()
                #
                # if len(simplex_children_values) > 0 and mutually_exclusive:
                #     continue

            # need to check the data value for simplex_required_names
            required = crossref.loc[crossref['Name'] == lower, 'Required'].any()
            if not required:
                continue

        complex_children_children = get_lower_complex(complex_children)
        # get as list the IDs of complex children of complex_name
        complex_children_children_ids = complex_children_children['LowerComplex'].values.tolist()
        # get as dataframe all the simplex names required and not required under all complex_children_children
        simplex_names = setup_xref_Simplex_Complex_lib[setup_xref_Simplex_Complex_lib['ID_setup_complex'].isin(complex_children_children_ids)]
        if len(simplex_names) > 0:
            merged = pd.merge(simplex_names, complex_children_children, left_on = 'ID_setup_complex', right_on='LowerComplex', suffixes=('_simplex_names', '_complex_children_children'))
            unique = merged[["Name_complex_children_children", "Name_simplex_names", "ID_setup_complex"]].drop_duplicates(subset=["ID_setup_complex"])
            # @@@ the term lower_complexes is deceiving since it may include simplex objects
            lower_complexes = dict(zip(unique['Name_complex_children_children'], unique['Name_simplex_names']))

            simplexes = []
            for lower in lower_complexes:
                required = crossref.loc[crossref['Name'] == lower, 'Required'].any()
                mutually_exclusive = setup_xref_Complex_Complex_lib.loc[setup_xref_Complex_Complex_lib['Name'] == lower, 'Group'].any()
                if not required:
                    continue


                simplex = lower_complexes[lower]

                simplex_id = get_simplex_setup_id([simplex])
                simplex_id = simplex_id['ID_setup_simplex'].values.tolist()


                xref_simplex_complex_value_select = xref_simplex_complex_value[xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_id)]

                # the grammar_path contains the rewrite rule for a specific object
                #   e.g., Participant-S --> Actor --> Collective actor
                grammar_path = get_grammar_path(complex_name, lower)
                grammar_path = grammar_path[0]

                # @@@@
                if is_verb:
                    head = grammar_path[0]
                    grammar_path = grammar_path[1:]
                    id_data_list = []
                    for item in grammar_path:
                        grammar_path = [head, item]
                        id_data =complex_data_IDs_in_grammar_path(grammar_path)
                        id_data_list.append(id_data)

                    combined_id_data = pd.concat(id_data_list, ignore_index=True)
                    data = pd.merge(combined_id_data, xref_simplex_complex_value_select, how='left', left_on=lower,
                                    right_on='ID_data_complex')

                    # data = data[data[complex_name].notna()]

                    # data = data.drop_duplicates(subset=[complex_name])
                    # data = data[[complex_name, lower, 'Value']]
                    # data = data.drop(lower, axis=1)
                    # data[['Type']] = lower
                    #
                    # simplexes.append(data)
                else: # NOT a verb
                    id_data =complex_data_IDs_in_grammar_path(grammar_path)

                    data = pd.merge(id_data, xref_simplex_complex_value_select, how = 'left', left_on = lower, right_on = 'ID_data_complex')
                    # data = data[data[complex_name].notna()]
                    data = data.drop_duplicates(subset=[complex_name])

                    # data = data[[complex_name, lower, 'Value']]
                    # data = data.drop(lower, axis = 1)
                    # data[['Type']] = lower
                    #
                    # simplexes.append(data)

                data = data[data[complex_name].notna()]
                data = data[[complex_name, lower, 'Value']]
                data = data.drop(lower, axis = 1)
                data[['Type']] = lower

                simplexes.append(data)

            #If all lower values were not required, add all lower values instead.
            if len(simplexes) == 0:
                for lower in lower_complexes:
                    simplex = lower_complexes[lower]

                    simplex_id = get_simplex_setup_id([simplex])
                    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

                    xref_simplex_complex_value_select = xref_simplex_complex_value[
                        xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_id)]

                    grammar_path = get_grammar_path(complex_name, lower)
                    grammar_path = grammar_path[0]

                    if is_verb:
                        head = grammar_path[0]
                        grammar_path = grammar_path[1:]
                        id_data_list = []
                        for item in grammar_path:
                            grammar_path = [head, item]
                            id_data =complex_data_IDs_in_grammar_path(grammar_path)
                            id_data_list.append(id_data)

                        combined_id_data = pd.concat(id_data_list, ignore_index=True)
                        data = pd.merge(combined_id_data, xref_simplex_complex_value_select, how='left', left_on=lower,
                                        right_on='ID_data_complex')
                        data = data[data[complex_name].notna()]
                        data = data.drop_duplicates(subset=[complex_name])
                        data = data[[complex_name, lower, 'Value']]
                        data = data.drop(lower, axis=1)
                        data[['Type']] = lower

                        simplexes.append(data)
                    else:
                        id_data =complex_data_IDs_in_grammar_path(grammar_path)

                        data = pd.merge(id_data, xref_simplex_complex_value_select, how='left', left_on=lower,
                                        right_on='ID_data_complex')
                        data = data[data[complex_name].notna()]
                        data = data.drop_duplicates(subset=[complex_name])
                        data = data[[complex_name, lower, 'Value']]
                        data = data.drop(lower, axis=1)
                        data[['Type']] = lower

                        simplexes.append(data)

            simplexes_combined = pd.concat(simplexes)

            id_to_identifier = data_Complex_lib.set_index('ID_data_complex')['Identifier']
            simplexes_combined['Identifier'] = simplexes_combined[complex_name].map(id_to_identifier)

        print(simplexes_combined)

    return simplexes_combined


def add_comment_info(df, object_name, comment_info):
    # @@@ Aiden must grab name from df
    object_ID = object_name + ' ID'
    # comments contain _x000D_ should be removed
    if 'Verifiers' in comment_info:
        data_xref_Comment_modified = data_xref_VComment_lib[['Complex', 'Comment', 'UserID', 'VerifierID']]
    else:
        # rename ID_data_complex to Complex
        data_xref_Comment_modified = data_xref_comment_complex_lib.rename(columns={'ID_data_complex': 'Actor ID'})
        data_xref_Comment_modified = data_xref_Comment_modified[[object_ID, 'Comment', 'UserID']]
    df = pd.merge(df, data_xref_Comment_modified, how='left', left_on='Macro Event ID',
                               right_on=object_ID)
    # df = df.drop('Complex', axis=1)

    utility_Security = utility_Security_lib[['ID', 'UserName']]
    utility_Security = utility_Security.rename(columns={'ID': 'UserID'})
    df = pd.merge(df, utility_Security, how='left', left_on='UserID', right_on='UserID')
    user_name = df.pop('UserName')
    userID_idx = df.columns.get_loc('UserID')
    df.insert(userID_idx + 1, 'UserName', user_name)
    if 'Verifiers' in comment_info:
        utility_Security_verifier = utility_Security.rename(columns={'ID': 'VerifierID', 'UserName': 'VerifierName'})
        df = pd.merge(df, utility_Security_verifier, how='left', left_on='VerifierID',
                                   right_on='VerifierID')
        verifier_name = df.pop('VerifierName')
        verifierID_idx = df.columns.get_loc('VerifierID')
        df.insert(verifierID_idx + 1, 'VerifierName', verifier_name)
    return df

def add_document_info(df):
    # @@@ Aiden error
    data_xref_Complex_Document_modified = data_xref_Complex_Document_lib[['ID_data_complex', 'ID_data_document']]
    simplex_version = pd.merge(df, data_xref_Complex_Document_modified, how='left', left_on='Semantic Triplet',
                               right_on='ID_data_complex')
    simplex_version = simplex_version.drop('ID_data_complex', axis=1)
    simplex_version = simplex_version.rename(
        columns={'Macro Event': 'Macro Event ID', 'Event': 'Event ID', 'Semantic Triplet': 'Semantic Triplet ID',
                 'ID_data_document': 'Document ID'})
    return simplex_version

# df is the input dataframe with the object data
# complex_name is the setup string value of the complex object
# return a modified dataframe of input df
def add_path_info_to_complex_object(complex_name, df):

     # S1: find the list of complex names from the top, primary complex value (e.g., Macro event) UP TO the selected complex
    top_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex']==1]['Name'].values[0]
    grammar_path = get_grammar_path(top_complex, complex_name)
    grammar_path = grammar_path[0]

    # Step 3: Map each complex in the grammar_path to its ID
    name_to_id = {
        name: get_complex_setup_id([name])['ID_setup_complex'].values[0]
        for name in grammar_path
    }

    # Step 4: Retrieve and store link IDs and relevant data_xref details
    link_data_frames = []
    for i in range(len(grammar_path) - 1):
        higher_id = name_to_id[grammar_path[i]]
        lower_id = name_to_id[grammar_path[i + 1]]

        # Find setup xref ID for each object in the grammar path
        xref_id = setup_xref_Complex_Complex_lib[
            (setup_xref_Complex_Complex_lib['HigherComplex'] == higher_id) &
            (setup_xref_Complex_Complex_lib['LowerComplex'] == lower_id)
            ]['ID_setup_xref_complex-complex'].values[0]

        # Retrieve and rename relevant data_xref columns
        # @@@@@@ Aiden question wrong fields
        data_xref = data_xref_Complex_Complex_lib[
            data_xref_Complex_Complex_lib['xrefID'] == xref_id # setup x ref ID for complex object
            ][['HigherComplex', 'LowerComplex']].rename(columns={
            'HigherComplex': f'{grammar_path[i]} ID',
            'LowerComplex': f'{grammar_path[i + 1]} ID'
        })

        # data_xref = data_xref_Complex_Complex_lib[
        #     data_xref_Complex_Complex_lib['ID_setup_xref_complex_complex'] == xref_id
        #     ][['ID_data_complex', 'ID_data_complex.1']].rename(columns={
        #     'ID_data_complex': f'{grammar_path[i]} ID',
        #     'ID_data_complex.1': f'{grammar_path[i + 1]} ID'
        # })
        link_data_frames.append(data_xref)

        # Step 5: Merge link data frames into a complete hierarchy while eliminating extra columns
    merged_data = link_data_frames[0]
    for i in range(1, len(link_data_frames)):
        merged_data = pd.merge(merged_data, link_data_frames[i],
                               left_on=f'{grammar_path[i]} ID',
                               right_on=f'{grammar_path[i]} ID',
                               how='right')

    # Step 7: Merge with simplex_version using semantic triplet ID as the key
    #   when calling from get_complex, Semantic Triplet ID should be the parent complex ID
    try:
        df = pd.merge(merged_data, df, how='left', left_on=f'{grammar_path[-1]} ID',
                                   right_on=f'{grammar_path[-1]} ID')
    except:
        df = pd.merge(merged_data, df, how='left', left_on=f'{grammar_path[-1]} ID',
                                   right_on='Semantic Triplet ID')

    # Step 8: Add the top complex identifier by merging with data_Complex
    data_complex_top = data_Complex_lib[['ID_data_complex', 'Identifier']].rename(
        columns={'ID_data_complex': f'{grammar_path[0]} ID', 'Identifier': f'{grammar_path[0]} Identifier'}
    )
    df = pd.merge(df, data_complex_top, how='left', on=f'{grammar_path[0]} ID')

    # Step 9: Reorder to have the top complex identifier and clean up any remaining extraneous columns
    top_complex_identifier = df.pop(f'{grammar_path[0]} Identifier')
    df.insert(1, f'{grammar_path[0]} Identifier', top_complex_identifier)

    # Final output should have only the relevant grammar_path columns and top complex identifier
    print("Final Hierarchy Data with Simplex Version:", df)
    return df

# get the semantic triplet with simplex
# return: dataframe: Semantic triplet data id, S data id, S Type, S Simplex, V data id, V Simplex, O data id, O Type, O Simplex
# p.s. Type = Individual / Organization / Collective actor
def semantic_triplet_simplex(inputDir, subject, verb, object, document_info, comment_info):
    semantic_triplet = get_parent_complex(subject)
    triplet = semantic_triplet_complex(semantic_triplet, subject, verb, object)

    # @@@

    s = get_simplex_value_for_complex(subject, False)

    s = s.rename(columns={'Value': 'Subject (S)', 'Type': 'S Type'})

    # @@@ turn verb False to True!!!
    v = get_simplex_value_for_complex(verb, True)
    v = v.rename(columns={'Value': 'Verb (V)', 'Type': 'V Type'})

    o = get_simplex_value_for_complex(object, False)
    o = o.rename(columns={'Value': 'Object (O)', 'Type': 'O Type'})

    if isinstance(semantic_triplet, list):
        semantic_triplet = str(semantic_triplet[0])

    simplex_version = pd.merge(triplet, s, how = 'left', left_on = 'S', right_on = subject)

    simplex_version = pd.merge(simplex_version, v, how = 'left', left_on = 'V', right_on = verb)
    simplex_version = pd.merge(simplex_version, o, how = 'left', left_on = 'O', right_on = object)

    simplex_version = simplex_version.loc[:, [semantic_triplet, 'S', 'S Identifier', 'S Type', 'Subject (S)', 'V', 'V Identifier','V Type', 'Verb (V)', 'O', 'O Identifier', 'O Type', 'Object (O)']]
    simplex_version = simplex_version.rename(columns = {semantic_triplet:'Semantic Triplet ID','S':'S ID','V':'V ID', 'O':'O ID'})
    id_to_identifier = data_Complex_lib.set_index('ID_data_complex')['Identifier']
    simplex_version['ST Identifier'] = simplex_version['Semantic Triplet ID'].map(id_to_identifier)
    col = simplex_version.pop('ST Identifier')
    target = simplex_version.columns.get_loc('Semantic Triplet ID')
    simplex_version.insert(target+1, 'ST Identifier', col)

    simplex_version = add_path_info_to_complex_object(semantic_triplet, simplex_version)

    if document_info:
        simplex_version = add_document_info(simplex_version)

    if comment_info!='':
        simplex_version = add_comment_info(simplex_version, semantic_triplet, comment_info)

    # S ID V ID O ID
    simplex_version.drop_duplicates(subset=['S ID', 'V ID', 'O ID'], inplace=True)
    return simplex_version


# prepare the function for the use in main
# get the semantic triplet with simplex
# return: dataframe: Semantic triplet data id, S data id, S Type, S Simplex, V data id, V Simplex, O data id, O Type, O Simplex
# p.s. Type = Individual / Orgaization / Collective actor
def semantic_triplet_simplex_main(inputDir, outputDir, macro_event_id, subject, verb, object, comment_info='', document_info=False):

    print('------------------------------------------------------------------------------------------------------------------------')
    print('Subject', subject)
    print('------------------------------------------------------------------------------------------------------------------------')
    print('verb', verb)
    print('------------------------------------------------------------------------------------------------------------------------')
    print('Object', object)

    simplex_version = semantic_triplet_simplex(inputDir, subject, verb, object, document_info, comment_info)

    if macro_event_id != '':
        macro_event_id = int(macro_event_id.split()[0])
        simplex_version = simplex_version[simplex_version['Macro Event ID'] == macro_event_id]

    # if document_info:
    #     simplex_version = simplex_version.drop('Document ID', axis=1)
    #
    # if comment_info == '':
    #     simplex_version = simplex_version.drop(['Comment', 'UserID', 'UserName', 'VerifierID', 'VerifierName'], axis=1)
    # elif comment_info == 'user':
    #     simplex_version = simplex_version.drop(['VerifierID', 'VerifierName'], axis=1)
    # elif comment_info == 'verifier':
    #     simplex_version = simplex_version.drop(['UserID', 'UserName'], axis=1)

    top_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'] == 1]['Name'].values[0]
    semantic_triplet = get_parent_complex(subject)
    if isinstance(semantic_triplet, list):
        semantic_triplet = semantic_triplet[0]
    grammar_path = get_grammar_path(top_complex, semantic_triplet)
    grammar_path = grammar_path[0]
    print(grammar_path)
    existing_columns = [f'{col} ID' for col in grammar_path if f'{col} ID' in simplex_version.columns]
    print('===============================================================================================')
    print(existing_columns)
    if existing_columns:
        simplex_version = simplex_version.sort_values(existing_columns, ascending=True)

    triplet_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'triplet (SVO)')
    simplex_version.to_csv(triplet_file_name, encoding='utf-8', index=False)

    return triplet_file_name

def get_time_simplex(inputDir, outputDir, time_label, subject, verb, object, macro_event_id, comment_info='', document_info=False):

    time = get_time_simplex(inputDir, time_label, subject, verb, object)

    time_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'time')
    time.to_csv(time_file_name, encoding='utf-8', index=False)

    return time_file_name
#
#    if macro_event_id != '':
#        macro_event_id = int(macro_event_id.split()[0])
#        simplex_version = simplex_version[simplex_version['Macro Event ID'] == macro_event_id]


# helper method for semantic_triplet_time
# link simplex of time complex with V
# return: a dataframe: Process = data id of complex Process, Indefinite time of day = data id of simplex Indefinite time of day, Time = text of Indefinite time of day
def get_time_simplex(inputDir, time_label, subject, verb, object, document_info, comment_info):

    simplexes = get_simplex_names_for_complex(time_label)
    simplex_id = get_simplex_setup_id(simplexes[0])
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
    data_Simplex_temp = pd.merge(data_Simplex_lib, data_SimplexText_lib, how = 'left', on = 'ID_data_date_number_text')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]
    xref_simplex_complex_value = pd.merge(data_xref_Simplex_Complex_lib, data_Simplex_temp, how = 'left', on = 'ID_data_simplex')
    xref_simplex_complex_value = xref_simplex_complex_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]
    xref_simplex_complex_value = xref_simplex_complex_value[xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_id)]
    all_path = get_grammar_path(verb, time_label)

    data = pd.DataFrame()
    for grammar_path in all_path:
        id_data_subLevel =complex_data_IDs_in_grammar_path(grammar_path)
        id_data_subLevel = id_data_subLevel[id_data_subLevel[verb].notna()]
        id_data_subLevel = id_data_subLevel.drop_duplicates(subset=[verb])
        data_subLevel = pd.merge(id_data_subLevel, xref_simplex_complex_value, how='left', left_on=time_label,right_on='ID_data_complex')
        if data_subLevel.empty:
            continue
        data = pd.concat([data, data_subLevel])
    result = ', '.join(simplexes[0])
    data = data.rename(columns = {'Value': result})

    return data

# get the semantic triplet (SVO) with time
def semantic_triplet_time(inputDir, outputDir, time_label, macro_event_id,  subject, verb, object, comment_info='', document_info=False):

    triplet = semantic_triplet_simplex(inputDir, subject, verb, object, document_info, comment_info)
    time = get_time_simplex(inputDir, time_label, subject, verb, object, document_info, comment_info)

    triplet_with_time = pd.merge(triplet, time, how = 'left', left_on = 'V ID', right_on = verb)
    triplet_with_time = triplet_with_time.drop(verb, axis = 1)
    triplet_with_time = triplet_with_time.rename(columns = {time_label:'Time ID'})
    triplet_with_space = triplet_with_time.dropna(subset=['Time ID'])

    # triplet_with_time = triplet_with_time.rename(columns = {time_label:'Time ID', 'Time':'Time of day'})

    if document_info:
        # move Document column to the last position of the dataframe
        document_id = triplet_with_time.pop('Document ID')
        triplet_with_time.insert(len(triplet_with_time.columns), 'Document ID', document_id)

    if comment_info != '':
        # move Comment column to the last position of the dataframe
        comment = triplet_with_time.pop('Comment')
        triplet_with_time.insert(len(triplet_with_time.columns), 'Comment', comment)

    if macro_event_id != '':
        macro_event_id = int(macro_event_id.split()[0])
        triplet_with_time = triplet_with_time[triplet_with_time['Macro Event ID'] == macro_event_id]

#   if comment_info == '':
#        triplet_with_time = triplet_with_time.drop(['Comment','UserID','UserName','VerifierID','VerifierName'], axis=1)
    if comment_info == 'user':
        triplet_with_time = triplet_with_time.drop(['VerifierID','VerifierName'], axis=1)
    elif comment_info == 'verifier':
        triplet_with_time = triplet_with_time.drop(['UserID','UserName'], axis=1)

    top_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'] == 1]['Name'].values[0]
    semantic_triplet = get_parent_complex(subject)
    if isinstance(semantic_triplet, list):
        semantic_triplet = semantic_triplet[0]
    grammar_path = get_grammar_path(top_complex, semantic_triplet)
    grammar_path = grammar_path[0]

    existing_columns = [f'{col} ID' for col in grammar_path if f'{col} ID' in triplet_with_time.columns]
    if existing_columns:
        triplet_with_time = triplet_with_time.sort_values(existing_columns, ascending=True)

    triplet_with_time_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                          'triplet (SVO) with time')
    triplet_with_time.to_csv(triplet_with_time_file_name, encoding='utf-8', index=False)

    return triplet_with_time_file_name


# helper method for semantic_triplet_space
# link simplex of space complex with V
# return: a dataframe: Process = data id of complex Process, Type of territory = data id of simplex Type of territory, Space = text of Type of territory
def get_space_simplex(inputDir, space_label_var, subject, verb, object):
    simplexes = get_simplex_names_for_complex(space_label_var)
    simplex_id = get_simplex_setup_id(simplexes[0])
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
    data_Simplex_temp = pd.merge(data_Simplex_lib, data_SimplexText_lib, how = 'left', on = 'ID_data_date_number_text')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]
    xref_simplex_complex_value = pd.merge(data_xref_Simplex_Complex_lib, data_Simplex_temp, how = 'left', on = 'ID_data_simplex')
    xref_simplex_complex_value = xref_simplex_complex_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]
    xref_simplex_complex_value = xref_simplex_complex_value[xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_id)]
    all_path = get_grammar_path(verb, space_label_var)

    data = pd.DataFrame()
    for grammar_path in all_path:
        id_data_subLevel =complex_data_IDs_in_grammar_path(grammar_path)
        id_data_subLevel = id_data_subLevel[id_data_subLevel[verb].notna()]
        id_data_subLevel = id_data_subLevel.drop_duplicates(subset=[verb])
        data_subLevel = pd.merge(id_data_subLevel, xref_simplex_complex_value, how='left', left_on=space_label_var,
                                 right_on='ID_data_complex')
        if data_subLevel.empty:
            continue
        data = pd.concat([data, data_subLevel])

    result = ', '.join(simplexes[0])
    data = data.rename(columns = {'Value':result})

    return data

def get_space_simplex(inputDir, outputDir, space_label_var, subject, verb, object, macro_event_id, comment_info='', document_info=False):

    space = get_space_simplex(inputDir, space_label_var, subject, verb, object)

    space_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'space')
    space.to_csv(space_file_name, encoding='utf-8', index=False)

    return space_file_name

# prepare the function for the use in main
# get semantic triplet with space
def semantic_triplet_space(inputDir, outputDir, space_label_var, macro_event_id, subject, verb, object, document_info, comment_info):

    triplet = semantic_triplet_simplex(inputDir, subject, verb, object, document_info, comment_info)
    space = get_space_simplex(inputDir, space_label_var, subject, verb, object, document_info, comment_info)

    triplet_with_space = pd.merge(triplet, space, how='left', left_on='V ID', right_on=verb)
    triplet_with_space = triplet_with_space.drop(verb, axis=1)
    triplet_with_space = triplet_with_space.rename(columns={space_label_var: 'Space ID'})
    triplet_with_space = triplet_with_space.dropna(subset=['Space ID'])

    if macro_event_id != '':
        macro_event_id = int(macro_event_id.split()[0])
        triplet_with_space = triplet_with_space[triplet_with_space['Macro Event ID'] == macro_event_id]

    # if not document_info:
    #     triplet_with_space = triplet_with_space.drop('Document ID', axis=1)

    # if comment_info == '':
    #     triplet_with_space = triplet_with_space.drop(['Comment','UserID','UserName','VerifierID','VerifierName'], axis=1)
    # elif comment_info == 'user':
    #     triplet_with_space = triplet_with_space.drop(['VerifierID','VerifierName'], axis=1)
    # elif comment_info == 'verifier':
    #     triplet_with_space = triplet_with_space.drop(['UserID','UserName'], axis=1)

    top_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'] == 1]['Name'].values[0]
    semantic_triplet = get_parent_complex(subject)
    if isinstance(semantic_triplet, list):
        semantic_triplet = semantic_triplet[0]
    grammar_path = get_grammar_path(top_complex, semantic_triplet)
    grammar_path = grammar_path[0]

    existing_columns = [f'{col} ID' for col in grammar_path if f'{col} ID' in triplet_with_space.columns]
    if existing_columns:
        triplet_with_space = triplet_with_space.sort_values(existing_columns, ascending=True)

    triplet_with_space_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'triplet (SVO) with space')
    triplet_with_space.to_csv(triplet_with_space_file_name, encoding='utf-8', index=False)

    return triplet_with_space_file_name


# get semantic triplet with time and space
def semantic_triplet_time_space(inputDir, outputDir, space_label_var, time_label, macro_event_id,  subject, verb, object, comment_info='', document_info=False):

    triplet = semantic_triplet_simplex(inputDir, subject, verb, object, document_info, comment_info)

    space = get_space_simplex(inputDir, space_label_var, subject, verb, object, document_info, comment_info)
    triplet_with_space = pd.merge(triplet, space, how = 'left', left_on = 'V ID', right_on = verb)
    time = get_time_simplex(inputDir, time_label, subject, verb, object)
    triplet_with_time_space = pd.merge(triplet_with_space, time, how = 'left', left_on = 'V ID', right_on = verb)
    # triplet_with_time_space = triplet_with_time_space.drop(verb, axis = 1)
    triplet_with_time_space = triplet_with_time_space.rename(columns = {time_label:'Time ID', space_label_var:'Space ID'})
    triplet_with_time_space = triplet_with_time_space.dropna(subset=['Space ID', 'Time ID'])


    if macro_event_id != '':
        macro_event_id = int(macro_event_id.split()[0])
        triplet_with_time_space = triplet_with_time_space[triplet_with_time_space['Macro Event ID'] == macro_event_id]

    # if comment_info == '':
    #     triplet_with_time_space = triplet_with_time_space.drop(['Comment','UserID','UserName','VerifierID','VerifierName'], axis=1)
    # elif comment_info == 'user':
    #     triplet_with_time_space = triplet_with_time_space.drop(['VerifierID','VerifierName'], axis=1)
    # elif comment_info == 'verifier':
    #     triplet_with_time_space = triplet_with_time_space.drop(['UserID','UserName'], axis=1)

    top_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'] == 1]['Name'].values[0]
    semantic_triplet = get_parent_complex(subject)
    if isinstance(semantic_triplet, list):
        semantic_triplet = semantic_triplet[0]
    grammar_path = get_grammar_path(top_complex, semantic_triplet)
    grammar_path = grammar_path[0]

    existing_columns = [f'{col} ID' for col in grammar_path if f'{col} ID' in triplet_with_time_space.columns]
    if existing_columns:
        triplet_with_time_space = triplet_with_time_space.sort_values(existing_columns, ascending=True)

    triplet_with_space_time_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                                'triplet (SVO) with space and time')
    triplet_with_time_space.to_csv(triplet_with_space_time_file_name, encoding='utf-8', index=False)

    return triplet_with_space_time_file_name

# Find paths for each simplexes under the actors var recursively
def get_complex_paths(complex_name, grammar_path, complete_complexes):
    # Make a copy of the grammar_path to avoid modifying the same list in recursive calls
    current_path = grammar_path + [complex_name]

    # Check if the complex_name is already in the grammar_path to prevent repeated cycles
    if complex_name in grammar_path:
        return

    # Get the simplex names and child complexes for the current complex
    simplex_names = get_simplex_names_for_complex(complex_name)
    child_complexes = get_child_complex(complex_name)

    # Add grammar_path if simplex names are present
    if simplex_names and simplex_names[0]:  # This covers cases with direct simplex
        complete_complexes.append(current_path)

    # Recursively process child complexes if they exist
    if child_complexes:
        if isinstance(child_complexes, list):  # Handle multiple child complexes
            for child_complex in child_complexes:
                get_complex_paths(child_complex, current_path, complete_complexes)
        else:  # Single child complex
            get_complex_paths(child_complexes, current_path, complete_complexes)

    # If there's no simplex and only child complexes, the grammar_path is not added
    return complete_complexes

# get individual characteristics

# NOT USED
def actor_characteristics(inputDir, outputDir, actors_var, macro_event_id='', comment_info='', document_info=False):

    # build table for complex
    id_complex = get_complex_setup_id([actors_var]).iat[0, 0]
    table_complex = data_Complex_lib[data_Complex_lib['ID_setup_complex'] == id_complex]

    # @ Hard-coded 'Personal characteristics' must change to reflect the specific setup of a specific project
    names_personal_characteristics = get_lower_complex([actors_var])
    names_personal_characteristics = names_personal_characteristics['Name'].values.tolist()

    data_Simplex_temp = pd.merge(data_Simplex_lib, data_SimplexText_lib, how = 'left', on = 'ID_data_date_number_text')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    xref_simplex_complex_value = pd.merge(data_xref_Simplex_Complex_lib, data_Simplex_temp, how = 'left', on = 'ID_data_simplex')
    xref_simplex_complex_value = xref_simplex_complex_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

    path_map = {}
    all_paths = []
    complete_complexes = []
    grammar_path = [actors_var]
    print('all_paths', all_paths)
    # Loop through all complete paths and update path_map
    for complex_name in names_personal_characteristics:
        grammar_path=grammar_path[:1]
        all_paths = get_complex_paths(complex_name, grammar_path, all_paths)
        for grammar_path in all_paths:
            last_complex = grammar_path[-1]
            if last_complex not in complete_complexes:
                complete_complexes.append(last_complex)
                path_map[last_complex] = grammar_path

    for complex_name, grammar_path in path_map.items():
        print(f"Complex Name: {complex_name}")
        print(f"grammar_path: {grammar_path}")
        print("-" * 40)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------')
    # loop through all the children complex objects (e.g., Age, First name and last name, ...)
    for name in complete_complexes:
        grammar_path = path_map[name]
        id_data_personal_characteristics =complex_data_IDs_in_grammar_path(grammar_path)
        data_personal_characteristics = get_identifier(id_data_personal_characteristics, [name])
        table_complex = pd.merge(table_complex, data_personal_characteristics, how='left', left_on='ID_data_complex',
                                 right_on=actors_var)
        table_complex = table_complex.drop(actors_var, axis=1)

    # Initialize a dictionary to track parent-child relationships for complexes without simplexes
    table_complex = table_complex.drop('ID_setup_complex', axis=1)
    table_complex = table_complex.rename(
        columns={'ID_data_complex': actors_var, 'Identifier': actors_var + ' Identifier'})

    # start to build simplex table
    table_simplex = table_complex

    complete_complexes.append(actors_var)
    # Loop through all complexes with direct simplexes and building simplex tables for each complex
    for complex_name in complete_complexes:
        simplex_names = get_simplex_names_for_complex(complex_name)

        print('simplex_names',  simplex_names)
        for i in range(0, len(simplex_names)):
            for simplex_name in simplex_names[i]:
                print("simplex name : ", simplex_name)
                simplex_id = get_simplex_setup_id([simplex_name])
                simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
                xref_simplex_complex_value_new = xref_simplex_complex_value[xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_id)]
                xref_simplex_complex_value_new = xref_simplex_complex_value_new.rename(columns={'ID_data_complex': complex_name})
                print(f"Columns in table_simplex: {table_simplex.columns}")
                print(f"Columns in xref_simplex_complex_value_new: {xref_simplex_complex_value_new.columns}")

                # Merge with table_simplex
                table_simplex = pd.merge(table_simplex, xref_simplex_complex_value_new, how='left', on=complex_name)
                table_simplex = table_simplex.rename(
                    columns={'ID_data_simplex': simplex_name + ' ID', 'Value': simplex_name + ' Simplex'})
                table_simplex = table_simplex.drop('ID_setup_simplex', axis=1)
        table_simplex = table_simplex.drop(complex_name, axis=1)
        table_simplex = table_simplex.drop(complex_name + ' Identifier', axis=1)
        print(table_simplex.columns)

    print('----------------------------------------------------------------------------------')
    print('before residence table_simplex', table_simplex)

    table_simplex = table_simplex.dropna(axis=1, how='all')
    individual_characteristics_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'individual characteristics')
    table_simplex.to_csv(individual_characteristics_file_name, encoding='utf-8', index=False)
    print("--------------------------------------------------------------------------------------------------------------------------------------------")
    print(table_simplex)
    return individual_characteristics_file_name


def individual_simplex_info(simplex, inputDir, outputDir):
    data = {'information': ['simplex name', 'frequency', 'complex name', 'higher complex', 'lower complex', 'relationship to event']}
    simplex_info = []

    # get data ID and simplex value in text-number-date file
    # data_simplex_temp = pd.concat([data_SimplexDate_lib, data_SimplexNumber_lib, data_SimplexText_lib])
    # get setup and data ID and value of all simplex
    data_simplex = pd.merge(data_Simplex_lib, data_SimplexText_lib, how = 'left', on = 'ID_data_date_number_text')
    data_simplex_selected = data_simplex[data_simplex['Value']==simplex]
    simplex_setup_id = data_simplex_selected['ID_setup_simplex'].values.tolist()
    simplex_names = setup_Simplex_lib[setup_Simplex_lib['ID_setup_simplex'].isin(simplex_setup_id)]
    simplex_names = simplex_names['Name'].values.tolist()
    for name in simplex_names:
        simplex_info.append([name])

    # frequency
    temp = pd.merge(data_xref_Simplex_Complex_lib, data_Simplex_lib, how = 'left', on = 'ID_data_simplex')
    ID_data_date_number_text = temp['ID_data_date_number_text'].values.tolist()
    ID_data_date_number_text = ID_data_date_number_text[0]
    data_xref_Simplex_Complex_select = temp[temp['ID_data_date_number_text']==ID_data_date_number_text]
    for i in range(len(simplex_info)):
        simplex_setup_id = get_simplex_setup_id([simplex_info[i][0]])
        simplex_setup_id = simplex_setup_id.iat[0,0]
        data_xref_Simplex_Complex_select_further = data_xref_Simplex_Complex_select[data_xref_Simplex_Complex_select['ID_setup_simplex']==simplex_setup_id]
        frequency = 0
        if len(data_xref_Simplex_Complex_select_further) !=0:
            frequency = data_xref_Simplex_Complex_select_further.groupby(['ID_data_simplex']).count()
            frequency = frequency.iat[0,0]
        simplex_info[i].append(frequency)

    # complex related info
    for i in range(len(simplex_info)):
        simplex_name = simplex_info[i][0]
        complex_name = get_parent_simplex_util([simplex_name])
        if len(complex_name) != 0:
            # highercomplex
            higher_complex = get_higher_complex(complex_name)
            higher_complex = higher_complex['Name'].values.tolist()
            # lowercomplex
            lower_complex = get_lower_complex(complex_name)
            lower_complex = lower_complex['Name'].values.tolist()
            # relationship to event
            grammar_path = get_grammar_path('Event', complex_name[0])
            grammar_path = grammar_path[0]
            # format
            complex_name_table = ', '.join(complex_name)
            higher_complex_table = ', '.join(higher_complex)
            lower_complex_table = ', '.join(lower_complex)
            path_table = ', '.join(grammar_path)
        else:
            complex_name_table = ''
            higher_complex_table = ''
            lower_complex_table = ''
            path_table = ''
        # save
        simplex_info[i].append(complex_name_table)
        simplex_info[i].append(higher_complex_table)
        simplex_info[i].append(lower_complex_table)
        simplex_info[i].append(path_table)


    for i in range(len(simplex_info)):
        name = 'value' + str(i+1)
        data[name] = simplex_info[i]

    df = pd.DataFrame(data)

    individual_simplex_info_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'individual simplex information')
    df.to_csv(individual_simplex_info_file_name, encoding='utf-8', index=False)

    return individual_simplex_info_file_name



def build_macro_event_dropdown_menu(inputDir):
    macro_event_dropdown_menu_list = []

    if os.path.exists(f"{inputDir}/{'setup_Complex'}.pkl"):
        has_files = True
    else:
        has_files = False
    if(has_files):

        macro_event_name = setup_Complex_lib['Name'][0]
        # macro_event_name_id = get_complex_setup_id(["Macro Event"], setup_Complex_lib)
        macro_event_name_id = get_complex_setup_id([macro_event_name])
        macro_event_name_id = macro_event_name_id.iloc[0,0]

        macro_event_identifier = data_Complex_lib[data_Complex_lib['ID_setup_complex'] == macro_event_name_id]

        macro_event_dropdown_menu_list = macro_event_identifier.apply(lambda x: f"{x['ID_data_complex']} - {x['Identifier']}", axis=1).tolist()

    return macro_event_dropdown_menu_list