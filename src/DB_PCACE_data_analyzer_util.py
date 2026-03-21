# remove the decimals caused by nan values in one of the dfs
# xref_simplex_complex_value["ID_data_xref_simplex_complex"] = xref_simplex_complex_value["ID_data_xref_simplex_complex"].fillna(-1).astype(int)
# xref_simplex_complex_value["ID_setup_xref_simplex_complex"] = xref_simplex_complex_value["ID_setup_xref_simplex_complex"].fillna(-1).astype(int)
# xref_simplex_complex_value["ID_data_simplex"] = xref_simplex_complex_value["ID_data_simplex"].fillna(-1).astype(int)
# xref_simplex_complex_value["ID_data_complex"] = xref_simplex_complex_value["ID_data_complex"].fillna(-1).astype(int)
# xref_simplex_complex_value["Order"] = xref_simplex_complex_value["Order"].fillna(-1).astype(int)
# xref_simplex_complex_value["ID_data_date_number_text"] = xref_simplex_complex_value["ID_data_date_number_text"].fillna(-1).astype(int)

# restrict records to Value date to remove any unwanted duplicates from Number or Text tables
# dates = pd.to_datetime(data_Simplex_DateValues['Value'], errors='coerce')
# data_Simplex_DateValues = data_Simplex_DateValues[(dates.notnull())]

# restrict records to Value number to remove any unwanted duplicates from Date or Text tables
# numbers = pd.to_numeric(data_Simplex_NumberValues['Value'], errors='coerce')
# data_Simplex_NumberValues = data_Simplex_NumberValues[(numbers.notnull())]

# insert the setup simplex name
# simplex_values_ALL = pd.merge(setup_Simplex_lib, simplex_values_ALL, left_on=
#                                       'ID_setup_simplex', right_on='ID_setup_simplex')
# simplex_values_ALL.rename(columns={'Name': "Simplex name"})
# simplex_values_ALL.rename(columns={'ValueType_x': "ValueType"})
# select columns    # restrict records to Value string to remove any unwanted duplicates from Date or Number tables
#     # strings = pd.to_string(data_Simplex_StringValues['Value'], errors='coerce')
#     # data_Simplex_StringValues = data_Simplex_StringValues[(strings.notnull())]
#
#     # data_Simplex_TextValues = data_Simplex_TextValues['Value'].dropna().astype(str)

# simplex_values_ALL = simplex_values_ALL[
#     ['ID_setup_simplex', 'Simplex name', 'ValueType', 'ID_data_simplex', 'ID_data_date_number_text', 'Value']]

# Anna (Qinchen) Ruan originally wrote the code
# Taeeun Kim Fall 2025 heavily edited the code generalizing functions and moving away from hard coded setup values so as to use the code across different databases
# Aiden Summer 2025 improved loading of different databases using pickle files, fixed SVO extractor, and continued to generalize the code across different databases
# RF added all visuals and several new functions

# LEGENDA
# ComplexType in data:complex & SimplexType in data:simplex point to setup IDs in setup:complex & setup:simplex
# xrefID in data_xref_complex_complex, data_xref_simplex_complex, data_xref_Simplex-Simplex-Document refer to
#   the ID in the respective setup_xref
# the number of records in data:complex is generally much < than data:xref_complex_complex
# the number of records in data:simplex is generally much < than data:xref_simplex-complex.

# ValueType in setup_Simplex takes on values 1, 2, 3 for string, numeric, and date values respectively

# There are SEVEN tables dealing with DOCUMENTS:
#   setup_Document, setup_xref_Simplex-Document, setup_xref_Complex-Document,
#   data_Document, data_xref_Complex-Document, data_xref_Simplex-Document, data_Simplex_Simplex-Document

# There are SIX tables dealing with COMMENTS (users and verifiers):
#   data_xref_comment_complex, data_xref_Comment_Simplex, data_xref_Comment_Document,
#   data_xref_VComment, data_xref_VComment-Document, data_VCommentArchive

import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "DB_PC-ACE_data_analyzer_main.py", ['os', 'tkinter','pandas','numpy'])==False:
    sys.exit(0)

import IO_user_interface_util
import tkinter as tk
import tkinter.messagebox as mb

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
    #                    message='There are no xlsx files in the input directory.\n\nThe script expects a set of xlsx files with overlapping ID fields across files in order to construct an SQLite relational database.\n\nPlease, select an input directory that contains 18 xlsx PC-ACE tables and try again')
    if not "data_Document.xlsx" in str(tableList) and not "data_Complex.xlsx" in str(tableList):
        # mb.showwarning(title='Warning',
        #                message='Although the input directory does contain xlsx files, these files do not have the expected PC-ACE filename (e.g. data_Document, data_Complex).\n\nPlease, select an input directory that contains xlsx PC-ACE tables and try again')
        tableList=[]
    # else:
    #     build_libraries(inputDir, outputDir)
    return tableList


# rename the ID fields of each table to a more meaningful value
#   e,g. The ID in setup_Complex.xlsx is renamed ID_setup_complex
#   The ID in setup_xref_complex-complex.xlsx is renamed ID_setup_xref_complex_complex

# 22 tables
reading_list = [
    ('setup_Complex.xlsx', {'ID':'ID_setup_complex'}),
    ('setup_Simplex.xlsx', {'ID':'ID_setup_simplex'}),
    ('setup_Document.xlsx', {'ID':'ID_setup_document'}),
    ('setup_xref_Complex-Complex.xlsx', {'ID':'ID_setup_xref_complex-complex'}),
    ('setup_xref_Simplex-Complex.xlsx', {'ID':'ID_setup_xref_simplex-complex', 'Complex':'ID_setup_complex', 'Simplex':'ID_setup_simplex'}),
    ('data_Complex.xlsx', {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"}),
    ('data_Simplex.xlsx', {"ID":"ID_data_simplex", "SimplexType":"ID_setup_simplex", "refValue":"ID_data_date_number_text"}),
    ('data_SimplexText.xlsx', {"ID":"ID_data_date_number_text"}),
    ('data_SimplexNumber.xlsx', {"ID":"ID_data_date_number_text"}),
    ('data_SimplexDate.xlsx', {"ID":"ID_data_date_number_text"}),
    ('data_xref_Simplex-Complex.xlsx', {'ID':'ID_data_xref_simplex-complex', 'xrefID':'ID_setup_xref_simplex-complex', 'Simplex':'ID_data_simplex', 'Complex':'ID_data_complex'}),
    ('data_xref_Complex-Complex.xlsx', {'ID':'ID_data_xref_complex-complex', 'HigherComplex':'ID_data_complex_HIGHER', 'xrefID':'ID_setup_xref_complex-complex', 'LowerComplex':'ID_data_complex_LOWER'}),
    ('data_xref_AnyComplex-Complex.xlsx', {'ID':'ID_data_xref_Anycomplex-complex', 'Complex':'ID_data_complex', 'AnyComplex':'ID_data_complex'}),
    ('data_Document.xlsx', {'ID':'ID_data_document'}),
    ('data_xref_Complex-Document.xlsx', {}),
    ('data_xref_Simplex-Document.xlsx', {'ID_datat_simplex':'ID_data_simplex'}),
    ('data_xref_comment-complex.xlsx', {}),
    ('data_xref_Comment-Simplex.xlsx', {}),
    ('data_xref_Comment-Document.xlsx', {}),
    ('data_xref_VComment.xlsx', {}),
    ('data_xref_VComment-Document.xlsx', {}),
    ('data_VCommentArchive.xlsx', {}),
    ('utility_Security.xlsx', {})
    # ('NLP_Simplex_values_ALL.xlsx', {}),
    # ('NLP_xref_Simplex-Complex_ALL.xlsx', {})
]

library = {}

def check_missing(fileName):
    if os.path.isfile(fileName):
        # fileName_lib = pd.DataFrame(pd.read_excel(fileName))
        fileName_lib = pd.read_excel(fileName)
        return fileName_lib
    else:
        mb.showwarning(title='Warning',
                    message='The table ' + fileName + ' is missing.\n\nPlease, make sure to export this table from PC-ACE data backend and try again')
        # create an empty dataframe
        return pd.DataFrame()

# returns a df in the form of a pkl file or _lib df
def create_pkl_file(inputDir, filename, colName_toDrop='', dropNanValues=False):
    df = check_missing(os.path.join(inputDir, filename+'.xlsx'))
    if df.empty:
        library[filename] = {}
    else:
        if dropNanValues:
            df = df.dropna(subset=[colName_toDrop])
        library[filename] = df
        pkl_fileName = f"{filename}.pkl"

        for fn, rename_columns in reading_list:
            if fn == filename+'.xlsx':
                if rename_columns:
                    df.rename(columns=rename_columns, inplace=True)
                library[filename] = df
                # pkl_fileName = f"{pkl_fileName}.pkl"
                break
        df.to_pickle(str(inputDir) + "/" + str(pkl_fileName))
    return df

# def load_lib(inputDir, outputDir):
#
#     import IO_user_interface_util
#     inputDocs = IO_files_util.getFileList('',inputDir, fileType='.xlsx', silent=True)
#     nDocs = len(inputDocs)
#
#     head, tail = os.path.split(inputDir)
#
#     if os.path.exists(f"{inputDir}/{'setup_Complex'}.pkl"):
#         timing = 2000
#         IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Loading PC-ACE database.', 'Loading ' + str(
#             nDocs) + ' pkl files from PC-ACE database ' + tail + '\n\nPlease, be patient',
#                                            False, '', True, '', False)
#     else:
#         timing = 4000
#         IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Loading PC-ACE database.', 'Loading ' + str(
#             nDocs) + ' xlsx files from PC-ACE database ' + tail + '\n\nPlease, be patient Depending on database size this may take several minutes.\n\nThe algorithm will create a set of pkl files that will make loading MUCH faster in the future',
#                                            False, '', True, '', False)
#
#     print('InputDir', inputDir)
#     i = 0
#     NumTables = len(reading_list)
#     # current_path = os.getcwd()
#     for filename, rename_columns in reading_list:
#         parts = filename.split(".")
#         name = parts[0]
#
#         if os.path.exists(f"{inputDir}/{name}.pkl"):
#             df = pd.read_pickle(f"{inputDir}/{name}.pkl")
#             library[filename] = df
#             print(library[filename])
#             i = i+1
#             print('  Filename ' + str(i) + '/' + str(NumTables), filename)
#         else:
#             i = i + 1
#             print('  Filename ' + str(i) + '/' + str(NumTables), filename)
#             df = check_missing(os.path.join(inputDir, filename))
#             if df.empty:
#                 library[filename] = {}
#             else:
#                 if rename_columns:
#                     df.rename(columns=rename_columns, inplace=True)
#                 library[filename] = df
#                 # save df as pkl file
#                 df.to_pickle(str(inputDir) + "/" + str(f"{name}.pkl"))
#
#     build_libraries(inputDir, outputDir)
#     build_NLP_libraries(inputDir, outputDir)
#
#     return



def build_NLP_libraries(inputDir, outputDir):
    global simplex_values_ALL_lib, xref_simplex_complex_ALL_lib
    name = 'NLP_Simplex_values_ALL'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name + '.xlsx'] = df
        simplex_values_ALL_lib = library[name + '.xlsx']
    else:
        simplex_values_ALL_lib = get_simplex_values_ALL(inputDir, outputDir)

    name = 'NLP_xref_Simplex-Complex_ALL'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name + '.xlsx'] = df
        xref_simplex_complex_ALL_lib = library[name + '.xlsx']
    else:
        xref_simplex_complex_ALL_lib = get_xref_simplex_complex_ALL(inputDir, outputDir)

    return

