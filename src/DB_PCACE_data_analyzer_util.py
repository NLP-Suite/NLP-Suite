# remove the decimals caused by nan values in one of the dfs
# xref_simplex_complex["ID_data_xref_simplex_complex"] = xref_simplex_complex["ID_data_xref_simplex_complex"].fillna(-1).astype(int)
# xref_simplex_complex["ID_setup_xref_simplex_complex"] = xref_simplex_complex["ID_setup_xref_simplex_complex"].fillna(-1).astype(int)
# xref_simplex_complex["ID_data_simplex"] = xref_simplex_complex["ID_data_simplex"].fillna(-1).astype(int)
# xref_simplex_complex["ID_data_complex"] = xref_simplex_complex["ID_data_complex"].fillna(-1).astype(int)
# xref_simplex_complex["Order"] = xref_simplex_complex["Order"].fillna(-1).astype(int)
# xref_simplex_complex["ID_data_date_number_text"] = xref_simplex_complex["ID_data_date_number_text"].fillna(-1).astype(int)

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
import numpy as np


import pandas as pd
import os
import tkinter.messagebox as mb

import IO_files_util

# pkl version: bump this whenever reading_list rename mappings change.
# build_libraries() checks this version and deletes stale pkl files automatically.
_PKL_VERSION = 4

def _check_pkl_version(inputDir):
    """Check if pkl files in inputDir match the current _PKL_VERSION.
    If not, delete all pkl files so they get regenerated with correct column names."""
    version_file = os.path.join(inputDir, '_pkl_version.txt')
    if os.path.exists(version_file):
        try:
            with open(version_file, 'r') as f:
                stored_version = int(f.read().strip())
            if stored_version == _PKL_VERSION:
                return  # version matches, nothing to do
        except (ValueError, IOError):
            pass  # corrupt or unreadable, treat as stale
    # Version mismatch or missing — delete all pkl files
    pkl_files = [f for f in os.listdir(inputDir) if f.endswith('.pkl')]
    if pkl_files:
        print(f"  Detected stale pkl files (version mismatch). Deleting {len(pkl_files)} pkl files for regeneration...")
        for f in pkl_files:
            try:
                os.remove(os.path.join(inputDir, f))
            except OSError:
                pass
    # Write current version
    with open(version_file, 'w') as f:
        f.write(str(_PKL_VERSION))

# RUN section ______________________________________________________________________________________________________________________________________________________

## OK Pass test of import PCACE
def import_PCACE_tables(inputDir, outputDir):
    dirSearch =os.listdir(inputDir)
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
    # if len(tableList) ==0:
    #     mb.showwarning(title='Warning',
    #                    message='There are no xlsx files in the input directory.\n\nThe script expects a set of xlsx files with overlapping ID fields across files in order to construct an SQLite relational database.\n\nPlease, select an input directory that contains 18 xlsx PC-ACE tables and try again')
    if not "data_Document.xlsx" in str(tableList) and not "data_Complex.xlsx" in str(tableList):
        # mb.showwarning(title='Warning',
        #                message='Although the input directory does contain xlsx files, these files do not have the expected PC-ACE filename (e.g. data_Document, data_Complex).\n\nPlease, select an input directory that contains xlsx PC-ACE tables and try again')
        tableList= []
    # else:
    #     build_libraries(inputDir, outputDir)
    return tableList


# rename the ID fields of each table to a more meaningful value
#   e,g. The ID in setup_Complex.xlsx is renamed ID_setup_complex
#   The ID in setup_xref_complex-complex.xlsx is renamed ID_setup_xref_complex-complex

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
    ('data_xref_Complex-Document.xlsx', {'ID':'ID_data_xref_complex-document', 'Complex':'ID_data_complex', 'Document':'ID_data_document'}),
    ('data_xref_Simplex-Document.xlsx', {'ID':'ID_data_xref_simplex-document', 'ID_datat_simplex':'ID_data_simplex', 'Simplex':'ID_data_simplex', 'Document':'ID_data_document'}),
    ('data_xref_comment-complex.xlsx', {'ID':'ID_data_xref_comment-complex', 'Complex':'ID_data_complex'}),
    ('data_xref_Comment-Simplex.xlsx', {'ID':'ID_data_xref_comment-simplex', 'Simplex':'ID_data_simplex'}),
    ('data_xref_Comment-Document.xlsx', {'ID':'ID_data_xref_comment-document', 'Document':'ID_data_document'}),
    ('data_xref_VComment.xlsx', {'ID':'ID_data_xref_Vcomment'}),
    ('data_xref_VComment-Document.xlsx', {'ID':'ID_data_xref_Vcomment-document'}),
    ('data_VCommentArchive.xlsx', {'ID':'ID_data_Vcomment_archive'}),
    ('utility_Security.xlsx', {})
    # ('NLP_data_Simplex_values_ALL.xlsx', {}),
    # ('NLP_data_xref_Simplex-Complex_ALL.xlsx', {})
]

library ={}

def check_missing(fileName):
    """Read a table file. Tries the given path first (typically .xlsx);
    if not found, tries the .csv version as a fallback for tables that
    exceed Excel's row limit (e.g., Popolo)."""
    if os.path.isfile(fileName):
        fileName_lib = pd.read_excel(fileName)
        # Drop fully-empty rows — Excel files often pad to 1,048,575 rows
        fileName_lib = fileName_lib.dropna(how='all')
        return fileName_lib
    else:
        # Try csv fallback (swap .xlsx → .csv)
        csv_path = os.path.splitext(fileName)[0] + '.csv'
        if os.path.isfile(csv_path):
            print(f"  Reading CSV fallback: {os.path.basename(csv_path)}")
            fileName_lib = pd.read_csv(csv_path, encoding='utf-8', on_bad_lines='skip')
            return fileName_lib
        mb.showwarning(title='Warning',
                    message='The table ' + fileName + ' is missing.\n\nPlease, make sure to export this table from PC-ACE data backend and try again')
        # create an empty dataframe
        return pd.DataFrame()

# returns a df in the form of a pkl file or _lib df
def create_pkl_file(inputDir, filename, colName_toDrop='', dropNanValues=False):
    df = check_missing(os.path.join(inputDir, filename+'.xlsx'))

    # Always apply column renames from reading_list, even for empty DataFrames,
    # so that downstream code can rely on consistent column names.
    for fn, rename_columns in reading_list:
        if fn == filename+'.xlsx':
            if rename_columns:
                df.rename(columns=rename_columns, inplace=True)
            break

    if df.empty:
        library[filename] = df
    else:
        if dropNanValues:
            df = df.dropna(subset= [colName_toDrop])
        library[filename] = df
        pkl_fileName = f"{filename}.pkl"
        df.to_pickle(str(inputDir) + "/" + str(pkl_fileName))
    return df

# def load_lib(inputDir, outputDir):
#
#     import IO_user_interface_util
#     inputDocs =IO_files_util.getFileList('',inputDir, fileType='.xlsx', silent= True)
#     nDocs = len(inputDocs)
#
#     head, tail =os.path.split(inputDir)
#
#     if os.path.exists(f"{inputDir}/{'setup_Complex'}.pkl"):
#         timing =2000
#         IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Loading PC-ACE database.', 'Loading ' + str(
#             nDocs) + ' pkl files from PC-ACE database ' + tail + '\n\nPlease, be patient',
#                                            False, '', True, '', False)
#     else:
#         timing =4000
#         IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Loading PC-ACE database.', 'Loading ' + str(
#             nDocs) + ' xlsx files from PC-ACE database ' + tail + '\n\nPlease, be patient Depending on database size this may take several minutes.\n\nThe algorithm will create a set of pkl files that will make loading MUCH faster in the future',
#                                            False, '', True, '', False)
#
#     print('InputDir', inputDir)
#     i =0
#     NumTables = len(reading_list)
#     # current_path =os.getcwd()
#     for filename, rename_columns in reading_list:
#         parts =filename.split(".")
#         name = parts[0]
#
#         if os.path.exists(f"{inputDir}/{name}.pkl"):
#             df = pd.read_pickle(f"{inputDir}/{name}.pkl")
#             library[filename] = df
#             print(library[filename])
#             i =i+1
#             print('  Filename ' + str(i) + '/' + str(NumTables), filename)
#         else:
#             i =i + 1
#             print('  Filename ' + str(i) + '/' + str(NumTables), filename)
#             df = check_missing(os.path.join(inputDir, filename))
#             if df.empty:
#                 library[filename] ={}
#             else:
#                 if rename_columns:
#                     df.rename(columns=rename_columns, inplace= True)
#                 library[filename] = df
#                 # save df as pkl file
#                 df.to_pickle(str(inputDir) + "/" + str(f"{name}.pkl"))
#
#     build_libraries(inputDir, outputDir)
#     build_NLP_libraries(inputDir, outputDir)
#
#     return



def build_NLP_libraries(inputDir, outputDir):
    global data_simplex_values_ALL_lib, data_xref_simplex_complex_ALL_lib
    name ='NLP_data_simplex_values_ALL'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name + '.xlsx'] = df
        data_simplex_values_ALL_lib = library[name + '.xlsx']
    else:
        data_simplex_values_ALL_lib =build_data_simplex_values_ALL_lib(inputDir, outputDir)

    name ='NLP_data_xref_Simplex-Complex_ALL'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name + '.xlsx'] = df
        data_xref_simplex_complex_ALL_lib = library[name + '.xlsx']
    else:
        data_xref_simplex_complex_ALL_lib =build_data_xref_simplex_complex_ALL_lib(inputDir, outputDir)

    return

# builds pkl files from Excel files
# pkl files are MUCH faster to open and read
def build_libraries(inputDir, outputDir):
    global setup_Complex_lib, setup_Simplex_lib, setup_xref_Complex_Complex_lib, crossref, setup_xref_simplex_complex_lib, data_Simplex_lib, data_SimplexText_lib, data_SimplexNumber_lib, data_SimplexDate_lib, data_Complex_lib, data_xref_Complex_Complex_lib, data_xref_AnyComplex_Complex_lib, data_xref_simplex_complex_lib, data_xref_Document_lib, data_xref_Simplex_Simplex_Document_lib, data_xref_Complex_Document_lib, data_xref_comment_complex_lib, data_xref_Comment_Document_lib, data_xref_VComment_lib, data_xref_VComment_Document_lib, utility_Security_lib, data_simplex_values_ALL_lib, data_xref_simplex_complex_ALL_lib, data_Document_lib
    # global dfs_df
    # headers = ['Parent (search) complex name', 'Parent (search) complex ID (data ID)', 'Complex child name', 'Complex child ID (data ID)', 'Simplex name', 'Value']
    # dfs_df = pd.DataFrame(columns=headers)

    import IO_user_interface_util

    # Check pkl version — delete stale pkl files if rename mappings have changed
    _check_pkl_version(inputDir)

    inputDocs = IO_files_util.getFileList('',inputDir, fileType='.pkl', silent= True)
    nDocs = len(inputDocs)

    head, tail =os.path.split(inputDir)

    if nDocs > 20: # there should be at least 20 pkl files, in fact as many as xlsx files
        timing = 2000
        IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Loading PC-ACE database.', 'Loading ' + str(
            nDocs) + ' pkl files from PC-ACE database ' + tail + '\n\nPlease, be patient...',
                                           False, '', True, '', False)
    else:
        inputDocs =IO_files_util.getFileList('', inputDir, fileType='.xlsx', silent= True)
        nDocs = len(inputDocs)
        timing =4000
        IO_user_interface_util.timed_alert(GUI_util.window, timing, 'Loading PC-ACE database.', 'Loading ' + str(
            nDocs) + ' xlsx files from PC-ACE database ' + tail + '\n\nThe algorithm will create a set of pkl files that will make loading MUCH faster in the future.\n\nPlease, be patient ... Depending on database size this may take several minutes.',
                                           False, '', True, '', False)
    print('InputDir', inputDir)

    # loading/creating all pkl files
    name ='setup_Complex'
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
        # Drop fully-empty rows (Excel padding to 1,048,575 rows)
        df = df.dropna(how='all')
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

    name='data_Document'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_Document_lib = library[name+'.xlsx']
    else:
        data_Document_lib = create_pkl_file(inputDir, name)

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

    # ── Build fast lookup dictionaries for O(1) access ──────────────────
    _build_lookup_indexes()

    print('Done importing libraries.')


# build extra libraries

# get ALL combined simplex values (date, number, text) using the setup_simplex table rather than the xref_simplex-complex table
def build_data_simplex_values_ALL_lib(inputDir, outputDir):

    ""
# Inner Merge (how='inner'): The default. It only keeps rows where the join keys exist in both DataFrames. It is like an intersection of sets.
# Left Merge (how='left'): Keeps all rows from the left DataFrame. If there is no match in the right DataFrame, the resulting right columns will contain NaN.
# Right Merge (how='right'): Keeps all rows from the right DataFrame. If there is no match in the left DataFrame, the resulting left columns will contain NaN.
    ""

    global data_simplex_values_ALL_lib
    name='NLP_data_Simplex_values_ALL'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_simplex_values_ALL_lib = library[name+'.xlsx']
        simplex_values_ALL = df
        return data_simplex_values_ALL_lib

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
    data_Simplex_DateValues = data_Simplex_DateValues[data_Simplex_DateValues['ValueType'] ==3]

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
    data_Simplex_NumberValues = data_Simplex_NumberValues[data_Simplex_NumberValues['ValueType'] ==2]

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
    data_Simplex_StringValues = data_Simplex_StringValues[data_Simplex_StringValues['ValueType'] ==1]

    # delete column Locked_y
    try: # in some cases Locked_y is not created :-(
        # drop the _y column
        data_Simplex_StringValues = data_Simplex_StringValues.drop('Locked_y', axis=1)
        # rename column Locked_x to Locked
        data_Simplex_StringValues = data_Simplex_StringValues.rename(columns={'Locked_x': "Locked"})
    except:
        pass

    # combine all three date, number, text dataframes into one
    data_Simplex_AllValues = pd.DataFrame()
    data_Simplex_AllValues = data_Simplex_DateValues
    data_Simplex_AllValues = pd.concat([data_Simplex_AllValues, data_Simplex_NumberValues], ignore_index= True)
    data_Simplex_AllValues = pd.concat([data_Simplex_AllValues, data_Simplex_StringValues], ignore_index= True).sort_values('ID_data_simplex')
    data_simplex_values_ALL = data_Simplex_AllValues

    # convert to int all ID fields

    # extension ='.xlsx' # change to '.csv' if necessary
    # outputFilename =IO_files_util.generate_output_file_name('', '', inputDir, extension,
    #                                                            'Simplex_values_ALL')

    data_simplex_values_ALL_lib =export_df_to_excel(data_simplex_values_ALL, inputDir, inputDir, 'NLP_data_Simplex_values_ALL')

    return data_simplex_values_ALL_lib

# the function builds a complete dataframe of complex & simplex setup and data IDs & simplex values
# return a complete dataframe (which is always invariant for any database);
#   so there is no need to recompute it once it is computed

# it exports a NLP_xref_Simplex-Complex_ALL.xlsx file, converted to pkl that will be used by several other functions

# ONLY THE COMPLEX OBJECTS THAT HAVE SIMPLEX ARE INCLUDED IN THE OUTPUT AND NOT ALL COMPLEX
#   THUS, ACTOR IS NOT INCLUDED IN THE OUTPUT FOR THE LYNCHING DB SINCE THE GRAMMAR FOR ACTOR DO NOT INCLUDE ANY SIMPLEX
def build_data_xref_simplex_complex_ALL_lib(inputDir, outputDir):
    global data_xref_simplex_complex_ALL_lib
    name='NLP_data_xref_Simplex-Complex_ALL'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        df = pd.read_pickle(f"{inputDir}/{name}.pkl")
        library[name+'.xlsx'] = df
        data_xref_simplex_complex_ALL_lib = library[name+'.xlsx']
        data_xref_simplex_complex_ALL_lib = df
        return data_xref_simplex_complex_ALL_lib

    data_xref_simplex_complex_ALL_lib = pd.DataFrame()

     # get ALL simplex values
    global data_simplex_values_ALL_lib
    if data_simplex_values_ALL_lib.empty:
        data_simplex_values_ALL_lib =build_data_simplex_values_ALL_lib(inputDir, outputDir)

    if not data_xref_simplex_complex_ALL_lib.empty:
        return data_xref_simplex_complex_ALL_lib

# SIMPLEX

# deal with the simplex info part -------------------------------------------------------------------------

    name ='NLP_data_xref_Simplex'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        xref_simplex_complex = pd.read_pickle(f"{inputDir}/{name}.pkl")
    else:
        # add the data xref simplex-complex IDs, setup xref simplex-complex IDs, data complex IDs, data simplex IDs, setup simplex IDs, simplex values
        xref_simplex_complex = pd.merge(data_xref_simplex_complex_lib, data_simplex_values_ALL_lib, how='left',
                                              left_on='ID_data_simplex', right_on='ID_data_simplex')
        # drop all rows of blank ID_setup_simplex because the parent complex has no required simplex, but perhaps mutually exclusive complex (e.g. Number in the lynching DB)
        # this causes problems in subsequent pd.merge
        xref_simplex_complex = xref_simplex_complex.dropna(subset= ['ID_setup_simplex'])

        # do NOT add the simplex setup name; already in xref_simplex_complex_value
        # add the setup XREF simplex name
        # output OK
        if 'ID_setup_xref_simplex-complex' in xref_simplex_complex.columns and 'ID_setup_xref_simplex-complex' in setup_xref_simplex_complex_lib.columns:
            xref_simplex_complex = pd.merge(xref_simplex_complex, setup_xref_simplex_complex_lib, how='left',
                                                  left_on='ID_setup_xref_simplex-complex', right_on='ID_setup_xref_simplex-complex')

            # delete columns _y (Order_y, ID_setup_simplex_y)
            try:  # in some cases Locked_y is not created :-(
                # drop the _y column
                xref_simplex_complex = xref_simplex_complex.drop('Order_y', axis=1)
                xref_simplex_complex = xref_simplex_complex.drop('ID_setup_simplex_y', axis=1)
                # rename columns _x
                xref_simplex_complex = xref_simplex_complex.rename(columns={'Order_x': "Order"})
                xref_simplex_complex = xref_simplex_complex.rename(columns={'ID_setup_simplex_x': "ID_setup_simplex"})
            except:
                pass

            xref_simplex_complex = xref_simplex_complex.rename(columns={'Name': 'Simplex name (xref)'})
            xref_simplex_complex = xref_simplex_complex.rename(columns={'Required': 'Simplex required'})
        else:
            print(f"  WARNING: 'ID_setup_xref_simplex-complex' column not found. Skipping setup xref simplex merge.")

        # select columns (only those that exist — some databases may not have all columns)
        desired_simplex_cols = ['ID_setup_simplex', 'Simplex name', 'Simplex required', 'ID_setup_xref_simplex-complex', 'Simplex name (xref)', 'ID_data_complex', 'ID_data_simplex', 'ID_data_xref_simplex-complex', 'Value']
        available_simplex_cols = [c for c in desired_simplex_cols if c in xref_simplex_complex.columns]
        xref_simplex_complex = xref_simplex_complex[available_simplex_cols]

        # drop all rows of blank ID_setup_simplex because the parent complex has no required simplex, but perhaps mutually exclusive complex (e.g. Number in the lynching DB)
        # this causes problems in subsequent pd.merge
        xref_simplex_complex = xref_simplex_complex.dropna(subset= ['ID_setup_simplex'])

# EXPORT simplex file ------------------------------------------------------------------------------
        # outputFilenametemp defined a few lines above to check if it exists to avoid re-computing
        # check and OK
        xref_simplex_complex = export_df_to_excel(xref_simplex_complex, inputDir, outputDir, 'NLP_data_xref_Simplex') # simplex

# COMPLEX

# deal with the complex info part -------------------------------------------------------------------------

    name ='NLP_data_xref_Complex'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        xref_complex_complex = pd.read_pickle(f"{inputDir}/{name}.pkl")
    else:
# STEP 1
        # add the data xref complex-complex IDs, setup xref complex-complex IDs, data complex IDs, data simplex IDs, setup simplex IDs, simplex values
        # 'inner'???


        if 'ID_data_complex_HIGHER' not in data_xref_Complex_Complex_lib.columns or 'ID_data_complex_LOWER' not in data_xref_Complex_Complex_lib.columns:
            print(f"  WARNING: data_xref_Complex_Complex_lib missing expected columns. Has: {list(data_xref_Complex_Complex_lib.columns)}")
            print(f"  Skipping complex-complex merge. Try deleting pkl files in the input directory and reloading.")
            xref_complex_complex_step1 = data_Complex_lib.copy()
        else:
            m1 = data_Complex_lib.merge(data_xref_Complex_Complex_lib, left_on="ID_data_complex", right_on='ID_data_complex_HIGHER')

            m2 = data_Complex_lib.merge(data_xref_Complex_Complex_lib, left_on="ID_data_complex", right_on='ID_data_complex_LOWER')

            xref_complex_complex_step1 = pd.concat([m1, m2], ignore_index=True)

        xref_complex_complex_step1.drop_duplicates(inplace=True)

        # should 'ID_data_xref_complex-complex' be ID_data_complex_HIGHER or LOWER?

        # drop all rows of blank ID_setup_simplex because the parent complex has no required simplex, but perhaps mutually exclusive complex (e.g. Number in the lynching DB)
        # this causes problems in subsequent pd.merge

        # xref_complex_complex_step1 = xref_complex_complex_step1.dropna(subset= ['ID_setup_complex'])

# EXPORT STEP 1
#         xref_complex_complex_step1 = export_df_to_excel(xref_complex_complex_step1, inputDir, inputDir,
#                                                 'NLP_data_xref_Complex_step1', False)

# STEP 2 add the setup complex name and setup xref complex name

        modified_setup_Complex_lib = setup_Complex_lib.drop(columns=["GrammarRule_Text"]) # Drop the column of Grammar rules which adds considerably to the file size and is not necessary

        # add the setup complex name
        xref_complex_complex_step2 = pd.merge(xref_complex_complex_step1, modified_setup_Complex_lib,
                                              left_on='ID_setup_complex', right_on='ID_setup_complex')

        xref_complex_complex_step2 = xref_complex_complex_step2.rename(columns={'Name': "Complex name"})

# EXPORT STEP 2
#         xref_complex_complex_step2 = export_df_to_excel(xref_complex_complex_step2, inputDir, inputDir, 'NLP_data_xref_Complex_step2', False)

# STEP 3 add the setup XREF complex name, and setup higher and lower
        if 'ID_setup_xref_complex-complex' in xref_complex_complex_step2.columns and 'ID_setup_xref_complex-complex' in setup_xref_Complex_Complex_lib.columns:
            xref_complex_complex_step3 = pd.merge(xref_complex_complex_step2, setup_xref_Complex_Complex_lib,
                                                  left_on='ID_setup_xref_complex-complex', right_on='ID_setup_xref_complex-complex')

            xref_complex_complex_step3 = xref_complex_complex_step3.rename(columns={'Name': "Child name"})
            xref_complex_complex_step3 = xref_complex_complex_step3.rename(columns={'Required': "Complex required"})
            xref_complex_complex_step3 = xref_complex_complex_step3.rename(columns={'Group': "Complex mutually exclusive"})
        else:
            print(f"  WARNING: 'ID_setup_xref_complex-complex' column not found. Skipping setup xref complex merge.")
            xref_complex_complex_step3 = xref_complex_complex_step2

# select and rearrange columns
        desired_step3_cols = ['ID_setup_complex', 'Complex name', 'ID_setup_xref_complex-complex', 'Child name', 'Complex required', 'Complex mutually exclusive', 'ID_data_complex', 'ID_data_xref_complex-complex', 'ID_data_complex_HIGHER', 'ID_data_complex_LOWER', 'Identifier']
        available_step3_cols = [c for c in desired_step3_cols if c in xref_complex_complex_step3.columns]
        xref_complex_complex_step3 = xref_complex_complex_step3[available_step3_cols]

# EXPORT STEP 3
#         xref_complex_complex_step3 = export_df_to_excel(xref_complex_complex_step3, inputDir, inputDir, 'NLP_data_xref_Complex_step3', False)

# xref simplex-complex

# STEP 4 - FINAL
# deal with the xref simplex-complex info part -------------------------------------------------------------

    name ='NLP_data_xref_Simplex-Complex_ALL'
    if os.path.exists(f"{inputDir}/{name}.pkl"):
        xref_complex_complex = pd.read_pickle(f"{inputDir}/{name}.pkl")
    else:
        # merge xref_simplex_complex_value & xref_complex_complex_value
        # Use left merge to keep all complex-complex relationships even when a complex has no direct simplex children
        xref_simplex_complex_step4 = pd.merge(xref_complex_complex_step3, xref_simplex_complex,
                                              left_on='ID_data_complex', right_on='ID_data_complex', how='left')

        # select and rearrange columns
        # need 'ID_data_xref_complex-complex' -----------------------------------------
        desired_all_cols = ['ID_setup_complex','Complex name', 'ID_setup_xref_complex-complex', 'Child name', 'Complex required', 'Complex mutually exclusive', 'ID_setup_simplex', 'Simplex name', 'ID_setup_xref_simplex-complex','Simplex name (xref)', 'Simplex required', 'ID_data_complex', 'ID_data_xref_complex-complex', 'ID_data_complex_HIGHER', 'ID_data_complex_LOWER', 'Identifier', 'ID_data_simplex', 'ID_data_xref_simplex-complex', 'Value']
        available_all_cols = [c for c in desired_all_cols if c in xref_simplex_complex_step4.columns]
        xref_simplex_complex_step4 = xref_simplex_complex_step4[available_all_cols]

        # Note: do NOT drop rows with blank ID_setup_simplex here — complexes without
        # direct simplex children (e.g., Semantic Triplet, Participant-S) are valid
        # and needed for the hierarchy traversal
        # outputFilename with simplex-complex_ALL is set at the top of the function so that it can be checked

