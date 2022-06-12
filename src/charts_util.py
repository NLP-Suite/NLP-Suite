# Written by Yuhang Feng November 2019-April 2020
# Written by Yuhang Feng November 2019-April 2020
# Edited by Roberto Franzosi, Tony May 2022

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"charts_Excel_util",['csv','tkinter','os','collections','openpyxl'])==False:
    sys.exit(0)

import tkinter.messagebox as mb
from collections import Counter

import pandas as pd

import IO_csv_util
import IO_user_interface_util
import charts_Excel_util
import charts_plotly_util
import charts_util
import statistics_csv_util

# Prepare the data (data_to_be_plotted) to be used in charts_Excel_util.create_excel_chart with the format:
#   the variable has this format:
# (['little, pig', 22])
#   one serie: [[['Name1','Frequency'], ['A', 7]]]
#   two series: [[['Name1','Frequency'], ['A', 7]], [['Name2','Frequency'], ['B', 4]]]
#   three series: [[['Name1','Frequency'], ['A', 7]], [['Name2','Frequency'], ['B', 4]], [['Name3','Frequency'], ['C', 9]]]
#   more series: ..........
# inputFilename has the full path
# columns_to_be_plotted is a double list [[0, 1], [0, 2], [0, 3]]
# TODO HOW DOES THIS DIFFER FROM def prepare_csv_data_for_chart?
def prepare_data_to_be_plotted(inputFilename, columns_to_be_plotted, chart_type_list,
                               count_var=0, column_yAxis_field_list = []):
    withHeader_var = IO_csv_util.csvFile_has_header(inputFilename) # check if the file has header
    data, headers = IO_csv_util.get_csv_data(inputFilename,withHeader_var) # get the data and header
    if len(data)==0:
        return None
    headers=list(headers)
    count_msg, withHeader_msg = build_timed_alert_message(chart_type_list[0],withHeader_var,count_var)
    if count_var == 1:
        dataRange = get_dataRange(columns_to_be_plotted, data)
        # TODO hover_over_values not being passed, neither are any potential aggregate columns
        #   get_data_to_be_plotted_with_counts is less general than
        data_to_be_plotted = get_data_to_be_plotted_with_counts(inputFilename,withHeader_var,headers,columns_to_be_plotted,column_yAxis_field_list,dataRange)
    else:
        try:
            data = pd.read_csv(inputFilename,encoding='utf-8')
        except:
            try:
                data = pd.read_csv(inputFilename,encoding='ISO-8859-1')
                IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Warning',
                                                   'Excel-util encountered errors with utf-8 encoding and switched to ISO-8859-1 in reading into pandas the csv file ' + inputFilename)
                print("Excel-util encountered errors with utf-8 encoding and switched to ISO-8859-1 encoding in reading into pandas the csv file " + inputFilename)
            except ValueError as err:
                if 'codec' in str(err):
                    err=str(err) + '\n\nExcel-util encountered errors with both utf-8 and ISO-8859-1 encoding in the function \'prepare_data_to_be_plotted\' while reading into pandas the csv file\n\n' + inputFilename + '\n\nPlease, check carefully the data in the csv file; it may contain filenames with non-utf-8/ISO-8859-1 characters; less likely, the data in the txt files that generated the csv file may also contain non-compliant characters. Run the utf-8 compliance algorithm and, perhaps, run the cleaning algorithm that converts apostrophes.\n\nNO EXCEL CHART PRODUCED.'
                mb.showwarning(title='Input file read error',
                       message=str(err))
                return
        data_to_be_plotted = get_data_to_be_plotted_NO_counts(inputFilename,withHeader_var,headers,columns_to_be_plotted,data)
    return data_to_be_plotted

