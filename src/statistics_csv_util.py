#written by Roberto Franzosi October 2019

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Statistics",['csv','tkinter','os','collections','pandas','numpy','scipy','itertools'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
from collections import Counter
import csv
import pandas as pd
import numpy as np
from scipy import stats

import IO_files_util
import IO_csv_util
import charts_util
import GUI_IO_util
import charts_Excel_util
import IO_user_interface_util

#column_to_be_counted is the column number (starting 0 in data_list for which a count is required)
#column_name is the name that will appear as the chart name
#value is the value in a column that needs to be added up; for either POSTAG (e.g., NN) or DEPREL tags, the tag value is displayed with its description to make reading easier
#most_common([n])
#Return a list of n elements and their counts.
#When n is omitted or None, most_common() returns all elements in the counter.
def compute_statistics_CoreNLP_CoNLL_tag(data_list,column_to_be_counted,column_name,CoreNLP_tag):
    import Stanford_CoreNLP_tags_util
    column_list=[]
    column_stats=[]
    if len(data_list) != 0:
        #get all the values in the selected column
        column_list = [i[column_to_be_counted] for i in data_list]
        column_stats = Counter(column_list)
        counts = column_stats.most_common()
        column_stats = [[column_name, "Frequencies"]]
        for value, count in counts:
            if CoreNLP_tag=="POSTAG":
                if value in Stanford_CoreNLP_tags_util.dict_POSTAG:
                    description= Stanford_CoreNLP_tags_util.dict_POSTAG[value]
                    column_stats.append([value + " - " + description, count])
            elif CoreNLP_tag=="DEPREL":
                if value in Stanford_CoreNLP_tags_util.dict_DEPREL:
                    description= Stanford_CoreNLP_tags_util.dict_DEPREL[value]
                    column_stats.append([value + " - " + description, count])
            elif CoreNLP_tag=="CLAUSALTAG":
                #print("in stats_visuals value ",value)
                if value in Stanford_CoreNLP_tags_util.dict_CLAUSALTAG:
                    description= Stanford_CoreNLP_tags_util.dict_CLAUSALTAG[value]
                    column_stats.append([value + " - " + description, count])
    # print("in compute_statistics_CoreNLP_CoNLL_tag column_stats ",column_stats)
    return column_stats

# https://datatofish.com/use-pandas-to-calculate-stats-from-an-imported-csv-file/
# https://www.shanelynn.ie/summarising-aggregation-and-grouping-data-in-python-pandas/
# PANDAS - Given a csv file as input, the function will compute basic stats on a specific column
#   Mean, Median, Mode, Total sum, Maximum, Minimum, Count, Standard deviation, Variance
# The function can also perform grouping calculations (e.g., computing the Sum of salaries, grouped by the Country column or Count of salaries, grouped by the Country column)
# https://www.geeksforgeeks.org/python-math-operations-for-data-analysis/
# inputFilename must be a csv file
# inputFilename includes the file path

# fullText.sum()                     Returns sum of all values in the series
# fullText.mean()                    Returns mean of all values in series. Equals to s.sum()/s.count()
# fullText.std()                     Returns standard deviation of all values
# fullText.min() or s.max()          Return min and max values from series
# fullText.idxmin() or s.idxmax()    ns index of min or max value in series
# fullText.median()                  Returns median of all value
# fullText.mode()                    Returns mode of the series
# fullText.value_counts()            Returns series with frequency of each value
# stats=[fullText[fieldName].describe()]
# groupByField
# You can  group by more than one variable, allowing more complex queries.
#   For instance, how many calls, sms, and data entries are in each month?
#   data.groupby(['month', 'item'])['date'].count()
# .sum(), .mean(), .mode(), .median() and other such mathematical operations
#    are not applicable on string or any other data type than numeric value.
# .sum() on a string series would give an unexpected output and return a string
#   by concatenating every string.

# Using the pandas 'describe' function returns a series
#   with information like mean, mode etc depending on
#       every NUMERIC field in the input file
#       or on a specific field passed

