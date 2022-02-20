# Written by Tony Chen Gu Feb 2022

from fileinput import filename
import sys
# import GUI_util
# import IO_libraries_util

# if IO_libraries_util.install_all_packages(GUI_util.window,"Excel_util",['csv','tkinter','os','collections'])==False:
#     sys.exit(0)

#import tkinter.messagebox as mb
from collections import Counter
from webbrowser import get

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os
import csv

import IO_csv_util
#import GUI_IO_util
#import IO_files_util
#import IO_user_interface_util

# if createExcelCharts:
#         columns_to_be_plotted = [[0, 1]]
#         hover_label = [2]
#         chartTitle = 'Mallet Topics'
#         xAxis = 'Topic #'
#         yAxis = 'Topic weight'
#         fileName = Keys_FileName
#         Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, fileName, outputDir,
#                                                   'Mallet_TM',
#                                                   chart_type_list=["bar"],
#                                                   chart_title=chartTitle,
#                                                   column_xAxis_label_var=xAxis,
#                                                   hover_info_column_list=hover_label,
#                                                   count_var=0,
#                                                   column_yAxis_label_var=yAxis)
#newline=''


#prepare barchart data
def prepare_data_bar(fileName, columns_to_be_plotted, hover_label):
    with open(fileName, 'r',newline='', encoding='utf-8',errors='ignore') as csvfile:
        fieldnames = columns_to_be_plotted
        data = csv.DictWriter(csvfile, fieldnames=fieldnames)
        hover = csv.DictWriter(csvfile, fieldnames=hover_label)
    return data, hover

#plot bar chart with matplotlib
def plot_bar_chart(x_label, height, fileName, outputDir, chartTitle):
    data = pd.read_csv(fileName, encoding='utf-8')
    plt.bar(data[x_label], data[height], align='center', alpha=0.5)
    plt.title(chartTitle)
    plt.xlabel(x_label)
    plt.ylabel(height)
    plt.show()
    return

# get frequencies of categorical variables
def get_frequencies(data, variable):
    #this line give a column of the counts for the categorical vairable
    #the name of row is the categorical variable
    data_count = data[variable].value_counts()
    #extract the row name = categorical variables
    data_head = data_count.index
    header = variable+"_count"
    #rebuild the dataframe with a column of categorical vairables and a column of their counts
    #the row name is still the categorical variable
    return pd.DataFrame({variable:data_head,header:data_count})

#plot bar chart with plotly
#fileName is a csv file with data to be plotted 
#x_label indicates the column name of x axis from the data
#height indicates the column name of y axis from the data
#the output file would be a html file with hover over effect names by the chart title
#duplicates allowed, would add up the counts
#Users are expected to provide the x label and their hights.
#If not call the get_frequencies function to get the frequencies of the categorical variables in x_label column
def plot_bar_chart_px(x_label, fileName, outputDir, chartTitle, height = None):
    data = pd.read_csv(fileName, encoding='utf-8')
    if height is None:
        height = x_label+"_count"
        data = get_frequencies(data, x_label)
    fig = px.bar(data,x=x_label,y=height)
    fig.update_layout(title=chartTitle, title_x=0.5)
    fig.show()
    savepath = os.path.join(outputDir, chartTitle + '.html')
    fig.write_html(savepath)
    return

#plot pie chart with plotly
#fileName is a csv file with data to be plotted 
#x_label indicates the column name of x axis from the data
#height indicates the column name of y axis from the data
#the output file would be a html file with hover over effect names by the chart title
#duplicates allowed, would add up the counts
def plot_pie_chart_px(x_label, fileName, outputDir, chartTitle, height = None):
    data = pd.read_csv(fileName, encoding='utf-8')
    fig = px.pie(data, values=height, names=x_label)
    fig.update_layout(title=chartTitle, title_x=0.5)
    fig.show()
    savepath = os.path.join(outputDir, chartTitle + '.html')
    #fig.write_html(savepath)
    return

#plot scatter chart with plotly
#fileName is a csv file with data to be plotted
#x_label indicates the column name of x axis from the data    COULD BE A DISCRETE VARIABLE
#y_label indicates the column name of y axis from the data    COULD BE A DISCRETE VARIABLE
#the output file would be a html file with hover over effect names by the chart title
def plot_scatter_chart_px(x_label, y_label, fileName, outputDir, chartTitle):
    data = pd.read_csv(fileName, encoding='utf-8')
    fig = px.scatter(data, x=x_label, y=y_label)
    fig.update_layout(title=chartTitle, title_x=0.5)
    fig.show()
    savepath = os.path.join(outputDir, chartTitle + '.html')
    #fig.write_html(savepath)
    return

#plot scatter chart with plotly
#fileName is a csv file with data to be plotted
#theta_label indicates the column name of the "feature" from the data    SHOULD BE A DISCRETE VARIABLE
#r_label indicates the column name of the value of the feature from the data    CANNOT BE A DISCRETE VARIABLE
#the output file would be a html file with hover over effect names by the chart title
def plot_radar_chart_px(theta_label, r_label, fileName, outputDir, chartTitle):
    data = pd.read_csv(fileName, encoding='utf-8')
    fig = px.line_polar(data, r=r_label, theta=theta_label, line_close=True)
    fig.update_layout(title=chartTitle, title_x=0.5)
    fig.show()
    savepath = os.path.join(outputDir, chartTitle + '.html')
    #fig.write_html(savepath)
    return

#=======================================================================================================================
#debug use
def main():
    x_label = 'char'
    height = 'count'
    hover_label = 'count'
    chartTitle = 'test chart'
    fileName =  'C:/Users/Tony Chen/Desktop/NLP_working/Test Input/bar_test_data.csv'
    outputDir = 'D:/'
    #plot_bar_chart(x_label, height, fileName, outputDir, chartTitle, hover_label)
    plot_bar_chart_px(x_label,fileName, outputDir, chartTitle, height = height)

if __name__ == "__main__":
    main()
