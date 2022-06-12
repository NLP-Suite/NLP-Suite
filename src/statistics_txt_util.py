# Written by Roberto Franzosi November 2019 
# Edited by Josh Karol
import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"statistics_txt_util",['nltk','csv','tkinter','os','string','collections','re','textstat','itertools'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
import collections
import re
from collections import Counter
import string
from nltk.stem.porter import PorterStemmer

import statistics_csv_util
import IO_user_interface_util

import csv
import nltk
# from nltk import tokenize
# from nltk import word_tokenize
from stanza_functions import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza

import ast
import textstat
import subprocess
import spacy
from nltk.tree import Tree
from nltk.draw import TreeView
from PIL import Image

# Sentence Complexity
import tree
import node_sentence_complexity as Node
import stanza

# from gensim.utils import lemmatize
from itertools import groupby
import pandas as pd
import ast
import textstat
import subprocess
import spacy
from nltk.tree import Tree
from nltk.draw import TreeView
from PIL import Image

#whether stopwordst were already downloaded can be tested, see stackoverflow
#   https://stackoverflow.com/questions/23704510/how-do-i-test-whether-an-nltk-resource-is-already-installed-on-the-machine-runni
#   see also caveats

# check stopwords
# IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/stopwords','stopwords')
# check punkt
# IO_libraries_util.import_nltk_resource(GUI_util.window,'tokenizers/punkt','punkt')

from nltk.corpus import stopwords
# from nltk.tokenize import sent_tokenize, word_tokenize
# from nltk.stem import WordNetLemmatizer
# from nltk.util import ngrams
from nltk.corpus import wordnet
from stanza_functions import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza
# from gensim.utils import lemmatize
from itertools import groupby
import textstat

import charts_util
import charts_util
import IO_files_util
import IO_csv_util
import reminders_util
import TIPS_util

#https://github.com/nltk/nltk/wiki/Frequently-Asked-Questions-(Stackoverflow-Edition)
#to extract bigrams, 3-grams, ...
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


def compute_line_length(window, config_filename, inputFilename, inputDir, outputDir,openOutputFiles,createCharts, chartPackage):
    filesToOpen=[]
    outputFilename=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'line_length')
    filesToOpen.append(outputFilename)
    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    Ndocs = str(len(inputDocs))
    if Ndocs==0:
        return
    reminders_util.checkReminder(config_filename, reminders_util.title_options_line_length,
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
    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running line length analysis at',
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
                    words = word_tokenize_stanza(stanzaPipeLine(line))
                    # print("Line {}: Length (in characters) {} Length (in words) {}".format(lineID, len(line), len(words)))
                    currentLine = [
                        [len(line), len(words),lineID,line.strip(), documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)]]
                    writer.writerows(currentLine)
                    line = file.readline()
    csvfile.close()

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running line length analysis at', True, '', True, startTime, True)

    # produce all charts
    chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                              columns_to_be_plotted_bar=[[1, 1]],
                                              columns_to_be_plotted_bySent=[[2, 1]],
                                              columns_to_be_plotted_byDoc=[[1, 5]],
                                              chartTitle='Frequency Distribution of Line Length',
                                              count_var=1, hover_label=[],
                                              outputFileNameType='line_bar', column_xAxis_label='Line length',
                                              groupByList=['Document ID','Document'], plotList=['Line length (in words)'], chart_label='Lines')

    if chart_outputFilename != None:
        filesToOpen.extend(chart_outputFilename)

    return filesToOpen

