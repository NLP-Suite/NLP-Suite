# Written by Roberto Franzosi November 2019 
# Edited by Josh Karol
import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"statistics_txt_util",['nltk','csv','tkinter','os','string','collections','re','textstat','itertools'])==False:
    sys.exit(0)

import os
import tkinter.messagebox as mb
import collections
import re
from collections import Counter
import string
from nltk.stem.porter import PorterStemmer

import csv
import nltk

import statistics_csv_util
import IO_user_interface_util

#whether stopwordst were already downloaded can be tested, see stackoverflow
#   https://stackoverflow.com/questions/23704510/how-do-i-test-whether-an-nltk-resource-is-already-installed-on-the-machine-runni
#   see also caveats

# check stopwords
IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/stopwords','stopwords')
# check punkt
IO_libraries_util.import_nltk_resource(GUI_util.window,'tokenizers/punkt','punkt')

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.util import ngrams
from nltk.corpus import wordnet
# from gensim.utils import lemmatize
from itertools import groupby
import textstat

import Excel_util
import IO_files_util
import IO_csv_util

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
        lemmatizer = WordNetLemmatizer()
        lemma = lemmatizer.lemmatize(word, p)
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
    stop_words = stopwords.words('english')
    # since stop_words are lowercase exclude initial-capital words (He, I)
    words_excludeStopwords = [word for word in words if not word.lower() in stop_words]
    words = words_excludeStopwords
    # exclude punctuation
    words_excludePunctuation = [word for word in words if not word in string.punctuation]
    words = words_excludePunctuation
    return words

def read_line(window, inputFilename, inputDir, outputDir,openOutputFiles,createExcelCharts):
    filesToOpen=[]
    outputFilenameCSV=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'line_length')
    filesToOpen.append(outputFilenameCSV)
    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    Ndocs = str(len(inputDocs))
    if Ndocs==0:
        return
    fieldnames=['Document ID',
        'Document',
        'Line length (in characters)',
        'Line length (in words)',
        'Line ID',
        'Line']
    if IO_csv_util.openCSVOutputFile(outputFilenameCSV):
        return
    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running line length analysis at', True)

    with open(outputFilenameCSV, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
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
                   words = nltk.word_tokenize(line)
                   # print("Line {}: Length (in characters) {} Length (in words) {}".format(lineID, len(line), len(words)))
                   currentLine = [
                       [documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc), len(line), len(words),lineID,line.strip()]]
                   writer.writerows(currentLine)
                   line = file.readline()
    csvfile.close()

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running line length analysis at', True)

    # compute statistics about line length ungrouped
    tempOutputfile=statistics_csv_util.compute_field_statistics_NoGroupBy(window, outputFilenameCSV, outputDir, openOutputFiles, createExcelCharts, 3)
    if tempOutputfile!=None:
        filesToOpen.extend(tempOutputfile)

    # compute statistics about line length grouped by Document
    list=['Document ID']
    tempOutputfile=statistics_csv_util.compute_field_statistics_groupBy(window, outputFilenameCSV, outputDir,
                                        list, openOutputFiles,
                                        createExcelCharts,3) # 'Line length (in words)'
    if tempOutputfile!=None:
        filesToOpen.extend(tempOutputfile)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
        filesToOpen=[] # to avoid re-opening in calling function

    return filesToOpen

