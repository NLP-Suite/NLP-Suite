# Written by Roberto Franzosi November 2019
# Edited by Josh Karol
import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"statistics_txt_util",['nltk','csv','tkinter','os','string','collections','re','textstat','itertools','stanza','spacy'])==False:
    sys.exit(0)

import os
import os
import tkinter as tk
import tkinter.messagebox as mb
import collections
import re
from collections import Counter
import string
from nltk.stem.porter import PorterStemmer
import stanza

# from nltk import tokenize
# from nltk import word_tokenize
# from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza
#
# import ast
# import textstat
# import subprocess
# import spacy
# from nltk.tree import Tree
# from nltk.draw import TreeView
# from PIL import Image

# Sentence Complexity
import tree
import node_sentence_complexity as Node

# from gensim.utils import lemmatize
from itertools import groupby
import pandas as pd
# import ast
# import textstat
# import subprocess
import spacy
import csv
import nltk
from nltk.tree import Tree
from nltk.draw import TreeView
from PIL import Image

#For objectivity/subjectivity
from spacytextblob.spacytextblob import SpacyTextBlob

#whether stopwordst were already downloaded can be tested, see stackoverflow
#   https://stackoverflow.com/questions/23704510/how-do-i-test-whether-an-nltk-resource-is-already-installed-on-the-machine-runni
#   see also caveats

# check stopwords
# IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/stopwords','stopwords')
# check punkt
IO_libraries_util.import_nltk_resource(GUI_util.window,'tokenizers/punkt','punkt')

from nltk.corpus import stopwords
from nltk.corpus import wordnet
# from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza
from itertools import groupby
import textstat

import IO_user_interface_util
import GUI_IO_util
import charts_util
import IO_files_util
import IO_csv_util
import reminders_util
import TIPS_util

#https://github.com/nltk/nltk/wiki/Frequently-Asked-Questions-(Stackoverflow-Edition)
#to compute bigrams, 3-grams, ...
#   from nltk import bigrams, trigrams
#   from nltk import ngrams
#   from nltk import everygrams

#https://stackoverflow.com/questions/24347029/python-nltk-bigrams-trigrams-fourgrams
# def compute_word_ngrams(window,inputFilename,outputFilename):
#     import nltk
#     #from nltk import word_tokenize
#     from nltk.util import ngrams
#     #OutputFile = open(outputFilename,"w")
#     text = (open(inputFilename, "r", encoding="utf-8").read())
#     #OutputFile.write ("2-grams, 3-grams, 4-grams, 5-grams")
#     grams2 = ngrams(text.split(), 2)
#     for grams in grams2 :
#         print(grams)
#     grams3 = [ngrams(text.split(), 3)]
#     for grams in grams3 :
#         print(grams)
#     grams4 = [ngrams(text.split(), 4)]
#     for grams in grams4 :
#         print(grams)

# returns a frequency distribution of words in text,
#    in the format {"chapman's": 1, 'carried': 1, 'hinesville': 1, 'broke': 1, 'an': 3,...

def get_wordnet_pos(word):#from https://www.machinelearningplus.com/nlp/lemmatization-examples-python/
    #https://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python
    #assign pos value to one word
    #sometimes the accuracy will be affected: for example, lemmatization of leaves can be both verb(leave) and noun(leaf)
    #this function put noun ahead of verb when assigning pos tags
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    return tag_dict.get(tag, wordnet.NOUN)


# def lemmatizing(word):#lemmatization with pos value
#     lemmatizer = WordNetLemmatizer()
#     return lemmatizer.lemmatize(word, get_wordnet_pos(word))

def lemmatizing(word):#edited by Claude Hu 08/2020
    #https://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python
    pos = ['n', 'v','a', 's', 'r']#list of postags
    result = word
    for p in pos:
        # if lemmatization with any postag gives different result from the word itself
        # that lemmatization is returned as result
        # lemmatizer = WordNetLemmatizer()
        # lemma = lemmatizer.lemmatize(word, p)
        from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza
        lemma = lemmatize_stanza(stanzaPipeLine(word))
        if lemma != word:
            result = lemma
            break
    return result


def word_count(text):
    counts = dict()
    words = text.split()
    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
    return counts


def excludeStopWords_list(words):
    # stop_words = stopwords.words('english')
    fin = open('../lib/wordLists/stopwords.txt', 'r')
    stop_words = set(fin.read().splitlines())
    # since stop_words are lowercase exclude initial-capital words (He, I)
    words_excludeStopwords = [word for word in words if not word.lower() in stop_words]
    words = words_excludeStopwords
    # exclude punctuation
    words_excludePunctuation = [word for word in words if not word in string.punctuation]
    words = words_excludePunctuation
    return words


# https://www.nltk.org/book/ch02.html
# For the Gutenberg Corpus they provide the programming code to do it. section 1.9   Loading your own Corpus.
# see also https://people.duke.edu/~ccc14/sta-663/TextProcessingSolutions.html
def compute_corpus_statistics(window, inputFilename, inputDir, outputDir, configFileName, openOutputFiles, createCharts, chartPackage,
                              excludeStopWords=True, lemmatizeWords=True):
    filesToOpen = []

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='corpus_stats',
                                                       silent=True)
    if outputDir == '':
        return

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'corpus_stats', '')
    filesToOpen.append(outputFilename)
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False, configFileName=configFileName)

    # read_line(inputFilename, inputDir, outputDir)
    # return

    Ndocs = str(len(inputDocs))
    fieldnames = ['Number of documents in corpus',
                  'Document ID',
                  'Document',
                  'Number of Sentences in Document',
                  'Number of Words in Document',
                  'Number of Syllables in Document',
                  'Word1', 'Frequency1',
                  'Word2', 'Frequency2',
                  'Word3', 'Frequency3',
                  'Word4', 'Frequency4',
                  'Word5', 'Frequency5',
                  'Word6', 'Frequency6',
                  'Word7', 'Frequency7',
                  'Word8', 'Frequency8',
                  'Word9', 'Frequency9',
                  'Word10', 'Frequency10',
                  'Word11', 'Frequency11',
                  'Word12', 'Frequency12',
                  'Word13', 'Frequency13',
                  'Word14', 'Frequency14',
                  'Word15', 'Frequency15',
                  'Word16', 'Frequency16',
                  'Word17', 'Frequency17',
                  'Word18', 'Frequency18',
                  'Word19', 'Frequency19',
                  'Word20', 'Frequency20']
    if IO_csv_util.openCSVOutputFile(outputFilename):
        return

    startTime = IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                                   'Started running document(s) statistics at',
                                                   True, '', True, '', False)

    with open(outputFilename, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        # print("Number of corpus text documents: ",Ndocs)
        # currentLine.append([Ndocs])
        documentID = 0
        for doc in inputDocs:
            head, tail = os.path.split(doc)
            documentID = documentID + 1
            # currentLine.append([documentID])
            print("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)
            # currentLine.append([doc])
            # fullText = (open(doc, "r", encoding="utf-8", errors="ignore").read())
            f = open(doc, "r", encoding="utf-8", errors="ignore")
            docText = f.read()
            f.close()
            Nsentences = textstat.sentence_count(docText)
            # print('TOTAL number of sentences: ',Nsentences)

            Nwords = textstat.lexicon_count(docText, removepunct=True)
            # print('TOTAL number of words: ',Nwords)

            Nsyllables = textstat.syllable_count(docText, lang='en_US')
            # print('TOTAL number of Syllables: ',Nsyllables)

            # words = fullText.split()
            # words = nltk.word_tokenize(fullText)
            from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, \
                lemmatize_stanza
            words = word_tokenize_stanza(stanzaPipeLine(docText))

            if excludeStopWords:
                words = excludeStopWords_list(words)

            if lemmatizeWords:
                # lemmatizer = WordNetLemmatizer()
                text_vocab = []
                for w in words:
                    if w.isalpha():
                        # text_vocab.append(lemmatizer.lemmatize(w.lower()))
                        from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, \
                            lemmatize_stanza
                        text_vocab.append(lemmatize_stanza(stanzaPipeLine(w.lower())))

                words = text_vocab

            word_counts = Counter(words)

            # 20 most frequent words in the document
            # print("\n\nTOP 20 most frequent words  ----------------------------")
            # for item in word_counts.most_common(20):
            #     print(item)
            currentLine = [
                [Ndocs, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc), Nsentences, Nwords, Nsyllables]]
            for item in word_counts.most_common(20):
                currentLine[0].append(item[0])  # word
                currentLine[0].append(item[1])  # frequency
            writer = csv.writer(csvfile)
            writer.writerows(currentLine)

        csvfile.close()

        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                           'Finished running document(s) statistics at', True, '', True, startTime,
                                           False)

    # number of sentences in input ---------------------------------------------------------------------
    # number of words in input ---------------------------------------------------------------------
    # number of syllables in input ---------------------------------------------------------------------
    columns_list = [['Document', 'Number of Sentences in Document'], ['Document', 'Number of Words in Document'], ['Document', 'Number of Syllables in Document']]
    import statistics_csv_util
    columns_to_be_plotted_numeric = statistics_csv_util.get_columns_to_be_plotted(outputFilename, columns_list)
    outputFiles = charts_util.run_all(columns_to_be_plotted_numeric, outputFilename, outputDir,
                          outputFileLabel='sent-word-syll',
                          chartPackage=chartPackage,
                          chart_type_list=['bar'],
                          chart_title='Number of Sentences, Words, Syllables by Document',
                          column_xAxis_label_var='Document',
                          column_yAxis_label_var='Frequencies',
                          hover_info_column_list=[],
                          count_var=0)  # always 1 to get frequencies of values, except for n-grams where we already pass stats

    if outputFiles != None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    # compute and chart mean, mode, skewness, kurtosis
    #   need at least 3 values, i.e., 3 documents, to compute skewness and kurtosis
    # do not use the compute_csv_column_statistics_groupBy function since only one value is available for
    #   each document
    columns_list = [['Document', 'Number of Sentences in Document'], ['Document', 'Number of Words in Document'], ['Document', 'Number of Syllables in Document']]
    columns_to_be_plotted_numeric = statistics_csv_util.get_columns_to_be_plotted(outputFilename, columns_list)

    # convert columns_to_be_plotted_numeric double list to list
    flat_list = []
    for row in columns_to_be_plotted_numeric:
        flat_list.extend(row)
    columns_to_be_plotted_numeric=flat_list

    outputFiles = statistics_csv_util.compute_csv_column_statistics_NoGroupBy(window, outputFilename, outputDir, False,
                                            createCharts, chartPackage,
                                            columns_to_be_plotted_numeric)

    if outputFiles != None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    # TODO
        #   we should create 10 classes of values by distance to the median of
        #       each value in the Number of Words in Document Col. E
        #   -0-10 11-20 21-30,… 91-100
        #   and plot them as column charts.

        # if openOutputFiles==True:
        #     IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
    return filesToOpen


