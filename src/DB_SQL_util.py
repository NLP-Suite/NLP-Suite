# import packages
import numpy as np
import pandas as pd

# give the list for all complex names
# parameter: dataframe of setup_Complex
# return: the list of all complex names
def give_all_complex_name(setup_Complex):
  complex_name = setup_Complex[['Name']]
  complex_name = complex_name[complex_name['Name'].notna()]
  list_complex_name = complex_name['Name'].values.tolist()
  list_complex_name.sort()
  return list_complex_name

# the list for all simplex names
# parameter: dataframe of setup_Simplex
# return: the list of all simplex names
def give_all_simplex_name(setup_Simplex):
  simplex_name = setup_Simplex[['Name']]
  simplex_name = simplex_name[simplex_name['Name'].notna()]
  list_simplex_name = simplex_name['Name'].values.tolist()
  return list_simplex_name

# find the id of the input complex (name)
# parameter: name of an complex in list type, dataframe of setup_Complex
# return: a dataframe: id, name of the input complex
def find_setup_id(complex, setup_Complex):
  data = setup_Complex[setup_Complex['Name'].isin(complex)]
  data = data[['ID_setup_complex', 'Name']]
  data['ID_setup_complex'] = [int(x) for x in data['ID_setup_complex']]
  return data

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
  higher_level_complex = higher_level_complex.rename(columns = {'ID_setup_complex':'HigherComplex', 'Name':'Name'})

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
  if(connection(complex1, complex2, path, setup_Complex, setup_xref_Complex_Complex)):
    return path
  else:
    return []

# the helper method of find_path
def connection(complex1, complex2, path, setup_Complex, setup_xref_Complex_Complex):
  if(complex1 == complex2):
    return True
  else:
    next = find_lower_complex([complex1], setup_Complex, setup_xref_Complex_Complex)
    next = next['Name'].values.tolist()
    if len(next) != 0:
      for each in next:
        if each not in path:
          path.append(each)
          if(connection(each, complex2, path, setup_Complex, setup_xref_Complex_Complex)):
            return True
          else:
            path.remove(each)
    return False