# builds pkl files from Excel files
# pkl files are MUCH faster to open and read
def build_libraries(inputDir, outputDir):
    global setup_Complex_lib, setup_Simplex_lib, setup_xref_Complex_Complex_lib, crossref, setup_xref_simplex_complex_lib, data_Simplex_lib, data_SimplexText_lib, data_SimplexNumber_lib, data_SimplexDate_lib, data_Complex_lib, data_xref_Complex_Complex_lib, data_xref_AnyComplex_Complex_lib, data_xref_simplex_complex_lib, data_xref_Document_lib, data_xref_Simplex_Simplex_Document_lib, data_xref_Complex_Document_lib, data_xref_comment_complex_lib, data_xref_Comment_Document_lib, data_xref_VComment_lib, data_xref_VComment_Document_lib, utility_Security_lib, simplex_values_ALL_lib, xref_simplex_complex_ALL_lib
    # global dfs_df
    # headers = ['Parent (search) complex name', 'Parent (search) complex ID (data ID)', 'Complex child name', 'Complex child ID (data ID)', 'Simplex name', 'Value']
    # dfs_df = pd.DataFrame(columns=headers)

    import IO_user_interface_util
    inputDocs = IO_files_util.getFileList('',inputDir, fileType='.pkl', silent=True)
    nDocs = len(inputDocs)

    head, tail = os.path.split(inputDir)

    if nDocs > 20: # there should be at least 20 pkl files, in fact as many as xlsx files
        timing = 2000
        IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Loading PC-ACE database.', 'Loading ' + str(
            nDocs) + ' pkl files from PC-ACE database ' + tail + '\n\nPlease, be patient...',
                                           False, '', True, '', False)
    else:
        inputDocs = IO_files_util.getFileList('', inputDir, fileType='.xlsx', silent=True)
        nDocs = len(inputDocs)
        timing = 4000
        IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Loading PC-ACE database.', 'Loading ' + str(
            nDocs) + ' xlsx files from PC-ACE database ' + tail + '\n\nThe algorithm will create a set of pkl files that will make loading MUCH faster in the future.\n\nPlease, be patient ... Depending on database size this may take several minutes.',
                                           False, '', True, '', False)
    print('InputDir', inputDir)

    # loading/creating all pkl files
    name = 'setup_Complex'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        setup_Complex_lib = library[name+'.xlsx']
    else:
        setup_Complex_lib = create_pkl_file(inputDir, name)

    name='setup_Simplex'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        setup_Simplex_lib = library[name+'.xlsx']
    else:
        setup_Simplex_lib = create_pkl_file(inputDir, name)

    name='setup_xref_Complex-Complex'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        setup_xref_Complex_Complex_lib = library[name+'.xlsx']
    else:
        setup_xref_Complex_Complex_lib = create_pkl_file(inputDir, name)
    # only keep required complex objects
    crossref = setup_xref_Complex_Complex_lib[['Required', 'Name']]

    name='setup_xref_Simplex-Complex'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        setup_xref_simplex_complex_lib = library[name+'.xlsx']
    else:
        setup_xref_simplex_complex_lib = create_pkl_file(inputDir, name)

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
        data_SimplexText_lib = library[name+'.xlsx']
    else:
        data_SimplexText_lib = create_pkl_file(inputDir, name)


    name='data_SimplexNumber'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_SimplexNumber_lib = library[name+'.xlsx']
    else:
        data_SimplexNumber_lib = create_pkl_file(inputDir, name)

    name='data_SimplexDate'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        # contrary to data_SimplexNumber and data_SimplexText, data_SimplexDate contains Nan blank Values
        # this only happens for the lynching DB!!!
        # df = df['Value'].dropna().astype(str)
        library[name+'.xlsx'] = df
        data_SimplexDate_lib = library[name+'.xlsx']
        data_SimplexDate_lib = data_SimplexDate_lib.rename(columns={'ID': 'ID_data_date_number_text'})
    else:
        # contrary to data_SimplexNumber and data_SimplexText, data_SimplexDate contains empty rows
        # this only happens for the lynching DB!!!
        data_SimplexDate_lib = create_pkl_file(inputDir, name, 'Value', True)
        try:
            data_SimplexDate_lib = data_SimplexDate_lib.rename(columns={'ID': 'ID_data_date_number_text'})
        except:
            pass

    name='data_Complex'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_Complex_lib = library[name+'.xlsx']
    else:
        data_Complex_lib = create_pkl_file(inputDir, name)

    name='data_xref_Complex-Complex'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_xref_Complex_Complex_lib = library[name+'.xlsx']
    else:
        data_xref_Complex_Complex_lib = create_pkl_file(inputDir, name)


    name='data_xref_AnyComplex-Complex'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_xref_AnyComplex_Complex_lib = library[name+'.xlsx']
    else:
        data_xref_AnyComplex_Complex_lib = create_pkl_file(inputDir, name)

    name='data_xref_Simplex-Complex'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_xref_simplex_complex_lib = library[name+'.xlsx']
    else:
        data_xref_simplex_complex_lib = create_pkl_file(inputDir, name)

    name='data_xref_Complex-Document'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_xref_Complex_Document_lib = library[name+'.xlsx']
    else:
        data_xref_Complex_Document_lib = create_pkl_file(inputDir, name)

    name='data_xref_Simplex-Simplex-Document'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_xref_Simplex_Simplex_Document_lib = library[name+'.xlsx']
    else:
        data_xref_Simplex_Simplex_Document_lib = create_pkl_file(inputDir, name)

    name='data_xref_comment-complex'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_xref_comment_complex_lib = library[name+'.xlsx']
    else:
        data_xref_comment_complex_lib = create_pkl_file(inputDir, name)

    name='data_xref_comment-simplex'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_xref_comment_simplex_lib = library[name+'.xlsx']
    else:
        data_xref_comment_simplex_lib = create_pkl_file(inputDir, name)

    name='data_xref_Comment-Document'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_xref_Comment_Document_lib = library[name+'.xlsx']
    else:
        data_xref_Comment_Document_lib = create_pkl_file(inputDir, name)

    name='data_xref_VComment'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_xref_VComment_lib = library[name+'.xlsx']
    else:
        data_xref_VComment_lib = create_pkl_file(inputDir, name)

    name='data_xref_VComment-Document'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_xref_VComment_Document_lib = library[name+'.xlsx']
    else:
        data_xref_VComment_Document_lib = create_pkl_file(inputDir, name)

    name='utility_Security'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        utility_Security_lib = library[name+'.xlsx']
    else:
        utility_Security_lib = create_pkl_file(inputDir, name)

    build_NLP_libraries(inputDir, outputDir)

    print('Done importing libraries.')

# check if a required document can be found.
# OK pass checks and returns a dataframe or a boolean set to False if the file is not found.

def export_df_to_csv(df, inputDir, outputDir, outputFilename, create_pkl_file=True):
    # save files to input directory since these are permanent files
    df.to_csv(outputFilename, index=False) # encoding='utf-8'
    if create_pkl_file:
        library[outputFilename] = df
        pkl_fileName = f"{outputFilename}.pkl"

def export_df_to_excel(df, inputDir, outputDir, outputFilename, create_pkl_file=True):
    # import IO_user_interface_util
    timing = 2000
    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Saving dataframe to Excel','Saving dataframe to Excel file ' + outputFilename + '\n\n\nPlease, be patient... Depending upon the size of the dataframe this may take a few minutes.')
    # save files to input directory since these are permanent files
    ExceloutputFilename = inputDir + os.sep + outputFilename + '.xlsx'
    df.to_excel(ExceloutputFilename, index=False) # encoding='utf-8'
    if create_pkl_file:
        library[outputFilename] = df
        # save df as pkl file
        df.to_pickle(str(inputDir) + "/" + str(f"{outputFilename}.pkl"))
        return df

# the entire grammar is printed using setup_complex as the excel_file
# the txt output file is exported to the input directory
def view_grammar(excel_file, column_name, output_file):
    """
    exports the contents from a specific excel file to a txt
    - excel_file (str): grammar_path to the Excel file.
    - column_name (str): Name of the column to read.
    - output_file (str): grammar_path to the output text file.
    """

    if os.path.exists(output_file):
        command = tk.messagebox.askyesno("File manager",
                                         "The grammar will be exported as a text file in the same directory of the input Excel fles.\n\nThere already exists a text file " + output_file + " in the data input directory. This will be replaced.\n\nAre you sure you want to continue?")
        if command == False:
            return

    try:
        df = pd.read_excel(excel_file)

        column_data = df[column_name].dropna().astype(str)

        #replacing extra '_x00D_' strings that appear
        column_data = column_data.str.replace('_x000d_', '', regex=False)
        column_data = column_data.str.replace('_x000D_', '', regex=False)

        grammar = 'LEGENDA\n\n   -->  Rewrite rule (the object to the left of --> can be rewritten in terms of the object(s) to the right)\n   ++   Hierarchical object (e.g., Macro event, Event, Semantic triplet)\n   +    Complex object (no + Simplex object)\n   <>   Can be rewritten\n   []   Optional object\n   {}   Multiples allowed\n   (1a) (1b) (1c)... mutually exclusive objects' \
                  '\n                      (e.g., <+Actor> rewritten as <+Individual (1a) <+Collective actor (1b). Both CANNOT be entered; it is one or the other).\n\n'


        with open(output_file, 'w', encoding='utf-8') as f:
            for i, row in enumerate(column_data, start=1):
                # f.write(f"{i}    {row}\n")
                # Aiden i is printed only the first time
                # place row number right before each row object, since the row number is sometimes referred to in the rewrite rules for objcets already rewritten
                row = row.replace(row,row[:1] + '\nLine ' + str(i) + ' ' + row[1:])
                grammar=grammar+row
            print('Grammar',grammar)
            f.write(grammar)

        IO_files_util.openFile('', output_file)
    except Exception as e:
         print(f"An error occurred: {e}")

# get a list of all setup complex and simplex names to be used in dropdown menus in _main
def get_complex_simplex_names():
    try:
        if setup_Complex_lib is not None and setup_Simplex_lib is not None:
            return setup_Complex_lib["Name"].dropna().sort_values().tolist(), setup_Simplex_lib["Name"].dropna().sort_values().tolist()
    except:
        return [], []


# helper method for get_Simplex_text_date_number
# convert the column named 'Value' into list type

# NOT used
def get_all_simplex_values(data):
    return data['Value'].dropna().tolist()

# given a simplex setup name, the function returns a list of all values in data_SimplexText, data_SimplexDate or data_SimplexNumber
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
    if any(df is None or df.empty for df in [setup_Simplex_lib, data_Simplex_lib, data_xref_simplex_complex_lib]):
        return None

    # name must be a list
    if isinstance(name, str):
        name = [name]

    simplex_ID = get_simplex_setup_ID(name)
    id, name = simplex_ID.iloc[0]

    merged_data = pd.merge(data_xref_simplex_complex_lib, data_Simplex_lib, how = 'left', on = 'ID_data_simplex')
    # filter the dataframe by the selected simplex
    filtered_simplex = merged_data[merged_data['ID_setup_simplex']==id][['ID_data_simplex', 'ID_data_complex']]

    simplex_data_combined = pd.merge(data_Simplex_lib, data_SimplexText_lib, how='left', on='ID_data_date_number_text')[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    if compute_frequencies:
        count = filtered_simplex.groupby(['ID_data_simplex']).size().reset_index(name='Frequency')
        result = pd.merge(count, simplex_data_combined, how = 'left', on = 'ID_data_simplex')
        result = result.rename(columns={'Value': name}).sort_values(by='Frequency', ascending=False)
        # TODO Anna: The first column should have a header "Name of Simplex Object"
        extension = '.xlsx' # change to '.csv' if necessary
        simplex_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
                                                                           name+'_simplex_freq')
    else:
        #list all simplex values
        extension = '.xlsx' # change to '.csv' if necessary
        result = pd.merge(filtered_simplex, simplex_data_combined, how = 'left', on = 'ID_data_simplex')
        simplex_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
                                                                           name+'_simplex_list')
    result.to_csv(simplex_file_name, encoding='utf-8', index=False)
    return simplex_file_name # this can be a file of simplex frequencies or simplex list


# Creates csv file with frequencies of complex associations for each simplex.
# return: grammar_path to generated csv or None if data is missing
def get_simplex_frequencies_all(inputDir, outputDir):
    if any(df is None or df.empty for df in [setup_Simplex_lib, data_Simplex_lib, data_xref_simplex_complex_lib]):
        return None

    list_simplex_name = setup_Simplex_lib['Name'].dropna().tolist()
    merged_data = pd.merge(data_xref_simplex_complex_lib, data_Simplex_lib, how='left', on='ID_data_simplex')

    all_rows=[]
    for name in list_simplex_name:
        simplex_info = get_simplex_setup_ID([name])
        simplex_ID = simplex_info.iloc[0,0]

        filtered_data = merged_data[merged_data['ID_setup_simplex'] == simplex_ID]
        all_rows.append([name, len(filtered_data)])

    count_lib = pd.DataFrame(all_rows, columns=['name', 'frequency'])

    extension = '.xlsx' # change to '.csv' if necessary
    output_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
                                                                       'all_simplex_freq')
    count_lib.to_csv(output_file_name, encoding='utf-8', index=False)

    return output_file_name


# @@@@@
# given a complex setup name selected in _main, the function returns an output file containing a set of information about the complex
#   e.g. identifier, simplex values
def get_complex(complex_name, comment_type, document_info, inputDir, outputDir, extended_headers=False):
    global dfs_df
    dfs_df = pd.DataFrame()
    if not extended_headers:
        headers = ['Parent (search) complex name', 'Parent (search) complex ID (data ID)', 'Complex child name', 'Complex child ID (data ID)', 'Simplex name', 'Value']
        dfs_df = pd.DataFrame(columns=headers)

    # append_rows = dfs(complex_name, inputDir, outputDir, complex_name, extended_headers)
    append_rows = dfs(complex_name, inputDir, outputDir, None, extended_headers)

    new_rows_df = pd.DataFrame(append_rows)
    dfs_df = pd.concat([dfs_df, new_rows_df], ignore_index=True)

    # @@@@@ Aiden question temporarily disconnected
    # dfs_df = get_path_info_to_complex_object(complex_name, dfs_df)

    if document_info:
        dfs_df = get_document_info(dfs_df)

    if comment_type!='':
        dfs_df = get_comment_info(dfs_df, complex_name, comment_type)

    # extension = '.xlsx' # change to '.csv' if necessary
    extension = '.csv' # change to '.excel' if necessary
    complex_object_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, extension, 'Complex_'+complex_name)
    dfs_df.to_csv(complex_object_file_name, index=False)

    return dfs_df, complex_object_file_name

def get_complex_frequencies(name, inputDir, outputDir):

    if any(df is None or df.empty for df in [setup_Complex_lib, data_Complex_lib, data_xref_Complex_Complex_lib]):
        return None

    if isinstance(name, str):
            name = [name]

    # Find the complex ID and name
    complex_info = get_complex_setup_ID(name)
    complex_ID, name = complex_info.iloc[0]

    # Merge DataFrames to get the relevant data
    merged_data = pd.merge(data_xref_Complex_Complex_lib, data_Complex_lib, how = 'left', on = 'ID_data_complex')
    select = merged_data[merged_data['ID_setup_complex'] == complex_ID]

    # Group and count the frequencies
    count = select.groupby('ID_data_complex_LOWER').size().reset_index(name='Frequency')
    result = pd.merge(count, data_Complex_lib, how = 'left', left_on = 'ID_data_complex_LOWER', right_on = 'ID_data_complex')

    result = result[['Identifier', 'Frequency']].rename(columns={'Identifier': name}).sort_values(by='Frequency', ascending=False)
    # extension = '.xlsx' # change to '.csv' if necessary
    extension = '.csv' # change to '.excel' if necessary
    complex_frequency_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
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
        complex_info = get_complex_setup_ID([name])
        complex_ID = complex_info.iat[0,0]

        select = merged_data[merged_data['ID_setup_complex'] == complex_ID]
        all_rows.append([name, len(select)])

    count = pd.DataFrame(all_rows, columns=['name', 'frequency'])

    # extension = '.xlsx' # change to '.csv' if necessary
    extension = '.csv' # change to '.excel' if necessary
    all_complex_frequency_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
                                                                       'all_complex_freq')
    count.to_csv(all_complex_frequency_file_name, encoding='utf-8', index=False)

    return all_complex_frequency_file_name