# columns_to_be_plotted_bar, columns_to_be_plotted_bySent, columns_to_be_plotted_byDoc
#   all double lists [[]]
# the variable groupByList,plotList, chart_label are used to compute column statistics
def visualize_chart(createCharts,chartPackage,inputFilename,outputDir,
                    columns_to_be_plotted_bar, columns_to_be_plotted_bySent, columns_to_be_plotted_byDoc,
                    chartTitle, count_var, hover_label, outputFileNameType, column_xAxis_label,groupByList,plotList, chart_label):
    if createCharts == True:
        filesToOpen=[]
        # standard bar chart ------------------------------------------------------------------------------
        if len(columns_to_be_plotted_bar[0])>0: # compute only if the double list is not empty
            chart_outputFilename = run_all(columns_to_be_plotted_bar, inputFilename, outputDir,
                                                      outputFileLabel=outputFileNameType,
                                                      chartPackage=chartPackage,
                                                      chart_type_list=['bar'],
                                                      chart_title=chartTitle,
                                                      column_xAxis_label_var=column_xAxis_label,
                                                      hover_info_column_list=hover_label,
                                                      count_var=1)

            if chart_outputFilename!=None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.append(chart_outputFilename)

        # bar charts by document
        # # document value are the second item in the list [[3,2]] i.e. 2
        if len(columns_to_be_plotted_byDoc[0])>0: # compute only if the double list is not empty
            chart_outputFilename = run_all(columns_to_be_plotted_byDoc, inputFilename, outputDir,
                                                      outputFileLabel='ByDoc',
                                                      chartPackage=chartPackage,
                                                      chart_type_list=['bar'],
                                                      chart_title=chartTitle + ' by Document',
                                                      column_xAxis_label_var='',
                                                      hover_info_column_list=hover_label,
                                                      count_var=1,
                                                      remove_hyperlinks=True)

            if chart_outputFilename!=None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.append(chart_outputFilename)

        # line plots by sentence index
        # # values to be plotted are the first item in the list [[3,2]] i.e. 3
        if len(columns_to_be_plotted_bySent[0])>0: # compute only if the double list is not empty
            chart_outputFilename = run_all(columns_to_be_plotted_bySent, inputFilename, outputDir,
                                                      outputFileLabel='BySent',
                                                      chartPackage=chartPackage,
                                                      chart_type_list=['line'],
                                                      chart_title=chartTitle + ' by Sentence Index',
                                                      column_xAxis_label_var='Sentence index',
                                                      hover_info_column_list=hover_label,
                                                      count_var=0,
                                                      complete_sid=True)

            if chart_outputFilename!=None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.append(chart_outputFilename)

        # compute field statistics;
        # THE FIELD MUST CONTAIN NUMERIC VALUES
        # plotList (a list []) contains the columns headers to be used to compute their stats
        if len(groupByList)>0: # compute only if list is not empty
            tempOutputfile = statistics_csv_util.compute_csv_column_statistics(GUI_util.window, inputFilename, outputDir,
                                                                               groupByList, plotList, chart_label,
                                                                               createCharts,
                                                                               chartPackage)

            if tempOutputfile != None:
                filesToOpen.extend(tempOutputfile)

    return filesToOpen

# best approach when all the columns to be plotted are already in the file
#   otherwise, use statistics_csv_util.compute_csv_column_frequencies
# only one hover-over column per series can be selected
# each series plotted has its own hover-over column
#   if the column is the same (e.g., sentence), this must be repeated as many times as there are series 