# EXPORT STEP 4 FINAL
        data_xref_simplex_complex_ALL_lib = export_df_to_excel(xref_simplex_complex_step4, inputDir, inputDir, 'NLP_data_xref_Simplex-Complex_ALL')

    return xref_simplex_complex_step4



# check if a required document can be found.
# OK pass checks and returns a dataframe or a boolean set to False if the file is not found.


def export_df_to_excel(df, inputDir, outputDir, outputFilename, create_pkl_file=True):
    if hasattr(inputDir, 'get'):
        inputDir = inputDir.get()
    if hasattr(outputDir, 'get'):
        outputDir = outputDir.get()    # import IO_user_interface_util
    timing =2000
    EXCEL_MAX_ROWS = 1048576
    if len(df) > EXCEL_MAX_ROWS:
        # DataFrame exceeds Excel row limit — save as CSV instead
        CSVoutputFilename = outputDir + os.sep + outputFilename + '.csv'
        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Saving dataframe to CSV',
            'Saving dataframe to CSV file ' + CSVoutputFilename +
            f'\n\n(Too large for Excel: {len(df):,} rows exceeds the {EXCEL_MAX_ROWS:,} Excel limit)'
            '\n\nPlease, be patient... Depending upon the size of the dataframe this may take a few minutes.')
        df.to_csv(CSVoutputFilename, index=False, encoding='utf-8')
    else:
        ExceloutputFilename = outputDir + os.sep + outputFilename + '.xlsx'
        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Saving dataframe to Excel','Saving dataframe to Excel file ' + ExceloutputFilename + '\n\n\nPlease, be patient... Depending upon the size of the dataframe this may take a few minutes.')
        # save files to input directory since these are permanent files
        df.to_excel(ExceloutputFilename, index=False) # encoding='utf-8'
    if create_pkl_file:
        library[outputFilename] = df
        # save df as pkl file
        df.to_pickle(str(inputDir) + "/" + str(f"{outputFilename}.pkl"))
    return df


def create_sqlite_from_pcace(inputDir, outputDir):
    """Export all loaded PC-ACE library DataFrames to a single SQLite database.

    Parameters
    ----------
    inputDir : str
        The PC-ACE input directory. The .sqlite file is saved here alongside the xlsx files.
    outputDir : str
        (Kept for backward compatibility but no longer used for database location.)

    Returns
    -------
    str or None
        Path to the created SQLite file, or None on failure.
    """
    import sqlite3

    if not library:
        print("  WARNING: No PC-ACE library loaded. Please load a database first.")
        return None

    head, tail = os.path.split(inputDir)
    db_name = tail.replace(' ', '_') + '.sqlite'
    db_path = os.path.join(inputDir, db_name)

    # Remove existing database so we start fresh
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError as e:
            print(f"  WARNING: Could not remove existing database: {e}")
            return None

    # Build a lookup of column renames from reading_list so we can ensure
    # every table has the correct renamed columns even if the library entry
    # was loaded from a stale pkl or without renames.
    _rename_lookup = {}
    for fn, rename_cols in reading_list:
        if rename_cols:
            base = os.path.splitext(fn)[0]
            _rename_lookup[base] = rename_cols

    conn = sqlite3.connect(db_path)
    table_count = 0

    for key, df in library.items():
        # Skip non-DataFrame entries (empty dicts from missing tables)
        if not isinstance(df, pd.DataFrame) or df.empty:
            continue

        # Build a clean table name from the library key
        # e.g., 'setup_Complex.xlsx' → 'setup_Complex', 'NLP_data_xref_Simplex' → 'NLP_data_xref_Simplex'
        table_name = key.replace('.xlsx', '').replace('-', '_').replace(' ', '_')

        try:
            # Ensure column renames from reading_list are applied.
            # The library entry may have been loaded from pkl without renames.
            base_key = key.replace('.xlsx', '')
            export_df = df
            if base_key in _rename_lookup:
                # Only rename columns that still have the old names
                applicable = {old: new for old, new in _rename_lookup[base_key].items()
                              if old in df.columns and old != new}
                if applicable:
                    export_df = df.copy()
                    export_df.rename(columns=applicable, inplace=True)

            # Handle duplicate column names (e.g., two columns both renamed to ID_data_complex)
            # by appending _2, _3, etc. — SQLite does not allow duplicate column names.
            cols = list(export_df.columns)
            if len(cols) != len(set(cols)):
                seen = {}
                new_cols = []
                for c in cols:
                    if c in seen:
                        seen[c] += 1
                        new_cols.append(f"{c}_{seen[c]}")
                    else:
                        seen[c] = 1
                        new_cols.append(c)
                if export_df is df:
                    export_df = df.copy()
                export_df.columns = new_cols

            export_df.to_sql(name=table_name, con=conn, index=False, if_exists='replace')
            table_count += 1
        except Exception as e:
            print(f"  WARNING: Could not export table '{table_name}': {e}")

    conn.close()

    if table_count == 0:
        print("  WARNING: No tables were exported to SQLite.")
        os.remove(db_path)
        return None

    print(f"\n  Exported {table_count} tables to SQLite database: {db_path}")
    return db_path


#######################################################################################################

#@
### SETUP TABLES ############################################################################################

# Functions that deal with the grammar of data collection as found in the setup tables.
# The grammar objects are  specific to a specific research project
#   e.g., Attore may be the grammar, setup name in the fascism project, but Actor in the lynching project
#

###############################################################################################


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
        if command ==False:
            return

    try:
        df = pd.read_excel(excel_file)

        column_data = df[column_name].dropna().astype(str)

        #replacing extra '_x00D_' strings that appear
        column_data = column_data.str.replace('_x000d_', '', regex=False)
        column_data = column_data.str.replace('_x000D_', '', regex=False)

        grammar ='LEGENDA\n\n   -->  Rewrite rule (the object to the left of --> can be rewritten in terms of the object(s) to the right)\n   ++   Hierarchical object (e.g., Macro event, Event, Semantic triplet)\n   +    Complex object (no + Simplex object)\n   <>   Can be rewritten\n   []   Optional object\n   {}   Multiples allowed\n   (1a) (1b) (1c)... mutually exclusive objects' \
                  '\n                      (e.g., <+Actor> rewritten as <+Individual (1a) <+Collective actor (1b). Both CANNOT be entered; it is one or the other).\n\n'


        with open(output_file, 'w', encoding='utf-8') as f:
            for i, row in enumerate(column_data, start=1):
                # f.write(f"{i}    {row}\n")
                # Aiden i is printed only the first time
                # place row number right before each row object, since the row number is sometimes referred to in the rewrite rules for objcets already rewritten
                row =row.replace(row,row[:1] + '\nLine ' + str(i) + ' ' + row[1:])
                grammar= grammar+row
            print('Grammar',grammar)
            f.write(grammar)

        IO_files_util.openFile('', output_file)
    except Exception as e:
         print(f"An error occurred: {e}")

def update_grammar_text(inputDir):
    """Auto-generate the GrammarRule_Text field in setup_Complex
    from the setup_xref tables. This reflects the current Required,
    AllowMultiple, and Group settings.
    Preserves existing +/++ prefixes from the original grammar when available."""
    global setup_Complex_lib

    # Parse existing prefixes from current GrammarRule_Text so we preserve
    # the original editorial +/++ markers instead of guessing from structure.
    existing_prefix = {}  # complex_name -> "<++" or "<+" or "<"
    if 'GrammarRule_Text' in setup_Complex_lib.columns:
        for _, row in setup_Complex_lib.iterrows():
            gt = str(row.get("GrammarRule_Text", "")).replace('_x000d_', '').strip()
            if gt and gt != 'nan' and '-->' in gt:
                if gt.startswith("<++"):
                    existing_prefix[row["Name"]] = "<++"
                elif gt.startswith("<+"):
                    existing_prefix[row["Name"]] = "<+"
                elif gt.startswith("<"):
                    existing_prefix[row["Name"]] = "<"

    # Build children lookup for structural fallback
    _children_of = {}
    for _, xrow in setup_xref_Complex_Complex_lib.iterrows():
        _children_of.setdefault(xrow["HigherComplex"], set()).add(xrow["LowerComplex"])

    # ++ detection using the Relationship field in setup_xref_Complex-Complex.
    # Relationship == 2 marks hierarchical links. Both ends of these links are ++
    # (e.g., Macro Event, Event, Semantic Triplet).
    # When Relationship field exists, it is authoritative — ignore existing prefixes.
    _structural_pp = set()
    if 'Relationship' in setup_xref_Complex_Complex_lib.columns:
        rel2 = setup_xref_Complex_Complex_lib[
            setup_xref_Complex_Complex_lib['Relationship'] == 2
        ]
        for _, r2row in rel2.iterrows():
            hid = r2row['HigherComplex']
            lid = r2row['LowerComplex']
            if hid != -1:
                _structural_pp.add(hid)
            if lid != -1:
                _structural_pp.add(lid)
        if _structural_pp:
            existing_prefix.clear()  # Relationship field is authoritative
    # Fallback if Relationship column not available: 3+ direct children + grandchild
    if not _structural_pp:
        for higher_id, children in _children_of.items():
            if len(children) >= 3:
                for child_id in children:
                    if child_id in _children_of:
                        _structural_pp.add(higher_id)
                        break

    def _get_prefix(complex_id, complex_name):
        """Return the grammar prefix for a complex type.
        Uses existing prefix if available, otherwise derives from structure."""
        if complex_name in existing_prefix:
            return existing_prefix[complex_name]
        # Structural fallback
        if complex_id in _structural_pp:
            return "<++"
        if complex_id in _children_of:
            return "<+"
        return "<"

    # Build a lookup: for each setup complex ID, what is its name?
    complex_name_map = {}
    for _, row in setup_Complex_lib.iterrows():
        complex_name_map[row["ID_setup_complex"]] = row["Name"]

    # Build a lookup: for each setup simplex ID, what is its name?
    simplex_name_map = {}
    for _, row in setup_Simplex_lib.iterrows():
        simplex_name_map[row["ID_setup_simplex"]] = row["Name"]

    # For each complex, generate its rewrite rule
    for idx, row in setup_Complex_lib.iterrows():
        complex_id = row["ID_setup_complex"]
        complex_name = row["Name"]

        # Get complex children, sorted by Order
        complex_children = setup_xref_Complex_Complex_lib[
            setup_xref_Complex_Complex_lib["HigherComplex"] == complex_id
        ].sort_values("Order")

        # Get simplex children, sorted by Order
        simplex_children = setup_xref_simplex_complex_lib[
            setup_xref_simplex_complex_lib["ID_setup_complex"] == complex_id
        ]
        if "Order" in simplex_children.columns:
            simplex_children = simplex_children.sort_values("Order")

        if len(complex_children) == 0 and len(simplex_children) == 0:
            # No rewrite rule needed for leaf nodes without children
            continue

        prefix = _get_prefix(complex_id, complex_name)

        # Build the right side of the rewrite rule
        parts = []

        # Add simplex children first
        for _, s_row in simplex_children.iterrows():
            simplex_id = s_row["ID_setup_simplex"]
            simplex_name = simplex_name_map.get(simplex_id, f"Simplex_{simplex_id}")
            required = s_row.get("Required", False)
            allow_multiple = s_row.get("AllowMultiple", False)
            group = str(s_row.get("Group", "0")) if pd.notna(s_row.get("Group", None)) else "0"

            token = f"<{simplex_name}>"

            # Add group notation for mutually exclusive
            if group not in ("0", "00", ""):
                token = f"<{simplex_name} ({group})>"

            # Wrap with {} if AllowMultiple
            if allow_multiple:
                token = "{" + token + "}"

            # Wrap with [] if not Required
            if not required:
                token = "[" + token + "]"

            parts.append(token)

        # Add complex children
        for _, c_row in complex_children.iterrows():
            child_id = c_row["LowerComplex"]
            child_name = complex_name_map.get(child_id, f"Complex_{child_id}")
            required = c_row.get("Required", False)
            allow_multiple = c_row.get("AllowMultiple", False)
            group = str(c_row.get("Group", "0")) if pd.notna(c_row.get("Group", None)) else "0"

            child_prefix = _get_prefix(child_id, child_name)

            token = f"{child_prefix}{child_name}>"

            # Add group notation for mutually exclusive
            if group not in ("0", "00", ""):
                token = f"{child_prefix}{child_name} ({group})>"

            # Wrap with {} if AllowMultiple
            if allow_multiple:
                token = "{" + token + "}"

            # Wrap with [] if not Required
            if not required:
                token = "[" + token + "]"

            parts.append(token)

        # Build the full rule
        rule = f"{prefix}{complex_name}> --> " + " ".join(parts)

        # Update GrammarRule_Text
        setup_Complex_lib.at[idx, "GrammarRule_Text"] = rule

    # Save updated setup_Complex back to files
    output_xlsx = os.path.join(inputDir, "setup_Complex.xlsx")
    output_pkl = os.path.join(inputDir, "setup_Complex.pkl")

    setup_Complex_lib.to_excel(output_xlsx, index=False)
    setup_Complex_lib.to_pickle(output_pkl)

    print(f"Grammar rules updated and saved to {output_xlsx}")
    mb.showwarning(title='Warning',
                   message='All grammar rules have been updated and saved to setup_Complex.xlsx and setup_Complex.pkl')

    return setup_Complex_lib

# given a complex setup name, the function returns its complex ID
def get_setup_complex_ID(complex_name):
    if isinstance(complex_name, str):
        complex_name = [complex_name]
    complex_ID = setup_Complex_lib[setup_Complex_lib['Name'].isin(complex_name)]
    complex_ID = complex_ID[['ID_setup_complex', 'Name']]
    complex_ID['ID_setup_complex'] = [int(x) for x in complex_ID['ID_setup_complex']]
    return complex_ID

# given a simplex setup name, the function returns its simplex ID
def get_setup_simplex_ID(simplex_name):
    if isinstance(simplex_name, str):
        simplex_name = [simplex_name]
    simplex_ID = setup_Simplex_lib[setup_Simplex_lib['Name'].isin(simplex_name)]
    simplex_ID = simplex_ID[['ID_setup_simplex', 'Name']]
    simplex_ID['ID_setup_simplex'] = [int(x) for x in simplex_ID['ID_setup_simplex']]
    return simplex_ID

# find the related names of setup simplexes, required and non required depending upon flag, to the input setup complex(es) names
# parameter:
#   complexes: setup names of complexes in list type
#   setup_Complex, setup_xref_simplex_complex
# return: related names of setup simplexes and required simplexes in nested list type

# get_setup_complex_simplex_children
def get_setup_complex_simplex_children(complexes, get_required_only=False):
    simplex_children_all = []
    simplex_children_required = []
    if isinstance(complexes, str):
        complexes = [complexes]

    for c in complexes:
        complex_ID = get_setup_complex_setup_ID([c])
        if complex_ID.empty:
            continue
        complex_ID = complex_ID.iat[0, 0]
        simplex_children_df = setup_xref_simplex_complex_lib[setup_xref_simplex_complex_lib['ID_setup_complex'] == complex_ID]
        simplex_children_all = simplex_children_df['Name'].values.tolist()
        print('List of ALL simplex', simplex_children_all)
        # simplex_children_all.append(simplex_children)
        if get_required_only:
            # MUST keep only required simplex children
            if len(simplex_children_df.loc[simplex_children_df['Required'] == True, 'Name'])>0:
                simplex_children_required = simplex_children_df.loc[simplex_children_df['Required'] == True, 'Name'].tolist()
                print('List of REQUIRED simplex', simplex_children_required)
                # simplex_children_required.append(simplex_children_required)
    return simplex_children_all, simplex_children_required

# find the list [] of ALL setup complex children, one level lower, REQUIRED and NON REQUIRED of the input setup complex name
# parameter: name of setup complex in string type, required boolean to return only required children
# return: two lists [] of xref setup complex names of all complex children and complex required children

def get_setup_complex_children(complex_name, get_required_only=True):
    has_files = True
    complex_children_all = []
    complex_children_required = []
    if isinstance(complex_name, str):
        complex_name = [complex_name]
    if setup_Complex_lib.empty or setup_xref_Complex_Complex_lib.empty:
        has_files =False

    if(has_files):
        if isinstance(complex_name, str):
            complexes = [complex_name]

        for c in complex_name:
            complex_ID = get_setup_complex_setup_ID([c])
            if complex_ID.empty:
                continue
        complex_ID = complex_ID.iat[0, 0]
        complex_children_all_df = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['HigherComplex'] == complex_ID]
        complex_children_all = complex_children_all_df['Name'].values.tolist()

        # Check if complex is required; only process required complex objects
        # MUST keep only required simplex children
        if get_required_only:
            if len(complex_children_all_df.loc[complex_children_all_df['Required'] == True, 'Name']) > 0:
                complex_children_required = complex_children_all_df.loc[
                    complex_children_all_df['Required'] == True, 'Name'].tolist()
                print('List of REQUIRED complex', complex_children_required)

    return complex_children_all, complex_children_required


# ============================================================================
# TOGGLE REQUIRED BOOLEAN
# ============================================================================

def get_required_value(object_type, object_name):
    """Look up the current REQUIRED boolean for a complex or simplex object in its xref table.

    Parameters:
        object_type: 'Complex' or 'Simplex'
        object_name: the Name of the object in setup_Complex or setup_Simplex

    Returns:
        (current_required_bool, info_dict) or (None, None) if not found.
        info_dict contains the xref table name and matching row indices for the update.
    """
    if object_type == 'Complex':
        # Look up the LowerComplex ID from setup_Complex
        match = setup_Complex_lib[setup_Complex_lib['Name'] == object_name]
        if match.empty:
            return None, None
        complex_id = match.iloc[0]['ID_setup_complex']
        # Find in setup_xref_Complex-Complex where LowerComplex == this ID
        xref_rows = setup_xref_Complex_Complex_lib[
            setup_xref_Complex_Complex_lib['LowerComplex'] == complex_id
        ]
        if xref_rows.empty:
            # Could also be a top-level complex (HigherComplex)
            # Check if it appears as HigherComplex
            print(f"  '{object_name}' (ID {complex_id}) not found as LowerComplex in setup_xref_Complex-Complex.")
            print(f"  It may be a top-level complex with no parent — REQUIRED is not applicable.")
            return None, None
        raw_val = xref_rows.iloc[0].get('Required', False)
        if isinstance(raw_val, str):
            current_val = raw_val.strip().upper() in ('TRUE', '1', 'YES')
        elif pd.isna(raw_val):
            current_val = False
        else:
            current_val = bool(raw_val)
        return current_val, {
            'table': 'setup_xref_Complex-Complex',
            'column': 'LowerComplex',
            'match_id': complex_id,
            'indices': xref_rows.index.tolist()
        }

    elif object_type == 'Simplex':
        # Look up the simplex ID from setup_Simplex
        match = setup_Simplex_lib[setup_Simplex_lib['Name'] == object_name]
        if match.empty:
            return None, None
        simplex_id = match.iloc[0]['ID_setup_simplex']
        # Find in setup_xref_Simplex-Complex where ID_setup_simplex == this ID
        xref_rows = setup_xref_simplex_complex_lib[
            setup_xref_simplex_complex_lib['ID_setup_simplex'] == simplex_id
        ]
        if xref_rows.empty:
            print(f"  '{object_name}' (ID {simplex_id}) not found in setup_xref_Simplex-Complex.")
            return None, None
        raw_val = xref_rows.iloc[0].get('Required', False)
        if isinstance(raw_val, str):
            current_val = raw_val.strip().upper() in ('TRUE', '1', 'YES')
        elif pd.isna(raw_val):
            current_val = False
        else:
            current_val = bool(raw_val)
        return current_val, {
            'table': 'setup_xref_Simplex-Complex',
            'column': 'ID_setup_simplex',
            'match_id': simplex_id,
            'indices': xref_rows.index.tolist()
        }

    return None, None


def toggle_required_value(object_type, object_name, new_value, inputDir):
    """Toggle the REQUIRED boolean for a complex or simplex object.
    Updates the xref DataFrame, saves xlsx + pkl, and regenerates grammar.

    Parameters:
        object_type: 'Complex' or 'Simplex'
        object_name: the Name of the object
        new_value: True or False
        inputDir: the PC-ACE database directory

    Returns:
        True on success, False on failure.
    """
    global setup_xref_Complex_Complex_lib, setup_xref_simplex_complex_lib

    current_val, info = get_required_value(object_type, object_name)
    if current_val is None:
        return False

    try:
        if object_type == 'Complex':
            # Update all rows where this complex appears as LowerComplex
            for idx in info['indices']:
                setup_xref_Complex_Complex_lib.at[idx, 'Required'] = new_value
            # Save xlsx and pkl
            table_name = 'setup_xref_Complex-Complex'
            xlsx_path = os.path.join(inputDir, f"{table_name}.xlsx")
            pkl_path = os.path.join(inputDir, f"{table_name}.pkl")
            setup_xref_Complex_Complex_lib.to_excel(xlsx_path, index=False)
            setup_xref_Complex_Complex_lib.to_pickle(pkl_path)
            print(f"  Updated REQUIRED for '{object_name}' to {new_value} in {table_name}")
            print(f"  Saved {xlsx_path} and {pkl_path}")

        elif object_type == 'Simplex':
            # Update all rows where this simplex appears
            for idx in info['indices']:
                setup_xref_simplex_complex_lib.at[idx, 'Required'] = new_value
            # Save xlsx and pkl
            table_name = 'setup_xref_Simplex-Complex'
            xlsx_path = os.path.join(inputDir, f"{table_name}.xlsx")
            pkl_path = os.path.join(inputDir, f"{table_name}.pkl")
            setup_xref_simplex_complex_lib.to_excel(xlsx_path, index=False)
            setup_xref_simplex_complex_lib.to_pickle(pkl_path)
            print(f"  Updated REQUIRED for '{object_name}' to {new_value} in {table_name}")
            print(f"  Saved {xlsx_path} and {pkl_path}")

        # Rebuild the Required-flag indexes
        if "Required" in setup_xref_Complex_Complex_lib.columns:
            _idx_xref_cc_setup.clear()
            _idx_xref_cc_setup.update(dict(zip(
                setup_xref_Complex_Complex_lib["ID_setup_xref_complex-complex"],
                setup_xref_Complex_Complex_lib["Required"])))
        if "Required" in setup_xref_simplex_complex_lib.columns:
            _idx_xref_sc_setup.clear()
            _idx_xref_sc_setup.update(dict(zip(
                setup_xref_simplex_complex_lib["ID_setup_xref_simplex-complex"],
                setup_xref_simplex_complex_lib["Required"])))

        # Regenerate grammar to reflect the new Required status
        print("  Regenerating grammar rules...")
        update_grammar_text(inputDir)

        return True

    except Exception as e:
        print(f"  ERROR toggling REQUIRED: {e}")
        import traceback
        traceback.print_exc()
        return False


# given a setup simplex name, the function returns a list of all the complex parents that have the simplex amo0ng its children, regardless of whether required

# find the one level higher setup complex of the input setup complex name
# parameter: name of setup complex
# return: a list of parent setup complex names
def get_setup_complex_parents(complex_name):
    global data_xref_simplex_complex_ALL_lib

    higher_level_complex = []
    has_files = True

    if isinstance(complex_name, str):
        complex_name = [complex_name]

    if setup_Complex_lib.empty or setup_xref_Complex_Complex_lib.empty:
        has_files =False

    if(has_files):
        complex_ID = get_setup_complex_setup_ID(complex_name)
        complex_ID = complex_ID['ID_setup_complex'].values.tolist()

        higher_level_complex = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['LowerComplex'].isin(complex_ID)]
        higher_level_complex =higher_level_complex['HigherComplex'].values.tolist()
        # higher_level_complex = [str(x) for x in higher_level_complex]

        higher_level_complex = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'].isin(higher_level_complex)]
        higher_level_complex =higher_level_complex[['ID_setup_complex', 'Name']]
        higher_level_complex =higher_level_complex.rename(columns={'ID_setup_complex': 'HigherComplex', 'Name': 'Name'})

        higher_level_complex =higher_level_complex['Name'].values.tolist()

    # returns list
    return higher_level_complex

# @@@ Aiden let's consolidate into one function; this is a BETTER function as it returns both ID and name in a dataframe

# find the one level higher setup complex of the input setup complex name
# parameter: name(s) of setup complex in list type, dataframe of setup_Complex and setup_xref_Complex_Complex
# return: a dataframe: setup ID and name of one level higher setup complex of the input complex