def Extract(lst):
    return [item[0] for item in lst]


def same_document_check(jgram):
    documentID = jgram[0][1]
    for token in jgram:
        if token[1] != documentID:
            return False
        else:
            continue
    return True


def compute_sentence_length(inputFilename, inputDir, outputDir, configFileName, createCharts, chartPackage):
    filesToOpen = []
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False, configFileName=configFileName)
    Ndocs = len(inputDocs)
    if Ndocs == 0:
        return
    startTime = IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                                   'Started running sentence length algorithm at',
                                                   True, '', True, '', False)

    fileID = 0
    long_sentences = 0
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                             'sentence_length')
    csv_headers = ['Sentence length (in words)', 'Sentence ID', 'Sentence', 'Document ID', 'Document']

    with open(outputFilename, 'w', newline="", encoding='utf-8', errors='ignore') as csvOut:
        writer = csv.writer(csvOut)
        writer.writerow(csv_headers)
        for doc in inputDocs:
            sentenceID = 0
            fileID = fileID + 1
            head, tail = os.path.split(doc)
            print("Processing file " + str(fileID) + "/" + str(Ndocs) + ' ' + tail)
            with open(doc, 'r', encoding='utf-8', errors='ignore') as inputFile:
                text = inputFile.read().replace("\n", " ")
                from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, \
                    lemmatize_stanza
                # sentences = tokenize.sent_tokenize(text)
                sentences = sent_tokenize_stanza(stanzaPipeLine(text))
                if len(sentences)==0:
                    mb.showwarning('Warning','The input file\n\n' + doc + '\n\nappears to be empty. Please, check the file and try again.')
                    return filesToOpen
                for sentence in sentences:
                    # tokens = nltk.word_tokenize(sentence)
                    tokens = word_tokenize_stanza(stanzaPipeLine(sentence))
                    if len(tokens) > 100:
                        long_sentences = long_sentences + 1
                    sentenceID = sentenceID + 1
                    writer.writerow(
                        [len(tokens), sentenceID, sentence, fileID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])
        csvOut.close()
        head, scriptName = os.path.split(os.path.basename(__file__))
        reminder_status = reminders_util.checkReminder(scriptName,
                                                       reminders_util.title_options_TIPS_file,
                                                       reminders_util.message_TIPS_file,
                                                       True)
        if reminder_status == 'Yes' or reminder_status == 'ON':  # 'Yes' the old way of saving reminders
            answer = tk.messagebox.askyesno("TIPS file on memory issues", str(Ndocs) + " file(s) processed in input.\n\n" +
                                            "Output csv file written to the output directory " + outputDir + "\n\n" +
                                            str(
                                                long_sentences) + " SENTENCES WERE LONGER THAN 100 WORDS (the average sentence length in modern English is 20 words).\n\nMore to the point... Stanford CoreNLP would heavily tax memory resources with such long sentences.\n\nYou should consider editing these sentences if Stanford CoreNLP takes too long to process the file or runs out of memory.\n\nPlease, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.\n\nDo you want to open the TIPS file now?")
            if answer:
                TIPS_util.open_TIPS('TIPS_NLP_Stanford CoreNLP memory issues.pdf')

    filesToOpen.append(outputFilename)

    outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                       columns_to_be_plotted_xAxis=[],
                                                       columns_to_be_plotted_yAxis=['Sentence length (in words)'],
                                                       chart_title='Sentence Length (In Words)',
                                                       count_var=1, hover_label=[],
                                                       outputFileNameType='Sent', #'line_bar',
                                                       column_xAxis_label='Sentence length',
                                                       groupByList=['Document'],
                                                       plotList=['Sentence length (in words)'],
                                                       chart_title_label='Sentence Lenghts')

    if outputFiles!=None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    return filesToOpen

def compute_line_length(window, configFileName, inputFilename, inputDir, outputDir,openOutputFiles,createCharts, chartPackage):
    filesToOpen=[]
    outputFilename=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'line_length')
    filesToOpen.append(outputFilename)
    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False, configFileName=configFileName)
    Ndocs = str(len(inputDocs))
    if Ndocs==0:
        return
    head, scriptName = os.path.split(os.path.basename(__file__))
    reminders_util.checkReminder(scriptName, reminders_util.title_options_line_length,
                                 reminders_util.message_line_length, True)
    fieldnames=[
        'Line length (in characters)',
        'Line length (in words)',
        'Line ID',
        'Line',
        'Document ID',
        'Document'
    ]
    if IO_csv_util.openCSVOutputFile(outputFilename):
        return
    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running line length analysis at',
                                                 True, '', True, '', True)

    with open(outputFilename, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer = csv.writer(csvfile)
        documentID = 0
        for doc in inputDocs:
            head, tail = os.path.split(doc)
            documentID += 1
            print("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)
            with open(doc, encoding='utf-8', errors='ignore') as file:
                lineID = 0
                try:
                    line = file.readline()
                except OSError as e:
                    print(str(e))
                    if 'UnicodeDecodeError' in str(e):
                        mb.showwarning(title='Input file error',
                                       message="The file\n\n" + doc + "\n\ncontains an invalid character. Please, check the file and try again. You may need to run the script to clean apostrophes and quotes.")
                    line='THE LINE CONTAINS ILLEGAL, NON UTF-8 CHARACTERS. PLEASE, CHECK.'
                    print('   ',line)
                    # continue
                while line:
                    lineID += 1
                    # words = nltk.word_tokenize(line)
                    from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, \
                        lemmatize_stanza
                    words = word_tokenize_stanza(stanzaPipeLine(line))
                    # print("Line {}: Length (in characters) {} Length (in words) {}".format(lineID, len(line), len(words)))
                    currentLine = [
                        [len(line), len(words),lineID,line.strip(), documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)]]
                    writer.writerows(currentLine)
                    line = file.readline()
    csvfile.close()

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running line length analysis at', True, '', True, startTime, True)

    # produce all charts
    outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                              columns_to_be_plotted_xAxis=[],
                                              columns_to_be_plotted_yAxis=['Line length (in words)'],
                                              chart_title='Frequency Distribution of Line Length',
                                              count_var=1, hover_label=[],
                                              outputFileNameType='', #'line_bar', column_xAxis_label='Line length',
                                              column_xAxis_label='Line length',
                                              groupByList=['Document'],
                                              plotList=['Line length (in words)'],
                                              chart_title_label='Line Length')

    if outputFiles!=None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    return filesToOpen


#compute_character_word_ngrams works for BOTH character and word ngrams
#https://stackoverflow.com/questions/18658106/quick-implementation-of-character-n-grams-for-word
#ngrams is the type of ngrams wanted 2grams,3grams,4grams,5grams MAX

# frequency = 0 n-grams
# frequency = 1 hapax

def compute_character_word_ngrams(window,inputFilename,inputDir,outputDir, configFileName,
                                  ngramsNumber=3,
                                  normalize=False,
                                  excludePunctuation=True, excludeDeterminants=True, excludeStopwords=True,
                                  wordgram=None,
                                  frequency = 0, openOutputFiles=False,
                                  createCharts=True, chartPackage='Excel', bySentenceID=None):
    # hapax have ngramsNumber = 1 and frequency = 1

    filesToOpen = []
    container = []
    if inputFilename=='' and inputDir=='':
        mb.showwarning(title='Input error', message='No input file or input directory have been specified.\n\nThe function will exit.\n\nPlease, enter the required input options and try again.')
        return

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'N-Grams start',
                                       'Started running Word/Characters N-Grams at',
                                       True, '', True, '', False)

    files = IO_files_util.getFileList(inputFilename, inputDir, '.txt', silent=False, configFileName=configFileName)
    nFile=len(files)
    if nFile==0:
        return

    if ngramsNumber == 1 and frequency == 1: # hapax
        hapax_label = "_hapax"
    else:
        hapax_label = ''

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='Ngrams'+hapax_label,
                                                       silent=True)
    if outputDir == '':
        return

    if wordgram==None:
        result = mb.askyesno("Word/character N-grams","Would you like to compute\n  WORD n-grams (Yes) or\n  CHARACTER n-grams (No)?")
        if result==True:
            wordgram=1
        else:
            wordgram=0

    if bySentenceID==None:
        result = mb.askyesno("By sentence index","Would you like to compute n-grams by sentence index?")
        if result==True:
            bySentenceID=1
        else:
            bySentenceID=0

    filesToOpen = get_ngramlist(inputFilename, inputDir, outputDir, configFileName, ngramsNumber, wordgram,
                                excludePunctuation, excludeDeterminants, excludeStopwords, frequency,
                                bySentenceID,  createCharts, chartPackage)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                                       'Finished running Word/Characters N-Grams at', True, '', True, startTime, False )

    return filesToOpen