# get all the data IDs (higher & lower) from data_xref_Complex_Complex as dataframe for a given setup complex name
# returns a dataframe with the first element as the higher & lower ID
#############################
def get_complex_data_ID(complex_name):
    # get data xref IDs
    # search_complex_setup_xref_ID df with
    #   the first element has the xref setup value and the second element as the ID for the complex name
    #   e.g., in the lynching DB actor has left values ID 35 and right values 30, 35, 36, 45, 48, 49
    search_complex_setup_xref_ID = setup_xref_Complex_Complex_lib.loc[(setup_xref_Complex_Complex_lib["Name"] == complex_name),  ["ID_setup_xref_complex-complex", "LowerComplex"]]

    complex_data_xref_ID_df = search_complex_setup_xref_ID.merge(data_xref_Complex_Complex_lib, left_on="ID_setup_xref_complex-complex", right_on="ID_setup_xref_complex-complex", how="left")

    print('\n\nNumber of xref records for complex ' + complex_name + ': ' + str(len(complex_data_xref_ID_df)))

    # the first element is all the xref setup values (e.g., 30, 35, 36, 45, 48, 49)
    # the second element is the xref ID of the searched complex (e.g., 35, always the same value)
    # the third element is all the ID of the data_xref_complex-complex
    # the successive elements have all the higher and lower data complex IDs

    return complex_data_xref_ID_df

# find the id of the input complex (name)
# parameter: name of a complex in list type (e.g. [, dataframe of setup_Complex
# return: a dataframe: id, name of the input complex
def get_complex_setup_ID(complex_name):
    if isinstance(complex_name, str):
        complex_name = [complex_name]
    data = setup_Complex_lib[setup_Complex_lib['Name'].isin(complex_name)]
    data = data[['ID_setup_complex', 'Name']]
    data['ID_setup_complex'] = [int(x) for x in data['ID_setup_complex']]
    return data

# given a complex setup name, the function returns its setup ID
def get_complex_setup_ID(complex_name):
    if isinstance(complex_name, str):
        complex_name = [complex_name]
    data = setup_Complex_lib[setup_Complex_lib['Name'].isin(complex_name)]
    data = data[['ID_setup_complex', 'Name']]
    data['ID_setup_complex'] = [int(x) for x in data['ID_setup_complex']]
    return data

# given a complex data ID value, returns its setup ID and name
def get_complex_setup_ID_Name_from_data_ID(complex_data_ID):
    try:
        ID_setup_complex = data_Complex_lib.loc[data_Complex_lib['ID_data_complex'] == complex_data_ID, 'ID_setup_complex']
        ID_setup_complex = ID_setup_complex.iloc[0]
    except:
        ID_setup_complex = -1
        mb.showwarning(title='Warning',
                       message='The ID value ' + str(complex_data_ID) + ' was not found in the table data_Complex_lib.\n\nPlease, enter a different ID and try again')
    if ID_setup_complex > -1:
        complex_name = setup_Complex_lib.loc[setup_Complex_lib['ID_setup_complex'] == ID_setup_complex, 'Name']
        complex_name = complex_name.iloc[0]
    else:
        complex_name = ''
    return ID_setup_complex, complex_name

# given a simplex data ID value, returns its setup ID and name
def get_simplex_setup_ID_Name_from_data_ID(simplex_data_ID):
    try:
        ID_setup_simplex = data_Simplex_lib.loc[data_Simplex_lib['ID_data_simplex'] == simplex_data_ID, 'ID_setup_simplex']
        ID_setup_simplex = ID_setup_simplex.iloc[0]
    except:
        ID_setup_simplex = -1
        mb.showwarning(title='Warning',
                       message='The ID value ' + str(simplex_data_ID) + ' was not found in the table data_Simplex_lib.\n\nPlease, enter a different ID and try again')
    if ID_setup_simplex > -1:
        simplex_name = setup_Simplex_lib.loc[setup_Simplex_lib['ID_setup_simplex'] == ID_setup_simplex, 'Name']
        simplex_name = simplex_name.iloc[0]
    else:
        simplex_name = ''
    return ID_setup_simplex, simplex_name

# @@@@@
# given a df with a column of IDs of data complex (ID_data_complex), returns a df of all complex setup IDs and names

# @@@@@@ Useful function

def get_complex_setup_ID_from_data_ID_ALL(df, inputDir, outputDir):
    #############
    # get setup IDs from data complex IDs
    df = pd.merge(df, data_Complex_lib, how='left', left_on='ID_data_complex', right_on='ID_data_complex')
    # get the setup complex name
    df = pd.merge(df, setup_Complex_lib, how='left', left_on='ID_setup_complex', right_on='ID_setup_complex')
    df = df.rename(columns={'Name': "Complex name"})
    # drop the grammar column which creates a very messy output csv file
    df = df.drop("GrammarRule_Text", axis=1)

    # extension = '.xlsx' # change to '.csv' if necessary
    # outputFilename = IO_files_util.generate_output_file_name('', inputDir, inputDir, extension,
    #                                                            'Complex')

    df = export_df_to_excel(df, inputDir, inputDir, 'NLP_Complex')

    return df

# def get_complex_setup_ID_from_data_ID_ALL(inputDir, outputDir):
#     # get setup IDs from data complex IDs
#     # could use HigherComplex, LowerComplex, or ID_data_xref_complex_complex
#     df = pd.merge(data_Complex_lib, data_xref_Complex_Complex_lib, how='left', left_on='ID_data_complex', right_on='ID')
#     # https://stackoverflow.com/questions/54310497/merge-on-one-column-or-another
#
#
#     # get the setup complex name
#     # could use xrefID instead of ID_setup_complex?
#     # HigherComplex, LowerComplex, and Order are duplicated
#     df1 = pd.merge(df, setup_xref_Complex_Complex_lib, how='left', left_on='ID_setup_complex', right_on='ID_setup_xref_complex-complex')
#     # drop _y columns
#     try: # in some cases HigherComplex_y is not created :-(
#         # drop the _y column
#         df1 = df1.drop('HigherComplex_y', axis=1)
#         # rename column HigherComplex_x to HigherComplex
#         df1 = df1.rename(columns={'HigherComplex_x': "HigherComplex"})
#     except:
#         pass
#
#     try: # in some cases LowerComplex_y is not created :-(
#         # drop the _y column
#         df1 = df1.drop('LowerComplex_y', axis=1)
#         # rename column LowerComplex_x to LowerComplex
#         df1 = df1.rename(columns={'LowerComplex_x': "LowerComplex"})
#     except:
#         pass
#
#     try: # in some cases LowerComplex_y is not created :-(
#         # drop the _y column
#         df1 = df1.drop('Order_y', axis=1)
#         # rename column Order_x to Order
#         df1 = df1.rename(columns={'Order_x': "Order"})
#     except:
#         pass
#
#     df1 = df1.rename(columns={'Name': "Complex name"})
#
#     # ### problem df1 contains some identifiers -1, -2, -3, . all the way to -20
#     #   something is wrong with the merge
#
#     extension = '.xlsx' # change to '.csv' if necessary
#     outputFilename = IO_files_util.generate_output_file_name('', inputDir, inputDir, extension,
#                                                                'complex')
#
#     export_df_to_excel(df1, inputDir, inputDir, outputFilename)
#
#     return df1

def get_simplex_setup_ID(simplex_name):
    if isinstance(simplex_name, str):
        complex_name = [simplex_name]
    data = setup_Simplex_lib[setup_Simplex_lib['Name'].isin(simplex_name)]
    data = data[['ID_setup_simplex', 'Name']]
    data['ID_setup_simplex'] = [int(x) for x in data['ID_setup_simplex']]
    return data

# find the related names of simplexes to the input complex(es)
# parameter:
#   complexes: names of complexes in list type
#   setup_Complex, setup_xref_simplex_complex
# return: related names of simplexes and required simplexes in nested list type

# get_simplex_names_for_complex
def get_simplex_names_for_complex(complexes):
    simplexes = []
    simplexes_required = []
    if isinstance(complexes, str):
        complexes = [complexes]

    for c in complexes:
        complex_ID = get_complex_setup_ID([c])
        if complex_ID.empty:
            continue
        complex_ID = complex_ID.iat[0, 0]
        simplex_children = setup_xref_simplex_complex_lib[setup_xref_simplex_complex_lib['ID_setup_complex'] == complex_ID]
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
def get_complex_children(complex):
    lower_level_complex = []
    has_files = True

    if isinstance(complex, str):
        complex = [complex]

    if setup_Complex_lib.empty or setup_xref_Complex_Complex_lib.empty:
        has_files = False

    if(has_files):
        complex_ID = get_complex_setup_ID(complex)
        complex_ID = complex_ID['ID_setup_complex'].values.tolist()
        lower_level_complex = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['HigherComplex'].isin(complex_ID)]
        lower_level_complex = lower_level_complex[['LowerComplex', 'Name']]
        lower_level_complex = lower_level_complex['Name'].values.tolist()

    return lower_level_complex


# find the one level higher complex of the input complex
# parameter: name of complex in string type, inputDir
# return: a list of parent complex

# @@ what is the difference with the function get_higher_complex?
def get_complex_parents(complex):

    higher_level_complex = []
    has_files = True

    if isinstance(complex, str):
        complex = [complex]

    if setup_Complex_lib.empty or setup_xref_Complex_Complex_lib.empty:
        has_files = False

    if(has_files):
        complex_ID = get_complex_setup_ID(complex)
        complex_ID = complex_ID['ID_setup_complex'].values.tolist()

        higher_level_complex = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['LowerComplex'].isin(complex_ID)]
        higher_level_complex = higher_level_complex['HigherComplex'].values.tolist()
        # higher_level_complex = [str(x) for x in higher_level_complex]

        higher_level_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'].isin(higher_level_complex)]
        higher_level_complex = higher_level_complex[['ID_setup_complex', 'Name']]
        higher_level_complex = higher_level_complex.rename(columns={'ID_setup_complex': 'HigherComplex', 'Name': 'Name'})

        higher_level_complex = higher_level_complex['Name'].values.tolist()

    return higher_level_complex

# given a simplex name, the function returns a list of all the parents that have the simplex amo0ng its children, regardless of whether required
def get_simplex_parent(simplex):

    higher_level_complex = []
    has_files = True

    if isinstance(simplex, str):
        simplex = [simplex]

    if setup_Simplex_lib.empty or setup_xref_simplex_complex_lib.empty:
        has_files = False

    if(has_files):
        simplex_ID = get_simplex_setup_ID(simplex)
        simplex_ID = simplex_ID['ID_setup_simplex'].values.tolist()

        ID_setup_complex = setup_xref_Complex_Complex_lib[setup_xref_simplex_complex_lib['LowerComplex'].isin(complex_ID)]
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

# @@@ what is the difference with the function get_complex_parents?

def get_higher_complex(complex):
    complex_ID = get_complex_setup_ID(complex)
    complex_ID = complex_ID['ID_setup_complex'].values.tolist()

    higher_level_complex = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['LowerComplex'].isin(complex_ID)]
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
def get_simplex_parent(name):
    higher_level_complex = []
    has_files = True

    if isinstance(name, str):
        name = [name]

    global setup_Complex_lib
    if setup_Complex_lib.empty or setup_Simplex_lib.empty or setup_xref_simplex_complex_lib.empty:
        has_files = False

    if(has_files):
        simplex_ID = get_simplex_setup_ID(name)
        simplex_ID = simplex_ID['ID_setup_simplex'].values.tolist()

        complex_ID = setup_xref_simplex_complex_lib[setup_xref_simplex_complex_lib['ID_setup_simplex'].isin(simplex_ID)]
        complex_ID = complex_ID['ID_setup_complex'].values.tolist()

        # reset type of 'ID_setup_complex' in setup_Complex.xlsx
        setup_Complex_lib = setup_Complex_lib[setup_Complex_lib['Name'].notna()]
        setup_Complex_lib[['ID_setup_complex']] = setup_Complex_lib[['ID_setup_complex']].astype(int)
        setup_Complex_lib = setup_Complex_lib[['ID_setup_complex', 'Name']]

        higher_level_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'].isin(complex_ID)]
        higher_level_complex = higher_level_complex['Name'].values.tolist()

    return higher_level_complex

def get_simplex_parent_util(name):
    simplex_ID = get_simplex_setup_ID(name)
    simplex_ID = simplex_ID['ID_setup_simplex'].values.tolist()

    complex_ID = setup_xref_simplex_complex_lib[setup_xref_simplex_complex_lib['ID_setup_simplex'].isin(simplex_ID)]
    complex_ID = complex_ID['ID_setup_complex'].values.tolist()

    # reset type of 'ID_setup_complex' in setup_Complex.xlsx
    setup_Complex = setup_Complex_lib[setup_Complex_lib['Name'].notna()]
    setup_Complex[['ID_setup_complex']] = setup_Complex[['ID_setup_complex']].astype(int)
    setup_Complex = setup_Complex[['ID_setup_complex', 'Name']]

    higher_level_complex = setup_Complex[setup_Complex['ID_setup_complex'].isin(complex_ID)]
    higher_level_complex = higher_level_complex['Name'].values.tolist()

    return higher_level_complex


# find the one level lower complex of the input complex
# parameter: name(s) of complex in list type, dataframe of setup_Complex and setup_xref_Complex_Complex
# return: a dataframe: id, name of one level lower complex of the input complex
def get_lower_complex(complex_name):
    # complex_name MUST be a list []
    if isinstance(complex_name, str):
        complex_name = [complex_name]
    complex_ID = get_complex_setup_ID(complex_name)
    complex_ID = complex_ID['ID_setup_complex'].values.tolist()

    lower_level_complex = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['HigherComplex'].isin(complex_ID)]
    lower_level_complex = lower_level_complex[['LowerComplex', 'Name']]
    if str(list(lower_level_complex.Name.tolist()))=='[]':
        print('\n\nList of complex names below complex(es) ' + str(complex_name) + ': NO COMPLEX OBJECTS AVAILABLE')
    else:
        print('\n\nList of complex names below complex(es) ' + str(complex_name) + ': ' + str(list(lower_level_complex.Name.tolist())))
    # returns a 2-cols dataframe LowerComplex and Name with complex ID and name
    return lower_level_complex



# give the lowest complex of a given complex
# parameter: name of complex in list type, dataframe of setup_Complex and setup_xref_Complex_Complex
# return: all lowest complex names in list type