# the OTHER function get_setup_complex_parents returns a list [] with the setup higher complex name (NO ID!!!)

# find the parent of the chosen setup simplex
# parameter: name of simplex in string type, inputDir
# return: a list of parent complex(es)
def get_setup_simplex_parent(simplex_name):
    setup_simplex_parent = []
    has_files = True

    if isinstance(simplex_name, str):
        simplex_name = [simplex_name]

    global setup_Complex_lib
    if setup_Complex_lib.empty or setup_Simplex_lib.empty or setup_xref_simplex_complex_lib.empty:
        has_files =False

    if(has_files):
        simplex_ID = get_setup_simplex_ID(simplex_name)
        simplex_ID = simplex_ID['ID_setup_simplex'].values.tolist()

        complex_ID = setup_xref_simplex_complex_lib[setup_xref_simplex_complex_lib['ID_setup_simplex'].isin(simplex_ID)]
        complex_ID = complex_ID['ID_setup_complex'].values.tolist()

        # reset type of 'ID_setup_complex' in setup_Complex.xlsx
        setup_Complex_lib = setup_Complex_lib[setup_Complex_lib['Name'].notna()]
        setup_Complex_lib[['ID_setup_complex']] = setup_Complex_lib[['ID_setup_complex']].astype(int)
        setup_Complex_lib = setup_Complex_lib[['ID_setup_complex', 'Name']]

        setup_simplex_parent = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'].isin(complex_ID)]
        setup_simplex_parent = setup_simplex_parent['Name'].values.tolist()

    # returns list
    return setup_simplex_parent

# find the one level lower complex of the input complex
# parameter: name(s) of complex in list type, dataframe of setup_Complex and setup_xref_Complex_Complex
# return: a dataframe: id, name of one level lower complex of the input complex
def get_lower_setup_complex(complex_name):
    # complex_name MUST be a list []
    if isinstance(complex_name, str):
        complex_name = [complex_name]
    complex_ID = get_setup_complex_setup_ID(complex_name)
    complex_ID = complex_ID['ID_setup_complex'].values.tolist()

    lower_level_complex = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib['HigherComplex'].isin(complex_ID)]
    lower_level_complex = lower_level_complex[['LowerComplex', 'Name']]
    if str(list(lower_level_complex.Name.tolist()))=='[]':
        print('\n\nList of complex names below complex(es) ' + str(complex_name) + ': NO COMPLEX OBJECTS AVAILABLE')
    else:
        print('\n\nList of complex names below complex(es) ' + str(complex_name) + ': ' + str(list(lower_level_complex.Name.tolist())))
    # returns a 2-cols dataframe LowerComplex and Name with complex ID and name
    return lower_level_complex

# helper method for get_lowestcomplex
# to fill lowest_complex_list with the names of complex at the lowest level
# parameter: dataframe returned by get_lower_setup_complex function containing id and name of complex,
#            dataframe of setup_Complex and setup_xref_Complex_Complex
# search_complex MUST be a list []
# Aiden does it find the lowest or the immediately lower? if lowest, should change function name?

# find the grammar_path between complex objects in the setup grammar
# parameter: name of complex1 at higher level, name of complex2 at lower level
#            dataframe of setup_Complex and setup_xref_Complex_Complex
# return: the list of two complex and the complex in the grammar_path
def get_grammar_path(complex1, complex2):
    all_paths = []
    get_connections(complex1, complex2, [complex1], all_paths, set())
    return all_paths

# Aiden what does this function do?
def get_connections(complex1, complex2, current_path, all_paths, visited, depth_limit=10):
    if complex1 == complex2:
        all_paths.append(list(current_path))
        return
    if len(current_path) > depth_limit:  # Prevent overly deep recursion
        return

    visited.add(complex1)
    lower_complexes = get_lower_setup_complex([complex1])
    next_complexes = lower_complexes['Name'].values.tolist()

    for next_complex in next_complexes:
        if next_complex not in visited:
            current_path.append(next_complex)
            get_connections(next_complex, complex2, current_path, all_paths, visited, depth_limit)
            current_path.pop()

    visited.remove(complex1)


# ---------------------------------------------------------------------------
# Cross-complex SQL query generator
#
# Uses BFS on the setup_xref_Complex-Complex hierarchy to find a path between
# any two complex types, then mechanically produces a SQL query with the
# appropriate chain of JOINs through data_xref_Complex_Complex.
#
# The generated query:
#   - optionally filters the SOURCE complex by a simplex name/value
#   - navigates UP or DOWN through the hierarchy
#   - extracts simplex values from the TARGET complex
#   - handles all three value types (text, number, date) via a UNION sub-query
# ---------------------------------------------------------------------------

def _build_hierarchy_graph():
    """Build bidirectional adjacency maps from setup_xref_Complex_Complex_lib.

    Returns (children_map, parents_map) where each is
    {setup_complex_id: [setup_complex_id, ...]}.
    """
    children = {}
    parents = {}
    for _, row in setup_xref_Complex_Complex_lib.iterrows():
        h = int(row['HigherComplex'])
        l = int(row['LowerComplex'])
        children.setdefault(h, []).append(l)
        parents.setdefault(l, []).append(h)
    return children, parents


def find_cross_complex_path(source_name, target_name):
    """BFS path between two complex types (by Name).

    Returns a list of (setup_complex_id, direction) tuples where direction
    is 'start', 'down', or 'up'.  Returns None if no path exists.
    """
    from collections import deque

    id_lookup = dict(zip(setup_Complex_lib['Name'],
                         setup_Complex_lib['ID_setup_complex'].astype(int)))
    source_id = id_lookup.get(source_name)
    target_id = id_lookup.get(target_name)
    if source_id is None or target_id is None:
        return None

    if source_id == target_id:
        return [(source_id, 'start')]

    children, parents = _build_hierarchy_graph()
    visited = {source_id}
    queue = deque([(source_id, [(source_id, 'start')])])

    while queue:
        current, path = queue.popleft()
        # Explore UP (parents) first — PC-ACE navigation naturally goes
        # UP to the Semantic Triplet hub, then DOWN to the target branch.
        for parent in parents.get(current, []):
            if parent not in visited:
                visited.add(parent)
                new_path = path + [(parent, 'up')]
                if parent == target_id:
                    return new_path
                queue.append((parent, new_path))
        for child in children.get(current, []):
            if child not in visited:
                visited.add(child)
                new_path = path + [(child, 'down')]
                if child == target_id:
                    return new_path
                queue.append((child, new_path))
    return None


def generate_cross_complex_query(source_name, target_name,
                                 source_filter_simplex=None,
                                 source_filter_value=None,
                                 source_filter_operator='LIKE',
                                 where_simplex=None,
                                 target_simplex=None):
    """Generate a SQL query that navigates from one complex type to another.

    Parameters
    ----------
    source_name : str
        Name of the source complex type (e.g. 'Event', 'Individual').
    target_name : str
        Name of the target complex type (e.g. 'City', 'Personal characteristics').
    source_filter_simplex : str, optional
        Name of a simplex attribute to filter the source (e.g. 'Type of event').
        Used to restrict which simplex column is displayed for the source.
    source_filter_value : str, optional
        Value or pattern for the WHERE filter (e.g. 'lynching', '%woman%').
    source_filter_operator : str, optional
        SQL operator for the filter: 'LIKE', '=', '!=', 'NOT LIKE'. Default 'LIKE'.
    where_simplex : str, optional
        Simplex name to apply the WHERE filter on. If provided, uses this
        instead of source_filter_simplex for the WHERE clause.
    target_simplex : str, optional
        If given, only extract this simplex from the target.  Otherwise all
        target simplexes are returned.

    Returns
    -------
    (query_string, path) or (None, error_message)
    """
    id_lookup = dict(zip(setup_Complex_lib['Name'],
                         setup_Complex_lib['ID_setup_complex'].astype(int)))
    name_lookup = dict(zip(setup_Complex_lib['ID_setup_complex'].astype(int),
                           setup_Complex_lib['Name']))

    source_id = id_lookup.get(source_name)
    target_id = id_lookup.get(target_name)
    if source_id is None or target_id is None:
        return None, "Unknown complex type name"

    path = find_cross_complex_path(source_name, target_name)
    if path is None:
        return None, "No path found between {} and {}".format(source_name, target_name)

    # Build aliases for each step in the path
    aliases = []
    for i, (node_id, direction) in enumerate(path):
        if i == 0:
            aliases.append(('src', node_id, direction))
        elif i == len(path) - 1:
            aliases.append(('tgt', node_id, direction))
        else:
            aliases.append(('nav{}'.format(i), node_id, direction))

    # Check whether source and target complex types have simplex definitions
    source_has_simplexes = len(get_cross_complex_simplex_names(source_name)) > 0
    target_has_simplexes = len(get_cross_complex_simplex_names(target_name)) > 0

    # ---- SELECT ----
    # COALESCE picks the value from the correct table based on LEFT JOIN + ValueType
    src_value_expr = "COALESCE(src_vt.Value, src_vn.Value, src_vd.Value)"
    tgt_value_expr = "COALESCE(tgt_vt.Value, tgt_vn.Value, tgt_vd.Value)"
    select_parts = ["    src_dc.ID_data_complex     AS Source_ID"]
    if source_has_simplexes:
        if source_filter_simplex:
            select_parts.append("    {} AS Source_Value".format(src_value_expr))
        else:
            select_parts.append("    src_ss.Name                AS Source_Simplex")
            select_parts.append("    {} AS Source_Value".format(src_value_expr))
    select_parts.append("    tgt_dc.ID_data_complex     AS Target_ID")
    if target_has_simplexes:
        if target_simplex:
            select_parts.append("    {} AS Target_Value".format(tgt_value_expr))
        else:
            select_parts.append("    tgt_ss.Name                AS Target_Simplex")
            select_parts.append("    {} AS Target_Value".format(tgt_value_expr))

    # ---- FROM + JOINs ----
    from_parts = ["    data_Complex src_dc"]

    # Navigation joins: walk UP or DOWN through the hierarchy.
    # Use CROSS JOIN to force SQLite to use left-to-right join order
    # (start from source, navigate outward). Without this, SQLite may
    # choose a bad plan that starts from the target with a full table scan.
    prev_alias = 'src'
    for i in range(1, len(aliases)):
        alias, node_id, direction = aliases[i]
        xref_alias = 'xref{}'.format(i)
        dc_alias = '{}_dc'.format(alias)

        if direction == 'down':
            from_parts.append(
                "    CROSS JOIN data_xref_Complex_Complex {xref}\n"
                "        ON {xref}.ID_data_complex_HIGHER = {prev}_dc.ID_data_complex\n"
                "    CROSS JOIN data_Complex {dc}\n"
                "        ON {dc}.ID_data_complex = {xref}.ID_data_complex_LOWER\n"
                "        AND {dc}.ID_setup_complex = {setup_id}".format(
                    xref=xref_alias, prev=prev_alias, dc=dc_alias, setup_id=node_id))
        else:  # up
            from_parts.append(
                "    CROSS JOIN data_xref_Complex_Complex {xref}\n"
                "        ON {xref}.ID_data_complex_LOWER = {prev}_dc.ID_data_complex\n"
                "    CROSS JOIN data_Complex {dc}\n"
                "        ON {dc}.ID_data_complex = {xref}.ID_data_complex_HIGHER\n"
                "        AND {dc}.ID_setup_complex = {setup_id}".format(
                    xref=xref_alias, prev=prev_alias, dc=dc_alias, setup_id=node_id))
        prev_alias = alias

    # Source simplex extraction (placed after navigation to preserve CROSS JOIN order)
    # Use ValueType to join the correct value table (1=Text, 2=Number, 3=Date)
    # to avoid spurious rows from ID overlaps across value tables.
    if source_has_simplexes:
        from_parts.append(
            "    JOIN [data_xref_Simplex_Complex] src_sxc\n"
            "        ON src_sxc.ID_data_complex = src_dc.ID_data_complex\n"
            "    JOIN data_Simplex src_ds\n"
            "        ON src_ds.ID_data_simplex = src_sxc.ID_data_simplex\n"
            "    JOIN setup_Simplex src_ss\n"
            "        ON src_ss.ID_setup_simplex = src_ds.ID_setup_simplex\n"
            "    LEFT JOIN data_SimplexText   src_vt ON src_vt.ID_data_date_number_text = src_ds.ID_data_date_number_text AND src_ss.ValueType = 1\n"
            "    LEFT JOIN data_SimplexNumber src_vn ON src_vn.ID_data_date_number_text = src_ds.ID_data_date_number_text AND src_ss.ValueType = 2\n"
            "    LEFT JOIN data_SimplexDate   src_vd ON src_vd.ID_data_date_number_text = src_ds.ID_data_date_number_text AND src_ss.ValueType = 3"
        )

    # Target simplex extraction (only if target has simplexes)
    if target_has_simplexes:
        from_parts.append(
            "    JOIN [data_xref_Simplex_Complex] tgt_sxc\n"
            "        ON tgt_sxc.ID_data_complex = tgt_dc.ID_data_complex\n"
            "    JOIN data_Simplex tgt_ds\n"
            "        ON tgt_ds.ID_data_simplex = tgt_sxc.ID_data_simplex\n"
            "    JOIN setup_Simplex tgt_ss\n"
            "        ON tgt_ss.ID_setup_simplex = tgt_ds.ID_setup_simplex\n"
            "    LEFT JOIN data_SimplexText   tgt_vt ON tgt_vt.ID_data_date_number_text = tgt_ds.ID_data_date_number_text AND tgt_ss.ValueType = 1\n"
            "    LEFT JOIN data_SimplexNumber tgt_vn ON tgt_vn.ID_data_date_number_text = tgt_ds.ID_data_date_number_text AND tgt_ss.ValueType = 2\n"
            "    LEFT JOIN data_SimplexDate   tgt_vd ON tgt_vd.ID_data_date_number_text = tgt_ds.ID_data_date_number_text AND tgt_ss.ValueType = 3"
        )

    # ---- WHERE ----
    where_parts = ["    src_dc.ID_setup_complex = {}".format(source_id)]
    if source_filter_simplex and source_has_simplexes:
        where_parts.append("    AND src_ss.Name = '{}'".format(source_filter_simplex))
    # WHERE filter: use where_simplex if provided, otherwise fall back to source_filter_simplex
    _filter_simplex = where_simplex or source_filter_simplex
    if source_filter_value and _filter_simplex and source_has_simplexes:
        _op = source_filter_operator.upper() if source_filter_operator else 'LIKE'
        if _op in ('LIKE', 'NOT LIKE'):
            where_parts.append("    AND LOWER({}) {} LOWER('{}')".format(
                src_value_expr, _op, source_filter_value))
        else:
            where_parts.append("    AND {} {} '{}'".format(
                src_value_expr, _op, source_filter_value))
        # If where_simplex differs from source_filter_simplex, add a filter on simplex name
        if where_simplex and where_simplex != source_filter_simplex:
            where_parts.append("    AND src_ss.Name = '{}'".format(where_simplex))
    if target_simplex and target_has_simplexes:
        where_parts.append("    AND tgt_ss.Name = '{}'".format(target_simplex))

    # ---- Comment header ----
    path_desc = ' -> '.join(
        '{}({})'.format(name_lookup.get(nid, nid), d) for nid, d in path)
    comment = (
        "-- Auto-generated cross-complex query\n"
        "-- Source: {src} (setup_complex={src_id})\n"
        "-- Target: {tgt} (setup_complex={tgt_id})\n"
        "-- Path: {path}\n".format(
            src=source_name, src_id=source_id,
            tgt=target_name, tgt_id=target_id,
            path=path_desc))
    if _filter_simplex and source_filter_value:
        comment += "-- WHERE: {} {} '{}'\n".format(
            _filter_simplex, source_filter_operator or 'LIKE', source_filter_value)
    elif source_filter_simplex:
        comment += "-- Filter simplex: {}\n".format(source_filter_simplex)
    if not source_has_simplexes:
        children = get_children_with_simplexes(source_name)
        comment += "-- Note: {} has no simplex attributes; source IDs only\n".format(
            source_name)
        if children:
            comment += "--   Try using as source: {}\n".format(', '.join(children))
    if not target_has_simplexes:
        children = get_children_with_simplexes(target_name)
        comment += "-- Note: {} has no simplex attributes; target IDs only\n".format(
            target_name)
        if children:
            comment += "--   Try using as target: {}\n".format(', '.join(children))

    # Order by source then target values when available
    if source_has_simplexes and target_has_simplexes:
        order_by = "ORDER BY src_dc.ID_data_complex, tgt_ss.Name, {}".format(tgt_value_expr)
    elif target_has_simplexes:
        order_by = "ORDER BY {}".format(tgt_value_expr)
    elif source_has_simplexes:
        order_by = "ORDER BY src_dc.ID_data_complex, src_ss.Name"
    else:
        order_by = "ORDER BY src_dc.ID_data_complex, tgt_dc.ID_data_complex"

    query = (
        "{comment}\n"
        "SELECT\n{select_}\n"
        "FROM\n{from_}\n"
        "WHERE\n{where}\n"
        "{order_by}\n".format(
            comment=comment,
            select_=',\n'.join(select_parts),
            from_='\n'.join(from_parts),
            where='\n'.join(where_parts),
            order_by=order_by))

    return query, path


def generate_multi_target_query(source_name, source_simplex=None,
                                targets=None):
    """Generate a SQL query with one source and multiple targets.

    Each target is independently navigated from the source and the results
    are LEFT JOINed on Source_ID so each target appears as its own column(s).

    Parameters
    ----------
    source_name : str
        Name of the source complex type.
    source_simplex : str or None
        Specific source simplex to extract (None = all).
    targets : list of (target_name, target_simplex_or_None)
        Each element is a (complex_name, simplex_name_or_None) pair.

    Returns
    -------
    (query_string, info_dict) or (None, error_message)
    """
    if not targets:
        return None, "No targets specified."

    id_lookup = dict(zip(setup_Complex_lib['Name'],
                         setup_Complex_lib['ID_setup_complex'].astype(int)))
    name_lookup = dict(zip(setup_Complex_lib['ID_setup_complex'].astype(int),
                           setup_Complex_lib['Name']))

    source_id = id_lookup.get(source_name)
    if source_id is None:
        return None, "Unknown source complex type: {}".format(source_name)

    source_has_simplexes = len(get_cross_complex_simplex_names(source_name)) > 0

    # Build one CTE per target
    cte_parts = []
    cte_names = []
    all_paths = []
    warnings = []

    for idx, (tgt_name, tgt_simplex) in enumerate(targets):
        tgt_id = id_lookup.get(tgt_name)
        if tgt_id is None:
            return None, "Unknown target complex type: {}".format(tgt_name)

        path = find_cross_complex_path(source_name, tgt_name)
        if path is None:
            return None, "No path from {} to {}".format(source_name, tgt_name)
        all_paths.append((tgt_name, path))

        tgt_has_simplexes = len(get_cross_complex_simplex_names(tgt_name)) > 0
        cte_alias = 'cte_{}'.format(idx)
        cte_names.append((cte_alias, tgt_name, tgt_simplex, tgt_has_simplexes))

        # Build aliases for path steps
        aliases = []
        for i, (node_id, direction) in enumerate(path):
            if i == 0:
                aliases.append(('src', node_id, direction))
            elif i == len(path) - 1:
                aliases.append(('tgt', node_id, direction))
            else:
                aliases.append(('nav{}'.format(i), node_id, direction))

        # SELECT for this CTE
        cte_select = ["        src_dc.ID_data_complex AS Source_ID"]
        if tgt_has_simplexes:
            val_expr = "COALESCE(tgt_vt.Value, tgt_vn.Value, tgt_vd.Value)"
            if tgt_simplex:
                cte_select.append("        {} AS Value".format(val_expr))
            else:
                cte_select.append("        tgt_ss.Name AS Simplex")
                cte_select.append("        {} AS Value".format(val_expr))
        else:
            cte_select.append("        tgt_dc.ID_data_complex AS Target_ID")

        # FROM for this CTE
        cte_from = ["        data_Complex src_dc"]
        prev = 'src'
        for i in range(1, len(aliases)):
            alias, node_id, direction = aliases[i]
            xref_alias = 'xref{}'.format(i)
            dc_alias = '{}_dc'.format(alias)
            if direction == 'down':
                cte_from.append(
                    "        CROSS JOIN data_xref_Complex_Complex {xref}\n"
                    "            ON {xref}.ID_data_complex_HIGHER = {prev}_dc.ID_data_complex\n"
                    "        CROSS JOIN data_Complex {dc}\n"
                    "            ON {dc}.ID_data_complex = {xref}.ID_data_complex_LOWER\n"
                    "            AND {dc}.ID_setup_complex = {sid}".format(
                        xref=xref_alias, prev=prev, dc=dc_alias, sid=node_id))
            else:
                cte_from.append(
                    "        CROSS JOIN data_xref_Complex_Complex {xref}\n"
                    "            ON {xref}.ID_data_complex_LOWER = {prev}_dc.ID_data_complex\n"
                    "        CROSS JOIN data_Complex {dc}\n"
                    "            ON {dc}.ID_data_complex = {xref}.ID_data_complex_HIGHER\n"
                    "            AND {dc}.ID_setup_complex = {sid}".format(
                        xref=xref_alias, prev=prev, dc=dc_alias, sid=node_id))
            prev = alias

        # Target simplex joins
        if tgt_has_simplexes:
            cte_from.append(
                "        JOIN [data_xref_Simplex_Complex] tgt_sxc\n"
                "            ON tgt_sxc.ID_data_complex = tgt_dc.ID_data_complex\n"
                "        JOIN data_Simplex tgt_ds\n"
                "            ON tgt_ds.ID_data_simplex = tgt_sxc.ID_data_simplex\n"
                "        JOIN setup_Simplex tgt_ss\n"
                "            ON tgt_ss.ID_setup_simplex = tgt_ds.ID_setup_simplex\n"
                "        LEFT JOIN data_SimplexText   tgt_vt ON tgt_vt.ID_data_date_number_text = tgt_ds.ID_data_date_number_text AND tgt_ss.ValueType = 1\n"
                "        LEFT JOIN data_SimplexNumber tgt_vn ON tgt_vn.ID_data_date_number_text = tgt_ds.ID_data_date_number_text AND tgt_ss.ValueType = 2\n"
                "        LEFT JOIN data_SimplexDate   tgt_vd ON tgt_vd.ID_data_date_number_text = tgt_ds.ID_data_date_number_text AND tgt_ss.ValueType = 3"
            )

        # WHERE for this CTE
        cte_where = ["        src_dc.ID_setup_complex = {}".format(source_id)]
        if tgt_simplex and tgt_has_simplexes:
            cte_where.append("        AND tgt_ss.Name = '{}'".format(tgt_simplex))

        cte_sql = (
            "    {alias} AS (\n"
            "        SELECT\n{sel}\n"
            "        FROM\n{frm}\n"
            "        WHERE\n{whr}\n"
            "    )".format(
                alias=cte_alias,
                sel=',\n'.join(cte_select),
                frm='\n'.join(cte_from),
                whr='\n'.join(cte_where)))
        cte_parts.append(cte_sql)

        if not tgt_has_simplexes:
            children = get_children_with_simplexes(tgt_name)
            msg = "'{}' has no simplex attributes.".format(tgt_name)
            if children:
                msg += " Try: {}".format(', '.join(children))
            warnings.append(msg)

    # ---- Source CTE (with optional source simplex filter) ----
    src_select = ["        src_dc.ID_data_complex AS Source_ID"]
    src_from = ["        data_Complex src_dc"]
    src_where = ["        src_dc.ID_setup_complex = {}".format(source_id)]

    if source_has_simplexes:
        src_value_expr = "COALESCE(src_vt.Value, src_vn.Value, src_vd.Value)"
        if source_simplex:
            src_select.append("        {} AS Source_Value".format(src_value_expr))
        else:
            src_select.append("        src_ss.Name AS Source_Simplex")
            src_select.append("        {} AS Source_Value".format(src_value_expr))
        src_from.append(
            "        JOIN [data_xref_Simplex_Complex] src_sxc\n"
            "            ON src_sxc.ID_data_complex = src_dc.ID_data_complex\n"
            "        JOIN data_Simplex src_ds\n"
            "            ON src_ds.ID_data_simplex = src_sxc.ID_data_simplex\n"
            "        JOIN setup_Simplex src_ss\n"
            "            ON src_ss.ID_setup_simplex = src_ds.ID_setup_simplex\n"
            "        LEFT JOIN data_SimplexText   src_vt ON src_vt.ID_data_date_number_text = src_ds.ID_data_date_number_text AND src_ss.ValueType = 1\n"
            "        LEFT JOIN data_SimplexNumber src_vn ON src_vn.ID_data_date_number_text = src_ds.ID_data_date_number_text AND src_ss.ValueType = 2\n"
            "        LEFT JOIN data_SimplexDate   src_vd ON src_vd.ID_data_date_number_text = src_ds.ID_data_date_number_text AND src_ss.ValueType = 3"
        )
        if source_simplex:
            src_where.append("        AND src_ss.Name = '{}'".format(source_simplex))

    src_cte = (
        "    src_cte AS (\n"
        "        SELECT\n{sel}\n"
        "        FROM\n{frm}\n"
        "        WHERE\n{whr}\n"
        "    )".format(
            sel=',\n'.join(src_select),
            frm='\n'.join(src_from),
            whr='\n'.join(src_where)))

    # ---- Final SELECT from CTEs ----
    final_select = ["    src_cte.Source_ID"]
    if source_has_simplexes:
        if source_simplex:
            final_select.append("    src_cte.Source_Value")
        else:
            final_select.append("    src_cte.Source_Simplex")
            final_select.append("    src_cte.Source_Value")

    final_from = ["    src_cte"]
    for cte_alias, tgt_name, tgt_simplex, tgt_has_sx in cte_names:
        # Clean label for column name
        label = tgt_name.replace(' ', '_')
        if tgt_has_sx:
            if tgt_simplex:
                final_select.append("    {a}.Value AS [{tgt}_{sx}]".format(
                    a=cte_alias, tgt=label, sx=tgt_simplex.replace(' ', '_')))
            else:
                final_select.append("    {a}.Simplex AS [{tgt}_Simplex]".format(
                    a=cte_alias, tgt=label))
                final_select.append("    {a}.Value AS [{tgt}_Value]".format(
                    a=cte_alias, tgt=label))
        else:
            final_select.append("    {a}.Target_ID AS [{tgt}_ID]".format(
                a=cte_alias, tgt=label))
        final_from.append(
            "    LEFT JOIN {a} ON {a}.Source_ID = src_cte.Source_ID".format(a=cte_alias))

    # ---- Comment header ----
    comment = "-- Auto-generated MULTI-TARGET cross-complex query\n"
    comment += "-- Source: {} (setup_complex={})\n".format(source_name, source_id)
    if source_simplex:
        comment += "-- Source simplex: {}\n".format(source_simplex)
    for tgt_name, path in all_paths:
        path_desc = ' -> '.join('{}({})'.format(name_lookup.get(nid, nid), d) for nid, d in path)
        comment += "-- Target: {} | Path: {}\n".format(tgt_name, path_desc)

    query = (
        "{comment}\n"
        "WITH\n{ctes}\n\n"
        "SELECT\n{sel}\n"
        "FROM\n{frm}\n"
        "ORDER BY src_cte.Source_ID\n".format(
            comment=comment,
            ctes=',\n'.join([src_cte] + cte_parts),
            sel=',\n'.join(final_select),
            frm='\n'.join(final_from)))

    info = {'paths': all_paths, 'warnings': warnings}
    return query, info