# columns_to_be_plotted is a double list [[0, 1], [0, 2], [0, 3]] where the first number refers to the x-axis value and the second to the y-axis value
# when count_var=1 the second number gets counted
# the complete sid need to be tested as na would be filled with 0
def run_all(columns_to_be_plotted,inputFilename, outputDir, outputFileLabel,
            chartPackage, chart_type_list,chart_title, column_xAxis_label_var,
            hover_info_column_list=[],
            count_var=0,
            column_yAxis_label_var='Frequencies',
            column_yAxis_field_list = [],
            reverse_column_position_for_series_label=False,
            series_label_list=[], second_y_var=0,second_yAxis_label='', complete_sid = False, remove_hyperlinks=False):

    use_plotly = 'plotly' in chartPackage.lower()
    # added by Tony, May 2022 for complete sentence index
    # the file should have a column named Sentence ID
    # the extra parameter "complete_sid" is set to True by default to avoid extra code mortification elsewhere
    if complete_sid:
        complete_sentence_index(inputFilename)
    if use_plotly:
        # def create_plotly_chart(inputFilename,outputDir,chartTitle,chart_type_list,cols_to_plot,
        #                 column_xAxis_label='',
        #                 column_yAxis_label='',
        #                 static_flag=False,):
        Plotly_outputFilename = charts_plotly_util.create_plotly_chart(inputFilename = inputFilename,
                                                                        outputDir = outputDir,
                                                                        chartTitle = chart_title,
                                                                        chart_type_list = chart_type_list,
                                                                        cols_to_plot = columns_to_be_plotted,
                                                                        column_xAxis_label = column_xAxis_label_var,
                                                                        column_yAxis_label = column_yAxis_label_var,
                                                                        remove_hyperlinks = remove_hyperlinks)
        return Plotly_outputFilename
    
    data_to_be_plotted = prepare_data_to_be_plotted(inputFilename,
                                columns_to_be_plotted,
                                chart_type_list,count_var,
                                column_yAxis_field_list)
    if data_to_be_plotted==None:
            return ''

    transform_list = []
    # the following is deciding which type of data is returned from prepare_data_to_be_plotted
    # for the function prepare_data_to_be_plotted branch into two different data handling functions which returns different data type
    # and due to complexity reasons, we keep them in this way:
    # check the data type for the return value and decide which step to take next
    if not(isinstance(data_to_be_plotted[0], list)):
        for df in data_to_be_plotted:
            header = list(df.columns)
            data = df.values.tolist()
            data.insert(0,header)
            transform_list.append(data)
            data_to_be_plotted=transform_list
    if data_to_be_plotted==None:
            chart_outputFilename = ""
    else:
        chart_title = chart_title
        chart_outputFilename = charts_Excel_util.create_excel_chart(GUI_util.window, data_to_be_plotted, inputFilename, outputDir,
                                                  outputFileLabel, chart_title, chart_type_list,
                                                  column_xAxis_label_var, column_yAxis_label_var,
                                                  hover_info_column_list,
                                                  reverse_column_position_for_series_label,
                                                  series_label_list, second_y_var, second_yAxis_label)
    return chart_outputFilename

#sortOrder = True (descending 3, 2, 1)
#sortOrder = False (ascending 1, 2, 3)
def sort_data (ExcelChartData, sortColumn,sortOrder):
    sorted_data = sorted(ExcelChartData, key=lambda tup:tup[sortColumn],reverse=sortOrder)
    return sorted_data

def build_timed_alert_message(chart_type,withHeader_var,count_var):
    if withHeader_var==1:
        withHeader_msg='WITH HEADERS'
    else:
        withHeader_msg='WITHOUT HEADERS'
    if count_var==1:
        count_msg='WITH COUNTS'
    else:
        count_msg='WITHOUT COUNTS'
    return withHeader_msg, count_msg

def get_hover_column_numbers(withHeader_var,headers,hover_info_column_list):
    hover_column_numbers = []
    
    for i in range(len(hover_info_column_list)): # iterate n times (i.e., len(selected_series), where n is the number of series
        if withHeader_var==1:
            if hover_info_column_list[i] in headers:
                x=headers.index(hover_info_column_list[i])
            else:
                if len(hover_info_column_list[i]) > 0:
                    mb.showwarning(title='Series No.'+ str(i+1) + ' ' + hover_info_column_list[i] + 'Hover Data Warning', message='The hover-over data column for series No.' + str(i+1) + ' will be empty.\n\nYou may have entered a column name which does not exist in the input CSV file.\n\nPlease, exit the program, check your input and try again.')
                x=-1
            # y=headers.index(selected_series[i][1])
        else: #NO headers
            try:
                x=int(hover_info_column_list[i])
            except:
                mb.showwarning(title='Series No.'+ str(i+1) + ' ' + hover_info_column_list[i] +' Hover Data Header', message='The input csv file has no header so the expected hover-over column header should be numbers(o for A, 1 for B,...) but the ENTERED hover-over data column for series No.' + str(i+1) + ' is not a number.\n\nPlease, exit the program, check your input and try again.')
                return
        hover_column_numbers.append(x)
    return hover_column_numbers


