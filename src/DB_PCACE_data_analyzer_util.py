
import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "DB_PC-ACE_data_analyzer_main.py", ['os', 'tkinter','pandas','numpy'])==False:
    sys.exit(0)

import numpy as np
import pandas as pd
import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import IO_csv_util
import IO_files_util
import GUI_IO_util
import TIPS_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def import_PCACE_tables(inputDir):
    dirSearch = os.listdir(inputDir)
    tableList = []

    for file in dirSearch:
        # Only include .xlsx files from the input dir
        if (file.startswith('data_') or file.startswith('setup_')) and (file.endswith('.xlsx')):
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
    return tableList


# give the list for all table names (e.g., simplex, complex)
# parameter: dataframe of setup_Complex or filename with path
# return: the list of all table names
def get_all_table_names(setup_Name):
    list_setup_Name = []
    if type(setup_Name) == str:
        if os.path.isfile(setup_Name):
            setup_Name = pd.DataFrame(pd.read_excel(setup_Name))
            setup_name = setup_Name[['Name']]
            setup_name = setup_name[setup_name['Name'].notna()]
            list_setup_Name = setup_name['Name'].values.tolist()
            list_setup_Name.sort()
    return list_setup_Name


# the list for all simplex names
# parameter: dataframe of setup_Simplex
# return: the list of all simplex names
def give_all_simplex_name(setup_Simplex):
    list_simplex_name = []
    if type(setup_Simplex) == str:
        if os.path.isfile(setup_Simplex):
            setup_Simplex_df = pd.DataFrame(pd.read_excel(setup_Simplex))
            setup_Simplex_df = setup_Simplex_df.rename(columns = {'ID':'ID_setup_simplex'})
            simplex_name = setup_Simplex_df[['Name']]
            simplex_name = simplex_name[simplex_name['Name'].notna()]
            list_simplex_name = simplex_name['Name'].values.tolist()
            list_simplex_name.sort()
    return list_simplex_name


# give the list for all complex names
# parameter: dataframe of setup_Complex
# return: the list of all complex names
def give_all_complex_name(setup_Complex):
    list_complex_name = []
    if type(setup_Complex) == str:
        if os.path.isfile(setup_Complex):
            setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
            setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})
            complex_name = setup_Complex_df[['Name']]
            complex_name = complex_name[complex_name['Name'].notna()]
            list_complex_name = complex_name['Name'].values.tolist()
            list_complex_name.sort()
    return list_complex_name


# helper method for give_Simplex_text_date_number
# convert the column named 'Value' into list type
def give_all_Simplex(data):
    data = data[data['Value'].notna()]
    simplex = data['Value'].values.tolist()
    return simplex

# depend on users' choice, get a list of all value in data_SimplexText, data_SimplexDate or data_SimplexNumber
def give_Simplex_text_date_number(simplex_type, data_SimplexText, data_SimplexDate, data_SimplexNumber):
    list_simplex_data = []
    if simplex_type == 'text':
        if type(data_SimplexText) == str:
            if os.path.isfile(data_SimplexText):
                data_SimplexText_df = pd.DataFrame(pd.read_excel(data_SimplexText))
                data = data_SimplexText_df[data_SimplexText_df['Value'].notna()]
                list_simplex_data = data['Value'].values.tolist()
    elif simplex_type == 'date':
        if type(data_SimplexDate) == str:
            if os.path.isfile(data_SimplexDate):
                data_SimplexDate_df = pd.DataFrame(pd.read_excel(data_SimplexDate))
                data = data_SimplexDate_df[data_SimplexDate_df['Value'].notna()]
                list_simplex_data = data['Value'].values.tolist()
    elif simplex_type == 'number':
        if type(data_SimplexNumber) == str:
            if os.path.isfile(data_SimplexNumber):
                data_SimplexNumber_df = pd.DataFrame(pd.read_excel(data_SimplexNumber))
                data = data_SimplexNumber_df[data_SimplexNumber_df['Value'].notna()]
                list_simplex_data = data['Value'].values.tolist()
                for i in range(len(list_simplex_data)):
                    num = list_simplex_data[i]
                    if num.is_integer():
                        list_simplex_data[i] = int(num)
    list_simplex_data.sort()
    return list_simplex_data

def find_complex_in_document(name, inputDir, outputDir):
    setup_Complex = os.path.join(inputDir, 'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})

    data_Complex = os.path.join(inputDir, 'data_Complex.xlsx')
    if os.path.isfile(data_Complex):
        data_Complex_df = pd.DataFrame(pd.read_excel(data_Complex))
        data_Complex_df = data_Complex_df.rename(columns = {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"})

    data_xref_Complex_Document=os.path.join(inputDir,'data_xref_Complex-Document.xlsx')
    if os.path.isfile(data_xref_Complex_Document):
        data_xref_Complex_Document_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Document))

    if type(name) == str:
        name = [name]

    complex_setup_info = find_setup_id(name, setup_Complex_df)
    complex_id = complex_setup_info['ID_setup_complex'].values.tolist()
    data = pd.merge(data_Complex_df, data_xref_Complex_Document_df, how = 'left', left_on = 'ID_data_complex', right_on = 'Complex')
    data = data[data['ID_setup_complex'].isin(complex_id)]
    data = data[['Document', 'ID_data_complex', 'Identifier']]

    complex_in_document_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'complex_in_document')
    data.to_csv(complex_in_document_name, encoding='utf-8', index=False)

    return complex_in_document_name


# give data for the input simplex name
# parameter: name: simplex name in str type
# return: dataframe: name, value, frequency
def get_simplex_frequencies(name, inputDir, outputDir):
    setup_Simplex = os.path.join(inputDir, 'setup_Simplex.xlsx')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df = pd.DataFrame(pd.read_excel(setup_Simplex))
        setup_Simplex_df = setup_Simplex_df.rename(columns = {'ID':'ID_setup_simplex'})

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex-Complex.xlsx')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Simplex_Complex))
        data_xref_Simplex_Complex_df = data_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_data_xref_simplex-complex', 'xrefID':'ID_setup_xref_simplex_complex', 'Simplex':'ID_data_simplex', 'Complex':'ID_data_complex'})

    data_Simplex = os.path.join(inputDir, 'data_Simplex.xlsx')
    if os.path.isfile(data_Simplex):
        data_Simplex_df = pd.DataFrame(pd.read_excel(data_Simplex))
        data_Simplex_df = data_Simplex_df.rename(columns = {"ID":"ID_data_simplex", "SimplexType":"ID_setup_simplex", "refValue":"ID_data_date_number_text"})

    data_SimplexText = os.path.join(inputDir, 'data_SimplexText.xlsx')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df = pd.DataFrame(pd.read_excel(data_SimplexText))

    if type(name) == str:
        name = [name]

    simplex_id = find_setup_id_simplex(name, setup_Simplex_df)
    id = simplex_id.iat[0,0]
    name = simplex_id.iat[0,1]

    temp = pd.merge(data_xref_Simplex_Complex_df, data_Simplex_df, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    select = temp[temp['ID_data_simplex']==id]
    select = select[['ID_data_simplex', 'ID_data_complex']]
    count = select.groupby(['ID_data_simplex']).count()

    data_Simplex_temp = pd.merge(data_Simplex_df, data_SimplexText_df, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]
    count = pd.merge(count, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')

    count = count[['Value', 'ID_data_complex']]
    count = count.rename(columns = {'Value':name, 'ID_data_complex':'Frequency'})
    count = count.sort_values(by=['Frequency'], ascending=False)

    # TODO Anna: The first column should have a header "Name of Simplex Object"

    simplex_frequency_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'simplex_freq')
    count.to_csv(simplex_frequency_file_name, encoding='utf-8', index=False)

    return simplex_frequency_file_name


def get_simplex_frequencies_all(inputDir, outputDir):
    setup_Simplex = os.path.join(inputDir, 'setup_Simplex.xlsx')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df = pd.DataFrame(pd.read_excel(setup_Simplex))
        setup_Simplex_df = setup_Simplex_df.rename(columns = {'ID':'ID_setup_simplex'})

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex-Complex.xlsx')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Simplex_Complex))
        data_xref_Simplex_Complex_df = data_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_data_xref_simplex-complex', 'xrefID':'ID_setup_xref_simplex_complex', 'Simplex':'ID_data_simplex', 'Complex':'ID_data_complex'})

    data_Simplex = os.path.join(inputDir, 'data_Simplex.xlsx')
    if os.path.isfile(data_Simplex):
        data_Simplex_df = pd.DataFrame(pd.read_excel(data_Simplex))
        data_Simplex_df = data_Simplex_df.rename(columns = {"ID":"ID_data_simplex", "SimplexType":"ID_setup_simplex", "refValue":"ID_data_date_number_text"})

    all_rows = []

    simplex_name = setup_Simplex_df[['Name']]
    simplex_name = simplex_name[simplex_name['Name'].notna()]
    list_simplex_name = simplex_name['Name'].values.tolist()

    for name in list_simplex_name:
        simplex_id = find_setup_id_simplex([name], setup_Simplex_df)
        id = simplex_id.iat[0,0]

        temp = pd.merge(data_xref_Simplex_Complex_df, data_Simplex_df, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
        select = temp[temp['ID_setup_simplex']==id]
        select = select[['ID_data_simplex', 'ID_data_complex']]

        all_rows.append([name, len(select)])

    count = pd.DataFrame(all_rows, columns=['name', 'frequency'])

    all_simplex_frequency_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'all_simplex_freq')
    count.to_csv(all_simplex_frequency_file_name, encoding='utf-8', index=False)

    return all_simplex_frequency_file_name


def get_complex_frequencies(name, inputDir, outputDir):
    setup_Complex = os.path.join(inputDir, 'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})

    data_xref_Complex_Complex = os.path.join(inputDir, 'data_xref_Complex-Complex.xlsx')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Complex))
        data_xref_Complex_Complex_df = data_xref_Complex_Complex_df.rename(columns = {'ID':'ID_data_xref_complex-complex', 'HigherComplex':'ID_data_complex', 'xrefID':'ID_setup_xref_complex_complex', 'LowerComplex':'ID_data_complex.1'})

    data_Complex = os.path.join(inputDir, 'data_Complex.xlsx')
    if os.path.isfile(data_Complex):
        data_Complex_df = pd.DataFrame(pd.read_excel(data_Complex))
        data_Complex_df = data_Complex_df.rename(columns = {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"})

    if type(name) == str:
        name = [name]

    complex_id = find_setup_id(name, setup_Complex_df)
    id = complex_id.iat[0,0]
    name = complex_id.iat[0,1]

    temp = pd.merge(data_xref_Complex_Complex_df, data_Complex_df, how = 'left', left_on = 'ID_data_complex.1', right_on = 'ID_data_complex')
    select = temp[temp['ID_setup_complex']==id]
    select = select[['ID_data_complex.1', 'ID_data_complex_x']]
    count = select.groupby(['ID_data_complex.1']).count()

    count = pd.merge(count, data_Complex_df, how = 'left', left_on = 'ID_data_complex.1', right_on = 'ID_data_complex')
    count = count[['Identifier', 'ID_data_complex_x']]
    count = count.rename(columns = {'Identifier':name, 'ID_data_complex_x':'Frequency'})
    count = count.sort_values(by=['Frequency'], ascending=False)

    complex_frequency_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'complex_freq')
    count.to_csv(complex_frequency_file_name, encoding='utf-8', index=False)

    return complex_frequency_file_name


def get_complex_frequencies_all(inputDir, outputDir):
    setup_Complex = os.path.join(inputDir, 'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})

    data_xref_Complex_Complex = os.path.join(inputDir, 'data_xref_Complex-Complex.xlsx')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Complex))
        data_xref_Complex_Complex_df = data_xref_Complex_Complex_df.rename(columns = {'ID':'ID_data_xref_complex-complex', 'HigherComplex':'ID_data_complex', 'xrefID':'ID_setup_xref_complex_complex', 'LowerComplex':'ID_data_complex.1'})

    data_Complex = os.path.join(inputDir, 'data_Complex.xlsx')
    if os.path.isfile(data_Complex):
        data_Complex_df = pd.DataFrame(pd.read_excel(data_Complex))
        data_Complex_df = data_Complex_df.rename(columns = {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"})

    all_rows = []

    complex_name = setup_Complex_df[['Name']]
    complex_name = complex_name[complex_name['Name'].notna()]
    list_complex_name = complex_name['Name'].values.tolist()

    for name in list_complex_name:
        simplex_id = find_setup_id([name], setup_Complex_df)
        id = simplex_id.iat[0,0]

        temp = pd.merge(data_xref_Complex_Complex_df, data_Complex_df, how = 'left', left_on = 'ID_data_complex.1', right_on = 'ID_data_complex')
        select = temp[temp['ID_setup_complex']==id]
        select = select[['ID_data_complex.1', 'ID_data_complex_x']]

        all_rows.append([name, len(select)])

    count = pd.DataFrame(all_rows, columns=['name', 'frequency'])

    all_complex_frequency_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'all_complex_freq')
    count.to_csv(all_complex_frequency_file_name, encoding='utf-8', index=False)

    return all_complex_frequency_file_name



# find the id of the input complex (name)
# parameter: name of an complex in list type, dataframe of setup_Complex
# return: a dataframe: id, name of the input complex
def find_setup_id(complex, setup_Complex):
    data = setup_Complex[setup_Complex['Name'].isin(complex)]
    data = data[['ID_setup_complex', 'Name']]
    data['ID_setup_complex'] = [int(x) for x in data['ID_setup_complex']]
    return data


# find the related names of simplexes to the input complex(es)
# parameter:
#           complexes: names of complexes in list type
#           setup_Complex, setup_xref_Simplex_Complex
# return: related names of simplexes in nested list type
def corresponding_name_simplex_complex(complexes, setup_Complex, setup_xref_Simplex_Complex):
    simplexes = []

    for c in complexes:
        complex_id = find_setup_id([c], setup_Complex)
        complex_id = complex_id.iat[0, 0]
        data = setup_xref_Simplex_Complex[setup_xref_Simplex_Complex['ID_setup_complex'] == complex_id]
        data = data['Name'].values.tolist()
        simplexes.append(data)

    return simplexes


# find the id of the input simplex (name)
# parameter: name of an simplex in list type, dataframe of setup_Complex
# return: a dataframe: id, name of the input complex
def find_setup_id_simplex(simplex, setup_Simplex):
    data = setup_Simplex[setup_Simplex['Name'].isin(simplex)]
    data = data[['ID_setup_simplex', 'Name']]
    data['ID_setup_simplex'] = [int(x) for x in data['ID_setup_simplex']]
    return data


# find the one level lower complex of the input complex
# parameter: name of complex in string type, inputDir
# return: a list of child complex
def find_child_complex(complex, inputDir):
    lower_level_complex = []
    has_files = True

    if isinstance(complex, str):
        complex = [complex]

    setup_Complex = os.path.join(inputDir, 'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})
    else:
        has_files = False

    setup_xref_Complex_Complex = os.path.join(inputDir, 'setup_xref_Complex-Complex.xlsx')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Complex_Complex))
        setup_xref_Complex_Complex_df = setup_xref_Complex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex'})
    else:
        has_files = False

    if(has_files):
        complex_id = find_setup_id(complex, setup_Complex_df)
        complex_id = complex_id['ID_setup_complex'].values.tolist()

        lower_level_complex = setup_xref_Complex_Complex_df[setup_xref_Complex_Complex_df['HigherComplex'].isin(complex_id)]
        lower_level_complex = lower_level_complex[['LowerComplex', 'Name']]
        lower_level_complex = lower_level_complex['Name'].values.tolist()

    return lower_level_complex