# https://www.nltk.org/book/ch02.html
# For the Gutenberg Corpus they provide the programming code to do it. section 1.9   Loading your own Corpus.
# see also https://people.duke.edu/~ccc14/sta-663/TextProcessingSolutions.html
def compute_corpus_statistics(window,inputFilename,inputDir,outputDir,openOutputFiles,createExcelCharts,excludeStopWords=True,lemmatizeWords=True):
    filesToOpen=[]
    outputFilenameCSV=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'corpus_stats', '')
    filesToOpen.append(outputFilenameCSV)
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
    if IO_csv_util.openCSVOutputFile(outputFilenameCSV):
        return

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running corpus statistics at', True)

    with open(outputFilenameCSV, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        #print("Number of corpus text documents: ",Ndocs)
        #currentLine.append([Ndocs])
        index=0
        for doc in inputDocs:
            head, tail = os.path.split(doc)
            index=index+1
            # currentLine.append([index])
            print("Processing file " + str(index) + "/" + str(Ndocs) + " " + tail)
            #currentLine.append([doc])
            fullText = (open(doc, "r", encoding="utf-8", errors="ignore").read())

            Nsentences=str(textstat.sentence_count(fullText))
            #print('TOTAL number of sentences: ',Nsentences)

            Nwords=str(textstat.lexicon_count(fullText, removepunct=True))
            #print('TOTAL number of words: ',Nwords)

            Nsyllables =textstat.syllable_count(fullText, lang='en_US')
            #print('TOTAL number of Syllables: ',Nsyllables)

            # words = fullText.split()
            words = nltk.word_tokenize(fullText)

            if excludeStopWords:
                words = excludeStopWords_list(words)

            if lemmatizeWords:
                lemmatizer = WordNetLemmatizer()
                text_vocab = []
                for w in words:
                    if w.isalpha():
                        text_vocab.append(lemmatizer.lemmatize(w.lower()))
                words = text_vocab

            word_counts = Counter(words)

            # 20 most frequent words in the document
            #print("\n\nTOP 20 most frequent words  ----------------------------")
            # for item in word_counts.most_common(20):
            #     print(item)
            # currentLine=[[Ndocs,index,doc,Nsentences,Nwords,Nsyllables]]
            currentLine=[[Ndocs,index,IO_csv_util.dressFilenameForCSVHyperlink(doc),Nsentences,Nwords,Nsyllables]]
            for item in word_counts.most_common(20):
                currentLine[0].append(item[0])  # word
                currentLine[0].append(item[1]) # frequency
            writer = csv.writer(csvfile)
            writer.writerows(currentLine)
        csvfile.close()

        # compute statistics about doc length grouped by Document
        list = ['Document ID']
        tempOutputfile = statistics_csv_util.compute_field_statistics_groupBy(window, outputFilenameCSV, outputDir,
                                                                              list, openOutputFiles,
                                                                              createExcelCharts, 4)
                                                                              # ,4)  # 'number of words in doc'
        if tempOutputfile != None:
            filesToOpen.extend(tempOutputfile)

        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running corpus statistics at', True)

        if createExcelCharts==True:
            columns_to_be_plotted=[[1,3],[1,4]]
            hover_label=['Document','Document']
            inputFilename=outputFilenameCSV
            Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                      outputFileLabel='',
                                                      chart_type_list=["bar"],
                                                      # chart_title='Corpus statistics\nCorpus directory: '+inputDir,
                                                      chart_title='Corpus Statistics: Frequency of Sentences & Words by Document',
                                                      column_xAxis_label_var='Document',
                                                      hover_info_column_list=hover_label)
            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

        # TODO
        #   we should create 10 classes of values by distance to the median of
        #       each value in the Number of Words in Document Col. E
        #   -0-10 11-20 21-30,… 91-100 
        #   and plot them as column charts. 
        
        if openOutputFiles==True:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
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
def compute_character_word_ngrams(window,inputFilename,inputDir,outputDir,ngramsNumber=4, normalize=False, excludePunctuation=False, wordgram=None, openOutputFiles=True, createExcelCharts=True, bySentenceID=None):
    filesToOpen = []
    container = []

    if inputFilename=='' and inputDir=='':
        mb.showwarning(title='Input error', message='No input file or input directory have been specified.\n\nThe function will exit.\n\nPlease, enter the required input options and try again.')
        return
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
        ngramsList = get_ngramlist(file, ngramsNumber, wordgram, excludePunctuation, bySentenceID, isdir=True)
        container.append(ngramsList)

    for index, f in enumerate(container):

        for n in f:
            for skip, gram in enumerate(n):
                if skip == 0:
                    gram.insert(-1, 'Document ID')
                    continue
                else:
                    gram.insert(-1, index + 1)
    one_gram = []
    for index, f in enumerate(container):
        if index == 0:
            one_gram += (f[0])
        else:
            one_gram += (f[0][1:])
        generalList = [one_gram]
    if ngramsNumber>1:
        two_gram = []
        for index, f in enumerate(container):
            if index == 0:
                two_gram += (f[1])
            else:
                two_gram += (f[1][1:])
        generalList = [one_gram, two_gram]
    if ngramsNumber>2:
        three_gram = []
        for index, f in enumerate(container):
            if index == 0:
                three_gram += (f[2])
            else:
                three_gram += (f[2][1:])
        generalList = [one_gram, two_gram, three_gram]
    if ngramsNumber>3:
        four_gram = []
        for index, f in enumerate(container):
            if index == 0:
                four_gram += (f[3])
            else:
                four_gram += (f[3][1:])
        generalList = [one_gram, two_gram, three_gram, four_gram]

    result=True
    # n-grams
    # if createExcelCharts==True:
    #     if nFile>10:
    #         result = mb.askyesno("Excel charts","You have " + str(nFile) + " files for which to compute Excel charts.\n\nTHIS WILL TAKE A LONG TIME.\n\nAre you sure you want to do that?",default='no')
    for index,ngramsList in enumerate(generalList):
        if nFile>1:
            csv_outputFilename=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'n-grams_' + str(index + 1) + '_' + fn, 'stats', '', '', '', False, True)
        else:
            csv_outputFilename=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'n-grams_' + str(index + 1) + '_' + fn, 'stats')

        filesToOpen.append(csv_outputFilename)
        IO_csv_util.list_to_csv(window,ngramsList, csv_outputFilename)

        # n-grams
        if createExcelCharts==True and result==True:
            inputFilename=csv_outputFilename
            if bySentenceID == True:
                columns_to_be_plotted=[[2,2]]
                hover_label=[str(index+1)+'-grams']
                Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                          outputFileLabel='n-grams_'+str(index+1)+'_'+fn,
                                                          chart_type_list=["line"],
                                                          chart_title=chartTitle + str(index+1) + '-grams',
                                                          column_xAxis_label_var='Sentence Index',
                                                          hover_info_column_list=hover_label)
                if Excel_outputFilename != "":
                    filesToOpen.append(Excel_outputFilename)
            else:
                columns_to_be_plotted=[[0,2]] # 0,1
                hover_label=[str(index+1)+'-grams'] # change to sentence

                # def run_all(columns_to_be_plotted, inputFilename, outputDir, outputFileLabel,
                #             chart_type_list, chart_title, column_xAxis_label_var,
                #             hover_info_column_list=[],
                #             count_var=0,
                #             column_yAxis_label_var='Frequencies',
                #             column_yAxis_field_list=[],
                #             reverse_column_position_for_series_label=False,
                #             series_label_list=[], second_y_var=0, second_yAxis_label=''):

                Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                          outputFileLabel='n-grams_'+str(index+1)+'_'+fn,
                                                          chart_type_list=["bar"],
                                                          chart_title=chartTitle + str(index+1) + '-grams',
                                                          column_xAxis_label_var='',
                                                          hover_info_column_list=hover_label)
                if Excel_outputFilename != "":
                    filesToOpen.append(Excel_outputFilename)

                # excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir, csv_outputFilename,
                # chart_type_list=["bar"], chart_title=chartTitle + str(index+1) + '-grams', column_xAxis_label_var='', column_yAxis_label_var='Frequency', outputExtension = '.xlsm', label1='n-grams_'+str(index+1)+'_'+fn,label2='bar',label3='chart',label4='',label5='', useTime=False,disable_suffix=True,  count_var=0, column_yAxis_field_list = [], reverse_column_position_for_series_label=False , series_label_list=[str(index+1)+'-grams'], second_y_var=0, second_yAxis_label='', hover_info_column_list=hover_label)
                # if excel_outputFilename != "":
                #     filesToOpen.append(excel_outputFilename)

    if len(inputDir) != 0:
        mb.showwarning(title='Warning', message='The output filename generated by N-grams is the name of the directory processed in input, rather than any individual file in the directory.\n\nThe output csv file includes all ' + str(nFile) + ' files in the input directory processed by N-grams.')

    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)


