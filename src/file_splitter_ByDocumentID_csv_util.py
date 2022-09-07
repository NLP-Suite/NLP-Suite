# Tony Mar 24 2022
# edited Roberto April 2022

import pandas as pd
import os
import IO_files_util
import tkinter.messagebox as mb

# split the csv file by document ID
# should at least contain a column called 'Document ID'
# the script would group by it and then save them separately
def split_NLP_Suite_csv_output_by_document_id(inputFilename,outputDir):
    df = pd.read_csv(inputFilename)
    head, tail = os.path.split(inputFilename)
    base_name = tail[:-4] + "_Document_"
    grouped = df.groupby(['Document ID'])
    # create a subdirectory in the output directory
    inputDir = ''
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='split_csv', silent=True)
    if outputDir == '':
        return
    for name, group in grouped:
        outFilename = os.path.join(outputDir, base_name + str(name) + '.csv')
        group.to_csv(outFilename, encoding='utf-8', index=False)
    mb.showwarning(title='Warning',
                   message="The 'split by Document ID' function created " + str(grouped.ngroups) + ' split csv files in the output directory ' + outputDir)
    return