# https://www.nltk.org/book/ch02.html
# For the Gutenberg Corpus they provide the programming code to do it. section 1.9   Loading your own Corpus.
# see also https://people.duke.edu/~ccc14/sta-663/TextProcessingSolutions.html
def compute_corpus_statistics(window,inputFilename,inputDir,outputDir,openOutputFiles,createCharts,chartPackage,excludeStopWords=True,lemmatizeWords=True):
    filesToOpen=[]
    outputFilename=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'corpus_stats', '')
    filesToOpen.append(outputFilename)
    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')

    # read_line(inputFilename, inputDir, outputDir)
    # return

    Ndocs=str(len(inputDocs))
    fieldnames=['Number of documents in corpus',
        'Document ID',
        'Document',
        'Number of Sentences in Document',
        'Number of Words in Document',
        'Number of Syllables in Document',
        'Word1','Frequency1',
        'Word2','Frequency2',
        'Word3','Frequency3',
        'Word4','Frequency4',
        'Word5','Frequency5',
        'Word6','Frequency6',
        'Word7','Frequency7',
        'Word8','Frequency8',
        'Word9','Frequency9',
        'Word10','Frequency10',
        'Word11','Frequency11',
        'Word12','Frequency12',
        'Word13','Frequency13',
        'Word14','Frequency14',
        'Word15','Frequency15',
        'Word16','Frequency16',
        'Word17','Frequency17',
        'Word18','Frequency18',
        'Word19','Frequency19',
        'Word20','Frequency20']
    if IO_csv_util.openCSVOutputFile(outputFilename):
        return

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running document(s) statistics at',
                                                 True, '', True, '', False)

    with open(outputFilename, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        #print("Number of corpus text documents: ",Ndocs)
        #currentLine.append([Ndocs])
        documentID=0
        for doc in inputDocs:
            head, tail = os.path.split(doc)
            documentID=documentID+1
            # currentLine.append([documentID])
            print("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)
            #currentLine.append([doc])
            fullText = (open(doc, "r", encoding="utf-8", errors="ignore").read())

            Nsentences=str(textstat.sentence_count(fullText))
            #print('TOTAL number of sentences: ',Nsentences)

            Nwords=str(textstat.lexicon_count(fullText, removepunct=True))
            #print('TOTAL number of words: ',Nwords)

            Nsyllables =textstat.syllable_count(fullText, lang='en_US')
            #print('TOTAL number of Syllables: ',Nsyllables)

            # words = fullText.split()
            # words = nltk.word_tokenize(fullText)
            words = word_tokenize_stanza(stanzaPipeLine(fullText))

            if excludeStopWords:
                words = excludeStopWords_list(words)

            if lemmatizeWords:
                # lemmatizer = WordNetLemmatizer()
                text_vocab = []
                for w in words:
                    if w.isalpha():
                        # text_vocab.append(lemmatizer.lemmatize(w.lower()))
                        text_vocab.append(lemmatize_stanza(stanzaPipeLine(w.lower())))

                words = text_vocab

            word_counts = Counter(words)

            # 20 most frequent words in the document
            #print("\n\nTOP 20 most frequent words  ----------------------------")
            # for item in word_counts.most_common(20):
            #     print(item)
            # currentLine=[[Ndocs,documentID,doc,Nsentences,Nwords,Nsyllables]]
            currentLine=[[Ndocs,documentID,IO_csv_util.dressFilenameForCSVHyperlink(doc),Nsentences,Nwords,Nsyllables]]
            for item in word_counts.most_common(20):
                currentLine[0].append(item[0])  # word
                currentLine[0].append(item[1]) # frequency
            writer = csv.writer(csvfile)
            writer.writerows(currentLine)
        csvfile.close()

        # number of sentences in input
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                           columns_to_be_plotted_bar=[[3, 3]],
                                                           columns_to_be_plotted_bySent=[[]], # sentence not available
                                                           columns_to_be_plotted_byDoc=[[3, 2]],
                                                           chartTitle='Frequency of Sentences',
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='line_bar',
                                                           column_xAxis_label='Line length',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Number of Sentences in Document'], chart_label='Sentences')

        if chart_outputFilename != None:
            filesToOpen.extend(chart_outputFilename)

        # number of words in input
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                           columns_to_be_plotted_bar=[[4, 4]],
                                                           columns_to_be_plotted_bySent=[[]], # sentence not available
                                                           columns_to_be_plotted_byDoc=[[4, 2]],
                                                           chartTitle='Frequency of Words',
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='line_bar',
                                                           column_xAxis_label='Line length',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Number of Words in Document'], chart_label='Words')

        if chart_outputFilename != None:
            filesToOpen.extend(chart_outputFilename)


        # number of syllables in input
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                           columns_to_be_plotted_bar=[[5, 5]],
                                                           columns_to_be_plotted_bySent=[[]], # sentence not available
                                                           columns_to_be_plotted_byDoc=[[5, 2]],
                                                           chartTitle='Frequency of Syllables',
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='syll_bar',
                                                           column_xAxis_label='Syllable length',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Number of Syllables in Document'], chart_label='Syllables')

        if chart_outputFilename != None:
            filesToOpen.extend(chart_outputFilename)

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


def same_sentence_check(jgram):
    sentenceID = jgram[0][1]
    for token in jgram:
        if token[1] != sentenceID:
            return False
        else:
            continue
    return True

#compute_character_word_ngrams works for BOTH character and word ngrams
#https://stackoverflow.com/questions/18658106/quick-implementation-of-character-n-grams-for-word
#ngrams is the type of ngrams wanted 2grams,3grams,4grams,5grams MAX
def compute_character_word_ngrams(window,inputFilename,inputDir,outputDir,ngramsNumber=3, normalize=False, excludePunctuation=False, wordgram=None, frequency = None, openOutputFiles=False, createCharts=True, chartPackage='Excel', bySentenceID=None):
    filesToOpen = []
    container = []

    if inputFilename=='' and inputDir=='':
        mb.showwarning(title='Input error', message='No input file or input directory have been specified.\n\nThe function will exit.\n\nPlease, enter the required input options and try again.')
        return

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'N-Grams start',
                                       'Started running Word/Characters N-Grams at',
                                       True, '', True, '', False)

    files = IO_files_util.getFileList(inputFilename, inputDir, '.txt')
    nFile=len(files)
    if nFile==0:
        return

    if wordgram==None:
        result = mb.askyesno("Word/character N-grams","Would you like to compute\n  WORD n-grams (Yes) or\n  CHARACTER n-grams (No)?")
        if result==True:
            wordgram=1
        else:
            wordgram=0

    if wordgram==1:
        fn="Wd"
        chartTitle="Word "
    else:
        fn="Ch"
        chartTitle="Character "

    if bySentenceID==None:
        result = mb.askyesno("By sentence index","Would you like to compute n-grams by sentence index?")
        if result==True:
            bySentenceID=1
        else:
            bySentenceID=0

    i=0
    for file in files:
        head, tail = os.path.split(file)
        i=i+1
        print("Processing file " + str(i) + "/" + str(nFile) + ' ' + tail)
        ngramsList = get_ngramlist(file, ngramsNumber, wordgram, excludePunctuation, frequency, bySentenceID, isdir=True)
        container.append(ngramsList)

    for documentID, f in enumerate(container):

        for n in f:
            for skip, gram in enumerate(n):
                if skip == 0:
                    gram.insert(-1, 'Document ID')
                    continue
                else:
                    gram.insert(-1, documentID + 1)
    one_gram = []
    for documentID, f in enumerate(container):
        if documentID == 0:
            one_gram += (f[0])
        else:
            one_gram += (f[0][1:])
    generalList = [one_gram]
    if ngramsNumber>1:
        two_gram = []
        for documentID, f in enumerate(container):
            if documentID == 0:
                two_gram += (f[1])
            else:
                two_gram += (f[1][1:])
        generalList = [one_gram, two_gram]
    if ngramsNumber>2:
        three_gram = []
        for documentID, f in enumerate(container):
            if documentID == 0:
                three_gram += (f[2])
            else:
                three_gram += (f[2][1:])
        generalList = [one_gram, two_gram, three_gram]

    # stop at 3; no point going above
    # if ngramsNumber>3:
    #     four_gram = []
    #     for documentID, f in enumerate(container):
    #         if documentID == 0:
    #             four_gram += (f[3])
    #         else:
    #             four_gram += (f[3][1:])
    #     generalList = [one_gram, two_gram, three_gram, four_gram]

    result=True
    # n-grams
    # if createCharts==True:
    #     if nFile>10:
    #         result = mb.askyesno("Excel charts","You have " + str(nFile) + " files for which to compute Excel charts.\n\nTHIS WILL TAKE A LONG TIME.\n\nAre you sure you want to do that?",default='no')
    if frequency == 1:  # hapax
        label = '1-grams_hapax_'
    else:
        label = 'n-grams_'
    for index,ngramsList in enumerate(generalList):
        if nFile>1:
            csv_outputFilename=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', label + str(index + 1) + '_' + fn, 'stats', '', '', '', False, True)
        else:
            csv_outputFilename=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', label + str(index + 1) + '_' + fn, 'stats')

        filesToOpen.append(csv_outputFilename)
        IO_csv_util.list_to_csv(window,ngramsList, csv_outputFilename)

        # n-grams line chart by sentence index
        if createCharts==True and result==True:
            inputFilename=csv_outputFilename
            if bySentenceID == True:
                columns_to_be_plotted=[[2,1]] # sentence ID field comes first [2
                hover_label=[str(index+1)+'-grams']
                chart_outputFilename = statistics_csv_util.compute_csv_column_frequencies(inputFilename=inputFilename,
                                                                                        outputDir=outputDir,
                                                                                        select_col=[],
                                                                                        group_col=['Sentence ID'],
                                                                                        chartTitle=chartTitle + str(index + 1) + '-grams Frequencies by Sentence Index',
                                                                                        series_label = ["Frequencies"])
                if chart_outputFilename != "":
                    filesToOpen.append(chart_outputFilename)
            else:
                columns_to_be_plotted=[[2,1]] # sentence ID field comes first [2
                hover_label=[str(index+1)+'-grams'] # change to sentence

                chart_outputFilename = charts_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                          outputFileLabel='n-grams_'+str(index+1)+'_'+fn,
                                                          chartPackage=chartPackage,
                                                          chart_type_list=["bar"],
                                                          chart_title=chartTitle + str(index+1) + '-grams',
                                                          column_xAxis_label_var='',
                                                          hover_info_column_list=hover_label)
                if chart_outputFilename != "":
                    filesToOpen.append(chart_outputFilename)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
                                       'Finished running Word/Characters N-Grams at', True, '', True, startTime, False )

    if len(inputDir) != 0:
        mb.showwarning(title='Warning', message='The output filename generated by N-grams is the name of the directory processed in input, rather than any individual file in the directory.\n\nThe output csv file includes all ' + str(nFile) + ' files in the input directory processed by N-grams.')

    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

    return filesToOpen

