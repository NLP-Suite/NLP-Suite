import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "sentiment_analysis_roBERTa_util", ['os', 'transformers','csv', 'argparse', 'tkinter', 'time', 'stanza']) == False:
    sys.exit(0)

from transformers import pipeline
import os
import csv
import time
import argparse
import tkinter.messagebox as mb
from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza

import IO_csv_util
import IO_files_util
import charts_util

model_path = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

#sentiment_task = pipeline("sentiment-analysis",
                        #  model=model_path, tokenizer=model_path, max_length=512, truncation=True)
sentiment_task = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path, truncation=True)


def analyzefile(inputFilename, outputDir, outputFilename, mode, Document_ID, Document):
    """
    Performs sentiment analysis on the text file given as input using roBERTa.
    Outputs results to a new CSV file in outputDir.
    :param inputFilename: path of .txt file to analyze
    :param outputDir: path of directory to create new output file
    :param mode: determines how sentiment values for a sentence are computed (median or mean)
    :return:
    """

    # TODO
    # the output filename is reset in the specific script; must be passed as a parameter
    # cannot use time in the filename or when re-generated n the main sentimen_concreteness_analysis.py it will have a different time stamp and the file will not be found

    # read file into string
    with open(inputFilename, 'r', encoding='utf-8', errors='ignore') as myfile:
        fulltext = myfile.read()
    # end method if file is empty
    if len(fulltext) < 1:
        mb.showerror(title='File empty', message='The file ' + inputFilename +
                     ' is empty.\n\nPlease, use another file and try again.')
        print('Empty file ', inputFilename)
        return

    sentences = sent_tokenize_stanza(stanzaPipeLine(fulltext))

    i = 1

    for s in sentences:
        sentiment = sentiment_task(s)

        writer.writerow({
            Sentiment_measure: sentiment[0].get('score'),
            Sentiment_label: sentiment[0].get('label'),
            'Sentence ID': i,
            'Sentence': s,
            'Document ID': Document_ID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document)
        })

        i += 1

    return outputFilename


def main(inputFilename, inputDir, outputDir, mode, createCharts=False, chartPackage='Excel'):
    """
    Runs analyzefile on the appropriate files, provided that the input paths are valid.
    :param inputFilename:
    :param inputDir:
    :param outputDir:
    :return:

    """

    filesToOpen = []

    if len(outputDir) < 0 or not os.path.exists(outputDir):
        print('No output directory specified, or path does not exist.')
        sys.exit(1)
    elif len(inputFilename) == 0 and len(inputDir) == 0:
        print('No input specified. Please, provide either a single file -- file or a directory of files to be analyzed --dir.')
        sys.exit(1)

    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir,  outputDir, '.csv', 'roBERTa', '', '', '', '', False, True)

    # check each word in sentence for sentiment and write to output_file
    with open(outputFilename, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
        global Sentiment_measure, Sentiment_label
        Sentiment_measure = 'Sentiment score'
        Sentiment_label = 'Sentiment label'
        fieldnames = [Sentiment_measure, Sentiment_label,
                      'Sentence ID', 'Sentence', 'Document ID', 'Document']
        global writer
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        if len(inputFilename) > 0:  # handle single file
            if os.path.exists(inputFilename):
                filesToOpen.append(analyzefile(
                    inputFilename, outputDir, outputFilename, mode, 1, inputFilename))
                output_file = analyzefile(
                    inputFilename, outputDir, outputFilename, mode, 1, inputFilename)
            else:
                print('Input file "' + inputFilename + '" is invalid.')
                sys.exit(1)
        elif len(inputDir) > 0:  # handle directory
            documentID = 0
            if os.path.isdir(inputDir):
                directory = os.fsencode(inputDir)
                for file in os.listdir(directory):
                    filename = os.path.join(inputDir, os.fsdecode(file))
                    if filename.endswith(".txt"):
                        start_time = time.time()
                        # print("Started SentiWordNet sentiment analysis of " + filename + "...")
                        documentID += 1
                        filesToOpen.append(analyzefile(
                            filename, outputDir, outputFilename, mode, documentID, filename))
                        # print("Finished SentiWordNet sentiment analysis of " + filename + " in " + str((time.time() - start_time)) + " seconds")
                        # print("Finished SentiWordNet sentiment analysis of " + filename + " in " + str((time.time() - start_time)) + " seconds")
            else:
                print('Input directory "' + inputDir + '" is invalid.')
                # sys.exit(1)
    csvfile.close()

    if createCharts == True:

        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Sentiment score'],
                                                           chartTitle='Frequency of roBERTa Sentiment Scores',
                                                           count_var=0, hover_label=[],
                                                           outputFileNameType='roBERTa_scores',  # 'line_bar',
                                                           column_xAxis_label='Sentiment score',
                                                           column_yAxis_label='Scores',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Sentiment Score'],
                                                           chart_title_label='Measures of roBERTa Sentiment Scores')

        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Sentiment label'],
                                                           chartTitle='Frequency of roBERTa Sentiment Labels',
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='roBERTa_labels',  # 'line_bar',
                                                           column_xAxis_label='Sentiment label',
                                                           column_yAxis_label='Frequency',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Sentiment label'],
                                                           chart_title_label='Measures of roBERTa Sentiment Labels')

        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

    return filesToOpen


if __name__ == '__main__':
    # get arguments from command line
    parser = argparse.ArgumentParser(
        description='Sentiment analysis with BERT')
    parser.add_argument('--file', type=str, dest='inputFilename', default='',
                        help='a string to hold the INPUT path and filename if only ONE txt file is processed; enter --file "" or eliminate --file flag to process ALL txt files in input directory; use "" if path and filenames contain spaces')
    parser.add_argument('--dir', type=str, dest='inputDir', default='',
                        help='a string to hold the INPUT path of the directory of ALL txt files to be processed; use "" if path contains spaces')
    parser.add_argument('--out', type=str, dest='outputDir', default='',
                        help='a string to hold the path of the OUTPUT directory; use "" if path contains spaces')
    parser.add_argument('--outfile', type=str, dest='outputFilename', default='',
                        help='output file')

    parser.add_argument('--mode', type=str, dest='mode', default='mean',
                        help='mode with which to calculate sentiment in the sentence: mean or median')
    args = parser.parse_args()

    # run main
    sys.exit(main(args.inputFilename, args.inputDir,
             args.outputDir, args.outputFilename, args.mode))
