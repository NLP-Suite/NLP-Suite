
import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_packages(GUI_util.window, "DB_PC-ACE_data_analyzer_main.py", ['os', 'tkinter','pandas'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
import pandas as pd
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
        if ".csv" in file and len(file) > 4:
            # Strip off the .csv extension
            # tableList.append(file[:len(file) - 4])
            tableList.append(file)
    # if len(tableList) == 0:
    #     mb.showwarning(title='Warning',
    #                    message='There are no csv files in the input directory.\n\nThe script expects a set of csv files with overlapping ID fields across files in order to construct an SQLite relational database.\n\nPlease, select an input directory that contains 18 csv PC-ACE tables and try again.')
    if not "data_Document.csv" in str(tableList) and not "data_Complex.csv" in str(tableList):
        # mb.showwarning(title='Warning',
        #                message='Although the input directory does contain csv files, these files do not have the expected PC-ACE filename (e.g., data_Document, data_Complex).\n\nPlease, select an input directory that contains csv PC-ACE tables and try again.')
        tableList=[]
    return tableList

