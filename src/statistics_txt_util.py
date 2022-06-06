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

import charts_Excel_util
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

def read_line(window, inputFilename, inputDir, outputDir,openOutputFiles,createExcelCharts, chartPackage):
    filesToOpen=[]
    outputFilenameCSV=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'line_length')
    filesToOpen.append(outputFilenameCSV)
    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    Ndocs = str(len(inputDocs))
    if Ndocs==0:
        return
    fieldnames=[
        'Line length (in characters)',
        'Line length (in words)',
        'Line ID',
        'Line',
        'Document ID',
        'Document'
    ]
    if IO_csv_util.openCSVOutputFile(outputFilenameCSV):
        return
    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running line length analysis at',
                                                 True, '', True, '', True)

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
                    # words = nltk.word_tokenize(line)
                    words = word_tokenize_stanza(stanzaPipeLine(line))
                    # print("Line {}: Length (in characters) {} Length (in words) {}".format(lineID, len(line), len(words)))
                    currentLine = [
                        [len(line), len(words),lineID,line.strip(), documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)]]
                    writer.writerows(currentLine)
                    line = file.readline()
    csvfile.close()

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running line length analysis at', True, '', True, startTime, True)

    # compute statistics about line length ungrouped
    tempOutputfile=statistics_csv_util.compute_field_statistics_NoGroupBy(window, outputFilenameCSV, outputDir, openOutputFiles, createExcelCharts, chartPackage, 3)
    if tempOutputfile!=None:
        filesToOpen.extend(tempOutputfile)

    # compute statistics about line length grouped by Document
    list=['Document ID','Document']
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
def compute_corpus_statistics(window,inputFilename,inputDir,outputDir,openOutputFiles,createExcelCharts,chartPackage,excludeStopWords=True,lemmatizeWords=True):
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

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running document(s) statistics at',
                                                 True, '', True, '', False)

    with open(outputFilenameCSV, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
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

        # compute statistics about doc length grouped by Document
        list = ['Document ID', 'Document']
        tempOutputfile = statistics_csv_util.compute_field_statistics_groupBy(window, outputFilenameCSV, outputDir,
                                                                              list, openOutputFiles,
                                                                              createExcelCharts, 4)
                                                                              # ,4)  # 'number of words in doc'
        if tempOutputfile != None:
            filesToOpen.extend(tempOutputfile)

        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running document(s) statistics at', True, '', True, startTime, False)

        if createExcelCharts==True:

            columns_to_be_plotted=[[2,3]]
            # hover_label=['Document']
            hover_label=[]
            inputFilename=outputFilenameCSV
            Excel_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                      outputFileLabel='',
                                                      chart_type_list=["bar"],
                                                      chart_title='Corpus Statistics: Frequency of Sentences by Document',
                                                      column_xAxis_label_var='', #Document
                                                      hover_info_column_list=hover_label)
            if Excel_outputFilename != "":
                # rename output file or it will be overwritten by the next chart
                Excel_extention = Excel_outputFilename[-5:]
                Excel_outputFilename_new=Excel_outputFilename[:-5]+'_sen.xlsm' + Excel_extention
                # the file already exists and must be removed
                if os.path.isfile(Excel_outputFilename_new):
                    os.remove(Excel_outputFilename_new)
                os.rename(Excel_outputFilename, Excel_outputFilename_new)
                filesToOpen.append(Excel_outputFilename_new)

            columns_to_be_plotted=[[2,4]]
            # hover_label=['Document']
            hover_label=[]
            inputFilename=outputFilenameCSV
            Excel_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                      outputFileLabel='',
                                                      chart_type_list=["bar"],
                                                      # chart_title='Corpus statistics\nCorpus directory: '+inputDir,
                                                      chart_title='Corpus Statistics: Frequency of Words by Document',
                                                      column_xAxis_label_var='Document',
                                                      hover_info_column_list=hover_label,
                                                      graph_type = chartPackage)
            if Excel_outputFilename != "":
                # rename output file or it will be overwritten by the next chart
                Excel_extention = Excel_outputFilename[-5:]
                Excel_outputFilename_new=Excel_outputFilename[:-5]+'_word'+Excel_extention
                # the file already exists and must be removed
                if os.path.isfile(Excel_outputFilename_new):
                    os.remove(Excel_outputFilename_new)
                os.rename(Excel_outputFilename, Excel_outputFilename_new)
                filesToOpen.append(Excel_outputFilename_new)

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
def compute_character_word_ngrams(window,inputFilename,inputDir,outputDir,ngramsNumber=4, normalize=False, excludePunctuation=False, wordgram=None, frequency = None, openOutputFiles=True, createExcelCharts=True, bySentenceID=None):
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
    # if createExcelCharts==True:
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
        if createExcelCharts==True and result==True:
            inputFilename=csv_outputFilename
            if bySentenceID == True:
                columns_to_be_plotted=[[2,1]]
                hover_label=[str(index+1)+'-grams']
                Excel_outputFilename = charts_Excel_util.compute_csv_column_frequencies(inputFilename=inputFilename,
                                                                                        outputDir=outputDir,
                                                                                        select_col=[],
                                                                                        group_col=['Sentence ID'],
                                                                                        chartTitle=chartTitle + str(index + 1) + '-grams Frequencies by Sentence Index')
                if Excel_outputFilename != "":
                    filesToOpen.append(Excel_outputFilename)
            else:
                columns_to_be_plotted=[[2,1]] # 0,1
                hover_label=[str(index+1)+'-grams'] # change to sentence

                Excel_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                          outputFileLabel='n-grams_'+str(index+1)+'_'+fn,
                                                          chart_type_list=["bar"],
                                                          chart_title=chartTitle + str(index+1) + '-grams',
                                                          column_xAxis_label_var='',
                                                          hover_info_column_list=hover_label,
                                                          graph_type = chartPackage)
                if Excel_outputFilename != "":
                    filesToOpen.append(Excel_outputFilename)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
                                       'Finished running Word/Characters N-Grams at', True, '', True, startTime, False )

    if len(inputDir) != 0:
        mb.showwarning(title='Warning', message='The output filename generated by N-grams is the name of the directory processed in input, rather than any individual file in the directory.\n\nThe output csv file includes all ' + str(nFile) + ' files in the input directory processed by N-grams.')

    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)


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
            mb.showinfo(title='Results', message='The value for the vocabulary richness statistics (word type/token ratio or Yule’s K) is: '+str(result) + '\n\nThe higher the value (0-100) and the richer is the vocabulary.')

        # print('   Yule’s K value: ' + str(result) + ' Value range: 0-100 (higher value, richer vocabulary)')
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
def process_words(window,inputFilename,inputDir,outputDir, openOutputFiles, createExcelCharts, chartPackage, processType='', excludeStopWords=True,word_length=3):
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
                    bySentenceID=True
                    tempOutputFiles=compute_character_word_ngrams(window,inputFilename,inputDir,outputDir, ngramsNumber, normalize, excludePunctuation, wordgram, frequency, openOutputFiles, createExcelCharts, chartPackage,
                                                                      bySentenceID)
                    # Excel charts are generated in compute_character_word_ngrams; return to exit here
                    return

        word_list.insert(0, header)

        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', fileLabel)
        IO_error=IO_csv_util.list_to_csv(window, word_list, outputFilename)
        if not IO_error:
            filesToOpen.append(outputFilename)

        if createExcelCharts == True:
            outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                         fileLabel)
            hover_label = []
            inputFilename = outputFilename
            Excel_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                             outputFileLabel=fileLabel,
                                                             chart_type_list=["bar"],
                                                             chart_title=chart_title_label,
                                                             column_xAxis_label_var=column_xAxis_label,
                                                             hover_info_column_list=hover_label,
                                                             count_var=True)
            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

            # should also provide a bar chart of the frequency of distinct documents by punctuation symbol
            hover_label = []
            inputFilename = outputFilename
            Excel_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted_byDocID, inputFilename, outputDir,
                                                             outputFileLabel=fileLabel_byDocID,
                                                             chart_type_list=["bar"],
                                                             chart_title=chart_title_byDocID,
                                                             column_xAxis_label_var='', #Document
                                                             hover_info_column_list=hover_label,
                                                             count_var=True)
            if Excel_outputFilename != "":
                filesToOpen.append(Excel_outputFilename)

            # if 'by sentence index' in processType.lower():
            # line plots by sentence index -----------------------------------------------------------------------------------------------
            Excel_outputFilename = charts_Excel_util.compute_csv_column_frequencies(inputFilename=outputFilename,
                                                                           outputDir=outputDir,
                                                                           select_col=select_col,
                                                                           group_col=['Sentence Index'],
                                                                           chartTitle=chart_title_bySentID)
            if Excel_outputFilename != None:
                filesToOpen.append(Excel_outputFilename)


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