def get_cross_complex_simplex_names(complex_name):
    """Return a list of simplex names associated with a complex type.

    Useful for populating dropdown menus so the user can pick which simplex
    to filter on or extract.
    """
    complex_id_df = get_setup_complex_ID(complex_name)
    if complex_id_df.empty:
        return []
    complex_id = int(complex_id_df['ID_setup_complex'].iloc[0])
    # Look up which simplexes are linked via setup_xref_Simplex-Complex
    linked = setup_xref_simplex_complex_lib[
        setup_xref_simplex_complex_lib['ID_setup_complex'] == complex_id]
    simplex_ids = linked['ID_setup_simplex'].unique()
    names = setup_Simplex_lib[
        setup_Simplex_lib['ID_setup_simplex'].isin(simplex_ids)]['Name']
    return sorted(names.dropna().tolist())


def get_children_with_simplexes(complex_name):
    """Return a list of child complex names that have simplex definitions.
    Useful for suggesting lower-level alternatives when a complex has no
    direct simplex attributes."""
    complex_id_df = get_setup_complex_ID(complex_name)
    if complex_id_df.empty:
        return []
    complex_id = int(complex_id_df['ID_setup_complex'].iloc[0])
    # Get children from setup_xref_Complex-Complex
    children = setup_xref_Complex_Complex_lib[
        setup_xref_Complex_Complex_lib['HigherComplex'] == complex_id
    ]['LowerComplex'].unique()
    result = []
    name_lookup = dict(zip(
        setup_Complex_lib['ID_setup_complex'].astype(int),
        setup_Complex_lib['Name']))
    for child_id in children:
        child_name = name_lookup.get(int(child_id))
        if child_name and len(get_cross_complex_simplex_names(child_name)) > 0:
            result.append(child_name)
    return sorted(result)


# get a list of all setup complex and simplex names to be used in dropdown menus in _main
def get_setup_complex_simplex_names():
    try:
        if setup_Complex_lib is not None and setup_Simplex_lib is not None:
            return setup_Complex_lib["Name"].dropna().sort_values().tolist(), setup_Simplex_lib["Name"].dropna().sort_values().tolist()
    except Exception as e:
        print(f"  WARNING: get_setup_complex_simplex_names error: {e}")
    return [], []


# Creates csv file with frequencies of each simplex grammar name as found in setup.
# parameters: simplex_name when='' all setup simplex data frequencies will be computed;
#   else only the frequency of the specific simplex will be computed
# return: grammar_path to generated csv or None if data is missing

def get_data_complex_frequencies(inputDir, outputDir, complex_name):
    if any(df is None or df.empty for df in [setup_Complex_lib, data_Complex_lib, data_xref_Complex_Complex_lib]):
        return None

    if complex_name =='':  # ALL complex
        list_complex_name = setup_Complex_lib['Name'].dropna().tolist()
        output_file_type ='all_complex_freq'
    else:
        # complex_name must be a list
        if isinstance(complex_name, str):
            list_complex_name = [complex_name]
            output_file_type = complex_name + '_complex_freq'

    # merged_data = pd.merge(data_xref_Complex_Complex_lib, data_Complex_lib, how='left', on='ID_data_complex')
    merged_data = pd.merge(data_xref_Complex_Complex_lib, data_Complex_lib, how='inner', left_on= ['ID_data_xref_complex-complex'], right_on= ['ID_data_complex'])

    all_rows = []
    for name in list_complex_name:
        complex_info = get_setup_complex_ID([name])
        complex_ID = complex_info.iloc[0, 0]

        filtered_data =merged_data[merged_data['ID_setup_complex'] == complex_ID]
        all_rows.append([name, len(filtered_data)])

    count = pd.DataFrame(all_rows, columns= ['Complex setup name', 'Frequency of data occurrences'])

    extension ='.csv'  # change to '.xlsx' if necessary

    output_file_name =IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
                                                               output_file_type)
    if extension =='.csv':
        count.to_csv(output_file_name, encoding='utf-8', index=False)
    else:
        count.to_excel(output_file_name, encoding='utf-8', index=False)

    return output_file_name



# given a complex setup name, the function returns its setup ID
def get_setup_complex_setup_ID(complex_name):
    if isinstance(complex_name, str):
        complex_name = [complex_name]
    results = setup_Complex_lib[setup_Complex_lib['Name'].isin(complex_name)]
    setup_complex_ID = results[['ID_setup_complex', 'Name']].copy()
    setup_complex_ID['ID_setup_complex'] = [int(x) for x in setup_complex_ID['ID_setup_complex']]
    return setup_complex_ID


#@@
### DATA & SETUP TABLES ############################################################################################

# Functions that deal with the relationship between grammar simplex objects (as found in setup tables)
#   and actual data as fond inn the data tables
# All grammar objects, simplex or complex, are always specific to a specific research project
#   e.g., the complex Attore may be the setup name in the fascism project, but Actor in the lynching project
#

###############################################################################################

# given a complex setup name selected in _main, the function returns an output file containing a set of information about the data complex

# given a complex setup name selected in _main, the function returns an output file containing a set of information about the data complex
#   e.g. identifier, simplex values

# get data for the input complex grammar name as found in setup
# parameter: name: complex name in str type
# return: dataframe: name, value, frequency
# def get_data_complex_frequencies(inputDir, outputDir, complex_name):
#
#     if any(df is None or df.empty for df in [setup_Complex_lib, data_Complex_lib, data_xref_Complex_Complex_lib]):
#         return None
#
#     if complex_name =='': # ALL complex
#         list_complex_name = setup_Complex_lib['Name'].dropna().tolist()
#         output_file_type ='all_complex_freq'
#     else:
#         # complex_name must be a list
#         if isinstance(complex_name, str):
#             list_simplex_name = [complex_name]
#             output_file_type = complex_name+'_complex_freq'
#
#     # Find the complex ID and name
#     complex_info = get_setup_complex_setup_ID(complex_name)
#     complex_ID, name = complex_info.iloc[0]
#
#     # Merge DataFrames to get the relevant data
#     merged_data = pd.merge(data_xref_Complex_Complex_lib, data_Complex_lib, how ='left', on ='ID_data_complex')
#     select =merged_data[merged_data['ID_setup_complex'] == complex_ID]
#
#     # Group and count the frequencies
#     count = select.groupby('ID_data_complex_LOWER').size().reset_index(name='Frequency')
#     result = pd.merge(count, data_Complex_lib, how ='left', left_on ='ID_data_complex_LOWER', right_on ='ID_data_complex')
#
#     result =result[['Identifier', 'Frequency']].rename(columns={'Identifier': name}).sort_values(by='Frequency', ascending=False)
#     # extension ='.xlsx' # change to '.csv' if necessary
#     extension ='.csv' # change to '.excel' if necessary
#     complex_frequency_file_name =IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
#                                                                        'complex_freq')
#     result.to_csv(complex_frequency_file_name, encoding='utf-8', index=False)
#
#     return complex_frequency_file_name

# Creates csv file with frequencies of each simplex grammar name as found in setup.
# parameters: simplex_name when='' all setup simplex data frequencies will be computed;
#   else only the frequency of the specific simplex will be computed
# return: grammar_path to generated csv or None if data is missing

def get_data_simplex_frequencies(inputDir, outputDir, simplex_name):
    if any(df is None or df.empty for df in [setup_Simplex_lib, data_Simplex_lib, data_xref_simplex_complex_lib]):
        return None

    if simplex_name =='': # ALL simplex
        list_simplex_name = setup_Simplex_lib['Name'].dropna().tolist()
        output_file_type ='all_simplex_freq'
    else:
        # simplex_name must be a list
        if isinstance(simplex_name, str):
            list_simplex_name = [simplex_name]
            output_file_type = simplex_name+'_simplex_freq'

    # Aiden, this function is under SETUP group but the next line uses data:
    merged_data = pd.merge(data_xref_simplex_complex_lib, data_Simplex_lib, how='left', on='ID_data_simplex')

    all_rows= []
    for name in list_simplex_name:
        simplex_info = get_setup_simplex_ID([name])
        simplex_ID = simplex_info.iloc[0,0]

        filtered_data =merged_data[merged_data['ID_setup_simplex'] == simplex_ID]
        all_rows.append([name, len(filtered_data)])

    count = pd.DataFrame(all_rows, columns= ['Simplex setup name', 'Frequency of data occurrences'])

    extension ='.csv' # change to '.xlsx' if necessary

    output_file_name =IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
                                                                       output_file_type)
    if extension =='.csv':
        count.to_csv(output_file_name, encoding='utf-8', index=False)
    else:
        count.to_excel(output_file_name, encoding='utf-8', index=False)

    return output_file_name


def get_data_simplex_values_listing(inputDir, outputDir, simplex_name):
    """List all actual data values for a given simplex name (e.g., 'City name')
    with their frequencies.  Returns the path to the output CSV, or None."""
    global data_simplex_values_ALL_lib
    if data_simplex_values_ALL_lib is None or data_simplex_values_ALL_lib.empty:
        print("  WARNING: data_simplex_values_ALL_lib not built yet.")
        return None
    if simplex_name == '':
        return None

    # Filter to the requested simplex name
    filtered = data_simplex_values_ALL_lib[
        data_simplex_values_ALL_lib['Simplex name'] == simplex_name]
    if filtered.empty:
        print(f"  No data values found for simplex '{simplex_name}'.")
        return None

    # Build frequency table of the 'Value' column
    freq = filtered['Value'].value_counts().reset_index()
    freq.columns = [simplex_name, 'Frequency']
    freq = freq.sort_values('Frequency', ascending=False)

    output_file_type = simplex_name + '_values_listing'
    output_file_name = IO_files_util.generate_output_file_name(
        '', inputDir, outputDir, '.csv', output_file_type)
    freq.to_csv(output_file_name, encoding='utf-8', index=False)
    print(f"  Simplex values listing: {len(freq)} unique values for '{simplex_name}' saved to {output_file_name}")
    return output_file_name


def get_simplex_value_type(simplex_name):
    """Return the ValueType (1=text, 2=number, 3=date) for a given simplex name.
    Returns None if the simplex is not found."""
    if setup_Simplex_lib is None or setup_Simplex_lib.empty:
        return None
    match = setup_Simplex_lib[setup_Simplex_lib['Name'] == simplex_name]
    if match.empty:
        return None
    if 'ValueType' not in setup_Simplex_lib.columns:
        return None
    try:
        return int(match.iloc[0]['ValueType'])
    except (ValueError, TypeError):
        return None


def find_near_duplicate_simplex_values(inputDir, outputDir, simplex_name='', similarity_threshold=0.8):
    """Find near-duplicate (potentially misspelled) text values in data_SimplexText.

    Groups similar strings within each simplex name. For example, if 'City name'
    has values 'Barnesville', 'Barnesvile', 'barnesville', these are flagged.

    Parameters:
        inputDir, outputDir: paths for file generation
        simplex_name: if specified, only check that simplex; if '', check all text simplexes
        similarity_threshold: 0.0-1.0, how similar strings must be (0.8 = 80% match)

    Returns: path to the review CSV, or None if no near-duplicates found.
    """
    import difflib

    global data_simplex_values_ALL_lib
    if data_simplex_values_ALL_lib is None or data_simplex_values_ALL_lib.empty:
        print("  WARNING: data_simplex_values_ALL_lib not available for spell-check.")
        return None

    # Filter to text-type simplexes (ValueType == 1)
    if 'ValueType' in data_simplex_values_ALL_lib.columns:
        text_data = data_simplex_values_ALL_lib[
            data_simplex_values_ALL_lib['ValueType'].astype(float).fillna(0).astype(int) == 1].copy()
    else:
        text_data = data_simplex_values_ALL_lib.copy()

    if simplex_name:
        text_data = text_data[text_data['Simplex name'] == simplex_name]

    if text_data.empty:
        return None

    clusters = []  # list of dicts for the output CSV

    # Group by simplex name and find near-duplicates within each group
    for sx_name, group in text_data.groupby('Simplex name'):
        values = group['Value'].dropna().astype(str).tolist()
        if not values:
            continue

        # Build frequency map
        freq_map = {}
        for v in values:
            freq_map[v] = freq_map.get(v, 0) + 1

        unique_vals = list(freq_map.keys())
        if len(unique_vals) < 2:
            continue

        # Normalize for comparison (lowercase, stripped)
        norm_map = {}  # normalized → list of original values
        for v in unique_vals:
            norm = v.strip().lower()
            norm_map.setdefault(norm, []).append(v)

        # Flag exact case-only duplicates (e.g., 'Police' vs 'police')
        for norm, originals in norm_map.items():
            if len(originals) > 1:
                # Pick the most frequent as the "canonical" form
                originals_sorted = sorted(originals, key=lambda x: freq_map.get(x, 0), reverse=True)
                canonical = originals_sorted[0]
                for variant in originals_sorted[1:]:
                    clusters.append({
                        'Simplex name': sx_name,
                        'Value': variant,
                        'Frequency': freq_map.get(variant, 0),
                        'Similar to': canonical,
                        'Canonical frequency': freq_map.get(canonical, 0),
                        'Match type': 'Case variant',
                        'Similarity': 1.0
                    })

        # Find fuzzy near-duplicates using SequenceMatcher
        checked = set()
        for i, v1 in enumerate(unique_vals):
            v1_lower = v1.strip().lower()
            if len(v1_lower) < 3:
                continue  # Skip very short strings (too many false positives)
            for j, v2 in enumerate(unique_vals):
                if j <= i:
                    continue
                v2_lower = v2.strip().lower()
                if len(v2_lower) < 3:
                    continue
                if v1_lower == v2_lower:
                    continue  # Already handled as case variants
                pair_key = (min(v1, v2), max(v1, v2))
                if pair_key in checked:
                    continue
                checked.add(pair_key)

                ratio = difflib.SequenceMatcher(None, v1_lower, v2_lower).ratio()
                if ratio >= similarity_threshold:
                    # The more frequent one is likely the correct spelling
                    if freq_map.get(v1, 0) >= freq_map.get(v2, 0):
                        canonical, variant = v1, v2
                    else:
                        canonical, variant = v2, v1
                    clusters.append({
                        'Simplex name': sx_name,
                        'Value': variant,
                        'Frequency': freq_map.get(variant, 0),
                        'Similar to': canonical,
                        'Canonical frequency': freq_map.get(canonical, 0),
                        'Match type': 'Fuzzy match',
                        'Similarity': round(ratio, 3)
                    })

    if not clusters:
        print("  No near-duplicate simplex text values found.")
        return None

    df = pd.DataFrame(clusters)
    df = df.sort_values(['Simplex name', 'Similarity'], ascending=[True, False])

    label = simplex_name + '_' if simplex_name else ''
    output_file_name = IO_files_util.generate_output_file_name(
        '', inputDir, outputDir, '.csv', label + 'near_duplicate_values')
    df.to_csv(output_file_name, encoding='utf-8', index=False)
    print(f"  Found {len(clusters)} potential near-duplicate value(s) across "
          f"{df['Simplex name'].nunique()} simplex(es). Saved to {output_file_name}")

    return output_file_name


def _detect_date_format(date_values):
    """Detect the most likely date format from a list of date strings.
    Returns one of: 'mm-dd-yyyy', 'dd-mm-yyyy', 'yyyy-mm-dd', 'yyyy-dd-mm',
    'mm-yyyy', 'yyyy-mm', 'yyyy', or None."""
    import re
    if not date_values:
        return None
    # Sample up to 20 values for detection
    samples = [str(v).strip() for v in date_values[:20] if pd.notna(v) and str(v).strip()]
    if not samples:
        return None
    # Count separator patterns
    yyyy_mm_dd = 0  # 2020-01-15 or 2020/01/15
    mm_dd_yyyy = 0  # 01-15-2020 or 01/15/2020
    dd_mm_yyyy = 0  # 15-01-2020 or 15/01/2020
    yyyy_only = 0   # 2020
    for s in samples:
        # Normalize separators
        s_norm = s.replace('/', '-').replace('.', '-')
        parts = s_norm.split('-')
        if len(parts) == 3:
            p0, p1, p2 = parts
            if len(p0) == 4:  # Starts with year
                yyyy_mm_dd += 1
            elif len(p2) == 4:  # Ends with year
                # Disambiguate mm-dd vs dd-mm
                try:
                    if int(p0) > 12:
                        dd_mm_yyyy += 1
                    elif int(p1) > 12:
                        mm_dd_yyyy += 1
                    else:
                        mm_dd_yyyy += 1  # Default US format
                except ValueError:
                    mm_dd_yyyy += 1
        elif len(parts) == 1 and re.match(r'^\d{4}$', s_norm):
            yyyy_only += 1

    if yyyy_mm_dd >= max(mm_dd_yyyy, dd_mm_yyyy, yyyy_only, 1):
        return 'yyyy-mm-dd'
    elif dd_mm_yyyy > mm_dd_yyyy:
        return 'dd-mm-yyyy'
    elif mm_dd_yyyy > 0:
        return 'mm-dd-yyyy'
    elif yyyy_only > 0:
        return 'yyyy'
    return 'mm-dd-yyyy'  # Default


def prepare_timechart_csv(inputDir, outputDir, simplex_name):
    """Create a timechart-ready CSV from a date-type simplex.

    Reads all date values for the given simplex and writes a CSV with
    columns 'Date' and 'Category' (the parent complex name).
    Returns (csv_path, date_format) or (None, None) if not applicable.
    """
    global data_simplex_values_ALL_lib

    # Verify this is a date simplex (ValueType == 3)
    vtype = get_simplex_value_type(simplex_name)
    if vtype != 3:
        return None, None

    if data_simplex_values_ALL_lib is None or data_simplex_values_ALL_lib.empty:
        return None, None

    filtered = data_simplex_values_ALL_lib[
        data_simplex_values_ALL_lib['Simplex name'] == simplex_name]
    if filtered.empty:
        return None, None

    date_values = filtered['Value'].dropna().tolist()
    if not date_values:
        return None, None

    # Detect date format from actual values
    date_format = _detect_date_format(date_values)
    if not date_format:
        return None, None

    # Find the parent complex name(s) for this simplex
    parent_names = get_setup_simplex_parent(simplex_name)
    parent_label = parent_names[0] if parent_names else 'Object'

    # Build a DataFrame with Date and Category columns
    # Each row is one occurrence of the date value, with the parent complex as category
    df = pd.DataFrame({
        'Date': date_values,
        parent_label: [parent_label] * len(date_values)
    })

    output_file_name = IO_files_util.generate_output_file_name(
        '', inputDir, outputDir, '.csv', simplex_name + '_timechart_data')
    df.to_csv(output_file_name, encoding='utf-8', index=False)
    print(f"  Timechart data: {len(df)} date values for '{simplex_name}' saved to {output_file_name}")

    return output_file_name, date_format


def prepare_gis_locations_csv(inputDir, outputDir, simplex_name):
    """Prepare a GIS-pipeline-compatible CSV from simplex location values.

    Reads every unique *data* value stored for the given simplex name
    (e.g., "City name" → Barnesville, Atlanta, …) and writes a CSV with
    the columns that ``GIS_pipeline_util.GIS_pipeline`` / ``GIS_geocode_util.geocode``
    expect:  Location · NER · Sentence · Document.

    The NER tag is inferred from the simplex name so that Nominatim can
    narrow the search (city vs. state vs. country).

    Returns the path to the output CSV, or *None* if data is missing.
    """
    global data_simplex_values_ALL_lib
    if data_simplex_values_ALL_lib is None or data_simplex_values_ALL_lib.empty:
        print("  WARNING: data_simplex_values_ALL_lib not built yet – cannot prepare GIS CSV.")
        return None
    if simplex_name == '':
        return None

    # ── Filter to the requested simplex ──────────────────────────────
    filtered = data_simplex_values_ALL_lib[
        data_simplex_values_ALL_lib['Simplex name'] == simplex_name]
    if filtered.empty:
        print(f"  No data values found for simplex '{simplex_name}' – GIS CSV not created.")
        return None

    # ── Map simplex name → NER tag (language-agnostic) ───────────────
    name_lower = simplex_name.lower()
    if any(kw in name_lower for kw in ['city', 'città', 'town', 'village', 'municipalit',
                                        'lynching']):          # "City of lynching"
        ner_tag = 'CITY'
    elif any(kw in name_lower for kw in ['state', 'stato', 'province', 'provincia',
                                          'region', 'regione']):
        ner_tag = 'STATE_OR_PROVINCE'
    elif any(kw in name_lower for kw in ['country', 'nation', 'paese', 'nazione']):
        ner_tag = 'COUNTRY'
    elif any(kw in name_lower for kw in ['county', 'contea']):
        ner_tag = 'CITY'          # county geocodes better at city level
    else:
        ner_tag = 'CITY'          # safe default

    # ── Collect unique non-null values ───────────────────────────────
    values = filtered['Value'].dropna().unique().tolist()
    # Remove blanks / whitespace-only
    values = [v for v in values if str(v).strip()]
    if not values:
        print(f"  All values for simplex '{simplex_name}' are empty – GIS CSV not created.")
        return None

    # ── Build GIS-compatible DataFrame ───────────────────────────────
    db_name = os.path.basename(inputDir) if inputDir else ''
    rows = [[str(v), ner_tag, '', db_name] for v in values]
    gis_df = pd.DataFrame(rows, columns=['Location', 'NER', 'Sentence', 'Document'])

    output_file_name = IO_files_util.generate_output_file_name(
        '', inputDir, outputDir, '.csv', simplex_name + '_GIS_locations')
    gis_df.to_csv(output_file_name, index=False, encoding='utf-8')
    print(f"  GIS locations CSV: {len(gis_df)} unique locations for '{simplex_name}' "
          f"(NER={ner_tag}) saved to {output_file_name}")
    return output_file_name


# find the id of the input complex (name)
# parameter: name of a complex in list type (e.g. [, dataframe of setup_Complex
# return: a dataframe: id, name of the input complex