def get_ngramlist(inputFilename,ngramsNumber=4, wordgram=1, excludePunctuation=False, frequency = None, bySentenceID=False, isdir=False):

    def transform(arr):
        t = []
        for jgramlist in arr:
            str = ''
            for word in jgramlist:
                str += (word[0] + ' ')
            t.append([str, jgramlist[0][1],jgramlist[0][2]])
        return t

    container = []
    Sentence_ID = 0
    tokens = []
    char_tokens = []
    text = (open(inputFilename, "r", encoding="utf-8", errors='ignore').read())
    # split into sentences
    # sentences = nltk.sent_tokenize(text)
    sentences = sent_tokenize_stanza(stanzaPipeLine(text))
    for each_sentence in sentences:
        if excludePunctuation:
            each_sentence = each_sentence.translate(str.maketrans('', '', string.punctuation))
        Sentence_ID += 1
        if wordgram==0: # character ngrams
            # char_tokens.append([''.join(nltk.word_tokenize(each_sentence)),Sentence_ID])
            char_tokens.append([''.join(word_tokenize_stanza(stanzaPipeLine(each_sentence))),Sentence_ID])
        else:
            # for tk in nltk.word_tokenize(each_sentence):
            for tk in word_tokenize_stanza(stanzaPipeLine(each_sentence)):
                tokens.append([tk, Sentence_ID, each_sentence])
    # 1:
    if wordgram==1: # word ngrams
        for j in range(1,ngramsNumber+1):
            ngramsList = []
            In=[tokens[i:i+j] for i in range(len(tokens)-(j-1))] # all jgrams
            In = transform([tk for tk in In if same_sentence_check(tk)])
            ctr = collections.Counter(Extract(In))
            for jgrams in In:
                jgrams.insert(1, ctr.get(jgrams[0]))
            # ngram     freq     sentenceID
            for i in In:
                if i[0] not in Extract(ngramsList):
                    if frequency == None:
                        ngramsList.append(i)
                    else: # hapax legomena with frequency=1; exclude items with frequency>1, i.e. i[1] > 1
                        if i[1] == 1:
                            ngramsList.append(i)
            ngramsList=sorted(ngramsList, key = lambda x: x[1])
            if excludePunctuation:
                if isdir:
                    for n in ngramsList:
                        # n.append(inputFilename)
                        n.append(IO_csv_util.dressFilenameForCSVHyperlink(inputFilename))
                    if bySentenceID == True:
                        ngramsList.insert(0, [str(j) + '-grams',  'Frequency', 'Sentence ID', 'Sentence',
                                              'Document'])
                    else:
                        for ngram in ngramsList:
                            ngram.pop(3)
                        ngramsList.insert(0, [str(j) + '-grams',  'Frequency', 'Sentence', 'Document'])
                else:
                    if bySentenceID == True:
                        ngramsList.insert(0, [str(j) + '-grams',  'Frequency', 'Sentence ID', 'Sentence'])
                    else:
                        for ngram in ngramsList:
                            ngram.pop(3)
                        ngramsList.insert(0, [str(j) + '-grams', 'Frequency'])
                container.append(ngramsList)
            else:
                for ng in ngramsList:
                    char_flag = False
                    for char in ng[0]:
                        if char in string.punctuation:
                            ng.insert(1,'yes')
                            char_flag = True
                            break
                        else:
                            continue
                    if not char_flag:
                        ng.insert(1,'no')
                if isdir:
                    for n in ngramsList:
                        # n.append(inputFilename)
                        n.append(IO_csv_util.dressFilenameForCSVHyperlink(inputFilename))
                    if bySentenceID == True:
                        ngramsList.insert(0, [str(j) + '-grams', 'Punctuation','Frequency', 'Sentence ID', 'Sentence', 'Document'])
                    else:
                        for ngram in ngramsList:
                            ngram.pop(3)
                        ngramsList.insert(0, [str(j) + '-grams','Punctuation', 'Frequency','Sentence', 'Document'])
                else:
                    if bySentenceID == True:
                        ngramsList.insert(0, [str(j) + '-grams','Punctuation', 'Frequency', 'Sentence ID', 'Sentence'])
                    else:
                        for ngram in ngramsList:
                            ngram.pop(3)
                        ngramsList.insert(0, [str(j) + '-grams', 'Punctuation','Frequency'])
                container.append(ngramsList)
    else: # character ngrams
        for j in range(1,ngramsNumber+1):
            ngramsList = []
            In = []
            for sent in char_tokens:
                for i in range(len(sent[0]) - (j - 1)):
                    In.append([sent[0][i:i + j], sent[1]])
            # all jgrams
            ctr = collections.Counter(Extract(In))
            for jgrams in In:
                jgrams.insert(1, ctr.get(jgrams[0]))
            # ngram     freq     sentenceID
            for i in In:
                if i[0] not in Extract(ngramsList):
                    ngramsList.append(i)
            ngramsList=sorted(ngramsList, key = lambda x: x[1])
            if excludePunctuation:
                if isdir:
                    for n in ngramsList:
                        # n.append(inputFilename)
                        n.append(IO_csv_util.dressFilenameForCSVHyperlink(inputFilename))
                    if bySentenceID == True:
                        ngramsList.insert(0, [str(j) + '-grams',  'Frequency', 'Sentence ID', 'Document'])
                    else:
                        for ngram in ngramsList:
                            ngram.pop(3)
                        ngramsList.insert(0, [str(j) + '-grams',  'Frequency', 'Document'])
                else:
                    if bySentenceID == True:
                        ngramsList.insert(0, [str(j) + '-grams',  'Frequency', 'Sentence ID', 'Sentence'])
                    else:
                        for ngram in ngramsList:
                            ngram.pop(3)
                        ngramsList.insert(0, [str(j) + '-grams',  'Frequency'])
                container.append(ngramsList)
            else:
                for ng in ngramsList:
                    char_flag = False
                    for char in ng[0]:
                        if char in string.punctuation:
                            ng.insert(1,'yes')
                            char_flag = True
                            break
                        else:
                            continue
                    if not char_flag:
                        ng.insert(1,'no')
                if isdir:
                    for n in ngramsList:
                        # n.append(inputFilename)
                        n.append(IO_csv_util.dressFilenameForCSVHyperlink(inputFilename))
                    if bySentenceID == True:
                        ngramsList.insert(0, [str(j) + '-grams',  'Punctuation','Frequency', 'Sentence ID', 'Document'])
                    else:
                        for ngram in ngramsList:
                            ngram.pop(3)
                        ngramsList.insert(0, [str(j) + '-grams', 'Punctuation', 'Frequency', 'Document'])
                else:
                    if bySentenceID == True:
                        ngramsList.insert(0, [str(j) + '-grams',  'Punctuation','Frequency', 'Sentence ID', 'Sentence'])
                    else:
                        for ngram in ngramsList:
                            ngram.pop(3)
                        ngramsList.insert(0, [str(j) + '-grams', 'Punctuation', 'Frequency'])
                container.append(ngramsList)

    return container

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
def yule(window, inputFilename, inputDir, outputDir, hideMessage=False):
    # yule's I measure (the inverse of yule's K measure)
    # higher number is higher diversity - richer vocabulary
    filesToOpen = []
    Yule_value_list=[]
    headers = ["Yule's K Value", "Document ID", "Document"]
    index = 0
    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')

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
    if outputFilename != '':
        filesToOpen.append(outputFilename)
    return filesToOpen


