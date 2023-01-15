
import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_packages(GUI_util.window, "DB_PC-ACE_data_analyzer_main.py", ['os', 'tkinter','pandas','numpy'])==False:
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
        # Only include .csv files from the input dir
        if (file.startswith('data_') or file.startswith('setup_')) and (file.endswith('.csv')):
            # Strip off the .csv extension
            # tableList.append(file[:len(file) - 4])
            if not file in str(tableList):
                if file=='data_Complex.csv':
                    print('')
                print(file)
                tableList.append(file)
    # if len(tableList) == 0:
    #     mb.showwarning(title='Warning',
    #                    message='There are no csv files in the input directory.\n\nThe script expects a set of csv files with overlapping ID fields across files in order to construct an SQLite relational database.\n\nPlease, select an input directory that contains 18 csv PC-ACE tables and try again.')
    if not "data_Document.csv" in str(tableList) and not "data_Complex.csv" in str(tableList):
        # mb.showwarning(title='Warning',
        #                message='Although the input directory does contain csv files, these files do not have the expected PC-ACE filename (e.g., data_Document, data_Complex).\n\nPlease, select an input directory that contains csv PC-ACE tables and try again.')
        tableList=[]
    return tableList


# give the list for all table names (e.g., simplex, complex)
# parameter: dataframe of setup_Complex or filename with path
# return: the list of all table names
def get_all_table_names(setup_Name):
    list_setup_Name = []
    if type(setup_Name) == str:
        if os.path.isfile(setup_Name):
            setup_Name = pd.read_csv(setup_Name)
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
            setup_Simplex = pd.read_csv(setup_Simplex)
            simplex_name = setup_Simplex[['Name']]
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
            setup_Complex = pd.read_csv(setup_Complex)
            complex_name = setup_Complex[['Name']]
            complex_name = complex_name[complex_name['Name'].notna()]
            list_complex_name = complex_name['Name'].values.tolist()
            list_complex_name.sort()
    return list_complex_name