# given a specific value for a simplex (e.g., woman ) the function returns a csv file with all the information f the simplex_value
# current function only processes text, not date or number
def get_data_simplex_info(inputDir, outputDir, simplex_value):
    # data:SimplexText[ID] --> data:Simplex[refValue]
    # data:Simplex[ID] --> data:xref:Simplex-Complex[Simplex]
    # Determine the second-level hierarchical complex generically (replaces hard-coded 'Event')
    _second_level_complex = ''
    if len(setup_Complex_lib) > 0:
        top_level_name = setup_Complex_lib['Name'].iloc[0]
        children_all, _ = get_setup_complex_children(top_level_name, get_required_only=False)
        if children_all:
            _second_level_complex = children_all[0]

    data ={'Information': ['Simplex value', 'Simplex name', 'Frequency', 'Complex name', 'Higher complex ID', 'Lower complex ID', f'Relationship to {_second_level_complex}' if _second_level_complex else 'Relationship to parent']}
    simplex_info = []

    # data_xref_simplex_complex_select is a df
    data_xref_simplex_complex_select = data_simplex_values_ALL_lib.loc[data_simplex_values_ALL_lib['Value'] == simplex_value, ['ID_setup_simplex', 'Simplex name']]
    # simplex_names is a list
    simplex_names = data_xref_simplex_complex_select['Simplex name'].values.tolist()
    for name in simplex_names:
        simplex_info.append([name])

    # frequency
    # data_xref_simplex_complex_select = simplex_values_ALL_lib[simplex_values_ALL_lib['Value' == simplex_value], 'ID_setup_simplex', 'Simplex name']
    # temp = pd.merge(data_xref_simplex_complex_lib, data_Simplex_lib, how ='left', on ='ID_data_simplex')
    # ID_data_date_number_text = simplex_values_ALL_lib.loc[['ID_data_date_number_text'].values.tolist()]
    # ID_data_date_number_text =ID_data_date_number_text[0]
    # data_xref_simplex_complex_select =ID_data_date_number_text[ID_data_date_number_text['ID_data_date_number_text']==ID_data_date_number_text]

    for i in range(len(simplex_info)):
        simplex_setup_ID = get_setup_simplex_ID([simplex_info[i][0]])
        simplex_setup_ID = simplex_setup_ID.iat[0,0]
        data_xref_simplex_complex_select_further = data_xref_simplex_complex_select[data_xref_simplex_complex_select['ID_setup_simplex']== simplex_setup_ID]
        frequency =0
        if len(data_xref_simplex_complex_select_further) !=0:
            frequency = data_xref_simplex_complex_select_further.groupby(['ID_data_simplex']).count()
            frequency =frequency.iat[0,0]
        simplex_info[i].append(frequency)

    # complex related info
    for i in range(len(simplex_info)):
        simplex_name = simplex_info[i][0]
        complex_name = get_setup_simplex_parent([simplex_name])
        if len(complex_name) !=0:
            # highercomplex this is a list with the name only
            higher_complex = get_setup_complex_parents(complex_name)
            # higher_complex = get_higher_setup_complex(complex_name)
            # higher_complex =higher_complex['Name'].values.tolist()
            # lowercomplex this is a df with ID and name
            lower_complex = get_lower_setup_complex(complex_name)
            lower_complex = lower_complex['Name'].values.tolist()
            # relationship to second-level hierarchical complex (generic, replaces hard-coded 'Event')
            grammar_path = get_grammar_path(_second_level_complex, complex_name[0]) if _second_level_complex else []
            grammar_path = grammar_path[0] if grammar_path else []
            # format
            complex_name_table =', '.join(complex_name)
            higher_complex_table =', '.join(higher_complex)
            lower_complex_table =', '.join(lower_complex)
            path_table =', '.join(grammar_path)
        else:
            complex_name_table =''
            higher_complex_table =''
            lower_complex_table =''
            path_table =''
        # save
        simplex_info[i].append(simplex_value)
        simplex_info[i].append(complex_name_table)
        simplex_info[i].append(higher_complex_table)
        simplex_info[i].append(lower_complex_table)
        simplex_info[i].append(path_table)

    for i in range(len(simplex_info)):
        name ='value' + str(i+1)
        data[name] = simplex_info[i]

    df = pd.DataFrame(data)

    # extension ='.xlsx' # change to '.csv' if necessary
    extension ='.csv' # change to '.excel' if necessary
    simplex_info_file_name =IO_files_util.generate_output_file_name('', inputDir, outputDir, extension,
                                                                       'simplex information')
    df.to_csv(simplex_info_file_name, encoding='utf-8', index=False)

    # headers =IO_csv_util.get_csvfile_headers(simplex_info_file_name)
    # columns_to_be_plotted_xAxis =IO_csv_util.get_headerValue_from_columnNumber(headers, column_number=0)
    # outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, simplex_info_file_name,
    #                                           outputDir,
    #                                           columns_to_be_plotted_xAxis= [columns_to_be_plotted_xAxis],
    #                                           columns_to_be_plotted_yAxis= ['Frequency'],
    #                                           chart_title='Frequency Distribution of Simplex Object\n' + str(
    #                                               simplex_data),
    #                                           # count_var =1 for columns of alphabetic values
    #                                           count_var=1, hover_label= [],
    #                                           outputFileNameType= str(simplex_data),  # 'gender_bar',
    #                                           column_xAxis_label= str(simplex_data),
    #                                           groupByList= [],
    #                                           plotList= [],
    #                                           chart_title_label='')

    return simplex_info_file_name