# find the one level higher complex of the input complex
# parameter: name of complex in string type, inputDir
# return: a list of parent complex
def find_parent_complex(complex, inputDir):
    higher_level_complex = []
    has_files = True

    if isinstance(complex, str):
        complex = [complex]

    setup_Complex = os.path.join(inputDir, 'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})
    else:
        has_files = False

    setup_xref_Complex_Complex = os.path.join(inputDir, 'setup_xref_Complex-Complex.xlsx')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Complex_Complex))
        setup_xref_Complex_Complex_df = setup_xref_Complex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex'})
    else:
        has_files = False

    if(has_files):
        complex_id = find_setup_id(complex, setup_Complex_df)
        complex_id = complex_id['ID_setup_complex'].values.tolist()

        higher_level_complex = setup_xref_Complex_Complex_df[setup_xref_Complex_Complex_df['LowerComplex'].isin(complex_id)]
        higher_level_complex = higher_level_complex['HigherComplex'].values.tolist()
        # higher_level_complex = [str(x) for x in higher_level_complex]

        higher_level_complex = setup_Complex_df[setup_Complex_df['ID_setup_complex'].isin(higher_level_complex)]
        higher_level_complex = higher_level_complex[['ID_setup_complex', 'Name']]
        higher_level_complex = higher_level_complex.rename(columns={'ID_setup_complex': 'HigherComplex', 'Name': 'Name'})

        higher_level_complex = higher_level_complex['Name'].values.tolist()

    return higher_level_complex


