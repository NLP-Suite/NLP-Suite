# Written by Tony Chen Gu

from fileinput import filename
import sys
# import GUI_util
# import IO_libraries_util

# if IO_libraries_util.install_all_packages(GUI_util.window,"Excel_util",['csv','tkinter','os','collections'])==False:
#     sys.exit(0)

#import tkinter.messagebox as mb
from collections import Counter

import pandas as pd
import matplotlib.pyplot as plt
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

def plot_bar_chart(x_label, height, fileName, outputDir, chartTitle, hover_label):
    data = pd.read_csv(fileName, encoding='utf-8')
    plt.bar(data[x_label], data[height], align='center', alpha=0.5)
    plt.show()
    return

#debug use
def main():
    x_label = 'char'
    height = 'count'
    hover_label = 'count'
    chartTitle = 'test chart'
    fileName =  'C:/Users/Tony Chen/Desktop/NLP_working/Test Input/bar_test_data.csv'
    outputDir = 'd:/'
    plot_bar_chart(x_label, height, fileName, outputDir, chartTitle, hover_label)

if __name__ == "__main__":
    main()