# helper method for get_data_simplex_text_date_number
# simplex_type can be text, date, or number
# convert the column named 'Value' in data_SimplexText or data_SimplexNumber, or data_SimplexDate, depending pon the selected simplex_type, into a list of values
# given a simplex type (text, date, or number), the function returns a list of all values in data_SimplexText, data_SimplexDate or data_SimplexNumber
def get_data_simplex_text_date_number(simplex_type):
    if simplex_type=='':
        return []
    data_files ={
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
    if simplex_type =='number':
        list_simplex_data = [int(num) if isinstance(num, float) and num.is_integer() else num for num in list_simplex_data]
    if list_simplex_data and all(isinstance(item, type(list_simplex_data[0])) for item in list_simplex_data):
        list_simplex_data.sort()

    return list_simplex_data


def get_simplex_values_by_name(simplex_name):
    """Return a sorted list of unique data values for a specific simplex name
    (e.g., 'City name' → ['Atlanta', 'Barnesville', ...]).
    Uses data_simplex_values_ALL_lib which merges text/date/number values."""
    global data_simplex_values_ALL_lib
    if data_simplex_values_ALL_lib is None or (hasattr(data_simplex_values_ALL_lib, 'empty') and data_simplex_values_ALL_lib.empty):
        return []
    if not simplex_name:
        return []
    filtered = data_simplex_values_ALL_lib[
        data_simplex_values_ALL_lib['Simplex name'] == simplex_name]
    if filtered.empty:
        return []
    values = filtered['Value'].dropna().unique().tolist()
    try:
        values.sort()
    except TypeError:
        values.sort(key=str)
    return values


# get all the data IDs (higher & lower) from data_xref_Complex_Complex as dataframe for a given setup complex name
# returns a dataframe with the first element as the higher & lower ID

def get_data_complex_ID(complex_name):
    # get data xref IDs
    # search_complex_setup_xref_ID df with
    #   the first element has the xref setup value and the second element as the ID for the complex name
    #   e.g., in the lynching DB actor has left values ID 35 and right values 30, 35, 36, 45, 48, 49
    search_complex_setup_xref_ID = setup_xref_Complex_Complex_lib.loc[(setup_xref_Complex_Complex_lib["Name"] == complex_name),  ["ID_setup_xref_complex-complex", "LowerComplex"]]

    complex_data_xref_ID_df = search_complex_setup_xref_ID.merge(data_xref_Complex_Complex_lib, left_on="ID_setup_xref_complex-complex", right_on="ID_setup_xref_complex-complex", how="left")

    # print('\n\nNumber of xref records for complex ' + complex_name + ': ' + str(len(complex_data_xref_ID_df)))

    # the first element is all the xref setup values (e.g., 30, 35, 36, 45, 48, 49)
    # the second element is the xref ID of the searched complex (e.g., 35, always the same value)
    # the third element is all the ID of the data_xref_complex-complex
    # the successive elements have all the higher and lower data complex IDs

    return complex_data_xref_ID_df


# given a complex data ID value, returns its setup ID and name
def get_setup_complex_ID_Name_from_data_complex_ID(data_complex_ID):
    try:
        setup_complex_ID = data_Complex_lib.loc[data_Complex_lib['ID_data_complex'] == data_complex_ID, 'ID_setup_complex']
        setup_complex_ID = setup_complex_ID.iloc[0]
    except:
        setup_complex_ID =-1
        mb.showwarning(title='Warning',
                       message='The ID value ' + str(data_complex_ID) + ' was not found in the table data_Complex_lib.\n\nPlease, enter a different ID and try again')
    if setup_complex_ID > -1:
        setup_complex_name = setup_Complex_lib.loc[setup_Complex_lib['ID_setup_complex'] == setup_complex_ID, 'Name']
        setup_complex_name = setup_complex_name.iloc[0]
    else:
        setup_complex_name =''
    return setup_complex_ID, setup_complex_name

# given a simplex data ID value, returns its setup ID and name
def get_setup_simplex_ID_Name_from_simplex_value_ID(data_simplex_ID):
    try:
        setup_simplex_ID = data_Simplex_lib.loc[data_Simplex_lib['ID_data_simplex'] == data_simplex_ID, 'ID_setup_simplex']
        setup_simplex_ID = setup_simplex_ID.iloc[0]
    except:
        setup_simplex_ID =-1
        mb.showwarning(title='Warning',
                       message='The ID value ' + str(data_simplex_ID) + ' was not found in the table data_Simplex_lib.\n\nPlease, enter a different ID and try again')
    if setup_simplex_ID > -1:
        setup_simplex_name = setup_Simplex_lib.loc[setup_Simplex_lib['ID_setup_simplex'] == setup_simplex_ID, 'Name']
        setup_simplex_name = setup_simplex_name.iloc[0]
    else:
        setup_simplex_name =''
    return setup_simplex_ID, setup_simplex_name

# @@@@@
# given a df with a column of IDs of data complex (ID_data_complex), returns a df of all complex setup IDs and names

# @@@@@@ Useful function


# get get_complex_data_IDs_in_grammar_path as a dataframe with 2 columns

def get_comment_info(df, object_name, comment_type, inputDir, outputDir):
    """Extract user and/or verifier comments for a given complex object (or all objects).

    Parameters
    ----------
    df : pd.DataFrame or any
        Pre-filtered dataframe of complex objects. Pass an empty string or
        empty DataFrame to export comments for ALL complex objects.
    object_name : str
        Setup complex name (e.g., 'Semantic Triplet'). '' means all objects.
    comment_type : str
        '*' for both, 'Users comments', or 'Verifiers comments'.
    inputDir, outputDir : str
        Directories for file I/O.

    Returns
    -------
    list[str]
        List of output file paths (xlsx).
    """
    output_files = []
    comment_type = str(comment_type) if not isinstance(comment_type, str) else comment_type

    # Resolve tkinter StringVar if needed
    if hasattr(inputDir, 'get'):
        inputDir = inputDir.get()
    if hasattr(outputDir, 'get'):
        outputDir = outputDir.get()

    want_users = '*' in comment_type or 'Users' in comment_type
    want_verifiers = '*' in comment_type or 'Verifiers' in comment_type

    # Build a lookup table: UserID -> UserName (never mutate the global lib)
    user_lookup = utility_Security_lib[['ID', 'UserName']].copy()

    name_prefix = object_name + '_' if object_name != '' else ''

    # ------------------------------------------------------------------
    # Helper: filter comments to a specific complex object if requested
    # ------------------------------------------------------------------
    def _enrich_with_complex_info(comment_df, complex_id_col):
        """Join comment rows with data_Complex and setup_Complex to add
        Identifier, Complex name, and optionally filter to a specific complex type.

        After this call the df will have columns: ..., Identifier, Complex name
        """
        # Join to get ID_setup_complex and Identifier from data_Complex
        enriched = pd.merge(comment_df, data_Complex_lib[['ID_data_complex', 'ID_setup_complex', 'Identifier']],
                            how='inner', left_on=complex_id_col, right_on='ID_data_complex')
        # Join to get the setup complex Name
        enriched = pd.merge(enriched, setup_Complex_lib[['ID_setup_complex', 'Name']],
                            how='left', on='ID_setup_complex')
        enriched = enriched.rename(columns={'Name': 'Complex name'})

        # Filter to the requested complex type if specified
        if object_name != '':
            setup_ids = get_setup_complex_ID(object_name)
            if setup_ids.empty:
                return pd.DataFrame()
            setup_id_list = setup_ids['ID_setup_complex'].tolist()
            enriched = enriched[enriched['ID_setup_complex'].isin(setup_id_list)]

        return enriched

    # ------------------------------------------------------------------
    # Users comments
    # ------------------------------------------------------------------
    if want_users:
        # data_xref_comment-complex has: ID_data_complex, Comment, UserID
        df_users = data_xref_comment_complex_lib.copy()
        df_users = _enrich_with_complex_info(df_users, 'ID_data_complex')

        if not df_users.empty:
            # Add user name
            df_users = pd.merge(df_users, user_lookup, how='left',
                                left_on='UserID', right_on='ID')

            df_users = df_users.rename(columns={'UserName': 'User name'})
            # Select and order output columns
            out_cols = ['Comment', 'Complex name', 'User name', 'Identifier']
            df_users = df_users[[c for c in out_cols if c in df_users.columns]]

            label = name_prefix + 'users-comments'
            export_df_to_excel(df_users, inputDir, outputDir, label, False)
            output_files.append(os.path.join(outputDir, label + '.xlsx'))

    # ------------------------------------------------------------------
    # Verifiers comments
    # ------------------------------------------------------------------
    if want_verifiers:
        # data_xref_VComment has: Complex (=ID_data_complex), Comment, Completed, UserID, VerifierID
        df_verif = data_xref_VComment_lib.copy()
        df_verif = _enrich_with_complex_info(df_verif, 'Complex')

        if not df_verif.empty:
            # Add user name (the coder)
            df_verif = pd.merge(df_verif, user_lookup.rename(columns={'ID': 'UserID', 'UserName': 'User name'}),
                                how='left', on='UserID')
            # Add verifier name
            df_verif = pd.merge(df_verif, user_lookup.rename(columns={'ID': 'VerifierID', 'UserName': 'Verifier name'}),
                                how='left', on='VerifierID')

            df_verif = df_verif.rename(columns={'Name': 'Complex name'})
            out_cols = ['Comment', 'Completed', 'Complex name', 'Verifier name', 'User name', 'Identifier']
            df_verif = df_verif[[c for c in out_cols if c in df_verif.columns]]

            label = name_prefix + 'verifiers-comments'
            export_df_to_excel(df_verif, inputDir, outputDir, label, False)
            output_files.append(os.path.join(outputDir, label + '.xlsx'))

    return output_files


# Find paths for each simplex under the actors var recursively

# the function returns all the macro events in the database, with their ID and Identifier, to be used in the dropdown menu
def build_macro_event_dropdown_menu(inputDir):
    macro_event_dropdown_menu_list = []

    # Guard: libraries must be loaded first (build_libraries must have been called)
    try:
        if setup_Complex_lib is None or data_Complex_lib is None:
            return macro_event_dropdown_menu_list
    except NameError:
        return macro_event_dropdown_menu_list

    if os.path.exists(f"{inputDir}/{'setup_Complex'}.pkl"):
        has_files = True
    else:
        has_files =False
    if(has_files):

        macro_event_name = setup_Complex_lib['Name'][0]
        macro_event_name_ID = get_setup_complex_setup_ID([macro_event_name])
        macro_event_name_ID =macro_event_name_ID.iloc[0,0]

        macro_event_IDentifier = data_Complex_lib[data_Complex_lib['ID_setup_complex'] ==macro_event_name_ID]

        def _format_macro_row(x):
            cid = x['ID_data_complex']
            ident = x.get('Identifier', '')
            if pd.isna(ident) or str(ident).strip() == '':
                ident = compute_identifier(cid)
            if ident:
                return f"{cid} - {macro_event_name}: {ident}"
            return f"{cid} - {macro_event_name}"
        macro_event_dropdown_menu_list = macro_event_IDentifier.apply(_format_macro_row, axis=1).tolist()

    return macro_event_dropdown_menu_list


def _get_structural_hierarchical_types():
    """Identify truly hierarchical complex types using the setup_xref_Complex-Complex
    table structure rather than grammar markers.
    A complex type is 'deeply hierarchical' if it has complex children AND at least
    one of those children also has complex children (i.e., multi-level nesting).
    This mirrors the <++ grammar rule semantics.
    Only types with at least one data instance are returned."""

    hierarchical_list = []
    if setup_xref_Complex_Complex_lib is None or setup_xref_Complex_Complex_lib.empty:
        return hierarchical_list
    if 'HigherComplex' not in setup_xref_Complex_Complex_lib.columns:
        return hierarchical_list

    # Use Relationship == 2 in setup_xref_Complex-Complex to identify hierarchical types.
    # Both ends of Relationship=2 links are hierarchical (e.g., Macro Event, Event, Semantic Triplet).
    hierarchical_ids = set()
    if 'Relationship' in setup_xref_Complex_Complex_lib.columns:
        rel2 = setup_xref_Complex_Complex_lib[
            setup_xref_Complex_Complex_lib['Relationship'] == 2
        ]
        for _, r2row in rel2.iterrows():
            hid = r2row['HigherComplex']
            lid = r2row['LowerComplex']
            if hid != -1:
                hierarchical_ids.add(hid)
            if lid != -1:
                hierarchical_ids.add(lid)
    # Fallback if Relationship column not available
    if not hierarchical_ids:
        _children_of = {}
        for _, xrow in setup_xref_Complex_Complex_lib.iterrows():
            _children_of.setdefault(xrow["HigherComplex"], set()).add(xrow["LowerComplex"])
        for higher_id, children in _children_of.items():
            if len(children) >= 3:
                for child_id in children:
                    if child_id in _children_of:
                        hierarchical_ids.add(higher_id)
                        break

    for setup_id in hierarchical_ids:
        name_rows = setup_Complex_lib[setup_Complex_lib['ID_setup_complex'] == setup_id]
        if name_rows.empty:
            continue
        complex_name = name_rows.iloc[0]['Name']
        # Only include if there are actual data instances
        instance_count = len(data_Complex_lib[data_Complex_lib['ID_setup_complex'] == setup_id])
        if instance_count > 0:
            hierarchical_list.append(complex_name)

    hierarchical_list.sort()
    return hierarchical_list


def build_hierarchical_complex_dropdown_menu(inputDir):
    """Build a dropdown list of hierarchical complex types.
    Primary approach: use GrammarRule_Text column in setup_Complex to find
    objects whose grammar rule starts with <++ (hierarchical complex objects).
    Fallback: if grammar-based filtering returns ALL complex types (meaning
    the grammar markers are not selective, as in the Avanti DB), fall back to
    structural detection via setup_xref_Complex-Complex.
    Only includes types that have at least one data instance.
    Returns a sorted list of complex type names."""

    hierarchical_list = []

    if len(setup_Complex_lib) == 0:
        print("    RETURNING EMPTY - setup_Complex_lib is empty")
        return hierarchical_list

    # --- Primary approach: grammar-based filtering ---
    if 'GrammarRule_Text' in setup_Complex_lib.columns:
        for _, row in setup_Complex_lib.iterrows():
            grammar = str(row.get("GrammarRule_Text", "")).replace('_x000d_', '').strip()
            if grammar.startswith("<++"):
                complex_name = row["Name"]
                setup_id = row["ID_setup_complex"]
                # Only include if there are actual data instances
                instance_count = len(data_Complex_lib[data_Complex_lib["ID_setup_complex"] == setup_id])
                if instance_count > 0:
                    hierarchical_list.append(complex_name)

    # Count ALL complex types with data instances for comparison
    all_types_with_data = []
    for _, row in setup_Complex_lib.iterrows():
        setup_id = row["ID_setup_complex"]
        if len(data_Complex_lib[data_Complex_lib["ID_setup_complex"] == setup_id]) > 0:
            all_types_with_data.append(row["Name"])

    # If grammar filter returned ALL types (not selective) or returned nothing,
    # fall back to structural detection
    if len(hierarchical_list) == 0 or len(hierarchical_list) >= len(all_types_with_data):
        structural_list = _get_structural_hierarchical_types()
        if structural_list:
            print(f"  Using structural hierarchy detection: {len(structural_list)} hierarchical types "
                  f"(grammar filter found {len(hierarchical_list)} of {len(all_types_with_data)} total)")
            hierarchical_list = structural_list

    hierarchical_list.sort()
    return hierarchical_list


def higher_lower(inputDir, outputDir, complex_name, export_identifier=False):
    df_builder = []
    # Track ancestor column names for later column ordering (populated from first processed ID)
    _ancestor_id_cols = []   # e.g., ["Evento", "Macro evento"] — parent first, root last
    _order_cols = []          # e.g., ["Semantic Triplet Order", "Evento Order"]
    _hierarchy_captured = False

    unique_IDs = set(data_xref_simplex_complex_ALL_lib[data_xref_simplex_complex_ALL_lib["Complex name"] == complex_name]["ID_data_complex"])

    # Fallback: if no IDs found in the ALL lib (e.g., leaf complexes not in complex-complex hierarchy),
    # find them directly from data_Complex_lib via setup_Complex_lib
    if not unique_IDs:
        setup_ids = setup_Complex_lib[setup_Complex_lib["Name"] == complex_name]["ID_setup_complex"]
        if len(setup_ids) > 0:
            unique_IDs = set(data_Complex_lib[data_Complex_lib["ID_setup_complex"].isin(setup_ids)]["ID_data_complex"])
            print(f"  Fallback: found {len(unique_IDs)} instances of '{complex_name}' directly from data_Complex")

    total_IDs = len(unique_IDs)
    import time as _time
    _t0 = _time.time()
    for idx, id in enumerate(unique_IDs, 1):
        if idx <= 3 or idx % 500 == 0 or idx == total_IDs:
            _elapsed = _time.time() - _t0
            _rate = idx / _elapsed if _elapsed > 0 else 0
            _eta = int((total_IDs - idx) / _rate) if _rate > 0 else 0
            print(f"Processing complex {idx}/{total_IDs}  ({_rate:.0f}/sec, ~{_eta}s remaining)")

        # Walk up the hierarchy generically (works with any grammar/language)
        ancestors = _get_ancestor_chain(id)

        # Capture hierarchy column names once (from the first ID with a full chain)
        if not _hierarchy_captured and ancestors:
            root = ancestors[-1]
            root_child = ancestors[-2] if len(ancestors) >= 2 else None
            _ancestor_id_cols = [root["name"]]
            _order_cols = [f"{complex_name} Order"]
            if root_child is not None:
                _ancestor_id_cols.append(root_child["name"])
                _order_cols.append(f"{root_child['name']} Order")
            _hierarchy_captured = True

        # Use indexed lookup instead of DataFrame scan
        _all_children_raw = _idx_all_lib_by_complex.get(id, [])
        _all_children = [(lower, cname) for lower, cname in _all_children_raw if lower != id]

        # Check if this complex has complex children or is a leaf complex
        has_complex_children = id in _idx_children_of_higher

        if not has_complex_children:
            # LEAF COMPLEX (e.g., Age, Collective actor): no complex children,
            # only simplex values directly attached. Extract them into a single row.
            row_dict = {}
            simplex_entries = _idx_xref_simplex_complex.get(id, [])

            for simplex_id, _ in simplex_entries:
                simplex_name = _get_simplex_name(simplex_id)
                text_value = get_text_value_simplex(simplex_id)
                col_name = f"{complex_name} > {simplex_name}"
                if col_name in row_dict:
                    existing_values = str(row_dict[col_name]).split(", ")
                    if str(text_value) not in existing_values:
                        row_dict[col_name] = str(row_dict[col_name]) + ", " + str(text_value)
                else:
                    row_dict[col_name] = text_value

            # Also traverse any complex children that ARE in data_xref_Complex_Complex (just in case)
            # and add Identifier if in identifier mode
            if export_identifier:
                top_identifier = _get_identifier(id)
                row_dict[complex_name + " Identifier"] = top_identifier

            if row_dict:
                # Walk up hierarchy for context (generic ancestor columns)
                _add_ancestor_columns(row_dict, ancestors, complex_name)
                row_dict[complex_name] = str(id)
                df_builder.append(row_dict)
            continue  # skip the children_by_type logic below

        # Group top-level children by their complex type name (e.g., Participant-S, Process, Participant-O)
        # Include all children that exist in the data, regardless of Required flag
        # (e.g., Participant-O is optional in the grammar but should be shown when present)
        # Track the Order for column sorting (S-V-O)
        children_by_type = {}  # { "Participant-S": [child_id1], "Process": [child_id2, child_id3], ... }
        type_order = {}  # { "Participant-S": 1, "Process": 2, "Participant-O": 3 }
        for val, child_type in _all_children:
            # Get Order and Required status via index — O(1)
            cc_info = _idx_cc_order.get((id, val))
            if cc_info is not None and child_type not in type_order:
                type_order[child_type] = cc_info[0]  # Order

            # Include ALL children that exist in the data, regardless of Required flag
            # (e.g., Participant-O is optional in the grammar but should be shown when present)

            # print(f"  Complex name we're processing: {child_type}, child ID: {val}")
            if child_type not in children_by_type:
                children_by_type[child_type] = []
            if val not in children_by_type[child_type]:
                children_by_type[child_type].append(val)

        # Sort children_by_type by Order so we process S before V before O
        sorted_types = sorted(children_by_type.keys(), key=lambda t: type_order.get(t, 999))

        if export_identifier:
            # Export the Identifier string for the top-level complex and each child
            # Also build child Identifiers per type for the cartesian product
            identifier_rows_by_type = {}
            for child_type in sorted_types:
                child_ids = children_by_type[child_type]
                identifier_rows_by_type[child_type] = []
                for child_id in child_ids:
                    child_identifier = _get_identifier(child_id)
                    identifier_rows_by_type[child_type].append({
                        child_type + " Identifier": child_identifier
                    })

            # Cartesian product of Identifiers across types
            combined_rows = [{}]
            for child_type in sorted_types:
                id_partials = identifier_rows_by_type.get(child_type, [])
                if not id_partials:
                    continue
                new_combined = []
                for existing in combined_rows:
                    for partial in id_partials:
                        merged = {**existing, **partial}
                        new_combined.append(merged)
                combined_rows = new_combined

            # Get top-level Identifier
            top_identifier = _get_identifier(id)

            for row_dict in combined_rows:
                if len(row_dict) > 0:
                    _add_ancestor_columns(row_dict, ancestors, complex_name)
                    row_dict[complex_name] = str(id)
                    row_dict[complex_name + " Identifier"] = top_identifier
                    df_builder.append(row_dict)

        else:
            # Original expanded column export
            # Traverse each child independently to get its simplex values
            partial_rows_by_type = {}
            columns_by_type = {}  # Track which columns come from which top-level type
            for child_type in sorted_types:
                child_ids = children_by_type[child_type]
                partial_rows_by_type[child_type] = []
                for child_id in child_ids:
                    partials = _traverse_complex_to_simplex(child_id, required_only=False, col_prefix=child_type)
                    partial_rows_by_type[child_type].extend(partials)
                # Collect all column names from this type's partials
                type_cols = set()
                for p in partial_rows_by_type[child_type]:
                    type_cols.update(p.keys())
                columns_by_type[child_type] = type_cols

            # Build output rows:
            # - Multiple instances of the SAME type (e.g., two Participant-O) are MERGED into one row
            # - Different types (S, V, O) are crossed via cartesian product
            combined_rows = [{}]
            for child_type in sorted_types:
                partials = partial_rows_by_type.get(child_type, [])
                if not partials:
                    continue

                # Merge all instances of this type into a single dict
                # (e.g., two Participant-O children: Negro + jail → one dict with both)
                merged_type = {}
                for partial in partials:
                    for col, val in partial.items():
                        if col in merged_type:
                            # Comma-separate if different value
                            existing_values = str(merged_type[col]).split(", ")
                            if str(val) not in existing_values:
                                merged_type[col] = str(merged_type[col]) + ", " + str(val)
                        else:
                            merged_type[col] = val

                # Cartesian product across types (S × V × O)
                new_combined = []
                for existing in combined_rows:
                    merged = {**existing, **merged_type}
                    new_combined.append(merged)
                combined_rows = new_combined

            for row_dict in combined_rows:
                if len(row_dict) > 0:
                    _add_ancestor_columns(row_dict, ancestors, complex_name)
                    row_dict[complex_name] = str(id)
                    row_dict["_type_order"] = type_order
                    df_builder.append(row_dict)

    df = pd.DataFrame(df_builder)

    # Remove duplicate rows (can arise from redundant xref paths in the data)
    # Drop _type_order before dedup since it's a dict and not comparable
    type_order_col = None
    if "_type_order" in df.columns:
        type_order_col = df["_type_order"]
        df = df.drop(columns=["_type_order"])
    df = df.drop_duplicates()
    if type_order_col is not None:
        # Re-add _type_order for column sorting (align with deduplicated index)
        df["_type_order"] = type_order_col.loc[df.index]

    # Build hierarchy column lists: root first, then root_child, then orders (root_child order, complex order)
    # _ancestor_id_cols = [root_name, root_child_name], _order_cols = [complex Order, root_child Order]
    hierarchy_cols = _ancestor_id_cols + list(reversed(_order_cols))
    sort_cols = [c for c in hierarchy_cols if c in df.columns]

    if export_identifier:
        # For identifier mode, order: hierarchy, then ID, top Identifier, then child Identifiers
        id_col = complex_name
        top_id_col = complex_name + " Identifier"
        cols = []
        for hc in hierarchy_cols:
            if hc in df.columns:
                cols.append(hc)
        if id_col in df.columns:
            cols.append(id_col)
        if top_id_col in df.columns:
            cols.append(top_id_col)
        for col in df.columns:
            if col not in cols:
                cols.append(col)
        df = df[cols]

        # Sort by hierarchy
        if sort_cols:
            df = df.sort_values(sort_cols).reset_index(drop=True)

        suffix = '_IDENTIFIER'
    else:
        # Build column order from the tracked _column_order lists
        if "_column_order" in df.columns:
            df = df.drop(columns=["_column_order"])

        # Sort columns by S-V-O prefix order, then alphabetically within each group
        # Extract all type_order mappings that were stored
        svo_order = {}  # { "Participant-S": 1, "Process": 2, "Participant-O": 3 }
        for row_dict in df_builder:
            if "_type_order" in row_dict:
                for k, v in row_dict["_type_order"].items():
                    if k not in svo_order:
                        svo_order[k] = v

        if "_type_order" in df.columns:
            df = df.drop(columns=["_type_order"])

        def col_sort_key(col_name):
            # Extract the prefix (e.g., "Participant-S" from "Participant-S > Individual > Name")
            for prefix in sorted(svo_order.keys(), key=lambda k: svo_order[k]):
                if col_name.startswith(prefix + " > "):
                    return (svo_order[prefix], col_name)
            return (999, col_name)

        # Hierarchy columns first, then complex ID, then S-V-O columns
        svo_cols = [c for c in df.columns if c != complex_name and c not in hierarchy_cols]
        sorted_svo = sorted(svo_cols, key=col_sort_key)

        cols = []
        for hc in hierarchy_cols:
            if hc in df.columns:
                cols.append(hc)
        if complex_name in df.columns:
            cols.append(complex_name)
        cols.extend(sorted_svo)
        df = df[cols]

        # Sort rows by hierarchy
        active_sort = [c for c in sort_cols if c in df.columns]
        if active_sort:
            df = df.sort_values(active_sort).reset_index(drop=True)

        suffix = '_ALL'

    res = export_df_to_excel(df, inputDir, outputDir, complex_name + suffix, False)

    return df


def _traverse_complex_to_simplex(start_complex_id, required_only=False, col_prefix=""):
    """Traverse a single complex down to its leaf simplex values.
    Returns a list of dicts, where each dict is one possible row.
    Multiple children of the same complex type produce cartesian products.
    If required_only=True, only include Required complex/simplex children.
    col_prefix is prepended to all column names (e.g., 'Participant-S' to distinguish S from O)."""

    # Start with the simplex values directly attached to this complex
    base = {}
    sc = get_required_simplex_objects(start_complex_id, required_only=required_only)
    for simplex_id in sc:
        parent_name = _get_complex_name(start_complex_id)
        simplex_name = _get_simplex_name(simplex_id)
        if col_prefix:
            col_name = f"{col_prefix} > {parent_name} > {simplex_name}"
        else:
            col_name = f"{parent_name} > {simplex_name}"
        text_value = str(get_text_value_simplex(simplex_id))
        # print(f"  Simplex name: {simplex_name}, parent complex: {parent_name}, ID: {simplex_id}")
        if col_name in base:
            existing_values = str(base[col_name]).split(", ")
            if text_value not in existing_values:
                base[col_name] = str(base[col_name]) + ", " + text_value
        else:
            base[col_name] = text_value

    # Get complex children, grouped by their setup complex type
    cc = get_required_complex_objects(start_complex_id, required_only=required_only)
    if not cc:
        # Leaf node — return just the base simplex values
        return [base] if base else [{}]

    # Group children by their complex type name
    children_by_type = {}
    for child_id in cc:
        child_type = _get_complex_name(child_id)
        if child_type not in children_by_type:
            children_by_type[child_type] = []
        children_by_type[child_type].append(child_id)

    # Recursively traverse each child, then cartesian product across types
    partial_rows_by_type = {}
    for child_type, child_ids in children_by_type.items():
        partial_rows_by_type[child_type] = []
        for child_id in child_ids:
            child_rows = _traverse_complex_to_simplex(child_id, required_only=required_only, col_prefix=col_prefix)
            partial_rows_by_type[child_type].extend(child_rows)

    # Start with base simplex values
    combined_rows = [dict(base)]

    # Cartesian product across all child types
    for child_type, partials in partial_rows_by_type.items():
        if not partials:
            continue
        new_combined = []
        for existing in combined_rows:
            for partial in partials:
                merged = {**existing, **partial}
                new_combined.append(merged)
        combined_rows = new_combined

    return combined_rows if combined_rows else [{}]


# ═══════════════════════════════════════════════════════════════════════════
# Fast lookup indexes — built once by _build_lookup_indexes(), used by all
# helper functions below for O(1) access instead of DataFrame scans.
# ═══════════════════════════════════════════════════════════════════════════

_idx_complex_to_setup = {}      # data_complex_id → setup_complex_id
_idx_setup_complex_name = {}    # setup_complex_id → Name
_idx_simplex_to_setup = {}      # data_simplex_id → setup_simplex_id
_idx_setup_simplex_name = {}    # setup_simplex_id → Name
_idx_simplex_dnt = {}           # data_simplex_id → ID_data_date_number_text
_idx_simplex_valuetype = {}     # setup_simplex_id → ValueType (int)
_idx_text_value = {}            # ID_data_date_number_text → Value (from SimplexText)
_idx_number_value = {}          # ID_data_date_number_text → Value (from SimplexNumber)
_idx_date_value = {}            # ID_data_date_number_text → Value (from SimplexDate)
_idx_complex_identifier = {}    # data_complex_id → Identifier string
_idx_parent_of_lower = {}       # data_complex_id (LOWER) → (parent_id, Order)
_idx_children_of_higher = {}    # data_complex_id (HIGHER) → list of LOWER ids
_idx_xref_simplex_complex = {}  # data_complex_id → list of (simplex_id, setup_xref_id)
_idx_complex_id_exists = set()  # set of all data_complex_ids that exist
_idx_xref_cc_setup = {}         # ID_setup_xref_complex-complex → Required (bool)
_idx_xref_sc_setup = {}         # ID_setup_xref_simplex-complex → Required (bool)
_idx_all_lib_by_complex = {}    # ID_data_complex → list of (ID_data_complex_LOWER, Child_name) from ALL_lib
_idx_cc_order = {}              # (HIGHER_id, LOWER_id) → (Order, setup_xref_id)
_idx_dnt_to_simplex = {}        # ID_data_date_number_text → list of data_simplex_id (reverse of _idx_simplex_dnt)
_idx_simplex_to_complexes = {}  # data_simplex_id → list of data_complex_id (reverse of _idx_xref_simplex_complex)


def _build_lookup_indexes():
    """Build dictionary indexes from the global DataFrames for O(1) lookups.
    Called once at the end of build_libraries()."""
    global _idx_complex_to_setup, _idx_setup_complex_name
    global _idx_simplex_to_setup, _idx_setup_simplex_name
    global _idx_simplex_dnt, _idx_simplex_valuetype
    global _idx_text_value, _idx_number_value, _idx_date_value
    global _idx_complex_identifier, _idx_parent_of_lower
    global _idx_children_of_higher, _idx_xref_simplex_complex
    global _idx_complex_id_exists, _idx_xref_cc_setup, _idx_xref_sc_setup
    global _idx_all_lib_by_complex, _idx_cc_order
    global _idx_dnt_to_simplex, _idx_simplex_to_complexes

    print("Building fast lookup indexes...")

    # data_complex_id → setup_complex_id
    _idx_complex_to_setup = dict(zip(
        data_Complex_lib["ID_data_complex"], data_Complex_lib["ID_setup_complex"]))

    # data_complex_id → Identifier
    if "Identifier" in data_Complex_lib.columns:
        mask = data_Complex_lib["Identifier"].notna()
        ids = data_Complex_lib.loc[mask, "ID_data_complex"]
        idents = data_Complex_lib.loc[mask, "Identifier"].astype(str)
        _idx_complex_identifier.update(dict(zip(ids, idents)))

    # set of all existing data_complex_ids
    _idx_complex_id_exists = set(data_Complex_lib["ID_data_complex"])

    # setup_complex_id → Name
    _idx_setup_complex_name = dict(zip(
        setup_Complex_lib["ID_setup_complex"], setup_Complex_lib["Name"]))

    # data_simplex_id → setup_simplex_id, ID_data_date_number_text
    _idx_simplex_to_setup = dict(zip(
        data_Simplex_lib["ID_data_simplex"], data_Simplex_lib["ID_setup_simplex"]))
    _idx_simplex_dnt = dict(zip(
        data_Simplex_lib["ID_data_simplex"], data_Simplex_lib["ID_data_date_number_text"]))

    # setup_simplex_id → Name, ValueType
    _idx_setup_simplex_name = dict(zip(
        setup_Simplex_lib["ID_setup_simplex"], setup_Simplex_lib["Name"]))
    if "ValueType" in setup_Simplex_lib.columns:
        vt_series = pd.to_numeric(setup_Simplex_lib["ValueType"], errors='coerce').fillna(1).astype(int)
        _idx_simplex_valuetype = dict(zip(setup_Simplex_lib["ID_setup_simplex"], vt_series))

    # Value lookup tables
    _idx_text_value = dict(zip(
        data_SimplexText_lib["ID_data_date_number_text"], data_SimplexText_lib["Value"]))
    _idx_number_value = dict(zip(
        data_SimplexNumber_lib["ID_data_date_number_text"], data_SimplexNumber_lib["Value"]))
    if data_SimplexDate_lib is not None and len(data_SimplexDate_lib) > 0:
        _idx_date_value = dict(zip(
            data_SimplexDate_lib["ID_data_date_number_text"], data_SimplexDate_lib["Value"]))

    # data_xref_Complex-Complex: parent/child relationships (vectorized)
    _idx_children_of_higher.clear()
    _idx_parent_of_lower.clear()
    cc_df = data_xref_Complex_Complex_lib
    has_order = "Order" in cc_df.columns
    has_setup_xref = "ID_setup_xref_complex-complex" in cc_df.columns
    highs = cc_df["ID_data_complex_HIGHER"].values
    lows = cc_df["ID_data_complex_LOWER"].values
    orders = cc_df["Order"].values if has_order else [0] * len(cc_df)
    for i in range(len(cc_df)):
        h, l, o = highs[i], lows[i], orders[i]
        _idx_parent_of_lower[l] = (h, o)
        if h not in _idx_children_of_higher:
            _idx_children_of_higher[h] = []
        _idx_children_of_higher[h].append(l)

    # setup_xref_complex-complex: Required flag
    if has_setup_xref:
        _idx_xref_cc_data_to_setup = {}
        sxrefs = cc_df["ID_setup_xref_complex-complex"].values
        for i in range(len(cc_df)):
            _idx_xref_cc_data_to_setup[(highs[i], lows[i])] = sxrefs[i]
    if "Required" in setup_xref_Complex_Complex_lib.columns:
        _idx_xref_cc_setup = dict(zip(
            setup_xref_Complex_Complex_lib["ID_setup_xref_complex-complex"],
            setup_xref_Complex_Complex_lib["Required"]))

    # data_xref_Simplex-Complex: simplex→complex links (vectorized)
    _idx_xref_simplex_complex.clear()
    sc_df = data_xref_simplex_complex_lib
    sc_cids = sc_df["ID_data_complex"].values
    sc_sids = sc_df["ID_data_simplex"].values
    sc_xids = sc_df["ID_setup_xref_simplex-complex"].values
    for i in range(len(sc_df)):
        cid = sc_cids[i]
        if cid not in _idx_xref_simplex_complex:
            _idx_xref_simplex_complex[cid] = []
        _idx_xref_simplex_complex[cid].append((sc_sids[i], sc_xids[i]))

    # Reverse index: simplex_id → list of complex_ids (for search)
    _idx_simplex_to_complexes.clear()
    for i in range(len(sc_df)):
        sid = sc_sids[i]
        if sid not in _idx_simplex_to_complexes:
            _idx_simplex_to_complexes[sid] = []
        _idx_simplex_to_complexes[sid].append(sc_cids[i])

    # Reverse index: dnt_id → list of simplex_ids (for search)
    _idx_dnt_to_simplex.clear()
    s_dnt_ids = data_Simplex_lib["ID_data_date_number_text"].values
    s_ids = data_Simplex_lib["ID_data_simplex"].values
    for i in range(len(data_Simplex_lib)):
        dnt = s_dnt_ids[i]
        if dnt not in _idx_dnt_to_simplex:
            _idx_dnt_to_simplex[dnt] = []
        _idx_dnt_to_simplex[dnt].append(s_ids[i])

    # setup_xref_simplex-complex: Required flag
    if "Required" in setup_xref_simplex_complex_lib.columns:
        _idx_xref_sc_setup = dict(zip(
            setup_xref_simplex_complex_lib["ID_setup_xref_simplex-complex"],
            setup_xref_simplex_complex_lib["Required"]))

    # data_xref_simplex_complex_ALL_lib: group by ID_data_complex for fast child lookup (vectorized)
    _idx_all_lib_by_complex.clear()
    if data_xref_simplex_complex_ALL_lib is not None and len(data_xref_simplex_complex_ALL_lib) > 0:
        has_child_name = "Child name" in data_xref_simplex_complex_ALL_lib.columns
        has_lower = "ID_data_complex_LOWER" in data_xref_simplex_complex_ALL_lib.columns
        if has_child_name and has_lower:
            al_cids = data_xref_simplex_complex_ALL_lib["ID_data_complex"].values
            al_lowers = data_xref_simplex_complex_ALL_lib["ID_data_complex_LOWER"].values
            al_names = data_xref_simplex_complex_ALL_lib["Child name"].values
            for i in range(len(data_xref_simplex_complex_ALL_lib)):
                cid = al_cids[i]
                if cid not in _idx_all_lib_by_complex:
                    _idx_all_lib_by_complex[cid] = []
                _idx_all_lib_by_complex[cid].append((al_lowers[i], al_names[i]))

    # data_xref_Complex-Complex: (HIGHER, LOWER) → (Order, setup_xref_id) for quick lookup (vectorized)
    _idx_cc_order.clear()
    # Reuse arrays already extracted above for cc_df
    cc_sxrefs = cc_df["ID_setup_xref_complex-complex"].values if has_setup_xref else [None] * len(cc_df)
    for i in range(len(cc_df)):
        _idx_cc_order[(highs[i], lows[i])] = (orders[i] if has_order else 999, cc_sxrefs[i])

    # Invalidate _get_role_name cache so it rebuilds on next call
    if hasattr(_get_role_name, '_cache'):
        del _get_role_name._cache

    print("  Lookup indexes ready.")


def _get_complex_name(data_complex_id):
    """Helper to resolve a data complex ID to its setup name — O(1)."""
    setup_id = _idx_complex_to_setup.get(data_complex_id)
    if setup_id is not None:
        name = _idx_setup_complex_name.get(setup_id)
        if name is not None:
            return name
    return f"Complex_{data_complex_id}"


def _get_ancestor_chain(data_complex_id):
    """Walk up the complex-complex hierarchy from a data complex ID — O(depth).
    Returns a list of ancestor dicts from immediate parent up to the top-level root."""
    ancestors = []
    current_id = data_complex_id
    visited = set()
    while current_id not in visited:
        visited.add(current_id)
        parent_info = _idx_parent_of_lower.get(current_id)
        if parent_info is None:
            break
        parent_id, order = parent_info
        if parent_id < 0 or parent_id not in _idx_complex_id_exists:
            break
        parent_name = _get_complex_name(parent_id)
        ancestors.append({"data_id": parent_id, "name": parent_name, "order": order})
        current_id = parent_id
    return ancestors


def _add_ancestor_columns(row_dict, ancestors, complex_name):
    """Add two levels of hierarchy context to a row_dict: the root ancestor
    and its immediate child (second-from-top).  Also adds the order of the
    analyzed complex within its immediate parent and the order of the
    second-level ancestor within the root.

    This mirrors the original 2-level context (e.g., Macro Event + Event)
    but derives the names from the actual grammar, making it work across
    any PC-ACE project regardless of language or hierarchy depth.

    Columns added (using actual setup names from the grammar):
      - '{root_name}'            = root ancestor data_id
      - '{root_child_name}'      = second-level ancestor data_id
      - '{root_child_name} Order'= order of root_child within root
      - '{complex_name} Order'   = order of analyzed complex within its parent
    """
    if not ancestors:
        return  # no hierarchy context available

    # Root = last in ancestor chain (topmost); root_child = second-to-last
    root = ancestors[-1]
    root_child = ancestors[-2] if len(ancestors) >= 2 else None
    immediate_parent = ancestors[0]

    # Root ancestor column (e.g., "Macro Event" / "Macro evento")
    row_dict[root["name"]] = root["data_id"]

    # Second-level ancestor column (e.g., "Event" / "Evento")
    if root_child is not None:
        row_dict[root_child["name"]] = root_child["data_id"]
        # Order of root_child within root
        row_dict[f"{root_child['name']} Order"] = root_child["order"]

    # Order of the analyzed complex within its immediate parent
    row_dict[f"{complex_name} Order"] = immediate_parent["order"]




def _get_identifier(data_complex_id):
    """Helper to retrieve the Identifier string for a data complex ID — O(1)."""
    return _idx_complex_identifier.get(data_complex_id, "")


def _get_simplex_name(data_simplex_id):
    """Helper to resolve a data simplex ID to its setup name — O(1)."""
    setup_id = _idx_simplex_to_setup.get(data_simplex_id)
    if setup_id is not None:
        name = _idx_setup_simplex_name.get(setup_id)
        if name is not None:
            return name
    return f"Simplex_{data_simplex_id}"


def get_required_complex_objects(data_complex_id, required_only=False):
    """Get complex children — O(1) lookup via index."""
    children = _idx_children_of_higher.get(data_complex_id, [])
    if not required_only:
        return list(children)

    res = []
    for child_id in children:
        # Look up the setup xref Required flag
        xref_rows = data_xref_Complex_Complex_lib[
            (data_xref_Complex_Complex_lib["ID_data_complex_HIGHER"] == data_complex_id) &
            (data_xref_Complex_Complex_lib["ID_data_complex_LOWER"] == child_id)
        ]
        if len(xref_rows) > 0 and "ID_setup_xref_complex-complex" in xref_rows.columns:
            setup_xref_id = xref_rows["ID_setup_xref_complex-complex"].iloc[0]
            if _idx_xref_cc_setup.get(setup_xref_id, False):
                res.append(child_id)
    return res

def get_required_simplex_objects(data_complex_id, required_only=False):
    """Get simplex objects for a complex — O(1) lookup via index."""
    entries = _idx_xref_simplex_complex.get(data_complex_id, [])

    if not required_only:
        return [sid for sid, _ in entries]

    res = []
    for simplex_id, setup_xref_id in entries:
        # print(f"  Processing simplex ID: {simplex_id}, setup xref ID: {setup_xref_id}")
        if _idx_xref_sc_setup.get(setup_xref_id, False):
            res.append(simplex_id)
    return res

def get_text_value_simplex(data_simplex_id):
    """Resolve a simplex ID to its text/number/date value — O(1) lookups."""
    dnt_id = _idx_simplex_dnt.get(data_simplex_id)
    if dnt_id is None:
        return ""

    setup_id = _idx_simplex_to_setup.get(data_simplex_id)
    value_type = _idx_simplex_valuetype.get(setup_id, 1) if setup_id else 1

    if value_type == 2:
        val = _idx_number_value.get(dnt_id)
    elif value_type == 3:
        val = _idx_date_value.get(dnt_id)
    elif value_type == 4:
        val = _idx_text_value.get(dnt_id)
        if val is None:
            val = _idx_number_value.get(dnt_id)
    else:
        val = _idx_text_value.get(dnt_id)

    if val is not None:
        return str(val)

    # Fallback: try all tables
    for idx in [_idx_text_value, _idx_number_value, _idx_date_value]:
        val = idx.get(dnt_id)
        if val is not None:
            return str(val)
    return ""

    return str(res)


def compute_identifier(data_complex_id):
    """Recursively compute the Identifier string for a data complex.
    Format: (simplex_value1 simplex_value2 (child1_identifier) (child2_identifier) ...)
    Uses O(1) lookup indexes instead of DataFrame scans for speed."""

    parts = []

    # Get all simplex values attached to this complex via fast lookup index
    simplex_pairs = _idx_xref_simplex_complex.get(data_complex_id, [])
    for simplex_id, xref_id in simplex_pairs:
        try:
            val = get_text_value_simplex(simplex_id)
            if val:
                parts.append(str(val))
        except Exception:
            pass

    # Get all complex children via fast lookup index
    child_ids = _idx_children_of_higher.get(data_complex_id, [])
    # Sort children by order if available
    if child_ids:
        child_ids_sorted = sorted(child_ids, key=lambda cid: _idx_cc_order.get((data_complex_id, cid), (999, None))[0])
        for child_id in child_ids_sorted:
            child_identifier = compute_identifier(child_id)
            if child_identifier:
                parts.append(child_identifier)

    if parts:
        return "(" + " ".join(parts) + ")"
    return ""


def update_all_identifiers(inputDir):
    """Recompute and update the Identifier field for all complexes in data_Complex_lib.
    Saves the updated table back to both .xlsx and .pkl."""
    global data_Complex_lib

    # Drop any fully-empty rows (Excel padding)
    data_Complex_lib = data_Complex_lib.dropna(how='all').reset_index(drop=True)

    total = len(data_Complex_lib)
    print(f"Updating identifiers... {total} complexes to process.")

    # Pre-extract IDs as numpy array for fast iteration
    complex_ids = data_Complex_lib["ID_data_complex"].values
    new_identifiers = []

    for i in range(total):
        new_identifiers.append(compute_identifier(complex_ids[i]))

        if (i + 1) % 500 == 0:
            print(f"  Updating identifiers... Processed {i + 1}/{total} complexes...")

    data_Complex_lib["Identifier"] = new_identifiers
    print(f"  Updating identifiers... Done. Processed {total} complexes.")

    # Save updated data_Complex back to files
    output_xlsx = os.path.join(inputDir, "data_Complex.xlsx")
    output_pkl = os.path.join(inputDir, "data_Complex.pkl")

    print(f"  Now saving data_Complex.xlsx file. Please be patient...")
    data_Complex_lib.to_excel(output_xlsx, index=False)
    print(f"  Now saving data_Complex.pkl file. Please be patient...")
    data_Complex_lib.to_pickle(output_pkl)

    print(f"  Saved updated Identifiers to {output_xlsx} and {output_pkl}")

    mb.showwarning(title='Warning',
                   message='ALL complex objects identifiers in both data_Complex.xlsx and data_Complex.pkl have been updated')

    return data_Complex_lib


# ============================================================================
# STORY FORM EXPORT
# ============================================================================

def build_story_dropdown(complex_name):
    """Build a dropdown list of Identifiers for the given complex type.
    Returns a list of strings in the format 'ID - ComplexTypeName: Identifier'.
    If Identifier is empty, computes it on-the-fly."""

    setup_ids = setup_Complex_lib[setup_Complex_lib["Name"] == complex_name]["ID_setup_complex"]
    if len(setup_ids) == 0:
        return []

    instances = data_Complex_lib[data_Complex_lib["ID_setup_complex"].isin(setup_ids)]
    dropdown_list = []
    for _, row in instances.iterrows():
        cid = row['ID_data_complex']
        identifier = row.get('Identifier', '')
        if pd.isna(identifier) or str(identifier).strip() == '':
            identifier = compute_identifier(cid)
        if identifier:
            dropdown_list.append(f"{cid} - {complex_name}: {identifier}")
        else:
            dropdown_list.append(f"{cid} - {complex_name}")

    return dropdown_list


def story_form(data_complex_id, outputDir, filename="story_form.txt"):
    """Render a complex object in indented story form and save to a text file.
    Recursively walks the full hierarchy from the given complex down to simplex leaves.

    Parameters:
        data_complex_id: the ID_data_complex of the root complex to render
        outputDir: directory to save the output text file
        filename: output filename (default: story_form.txt)

    Returns:
        The story string and the output file path.
    """
    print(f"  Building text story form for complex ID {data_complex_id}...")
    lines = []
    _story_recurse(data_complex_id, lines, indent=0)
    story_text = "\n".join(lines)

    print(f"  Text story built ({len(lines)} lines). Now writing file...")
    output_path = os.path.join(outputDir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(story_text)

    print(f"  Story form saved to {output_path}")
    return story_text, output_path


def _get_role_name(setup_xref_id):
    """Helper to resolve a setup_xref_complex-complex ID to its Name — O(1)."""
    if not hasattr(_get_role_name, '_cache'):
        # Build cache on first call
        _get_role_name._cache = dict(zip(
            setup_xref_Complex_Complex_lib["ID_setup_xref_complex-complex"],
            setup_xref_Complex_Complex_lib["Name"]))
    return _get_role_name._cache.get(setup_xref_id, "")


def _story_recurse(data_complex_id, lines, indent=0):
    """Recursively build indented story lines for a complex object.
    Uses O(1) lookup indexes for speed."""
    prefix = "    " * indent  # 4 spaces per level

    # Get this complex's type name
    complex_name = _get_complex_name(data_complex_id)

    # Get simplex values directly attached to this complex via fast lookup
    simplex_pairs = _idx_xref_simplex_complex.get(data_complex_id, [])
    simplex_values = []
    for simplex_id, xref_id in simplex_pairs:
        simplex_name = _get_simplex_name(simplex_id)
        text_value = get_text_value_simplex(simplex_id)
        if text_value:
            simplex_values.append((simplex_name, text_value))

    # Build the header line for this complex
    if simplex_values:
        lines.append(f"{prefix}{complex_name}")
        for s_name, s_value in simplex_values:
            lines.append(f"{prefix}    {s_name}: {s_value}")
    else:
        lines.append(f"{prefix}{complex_name}")

    # Get complex children via fast lookup, sorted by order
    child_ids = _idx_children_of_higher.get(data_complex_id, [])
    if child_ids:
        child_ids_sorted = sorted(child_ids,
            key=lambda cid: _idx_cc_order.get((data_complex_id, cid), (999, None))[0])
        for child_id in child_ids_sorted:
            # Get the role name from setup_xref
            order_info = _idx_cc_order.get((data_complex_id, child_id))
            role_name = ""
            if order_info and order_info[1] is not None:
                role_name = _get_role_name(order_info[1])

            if role_name:
                lines.append(f"{prefix}    [{role_name}]")
                _story_recurse(child_id, lines, indent=indent + 2)
            else:
                _story_recurse(child_id, lines, indent=indent + 1)


def story_form_from_dropdown(dropdown_value, outputDir):
    """Called from the GUI when the user selects an item from the story dropdown.
    Parses the 'ID - Identifier' string and calls story_form.

    Parameters:
        dropdown_value: string in format 'ID - Identifier' from the dropdown
        outputDir: directory to save the output text file

    Returns:
        The story string and the output file path.
    """
    try:
        data_complex_id = int(dropdown_value.split(" - ")[0].strip())
    except (ValueError, IndexError):
        print(f"Error: could not parse ID from dropdown value: {dropdown_value}")
        return "", ""

    # Use the Identifier (truncated) as part of the filename
    identifier_part = dropdown_value.split(" - ", 1)[1] if " - " in dropdown_value else ""
    # Clean up for filename: take first 40 chars, remove special characters
    clean_id = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in identifier_part)[:40].strip()
    filename = f"story_form_{data_complex_id}_{clean_id}.txt"

    return story_form(data_complex_id, outputDir, filename)


def export_all_stories_for_type(complex_type_name, outputDir):
    """Export story forms (txt) for ALL instances of a given complex type.
    Saves all stories to a single text file.

    Parameters:
        complex_type_name: the setup complex type name (e.g., 'Tripletta semantica')
        outputDir: directory to save the output text file

    Returns:
        The output file path, or empty string if no instances found.
    """
    import time as _time
    t0 = _time.time()

    setup_ids = setup_Complex_lib[setup_Complex_lib["Name"] == complex_type_name]["ID_setup_complex"]
    if len(setup_ids) == 0:
        print(f"  No setup IDs found for complex type '{complex_type_name}'")
        return ""

    instances = data_Complex_lib[data_Complex_lib["ID_setup_complex"].isin(setup_ids)]
    if instances.empty:
        print(f"  No data instances found for complex type '{complex_type_name}'")
        return ""

    all_ids = instances['ID_data_complex'].tolist()
    print(f"  Exporting {len(all_ids)} story forms for '{complex_type_name}'...")

    all_lines = []
    all_lines.append(f"ALL STORY FORMS FOR: \"{complex_type_name}\"")
    all_lines.append(f"{len(all_ids)} object(s)")
    all_lines.append("=" * 80)

    for i, cid in enumerate(all_ids):
        if (i + 1) % 50 == 0:
            print(f"    Processing story {i + 1} of {len(all_ids)}...")
        all_lines.append("")
        identifier = _get_identifier(cid)
        all_lines.append(f"--- {complex_type_name} {cid}: {identifier} ---")
        all_lines.append("")
        _story_recurse(cid, all_lines, indent=0)
        all_lines.append("")
        all_lines.append("=" * 80)

    story_text = "\n".join(all_lines)

    clean_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in complex_type_name)[:30].strip()
    filename = f"story_all_{clean_name}.txt"
    output_path = os.path.join(outputDir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(story_text)

    elapsed = _time.time() - t0
    print(f"  All story forms saved to {output_path}  ({elapsed:.1f}s)")
    return output_path


def export_all_stories_html_for_type(complex_type_name, outputDir):
    """Export story forms (HTML) for ALL instances of a given complex type.
    Saves all stories to a single HTML file with collapsible sections.

    Parameters:
        complex_type_name: the setup complex type name (e.g., 'Tripletta semantica')
        outputDir: directory to save the output HTML file

    Returns:
        The output file path, or empty string if no instances found.
    """
    import time as _time
    t0 = _time.time()

    setup_ids = setup_Complex_lib[setup_Complex_lib["Name"] == complex_type_name]["ID_setup_complex"]
    if len(setup_ids) == 0:
        return ""

    instances = data_Complex_lib[data_Complex_lib["ID_setup_complex"].isin(setup_ids)]
    if instances.empty:
        return ""

    all_ids = instances['ID_data_complex'].tolist()

    # Cap at 200 to prevent huge HTML files
    capped = False
    if len(all_ids) > 200:
        all_ids = all_ids[:200]
        capped = True

    print(f"  Exporting {len(all_ids)} HTML story forms for '{complex_type_name}'...")

    body_parts = []
    for i, cid in enumerate(all_ids):
        if (i + 1) % 50 == 0:
            print(f"    Processing HTML story {i + 1} of {len(all_ids)}...")
        identifier = _get_identifier(cid)
        body_parts.append(f'\n<h2>{complex_type_name} (ID {cid}): {_html_escape(identifier)}</h2>')
        body_parts.append('<div class="story-section">')
        _story_recurse_html(cid, body_parts, indent=0, search_term=None)
        body_parts.append('</div>')
        if i < len(all_ids) - 1:
            body_parts.append('<hr class="story-separator">')

    subtitle = f'{len(all_ids)} object(s) of type "{_html_escape(complex_type_name)}"'
    if capped:
        subtitle += f' (showing first 200 of {instances.shape[0]})'

    html = _STORY_HTML_TEMPLATE.format(
        title=f'All Stories: {_html_escape(complex_type_name)}',
        subtitle=subtitle,
        body='\n'.join(body_parts)
    )

    clean_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in complex_type_name)[:30].strip()
    filename = f"story_all_{clean_name}.html"
    output_path = os.path.join(outputDir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    elapsed = _time.time() - t0
    print(f"  All HTML story forms saved to {output_path}  ({elapsed:.1f}s)")
    return output_path


# ============================================================================
# SIMPLEX VALUE SEARCH → STORY FORM
# ============================================================================


def _walk_up_to_hierarchical(data_complex_id, visited=None):
    """Walk up the complex-complex hierarchy from a given data complex
    to find its top-level ancestor (e.g., Macro Event).

    Uses O(1) _idx_parent_of_lower lookup instead of DataFrame scans.

    Many complex types in the grammar are marked ++ (hierarchical), including
    low-level ones like City, Actor, Participant-S.  This function walks past
    ALL of them and returns the root — the complex that has no parent in
    data_xref_Complex-Complex.  This is typically the Macro Event."""

    if visited is None:
        visited = set()

    current = data_complex_id
    while current not in visited:
        visited.add(current)
        parent_info = _idx_parent_of_lower.get(current)
        if parent_info is None:
            # No parent — this IS the top-level object
            return current
        current = parent_info[0]  # higher_id

    # Cycle detected — return what we have
    return data_complex_id


def search_simplex_value(search_term, case_sensitive=False):
    """Search for a simplex text value across all simplex tables.
    Returns a list of tuples: (data_simplex_id, value, data_complex_id, complex_name, hierarchical_id, hierarchical_identifier)

    Uses O(1) lookup indexes for dnt→simplex and simplex→complex resolution
    instead of DataFrame scans. Only the initial text search uses pandas
    str.contains (unavoidable for substring matching).

    Parameters:
        search_term: the text to search for (e.g., 'Barnesville')
        case_sensitive: if False (default), searches case-insensitively
    """
    import time as _time
    t0 = _time.time()

    results = []

    # Search in data_SimplexText_lib for matching values
    # (This pandas str.contains is unavoidable for substring matching)
    if case_sensitive:
        matching_text = data_SimplexText_lib[
            data_SimplexText_lib["Value"].astype(str).str.contains(search_term, na=False)
        ]
    else:
        matching_text = data_SimplexText_lib[
            data_SimplexText_lib["Value"].astype(str).str.contains(search_term, case=False, na=False)
        ]

    if len(matching_text) == 0:
        print(f"  No simplex values found matching '{search_term}'")
        return results

    t1 = _time.time()
    print(f"  Found {len(matching_text)} simplex text values matching '{search_term}' ({t1-t0:.1f}s)")

    # Cache walk-up results so we don't re-walk the same complex multiple times
    _hier_cache = {}

    # For each matching text value, resolve dnt→simplex→complex→hierarchical via indexes
    text_ids = matching_text["ID_data_date_number_text"].values
    text_values = matching_text["Value"].astype(str).values

    for i in range(len(matching_text)):
        text_id = text_ids[i]
        text_value = text_values[i]

        # O(1): dnt_id → list of simplex_ids
        simplex_ids = _idx_dnt_to_simplex.get(text_id, [])

        for simplex_id in simplex_ids:
            # O(1): simplex_id → list of complex_ids
            complex_ids = _idx_simplex_to_complexes.get(simplex_id, [])

            for complex_id in complex_ids:
                complex_name = _get_complex_name(complex_id)

                # Walk up to the root ancestor (cached)
                if complex_id not in _hier_cache:
                    _hier_cache[complex_id] = _walk_up_to_hierarchical(complex_id)
                hierarchical_id = _hier_cache[complex_id]

                hierarchical_identifier = ""
                if hierarchical_id is not None:
                    hierarchical_identifier = _get_identifier(hierarchical_id)

                results.append((
                    simplex_id, text_value, complex_id, complex_name,
                    hierarchical_id, hierarchical_identifier
                ))

    t2 = _time.time()
    print(f"  Resolved {len(results)} results in {t2-t1:.1f}s (total {t2-t0:.1f}s)")
    return results


def build_search_results_dropdown(search_term):
    """Search for a simplex value and build a dropdown of ++ objects
    that contain it. Returns a list of 'ID - ComplexTypeName: Identifier' strings
    for unique hierarchical objects.

    Format: "12345 - Semantic Triplet: (mob lynched Negro)"
    If Identifier is empty, computes it on-the-fly.

    Parameters:
        search_term: the text to search for (e.g., 'Barnesville')
    """

    results = search_simplex_value(search_term)
    if not results:
        return []

    # Deduplicate by hierarchical_id
    seen = set()
    dropdown_list = []
    for _, text_value, _, _, hier_id, hier_identifier in results:
        if hier_id is not None and hier_id not in seen:
            seen.add(hier_id)
            # Get the complex type name (e.g., "Semantic Triplet", "Evento")
            complex_type = _get_complex_name(hier_id)
            # If identifier is empty, try to compute it on-the-fly
            identifier = hier_identifier
            if not identifier:
                identifier = compute_identifier(hier_id)
            # Format: "12345 - Semantic Triplet: (mob lynched Negro)"
            if identifier:
                dropdown_list.append(f"{hier_id} - {complex_type}: {identifier}")
            else:
                dropdown_list.append(f"{hier_id} - {complex_type}")

    dropdown_list.sort()
    return dropdown_list


def search_and_export_stories(search_term, outputDir):
    """Search for a simplex value and export story forms for all
    ++ objects that contain it. Saves all stories to a single text file.

    Parameters:
        search_term: the text to search for (e.g., 'Barnesville')
        outputDir: directory to save the output text file

    Returns:
        The output file path, or empty string if no results.
    """

    results = search_simplex_value(search_term)
    if not results:
        mb.showwarning(title='Search',
                       message=f'No results found for "{search_term}".')
        return ""

    # Deduplicate by hierarchical_id
    seen = set()
    hierarchical_ids = []
    for _, _, _, _, hier_id, _ in results:
        if hier_id is not None and hier_id not in seen:
            seen.add(hier_id)
            hierarchical_ids.append(hier_id)

    if not hierarchical_ids:
        mb.showwarning(title='Search',
                       message=f'Found simplex values matching "{search_term}" but could not find parent hierarchical objects.')
        return ""

    # Build all stories
    all_lines = []
    all_lines.append(f"STORY FORM SEARCH RESULTS FOR: \"{search_term}\"")
    all_lines.append(f"Found in {len(hierarchical_ids)} hierarchical object(s)")
    all_lines.append("=" * 80)

    for hier_id in hierarchical_ids:
        all_lines.append("")
        identifier = _get_identifier(hier_id)
        complex_name = _get_complex_name(hier_id)
        all_lines.append(f"--- {complex_name} {hier_id}: {identifier} ---")
        all_lines.append("")
        _story_recurse(hier_id, all_lines, indent=0)
        all_lines.append("")
        all_lines.append("=" * 80)

    story_text = "\n".join(all_lines)

    # Clean search term for filename
    clean_term = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in search_term)[:30].strip()
    filename = f"story_search_{clean_term}.txt"
    output_path = os.path.join(outputDir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(story_text)

    print(f"Story search results saved to {output_path}")
    print(f"  {len(hierarchical_ids)} hierarchical objects found for '{search_term}'")

    return output_path


# ============================================================================
# STORY FORM — HTML EXPORT WITH HIGHLIGHTED SIMPLEX VALUES
# ============================================================================

# Color palette for simplex value types in HTML story form
_SIMPLEX_HTML_COLORS = {
    'text':   '#2196F3',   # blue
    'number': '#FF9800',   # orange
    'date':   '#9C27B0',   # purple
}

# Color palette for SVO roles in HTML story form
_ROLE_HTML_COLORS = {
    'Participant-S': '#E04040',  # red
    'Process':       '#4060E0',  # blue
    'Participant-O': '#30A030',  # green
    'Circumstance':  '#FF9800',  # orange
}


def _simplex_value_type_label(data_simplex_id):
    """Return the value type label ('text', 'number', 'date') for a simplex."""
    setup_id = _idx_simplex_to_setup.get(data_simplex_id)
    if setup_id is None:
        return 'text'
    vt = _idx_simplex_valuetype.get(setup_id, 1)
    if vt == 2:
        return 'number'
    elif vt == 3:
        return 'date'
    return 'text'


def _html_escape(text):
    """Escape HTML special characters."""
    if text is None:
        return ''
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))


