"""
Author: Doris Zhou
Date: September 29, 2017
Modified by Gabriel Wang May 2018
Modified by Roberto Franzosi February 2019
Modified by Josh Karol October 2019

Performs sentiment analysis on a text file using ANEW (Affective Norms for English Words).
Parameters:
    --file [path of text file]
        specifies location of specific file to analyze; FOR SINGLE FILE
    --dir [path of directory]
        specifies directory of files to analyze
    --out [path of directory]
        specifies directory to create output files
    --mode [mode]
        takes either "median" or "mean"; determines which is used to calculate sentence sentiment values

    ratings of pleasure (pleasant/unpleasant), arousal (calm/excited), and dominance (controlled/in control)
    each rating receives a total of 9 possible points (9 max)

    Bradley, M.M. & Lang, P.J. (2017). Affective Norms for English Words (ANEW): Instruction manual and affective ratings. Technical Report C-3. Gainesville, FL:UF Center for the Study of Emotion and Attention.

    cd "C:\\Program files (x86)\\PC-ACE\\NLP\\SentimentAnalysis" & Python SentimentAnalysisAnew.py --file "C:\\Users\\rfranzo\\Documents\\My Publications\\My Papers\\IN PROGRESS\\PC-ACE - QNA - CAQDAS - NLP\\SAGE Encyclopedia\\Data\\The Three Little Pigs.txt" --out C:\\Users\\rfranzo\\Desktop\\NLP_output\\

"""
# add parameter to exclude duplicates? also mean or median analysis

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Sentiment Analysis ANEW",['stanza','os','csv','argparse','pandas','tkinter','numpy','time'])==False:
    sys.exit(0)

import csv
import os
import numpy as np #np
import time
import argparse

from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza
import pandas as pd
import tkinter.messagebox as mb

import IO_csv_util
import IO_files_util
import GUI_IO_util
import charts_util

fin = open('../lib/wordLists/stopwords.txt', 'r')
stops = set(fin.read().splitlines())

anew = GUI_IO_util.sentiment_libPath + os.sep + "EnglishShortenedANEW.csv"
if not os.path.isfile(anew):
    print("The file "+anew+" could not be found. The ANEW sentiment analysis routine expects a csv dictionary file 'EnglishShortenedANEW.csv' in a directory 'lib' expected to be a subdirectory of the directory where the sentiment_analysis_ANEW.py script is stored.\n\nPlease, check your lib directory and try again.")
    sys.exit()
data = pd.read_csv(anew, encoding='utf-8',on_bad_lines='warn')
data_dict = {col: list(data[col]) for col in data.columns}