# find the parent of the chosen simplex (corresponding complex)
# parameter: name of simplex in string type, inputDir
# return: a list of parent complex
def find_parent_simplex(name, inputDir):
    higher_level_complex = []
    has_files = True

    if isinstance(name, str):
        name = [name]

    setup_Simplex = os.path.join(inputDir, 'setup_Simplex.xlsx')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df = pd.DataFrame(pd.read_excel(setup_Simplex))
        setup_Simplex_df = setup_Simplex_df.rename(columns = {'ID':'ID_setup_simplex'})
    else:
        has_files = False

    setup_xref_Simplex_Complex = os.path.join(inputDir, 'setup_xref_Simplex-Complex.xlsx')
    if os.path.isfile(setup_xref_Simplex_Complex):
        setup_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Simplex_Complex))
        setup_xref_Simplex_Complex_df = setup_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_setup_xref_simplex-complex','Complex':'ID_setup_complex','Simplex':'ID_setup_simplex'})
    else:
        has_files = False

    setup_Complex = os.path.join(inputDir, 'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})
    else:
        has_files = False

    if(has_files):
        simplex_id = find_setup_id_simplex(name, setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

        complex_id = setup_xref_Simplex_Complex_df[setup_xref_Simplex_Complex_df['ID_setup_simplex'].isin(simplex_id)]
        complex_id = complex_id['ID_setup_complex'].values.tolist()

        # reset type of 'ID_setup_complex' in setup_Complex.xlsx
        setup_Complex_df = setup_Complex_df[setup_Complex_df['Name'].notna()]
        setup_Complex_df[['ID_setup_complex']] = setup_Complex_df[['ID_setup_complex']].astype(int)
        setup_Complex_df = setup_Complex_df[['ID_setup_complex', 'Name']]

        higher_level_complex = setup_Complex_df[setup_Complex_df['ID_setup_complex'].isin(complex_id)]
        higher_level_complex = higher_level_complex['Name'].values.tolist()

    return higher_level_complex

def find_parent_simplex_util(name, setup_Simplex, setup_xref_Simplex_Complex, setup_Complex):
    simplex_id = find_setup_id_simplex(name, setup_Simplex)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

    complex_id = setup_xref_Simplex_Complex[setup_xref_Simplex_Complex['ID_setup_simplex'].isin(simplex_id)]
    complex_id = complex_id['ID_setup_complex'].values.tolist()

    # reset type of 'ID_setup_complex' in setup_Complex.xlsx
    setup_Complex = setup_Complex[setup_Complex['Name'].notna()]
    setup_Complex[['ID_setup_complex']] = setup_Complex[['ID_setup_complex']].astype(int)
    setup_Complex = setup_Complex[['ID_setup_complex', 'Name']]

    higher_level_complex = setup_Complex[setup_Complex['ID_setup_complex'].isin(complex_id)]
    higher_level_complex = higher_level_complex['Name'].values.tolist()

    return higher_level_complex


# find the one level lower complex of the input complex
# parameter: name(s) of complex in list type, dataframe of setup_Complex and setup_xref_Complex_Complex
# return: a dataframe: id, name of one level lower comple of the input complex
def find_lower_complex(complex, setup_Complex, setup_xref_Complex_Complex):
    complex_id = find_setup_id(complex, setup_Complex)
    complex_id = complex_id['ID_setup_complex'].values.tolist()

    lower_level_complex = setup_xref_Complex_Complex[setup_xref_Complex_Complex['HigherComplex'].isin(complex_id)]
    lower_level_complex = lower_level_complex[['LowerComplex', 'Name']]

    return lower_level_complex


# find the one level upper complex of the input complex
# parameter: name(s) of complex in list type, dataframe of setup_Complex and setup_xref_Complex_Complex
# return: a dataframe: id, name of one level higher comple of the input complex
def find_higher_complex(complex, setup_Complex, setup_xref_Complex_Complex):
    complex_id = find_setup_id(complex, setup_Complex)
    complex_id = complex_id['ID_setup_complex'].values.tolist()

    higher_level_complex = setup_xref_Complex_Complex[setup_xref_Complex_Complex['LowerComplex'].isin(complex_id)]
    higher_level_complex = higher_level_complex['HigherComplex'].values.tolist()
    higher_level_complex = [str(x) for x in higher_level_complex]

    higher_level_complex = setup_Complex[setup_Complex['ID_setup_complex'].isin(higher_level_complex)]
    higher_level_complex = higher_level_complex[['ID_setup_complex', 'Name']]
    higher_level_complex = higher_level_complex.rename(columns={'ID_setup_complex': 'HigherComplex', 'Name': 'Name'})

    return higher_level_complex


# give the lowest complex of the give complex
# parameter: name of complex in list type, dataframe of setup_Complex and setup_xref_Complex_Complex
# return: the lowest complex in list type
def get_lowest_complex(complex_name, setup_Complex, setup_xref_Complex_Complex):
    start = find_lower_complex(complex_name, setup_Complex, setup_xref_Complex_Complex)
    checked_complex = complex_name
    lowest_complex_list = []
    lower(start, lowest_complex_list, checked_complex, setup_Complex, setup_xref_Complex_Complex)
    return lowest_complex_list


# helper method for get_lowest_complex
# to fill lowest_complex_list with the names of complex at the lowest level
# parameter: dataframe returned by find_lower_complex function containing id and name of complex,
#            dataframe of setup_Complex and setup_xref_Complex_Complex
def lower(start, lowest_complex_list, checked_complex, setup_Complex, setup_xref_Complex_Complex):
    start = start['Name'].values.tolist()
    for each in start:
        if each not in checked_complex:
            checked_complex.append(each)
            temp = find_lower_complex([each], setup_Complex, setup_xref_Complex_Complex)
            if len(temp) == 0:
                lowest_complex_list.append(each)
            else:
                lower(temp, lowest_complex_list, checked_complex, setup_Complex, setup_xref_Complex_Complex)


# find the path between complex
# parameter: name of complex1 at higher level, namne of complex2 at lower level
#            dataframe of setup_Complex and setup_xref_Complex_Complex
# return: the list of two complex and the complex in the path
def find_path(complex1, complex2, setup_Complex, setup_xref_Complex_Complex):
    path = []
    path.append(complex1)
    if (connection(complex1, complex2, path, setup_Complex, setup_xref_Complex_Complex)):
        return path
    else:
        return []


# the helper method of find_path
def connection(complex1, complex2, path, setup_Complex, setup_xref_Complex_Complex):
    if (complex1 == complex2):
        return True
    else:
        next = find_lower_complex([complex1], setup_Complex, setup_xref_Complex_Complex)
        next = next['Name'].values.tolist()
        if len(next) != 0:
            for each in next:
                if each not in path:
                    path.append(each)
                    if (connection(each, complex2, path, setup_Complex, setup_xref_Complex_Complex)):
                        return True
                    else:
                        path.remove(each)
        return False


# link the data of the highest complex and lowest complex in the path
# parameter: return of path function
#            setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex
# return: data id of the highest complex and lowest complex in the given path with xref
def link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex):
    highest_name = path[0]
    lowest_name = path[len(path) - 1]

    higher = highest_name
    higher = find_setup_id([higher], setup_Complex)
    higher = higher.iat[0, 0]
    path = path[1:]
    xrefs = []

    for each in path:
        lower = find_setup_id([each], setup_Complex)
        lower = lower.iat[0, 0]
        xref = setup_xref_Complex_Complex[(setup_xref_Complex_Complex['HigherComplex'] == higher) & (
                    setup_xref_Complex_Complex['LowerComplex'] == lower)]
        xref = xref.iat[0, 0]
        higher = lower
        xrefs.append(xref)

    xref = xrefs.pop()
    data = data_xref_Complex_Complex[data_xref_Complex_Complex['ID_setup_xref_complex_complex'] == xref]
    data = data[['ID_data_complex', 'ID_data_complex.1']]
    for each in reversed(xrefs):
        filter = data_xref_Complex_Complex[data_xref_Complex_Complex['ID_setup_xref_complex_complex'] == each]
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
def find_identifier(data, cols, data_Complex):
    for col in cols:
        data = pd.merge(data, data_Complex, how='left', left_on=col, right_on='ID_data_complex')
        data = data.drop('ID_data_complex', axis=1)
        data = data.drop('ID_setup_complex', axis=1)
        index = data.columns.get_loc(col)
        temp = data.pop('Identifier')
        data.insert(index + 1, col + ' Identifier', temp)
        data = data.rename(columns={'Value': col + ' Identifier'})

    return data


# give simplex to the return of the complex data ids
# parameter:
#           data: data: dataframe with column names = names of complexes and data = complex data id
#           cols: names of complexes that are part of column names of data
#           data_xref_Simplex_Complex, data_Simplex, data_SimplexText
# return: adding corresponding simplex to input data dataframe
def find_simplex_data(data, cols, data_xref_Simplex_Complex, data_Simplex, data_SimplexText):
    xref_s_c = data_xref_Simplex_Complex[['ID_data_simplex', 'ID_data_complex']]
    data_Simplex_temp = pd.merge(data_Simplex, data_SimplexText, how='left', left_on='ID_data_date_number_text',
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
# return: dataframe containing individual data id, simplex, identifer
def find_simplex_identifier_one_complextype(complex_name, data_Simplex, data_SimplexText, setup_Complex, data_Complex, data_xref_Simplex_Complex):
    data_Simplex_temp = pd.merge(data_Simplex, data_SimplexText, how='left', left_on='ID_data_date_number_text',
                                 right_on='ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'Value']]

    complex_id = find_setup_id(complex_name, setup_Complex).iat[0, 0]
    complex_id = data_Complex[data_Complex['ID_setup_complex'].isin([complex_id])]
    complex_id = complex_id[['ID_data_complex']]
    complex_id = complex_id.rename(columns={'ID_data_complex': complex_name[0]})

    complexes = find_identifier(complex_id, complex_name, data_Complex)
    complexes = find_simplex_data(complexes, complex_name, data_xref_Simplex_Complex, data_Simplex, data_SimplexText)

    return complexes


# give distribution frequency for the input simplex name
# parameter: name: simplex name in list type
# return: dataframe: name, value, frequency
# duplicate function name
def dist_1(name, setup_Simplex, setup_xref_Simplex_Complex, data_xref_Simplex_Complex, data_Simplex, data_SimplexText):
    simplex_id = find_setup_id_simplex(name, setup_Simplex)
    id = simplex_id.iat[0,0]
    xref_id = setup_xref_Simplex_Complex[setup_xref_Simplex_Complex['ID_setup_simplex']==id].iat[0,0]
    xref_data = data_xref_Simplex_Complex[data_xref_Simplex_Complex['ID_setup_xref_simplex_complex']==xref_id]
    xref_data = xref_data[['ID_data_simplex', 'ID_data_complex']]
    count = xref_data.groupby(['ID_data_simplex']).count()

    data_Simplex_temp = pd.merge(data_Simplex, data_SimplexText, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]
    count = pd.merge(count, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    count = count[['ID_data_simplex', 'Value', 'ID_data_complex']]

    count = count.rename(columns = {'ID_data_simplex':name[0], 'ID_data_complex':'Frequency'})

    return count


# give identifier version of semantic triplet
# return: dataframe: Semantic triplet data id, S data id, S Identifier, V data id, V Identifier, O data id, O Identifier
def semantic_triplet_complex(setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex, data_Complex):
    id = find_setup_id(['Semantic Triplet'], setup_Complex).iat[0,0]

    save = setup_xref_Complex_Complex[setup_xref_Complex_Complex['HigherComplex'] == id]
    save = save['ID_setup_xref_complex-complex'].values.tolist()
    save = save[:3]

    triplet = data_xref_Complex_Complex[data_xref_Complex_Complex['ID_setup_xref_complex_complex'].isin(save)]
    triplet = triplet.pivot_table(
        index = ['ID_data_complex'],
        columns = 'ID_setup_xref_complex_complex',
        values = 'ID_data_complex.1'
    ).reset_index()
    triplet = triplet.rename(columns = {'ID_data_complex': 'Semantic Triplet',63: 'S', 64: 'V', 65: 'O'})

    complexes = ['S', 'V', 'O']

    for i in range(3):
        complex = complexes[i]
        triplet = pd.merge(triplet, data_Complex, how = 'left', left_on = complex, right_on = 'ID_data_complex')
        pop = triplet.pop('Identifier')
        name = complex + ' Identifier'
        triplet.insert((i+1)*2, name, pop)
        triplet = triplet.drop('ID_data_complex', axis = 1)
        triplet = triplet.drop('ID_setup_complex', axis = 1)

    return triplet

# give data for Participant-S or Participant-O
# parameter: "Participant-S" or "Participant-O"
# return: dataframe: Participant-S data id, Value = simplex, Type = simplex name
def participant_simplex(participant, data_Simplex, data_SimplexText, setup_Complex, setup_Simplex, data_Complex, data_xref_Simplex_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex):
    data_Simplex_temp = pd.merge(data_Simplex, data_SimplexText, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]
    xref_sc_value = pd.merge(data_xref_Simplex_Complex, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

    simplexes = []

    lower_complexes = {'Individual':'Name of individual actor', 'Collective actor':'Name of collective actor', 'Organization':'Role in the Organization'}

    for lower in lower_complexes:
        simplex = lower_complexes[lower]

        simplex_id = find_setup_id_simplex([simplex], setup_Simplex)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

        xref_sc_value_select = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]

        path = find_path(participant, lower, setup_Complex, setup_xref_Complex_Complex)
        id_data = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)

        data = pd.merge(id_data, xref_sc_value_select, how = 'left', left_on = lower, right_on = 'ID_data_complex')
        data = data[data[participant].notna()]
        data = data.drop_duplicates(subset=[participant])
        data = data[[participant, lower, 'Value']]
        data = data.drop(lower, axis = 1)
        data[['Type']] = lower

        simplexes.append(data)

    simplexes_combined = pd.concat([simplexes[0], simplexes[1], simplexes[2]])

    return simplexes_combined


# give data for Process
# return: dataframe: Process data id, Simple process data id, Value = simplex
def process_simplex(setup_Simplex, data_Simplex, data_SimplexText, data_xref_Simplex_Complex, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex):
    simplex_id = find_setup_id_simplex(['Negation', 'Modal verb', 'Verbal phrase'], setup_Simplex)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

    data_Simplex_temp = pd.merge(data_Simplex, data_SimplexText, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]
    xref_sc_value = pd.merge(data_xref_Simplex_Complex, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]
    xref_sc_value = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]

    path = ['Process', 'Simple process']
    id_data_simple_process_oneLevel = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    data_simple_process_oneLevel = pd.merge(id_data_simple_process_oneLevel, xref_sc_value, how = 'left', left_on = 'Simple process', right_on = 'ID_data_complex')
    data_simple_process_oneLevel = data_simple_process_oneLevel.sort_values(by = ['ID_data_complex','ID_setup_simplex'], ascending = False)
    data_simple_process_oneLevel = data_simple_process_oneLevel.groupby(['Process'])['Value'].apply(lambda x: x.str.cat(sep=' ')).reset_index()
    data_oneLevel = pd.merge(id_data_simple_process_oneLevel, data_simple_process_oneLevel, how = 'left', left_on = 'Process', right_on = 'Process')

    path = ['Process', 'Complex process', 'Simple process']
    id_data_simple_process_twoLevel = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    data_simple_process_twoLevel = pd.merge(id_data_simple_process_twoLevel, xref_sc_value, how = 'left', left_on = 'Simple process', right_on = 'ID_data_complex')
    data_simple_process_twoLevel = data_simple_process_twoLevel.sort_values(by = ['ID_data_complex','ID_setup_simplex'], ascending = False)
    data_simple_process_twoLevel = data_simple_process_twoLevel.groupby(['Process'])['Value'].apply(lambda x: x.str.cat(sep=' ')).reset_index()
    data_twoLevel = pd.merge(id_data_simple_process_twoLevel, data_simple_process_twoLevel, how = 'left', left_on = 'Process', right_on = 'Process')

    data_process_simplex = pd.concat([data_oneLevel, data_twoLevel])

    return data_process_simplex


# give the semantic triplet with simplex
# return: dataframe: Semantic triplet data id, S data id, S Type, S Simplex, V data id, V Simplex, O data id, O Type, O Simplex
# p.s. Type = Individual / Orgaization / Collective actor
def semantic_triplet_simplex(setup_Complex, setup_Simplex, setup_xref_Complex_Complex, data_xref_Complex_Complex, data_Complex, data_Simplex, data_SimplexText, data_xref_Simplex_Complex, data_xref_Complex_Document, data_xref_VComment, utility_Security):
    triplet = semantic_triplet_complex(setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex, data_Complex)
    s = participant_simplex('Participant-S', data_Simplex, data_SimplexText, setup_Complex, setup_Simplex, data_Complex, data_xref_Simplex_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    s = s.rename(columns = {'Value':'Subject (S)', 'Type':'S Type'})
    v = process_simplex(setup_Simplex, data_Simplex, data_SimplexText, data_xref_Simplex_Complex, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    o = participant_simplex('Participant-O', data_Simplex, data_SimplexText, setup_Complex, setup_Simplex, data_Complex, data_xref_Simplex_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    o = o.rename(columns = {'Value':'Object (O)', 'Type':'O Type'})

    simplex_version = pd.merge(triplet, s, how = 'left', left_on = 'S', right_on = 'Participant-S')
    simplex_version = pd.merge(simplex_version, v, how = 'left', left_on = 'V', right_on = 'Process')
    simplex_version = pd.merge(simplex_version, o, how = 'left', left_on = 'O', right_on = 'Participant-O')
    simplex_version = simplex_version.loc[:, ['Semantic Triplet', 'S', 'S Type', 'Subject (S)', 'V', 'Value', 'O', 'O Type', 'Object (O)']]
    simplex_version = simplex_version.rename(columns = {'Value':'Verb (V)'})
    simplex_version = simplex_version.rename(columns = {'S':'S ID','V':'V ID', 'O':'O ID'})

    # add 'Macro Event' and 'Event' data id

    # S1: find setup id of 'Macro Event', 'Event' and 'Semantic Triplet'
    macro_event_id = find_setup_id(['Macro Event'], setup_Complex)
    macro_event_id = macro_event_id.iloc[[0], [0]].values[0][0]
    event_id = find_setup_id(['Event'], setup_Complex)
    event_id = event_id.iloc[[0], [0]].values[0][0]
    semantic_triplet_id = find_setup_id(['Semantic Triplet'], setup_Complex)
    semantic_triplet_id = semantic_triplet_id.iloc[[0], [0]].values[0][0]

    # S2: find setup_xref id of 'Macro Event' and 'Event', and 'Event' and 'Semantic Triplet'
    macro_event_event_setup_id = setup_xref_Complex_Complex[
        (setup_xref_Complex_Complex['HigherComplex'] == macro_event_id) & (
                    setup_xref_Complex_Complex['LowerComplex'] == event_id)]
    macro_event_event_setup_id = macro_event_event_setup_id.iloc[[0], [0]].values[0][0]
    event_semantic_triplet_setup_id = setup_xref_Complex_Complex[
        (setup_xref_Complex_Complex['HigherComplex'] == event_id) & (
                    setup_xref_Complex_Complex['LowerComplex'] == semantic_triplet_id)]
    event_semantic_triplet_setup_id = event_semantic_triplet_setup_id.iloc[[0], [0]].values[0][0]

    # S3: find data_xref_id
    macro_event_event_data = data_xref_Complex_Complex[
        data_xref_Complex_Complex['ID_setup_xref_complex_complex'] == macro_event_event_setup_id]
    macro_event_event_data = macro_event_event_data.rename(
        columns={'ID_data_complex': 'Macro Event', 'ID_data_complex.1': 'Event'})
    macro_event_event_data = macro_event_event_data[['Macro Event', 'Event']]
    event_semantic_triplet_data = data_xref_Complex_Complex[
        data_xref_Complex_Complex['ID_setup_xref_complex_complex'] == event_semantic_triplet_setup_id]
    event_semantic_triplet_data = event_semantic_triplet_data.rename(
        columns={'ID_data_complex': 'Event', 'ID_data_complex.1': 'Semantic Triplet'})
    event_semantic_triplet_data = event_semantic_triplet_data[['Event', 'Semantic Triplet']]

    # S4: merge
    macro_event_event_semantic_triplet = pd.merge(macro_event_event_data, event_semantic_triplet_data, how='right',
                                                  left_on='Event', right_on='Event')
    simplex_version = pd.merge(macro_event_event_semantic_triplet, simplex_version, how='left',
                               left_on='Semantic Triplet', right_on='Semantic Triplet')

    data_complex_macro_event = data_Complex[['ID_data_complex','Identifier']]
    data_complex_macro_event = data_complex_macro_event.rename(
        columns={'ID_data_complex': 'Macro Event', 'Identifier': 'Macro Event Identifier'})
    simplex_version = pd.merge(simplex_version, data_complex_macro_event, how = 'left', left_on = 'Macro Event', right_on = 'Macro Event')
    macro_event_identifier = simplex_version.pop('Macro Event Identifier')
    simplex_version.insert(1, 'Macro Event Identifier', macro_event_identifier)

    # S5: add document information
    # ref: complex id for semantic triplet
    data_xref_Complex_Document_modified = data_xref_Complex_Document[['Complex','Document']]
    simplex_version = pd.merge(simplex_version, data_xref_Complex_Document_modified, how = 'left', left_on = 'Semantic Triplet', right_on = 'Complex')
    simplex_version = simplex_version.drop('Complex', axis = 1)

    # S6: add VComment
    # ref: complex id for semantic triplet
    data_xref_VComment_modified = data_xref_VComment[['Complex','Comment','UserID','VerifierID']]
    simplex_version = pd.merge(simplex_version, data_xref_VComment_modified, how = 'left', left_on = 'Macro Event', right_on = 'Complex')
    simplex_version = simplex_version.drop('Complex', axis = 1)

    utility_Security = utility_Security[['ID', 'UserName']]
    utility_Security_user = utility_Security.rename(columns={'ID': 'UserID'})
    simplex_version = pd.merge(simplex_version, utility_Security_user, how = 'left', left_on = 'UserID', right_on = 'UserID')
    user_name = simplex_version.pop('UserName')
    userID_idx = simplex_version.columns.get_loc('UserID')
    simplex_version.insert(userID_idx + 1, 'UserName', user_name)
    utility_Security_verifier = utility_Security.rename(columns={'ID': 'VerifierID', 'UserName':'VerifierName'})
    simplex_version = pd.merge(simplex_version, utility_Security_verifier, how = 'left', left_on = 'VerifierID', right_on = 'VerifierID')
    verifier_name = simplex_version.pop('VerifierName')
    verifierID_idx = simplex_version.columns.get_loc('VerifierID')
    simplex_version.insert(verifierID_idx + 1, 'VerifierName', verifier_name)

    simplex_version = simplex_version.rename(columns = {'Macro Event':'Macro Event ID','Event':'Event ID', 'Semantic Triplet':'Semantic Triplet ID', 'Document':'Document ID'})

    return simplex_version


# prepare the function for the use in main
# give the semantic triplet with simplex
# return: dataframe: Semantic triplet data id, S data id, S Type, S Simplex, V data id, V Simplex, O data id, O Type, O Simplex
# p.s. Type = Individual / Orgaization / Collective actor
def semantic_triplet_simplex_main(inputDir, outputDir, macro_event_id):
    setup_Complex=os.path.join(inputDir,'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.xlsx')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df = pd.DataFrame(pd.read_excel(setup_Simplex))
        setup_Simplex_df = setup_Simplex_df.rename(columns = {'ID':'ID_setup_simplex'})

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex-Complex.xlsx')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Complex_Complex))
        setup_xref_Complex_Complex_df = setup_xref_Complex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex'})

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex-Complex.xlsx')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Complex))
        data_xref_Complex_Complex_df = data_xref_Complex_Complex_df.rename(columns = {'ID':'ID_data_xref_complex-complex', 'HigherComplex':'ID_data_complex', 'xrefID':'ID_setup_xref_complex_complex', 'LowerComplex':'ID_data_complex.1'})

    data_Complex=os.path.join(inputDir,'data_Complex.xlsx')
    if os.path.isfile(data_Complex):
        data_Complex_df = pd.DataFrame(pd.read_excel(data_Complex))
        data_Complex_df = data_Complex_df.rename(columns = {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"})

    data_Simplex=os.path.join(inputDir,'data_Simplex.xlsx')
    if os.path.isfile(data_Simplex):
        data_Simplex_df = pd.DataFrame(pd.read_excel(data_Simplex))
        data_Simplex_df = data_Simplex_df.rename(columns = {"ID":"ID_data_simplex", "SimplexType":"ID_setup_simplex", "refValue":"ID_data_date_number_text"})

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.xlsx')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df = pd.DataFrame(pd.read_excel(data_SimplexText))

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex-Complex.xlsx')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Simplex_Complex))
        data_xref_Simplex_Complex_df = data_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_data_xref_simplex-complex', 'xrefID':'ID_setup_xref_simplex_complex', 'Simplex':'ID_data_simplex', 'Complex':'ID_data_complex'})

    data_xref_Complex_Document=os.path.join(inputDir,'data_xref_Complex-Document.xlsx')
    if os.path.isfile(data_xref_Complex_Document):
        data_xref_Complex_Document_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Document))

    data_xref_VComment=os.path.join(inputDir,'data_xref_VComment.xlsx')
    if os.path.isfile(data_xref_VComment):
        data_xref_VComment_df = pd.DataFrame(pd.read_excel(data_xref_VComment))

    utility_Security=os.path.join(inputDir,'utility_Security.xlsx')
    if os.path.isfile(utility_Security):
        utility_Security_df = pd.DataFrame(pd.read_excel(utility_Security))
    else:
        mb.showwarning(title='Warning',
                       message='The table "utility_Security" is missing.\n\nPlease, make sure to export this table from PC-ACE data backened and try again.')
        return

    simplex_version = semantic_triplet_simplex(setup_Complex_df, setup_Simplex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_Complex_df, data_Simplex_df, data_SimplexText_df, data_xref_Simplex_Complex_df, data_xref_Complex_Document_df, data_xref_VComment_df, utility_Security_df)

    if macro_event_id != '':
        macro_event_id = int(macro_event_id.split()[0])
        simplex_version = simplex_version[simplex_version['Macro Event ID'] == macro_event_id]

    simplex_version = simplex_version.sort_values(['Macro Event ID', 'Event ID', 'Semantic Triplet ID'], ascending=[True, True, True])

    triplet_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'triplet (SVO)')
    simplex_version.to_csv(triplet_file_name, encoding='utf-8', index=False)

    return triplet_file_name


# helper method for semantic_triplet_time
# link simplex of time complex with V
# return: a dataframe: Process = data id of complex Process, Indefinite time of day = data id of simplex Indefinite time of day, Time = text of Indefinite time of day
def find_time_simplex(setup_Simplex, data_Simplex, data_SimplexText, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex, data_xref_Simplex_Complex):
    simplex_id = find_setup_id_simplex(['Moment of the day'], setup_Simplex)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

    data_Simplex_temp = pd.merge(data_Simplex, data_SimplexText, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]
    xref_sc_value = pd.merge(data_xref_Simplex_Complex, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]
    xref_sc_value = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]

    path = ['Process', 'Simple process', 'Circumstances', 'Time', 'Time of day', 'Indefinite time of day']
    id_data_oneLevel = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    id_data_oneLevel = id_data_oneLevel[id_data_oneLevel['Process'].notna()]
    id_data_oneLevel = id_data_oneLevel.drop_duplicates(subset = ['Process'])
    data_oneLevel = pd.merge(id_data_oneLevel, xref_sc_value, how = 'left', left_on = 'Indefinite time of day', right_on = 'ID_data_complex')

    path = ['Process', 'Complex process', 'Simple process', 'Circumstances', 'Time', 'Time of day', 'Indefinite time of day']
    id_data_twoLevel = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    id_data_twoLevel = id_data_twoLevel[id_data_twoLevel['Process'].notna()]
    id_data_twoLevel = id_data_twoLevel.drop_duplicates(subset = ['Process'])
    data_twoLevel = pd.merge(id_data_twoLevel, xref_sc_value, how = 'left', left_on = 'Indefinite time of day', right_on = 'ID_data_complex')

    data = pd.concat([data_oneLevel, data_twoLevel])
    data = data[['Process', 'Indefinite time of day', 'Value']]
    data = data.rename(columns = {'Value':'Time'})

    return data


# give the semantic triplet (SVO) with time
def semantic_triplet_time(inputDir, outputDir, macro_event_id):
    setup_Complex=os.path.join(inputDir,'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.xlsx')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df = pd.DataFrame(pd.read_excel(setup_Simplex))
        setup_Simplex_df = setup_Simplex_df.rename(columns = {'ID':'ID_setup_simplex'})

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex-Complex.xlsx')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Complex_Complex))
        setup_xref_Complex_Complex_df = setup_xref_Complex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex'})

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex-Complex.xlsx')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Complex))
        data_xref_Complex_Complex_df = data_xref_Complex_Complex_df.rename(columns = {'ID':'ID_data_xref_complex-complex', 'HigherComplex':'ID_data_complex', 'xrefID':'ID_setup_xref_complex_complex', 'LowerComplex':'ID_data_complex.1'})

    data_Complex=os.path.join(inputDir,'data_Complex.xlsx')
    if os.path.isfile(data_Complex):
        data_Complex_df = pd.DataFrame(pd.read_excel(data_Complex))
        data_Complex_df = data_Complex_df.rename(columns = {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"})

    data_Simplex=os.path.join(inputDir,'data_Simplex.xlsx')
    if os.path.isfile(data_Simplex):
        data_Simplex_df = pd.DataFrame(pd.read_excel(data_Simplex))
        data_Simplex_df = data_Simplex_df.rename(columns = {"ID":"ID_data_simplex", "SimplexType":"ID_setup_simplex", "refValue":"ID_data_date_number_text"})

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.xlsx')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df = pd.DataFrame(pd.read_excel(data_SimplexText))

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex-Complex.xlsx')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Simplex_Complex))
        data_xref_Simplex_Complex_df = data_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_data_xref_simplex-complex', 'xrefID':'ID_setup_xref_simplex_complex', 'Simplex':'ID_data_simplex', 'Complex':'ID_data_complex'})

    data_xref_Complex_Document=os.path.join(inputDir,'data_xref_Complex-Document.xlsx')
    if os.path.isfile(data_xref_Complex_Document):
        data_xref_Complex_Document_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Document))

    data_xref_VComment=os.path.join(inputDir,'data_xref_VComment.xlsx')
    if os.path.isfile(data_xref_VComment):
        data_xref_VComment_df = pd.DataFrame(pd.read_excel(data_xref_VComment))

    utility_Security=os.path.join(inputDir,'utility_Security.xlsx')
    if os.path.isfile(utility_Security):
        utility_Security_df = pd.DataFrame(pd.read_excel(utility_Security))
    else:
        mb.showwarning(title='Warning',
                       message='The table "utility_Security" is missing.\n\nPlease, make sure to export this table from PC-ACE data backened and try again.')
        return

    triplet = semantic_triplet_simplex(setup_Complex_df, setup_Simplex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_Complex_df, data_Simplex_df, data_SimplexText_df, data_xref_Simplex_Complex_df, data_xref_Complex_Document_df, data_xref_VComment_df, utility_Security_df)
    # triplet has document information in it
    time = find_time_simplex(setup_Simplex_df, data_Simplex_df, data_SimplexText_df, setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_xref_Simplex_Complex_df)

    triplet_with_time = pd.merge(triplet, time, how = 'left', left_on = 'V ID', right_on = 'Process')
    triplet_with_time = triplet_with_time.drop('Process', axis = 1)
    triplet_with_time = triplet_with_time.rename(columns = {'Indefinite time of day':'Time ID', 'Time':'Time Simplex'})

    # move Document column to the last position of the dataframe
    document_id = triplet_with_time.pop('Document ID')
    triplet_with_time.insert(len(triplet_with_time.columns), 'Document ID', document_id)

    # move Comment column to the last position of the dataframe
    comment = triplet_with_time.pop('Comment')
    triplet_with_time.insert(len(triplet_with_time.columns), 'Comment', comment)

    # move VerifierID column to the last position of the dataframe
    UserID = triplet_with_time.pop('UserID')
    triplet_with_time.insert(len(triplet_with_time.columns), 'UserID', UserID)
    user_name = triplet_with_time.pop('UserName')
    triplet_with_time.insert(len(triplet_with_time.columns), 'UserName', user_name)
    VerifierID = triplet_with_time.pop('VerifierID')
    triplet_with_time.insert(len(triplet_with_time.columns), 'VerifierID', VerifierID)
    verifier_name = triplet_with_time.pop('VerifierName')
    triplet_with_time.insert(len(triplet_with_time.columns), 'VerifierName', verifier_name)

    if macro_event_id != '':
        macro_event_id = int(macro_event_id.split()[0])
        triplet_with_time = triplet_with_time[triplet_with_time['Macro Event ID'] == macro_event_id]

    triplet_with_time = triplet_with_time.sort_values(['Macro Event ID', 'Event ID', 'Semantic Triplet ID'], ascending=[True, True, True])

    triplet_with_time_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'triplet (SVO) with time')
    triplet_with_time.to_csv(triplet_with_time_file_name, encoding='utf-8', index=False)

    return triplet_with_time_file_name


# helper method for semantic_triplet_space
# link simplex of space complex with V
# return: a dataframe: Process = data id of complex Process, Type of territory = data id of simplex Type of territory, Space = text of Type of territory
def find_space_simplex(setup_Simplex, data_Simplex, data_SimplexText, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex, data_xref_Simplex_Complex):
    simplex_id = find_setup_id_simplex(['City name', 'County', 'State'], setup_Simplex)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

    data_Simplex_temp = pd.merge(data_Simplex, data_SimplexText, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]
    xref_sc_value = pd.merge(data_xref_Simplex_Complex, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]
    xref_sc_value = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]

    path = ['Process', 'Simple process', 'Circumstances', 'Space', 'Territory', 'Type of territory']
    id_data_territory_oneLevel = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    id_data_territory_oneLevel = id_data_territory_oneLevel[id_data_territory_oneLevel['Process'].notna()]
    id_data_territory_oneLevel = id_data_territory_oneLevel.drop_duplicates(subset = ['Process'])
    data_territory_oneLevel = pd.merge(id_data_territory_oneLevel, xref_sc_value, how = 'left', left_on = 'Type of territory', right_on = 'ID_data_complex')

    path = ['Process', 'Complex process', 'Simple process', 'Circumstances', 'Space', 'Territory', 'Type of territory']
    id_data_territory_twoLevel = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    id_data_territory_twoLevel = id_data_territory_twoLevel[id_data_territory_twoLevel['Process'].notna()]
    id_data_territory_twoLevel = id_data_territory_twoLevel.drop_duplicates(subset = ['Process'])
    data_territory_twoLevel = pd.merge(id_data_territory_twoLevel, xref_sc_value, how = 'left', left_on = 'Type of territory', right_on = 'ID_data_complex')

    data = pd.concat([data_territory_oneLevel, data_territory_twoLevel])
    data = data[['Process', 'Type of territory', 'Value']]
    data = data.rename(columns = {'Value':'Space'})

    return data


# helper method for semantic_triplet_space
# link simplex of space complex with event complex
# return: a dataframe: Semantic Triplet = data id of complex Semantic Triplet, Type of territory = data id of simplex Type of territory, Space = text of Type of territory
def find_space_simplex_event(setup_Simplex, data_Simplex, data_SimplexText, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex, data_xref_Simplex_Complex):
    simplex_id = find_setup_id_simplex(['City name', 'County', 'State'], setup_Simplex)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

    data_Simplex_temp = pd.merge(data_Simplex, data_SimplexText, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]
    xref_sc_value = pd.merge(data_xref_Simplex_Complex, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]
    xref_sc_value = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]

    path = ['Event', 'Semantic Triplet', 'Process', 'Simple process', 'Circumstances', 'Space', 'Territory', 'Type of territory']
    id_data_territory_oneLevel = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    id_data_territory_oneLevel = id_data_territory_oneLevel[id_data_territory_oneLevel['Event'].notna()]
    id_data_territory_oneLevel = id_data_territory_oneLevel.drop_duplicates(subset = ['Event'])
    data_territory_oneLevel = pd.merge(id_data_territory_oneLevel, xref_sc_value, how = 'left', left_on = 'Type of territory', right_on = 'ID_data_complex')

    path = ['Event', 'Semantic Triplet', 'Process', 'Complex process', 'Simple process', 'Circumstances', 'Space', 'Territory', 'Type of territory']
    id_data_territory_twoLevel = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    id_data_territory_twoLevel = id_data_territory_twoLevel[id_data_territory_twoLevel['Event'].notna()]
    id_data_territory_twoLevel = id_data_territory_twoLevel.drop_duplicates(subset = ['Event'])
    data_territory_twoLevel = pd.merge(id_data_territory_twoLevel, xref_sc_value, how = 'left', left_on = 'Type of territory', right_on = 'ID_data_complex')

    data = pd.concat([data_territory_oneLevel, data_territory_twoLevel])
    data = data[['Event', 'Type of territory', 'Value']]
    data = data.rename(columns = {'Value':'Space'})

    path = ['Event', 'Semantic Triplet']
    st = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    data = pd.merge(data, st, how = 'left', right_on = 'Event', left_on = 'Event')
    data = data[['Semantic Triplet', 'Type of territory', 'Space']]

    return data


