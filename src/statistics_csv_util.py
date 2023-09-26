#written by Roberto Franzosi October 2019

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"Statistics",['csv','tkinter','os','collections','pandas','numpy','scipy','itertools'])==False:
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

def compute_csv_column_statistics_NoGroupBy(window,inputFilename, outputDir, openOutputFiles,
                                            createCharts, chartPackage,
                                            columnNumber=-1):
    if inputFilename[-4:]!='.csv':
        mb.showwarning(title='File type error', message="The input file\n\n" + inputFilename + "\n\nis not a csv file. The statistical function only works with input csv files.\n\nPlease, select a csv file in input and try again!")
        return None

    outputFilename=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', '', 'ungroup_stats')

    stats=[]
    if columnNumber > -1:
        loopValue=[columnNumber]
    else:
        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(inputFilename)
        loopValue=range(nColumns)
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
            df = pd.read_csv(inputFilename, encoding="utf-8", on_bad_lines='skip', squeeze = True)
        except:
            mb.showwarning(title='Data encoding error', message="The input file\n\n" + inputFilename + "\n\nhas character encoding that breaks the code. The statistical function only works with utf-8 compliant files.\n\nPlease, check your input file encoding and try again!")
            return None
        if df.iloc[:, currentColumn].dtypes!='object': #alphabetic field; do NOT process
            currentName=df.iloc[:, currentColumn].name
            #currentStats=df.iloc[:, currentColumn].describe()
            inputFile_headers=IO_csv_util.get_csvfile_headers(inputFilename)
            # get maximum number of documents in Document ID iff there is a Document ID field
            if 'Document ID' in inputFile_headers:
                docIDColumn=IO_csv_util.get_columnNumber_from_headerValue(inputFile_headers,'Document ID', inputFilename)
                nDocs=df.iloc[:, docIDColumn].max()
            else:
                nDocs=1
            currentStats=nDocs,df.iloc[:, currentColumn].sum(), \
                         df.iloc[:, currentColumn].mean(), \
                         df.iloc[:, currentColumn].mode(), \
                         df.iloc[:, currentColumn].median(), \
                         df.iloc[:, currentColumn].std(), \
                         df.iloc[:, currentColumn].min(), \
                         df.iloc[:, currentColumn].max(), \
                         df.iloc[:, currentColumn].skew(),\
                         df.iloc[:, currentColumn].kurt(), \
                         df.iloc[:, currentColumn].quantile(0.25), \
                         df.iloc[:, currentColumn].quantile(0.50), \
                         df.iloc[:, currentColumn].quantile(0.75)
            currentLine=[]
            currentLine.append(currentName)
            for i in str(currentStats).replace('(', '').replace(')', '').split(','):
                if 'dtype' not in i:
                    currentLine.append(i)

            stats.append(currentLine)
        # stats.to_csv(outputFilename, encoding='utf-8')
    if len(stats)>0:
        df = pd.DataFrame(stats)
        IO_csv_util.df_to_csv(GUI_util.window, df, outputFilename, headers=None, index=False,
                              language_encoding='utf-8')
    return outputFilename

def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'percentile_%s' % n
    return percentile_


#written by Yi Wang March 2020, edited Landau/Franzosi February 2021, November 2022