# called by sentence_analysis_main and style_analysis_main
def process_words(window,inputFilename,inputDir,outputDir, openOutputFiles, createCharts, chartPackage, processType='', excludeStopWords=True,word_length=3):
    filesToOpen=[]
    documentID = 0
    multiple_punctuation=0
    exclamation_punctuation=0
    question_punctuation=0
    punctuation_docs=[]

    word_list=[]

    fin = open('../lib/wordLists/stopwords.txt', 'r')
    stops = set(fin.read().splitlines())
    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')

    Ndocs=str(len(inputDocs))

    if processType != '':
        hideMessage = False
    else:
        hideMessage = True
    if Ndocs == 1:
        hideMessage = False
    else:
        hideMessage = True

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                           'Started running ' + processType + ' at', True)

    for doc in inputDocs:
        head, tail = os.path.split(doc)
        documentID = documentID + 1
        print("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)

        fullText = (open(doc, "r", encoding="utf-8", errors="ignore").read())
        fullText = fullText.replace('\n', ' ')
        sentences = sent_tokenize_stanza(stanzaPipeLine(fullText))

        sentenceID = 0  # to store sentence index
        # check each word in sentence for concreteness and write to outputFilename

        # analyze each sentence for concreteness
        for s in sentences:
            sentenceID = sentenceID + 1
            # print("S" + str(i) +": " + s)
            all_words = []
            found_words = []
            total_words = 0

            words = word_tokenize_stanza(stanzaPipeLine(s))
            # don't process stopwords
            filtered_words = words
            if processType != '' and not "punctuation" in processType.lower():
                if excludeStopWords:
                    words = excludeStopWords_list(words)
                    filtered_words = [word for word in words if word.isalpha()]  # strip out words with punctuation
            # words = fullText.translate(string.punctuation).split()
            for wordID, word in enumerate(filtered_words):

# SHORT WORDS --------------------------------------------------------------------------

                if processType=='' or "short" in processType.lower():
                    header = ['Short words (<4 characters)', 'Word ID (in sentence)', 'Number of words in sentence', 'Sentence ID','Sentence','Document ID','Document']
                    select_col = ['Short words (<4 characters)']
                    fileLabel='short_words'
                    fileLabel_byDocID = 'vowel_words_byDoc'
                    columns_to_be_plotted = [[0, 0]] # bar chart
                    columns_to_be_plotted_byDocID = [[6, 6]] # bar chart
                    chart_title_label = 'Frequency of Short Words (<4 Characters)'
                    chart_title_byDocID='Frequency of Short Words by Document'
                    chart_title_bySentID ='Frequency of Short Words by Sentence Index'
                    column_xAxis_label = 'Short Words (<4 Characters)'

                    # exclude numbers from list
                    if word and len(word) <= int(word_length) and word.isalpha():
                        word_list.append([word, wordID + 1, len(words), sentenceID, s, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])

# INITIAL-CAPITAL WORDS --------------------------------------------------------------------------

                if processType=='' or "capital" in processType.lower():
                    header = ['Initial-capital words', 'Word ID (in sentence)', 'Number of words in sentence', 'Sentence ID', 'Sentence', 'Document ID','Document']
                    select_col = ['Initial-capital words']
                    fileLabel='init_cap_words'
                    fileLabel_byDocID = 'vowel_words_byDoc'
                    columns_to_be_plotted = [[0, 0]] # bar chart
                    columns_to_be_plotted_byDocID = [[6, 6]] # bar chart
                    chart_title_label = 'Frequency of Initial-Capital Words'
                    chart_title_byDocID ='Frequency of Initial-Capital Words by Document'
                    chart_title_bySentID ='Frequency of Initial-Vowel Words by Sentence Index'
                    column_xAxis_label = 'Initial-Capital Words'

                    if word and word and word[0].isupper():
                        word_list.append([word, wordID + 1, len(words), sentenceID, s, documentID,
                                  IO_csv_util.dressFilenameForCSVHyperlink(doc)])

# INITIAL-VOWEL WORDS --------------------------------------------------------------------------

                if processType=='' or "vowel" in processType.lower():
                    header = ['Initial-vowel', 'Word ID (in sentence)', 'Number of words in sentence', 'Sentence ID', 'Sentence', 'Document ID', 'Document']
                    select_col = ['Initial-vowel words']
                    fileLabel='vowel_words'
                    fileLabel_byDocID = 'vowel_words_byDoc'
                    columns_to_be_plotted = [[0, 0]] # bar chart
                    columns_to_be_plotted_byDocID = [[6, 6]] # bar chart
                    chart_title_label = 'Frequency of Initial-Vowel Words'
                    chart_title_byDocID='Frequency of Initial-Vowel Words by Document'
                    chart_title_bySentID = 'Frequency of Initial-Vowel Words by Sentence Index'
                    column_xAxis_label = 'Initial-Vowel Words'
                    if word and word and word[0] in "aeiou" and word.isalpha():
                        word_list.append([word, wordID + 1, len(words), sentenceID, s, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])

# PUNCTUATION SYMBOLS --------------------------------------------------------------------------

                if processType == '' or "punctuation" in processType.lower():
                    header = ['Punctuation symbols of pathos (?!)', 'Word ID (in sentence)', 'Number of words in sentence', 'Sentence ID', 'Sentence', 'Document ID','Document']
                    select_col = ['Punctuation symbols of pathos (?!)'] # line chart by sentence index
                    fileLabel = 'punctuation'
                    fileLabel_byDocID = 'punctuation_byDoc'
                    columns_to_be_plotted = [[0, 0]] # bar chart
                    columns_to_be_plotted_byDocID = [[6, 6]] # bar chart
                    chart_title_label = 'Frequency of Punctuation Symbols of Pathos (?!)'
                    chart_title_byDocID='Frequency of Punctuation Symbols of Pathos (?!) by Document'
                    chart_title_bySentID='Frequency of Punctuation Symbols of Pathos (?!) by Sentence Index'
                    column_xAxis_label = 'Punctuation symbols of pathos (?!)'
                    if word != '!' and word != '?':
                        continue
                    word_list.extend([[word, wordID + 1, len(words), sentenceID, s, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)]])
                    if doc not in punctuation_docs:
                        punctuation_docs.append(doc)
                    if '!' in word and '?' in word:
                        multiple_punctuation=multiple_punctuation+1
                    elif '!' in word:
                        exclamation_punctuation=exclamation_punctuation+1
                    elif '?' in word:
                        question_punctuation=question_punctuation+1