def process_punctuation(inputFilename, inputDir, excludePunctuation, ngrams_list, ctr_document, documentID):
    ngrams_list = []

    for item in ctr_document: # item is every token in the document
        if item in string.punctuation and excludePunctuation:
            continue
        if inputDir == '':
            ngrams_list.append([item, ctr_document[item], documentID, IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)])
        else:
            # insert 0 for corpus frequency to be updated at a later point
            ngrams_list.append([item, ctr_document[item], 0, documentID, IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)])
    return ngrams_list

# process the sentence ngramsList for frequency = 1 only (hapax legomena)
def process_hapax(ngramsList, frequency, excludePunctuation):
    if excludePunctuation:
        freq_col = 1
    else:
        freq_col = 2
    if frequency == 1:  # hapax
        # for hapax legomena keep rows with frequency=1 only; exclude items with frequency>1, i.e. i[1] > 1
        ngramsList_new=list(filter(lambda a: a[freq_col] == 1, ngramsList))
        ngramsList=ngramsList_new
    return ngramsList

# re-written by Roberto June 2022

import ngrams_util
def get_ngramlist(inputFilename, inputDir, outputDir, configFileName, ngramsNumber=3, wordgram=1,
    excludePunctuation=True, excludeDeterminants=True, excludeStopWords=True,
    frequency = None, bySentenceID=False, createCharts=True,chartPackage='Excel'):
    files = IO_files_util.getFileList(inputFilename, inputDir, '.txt', silent=False, configFileName=configFileName)
    # print(excludePunctuation)
    documents = [ngrams_util.readandsplit(i,excludePunctuation, excludeDeterminants, excludeStopWords,len(files)) for i in files]
    # we need to allow as many n-grams as the user selects in ngramsNumber 1-6
    onegram_freq, bigram_freq, trigram_freq = ngrams_util.operate(documents,files,ngramsNumber)
    results = [onegram_freq, bigram_freq, trigram_freq]
    filesToOpen = []
    for index,result in enumerate(results):
        corpus_ngramsList = result.values.tolist()
        corpus_ngramsList.insert(0,[str(index+1)+'-grams', 'Frequency in Document', 'Frequency in Corpus', 'Document ID', 'Document'])
        csv_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                     'n-grams' + str(index+1) + '_Word',
                                                                     'stats', '', '',
                                                                     '', False, True)
        errorFound = IO_csv_util.list_to_csv(GUI_util.window, corpus_ngramsList, csv_outputFilename)

        if not errorFound:
            filesToOpen.append(csv_outputFilename)
            columns_to_be_plotted_xAxis = [str(index+1) + '-grams']
            if inputDir == '':
                columns_to_be_plotted_yAxis = ['Frequency in Document']
            else:
                columns_to_be_plotted_yAxis = ['Frequency in Document', 'Frequency in Corpus']
            outputFiles = charts_util.visualize_chart(createCharts, chartPackage, csv_outputFilename,
                                                      outputDir,
                                                      columns_to_be_plotted_xAxis=columns_to_be_plotted_xAxis,
                                                      columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
                                                      chart_title='Frequency of ' + str(index+1) + '-gram' ,
                                                      count_var=0, hover_label=[],  # hover_label,
                                                      # outputFileNameType='n-grams_'+str(gram), # +'_'+ tail,
                                                      outputFileNameType='',
                                                      column_xAxis_label=str(index+1) + '-gram',
                                                      groupByList=['Document'],
                                                      plotList=['Frequency in Document'],
                                                      chart_title_label=str(index+1) + '-gram')
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)
    return filesToOpen
# # return a list for each document
# def get_ngramlist(inputFilename, inputDir, outputDir, configFileName, ngramsNumber=3, wordgram=1, excludePunctuation=True, frequency = None, bySentenceID=False, createCharts=True,chartPackage='Excel'):
#
#     # the function combines each token with the next token in the list
#     def combine_tokens_in_ngrams(ngrams_list):
#         t = []
#         str = ''
#         for jgramlist in ngrams_list:
#             for word in jgramlist:
#                 str += (word[0] + ' ')
#             str = str.strip()
#             t.append([str, jgramlist[0][1],jgramlist[0][2]])
#             str = ''
#         return t
#
#     if wordgram==0:
#         mb.showinfo(title='Warning', message='The computation of character n-grams is currently not available. Sorry!')
#         return
#     files = IO_files_util.getFileList(inputFilename, inputDir, '.txt', silent=False, configFileName=configFileName)
#     nFile=len(files)
#     if nFile==0:
#         return
#
#     if wordgram==1:
#         gram_type_label_short="Wd"
#         gram_type_label_full="Word"
#     else:
#         gram_type_label_short="Ch"
#         gram_type_label_full="Character"
#
#     filesToOpen = []
#
#     if frequency==1: # hapax
#         hapax_label="_hapax_"
#         hapax_header=" (hapax)"
#         ngramsNumber=1 # if hapax, there is no point computing higher-level n-grams
#     else:
#         hapax_label=""
#         hapax_header=""
#
#     gram = 1
#     while gram <= ngramsNumber:
#         container = []
#         documentID = 0
#         ngramsList = []
#         corpus_ngramsList = []
#         corpus_tokens = []
#         print("Processing " + gram_type_label_full + " n-grams " + str(gram) + "/" + str(ngramsNumber))
#         for file in files:
#             head, tail = os.path.split(file)
#             documentID += 1
#             Sentence_ID = 0
#             doc_ngramsList = []
#             print("   Processing file " + str(documentID) + "/" + str(nFile) + ' ' + tail)
#             text = (open(file, "r", encoding="utf-8", errors='ignore').read())
#
# # word ngrams ---------------------------------------------------------
#
#             if wordgram==1: # word ngrams
#                 document_tokens=[]
#                 from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, \
#                     lemmatize_stanza
#                 for tk in word_tokenize_stanza(stanzaPipeLine(text)):
#                     document_tokens.append([tk, documentID, file])
#                 corpus_tokens.append(document_tokens)
#
#                 ngrams=[]
#                 ngrams = [document_tokens[i:i+gram] for i in range(len(document_tokens)-(gram-1))]
#                 # compute all ngrams, combining each token with the next token(s) and convert triple list to double list [[
#                 ngrams = combine_tokens_in_ngrams([tk for tk in ngrams if same_document_check(tk)])
#                 # the counter contains the frequency of each token in the document
#                 ctr_document = collections.Counter(Extract(ngrams))
#                 # process punctuation
#                 document_ngramsList=process_punctuation(file, inputDir, excludePunctuation, ngrams, ctr_document, documentID)
#                 # process hapax
#                 document_ngramsList = process_hapax(document_ngramsList, frequency, excludePunctuation)
#
#                 if len(ngrams)>1 and isinstance(ngrams[0], list):
#                     ngramsList.extend(ngrams)
#                 else:
#                     ngramsList.append(ngrams)
#                 if len(document_ngramsList)>1 and isinstance(document_ngramsList[0], list):
#                     corpus_ngramsList.extend(document_ngramsList)
#                 else:
#                     corpus_ngramsList.append(document_ngramsList)
#         if excludePunctuation:
#             corpus_freq_pos = 2  # corpus frequency position
#         else:
#             corpus_freq_pos = 3  # corpus frequency position
#
#         if inputDir != '':
#             # n-grams frequencies must be computed by entire corpus
#             try:
#                 # n-grams frequencies must be computed by entire corpus
#                 ctr_corpus = collections.Counter(Extract(ngramsList))
#             except:
#                 temp = Extract(ngramsList)
#                 ctr_corpus = collections.Counter(Extract(temp))
#             # loop through the distinct values of every token in the corpus to get their frequencies
#             for item in ctr_corpus:
#                 # loop through all values of the ngramsList organized by documents
#                 #   so as to update the specific token for its corpus frequency
#                 for ngrams in corpus_ngramsList:
#                     if ngrams[0]==item:
#                         corpus_freq = ctr_corpus[item]
#                         ngrams[corpus_freq_pos]=corpus_freq # compute n-grams corpus frequencies
#
#         # code breaks
#         # ngramsList = sorted(ngramsList, key=lambda x: x[1])
#
#         # insert headers
#         if inputDir == '':
#             corpus_ngramsList.insert(0, [str(gram) + '-grams' + hapax_header, 'Frequency in Document',
#                                  'Document ID', 'Document'])
#         else:
#             corpus_ngramsList.insert(0, [str(gram) + '-grams' + hapax_header, 'Frequency in Document', 'Frequency in Corpus',
#                                          'Document ID', 'Document'])
#
#         columns_to_be_plotted_xAxis=[str(gram) + '-grams' + hapax_header]
#         if inputDir == '':
#             columns_to_be_plotted_yAxis=['Frequency in Document']
#         else:
#             columns_to_be_plotted_yAxis=['Frequency in Document', 'Frequency in Corpus']
#         # save output file after each n-gram value in the range
#         # code in next line breaks
#         # corpus_ngramsList = sorted(corpus_ngramsList, key=lambda x: x[1])
#         csv_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
#                                                                      'n-grams' + str(gram) + '_' + gram_type_label_short,
#                                                                      hapax_label + 'stats', '', '',
#                                                                      '', False, True)
#         errorFound = IO_csv_util.list_to_csv(GUI_util.window, corpus_ngramsList, csv_outputFilename)
#
#         if not errorFound:
#             filesToOpen.append(csv_outputFilename)
#             outputFiles = charts_util.visualize_chart(createCharts, chartPackage, csv_outputFilename,
#                                                                outputDir,
#                                                                columns_to_be_plotted_xAxis=columns_to_be_plotted_xAxis,
#                                                                columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
#                                                                chart_title='Frequency of ' + str(gram) + '-gram' + hapax_header,
#                                                                count_var=0, hover_label=[], #hover_label,
#                                                                # outputFileNameType='n-grams_'+str(gram), # +'_'+ tail,
#                                                                outputFileNameType='',
#                                                                column_xAxis_label=str(gram) + '-gram',
#                                                                groupByList=['Document'],
#                                                                plotList=['Frequency in Document'],
#                                                                chart_title_label=str(gram) + '-gram')
#             if outputFiles!=None:
#                 if isinstance(outputFiles, str):
#                     filesToOpen.append(outputFiles)
#                 else:
#                     filesToOpen.extend(outputFiles)
#         gram += 1
#
#     return filesToOpen