# lists are the columns to be used for grouping (e.g., Document ID, Document) as ['Document ID', 'Document']
# plotField are the columns to be used for plotting (e.g., Mean, Mode)) as ['Mean', 'Mode'] or ['Mean']
#   plotField columns MUST contain NUMERIC values
# chart_title_label is used as part of the chart_title
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
        df = pd.read_csv(inputFilename, encoding="utf-8", on_bad_lines='skip', squeeze=True)
    except:
        mb.showwarning(title='Data encoding error',
                       message="The input file\n\n" + inputFilename + "\n\nhas character encoding that breaks the code. The statistical function only works with utf-8 compliant files.\n\nPlease, check your input file encoding and try again!")
        return None

    # group the data frame by group columns
    if len(groupByField)>0:
        try:
            # np as numpy
            df_group = df.groupby(groupByField).agg([np.sum, np.mean, lambda x: stats.mode(x, keepdims=False)[0], np.median,
                                                     np.std, np.min, np.max,
                                                     stats.skew, stats.kurtosis,
                                                     percentile(25), percentile(50), percentile(75)])
        except ValueError as e:
            IO_user_interface_util.timed_alert(GUI_util.window, 5000, 'Input file error',
                    "There was an error reading the input file\n\n" + \
                    str(inputFilename) + "\n\nto group by " + str(groupByField) + "\n\nERROR RAISED: " + str(e) +
                    "\n\nIn terminal/command line and in the NLP environment, try pip install scipy --upgrade and pip install numpy --upgrade", \
                    False, '', True, silent=False)
            return None
    if len(plotField) > 0:
        column_name=plotField[0]
        try:
            df_group = df_group[[column_name]]
        except:
            return None
        df_list = [pd.concat([df_group[column_name]],keys=[column_name],names=['Column header'])]
    else:
        df_list = [pd.concat([df_group[index]],keys=[index],names=['Column header']) for index in df_group.columns.levels[0]]
    df_group = pd.concat(df_list,axis=0)
    # putting data into the original headers
    headers_stats=['Count','Mean','Mode','Median','Standard deviation','Minimum','Maximum',
                   'Skewness','Kurtosis','25% quantile','50% quantile','75% quantile']
    df_group.columns = headers_stats
    df_group.to_csv(outputFilename, encoding='utf-8')
    filesToOpen.append(outputFilename)

    if createCharts:
        column_name_to_be_plotted=headers_stats[1] # Mean
        column_name_to_be_plotted=column_name_to_be_plotted + ', ' + headers_stats[2] # Mode
        column_name_to_be_plotted=column_name_to_be_plotted + ', ' + headers_stats[7] # Skewness
        column_name_to_be_plotted=column_name_to_be_plotted + ', ' + headers_stats[8] # Kurtosis
        # Plot Mean, Mode, Skewness, Kurtosis
        # headers_stats = ['Count', 'Mean', 'Mode', 'Median', 'Standard deviation', 'Minimum', 'Maximum',
        #                  'Skewness', 'Kurtosis', '25% quantile', '50% quantile', '75% quantile']

        columns_to_be_plotted_xAxis=[]
        #@@@
        # see note above about the order of items in columns_to_be_plotted list
        #   the group_cols item must always be the last item in the columns_to_be_plotted list
        columns_to_be_plotted_yAxis=[[2,4], [2,5], [2,10], [2,11]] # document field comes first [2
        # columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Mean', 'Mode', 'Skewness', 'Kurtosis'] # document field comes first [2
        # hover_label=['Document']
        hover_label=[]
        #@@@
        outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, outputFilename, outputDir,
                                                  outputFileLabel='',
                                                  chartPackage=chartPackage,
                                                  chart_type_list=["bar"],
                                                  #chart_title=column_name_to_be_plotted + '\n' + chart_title_label + ' by Document',
                                                  chart_title=column_name_to_be_plotted + '\n' + chart_title_label + ' by Document',
                                                  column_xAxis_label_var='', #Document
                                                  column_yAxis_label_var=column_name_to_be_plotted,
                                                  hover_info_column_list=hover_label,
                                                  remove_hyperlinks=True)
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    return filesToOpen


# The function will provide several statistical measure for a csv field values: 'Count', 'Mean', 'Mode', 'Median', 'Standard deviation', 'Minimum', 'Maximum',
#   csv field values MUST be NUMERIC!
#   'Skewness', 'Kurtosis', '25% quantile', '50% quantile', '75% quantile'
#   it will provide statistics both ungrouped and grouped by Document ID
def compute_csv_column_statistics(window,inputFilename,outputDir, outputFileNameLabel,
                groupByList, plotList, chart_title_label='', createCharts=False, chartPackage='Excel'):
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
        outputFiles=compute_csv_column_statistics_groupBy(window,inputFilename,outputDir,outputFileNameLabel,groupByList,plotList,chart_title_label,createCharts,chartPackage)
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)
    return filesToOpen