def get_ngramlist(inputFilename,ngramsNumber=4, wordgram=1, excludePunctuation=False, bySentenceID=False, isdir=False):

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
    sentences = nltk.sent_tokenize(text)
    for each_sentence in sentences:
        if excludePunctuation:
            each_sentence = each_sentence.translate(str.maketrans('', '', string.punctuation))
        Sentence_ID += 1
        if wordgram==0: # character ngrams
            char_tokens.append([''.join(nltk.word_tokenize(each_sentence)),Sentence_ID])
        else:
            for tk in nltk.word_tokenize(each_sentence):
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

    index = 0
    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')

    Ndocs=str(len(inputDocs))
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
            mb.showinfo(title='Results', message='The value for the vocabulary richness statistics (word type/token ratio or Yule’s K) is: '+str(result) + '\n\nThe higher the value (0-100) and the richer is the vocabulary.')
        print('   Yule’s K value: ' + str(result) + ' Value range: 0-100 (higher value, richer vocabulary)')

def print_results(window, words, class_word_list, header, inputFilename, outputDir, excludestowords, fileLabel, hideMessage, filesToOpen):
    if excludestowords:
        stopMsg="(excluding stopwords)"
    else:
        stopMsg="(including stopwords)"
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', fileLabel)
    class_word_list.insert(0, header,IO_csv_util.dressFilenameForCSVHyperlink(inputFilename))
    IO_error=IO_csv_util.list_to_csv(window, class_word_list, outputFilename)
    if IO_error:
        outputFilename=''

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