# N-GRAMS & HAPAX --------------------------------------------------------------------------

                if processType == '' or "N-grams" in processType or "hapax" in processType.lower():
                    if "hapax" in processType.lower():
                        ngramsNumber=1
                        frequency=1 #hapax
                    else:
                        ngramsNumber = 3
                        frequency = None  # N-grams
                    normalize=False
                    excludePunctuation=True
                    wordgram=True
                    bySentenceID=False
                    tempOutputFiles=compute_character_word_ngrams(window,inputFilename,inputDir,outputDir, ngramsNumber, normalize, excludePunctuation, wordgram, frequency, openOutputFiles, createCharts, chartPackage,
                                                                      bySentenceID)
                    # Excel charts are generated in compute_character_word_ngrams; return to exit here
                    return

        word_list.insert(0, header)

        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', fileLabel)
        IO_error=IO_csv_util.list_to_csv(window, word_list, outputFilename)
        if not IO_error:
            filesToOpen.append(outputFilename)

        if createCharts == True:
            outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                         fileLabel)
            hover_label = []
            inputFilename = outputFilename
            chart_outputFilename = charts_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                             outputFileLabel=fileLabel,
                                                             chartPackage=chartPackage,
                                                             chart_type_list=["bar"],
                                                             chart_title=chart_title_label,
                                                             column_xAxis_label_var=column_xAxis_label,
                                                             hover_info_column_list=hover_label,
                                                             count_var=True)
            if chart_outputFilename != "":
                filesToOpen.append(chart_outputFilename)

            # should also provide a bar chart of the frequency of distinct documents by punctuation symbol
            hover_label = []
            inputFilename = outputFilename
            chart_outputFilename = charts_util.run_all(columns_to_be_plotted_byDocID, inputFilename, outputDir,
                                                             outputFileLabel=fileLabel_byDocID,
                                                             chartPackage=chartPackage,
                                                             chart_type_list=["bar"],
                                                             chart_title=chart_title_byDocID,
                                                             column_xAxis_label_var='', #Document
                                                             hover_info_column_list=hover_label,
                                                             count_var=True)
            if chart_outputFilename != "":
                filesToOpen.append(chart_outputFilename)

            # if 'by sentence index' in processType.lower():
            # n-grams
            # line plots by sentence index -----------------------------------------------------------------------------------------------
            chart_outputFilename = statistics_csv_util.compute_csv_column_frequencies(inputFilename=outputFilename,
                                                                            outputDir=outputDir,
                                                                            select_col=select_col,
                                                                            group_col=['Sentence ID'],
                                                                            chartPackage=chartPackage,
                                                                            chartTitle=chart_title_bySentID)
            if chart_outputFilename != None:
                filesToOpen.append(chart_outputFilename)


    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
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
    print(cleaned_words)
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

    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')

    Ndocs=str(len(inputDocs))

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running txt conversion (lemmatization & stopwords) at',
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
            words = word_tokenize_stanza(stanzaPipeLine(fullText))

            if excludeStopWords:
                words = excludeStopWords_list(words)

            if lemmatizeWords:
                # lemmatizer = WordNetLemmatizer()
                # text_vocab = set(lemmatizer.lemmatize(w.lower()) for w in fullText.split(" ") if w.isalpha())
                # words = set(lemmatizing(w.lower()) for w in words if w.isalpha()) # fullText.split(" ") if w.isalpha())
                text_vocab = set(lemmatize_stanza(stanzaPipeLine(w.lower())) for w in fullText.split(" ") if w.isalpha())
                words = set(lemmatizing(w.lower()) for w in words if w.isalpha()) # fullText.split(" ") if w.isalpha())