# written by Roberto June 2022
def get_columns_to_be_plotted(inputFilename, group_cols, plot_cols):
    headers = IO_csv_util.get_csvfile_headers(inputFilename)
    X_col_number = IO_csv_util.get_columnNumber_from_headerValue(headers, group_cols[0], inputFilename)
    Y_col_number = IO_csv_util.get_columnNumber_from_headerValue(headers, plot_cols[0], inputFilename)
    columns_to_be_plotted=[[X_col_number, Y_col_number]]
    # we return the double list [[]] columns_to_be_plotted
    return columns_to_be_plotted

# TODO Tony, can you pass more than one value? Yngve and Frazier
# index is the string value for the column, e.g., 'Sentence ID'
def csv_data_pivot(inputFilename, index, values, no_hyperlinks=True):
    if no_hyperlinks:
        temp, no_hyperlinks_filename = IO_csv_util.remove_hyperlinks(inputFilename)
    else:
        no_hyperlinks_filename = inputFilename
    data = pd.read_csv(no_hyperlinks_filename, encoding='utf-8',on_bad_lines='skip')
    # data = data.pivot(index = 'Sentence ID', columns = 'Document', values = "Yngve score")
    data = data.pivot(index = index, columns = 'Document', values = values)
    data.to_csv(no_hyperlinks_filename, encoding='utf-8')
    # end of function and pass the document forward
    return no_hyperlinks_filename

# written by Tony Chen Gu, April 2022
# TODO TONY How does this differ from the several compute frequency options that I have extensively commented for clarity
    # the latter one seems doing the same staff  but the former one is only for stats results
# the three steps function computes
#   1. the frequencies of a given csv field (select_col) aggregating the results by (group_cols and select_col).
#   2. the resulting frequencies are pivoted in order plot the data in a multi-line chart (one chart for every distinct value of select_col) by Sentence ID.
#   3. the result of pivoting is then plotted
# select_col should be one column name to be plotted eg: ['Verb Voice']
# group_cols should be a list of column names eg ['Sentence ID']
# enable complete_sid to make sentence index continuous
# enable graph to make a multiline graph
# the input should be saved to a csv file first
# def compute_csv_column_frequencies(inputFilename, group_cols, select_col, outputDir, chart_title,
#         graph = True, complete_sid = True, series_label = None, chartPackage = 'Excel'):
#     cols = group_cols + select_col
#     if 'Excel' in chartPackage:
#        use_plotly = False
#     else:
#         use_plotly = True
#     try:
#         data,header = IO_csv_util.get_csv_data(inputFilename, True)
#         data = pd.DataFrame(data, columns=header)
#     except:
#         # an error message about unable to read the file
#         print("Error: cannot read the csv file " + inputFilename)
#         return
#     #data = CoNLL_verb_analysis_util.verb_voice_data_preparation(data)
#     #data,stats,pas,aux,act = CoNLL_verb_analysis_util.voice_output(data, group_cols)
#     #data = pd.DataFrame(data,columns=header+["Verb Voice"])
#     try:
#         print(data[select_col])
#         print(data[group_cols])
#     except:
#         # an error message about wrong csv file without the necessary columns
#         print("Please select the correct csv file, with correct columns")
#         return
#     name = outputDir + os.sep + os.path.splitext(os.path.basename(inputFilename))[0] + "_frequencies.csv"
#     data.to_csv(name, encoding='utf-8')
#     Excel_outputFilename=name
#     # group by both group col and select cols and get a row named count to count the number of frequencies
#     data = data.groupby(cols).size().to_frame("count")
#     data.to_csv(name, encoding='utf-8')
#     data = pd.read_csv(name, encoding='utf-8',on_bad_lines='skip')
#     # transform the data by the select columns
#     # Reshape data (produce a “pivot” table) based on column values. Uses unique values from specified index / columns to form axes of the resulting DataFrame.
#     data = data.pivot(index = group_cols, columns = select_col, values = "count")
#     print(data)
#     data.to_csv(name, encoding='utf-8')
#     # complete sentence id if needed
#     if(complete_sid):
#         # TODO Samir
#         print("Completing sentence index...")
#         charts_util.add_missing_IDs(name, name)
#     print(name)
#     if(graph):
#         #TODO: need filename generation and chart_title generation
#         data = pd.read_csv(name,header=0, encoding='utf-8',on_bad_lines='skip')
#         cols_to_be_plotted = []
#         for i in range(1,len(data.columns)):
#             cols_to_be_plotted.append([0,i])
#         if series_label is None:
#             Excel_outputFilename = charts_util.run_all(cols_to_be_plotted, name, outputDir,
#                                                        "frequency_multi-line_chart", chart_type_list=["line"],
#                                                        chart_title=chart_title,
#                                                        column_xAxis_label_var="Sentence ID", chartPackage=chartPackage)
#         else:
#             Excel_outputFilename = charts_util.run_all(cols_to_be_plotted, name, outputDir,
#                                                        "frequency_multi-line_chart", chart_type_list=["line"],
#                                                        chart_title=chart_title,
#                                                        column_xAxis_label_var="Sentence ID", series_label_list=series_label,
#                                                        chartPackage=chartPackage)
#     return Excel_outputFilename


