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
import charts_Excel_util

#column_to_be_counted is the column number (starting 0 in data_list for which a count is required)
#column_name is the name that will appear as the chart name
#value is the value in a column that needs to be added up; for either POSTAG (e.g., NN) or DEPREL tags, the tag value is displayed with its description to make reading easier 
#most_common([n])
#Return a list of n elements and their counts. 
#When n is omitted or None, most_common() returns all elements in the counter.
def compute_stats_CoreNLP_tag(data_list,column_to_be_counted,column_name,CoreNLP_tag):
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
    # print("in compute_stats_CoreNLP_tag column_stats ",column_stats)
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

def compute_field_statistics_NoGroupBy(window,inputFilename, outputDir, openOutputFiles, createExcelCharts, chartPackage, columnNumber=-1):
    filesToOpen = []
    if inputFilename[-4:]!='.csv':
        mb.showwarning(title='File type error', message="The input file\n\n" + inputFilename + "\n\nis not a csv file. The statistical function only works with input csv files.\n\nPlease, select a csv file in input and try again!")
        return None

    output_file_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', '', 'ungroup_stats')
    filesToOpen.append(output_file_name)

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
            df = pd.read_csv(inputFilename, encoding="utf-8",squeeze = True)
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
            currentLine.extend(currentStats)
            stats.append(currentLine)
    
    if len(stats)>0:
        IO_csv_util.list_to_csv(window,stats,output_file_name)
        if openOutputFiles==True:
            IO_files_util.OpenOutputFiles(window, openOutputFiles, filesToOpen)
            filesToOpen=[] # empty list to avoid dual opening in calling function
        return filesToOpen
    else:
        return None


def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'percentile_%s' % n
    return percentile_


#written by Yi Wang March 2020, edited Landau/Franzosi February 20021
def compute_field_statistics_groupBy(window,inputFilename, outputDir, groupByField: list, openOutputFiles, createExcelCharts, chartPackage, columnNumber=-1):
    filesToOpen=[]
    output_name=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', '', 'group_stats')
    # filesToOpen.append(output_name)

    if not set(groupByField).issubset(set(IO_csv_util.get_csvfile_headers(inputFilename))):
        mb.showwarning(title='Groupby field error',
                       message="Not all of the selected groupby fields are contained in "+ inputFilename)

    if inputFilename[-4:] != '.csv':
        mb.showwarning(title='File type error',
                       message="The input file\n\n" + inputFilename + "\n\nis not a csv file. The statistical function only works with input csv files.\n\nPlease, select a csv file in input and try again!")
        return None
    # reading csv file
    try:
        df = pd.read_csv(inputFilename, encoding="utf-8", squeeze=True)
    except:
        mb.showwarning(title='Data encoding error',
                       message="The input file\n\n" + inputFilename + "\n\nhas character encoding that breaks the code. The statistical function only works with utf-8 compliant files.\n\nPlease, check your input file encoding and try again!")
        return None

    df_group = df.groupby(groupByField).agg([np.sum, np.mean, lambda x: stats.mode(x)[0], np.median,
                                         np.std, np.min, np.max,
                                         stats.skew, stats.kurtosis,
                                         percentile(25), percentile(50), percentile(75)])

    if columnNumber>-1:
        headers = IO_csv_util.get_csvfile_headers(inputFilename)
        column_name=headers[columnNumber]
        df_group = df_group[[column_name]]
        df_list = [pd.concat([df_group[column_name]],keys=[column_name],names=['Column header'])]
    else:
        df_list = [pd.concat([df_group[index]],keys=[index],names=['Column header']) for index in df_group.columns.levels[0]]
    df_group = pd.concat(df_list,axis=0)
    # putting data into the original headers
    headers_stats=['Count','Mean','Mode','Median','Standard deviation','Minimum','Maximum',
                   'Skewness','Kurtosis','25% quantile','50% quantile','75% quantile']
    df_group.columns = headers_stats
    df_group.to_csv(output_name)
    filesToOpen.append(output_name)
    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(window, openOutputFiles, filesToOpen)
        filesToOpen=[] # empty list to avoid dual opening in calling function
    return filesToOpen

def compute_field_statistics(window,inputFilename,outputDir, openOutputFiles,createExcelCharts=False):
    command = tk.messagebox.askyesno("Groupby fields", "Do you want to compute statistics grouping results by the values of one or more fields (e.g., the DocumentID of a CoNLL table)?")
    if command ==False:
        compute_field_statistics_NoGroupBy(window,inputFilename,outputDir, openOutputFiles)
    else:
        import GUI_IO_util
        groupByValue=GUI_IO_util.slider_widget("Enter comma-separated csv headers for GroupBy option","Enter headers",1,'')
        if len(groupByValue)>0:
            filesToOpen=compute_field_statistics_groupBy(window,inputFilename,outputDir,groupByValue,openOutputFiles)