def _highlight_search_term(text, search_term):
    """Wrap occurrences of search_term in <mark> tags (case-insensitive)."""
    if not search_term:
        return text
    import re
    escaped = re.escape(_html_escape(search_term))
    return re.sub(f'({escaped})', r'<mark>\1</mark>',
                  _html_escape(text), flags=re.IGNORECASE)


def _story_recurse_html(data_complex_id, parts, indent=0, search_term=''):
    """Recursively build HTML story for a complex object.

    Parameters:
        data_complex_id: the complex to render
        parts: list to append HTML fragments to
        indent: nesting level (for visual indentation)
        search_term: optional term to highlight in simplex values
    """
    complex_name = _get_complex_name(data_complex_id)
    margin = indent * 24  # pixels

    # Start a collapsible section
    parts.append(f'<div class="complex-block" style="margin-left:{margin}px">')
    parts.append(f'<div class="complex-header" onclick="this.parentElement.classList.toggle(\'collapsed\')">')
    parts.append(f'<span class="toggle-icon">&#9660;</span> ')
    parts.append(f'<span class="complex-name">{_html_escape(complex_name)}</span>')
    parts.append(f'</div>')  # end header

    # Simplex values
    simplex_pairs = _idx_xref_simplex_complex.get(data_complex_id, [])
    if simplex_pairs:
        parts.append('<div class="simplex-list">')
        for simplex_id, xref_id in simplex_pairs:
            simplex_name = _get_simplex_name(simplex_id)
            text_value = get_text_value_simplex(simplex_id)
            if text_value:
                vtype = _simplex_value_type_label(simplex_id)
                color = _SIMPLEX_HTML_COLORS.get(vtype, '#2196F3')
                if search_term:
                    display_value = _highlight_search_term(text_value, search_term)
                else:
                    display_value = _html_escape(text_value)
                parts.append(
                    f'<div class="simplex-row">'
                    f'<span class="simplex-name">{_html_escape(simplex_name)}:</span> '
                    f'<span class="simplex-value" style="background-color:{color}20;'
                    f'border-left:3px solid {color};padding:2px 6px">'
                    f'{display_value}</span>'
                    f'<span class="vtype-badge" style="color:{color}">[{vtype}]</span>'
                    f'</div>')
        parts.append('</div>')  # end simplex-list

    # Children
    child_ids = _idx_children_of_higher.get(data_complex_id, [])
    if child_ids:
        child_ids_sorted = sorted(child_ids,
            key=lambda cid: _idx_cc_order.get((data_complex_id, cid), (999, None))[0])
        parts.append('<div class="children-block">')
        for child_id in child_ids_sorted:
            order_info = _idx_cc_order.get((data_complex_id, child_id))
            role_name = ""
            if order_info and order_info[1] is not None:
                role_name = _get_role_name(order_info[1])

            if role_name:
                role_color = _ROLE_HTML_COLORS.get(role_name, '#666')
                parts.append(
                    f'<div class="role-label" style="margin-left:{(indent+1)*24}px;'
                    f'color:{role_color};border-left:3px solid {role_color};'
                    f'padding-left:6px">[{_html_escape(role_name)}]</div>')
                _story_recurse_html(child_id, parts, indent=indent + 2, search_term=search_term)
            else:
                _story_recurse_html(child_id, parts, indent=indent + 1, search_term=search_term)
        parts.append('</div>')  # end children-block

    parts.append('</div>')  # end complex-block


