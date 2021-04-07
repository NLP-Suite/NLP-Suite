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

if IO_libraries_util.install_all_packages(GUI_util.window,"Sentiment Analysis ANEW",['nltk','os','csv','argparse','pandas','tkinter','numpy','time'])==False:
    sys.exit(0)

import csv
import os
import numpy as np #np
import time
import argparse

from nltk import tokenize
from nltk import word_tokenize
import pandas as pd
import tkinter.messagebox as mb

import IO_csv_util
import IO_files_util
import GUI_IO_util

IO_libraries_util.import_nltk_resource(GUI_util.window,'tokenizers/punkt','punkt')
# check WordNet
IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/WordNet','WordNet')
from nltk.stem.wordnet import WordNetLemmatizer
# check stopwords
IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/stopwords','stopwords')
from nltk.corpus import stopwords
stops = set(stopwords.words("english"))
anew = GUI_IO_util.sentiment_libPath + os.sep + "EnglishShortenedANEW.csv"
if not os.path.isfile(anew):
    print("The file "+anew+" could not be found. The ANEW sentiment analysis routine expects a csv dictionary file 'EnglishShortenedANEW.csv' in a directory 'lib' expected to be a subdirectory of the directory where the sentiment_analysis_ANEW.py script is stored.\n\nPlease, check your lib directory and try again.")
    sys.exit()
data = pd.read_csv(anew)
data_dict = {col: list(data[col]) for col in data.columns}