def compute_sentence_length(inputFilename, inputDir, outputDir, createCharts, chartPackage):
    filesToOpen = []
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    Ndocs = len(inputDocs)
    if Ndocs == 0:
        return
    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
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
                # sentences = tokenize.sent_tokenize(text)
                sentences = sent_tokenize_stanza(stanzaPipeLine(text))
                for sentence in sentences:
                    # tokens = nltk.word_tokenize(sentence)
                    tokens = word_tokenize_stanza(stanzaPipeLine(sentence))
                    if len(tokens) > 100:
                        long_sentences = long_sentences + 1
                    sentenceID = sentenceID + 1
                    writer.writerow(
                        [len(tokens), sentenceID, sentence, fileID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])
        csvOut.close()

        answer = tk.messagebox.askyesno("TIPS file on memory issues", str(Ndocs) + " file(s) processed in input.\n\n" +
                                        "Output csv file written to the output directory " + outputDir + "\n\n" +
                                        str(
                                            long_sentences) + " SENTENCES WERE LONGER THAN 100 WORDS (the average sentence length in modern English is 20 words).\n\nMore to the point... Stanford CoreNLP would heavily tax memory resources with such long sentences.\n\nYou should consider editing these sentences if Stanford CoreNLP takes too long to process the file or runs out of memory.\n\nPlease, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.\n\nDo you want to open the TIPS file now?")
        if answer:
            TIPS_util.open_TIPS('TIPS_NLP_Stanford CoreNLP memory issues.pdf')

    filesToOpen.append(outputFilename)

    # number of sentences in input
    chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                       columns_to_be_plotted_bar=[[0, 0]],
                                                       columns_to_be_plotted_bySent=[[1,0]],
                                                       columns_to_be_plotted_byDoc=[[0, 4]],
                                                       chartTitle='Frequency of Sentences',
                                                       count_var=1, hover_label=[],
                                                       outputFileNameType='line_bar',
                                                       column_xAxis_label='Sentence length',
                                                       groupByList=['Document ID', 'Document'],
                                                       plotList=['Sentence length (in words)'], chart_label='Sentences')

    if chart_outputFilename != None:
        filesToOpen.extend(chart_outputFilename)

    return filesToOpen

# wordList is a string
def extract_sentences(window, inputFilename, inputDir, outputDir, inputString):
    filesToOpen=[]
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    Ndocs = len(inputDocs)
    if Ndocs == 0:
        return

    # Win/Mac may use different quotation, we replace any directional quotes to straight ones
    right_double = u"\u201C"  # “
    left_double = u"\u201D"  # ”
    straight_double = u"\u0022"  # "
    if (right_double in inputString) or (left_double in inputString):
        inputString = inputString.replace(right_double, straight_double)
        inputString = inputString.replace(left_double, straight_double)
    if inputString.count(straight_double) == 2:
        # Append ', ' to the end of search_words_var so that literal_eval creates a list
        inputString += ', '
    # convert the string inputString to a list []
    def Convert(inputString):
        wordList = list(inputString.split(","))
        return wordList

    wordList = Convert(inputString)

    # wordList = ast.literal_eval(inputString)
    # print('wordList',wordList)
    # try:
    # 	wordList = ast.literal_eval(inputString)
    # except:
    # 	mb.showwarning(title='Search error',message='The search function encountered an error. If you have entered multi-word expressions (e.g. beautiful girl make sure to enclose them in double quotes "beautiful girl"). Also, make sure to separate single-word expressions, with a comma (e.g., go, come).')
    # 	return
    caseSensitive = mb.askyesno("Python", "Do you want to process your search word(s) as case sensitive?")

    if inputFilename!='':
        inputFileBase = os.path.basename(inputFilename)[0:-4]  # without .txt
        outputDir_sentences = os.path.join(outputDir, "sentences_" + inputFileBase)
    else:
        # processing a directory
        inputDirBase = os.path.basename(inputDir)
        outputDir_sentences = os.path.join(outputDir, "sentences_Dir_" + inputDirBase)

    # create a subdirectory in the output directory
    outputDir_sentences_extract = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='extract', silent=True)
    if outputDir_sentences_extract == '':
        return
    outputDir_sentences_extract_minus = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='extract_minus', silent=True)
    if outputDir_sentences_extract_minus == '':
        return

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                   'Started running the Word search function at',
                                                   True, '', True)

    fileID = 0
    file_extract_written = False
    file_extract_minus_written = False
    nDocsExtractOutput = 0
    nDocsExtractMinusOutput = 0

    for doc in inputDocs:
        wordFound = False
        fileID = fileID + 1
        head, tail = os.path.split(doc)
        print("Processing file " + str(fileID) + "/" + str(Ndocs) + ' ' + tail)
        with open(doc, 'r', encoding='utf-8', errors='ignore') as inputFile:
            text = inputFile.read().replace("\n", " ")
        outputFilename_extract = os.path.join(outputDir_sentences_extract,tail[:-4]) + "_extract.txt"
        outputFilename_extract_minus = os.path.join(outputDir_sentences_extract_minus,tail[:-4]) + "_extract_minus.txt"
        with open(outputFilename_extract, 'w', encoding='utf-8', errors='ignore') as outputFile_extract, open(
                outputFilename_extract_minus, 'w', encoding='utf-8', errors='ignore') as outputFile_extract_minus:
            # sentences = tokenize.sent_tokenize(text)
            sentences = sent_tokenize_stanza(stanzaPipeLine(text))
            n_sentences_extract = 0
            n_sentences_extract_minus = 0
            for sentence in sentences:
                wordFound = False
                sentenceSV = sentence
                nextSentence = False
                for word in wordList:
                    if nextSentence == True:
                        # go to next sentence; do not write the same sentence several times if it contains several words in wordList
                        break
                    #
                    if caseSensitive==False:
                        sentence = sentence.lower()
                        word = word.lower()
                    if word in sentence:
                        wordFound = True
                        nextSentence = True
                        n_sentences_extract += 1
                        outputFile_extract.write(sentenceSV + " ")  # write out original sentence
                        file_extract_written = True
                        # if none of the words in wordList are found in a sentence write the sentence to the extract_minus file
                if wordFound == False:
                    n_sentences_extract_minus += 1
                    outputFile_extract_minus.write(sentenceSV + " ")  # write out original sentence
                    file_extract_minus_written = True
        if file_extract_written == True:
            # filesToOpen.append(outputFilename_extract)
            nDocsExtractOutput += 1
            file_extract_written = False
        outputFile_extract.close()
        if n_sentences_extract == 0: # remove empty file
            os.remove(outputFilename_extract)
        if file_extract_minus_written:
            # filesToOpen.append(outputFilename_extract_minus)
            nDocsExtractMinusOutput += 1
            file_extract_minus_written = False
        outputFile_extract_minus.close()
        if n_sentences_extract_minus == 0: # remove empty file
            os.remove(outputFilename_extract_minus)
    if Ndocs == 1:
        msg1 = str(Ndocs) + " file was"
    else:
        msg1 = str(Ndocs) + " files were"
    if nDocsExtractOutput == 1:
        msg2 = str(nDocsExtractOutput) + " file was"
    else:
        msg2 = str(nDocsExtractOutput) + " files were"
    if nDocsExtractMinusOutput == 1:
        msg3 = str(nDocsExtractMinusOutput) + " file was"
    else:
        msg3 = str(nDocsExtractMinusOutput) + " files were"
    mb.showwarning("Warning", msg1 + " processed in input.\n\n" +
                   msg2 + " written with _extract in the filename.\n\n" +
                   msg3 + " written with _extract_minus in the filename.\n\n" +
                   "Files were written to the subdirectories " + outputDir_sentences_extract + " and " + outputDir_sentences_extract_minus + " of the output directory." +
                   "\n\nPlease, check the output subdirectories for filenames ending with _extract.txt and _extract_minus.txt.")

    IO_files_util.openExplorer(window, outputDir_sentences)


    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                   'Finished running the Word search unction at', True)


