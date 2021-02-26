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

import GUI_IO_util
import IO_files_util
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Sentiment Analysis HEDONOMETER",['nltk','json','os','csv','argparse','pandas','tkinter','numpy','time'])==False:
    sys.exit(0)

import os
import csv
import json
import statistics
import time
import argparse
import tkinter.messagebox as mb

import IO_csv_util

from nltk import tokenize
from nltk import word_tokenize

IO_libraries_util.import_nltk_resource(GUI_util.window,'tokenizers/punkt','punkt')
# check WordNet
IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/WordNet','WordNet')
from nltk.stem.wordnet import WordNetLemmatizer
# check stopwords
IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/stopwords','stopwords')
from nltk.corpus import stopwords
stops = set(stopwords.words("english"))
database = GUI_IO_util.sentiment_libPath + os.sep + "hedonometer.json"
if not os.path.isfile(database):
    print("The file './lib/hedonometer.json' could not be found. The hedonemeter sentiment analysis routine expects a JSON dictionary file 'hedonometer.json' in a directory 'lib' expected to be a subdirectory of the directory where the sentiment_analysis_hedonometer.py script is stored.\n\nPlease, check your lib directory and try again.")
    sys.exit()

parsed_data = json.load(open(database))

# performs sentiment analysis on inputFile using the hedonometer database, outputting results to a new CSV file in outputDir
def analyzefile(input_file, output_dir, output_file, mode, Document_ID, Document):
    """
    Performs sentiment analysis on the text file given as input using the Hedonometer database.
    Outputs results to a new CSV file in output_dir.
    :param input_file: path of .txt file to analyze
    :param output_dir: path of directory to create new output file
    :param mode: determines how sentiment values for a sentence are computed (median or mean)
    :return:
    """
    #TODO
    #the output filename is reset in the specific script; must be passed as a parameter
    #cannot use time in the filename or when re-generated n the main sentimen_concreteness_analysis.py it will have a different time stamp and the file will not be found
    # read file into string
    with open(input_file, 'r',encoding='utf-8',errors='ignore') as myfile:
        fulltext = myfile.read()
    # end method if file is empty
    if len(fulltext) < 1:
        mb.showerror(title='File empty', message='The file ' + myfile + ' is empty.\n\nPlease, use another file and try again.')
        print('Empty file '+ myfile )
        return

    # otherwise, split into sentences
    sentences = tokenize.sent_tokenize(fulltext)
    i = 1 # to store sentence index
    # check each word in sentence for sentiment and write to output_file
    # analyze each sentence for sentiment
    for s in sentences:
        # print("S" + str(i) +": " + s)
        found_words = []
        total_words = 0
        v_list = []  # holds valence scores

        # search for each valid word's sentiment in hedonometer database
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

            # search for lemmatized word in database
            for record in parsed_data["objects"]:
                if record["word"] == lemma.casefold():
                    v_list.append(record["happs"])
                    found_words.append(lemma)


        if len(found_words) == 0:  # no words found for this sentence
            writer.writerow({'Document ID': Document_ID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document), 'Sentence ID': i,
                            'Sentence': s,
                            # Sentiment_measure: 0,
                            # Sentiment_label: "",
                            'Sentiment (Mean score)': 0,
                            'Sentiment (Mean value)': "",
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
                if sentiment > 6 :
                    label_mean = 'positive'
                elif sentiment < 4:
                    label_mean = 'negative'
                else:
                    label_mean = "neutral"
            if mode == 'median' or mode == 'both':
                sentiment_median = statistics.median(v_list)
                sentiment=sentiment_median
                if sentiment > 6 :
                    label_median = 'positive'
                elif sentiment < 4:
                    label_median = 'negative'
                else:
                    label_median = "neutral"

            if mode == 'mean':
                writer.writerow({'Document ID': Document_ID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document), 'Sentence ID': i,
                                 'Sentence': s,
                                 'Sentiment (Mean score)': sentiment_mean,
                                 'Sentiment (Mean value)': label_mean,
                                 'Found Words': ("%d out of %d" % (len(found_words), total_words)),
                                 'Word List': ', '.join(found_words)
                                 })
            elif mode == 'median':
                writer.writerow({'Document ID': Document_ID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document), 'Sentence ID': i,
                                 'Sentence': s,
                                 'Sentiment (Median score)':sentiment_median,
                                 'Sentiment (Median value)': label_median,
                                 'Found Words': ("%d out of %d" % (len(found_words), total_words)),
                                 'Word List': ', '.join(found_words)
                                 })
            elif mode == 'both':
                writer.writerow({'Document ID': Document_ID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document),
                                 'Sentence ID': i,
                                 'Sentence': s,
                                 'Sentiment (Mean score)': sentiment_mean,
                                 'Sentiment (Mean value)': label_mean,
                                 'Sentiment (Median score)': sentiment_median,
                                 'Sentiment (Median value)': label_median,
                                 'Found Words': ("%d out of %d" % (len(found_words), total_words)),
                                 'Word List': ', '.join(found_words)
                                 })

        i += 1
    return output_file #LINE ADDED

fileNamesToPass = [] #LINE ADDED
def main(input_file, input_dir, output_dir, output_file, mode):
    """
    Runs analyzefile on the appropriate files, provided that the input paths are valid.
    :param input_file:
    :param input_dir:
    :param output_dir:
    :return:
    """

    if len(output_dir) < 0 or not os.path.exists(output_dir):  # empty output
        print('No output directory specified, or path does not exist')
        sys.exit(0)
    elif len(input_file) == 0 and len(input_dir)  == 0:  # empty input
        print('No input specified. Please give either a single file or a directory of files to analyze.')
        sys.exit(1)

    with open(output_file, 'w', encoding='utf-8',errors='ignore', newline='') as csvfile:
        if (mode == 'both'):
            fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence', 'Sentiment (Mean score)', 'Sentiment (Mean value)','Sentiment (Median score)', 'Sentiment (Median value)', 'Found Words', 'Word List']
        else:
            if mode == 'mean':
                fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence', 'Sentiment (Mean score)', 'Sentiment (Mean value)', 'Found Words', 'Word List']
            elif mode == 'median':
                fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence', 'Sentiment (Median score)', 'Sentiment (Median value)', 'Found Words', 'Word List']
        global writer
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()


        if len(input_file) > 0:  # handle single file
            if os.path.exists(input_file):
                fileNamesToPass.append(analyzefile(input_file, output_dir, output_file, mode, 1, input_file))
                analyzefile(input_file, output_dir, output_file, mode, 1, input_file)
            else:
                print('Input file "' + input_file + '" is invalid.')
                sys.exit(0)
        elif len(input_dir) > 0:  # handle directory
            if os.path.isdir(input_dir):
                directory = os.fsencode(input_dir)
                Document_ID = 0
                for file in os.listdir(directory):
                    filename = os.path.join(input_dir, os.fsdecode(file))
                    if filename.endswith(".txt"):
                        start_time = time.time()
                        print("Started HEDONOMETER sentiment analysis of " + filename + "...")
                        Document_ID += 1
                        fileNamesToPass.append(analyzefile(filename, output_dir, output_file,mode, Document_ID, filename)) #LINE ADDED (edited)
                        print("Finished HEDONOMETER sentiment analysis of " + filename + " in " + str((time.time() - start_time)) + " seconds")
            else:
                print('Input directory "' + input_dir + '" is invalid.')
                sys.exit(0)
    return fileNamesToPass #LINE ADDED


if __name__ == '__main__':
    # get arguments from command line
    parser = argparse.ArgumentParser(description='Sentiment analysis with Hedonometer.')
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