# give data for the input simplex name
# parameter: name: simplex name in list type
# return: dataframe: name, value, frequency
def get_simplex_frequencies(name, inputDir, outputDir):
    setup_Simplex = os.path.join(inputDir, 'setup_Simplex.csv')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df = pd.read_csv(setup_Simplex)

    setup_xref_Simplex_Complex = os.path.join(inputDir, 'setup_xref_Simplex_Complex.csv')
    if os.path.isfile(setup_xref_Simplex_Complex):
        setup_xref_Simplex_Complex_df = pd.read_csv(setup_xref_Simplex_Complex)

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex_Complex.csv')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.read_csv(data_xref_Simplex_Complex)

    data_Simplex = os.path.join(inputDir, 'data_Simplex.csv')
    if os.path.isfile(data_Simplex):
        data_Simplex_df = pd.read_csv(data_Simplex)

    data_SimplexText = os.path.join(inputDir, 'data_SimplexText.csv')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df = pd.read_csv(data_SimplexText)

    simplex_id = find_setup_id_simplex(name, setup_Simplex_df)
    id = simplex_id.iat[0,0]
    name = simplex_id.iat[0,1]

    temp = pd.merge(data_xref_Simplex_Complex_df, data_Simplex_df, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    select = temp[temp['ID_setup_simplex']==id]
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
# parameter: name of an complex in list type, dataframe of setup_Complex
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

    setup_Complex = os.path.join(inputDir, 'setup_Complex.csv')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.read_csv(setup_Complex)
    else:
        has_files = False

    setup_xref_Complex_Complex = os.path.join(inputDir, 'setup_xref_Complex_Complex.csv')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df = pd.read_csv(setup_xref_Complex_Complex)
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
    lower_level_complex = []
    has_files = True

    if isinstance(complex, str):
        complex = [complex]

    setup_Complex = os.path.join(inputDir, 'setup_Complex.csv')
    if os.path.isfile(setup_Complex):
        setup_Complex_df = pd.read_csv(setup_Complex)
    else:
        has_files = False

    setup_xref_Complex_Complex = os.path.join(inputDir, 'setup_xref_Complex_Complex.csv')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df = pd.read_csv(setup_xref_Complex_Complex)
    else:
        has_files = False

    if(has_files):
        complex_id = find_setup_id(complex, setup_Complex_df)
        complex_id = complex_id['ID_setup_complex'].values.tolist()

        higher_level_complex = setup_xref_Complex_Complex_df[setup_xref_Complex_Complex_df['LowerComplex'].isin(complex_id)]
        higher_level_complex = higher_level_complex['HigherComplex'].values.tolist()
        higher_level_complex = [str(x) for x in higher_level_complex]

        higher_level_complex = setup_Complex_df[setup_Complex_df['ID_setup_complex'].isin(higher_level_complex)]
        higher_level_complex = higher_level_complex[['ID_setup_complex', 'Name']]
        higher_level_complex = higher_level_complex.rename(columns={'ID_setup_complex': 'HigherComplex', 'Name': 'Name'})

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


# build semantic triplet with identifiers
# return:
#        dataframe: Semantic Triplet: Semantic Triplet data id,
#                   S: Participant-S data id
#                   S Identifier: Participant-S Identifier
#                   V: Process data id
#                   V Identifier: Process Identifier
#                   O: Participant-O data id
#                   O Identifier: Participant-O Identifier
def semantic_triplet_complex(setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex, data_Complex):
    id = find_setup_id(['Semantic Triplet'], setup_Complex).iat[0, 0]

    save = setup_xref_Complex_Complex[setup_xref_Complex_Complex['HigherComplex'] == id]
    save = save['ID_setup_xref_complex-complex'].values.tolist()
    save = save[:3]

    triplet = data_xref_Complex_Complex[data_xref_Complex_Complex['ID_setup_xref_complex_complex'].isin(save)]
    triplet = triplet.pivot_table(
        index=['ID_data_complex'],
        columns='ID_setup_xref_complex_complex',
        values='ID_data_complex.1'
    ).reset_index()
    # TODO Anna: ID_data_complex is renamed to Semantic Triplet but then it is used a few lines down
    triplet = triplet.rename(columns={'ID_data_complex': 'Semantic Triplet', 63: 'S', 64: 'V', 65: 'O'})

    complexes = ['S', 'V', 'O']

    for i in range(3):
        complex = complexes[i]
        # TODO Anna: ID_data_complex has been renamed to Semantic Triplet above
        triplet = pd.merge(triplet, data_Complex, how='left', left_on=complex, right_on='ID_data_complex')
        # TODO Anna: Identifier is not an item retrieved above
        pop = triplet.pop('Identifier')
        name = complex + ' Identifier'
        triplet.insert((i + 1) * 2, name, pop)
        # TODO Anna: ID_data_complex has been renamed to Semantic Triplet above
        triplet = triplet.drop('ID_data_complex', axis=1)
        # TODO Anna: ID_data_complex has been renamed to Semantic Triplet above
        triplet = triplet.drop('ID_setup_complex', axis=1)

    return triplet


# give simplex of process
# return:
#        dataframe:
#                  Process: Process data id
#                  Simplex process: Simple process data id
#                  Value: simplex in the format of "simplex1", "simplex2", ...
def process_simplex(data_Simplex, data_SimplexText, data_xref_Simplex_Complex, setup_Complex,
                    setup_xref_Complex_Complex, data_xref_Complex_Complex):
    data_Simplex_temp = pd.merge(data_Simplex, data_SimplexText, how='left', left_on='ID_data_date_number_text',
                                 right_on='ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]
    xref_sc_value = pd.merge(data_xref_Simplex_Complex, data_Simplex_temp, how='left', left_on='ID_data_simplex',
                             right_on='ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_data_simplex', 'Value']]

    path = ['Process', 'Simple process']
    id_data_simple_process_oneLevel = link_data_id(path, setup_Complex, setup_xref_Complex_Complex,
                                                   data_xref_Complex_Complex)
    data_simple_process_oneLevel = pd.merge(id_data_simple_process_oneLevel, xref_sc_value, how='left',
                                            left_on='Simple process', right_on='ID_data_complex')
    data_simple_process_oneLevel_new = data_simple_process_oneLevel.groupby(['Process'])['Value'].apply(list).to_frame()
    data_simple_process_oneLevel_new['Value'] = data_simple_process_oneLevel_new['Value'].apply(
        lambda x: str(x).replace('[', '').replace(']', ''))
    data_oneLevel = pd.merge(id_data_simple_process_oneLevel, data_simple_process_oneLevel_new, how='left',
                             left_on='Process', right_on='Process')

    path = ['Process', 'Complex process', 'Simple process']
    id_data_simple_process_twoLevel = link_data_id(path, setup_Complex, setup_xref_Complex_Complex,
                                                   data_xref_Complex_Complex)
    data_simple_process_twoLevel = pd.merge(id_data_simple_process_twoLevel, xref_sc_value, how='left',
                                            left_on='Simple process', right_on='ID_data_complex')
    data_simple_process_twoLevel_new = data_simple_process_twoLevel.groupby(['Process'])['Value'].apply(list).to_frame()
    data_simple_process_twoLevel_new['Value'] = data_simple_process_twoLevel_new['Value'].apply(
        lambda x: str(x).replace('[', '').replace(']', ''))
    data_twoLevel = pd.merge(id_data_simple_process_twoLevel, data_simple_process_twoLevel_new, how='left',
                             left_on='Process', right_on='Process')

    data_process_simplex = pd.concat([data_oneLevel, data_twoLevel])

    return data_process_simplex


# give simplex of participant-s
# parameter: participant: select between "Participant-S" and "Participant-O"
# return: dataframe:
#                   Participant-X: Participant-X data id (determined by the input of participant parameter)
#                   Individual Simplex: simplex of Individual in the format of "simplex1", "simplex2", ...
#                   Collective actor Simplex: simplex of Collective actor in the format of "simplex1", "simplex2", ...
#                   Organization Simplex: simplex of Orgaization in the format of "simplex1", "simplex2", ...
def participant_simplex(participant, data_Simplex, data_SimplexText, setup_Complex, data_Complex,
                        data_xref_Simplex_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex):
    simplex = []

    lowers = find_lower_complex(['Actor'], setup_Complex, setup_xref_Complex_Complex)
    lowers = lowers['Name'].values.tolist()

    for lower in lowers:
        temp = find_simplex_identifier_one_complextype([lower], data_Simplex, data_SimplexText, setup_Complex,
                                                       data_Complex, data_xref_Simplex_Complex)
        temp = temp.drop(lower + ' Identifier', axis=1)

        path = find_path(participant, lower, setup_Complex, setup_xref_Complex_Complex)
        data = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
        data = data[data[participant].notna()]
        data = pd.merge(data, temp, how='left', left_on=lower, right_on=lower)

        data_new = data.groupby([participant])[lower + ' Simplex'].apply(list).to_frame()
        data_new[lower + ' Simplex'] = data_new[lower + ' Simplex'].apply(
            lambda x: str(x).replace('[', '').replace(']', ''))

        simplex.append(data_new)

    data_s_simplex = pd.merge(simplex[0], simplex[1], how='outer', left_on=participant, right_on=participant)
    data_s_simplex = pd.merge(data_s_simplex, simplex[2], how='outer', left_on=participant, right_on=participant)

    return data_s_simplex


# give simplex of each component in semantic triplet
# return: dataframe:
#         Semantic Triplet: data id
#         S: Participant-S data id
#         S Individual, S Collective actor, S Organization: Participant-S simplex data
#         V: Process data id
#         Process: Process simplex data
#         O: Participant-O data id
#         O Individual, O Collective actor, O Organization: Participant-O simplex data
def semantic_triplet_simplex(setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex, data_Complex,
                             data_Simplex, data_SimplexText, data_xref_Simplex_Complex):
    triplet = semantic_triplet_complex(setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex,
                                       data_Complex)
    s = participant_simplex('Participant-S', data_Simplex, data_SimplexText, setup_Complex, data_Complex,
                            data_xref_Simplex_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    s = s.rename(columns={'Individual Simplex': 'S Individual', 'Collective actor Simplex': 'S Collective actor',
                          'Organization Simplex': 'S Organization'})
    v = process_simplex(data_Simplex, data_SimplexText, data_xref_Simplex_Complex, setup_Complex,
                        setup_xref_Complex_Complex, data_xref_Complex_Complex)
    o = participant_simplex('Participant-O', data_Simplex, data_SimplexText, setup_Complex, data_Complex,
                            data_xref_Simplex_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    o = o.rename(columns={'Individual Simplex': 'O Individual', 'Collective actor Simplex': 'O Collective actor',
                          'Organization Simplex': 'O Organization'})

    simplex_version = pd.merge(triplet, s, how='left', left_on='S', right_on='Participant-S')
    simplex_version = pd.merge(simplex_version, v, how='left', left_on='V', right_on='Process')
    simplex_version = pd.merge(simplex_version, o, how='left', left_on='O', right_on='Participant-O')
    simplex_version = simplex_version.loc[:,
                      ['Semantic Triplet', 'S', 'S Individual', 'S Collective actor', 'S Organization', 'V', 'Value',
                       'O', 'O Individual', 'O Collective actor', 'O Organization']]
    simplex_version = simplex_version.rename(columns={'Value': 'Process'})

    return simplex_version


# give time or space identifer for corresponding process
# parameter: environment: select between Time and Space
# return: dataframe:
#                   ID_data_complex: Process data id
#                   Identifier: Process Identifier
#                   X: X data id, determined by the input of environment
#                   X Identifier: X Identifier, determined by the input of environment
def find_environment(environment, setup_Complex, data_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex):
    id_complex = find_setup_id(['Process'], setup_Complex).iat[0, 0]
    table = data_Complex[data_Complex['ID_setup_complex'].isin([id_complex])]
    table = table.drop('ID_setup_complex', axis=1)

    path = ['Process', 'Simple process', 'Circumstances', environment]
    id_data_time = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    data_time = find_identifier(id_data_time, [environment], data_Complex)
    table1 = pd.merge(table, data_time, how='left', left_on='ID_data_complex', right_on='Process')
    table1 = table1.drop('Process', axis=1)

    path = ['Process', 'Complex process', 'Simple process', 'Circumstances', environment]
    id_data_time = link_data_id(path, setup_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    data_time = find_identifier(id_data_time, [environment], data_Complex)
    table2 = pd.merge(table, data_time, how='left', left_on='ID_data_complex', right_on='Process')
    table2 = table2.drop('Process', axis=1)

    table1[environment] = table1[environment].fillna(0)
    table1[environment + ' Identifier'] = table1[environment + ' Identifier'].fillna('')
    table2[environment] = table2[environment].fillna(0)
    table2[environment + ' Identifier'] = table2[environment + ' Identifier'].fillna('')

    result = pd.merge(table1, table2, how='outer', left_on='ID_data_complex', right_on='ID_data_complex')
    result = result.drop('Identifier_y', axis=1)
    result = result.rename(columns={'Identifier_x': 'Identifier'})

    result[environment] = result[environment + '_x'] + result[environment + '_y']
    result[environment + ' Identifier'] = result[environment + ' Identifier_x'] + result[environment + ' Identifier_y']
    result = result[['ID_data_complex', 'Identifier', environment, environment + ' Identifier']]

    return result


# merge environment with semantic triplet
# note: suppose the input triplet has the data id of process
def semantic_triplet_time(triplet, setup_Complex, data_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex):
    time = find_environment('Time', setup_Complex, data_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex)
    triplet_with_time = pd.merge(triplet, time, how='left', left_on='V', right_on='ID_data_complex')
    triplet_with_time = triplet_with_time.drop('ID_data_complex', axis=1)
    triplet_with_time = triplet_with_time.drop('Identifier', axis=1)
    return triplet_with_time


def semantic_triplet_space(triplet, setup_Complex, data_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex):
    space = find_environment('Space', setup_Complex, data_Complex, setup_xref_Complex_Complex,
                             data_xref_Complex_Complex)
    triplet_with_space = pd.merge(triplet, space, how='left', left_on='V', right_on='ID_data_complex')
    triplet_with_space = triplet_with_space.drop('ID_data_complex', axis=1)
    triplet_with_space = triplet_with_space.drop('Identifier', axis=1)
    return triplet_with_space


def semantic_triplet_time_space(triplet, setup_Complex, data_Complex, setup_xref_Complex_Complex,
                                data_xref_Complex_Complex):
    triplet_with_time = semantic_triplet_time(triplet, setup_Complex, data_Complex, setup_xref_Complex_Complex,
                                              data_xref_Complex_Complex)
    space = find_environment('Space', setup_Complex, data_Complex, setup_xref_Complex_Complex,
                             data_xref_Complex_Complex)
    triplet_with_time_space = pd.merge(triplet_with_time, space, how='left', left_on='V', right_on='ID_data_complex')
    triplet_with_time_space = triplet_with_time_space.drop('ID_data_complex', axis=1)
    triplet_with_time_space = triplet_with_time_space.drop('Identifier', axis=1)
    return triplet_with_time_space


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
def find_simplex_identifier_one_complextype(complex_name, data_Simplex, data_SimplexText, setup_Complex, data_Complex,
                                            data_xref_Simplex_Complex):
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
def semantic_triplet_simplex(inputDir, outputDir):
    setup_Complex=os.path.join(inputDir,'setup_Complex.csv')
    if os.path.isfile(setup_Complex):
        setup_Complex_df=pd.read_csv(setup_Complex)

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.csv')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df=pd.read_csv(setup_Simplex)

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex_Complex.csv')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df=pd.read_csv(setup_xref_Complex_Complex)

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex_Complex.csv')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df=pd.read_csv(data_xref_Complex_Complex)

    data_Complex=os.path.join(inputDir,'data_Complex.csv')
    if os.path.isfile(data_Complex):
        data_Complex_df=pd.read_csv(data_Complex)

    data_Simplex=os.path.join(inputDir,'data_Simplex.csv')
    if os.path.isfile(data_Simplex):
        data_Simplex_df=pd.read_csv(data_Simplex)

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.csv')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df=pd.read_csv(data_SimplexText)

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex_Complex.csv')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.read_csv(data_xref_Simplex_Complex)

    triplet = semantic_triplet_complex(setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_Complex_df)
    s = participant_simplex('Participant-S', data_Simplex_df, data_SimplexText_df, setup_Complex_df, setup_Simplex_df, data_Complex_df, data_xref_Simplex_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
    s = s.rename(columns = {'Value':'Subject (S)', 'Type':'S Type'})
    v = process_simplex(setup_Simplex_df, data_Simplex_df, data_SimplexText_df, data_xref_Simplex_Complex_df, setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
    o = participant_simplex('Participant-O', data_Simplex_df, data_SimplexText_df, setup_Complex_df, setup_Simplex_df, data_Complex_df, data_xref_Simplex_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
    o = o.rename(columns = {'Value':'Object (O)', 'Type':'O Type'})

    simplex_version = pd.merge(triplet, s, how = 'left', left_on = 'S', right_on = 'Participant-S')
    simplex_version = pd.merge(simplex_version, v, how = 'left', left_on = 'V', right_on = 'Process')
    simplex_version = pd.merge(simplex_version, o, how = 'left', left_on = 'O', right_on = 'Participant-O')
    simplex_version = simplex_version.loc[:, ['Semantic Triplet', 'S', 'S Type', 'Subject (S)', 'V', 'Value', 'O', 'O Type', 'Object (O)']]
    simplex_version = simplex_version.rename(columns = {'Value':'Verb (V)'})

    triplet_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'triplet (SVO)')
    simplex_version.to_csv(triplet_file_name, encoding='utf-8', index=False)

    return triplet_file_name


# helper method for semantic_triplet_time
# link simplex of time complex with V
# return: a dataframe: Process = data id of complex Process, Indefinite time of day = data id of simplex Indefinite time of day, Time = text of Indefinite time of day
def find_time_simplex(setup_Simplex, data_Simplex, data_SimplexText, setup_Complex, data_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex):
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
def semantic_triplet_time(inputDir, outputDir):
    setup_Complex=os.path.join(inputDir,'setup_Complex.csv')
    if os.path.isfile(setup_Complex):
        setup_Complex_df=pd.read_csv(setup_Complex)

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.csv')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df=pd.read_csv(setup_Simplex)

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex_Complex.csv')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df=pd.read_csv(setup_xref_Complex_Complex)

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex_Complex.csv')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df=pd.read_csv(data_xref_Complex_Complex)

    data_Complex=os.path.join(inputDir,'data_Complex.csv')
    if os.path.isfile(data_Complex):
        data_Complex_df=pd.read_csv(data_Complex)

    data_Simplex=os.path.join(inputDir,'data_Simplex.csv')
    if os.path.isfile(data_Simplex):
        data_Simplex_df=pd.read_csv(data_Simplex)

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.csv')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df=pd.read_csv(data_SimplexText)

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex_Complex.csv')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.read_csv(data_xref_Simplex_Complex)

    triplet = semantic_triplet_simplex(setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_Complex_df, data_Simplex_df, data_SimplexText_df, data_xref_Simplex_Complex_df)
    time = find_time_simplex(setup_Simplex_df, data_Simplex_df, data_SimplexText_df, setup_Complex_df, data_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)

    triplet_with_time = pd.merge(triplet, time, how = 'left', left_on = 'V', right_on = 'Process')
    triplet_with_time = triplet_with_time.drop('Process', axis = 1)
    triplet_with_time = triplet_with_time.rename(columns = {'Indefinite time of day':'Time', 'Time':'Time Simplex'})

    triplet_with_time_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'triplet (SVO) with time')
    triplet_with_time.to_csv(triplet_with_time_file_name, encoding='utf-8', index=False)

    return triplet_with_time_file_name


# helper method for semantic_triplet_space
# link simplex of space complex with V
# return: a dataframe: Process = data id of complex Process, Type of territory = data id of simplex Type of territory, Space = text of Type of territory
def find_space_simplex(setup_Simplex, data_Simplex, data_SimplexText, setup_Complex, data_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex):
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
def find_space_simplex_event(setup_Simplex, data_Simplex, data_SimplexText, setup_Complex, data_Complex, setup_xref_Complex_Complex, data_xref_Complex_Complex):
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
def semantic_triplet_space(inputDir, outputDir):
    setup_Complex=os.path.join(inputDir,'setup_Complex.csv')
    if os.path.isfile(setup_Complex):
        setup_Complex_df=pd.read_csv(setup_Complex)

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.csv')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df=pd.read_csv(setup_Simplex)

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex_Complex.csv')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df=pd.read_csv(setup_xref_Complex_Complex)

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex_Complex.csv')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df=pd.read_csv(data_xref_Complex_Complex)

    data_Complex=os.path.join(inputDir,'data_Complex.csv')
    if os.path.isfile(data_Complex):
        data_Complex_df=pd.read_csv(data_Complex)

    data_Simplex=os.path.join(inputDir,'data_Simplex.csv')
    if os.path.isfile(data_Simplex):
        data_Simplex_df=pd.read_csv(data_Simplex)

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.csv')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df=pd.read_csv(data_SimplexText)

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex_Complex.csv')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.read_csv(data_xref_Simplex_Complex)

    triplet = semantic_triplet_simplex(setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_Complex_df, data_Simplex_df, data_SimplexText_df, data_xref_Simplex_Complex_df)

    space1 = find_space_simplex(setup_Simplex_df, data_Simplex_df, data_SimplexText_df, setup_Complex_df, data_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
    triplet_with_space1 = pd.merge(triplet, space1, how = 'left', left_on = 'V', right_on = 'Process')
    triplet_with_space1 = triplet_with_space1.drop('Process', axis = 1)
    triplet_with_space1 = triplet_with_space1.rename(columns = {'Type of territory':'Space', 'Space':'Space Simplex'})
    triplet_with_space1 = triplet_with_space1[['V', 'Space', 'Space Simplex']]
    triplet_with_space1 = triplet_with_space1.dropna(subset = ['Space'])

    space2 = find_space_simplex_event(setup_Simplex_df, data_Simplex_df, data_SimplexText_df, setup_Complex_df, data_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
    triplet_with_space2 = pd.merge(triplet, space2, how = 'left', left_on = 'Semantic Triplet', right_on = 'Semantic Triplet')
    triplet_with_space2 = triplet_with_space2.rename(columns = {'Type of territory':'Space', 'Space':'Space Simplex'})
    triplet_with_space2 = triplet_with_space2[['V', 'Space', 'Space Simplex']]
    triplet_with_space2 = triplet_with_space2.dropna(subset = ['Space'])

    triplet_with_space = pd.concat([triplet_with_space1, triplet_with_space2])
    triplet_with_space = pd.merge(triplet, triplet_with_space, how = 'left', left_on = 'V', right_on = 'V')

    triplet_with_space_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'triplet (SVO) with space')
    triplet_with_space.to_csv(triplet_with_space_file_name, encoding='utf-8', index=False)

    return triplet_with_space_file_name

# give semantic triplet with time and space
def semantic_triplet_time_space(inputDir, outputDir):
    setup_Complex=os.path.join(inputDir,'setup_Complex.csv')
    if os.path.isfile(setup_Complex):
        setup_Complex_df=pd.read_csv(setup_Complex)

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.csv')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df=pd.read_csv(setup_Simplex)

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex_Complex.csv')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df=pd.read_csv(setup_xref_Complex_Complex)

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex_Complex.csv')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df=pd.read_csv(data_xref_Complex_Complex)

    data_Complex=os.path.join(inputDir,'data_Complex.csv')
    if os.path.isfile(data_Complex):
        data_Complex_df=pd.read_csv(data_Complex)

    data_Simplex=os.path.join(inputDir,'data_Simplex.csv')
    if os.path.isfile(data_Simplex):
        data_Simplex_df=pd.read_csv(data_Simplex)

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.csv')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df=pd.read_csv(data_SimplexText)

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex_Complex.csv')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.read_csv(data_xref_Simplex_Complex)

    triplet = semantic_triplet_simplex(setup_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df, data_Complex_df, data_Simplex_df, data_SimplexText_df, data_xref_Simplex_Complex_df)

    triplet_with_space = semantic_triplet_space(setup_Simplex_df, data_Simplex_df, data_SimplexText_df, setup_Complex_df, data_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
    time = find_time_simplex(setup_Simplex_df, data_Simplex_df, data_SimplexText_df, setup_Complex_df, data_Complex_df, setup_xref_Complex_Complex_df, data_xref_Complex_Complex_df)
    triplet_with_time_space = pd.merge(triplet_with_space, time, how = 'left', left_on = 'V', right_on = 'Process')
    triplet_with_time_space = triplet_with_time_space.drop('Process', axis = 1)
    triplet_with_time_space = triplet_with_time_space.rename(columns = {'Indefinite time of day':'Time', 'Time':'Time Simplex'})

    triplet_with_space_time_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'triplet (SVO) with space and time')
    triplet_with_time_space.to_csv(triplet_with_space_time_file_name, encoding='utf-8', index=False)
    return triplet_with_space_time_file_name

# give indivudal characteristics
def individual_characteristics(inputDir, outputDir):
    setup_Complex=os.path.join(inputDir,'setup_Complex.csv')
    if os.path.isfile(setup_Complex):
        setup_Complex_df=pd.read_csv(setup_Complex)

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.csv')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df=pd.read_csv(setup_Simplex)

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex_Complex.csv')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df=pd.read_csv(setup_xref_Complex_Complex)

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex_Complex.csv')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df=pd.read_csv(data_xref_Complex_Complex)

    data_Complex=os.path.join(inputDir,'data_Complex.csv')
    if os.path.isfile(data_Complex):
        data_Complex_df=pd.read_csv(data_Complex)

    data_Simplex=os.path.join(inputDir,'data_Simplex.csv')
    if os.path.isfile(data_Simplex):
        data_Simplex_df=pd.read_csv(data_Simplex)

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.csv')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df=pd.read_csv(data_SimplexText)

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex_Complex.csv')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.read_csv(data_xref_Simplex_Complex)

    setup_xref_Simplex_Complex = os.path.join(inputDir, 'setup_xref_Simplex_Complex.csv')
    if os.path.isfile(setup_xref_Simplex_Complex):
        setup_xref_Simplex_Complex_df = pd.read_csv(setup_xref_Simplex_Complex)

    data_SimplexNumber = os.path.join(inputDir, 'data_SimplexNumber.csv')
    if os.path.isfile(data_SimplexNumber):
        data_SimplexNumber_df = pd.read_csv(data_SimplexNumber)

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
      simplex_id = find_setup_id_simplex([simplex_name], setup_xref_Simplex_Complex)
      simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
      xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
      xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

      table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
      table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
      table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    individual_characteristics_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'individual characteristics')
    table_simplex.to_csv(individual_characteristics_file_name, encoding='utf-8', index=False)

    return individual_characteristics_file_name

# give collective actor characteristics
def collective_actor_characteristics(inputDir, outputDir):
    setup_Complex=os.path.join(inputDir,'setup_Complex.csv')
    if os.path.isfile(setup_Complex):
        setup_Complex_df=pd.read_csv(setup_Complex)

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.csv')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df=pd.read_csv(setup_Simplex)

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex_Complex.csv')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df=pd.read_csv(setup_xref_Complex_Complex)

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex_Complex.csv')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df=pd.read_csv(data_xref_Complex_Complex)

    data_Complex=os.path.join(inputDir,'data_Complex.csv')
    if os.path.isfile(data_Complex):
        data_Complex_df=pd.read_csv(data_Complex)

    data_Simplex=os.path.join(inputDir,'data_Simplex.csv')
    if os.path.isfile(data_Simplex):
        data_Simplex_df=pd.read_csv(data_Simplex)

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.csv')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df=pd.read_csv(data_SimplexText)

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex_Complex.csv')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.read_csv(data_xref_Simplex_Complex)

    setup_xref_Simplex_Complex = os.path.join(inputDir, 'setup_xref_Simplex_Complex.csv')
    if os.path.isfile(setup_xref_Simplex_Complex):
        setup_xref_Simplex_Complex_df = pd.read_csv(setup_xref_Simplex_Complex)

    data_SimplexNumber = os.path.join(inputDir, 'data_SimplexNumber.csv')
    if os.path.isfile(data_SimplexNumber):
        data_SimplexNumber_df = pd.read_csv(data_SimplexNumber)

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
    complex_name = 'Part qualifier'

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
    data_Simplex_temp2 = pd.merge(data_Simplex_df, data_SimplexNumber_df, how = 'right', left_on = 'ID_data_date_number_text', right_on = 'ID_data_date_number_text')
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
      simplex_id = find_setup_id_simplex([simplex_name], setup_xref_Simplex_Complex)
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
      simplex_id = find_setup_id_simplex([simplex_name], setup_xref_Simplex_Complex)
      simplex_id = simplex_id['ID_setup_simplex'].values.tolist()
      xref_sc_value_new = xref_sc_value[xref_sc_value['ID_setup_simplex'].isin(simplex_id)]
      xref_sc_value_new = xref_sc_value_new.rename(columns = {'ID_data_complex':complex_name})

      table_simplex = pd.merge(table_simplex, xref_sc_value_new, how = 'left', left_on = complex_name, right_on = complex_name)
      table_simplex = table_simplex.rename(columns = {'ID_data_simplex':simplex_name, 'Value':simplex_name+' Simplex'})
      table_simplex = table_simplex.drop('ID_setup_simplex', axis = 1)

    table_simplex = table_simplex.drop(complex_name, axis = 1)
    table_simplex = table_simplex.drop(complex_name+' Identifier', axis = 1)

    collective_actor_characteristics_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                       'collective actor characteristics')
    table_simplex.to_csv(collective_actor_characteristics_file_name, encoding='utf-8', index=False)

    return collective_actor_characteristics_file_name

# give features of institutions
def institution_features(inputDir, outputDir):
    setup_Complex=os.path.join(inputDir,'setup_Complex.csv')
    if os.path.isfile(setup_Complex):
        setup_Complex_df=pd.read_csv(setup_Complex)

    setup_Simplex=os.path.join(inputDir,'setup_Simplex.csv')
    if os.path.isfile(setup_Simplex):
        setup_Simplex_df=pd.read_csv(setup_Simplex)

    setup_xref_Complex_Complex=os.path.join(inputDir,'setup_xref_Complex_Complex.csv')
    if os.path.isfile(setup_xref_Complex_Complex):
        setup_xref_Complex_Complex_df=pd.read_csv(setup_xref_Complex_Complex)

    data_xref_Complex_Complex=os.path.join(inputDir,'data_xref_Complex_Complex.csv')
    if os.path.isfile(data_xref_Complex_Complex):
        data_xref_Complex_Complex_df=pd.read_csv(data_xref_Complex_Complex)

    data_Complex=os.path.join(inputDir,'data_Complex.csv')
    if os.path.isfile(data_Complex):
        data_Complex_df=pd.read_csv(data_Complex)

    data_Simplex=os.path.join(inputDir,'data_Simplex.csv')
    if os.path.isfile(data_Simplex):
        data_Simplex_df=pd.read_csv(data_Simplex)

    data_SimplexText=os.path.join(inputDir,'data_SimplexText.csv')
    if os.path.isfile(data_SimplexText):
        data_SimplexText_df=pd.read_csv(data_SimplexText)

    data_xref_Simplex_Complex = os.path.join(inputDir, 'data_xref_Simplex_Complex.csv')
    if os.path.isfile(data_xref_Simplex_Complex):
        data_xref_Simplex_Complex_df = pd.read_csv(data_xref_Simplex_Complex)

    setup_xref_Simplex_Complex = os.path.join(inputDir, 'setup_xref_Simplex_Complex.csv')
    if os.path.isfile(setup_xref_Simplex_Complex):
        setup_xref_Simplex_Complex_df = pd.read_csv(setup_xref_Simplex_Complex)

    data_SimplexNumber = os.path.join(inputDir, 'data_SimplexNumber.csv')
    if os.path.isfile(data_SimplexNumber):
        data_SimplexNumber_df = pd.read_csv(data_SimplexNumber)

    # build table for complex
    id_complex = find_setup_id(['Institution'], setup_Complex_df).iat[0, 0]
    table_complex = data_Complex_df[data_Complex_df['ID_setup_complex'].isin([id_complex])]

    table_complex = table_complex.drop('ID_setup_complex', axis = 1)
    table_complex = table_complex.rename(columns = {'ID_data_complex':'Institution', 'Identifier':'Institution Identifier'})

    # start to build simplex table
    table_simplex = table_complex

    data_Simplex_temp = pd.merge(data_Simplex_df, data_SimplexText_df, how = 'left', left_on = 'ID_data_date_number_text', right_on = 'ID')
    data_Simplex_temp = data_Simplex_temp[['ID_data_simplex', 'ID_setup_simplex', 'Value']]

    xref_sc_value = pd.merge(data_xref_Simplex_Complex_df, data_Simplex_temp, how = 'left', left_on = 'ID_data_simplex', right_on = 'ID_data_simplex')
    xref_sc_value = xref_sc_value[['ID_data_complex', 'ID_setup_simplex', 'ID_data_simplex', 'Value']]

    complex_name = 'Institution'
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

    institution_characteristics_file_name = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                     'institution characteristics')
    table_simplex.to_csv(institution_characteristics_file_name, encoding='utf-8', index=False)

    return institution_characteristics_file_name