def tokenize(s):
    tokens = re.split(r"[^0-9A-Za-z\-'_]+", s)
    return tokens

# measures lexical diversity
# see code in cophi https://github.com/cophi-wue/cophi-toolbox
# code from https://gist.github.com/magnusnissel/d9521cb78b9ae0b2c7d6#file-lexical_diversity_yule-py
def get_yules_k_i(s):
    """
    Returns a tuple with Yule's K and Yule's I.
    (cf. Oakes, M.P. 1998. Statistics for Corpus Linguistics.
    International Journal of Applied Linguistics, Vol 10 Issue 2)

    In production this needs exception handling.
    """
    tokens = tokenize(s)
    token_counter = collections.Counter(tok.upper() for tok in tokens)
    m1 = sum(token_counter.values())
    m2 = sum([freq ** 2 for freq in token_counter.values()])
    i = (m1*m1) / (m2-m1)
    # k = 10000/i
    k = 1/i * 10000
    return (k, i)

# https://swizec.com/blog/measuring-vocabulary-richness-with-python/swizec/2528
def yule(window, inputFilename, inputDir, outputDir, configFileName, hideMessage=False):
    # yule's I measure (the inverse of yule's K measure)
    # higher number is higher diversity - richer vocabulary
    filesToOpen = []
    Yule_value_list=[]
    headers = ["Yule's K Value", "Document ID", "Document"]
    index = 0
    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False, configFileName=configFileName)

    Ndocs=str(len(inputDocs))
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'Yule K')
    Yule_value_list.insert(0, headers)
    for doc in inputDocs:
        head, tail = os.path.split(doc)
        d = {}
        index = index + 1
        print("Processing file " + str(index) + "/" + str(Ndocs) + " " + tail)
        fullText = (open(doc, "r", encoding="utf-8", errors="ignore").read())
        words = filter(lambda w: len(w) > 0,
                  [w.strip("0123456789!:,.?(){}[]") for w in fullText.translate(string.punctuation).lower().split()])
        stemmer = PorterStemmer()
        for w in words:
            w = stemmer.stem(w).lower()
            try:
                d[w] += 1
            except KeyError:
                d[w] = 1
        # TODO
        # get freq of unique words and print it in the end
        M1 = float(len(d))
        M2 = sum([len(list(g))*(freq**2) for freq,g in groupby(sorted(d.values()))])

        try:
            result=round((M1*M1)/(M2-M1),2)
        except ZeroDivisionError:
            result= 0

        # print results
        if inputFilename!='' and hideMessage==False:
            IO_user_interface_util.timed_alert(GUI_util.window, 4000, message_title='Yule’s K Vocabulary richness', message_text='The value for the vocabulary richness statistics (word type/token ratio or Yule’s K) is: '+str(result) + '\n\nValue range: 0-100. The higher the value, the richer the vocabulary.')
            print('The value for the vocabulary richness statistics (word type/token ratio or Yule’s K) is: '+str(result) + '\n\nThe higher the value (0-100) and the richer is the vocabulary.\n\nValue range: 0-100. The higher the value, the richer the vocabulary.')
        temp = [result,index,IO_csv_util.dressFilenameForCSVHyperlink(doc)]
        Yule_value_list.append(temp)
    IO_error=IO_csv_util.list_to_csv(window, Yule_value_list, outputFilename)
    if not IO_error:
        filesToOpen.append(outputFilename)

    return filesToOpen


def print_results(window, words, class_word_list, header, inputFilename, outputDir, excludestowords, fileLabel, hideMessage, filesToOpen):
    if excludestowords:
        stopMsg="(excluding stopwords)"
    else:
        stopMsg="(including stopwords)"
    # outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', fileLabel)
    # # class_word_list.insert(0, header,IO_csv_util.dressFilenameForCSVHyperlink(inputFilename))
    # class_word_list.insert(0, header)
    # IO_error=IO_csv_util.list_to_csv(window, class_word_list, outputFilename)
    # if IO_error:
    #     outputFilename=''

    if hideMessage==False:
        # do not count header
        mb.showinfo(title='Results', message='Total word count ' + stopMsg + ': ' + str(len(words)) +
                                             '\n\nTotal word count for ' + header + ' ' + stopMsg + ': ' + str(len(class_word_list)-1))
    # print results
    print('\nTotal word count ' + stopMsg + ': ' + str(len(words)))
    # do not count header
    print('Total word count for ' + header + ' ' + stopMsg + ': ' + str(len(class_word_list)-1))
    print('\n\nList of ' + header + ' ' + stopMsg + '\n\n', class_word_list)
    # if outputFilename != '':
    #     filesToOpen.append(outputFilename)
    # return filesToOpen