def compute_csv_column_statistics_NoGroupBy(window,inputFilename, outputDir, createCharts, chartPackage, columnNumber=-1):
    if inputFilename[-4:]!='.csv':
        mb.showwarning(title='File type error', message="The input file\n\n" + inputFilename + "\n\nis not a csv file. The statistical function only works with input csv files.\n\nPlease, select a csv file in input and try again!")
        return None

    outputFilename=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', '', 'ungroup_stats')

    stats=[]
    if columnNumber > -1:
        loopValue=[columnNumber]
    else:
        numberOfColumns= IO_csv_util.get_csvfile_numberofColumns(inputFilename)
        loopValue=range(numberOfColumns)
    # insert headers
    headers=['Column header','Number of documents',
             'Count','Mean','Mode','Median','Standard deviation','Minimum','Maximum',
                   'Skewness','Kurtosis','25% quantile','50% quantile','75% quantile']
    stats.append(headers)
    for currentColumn in loopValue:
        #reading csv file
        try:
            # squeeze 1 dimensional axis objects into scalars
            # This method is most useful when you don’t know if your object is a Series or DataFrame,
            #   but you do know it has just a single column.
            #   In that case you can safely call squeeze to ensure you have a Series.
            df = pd.read_csv(inputFilename, encoding="utf-8", error_bad_lines=False, squeeze = True)
        except:
            mb.showwarning(title='Data encoding error', message="The input file\n\n" + inputFilename + "\n\nhas character encoding that breaks the code. The statistical function only works with utf-8 compliant files.\n\nPlease, check your input file encoding and try again!")
            return None
        if df.iloc[:, currentColumn].dtypes!='object': #alphabetic field; do NOT process
            currentName=df.iloc[:, currentColumn].name
            #currentStats=df.iloc[:, currentColumn].describe()
            inputFile_headers=IO_csv_util.get_csvfile_headers(inputFilename)
            # get maximum number of documents in Document ID iff there is a Document ID field
            if 'Document ID' in inputFile_headers:
                docIDColumn=IO_csv_util.get_columnNumber_from_headerValue(inputFile_headers,'Document ID')
                nDocs=df.iloc[:, docIDColumn].max()
            else:
                nDocs=1
            currentStats=nDocs,df.iloc[:, currentColumn].sum(), df.iloc[:, currentColumn].mean(), df.iloc[:, currentColumn].mode(), df.iloc[:, currentColumn].median(), df.iloc[:, currentColumn].std(), df.iloc[:, currentColumn].min(), df.iloc[:, currentColumn].max(), df.iloc[:, currentColumn].kurt(),df.iloc[:, currentColumn].kurt(), df.iloc[:, currentColumn].quantile(0.25), df.iloc[:, currentColumn].quantile(0.50), df.iloc[:, currentColumn].quantile(0.75)
            currentLine=[]
            currentLine.append(currentName)
            currentLine.append(currentStats)
            stats.append(currentLine)

    return outputFilename

def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'percentile_%s' % n
    return percentile_


#written by Yi Wang March 2020, edited Landau/Franzosi February 2021