# performs sentiment analysis on inputFile using the ANEW database, outputting results to a new CSV file in outputDir
def analyzefile(inputFilename, outputDir, outputFilename, csvfile, mode, Document_ID, Document):
    """
    Performs sentiment analysis on the text file given as input using the ANEW database.
    Outputs results to a new CSV file in outputFilename.
    :param inputFilename: path of .txt file to analyze
    :param outputFilename: path of directory to create new output file
    :param mode: determines how sentiment values for a sentence are computed (median or mean)
    :return:
    """
    #TODO
    #the output filename is reset in the specific script; must be passed as a parameter
    #cannot use time in the filename or when re-generated n the main sentimen_concreteness_analysis.py it will have a different time stamp and the file will not be found
    # if outputFilename == '':
    #     outputFilename = IO_files_util.generate_outputFilename_name(inputFilename, outputFilename, '.csv', 'SC', 'ANEW', '', '', '', False, True)

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
    # # check each word in sentence for sentiment and write to outputFilename

    # analyze each sentence for sentiment
    i=1
    for s in sentences:
        # print("S" + str(i) +": " + s)
        found_words = []
        total_words = 0
        v_list = []  # holds valence scores
        a_list = []  # holds arousal scores
        d_list = []  # holds dominance scores

        # search for each valid word's sentiment in ANEW
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

            # search for lemmatized word in ANEW
            if lemma in data_dict['Word']:
                index = data_dict['Word'].index(lemma)

                if neg:
                        found_words.append("neg-"+lemma)
                else:
                    found_words.append(lemma)

                v_list.append(float(data_dict['valence'][index]))
                a_list.append(float(data_dict['arousal'][index]))
                d_list.append(float(data_dict['dominance'][index]))
        if len(found_words) == 0:  # no words found in ANEW for this sentence
            # writer.writerow({'Document ID': Document ID, 'Document': IO_util.dressFilenameForCSVHyperlink(Document), 'Sentence ID': i,
            #                 'Sentence': s,
            #                 Sentiment score (Mean): 0,
            #                 sentiment_label: "",
            #                 })
            i += 1
            pass
        else:  # output sentiment info for this sentence
            # get values
            if mode == 'mean' or mode == 'both':
                Sentiment_mean_score = np.mean(v_list)
                Arousal_mean_score = np.mean(a_list)
                Dominance_mean_score = np.mean(d_list)
            if mode == 'median' or mode == 'both':
                Sentiment_median_score = np.median(v_list)
                Arousal_median_score = np.median(a_list)
                Dominance_median_score = np.median(d_list)

            if neg:  # reverse polarity
                if mode == 'mean' or mode == 'both':
                    Sentiment_mean_score = 5 - (Sentiment_mean_score-5)
                    Arousal_mean_score = 5 - (Arousal_mean_score-5)
                    Dominance_mean_score = 5 - (Dominance_mean_score-5)
                if mode == 'median' or mode == 'both':
                    Sentiment_median_score = 5 - (Sentiment_median_score-5)
                    Arousal_median_score = 5 - (Arousal_median_score-5)
                    Dominance_median_score = 5 - (Dominance_median_score-5)

            # set sentiment label

            sentiment_label = 'neutral'
            if mode == 'median' or mode == 'both':
                if Sentiment_median_score < 3:
                    sentiment_label = 'very unpleasant'
                elif Sentiment_median_score >= 3 and Sentiment_median_score < 5:
                    sentiment_label = 'unpleasant'
                elif Sentiment_median_score  == 5:
                    sentiment_label = 'neutral'
                elif Sentiment_median_score > 5 and Sentiment_median_score < 8:
                    sentiment_label = 'pleasant'
                elif Sentiment_median_score >=8 and Sentiment_median_score <=9:
                    sentiment_label = 'very pleasant'

                # set arousal label
                arousal_label = 'neutral'
                if Arousal_median_score < 3:
                    arousal_label = 'very calm'
                elif Arousal_median_score >= 3 and Arousal_median_score < 5:
                    arousal_label = 'calm'
                elif Arousal_median_score == 5:
                    arousal_label = 'neutral'
                elif Arousal_median_score > 5 and Arousal_median_score < 8:
                    arousal_label = 'excited'
                elif Arousal_median_score >=8 and Arousal_median_score <=9:
                    arousal_label = 'very excited'

                # set dominance label
                dominance_label = 'neutral'
                if Dominance_median_score < 3:
                    dominance_label = 'very controlled'
                elif Dominance_median_score >= 3 and Dominance_median_score < 5:
                    dominance_label = 'controlled'
                elif Dominance_median_score == 5:
                    dominance_label = 'neutral'
                elif Dominance_median_score > 5 and Dominance_median_score < 8:
                    dominance_label = 'in control'
                elif Dominance_median_score >=8 and Dominance_median_score <=9:
                    dominance_label = 'very much in control'

            sentiment_label = 'neutral'
            if mode == 'mean' or mode == 'both':
                if Sentiment_mean_score < 3:
                    sentiment_label = 'very unpleasant'
                elif Sentiment_mean_score >= 3 and Sentiment_mean_score < 5:
                    sentiment_label = 'unpleasant'
                elif Sentiment_mean_score == 5:
                    sentiment_label = 'neutral'
                elif Sentiment_mean_score > 5 and Sentiment_mean_score < 8:
                    sentiment_label = 'pleasant'
                elif Sentiment_mean_score >= 8 and Sentiment_mean_score <= 9:
                    sentiment_label = 'very pleasant'

                # set arousal label
                arousal_label = 'neutral'
                if Arousal_mean_score < 3:
                    arousal_label = 'very calm'
                elif Arousal_mean_score >= 3 and Arousal_mean_score < 5:
                    arousal_label = 'calm'
                elif Arousal_mean_score == 5:
                    arousal_label = 'neutral'
                elif Arousal_mean_score > 5 and Arousal_mean_score < 8:
                    arousal_label = 'excited'
                elif Arousal_mean_score >= 8 and Arousal_mean_score <= 9:
                    arousal_label = 'very excited'

                # set dominance label
                dominance_label = 'neutral'
                if Dominance_mean_score < 3:
                    dominance_label = 'very controlled'
                elif Dominance_mean_score >= 3 and Dominance_mean_score < 5:
                    dominance_label = 'controlled'
                elif Dominance_mean_score == 5:
                    dominance_label = 'neutral'
                elif Dominance_mean_score > 5 and Dominance_mean_score < 8:
                    dominance_label = 'in control'
                elif Dominance_mean_score >= 8 and Dominance_mean_score <= 9:
                    dominance_label = 'very much in control'

            if mode == 'mean':
                writer.writerow({
                                 'Sentiment score (Mean)': Sentiment_mean_score,
                                 'Sentiment label (Mean)': sentiment_label,
                                 'Arousal score (Mean)': Arousal_mean_score,
                                 'Arousal label (Mean)': arousal_label,
                                 'Dominance score (Mean)': Dominance_mean_score,
                                 'Dominance label (Mean)': dominance_label,
                                 'Found Words': ("%d out of %d" % (len(found_words), total_words)),
                                 'Word List': ', '.join(found_words),
                                'Sentence ID': i,
                                'Sentence': s,
                                'Document ID': Document_ID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document)
                })
            elif mode == 'median':
                writer.writerow({
                                 'Sentiment score (Median)':Sentiment_median_score,
                                 'Sentiment label (Median)': sentiment_label,
                                 'Arousal score (Median)':Arousal_median_score,
                                 'Arousal label (Median)': arousal_label,
                                 'Dominance score (Median)':Dominance_median_score,
                                 'Dominance label (Median)': dominance_label,
                                 'Found Words': ("%d out of %d" % (len(found_words), total_words)),
                                 'Word List': ', '.join(found_words),
                                 'Sentence ID': i,
                                 'Sentence': s,
                                  'Document ID': Document_ID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document)
                                  })
            elif mode == 'both':
                writer.writerow({
                                 'Sentiment score (Mean)': Sentiment_mean_score,
                                 'Sentiment label (Mean)': sentiment_label,
                                 'Arousal score (Mean)': Arousal_mean_score,
                                 'Arousal label (Mean)': arousal_label,
                                 'Dominance score (Mean)': Dominance_mean_score,
                                 'Dominance label (Mean)': dominance_label,
                                 'Sentiment score (Median)': Sentiment_median_score,
                                 'Sentiment label (Median)': sentiment_label,
                                 'Arousal score (Median)':Arousal_median_score,
                                 'Arousal label (Median)': arousal_label,
                                 'Dominance score (Median)':Dominance_median_score,
                                 'Dominance label (Median)': dominance_label,
                                 'Found Words': ("%d out of %d" % (len(found_words), total_words)),
                                 'Word List': ', '.join(found_words),
                                 'Sentence ID': i,
                                 'Sentence': s,
                                 'Document ID': Document_ID,
                                 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document)
                                 })
                i += 1
    return outputFilename