# called by sentence_analysis_main and style_analysis_main
def process_words(window, configFileName, inputFilename,inputDir,outputDir, openOutputFiles, createCharts, chartPackage,
    processType='', language='English', excludeStopWords=True,word_length=3):
    filesToOpen=[]
    documentID = 0
    multiple_punctuation=0
    exclamation_punctuation=0
    question_punctuation=0
    punctuation_docs=[]
    header=[]
    fileLabel = ''
    columns_to_be_plotted_xAxis=[]
    columns_to_be_plotted_yAxis=[]
    chart_title_label=''
    column_xAxis_label=''
    hover_label=''
    word_list=[]

    word_list_temp = []
    word_list_temp3 = []


    fin = open('../lib/wordLists/stopwords.txt', 'r')
    stops = set(fin.read().splitlines())
    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False, configFileName=configFileName)

    Ndocs=str(len(inputDocs))

    if processType != '':
        hideMessage = False
    else:
        hideMessage = True
    if Ndocs == 1:
        hideMessage = False
    else:
        hideMessage = True

    # ngrams already display the started running... No need to duplicate
    if not 'unigrams' in processType:
        startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                               'Started running ' + processType + ' at', True)

    # process separately outside the loop through documents which is carried out inside compute_character_word_ngrams
    if processType == '' or "N-grams" in processType or \
            "hapax" in processType.lower() or "unigrams" in processType.lower():
        if "hapax" in processType.lower():
            ngramsNumber = 1
            frequency = 1  # hapax
        elif "unigrams" in processType.lower():
            ngramsNumber = 1
            frequency = 0
        else:
            ngramsNumber = 3  # TODO ROBY
            frequency = 0  # N-grams
        normalize = False
        excludePunctuation = True
        wordgram = True
        bySentenceID = False
        tempOutputFiles = compute_character_word_ngrams(window, inputFilename, inputDir, outputDir, configFileName,
                                                        ngramsNumber,
                                                        normalize, excludePunctuation,
                                                        wordgram, frequency,
                                                        openOutputFiles, createCharts, chartPackage,
                                                        bySentenceID)
        # Excel charts are generated in compute_character_word_ngrams; return to exit here
        return tempOutputFiles

    #For the user input of K sentences or words to be analyzed
    if 'Repetition: Words' in processType or 'Repetition: Last' in processType:
        if '*' in processType:
            k_str = '4' # when processing all style algorithms, set the k_str not to stop the process
        else:
            k_str = ''
            # do not activate the reminder when processing ALL style options
            head, scriptName = os.path.split(os.path.basename(__file__))
            reminder_status = reminders_util.checkReminder(scriptName,
                                                           reminders_util.title_options_only_CoreNLP_CoNLL_repetition_finder,
                                                           reminders_util.message_only_CoreNLP_CoNLL_repetition_finder)
        if 'Repetition: Last' in processType and k_str == '':
            k_str, useless = GUI_IO_util.enter_value_widget("Enter the number of words, K, to be analyzed (Repetition finder)", 'K',
                                                           1, '', '', '')
        elif 'Repetition: Words' in processType and k_str == '':
            k_str, useless = GUI_IO_util.enter_value_widget("Enter the number of sentences, K, to be analyzed (Repetition finder)", 'K',
                                                           1, '', '', '')
        if k_str=='':
            return
        k = int(k_str)

    for doc in inputDocs:
        head, tail = os.path.split(doc)
        documentID = documentID + 1
        print("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)

        fullText = (open(doc, "r", encoding="utf-8", errors="ignore").read())
        fullText = fullText.replace('\n', ' ')
        from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza
        sentences = sent_tokenize_stanza(stanzaPipeLine(fullText))

        rep_words_first = []
        rep_words_last = []
        word_list_temp = []

        sentenceID = 0  # to store sentence index
        # check each word in sentence for concreteness and write to outputFilename

        # analyze each sentence
        sentence_list = []
        for s in sentences:
            sentenceID = sentenceID + 1
            # print("S" + str(i) +": " + s)
            all_words = []
            found_words = []
            total_words = 0
            num_words_in_s = s.count(" ") + 1

            from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, \
                lemmatize_stanza
            words = word_tokenize_stanza(stanzaPipeLine(s))
            words_with_stop = [word for word in words if word.isalpha()]
            #print(words_with_stop)
            # don't process stopwords
            filtered_words = words
            if processType != '' and not "punctuation" in processType.lower():
                if excludeStopWords:
                    words = excludeStopWords_list(words)
                    filtered_words = [word for word in words if word.isalpha()]  # strip out words with punctuation
            # words = fullText.translate(string.punctuation).split()
            #for wordID, word in enumerate(filtered_words):
            #print(filtered_words)

# SUBJECTIVITY/OBJECTIVITY PER SENTENCE---------------------------------------------------------------------------------------------
            if "Objectivity/subjectivity" in processType:
                # import spaCy_util
                # annotator_available = spaCy_util.check_spaCy_annotator_availability(['Objectivity/subjectivity'], language, silent=False)
                # if not annotator_available:
                #     return
                nlp = spacy.load('en_core_web_sm')
                nlp.add_pipe('spacytextblob')

                header = ["Subjectivity Score", "Sentence ID", "Sentence", "Document ID", "Document"]
                select_col = ['Subjectivity Scores']
                fileLabel = 'Objectivity_subjectivity per sentence'
                fileLabel_byDocID = 'Objecitivity_subjectivity_per_sentence_byDoc'
                columns_to_be_plotted_yAxis = ['Subjectivity Score']
                chart_title_label = 'Frequency of subjectivity scores'
                chart_title_byDocID = 'Frequency of subjectivity scores by Document'
                chart_title_bySentID = 'Frequency of subjectivity scores by Sentence ID'
                column_xAxis_label = 'Subjectivity scores'

                d = nlp(s)
                subjectivity_score = d._.blob.subjectivity

                word_list.append([subjectivity_score, sentenceID, s, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])


    # WORD LENGTH --------------------------------------------------------------------------
            for wordID, word in enumerate(filtered_words):
                if processType=='' or "word length" in processType.lower():
                    header = ['Word', 'Word length (in characters)', 'Word ID (in sentence)', 'Number of words in sentence', 'Sentence ID','Sentence','Document ID','Document']
                    select_col = ['Word length']
                    fileLabel='word_length'
                    fileLabel_byDocID = 'word_length_byDoc'
                    columns_to_be_plotted_yAxis=['Word length'] # bar chart
                    chart_title_label = 'Frequency of Word Lengths (in Characters)'
                    chart_title_byDocID='Frequency of Word Lengths (in Characters) by Document'
                    chart_title_bySentID ='Frequency of Word Lengths (in Characters) by Sentence Index'
                    column_xAxis_label = 'Word length (in characters)'

                    # exclude numbers from list
                    if word and word.isalpha():
                        word_list.append([word, len(word), wordID + 1, len(words), sentenceID, s, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])

    # INITIAL-CAPITAL WORDS --------------------------------------------------------------------------

                if processType=='' or "capital" in processType.lower():
                    header = ['Initial-capital words', 'Word ID (in sentence)', 'Number of words in sentence', 'Sentence ID', 'Sentence', 'Document ID','Document']
                    select_col = ['Initial-capital words']
                    fileLabel='init_cap_words'
                    fileLabel_byDocID = '' # 'capital_words_byDoc'
                    columns_to_be_plotted_yAxis=['Initial-capital words'] # bar chart
                    chart_title_label = 'Frequency of Initial-Capital Words'
                    chart_title_byDocID ='Frequency of Initial-Capital Words by Document'
                    chart_title_bySentID ='Frequency of Initial-Capital Words by Sentence Index'
                    column_xAxis_label = 'Initial-capital words'

                    if word and word and word[0].isupper():
                        word_list.append([word, wordID + 1, len(words), sentenceID, s, documentID,
                                  IO_csv_util.dressFilenameForCSVHyperlink(doc)])
                        # word_list.append([word, wordID + 1, len(words), sentenceID, s, documentID,
                        #           IO_csv_util.dressFilenameForCSVHyperlink(doc)])

    # INITIAL-VOWEL WORDS --------------------------------------------------------------------------

                if processType=='' or "vowel" in processType.lower():
                    header = ['Initial vowel', 'Word ID (in sentence)', 'Number of words in sentence', 'Sentence ID', 'Sentence', 'Document ID', 'Document']
                    select_col = ['Initial-vowel words']
                    fileLabel='vowel_words'
                    fileLabel_byDocID = 'vowel_words_byDoc'
                    columns_to_be_plotted_yAxis=['Initial vowel'] # bar chart
                    chart_title_label = 'Frequency of Initial-Vowel Words'
                    chart_title_byDocID='Frequency of Initial-Vowel Words by Document'
                    chart_title_bySentID = 'Frequency of Initial-Vowel Words by Sentence Index'
                    column_xAxis_label = 'Initial-vowel words'
                    if word and word and word[0].lower() in "aeiou" and word.isalpha():
                        word_list.append([word, wordID + 1, len(words), sentenceID, s, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])
    # PUNCTUATION SYMBOLS --------------------------------------------------------------------------

                if processType == '' or "punctuation" in processType.lower():
                    header = ['Punctuation symbols of pathos (?!)', 'Word ID (in sentence)', 'Number of words in sentence', 'Sentence ID', 'Sentence', 'Document ID','Document']
                    select_col = ['Punctuation symbols of pathos (?!)'] # line chart by sentence index
                    fileLabel = 'punctuation'
                    fileLabel_byDocID = 'punctuation_byDoc'
                    columns_to_be_plotted_yAxis=['Punctuation symbols of pathos (?!)'] # bar chart
                    chart_title_label = 'Frequency of Punctuation Symbols of Pathos (?!)'
                    chart_title_byDocID='Frequency of Punctuation Symbols of Pathos (?!) by Document'
                    chart_title_bySentID='Frequency of Punctuation Symbols of Pathos (?!) by Sentence Index'
                    column_xAxis_label = 'Punctuation symbols of pathos (?!)'
                    if word != '!' and word != '?':
                        continue
                    word_list.append([word, wordID + 1, len(words), sentenceID, s, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])
                    if doc not in punctuation_docs:
                        punctuation_docs.append(doc)
                    if '!' in word and '?' in word:
                        multiple_punctuation=multiple_punctuation+1
                    elif '!' in word:
                        exclamation_punctuation=exclamation_punctuation+1
                    elif '?' in word:
                        question_punctuation=question_punctuation+1

                from collections import Counter
                # REPEATED WORDS FIRST K SENTENCES/LAST K SENTENCES  -------------------------------------------------------------------------------
                if 'Repetition: Words' in processType:
                    for wrdID, wrd in enumerate(filtered_words):

                        header = ["First/Last Sentence", "K Value", "Word", "Word ID", "Sentence ID", "Sentence",
                                  "Document ID", "Document"]
                        select_col = ['Word']
                        fileLabel = str(k) + '_K_Sentences'
                        fileLabel_byDocID = 'Rep_Words_First_Last_' +str(k) + '_K_Sentences_byDoc'
                        columns_to_be_plotted_yAxis = ['Word']
                        chart_title_label = f'Frequency of repeated words in first and last K ({k}) sentences'
                        chart_title_byDocID = f'Frequency of repeated words in first and last K ({k}) sentences by Document'
                        chart_title_bySentID = f'Frequency of repeated words in first and last K ({k}) sentences by Sentence ID'
                        column_xAxis_label = 'Words'

                        if sentenceID <= k:
                            word_list_temp.append(["First", k, wrd, wrdID + 1, sentenceID, s, documentID,
                                                   IO_csv_util.dressFilenameForCSVHyperlink(doc)])
                            rep_words_first.append(wrd)

                        elif sentenceID > len(sentences) - k:
                            word_list_temp.append(["Last", k, wrd, wrdID + 1, sentenceID, s, documentID,
                                                   IO_csv_util.dressFilenameForCSVHyperlink(doc)])
                            rep_words_last.append(wrd)
                    # print(rep_words_first)
                    # print(rep_words_last)

                if "Repetition: Words" in processType:
                    word_list.extend([sublist for sublist in word_list_temp if
                                      sublist[2] in rep_words_first and sublist[2] in rep_words_last])

                # REPEATED WORDS END OF SENTENCE/BEGINNING NEXT SENTENCE  --------------------------------------------------------------------------
                if 'Repetition: Last' in processType:
                    for wrdID, wrd in enumerate(words_with_stop):
                        # print(wordID)
                        # print(word)
                        # mb.showwarning("Naman","Naman, this for you!")

                        header = ["First/Last Sentence", "K Value", "Word", "Word ID", "Sentence ID", "Sentence",
                                  "Document ID", "Document"]
                        select_col = ['Word']
                        # fileLabel = 'Last K words of a sentence and first K words of next sentence'
                        fileLabel = str(k) + '_K words'
                        fileLabel_byDocID = 'Last/First_'+str(k) + '_k_words_byDoc'
                        columns_to_be_plotted_yAxis = ['Word']
                        chart_title_label = 'Frequency of Last K ('+str(k) +') words of a sentence and first K words of next sentence'
                        chart_title_byDocID = 'Frequency of Last K ('+str(k) +') words of a sentence and first K words of next sentence by Document'
                        chart_title_bySentID = 'Frequency of Last K ('+str(k) +') words of a sentence and first K words of next sentence by Sentence Index'
                        column_xAxis_label = 'Words'
                        if sentenceID == 1:
                            if wrdID + 1 > len(words_with_stop) - k:
                                word_list.append(["Last", k, wrd, wrdID + 1, sentenceID, s, documentID,
                                                  IO_csv_util.dressFilenameForCSVHyperlink(doc)])

                        else:
                            if wrdID + 1 <= k:
                                word_list.append(["First", k, wrd, wrdID + 1, sentenceID, s, documentID,
                                                  IO_csv_util.dressFilenameForCSVHyperlink(doc)])
                            elif wrdID + 1 > len(words_with_stop) - k:
                                word_list.append(["Last", k, wrd, wrdID + 1, sentenceID, s, documentID,
                                                  IO_csv_util.dressFilenameForCSVHyperlink(doc)])

    # N-GRAMS & HAPAX --------------------------------------------------------------------------
        # hapax and ngrams are processed above outside the for doc loop
        #    a for doc loop is already carried out in the function compute_character_word_ngrams

    if len(word_list)==0:
        IO_user_interface_util.timed_alert(GUI_util.window,2000,"Empty file",
                                               "The " + processType + " algorithm has not generated any output.")
        return filesToOpen

    word_list.insert(0, header)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', fileLabel)
    IO_error=IO_csv_util.list_to_csv(window, word_list, outputFilename)
    if not IO_error:
        filesToOpen.append(outputFilename)

    outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                columns_to_be_plotted_xAxis=[],
                                                columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
                                                chart_title=chart_title_label,
                                                count_var=1, hover_label=[],
                                                outputFileNameType='',  # 'line_bar',
                                                column_xAxis_label=column_xAxis_label,
                                                groupByList=['Document'],
                                                plotList=['Frequency'],
                                                chart_title_label=column_xAxis_label)

    if outputFiles!=None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    # ngrams already display the started running... No need to duplicate
    if not 'unigrams' in processType:
        IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                                               'Finished running ' + processType + ' at', True, '', True, startTime)

    return filesToOpen