# lists are the columns to be used for grouping (e.g., Document ID, Document) ['Document ID', 'Document']
# plotField are the columns to be used for plotting (e.g., Mean, Mode)) ['Mean', 'Mode'] or ['Mean']
#   columns MUST contain NUMERIC values
# chart_title_label is used as part of the the chart_title
def compute_csv_column_statistics_groupBy(window,inputFilename, outputDir, outputFileNameLabel, groupByField: list, plotField: list, chart_title_label, createCharts, chartPackage):
    filesToOpen=[]
    outputFilename=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', '', outputFileNameLabel + '_group_stats')
    # filesToOpen.append(output_name)

    if not set(groupByField).issubset(set(IO_csv_util.get_csvfile_headers(inputFilename))):
        mb.showwarning(title='Groupby field error',
                       message="The selected groupby fields (" + ", ".join(groupByField) + ") are not in the headers (" + ", ".join(IO_csv_util.get_csvfile_headers(inputFilename)) + ") of the file " + inputFilename)

    if inputFilename[-4:] != '.csv':
        mb.showwarning(title='File type error',
                       message="The input file\n\n" + inputFilename + "\n\nis not a csv file. The statistical function only works with input csv files.\n\nPlease, select a csv file in input and try again!")
        return None
    # reading csv file
    try:
        df = pd.read_csv(inputFilename, encoding="utf-8", error_bad_lines=False, squeeze=True)
    except:
        mb.showwarning(title='Data encoding error',
                       message="The input file\n\n" + inputFilename + "\n\nhas character encoding that breaks the code. The statistical function only works with utf-8 compliant files.\n\nPlease, check your input file encoding and try again!")
        return None

    if len(groupByField)>0:
        try:
            df_group = df.groupby(groupByField).agg([np.sum, np.mean, lambda x: stats.mode(x)[0], np.median,
                                                     np.std, np.min, np.max,
                                                     stats.skew, stats.kurtosis,
                                                     percentile(25), percentile(50), percentile(75)])
        except: # the np.sum etc. will break the code if the field passed is alphabetic
            IO_user_interface_util.timed_alert(window, 4000, 'Warning',
                                               "The fields to be grouped by " + str(groupByField) + " are alphabetic and statistical measures cannot be computed.",
                                               False, '', True, '', False)
            return
    if len(plotField) > 0:
        column_name=plotField[0]
        try:
            df_group = df_group[[column_name]]
        except:
            return filesToOpen
        df_list = [pd.concat([df_group[column_name]],keys=[column_name],names=['Column header'])]
    else:
        df_list = [pd.concat([df_group[index]],keys=[index],names=['Column header']) for index in df_group.columns.levels[0]]
    df_group = pd.concat(df_list,axis=0)
    # putting data into the original headers
    headers_stats=['Count','Mean','Mode','Median','Standard deviation','Minimum','Maximum',
                   'Skewness','Kurtosis','25% quantile','50% quantile','75% quantile']
    df_group.columns = headers_stats
    df_group.to_csv(outputFilename, encoding='utf-8')
    filesToOpen.append(outputFilename, encoding='utf-8')

    if createCharts==True:
        column_name_to_be_plotted=headers_stats[1] # Mean
        column_name_to_be_plotted=column_name_to_be_plotted + ', ' + headers_stats[2] # Mode
        column_name_to_be_plotted=column_name_to_be_plotted + ', ' + headers_stats[7] # Skewness
        column_name_to_be_plotted=column_name_to_be_plotted + ', ' + headers_stats[8] # Kurtosis
        # Plot Mean, Mode, Skewness, Kurtosis
        # headers_stats = ['Count', 'Mean', 'Mode', 'Median', 'Standard deviation', 'Minimum', 'Maximum',
        #                  'Skewness', 'Kurtosis', '25% quantile', '50% quantile', '75% quantile']

        columns_to_be_plotted=[[2,4], [2,5], [2,10], [2,11]] # document field comes first [2
        # columns_to_be_plotted=['Mean', 'Mode', 'Skewness', 'Kurtosis'] # document field comes first [2
        # hover_label=['Document']
        hover_label=[]
        chart_outputFilename = charts_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                  outputFileLabel='',
                                                  chartPackage=chartPackage,
                                                  chart_type_list=["bar"],
                                                  #chart_title=column_name_to_be_plotted + '\n' + chart_title_label + ' by Document',
                                                  chart_title=column_name_to_be_plotted + '\n' + chart_title_label + ' by Document',
                                                  column_xAxis_label_var='', #Document
                                                  column_yAxis_label_var=column_name_to_be_plotted,
                                                  hover_info_column_list=hover_label,
                                                  remove_hyperlinks = True)
        if chart_outputFilename != None:
            filesToOpen.append(chart_outputFilename)

    return filesToOpen