# performs sentiment analysis on inputFile using the ANEW database, outputting results to a new CSV file in outputDir
def analyzefile(input_file, output_dir, output_file, csvfile, mode, Document_ID, Document):
    """
    Performs sentiment analysis on the text file given as input using the ANEW database.
    Outputs results to a new CSV file in output_dir.
    :param input_file: path of .txt file to analyze
    :param output_dir: path of directory to create new output file
    :param mode: determines how sentiment values for a sentence are computed (median or mean)
    :return:
    """
    #TODO
    #the output filename is reset in the specific script; must be passed as a parameter
    #cannot use time in the filename or when re-generated n the main sentimen_concreteness_analysis.py it will have a different time stamp and the file will not be found    
    # if output_file == '':
    #     output_file = IO_files_util.generate_output_file_name(input_file, output_dir, '.csv', 'SC', 'ANEW', '', '', '', False, True)

    # read file into string
    with open(input_file, 'r',encoding='utf-8',errors='ignore') as myfile:
        fulltext = myfile.read()
    # end method if file is empty
    if len(fulltext) < 1:
        mb.showerror(title='File empty', message='The file ' + input_file + ' is empty.\n\nPlease, use another file and try again.')
        print('Empty file ', input_file)
        return

    # otherwise, split into sentences
    sentences = tokenize.sent_tokenize(fulltext)
    # # check each word in sentence for sentiment and write to output_file
    # with open(output_file, 'w', encoding='utf-8',errors='ignore', newline='') as csvfile:

    # if mode == 'mean':
    #     fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence',
    #                   'Sentiment (Mean score)', 'Sentiment (Mean value)',
    #                   'Arousal (Mean score)', 'Arousal (Mean value)',
    #                   'Dominance (Mean score)','Dominance (Mean value)','Found Words', 'Word List']
    # elif mode == 'median':
    #     fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence',
    #                   'Sentiment (Median score)', 'Sentiment (Median value)',
    #                   'Arousal (Median score)', 'Arousal (Median value)',
    #                   'Dominance (Median score)','Dominance (Median value)','Found Words', 'Word List']
    # elif mode == 'both':
    #     fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence',
    #                   'Sentiment (Mean score)', 'Sentiment (Mean value)', 'Sentiment (Median score)', 'Sentiment (Median value)',
    #                   'Arousal (Mean score)', 'Arousal (Mean value)', 'Arousal (Median score)', 'Arousal (Median value)',
    #                   'Dominance (Mean score)','Dominance (Mean value)','Dominance (Median score)','Dominance (Median value)','Found Words', 'Word List']
    #
    # writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    # writer.writeheader()

    # analyze each sentence for sentiment
    i=0
    for s in sentences:
        # print("S" + str(i) +": " + s)
        found_words = []
        total_words = 0
        v_list = []  # holds valence scores
        a_list = []  # holds arousal scores
        d_list = []  # holds dominance scores

        # search for each valid word's sentiment in ANEW
        words = word_tokenize(s.lower())
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
            lmtzr = WordNetLemmatizer()
            lemma = lmtzr.lemmatize(w, pos='v')
            if lemma == w:
                lemma = lmtzr.lemmatize(w, pos='n')

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
            #                 Sentiment (Mean score): 0,
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
            if Sentiment_mean_score < 3:
                sentiment_label = 'very unpleasant'
            elif Sentiment_mean_score >= 3 and Sentiment_mean_score < 5:
                sentiment_label = 'unpleasant'
            elif Sentiment_mean_score  == 5:
                sentiment_label = 'neutral'
            elif Sentiment_mean_score > 5 and Sentiment_mean_score < 8:
                sentiment_label = 'pleasant'
            elif Sentiment_mean_score >=8 and Sentiment_mean_score <=9:
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
            elif Arousal_mean_score >=8 and Arousal_mean_score <=9:
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
            elif Dominance_mean_score >=8 and Dominance_mean_score <=9:
                dominance_label = 'very much in control'

            if mode == 'mean':
                writer.writerow({'Document ID': Document_ID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document), 'Sentence ID': i,
                                 'Sentence': s,
                                 'Sentiment (Mean score)': Sentiment_mean_score,
                                 'Sentiment (Mean value)': sentiment_label,
                                 'Arousal (Mean score)': Arousal_mean_score,
                                 'Arousal (Mean value)': arousal_label,
                                 'Dominance (Mean score)': Dominance_mean_score,
                                 'Dominance (Mean value)': dominance_label,
                                 'Found Words': ("%d out of %d" % (len(found_words), total_words)),
                                 'Word List': ', '.join(found_words)
                                 })
            elif mode == 'median':
                writer.writerow({'Document ID': Document_ID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document), 'Sentence ID': i,
                                 'Sentence': s,
                                 'Sentiment (Median score)':Sentiment_median_score,
                                 'Sentiment (Median value)': sentiment_label,
                                 'Arousal (Median score)':Arousal_median_score,
                                 'Arousal (Median value)': arousal_label,
                                 'Dominance (Median score)':Dominance_median_score,
                                 'Dominance (Median value)': dominance_label,
                                 'Found Words': ("%d out of %d" % (len(found_words), total_words)),
                                 'Word List': ', '.join(found_words)
                                 })
            elif mode == 'both':
                writer.writerow({'Document ID': Document_ID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document), 'Sentence ID': i,
                                 'Sentence': s,
                                 'Sentiment (Mean score)': Sentiment_mean_score,
                                 'Sentiment (Mean value)': sentiment_label,
                                 'Arousal (Mean score)': Arousal_mean_score,
                                 'Arousal (Mean value)': arousal_label,
                                 'Dominance (Mean score)': Dominance_mean_score,
                                 'Dominance (Mean value)': dominance_label,
                                 'Sentiment (Median score)': Sentiment_median_score,
                                 'Sentiment (Median value)': sentiment_label,
                                 'Arousal (Median score)':Arousal_median_score,
                                 'Arousal (Median value)': arousal_label,
                                 'Dominance (Median score)':Dominance_median_score,
                                 'Dominance (Median value)': dominance_label,
                                 'Found Words': ("%d out of %d" % (len(found_words), total_words)),
                                 'Word List': ', '.join(found_words)
                                 })

                i += 1
    i = 1 # to store sentence index
    return output_file #LINE ADDED