# give semantic triplet with space
def semantic_triplet_space(setup_Simplex_df, data_Simplex_df, data_SimplexText_df, setup_Complex_df, data_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_xref_Simplex_Complex_df, data_xref_Complex_Document_df, data_xref_VComment_df, utility_Security_df):
    triplet = semantic_triplet_simplex(setup_Complex_df, setup_Simplex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_Complex_df, data_Simplex_df, data_SimplexText_df, data_xref_Simplex_Complex_df, data_xref_Complex_Document_df, data_xref_VComment_df, utility_Security_df)
    # triplet has document and VComment information in it

    space1 = find_space_simplex(setup_Simplex_df, data_Simplex_df, data_SimplexText_df, setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_xref_Simplex_Complex_df)
    triplet_with_space1 = pd.merge(triplet, space1, how = 'left', left_on = 'V ID', right_on = 'Process')
    triplet_with_space1 = triplet_with_space1.drop('Process', axis = 1)
    triplet_with_space1 = triplet_with_space1.rename(columns = {'Type of territory':'Space', 'Space':'Space Simplex'})
    triplet_with_space1 = triplet_with_space1[['V ID', 'Space', 'Space Simplex']]
    triplet_with_space1 = triplet_with_space1.dropna(subset = ['Space'])

    space2 = find_space_simplex_event(setup_Simplex_df, data_Simplex_df, data_SimplexText_df, setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_xref_Simplex_Complex_df)
    triplet_with_space2 = pd.merge(triplet, space2, how = 'left', left_on = 'Semantic Triplet ID', right_on = 'Semantic Triplet')
    triplet_with_space2 = triplet_with_space2.drop('Semantic Triplet', axis = 1)
    triplet_with_space2 = triplet_with_space2.rename(columns = {'Type of territory':'Space', 'Space':'Space Simplex'})
    triplet_with_space2 = triplet_with_space2[['V ID', 'Space', 'Space Simplex']]
    triplet_with_space2 = triplet_with_space2.dropna(subset = ['Space'])

    triplet_with_space = pd.concat([triplet_with_space1, triplet_with_space2])
    triplet_with_space = pd.merge(triplet, triplet_with_space, how = 'left', left_on = 'V ID', right_on = 'V ID')
    triplet_with_space = triplet_with_space.rename(columns = {'Space':'Space ID'})

    # move Document column to the last position of the dataframe
    document_id = triplet_with_space.pop('Document ID')
    triplet_with_space.insert(len(triplet_with_space.columns), 'Document ID', document_id)

    # move Comment column to the last position of the dataframe
    comment = triplet_with_space.pop('Comment')
    triplet_with_space.insert(len(triplet_with_space.columns), 'Comment', comment)

    UserID = triplet_with_space.pop('UserID')
    triplet_with_space.insert(len(triplet_with_space.columns), 'UserID', UserID)
    user_name = triplet_with_space.pop('UserName')
    triplet_with_space.insert(len(triplet_with_space.columns), 'UserName', user_name)
    VerifierID = triplet_with_space.pop('VerifierID')
    triplet_with_space.insert(len(triplet_with_space.columns), 'VerifierID', VerifierID)
    verifier_name = triplet_with_space.pop('VerifierName')
    triplet_with_space.insert(len(triplet_with_space.columns), 'VerifierName', verifier_name)

    return triplet_with_space


# prepare the function for the use in main
# give semantic triplet with space
def semantic_triplet_space_main(inputDir, outputDir, macro_event_id):
    setup_Complex=os.path.join(inputDir,'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.xlsx')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df = pd.DataFrame(pd.read_excel(setup_Simplex))
        setup_Simplex_df = setup_Simplex_df.rename(columns = {'ID':'ID_setup_simplex'})

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex-Complex.xlsx')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Complex_Complex))
        setup_xref_Complex_Complex_df = setup_xref_Complex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex'})

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex-Complex.xlsx')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Complex))
        data_xref_Complex_Complex_df = data_xref_Complex_Complex_df.rename(columns = {'ID':'ID_data_xref_complex-complex', 'HigherComplex':'ID_data_complex', 'xrefID':'ID_setup_xref_complex_complex', 'LowerComplex':'ID_data_complex.1'})

    data_Complex=os.path.join(inputDir,'data_Complex.xlsx')
    if os.path.isfile(data_Complex):
        data_Complex_df = pd.DataFrame(pd.read_excel(data_Complex))
        data_Complex_df = data_Complex_df.rename(columns = {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"})

    data_Simplex=os.path.join(inputDir,'data_Simplex.xlsx')
    if os.path.isfile(data_Simplex):
        data_Simplex_df = pd.DataFrame(pd.read_excel(data_Simplex))
        data_Simplex_df = data_Simplex_df.rename(columns = {"ID":"ID_data_simplex", "SimplexType":"ID_setup_simplex", "refValue":"ID_data_date_number_text"})

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.xlsx')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df = pd.DataFrame(pd.read_excel(data_SimplexText))

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex-Complex.xlsx')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Simplex_Complex))
        data_xref_Simplex_Complex_df = data_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_data_xref_simplex-complex', 'xrefID':'ID_setup_xref_simplex_complex', 'Simplex':'ID_data_simplex', 'Complex':'ID_data_complex'})

    data_xref_Complex_Document=os.path.join(inputDir,'data_xref_Complex-Document.xlsx')
    if os.path.isfile(data_xref_Complex_Document):
        data_xref_Complex_Document_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Document))

    data_xref_VComment=os.path.join(inputDir,'data_xref_VComment.xlsx')
    if os.path.isfile(data_xref_VComment):
        data_xref_VComment_df = pd.DataFrame(pd.read_excel(data_xref_VComment))

    utility_Security=os.path.join(inputDir,'utility_Security.xlsx')
    if os.path.isfile(utility_Security):
        utility_Security_df = pd.DataFrame(pd.read_excel(utility_Security))
    else:
        mb.showwarning(title='Warning',
                       message='The table "utility_Security" is missing.\n\nPlease, make sure to export this table from PC-ACE data backened and try again.')
        return

    triplet_with_space = semantic_triplet_space(setup_Simplex_df, data_Simplex_df, data_SimplexText_df, setup_Complex_df, data_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_xref_Simplex_Complex_df, data_xref_Complex_Document_df, data_xref_VComment_df, utility_Security_df)

    if macro_event_id != '':
        macro_event_id = int(macro_event_id.split()[0])
        triplet_with_space = triplet_with_space[triplet_with_space['Macro Event ID'] == macro_event_id]

    triplet_with_space = triplet_with_space.sort_values(['Macro Event ID', 'Event ID', 'Semantic Triplet ID'], ascending=[True, True, True])

    triplet_with_space_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'triplet (SVO) with space')
    triplet_with_space.to_csv(triplet_with_space_file_name, encoding='utf-8', index=False)

    return triplet_with_space_file_name