# The function will provide several statistical measure for a csv field valuues: 'Count', 'Mean', 'Mode', 'Median', 'Standard deviation', 'Minimum', 'Maximum',
#   csv field values MUST be NUMERIC!
#   'Skewness', 'Kurtosis', '25% quantile', '50% quantile', '75% quantile'
#   it will provide statistics both ungrouped and grouped by Document ID
def compute_csv_column_statistics(window,inputFilename,outputDir, outputFileNameLabel, groupByList, plotList, chart_title_label='', createCharts=False, chartPackage='Excel'):
    filesToOpen=[]
    if len(groupByList)==0:
        command = tk.messagebox.askyesno("Groupby fields", "Do you want to compute statistics grouping results by the values of one or more fields (e.g., the DocumentID of a CoNLL table)?")
        if command ==True:
            groupByList=GUI_IO_util.slider_widget(GUI_util.window,"Enter comma-separated csv headers for GroupBy option",1,10,'')
    # TODO TONY temporarily disconnected while waiting to fix problems in the compute_csv_column_statistics_NoGroupBy function
    # temp_outputfile = compute_csv_column_statistics_NoGroupBy(window,inputFilename,outputDir,createCharts,chartPackage)
    # if temp_outputfile!='':
    #     filesToOpen.append(temp_outputfile)
    if len(groupByList)>0:
        temp_outputfile=compute_csv_column_statistics_groupBy(window,inputFilename,outputDir,outputFileNameLabel,groupByList,plotList,chart_title_label,createCharts,chartPackage)
        if not (temp_outputfile is None):
            # append because temp_outputfile is a list
            filesToOpen = temp_outputfile #.append(temp_outputfile)
    return filesToOpen


# TODO TONY HOW DOES THIS DIFFER FROM def prepare_data_to_be_plotted_inExcel?
# compute frequencies of a field for a specific value and with hover-over effects (e.g., NER field, value Location)
# the function does not aggregate the values by another field (e.g., NER field by Document ID)
# in INPUT the function can use either a csv file or a data frame
#   either or both????
# in OUTPUT the function returns a csv file with frequencies for the selected field
# it does not seem to provide a way to aggregate by specific fields (e.g., Document ID)
#   as done by compute_csv_column_frequencies_with_aggregation
# def prepare_csv_data_for_chart(window,inputFlename, inputDataFrame, outputDir, select_col : list, hover_col : list, group_col : list, fileNameType, chartType, openOutputFiles, createExcelCharts, chartPackage,count_var=0):
#     outputFilename = IO_files_util.generate_output_file_name(inputFlename, '', outputDir, '.csv')
#     if len(inputDataFrame) != 0:
#             df = inputDataFrame
#         else:
#             with open(inputFilename, encoding='utf-8', errors='ignore') as infile:
#                 reader = csv.reader(x.replace('\0', '') for x in infile)
#                 headers = next(reader)
#             header_indices = [i for i, item in enumerate(headers) if item]
#             df = pd.read_csv(inputFilename, usecols=header_indices, encoding='utf-8')
#     # convert a list to a str
#     select_column = select_col[0]
#     # separate a complete csv file into multiple dataframes filter by select_col, which will produce unequal index numbers
#     df_list = sort_by_column(df, select_column)
#     # makes those separate dataframes align to the same maximum index
#     df_hover = slicing_dataframe(df,group_col + hover_col)
#     df_list = align_dataframes(df_list)
#     #append aligned dataframes as frequency columns in the new dataframe
#     df_list = [slicing_dataframe(d, group_col + select_col + ['Frequency']) for d in df_list]
#     # rename those newly added columns
#     df_list = [rename_df(d,select_column) for d in df_list]
#     # append the hover-over data (Labels) in the original csv file
#     df_list.append(df_hover)
#     # horizontally concatenate all the frequency dataframes and the hover-over dataframe
#     df_merged = reduce(lambda left, right: pd.merge(left, right, how='outer',on=group_col), df_list)
#     # replace all the empty strings inside this new df_merged dataframe with 0
#     df_merged = df_merged.replace(r'^\s*$', 0, regex=True)
#     df_merged.to_csv(outputFilename,index=False) # output
#     return outputFilename
#
#
# def sort_by_column(input, column):
#     if isinstance(input, pd.DataFrame):
#         df = input
#     else:
#         df = pd.read_csv(input)
#     col_list = set(df[column].tolist())
#     df_list = [df[df[column] == value] for value in col_list]
#     return df_list
#
#
# def align_dataframes(df_list):
#     max = 0
#     for df in df_list:
#         header = list(df.columns)
#         if 'Sentence ID' in header:
#             sentenceID = 'Sentence ID'
#         if df[sentenceID].max() > max:
#             max = df[sentenceID].max()
#     new_list = []
#     for df in df_list:
#         if df.empty:
#             continue
#         temp = df.iloc[-1,:]
#         if temp[sentenceID] != max:
#             # TODO solve warning issue
#             # https://www.dataquest.io/blog/settingwithcopywarning/
#             # ​​​​SettingwithCopyWarning
#             temp[sentenceID] = max
#             temp['Frequency'] = 0
#             new_df = df.append(temp,ignore_index=True)
#         else:
#             new_df = df
#         new_list.append(new_df)
#
#     df_list = [add_missing_IDs(data) for data in new_list if not data.empty]
#     return df_list
#
#
# def slicing_dataframe(df,columns):
#     df = df[columns]
#     return df
#
#
# def rename_df(df,col):
#     for index, row in df.iterrows():
#         if row[col] != '':
#             name = row[col]
#             break
#     df.rename(columns={"Frequency": name + " Frequency"},inplace=True)
#     df = df.drop(columns=[col])
#     return df