# NOT USED

# complex_name is a string
def get_lowest_complex(complex_name):
    # get a dataframe of all lower complex names under complex_name
    start = get_lower_complex(complex_name)
    lowest_complex_list = []
    lower(start, lowest_complex_list, complex_name)
    print('\n\nList of lowest complex names below complex ' + str(complex_name) + ': ' + str(lowest_complex_list))
    return lowest_complex_list


# helper method for get_lowest_complex
# to fill lowest_complex_list with the names of complex at the lowest level
# parameter: dataframe returned by get_lower_complex function containing id and name of complex,
#            dataframe of setup_Complex and setup_xref_Complex_Complex
# search_complex MUST be a list []
def lower(start, lowest_complex_list, search_complex):
    # search_complex MUST be a list []
    if isinstance(search_complex, str):
        search_complex = [search_complex]
    start = start['Name'].values.tolist()
    for each in start:
        if each not in search_complex:
            search_complex.append(each)
            temp = get_lower_complex([each])
            if len(temp) == 0:
                lowest_complex_list.append(each)
            else:
                lower(temp, lowest_complex_list, search_complex)

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
# return: a dataframe with 2 columns of data IDs of the highest complex and lowest complex in the given grammar_path with xref
#   e.g. if grammar_path contains the values Participant-S, Actor, Individual, it will return the data IDs for Participant-S and Individual

# get complex_data_IDs_in_grammar_path as a dataframe with 2 columns
def complex_data_IDs_in_grammar_path(grammar_path):
    highest_name = grammar_path[0]
    lowest_name = grammar_path[len(grammar_path) - 1]

    higher = highest_name
    higher = get_complex_setup_ID([higher])
    higher = higher.iat[0, 0]
    ###################
    # commented next line
    grammar_path = grammar_path[1:]
    xrefs = []
    for each in grammar_path:
        lower = get_complex_setup_ID([each])
        lower = lower.iat[0, 0]
        xref = setup_xref_Complex_Complex_lib[(setup_xref_Complex_Complex_lib['HigherComplex'] == higher) & (
                    setup_xref_Complex_Complex_lib['LowerComplex'] == lower)]

        if xref.empty:
            continue
        xref = xref.iat[0, 0]
        higher = lower
        xrefs.append(xref)

    if len(xrefs) == 0:
        print("Returning empty dataframe for: ", grammar_path)
        return pd.DataFrame()

    xref = xrefs.pop()
    data = data_xref_Complex_Complex_lib[data_xref_Complex_Complex_lib['ID_setup_xref_complex-complex'] == xref]
    data = data[['ID_data_complex_HIGHER', 'ID_data_complex_LOWER']]
    # data = data[['ID_data_complex_HIGHER']]
    for each in reversed(xrefs):
        filter = data_xref_Complex_Complex_lib[data_xref_Complex_Complex_lib['ID_setup_xref_complex-complex'] == each]
        filter = filter[['ID_data_complex', 'ID_data_complex_LOWER']]
        data = pd.merge(filter, data, how='right', right_on='ID_data_complex', left_on='ID_data_complex_LOWER')
        data = data[['ID_data_complex_x', 'ID_data_complex_LOWER_y']]
        data = data.rename(columns={'ID_data_complex_x': 'ID_data_complex', 'ID_data_complex_LOWER_y': 'ID_data_complex_LOWER'})

    data_df = data.rename(columns={'ID_data_complex': highest_name, 'ID_data_complex_LOWER': lowest_name})

    # returns a 2-column dataframe of complex_data_IDs_in_grammar_path
    return data_df


# give identifiers corresponding to the complex data ids
# parameter:
#            data: dataframe with column names = names of complexes and data = complex data id
#            cols: names of complexes that are part of column names of data
#            data_Complex
# return: dataframe of complex data id and identifier
def get_IDentifier(data, cols):
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
#           data_xref_simplex_complex, data_Simplex, data_SimplexText
# return: adding corresponding simplex to input data dataframe

# NOT USED
def get_simplex_data(data, cols):
    xref_s_c = data_xref_simplex_complex_lib[['ID_data_simplex', 'ID_data_complex']]
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
#           data_Simplex, data_SimplexText, setup_Complex, data_Complex, data_xref_simplex_complex
# return: dataframe containing individual data id, simplex, identifier

# NOT USED
def get_simplex_IDentifier_one_complextype(complex_name):
    data_Simplex_temp = pd.merge(data_Simplex_lib, data_SimplexText_lib, how='left', left_on='ID_data_date_number_text',
                                 right_on='ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'Value']]

    complex_ID = get_complex_setup_ID(complex_name).iat[0, 0]
    complex_ID = data_Complex_lib[data_Complex_lib['ID_setup_complex'].isin([complex_ID])]
    complex_ID = complex_ID[['ID_data_complex']]
    complex_ID = complex_ID.rename(columns={'ID_data_complex': complex_name[0]})

    complexes = get_IDentifier(complex_ID, complex_name)
    complexes = get_simplex_data(complexes, complex_name)

    return complexes


# give distribution frequency for the input simplex name
# parameter: name: simplex name in list type
# return: dataframe: name, value, frequency
# duplicate function name

# NOT USED

def dist_1(name):
    simplex_ID = get_simplex_setup_ID(name)
    id = simplex_ID.iat[0,0]
    xref_ID = setup_xref_simplex_complex_lib[setup_xref_simplex_complex_lib['ID_setup_simplex']==id].iat[0,0]
    xref_data = data_xref_simplex_complex_lib[data_xref_simplex_complex_lib['ID_setup_xref_simplex-complex']==xref_ID]
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
    id = get_complex_setup_ID([semantic_triplet]).iat[0,0]

    save = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['HigherComplex'] == id]
    save = save['ID_setup_xref_complex-complex'].values.tolist()
    save = save[:3]

    triplet = data_xref_Complex_Complex_lib[data_xref_Complex_Complex_lib['ID_setup_xref_complex-complex'].isin(save)]
    triplet = triplet.pivot_table(
        index = ['ID_data_complex_HIGHER'],
        columns = 'ID_setup_xref_complex-complex',
        values = 'ID_data_complex_LOWER'
    ).reset_index()
    print('=============================================================================')
    print(triplet.head())
    subject_ID = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['Name'] == subject]['ID_setup_xref_complex-complex'].values[0]
    verb_ID = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['Name'] == verb]['ID_setup_xref_complex-complex'].values[0]
    object_ID = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['Name'] == object]['ID_setup_xref_complex-complex'].values[0]

    triplet = triplet.rename(columns = {'ID_data_complex_HIGHER': semantic_triplet, subject_ID: 'S', verb_ID: 'V', object_ID: 'O'})
    triplet["S"] = triplet["S"].fillna(-1).astype(int)
    triplet["S"] = triplet["S"].astype("Int64")

    triplet["V"] = triplet["V"].fillna(-1).astype(int)
    triplet["V"] = triplet["V"].astype("Int64")

    triplet["O"] = triplet["O"].fillna(-1).astype(int)
    triplet["O"] = triplet["O"].astype("Int64")

    complexes = ['S', 'V', 'O']

    for i in range(3):
        complex = complexes[i]

        #ID data complex becomes nan about halfway down the dataframe triplet when merging
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
    simplex_ID = get_simplex_setup_ID([simplex_name])
    simplex_ID = simplex_ID['ID_setup_simplex'].values.tolist()
    xref_simplex_complex_value_new = xref_simplex_complex_value[
        xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_ID)]
    simplexes_combined = xref_simplex_complex_value_new
    simplexes_combined = simplexes_combined.rename(columns={'ID_data_complex': complex_name})
    simplexes_combined['Type'] = complex_name
    return simplexes_combined

dfs_df = pd.DataFrame()

# OLD dfs extended headers working properly
# def dfs(parent, inputDir, outputDir):
#     global dfs_df
#     # export to Excel with one column for each complex object
#     extended_headers = True
#
#     required = crossref.loc[crossref['Name'] == parent, 'Required'].any()
#     if not required:
#         return []
#
#     parent_ID = -1
#     simplex_names, simplex_required_names = get_simplex_names_for_complex([parent])
#     global xref_simplex_complex_ALL_lib
#     if xref_simplex_complex_ALL_lib.empty:
#         xref_simplex_complex_ALL_lib = get_xref_simplex_complex_data_setup_IDs_simplex_values_ALL(inputDir, outputDir)
#
#     # when first going in xref_simplex_complex_ALL will not contain any rows for parent IFF parent does not have any simplex objects; it will have been dropped
#     # we should perhaps not drop nan values to extract the ID_data_complex value for the searched complex
#     # parent_ID = xref_simplex_complex_ALL.loc[(xref_simplex_complex_ALL["Complex name"] == parent), "ID_data_complex"]
#     # parent_ID = parent_ID.reset_index(drop=True)
#     # #
#     # #
#     # try:
#     #     parent_ID = parent_ID.loc[0]
#     # except:
#     #     parent_ID = "NO_ID_FOUND"
#
#     # check setup_xref_simplex-complex to see if the simplex is Required and only use the required simplex
#     NSimplex = len(simplex_required_names[0])
#     if NSimplex >1:
#         mb.showwarning(title='Warning',
#                        message="The complex object '" + str(parent) + "' contains " + str(NSimplex) + " required simplex objects (" + str(', '.join(simplex_required_names[0])) + ") Only the first simplex object (" + str(simplex_required_names[0][0]) + ") will be used to construct the triplet Required simplex objects will have priority over any complex object children.\n\nTO CHANGE THE REQUIRED STATE OF ANY OF THESE SIMPLEX OBJECTS, OPEN THE FILE setup_xref_simplex-complex AND SET THE VALUE OF REQUIRED TO FALSE FOR SELECTED SIMPLEX.")
#
#     if simplex_required_names and len(simplex_required_names[0]) > 0:
#         simplex = simplex_required_names[0][0]
#         simplex_ID = get_simplex_setup_ID([simplex])
#         simplex_ID = simplex_ID['ID_setup_simplex'].values.tolist()
#
#         # get ALL combined simplex values (date, number, text)
#         global simplex_values_ALL_lib
#         if simplex_values_ALL_lib.empty:
#             simplex_values_ALL_lib = get_simplex_values_ALL(inputDir, outputDir)
#
#         xref_simplex_complex_value = pd.merge(
#             data_xref_simplex_complex_lib, simplex_values_ALL_lib,
#             how='left', on='ID_data_simplex'
#         )[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]
#
#         simplex_children_values = xref_simplex_complex_value[
#             xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_ID)
#         ]
#
#         if simplex_children_values.empty:
#             return []
#
#         # add column headers
#         simplex_values = simplex_children_values['Value'].tolist()
#
#         child_rows = []
#
#         # filter the xref_simplex_complex_ALL_lib for the search complex
#         xref_simplex_complex_selected = xref_simplex_complex_ALL_lib[xref_simplex_complex_ALL_lib["Complex name"] == parent]
#
#         for index, row in xref_simplex_complex_selected.iterrows():
#             complex_ID = row.loc["ID_data_complex"]
#             simplex_value = row.loc['Value']
#             simplex_name = row.loc["Simplex name"]
#
#             child_rows.append({
#                 parent + " ID (data_ID)": complex_ID,
#                 "Complex name": parent,
#                 "Simplex name": simplex_name,
#                 "Value": simplex_value,
#             })
#
#         return child_rows
#
#     else:
#         complex_children = get_lower_complex(parent)
#         children = complex_children['Name'].tolist()
#
#         if not children:
#             return []
#
#         append_rows = []
#         # add column headers
#
#         # export to Excel with parent column and only one child complex column
#
#         if extended_headers:
#             # export to Excel with one column for each complex object
#             for child in children:
#                 child_rows = (dfs(child, inputDir, outputDir))
#                 if child_rows:
#                     append_rows.extend(child_rows)
#         else:
#             append_rows_header = ['Search complex name', 'Complex child name', 'Complex child ID (data ID)', 'Simplex name', 'Value']
#             # must extract append_rows
#             # append_rows.extend(child_rows)
#
#         if append_rows:
#             # the top-level searched complex does not have any ID_data_complex values if the complex object has no required simplex and rows would have been dropped
#
#             # should deal with extended_headers:
#             if parent_ID == -1:
#                 append_rows = [{parent: parent, **row} for row in append_rows]
#             else:
#                 append_rows = [{parent + " ID (data_ID)": parent_ID, parent: parent, **row} for row in append_rows]
#         return append_rows


# NEW dfs compact headers working perfectly; extended headers not working

