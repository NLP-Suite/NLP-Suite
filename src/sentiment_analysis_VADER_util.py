"""
Author: Doris Zhou September 29, 2017
Modified by Gabriel Wang May 2018
Modified by Roberto Franzosi February 2019
Modified by Josh Karol October 2019

Performs sentiment analysis on a text file using the NLTK's VADER sentiment analysis function.
VADER (Valence Aware Dictionary and sEntiment Reasoner)
VADER has been found to be quite successful when dealing with tweets.
    This is because VADER not only tells about the Positivity and Negativity score
        but also tells us about how positive or negative a sentiment is.
The routine relies on the VADER rated dictionary
Parameters:
    --file [path and filename of file to be analyzed]
        specifies location of ONE specific file to analyze
        Enter --file "" or take out --file altogether if you want to analyze all txt files in a folder
    --dir [path of directory]
        specifies directory of files to analyze
    --out [path of directory]
        specifies directory to create output files
    --mode [mode]
        takes either "median" or "mean"; determines which is used to calculate sentence sentiment values

The flags --file, --dir, --out MUST be entered before the respective strings but only --file or --dir can be entered;

"""

# The VADER algorithm outputs sentiment scores to 4 classes of sentiments
#   https://github.com/nltk/nltk/blob/develop/nltk/sentiment/vader.py#L441:
# neg: Negative
# neu: Neutral
# pos: Positive
# compound: Compound (i.e. aggregated score)
# The "compound" score, ranging from -1 (most neg) to 1 (most pos)
#   would provide a single measure of polarity.

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "sentiment_analysis_VADER", ['nltk','os','csv','argparse','tkinter','time','stanza'])==False:
    sys.exit(0)

import csv
import os
import time
import argparse
import tkinter.messagebox as mb
from nltk.sentiment.vader import SentimentIntensityAnalyzer
# from nltk import tokenize
# from nltk import word_tokenize
from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza

import GUI_IO_util
import IO_csv_util
import IO_files_util
import charts_util

# if VADER fails, run: "python -m nltk.downloader all"

# IO_libraries_util.import_nltk_resource(GUI_util.window,'tokenizers/punkt','punkt')
# check WordNet
# IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/WordNet','WordNet')
# from nltk.stem.wordnet import WordNetLemmatizer
# check stopwords
# IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/stopwords','stopwords')
# from nltk.corpus import stopwords
# stops = set(stopwords.words("english"))
fin = open('../lib/wordLists/stopwords.txt', 'r')
stops = set(fin.read().splitlines())

vader = GUI_IO_util.sentiment_libPath + os.sep + "vader_lexicon.txt"
if not os.path.isfile(vader):
    print("The file './lib/vader_lexicon.txt' could not be found. The VADER sentiment analysis routine expects a txt dictionary file 'vader_lexicon.txt' in a directory 'lib' expected to be a subdirectory of the directory where the sentiment_analysis_VADER.py script is stored.\n\nPlease, check your lib directory and try again.")
    sys.exit()

#https://github.com/cjhutto/vaderSentiment/blob/master/vaderSentiment/vaderSentiment.py
# The vader_lexicon.txt file has four tab delimited columns as you said.
# Column 1: The Token
# Column 2: It is the Mean of the human Sentiment ratings
# Column 3: It is the Standard Deviation of the token assuming it follows Normal Distribution
# Column 4: It is the list of 10 human ratings taken during experiments

#TODO change to txt vader
#https://stackoverflow.com/questions/50882838/python-vader-lexicon-structure-for-sentiment-analysis
#ONLY THE FIRST VALUE FOR EACH WORD IS USED
#THUS, TAKE THE WORD OBLITERATE:
#obliterate -2.9    0.83066 [-3, -4, -3, -3, -3, -3, -2, -1, -4, -3]
#ONLY -2.9 IS USED

# data = pd.read_csv(vader)
# data_dict = {col: list(data[col]) for col in data.columns}