def process_words(window,inputFilename,inputDir,outputDir, openOutputFiles, createExcelCharts, processType='', excludeStopWords=True,word_length=3):
    filesToOpen=[]
    index = 0
    multiple_punctuation=0
    exclamation_punctuation=0
    question_punctuation=0
    punctuation_docs=[]

    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')

    Ndocs=str(len(inputDocs))
    word_list=[]
    for doc in inputDocs:
        head, tail = os.path.split(doc)
        index = index + 1
        print("Processing file " + str(index) + "/" + str(Ndocs) + " " + tail)
        fullText = (open(doc, "r", encoding="utf-8", errors="ignore").read())
        # words = fullText.translate(string.punctuation).lower().split()
        fullText = fullText.replace('\n',' ')
        words = fullText.translate(string.punctuation).split()
        if excludeStopWords:
            words = excludeStopWords_list(words)
        if processType != '':
            hideMessage = False
        else:
            hideMessage = True
        if Ndocs == 1:
            hideMessage = False
        else:
            hideMessage = True
        if processType=='' or "short" in processType.lower():
            header='Short words (<4 chars)'
            fileLabel='short_words'
            # exclude numbers from list
            word_list = [word for word in words if word and len(word) <= int(word_length) and word.isalpha()]
            filesToOpen=print_results(window, words, word_list, header, inputFilename, outputDir, excludeStopWords, fileLabel, hideMessage, filesToOpen)
            # filesToOpen.append(outputFilename)
        if processType=='' or "capital" in processType.lower():
            header='Initial-capital words'
            fileLabel='init_cap_words'
            word_list = [word for word in words if
                               word and word[
                                   0].isupper()]
            filesToOpen=print_results(window, words, word_list, header, inputFilename, outputDir, excludeStopWords, fileLabel, hideMessage, filesToOpen)
            # if outputFilename!='':
            #     filesToOpen.append(outputFilename)
        if processType=='' or "vowel" in processType.lower():
            header='Vowel words'
            fileLabel='vowel_words'
            word_list = [word for word in words if word and word[0] in "aeiou" and word.isalpha()]
            filesToOpen=print_results(window, words, word_list, header, inputFilename, outputDir, excludeStopWords, fileLabel, hideMessage, filesToOpen)
            # if outputFilename!='':
            #     filesToOpen.append(outputFilename)
        if processType == '' or "punctuation" in processType.lower():
            header = ['Word','Punctuation symbols of pathos (?!)','Document ID','Document']
            fileLabel = 'punctuation'
            for word in words:
                punctuation =''
                character_index=0
                for i in word:
                    if '!' in i or '?' in i:
                        punctuation=word[character_index:len(word)]
                        continue
                    character_index = character_index + 1
                if punctuation != '':
                    if doc not in punctuation_docs:
                        punctuation_docs.append(doc)
                    word_list.extend([[word, punctuation, index, IO_csv_util.dressFilenameForCSVHyperlink(doc)]])
                    if '!' in punctuation and '?' in punctuation:
                        multiple_punctuation=multiple_punctuation+1
                    elif '!' in punctuation:
                        exclamation_punctuation=exclamation_punctuation+1
                    elif '?' in punctuation:
                        question_punctuation=question_punctuation+1

    mb.showinfo(title='Results', message="Combinations of ! and ? punctuation symbols were used " + str(multiple_punctuation) + \
                        " times.\n\n! punctuation symbols were used " + str(exclamation_punctuation) + \
                        " times.\n\n? punctuation symbols were used " + str(question_punctuation) + \
                        " times.\n\n\nPunctuation symbols of pathos (!?) were used in " + str(len(punctuation_docs)) + " separate documents out of " + str(Ndocs) + " documents.\n\nCHECK COMMAND LINE FOR A COPY OF THESE RESULTS.")

    print("\nCombinations of ! and ? punctuation symbols were used " + str(multiple_punctuation) + \
                        " times.\n\n! punctuation symbols were used " + str(exclamation_punctuation) + \
                        " times.\n\n? punctuation symbols were used " + str(question_punctuation) + \
                        " times.\n\nPunctuation symbols of pathos (!?) were used in " + str(len(punctuation_docs)) + " separate documents out of " + str(Ndocs) + " documents.")

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', fileLabel)
    word_list.insert(0, header)
    IO_error = IO_csv_util.list_to_csv(window, word_list, outputFilename)

    if createExcelCharts == True:
        columns_to_be_plotted = [[1, 1]]
        hover_label = []
        inputFilename = outputFilename
        Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                  outputFileLabel='punct_stats',
                                                  chart_type_list=["bar"],
                                                  # chart_title='Corpus statistics\nCorpus directory: '+inputDir,
                                                  chart_title='Frequency of Punctuation Symbols of Pathos (?!)',
                                                  column_xAxis_label_var='Punctuation symbols of pathos (?!)',
                                                  hover_info_column_list=hover_label,
                                                  count_var=True)
        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)

        # should also provide a bar chart of the frequency of distinct documents by punctuation symbol
        columns_to_be_plotted = [[2,2]]
        hover_label = []
        inputFilename = outputFilename
        Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                  outputFileLabel='punct_doc_stats',
                                                  chart_type_list=["bar"],
                                                  # chart_title='Corpus statistics\nCorpus directory: '+inputDir,
                                                  chart_title='Frequency of ' + str(Ndocs) + ' Documents with Punctuation Symbols of Pathos (?!)',
                                                  column_xAxis_label_var='Punctuation symbols of pathos (?!)',
                                                  hover_info_column_list=hover_label,
                                                  count_var=True)
        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)

    if not IO_error:
        filesToOpen.append(outputFilename)
    return filesToOpen