# compute frequencies of a field for a specific value (e.g., NER field, value Location)
# the function does not aggregate the values by another field (e.g., NER field by Document ID)
#   as done by compute_csv_column_frequencies_with_aggregation
# in INPUT it uses a data list, rather than filename, and returns
# in OUTPUT a list complete_column_frequencies
# TODO does it compute frequencies by some aggregate values (e.g., document ID)?
# def compute_column_frequencies_4Excel(columns_to_be_plotted, data_list, headers,specific_column_value_list=[]):
#     column_list=[]
#     column_frequencies=[]
#     column_stats=[]
#     specific_column_value=''
#     complete_column_frequencies=[]
#     if len(data_list) != 0:
#         for k in range(len(columns_to_be_plotted)):
#             res=[]
#             if len(specific_column_value_list)>0:
#                 specific_column_value=specific_column_value_list[k]
#             #get all the values in the selected column
#             column_list = [i[1] for i in data_list[k]]
#             counts = Counter(column_list).most_common()
#             if len(headers) > 0:
#                 id_name_num = columns_to_be_plotted[k][0]
#                 id_name = headers[id_name_num]
#                 column_name_num = columns_to_be_plotted[k][1]
#                 column_name = headers[column_name_num]
#                 if len(specific_column_value_list)==0:
#                     column_frequencies = [[column_name + " values", "Frequencies of " + column_name]]
#                 else:
#                     for y in range(len(specific_column_value_list)):
#                         column_frequencies = [[id_name, "Frequencies of " + str(specific_column_value) + " in Column " + str(column_name)]]
#             else:
#                 id_name_num = columns_to_be_plotted[k][0]
#                 id_name = "column_" + str(id_name_num+1)
#                 column_name_num = columns_to_be_plotted[k][1]
#                 column_name = "column_" + str(column_name_num+1)
#                 if len(specific_column_value)==0:
#                     column_frequencies = [[column_name + " values", "Frequencies of " + column_name]]
#                 else:
#                     for y in range(len(specific_column_value_list)):
#                         column_frequencies = [[id_name, "Frequencies of " + str(specific_column_value) + " in Column_" + str(column_name_num+1)]]
#             if len(specific_column_value) == 0:
#                 for value, count in counts:
#                     column_frequencies.append([value, count])
#             else:
#                 for i in range(len(column_list)):
#                     if column_list[i] == specific_column_value:
#                         res.append(1)
#                     else:
#                         res.append(0)
#                 for j in range(len(data_list[k])):
#                     column_frequencies.append([data_list[k][j][0], res[j]])
#             complete_column_frequencies.append(column_frequencies)
#     return complete_column_frequencies