# give semantic triplet with time and space
def semantic_triplet_time_space(inputDir, outputDir, macro_event_id):
    setup_Complex=os.path.join(inputDir,'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.xlsx')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df = pd.DataFrame(pd.read_excel(setup_Simplex))
        setup_Simplex_df = setup_Simplex_df.rename(columns = {'ID':'ID_setup_simplex'})

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex-Complex.xlsx')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Complex_Complex))
        setup_xref_Complex_Complex_df = setup_xref_Complex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex'})

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex-Complex.xlsx')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Complex))
        data_xref_Complex_Complex_df = data_xref_Complex_Complex_df.rename(columns = {'ID':'ID_data_xref_complex-complex', 'HigherComplex':'ID_data_complex', 'xrefID':'ID_setup_xref_complex_complex', 'LowerComplex':'ID_data_complex.1'})

    data_Complex=os.path.join(inputDir,'data_Complex.xlsx')
    if os.path.isfile(data_Complex):
        data_Complex_df = pd.DataFrame(pd.read_excel(data_Complex))
        data_Complex_df = data_Complex_df.rename(columns = {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"})

    data_Simplex=os.path.join(inputDir,'data_Simplex.xlsx')
    if os.path.isfile(data_Simplex):
        data_Simplex_df = pd.DataFrame(pd.read_excel(data_Simplex))
        data_Simplex_df = data_Simplex_df.rename(columns = {"ID":"ID_data_simplex", "SimplexType":"ID_setup_simplex", "refValue":"ID_data_date_number_text"})

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.xlsx')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df = pd.DataFrame(pd.read_excel(data_SimplexText))

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex-Complex.xlsx')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Simplex_Complex))
        data_xref_Simplex_Complex_df = data_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_data_xref_simplex-complex', 'xrefID':'ID_setup_xref_simplex_complex', 'Simplex':'ID_data_simplex', 'Complex':'ID_data_complex'})

    data_xref_Complex_Document=os.path.join(inputDir,'data_xref_Complex-Document.xlsx')
    if os.path.isfile(data_xref_Complex_Document):
        data_xref_Complex_Document_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Document))

    data_xref_VComment=os.path.join(inputDir,'data_xref_VComment.xlsx')
    if os.path.isfile(data_xref_VComment):
        data_xref_VComment_df = pd.DataFrame(pd.read_excel(data_xref_VComment))

    utility_Security=os.path.join(inputDir,'utility_Security.xlsx')
    if os.path.isfile(utility_Security):
        utility_Security_df = pd.DataFrame(pd.read_excel(utility_Security))
    else:
        mb.showwarning(title='Warning',
                       message='The table "utility_Security" is missing.\n\nPlease, make sure to export this table from PC-ACE data backened and try again.')
        return

    # triplet = semantic_triplet_simplex(setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_Complex_df, data_Simplex_df, data_SimplexText_df, data_xref_Simplex_Complex_df)

    triplet_with_space = semantic_triplet_space(setup_Simplex_df, data_Simplex_df, data_SimplexText_df, setup_Complex_df, data_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_xref_Simplex_Complex_df, data_xref_Complex_Document_df, data_xref_VComment_df, utility_Security_df)
    time = find_time_simplex(setup_Simplex_df, data_Simplex_df, data_SimplexText_df, setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_xref_Simplex_Complex_df)
    triplet_with_time_space = pd.merge(triplet_with_space, time, how = 'left', left_on = 'V ID', right_on = 'Process')
    triplet_with_time_space = triplet_with_time_space.drop('Process', axis = 1)
    triplet_with_time_space = triplet_with_time_space.rename(columns = {'Indefinite time of day':'Time ID', 'Time':'Time Simplex'})

    # move Document column to the last position of the dataframe
    document_id = triplet_with_time_space.pop('Document ID')
    triplet_with_time_space.insert(len(triplet_with_time_space.columns), 'Document ID', document_id)

    # move Comment column to the last position of the dataframe
    comment = triplet_with_time_space.pop('Comment')
    triplet_with_time_space.insert(len(triplet_with_time_space.columns), 'Comment', comment)

    # move VerifierID column to the last position of the dataframe
    UserID = triplet_with_time_space.pop('UserID')
    triplet_with_time_space.insert(len(triplet_with_time_space.columns), 'UserID', UserID)
    user_name = triplet_with_time_space.pop('UserName')
    triplet_with_time_space.insert(len(triplet_with_time_space.columns), 'UserName', user_name)
    VerifierID = triplet_with_time_space.pop('VerifierID')
    triplet_with_time_space.insert(len(triplet_with_time_space.columns), 'VerifierID', VerifierID)
    verifier_name = triplet_with_time_space.pop('VerifierName')
    triplet_with_time_space.insert(len(triplet_with_time_space.columns), 'VerifierName', verifier_name)

    if macro_event_id != '':
        macro_event_id = int(macro_event_id.split()[0])
        triplet_with_time_space = triplet_with_time_space[triplet_with_time_space['Macro Event ID'] == macro_event_id]

    triplet_with_time_space = triplet_with_time_space.sort_values(['Macro Event ID', 'Event ID', 'Semantic Triplet ID'], ascending=[True, True, True])

    triplet_with_space_time_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'triplet (SVO) with space and time')
    triplet_with_time_space.to_csv(triplet_with_space_time_file_name, encoding='utf-8', index=False)
    return triplet_with_space_time_file_name