# n is n most common words
# text is the plain text read in from a file
def n_most_common_words(n,text):
    cleaned_words, common_words = [], []
    for word in text.split():
        if word not in stopwords and '\'' not in word and '\"' not in word:
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

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running txt conversion (lemmatization & stopwords) at', True)

    with open(outputFilename, 'w', encoding='utf-8', errors='ignore', newline='') as outfile:
        #print("Number of corpus text documents: ",Ndocs)
        #currentLine.append([Ndocs])
        index=0
        for doc in inputDocs:
            head, tail = os.path.split(doc)
            index=index+1
            # currentLine.append([index])
            print("Processing file " + str(index) + "/" + str(Ndocs) + " " + tail)
            fullText = (open(doc, "r", encoding="utf-8", errors="ignore").read())

            Nsentences=str(textstat.sentence_count(fullText))
            #print('TOTAL number of sentences: ',Nsentences)

            Nwords=str(textstat.lexicon_count(fullText, removepunct=True))
            #print('TOTAL number of words: ',Nwords)

            Nsyllables =textstat.syllable_count(fullText, lang='en_US')
            #print('TOTAL number of Syllables: ',Nsyllables)

            # words = fullText.split()
            words = nltk.word_tokenize(fullText)

            if excludeStopWords:
                words = excludeStopWords_list(words)

            if lemmatizeWords:
                lemmatizer = WordNetLemmatizer()
                text_vocab = set(lemmatizer.lemmatize(w.lower()) for w in fullText.split(" ") if w.isalpha())
                words = set(lemmatizing(w.lower()) for w in words if w.isalpha()) # fullText.split(" ") if w.isalpha())