fileNamesToPass = [] #LINE ADDED
def main(input_file, input_dir, output_dir,output_file, mode):
    """
    Runs analyzefile on the appropriate files, provided that the input paths are valid.
    :param input_file:
    :param input_dir:
    :param output_dir:
    :param mode:
    :return:
    """
    # startTime = time.localtime()
    # print("Started running ANEW at " + str(startTime[3]) + ':' + str(startTime[4]))

    if len(output_dir) < 0 or not os.path.exists(output_dir):  # empty output
        print('No output directory specified, or path does not exist')
        sys.exit(0)
    elif len(input_file) == 0 and len(input_dir)  == 0:  # empty input
        print('No input specified. Please give either a single file or a directory of files to analyze.')
        sys.exit(1)
    if output_file == '':
        output_file = IO_files_util.generate_output_file_name(input_file, output_dir, '.csv', 'SC', 'ANEW', '',
                                                              '', '', False, True)
    fileNamesToPass.append(output_file)
    with open(output_file, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
        if mode == 'mean':
            fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence',
                          'Sentiment (Mean score)', 'Sentiment (Mean value)',
                          'Arousal (Mean score)', 'Arousal (Mean value)',
                          'Dominance (Mean score)', 'Dominance (Mean value)', 'Found Words', 'Word List']
        elif mode == 'median':
            fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence',
                          'Sentiment (Median score)', 'Sentiment (Median value)',
                          'Arousal (Median score)', 'Arousal (Median value)',
                          'Dominance (Median score)', 'Dominance (Median value)', 'Found Words', 'Word List']
        elif mode == 'both':
            fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence',
                          'Sentiment (Mean score)', 'Sentiment (Mean value)', 'Sentiment (Median score)',
                          'Sentiment (Median value)',
                          'Arousal (Mean score)', 'Arousal (Mean value)', 'Arousal (Median score)',
                          'Arousal (Median value)',
                          'Dominance (Mean score)', 'Dominance (Mean value)', 'Dominance (Median score)',
                          'Dominance (Median value)', 'Found Words', 'Word List']
        global writer
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        if len(input_file) > 0:  # handle single file
            if os.path.exists(input_file):
                analyzefile(input_file, output_dir, output_file, csvfile, mode, 1, input_file)
            else:
                print('Input file "' + input_file + '" is invalid.')
                sys.exit(0)
        elif len(input_dir) > 0:  # handle directory
            if os.path.isdir(input_dir):
                directory = os.fsencode(input_dir)
                Document_ID = 0
                # check each word in sentence for sentiment and write to output_file
                for file in os.listdir(directory):
                    filename = os.path.join(input_dir, os.fsdecode(file))
                    if filename.endswith(".txt"):
                        start_time = time.time()
                        print("Started ANEW sentiment analysis of " + filename + "...")
                        Document_ID += 1
                        analyzefile(filename, output_dir, output_file,csvfile, mode, Document_ID, filename)
                        print("Finished ANEW sentiment analysis of " + filename + " in " + str((time.time() - start_time)) + " seconds")
            else:
                print('Input directory "' + input_dir + '" is invalid.')
                sys.exit(1)
    csvfile.close()
    return fileNamesToPass #LINE ADDED

    # endTime = time.localtime()
    # print("Finished running ANEW at " + str(endTime[3]) + ':' + str(endTime[4]))

if __name__ == '__main__':
    # get arguments from command line
    parser = argparse.ArgumentParser(description='Sentiment analysis with ANEW.')
    parser.add_argument('--file', type=str, dest='input_file', default='',
                        help='a string to hold the path of one file to process')
    parser.add_argument('--dir', type=str, dest='input_dir', default='',
                        help='a string to hold the path of a directory of files to process')
    parser.add_argument('--out', type=str, dest='output_dir', default='',
                        help='a string to hold the path of the output directory')
    parser.add_argument('--outfile', type=str, dest='output_file', default='',
                        help='output file')
    parser.add_argument('--mode', type=str, dest='mode', default='mean',
                        help='mode with which to calculate sentiment in the sentence: mean or median')
    args = parser.parse_args()

    # run main
    sys.exit(main(args.input_file, args.input_dir, args.output_dir, args.output_file, args.mode))
    #sys.exit(main('','./in','./out',''))
    #python SentimentAnalysisAnew.py --file "C:\Users\rfranzo\Documents\ACCESS Databases\PC-ACE\NEW\DATA\CORPUS DATA\MURPHY\Murphy Miracles thicker than fog CORENLP.txt" --out C:\Users\rfranzo\Desktop\NLP_output --mode mean