# written by Tony Chen Gu, April 2022
# TODO TONY How does this differ from the several compute frequency options that I have extensively commented for clarity
    # the latter one seems doing the same staff  but the former one is only for stats results
# the three steps function computes
#   1. the frequencies of a given csv field (select_col) aggregating the results by (group_col and select_col).
#   2. the resulting frequencies are pivoted in order plot the data in a multi-line chart (one chart for every distinct value of select_col) by Sentence ID.
#   3. the result of pivoting is then plotted
# select_col should be one column name to be plotted eg: ['Verb Voice']
# group_col should be a list of column names eg ['Sentence ID']
# enable complete_sid to make sentence index continuous
# enable graph to make a multiline graph
# the input should be saved to a csv file first
def compute_csv_column_frequencies(inputFilename, group_col, select_col, outputDir, chartTitle,
        graph = True, complete_sid = True, series_label = None, chartPackage = 'Excel'):
    cols = group_col + select_col
    if 'Excel' in chartPackage:
       use_plotly = False
    else:
        use_plotly = True
    try:
        data,header = IO_csv_util.get_csv_data(inputFilename, True)
        data = pd.DataFrame(data, columns=header)
    except:
        # an error message about unable to read the file
        print("Error: cannot read the csv file " + inputFilename)
        return
    #data = CoNLL_verb_analysis_util.verb_voice_data_preparation(data)
    #data,stats,pas,aux,act = CoNLL_verb_analysis_util.voice_output(data, group_col)
    #data = pd.DataFrame(data,columns=header+["Verb Voice"])
    try:
        print(data[select_col])
        print(data[group_col])
    except:
        # an error message about wrong csv file without the necessary columns
        print("Please select the correct csv file, with correct columns")
        return
    name = outputDir + os.sep + os.path.splitext(os.path.basename(inputFilename))[0] + "_frequencies.csv"
    data.to_csv(name, encoding='utf-8')
    Excel_outputFilename=name
    # group by both group col and select cols and get a row named count to count the number of frequencies
    data = data.groupby(cols).size().to_frame("count")
    data.to_csv(name, encoding='utf-8')
    data = pd.read_csv(name, encoding='utf-8',error_bad_lines=False)
    # transform the data by the select columns
    # Reshape data (produce a “pivot” table) based on column values. Uses unique values from specified index / columns to form axes of the resulting DataFrame.
    data = data.pivot(index = group_col, columns = select_col, values = "count")
    print(data)
    data.to_csv(name, encoding='utf-8')
    # complete sentence id if needed
    if(complete_sid):
        print("Completing sentence index...")
        charts_util.add_missing_IDs(name, name)
    print(name)
    if(graph):
        #TODO: need filename generation and chartTitle generation
        data = pd.read_csv(name,header=0, encoding='utf-8',error_bad_lines=False)
        cols_to_be_plotted = []
        for i in range(1,len(data.columns)):
            cols_to_be_plotted.append([0,i])
        if series_label is None:
            Excel_outputFilename = charts_util.run_all(cols_to_be_plotted,name,outputDir,
                                            "frequency_multi-line_chart", chart_type_list=["line"],
                                            chart_title=os.path.splitext(os.path.basename(inputFilename))[0]+"_"+chartTitle, column_xAxis_label_var="Sentence ID",chartPackage = chartPackage)
        else:
            Excel_outputFilename = charts_util.run_all(cols_to_be_plotted,name,outputDir,
                                            "frequency_multi-line_chart", chart_type_list=["line"],
                                            chart_title=os.path.splitext(os.path.basename(inputFilename))[0]+"_"+chartTitle, column_xAxis_label_var="Sentence ID",series_label_list = series_label, chartPackage = chartPackage)
    return Excel_outputFilename