# written by Yi Wang
# edited by Roberto June 2022

# compute frequencies of a field for a specific field value and with hover-over effects (e.g., NER field, value Location)
# the function also aggregates the values by another field (e.g., NER field by Document ID)
# in INPUT the function can use either a csv file or a data frame
# in OUTPUT the function returns a csv file with frequencies for the selected field

# plot_cols, hover_col, group_cols are single lists with the column headers (alphabetic, rather than column number)
#   plot_cols=['POS'], hover_col=[], group_cols=[Sentence ID', 'Sentence', 'Document ID', 'Document']
def compute_csv_column_frequencies(window,inputFilename, inputDataFrame, outputDir,
            openOutputFiles,createCharts,chartPackage,
            plot_cols, hover_col, group_cols, complete_sid,
            chart_title, fileNameType='CSV',chartType='line',pivot=True):
    name = outputDir + os.sep + os.path.splitext(os.path.basename(inputFilename))[0] + "_frequencies.csv"

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
        import pandas as pd
        data = pd.read_csv(inputFilename, usecols=header_indices,encoding='utf-8',on_bad_lines='skip')

    # remove hyperlink before processing
    data.to_csv(inputFilename,encoding='utf-8', index=False)
    if 'Document' in headers:
        removed_hyperlinks, inputFilename = IO_csv_util.remove_hyperlinks(inputFilename)
    data = pd.read_csv(inputFilename,encoding='utf-8',on_bad_lines='skip')
    # TODO check if data is empty exit
    # fileNameType=fileNameType.replace('/','-')
    # outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir,
    #                 '.csv', 'col-freq_'+fileNameType)
    file_label=''
    for col in plot_cols:
        file_label = file_label + col + '_'
    if len(group_cols)>0:
        if 'Document' in group_cols:
            # file_label = file_label + 'byDoc'
            file_label = 'byDoc'
        else:
            # file_label = file_label + 'by'+group_cols[0] # add only the first element
            file_label = 'by' + group_cols[0]  # add only the first element

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir,
                    '.csv', file_label + '_freq') # + '_col-freq'
    # the outputFilename may get too long and lead to code breakdown when saving the file
    if len(plot_cols) == 0:
        mb.showwarning('Missing field', 'You have not selected the csv field for which to compute frequencies.\n\nPlease, select the field and try again.')
        return filesToOpen

