"""
Author Roberto Franzosi Cynthia Dong May 2020

Performs sentiment analysis on a text file using the NLTK's SentiWordNet sentiment analysis function.
The routine relies on the WordNet dictionary

https://stackoverflow.com/questions/38263039/sentiwordnet-scoring-with-python
https://github.com/aesuli/sentiwordnet
http://www.nltk.org/howto/sentiwordnet.html

"""

# The SentiWordNet algorithm outputs sentiment scores to 4 classes of sentiments:
# neg: Negative
# neu: Neutral
# pos: Positive
# compound: Compound (i.e. aggregated score)
#The "compound" score, ranging from -1 (most neg) to 1 (most pos) 
#   would provide a single measure of polarity.

import sys
import IO_files_util
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"sentiment_analysis_SentiWordNet",['nltk','os','csv','argparse','tkinter','time'])==False:
    sys.exit(0)

import csv
import os
import time
import argparse
import tkinter.messagebox as mb
import IO_csv_util

from nltk.corpus import wordnet as wn
from nltk.corpus import sentiwordnet as swn
from nltk import tokenize
from nltk import word_tokenize, pos_tag

# if SentiWordNet fails, run: "python -m nltk.downloader all"

IO_libraries_util.import_nltk_resource(GUI_util.window,'tokenizers/punkt','punkt')
# check WordNet
IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/WordNet','WordNet')
from nltk.stem.wordnet import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
# check stopwords
IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/stopwords','stopwords')
from nltk.corpus import stopwords
stops = set(stopwords.words("english"))

def penn_to_wn(tag):
    """
    Convert between the PennTreebank tags to simple Wordnet tags
    """
    if tag.startswith('J'):
        return wn.ADJ
    elif tag.startswith('N'):
        return wn.NOUN
    elif tag.startswith('R'):
        return wn.ADV
    elif tag.startswith('V'):
        return wn.VERB
    return None
 

# performs sentiment analysis on inputFile using the NLTK, outputting results to a new CSV file in outputDir
def analyzefile(inputFilename, outputDir, output_file, mode, documentID, documentName):
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
    if output_file == '':
        output_file = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'SC', 'SentiWordNet', '', '', '', False, True)

    # read file into string
    with open(inputFilename, 'r',encoding='utf-8',errors='ignore') as myfile:
        fulltext = myfile.read()
    # end method if file is empty
    if len(fulltext) < 1:
        mb.showerror(title='File empty', message='The file ' + inputFilename + ' is empty.\n\nPlease, use another file and try again.')
        print('Empty file '+ inputFilename)
        return

    sentences = tokenize.sent_tokenize(fulltext)  # split text into sentences

    # SentiWordNet Interface http://www.nltk.org/howto/sentiwordnet.html
    # SentiSynsets
    
    i = 1  # to store sentence index


    # analyze each sentence s for sentiment
    sentenceID = 1
    for s in sentences:
        tagged_sentence = pos_tag(word_tokenize(s))
        sentiment = 0
        tokens_count = 0
        label = ""
        for word, tag in tagged_sentence:
            wn_tag = penn_to_wn(tag)
            if wn_tag not in (wn.NOUN, wn.ADJ, wn.ADV):
                continue

            lemma = lemmatizer.lemmatize(word, pos=wn_tag)
            if not lemma:
                continue

            synsets = wn.synsets(lemma, pos=wn_tag)
            if not synsets:
                continue

            # Take the first sense, the most common
            synset = synsets[0]
            swn_synset = swn.senti_synset(synset.name())
            sentiment += swn_synset.pos_score() - swn_synset.neg_score()
            tokens_count += 1
            # judgment call ? Default to positive or negative
        if not tokens_count:
            sentiment = 2
            label = "neutral"
        elif sentiment / tokens_count >= 0:
            sentiment = 3
            label = "positive"
        else:
            sentiment = 1
            label = "negative"

        writer.writerow({'Document ID': documentID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(documentName), 'Sentence ID': sentenceID,
                            'Sentence': s,
                            Sentiment_measure: sentiment,
                            Sentiment_label: label,
                            })

        sentenceID += 1
    # csvfile.close()
    return output_file

fileNamesToPass = [] #LINE ADDED

def main(inputFilename, input_dir, outputDir, output_file, mode):
    """
    Runs analyzefile on the appropriate files, provided that the input paths are valid.
    :param inputFilename:
    :param input_dir:
    :param outputDir:
    :return:

    """

    if len(outputDir) < 0 or not os.path.exists(outputDir):
        print('No output directory specified, or path does not exist.')
        sys.exit(1)
    elif len(inputFilename) == 0 and len(input_dir)  == 0:
        print('No input specified. Please, provide either a single file -- file or a directory of files to be analyzed --dir.')
        sys.exit(1)
    # check each word in sentence for sentiment and write to output_file
    with open(output_file, 'w', encoding='utf-8',errors='ignore', newline='') as csvfile:
        global Sentiment_measure, Sentiment_label
        Sentiment_measure='Sentiment score'
        Sentiment_label='Sentiment value'
        fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence', Sentiment_measure, Sentiment_label]
        global writer
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        if len(inputFilename) > 0:  # handle single file
            if os.path.exists(inputFilename):
                fileNamesToPass.append(analyzefile(inputFilename, outputDir, output_file, mode, 1, inputFilename))
                output_file = analyzefile(inputFilename, outputDir, output_file, mode, 1, inputFilename)
                #print("Output Vader Sentiment " + output_file + " created")
            else:
                print('Input file "' + inputFilename + '" is invalid.')
                sys.exit(1)
        elif len(input_dir) > 0:  # handle directory
            documentID = 0
            if os.path.isdir(input_dir):
                directory = os.fsencode(input_dir)
                for file in os.listdir(directory):
                    filename = os.path.join(input_dir, os.fsdecode(file))
                    if filename.endswith(".txt"):
                        start_time = time.time()
                        print("Started SentiWordNet sentiment analysis of " + filename + "...")
                        documentID += 1
                        fileNamesToPass.append(analyzefile(filename, outputDir, output_file,mode, documentID, filename)) #LINE ADDED (edited)
                        print("Finished SentiWordNet sentiment analysis of " + filename + " in " + str((time.time() - start_time)) + " seconds")
                        #print("Output Vader Sentiment " + output_file + " created")
            else:
                print('Input directory "' + input_dir + '" is invalid.')
                sys.exit(1)
    return fileNamesToPass #LINE ADDED


if __name__ == '__main__':
    # get arguments from command line
    parser = argparse.ArgumentParser(description='Sentiment analysis with SentiWordNet')
    parser.add_argument('--file', type=str, dest='inputFilename', default='',
                        help='a string to hold the INPUT path and filename if only ONE txt file is processed; enter --file "" or eliminate --file flag to process ALL txt files in input directory; use "" if path and filenames contain spaces')
    parser.add_argument('--dir', type=str, dest='input_dir', default='',
                        help='a string to hold the INPUT path of the directory of ALL txt files to be processed; use "" if path contains spaces')
    parser.add_argument('--out', type=str, dest='outputDir', default='',
                        help='a string to hold the path of the OUTPUT directory; use "" if path contains spaces')
    parser.add_argument('--outfile', type=str, dest='output_file', default='',
                        help='output file')
       
    parser.add_argument('--mode', type=str, dest='mode', default='mean',
                        help='mode with which to calculate sentiment in the sentence: mean or median')
    args = parser.parse_args()

    # run main
    sys.exit(main(args.inputFilename, args.input_dir, args.outputDir, args.output_file, args.mode))