# written by Roberto June 2022
def get_columns_to_be_plotted(outputFilename,col):
    headers = IO_csv_util.get_csvfile_headers(outputFilename)
    col1_nunmber = IO_csv_util.get_columnNumber_from_headerValue(headers, col)
    col2_nunmber = IO_csv_util.get_columnNumber_from_headerValue(headers, 'Frequency')
    columns_to_be_plotted=[[col1_nunmber, col2_nunmber]]
    return columns_to_be_plotted

# TODO Tony, can you pass more than one value? Yngve and Frazier
# index is the string value for the column, e.g., 'Sentence ID'
def csv_data_pivot(inputFilename, index, values, no_hyperlinks=True):
    if no_hyperlinks:
        temp, no_hyperlinks_filename = IO_csv_util.remove_hyperlinks(inputFilename)
    else:
        no_hyperlinks_filename = inputFilename
    data = pd.read_csv(no_hyperlinks_filename, encoding='utf-8',error_bad_lines=False)
    # data = data.pivot(index = 'Sentence ID', columns = 'Document', values = "Yngve score")
    data = data.pivot(index = index, columns = 'Document', values = values)
    data.to_csv(no_hyperlinks_filename, encoding='utf-8')
    # end of function and pass the document forward
    return no_hyperlinks_filename

# written by Yi Wang
# edited by Roberto June 2022

# compute frequencies of a field for a specific field value and with hover-over effects (e.g., NER field, value Location)
# the function also aggregates the values by another field (e.g., NER field by Document ID)
# in INPUT the function can use either a csv file or a data frame
# in OUTPUT the function returns a csv file with frequencies for the selected field