# split the pairs of gui x y values into two separate lists of x axis values and y axis value
def get_xaxis_yaxis_values(columns_to_be_plotted):
    x = [a[0] for a in columns_to_be_plotted] # select all the x axis number and put them in a list
    y = [a[1] for a in columns_to_be_plotted] # select all the y axis number and put them in a list
    x1 = [ int(b) for b in x ]  # convert them into int type
    y1 = [ int(b) for b in y]  # convert them into int type
    return x1, y1

def get_dataRange(columns_to_be_plotted, data):
    dataRange = []
    for i in range(len(columns_to_be_plotted)):
        for row in data:
            rowValues = list(row[w] for w in columns_to_be_plotted[i])
            dataRange.append(rowValues)
    dataRange = [ dataRange [i:i + len(data)] for i in range(0, len(dataRange), len(data)) ]
    return dataRange

# TODO if hover_over columns are passed, it should concatenate all values, instead of displaying the first one only
#   (e.g. an example run the going UP function in WordNet)
# this function seems to be less general than def compute_csv_column_frequencies; that function handl;es aggregation and hover over effects
# we should consolidate the two and use the most general one under he heading get_data_to_be_plotted_with_counts

# def get_data_to_be_plotted_with_counts(inputFileName,withHeader_var,headers,columns_to_be_plotted,column_yAxis_field_list,dataRange):
#     CALL compute_column_frequencies(columns_to_be_plotted, dataRange, headers,column_yAxis_field_list)
#
#     CALLED compute_column_frequencies(columns_to_be_plotted, data_list, headers,specific_column_value_list=[]):


# -----------------------------------------------------------------
# MUST COMPUTE HOVER OVER VALUES!!! see below

# create a list of unique words to be displayed in hover over
# result = IO_files_util.openCSVFile(outputFilenameCSV1, 'r', 'utf-8')
# DataCaptured = csv.reader(result)
# words = set()
# for row in DataCaptured:
#     words.add(row[0])
# also IO_csv_util.get_csv_field_values(inputfile_name, column_name)

def get_data_to_be_plotted_with_counts(inputFilename,withHeader_var,headers,columns_to_be_plotted,specific_column_value_list,data_list):
    data_to_be_plotted=[]
    # data_to_be_plotted = compute_column_frequencies_4Excel(columns_to_be_plotted, dataRange, headers, column_yAxis_field_list)

    column_list=[]
    column_frequencies=[]
    column_stats=[]
    specific_column_value=''
    complete_column_frequencies=[]
    if len(data_list) != 0:
        for k in range(len(columns_to_be_plotted)):
            res=[]
            if len(specific_column_value_list)>0:
                specific_column_value=specific_column_value_list[k]
            #get all the values in the selected column
            column_list = [i[1] for i in data_list[k]]
            counts = Counter(column_list).most_common()
            if len(headers) > 0:
                id_name_num = columns_to_be_plotted[k][0]
                id_name = headers[id_name_num]
                column_name_num = columns_to_be_plotted[k][1]
                column_name = headers[column_name_num]
                if len(specific_column_value_list)==0:
                    column_frequencies = [[column_name + " values", "Frequencies of " + column_name]]
                else:
                    for y in range(len(specific_column_value_list)):
                        column_frequencies = [[id_name, "Frequencies of " + str(specific_column_value) + " in Column " + str(column_name)]]
            else:
                id_name_num = columns_to_be_plotted[k][0]
                id_name = "column_" + str(id_name_num+1)
                column_name_num = columns_to_be_plotted[k][1]
                column_name = "column_" + str(column_name_num+1)
                if len(specific_column_value)==0:
                    column_frequencies = [[column_name + " values", "Frequencies of " + column_name]]
                else:
                    for y in range(len(specific_column_value_list)):
                        column_frequencies = [[id_name, "Frequencies of " + str(specific_column_value) + " in Column_" + str(column_name_num+1)]]
            if len(specific_column_value) == 0:
                for value, count in counts:
                    column_frequencies.append([value, count])
            else:
                for i in range(len(column_list)):
                    if column_list[i] == specific_column_value:
                        res.append(1)
                    else:
                        res.append(0)
                for j in range(len(data_list[k])):
                    column_frequencies.append([data_list[k][j][0], res[j]])
            data_to_be_plotted.append(column_frequencies)

    return data_to_be_plotted