'''
When calling dfs, if you want extended headers, it does NOT modify the global dfs_df. It returns rows instead 
that can be made into another df.

When calling dfs without extended headers, it DOES modify the global dfs_df. No return type is needed. 
'''
def dfs(current_parent, inputDir, outputDir, search_parent=None, extended_headers=False):
    global dfs_df

    parent_ID = -1

    # Keep track of the initial parent that started the search.
    if search_parent is None:
        # timing = 2000
        # IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Warning',
        #                                    f"You are running the parent complex search for " + current_parent.upper() + " with extended_headers = " + str(extended_headers) + ".To change the setting, tick the extended_headers checkbox in the GUI.",
        #                                    False, '', True, '', False)

        search_parent = current_parent
        lower_complex = get_lower_complex(search_parent)
        lower_complex = lower_complex['Name'].values.tolist()
        # grammar_path is a double list [[]], e.g., [[Semantic Triplet, Participant-S]]
        grammar_path = get_grammar_path(search_parent, lower_complex[0])
        # get first element of the double list, e.g., [Semantic Triplet, Participant-S]
        grammar_path = grammar_path[0]

        ID_data_complex_df = complex_data_IDs_in_grammar_path(grammar_path)

        ###################################
        # Aiden should the next lines be indented?
        if dfs_df.empty and not extended_headers:
            headers = ['Parent (search) complex name', 'Parent (search) complex ID (data ID)', 'Complex child name', 'Complex child ID (data ID)', 'Simplex name',
                       'Value']
            dfs_df = pd.DataFrame(columns=headers)

    global xref_simplex_complex_ALL_lib
    global simplex_values_ALL_lib

    # Check if parent is required; only process required complex objects
    required = crossref.loc[crossref['Name'] == current_parent, 'Required'].any()
    if not required:
        return []

    # Get parent_ID if present
    # the xref_simplex_complex_ALL_lib contains a Complex name ONLY IF the complex has any simplex as children, otherwise it is not listed
    if xref_simplex_complex_ALL_lib.empty:
        xref_simplex_complex_ALL_lib = get_xref_simplex_complex_ALL(inputDir, outputDir)

    parent_row = xref_simplex_complex_ALL_lib.loc[
        xref_simplex_complex_ALL_lib["Complex name"] == current_parent, "ID_data_complex"
    ]
    parent_ID = parent_row.iloc[0] if not parent_row.empty else -1

    if parent_row.empty:
        search_parent = current_parent
        ###################################
        lower_complex = get_lower_complex(search_parent)
        lower_complex = lower_complex['Name'].values.tolist()
        grammar_path = get_grammar_path(search_parent, lower_complex[0])
        grammar_path = grammar_path[0]

        parent_row = complex_data_IDs_in_grammar_path(grammar_path)

    # Get simplex names for this parent
    simplex_names, simplex_required_names = get_simplex_names_for_complex([current_parent])

    # Handle required simplex
    if simplex_required_names and len(simplex_required_names[0]) > 0:
        NSimplex = len(simplex_required_names[0])
        if NSimplex > 1:
            # import IO_user_interface_util
            timing = 2000
            IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Warning', f"The complex object '{current_parent}' contains {NSimplex} required simplex objects "
                    f"({', '.join(simplex_required_names[0])}). Only the first simplex object "
                    f"({simplex_required_names[0][0]}) will be used.",
                                               False, '', True, '', False)

            # mb.showwarning(
            #     title='Warning',
            #     message=(
            #         f"The complex object '{current_parent}' contains {NSimplex} required simplex objects "
            #         f"({', '.join(simplex_required_names[0])}). Only the first simplex object "
            #         f"({simplex_required_names[0][0]}) will be used."
            #     )
            # )

        simplex = simplex_required_names[0][0]
        # ... (The logic for finding simplex values remains the same) ...
        # Assume the logic here correctly populates xref_simplex_complex_selected

        # xref_simplex_complex_selected = search_parent, xref_simplex_complex_ALL_lib[
        #     xref_simplex_complex_ALL_lib["Complex name"] == current_parent]
        xref_simplex_complex_selected = xref_simplex_complex_ALL_lib[
            xref_simplex_complex_ALL_lib["Complex name"] == current_parent]

        if xref_simplex_complex_selected.empty:
            return []

        xref_simplex_complex_search_parent = xref_simplex_complex_ALL_lib[
            xref_simplex_complex_ALL_lib["Complex name"] == search_parent]


        complex_data_ID_search_parent_df = get_complex_data_ID(search_parent)

        # xref_simplex_complex_selected_new not used???
        xref_simplex_complex_selected_new = xref_simplex_complex_selected.append(complex_data_ID_search_parent_df)

        append_rows = []
        for _, row in xref_simplex_complex_selected.iterrows():
            if extended_headers:
                child_rows_dict = {
                    current_parent + " ID (data_ID)": row.get("ID_data_complex"),
                    "Complex name": current_parent,
                    "Simplex name": row.get("Simplex name"),
                    "Value": row.get("Value")
                }
            else:
                child_rows_dict = {
                    "Parent (search) complex name": search_parent,
                    ### both Parent (search) complex ID (data ID) and Complex child ID (data ID) are assigned the same value ID_data_complex; MUST CHANGE
                    "Parent (search) complex ID (data ID)": row.get("ID_data_complex"), # temporary value MUST change
                    "Complex child ID (data ID)": row.get("ID_data_complex"),
                    "Complex child name": current_parent,
                    "Simplex name": row.get("Simplex name"),
                    "Value": row.get("Value")
                }
            append_rows.append(child_rows_dict)

        if extended_headers:
            return append_rows
        else:
            # When using fixed headers, append directly to the global DataFrame
            if append_rows:
                df_append = pd.DataFrame(append_rows)
                # Ensure columns are in the correct order for concatenation
                df_append = df_append[dfs_df.columns]
                dfs_df = pd.concat([dfs_df, df_append], ignore_index=True)
            return []

    else:
        # If no required simplex, recurse on children
        complex_children = get_lower_complex(current_parent)
        children = complex_children['Name'].tolist() if not complex_children.empty else []

        if not children:
            return []

        append_rows = []
        if extended_headers:
            # Recurse and gather results for wide format
            for child in children:
                # Pass search_parent in recursive call
                child_rows = dfs(child, inputDir, outputDir, search_parent, extended_headers)
                if child_rows:
                    append_rows.extend(child_rows)

            # This block correctly prepends the current parent's info
            if append_rows:
                if parent_ID != -1:
                    return [{current_parent + " ID (data_ID)": parent_ID, current_parent: current_parent, **row} for row
                            in append_rows]
                else:
                    return [{current_parent: current_parent, **row} for row in append_rows]
            return []  # Return empty if no child rows were found

        else:
            # For fixed headers, just make the recursive calls. They will append to the global df.
            for child in children:
                # Pass search_parent in recursive call
                dfs(child, inputDir, outputDir, search_parent, extended_headers)
            return []

    return []


# get ALL combined simplex values (date, number, text) using the setup_simplex table rather than the xref_simplex-complex table
def get_simplex_values_ALL(inputDir, outputDir):

    global simplex_values_ALL_lib
    name='NLP_Simplex_values_ALL'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        simplex_values_ALL_lib = library[name+'.xlsx']
        simplex_values_ALL = df
        return simplex_values_ALL_lib

    data_Simplex_AllValues = pd.DataFrame()

    # DATE records
    global data_Simplex_lib, data_SimplexDate_lib
    data_Simplex_DateValues = pd.merge(data_Simplex_lib, data_SimplexDate_lib, left_on=
                                          'ID_data_date_number_text', right_on='ID_data_date_number_text')
    # insert the setup simplex name
    data_Simplex_DateValues = pd.merge(setup_Simplex_lib, data_Simplex_DateValues, left_on=
                                          'ID_setup_simplex', right_on='ID_setup_simplex')
    data_Simplex_DateValues = data_Simplex_DateValues.rename(columns={'Name': "Simplex name"})
    # drop all records where ValueType <> 3 (i.e. date)
    data_Simplex_DateValues = data_Simplex_DateValues[data_Simplex_DateValues['ValueType'] == 3]

    # delete column Locked_y
    try: # in some cases Locked_y is not created :-(
        # drop the _y column
        data_Simplex_DateValues = data_Simplex_DateValues.drop('Locked_y', axis=1)
        # rename column Locked_x to Locked
        data_Simplex_DateValues = data_Simplex_DateValues.rename(columns={'Locked_x': "Locked"})
    except:
        pass

    # NUMBER records
    data_Simplex_NumberValues = pd.merge(data_Simplex_lib, data_SimplexNumber_lib, left_on=
                                          'ID_data_date_number_text', right_on='ID_data_date_number_text')
    # insert the setup simplex name
    data_Simplex_NumberValues = pd.merge(setup_Simplex_lib, data_Simplex_NumberValues, left_on=
                                          'ID_setup_simplex', right_on='ID_setup_simplex')
    data_Simplex_NumberValues = data_Simplex_NumberValues.rename(columns={'Name': "Simplex name"})

    # drop all records where ValueType <> 2 (i.e. number)
    data_Simplex_NumberValues = data_Simplex_NumberValues[data_Simplex_NumberValues['ValueType'] == 2]

    # delete column Locked_y
    try: # in some cases Locked_y is not created :-(
        # drop the _y column
        data_Simplex_NumberValues = data_Simplex_NumberValues.drop('Locked_y', axis=1)
        # rename column Locked_x to Locked
        data_Simplex_NumberValues = data_Simplex_NumberValues.rename(columns={'Locked_x': "Locked"})
    except:
        pass

    # STRING records
    data_Simplex_StringValues = pd.merge(data_Simplex_lib, data_SimplexText_lib, left_on=
                                          'ID_data_date_number_text', right_on='ID_data_date_number_text')
    # insert the setup simplex name
    data_Simplex_StringValues = pd.merge(setup_Simplex_lib, data_Simplex_StringValues, left_on=
                                          'ID_setup_simplex', right_on='ID_setup_simplex')

    data_Simplex_StringValues = data_Simplex_StringValues.rename(columns={'Name': "Simplex name"})
    # drop all records where ValueType <> 1 (i.e. string)
    data_Simplex_StringValues = data_Simplex_StringValues[data_Simplex_StringValues['ValueType'] == 1]

    # delete column Locked_y
    try: # in some cases Locked_y is not created :-(
        # drop the _y column
        data_Simplex_StringValues = data_Simplex_StringValues.drop('Locked_y', axis=1)
        # rename column Locked_x to Locked
        data_Simplex_StringValues = data_Simplex_StringValues.rename(columns={'Locked_x': "Locked"})
    except:
        pass

    # combine all three dataframes into one
    data_Simplex_AllValues = pd.DataFrame()
    data_Simplex_AllValues = data_Simplex_DateValues
    data_Simplex_AllValues = pd.concat([data_Simplex_AllValues, data_Simplex_NumberValues], ignore_index=True)
    data_Simplex_AllValues = pd.concat([data_Simplex_AllValues, data_Simplex_StringValues], ignore_index=True).sort_values('ID_data_simplex')
    simplex_values_ALL = data_Simplex_AllValues

    # convert to int all ID fields

    # extension = '.xlsx' # change to '.csv' if necessary
    # outputFilename = IO_files_util.generate_output_file_name('', '', inputDir, extension,
    #                                                            'Simplex_values_ALL')

    simplex_values_ALL_lib = export_df_to_excel(simplex_values_ALL, inputDir, inputDir, 'NLP_Simplex_values_ALL')

    return simplex_values_ALL_lib

# the function builds a complete dataframe of complex & simplex setup and data IDs & simplex values
# return a complete dataframe (which is always invariant for any database);
#   so there is no need to recompute it once it is computed

# it exports a NLP_xref_Simplex-Complex_ALL.xlsx file, converted to pkl that will be used by several other functions

# ONLY THE COMPLEX OBJECTS THAT HAVE SIMPLEX ARE INCLUDED IN THE OUTPUT AND NOT ALL COMPLEX
#   THUS, ACTOR IS NOT INCLUDED IN THE OUTPUT FOR THE LYNCHING DB SINCE THE GRAMMAR FOR ACTOR DO NOT INCLUDE ANY SIMPLEX
def get_xref_simplex_complex_ALL(inputDir, outputDir):
    global xref_simplex_complex_ALL_lib
    name='NLP_xref_Simplex-Complex_ALL'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        xref_simplex_complex_ALL_lib = library[name+'.xlsx']
        xref_simplex_complex_ALL_lib = df
        return xref_simplex_complex_ALL_lib

    xref_simplex_complex_ALL_lib = pd.DataFrame()

     # get ALL simplex values
    global simplex_values_ALL_lib
    if simplex_values_ALL_lib.empty:
        simplex_values_ALL_lib = get_simplex_values_ALL(inputDir, outputDir)

    if not xref_simplex_complex_ALL_lib.empty:
        return xref_simplex_complex_ALL_lib

# deal with the simplex info part -------------------------------------------------------------------------

    name = 'NLP_Simplex'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        xref_simplex_complex_value = pd.read_pickle(f"{inputDir}/{name}.pkl")
    else:
        # add the data xref simplex-complex IDs, setup xref simplex-complex IDs, data complex IDs, data simplex IDs, setup simplex IDs, simplex values
        xref_simplex_complex_value = pd.merge(data_xref_simplex_complex_lib, simplex_values_ALL_lib, how='left',
                                              left_on='ID_data_simplex', right_on='ID_data_simplex')
        # drop all rows of blank ID_setup_simplex because the parent complex has no required simplex, but perhaps mutually exclusive complex (e.g. Number in the lynching DB)
        # this causes problems in subsequent pd.merge
        xref_simplex_complex_value = xref_simplex_complex_value.dropna(subset=['ID_setup_simplex'])

        # do NOT add the simplex setup name; already in xref_simplex_complex_value
        # add the setup XREF simplex name
        xref_simplex_complex_value = pd.merge(xref_simplex_complex_value, setup_xref_simplex_complex_lib, how='left',
                                              left_on='ID_setup_xref_simplex-complex', right_on='ID_setup_xref_simplex-complex')

        # delete columns _y (Order_y, ID_setup_simplex_y)
        try:  # in some cases Locked_y is not created :-(
            # drop the _y column
            xref_simplex_complex_value = xref_simplex_complex_value.drop('Order_y', axis=1)
            xref_simplex_complex_value = xref_simplex_complex_value.drop('ID_setup_simplex_y', axis=1)
            # rename columns _x
            xref_simplex_complex_value = xref_simplex_complex_value.rename(columns={'Order_x': "Order"})
            xref_simplex_complex_value = xref_simplex_complex_value.rename(columns={'ID_setup_simplex_x': "ID_setup_simplex"})
        except:
            pass

        xref_simplex_complex_value = xref_simplex_complex_value.rename(columns={'Name': 'Simplex name (xref)'})

        # select columns
        xref_simplex_complex_value = xref_simplex_complex_value[
            ['ID_setup_simplex', 'Simplex name', 'ID_setup_xref_simplex-complex', 'Simplex name (xref)', 'ID_data_complex', 'ID_data_simplex', 'Value']]

        # drop all rows of blank ID_setup_simplex because the parent complex has no required simplex, but perhaps mutually exclusive complex (e.g. Number in the lynching DB)
        # this causes problems in subsequent pd.merge
        xref_simplex_complex_value = xref_simplex_complex_value.dropna(subset=['ID_setup_simplex'])

    # export simplex file ------------------------------------------------------------------------------
        # outputFilenametemp defined a few lines above to check if it exists to avoid re-computing
        xref_simplex_complex_value = export_df_to_excel(xref_simplex_complex_value, inputDir, outputDir, 'NLP_Simplex') # simplex