# n is n most common words
# text is the plain text read in from a file
def n_most_common_words(n,text):
    cleaned_words, common_words = [], []
    for word in text.split():
        fin = open('../lib/wordLists/stopwords.txt', 'r')
        stop_words = set(fin.read().splitlines())
        if word not in stop_words and '\'' not in word and '\"' not in word:
            cleaned_words.append(word)
    # print(cleaned_words)
    counts = Counter(cleaned_words)
    #print(cleaned_words)
    #print(str(n), ' most common words in the repeated phrases:')
    for key, value in counts.most_common(n):
        common_words.append([key, value])
        #print(key, value)
    return(common_words)

def convert_txt_file(window,inputFilename,inputDir,outputDir,openOutputFiles,excludeStopWords=True,lemmatizeWords=True):
    filesToOpen=[]
    outputFilename=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.txt', 'corpus', 'lemma_stw')
    filesToOpen.append(outputFilename)

    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False, configFileName=configFileName)

    Ndocs=str(len(inputDocs))

    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running txt conversion (lemmatization & stopwords) at',
                                                 True, '', True, '', True)

    with open(outputFilename, 'w', encoding='utf-8', errors='ignore', newline='') as outfile:
        #print("Number of corpus text documents: ",Ndocs)
        #currentLine.append([Ndocs])
        documentID=0
        for doc in inputDocs:
            head, tail = os.path.split(doc)
            documentID=documentID+1
            # currentLine.append([documentID])
            print("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)
            fullText = (open(doc, "r", encoding="utf-8", errors="ignore").read())

            Nsentences=str(textstat.sentence_count(fullText))
            #print('TOTAL number of sentences: ',Nsentences)

            Nwords=str(textstat.lexicon_count(fullText, removepunct=True))
            #print('TOTAL number of words: ',Nwords)

            Nsyllables =textstat.syllable_count(fullText, lang='en_US')
            #print('TOTAL number of Syllables: ',Nsyllables)

            # words = fullText.split()
            # words = nltk.word_tokenize(fullText)
            from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, \
                lemmatize_stanza
            words = word_tokenize_stanza(stanzaPipeLine(fullText))

            if excludeStopWords:
                words = excludeStopWords_list(words)

            if lemmatizeWords:
                # lemmatizer = WordNetLemmatizer()
                # text_vocab = set(lemmatizer.lemmatize(w.lower()) for w in fullText.split(" ") if w.isalpha())
                # words = set(lemmatizing(w.lower()) for w in words if w.isalpha()) # fullText.split(" ") if w.isalpha())
                from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, \
                    lemmatize_stanza
                text_vocab = set(lemmatize_stanza(stanzaPipeLine(w.lower())) for w in fullText.split(" ") if w.isalpha())
                words = set(lemmatizing(w.lower()) for w in words if w.isalpha()) # fullText.split(" ") if w.isalpha())


# https://pypi.org/project/textstat/
def compute_sentence_text_readability(window, inputFilename, inputDir, outputDir, configFileName, openOutputFiles, createCharts, chartPackage):
    filesToOpen = []
    documentID = 0

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='readability',
                                                              silent=True)
    if outputDir == '':
        return

    files = IO_files_util.getFileList(inputFilename, inputDir, '.txt', silent=False, configFileName=configFileName)

    nFile = len(files)
    if nFile == 0:
        return

    startTime = IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                                   'Started running Text Readability at',
                                                   True, '\nYou can follow Text Readability in command line.')

    if nFile > 1:
        outputFilenameTxt = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.txt', 'READ',
                                                                    'stats')
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'READ',
                                                                    'stats')
    else:
        outputFilenameTxt = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.txt', 'READ',
                                                                    'stats')
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'READ',
                                                                    'stats')
    filesToOpen.append(outputFilenameTxt)
    filesToOpen.append(outputFilename)

    fieldnames = ['Flesch Reading Ease formula',
                  'Flesch-Kincaid Grade Level',
                  'Fog Scale (Gunning FOG Formula)',
                  'SMOG (Simple Measure of Gobbledygook) Index',
                  'Automated Readability Index',
                  'Coleman-Liau Index',
                  'Linsear Write Formula',
                  'Dale-Chall Readability Score',
                  'Overall readability consensus',
                  'Grade level',
                  'Sentence ID', 'Sentence',
                  'Document ID', 'Document']

    with open(outputFilename, 'w', encoding='utf-8', errors='ignore', newline='') as outputCsvFile:
        writer = csv.DictWriter(outputCsvFile, fieldnames=fieldnames)
        writer.writeheader()

        # already shown in NLP.py
        # IO_util.timed_alert(GUI_util.window,2000,'Analysis start','Started running NLTK unusual words at',True,'You can follow NLTK unusual words in command line.')

        # open txt output file
        outputTxtFile = open(outputFilenameTxt, "w")
        documentID = 0
        for file in files:
            # read txt file
            text = (open(file, "r", encoding="utf-8", errors="ignore").read())

            documentID = documentID + 1
            head, tail = os.path.split(file)
            print("Processing file " + str(documentID) + "/" + str(nFile) + ' ' + tail)

            # write text files ____________________________________________

            outputTxtFile.write("TEXT READABILITY SCORES (by Python library textstat)" + "\n\n")
            outputTxtFile.write(file + "\n\n")

            # This legenda is now available as a TIPS file
            # outputTxtFile.write ("LEGENDA -----------------------------------------------------------------------------------------------------------------------------------------------\n\n")
            # outputTxtFile.write ("Text readability measures the understandability of a text.\n")
            # outputTxtFile.write ("The different measures of readability map on the U.S grade level (1 through 12) needed to comprehend a text.\n\n  12 readability score requires HIGHSCHOOL education;\n  16 readability score requires COLLEGE education;\n  18 readability score requires MASTER education;\n  24 readability score requires DOCTORAL education;\n  >24 readability score requires POSTDOC education.\n\n")

            # outputTxtFile.write ("Automated Readability Index (ARI) outputs a number that approximates the grade level needed to comprehend the text. For example if the ARI is 6.5, then the grade level to comprehend the text is 6th to 7th grade.\n\n")
            # outputTxtFile.write ("Coleman-Liau Index, Linsear Write Formula, Flesch-Kincaid Grade, SMOG index, Fog Scale (Gunning FOG Formula) are grade formula in that a score of 9.3 means that a ninth grader would be able to read the document.\n\n")

            # outputTxtFile.write ("The Flesch Reading Ease formula has the following range of values (the maximum score is 121.22; there is no limit on how low the score can be, with a negative score being valid):\n")
            # outputTxtFile.write ("  0-30 College\n")
            # outputTxtFile.write ("  50-60 High School\n")
            # outputTxtFile.write ("  90-100 Fourth Grade\n\n")

            # outputTxtFile.write ("The Dale-Chall index has the following range of values (different from other tests, since it uses a lookup table of the most commonly used 3000 English words and returns the grade level using the New Dale-Chall Formula):\n")
            # outputTxtFile.write ("  4.9 or lower    easily understood by an average 4th-grade student or lower\n")
            # outputTxtFile.write ("  5.0–5.9 easily understood by an average 5th or 6th-grade student\n")
            # outputTxtFile.write ("  6.0–6.9 easily understood by an average 7th or 8th-grade student\n")
            # outputTxtFile.write ("  7.0–7.9 easily understood by an average 9th or 10th-grade student\n")
            # outputTxtFile.write ("  8.0–8.9 easily understood by an average 11th or 12th-grade student\n")
            # outputTxtFile.write ("  9.0–9.9 easily understood by an average 13th to 15th-grade (college) student\n\n")

            outputTxtFile.write(
                "RESULTS -----------------------------------------------------------------------------------------------------------------------------------------------\n\n")
            # Syllable count
            str_value = "Syllable count " + str(textstat.syllable_count(text, lang='en_US'))
            outputTxtFile.write(str_value + "\n")
            # print("\n\nSyllable count ",textstat.syllable_count(text, lang='en_US'))
            # Lexicon count
            str_value = "Lexicon count " + str(textstat.lexicon_count(text, removepunct=True))
            outputTxtFile.write(str_value + "\n")
            # print("Lexicon count ",textstat.lexicon_count(text, removepunct=True))
            # Sentence count
            str_value = "Sentence count " + str(textstat.sentence_count(text))
            outputTxtFile.write(str_value + "\n\n")
            # print("Sentence count ",textstat.sentence_count(text))

            # The Flesch Reading Ease formula
            str_value = "Flesch Reading Ease formula " + str(textstat.flesch_reading_ease(text))
            outputTxtFile.write(str_value + "\n")
            # print("Flesch Reading Ease formula",textstat.flesch_reading_ease(text))
            # The Flesch-Kincaid Grade Level
            str_value = "Flesch-Kincaid Grade Level " + str(textstat.flesch_kincaid_grade(text))
            outputTxtFile.write(str_value + "\n")
            # print("Flesch-Kincaid Grade Level",textstat.flesch_kincaid_grade(text))
            # The Fog Scale (Gunning FOG Formula)
            str_value = "Fog Scale (Gunning FOG Formula) " + str(textstat.gunning_fog(text))
            outputTxtFile.write(str_value + "\n")
            # print("Fog Scale (Gunning FOG Formula)",textstat.gunning_fog(text))
            # The SMOG Index
            str_value = "SMOG (Simple Measure of Gobbledygook) Index " + str(textstat.smog_index(text))
            outputTxtFile.write(str_value + "\n")
            # print("SMOG (Simple Measure of Gobbledygook) Index",textstat.smog_index(text))
            # Automated Readability Index
            str_value = "Automated Readability Index " + str(textstat.automated_readability_index(text))
            outputTxtFile.write(str_value + "\n")
            # print("Automated Readability Index",textstat.automated_readability_index(text))
            # The Coleman-Liau Index
            str_value = "Coleman-Liau Index " + str(textstat.coleman_liau_index(text))
            outputTxtFile.write(str_value + "\n")
            # print("Coleman-Liau Index",textstat.coleman_liau_index(text))
            # Linsear Write Formula
            str_value = "Linsear Write Formula " + str(textstat.linsear_write_formula(text))
            outputTxtFile.write(str_value + "\n")
            # print("Linsear Write Formula",textstat.linsear_write_formula(text))
            # Dale-Chall Readability Score
            str_value = "Dale-Chall Readability Score " + str(textstat.dale_chall_readability_score(text))
            outputTxtFile.write(str_value + "\n")
            # print("Dale-Chall Readability Score",textstat.dale_chall_readability_score(text))
            # Readability Consensus based upon all the above tests
            str_value = "\n\nReadability Consensus Level based upon all the above tests: " + str(
                textstat.text_standard(text, float_output=False) + '\n\n')
            outputTxtFile.write(str_value + "\n")
            # print("\n\nReadability Consensus based upon all the above tests: ",textstat.text_standard(text, float_output=False))

            # write csv files ____________________________________________

            # split into sentences
            # sentences = nltk.sent_tokenize(text)
            from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, \
                lemmatize_stanza
            sentences = sentences = sent_tokenize_stanza(stanzaPipeLine(text))
            # analyze each sentence in text for readability
            sentenceID = 0  # to store sentence index
            for sent in sentences:
                sentenceID = sentenceID + 1
                # Flesch Reading Ease formula
                str1 = str(textstat.flesch_reading_ease(sent))
                # The Flesch-Kincaid Grade Level
                str2 = str(textstat.flesch_kincaid_grade(sent))
                # Th3 Fog Scale (Gunning FOG Formula)
                str3 = str(textstat.gunning_fog(sent))
                # The SMOG Index
                str4 = str(textstat.smog_index(sent))
                # Automated Readability Index
                str5 = str(textstat.automated_readability_index(sent))
                # The Coleman-Liau Index
                str6 = str(textstat.coleman_liau_index(sent))
                # Linsear Write Formula
                str7 = str(textstat.linsear_write_formula(sent))
                # Dale-Chall Readability Score
                str8 = str(textstat.dale_chall_readability_score(sent))
                # Overall summary measure
                str9 = str(textstat.text_standard(sent, float_output=False))
                if str9 == "-1th and 0th grade":
                    sortOrder = 0
                elif str9 == "0th and 1st grade":
                    sortOrder = 1
                elif str9 == "1st and 2nd grade":
                    sortOrder = 2
                elif str9 == "2nd and 3rd grade":
                    sortOrder = 3
                elif str9 == "3rd and 4th grade":
                    sortOrder = 4
                elif str9 == "4th and 5th grade":
                    sortOrder = 5
                elif str9 == "5th and 6th grade":
                    sortOrder = 6
                elif str9 == "6th and 7th grade":
                    sortOrder = 7
                elif str9 == "7th and 8th grade":
                    sortOrder = 8
                elif str9 == "8th and 9th grade":
                    sortOrder = 9
                elif str9 == "9th and 10th grade":
                    sortOrder = 10
                elif str9 == "10th and 11th grade":
                    sortOrder = 11
                elif str9 == "11th and 12th grade":
                    sortOrder = 12
                elif str9 == "12th and 13th grade":
                    sortOrder = 13
                elif str9 == "13th and 14th grade":
                    sortOrder = 14
                elif str9 == "14th and 15th grade":
                    sortOrder = 15
                elif str9 == "15th and 16th grade":
                    sortOrder = 16
                elif str9 == "16th and 17th grade":
                    sortOrder = 17
                elif str9 == "17th and 18th grade":
                    sortOrder = 18
                elif str9 == "18th and 19th grade":
                    sortOrder = 19
                elif str9 == "19th and 20th grade":
                    sortOrder = 20
                elif str9 == "20th and 21st grade":
                    sortOrder = 21
                elif str9 == "21st and 22nd grade":
                    sortOrder = 22
                elif str9 == "22nd and 23rd grade":
                    sortOrder = 23
                elif str9 == "23rd and 24th grade":
                    sortOrder = 24
                else:
                    str9 = 'Unclassified'
                    sortOrder = 25
                # rowValue=[[documentID,file,sentenceID,sent,str1,str2,str3,str4,str5,str6,str7,str8,str9,sortOrder]]
                rowValue = [
                    [str1, str2, str3, str4, str5, str6, str7, str8, str9, sortOrder, sentenceID, sent, documentID, IO_csv_util.dressFilenameForCSVHyperlink(file)]]
                writer = csv.writer(outputCsvFile)
                writer.writerows(rowValue)
        # at least 12th grade level HIGH-SCHOOL EDUCATION
        # at least 16th grade level UNDERGRADUATE COLLEGE EDUCATION
        # at least 18th grade level MA EDUCATION
        # at least 24th grade level PhD EDUCATION
        # > 24th grade level PostDoc EDUCATION

        # TODO YI not sure what to pass to the sort function;
        # IO filenames should be computed here
        # outputFilename1=IO_util.generate_output_file_name(inputFilename,outputDir,'.csv','READ','stats1')
        # IO_util.sort_csvFile_by_columns(outputFilename, outputFilename, ['Document ID','Sort order'])
        outputTxtFile.close()
        outputCsvFile.close()
        result = True

        # readability
        if createCharts == True:
            result = True
            # if nFile>10:
            #     result = mb.askyesno("Excel charts","You have " + str(nFile) + " files for which to compute Excel charts for each file.\n\nTHIS WILL TAKE A LONG TIME TO PRODUCE.\n\nAre you sure you want to do that?")
            if result == True:

                # overall qualitative grade level (e.g., 4th)
                hover_label = []
                outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                                   outputDir,
                                                                   columns_to_be_plotted_xAxis=[],
                                                                   columns_to_be_plotted_yAxis=['Overall readability consensus'],
                                                                   chart_title='Text Readability\nFrequencies of Overall Readability Consensus',
                                                                   count_var=1, hover_label=[],
                                                                   outputFileNameType='cons',  # 'READ_bar',
                                                                   column_xAxis_label='Consensus readability level',
                                                                   groupByList=[],
                                                                   plotList=[],
                                                                   chart_title_label='')
                if outputFiles!=None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)

                # 0 (Flesch Reading Ease) has a different scale and 3 (SMOG) is often 0
                #	do NOT plot on the same chart these two measures
                #	plot all other 6 measures
                columns_to_be_plotted_yAxis=['Flesch-Kincaid Grade Level','Fog Scale (Gunning FOG Formula)','Automated Readability Index','Coleman-Liau Index','Linsear Write Formula','Dale-Chall Readability Score']
                # multiple lines with hover-over effects the sample line chart produces wrong results
                # hover_label = ['Sentence', 'Sentence', 'Sentence', 'Sentence', 'Sentence', 'Sentence']
                hover_label = []

                outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                                   outputDir,
                                                                   columns_to_be_plotted_xAxis=[],
                                                                   columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
                                                                   chart_title='Text Readability\nFrequencies of 6 Readability Measures',
                                                                   count_var=0, hover_label=[],
                                                                   outputFileNameType='',  # 'READ_bar',
                                                                   column_xAxis_label='Readability scores',
                                                                   groupByList=[],
                                                                   plotList=[],
                                                                   chart_title_label='')
                if outputFiles!=None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)

                # overall numeric grade level
                hover_label = []
                outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                                   outputDir,
                                                                   columns_to_be_plotted_xAxis=[],
                                                                   columns_to_be_plotted_yAxis=['Grade level'],
                                                                   chart_title='Text Readability\nFrequencies of Overall Grade Level',
                                                                   count_var=0, hover_label=[],
                                                                   outputFileNameType='grade',  # 'READ_bar',
                                                                   column_xAxis_label='Grade level',
                                                                   groupByList=['Document'],
                                                                   plotList=['Grade level'],
                                                                   chart_title_label='Readability Grade Level')
                if outputFiles!=None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running Text Readability at',
                                       True, '', True, startTime)

    if len(inputDir) != 0:
        mb.showwarning(title='Warning',
                       message='The output filenames generated by Textstat readability contain the name of the directory processed in input, rather than the name of any individual file in the directory.\n\nBoth txt & csv files include all ' + str(
                           nFile) + ' files in the input directory processed by Textstat.')
    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(window, openOutputFiles, filesToOpen, outputDir)