# [[0,2]], [0], [2]
def get_data_to_be_plotted_NO_counts(inputFilename,withHeader_var,headers,columns_to_be_plotted,data):
    data_to_be_plotted=[]
    for gp in columns_to_be_plotted:
        data.iloc[:, gp[1]].replace('N/A', 0)
        # data.iloc[:, gp[1]].astype('float')
        tempData=data.iloc[:,gp]
        data_to_be_plotted.append(data.iloc[:,gp])
    return data_to_be_plotted


# Tony Chen Gu written at April 2022 mortified at May 2022
# remove comments before variable begin with d_id to enable complete document id function
# need to have a document id column and sentence id column
# would complete the file (make document id and sentence id continuous) and padding zero values for the added rows
def complete_sentence_index(file_path):
    data = pd.read_csv(file_path)
    try:
        print(data["Sentence ID"])
    except:
        print("Only enable complete sentence index when there is a Sentence ID column in the csv file")
        return
    if(len(data) == 1):
        return data
    max_sid = max(data["Sentence ID"])+1
    sid_list = list(range(1, max_sid))
    df_sid = pd.DataFrame (sid_list, columns = ['Sentence ID'])
    # use merge to accelerate the process
    data = data.merge(right = df_sid, how = "right", on = "Sentence ID")
    data = data.fillna(0)
    data.to_csv(file_path, index = False)
    return

# when hover-over data (Labels) are displayed the Excel filename extension MUST be xlsm (for macro VBA enabling)
def prepare_hover_data(inputFilename, hover_info_column, index):
    hover_data = []
    withHeader_var = IO_csv_util.csvFile_has_header(inputFilename) # check if the file has header
    data, headers = IO_csv_util.get_csv_data(inputFilename,withHeader_var) # get the data and header
    if withHeader_var:
        if hover_info_column >= 0:
            hover_data.append([headers[hover_info_column]])
        else:
            hover_data.append(['Hover-over data for series ' + str(index+1)])
    else:
        hover_data.append(['Hover-over data for series ' + str(index+1)])


    for i in range(len(data)):
        if hover_info_column >= 0:
            hover_data.append([data[i][hover_info_column]])
        else:
            hover_data.append([''])
        # print("hover_data",hover_data)
    return hover_data

#data_to_be_plotted contains the values to be plotted
#   the variable has this format:
#   this includes both headers AND data
#   one series: [[['Name1','Frequency'], ['A', 7]]]
#   two series: [[['Name1','Frequency'], ['A', 7]], [['Name2','Frequency'], ['B', 4]]]
#   three series: [[['Name1','Frequency'], ['A', 7]], [['Name2','Frequency'], ['B', 4]], [['Name3','Frequency'], ['C', 9]]]
#   more series: ..........
#chartTitle is the name of the sheet
#num_label number of bars, for instance, that will be displayed in a bar chart 
#second_y_var is a boolean that tells the function whether a second y axis is needed 
#   because it has a different scale and plotted values would otherwise be "masked"
#   ONLY 2 y-axes in a single chart are allowed by openpyxl
#chart_type_list is in form ['line', 'line','bar']... one for each of n series plotted
#when called from scripts other than Excel_charts, the list can be of length 1 although more series may be plotted
#   in which case values are filled below
#output_file_name MUST be of xlsx type, rather tan csv

# when NO hover-over data are displayed the Excel filename extension MUST be xlsx and NOT xlsm (becauuse no macro VBA is enabled in this case)

def df_to_list_w_header(df):
    res = []
    header = list(df.columns)
    res.append(header)
    for index, row in df.iterrows():
        temp = [row[tag] for tag in header]
        res.append(temp)
    return res


