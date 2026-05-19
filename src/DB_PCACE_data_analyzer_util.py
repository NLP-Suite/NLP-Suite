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
        xref_complex_complex_step1 = export_df_to_excel(xref_complex_complex_step1, inputDir, inputDir,
                                                'NLP_data_xref_Complex_step1', False)

# STEP 2 add the setup complex name and setup xref complex name

        modified_setup_Complex_lib = setup_Complex_lib.drop(columns=["GrammarRule_Text"]) # Drop the column of Grammar rules which adds considerably to the file size and is not necessary

        # add the setup complex name
        xref_complex_complex_step2 = pd.merge(xref_complex_complex_step1, modified_setup_Complex_lib,
                                              left_on='ID_setup_complex', right_on='ID_setup_complex')

        xref_complex_complex_step2 = xref_complex_complex_step2.rename(columns={'Name': "Complex name"})

# EXPORT STEP 2
        xref_complex_complex_step2 = export_df_to_excel(xref_complex_complex_step2, inputDir, inputDir, 'NLP_data_xref_Complex_step2', False)

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
        xref_complex_complex_step3 = export_df_to_excel(xref_complex_complex_step3, inputDir, inputDir, 'NLP_data_xref_Complex_step3', False)

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
    AllowMultiple, and Group settings."""
    global setup_Complex_lib

    # Compute hierarchical complex IDs (these get ++ prefix)
    # A complex is ++ if any of its complex children also have complex children
    hierarchical_ids = set()
    higher_ids = setup_xref_Complex_Complex_lib["HigherComplex"].unique()
    for higher_id in higher_ids:
        child_ids = setup_xref_Complex_Complex_lib[
            setup_xref_Complex_Complex_lib["HigherComplex"] == higher_id
        ]["LowerComplex"].unique()
        for child_id in child_ids:
            if len(setup_xref_Complex_Complex_lib[
                setup_xref_Complex_Complex_lib["HigherComplex"] == child_id
            ]) > 0:
                hierarchical_ids.add(higher_id)
                break

    hierarchical_names = set()
    for hid in hierarchical_ids:
        name_match = setup_Complex_lib[setup_Complex_lib["ID_setup_complex"] == hid]
        if len(name_match) > 0:
            hierarchical_names.add(name_match["Name"].iloc[0])

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

        # Determine prefix for this complex
        if complex_name in hierarchical_names:
            prefix = "<++"
        else:
            # Check if this complex has complex children (making it a + complex)
            has_complex_children = len(complex_children) > 0
            prefix = "<+" if has_complex_children else "<"

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

            # Determine child prefix
            if child_name in hierarchical_names:
                child_prefix = "<++"
            else:
                # Check if child has its own complex children
                child_has_complex = len(setup_xref_Complex_Complex_lib[
                    setup_xref_Complex_Complex_lib["HigherComplex"] == child_id
                ]) > 0
                child_prefix = "<+" if child_has_complex else "<"

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


# get a list of all setup complex and simplex names to be used in dropdown menus in _main
def get_setup_complex_simplex_names():
    try:
        if setup_Complex_lib is not None and setup_Simplex_lib is not None:
            return setup_Complex_lib["Name"].dropna().sort_values().tolist(), setup_Simplex_lib["Name"].dropna().sort_values().tolist()
    except:
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
    simplex_names = data_xref_simplex_complex_select['Simplex name'].values.tolist(index=False)
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

    if os.path.exists(f"{inputDir}/{'setup_Complex'}.pkl"):
        has_files = True
    else:
        has_files =False
    if(has_files):

        macro_event_name = setup_Complex_lib['Name'][0]
        macro_event_name_ID = get_setup_complex_setup_ID([macro_event_name])
        macro_event_name_ID =macro_event_name_ID.iloc[0,0]

        macro_event_IDentifier = data_Complex_lib[data_Complex_lib['ID_setup_complex'] ==macro_event_name_ID]

        macro_event_dropdown_menu_list =macro_event_IDentifier.apply(lambda x: f"{x['ID_data_complex']} - {x['Identifier']}", axis=1).tolist()

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

    # A complex is truly hierarchical (++) if any of its complex children
    # also have complex children — same logic as update_grammar_text()
    hierarchical_ids = set()
    higher_ids = setup_xref_Complex_Complex_lib["HigherComplex"].unique()
    for higher_id in higher_ids:
        child_ids = setup_xref_Complex_Complex_lib[
            setup_xref_Complex_Complex_lib["HigherComplex"] == higher_id
        ]["LowerComplex"].unique()
        for child_id in child_ids:
            if len(setup_xref_Complex_Complex_lib[
                setup_xref_Complex_Complex_lib["HigherComplex"] == child_id
            ]) > 0:
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

    for id in unique_IDs:

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

        filter_df = data_xref_simplex_complex_ALL_lib[(data_xref_simplex_complex_ALL_lib["ID_data_complex"] == id) & (data_xref_simplex_complex_ALL_lib["ID_data_complex_LOWER"] != id)]

        # Check if this complex has complex children or is a leaf complex
        has_complex_children = len(data_xref_Complex_Complex_lib[data_xref_Complex_Complex_lib["ID_data_complex_HIGHER"] == id]) > 0

        if not has_complex_children:
            # LEAF COMPLEX (e.g., Age, Collective actor): no complex children,
            # only simplex values directly attached. Extract them into a single row.
            row_dict = {}
            simplex_rows = data_xref_simplex_complex_lib[data_xref_simplex_complex_lib["ID_data_complex"] == id]
            if "Order" in simplex_rows.columns:
                simplex_rows = simplex_rows.sort_values("Order")

            for _, srow in simplex_rows.iterrows():
                simplex_id = srow["ID_data_simplex"]
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
        for index, row in filter_df.iterrows():
            val = row["ID_data_complex_LOWER"]
            child_type = row["Child name"]

            # Get the Order and Required status from data_xref_Complex_Complex_lib
            xref_row = data_xref_Complex_Complex_lib[
                (data_xref_Complex_Complex_lib["ID_data_complex_HIGHER"] == id) &
                (data_xref_Complex_Complex_lib["ID_data_complex_LOWER"] == val)
            ]
            if len(xref_row) > 0 and child_type not in type_order:
                order_val = xref_row["Order"].iloc[0] if "Order" in xref_row.columns else 999
                type_order[child_type] = order_val

            # In expanded mode, skip non-required top-level children
            if not export_identifier and len(xref_row) > 0:
                xref_id = xref_row["ID_setup_xref_complex-complex"]
                setup_match = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib["ID_setup_xref_complex-complex"].isin(xref_id)]
                if len(setup_match) > 0 and not setup_match["Required"].iloc[0]:
                    print(f"  Skipping non-required top-level child: {child_type}, ID: {val}")
                    continue

            print('Row values', [val])
            print("Complex name we're processing: ", child_type)
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
                    partials = _traverse_complex_to_simplex(child_id, required_only=True, col_prefix=child_type)
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
        print(f"  Simplex name: {simplex_name}, parent complex: {parent_name}, ID: {simplex_id}")
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
            print(f"Complex name we're processing  {child_type}")
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


def _get_complex_name(data_complex_id):
    """Helper to resolve a data complex ID to its setup name."""
    setup_id = data_Complex_lib.loc[data_Complex_lib["ID_data_complex"] == data_complex_id, "ID_setup_complex"]
    if len(setup_id) > 0:
        name = setup_Complex_lib.loc[setup_Complex_lib["ID_setup_complex"] == setup_id.iloc[0], "Name"]
        if len(name) > 0:
            return name.iloc[0]
    return f"Complex_{data_complex_id}"


def _get_ancestor_chain(data_complex_id):
    """Walk up the complex-complex hierarchy from a data complex ID.
    Returns a list of ancestor dicts from immediate parent up to the top-level root:
        [{"data_id": parent_id, "name": "Evento", "order": 5},
         {"data_id": grandparent_id, "name": "Macro evento", "order": 2}, ...]
    where 'order' is the Order value of the child within that ancestor.
    Works with any PC-ACE grammar regardless of language or hierarchy depth."""
    ancestors = []
    current_id = data_complex_id
    visited = set()
    while current_id not in visited:
        visited.add(current_id)
        parent_rows = data_xref_Complex_Complex_lib[
            data_xref_Complex_Complex_lib["ID_data_complex_LOWER"] == current_id
        ]
        if len(parent_rows) == 0:
            break  # reached the top-level root (no parent)
        parent_id = parent_rows["ID_data_complex_HIGHER"].iloc[0]
        # Stop if parent is a sentinel value (e.g., -1) or doesn't exist in data_Complex
        if parent_id < 0 or len(data_Complex_lib[data_Complex_lib["ID_data_complex"] == parent_id]) == 0:
            break
        order = parent_rows["Order"].iloc[0] if "Order" in parent_rows.columns else 0
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
    """Helper to retrieve the Identifier string for a data complex ID."""
    match = data_Complex_lib.loc[data_Complex_lib["ID_data_complex"] == data_complex_id, "Identifier"]
    if len(match) > 0:
        val = match.iloc[0]
        if pd.notna(val):
            return str(val)
    return ""


def _get_simplex_name(data_simplex_id):
    """Helper to resolve a data simplex ID to its setup name."""
    simplex_setup_id = data_Simplex_lib.loc[data_Simplex_lib["ID_data_simplex"] == data_simplex_id, "ID_setup_simplex"]
    if len(simplex_setup_id) > 0:
        simplex_name = setup_Simplex_lib.loc[setup_Simplex_lib["ID_setup_simplex"] == simplex_setup_id.iloc[0], "Name"]
        if len(simplex_name) > 0:
            return simplex_name.iloc[0]
    return f"Simplex_{data_simplex_id}"


def get_required_complex_objects(data_complex_id, required_only=False):
    # Get complex children, optionally filtered by Required
    children_data_complex_ids = data_xref_Complex_Complex_lib[data_xref_Complex_Complex_lib["ID_data_complex_HIGHER"] ==\
        data_complex_id]["ID_data_complex_LOWER"].values

    if not required_only:
        return list(children_data_complex_ids)

    res = []
    for child_id in children_data_complex_ids:
        xref_row = data_xref_Complex_Complex_lib[
            (data_xref_Complex_Complex_lib["ID_data_complex_HIGHER"] == data_complex_id) &
            (data_xref_Complex_Complex_lib["ID_data_complex_LOWER"] == child_id)
        ]
        xref_id = xref_row["ID_setup_xref_complex-complex"]
        if len(xref_id) > 0:
            setup_match = setup_xref_Complex_Complex_lib[setup_xref_Complex_Complex_lib["ID_setup_xref_complex-complex"].isin(xref_id)]
            if len(setup_match) > 0 and setup_match["Required"].iloc[0]:
                res.append(child_id)
    return res

def get_required_simplex_objects(data_complex_id, required_only=False):
    # Get xref rows linking simplexes to this complex
    xref_rows = data_xref_simplex_complex_lib[data_xref_simplex_complex_lib["ID_data_complex"] == data_complex_id]

    res = []

    for _, row in xref_rows.iterrows():
        simplex_id = row["ID_data_simplex"]
        setup_xref_id = row["ID_setup_xref_simplex-complex"]
        print(f"  Processing simplex ID: {simplex_id}, setup xref ID: {setup_xref_id}")

        if required_only:
            setup_match = setup_xref_simplex_complex_lib[setup_xref_simplex_complex_lib["ID_setup_xref_simplex-complex"] == setup_xref_id]
            if len(setup_match) > 0 and setup_match["Required"].iloc[0]:
                res.append(simplex_id)
        else:
            res.append(simplex_id)

    return res

def get_text_value_simplex(data_simplex_id):

    simplex_row = data_Simplex_lib[data_Simplex_lib["ID_data_simplex"] == data_simplex_id]
    if len(simplex_row) == 0:
        return ""

    id_data_date_number_text = simplex_row["ID_data_date_number_text"].iloc[0]

    # Determine the value type (1=text, 2=number, 3=date, 4=boolean) from setup_Simplex_lib
    setup_simplex_id = simplex_row["ID_setup_simplex"].iloc[0]
    value_type = 1  # default to text
    setup_row = setup_Simplex_lib[setup_Simplex_lib["ID_setup_simplex"] == setup_simplex_id]
    if len(setup_row) > 0 and "ValueType" in setup_row.columns:
        try:
            value_type = int(setup_row["ValueType"].iloc[0])
        except (ValueError, TypeError):
            value_type = 1

    try:
        if value_type == 2:
            res = data_SimplexNumber_lib[data_SimplexNumber_lib["ID_data_date_number_text"] == id_data_date_number_text]["Value"].iloc[0]
        elif value_type == 3:
            res = data_SimplexDate_lib[data_SimplexDate_lib["ID_data_date_number_text"] == id_data_date_number_text]["Value"].iloc[0]
        elif value_type == 4:
            # Boolean — try text table first, fall back to number
            try:
                res = data_SimplexText_lib[data_SimplexText_lib["ID_data_date_number_text"] == id_data_date_number_text]["Value"].iloc[0]
            except (IndexError, KeyError):
                res = data_SimplexNumber_lib[data_SimplexNumber_lib["ID_data_date_number_text"] == id_data_date_number_text]["Value"].iloc[0]
        else:
            res = data_SimplexText_lib[data_SimplexText_lib["ID_data_date_number_text"] == id_data_date_number_text]["Value"].iloc[0]
    except (IndexError, KeyError):
        # Fallback: try all tables
        for lib in [data_SimplexText_lib, data_SimplexNumber_lib, data_SimplexDate_lib]:
            try:
                res = lib[lib["ID_data_date_number_text"] == id_data_date_number_text]["Value"].iloc[0]
                return str(res)
            except (IndexError, KeyError):
                continue
        return ""

    return str(res)


def compute_identifier(data_complex_id):
    """Recursively compute the Identifier string for a data complex.
    Format: (simplex_value1 simplex_value2 (child1_identifier) (child2_identifier) ...)
    The Identifier provides a human-readable representation of the entire complex hierarchy."""

    parts = []

    # Get all simplex values attached to this complex (ordered by Order if available)
    simplex_rows = data_xref_simplex_complex_lib[data_xref_simplex_complex_lib["ID_data_complex"] == data_complex_id]
    if "Order" in simplex_rows.columns:
        simplex_rows = simplex_rows.sort_values("Order")

    for _, row in simplex_rows.iterrows():
        simplex_id = row["ID_data_simplex"]
        try:
            val = get_text_value_simplex(simplex_id)
            if val:
                parts.append(str(val))
        except Exception:
            pass

    # Get all complex children (ordered by Order)
    children_rows = data_xref_Complex_Complex_lib[
        data_xref_Complex_Complex_lib["ID_data_complex_HIGHER"] == data_complex_id
    ]
    if "Order" in children_rows.columns:
        children_rows = children_rows.sort_values("Order")

    for _, row in children_rows.iterrows():
        child_id = row["ID_data_complex_LOWER"]
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

    print("Recomputing Identifiers for all complexes...")
    total = len(data_Complex_lib)

    for idx, row in data_Complex_lib.iterrows():
        data_complex_id = row["ID_data_complex"]
        new_identifier = compute_identifier(data_complex_id)
        data_Complex_lib.at[idx, "Identifier"] = new_identifier

        if (idx + 1) % 500 == 0:
            print(f"  Processed {idx + 1}/{total} complexes...")

    print(f"  Done. Processed {total} complexes.")

    # Save updated data_Complex back to files
    output_xlsx = os.path.join(inputDir, "data_Complex.xlsx")
    output_pkl = os.path.join(inputDir, "data_Complex.pkl")

    data_Complex_lib.to_excel(output_xlsx, index=False)
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
    Returns a list of strings in the format 'ID - Identifier'
    (same format as build_macro_event_dropdown_menu)."""

    setup_ids = setup_Complex_lib[setup_Complex_lib["Name"] == complex_name]["ID_setup_complex"]
    if len(setup_ids) == 0:
        return []

    instances = data_Complex_lib[data_Complex_lib["ID_setup_complex"].isin(setup_ids)]
    dropdown_list = instances.apply(
        lambda x: f"{x['ID_data_complex']} - {x['Identifier']}", axis=1
    ).tolist()

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
    lines = []
    _story_recurse(data_complex_id, lines, indent=0)
    story_text = "\n".join(lines)

    output_path = os.path.join(outputDir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(story_text)

    print(f"Story form saved to {output_path}")
    return story_text, output_path


def _story_recurse(data_complex_id, lines, indent=0):
    """Recursively build indented story lines for a complex object."""
    prefix = "    " * indent  # 4 spaces per level

    # Get this complex's type name
    complex_name = _get_complex_name(data_complex_id)

    # Get simplex values directly attached to this complex
    simplex_rows = data_xref_simplex_complex_lib[
        data_xref_simplex_complex_lib["ID_data_complex"] == data_complex_id
    ]
    if "Order" in simplex_rows.columns:
        simplex_rows = simplex_rows.sort_values("Order")

    simplex_values = []
    for _, srow in simplex_rows.iterrows():
        simplex_id = srow["ID_data_simplex"]
        simplex_name = _get_simplex_name(simplex_id)
        text_value = get_text_value_simplex(simplex_id)
        if text_value:
            simplex_values.append((simplex_name, text_value))

    # Build the header line for this complex
    if simplex_values:
        # Show the complex name with its simplex values on the same line or indented below
        lines.append(f"{prefix}{complex_name}")
        for s_name, s_value in simplex_values:
            lines.append(f"{prefix}    {s_name}: {s_value}")
    else:
        lines.append(f"{prefix}{complex_name}")

    # Get complex children, with their role names and order
    children_xref = data_xref_Complex_Complex_lib[
        data_xref_Complex_Complex_lib["ID_data_complex_HIGHER"] == data_complex_id
    ]
    if "Order" in children_xref.columns:
        children_xref = children_xref.sort_values("Order")

    for _, crow in children_xref.iterrows():
        child_id = crow["ID_data_complex_LOWER"]

        # Get the role name (e.g., "Participant-S", "Process") from setup_xref
        role_name = ""
        if "ID_setup_xref_complex-complex" in crow.index:
            xref_id = crow["ID_setup_xref_complex-complex"]
            setup_match = setup_xref_Complex_Complex_lib[
                setup_xref_Complex_Complex_lib["ID_setup_xref_complex-complex"] == xref_id
            ]
            if len(setup_match) > 0:
                role_name = setup_match["Name"].iloc[0]

        # Add a role label line if we have one, then recurse into the child
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


# ============================================================================
# SIMPLEX VALUE SEARCH → STORY FORM
# ============================================================================


def _walk_up_to_hierarchical(data_complex_id, visited=None):
    """Walk up the complex-complex hierarchy from a given data complex
    to find its top-level ancestor (e.g., Macro Event).

    Many complex types in the grammar are marked ++ (hierarchical), including
    low-level ones like City, Actor, Participant-S.  This function walks past
    ALL of them and returns the root — the complex that has no parent in
    data_xref_Complex-Complex.  This is typically the Macro Event."""

    if visited is None:
        visited = set()

    if data_complex_id in visited:
        return None
    visited.add(data_complex_id)

    # Find parents of this complex
    parent_rows = data_xref_Complex_Complex_lib[
        data_xref_Complex_Complex_lib["ID_data_complex_LOWER"] == data_complex_id
    ]

    if len(parent_rows) == 0:
        # No parent — this IS the top-level object
        return data_complex_id

    # Keep walking up through the first available parent
    for _, prow in parent_rows.iterrows():
        parent_id = prow["ID_data_complex_HIGHER"]
        result = _walk_up_to_hierarchical(parent_id, visited)
        if result is not None:
            return result

    # Fallback (shouldn't normally reach here)
    return data_complex_id


def search_simplex_value(search_term, case_sensitive=False):
    """Search for a simplex text value across all simplex tables.
    Returns a list of tuples: (data_simplex_id, value, data_complex_id, complex_name, hierarchical_id, hierarchical_identifier)

    Parameters:
        search_term: the text to search for (e.g., 'Barnesville')
        case_sensitive: if False (default), searches case-insensitively
    """

    results = []

    # Search in data_SimplexText_lib for matching values
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

    print(f"  Found {len(matching_text)} simplex text values matching '{search_term}'")

    # For each matching text value, find which data_simplex it belongs to
    for _, trow in matching_text.iterrows():
        text_id = trow["ID_data_date_number_text"]
        text_value = str(trow["Value"])

        # Find data_simplex rows that reference this text
        simplex_rows = data_Simplex_lib[data_Simplex_lib["ID_data_date_number_text"] == text_id]

        for _, srow in simplex_rows.iterrows():
            simplex_id = srow["ID_data_simplex"]

            # Find which complex this simplex belongs to
            xref_rows = data_xref_simplex_complex_lib[
                data_xref_simplex_complex_lib["ID_data_simplex"] == simplex_id
            ]

            for _, xrow in xref_rows.iterrows():
                complex_id = xrow["ID_data_complex"]
                complex_name = _get_complex_name(complex_id)

                # Walk up to the nearest ++ ancestor
                hierarchical_id = _walk_up_to_hierarchical(complex_id)
                hierarchical_identifier = ""
                if hierarchical_id is not None:
                    hierarchical_identifier = _get_identifier(hierarchical_id)

                results.append((
                    simplex_id, text_value, complex_id, complex_name,
                    hierarchical_id, hierarchical_identifier
                ))

    return results


def build_search_results_dropdown(search_term):
    """Search for a simplex value and build a dropdown of ++ objects
    that contain it. Returns a list of 'ID - Identifier' strings
    for unique hierarchical objects.

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
            dropdown_list.append(f"{hier_id} - {hier_identifier}")

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

    # Build document name lookup: document ID → newspaper/source name
    # Chain: data_xref_Simplex-Document → data_Simplex (filter by setup_simplex 68 = newspaper name) → data_SimplexText
    doc_name_lookup = {}
    try:
        # Get the simplex-document xref from library
        xref_simplex_doc = library.get('data_xref_Simplex-Document.xlsx', pd.DataFrame())
        if len(xref_simplex_doc) == 0:
            # Try loading directly
            sd_pkl = os.path.join(inputDir, "data_xref_Simplex-Document.pkl")
            sd_xlsx = os.path.join(inputDir, "data_xref_Simplex-Document.xlsx")
            if os.path.exists(sd_pkl):
                xref_simplex_doc = pd.read_pickle(sd_pkl)
            elif os.path.exists(sd_xlsx):
                xref_simplex_doc = pd.read_excel(sd_xlsx)

        if len(xref_simplex_doc) > 0 and len(data_Simplex_lib) > 0 and len(data_SimplexText_lib) > 0:
            # Determine the simplex ID column in xref (could be ID_datat_simplex or ID_data_simplex)
            sd_simplex_col = 'ID_data_simplex' if 'ID_data_simplex' in xref_simplex_doc.columns else 'ID_datat_simplex'
            sd_doc_col = 'ID_data_document'

            # Filter data_Simplex for newspaper name type (setup_simplex 68) and source (69)
            newspaper_simplexes = data_Simplex_lib[
                data_Simplex_lib['ID_setup_simplex'].isin([68, 69])
            ][['ID_data_simplex', 'ID_data_date_number_text']]

            # Join: xref_simplex_doc → newspaper_simplexes → SimplexText
            doc_names = pd.merge(xref_simplex_doc, newspaper_simplexes,
                                 left_on=sd_simplex_col, right_on='ID_data_simplex', how='inner')
            doc_names = pd.merge(doc_names, data_SimplexText_lib,
                                 on='ID_data_date_number_text', how='left')

            # Build lookup: doc_id → list of newspaper names
            for _, row in doc_names.iterrows():
                doc_id = row[sd_doc_col]
                name = row.get('Value', '')
                if pd.notna(name) and name != '' and name != 'N/A':
                    if doc_id not in doc_name_lookup:
                        doc_name_lookup[doc_id] = []
                    if name not in doc_name_lookup[doc_id]:
                        doc_name_lookup[doc_id].append(name)

            print(f"  Document name lookup built: {len(doc_name_lookup)} documents with names")
        else:
            print("  Warning: could not build document name lookup (missing tables)")
    except Exception as e:
        print(f"  Warning: could not build document name lookup: {e}")

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
                # Get document details
                doc_row = data_Document_lib[data_Document_lib[doc_id_col] == doc_id]
                doc_info = {}
                if len(doc_row) > 0:
                    for col in doc_row.columns:
                        if col != doc_id_col:
                            doc_info[f"Document {col}"] = doc_row[col].iloc[0]

                results.append({
                    "Complex type": complex_name,
                    "Complex ID": complex_id,
                    "Identifier": identifier,
                    "Document ID": doc_id,
                    "Document name": "; ".join(doc_name_lookup.get(doc_id, [""])),
                    "Link level": "direct",
                    **doc_info
                })
        else:
            # No direct link — try walking down to child complexes
            child_doc_ids = _find_documents_in_children(complex_id)
            if child_doc_ids:
                for doc_id in child_doc_ids:
                    doc_row = data_Document_lib[data_Document_lib[doc_id_col] == doc_id]
                    doc_info = {}
                    if len(doc_row) > 0:
                        for col in doc_row.columns:
                            if col != doc_id_col:
                                doc_info[f"Document {col}"] = doc_row[col].iloc[0]

                    results.append({
                        "Complex type": complex_name,
                        "Complex ID": complex_id,
                        "Identifier": identifier,
                        "Document ID": doc_id,
                        "Document name": "; ".join(doc_name_lookup.get(doc_id, [""])),
                        "Link level": "child",
                        **doc_info
                    })
            else:
                # No documents found at any level
                results.append({
                    "Complex type": complex_name,
                    "Complex ID": complex_id,
                    "Identifier": identifier,
                    "Document ID": "",
                    "Document name": "",
                    "Link level": "none"
                })

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