# # 1.22 Yi we do not need a columns_to_be_plotted variable in this function, passing numbers of columns to prepare_csv_data_for_chart will cause error
def compute_stats_NLP_main(window,inputFilename, inputDataFrame, outputDir,
            openOutputFiles,createExcelCharts,chartPackage,
            columns_to_be_plotted,selected_col, hover_col, group_col,
            fileNameType='CSV',chartType='line'):

    filesToOpen = []
    container = []
    if len(inputDataFrame)!=0:
        data = inputDataFrame
    else:
        with open(inputFilename,encoding='utf-8',errors='ignore') as infile:
            reader = csv.reader(x.replace('\0', '') for x in infile)
            headers = next(reader)
        header_indices = [i for i, item in enumerate(headers) if item]
        data = pd.read_csv(inputFilename, usecols=header_indices,encoding='utf-8')

    if len(selected_col) == 0:
        mb.showwarning('Missing field', 'You have not selected the csv field for which to compute frequencies.\n\nPlease, select the field and try again.')

    elif len(selected_col) != 0 and len(group_col) == 0:
        for col in selected_col:
            output_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', col)
            data = data[col].value_counts().to_frame().reset_index()
            hdr = [col, col + ' Frequency']

            Hover_over_header = []
            if len(hover_col) != 0:
                hover_header = ', '.join(hover_col)
                Hover_over_header = ['Hover_over: ' + hover_header]
                hdr.append(Hover_over_header)
                data.columns = hdr
                temp_str = '%s' + '\n%s' * (len(hover_col) - 1)
                data['Hover_over: ' + hover_header] = data.apply(lambda x: temp_str % tuple(x[h] for h in hover_col),
                                                                 axis=1)
                data.drop(hover_col, axis=1, inplace=True)
            else:
                data.columns = hdr
            data.to_csv(output_file_name,index=False)
            filesToOpen.append(output_file_name)

            if createExcelCharts:
                # columns_to_be_plotted = [[1, 2]] # hard code Yi
                Excel_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                      outputFileLabel=fileNameType,
                                                      chart_type_list=chartType,
                                                      chart_title='',
                                                      column_xAxis_label_var=col,
                                                      hover_info_column_list=Hover_over_header)
                if Excel_outputFilename != "":
                    filesToOpen.append(Excel_outputFilename)

    elif len(selected_col) != 0 and len(group_col) != 0 and len(hover_col) == 0:
        for col in selected_col:
            output_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', col)
            temp = group_col.copy()
            temp.append(col)
            data = data.groupby(temp).size().reset_index(name='Frequency')
            for index, row in data.iterrows():
                if row[col] == '':
                    data.at[index,'Frequency'] = 0
            data.to_csv(output_file_name,index=False)
            filesToOpen.append(output_file_name)
            if createExcelCharts:
                # columns_to_be_plotted = [[1, 2]] # hard code Yi
                Excel_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                      outputFileLabel=fileNameType,
                                                      chart_type_list=chartType,
                                                      chart_title='',
                                                      column_xAxis_label_var=col,
                                                      hover_info_column_list=Hover_over_header)
                filesToOpen.append(Excel_outputFilename)
                if Excel_outputFilename != "":
                    filesToOpen.append(Excel_outputFilename)

                # # columns_to_be_plotted = [[1, 2]] # hard code Yi
                # Excel_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                #                                       outputFileLabel=fileNameType,
                #                                       chart_type_list=[chartType],
                #                                       chart_title='',
                #                                       column_xAxis_label_var=col,
                #                                       hover_info_column_list=Hover_over_header)
                # filesToOpen.append(Excel_outputFilename)
    else:
        for col in hover_col:
            temp = group_col.copy()
            temp.append(col)
            c = data.groupby(group_col)[col].apply(list).to_dict()

            container.append(c)

        temp = group_col.copy()
        temp.extend(selected_col)
        data = data.groupby(temp).size().reset_index(name='Frequency')
        for index, row in data.iterrows():
            if row[selected_col[0]] == '':
                data.at[index,'Frequency'] = 0

        hover_header = ', '.join(hover_col)
        Hover_over_header=['Hover_over: ' + hover_header]

        for index, hover in enumerate(hover_col):
            df = pd.Series(container[index]).reset_index()
            temp = group_col.copy()
            temp.append(hover)
            df.columns = temp
            data = data.merge(df, how = 'left', left_on= group_col,right_on = group_col)
        temp_str = '%s'+'\n%s'* (len(hover_col)-1)
        data['Hover_over: ' + hover_header] = data.apply(lambda x: temp_str % tuple(x[h] for h in hover_col),axis=1)
        data.drop(hover_col, axis=1, inplace=True)

        if createExcelCharts:
            # columns_to_be_plotted = [[1, 2]] # hard code Yi
            Excel_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                      outputFileLabel=fileNameType,
                                                      chart_type_list=chartType,
                                                      chart_title='',
                                                      column_xAxis_label_var=col,
                                                      hover_info_column_list=Hover_over_header)
            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)
            
        # need change, put run_all
        # if createExcelCharts:
        #     filesToOpen=charts_Excel_util.prepare_csv_data_for_chart(window,
        #                                                         inputFilename, data, outputDir,
        #                                                         selected_col,
        #                                                         Hover_over_header, group_col, fileNameType,
        #                                                         chartType,openOutputFiles, createExcelCharts)
    if openOutputFiles == 1:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
        filesToOpen=[] # empty list not to display twice

    return filesToOpen #2 files