# deal with the complex info part -------------------------------------------------------------------------

    name = 'NLP_Complex'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        xref_complex_complex = pd.read_pickle(f"{inputDir}/{name}.pkl")
    else:
        # add complex setup IDs and Names
        # the complex file is exported in the function get_complex_setup_ID_from_data_ID_ALL
        xref_complex_complex = get_complex_setup_ID_from_data_ID_ALL(xref_simplex_complex_value, inputDir, outputDir)
        # select columns
        xref_complex_complex = xref_complex_complex[
            ['ID_data_complex', 'ID_setup_complex', 'Complex name', 'Identifier']]

        # the complex file is exported in the function get_complex_setup_ID_from_data_ID_ALL

# deal with the xref simplex-complex info part -------------------------------------------------------------

    name = 'NLP_xref_Simplex-Complex_ALL'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        xref_complex_complex = pd.read_pickle(f"{inputDir}/{name}.pkl")
    else:
        # merge xref_simplex_complex_value & xref_complex_complex_value
        xref_simplex_complex = pd.merge(xref_complex_complex, xref_simplex_complex_value, how='left',
                                              left_on='ID_data_complex', right_on='ID_data_complex')

        # delete columns _y (Order_y, ID_setup_simplex_y)
        try:  # in some cases Locked_y is not created :-(
            # drop the _y column
            xref_simplex_complex = xref_simplex_complex.drop('ID_setup_simplex_y', axis=1)
            xref_simplex_complex = xref_simplex_complex.drop('ID_data_simplex_y', axis=1)
            xref_simplex_complex = xref_simplex_complex.drop('ID_setup_xref_simplex-complex_y', axis=1)
            xref_simplex_complex = xref_simplex_complex.drop('Simplex name_y', axis=1)
            xref_simplex_complex = xref_simplex_complex.drop('Simplex name (xref)_y', axis=1)
            xref_simplex_complex = xref_simplex_complex.drop('Value_y', axis=1)
            # rename columns _x
            xref_simplex_complex = xref_simplex_complex.rename(columns={'ID_setup_simplex_x': "ID_setup_simplex"})
            xref_simplex_complex = xref_simplex_complex.rename(columns={'ID_data_simplex_x': "ID_data_simplex"})
            xref_simplex_complex = xref_simplex_complex.rename(columns={'ID_setup_xref_simplex-complex_x': "ID_setup_xref_simplex-complex"})
            xref_simplex_complex = xref_simplex_complex.rename(columns={'Simplex name_x': "Simplex name"})
            xref_simplex_complex = xref_simplex_complex.rename(columns={'Simplex name (xref)_x': "Simplex name (xref)"})
            xref_simplex_complex = xref_simplex_complex.rename(columns={'Value_x': "Value"})
        except:
            pass

        # select columns
        xref_simplex_complex = xref_simplex_complex [
            ['ID_setup_complex','Complex name', 'ID_setup_simplex', 'Simplex name', 'ID_data_complex', 'ID_data_simplex', 'Value']]

        # drop all rows of blank ID_setup_simplex because the parent complex has no required simplex, but perhaps mutually exclusive complex (e.g. Number in the lynching DB)
        # should convert to int all ID fields?
        xref_simplex_complex = xref_simplex_complex.dropna(subset=['ID_setup_simplex'])
        # outputFilename with simplex-complex_ALL is set at the top of the function so that it can be checked
        xref_simplex_complex_ALL_lib = export_df_to_excel(xref_simplex_complex, inputDir, inputDir, 'NLP_xref_Simplex-Complex_ALL')

    # xref_simplex_complex_ALL = xref_simplex_complex

    return xref_simplex_complex_ALL_lib


# NOT used
def get_simplex_value_for_complex(complex_name, is_verb, inputDir, outputDir):

    # check whether Group is 0 or 1a, 1b, 1c,. i.e. whether the complex objects are mutually exclusive
    mutually_exclusive = setup_xref_Complex_Complex_lib[['Group', 'Name']]

    # initialize empty dataframe simplexes_combined
    simplexes_combined = pd.DataFrame()

    # # get a list of all the simplex and complex data IDs, setup IDs, and simplex TEXT values
    if xref_simplex_complex_ALL_lib.empty:
        xref_simplex_complex_value = get_xref_simplex_complex_ALL(inputDir, outputDir)

    simplex_names, simplex_required_names = get_simplex_names_for_complex([complex_name])

    # check setup_xref_simplex-complex to see if the simplex is Required and only use the required simplex
    NSimplex = len(simplex_required_names[0])
    if NSimplex >1:
        mb.showwarning(title='Warning',
                       message="The complex object '" + str(complex_name) + "' contains " + str(NSimplex) + " required simplex objects (" + str(', '.join(simplex_required_names[0])) + ") Only the first simplex object (" + str(simplex_required_names[0][0]) + ") will be used to construct the triplet Required simplex objects will have priority over any complex object children.\n\nTO CHANGE THE REQUIRED STATE OF ANY OF THESE SIMPLEX OBJECTS, OPEN THE FILE setup_xref_simplex-complex AND SET THE VALUE OF REQUIRED TO FALSE FOR SELECTED SIMPLEX.")

    # for simplex_name in simplex_names[0]:
    #     simplex_ID = get_simplex_setup_ID([simplex_name], setup_Simplex_lib)
    #     simplex_ID = simplex_ID['ID_setup_simplex'].values.tolist()
    #     xref_simplex_complex_value_new = xref_simplex_complex_value[
    #     xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_ID)]
    #     xref_simplex_complex_value_new = xref_simplex_complex_value_new.rename(columns={'ID_data_complex': subject})
    if len(simplex_required_names[0])>0:
        simplex_ID = get_simplex_setup_ID([simplex_required_names[0][0]])
        simplex_ID = simplex_ID['ID_setup_simplex'].values.tolist()
        xref_simplex_complex_value_new = xref_simplex_complex_value[xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_ID)]
        simplexes_combined = xref_simplex_complex_value_new
        simplexes_combined = simplexes_combined.rename(columns={'ID_data_complex': complex_name})
        simplexes_combined['Type'] = complex_name
    else:
        # get a list of all the simplex names, children of the complex object complex_name
        # get a list of all the simplex values
        if xref_simplex_complex_value.empty:
            xref_simplex_complex_value = get_xref_simplex_complex_ALL(inputDir, outputDir)

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
                simplex_ID = get_simplex_setup_ID([simplex])
                simplex_ID = simplex_ID['ID_setup_simplex'].values.tolist()

                simplex_children_values = xref_simplex_complex_value[
                    xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_ID)]
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
        complex_children_children_IDs = complex_children_children['LowerComplex'].values.tolist()
        # get as dataframe all the simplex names required and not required under all complex_children_children
        simplex_names = setup_xref_simplex_complex_lib[setup_xref_simplex_complex_lib['ID_setup_complex'].isin(complex_children_children_IDs)]
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

                simplex_ID = get_simplex_setup_ID([simplex])
                simplex_ID = simplex_ID['ID_setup_simplex'].values.tolist()


                xref_simplex_complex_value_select = xref_simplex_complex_value[xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_ID)]

                # the grammar_path contains the rewrite rule for a specific object
                #   e.g. Participant-S --> Actor --> Collective actor
                grammar_path = get_grammar_path(complex_name, lower)
                grammar_path = grammar_path[0]

                # @@@@
                if is_verb:
                    head = grammar_path[0]
                    grammar_path = grammar_path[1:]
                    ID_data_list = []
                    for item in grammar_path:
                        grammar_path = [head, item]
                        ID_data_complex_df = complex_data_IDs_in_grammar_path(grammar_path)
                        ID_data_list.append(ID_data_complex_df)

                    combined_ID_data = pd.concat(ID_data_list, ignore_index=True)
                    data = pd.merge(combined_ID_data, xref_simplex_complex_value_select, how='left', left_on=lower,
                                    right_on='ID_data_complex')

                    # data = data[data[complex_name].notna()]

                    # data = data.drop_duplicates(subset=[complex_name])
                    # data = data[[complex_name, lower, 'Value']]
                    # data = data.drop(lower, axis=1)
                    # data[['Type']] = lower
                    #
                    # simplexes.append(data)
                else: # NOT a verb
                    ID_data_complex_df = complex_data_IDs_in_grammar_path(grammar_path)

                    data = pd.merge(ID_data_complex_df, xref_simplex_complex_value_select, how = 'left', left_on = lower, right_on = 'ID_data_complex')
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

                    simplex_ID = get_simplex_setup_ID([simplex])
                    simplex_ID = simplex_ID['ID_setup_simplex'].values.tolist()

                    xref_simplex_complex_value_select = xref_simplex_complex_value[
                        xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_ID)]

                    grammar_path = get_grammar_path(complex_name, lower)
                    grammar_path = grammar_path[0]

                    if is_verb:
                        head = grammar_path[0]
                        grammar_path = grammar_path[1:]
                        ID_data_list = []
                        for item in grammar_path:
                            grammar_path = [head, item]
                            ID_data_complex_df = complex_data_IDs_in_grammar_path(grammar_path)
                            ID_data_list.append(ID_data_complex_df)

                        combined_ID_data = pd.concat(ID_data_list, ignore_index=True)
                        data = pd.merge(combined_ID_data, xref_simplex_complex_value_select, how='left', left_on=lower,
                                        right_on='ID_data_complex')
                        data = data[data[complex_name].notna()]
                        data = data.drop_duplicates(subset=[complex_name])
                        data = data[[complex_name, lower, 'Value']]
                        data = data.drop(lower, axis=1)
                        data[['Type']] = lower

                        simplexes.append(data)
                    else:
                        ID_data_complex_df =complex_data_IDs_in_grammar_path(grammar_path)

                        data = pd.merge(ID_data_complex_df, xref_simplex_complex_value_select, how='left', left_on=lower,
                                        right_on='ID_data_complex')
                        data = data[data[complex_name].notna()]
                        data = data.drop_duplicates(subset=[complex_name])
                        data = data[[complex_name, lower, 'Value']]
                        data = data.drop(lower, axis=1)
                        data[['Type']] = lower

                        simplexes.append(data)

            simplexes_combined = pd.concat(simplexes)

            id_to_IDentifier = data_Complex_lib.set_index('ID_data_complex')['Identifier']
            simplexes_combined['Identifier'] = simplexes_combined[complex_name].map(id_to_IDentifier)

        print(simplexes_combined)

    return simplexes_combined


def get_comment_info(df, object_name, comment_type, inputDir, outputDir):
    outputFiles = []
    if object_name!='':
        object_ID = object_name + ' ID'
        if '*' in comment_type or 'Verifiers' in comment_type:
            data_xref_Comment_modified = data_xref_VComment_lib[['Complex', 'Comment', 'UserID', 'VerifierID']]
        if '*' in comment_type or 'Users' in comment_type:
            # rename ID_data_complex to Complex
            # Aiden Actor ID is wrong
            data_xref_Comment_modified = data_xref_comment_complex_lib.rename(columns={'ID_data_complex': 'Actor ID'})
            data_xref_Comment_modified = data_xref_Comment_modified[[object_ID, 'Comment', 'UserID']]
        df = pd.merge(df, data_xref_Comment_modified, how='left', left_on='Macro Event ID',
                                   right_on=object_ID)
    else: # exporting all comments regardless of selected complex object
        if '*' in comment_type or 'Users' in comment_type:
            df = pd.merge(data_xref_comment_complex_lib, data_Complex_lib, how='left', left_on='ID_data_complex', right_on='ID_data_complex')
            df = pd.merge(df, setup_Complex_lib, how='left', left_on='ID_setup_complex', right_on='ID_setup_complex')
        # Aiden question when * is used we overwrite what was done three lines above..
        if '*' in comment_type or 'Verifiers' in comment_type:
            df = pd.merge(data_xref_VComment_lib, data_Complex_lib, how='left', left_on='Complex', right_on='ID_data_complex')
            df = pd.merge(df, setup_Complex_lib, how='left', left_on='ID_setup_complex', right_on='ID_setup_complex')

    # df = df.drop('Complex', axis=1)

    # get the users and verifiers names in utility_security
    if '*' in comment_type or 'Users' in comment_type:
        utility_Security = utility_Security_lib[['ID', 'UserName']]
        utility_Security = utility_Security.rename(columns={'ID': 'UserID'})
        df = pd.merge(df, utility_Security, how='left', left_on='UserID', right_on='UserID')
        user_name = df.pop('UserName')
        # Aiden question what are these lines?
        userID_IDx = df.columns.get_loc('UserID')
        df.insert(userID_IDx + 1, 'UserName', user_name)

    if '*' in comment_type or 'Verifiers' in comment_type:
        # Aiden question when * is used we overwrite what was done three lines above..
        # Aiden question wrong columns for verifier
        # utility_Security = utility_Security_lib[['ID', 'UserName', 'UserLevel']]
        # utility_Security = utility_Security.rename(columns={'ID': 'VerifierID', 'UserName': 'VerifierName'})
        df = pd.merge(df, utility_Security_lib, how='left', left_on='UserID', right_on='ID')
        df = df.rename(columns={'UserName': 'User name'})

        df = pd.merge(df, utility_Security_lib, how='left', left_on='VerifierID', right_on='ID')
        # df = df.rename(columns={'UserName': 'Verifier name'})
        # select all verifiers names
        verifier_name = utility_Security_lib.pop('UserName')
        # Aiden question what are these lines?
        verifierID_IDx = df.columns.get_loc('VerifierID')
        df.insert(verifierID_IDx + 1, 'Verifier name', verifier_name)
        df = df.rename(columns={'UserName': 'Verifier name'})

    if '*' in comment_type:
        df = df.rename(
        columns={'VerifierName': 'Verifier name', 'UserName': 'User name', 'Name': 'Complex name'})
        # select columns
        df = df[
            ['Comment', 'Complex name', 'Verifier name', 'User name', 'Identifier']]

        extension = '.xlsx' # change to '.csv' if necessary
        outputFilename = IO_files_util.generate_output_file_name('', inputDir, inputDir, extension,
                                                                     'verifiers_users-comments')

        export_df_to_excel(df, inputDir, outputDir, outputFilename)

        outputFiles.apppend(outputFilename)
    elif 'Users' in comment_type:
        df = df.rename(columns={'UserName': 'User name', 'Name': 'Complex name'})
        # select columns
        df = df[
            ['Comment', 'Complex name', 'User name', 'Identifier']]
        extension = '.xlsx' # change to '.csv' if necessary
        outputFilename = IO_files_util.generate_output_file_name('', inputDir, inputDir, extension,
                                                                     'users-comments')

        export_df_to_excel(df, inputDir, outputDir, outputFilename)
        outputFiles.append(outputFilename)
    elif 'Verifiers' in comment_type:
        df = df.rename(columns={'VerifierName': 'Verifier name', 'UserName': 'User name', 'Name': 'Complex name'})
        # select columns
        extension = '.xlsx' # change to '.csv' if necessary
        df = df[
            ['Comment', 'Completed', 'Complex name', 'Verifier name', 'User name', 'Identifier']]
        outputFilename = IO_files_util.generate_output_file_name('', inputDir, inputDir, extension,
                                                                     'verifiers-comments')

        export_df_to_excel(df, inputDir, outputDir, outputFilename)
        outputFiles.append(outputFilename)

    if object_name=='':
        return outputFiles
    else:
        return df

