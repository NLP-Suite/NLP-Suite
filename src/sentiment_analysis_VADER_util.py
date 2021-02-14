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

if IO_libraries_util.install_all_packages(GUI_util.window, "sentiment_analysis_VADER", ['nltk','os','csv','argparse','pandas','tkinter','numpy','time','twython'])==False:
    sys.exit(0)

import csv
import os
import time
import argparse
import tkinter.messagebox as mb
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
from nltk import word_tokenize

import GUI_IO_util
import IO_csv_util

# if VADER fails, run: "python -m nltk.downloader all"

IO_libraries_util.import_nltk_resource(GUI_util.window,'tokenizers/punkt','punkt')
# check WordNet
IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/WordNet','WordNet')
from nltk.stem.wordnet import WordNetLemmatizer
# check stopwords
IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/stopwords','stopwords')
from nltk.corpus import stopwords
stops = set(stopwords.words("english"))
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
def analyzefile(input_file, output_dir, output_file, mode, Document_ID, Document):
    """
    Performs sentiment analysis on the text file given as input using the VADER database.
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
        mb.showerror(title='File empty', message='The file ' + input_file + ' is empty.\n\nPlease, use another file and try again.')
        print('Empty file '+ input_file)
        return

    sentences = tokenize.sent_tokenize(fulltext)  # split text into sentences
    sid = SentimentIntensityAnalyzer()  # create sentiment analyzer
    i = 1  # to store sentence index

    # check each word in sentence for sentiment and write to output_file
    # check each word in sentence for sentiment and write to output_file
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

        writer.writerow({'Document ID': Document_ID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document), 'Sentence ID': i,
                            'Sentence': s,
                            Sentiment_measure: sentiment,
                            Sentiment_label: label,
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
    #csvfile.close()
    return output_file

fileNamesToPass = [] #LINE ADDED

def main(input_file, input_dir, output_dir, output_file, mode):
    """
    Runs analyzefile on the appropriate files, provided that the input paths are valid.
    :param input_file:
    :param input_dir:
    :param output_dir:
    :return:

    """

    if len(output_dir) < 0 or not os.path.exists(output_dir):
        print('No output directory specified, or path does not exist.')
        sys.exit(1)
    elif len(input_file) == 0 and len(input_dir)  == 0:
        print('No input specified. Please, provide either a single file -- file or a directory of files to be analyzed --dir.')
        sys.exit(1)
    with open(output_file, 'w', encoding='utf-8',errors='ignore', newline='') as csvfile:

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
        fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence', Sentiment_measure, Sentiment_label]
        global writer
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        if len(input_file) > 0:  # handle single file
            if os.path.exists(input_file):
                fileNamesToPass.append(analyzefile(input_file, output_dir, output_file, mode, 1, input_file))
                output_file = analyzefile(input_file, output_dir, output_file, mode, 1, input_file)
                #print("Output Vader Sentiment " + output_file + " created")
            else:
                print('Input file "' + input_file + '" is invalid.')
                sys.exit(1)
        elif len(input_dir) > 0:  # handle directory
            if os.path.isdir(input_dir):
                directory = os.fsencode(input_dir)
                documentID = 0
                for file in os.listdir(directory):
                    filename = os.path.join(input_dir, os.fsdecode(file))
                    if filename.endswith(".txt"):
                        documentID += 1
                        start_time = time.time()
                        print("Started VADER sentiment analysis of " + filename + "...")
                        output_file=''
                        analyzefile(filename, output_dir, output_file,mode, documentID, filename)
                        print("Finished VADER sentiment analysis of " + filename + " in " + str((time.time() - start_time)) + " seconds")
                        #print("Output Vader Sentiment " + output_file + " created")
            else:
                print('Input directory "' + input_dir + '" is invalid.')
                sys.exit(1)
    return fileNamesToPass #LINE ADDED


if __name__ == '__main__':
    # get arguments from command line
    parser = argparse.ArgumentParser(description='Sentiment analysis with VADER')
    parser.add_argument('--file', type=str, dest='input_file', default='',
                        help='a string to hold the INPUT path and filename if only ONE txt file is processed; enter --file "" or eliminate --file flag to process ALL txt files in input directory; use "" if path and filenames contain spaces')
    parser.add_argument('--dir', type=str, dest='input_dir', default='',
                        help='a string to hold the INPUT path of the directory of ALL txt files to be processed; use "" if path contains spaces')
    parser.add_argument('--out', type=str, dest='output_dir', default='',
                        help='a string to hold the path of the OUTPUT directory; use "" if path contains spaces')
    parser.add_argument('--outfile', type=str, dest='output_file', default='',
                        help='output file')
       
    parser.add_argument('--mode', type=str, dest='mode', default='mean',
                        help='mode with which to calculate sentiment in the sentence: mean or median')
    args = parser.parse_args()

    # run main
    sys.exit(main(args.input_file, args.input_dir, args.output_dir, args.output_file, args.mode))