# give indivudal characteristics
def individual_characteristics(inputDir, outputDir):
    setup_Complex=os.path.join(inputDir,'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.xlsx')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df = pd.DataFrame(pd.read_excel(setup_Simplex))
        setup_Simplex_df = setup_Simplex_df.rename(columns = {'ID':'ID_setup_simplex'})

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex-Complex.xlsx')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Complex_Complex))
        setup_xref_Complex_Complex_df = setup_xref_Complex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex'})

    setup_xref_Simplex_Complex=os.path.join(inputDir,'setup_xref_Simplex-Complex.xlsx')
    if os.path.isfile(setup_xref_Simplex_Complex):
        setup_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Simplex_Complex))
        setup_xref_Simplex_Complex_df = setup_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex', 'Complex':'ID_setup_complex', 'Simplex':'ID_setup_simplex'})

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex-Complex.xlsx')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Complex))
        data_xref_Complex_Complex_df = data_xref_Complex_Complex_df.rename(columns = {'ID':'ID_data_xref_complex-complex', 'HigherComplex':'ID_data_complex', 'xrefID':'ID_setup_xref_complex_complex', 'LowerComplex':'ID_data_complex.1'})

    data_Complex=os.path.join(inputDir,'data_Complex.xlsx')
    if os.path.isfile(data_Complex):
        data_Complex_df = pd.DataFrame(pd.read_excel(data_Complex))
        data_Complex_df = data_Complex_df.rename(columns = {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"})

    data_Simplex=os.path.join(inputDir,'data_Simplex.xlsx')
    if os.path.isfile(data_Simplex):
        data_Simplex_df = pd.DataFrame(pd.read_excel(data_Simplex))
        data_Simplex_df = data_Simplex_df.rename(columns = {"ID":"ID_data_simplex", "SimplexType":"ID_setup_simplex", "refValue":"ID_data_date_number_text"})

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.xlsx')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df = pd.DataFrame(pd.read_excel(data_SimplexText))

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex-Complex.xlsx')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Simplex_Complex))
        data_xref_Simplex_Complex_df = data_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_data_xref_simplex-complex', 'xrefID':'ID_setup_xref_simplex_complex', 'Simplex':'ID_data_simplex', 'Complex':'ID_data_complex'})

    data_SimplexNumber = os.path.join(inputDir, 'data_SimplexNumber.xlsx')
    if os.path.isfile(data_SimplexNumber):
        data_SimplexNumber_df = pd.DataFrame(pd.read_excel(data_SimplexNumber))

    data_xref_Complex_Document=os.path.join(inputDir,'data_xref_Complex-Document.xlsx')
    if os.path.isfile(data_xref_Complex_Document):
        data_xref_Complex_Document_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Document))

    data_xref_VComment=os.path.join(inputDir,'data_xref_VComment.xlsx')
    if os.path.isfile(data_xref_VComment):
        data_xref_VComment_df = pd.DataFrame(pd.read_excel(data_xref_VComment))

    utility_Security=os.path.join(inputDir,'utility_Security.xlsx')
    if os.path.isfile(utility_Security):
        utility_Security_df = pd.DataFrame(pd.read_excel(utility_Security))
    else:
        mb.showwarning(title='Warning',
                       message='The table "utility_Security" is missing.\n\nPlease, make sure to export this table from PC-ACE data backened and try again.')
        return


    # build table for complex
    id_complex = find_setup_id(['Individual'], setup_Complex_df).iat[0, 0]
    table_complex = data_Complex_df[data_Complex_df['ID_setup_complex'].isin([id_complex])]

    names_personal_characteristics = find_lower_complex(['Personal characteristics'], setup_Complex_df, setup_xref_Complex_Complex_df)
    names_personal_characteristics = names_personal_characteristics['Name'].values.tolist()

    path = ['Individual', 'Personal characteristics']

    for name in names_personal_characteristics:
        path.append(name)
        id_data_personal_characteristics = link_data_id(path, setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
        data_personal_characteristics = find_identifier(id_data_personal_characteristics, [name], data_Complex_df)
        table_complex = pd.merge(table_complex, data_personal_characteristics, how = 'left', left_on = 'ID_data_complex', right_on = 'Individual')
        table_complex = table_complex.drop('Individual', axis = 1)
        path.pop()

    table_complex = table_complex.drop('ID_setup_complex', axis = 1)
    table_complex = table_complex.rename(columns = {'ID_data_complex':'Individual', 'Identifier':'Individual Identifier'})

    # start to build simplex table
    table_simplex = table_complex

    data_Simplex_temp = pd.merge(data_Simplex_df, data_SimplexText_df, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    xref_sc_value = pd.merge(data_xref_Simplex_Complex_df, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

    # First name and last name
    complex_name = 'First name and last name'
    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)

    for i in range(3):
        simplex_name = simplex_names[0][i]
        simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Residence
    complex_name = 'Residence'

    simplex_id = find_setup_id_simplex(['City name', 'County', 'State'], setup_Simplex_df)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

    xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
    xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':'Type of territory'})

    path = ['Residence', 'Space', 'Territory', 'Type of territory']
    id_data_territory = link_data_id(path, setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
    id_data_territory = id_data_territory[id_data_territory['Residence'].notna()]
    id_data_territory = id_data_territory.drop_duplicates(subset = ['Residence'])
    data_territory = pd.merge(id_data_territory, xref_sc_value_new, how = 'left', left_on = 'Type of territory', right_on = 'Type of territory')
    data_territory = data_territory[['Residence', 'Type of territory', 'Value']]

    table_simplex = pd.merge(table_simplex, data_territory, how = 'left', left_on = complex_name, right_on = complex_name)

    table_simplex = table_simplex.rename(columns = {'Value':'Type of territory Simplex'})
    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Organization
    complex_name = 'Organization'

    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_name = simplex_names[0][0]
    simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex_df)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
    xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
    xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

    table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
    table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
    table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Family relationship
    complex_name = 'Family relationship'

    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_name = simplex_names[0][0]
    simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex_df)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
    xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
    xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

    table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
    table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
    table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Age
    data_Simplex_temp1 = pd.merge(data_Simplex_df, data_SimplexText_df, how = 'right', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp1 = data_Simplex_temp1.dropna(subset = ['Value'])
    data_Simplex_temp2 = pd.merge(data_Simplex_df, data_SimplexNumber_df, how = 'right', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp2 = data_Simplex_temp2.dropna(subset = ['Value'])
    data_Simplex_temp = pd.concat([data_Simplex_temp1, data_Simplex_temp2])
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'Value']]
    data_Simplex_temp = pd.merge(data_Simplex_df, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    xref_sc_value = pd.merge(data_xref_Simplex_Complex_df, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

    complex_name = 'Age'
    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)

    for i in range(2):
        simplex_name = simplex_names[0][i]
        simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # simplex directly under Individual
    complex_name = 'Individual'

    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_names = simplex_names[0]

    for name in simplex_names:
        simplex_id = find_setup_id_simplex([name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':name, 'Value':name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex.rename(columns=lambda x: x + " ID" if "Simplex" not in x else x, inplace=True)

    # add document information
    # ref: complex id for semantic triplet
    data_xref_Complex_Document_modified = data_xref_Complex_Document_df[['Complex','Document']]
    table_simplex = pd.merge(table_simplex, data_xref_Complex_Document_modified, how = 'left', left_on = 'Individual ID', right_on = 'Complex')
    table_simplex = table_simplex.drop('Complex', axis = 1)
    table_simplex = table_simplex.rename(columns={'Document':'Document ID'})

    # add VComment
    # ref: complex id for semantic triplet
    data_xref_VComment_modified = data_xref_VComment_df[['Complex','Comment','UserID','VerifierID']]
    table_simplex = pd.merge(table_simplex, data_xref_VComment_modified, how = 'left', left_on = 'Individual ID', right_on = 'Complex')
    table_simplex = table_simplex.drop('Complex', axis = 1)

    utility_Security_df = utility_Security_df[['ID', 'UserName']]
    utility_Security_user = utility_Security_df.rename(columns={'ID': 'UserID'})
    table_simplex = pd.merge(table_simplex, utility_Security_user, how = 'left', left_on = 'UserID', right_on = 'UserID')
    user_name = table_simplex.pop('UserName')
    userID_idx = table_simplex.columns.get_loc('UserID')
    table_simplex.insert(userID_idx + 1, 'UserName', user_name)
    utility_Security_verifier = utility_Security_df.rename(columns={'ID': 'VerifierID', 'UserName':'VerifierName'})
    table_simplex = pd.merge(table_simplex, utility_Security_verifier, how = 'left', left_on = 'VerifierID', right_on = 'VerifierID')
    verifier_name = table_simplex.pop('VerifierName')
    verifierID_idx = table_simplex.columns.get_loc('VerifierID')
    table_simplex.insert(verifierID_idx + 1, 'VerifierName', verifier_name)

    individual_characteristics_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'individual characteristics')
    table_simplex.to_csv(individual_characteristics_file_name, encoding='utf-8', index=False)

    return individual_characteristics_file_name


# give collective actor characteristics
def collective_actor_characteristics(inputDir, outputDir):
    setup_Complex=os.path.join(inputDir,'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.xlsx')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df = pd.DataFrame(pd.read_excel(setup_Simplex))
        setup_Simplex_df = setup_Simplex_df.rename(columns = {'ID':'ID_setup_simplex'})

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex-Complex.xlsx')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Complex_Complex))
        setup_xref_Complex_Complex_df = setup_xref_Complex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex'})

    setup_xref_Simplex_Complex=os.path.join(inputDir,'setup_xref_Simplex-Complex.xlsx')
    if os.path.isfile(setup_xref_Simplex_Complex):
        setup_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Simplex_Complex))
        setup_xref_Simplex_Complex_df = setup_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex', 'Complex':'ID_setup_complex', 'Simplex':'ID_setup_simplex'})

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex-Complex.xlsx')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Complex))
        data_xref_Complex_Complex_df = data_xref_Complex_Complex_df.rename(columns = {'ID':'ID_data_xref_complex-complex', 'HigherComplex':'ID_data_complex', 'xrefID':'ID_setup_xref_complex_complex', 'LowerComplex':'ID_data_complex.1'})

    data_Complex=os.path.join(inputDir,'data_Complex.xlsx')
    if os.path.isfile(data_Complex):
        data_Complex_df = pd.DataFrame(pd.read_excel(data_Complex))
        data_Complex_df = data_Complex_df.rename(columns = {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"})

    data_Simplex=os.path.join(inputDir,'data_Simplex.xlsx')
    if os.path.isfile(data_Simplex):
        data_Simplex_df = pd.DataFrame(pd.read_excel(data_Simplex))
        data_Simplex_df = data_Simplex_df.rename(columns = {"ID":"ID_data_simplex", "SimplexType":"ID_setup_simplex", "refValue":"ID_data_date_number_text"})

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.xlsx')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df = pd.DataFrame(pd.read_excel(data_SimplexText))

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex-Complex.xlsx')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Simplex_Complex))
        data_xref_Simplex_Complex_df = data_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_data_xref_simplex-complex', 'xrefID':'ID_setup_xref_simplex_complex', 'Simplex':'ID_data_simplex', 'Complex':'ID_data_complex'})

    data_SimplexNumber = os.path.join(inputDir, 'data_SimplexNumber.xlsx')
    if os.path.isfile(data_SimplexNumber):
        data_SimplexNumber_df = pd.DataFrame(pd.read_excel(data_SimplexNumber))

    data_xref_Complex_Document=os.path.join(inputDir,'data_xref_Complex-Document.xlsx')
    if os.path.isfile(data_xref_Complex_Document):
        data_xref_Complex_Document_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Document))

    data_xref_VComment=os.path.join(inputDir,'data_xref_VComment.xlsx')
    if os.path.isfile(data_xref_VComment):
        data_xref_VComment_df = pd.DataFrame(pd.read_excel(data_xref_VComment))

    utility_Security=os.path.join(inputDir,'utility_Security.xlsx')
    if os.path.isfile(utility_Security):
        utility_Security_df = pd.DataFrame(pd.read_excel(utility_Security))
    else:
        mb.showwarning(title='Warning',
                       message='The table "utility_Security" is missing.\n\nPlease, make sure to export this table from PC-ACE data backened and try again.')
        return


    # build table for complex
    id_complex = find_setup_id(['Collective actor'], setup_Complex_df).iat[0, 0]
    table_complex = data_Complex_df[data_Complex_df['ID_setup_complex'].isin([id_complex])]

    names_collective_characteristics = find_lower_complex(['Collective characteristics'], setup_Complex_df, setup_xref_Complex_Complex_df)
    names_collective_characteristics = names_collective_characteristics['Name'].values.tolist()
    names_collective_characteristics.remove('Subgroup (among which)')

    path = ['Collective actor', 'Collective characteristics']

    for name in names_collective_characteristics:
        path.append(name)
        id_data_collective_characteristics = link_data_id(path, setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
        data_collective_characteristics = find_identifier(id_data_collective_characteristics, [name], data_Complex_df)
        table_complex = pd.merge(table_complex, data_collective_characteristics, how = 'left', left_on = 'ID_data_complex', right_on = 'Collective actor')
        table_complex = table_complex.drop('Collective actor', axis = 1)
        path.pop()

    table_complex = table_complex.drop('ID_setup_complex', axis = 1)
    table_complex = table_complex.rename(columns = {'ID_data_complex':'Collective actor', 'Identifier':'Collective actor Identifier'})

    # start to build simplex table
    table_simplex = table_complex

    data_Simplex_temp = pd.merge(data_Simplex_df, data_SimplexText_df, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    xref_sc_value = pd.merge(data_xref_Simplex_Complex_df, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

    # Organization
    complex_name = 'Organization'

    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_name = simplex_names[0][0]
    simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex_df)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
    xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
    xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

    table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
    table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
    table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Group composition
    complex_name = 'Group composition'

    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_name = simplex_names[0][0]
    simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex_df)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
    xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
    xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

    table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
    table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
    table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Residence
    complex_name = 'Residence'

    simplex_id = find_setup_id_simplex(['City name', 'County', 'State'], setup_Simplex_df)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

    xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
    xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':'Type of territory'})

    path = ['Residence', 'Space', 'Territory', 'Type of territory']
    id_data_territory = link_data_id(path, setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
    id_data_territory = id_data_territory[id_data_territory['Residence'].notna()]
    id_data_territory = id_data_territory.drop_duplicates(subset = ['Residence'])
    data_territory = pd.merge(id_data_territory, xref_sc_value_new, how = 'left', left_on = 'Type of territory', right_on = 'Type of territory')
    data_territory = data_territory[['Residence', 'Type of territory', 'Value']]

    table_simplex = pd.merge(table_simplex, data_territory, how = 'left', left_on = complex_name, right_on = complex_name)

    table_simplex = table_simplex.rename(columns = {'Value':'Type of territory Simplex'})
    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Family relationship
    complex_name = 'Family relationship'

    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_name = simplex_names[0][0]
    simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex_df)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
    xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
    xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

    table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
    table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
    table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Age
    data_Simplex_temp1 = pd.merge(data_Simplex_df, data_SimplexText_df, how = 'right', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp1 = data_Simplex_temp1.dropna(subset = ['Value'])
    data_Simplex_temp2 = pd.merge(data_Simplex_df, data_SimplexNumber_df, how = 'right', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp2 = data_Simplex_temp2.dropna(subset = ['Value'])
    data_Simplex_temp = pd.concat([data_Simplex_temp1, data_Simplex_temp2])
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'Value']]
    data_Simplex_temp = pd.merge(data_Simplex_df, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    xref_sc_value = pd.merge(data_xref_Simplex_Complex_df, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

    complex_name = 'Age'
    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)

    for i in range(2):
        simplex_name = simplex_names[0][i]
        simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Number
    complex_name = 'Number'
    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)

    for i in range(2):
        simplex_name = simplex_names[0][i]
        simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Simplex directly under Collective actor
    complex_name = 'Collective actor'

    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_names = simplex_names[0]

    for name in simplex_names:
        simplex_id = find_setup_id_simplex([name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':name, 'Value':name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex.rename(columns=lambda x: x + " ID" if "Simplex" not in x else x, inplace=True)

    # add document information
    # ref: complex id for semantic triplet
    data_xref_Complex_Document_modified = data_xref_Complex_Document_df[['Complex','Document']]
    table_simplex = pd.merge(table_simplex, data_xref_Complex_Document_modified, how = 'left', left_on = 'Collective actor ID', right_on = 'Complex')
    table_simplex = table_simplex.drop('Complex', axis = 1)
    table_simplex = table_simplex.rename(columns={'Document':'Document ID'})

    # add VComment
    # ref: complex id for semantic triplet
    data_xref_VComment_modified = data_xref_VComment_df[['Complex','Comment','UserID','VerifierID']]
    table_simplex = pd.merge(table_simplex, data_xref_VComment_modified, how = 'left', left_on = 'Collective actor ID', right_on = 'Complex')
    table_simplex = table_simplex.drop('Complex', axis = 1)

    utility_Security_df = utility_Security_df[['ID', 'UserName']]
    utility_Security_user = utility_Security_df.rename(columns={'ID': 'UserID'})
    table_simplex = pd.merge(table_simplex, utility_Security_user, how = 'left', left_on = 'UserID', right_on = 'UserID')
    user_name = table_simplex.pop('UserName')
    userID_idx = table_simplex.columns.get_loc('UserID')
    table_simplex.insert(userID_idx + 1, 'UserName', user_name)
    utility_Security_verifier = utility_Security_df.rename(columns={'ID': 'VerifierID', 'UserName':'VerifierName'})
    table_simplex = pd.merge(table_simplex, utility_Security_verifier, how = 'left', left_on = 'VerifierID', right_on = 'VerifierID')
    verifier_name = table_simplex.pop('VerifierName')
    verifierID_idx = table_simplex.columns.get_loc('VerifierID')
    table_simplex.insert(verifierID_idx + 1, 'VerifierName', verifier_name)

    collective_actor_characteristics_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'collective actor characteristics')
    table_simplex.to_csv(collective_actor_characteristics_file_name, encoding='utf-8', index=False)

    return collective_actor_characteristics_file_name


def organization_characteristics(setup_Simplex, data_Simplex, data_SimplexText, data_SimplexNumber, data_Complex, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex, setup_xref_Simplex_Complex, data_xref_Simplex_Complex, data_xref_Complex_Document_df, data_xref_VComment_df, utility_Security_df):
    # organization
    id_complex = find_setup_id(['Organization'], setup_Complex).iat[0, 0]
    table = data_Complex[data_Complex['ID_setup_complex'].isin([id_complex])]

    names_organization = find_lower_complex(['Organization'], setup_Complex, setup_xref_Complex_Complex)
    names_organization = names_organization['Name'].values.tolist()

    path = ['Organization']

    for name in names_organization:
        path.append(name)
        id_data_collective_characteristics = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
        data_collective_characteristics = find_identifier(id_data_collective_characteristics, [name], data_Complex)
        table = pd.merge(table, data_collective_characteristics, how = 'left', left_on = 'ID_data_complex', right_on = 'Organization')
        table = table.drop('Organization', axis = 1)
        path.pop()

    table = table.drop('ID_setup_complex', axis = 1)
    table = table.rename(columns={'ID_data_complex':'Organization', 'Identifier':'Organization Identifier'})

    organization_table_complex = table

    # institution
    # build table for complex
    id_complex = find_setup_id(['Institution'], setup_Complex).iat[0, 0]
    table_complex = data_Complex[data_Complex['ID_setup_complex'].isin([id_complex])]

    table_complex = table_complex.drop('ID_setup_complex', axis = 1)
    table_complex = table_complex.rename(columns = {'ID_data_complex':'Institution', 'Identifier':'Institution Identifier'})

    # start to build simplex table
    table_simplex = table_complex

    data_Simplex_temp = pd.merge(data_Simplex, data_SimplexText, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    xref_sc_value = pd.merge(data_xref_Simplex_Complex, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

    complex_name = 'Institution'
    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex, setup_xref_Simplex_Complex)
    simplex_names = simplex_names[0]

    for i in range(len(simplex_names)):
        simplex_name = simplex_names[i]
        simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    institution_table_simplex = table_simplex
    institution_table_simplex = institution_table_simplex.drop('Institution Identifier', axis = 1)

    # attach institution_table_simplex to organization_table_complex
    organization_table_complex = pd.merge(organization_table_complex, institution_table_simplex, how = 'left', left_on = 'Institution', right_on = 'Institution')
    organization_table_complex = organization_table_complex.drop('Institution Identifier', axis = 1)
    organization_table_complex = organization_table_complex.drop('Institution', axis = 1)

    # Complex organization
    id_complex = find_setup_id(['Complex organization'], setup_Complex).iat[0, 0]
    table = data_Complex[data_Complex['ID_setup_complex'].isin([id_complex])]

    names_organization = find_lower_complex(['Complex organization'], setup_Complex, setup_xref_Complex_Complex)
    names_organization = names_organization['Name'].values.tolist()

    path = ['Organization', 'Complex organization']

    for name in names_organization:
        path.append(name)
        id_data_collective_characteristics = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
        data_collective_characteristics = find_identifier(id_data_collective_characteristics, [name], data_Complex)
        table = pd.merge(table, data_collective_characteristics, how = 'left', left_on = 'ID_data_complex', right_on = 'Organization')
        table = table.drop('Organization', axis = 1)
        path.pop()

    table = table.drop('ID_setup_complex', axis = 1)
    table = table.rename(columns={'ID_data_complex':'Complex organization', 'Identifier':'Complex organization Identifier'})

    complex_organization_table_complex = table

    # Complex Organization: Number of individuals in unit
    data_Simplex_temp1 = pd.merge(data_Simplex, data_SimplexText, how = 'right', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp1 = data_Simplex_temp1.dropna(subset = ['Value'])
    data_Simplex_temp2 = pd.merge(data_Simplex, data_SimplexNumber, how = 'right', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp2 = data_Simplex_temp2.dropna(subset = ['Value'])
    data_Simplex_temp = pd.concat([data_Simplex_temp1, data_Simplex_temp2])
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'Value']]
    data_Simplex_temp = pd.merge(data_Simplex, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    xref_sc_value = pd.merge(data_xref_Simplex_Complex, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

    direct_complex = 'Number of individuals in unit'

    path = ['Number of individuals in unit', 'Number']
    table_simplex = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)

    complex_name = 'Number'
    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex, setup_xref_Simplex_Complex)

    for i in range(2):
        simplex_name = simplex_names[0][i]
        simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name+' of '+direct_complex, 'Value':simplex_name+' Simplex of '+direct_complex})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)


    table_simplex = table_simplex.drop('Number', axis = 1)

    num_in_units_table_simplex = table_simplex

    # attach num_in_units_table_simplex to complex_organization_table_complex
    complex_organization_table_complex = pd.merge(complex_organization_table_complex, num_in_units_table_simplex, how = 'left', left_on = direct_complex, right_on = direct_complex)
    complex_organization_table_complex = complex_organization_table_complex.drop(direct_complex, axis = 1)
    complex_organization_table_complex = complex_organization_table_complex.drop(direct_complex+' Identifier', axis = 1)

    # Locality of unit
    complex_name = 'Locality of unit'

    path = ['Locality of unit', 'Space']
    table_simplex = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)

    simplex_id = find_setup_id_simplex(['City name', 'County', 'State'], setup_Simplex)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

    xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
    xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':'Type of territory'})

    path = ['Locality of unit', 'Space', 'Territory', 'Type of territory']
    id_data_territory = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    id_data_territory = id_data_territory[id_data_territory[complex_name].notna()]
    id_data_territory = id_data_territory.drop_duplicates(subset = [complex_name])
    data_territory = pd.merge(id_data_territory, xref_sc_value_new, how = 'left', left_on = 'Type of territory', right_on = 'Type of territory')
    data_territory = data_territory[[complex_name, 'Type of territory', 'Value']]

    data_territory = data_territory.rename(columns = {'Type of territory':'Type of territory of '+complex_name, 'Value':'Type of territory Simplex of '+complex_name})

    locality_unit_table_simplex = data_territory

    # attach locality_unit_table_simplex to complex_organization_table_complex
    complex_organization_table_complex = pd.merge(complex_organization_table_complex, locality_unit_table_simplex, how = 'left', left_on = complex_name, right_on = complex_name)
    complex_organization_table_complex = complex_organization_table_complex.drop(complex_name, axis = 1)
    complex_organization_table_complex = complex_organization_table_complex.drop(complex_name+' Identifier', axis = 1)

    # Number and level of organizational unit
    direct_complex = 'Number and level of organizational unit'

    path = ['Number and level of organizational unit', 'Number']
    table_simplex = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)

    complex_name = 'Number'
    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex, setup_xref_Simplex_Complex)

    for i in range(2):
        simplex_name = simplex_names[0][i]
        simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name+' of '+direct_complex, 'Value':simplex_name+' Simplex of '+direct_complex})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop('Number', axis = 1)

    numlevel_units_table_simplex = table_simplex

    # attach numlevel_units_table_simplex to complex_organization_table_complex
    complex_organization_table_complex = pd.merge(complex_organization_table_complex, numlevel_units_table_simplex, how = 'left', left_on = direct_complex, right_on = direct_complex)
    complex_organization_table_complex = complex_organization_table_complex.drop(direct_complex, axis = 1)
    complex_organization_table_complex = complex_organization_table_complex.drop(direct_complex+' Identifier', axis = 1)

    # Name of units
    path = ['Complex organization', 'Name of unit']
    table_simplex = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)

    data_Simplex_temp = pd.merge(data_Simplex, data_SimplexText, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    xref_sc_value = pd.merge(data_xref_Simplex_Complex, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

    complex_name = 'Name of unit'
    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex, setup_xref_Simplex_Complex)
    simplex_names = simplex_names[0]

    for i in range(len(simplex_names)):
        simplex_name = simplex_names[i]
        simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    name_unit_table_simplex = table_simplex

    # attach name_unit_table_simplex to complex_organization_table_complex
    complex_organization_table_complex = complex_organization_table_complex.drop(complex_name, axis = 1)
    complex_organization_table_complex = complex_organization_table_complex.drop(complex_name+' Identifier', axis = 1)
    complex_organization_table_complex = pd.merge(complex_organization_table_complex, name_unit_table_simplex, how = 'left', left_on = 'Complex organization', right_on = 'Complex organization')

    # Ownership
    complex_name = 'Ownership'

    path = [complex_name]
    ownership_lower_complex = find_lower_complex([complex_name], setup_Complex, setup_xref_Complex_Complex)
    ownership_lower_complex = ownership_lower_complex['Name'].values.tolist()

    name = ownership_lower_complex[0]
    path.append(name)
    table_simplex = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    table_simplex = table_simplex.rename(columns = {name:name + ' of ' + complex_name})
    path.pop()

    ownership_lower_complex = ownership_lower_complex[1:]

    for name in ownership_lower_complex:
        path.append(name)
        id_data_ownership_lower_complex = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
        table_simplex = pd.merge(table_simplex, id_data_ownership_lower_complex, how = 'left', left_on = path[0], right_on = path[0])
        table_simplex = table_simplex.rename(columns = {name:name + ' of ' + complex_name})
        path.pop()

    # attach table_simplex to complex_organization_table_complex
    complex_organization_table_complex = pd.merge(complex_organization_table_complex, table_simplex, how = 'left', left_on = complex_name, right_on = complex_name)
    complex_organization_table_complex = complex_organization_table_complex.drop(complex_name, axis = 1)
    # complex_organization_table_complex = complex_organization_table_complex.drop(complex_name+' Identifier', axis = 1)

    # merge complex_organization_table_complex to organization_table_complex
    complex_organization_table_complex = complex_organization_table_complex.drop('Complex organization Identifier', axis = 1)
    organization_table = pd.merge(organization_table_complex, complex_organization_table_complex, how = 'left', left_on = 'Complex organization', right_on = 'Complex organization')
    organization_table = organization_table.drop('Complex organization', axis = 1)
    organization_table = organization_table.drop('Complex organization Identifier', axis = 1)

    # Simplex directly under Organization
    complex_name = 'Organization'

    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex, setup_xref_Simplex_Complex)
    simplex_names = simplex_names[0]

    for name in simplex_names:
        simplex_id = find_setup_id_simplex([name], setup_Simplex)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        organization_table = pd.merge(organization_table, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        organization_table = organization_table.rename(columns = {'ID_data_simplex':name, 'Value':name+' Simplex'})
        organization_table = organization_table.drop('ID_setup_simplex', axis = 1)

    organization_table.rename(columns=lambda x: x + " ID" if "Simplex" not in x else x, inplace=True)

    # add document information
    # ref: complex id for semantic triplet
    data_xref_Complex_Document_modified = data_xref_Complex_Document_df[['Complex','Document']]
    organization_table = pd.merge(organization_table, data_xref_Complex_Document_modified, how = 'left', left_on = 'Organization ID', right_on = 'Complex')
    organization_table = organization_table.drop('Complex', axis = 1)
    organization_table = organization_table.rename(columns={'Document':'Document ID'})

    # add VComment
    # ref: complex id for semantic triplet
    data_xref_VComment_modified = data_xref_VComment_df[['Complex','Comment','UserID','VerifierID']]
    organization_table = pd.merge(organization_table, data_xref_VComment_modified, how = 'left', left_on = 'Organization ID', right_on = 'Complex')
    organization_table = organization_table.drop('Complex', axis = 1)

    utility_Security_df = utility_Security_df[['ID', 'UserName']]
    utility_Security_user = utility_Security_df.rename(columns={'ID': 'UserID'})
    organization_table = pd.merge(organization_table, utility_Security_user, how = 'left', left_on = 'UserID', right_on = 'UserID')
    user_name = organization_table.pop('UserName')
    userID_idx = organization_table.columns.get_loc('UserID')
    organization_table.insert(userID_idx + 1, 'UserName', user_name)
    utility_Security_verifier = utility_Security_df.rename(columns={'ID': 'VerifierID', 'UserName':'VerifierName'})
    organization_table = pd.merge(organization_table, utility_Security_verifier, how = 'left', left_on = 'VerifierID', right_on = 'VerifierID')
    verifier_name = organization_table.pop('VerifierName')
    verifierID_idx = organization_table.columns.get_loc('VerifierID')
    organization_table.insert(verifierID_idx + 1, 'VerifierName', verifier_name)

    return organization_table


def organization_characteristics_main(inputDir, outputDir):
    setup_Complex=os.path.join(inputDir,'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.xlsx')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df = pd.DataFrame(pd.read_excel(setup_Simplex))
        setup_Simplex_df = setup_Simplex_df.rename(columns = {'ID':'ID_setup_simplex'})

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex-Complex.xlsx')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Complex_Complex))
        setup_xref_Complex_Complex_df = setup_xref_Complex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex'})

    setup_xref_Simplex_Complex=os.path.join(inputDir,'setup_xref_Simplex-Complex.xlsx')
    if os.path.isfile(setup_xref_Simplex_Complex):
        setup_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Simplex_Complex))
        setup_xref_Simplex_Complex_df = setup_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex', 'Complex':'ID_setup_complex', 'Simplex':'ID_setup_simplex'})

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex-Complex.xlsx')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Complex))
        data_xref_Complex_Complex_df = data_xref_Complex_Complex_df.rename(columns = {'ID':'ID_data_xref_complex-complex', 'HigherComplex':'ID_data_complex', 'xrefID':'ID_setup_xref_complex_complex', 'LowerComplex':'ID_data_complex.1'})

    data_Complex=os.path.join(inputDir,'data_Complex.xlsx')
    if os.path.isfile(data_Complex):
        data_Complex_df = pd.DataFrame(pd.read_excel(data_Complex))
        data_Complex_df = data_Complex_df.rename(columns = {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"})

    data_Simplex=os.path.join(inputDir,'data_Simplex.xlsx')
    if os.path.isfile(data_Simplex):
        data_Simplex_df = pd.DataFrame(pd.read_excel(data_Simplex))
        data_Simplex_df = data_Simplex_df.rename(columns = {"ID":"ID_data_simplex", "SimplexType":"ID_setup_simplex", "refValue":"ID_data_date_number_text"})

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.xlsx')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df = pd.DataFrame(pd.read_excel(data_SimplexText))

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex-Complex.xlsx')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Simplex_Complex))
        data_xref_Simplex_Complex_df = data_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_data_xref_simplex-complex', 'xrefID':'ID_setup_xref_simplex_complex', 'Simplex':'ID_data_simplex', 'Complex':'ID_data_complex'})

    data_SimplexNumber = os.path.join(inputDir, 'data_SimplexNumber.xlsx')
    if os.path.isfile(data_SimplexNumber):
        data_SimplexNumber_df = pd.DataFrame(pd.read_excel(data_SimplexNumber))

    data_xref_Complex_Document=os.path.join(inputDir,'data_xref_Complex-Document.xlsx')
    if os.path.isfile(data_xref_Complex_Document):
        data_xref_Complex_Document_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Document))

    data_xref_VComment=os.path.join(inputDir,'data_xref_VComment.xlsx')
    if os.path.isfile(data_xref_VComment):
        data_xref_VComment_df = pd.DataFrame(pd.read_excel(data_xref_VComment))

    utility_Security=os.path.join(inputDir,'utility_Security.xlsx')
    if os.path.isfile(utility_Security):
        utility_Security_df = pd.DataFrame(pd.read_excel(utility_Security))
    else:
        mb.showwarning(title='Warning',
                       message='The table "utility_Security" is missing.\n\nPlease, make sure to export this table from PC-ACE data backened and try again.')
        return

    table_simplex = organization_characteristics(setup_Simplex_df, data_Simplex_df, data_SimplexText_df, data_SimplexNumber_df, data_Complex_df, setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, setup_xref_Simplex_Complex_df, data_xref_Simplex_Complex_df, data_xref_Complex_Document_df, data_xref_VComment_df, utility_Security_df)

    organization_characteristics_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'organization characteristics')
    table_simplex.to_csv(organization_characteristics_file_name, encoding='utf-8', index=False)

    return organization_characteristics_file_name