# written by Siyan Pu October 2021
# edited by Roberto Franzosi October 2021
def sentence_structure_tree(inputFilename, outputDir):
    if inputFilename == '':
        sentences = GUI_IO_util.enter_value_widget(
            'Enter sentence                                                                               ', 'Enter', 1)
        sent = [sentences[0]]
        if len(sent) == 0:
            return
        else:
            sentences = sent
        maxNum = 1
    else:
        # split into sentences
        text = (open(inputFilename, "r", encoding="utf-8", errors='ignore').read())
        sentences = nltk.sent_tokenize(text)
        maxNum = GUI_IO_util.enter_value_widget('Enter number of sentences to be visualized', 'Enter', 1)
        maxNum = str(maxNum[0])
        if maxNum == '':
            return
        maxNum = int(maxNum)
        if maxNum >= 10:
            result = mb.askyesno('Warning',
                                 "The number of sentences entered is quite large. The tree graph algorithm will produce a png file for every sentence.\n\nAre you sure you want to continue?")
            if result == False:  # yes no False
                return

    sentenceID = 0  # to store sentence index

    spacy_nlp = spacy.load("en_core_web_sm")

    for sent in sentences:
        sentenceID = sentenceID + 1
        if sentenceID == maxNum + 1:
            return

        doc = spacy_nlp(sent)

        def token_format(token):
            return "_".join([token.orth_, token.tag_, token.dep_])

        def to_nltk_tree(node):
            if node.n_lefts + node.n_rights > 0:
                return Tree(token_format(node),
                            [to_nltk_tree(child)
                             for child in node.children]
                            )
            else:
                return token_format(node)

        tree = [to_nltk_tree(sent.root) for sent in doc.sents]

        cf = TreeView(tree[0])._cframe

        if inputFilename == '':
            cf.print_to_file(outputDir + 'NLP_sentence_tree.ps')
        else:
            cf.print_to_file(outputDir + '/' + os.path.basename(inputFilename) + '_' + str(sentenceID) + '_tree.ps')