_STORY_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 20px 40px;
    background: #fafafa;
    color: #333;
    line-height: 1.5;
  }}
  h1 {{ color: #1a237e; font-size: 1.5em; border-bottom: 2px solid #1a237e; padding-bottom: 8px; }}
  h2 {{ color: #37474f; font-size: 1.2em; margin-top: 24px; }}
  .meta {{ color: #666; font-size: 0.9em; margin-bottom: 16px; }}
  .story-section {{
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }}
  .story-separator {{
    border: none;
    border-top: 2px solid #1a237e;
    margin: 24px 0;
  }}
  .complex-block {{
    margin-top: 4px;
    margin-bottom: 2px;
  }}
  .complex-block.collapsed > .simplex-list,
  .complex-block.collapsed > .children-block {{
    display: none;
  }}
  .complex-block.collapsed > .complex-header .toggle-icon {{
    transform: rotate(-90deg);
    display: inline-block;
  }}
  .complex-header {{
    cursor: pointer;
    padding: 3px 0;
    user-select: none;
  }}
  .complex-header:hover {{
    background: #f5f5f5;
    border-radius: 4px;
  }}
  .toggle-icon {{
    font-size: 0.7em;
    color: #999;
    transition: transform 0.15s;
    display: inline-block;
    width: 14px;
  }}
  .complex-name {{
    font-weight: 600;
    color: #37474f;
  }}
  .simplex-list {{
    margin: 2px 0 4px 20px;
  }}
  .simplex-row {{
    margin: 2px 0;
    font-size: 0.95em;
  }}
  .simplex-name {{
    color: #555;
    font-weight: 500;
  }}
  .simplex-value {{
    border-radius: 3px;
    font-weight: 500;
  }}
  .vtype-badge {{
    font-size: 0.75em;
    margin-left: 6px;
    opacity: 0.7;
  }}
  .role-label {{
    font-weight: 600;
    font-size: 0.9em;
    margin-top: 4px;
    margin-bottom: 2px;
  }}
  .children-block {{
    margin-top: 2px;
  }}
  mark {{
    background: #fff176;
    padding: 0 2px;
    border-radius: 2px;
  }}
  .toolbar {{
    position: sticky;
    top: 0;
    background: #fff;
    border-bottom: 1px solid #e0e0e0;
    padding: 8px 0;
    margin-bottom: 16px;
    z-index: 100;
    display: flex;
    gap: 12px;
    align-items: center;
  }}
  .toolbar button {{
    padding: 5px 14px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: #f5f5f5;
    cursor: pointer;
    font-size: 0.9em;
  }}
  .toolbar button:hover {{ background: #e0e0e0; }}
  .legend {{
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 12px;
    font-size: 0.85em;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 4px;
  }}
  .legend-swatch {{
    width: 14px;
    height: 14px;
    border-radius: 3px;
    display: inline-block;
  }}
</style>
</head>
<body>
<div class="toolbar">
  <button onclick="expandAll()">Expand All</button>
  <button onclick="collapseAll()">Collapse All</button>
</div>
<h1>{title}</h1>
<div class="meta">{meta}</div>
<div class="legend">
  <strong>Simplex types:&nbsp;</strong>
  <span class="legend-item"><span class="legend-swatch" style="background:#2196F320;border:2px solid #2196F3"></span> Text</span>
  <span class="legend-item"><span class="legend-swatch" style="background:#FF980020;border:2px solid #FF9800"></span> Number</span>
  <span class="legend-item"><span class="legend-swatch" style="background:#9C27B020;border:2px solid #9C27B0"></span> Date</span>
  &nbsp;&nbsp;<strong>Roles:&nbsp;</strong>
  <span class="legend-item" style="color:#E04040;font-weight:600">Participant-S</span>
  <span class="legend-item" style="color:#4060E0;font-weight:600">Process</span>
  <span class="legend-item" style="color:#30A030;font-weight:600">Participant-O</span>
  <span class="legend-item" style="color:#FF9800;font-weight:600">Circumstance</span>
</div>
{body}
<script>
function expandAll() {{
  document.querySelectorAll('.complex-block.collapsed').forEach(el => el.classList.remove('collapsed'));
}}
function collapseAll() {{
  document.querySelectorAll('.complex-block').forEach(el => el.classList.add('collapsed'));
  // Keep top-level expanded
  document.querySelectorAll('body > .story-section > .complex-block').forEach(el => el.classList.remove('collapsed'));
}}
</script>
</body>
</html>"""


def story_form_html(data_complex_id, outputDir, filename=None):
    """Render a complex object as an interactive HTML file with highlighted simplex values.

    Parameters:
        data_complex_id: the ID_data_complex of the root complex to render
        outputDir: directory to save the output HTML file
        filename: output filename (auto-generated if None)

    Returns:
        The output file path, or empty string on failure.
    """
    import time as _time
    t0 = _time.time()

    complex_name = _get_complex_name(data_complex_id)
    identifier = _get_identifier(data_complex_id)
    print(f"  Building HTML story form for {complex_name} (ID {data_complex_id})...")

    parts = []
    parts.append('<div class="story-section">')
    _story_recurse_html(data_complex_id, parts, indent=0)
    parts.append('</div>')

    t1 = _time.time()
    print(f"  HTML tree built ({len(parts)} elements, {t1-t0:.1f}s). Now writing file...")

    title = f"Story Form: {_html_escape(complex_name)} — {_html_escape(identifier)}"
    meta = f"Complex ID: {data_complex_id}"
    body_html = "\n".join(parts)

    html = _STORY_HTML_TEMPLATE.format(title=title, meta=meta, body=body_html)

    if filename is None:
        clean_id = "".join(c if c.isalnum() or c in (' ', '-', '_') else ''
                           for c in str(identifier))[:40].strip()
        filename = f"story_form_{data_complex_id}_{clean_id}.html"

    output_path = os.path.join(outputDir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    t2 = _time.time()
    print(f"  HTML story form saved to {output_path} ({t2-t0:.1f}s total)")
    return output_path


def story_form_html_from_dropdown(dropdown_value, outputDir):
    """Called from the GUI when the user selects an item from the story dropdown.
    Parses the 'ID - ComplexTypeName: Identifier' string and calls story_form_html.

    Returns:
        The output file path, or empty string on failure.
    """
    print(f"  Now generating HTML story form... Please be patient.")
    try:
        id_str = dropdown_value.split(" - ")[0].strip()
        data_complex_id = int(id_str)
    except (ValueError, IndexError):
        print(f"Could not parse complex ID from: {dropdown_value}")
        return ""

    identifier_part = dropdown_value.split(" - ", 1)[1] if " - " in dropdown_value else ""
    clean_id = "".join(c if c.isalnum() or c in (' ', '-', '_') else ''
                       for c in identifier_part)[:40].strip()
    filename = f"story_form_{data_complex_id}_{clean_id}.html"

    return story_form_html(data_complex_id, outputDir, filename)


def search_and_export_stories_html(search_term, outputDir):
    """Search for a simplex value and export story forms for all
    ++ objects that contain it as an interactive HTML file with
    the search term highlighted.

    Parameters:
        search_term: the text to search for (e.g., 'Barnesville')
        outputDir: directory to save the output HTML file

    Returns:
        The output file path, or empty string if no results.
    """
    results = search_simplex_value(search_term)
    if not results:
        mb.showwarning(title='Search',
                       message=f'No results found for "{search_term}".')
        return ""

    # Deduplicate by hierarchical_id
    seen = set()
    hierarchical_ids = []
    for _, _, _, _, hier_id, _ in results:
        if hier_id is not None and hier_id not in seen:
            seen.add(hier_id)
            hierarchical_ids.append(hier_id)

    if not hierarchical_ids:
        mb.showwarning(title='Search',
                       message=f'Found simplex values matching "{search_term}" but could not find parent hierarchical objects.')
        return ""

    import time as _time
    t0 = _time.time()

    # Cap at 200 objects to avoid very long generation times
    MAX_HTML_STORIES = 200
    total_hier = len(hierarchical_ids)
    if total_hier > MAX_HTML_STORIES:
        print(f"  Limiting HTML export to first {MAX_HTML_STORIES} of {total_hier} objects")
        hierarchical_ids = hierarchical_ids[:MAX_HTML_STORIES]

    # Build all stories as HTML
    body_parts = []
    if total_hier > MAX_HTML_STORIES:
        body_parts.append(f'<h2>Showing first {MAX_HTML_STORIES} of {total_hier} hierarchical object(s)</h2>')
    else:
        body_parts.append(f'<h2>Found in {total_hier} hierarchical object(s)</h2>')

    for i, hier_id in enumerate(hierarchical_ids):
        identifier = _get_identifier(hier_id)
        complex_name = _get_complex_name(hier_id)

        if (i + 1) % 50 == 0:
            print(f"  Building HTML stories... {i + 1}/{len(hierarchical_ids)}")

        if i > 0:
            body_parts.append('<hr class="story-separator">')
        body_parts.append(f'<h2>{_html_escape(complex_name)} (ID {hier_id}): '
                          f'{_html_escape(identifier)}</h2>')
        body_parts.append('<div class="story-section">')
        _story_recurse_html(hier_id, body_parts, indent=0, search_term=search_term)
        body_parts.append('</div>')

    print(f"  HTML stories built in {_time.time()-t0:.1f}s. Now writing file...")

    title = f'Story Search: "{_html_escape(search_term)}"'
    meta = f'{len(hierarchical_ids)} hierarchical object(s) containing "{_html_escape(search_term)}"'
    body_html = "\n".join(body_parts)

    html = _STORY_HTML_TEMPLATE.format(title=title, meta=meta, body=body_html)

    clean_term = "".join(c if c.isalnum() or c in (' ', '-', '_') else ''
                         for c in search_term)[:30].strip()
    filename = f"story_search_{clean_term}.html"
    output_path = os.path.join(outputDir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML story search saved to {output_path}")
    print(f"  {len(hierarchical_ids)} hierarchical objects found for '{search_term}'")

    return output_path


# ============================================================================
# DOCUMENT SOURCES FOR COMPLEX OBJECTS
# ============================================================================

def get_document_sources_for_complex(inputDir, outputDir, complex_name):
    """Find all document sources linked to instances of the given complex type.

    The linkage chain is:
        complex instance (data_Complex)
            → data_xref_Complex-Document (links complex ID to document ID)
            → data_Document (document details)

    For hierarchical objects (++), we also check document links on child complexes
    by walking down the tree.

    Parameters:
        inputDir: input directory
        outputDir: output directory
        complex_name: name of the complex type (e.g., 'Actor', 'Semantic Triplet')

    Returns:
        DataFrame with complex instances and their linked documents.
    """

    # data_Document_lib is now loaded as a global during initialization
    if len(data_Document_lib) == 0:
        print("  Warning: data_Document table is empty or not loaded")
    else:
        print(f"  data_Document columns: {list(data_Document_lib.columns)}")
        print(f"  data_xref_Complex_Document columns: {list(data_xref_Complex_Document_lib.columns)}")

    # Build document simplex lookup: document ID → {Newspaper name, Newspaper date, Page number, Column number, ...}
    # Chain: data_xref_Simplex-Document → data_Simplex (filter by setup simplex IDs linked to documents)
    #        → data_SimplexText / data_SimplexDate / data_SimplexNumber (depending on ValueType)
    #
    # Instead of hardcoding simplex IDs, we dynamically read setup_xref_Simplex-Document
    # to discover which simplexes are linked to documents and their Required flag.
    # ValueType in setup_Simplex: 1=Text, 2=Number, 3=Date
    doc_simplex_lookup = {}  # doc_id → {simplex_name: value, ...}
    _doc_simplex_names = []  # ordered list of simplex names for column headers
    try:
        # Load setup_xref_Simplex-Document to discover document-linked simplexes
        sxsd_pkl = os.path.join(inputDir, "setup_xref_Simplex-Document.pkl")
        sxsd_xlsx = os.path.join(inputDir, "setup_xref_Simplex-Document.xlsx")
        if os.path.exists(sxsd_pkl):
            setup_xref_sd = pd.read_pickle(sxsd_pkl)
        elif os.path.exists(sxsd_xlsx):
            setup_xref_sd = pd.read_excel(sxsd_xlsx)
        else:
            setup_xref_sd = pd.DataFrame()

        # Get the data xref (Simplex-Document)
        xref_simplex_doc = library.get('data_xref_Simplex-Document.xlsx', pd.DataFrame())
        if len(xref_simplex_doc) == 0:
            sd_pkl = os.path.join(inputDir, "data_xref_Simplex-Document.pkl")
            sd_xlsx = os.path.join(inputDir, "data_xref_Simplex-Document.xlsx")
            if os.path.exists(sd_pkl):
                xref_simplex_doc = pd.read_pickle(sd_pkl)
            elif os.path.exists(sd_xlsx):
                xref_simplex_doc = pd.read_excel(sd_xlsx)

        if len(setup_xref_sd) > 0 and len(xref_simplex_doc) > 0 and len(data_Simplex_lib) > 0:
            # Detect the simplex ID column in setup_xref_Simplex-Document
            # (lynching DB uses 'ID_setup_simplex'; Italian DBs use 'Simplex')
            if 'ID_setup_simplex' in setup_xref_sd.columns:
                _sxsd_simplex_col = 'ID_setup_simplex'
            elif 'Simplex' in setup_xref_sd.columns:
                _sxsd_simplex_col = 'Simplex'
            else:
                _sxsd_simplex_col = setup_xref_sd.columns[3] if len(setup_xref_sd.columns) > 3 else 'Simplex'

            # Detect the simplex ID column in setup_Simplex_lib
            # (lynching DB already renamed to 'ID_setup_simplex' via reading_list; Italian raw xlsx uses 'ID')
            if 'ID_setup_simplex' in setup_Simplex_lib.columns:
                _ss_id_col = 'ID_setup_simplex'
            elif 'ID' in setup_Simplex_lib.columns:
                _ss_id_col = 'ID'
            else:
                _ss_id_col = setup_Simplex_lib.columns[0]

            # Determine which simplexes are Required for documents (prioritize those)
            # Sort by Order column so columns appear in the natural order
            if 'Order' in setup_xref_sd.columns:
                setup_xref_sd = setup_xref_sd.sort_values('Order')
            # Filter to Required simplexes first; if none, use all
            required_sd = setup_xref_sd[setup_xref_sd.get('Required', pd.Series(dtype=bool)) == True]
            if len(required_sd) == 0:
                required_sd = setup_xref_sd
            doc_simplex_ids = required_sd[_sxsd_simplex_col].tolist()
            _doc_simplex_names = required_sd['Name'].tolist()

            # Build a map: setup_simplex_id → (name, value_type, default_val)
            simplex_info = {}
            for _, srow in required_sd.iterrows():
                sid = srow[_sxsd_simplex_col]
                sname = srow['Name']
                # Look up ValueType from setup_Simplex_lib
                vtype_row = setup_Simplex_lib[setup_Simplex_lib[_ss_id_col] == sid]
                vtype = int(vtype_row['ValueType'].iloc[0]) if len(vtype_row) > 0 else 1
                # defaultVal from setup_xref_Simplex-Document (used when no explicit data exists)
                default_ref = srow.get('defaultVal', 0)
                if pd.isna(default_ref):
                    default_ref = 0
                else:
                    default_ref = int(default_ref)
                simplex_info[sid] = (sname, vtype, default_ref)

            print(f"  Document simplex columns: {_doc_simplex_names}")

            # Determine the simplex ID column in data_xref_Simplex-Document
            # Renamed DBs: 'ID_data_simplex'; lynching raw: 'ID_datat_simplex'; Italian raw xlsx: 'Simplex'
            print(f"  xref_simplex_doc columns: {list(xref_simplex_doc.columns)}")
            if 'ID_data_simplex' in xref_simplex_doc.columns:
                sd_simplex_col = 'ID_data_simplex'
            elif 'ID_datat_simplex' in xref_simplex_doc.columns:
                sd_simplex_col = 'ID_datat_simplex'
            elif 'Simplex' in xref_simplex_doc.columns:
                sd_simplex_col = 'Simplex'
            else:
                sd_simplex_col = xref_simplex_doc.columns[1] if len(xref_simplex_doc.columns) > 1 else 'Simplex'

            # Determine the document ID column: 'ID_data_document' (renamed) or 'Document' (raw)
            if 'ID_data_document' in xref_simplex_doc.columns:
                sd_doc_col = 'ID_data_document'
            elif 'Document' in xref_simplex_doc.columns:
                sd_doc_col = 'Document'
            else:
                sd_doc_col = xref_simplex_doc.columns[2] if len(xref_simplex_doc.columns) > 2 else 'Document'

            # Filter data_Simplex for the document-linked simplex types
            doc_simplexes = data_Simplex_lib[
                data_Simplex_lib['ID_setup_simplex'].isin(doc_simplex_ids)
            ][['ID_data_simplex', 'ID_setup_simplex', 'ID_data_date_number_text']]

            # Join xref_simplex_doc → doc_simplexes
            doc_vals = pd.merge(xref_simplex_doc, doc_simplexes,
                                left_on=sd_simplex_col, right_on='ID_data_simplex', how='inner')

            # For each row, resolve the value from the appropriate value table
            # Build value lookups for each type
            text_lookup = {}
            if data_SimplexText_lib is not None and len(data_SimplexText_lib) > 0:
                text_lookup = dict(zip(
                    data_SimplexText_lib['ID_data_date_number_text'],
                    data_SimplexText_lib['Value']))
            number_lookup = {}
            if data_SimplexNumber_lib is not None and len(data_SimplexNumber_lib) > 0:
                number_lookup = dict(zip(
                    data_SimplexNumber_lib['ID_data_date_number_text'],
                    data_SimplexNumber_lib['Value']))
            date_lookup = {}
            if data_SimplexDate_lib is not None and len(data_SimplexDate_lib) > 0:
                date_lookup = dict(zip(
                    data_SimplexDate_lib['ID_data_date_number_text'],
                    data_SimplexDate_lib['Value']))

            # Diagnostic: show lookup sizes and a sample for each simplex type
            print(f"  Value lookup sizes: text={len(text_lookup)}, number={len(number_lookup)}, date={len(date_lookup)}")
            print(f"  doc_vals shape: {doc_vals.shape}, columns: {list(doc_vals.columns)}")
            # Show per-simplex-type counts in doc_vals
            for sid, (sname, vtype, _defval) in simplex_info.items():
                type_label = {1:'text', 2:'number', 3:'date'}.get(vtype, '?')
                count = len(doc_vals[doc_vals['ID_setup_simplex'] == sid])
                # Sample a ref_id for this type to check if it's in the lookup
                sample_refs = doc_vals[doc_vals['ID_setup_simplex'] == sid]['ID_data_date_number_text'].head(3).tolist()
                found = []
                lookup = {1: text_lookup, 2: number_lookup, 3: date_lookup}.get(vtype, text_lookup)
                for r in sample_refs:
                    found.append(f"{r}→{lookup.get(r, '??MISSING??')}")
                print(f"    {sname} (setup_id={sid}, type={type_label}): {count} rows, samples: {found}")

            # Populate doc_simplex_lookup: doc_id → {simplex_name: value}
            for _, row in doc_vals.iterrows():
                doc_id = row[sd_doc_col]
                setup_sid = row['ID_setup_simplex']
                ref_id = row['ID_data_date_number_text']

                if setup_sid not in simplex_info:
                    continue
                sname, vtype, _ = simplex_info[setup_sid]

                # Skip ref_id=0 — PC-ACE uses 0 as "no value" marker
                if ref_id == 0 or (isinstance(ref_id, float) and ref_id == 0.0):
                    continue

                # Resolve value from the right table
                if vtype == 1:  # Text
                    val = text_lookup.get(ref_id, '')
                elif vtype == 2:  # Number
                    val = number_lookup.get(ref_id, '')
                elif vtype == 3:  # Date
                    val = date_lookup.get(ref_id, '')
                else:
                    val = text_lookup.get(ref_id, '')

                if pd.isna(val) or val == '':
                    continue  # Skip empty values — don't pollute with blanks

                # Format values for clean display
                if vtype == 3:  # Date — format as YYYY-MM-DD, stripping time component
                    try:
                        if hasattr(val, 'strftime'):
                            val = val.strftime('%Y-%m-%d')
                        else:
                            val = str(val).split(' ')[0]  # Take date part before any space
                    except Exception:
                        val = str(val)
                elif vtype == 2:  # Number — display as integer when possible (3.0 → 3)
                    try:
                        if float(val) == int(float(val)):
                            val = int(float(val))
                    except (ValueError, TypeError):
                        pass

                if doc_id not in doc_simplex_lookup:
                    doc_simplex_lookup[doc_id] = {}
                # Store as list of values — one entry per source article
                if sname not in doc_simplex_lookup[doc_id]:
                    doc_simplex_lookup[doc_id][sname] = []
                # Deduplicate: only add if not already present
                if str(val) not in [str(v) for v in doc_simplex_lookup[doc_id][sname]]:
                    doc_simplex_lookup[doc_id][sname].append(val)

            # For simplex types with 0 data rows but a known database-wide value
            # (e.g., newspaper name when all documents are from the same source),
            # the column will remain empty — the name is implied by the database itself.
            _empty_types = [sname for sid, (sname, vtype, _) in simplex_info.items()
                            if len(doc_vals[doc_vals['ID_setup_simplex'] == sid]) == 0]
            if _empty_types:
                print(f"  Note: no data found for: {_empty_types} (values may be implied by the database)")

            print(f"  Document simplex lookup built: {len(doc_simplex_lookup)} documents with attributes")
        else:
            print("  Warning: could not build document simplex lookup (missing tables)")
    except Exception as e:
        print(f"  Warning: could not build document simplex lookup: {e}")
        import traceback
        traceback.print_exc()

    # Determine the document ID column name (could be 'ID' or 'ID_data_document')
    if 'ID_data_document' in data_Document_lib.columns:
        doc_id_col = 'ID_data_document'
    elif 'ID' in data_Document_lib.columns:
        doc_id_col = 'ID'
    else:
        doc_id_col = data_Document_lib.columns[0] if len(data_Document_lib.columns) > 0 else 'ID'
        print(f"  Warning: could not find document ID column, using '{doc_id_col}'")

    # Determine the complex-document xref column names
    if 'ID_data_complex' in data_xref_Complex_Document_lib.columns:
        xref_complex_col = 'ID_data_complex'
    elif 'Complex' in data_xref_Complex_Document_lib.columns:
        xref_complex_col = 'Complex'
    else:
        print(f"  Warning: data_xref_Complex_Document columns: {list(data_xref_Complex_Document_lib.columns)}")
        xref_complex_col = data_xref_Complex_Document_lib.columns[1] if len(data_xref_Complex_Document_lib.columns) > 1 else 'Complex'

    if 'ID_data_document' in data_xref_Complex_Document_lib.columns:
        xref_doc_col = 'ID_data_document'
    elif 'Document' in data_xref_Complex_Document_lib.columns:
        xref_doc_col = 'Document'
    else:
        xref_doc_col = data_xref_Complex_Document_lib.columns[2] if len(data_xref_Complex_Document_lib.columns) > 2 else 'Document'

    print(f"  Document ID column: '{doc_id_col}', Xref complex col: '{xref_complex_col}', Xref doc col: '{xref_doc_col}'")

    # Find all instances of the selected complex type
    setup_ids = setup_Complex_lib[setup_Complex_lib["Name"] == complex_name]["ID_setup_complex"]
    if len(setup_ids) == 0:
        print(f"  No setup complex found for '{complex_name}'")
        return pd.DataFrame()

    instances = data_Complex_lib[data_Complex_lib["ID_setup_complex"].isin(setup_ids)]
    if len(instances) == 0:
        print(f"  No data instances found for '{complex_name}'")
        return pd.DataFrame()

    print(f"  Found {len(instances)} instances of '{complex_name}'")

    # For each instance, find linked documents
    # First: direct links from data_xref_Complex-Document
    results = []

    # Helper to build result rows with document simplex values.
    # Returns a LIST of rows: one per source article when a document has
    # multiple values (e.g., 14 newspaper dates → 14 rows).
    # Values are zipped positionally: the Nth date pairs with the Nth page number.
    def _build_doc_rows(complex_name, complex_id, identifier, doc_id, link_level):
        base = {
            "Complex type": complex_name,
            "Complex ID": complex_id,
            "Identifier": identifier,
            "Document ID": doc_id,
            "Link level": link_level,
        }
        doc_attrs = doc_simplex_lookup.get(doc_id, {})
        if not doc_attrs:
            # No simplex data — single row with empty columns
            row = dict(base)
            for sname in _doc_simplex_names:
                row[sname] = ''
            return [row]

        # Find the maximum number of values across all simplex columns
        max_vals = max(len(vals) for vals in doc_attrs.values()) if doc_attrs else 1

        rows = []
        for i in range(max_vals):
            row = dict(base)
            for sname in _doc_simplex_names:
                vals_list = doc_attrs.get(sname, [])
                # Use the i-th value if available, otherwise leave blank
                row[sname] = vals_list[i] if i < len(vals_list) else ''
            rows.append(row)
        return rows

    for _, inst in instances.iterrows():
        complex_id = inst["ID_data_complex"]
        identifier = inst["Identifier"] if pd.notna(inst.get("Identifier")) else ""

        # Direct document links for this complex
        doc_links = data_xref_Complex_Document_lib[
            data_xref_Complex_Document_lib[xref_complex_col] == complex_id
        ]

        if len(doc_links) > 0:
            for _, dlink in doc_links.iterrows():
                doc_id = dlink[xref_doc_col]
                results.extend(_build_doc_rows(complex_name, complex_id, identifier, doc_id, "direct"))
        else:
            # No direct link — try walking down to child complexes
            child_doc_ids = _find_documents_in_children(complex_id)
            if child_doc_ids:
                for doc_id in child_doc_ids:
                    results.extend(_build_doc_rows(complex_name, complex_id, identifier, doc_id, "child"))
            else:
                # No documents found at any level
                row = {
                    "Complex type": complex_name,
                    "Complex ID": complex_id,
                    "Identifier": identifier,
                    "Document ID": "",
                    "Link level": "none",
                }
                for sname in _doc_simplex_names:
                    row[sname] = ''
                results.append(row)

    df = pd.DataFrame(results)

    if len(df) > 0:
        res = export_df_to_excel(df, inputDir, outputDir, complex_name + "_documents", False)

    doc_count = len(df[df["Document ID"] != ""])
    no_doc_count = len(df[df["Document ID"] == ""])
    print(f"  Results: {doc_count} complex-document links found, {no_doc_count} instances with no document")

    return df


def _find_documents_in_children(data_complex_id, visited=None):
    """Recursively walk down the complex-complex hierarchy looking for
    document links on child complexes. Returns a set of document IDs."""

    if visited is None:
        visited = set()

    if data_complex_id in visited:
        return set()
    visited.add(data_complex_id)

    doc_ids = set()

    # Detect xref column names
    if 'ID_data_complex' in data_xref_Complex_Document_lib.columns:
        xc = 'ID_data_complex'
    elif 'Complex' in data_xref_Complex_Document_lib.columns:
        xc = 'Complex'
    else:
        xc = data_xref_Complex_Document_lib.columns[1] if len(data_xref_Complex_Document_lib.columns) > 1 else 'Complex'

    if 'ID_data_document' in data_xref_Complex_Document_lib.columns:
        xd = 'ID_data_document'
    elif 'Document' in data_xref_Complex_Document_lib.columns:
        xd = 'Document'
    else:
        xd = data_xref_Complex_Document_lib.columns[2] if len(data_xref_Complex_Document_lib.columns) > 2 else 'Document'

    # Check direct document links on this complex
    doc_links = data_xref_Complex_Document_lib[
        data_xref_Complex_Document_lib[xc] == data_complex_id
    ]
    for _, dlink in doc_links.iterrows():
        doc_ids.add(dlink[xd])

    # Recurse into children
    children = data_xref_Complex_Complex_lib[
        data_xref_Complex_Complex_lib["ID_data_complex_HIGHER"] == data_complex_id
    ]
    for _, crow in children.iterrows():
        child_id = crow["ID_data_complex_LOWER"]
        doc_ids.update(_find_documents_in_children(child_id, visited))

    return doc_ids