def main(inputFilename, inputDir, outputDir, mode, createCharts=False, chartPackage='Excel'):
    """
    Runs analyzefile on the appropriate files, provided that the input paths are valid.
    :param inputFilename:
    :param inputDir:
    :param outputFilename:
    :param mode:
    :return:
    """

    filesToOpen = []

    # create output subdirectory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='sentiment_ANEW',
                                                       silent=False)
    if outputDir == '':
        return

    # startTime = time.localtime()
    # print("Started running ANEW at " + str(startTime[3]) + ':' + str(startTime[4]))

    if len(outputDir) < 0 or not os.path.exists(outputDir):
        print('No output directory specified, or path does not exist.')
        sys.exit(1)
    elif len(inputFilename) == 0 and len(inputDir)  == 0:
        print('No input specified. Please, provide either a single file -- file or a directory of files to be analyzed --dir.')
        sys.exit(1)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir,  outputDir, '.csv', 'ANEW', '', '', '', '', False, True)

    filesToOpen.append(outputFilename)
    with open(outputFilename, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
        if mode == 'mean':
            fieldnames = [
                          'Sentiment score (Mean)', 'Sentiment label (Mean)',
                          'Arousal score (Mean)', 'Arousal label (Mean)',
                          'Dominance score (Mean)', 'Dominance label (Mean)',
                          'Found Words', 'Word List',
                          'Sentence ID', 'Sentence', 'Document ID', 'Document']
        elif mode == 'median':
            fieldnames = [
                          'Sentiment score (Median)', 'Sentiment label (Median)',
                          'Arousal score (Median)', 'Arousal label (Median)',
                          'Dominance score (Median)', 'Dominance label (Median)',
                          'Found Words', 'Word List',
                          'Sentence ID', 'Sentence', 'Document ID', 'Document']
        elif mode == 'both':
            fieldnames = [
                          'Sentiment score (Mean)', 'Sentiment label (Mean)',
                          'Sentiment score (Median)', 'Sentiment label (Median)',
                          'Arousal score (Mean)', 'Arousal label (Mean)',
                          'Arousal score (Median)', 'Arousal label (Median)',
                          'Dominance score (Mean)', 'Dominance label (Mean)',
                          'Dominance score (Median)', 'Dominance label (Median)',
                           'Found Words', 'Word List',
                           'Sentence ID', 'Sentence','Document ID', 'Document']
        global writer
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        if len(inputFilename) > 0:  # handle single file
            if os.path.exists(inputFilename):
                filesToOpen.append(analyzefile(inputFilename, outputDir, outputFilename, csvfile, mode, 1, inputFilename))
            else:
                print('Input file "' + inputFilename + '" is invalid.')
                sys.exit(0)
        elif len(inputDir) > 0:  # handle directory
            if os.path.isdir(inputDir):
                directory = os.fsencode(inputDir)
                Document_ID = 0
                # check each word in sentence for sentiment and write to outputFilename
                for file in os.listdir(directory):
                    filename = os.path.join(inputDir, os.fsdecode(file))
                    if filename.endswith(".txt"):
                        start_time = time.time()
                        # print("Started ANEW sentiment analysis of " + filename + "...")
                        Document_ID += 1
                        filesToOpen.append(analyzefile(filename, outputDir, outputFilename,csvfile, mode, Document_ID, filename))
                        # print("Finished ANEW sentiment analysis of " + filename + " in " + str((time.time() - start_time)) + " seconds")
            else:
                print('Input directory "' + inputDir + '" is invalid.')
                sys.exit(1)
    csvfile.close()

    if createCharts == True:
        if mode == "both":
            columns_to_be_plotted_yAxis=['Sentiment score (Mean)', 'Arousal score (Mean)', 'Dominance score (Mean)',
                                'Sentiment score (Median)', 'Arousal score (Median)', 'Dominance score (Median)']
            # hover_label = ['Sentence', 'Sentence', 'Sentence', 'Sentence', 'Sentence', 'Sentence']
        elif mode == "mean":
            columns_to_be_plotted_yAxis=['Sentiment score (Mean)', 'Arousal score (Mean)', 'Dominance score (Mean)']
            # hover_label = ['Sentence', 'Sentence', 'Sentence']
        elif mode == "median":
            columns_to_be_plotted_yAxis=['Sentiment score (Median)', 'Arousal score (Median)', 'Dominance score (Median)']
            # hover_label = ['Sentence', 'Sentence', 'Sentence']

        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                   columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
                                                   chartTitle='Frequency of ANEW Sentiment Scores',
                                                   count_var=0, hover_label=[],
                                                   outputFileNameType='',
                                                   column_xAxis_label='Sentiment score',
                                                   column_yAxis_label='Scores',
                                                   groupByList=['Document ID', 'Document'],
                                                   plotList=columns_to_be_plotted_yAxis,
                                                   chart_title_label='Measures of ANEW Sentiment Scores')

        if chart_outputFilename != None:
            if len(chart_outputFilename)> 0:
                filesToOpen.extend(chart_outputFilename)

    # endTime = time.localtime()
    # print("Finished running ANEW at " + str(endTime[3]) + ':' + str(endTime[4]))

    return filesToOpen


if __name__ == '__main__':
    # get arguments from command line
    parser = argparse.ArgumentParser(description='Sentiment analysis with ANEW.')
    parser.add_argument('--file', type=str, dest='inputFilename', default='',
                        help='a string to hold the path of one file to process')
    parser.add_argument('--dir', type=str, dest='inputDir', default='',
                        help='a string to hold the path of a directory of files to process')
    parser.add_argument('--out', type=str, dest='outputFilename', default='',
                        help='a string to hold the path of the output directory')
    parser.add_argument('--outfile', type=str, dest='outputFilename', default='',
                        help='output file')
    parser.add_argument('--mode', type=str, dest='mode', default='mean',
                        help='mode with which to calculate sentiment in the sentence: mean or median')
    args = parser.parse_args()

    # run main
    sys.exit(main(args.inputFilename, args.inputDir, args.outputFilename, args.outputFilename, args.mode))
    #sys.exit(main('','./in','./out',''))
    #python SentimentAnalysisAnew.py --file "C:\Users\rfranzo\Documents\ACCESS Databases\PC-ACE\NEW\DATA\CORPUS DATA\MURPHY\Murphy Miracles thicker than fog CORENLP.txt" --out C:\Users\rfranzo\Desktop\NLP_output --mode mean