# no aggregation by group_cols --------------------------------------------------------
    elif len(plot_cols) != 0 and len(group_cols) == 0:
        for col in plot_cols:
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
            if (complete_sid):
                # TODO Samir
                print("Completing sentence index...")
                charts_util.add_missing_IDs(outputFilename, outputFilename)
            data.to_csv(outputFilename,encoding='utf-8', index=False)
            filesToOpen.append(outputFilename)

# PREVIOUS CODE

    # aggregation by group_cols NO hover over ----------------------------------------
    elif len(plot_cols) != 0 and len(group_cols) != 0 and len(hover_col) == 0:

# aggregation by group_cols NO hover over ----------------------------------------
#     elif len(plot_cols) != 0 and len(group_cols) != 0 and len(hover_col) == 0:
#         columns_to_be_plotted = []


        # for col in plot_cols:
        #     # plot_cols, hover_col, group_cols are single lists with the column headers
        #     #   plot_cols=['POStag'], hover_col=[], group_cols=[Sentence ID', 'Sentence', 'Document ID', 'Document']
        #     # the aggregation can deal with column items passed as integer (from visualization_chart) or
        #     #   alphabetic values (from statistics_NLP_main)
        group_cols_SV = group_cols.copy()
        group_colsumn_names=[]
        # create a single list
        temp_group_colsumn_names = group_cols + plot_cols
        # test for list of lists [[],[]]
        if any(isinstance(el, list) for el in temp_group_colsumn_names):
            # flatten the list of lists to a single list
            temp_group_colsumn_names = [x for xs in temp_group_colsumn_names for x in xs]
        i = 0
        while i<len(temp_group_colsumn_names):
            t = temp_group_colsumn_names[i]
            header = t
            # check that t is not already in the list group_colsumn_names
            if isinstance(t, (int, float)):
                header = IO_csv_util.get_headerValue_from_columnNumber(headers, t)
                if group_colsumn_names.count(header) == 0:
                    group_colsumn_names.append(header)
            else:
                if group_colsumn_names.count(header) == 0:
                    group_colsumn_names.append(header)
            i = i+1
        if len(group_colsumn_names)==0:
            group_colsumn_names=temp_group_colsumn_names
        # #     data = data.groupby(group_colsumn_names).size().reset_index(name='Frequency')

        group_colsumn_names_SV = group_colsumn_names.copy()
        group_cols_SV = group_cols.copy()

        group_list = group_cols.copy()
        data_final = pd.DataFrame()


        # you can pass Document ID and Document (e.g., in NLTK unusual words), Document (e.g., annotator POS)
        # aggregating by document
        if group_cols[0] == 'Document ID' or group_cols[0] == 'Document':
            if not 'by Document' in chart_title:
                chart_title = chart_title + ' by Document'
            # the data_final ALWAYS has the following column layout:
            #   Document ID, Document, Frequency Document ID,
            #   then all other fields each with its respective frequency
            # [0, 2] will display the document ID in the Data sheet of the xlsx file;
            #   but then the user will not know which document the ID refers to
            # [1, 2] will display the document name in the Data sheet of the xlsx file

            # 0 is the Document ID
            # 1 is the Document
            # 2 is Frequency of Document
            # 3 is the column plotted (e.g., Form, NER)
            # 4 is the frequency of the column plotted (e.g., Form, NER)
            # order of items in the list matters
            # For example, [[3, 4], [1, 2]], for NER, will plot the document and the NER frequency, with document on X axis
            # For example, [[1, 2], [3, 4]], for NER, will plot the document and the NER frequency, with NER on X axis
            # 0 is the groupBy field with no-hyperlinks (e.g., NER)
            # sel_column_name = IO_csv_util. = IO_csv_util.get_columnNumber_from_headerValue(headers, 'Document', inputFilename)(headers, 1)
            columns_to_be_plotted = [[3, 4], [1, 2]]
            # columns_to_be_plotted = get_columns_to_be_plotted(outputFilename, group_cols[0], header)
        else:
            if group_cols[0]!='':
                chart_title = chart_title + ' by ' + str(group_cols[0])
            # if there is no document ID and/or document 0 refers to the field name to be plotted and 1 to its frequency
            # see note above about the order of items in columns_to_be_plotted list
            #   the group_cols item must always be the last item in the columns_to_be_plotted list
            columns_to_be_plotted = [[2, 3], [0, 1]]
            #@@@
            print('outputFilename',outputFilename, 'columns_to_be_plotted',columns_to_be_plotted)

        def multi_level_grouping_and_frequency(data, plot_colss, group_cols):
            # Calculate the first selected column (Lemma) frequency within each group
            grouped = data.groupby(group_cols + plot_colss).size().reset_index(name='Frequency_Document ID')

            if 'Document' == group_cols[0]:
                # Create a dictionary to map each document to its index
                document_id_map = {document: i+1 for i, document in enumerate(grouped['Document'].unique())}

                # Add the 'Document ID' column to the dataframe
                grouped['Document ID'] = grouped['Document'].map(document_id_map)

            # Step 2: Separate into two dataframes for frequencies.
            freq_0 = grouped.groupby(group_cols + [plot_colss[0]])['Frequency_Document ID'].sum().reset_index(
                name=f'Frequency_{plot_colss[0]}')
            freq_1 = grouped.groupby(group_cols + [plot_colss[1]])['Frequency_Document ID'].sum().reset_index(
                name=f'Frequency_{plot_colss[1]}')

            # Step 3: Merge these dataframes back together.
            result = pd.merge(grouped, freq_0, on=group_cols + [plot_colss[0]], how='left')
            result = pd.merge(result, freq_1, on=group_cols + [plot_colss[1]], how='left')

            # Rearrange columns to desired order
            if 'Document' in group_cols:
                result = result[group_cols + ['Frequency_Document ID', plot_colss[0], f'Frequency_{plot_colss[0]}', plot_colss[1],
                                             f'Frequency_{plot_colss[1]}']]
            else:
                result = result[group_cols + [plot_colss[0], f'Frequency_{plot_colss[0]}', plot_colss[1],
                                             f'Frequency_{plot_colss[1]}']]
            counts = result.groupby(group_cols[0]).size()
            # Map the counts back to the original dataframe
            result['Frequency_'+str(group_cols[0])] = result[group_cols[0]].map(counts)

            return result

        def double_level_grouping_and_frequency(data, plot_cols, group_cols):
            # Calculate the counts for each column
            group_cols_count = data[group_cols[0]].value_counts().reset_index()
            group_cols_count.columns = [group_cols[0], f'Frequency_{group_cols[0]}']

            plot_cols_count = data.groupby(group_cols)[plot_cols[0]].value_counts().reset_index(
                name=f'Frequency_{plot_cols[0]}')

            # you can pass Document ID and Document (e.g., in NLTK unusual words), Document (e.g., annotator POS)
            if 'Document' in group_cols[0]:
                # Create a dictionary to map each document to its index starting from 1
                document_id_map = {document: i + 1 for i, document in enumerate(group_cols_count[group_cols[0]].unique())}

                # Add the 'Document ID' column to the dataframe
                # SIMON Document ID should always be the first item, before Document
                group_cols_count['Document ID'] = group_cols_count[group_cols[0]].map(document_id_map)

            # Merge the counts back into the original dataframe
            data_final = pd.merge(group_cols_count, plot_cols_count, how='inner', on=group_cols[0])
            # Remove potential duplicate rows
            data_final = data_final.drop_duplicates()

            # Rearrange columns to desired order
            if group_cols[0] == 'Document ID' and group_cols[1] == 'Document':
                data_final = data_final[[group_cols[0], group_cols[1], f'Frequency_{group_cols[0]}', plot_cols[0], f'Frequency_{plot_cols[0]}']]
                # the data_final has the column layout: Document ID, Document, Frequency Document ID, then all other fields each with its respective frequency
                # [0, 2] will display the document ID in the Data sheet of the xlsx file; but then the user will not know which document the ID refers to
                # [1, 2] will display the document name in the Data sheet of the xlsx file
                # see note above about the order of items in columns_to_be_plotted list
                #   the group_cols item must always be the last item in the columns_to_be_plotted list
                columns_to_be_plotted = [[3, 4], [1, 2]]
                #@@@
                print('outputFilename',outputFilename, 'columns_to_be_plotted',columns_to_be_plotted)

            return data_final

        # print(plot_cols,group_cols)
        if len(plot_cols) >=2:
            data_final = multi_level_grouping_and_frequency(data,plot_cols,group_cols)
        else:
            data_final = double_level_grouping_and_frequency(data,plot_cols,group_cols)
            # Calculate the counts for each column

        if 'Document ID' in data_final.columns and 'Document' in data_final.columns:
            # Create a list of all other columns except 'Document ID' and 'Document'
            other_cols = [col for col in data_final.columns if col not in ['Document ID', 'Document']]

            # Reorder the dataframe
            data_final = data_final[['Document ID', 'Document'] + other_cols]
        # This ensures you have enforced the order. Easily you can generalize it to enforce the order of other columns simply by tweaking the

        # print(inputFilename,columns_to_be_plotted)
        # Pivot the dataframe if you want to change the layout
        # If you want to keep it as it is, you can comment these lines out.
        #data_final = data_final.pivot(index=group_cols, columns=plot_cols, values="Frequency")
        data_final.fillna(0, inplace=True)
        data = data_final
        # Excel allows to group a series value by another series values (e.g., Form or Lemma values by POS or NER tags)
        #   two x-axis labels will be created
        #   https://www.extendoffice.com/documents/excel/2715-excel-chart-group-axis-labels.html
        # but the only way to do this in openpyxl is by plotting TWO separate series,
        #   e.g., a bar chart for Form or Lemma values and a bar or line chart for POS tags
        #   https://openpyxl.readthedocs.io/en/latest/charts/secondary.html

        # SIMON should get the col of frequency in data_final
        #group_list = group_cols_SV.copy()

        # df = data
        # '''something done to ensure a brutal order here'''
        # if plot_cols == ['Form', 'Lemma'] and 'Document' in group_cols:
        #     try:
        #         document_col = df.filter(like="Document").columns[0]  # Assuming only one column matches
        #
        #         # 2. Calculate the primary columns
        #         df['Document ID'] = df.groupby(document_col).cumcount() + 1
        #         document_frequencies = df[document_col].value_counts()
        #         df['Document_Frequency'] = df[document_col].map(document_frequencies)
        #         df['Document ID_Frequency'] = df['Document_Frequency']
        #
        #         # 3 & 4. Preserve the order of other columns and remove any redundant ones
        #         desired_columns = ['Document', 'Document ID', 'Document_Frequency', 'Document ID_Frequency']
        #         other_columns = [col for col in df.columns if
        #                          col not in desired_columns and 'Document' not in col and 'Document ID' not in col]
        #
        #         final_columns_order = desired_columns + other_columns
        #         df = df[final_columns_order]
        #     except:
        #         pass
        # added TONY1
        # pivot=True
        if pivot==True:
            data = data.pivot(index = group_colsumn_names[1:], columns = group_colsumn_names[0], values = "Frequency")
            data.fillna(0, inplace=True)
            #data.reset_index("Document")
        if (complete_sid):
            # TODO Samir
            print("Completing sentence index...")
            charts_util.add_missing_IDs(outputFilename, outputFilename)
        data.to_csv(outputFilename,encoding='utf-8', index=False)
        filesToOpen.append(outputFilename)
        hover_over_header = []
        chartType='bar'