def get_document_info(df=None):
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
def get_path_info_to_complex_object(complex_name, df):

     # S1: find the list of complex names from the top, primary complex value (e.g. Macro event) UP TO the selected complex
    top_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex']==1]['Name'].values[0]
    grammar_path = get_grammar_path(top_complex, complex_name)
    grammar_path = grammar_path[0]

    # Step 3: Map each complex in the grammar_path to its ID
    name_to_ID = {
        name: get_complex_setup_ID([name])['ID_setup_complex'].values[0]
        for name in grammar_path
    }

    # Step 4: Retrieve and store link IDs and relevant data_xref details
    link_data_frames = []
    for i in range(len(grammar_path) - 1):
        higher_ID = name_to_ID[grammar_path[i]]
        lower_ID = name_to_ID[grammar_path[i + 1]]

        # Find setup xref ID for each object in the grammar path
        xref_ID = setup_xref_Complex_Complex_lib[
            (setup_xref_Complex_Complex_lib['HigherComplex'] == higher_ID) &
            (setup_xref_Complex_Complex_lib['LowerComplex'] == lower_ID)
            ]['ID_setup_xref_complex-complex'].values[0]

        # Retrieve and rename relevant data_xref columns
        # @@@@@@ Aiden question wrong fields
        data_xref = data_xref_Complex_Complex_lib[
            data_xref_Complex_Complex_lib['ID_setup_xref_complex-complex'] == xref_ID # setup x ref ID for complex object
            ][['ID_data_complex_HIGHER', 'ID_data_complex_LOWER']].rename(columns={
            'ID_data_complex_HIGHER': f'{grammar_path[i]} ID',
            'ID_data_complex_LOWER': f'{grammar_path[i + 1]} ID'
        })

        # data_xref = data_xref_Complex_Complex_lib[
        #     data_xref_Complex_Complex_lib['ID_setup_xref_complex-complex'] == xref_ID
        #     ][['ID_data_complex', 'ID_data_complex_LOWER']].rename(columns={
        #     'ID_data_complex': f'{grammar_path[i]} ID',
        #     'ID_data_complex_LOWER': f'{grammar_path[i + 1]} ID'
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
    top_complex_IDentifier = df.pop(f'{grammar_path[0]} Identifier')
    df.insert(1, f'{grammar_path[0]} Identifier', top_complex_IDentifier)

    # Final output should have only the relevant grammar_path columns and top complex identifier
    print("Final Hierarchy Data with Simplex Version:", df)
    return df

# get the semantic triplet with simplex
# return: dataframe: Semantic triplet data id, S data id, S Setup name, S Simplex, V data id, V Setup name, V Simplex, O data id, O Setup name, O Simplex
# p.s Setup name = Individual / Organization / Collective actor
def semantic_triplet_simplex(inputDir, outputDir, subject, verb, object, document_info, comment_type, extended_headers):
    semantic_triplet = get_complex_parents(subject)
    triplet = semantic_triplet_complex(semantic_triplet, subject, verb, object)
    # return

    # s = get_simplex_value_for_complex(subject, False, inputDir, outputDir)
    s, outputFilename = get_complex(subject, comment_type, document_info, inputDir, outputDir, extended_headers)
    # s = s.rename(columns={'Value': 'Subject (S)', 'Type': 'S Setup name'})
    s = s.rename(columns={'Value': 'Subject (S)', 'Complex child name': 'S Setup name'})
    # select columns

    # v = get_simplex_value_for_complex(verb, True, inputDir, outputDir)
    v, outputFilename = get_complex(verb, comment_type, document_info, inputDir, outputDir, extended_headers)
    v = v.rename(columns={'Value': 'Verb (V)', 'Complex child name': 'V Setup name'})

    # o = get_simplex_value_for_complex(object, False, inputDir, outputDir)
    o, outputFilename = get_complex(object, comment_type, document_info, inputDir, outputDir, extended_headers)
    o = o.rename(columns={'Value': 'Object (O)', 'Complex child name': 'O Setup name'})

    if isinstance(semantic_triplet, list):
        semantic_triplet = str(semantic_triplet[0])

    # merge the triplet DF with the s, v, o DF
    # Complex child ID (data ID) is the child complex object ID
    ### 10/27/2025 Aiden s, v, o contain the correct data but from here on produce bad results
    simplex_version = pd.merge(triplet, s, how = 'left', left_on = 'S', right_on = 'Complex child ID (data ID)')  # subject)
    simplex_version = pd.merge(simplex_version, v, how = 'left', left_on = 'V', right_on = 'Complex child ID (data ID)') #verb)
    simplex_version = pd.merge(simplex_version, o, how = 'left', left_on = 'O', right_on = 'Complex child ID (data ID)') # object)

    simplex_version = simplex_version.loc[:, [semantic_triplet, 'S', 'S Identifier', 'S Setup name', 'Subject (S)', 'V', 'V Identifier','V Setup name', 'Verb (V)', 'O', 'O Identifier', 'O Setup name', 'Object (O)']]
    simplex_version = simplex_version.rename(columns = {semantic_triplet:'Semantic Triplet ID','S':'S ID','V':'V ID', 'O':'O ID'})
    id_to_IDentifier = data_Complex_lib.set_index('ID_data_complex')['Identifier']
    simplex_version['ST Identifier'] = simplex_version['Semantic Triplet ID'].map(id_to_IDentifier)
    col = simplex_version.pop('ST Identifier')
    target = simplex_version.columns.get_loc('Semantic Triplet ID')
    simplex_version.insert(target+1, 'ST Identifier', col)

    simplex_version = get_path_info_to_complex_object(semantic_triplet, simplex_version)

    if document_info:
        simplex_version = get_document_info(simplex_version)

    if comment_type!='':
        simplex_version = get_comment_info(simplex_version, semantic_triplet, comment_type, inputDir, outputDir)

    # S ID V ID O ID
    simplex_version.drop_duplicates(subset=['S ID', 'V ID', 'O ID'], inplace=True)
    return simplex_version


# prepare the function for the use in main
# get the semantic triplet with simplex
# return: dataframe: Semantic triplet data id, S data id, S Setup name, S Simplex, V data id, V Setup name, V Simplex, O data id, O Setup name, O Simplex
# For example, Type = Individual  / Collective actor / Organization
def semantic_triplet_simplex_main(inputDir, outputDir, macro_event_ID, subject, verb, object, comment_type='', document_info=False, extended_headers=False):

    print('------------------------------------------------------------------------------------------------------------------------')
    print('Subject', subject)
    print('------------------------------------------------------------------------------------------------------------------------')
    print('verb', verb)
    print('------------------------------------------------------------------------------------------------------------------------')
    print('Object', object)

    simplex_version = semantic_triplet_simplex(inputDir, outputDir, subject, verb, object, document_info, comment_type, extended_headers)

    if macro_event_ID != '':
        macro_event_ID = int(macro_event_ID.split()[0])
        simplex_version = simplex_version[simplex_version['Macro Event ID'] == macro_event_ID]

    # if document_info:
    #     simplex_version = simplex_version.drop('Document ID', axis=1)
    #
    # if comment_type == '':
    #     simplex_version = simplex_version.drop(['Comment', 'UserID', 'UserName', 'VerifierID', 'VerifierName'], axis=1)
    # elif comment_type == 'user':
    #     simplex_version = simplex_version.drop(['VerifierID', 'VerifierName'], axis=1)
    # elif comment_type == 'verifier':
    #     simplex_version = simplex_version.drop(['UserID', 'UserName'], axis=1)

    top_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'] == 1]['Name'].values[0]
    semantic_triplet = get_complex_parents(subject)
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

    # extension = '.xlsx' # change to '.csv' if necessary
    extension = '.csv' # change to '.excel' if necessary
    triplet_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, extension, 'triplet (SVO)')
    simplex_version.to_csv(triplet_file_name, encoding='utf-8', index=False)

    return triplet_file_name

def get_time_simplex(inputDir, outputDir, time_label, subject, verb, object, macro_event_ID, comment_type='', document_info=False):

    time = get_time_simplex(inputDir, outputDir, time_label, subject, verb, object)

    # extension = '.xlsx' # change to '.csv' if necessary
    extension = '.csv' # change to '.excel' if necessary
    time_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
                                                                       'time')
    time.to_csv(time_file_name, encoding='utf-8', index=False)

    return time_file_name
#
#    if macro_event_ID != '':
#        macro_event_ID = int(macro_event_ID.split()[0])
#        simplex_version = simplex_version[simplex_version['Macro Event ID'] == macro_event_ID]


# helper method for semantic_triplet_time
# link simplex of time complex with V
# return: a dataframe: Process = data id of complex Process, Indefinite time of day = data id of simplex Indefinite time of day, Time = text of Indefinite time of day
def get_time_simplex(inputDir, outputDir, time_label, subject, verb, object, document_info, comment_type):

    simplexes = get_simplex_names_for_complex(time_label)
    simplex_ID = get_simplex_setup_ID(simplexes[0])
    simplex_ID = simplex_ID['ID_setup_simplex'].values.tolist()
    data_Simplex_temp = pd.merge(data_Simplex_lib, data_SimplexText_lib, how = 'left', on = 'ID_data_date_number_text')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]
    xref_simplex_complex_value = pd.merge(data_xref_simplex_complex_lib, data_Simplex_temp, how = 'left', on = 'ID_data_simplex')
    xref_simplex_complex_value = xref_simplex_complex_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]
    xref_simplex_complex_value = xref_simplex_complex_value[xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_ID)]
    all_path = get_grammar_path(verb, time_label)

    data_df = pd.DataFrame()
    for grammar_path in all_path:
        ID_data_subLevel_df =complex_data_IDs_in_grammar_path(grammar_path)
        ID_data_subLevel_df = ID_data_subLevel_df[ID_data_subLevel_df[verb].notna()]
        ID_data_subLevel_df = ID_data_subLevel_df.drop_duplicates(subset=[verb])
        data_subLevel_df = pd.merge(ID_data_subLevel_df, xref_simplex_complex_value, how='left', left_on=time_label,right_on='ID_data_complex')
        if data_subLevel_df.empty:
            continue
        data_df = pd.concat([data_df, data_subLevel_df])
    result = ', '.join(simplexes[0])
    data_df = data_df.rename(columns = {'Value': result})

    return data_df

# get the semantic triplet (SVO) with time
def semantic_triplet_time(inputDir, outputDir, time_label, macro_event_ID,  subject, verb, object, comment_type='', document_info=False):

    triplet = semantic_triplet_simplex(inputDir, outputDir, subject, verb, object, document_info, comment_type)
    time = get_time_simplex(inputDir, outputDir, time_label, subject, verb, object, document_info, comment_type)

    triplet_with_time = pd.merge(triplet, time, how = 'left', left_on = 'V ID', right_on = verb)
    triplet_with_time = triplet_with_time.drop(verb, axis = 1)
    triplet_with_time = triplet_with_time.rename(columns = {time_label:'Time ID'})
    triplet_with_space = triplet_with_time.dropna(subset=['Time ID'])

    # triplet_with_time = triplet_with_time.rename(columns = {time_label:'Time ID', 'Time':'Time of day'})

    if document_info:
        # move Document column to the last position of the dataframe
        document_ID = triplet_with_time.pop('Document ID')
        triplet_with_time.insert(len(triplet_with_time.columns), 'Document ID', document_ID)

    if comment_type != '':
        # move Comment column to the last position of the dataframe
        comment = triplet_with_time.pop('Comment')
        triplet_with_time.insert(len(triplet_with_time.columns), 'Comment', comment)

    if macro_event_ID != '':
        macro_event_ID = int(macro_event_ID.split()[0])
        triplet_with_time = triplet_with_time[triplet_with_time['Macro Event ID'] == macro_event_ID]

#   if comment_type == '':
#        triplet_with_time = triplet_with_time.drop(['Comment','UserID','UserName','VerifierID','VerifierName'], axis=1)
    if comment_type == 'user':
        triplet_with_time = triplet_with_time.drop(['VerifierID','VerifierName'], axis=1)
    elif comment_type == 'verifier':
        triplet_with_time = triplet_with_time.drop(['UserID','UserName'], axis=1)

    top_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'] == 1]['Name'].values[0]
    semantic_triplet = get_complex_parents(subject)
    if isinstance(semantic_triplet, list):
        semantic_triplet = semantic_triplet[0]
    grammar_path = get_grammar_path(top_complex, semantic_triplet)
    grammar_path = grammar_path[0]

    existing_columns = [f'{col} ID' for col in grammar_path if f'{col} ID' in triplet_with_time.columns]
    if existing_columns:
        triplet_with_time = triplet_with_time.sort_values(existing_columns, ascending=True)

    # extension = '.xlsx' # change to '.csv' if necessary
    extension = '.csv' # change to '.excel' if necessary
    triplet_with_time_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
                                                                          'triplet (SVO) with time')
    triplet_with_time.to_csv(triplet_with_time_file_name, encoding='utf-8', index=False)

    return triplet_with_time_file_name