def df_to_list(df):
    res = []
    header = list(df.columns)
    for index, row in df.iterrows():
        temp = [row[tag] for tag in header]
        res.append(temp)
    return res


def list_to_df(tag_list):
    header = tag_list[0]
    df = pd.DataFrame(tag_list[1:], columns=header)
    return df


def header_check(inputFile):
    sentenceID_pos=''
    docID_pos=''
    docName_pos=''

    if isinstance(inputFile, pd.DataFrame):
        header = list(inputFile.columns)
    else:
        header = IO_csv_util.get_csvfile_headers(inputFile)
    if 'Sentence ID' in header:
        sentenceID_pos = header.index('Sentence ID')
    else:
        pass

    if 'Document ID' in header:
        docID_pos = header.index('Document ID')
    else:
        pass

    if 'Document' in header:
        docName_pos = header.index('Document')
    else:
        pass
    return sentenceID_pos, docID_pos, docName_pos, header


# input can be a csv filename or a dataFrame
# output is a dataFrame
# TODO any funtion that plots data by sentence index should really check that the required sentence IDs are all there and insert them otherwise
def add_missing_IDs(input):
    if isinstance(input, pd.DataFrame):
        df = input
    else:
        df = pd.read_csv(input)
    sentenceID_pos, docID_pos, docName_pos, header = header_check(input)
    Row_list = df_to_list(df)
    for index,row in enumerate(Row_list):
        if index == 0 and Row_list[index][sentenceID_pos] != 1:
            for i in range(Row_list[index][sentenceID_pos]-1,0,-1):
                temp= [''] * len(header)
                for j in range(len(header)):
                    if j == sentenceID_pos:
                        temp[j] = i
                    elif j == docID_pos:
                        temp[j] = Row_list[index][docID_pos]
                    elif j == docName_pos:
                        temp[j] = Row_list[index][docName_pos]
                Row_list.insert(0,temp)
        else:
            if index < len(Row_list)-1 and Row_list[index+1][sentenceID_pos] - Row_list[index][sentenceID_pos] > 1:
                for i in range(Row_list[index+1][sentenceID_pos]-1,Row_list[index][sentenceID_pos],-1):
                    temp = [''] * len(header)
                    for j in range(len(header)):
                        if j == sentenceID_pos:
                            temp[j] = i
                        elif j == docID_pos:
                            temp[j] = Row_list[index][docID_pos]
                        elif j == docName_pos:
                            temp[j] = Row_list[index][docName_pos]
                    Row_list.insert(index+1,temp)
    df = pd.DataFrame(Row_list,columns=header)
    return df


def sort_by_column(input, column):
    if isinstance(input, pd.DataFrame):
        df = input
    else:
        df = pd.read_csv(input)
    col_list = set(df[column].tolist())
    df_list = [df[df[column] == value] for value in col_list]
    return df_list


def align_dataframes(df_list):
    max = 0
    for df in df_list:
        header = list(df.columns)
        if 'Sentence ID' in header:
            sentenceID = 'Sentence ID'
        if df[sentenceID].max() > max:
            max = df[sentenceID].max()
    new_list = []
    for df in df_list:
        if df.empty:
            continue
        temp = df.iloc[-1,:]
        if temp[sentenceID] != max:
            # TODO solve warning issue
            # https://www.dataquest.io/blog/settingwithcopywarning/
            # ​​​​SettingwithCopyWarning
            temp[sentenceID] = max
            temp['Frequency'] = 0
            new_df = df.append(temp,ignore_index=True)
        else:
            new_df = df
        new_list.append(new_df)

    df_list = [add_missing_IDs(data) for data in new_list if not data.empty]
    return df_list


def slicing_dataframe(df,columns):
    df = df[columns]
    return df


def rename_df(df,col):
    for index, row in df.iterrows():
        if row[col] != '':
            name = row[col]
            break
    df.rename(columns={"Frequency": name + " Frequency"},inplace=True)
    df = df.drop(columns=[col])
    return df