# aggregation by group_cols & hover over -----------------------------------------------
    else:
        for col_hover in hover_col:
            col = str(plot_cols[0])
            temp = group_cols.copy()
            temp.append(col_hover)
            c = data.groupby(group_cols)[col_hover].apply(list).to_dict()

            container.append(c)

        temp = group_cols.copy()
        temp.extend(plot_cols) # plotting variable
        data = data.groupby(temp).size().reset_index(name='Frequency')
        for index, row in data.iterrows():
            if row[plot_cols[0]] == '':
                data.at[index,'Frequency'] = 0

        hover_header = ', '.join(hover_col)
        hover_over_header=['Hover_over: ' + hover_header]
        for index, hover in enumerate(hover_col):
            df = pd.Series(container[index]).reset_index()
            temp = group_cols.copy()
            temp.append(hover)
            df.columns = temp
            data = data.merge(df, how = 'left', left_on= group_cols,right_on = group_cols)
        temp_str = '%s'+'\n%s'* (len(hover_col)-1)
        data['Hover_over: ' + hover_header+'_y'] = data.apply(lambda x: temp_str % tuple(x[h] for h in hover_col),axis=1)
        data.drop(hover_col, axis=1, inplace=True)
        data.to_csv(outputFilename, encoding='utf-8', index=False)
        filesToOpen.extend(outputFilename)
        #@@@
        columns_to_be_plotted = [[1, 2]]
        hover_over_header = [hover_over_header + '_y']