# helper method for semantic_triplet_space
# link simplex of space complex with V
# return: a dataframe: Process = data id of complex Process, Type of territory = data id of simplex Type of territory, Space = text of Type of territory
def get_space_simplex(inputDir, space_label_var, subject, verb, object):
    simplexes = get_simplex_names_for_complex(space_label_var)
    simplex_ID = get_simplex_setup_ID(simplexes[0])
    simplex_ID = simplex_ID['ID_setup_simplex'].values.tolist()
    data_Simplex_temp = pd.merge(data_Simplex_lib, data_SimplexText_lib, how = 'left', on = 'ID_data_date_number_text')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]
    xref_simplex_complex_value = pd.merge(data_xref_simplex_complex_lib, data_Simplex_temp, how = 'left', on = 'ID_data_simplex')
    xref_simplex_complex_value = xref_simplex_complex_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]
    xref_simplex_complex_value = xref_simplex_complex_value[xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_ID)]
    all_path = get_grammar_path(verb, space_label_var)

    data = pd.DataFrame()
    for grammar_path in all_path:
        ID_data_subLevel_df =complex_data_IDs_in_grammar_path(grammar_path)
        ID_data_subLevel_df = ID_data_subLevel_df[ID_data_subLevel_df[verb].notna()]
        ID_data_subLevel_df = ID_data_subLevel_df.drop_duplicates(subset=[verb])
        data_subLevel_df = pd.merge(ID_data_subLevel_df, xref_simplex_complex_value, how='left', left_on=space_label_var,
                                 right_on='ID_data_complex')
        if data_subLevel_df.empty:
            continue
        data = pd.concat([data, data_subLevel_df])

    result = ', '.join(simplexes[0])
    data = data.rename(columns = {'Value':result})

    return data

def get_space_simplex(inputDir, outputDir, space_label_var, subject, verb, object, macro_event_ID, comment_type='', document_info=False):

    space = get_space_simplex(inputDir, space_label_var, subject, verb, object)
    # extension = '.xlsx' # change to '.csv' if necessary
    extension = '.csv' # change to '.excel' if necessary
    space_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
                                                                       'space')
    space.to_csv(space_file_name, encoding='utf-8', index=False)

    return space_file_name

# prepare the function for the use in main
# get semantic triplet with space
def semantic_triplet_space(inputDir, outputDir, space_label_var, macro_event_ID, subject, verb, object, document_info, comment_type):

    triplet = semantic_triplet_simplex(inputDir, subject, verb, object, document_info, comment_type)
    space = get_space_simplex(inputDir, space_label_var, subject, verb, object, document_info, comment_type)

    triplet_with_space = pd.merge(triplet, space, how='left', left_on='V ID', right_on=verb)
    triplet_with_space = triplet_with_space.drop(verb, axis=1)
    triplet_with_space = triplet_with_space.rename(columns={space_label_var: 'Space ID'})
    triplet_with_space = triplet_with_space.dropna(subset=['Space ID'])

    if macro_event_ID != '':
        macro_event_ID = int(macro_event_ID.split()[0])
        triplet_with_space = triplet_with_space[triplet_with_space['Macro Event ID'] == macro_event_ID]

    # if not document_info:
    #     triplet_with_space = triplet_with_space.drop('Document ID', axis=1)

    # if comment_type == '':
    #     triplet_with_space = triplet_with_space.drop(['Comment','UserID','UserName','VerifierID','VerifierName'], axis=1)
    # elif comment_type == 'user':
    #     triplet_with_space = triplet_with_space.drop(['VerifierID','VerifierName'], axis=1)
    # elif comment_type == 'verifier':
    #     triplet_with_space = triplet_with_space.drop(['UserID','UserName'], axis=1)

    top_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'] == 1]['Name'].values[0]
    semantic_triplet = get_complex_parents(subject)
    if isinstance(semantic_triplet, list):
        semantic_triplet = semantic_triplet[0]
    grammar_path = get_grammar_path(top_complex, semantic_triplet)
    grammar_path = grammar_path[0]

    existing_columns = [f'{col} ID' for col in grammar_path if f'{col} ID' in triplet_with_space.columns]
    if existing_columns:
        triplet_with_space = triplet_with_space.sort_values(existing_columns, ascending=True)
    # extension = '.xlsx' # change to '.csv' if necessary
    extension = '.csv' # change to '.excel' if necessary
    triplet_with_space_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
                                                                       'triplet (SVO) with space')
    triplet_with_space.to_csv(triplet_with_space_file_name, encoding='utf-8', index=False)

    return triplet_with_space_file_name


# get semantic triplet with time and space
def semantic_triplet_time_space(inputDir, outputDir, space_label_var, time_label, macro_event_ID,  subject, verb, object, comment_type='', document_info=False):

    triplet = semantic_triplet_simplex(inputDir, subject, verb, object, document_info, comment_type)

    space = get_space_simplex(inputDir, outputDir, space_label_var, subject, verb, object, document_info, comment_type)
    triplet_with_space = pd.merge(triplet, space, how = 'left', left_on = 'V ID', right_on = verb)
    time = get_time_simplex(inputDir, outputDir, time_label, subject, verb, object)
    triplet_with_time_space = pd.merge(triplet_with_space, time, how = 'left', left_on = 'V ID', right_on = verb)
    # triplet_with_time_space = triplet_with_time_space.drop(verb, axis = 1)
    triplet_with_time_space = triplet_with_time_space.rename(columns = {time_label:'Time ID', space_label_var:'Space ID'})
    triplet_with_time_space = triplet_with_time_space.dropna(subset=['Space ID', 'Time ID'])


    if macro_event_ID != '':
        macro_event_ID = int(macro_event_ID.split()[0])
        triplet_with_time_space = triplet_with_time_space[triplet_with_time_space['Macro Event ID'] == macro_event_ID]

    # if comment_type == '':
    #     triplet_with_time_space = triplet_with_time_space.drop(['Comment','UserID','UserName','VerifierID','VerifierName'], axis=1)
    # elif comment_type == 'user':
    #     triplet_with_time_space = triplet_with_time_space.drop(['VerifierID','VerifierName'], axis=1)
    # elif comment_type == 'verifier':
    #     triplet_with_time_space = triplet_with_time_space.drop(['UserID','UserName'], axis=1)

    top_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'] == 1]['Name'].values[0]
    semantic_triplet = s(subject)
    if isinstance(semantic_triplet, list):
        semantic_triplet = semantic_triplet[0]
    grammar_path = get_grammar_path(top_complex, semantic_triplet)
    grammar_path = grammar_path[0]

    existing_columns = [f'{col} ID' for col in grammar_path if f'{col} ID' in triplet_with_time_space.columns]
    if existing_columns:
        triplet_with_time_space = triplet_with_time_space.sort_values(existing_columns, ascending=True)

    # extension = '.xlsx' # change to '.csv' if necessary
    extension = '.csv' # change to '.excel' if necessary
    triplet_with_space_time_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
                                                                                'triplet (SVO) with space and time')
    triplet_with_time_space.to_csv(triplet_with_space_time_file_name, encoding='utf-8', index=False)

    return triplet_with_space_time_file_name

# Find paths for each simplex under the actors var recursively
def get_complex_paths(complex_name, grammar_path, complete_complexes):
    # Make a copy of the grammar_path to avoid modifying the same list in recursive calls
    current_path = grammar_path + [complex_name]

    # Check if the complex_name is already in the grammar_path to prevent repeated cycles
    if complex_name in grammar_path:
        return

    # Get the simplex names and child complexes for the current complex
    simplex_names = get_simplex_names_for_complex(complex_name)
    child_complexes = get_complex_children(complex_name)

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
def actor_characteristics(inputDir, outputDir, actors_var, macro_event_ID='', comment_type='', document_info=False):

    # build table for complex
    id_complex = get_complex_setup_ID([actors_var]).iat[0, 0]
    table_complex = data_Complex_lib[data_Complex_lib['ID_setup_complex'] == id_complex]

    # @ Hard-coded 'Personal characteristics' must change to reflect the specific setup of a specific project
    names_personal_characteristics = get_lower_complex([actors_var])
    names_personal_characteristics = names_personal_characteristics['Name'].values.tolist()

    data_Simplex_temp = pd.merge(data_Simplex_lib, data_SimplexText_lib, how = 'left', on = 'ID_data_date_number_text')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    xref_simplex_complex_value = pd.merge(data_xref_simplex_complex_lib, data_Simplex_temp, how = 'left', on = 'ID_data_simplex')
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
    # loop through all the children complex objects (e.g. Age, First name and last name, ..)
    for name in complete_complexes:
        grammar_path = path_map[name]
        ID_data_personal_characteristics = complex_data_IDs_in_grammar_path(grammar_path)
        data_personal_characteristics = get_IDentifier(ID_data_personal_characteristics, [name])
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
                simplex_ID = get_simplex_setup_ID([simplex_name])
                simplex_ID = simplex_ID['ID_setup_simplex'].values.tolist()
                xref_simplex_complex_value_new = xref_simplex_complex_value[xref_simplex_complex_value['ID_setup_simplex'].isin(simplex_ID)]
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
    # extension = '.xlsx' # change to '.csv' if necessary
    extension = '.csv' # change to '.excel' if necessary
    individual_characteristics_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
                                                                       'individual characteristics')
    table_simplex.to_csv(individual_characteristics_file_name, encoding='utf-8', index=False)
    print("--------------------------------------------------------------------------------------------------------------------------------------------")
    print(table_simplex)
    return individual_characteristics_file_name


def get_simplex_info(simplex, inputDir, outputDir):
    data = {'information': ['simplex name', 'frequency', 'complex name', 'higher complex', 'lower complex', 'relationship to event']}
    simplex_info = []

    # get data ID and simplex value in text-number-date file
    # data_simplex_temp = pd.concat([data_SimplexDate_lib, data_SimplexNumber_lib, data_SimplexText_lib])
    # get setup and data ID and value of all simplex
    data_simplex = pd.merge(data_Simplex_lib, data_SimplexText_lib, how = 'left', on = 'ID_data_date_number_text')
    data_simplex_selected = data_simplex[data_simplex['Value']==simplex]
    simplex_setup_ID = data_simplex_selected['ID_setup_simplex'].values.tolist()
    simplex_names = setup_Simplex_lib[setup_Simplex_lib['ID_setup_simplex'].isin(simplex_setup_ID)]
    simplex_names = simplex_names['Name'].values.tolist()
    for name in simplex_names:
        simplex_info.append([name])

    # frequency
    temp = pd.merge(data_xref_simplex_complex_lib, data_Simplex_lib, how = 'left', on = 'ID_data_simplex')
    ID_data_date_number_text = temp['ID_data_date_number_text'].values.tolist()
    ID_data_date_number_text = ID_data_date_number_text[0]
    data_xref_simplex_complex_select = temp[temp['ID_data_date_number_text']==ID_data_date_number_text]

    for i in range(len(simplex_info)):
        simplex_setup_ID = get_simplex_setup_ID([simplex_info[i][0]])
        simplex_setup_ID = simplex_setup_ID.iat[0,0]
        data_xref_simplex_complex_select_further = data_xref_simplex_complex_select[data_xref_simplex_complex_select['ID_setup_simplex']==simplex_setup_ID]
        frequency = 0
        if len(data_xref_simplex_complex_select_further) !=0:
            frequency = data_xref_simplex_complex_select_further.groupby(['ID_data_simplex']).count()
            frequency = frequency.iat[0,0]
        simplex_info[i].append(frequency)

    # complex related info
    for i in range(len(simplex_info)):
        simplex_name = simplex_info[i][0]
        complex_name = get_simplex_parent_util([simplex_name])
        if len(complex_name) != 0:
            # highercomplex
            higher_complex = get_higher_complex(complex_name)
            higher_complex = higher_complex['Name'].values.tolist()
            # lowercomplex
            lower_complex = get_lower_complex(complex_name)
            lower_complex = lower_complex['Name'].values.tolist()
            # relationship to event
            # hard-coded value Event, unless renamed?
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

    # extension = '.xlsx' # change to '.csv' if necessary
    extension = '.csv' # change to '.excel' if necessary
    simplex_info_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
                                                                       'simplex information')
    df.to_csv(simplex_info_file_name, encoding='utf-8', index=False)

    # headers = IO_csv_util.get_csvfile_headers(simplex_info_file_name)
    # columns_to_be_plotted_xAxis = IO_csv_util.get_headerValue_from_columnNumber(headers, column_number=0)
    # outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, simplex_info_file_name,
    #                                           outputDir,
    #                                           columns_to_be_plotted_xAxis=[columns_to_be_plotted_xAxis],
    #                                           columns_to_be_plotted_yAxis=['Frequency'],
    #                                           chart_title='Frequency Distribution of Simplex Object\n' + str(
    #                                               simplex_data),
    #                                           # count_var = 1 for columns of alphabetic values
    #                                           count_var=1, hover_label=[],
    #                                           outputFileNameType=str(simplex_data),  # 'gender_bar',
    #                                           column_xAxis_label=str(simplex_data),
    #                                           groupByList=[],
    #                                           plotList=[],
    #                                           chart_title_label='')

    return simplex_info_file_name


# the function returns all the macro events in the database, with their ID and Identifier, to be used in the dropdown menu
def build_macro_event_dropdown_menu(inputDir):
    macro_event_dropdown_menu_list = []

    if os.path.exists(f"{inputDir}/{'setup_Complex'}.pkl"):
        has_files = True
    else:
        has_files = False
    if(has_files):

        macro_event_name = setup_Complex_lib['Name'][0]
        # macro_event_name_ID = get_complex_setup_ID(["Macro Event"], setup_Complex_lib)
        macro_event_name_ID = get_complex_setup_ID([macro_event_name])
        macro_event_name_ID = macro_event_name_ID.iloc[0,0]

        macro_event_IDentifier = data_Complex_lib[data_Complex_lib['ID_setup_complex'] == macro_event_name_ID]

        macro_event_dropdown_menu_list = macro_event_IDentifier.apply(lambda x: f"{x['ID_data_complex']} - {x['Identifier']}", axis=1).tolist()

    return macro_event_dropdown_menu_list