# https://pypi.org/project/textstat/
def sentence_text_readability(window, inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage, processType):
    filesToOpen = []
    documentID = 0

    files = IO_files_util.getFileList(inputFilename, inputDir, '.txt')
    nFile = len(files)
    if nFile == 0:
        return

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
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
        # IO_util.timed_alert(GUI_util.window,3000,'Analysis start','Started running NLTK unusual words at',True,'You can follow NLTK unusual words in command line.')

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
                # 0 (Flesch Reading Ease) has a different scale and 3 (SMOG) is often 0
                #	do NOT plot on the same chart these two measures
                #	plot all other 6 measures
                columns_to_be_plotted = [[10, 1], [10, 2], [10, 4], [10, 5], [10, 6],[10, 7]]
                # multiple lines with hover-over effects the sample line chart produces wrong results
                # hover_label = ['Sentence', 'Sentence', 'Sentence', 'Sentence', 'Sentence', 'Sentence']
                hover_label = []

                chart_outputFilename = charts_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                                 outputFileLabel='READ',
                                                                 chartPackage=chartPackage,
                                                                 chart_type_list=["line"],
                                                                 chart_title='Text Readability (6 Readability Measures)',
                                                                 column_xAxis_label_var='Sentence index',
                                                                 hover_info_column_list=hover_label,
                                                                 count_var=0,
                                                                 column_yAxis_label_var='6 Readability measures')

                if chart_outputFilename != "":
                    # rename filename not be overwritten by next line plot
                    try:
                        chart_outputFilename_new = chart_outputFilename.replace("line_chart", "ALL_line_chart")
                        os.rename(chart_outputFilename, chart_outputFilename_new)
                    except:
                        # the file already exists and must be removed
                        if os.path.isfile(chart_outputFilename_new):
                            os.remove(chart_outputFilename_new)
                        os.rename(chart_outputFilename, chart_outputFilename_new)

                    filesToOpen.append(chart_outputFilename_new)

                # outputFilenameXLSM_1 = charts_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                #                                           outputFilename, chart_type_list=["line"],
                #                                           chart_title="Text Readability",
                #                                           column_xAxis_label_var='Sentence Index',
                #                                           column_yAxis_label_var='Readability grade level',
                #                                           outputExtension='.xlsm', label1='READ', label2='line',
                #                                           label3='charts', label4='', label5='', useTime=False,
                #                                           disable_suffix=True,
                #                                           count_var=0, column_yAxis_field_list=[],
                #                                           reverse_column_position_for_series_label=False,
                #                                           series_label_list=[''], second_y_var=0, second_yAxis_label='',
                #                                           hover_var=1, hover_info_column_list=hover_label)
                # if outputFilenameXLSM_1 != "":
                #     filesToOpen.append(outputFilenameXLSM_1)

                # plot overall grade level
                columns_to_be_plotted = [[10, 9]]
                hover_label = ['Sentence']
                chart_outputFilename = charts_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                                 outputFileLabel='READ',
                                                                 chartPackage=chartPackage,
                                                                 chart_type_list=["line"],
                                                                 chart_title='Text Readability (Readability Grade Level)',
                                                                 column_xAxis_label_var='Sentence index',
                                                                 hover_info_column_list=hover_label,
                                                                 count_var=0,
                                                                 column_yAxis_label_var='Readability grade level')

                if chart_outputFilename != "":
                    filesToOpen.append(chart_outputFilename)

                # outputFilenameXLSM_2 = charts_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                #                                           outputFilename, chart_type_list=["line"],
                #                                           chart_title="Text Readability",
                #                                           column_xAxis_label_var='Sentence Index',
                #                                           column_yAxis_label_var='Readability grade level',
                #                                           outputExtension='.xlsm', label1='READ', label2='line',
                #                                           label3='chart', label4='', label5='', useTime=False,
                #                                           disable_suffix=True,
                #                                           count_var=0, column_yAxis_field_list=[],
                #                                           reverse_column_position_for_series_label=False,
                #                                           series_label_list=[''], second_y_var=0, second_yAxis_label='',
                #                                           hover_var=1, hover_info_column_list=hover_label)
                # if outputFilenameXLSM_2 != "":
                #     filesToOpen.append(outputFilenameXLSM_2)

            # bar chart of the frequency of sentences by grade levels
            columns_to_be_plotted = [[10, 8]]
            hover_label = []

            chart_outputFilename = charts_util.run_all(columns_to_be_plotted, outputFilename, outputDir,
                                                             outputFileLabel='READ',
                                                             chartPackage=chartPackage,
                                                             chart_type_list=["bar"],
                                                             chart_title='Frequency of Sentences by Readability Consensus of Grade Level',
                                                             column_xAxis_label_var='',
                                                             hover_info_column_list=hover_label,
                                                             count_var=1)
            if chart_outputFilename != "":
                filesToOpen.append(chart_outputFilename)

            # outputFilenameXLSM_3 = charts_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
            #                                           outputFilename, chart_type_list=["bar"],
            #                                           chart_title="Frequency of Sentences by Readability Consensus of Grade Level",
            #                                           column_xAxis_label_var='', column_yAxis_label_var='Frequency',
            #                                           outputExtension='.xlsm', label1='READ', label2='bar',
            #                                           label3='chart', label4='', label5='', useTime=False,
            #                                           disable_suffix=True,
            #                                           count_var=1, column_yAxis_field_list=[],
            #                                           reverse_column_position_for_series_label=False,
            #                                           series_label_list=[''], second_y_var=0, second_yAxis_label='',
            #                                           hover_var=1, hover_info_column_list=hover_label)
            # if outputFilenameXLSM_3 != "":
            #     filesToOpen.append(outputFilenameXLSM_3)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running Text Readability at',
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
def compute_sentence_complexity(window, inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage):
    ## list for csv file
    documentID = []
    document = []
    documentName = []

    all_input_docs = {}
    dId = 0

    filesToOpen = []

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start',
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
        numFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
        if numFiles == 0:
            mb.showerror(title='Number of files error',
                         message='The selected input directory does NOT contain any file of txt type.\n\nPlease, select a different directory and try again.')
            return

        for doc in os.listdir(inputDir):
            if doc.endswith('.txt'):
                head, tail = os.path.split(doc)
                with open(os.path.join(inputDir, doc), 'r', encoding='utf-8', errors='ignore') as file:
                    dId += 1
                    print("Importing filename " + str(dId) + '/' + str(numFiles) + tail)
                    text = file.read()
                    documentID.append(dId)
                    document.append(IO_csv_util.dressFilenameForCSVHyperlink(os.path.join(inputDir, doc)))
                    all_input_docs[dId] = text
    document_df = pd.DataFrame({'Document ID': documentID, 'Document': document})
    document_df = document_df.astype('str')

    nlp = stanza.Pipeline(lang='en', processors='tokenize,pos, constituency',use_gpu=False)
    op = pd.DataFrame(
        columns=['Sentence length (No. of words)', 'Yngve score', 'Yngve sum', 'Frazier score', 'Frazier sum',
                 'Sentence ID', 'Sentence', 'Document ID', 'Document'])
    for idx, txt in enumerate(all_input_docs.items()):
        doc = nlp(txt[1])
        tail = os.path.split(IO_csv_util.undressFilenameForCSVHyperlink(document[idx]))[1]
        print("Processing file " + str(dId) + '/' + str(numFiles) + tail)
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
            op = op.append({
                'Sentence length (No. of words)': sentence_length,
                'Yngve score': yAvg,
                'Yngve sum': ySum,
                'Frazier score': fAvg,
                'Frazier sum': fSum,
                'Sentence ID': i + 1,
                'Sentence': sentence.text,
                'Document ID': idx + 1,
                'Document': document[idx],
            },
                ignore_index=True)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                             'SentenceComplexity')
    op.to_csv(outputFilename, index=False)
    filesToOpen.append(outputFilename)

    chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                       columns_to_be_plotted_bar=[[1, 1], [3, 3]],
                                                       columns_to_be_plotted_bySent=[[5, 1], [5, 3]],
                                                       columns_to_be_plotted_byDoc=[[1,8], [3,8]],
                                                       chartTitle='Frequency Distribution of Complexity Scores',
                                                       count_var=1, hover_label=[],
                                                       outputFileNameType='pronouns_bar',
                                                       column_xAxis_label='Complexity scores',
                                                       groupByList=['Document ID','Document'],
                                                       plotList=['Yngve score','Frazier score'],
                                                       chart_label='Complexity')
    if chart_outputFilename != None:
        if len(chart_outputFilename) > 0:
            filesToOpen.extend(chart_outputFilename)

    # # compute statistics about complexity measures
    # groupByList=['Document ID','Document']
    # plotList=['Yngve score',['Frazier score']]
    # chart_label='Complexity'
    # tempOutputfile=statistics_csv_util.compute_csv_column_statistics(GUI_util.window, outputFilename, outputDir,
    #                                     groupByList, plotList,chart_label,
    #                                     createCharts, chartPackage)
    # if tempOutputfile!=None:
    #     filesToOpen.extend(tempOutputfile)
    #
    # if createCharts == True:
    #     inputFilename = outputFilename

        # columns_to_be_plotted = [[1, 1], [3, 3]]
        # # hover_label = ['Sentence', 'Sentence']
        # hover_label = []
        # chart_outputFilename = charts_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
        #                                                  outputFileLabel='Complex',
        #                                                  chartPackage=chartPackage,
        #                                                  chart_type_list=["bar"],
        #                                                  chart_title='Complexity Scores (Yngve, Frazier)',
        #                                                  column_xAxis_label_var='',
        #                                                  hover_info_column_list=hover_label,
        #                                                  count_var=1,
        #                                                  column_yAxis_label_var='Scores')
        # if chart_outputFilename != "":
        #     filesToOpen.append(chart_outputFilename)

        # columns_to_be_plotted = [[5, 1], [5, 3]] # sentence ID field comes first [5
        # # hover_label = ['Sentence', 'Sentence']
        # hover_label = []
        # chart_outputFilename = charts_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
        #                                                  outputFileLabel='Complex',
        #                                                  chartPackage=chartPackage,
        #                                                  chart_type_list=["line"],
        #                                                  chart_title='Complexity Scores (Yngve, Frazier) by Sentence Index',
        #                                                  column_xAxis_label_var='Sentence index',
        #                                                  hover_info_column_list=hover_label,
        #                                                  count_var=0,
        #                                                  column_yAxis_label_var='Scores',
        #                                                  complete_sid=True)
        # if chart_outputFilename != "":
        #     filesToOpen.append(chart_outputFilename)

        # columns_to_be_plotted = [[1,8], [3,8]] # Document comes second [5
        # # hover_label = ['Sentence', 'Sentence']
        # hover_label = []
        # chart_outputFilename = charts_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
        #                                                  outputFileLabel='ByDoc',
        #                                                  chartPackage=chartPackage,
        #                                                  chart_type_list=["bar"],
        #                                                  chart_title='Complexity Scores (Yngve, Frazier) by Document',
        #                                                  column_xAxis_label_var='',
        #                                                  hover_info_column_list=hover_label,
        #                                                  count_var=1,
        #                                                  column_yAxis_label_var='Scores',
        #                                                  remove_hyperlinks=True)
        # if chart_outputFilename != "":
        #     filesToOpen.append(chart_outputFilename)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
                                       'Finished running Sentence Complexity at', True, '', True, startTime)
    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(window, openOutputFiles, filesToOpen, outputDir)