# plot the data from compute_csv_column_frequencies
    def do_special_lemma_form_by_Doc(data, outputDir):
        return

    df = data
    if createCharts:
        # The form/lemma + doc have a special treatment
        if plot_cols == ['Form','Lemma'] and 'Document' in group_cols:
            # the headers layout of the outputFilename is the following:
            #   Document, Frequency_Document ID, Form, Frequency_Form, Lemma, Frequency_Lemma, Frequency_Document
            #@@@
            # columns_to_be_plotted = get_columns_to_be_plotted(outputFilename, group_cols[0], plot_cols[0])
            # [1, 2] frequency of docs, then form and lemma,
            #   where 1, 3, and 5 are the document name, the form values, and the lemma values
            #   and 2, 4, 6 are their respective frequencies
            # columns_to_be_plotted = [[1, 2], [3, 4], [5, 6]]
            #   will display form and lemma in the X axes (in which case column_xAxis_label_var must be changed)
            # columns_to_be_plotted = [[2, 3], [4, 5], [0, 1]]
            #   will display document in the X axes
            columns_to_be_plotted = [[2, 3], [4, 5], [0, 1]]
            column_xAxis_label_var = group_cols[0]
            outputFiles = charts_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                              outputFileLabel=fileNameType,
                                              chartPackage=chartPackage,
                                              chart_type_list=[chartType],
                                              chart_title=chart_title,
                                              column_xAxis_label_var=column_xAxis_label_var,
                                              hover_info_column_list=hover_over_header)
        else:
            # column_xAxis_label_var = ''
            # headers = IO_csv_util.get_csvfile_headers(outputFilename)
            column_xAxis_label_var = group_cols[0]
            # see note above about the order of items in columns_to_be_plotted list
            #   the group_cols item must always be the last item in the columns_to_be_plotted list
            #@@@
            headers = IO_csv_util.get_csvfile_headers(outputFilename)

            if 'Document' in headers:
                columns_to_be_plotted = [[3, 4], [1, 2]] # Document and doc freq
            else:
                columns_to_be_plotted = [[0, 1], [2, 3]]  # POS and form freq

            outputFiles = charts_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                              outputFileLabel=fileNameType,
                                              chartPackage=chartPackage,
                                              chart_type_list=[chartType],
                                              chart_title=chart_title,
                                              column_xAxis_label_var=column_xAxis_label_var,
                                              column_yAxis_label_var=header,
                                              hover_info_column_list=hover_over_header)
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)
    # we can now remove the no_hyperlinks file (i.e., inputFilename), since the frequency file has been computed
    if removed_hyperlinks:
        os.remove(inputFilename)
    return filesToOpen # several files with the charts