# performs sentiment analysis on inputFile using the NLTK, outputting results to a new CSV file in outputDir
def analyzefile(inputFilename, outputDir, outputFilename, mode, Document_ID, Document):
    """
    Performs sentiment analysis on the text file given as input using the VADER database.
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

    # sentences = tokenize.sent_tokenize(fulltext)  # split text into sentences
    sentences = sent_tokenize_stanza(stanzaPipeLine(fulltext))
    sid = SentimentIntensityAnalyzer()  # create sentiment analyzer
    i = 1  # to store sentence index

    # check each word in sentence for sentiment and write to outputFilename
    # check each word in sentence for sentiment and write to outputFilename
    # analyze each sentence s for sentiment
    for s in sentences:
        ss = sid.polarity_scores(s)  # get sentiment scores
        # determine sentiment label:
        # "compound" score, ranging from -1 (most neg) to 1 (most pos)
        #   negative = compound score < -0.05
        #   positive = compound score > 0.05
        #   neutral = (compound score > -0.05) and (compound score < 0.05)
        label = 'neutral'
        sentiment = ss['compound'] #for the whole sentence
        if sentiment > 0.05 :
            label = 'positive'
        elif sentiment < -0.05:
            label = 'negative'

        # VADER, as is, cannot compute mean and median because compound refers to the value of the entire sentence
        #   look at hedonometer to compute separate values and word list of words found
        # label = 'neutral'
        # label_mean = 'neutral'
        # label_median = 'neutral'
        # if mode == 'mean' or mode == 'both':
        #     sentiment_mean = ss['compound'] #for the whole sentence
        #     sentiment=sentiment_mean
        #     if sentiment > 0.05 :
        #         label_mean = 'positive'
        #     elif sentiment < -0.05:
        #         label_mean = 'negative'
        #     label=label_mean
        # if mode == 'median' or mode == 'both':
        #     sentiment_median = ss['compound']
        #     #print("sentiment_median",sentiment_median)
        #     #sentiment_median = statistics.median(ss['compound'])
        #     sentiment=sentiment_median
        #     if sentiment > 0.05 :
        #         label_median = 'positive'
        #     elif sentiment < -0.05:
        #         label_median = 'negative'
        #     label=label_median

        # search for each valid word's sentiment in VADER database
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

        writer.writerow({
                         Sentiment_measure: sentiment,
                         Sentiment_label: label,
                         'Sentence ID': i,
                         'Sentence': s,
                         'Document ID': Document_ID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document)
        })

        # if mode == 'mean' or mode == 'median':
        #     writer.writerow({'Sentence ID': i,
        #                         'Sentence': s,
        #                         Sentiment_measure: sentiment,
        #                         Sentiment_label: label,
        #                         })
        # else:
        #     writer.writerow({'Sentence ID': i,
        #                         'Sentence': s,
        #                          'Sentiment score': sentiment_mean,
        #                          'Sentiment label': label_mean,
        #                          'Sentiment (Median)': sentiment_median,
        #                          'Sentiment Label (Median)': label_median,
        #                         })

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

    # create output subdirectory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='sentiment_VADER',
                                                       silent=False)
    if outputDir == '':
        return

    if len(outputDir) < 0 or not os.path.exists(outputDir):
        print('No output directory specified, or path does not exist.')
        sys.exit(1)
    elif len(inputFilename) == 0 and len(inputDir)  == 0:
        print('No input specified. Please, provide either a single file -- file or a directory of files to be analyzed --dir.')
        sys.exit(1)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir,  outputDir, '.csv', 'VADER', '', '', '', '', False, True)

    with open(outputFilename, 'w', encoding='utf-8',errors='ignore', newline='') as csvfile:

        # VADER, as is, cannot compute mean and median because compound refers to the value of the entire sentence
        #   look at hedonometer to compute separate values and word list of words found
        # if mode == 'both':
        # fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence', 'Sentiment score', 'Sentiment label']
        # else:
        #     if mode == 'mean':
        #         Sentiment_measure='Sentiment score'
        #         Sentiment_label='Sentiment label'
        #     elif mode == 'median':
        #         Sentiment_measure='Sentiment (Median)'
        #         Sentiment_label='Sentiment Label (Median)'
        #     fieldnames = ['Sentence ID', 'Sentence', Sentiment_measure, Sentiment_label]

        global Sentiment_measure, Sentiment_label
        Sentiment_measure='Sentiment score'
        Sentiment_label='Sentiment label'
        fieldnames = [Sentiment_measure, Sentiment_label,'Sentence ID', 'Sentence', 'Document ID', 'Document']
        global writer
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        if len(inputFilename) > 0:  # handle single file
            if os.path.exists(inputFilename):
                filesToOpen.append(analyzefile(inputFilename, outputDir, outputFilename, mode, 1, inputFilename))
                analyzefile(inputFilename, outputDir, outputFilename, mode, 1, inputFilename)
                #print("Output Vader Sentiment " + outputFilename + " created")
            else:
                print('Input file "' + inputFilename + '" is invalid.')
                sys.exit(1)
        elif len(inputDir) > 0:  # handle directory
            if os.path.isdir(inputDir):
                directory = os.fsencode(inputDir)
                documentID = 0
                for file in os.listdir(directory):
                    filename = os.path.join(inputDir, os.fsdecode(file))
                    if filename.endswith(".txt"):
                        documentID += 1
                        start_time = time.time()
                        # print("Started VADER sentiment analysis of " + filename + "...")
                        filesToOpen.append(analyzefile(filename, outputDir, outputFilename,mode, documentID, filename))
                        # print("Finished VADER sentiment analysis of " + filename + " in " + str((time.time() - start_time)) + " seconds")
            else:
                print('Input directory "' + inputDir + '" is invalid.')
                sys.exit(1)
    csvfile.close()

    if createCharts == True:
        # VADER does not compute separate mean and median values

        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                   columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Sentiment score'],
                                                   chartTitle='Frequency of VADER Sentiment Scores',
                                                   count_var=0, hover_label=[],
                                                   outputFileNameType='VADER',  # 'line_bar',
                                                   column_xAxis_label='Sentiment label',
                                                   column_yAxis_label='Scores',
                                                   groupByList=['Document ID', 'Document'],
                                                   plotList=['Sentiment Score'],
                                                   chart_title_label='Measures of VADER Sentiment Scores')

        if chart_outputFilename != None:
            if len(chart_outputFilename)> 0:
                filesToOpen.extend(chart_outputFilename)

    return filesToOpen

if __name__ == '__main__':
    # get arguments from command line
    parser = argparse.ArgumentParser(description='Sentiment analysis with VADER')
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
    sys.exit(main(args.inputFilename, args.inputDir, args.outputDir, args.outputFilename, args.mode))