def victim_of_lynching_info(inputDir, outputDir):
    setup_Complex=os.path.join(inputDir,'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.xlsx')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df = pd.DataFrame(pd.read_excel(setup_Simplex))
        setup_Simplex_df = setup_Simplex_df.rename(columns = {'ID':'ID_setup_simplex'})

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex-Complex.xlsx')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Complex_Complex))
        setup_xref_Complex_Complex_df = setup_xref_Complex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex'})

    setup_xref_Simplex_Complex=os.path.join(inputDir,'setup_xref_Simplex-Complex.xlsx')
    if os.path.isfile(setup_xref_Simplex_Complex):
        setup_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Simplex_Complex))
        setup_xref_Simplex_Complex_df = setup_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex', 'Complex':'ID_setup_complex', 'Simplex':'ID_setup_simplex'})

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex-Complex.xlsx')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Complex))
        data_xref_Complex_Complex_df = data_xref_Complex_Complex_df.rename(columns = {'ID':'ID_data_xref_complex-complex', 'HigherComplex':'ID_data_complex', 'xrefID':'ID_setup_xref_complex_complex', 'LowerComplex':'ID_data_complex.1'})

    data_Complex=os.path.join(inputDir,'data_Complex.xlsx')
    if os.path.isfile(data_Complex):
        data_Complex_df = pd.DataFrame(pd.read_excel(data_Complex))
        data_Complex_df = data_Complex_df.rename(columns = {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"})

    data_Simplex=os.path.join(inputDir,'data_Simplex.xlsx')
    if os.path.isfile(data_Simplex):
        data_Simplex_df = pd.DataFrame(pd.read_excel(data_Simplex))
        data_Simplex_df = data_Simplex_df.rename(columns = {"ID":"ID_data_simplex", "SimplexType":"ID_setup_simplex", "refValue":"ID_data_date_number_text"})

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.xlsx')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df = pd.DataFrame(pd.read_excel(data_SimplexText))

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex-Complex.xlsx')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Simplex_Complex))
        data_xref_Simplex_Complex_df = data_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_data_xref_simplex-complex', 'xrefID':'ID_setup_xref_simplex_complex', 'Simplex':'ID_data_simplex', 'Complex':'ID_data_complex'})

    data_SimplexNumber = os.path.join(inputDir, 'data_SimplexNumber.xlsx')
    if os.path.isfile(data_SimplexNumber):
        data_SimplexNumber_df = pd.DataFrame(pd.read_excel(data_SimplexNumber))

    # build table for complex
    id_complex = find_setup_id(['Victim of lynching'], setup_Complex_df).iat[0, 0]
    table_complex = data_Complex_df[data_Complex_df['ID_setup_complex'].isin([id_complex])]

    names_victim_of_lynching = find_lower_complex(['Victim of lynching'], setup_Complex_df, setup_xref_Complex_Complex_df)
    names_victim_of_lynching = names_victim_of_lynching['Name'].values.tolist()

    path = ['Victim of lynching']

    for name in names_victim_of_lynching:
        path.append(name)
        id_data_victim_of_lynching = link_data_id(path, setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
        data_victim_of_lynching = find_identifier(id_data_victim_of_lynching, [name], data_Complex_df)
        table_complex = pd.merge(table_complex, data_victim_of_lynching, how = 'left', left_on = 'ID_data_complex', right_on = 'Victim of lynching')
        table_complex = table_complex.drop('Victim of lynching', axis = 1)
        path.pop()

    table_complex = table_complex.drop('ID_setup_complex', axis = 1)
    table_complex = table_complex.rename(columns = {'ID_data_complex':'Victim of lynching', 'Identifier':'Victim of lynching Identifier'})

    # start to build simplex table
    table_simplex = table_complex

    data_Simplex_temp = pd.merge(data_Simplex_df, data_SimplexText_df, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    xref_sc_value = pd.merge(data_xref_Simplex_Complex_df, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

    # Age
    data_Simplex_temp1 = pd.merge(data_Simplex_df, data_SimplexText_df, how = 'right', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp1 = data_Simplex_temp1.dropna(subset = ['Value'])
    data_Simplex_temp2 = pd.merge(data_Simplex_df, data_SimplexNumber_df, how = 'right', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp2 = data_Simplex_temp2.dropna(subset = ['Value'])
    data_Simplex_temp = pd.concat([data_Simplex_temp1, data_Simplex_temp2])
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'Value']]
    data_Simplex_temp = pd.merge(data_Simplex_df, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    xref_sc_value = pd.merge(data_xref_Simplex_Complex_df, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

    complex_name = 'Age'
    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)

    for i in range(2):
        simplex_name = simplex_names[0][i]
        simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Residence
    complex_name = 'Residence'

    simplex_id = find_setup_id_simplex(['City name', 'County', 'State'], setup_Simplex_df)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

    xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
    xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':'Type of territory'})

    path = ['Residence', 'Space', 'Territory', 'Type of territory']
    id_data_territory = link_data_id(path, setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
    id_data_territory = id_data_territory[id_data_territory['Residence'].notna()]
    id_data_territory = id_data_territory.drop_duplicates(subset = ['Residence'])
    data_territory = pd.merge(id_data_territory, xref_sc_value_new, how = 'left', left_on = 'Type of territory', right_on = 'Type of territory')
    data_territory = data_territory[['Residence', 'Type of territory', 'Value']]

    table_simplex = pd.merge(table_simplex, data_territory, how = 'left', left_on = complex_name, right_on = complex_name)

    table_simplex = table_simplex.rename(columns = {'Value':'Type of territory Simplex'})
    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Victim (Beck)
    complex_name = 'Victim (Beck)'

    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_names = simplex_names[0]

    for name in simplex_names:
        simplex_id = find_setup_id_simplex([name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':name, 'Value':name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Victim (Brundage)
    complex_name = 'Victim (Brundage)'

    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_names = simplex_names[0]

    for name in simplex_names:
        simplex_id = find_setup_id_simplex([name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':name, 'Value':name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # simplex directly under Individual
    complex_name = 'Victim of lynching'

    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_names = simplex_names[0]

    for name in simplex_names:
        simplex_id = find_setup_id_simplex([name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':name, 'Value':name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)



    information_victim_of_lynching_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'victim of lynching information')
    table_simplex.to_csv(information_victim_of_lynching_file_name, encoding='utf-8', index=False)

    return information_victim_of_lynching_file_name


def victim_of_alleged_crime_info(inputDir, outputDir):
    setup_Complex=os.path.join(inputDir,'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.xlsx')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df = pd.DataFrame(pd.read_excel(setup_Simplex))
        setup_Simplex_df = setup_Simplex_df.rename(columns = {'ID':'ID_setup_simplex'})

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex-Complex.xlsx')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Complex_Complex))
        setup_xref_Complex_Complex_df = setup_xref_Complex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex'})

    setup_xref_Simplex_Complex=os.path.join(inputDir,'setup_xref_Simplex-Complex.xlsx')
    if os.path.isfile(setup_xref_Simplex_Complex):
        setup_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Simplex_Complex))
        setup_xref_Simplex_Complex_df = setup_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex', 'Complex':'ID_setup_complex', 'Simplex':'ID_setup_simplex'})

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex-Complex.xlsx')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Complex))
        data_xref_Complex_Complex_df = data_xref_Complex_Complex_df.rename(columns = {'ID':'ID_data_xref_complex-complex', 'HigherComplex':'ID_data_complex', 'xrefID':'ID_setup_xref_complex_complex', 'LowerComplex':'ID_data_complex.1'})

    data_Complex=os.path.join(inputDir,'data_Complex.xlsx')
    if os.path.isfile(data_Complex):
        data_Complex_df = pd.DataFrame(pd.read_excel(data_Complex))
        data_Complex_df = data_Complex_df.rename(columns = {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"})

    data_Simplex=os.path.join(inputDir,'data_Simplex.xlsx')
    if os.path.isfile(data_Simplex):
        data_Simplex_df = pd.DataFrame(pd.read_excel(data_Simplex))
        data_Simplex_df = data_Simplex_df.rename(columns = {"ID":"ID_data_simplex", "SimplexType":"ID_setup_simplex", "refValue":"ID_data_date_number_text"})

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.xlsx')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df = pd.DataFrame(pd.read_excel(data_SimplexText))

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex-Complex.xlsx')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Simplex_Complex))
        data_xref_Simplex_Complex_df = data_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_data_xref_simplex-complex', 'xrefID':'ID_setup_xref_simplex_complex', 'Simplex':'ID_data_simplex', 'Complex':'ID_data_complex'})

    data_SimplexNumber = os.path.join(inputDir, 'data_SimplexNumber.xlsx')
    if os.path.isfile(data_SimplexNumber):
        data_SimplexNumber_df = pd.DataFrame(pd.read_excel(data_SimplexNumber))

    # build table for complex
    id_complex = find_setup_id(['Victim of alleged crime'], setup_Complex_df).iat[0, 0]
    table_complex = data_Complex_df[data_Complex_df['ID_setup_complex'].isin([id_complex])]

    names_victim_of_alleged_crime = find_lower_complex(['Victim of alleged crime'], setup_Complex_df, setup_xref_Complex_Complex_df)
    names_victim_of_alleged_crime = names_victim_of_alleged_crime['Name'].values.tolist()

    path = ['Victim of alleged crime']

    for name in names_victim_of_alleged_crime:
        path.append(name)
        id_data_victim_of_alleged_crime = link_data_id(path, setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
        data_victim_of_alleged_crime = find_identifier(id_data_victim_of_alleged_crime, [name], data_Complex_df)
        table_complex = pd.merge(table_complex, data_victim_of_alleged_crime, how = 'left', left_on = 'ID_data_complex', right_on = 'Victim of alleged crime')
        table_complex = table_complex.drop('Victim of alleged crime', axis = 1)
        path.pop()

    table_complex = table_complex.drop('ID_setup_complex', axis = 1)
    table_complex = table_complex.rename(columns = {'ID_data_complex':'Victim of alleged crime', 'Identifier':'Victim of alleged crime Identifier'})

    # start to build simplex table
    table_simplex = table_complex

    data_Simplex_temp = pd.merge(data_Simplex, data_SimplexText, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    xref_sc_value = pd.merge(data_xref_Simplex_Complex, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

    # Age
    data_Simplex_temp1 = pd.merge(data_Simplex_df, data_SimplexText_df, how = 'right', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp1 = data_Simplex_temp1.dropna(subset = ['Value'])
    data_Simplex_temp2 = pd.merge(data_Simplex_df, data_SimplexNumber_df, how = 'right', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp2 = data_Simplex_temp2.dropna(subset = ['Value'])
    data_Simplex_temp = pd.concat([data_Simplex_temp1, data_Simplex_temp2])
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'Value']]
    data_Simplex_temp = pd.merge(data_Simplex_df, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    xref_sc_value = pd.merge(data_xref_Simplex_Complex_df, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

    complex_name = 'Age'
    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)

    for i in range(2):
        simplex_name = simplex_names[0][i]
        simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Residence
    complex_name = 'Residence'

    simplex_id = find_setup_id_simplex(['City name', 'County', 'State'], setup_Simplex_df)
    simplex_id = simplex_id['ID_setup_simplex'].values.tolist()

    xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
    xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':'Type of territory'})

    path = ['Residence', 'Space', 'Territory', 'Type of territory']
    id_data_territory = link_data_id(path, setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
    id_data_territory = id_data_territory[id_data_territory['Residence'].notna()]
    id_data_territory = id_data_territory.drop_duplicates(subset = ['Residence'])
    data_territory = pd.merge(id_data_territory, xref_sc_value_new, how = 'left', left_on = 'Type of territory', right_on = 'Type of territory')
    data_territory = data_territory[['Residence', 'Type of territory', 'Value']]

    table_simplex = pd.merge(table_simplex, data_territory, how = 'left', left_on = complex_name, right_on = complex_name)

    table_simplex = table_simplex.rename(columns = {'Value':'Type of territory Simplex'})
    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # First name and last name
    complex_name = 'First name and last name'
    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)

    for i in range(3):
        simplex_name = simplex_names[0][i]
        simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Census linking
    complex_name = 'Census linking'

    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_names = simplex_names[0]

    for name in simplex_names:
        simplex_id = find_setup_id_simplex([name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':name, 'Value':name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Siblings
    complex_name = 'Siblings'

    # lower complex: First name and last name
    lower_complex = find_lower_complex([complex_name], setup_Complex_df, setup_xref_Complex_Complex_df)
    lower_complex = lower_complex.iat[0, 1]
    id_data_lower_complex = link_data_id([complex_name, lower_complex], setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
    data_lower_complex = find_identifier(id_data_lower_complex, [lower_complex], data_Complex_df)

    # First name and last name
    simplex_names = corresponding_name_simplex_complex([lower_complex], setup_Complex_df, setup_xref_Simplex_Complex_df)

    for i in range(3):
        simplex_name = simplex_names[0][i]
        simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':lower_complex})

        data_lower_complex = pd.merge(data_lower_complex, xref_sc_value_new, how = 'left', left_on = lower_complex, right_on = lower_complex)
        data_lower_complex = data_lower_complex.rename(columns = {'ID_data_simplex':complex_name+'\'s '+simplex_name, 'Value':complex_name+'\'s '+simplex_name+' Simplex'})
        data_lower_complex = data_lower_complex.drop('ID_setup_simplex', axis = 1)


    data_lower_complex = data_lower_complex.drop(lower_complex, axis = 1)
    data_lower_complex = data_lower_complex.drop(lower_complex+' Identifier', axis = 1)

    table_simplex = pd.merge(table_simplex, data_lower_complex, how = 'left', left_on = 'Siblings', right_on = 'Siblings')

    # simplex: Number of siblings
    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_names = simplex_names[0]

    for name in simplex_names:
        simplex_id = find_setup_id_simplex([name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':name, 'Value':name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Children
    complex_name = 'Children'

    # lower complex: First name and last name
    lower_complex = find_lower_complex([complex_name], setup_Complex_df, setup_xref_Complex_Complex_df)
    lower_complex = lower_complex.iat[0, 1]
    id_data_lower_complex = link_data_id([complex_name, lower_complex], setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
    data_lower_complex = find_identifier(id_data_lower_complex, [lower_complex], data_Complex_df)

    # First name and last name
    simplex_names = corresponding_name_simplex_complex([lower_complex], setup_Complex_df, setup_xref_Simplex_Complex_df)

    for i in range(3):
        simplex_name = simplex_names[0][i]
        simplex_id = find_setup_id_simplex([simplex_name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':lower_complex})

        data_lower_complex = pd.merge(data_lower_complex, xref_sc_value_new, how = 'left', left_on = lower_complex, right_on = lower_complex)
        data_lower_complex = data_lower_complex.rename(columns = {'ID_data_simplex':complex_name+'\'s '+simplex_name, 'Value':complex_name+'\'s '+simplex_name+' Simplex'})
        data_lower_complex = data_lower_complex.drop('ID_setup_simplex', axis = 1)


    data_lower_complex = data_lower_complex.drop(lower_complex, axis = 1)
    data_lower_complex = data_lower_complex.drop(lower_complex+' Identifier', axis = 1)

    table_simplex = pd.merge(table_simplex, data_lower_complex, how = 'left', left_on = 'Children', right_on = 'Children')

    # simplex: Number of children
    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_names = simplex_names[0]

    for name in simplex_names:
        simplex_id = find_setup_id_simplex([name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':name, 'Value':name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # Relationship to others
    complex_name = 'Relationship to others'

    # lower complex: Personal characteristics

    # simplex: Type of relationship
    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_names = simplex_names[0]

    for name in simplex_names:
        simplex_id = find_setup_id_simplex([name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':name, 'Value':name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    # simplex directly under Individual
    complex_name = 'Victim of alleged crime'

    simplex_names = corresponding_name_simplex_complex([complex_name], setup_Complex_df, setup_xref_Simplex_Complex_df)
    simplex_names = simplex_names[0]

    for name in simplex_names:
        simplex_id = find_setup_id_simplex([name], setup_Simplex_df)
        simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
        xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
        xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

        table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
        table_simplex = table_simplex.rename(columns = {'ID_data_simplex':name, 'Value':name+' Simplex'})
        table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)



    information_victim_of_alleged_crime_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv','victim of alleged crime information')
    table_simplex.to_csv(information_victim_of_alleged_crime_file_name, encoding='utf-8', index=False)

    return information_victim_of_alleged_crime_file_name


def individual_simplex_info(simplex, setup_Simplex, setup_Complex, setup_xref_Simplex_Complex, setup_xref_Complex_Complex, data_xref_Simplex_Complex, data_Simplex, data_SimplexDate, data_SimplexNumber, data_SimplexText):
    data = {'information': ['simplex name', 'frequency', 'complex name', 'higher complex', 'lower complex', 'relationship to event']}
    simplex_info = []

    # the name of simplex
    data_simplex_temp = pd.concat([data_SimplexDate, data_SimplexNumber, data_SimplexText])
    data_simplex_temp = pd.merge(data_Simplex, data_SimplexText, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_simplex_select = data_simplex_temp[data_simplex_temp['Value']==simplex]
    simplex_setup_id = data_simplex_select['ID_setup_simplex'].values.tolist()
    simplex_name = setup_Simplex[setup_Simplex['ID_setup_simplex'].isin(simplex_setup_id)]
    simplex_name = simplex_name['Name'].values.tolist()
    for name in simplex_name:
        simplex_info.append([name])

    # frequency
    temp = pd.merge(data_xref_Simplex_Complex, data_Simplex, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    ID_data_date_number_text = data_simplex_select['ID_data_date_number_text'].values.tolist()
    ID_data_date_number_text = ID_data_date_number_text[0]
    data_xref_Simplex_Complex_select = temp[temp['ID_data_date_number_text']==ID_data_date_number_text]
    for i in range(len(simplex_info)):
        simplex_setup_id = find_setup_id_simplex([simplex_info[i][0]], setup_Simplex)
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
        complex_name = find_parent_simplex_util([simplex_name], setup_Simplex, setup_xref_Simplex_Complex, setup_Complex)
        if len(complex_name) != 0:
            # highercomplex
            higher_complex = find_higher_complex(complex_name, setup_Complex, setup_xref_Complex_Complex)
            higher_complex = higher_complex['Name'].values.tolist()
            # lowercomplex
            lower_complex = find_lower_complex(complex_name, setup_Complex, setup_xref_Complex_Complex)
            lower_complex = lower_complex['Name'].values.tolist()
            # relationship to event
            path = find_path('Event', complex_name[0], setup_Complex, setup_xref_Complex_Complex)
            # format
            complex_name_table = ', '.join(complex_name)
            higher_complex_table = ', '.join(higher_complex)
            lower_complex_table = ', '.join(lower_complex)
            path_table = ', '.join(path)
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

    return df


def individual_simplex_info_main(simplex, inputDir, outputDir):
    df = []

    setup_Complex=os.path.join(inputDir,'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.xlsx')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df = pd.DataFrame(pd.read_excel(setup_Simplex))
        setup_Simplex_df = setup_Simplex_df.rename(columns = {'ID':'ID_setup_simplex'})

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex-Complex.xlsx')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Complex_Complex))
        setup_xref_Complex_Complex_df = setup_xref_Complex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex'})

    setup_xref_Simplex_Complex=os.path.join(inputDir,'setup_xref_Simplex-Complex.xlsx')
    if os.path.isfile(setup_xref_Simplex_Complex):
        setup_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(setup_xref_Simplex_Complex))
        setup_xref_Simplex_Complex_df = setup_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_setup_xref_complex-complex', 'Complex':'ID_setup_complex', 'Simplex':'ID_setup_simplex'})

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex-Complex.xlsx')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Complex_Complex))
        data_xref_Complex_Complex_df = data_xref_Complex_Complex_df.rename(columns = {'ID':'ID_data_xref_complex-complex', 'HigherComplex':'ID_data_complex', 'xrefID':'ID_setup_xref_complex_complex', 'LowerComplex':'ID_data_complex.1'})

    data_Complex=os.path.join(inputDir,'data_Complex.xlsx')
    if os.path.isfile(data_Complex):
        data_Complex_df = pd.DataFrame(pd.read_excel(data_Complex))
        data_Complex_df = data_Complex_df.rename(columns = {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"})

    data_Simplex=os.path.join(inputDir,'data_Simplex.xlsx')
    if os.path.isfile(data_Simplex):
        data_Simplex_df = pd.DataFrame(pd.read_excel(data_Simplex))
        data_Simplex_df = data_Simplex_df.rename(columns = {"ID":"ID_data_simplex", "SimplexType":"ID_setup_simplex", "refValue":"ID_data_date_number_text"})

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.xlsx')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df = pd.DataFrame(pd.read_excel(data_SimplexText))

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex-Complex.xlsx')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.DataFrame(pd.read_excel(data_xref_Simplex_Complex))
        data_xref_Simplex_Complex_df = data_xref_Simplex_Complex_df.rename(columns = {'ID':'ID_data_xref_simplex-complex', 'xrefID':'ID_setup_xref_simplex_complex', 'Simplex':'ID_data_simplex', 'Complex':'ID_data_complex'})

    data_SimplexNumber = os.path.join(inputDir, 'data_SimplexNumber.xlsx')
    if os.path.isfile(data_SimplexNumber):
        data_SimplexNumber_df = pd.DataFrame(pd.read_excel(data_SimplexNumber))

    data_SimplexDate=os.path.join(inputDir,'data_SimplexDate.xlsx')
    if os.path.isfile(data_SimplexDate):
        data_SimplexDate_df=pd.DataFrame(pd.read_excel(data_SimplexDate))

    if isinstance(simplex, str):
        df = individual_simplex_info(simplex, setup_Simplex_df, setup_Complex_df, setup_xref_Simplex_Complex_df, setup_xref_Complex_Complex_df, data_xref_Simplex_Complex_df, data_Simplex_df, data_SimplexDate_df, data_SimplexNumber_df, data_SimplexText_df)

    individual_simplex_info_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'individual simplex information')
    df.to_csv(individual_simplex_info_file_name, encoding='utf-8', index=False)

    return individual_simplex_info_file_name





def build_macro_event_dropdown_menu(inputDir):
    downdown_menu_list = []
    has_files = True

    setup_Complex=os.path.join(inputDir,'setup_Complex.xlsx')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.DataFrame(pd.read_excel(setup_Complex))
        setup_Complex_df = setup_Complex_df.rename(columns = {'ID':'ID_setup_complex'})
    else:
        has_files = False

    data_Complex=os.path.join(inputDir,'data_Complex.xlsx')
    if os.path.isfile(data_Complex):
        data_Complex_df = pd.DataFrame(pd.read_excel(data_Complex))
        data_Complex_df = data_Complex_df.rename(columns = {"ID":"ID_data_complex", "ComplexType":"ID_setup_complex"})
    else:
        has_files = False

    if(has_files):
        macro_event_name_id = find_setup_id(["Macro Event"], setup_Complex_df)
        macro_event_name_id = macro_event_name_id.iloc[0,0]

        macro_event_identifier = data_Complex_df[data_Complex_df['ID_setup_complex'] == macro_event_name_id]

        downdown_menu_list = macro_event_identifier.apply(lambda x: f"{x['ID_data_complex']} - {x['Identifier']}", axis=1).tolist()

    return downdown_menu_list