# selected_col, hover_col, group_col are single lists with the column headers (alphabetic, rather than column number)
#   selected_col=['POStag'], hover_col=[], group_col=[Sentence ID', 'Sentence', 'Document ID', 'Document']
def compute_csv_column_frequencies_with_aggregation(window,inputFilename, inputDataFrame, outputDir,
            openOutputFiles,createCharts,chartPackage,
            selected_col, hover_col, group_col,
            fileNameType='CSV',chartType='line',pivot=True):

    filesToOpen = []
    container = []
    hover_over_header = []
    removed_hyperlinks = False
    if inputDataFrame is not None:
        if len(inputDataFrame)!=0:
            data = inputDataFrame
    else:
        with open(inputFilename,encoding='utf-8',errors='ignore') as infile:
            reader = csv.reader(x.replace('\0', '') for x in infile)
            headers = next(reader)
        header_indices = [i for i, item in enumerate(headers) if item]
        data = pd.read_csv(inputFilename, usecols=header_indices,encoding='utf-8',error_bad_lines=False)


    # remove hyperlink before processing
    data.to_csv(inputFilename,encoding='utf-8', index=False)
    removed_hyperlinks, inputFilename = IO_csv_util.remove_hyperlinks(inputFilename)
    data = pd.read_csv(inputFilename,encoding='utf-8',error_bad_lines=False)
    # TODO check if data is empty exit
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'col-freq')

    if len(selected_col) == 0:
        mb.showwarning('Missing field', 'You have not selected the csv field for which to compute frequencies.\n\nPlease, select the field and try again.')

    elif len(selected_col) != 0 and len(group_col) == 0:
        # no aggregation by group_col --------------------------------------------------------
        for col in selected_col:
            data = data[col].value_counts().to_frame().reset_index()
            hdr = [col, col + ' Frequency']
            hover_over_header = []
            if len(hover_col) != 0:
                hover_header = ', '.join(hover_col)
                hover_over_header = ['Hover_over: ' + hover_header]
                hdr.append(hover_over_header)
                data.columns = hdr
                temp_str = '%s' + '\n%s' * (len(hover_col) - 1)
                data['Hover_over: ' + hover_header] = data.apply(lambda x: temp_str % tuple(x[h] for h in hover_col),
                                                                 axis=1)
                data.drop(hover_col, axis=1, inplace=True)
            else:
                data.columns = hdr
            data.to_csv(outputFilename,encoding='utf-8', index=False)
    elif len(selected_col) != 0 and len(group_col) != 0 and len(hover_col) == 0:
        # aggregation by group_col NO hover over ----------------------------------------
        for col in selected_col:
            # selected_col, hover_col, group_col are single lists with the column headers
            #   selected_col=['POStag'], hover_col=[], group_col=[Sentence ID', 'Sentence', 'Document ID', 'Document']
            # the aggregation can deal with column items passed as integer (from visualization_chart) or
            #   alphabetic values (from statistics_NLP_main)
            group_column_names=[]
            # create a single list
            temp_group_column_names = group_col + selected_col
            # test for list of lists [[],[]]
            if any(isinstance(el, list) for el in temp_group_column_names):
                # flatten the list of lists to a single list
                temp_group_column_names = [x for xs in temp_group_column_names for x in xs]
            i = 0
            while i<len(temp_group_column_names):
                t = temp_group_column_names[i]
                # check that t is not already in the list group_column_names
                if isinstance(t, (int, float)):
                    header = IO_csv_util.get_headerValue_from_columnNumber(headers, t)
                    if group_column_names.count(header) == 0:
                        group_column_names.append(header)
                else:
                    if group_column_names.count(header) == 0:
                        group_column_names.append(header)
                i = i+1
            if len(group_column_names)==0:
                group_column_names=temp_group_column_names
            data = data.groupby(group_column_names).size().reset_index(name='Frequency')
            # it is already sorted
            # data = data.sort_values(by=group_column_names, ascending=True)
            # data.sort_values(by=group_column_names, ascending=True, inplace=True)
            # added TONY1
            # pivot=True
            if pivot==True:
                data = data.pivot(index = group_column_names[1:], columns = group_column_names[0], values = "Frequency")
                data.fillna(0, inplace=True)
                #data.reset_index("Document")
                data.to_csv(outputFilename,encoding='utf-8', index=False)
            # end add
            else:
                data.to_csv(outputFilename,encoding='utf-8', index=False)
            filesToOpen.append(outputFilename)
    else: # aggregation by group_col & hover over -----------------------------------------------
        for col_hover in hover_col:
            col = str(selected_col[0])
            temp = group_col.copy()
            temp.append(col_hover)
            c = data.groupby(group_col)[col_hover].apply(list).to_dict()

            container.append(c)

        temp = group_col.copy()
        temp.append(selected_col) # plotting variable
        data = data.groupby(temp).size().reset_index(name='Frequency')
        for index, row in data.iterrows():
            if row[selected_col[0]] == '':
                data.at[index,'Frequency'] = 0

        hover_header = ', '.join(hover_col)
        hover_over_header=['Hover_over: ' + hover_header]
        for index, hover in enumerate(hover_col):
            df = pd.Series(container[index]).reset_index()
            temp = group_col.copy()
            temp.append(hover)
            df.columns = temp
            data = data.merge(df, how = 'left', left_on= group_col,right_on = group_col)
        temp_str = '%s'+'\n%s'* (len(hover_col)-1)
        data['Hover_over: ' + hover_header] = data.apply(lambda x: temp_str % tuple(x[h] for h in hover_col),axis=1)
        data.drop(hover_col, axis=1, inplace=True)
        data.to_csv(outputFilename, encoding='utf-8', index=False)
        filesToOpen.append(outputFilename)
    # if createCharts:
    #     columns_to_be_plotted = get_columns_to_be_plotted(outputFilename,col)
    #     chart_outputFilename = charts_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
    #                                           outputFileLabel=fileNameType,
    #                                           chartPackage=chartPackage,
    #                                           chart_type_list=chartType,
    #                                           chart_title='Frequency Distribution of ' + col + ' Values',
    #                                           column_xAxis_label_var=col,
    #                                           hover_info_column_list=hover_over_header)
    #     if chart_outputFilename != None:
    #         filesToOpen.filesToOpen(chart_outputFilename)

    # we can now remove the no_hyperlinks file (i.e., inputFilename), since the frequency file has been computed
    if removed_hyperlinks:
        os.remove(inputFilename)
    return filesToOpen # several files with the charts