# written by Mino Cha March/April 2022
def compute_sentence_complexity(window, inputFilename, inputDir, outputDir, configFileName, openOutputFiles, createCharts, chartPackage):
    ## list for csv file
    columns=[]
    documentID = []
    document = []
    documentName = []

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='complexity',
                                                              silent=True)
    if outputDir == '':
        return

    all_input_docs = {}
    dId = 0

    filesToOpen = []

    startTime = IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                                   'Started running Sentence Complexity at', True)
    if len(inputFilename) > 0:
        numFiles = 1
        doc = inputFilename
        if doc.endswith('.txt'):
            with open(doc, 'r', encoding='utf-8', errors='ignore') as file:
                dId += 1
                head, tail = os.path.split(doc)
                print("Processing file " + str(dId) + '/' + str(numFiles) + tail)
                text = file.read()
                documentID.append(dId)
                document.append(IO_csv_util.dressFilenameForCSVHyperlink(os.path.join(inputDir, doc)))
                all_input_docs[dId] = text
    else:
        # numFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
        # if numFiles == 0:
        #     mb.showerror(title='Number of files error',
        #                  message='The selected input directory does NOT contain any file of txt type.\n\nPlease, select a different directory and try again.')
        #     return

        inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False,
                                                  configFileName=configFileName)
        numFiles = len(inputDocs)
        if numFiles == 0:
            return

        for doc in inputDocs:
            if doc.endswith('.txt'):
                head, tail = os.path.split(doc)
                with open(os.path.join(inputDir, doc), 'r', encoding='utf-8', errors='ignore') as file:
                    dId += 1
                    print("Importing filename " + str(dId) + '/' + str(numFiles) + ' ' + tail)
                    text = file.read()
                    documentID.append(dId)
                    document.append(IO_csv_util.dressFilenameForCSVHyperlink(os.path.join(inputDir, doc)))
                    all_input_docs[dId] = text
    document_df = pd.DataFrame({'Document ID': documentID, 'Document': document})
    document_df = document_df.astype('str')

    columns = ['Sentence length (No. of words)', 'Yngve score', 'Yngve sum', 'Frazier score', 'Frazier sum',
               'Sentence ID', 'Sentence', 'Document ID', 'Document']
    try:
        nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,constituency',use_gpu=False)
    except:
        import subprocess
        import sys
        # subprocess.check_call([sys.executable, "-m", "pip", "install", "git+https://github.com/stanfordnlp/stanza.git@dev"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "stanza==1.4.0"])
        # import stanza
        nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,constituency',use_gpu=False)
    op = pd.DataFrame(columns=columns)
    for idx, txt in enumerate(all_input_docs.items()):
        doc = nlp(txt[1])
        tail = os.path.split(IO_csv_util.undressFilenameForCSVHyperlink(document[idx]))[1]
        print("Processing file " + str(idx+1) + '/' + str(numFiles) + ' ' + tail)
        for i, sentence in enumerate(doc.sentences):
            sent = str(sentence.constituency)
            root1 = tree.make_tree(sent)
            root2 = tree.make_tree(sent)
            leaves_list = tree.getLeavesAsList(root1)
            # print(i)
            # print(sentence.text)
            sentence_length = len(sentence.words)
            # print(sentence_length)

            newRoot1 = Node.Node(root1)
            newRoot2 = Node.Node(root2)
            newRoot1.calY()
            newRoot2.calF()
            leaf = len(leaves_list)

            words = str(sentence).split(" ")
            size = len(words) - 1

            ySum = newRoot1.sumY()
            yAvg = round(ySum / leaf, 2)
            # print(f"Yngve: {yAvg}, {ySum}")

            fSum = newRoot2.sumF()
            fAvg = round(fSum / leaf, 2)
            # print(f"Frazier: {fAvg}, {fSum}\n")

            # new ordering
            # op = op.append({
            #     'Sentence length (No. of words)': sentence_length,
            #     'Yngve score': yAvg,
            #     'Yngve sum': ySum,
            #     'Frazier score': fAvg,
            #     'Frazier sum': fSum,
            #     'Sentence ID': i + 1,
            #     'Sentence': sentence.text,
            #     'Document ID': idx + 1,
            #     'Document': document[idx],
            # },ignore_index=True)
            # op = op.append({ deprecated
            # https://stackoverflow.com/questions/75956209/dataframe-object-has-no-attribute-append
            # df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            op = pd.concat([op, pd.DataFrame([{
                'Sentence length (No. of words)': sentence_length,
                'Yngve score': yAvg,
                'Yngve sum': ySum,
                'Frazier score': fAvg,
                'Frazier sum': fSum,
                'Sentence ID': i + 1,
                'Sentence': sentence.text,
                'Document ID': idx + 1,
                'Document': document[idx]}])],
            ignore_index=True)
    # not necessary sorted already
    # op.sort_values(by=['Document ID', 'Sentence ID'], ascending=True, inplace=True)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                             'SentenceComplexity')
    IO_csv_util.df_to_csv(window, op, outputFilename, columns, False, 'utf-8')
    filesToOpen.append(outputFilename)
    # TODO we need an X-axis to plot these scores against
    # , 'Frazier score'
    outputFiles = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                       columns_to_be_plotted_xAxis=[],
                                                       columns_to_be_plotted_yAxis=['Yngve score'],
                                                       chart_title='Frequency Distribution of Complexity Scores\n(Yngve & Frazier)',
                                                       count_var=0, # 1 for alphabetic fields that need to be coounted;  1 for numeric fields (e.g., frequencies, scorers)
                                                       hover_label=[],
                                                       outputFileNameType='', #'' #'complexity_bar',
                                                       column_xAxis_label='Complexity scores',
                                                       column_yAxis_label='Scores',
                                                       groupByList=['Document'],
                                                       plotList=['Yngve score','Frazier score'],
                                                       chart_title_label='Complexity Scores')
    if outputFiles!=None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                                       'Finished running Sentence Complexity at', True, '', True, startTime)
    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(window, openOutputFiles, filesToOpen, outputDir)
