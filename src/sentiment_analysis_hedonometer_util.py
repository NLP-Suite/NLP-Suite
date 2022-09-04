"""
Author: Doris Zhou September 29, 2017
Modified by Gabriel Wang May 2018
Modified by Roberto Franzosi February 2019
Modified by Josh Karol October 2019

Performs sentiment analysis on a text file using Hedonometer; needs the file hedonometer.json
Works best  with social media texts, NY Times editorials, movie reviews, and product reviews.

#The structure of the json file has the format explained here
#https://hedonometer.org/words.html

Parameters:
    --dir [path of directory]
        specifies directory of files to analyze
    --file [path of text file]
        specifies location of specific file to analyze
    --out [path of directory]
        specifies directory to create output files
    --mode [mode]
        takes either "median" or "mean"; determines which is used to calculate sentence sentiment values
"""
# add parameter to exclude duplicates? also mean or median analysis

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Sentiment Analysis HEDONOMETER",['stanza','json','os','csv','argparse','tkinter','time'])==False:
    sys.exit(0)

import os
import csv
import json
import statistics
import time
import argparse
import tkinter.messagebox as mb
from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza

import IO_csv_util
import GUI_IO_util
import charts_util
import IO_files_util

fin = open('../lib/wordLists/stopwords.txt', 'r')
stops = set(fin.read().splitlines())
database = GUI_IO_util.sentiment_libPath + os.sep + "hedonometer.json"
if not os.path.isfile(database):
    print("The file './lib/hedonometer.json' could not be found. The hedonemeter sentiment analysis routine expects a JSON dictionary file 'hedonometer.json' in a directory 'lib' expected to be a subdirectory of the directory where the sentiment_analysis_hedonometer.py script is stored.\n\nPlease, check your lib directory and try again.")
    sys.exit()

parsed_data = json.load(open(database))

# performs sentiment analysis on inputFile using the hedonometer database, outputting results to a new CSV file in outputDir
def analyzefile(inputFilename, outputDir, outputFilename, mode, Document_ID, Document):
    """
    Performs sentiment analysis on the text file given as input using the Hedonometer database.
    Outputs results to a new CSV file in outputDir.
    :param inputFilename: path of .txt file to analyze
    :param outputDir: path of directory to create new output file
    :param mode: determines how sentiment values for a sentence are computed (median or mean)
    :return:
    """
    #TODO
    #the output filename is reset in the specific script; must be passed as a parameter
    #cannot use time in the filename or when re-generated n the main sentimen_concreteness_analysis.py it will have a different time stamp and the file will not be found
    # read file into string
    with open(inputFilename, 'r',encoding='utf-8',errors='ignore') as myfile:
        fulltext = myfile.read()
    # end method if file is empty
    if len(fulltext) < 1:
        mb.showerror(title='File empty', message='The file ' + inputFilename + ' is empty.\n\nPlease, use another file and try again.')
        print('Empty file ', inputFilename)
        return

    # otherwise, split into sentences
    # sentences = tokenize.sent_tokenize(fulltext)
    sentences = sent_tokenize_stanza(stanzaPipeLine(fulltext))

    i = 1 # to store sentence index
    # check each word in sentence for sentiment and write to outputFilename
    # analyze each sentence for sentiment
    for s in sentences:
        # print("S" + str(i) +": " + s)
        found_words = []
        total_words = 0
        v_list = []  # holds valence scores

        # search for each valid word's sentiment in hedonometer database
        # words = word_tokenize(s.lower())
        words = word_tokenize_stanza(stanzaPipeLine(s.lower()))
        filtered_words = [word for word in words if word.isalpha()]  # strip out words with punctuation
        for index, w in enumerate(filtered_words):
            # don't process stops
            if w in stops:
                continue

            # check for negation in 3 words before current word
            neg = False
            j = index-1
            while j >= 0 and j >= index-3:
                if filtered_words[j] == 'not' or filtered_words[j] == 'no':
                    neg = True
                j -= 1

            # lemmatize word
            # lmtzr = WordNetLemmatizer()
            # lemma = lmtzr.lemmatize(w, pos='v')
            # if lemma == w:
            #     lemma = lmtzr.lemmatize(w, pos='n')
            lemma = lemmatize_stanza(stanzaPipeLine(w))

            total_words += 1

            # search for lemmatized word in database
            for record in parsed_data["objects"]:
                if record["word"] == lemma.casefold():
                    v_list.append(record["happs"])
                    found_words.append(lemma)


        if len(found_words) == 0:  # no words found for this sentence
            writer.writerow({
                            # Sentiment_measure: 0,
                            # Sentiment_label: "",
                            'Sentiment score (Mean)': 0,
                            'Sentiment label (Mean)': "",
                            'Sentence ID': i,
                            'Sentence': s,
                            'Document ID': Document_ID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document)
                            })
            i += 1
            continue
        else:  # output sentiment info for this sentence

            # set sentiment label
            label_mean = 'neutral'
            label_median = 'neutral'
            if mode == 'mean' or mode == 'both':
                sentiment_mean = statistics.mean(v_list)
                sentiment=sentiment_mean
                if sentiment > 7.5 :
                    label_mean = 'very positive'
                elif sentiment > 6:
                    label_mean = 'positive'
                elif sentiment < 4.5:
                    label_mean = 'negative'
                elif sentiment < 2.5:
                    label_mean = 'very negative'
                else:
                    label_mean = "neutral"
            if mode == 'median' or mode == 'both':
                sentiment_median = statistics.median(v_list)
                sentiment=sentiment_median
                if sentiment > 7.5 :
                    label_median = 'very positive'
                elif sentiment > 6:
                    label_median = 'positive'
                elif sentiment < 4.5:
                    label_median = 'negative'
                elif sentiment < 2.5:
                    label_median = 'very negative'
                else:
                    label_median = "neutral"

            if mode == 'mean':
                writer.writerow({
                                 'Sentiment score (Mean)': sentiment_mean,
                                 'Sentiment label (Mean)': label_mean,
                                 'Found Words': ("%d out of %d" % (len(found_words), total_words)),
                                 'Word List': ', '.join(found_words),
                                 'Sentence ID': i,
                                 'Sentence': s,
                                 'Document ID': Document_ID,
                                 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document)
                })
            elif mode == 'median':
                writer.writerow({'Sentiment score (Median)':sentiment_median,
                                 'Sentiment label (Median)': label_median,
                                 'Found Words': ("%d out of %d" % (len(found_words), total_words)),
                                 'Word List': ', '.join(found_words),
                                 'Sentence ID': i,
                                 'Sentence': s,
                                 'Document ID': Document_ID,
                                 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document)
                                 })
            elif mode == 'both':
                writer.writerow({
                                 'Sentiment score (Mean)': sentiment_mean,
                                 'Sentiment label (Mean)': label_mean,
                                 'Sentiment score (Median)': sentiment_median,
                                 'Sentiment label (Median)': label_median,
                                 'Found Words': ("%d out of %d" % (len(found_words), total_words)),
                                 'Word List': ', '.join(found_words),
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

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'Hedo',
                                                                 '', '', '', '', False, True)

    if len(outputDir) < 0 or not os.path.exists(outputDir):  # empty output
        print('No output directory specified, or path does not exist')
        sys.exit(0)
    elif len(inputFilename) == 0 and len(inputDir)  == 0:  # empty input
        print('No input specified. Please give either a single file or a directory of files to analyze.')
        sys.exit(1)

    with open(outputFilename, 'w', encoding='utf-8',errors='ignore', newline='') as csvfile:
        if (mode == 'both'):
            fieldnames = ['Sentiment score (Mean)', 'Sentiment label (Mean)','Sentiment score (Median)', 'Sentiment label (Median)', 'Found Words', 'Word List', 'Sentence ID', 'Sentence','Document ID', 'Document']
        else:
            if mode == 'mean':
                fieldnames = ['Sentiment score (Mean)', 'Sentiment label (Mean)', 'Found Words', 'Word List', 'Sentence ID', 'Sentence','Document ID', 'Document']
            elif mode == 'median':
                fieldnames = ['Sentiment score (Median)', 'Sentiment label (Median)', 'Found Words', 'Word List', 'Sentence ID', 'Sentence','Document ID', 'Document']
        global writer
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()


        if len(inputFilename) > 0:  # handle single file
            if os.path.exists(inputFilename):
                filesToOpen.append(analyzefile(inputFilename, outputDir, outputFilename, mode, 1, inputFilename))
                analyzefile(inputFilename, outputDir, outputFilename, mode, 1, inputFilename)
            else:
                print('Input file "' + inputFilename + '" is invalid.')
                sys.exit(0)
        elif len(inputDir) > 0:  # handle directory
            if os.path.isdir(inputDir):
                directory = os.fsencode(inputDir)
                Document_ID = 0
                for file in os.listdir(directory):
                    filename = os.path.join(inputDir, os.fsdecode(file))
                    if filename.endswith(".txt"):
                        start_time = time.time()
                        # print("Started HEDONOMETER sentiment analysis of " + filename + "...")
                        Document_ID += 1
                        filesToOpen.append(analyzefile(filename, outputDir, outputFilename,mode, Document_ID, filename)) #LINE ADDED (edited)
                        # print("Finished HEDONOMETER sentiment analysis of " + filename + " in " + str((time.time() - start_time)) + " seconds")
            else:
                print('Input directory "' + inputDir + '" is invalid.')
                sys.exit(1)
    csvfile.close()

    if createCharts == True:
        if mode == "both":
            columns_to_be_plotted = ['Sentiment score (Mean)', 'Sentiment score (Median)']
            # hover_label = ['Sentence', 'Sentence']
        elif mode == "mean":
            columns_to_be_plotted = ['Sentiment score (Mean)']
            # hover_label = ['Sentence']
        elif mode == "median":
            columns_to_be_plotted = ['Sentiment score (Median)']
        # inputFilename = outputFilename

        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                   columns_to_be_plotted=columns_to_be_plotted,
                                                   chartTitle='Frequency of Hedonometer Sentiment Scores',
                                                   count_var=0, hover_label=[],
                                                   outputFileNameType='Hedo',  # 'line_bar',
                                                   column_xAxis_label='Sentiment score',
                                                   column_yAxis_label='Scores',
                                                   groupByList=['Document ID', 'Document'],
                                                   plotList=['Sentiment Score'],
                                                   chart_title_label='Measures of Hedonometer Sentiment Scores')

        if chart_outputFilename != None:
            if len(chart_outputFilename)> 0:
                filesToOpen.extend(chart_outputFilename)

    return filesToOpen

if __name__ == '__main__':
    # get arguments from command line
    parser = argparse.ArgumentParser(description='Sentiment analysis with Hedonometer.')
    parser.add_argument('--file', type=str, dest='inputFilename', default='',
                        help='a string to hold the path of one file to process')
    parser.add_argument('--dir', type=str, dest='inputDir', default='',
                        help='a string to hold the path of a directory of files to process')
    parser.add_argument('--out', type=str, dest='outputDir', default='',
                        help='a string to hold the path of the output directory')
    parser.add_argument('--outfile', type=str, dest='outputFilename', default='',
                        help='output file')
    parser.add_argument('--mode', type=str, dest='mode', default='mean',
                        help='mode with which to calculate sentiment in the sentence: mean or median')
    args = parser.parse_args()

    # run main
    sys.exit(main(args.inputFilename, args.inputDir, args.outputDir, args.outputFilename, args.mode))
