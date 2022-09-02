import sys
import GUI_util
import IO_libraries_util

# You mentioned that you tried pip installing spellchecker & pyspellchecker.
# It is important to note that the spellchecker package was last updated in 2013 and appears to be irrelevant to the issue you are trying to solve (https://pypi.org/project/spellchecker/).
# This is where it gets confusing, the pyspellchecker package comes with a spellchecker module (https://pypi.org/project/pyspellchecker/).
# So... pip uninstall spellchecker, as this package is outdated and irrelevant.
# pip install pyspellchecker.
# To verify that this package is installed in the install packages method (IO_libraries_util.py), you should verify that the "spellchecker" module is present using "__import__()". T
# Instead of passing "pyspellchecker" as a listed package to be verified, we need to pass "spellchecker".
# This is because "spellchecker" is the module installed by the pyspellchecker package (https://pypi.org/project/pyspellchecker/).

if not IO_libraries_util.install_all_packages(GUI_util.window,"spell_checker_util",['nltk','tkinter','os','langdetect','spacy','spacy_langdetect','langid','csv','spellchecker','textblob','autocorrect','stanfordcorenlp','pandas','collections']):
    sys.exit(0)

import os
#from nltk.stem import WordNetLemmatizer
from tkinter import filedialog
#from nltk import tokenize
from Stanza_functions import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza
import nltk
# IO_libraries_util.import_nltk_resource(GUI_util.window,'tokenizers/punkt','punkt')
import pandas
import pandas as pd
from stanfordcorenlp import StanfordCoreNLP
import collections
import tkinter.messagebox as mb
from autocorrect import Speller
from spellchecker import SpellChecker
from textblob import Word
from pandas import DataFrame
import math
from langdetect import DetectorFactory, detect, detect_langs
import spacy
from spacy_langdetect import LanguageDetector
import langid
from langid.langid import LanguageIdentifier, model
import csv
import subprocess
import time

import file_cleaner_util
import charts_util
import IO_csv_util
import IO_files_util
import IO_user_interface_util
from IO_files_util import make_directory
import reminders_util

def lemmatizing(word):#edited by Claude Hu 08/2020
    #https://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python
    pos = ['n', 'v','a', 's', 'r']#list of postags
    result = word
    for p in pos:
        # if lemmatization with any postag gives different result from the word itself
        # that lemmatization is returned as #
        # lemmatizer = WordNetLemmatizer()
        # lemma = lemmatizer.lemmatize(word, p)
        lemma = lemmatize_stanza(stanzaPipeLine(word))
        if lemma != word:
            result = lemma
            break
    return result

# https://www.nltk.org/book/ch02.html
def nltk_unusual_words(window,inputFilename,inputDir,outputDir, openOutputFiles, createCharts=True, silent=False):
    filesToOpen=[]
    unusual=[]
    container=[]
    documentID=0
    files=IO_files_util.getFileList(inputFilename, inputDir, '.txt')
    nFile=len(files)
    if nFile==0:
        return
    outputFilename=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'NLTK_unus', 'stats')
    filesToOpen.append(outputFilename)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'NLTK unusual words/spelling checker start',
                                       'Started running NLTK unusual words/spelling checker at', True,
                                       '',True,'',True)

    # already shown in NLP.py
    # IO_util.timed_alert(GUI_util.window,2000,'Analysis start','Started running NLTK unusual words at',True,'You can follow NLTK unusual words in command line.')
    for file in files:
        documentID=documentID+1
        head, tail = os.path.split(file)
        print("Processing file " + str(documentID) + "/" + str(nFile) + ' ' + tail)
        text = (open(file, "r", encoding="utf-8", errors="ignore").read())
        #lemmatizer = WordNetLemmatizer()
        # text_vocab = set(lemmatizer.lemmatize(w.lower()) for w in text.split(" ") if w.isalpha())
        text_vocab = set(lemmatizing(w.lower()) for w in text.split(" ") if w.isalpha())
        english_vocab = set([w.lower() for w in nltk.corpus.words.words()])
        print("english_vocab",english_vocab)
        print("text_vocab",text_vocab)
        unusual = text_vocab - english_vocab
        #convert the set to a list
        unusual=list(unusual)
        #sort the list
        unusual.sort()
        # unusual = [[documentID, file, word] for word in unusual]
        unusual = [[documentID, IO_csv_util.dressFilenameForCSVHyperlink(file), word] for word in unusual]
        container.append(unusual)
    container.insert(0, ['Misspelled/unusual word', 'Document ID', 'Document'])
    if len(container)>0:
        if IO_csv_util.list_to_csv(window,container,outputFilename): return
    else:
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Spelling checker (via nltk)', 'No misspelled/unusual words found in\n' + file, True)
        if nFile==1:
            return

    # if not silent: IO_user_interface_util.single_file_output_save(inputDir,'NLTK')

    # NLTK unusual words
    if createCharts:
        if nFile>10:
             result = mb.askyesno("Excel charts","You have " + str(nFile) + " files for which to compute Excel charts.\n\nTHIS WILL TAKE A LONG TIME.\n\nAre you sure you want to do that?")
             if result==False:
                 pass
        columns_to_be_plotted=[[2,2]]
        hover_label=['']
        inputFilename=outputFilename
        chart_outputFilename = charts_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                   outputFileLabel='NLTK_spell',
                                                   chart_type_list=["bar"],
                                                   chart_title='Misspelled/Unusual Words Frequency',
                                                   column_xAxis_label_var='',
                                                   hover_info_column_list=hover_label,
                                                   count_var=1)
        if chart_outputFilename != None:
             filesToOpen.append(chart_outputFilename)

    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
        filesToOpen=[] # do not open twice, hee and calling function
    # already shown in NLP.py
    # IO_util.timed_alert(GUI_util.window,3000,'Analysis end','Finished running NLTK unusual words at',True)
    for u in unusual:
        print(u[-1])

    print(len(unusual))
    return filesToOpen

def generate_simple_csv(Dataframe):
    pass

def createChart(inputFilename,outputDir,columns_to_be_plotted,hover_label):
    chart_outputFilename = charts_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                              outputFileLabel='Leven_spell',
                                              chart_type_list=["pie"],
                                              chart_title='Frequency of Potential Typos',
                                              column_xAxis_label_var='',
                                              hover_info_column_list=hover_label,
                                              count_var=1)
    return chart_outputFilename


# check within subdirectory
def check_for_typo_sub_dir(inputDir, outputDir, openOutputFiles, createCharts, chartPackage, NERs, similarity_value, by_all_tokens_var,spelling_checker_var):
    filesToOpen=[]
    if inputDir=='':
        return
    subdir = [f.path for f in os.scandir(inputDir) if f.is_dir()]
    if subdir == []:
        mb.showwarning(title='Check Subdir option',
                       message='There are no sub directories under the selected input directory\n\n' + inputDir +'\n\nPlease, uncheck your subdir option if you want to process this directory and try again.')
    df_list = []
    for dir in subdir:
        dfs = check_for_typo(inputDir, outputDir, openOutputFiles, createCharts, chartPackage, NERs, similarity_value, by_all_tokens_var)
        df_list.append(dfs)
    if len(df_list) > 0:
        df_complete_list = [df[0] for df in df_list]
        df_simple_list = [df[1] for df in df_list]
        df_complete = pd.concat(df_complete_list, ignore_index=True)
        df_simple = pd.concat(df_simple_list, ignore_index=True)
        df_simple.to_csv(outputFileName_simple, index=False)
        df_complete.to_csv(outputFileName_complete, index=False)

        filesToOpen.append(outputFileName_simple)
        filesToOpen.append(outputFileName_complete)

        if createCharts:
            chart_outputFilename = createChart(outputFileName_simple,outputDir, [[10, 10]], '')
            if chart_outputFilename!="":
                filesToOpen.append(chart_outputFilename)

        if openOutputFiles == True:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
            filesToOpen=[] # empty the list to avoid opening files twice

    return filesToOpen

# the check for typo function
# check whether a single word is considered as typo within a list of words
# design choice for this algorithm:
#   if the word is shorter than user-supplied word length (default 4 characters):
#       1 or more character mistake will be considered as typo should use 1 only for longer words
#   else(the word is longer than or equal to user-supplied word length (default 4 characters):
#       2 or more character mistake will be considered as typo; DEFAULT

# checklist contains words with more than 1 time of appearance
# similarity_value is the gaging_difference attribute
def check_edit_dist(input_word, checklist, similarity_value):
    exist_typo = False
    for word in checklist:
        # TODO see also pyslpellchecker https://pypi.org/project/pyspellchecker/ which is based on
        #   Peter Norvig’s blog post on setting up a simple spell checking algorithm based on Levenshtein's edit distance
        # It uses a Levenshtein Distance
        dist = nltk.edit_distance(input_word, word[0])
        if len(input_word) >= similarity_value:
            if 0 < dist <= 2:
                exist_typo = True
                return exist_typo, word[0], word[1]
        else:
            if 0 < dist <= 1:
                exist_typo = True
                return exist_typo, word[0], word[1]
    return exist_typo, '', ''

# the main checking function, takes input:
#   CoreNLPDirectory, inputDir, output_file_path
# now checking for NE list ['CITY', 'LOCATION', 'PERSON']
# output csv header list: ['NNPs', 'sentenceID', 'DocumentID', 'fileName', 'NamedEntity', 'potential_Typo']

# using Levenshtein distance to check for typos
def check_for_typo(inputDir, outputDir, openOutputFiles, createCharts, chartPackage, NERs, similarity_value, by_all_tokens_var):
    filesToOpen=[]
    all_header_rows_dict = []
    ner_dict = {}

    # check that the CoreNLPdir as been setup
    CoreNLPdir, missing_external_software  = IO_libraries_util.get_external_software_dir('spell_checker_main', 'Stanford CoreNLP')

    if CoreNLPdir == '':
        return

    if by_all_tokens_var:
        pass
    else:
        if NERs[0] == '*':
            NERs = ['CITY', 'LOCATION', 'PERSON', 'COUNTRY', 'STATE_OR_PROVINCE', 'ORGANIZATION']
        else:
            pass
    documents = []
    folderID=0
    fileID=0
    subfolder=[]
    nFiles = nFolders = 0

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Word similarity start', 'Started running Word similarity at',
                                                 True, '', True, '', True)

    # TODO which annotators is it using? We do not need all annotators! Sentence splitter and tokenizer (and NER)
    p = subprocess.Popen(
        ['java', '-mx' + str(5) + "g", '-cp', os.path.join(CoreNLPdir, '*'),
         'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', '-timeout', '999999'])
    time.sleep(5)

    print('Starting to run Stanford CoreNLP to prepare data for each folder and file.')

    for folder, subs, files in os.walk(inputDir):
        nFolders=len(subs)+1
        folderID+=1
        print("\nProcessing folder "+str(folderID)+"/"+str(nFolders)+": "+os.path.basename(os.path.normpath(folder)))
        fileID=0
        for filename in files:
            fileID+=1
            if not filename.endswith('.txt'):
                continue
            print("  Processing file "+str(fileID)+"/"+str(len(files)) + ": " + filename)
            dir_path = os.path.join(folder, filename)
            with open(dir_path, 'r', encoding='utf-8', errors='ignore') as src:
                text = src.read().replace("\n", " ")
                NLP = StanfordCoreNLP('http://localhost', port=9000)
            # sentences = tokenize.sent_tokenize(text)
            sentences = sent_tokenize_stanza(stanzaPipeLine(text))
            documents.append([sentences,filename, dir_path])

    # IO_util.timed_alert(GUI_util.window, 5000, 'Word similarity', 'Finished preparing data...\n\nProcessed '+str(folderID)+' subfolders and '+str(fileID)+' files.\n\nNow running Stanford CoreNLP to get NER values on every file processed... PLEASE, be patient. This may take a while...')

    if by_all_tokens_var:

        # TODO header_rows ends up including filename as well; must only include the words in the documents
        header_rows = [[token, sentence_number + 1, document_number + 1,sentence, document[1],IO_csv_util.dressFilenameForCSVHyperlink(document[2]), '']
                for document_number, document in enumerate(documents)
                for sentence_number, sentence in enumerate(document[0])
                for token in list(set(NLP.word_tokenize(sentence)))]
        temp = [elmt[0] for elmt in header_rows]
        all_header_rows_dict = [(item, count) for item, count in collections.Counter(temp).items() if count > 1]
        header_row_list_to_check = header_rows

    else:

        NER = [[ners[0], sentence_number + 1, document_number + 1, sentence, document[1],IO_csv_util.dressFilenameForCSVHyperlink(document[2]), ners[1]] for document_number, document in
               enumerate(documents)
               for sentence_number, sentence in enumerate(document[0])
               for ners in NLP.ner(sentence) if ners[1] in NERs]
        ner_dict = {}
        for each_ner in NERs:
            temp = [elmt[0] for elmt in NER if elmt[-1] == each_ner]
            ner_dict[each_ner] = [(item, count) for item, count in collections.Counter(temp).items() if count > 1]
        header_row_list_to_check = NER

    # word_list contains all the first element - token - of each row, i.e., a list of all wrods
    word_list = [elmt[0] for elmt in header_row_list_to_check]
    distinct_word_list = set(word_list)
    word_freq_dict = {i: word_list.count(i) for i in set(word_list)}
    # convert word_list to set to obtain a list of DISTINCT words
    # for each element in list_to_check, it is in this format:
    # word, NamedEntity, sentenceID, documentID, fileName

    print('Finished running Stanford CoreNLP to prepare data for folder '+str(folderID)+' and '+str(fileID)+' files.')
    print('   Processed '+str(len(header_row_list_to_check))+' words and '+ str(len(distinct_word_list)) +' DISTINCT words. Now computing spelling and word differences for DISTINCT words...')
    # IO_util.timed_alert(GUI_util.window, 5000, 'Word similarity', 'Finished running Stanford CoreNLP...\n\nProcessed '+str(len(list_to_check))+' words.\n\nNow computing word differences... PLEASE, be patient. This may take a while...')
    # These headers reflect the items returned from the processing above
    # THEIR ORDER CANNOT BE CHANGED, UNLESS ABOVE ORDER OF PROCESSING IS ALSO CHANGED
    # These headers are then used selectively for the output (see headers2)
    headers1 = ['Words', 'Word frequency in document', 'Sentence ID', 'Document ID',
                'Sentence', 'Document', 'Document path', 'Named Entity (NER)',
                'Similar word in directory', 'Similar-word frequency in directory', 'Typo?']
    if by_all_tokens_var:
        # headers 2 rearranges the headers but must have the same values
        headers2=['Words', 'Word frequency in document', 'Similar word in directory',
                 'Similar-word frequency in directory', 'Typo?',
                 'Number of documents processed', 'Sentence ID', 'Sentence',
                 'Document ID', 'Document', 'Document path', 'Processed directory']
        header_rowID=0
        processed_word_list=[]
        processed_wordID=0

        # for header_row in header_row_list_to_check:
        # for header_row in header_row_list_to_check:
        #     header_row.insert(1, word_freq_dict.get(word[0]))
        #     checker_against = all_word_dict
        #     value_tuple = check_edit_dist(word[0], checker_against, similarity_value)
        #     if value_tuple[0]:
        #         header_row.append(value_tuple[1])  # returned similar word from check_edit_list
        #         header_row.append(value_tuple[2])  # returned similar word frequency from check_edit_list
        #         header_row.append('Typo?')
        #     else:
        #         header_row.append('')
        #         header_row.append('')
        #         header_row.append('')

        checker_against = all_header_rows_dict
        for word in distinct_word_list:
            if (word not in processed_word_list) and (word.isalpha()):
                processed_wordID=processed_wordID+1
                speller = SpellChecker()
                respelled_word = speller.correction(word)
                # print("      Processing DISTINCT word " + str(processed_wordID) + "/" + str(len(distinct_word_list)) + " Row " + str(header_rowID) + "/" + str(len(header_row_list_to_check)) + ":" + word)
                print("      Processing DISTINCT word " + str(processed_wordID) + "/" + str(len(distinct_word_list)) + ": " + word)
            else:
                respelled_word = word
            value_tuple=[]
            if respelled_word!=word:
                # should check edit distance only if the word is misspelled
                value_tuple = check_edit_dist(word, checker_against, similarity_value)
            else:
                value_tuple=[False, '', '']
            # TODO need to get specific row(s) from header_row_list_to_check where word = header_row_list_to_check[0] first item in the list (i.e., token)
            header_row = header_row_list_to_check
            if value_tuple[0]:
                header_rowID += 1
                header_row.insert(1, word_freq_dict.get(word))
                header_row.append(value_tuple[1])  # returned similar word from check_edit_list
                header_row.append(value_tuple[2])  # returned similar word frequency from check_edit_list
                header_row.append('Typo?')
            else:
                header_row.append('')
                header_row.append('')
                header_row.append('')
            # print("      Processing word " + str(header_rowID) + "/" + str(len(header_row_list_to_check)) + ":" + word)

            if word not in processed_word_list: processed_word_list.append(word)

    # Processing NER
    else:
        # headers 2 rearranges the headers but must have the same values
        # it includes the NER tag
        headers2=['Words', 'Named Entity (NER)', 'Word frequency in document',
                  'Similar word in directory',
                 'Similar-word frequency in directory', 'Typo?',
                 'Number of documents processed', 'Sentence ID', 'Sentence',
                  'Document ID', 'Document', 'Document path', 'Processed directory']
        for header_row in header_row_list_to_check:
            word=header_row[0]
            header_row.insert(1, word_freq_dict.get(word))
            # [('word', Count:int)]
            for each_ner in NERs:
                if header_row[-1] == each_ner:
                    checker_against = ner_dict.get(each_ner)
                    value_tuple = check_edit_dist(word[0], checker_against, similarity_value)
                    if value_tuple[0]:
                        header_row.append(value_tuple[1])  # returned similar word from check_edit_list
                        header_row.append(value_tuple[2])  # returned similar word frequency from check_edit_list
                        header_row.append('Typo?')
                    else:
                        header_row.append('')
                        header_row.append('')
                        header_row.append('')

    df = pd.DataFrame(header_row_list_to_check, columns=headers1)
    for index, row in df.iterrows():
        if row['Similar-word frequency in directory'] != None:
            tmp = df[df['Words'] == row['Similar word in directory']]
            df.loc[index, 'Number of documents processed'] = tmp.Document.nunique()
    df['Processed directory'] = IO_csv_util.dressFilenameForCSVHyperlink(inputDir)
    df = df[headers2]

    # complete includes all repeats
    df_complete = df[headers2]

    # simple excludes all repeats
    df_simple = df.drop_duplicates(subset=['Words', 'Document ID'], keep='last')

    if by_all_tokens_var:
        outputFileName_complete = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'WordSimil',
                                                                          str(similarity_value), 'Edit_dist_algo',
                                                                          'header_rows', 'Full-table')
        outputFileName_simple = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'WordSimil',
                                                                        str(similarity_value), 'Edit_dist_algo',
                                                                        'header_rows', 'Concise-table')
    else:
        outputFileName_complete = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'WordSimil',
                                                                          str(similarity_value), 'Edit_dist_algo',
                                                                          'NERs', 'Full-table')
        outputFileName_simple = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'WordSimil',
                                                                        str(similarity_value), 'Edit_dist_algo', 'NERs',
                                                                            'Concise-table')
    if len(df_simple) > 0 and len(df_complete) > 0:
            df_simple.to_csv(outputFileName_simple, index=False)
            df_complete.to_csv(outputFileName_complete, index=False)
            filesToOpen.append(outputFileName_simple)
            filesToOpen.append(outputFileName_complete)

            filesToOpen.append(outputFileName_simple)
            filesToOpen.append(outputFileName_complete)

            IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Word similarity end',
                                               'Finished running Word similarity at', True)

            if createCharts:
                chart_outputFilename=createChart(outputFileName_simple, outputDir, [[10, 10]], '')

                if chart_outputFilename != None:
                    filesToOpen.append(chart_outputFilename)

    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
        filesToOpen=[] # empty the list to avoid opening files twice

    p.kill()

    return filesToOpen


def spelling_checker_cleaner(window,inputFilename, inputDir, outputDir, openOutputFiles):
    mb.showwarning(title='Find & Replace csv file (with \'Original\' and \'Corrected\' headers)',
                   message='Please, select the csv file that contains the information about words that need correcting.\n\nMostly likely this file was created by the spell checker algorithms and edited by you keeping only correct entries.\n\nThe Find & Replace will expect 2 column headers \'Original\' and \'Corrected\'.\n\nPlease, make sure that your csv file has those characteristics.')
    # initialdir=initialFolder,
    csv_spelling_file = filedialog.askopenfilename(title='Select INPUT csv spelling file (with \'Original\' and \'Corrected\' headers)', filetypes=[("csv files", "*.csv")]) #https://docs.python.org/3/library/dialog.html
    if csv_spelling_file=='':
        return
    df = pd.read_csv(csv_spelling_file, encoding='utf-8', errors='ignore')
    try:#make sure the csv have two columns of "original" and "corrected"
    	original = df['Original']
    	corrected = df['Corrected']
    except:
    	mb.showwarning(title='CSV file error',
					   message='The selected csv file does not have the expected format. The Find & Replace expects 2 column headers \'Original\' and \'Corrected\'.\n\nPlease, make sure that your csv file has those characteristics and try again.')
    	print(
 			"The selected csv file does not have the expected format. The Find & Replace expects 2 column headers \'Original\' and \'Corrected\'.\n\nPlease, make sure that your csv file has those characteristics and try again.")
    	return
    #preparting the input to the cleaning function: lists of words to replace
    input_original = []
    input_corrected = []
    for i in range(len(original)):
       if (isinstance(corrected[i], str) and corrected[i] != '') or (not math.isnan(corrected[i])):#the correction is neither empyt string, nor NaN, then both original and corrected will be added to the input lists
           input_original.append(original[i])
           input_corrected.append(corrected[i])
    file_cleaner_util.find_replace_string(window,inputFilename, inputDir, outputDir, openOutputFiles,input_original,input_corrected,False)



def spellchecking_autocorrect(text: str, inputFilename) -> (str, DataFrame):
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Autocorrect spelling checker start',
                                       'Started running AUTOCORRECT spelling checker on ' + inputFilename + ' at ', True,
                                       'You can follow Autocorrect spelling checker in command line.')
    original_str_list = []
    new_str_list = []
    speller = Speller()
    # for word in nltk.word_tokenize(text):
    for word in word_tokenize_stanza(stanzaPipeLine(text)):
        if word.isalnum():
            original_str_list.append(word)
            respelled_word = speller(word)
            if respelled_word != word:
                new_str_list.append(respelled_word)
            else:
                new_str_list.append('')
    return speller(text), DataFrame({
        'Original': original_str_list,
        'Corrected': new_str_list
    })


# the library has an indexer problem
# if checkIO_Filename_inputDir ("Spelling checker (via SpellChecker)",inputFilename, "NO input directory required", 'txt'):
#     print("going to spell")
#     outputFilename=IO_util.generate_output_file_name(inputFilename,outputDir,'.csv','Spell')
#     misspelledWordsList=statistics_corpus_util.spellingChecker(GUI_util.window,inputFilename,outputFilename)
#     if len(misspelledWordsList)>0:
#         openOutputFiles=True
#         filesToOpen.append(outputFilename)
#     else:
#         mb.showwarning(title='Spelling checker (via SpellChecker)', message='No misspelled/unusual words found in\n'+inputFilename)
#https://www.tutorialspoint.com/python_text_processing/python_spelling_check.htm
# def spellingChecker(window,inputFilename,outputFilename):
#     print("IN spellingChecker")
#     text = (open(inputFilename, "r", encoding="utf-8", errors="ignore").read())
#     spell = SpellChecker()
#     # SHOULD HAVE THIS FORMAT
#     # misspelled = spell.unknown(['let', 'us', 'wlak','on','the','groun'])
#     # string.punctuation doesn't include non-English punctuation at all
#     # https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string
#     #text=text.translate(str.maketrans('', '', string.punctuation))
#     import re
#     #s = "string. With. Punctuation?"
#     text = re.sub(r'[^\w\s]','',text)
#     arr = text.split(" ")
#     print("len(arr)",len(arr))
#     # misspelled contains the list of misspelled words
#     misspelled = spell.unknown(arr)
#     print("len(misspelled)",len(misspelled))
#     #print ("misspelled",misspelled)
#     for word in misspelled:
#         print("word: ",word)
#         # Get the one `most likely` answer
#         print("correction: ",spell.correction(word))
#         # Get a list of `likely` options
#         print("candidates: ",spell.candidates(word))
#     return misspelled

def spellchecking_pyspellchecker(text: str, inputFilename) -> (str, DataFrame):
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Pyspellchecker spelling checker start',
                                       'Started running PYSPELLCHECKER spelling checker on ' + inputFilename + ' at', True,
                                       'You can follow Pyspellchecker spelling checker in command line.')
    # :: pyspellchecker seems to remove punctuations.
    new_str_list = []
    original_str_list = []
    new_str_list_for_df = []
    treebank = nltk.tokenize.treebank.TreebankWordDetokenizer()
    speller = SpellChecker()
    # for word in nltk.word_tokenize(text):
    for word in word_tokenize_stanza(stanzaPipeLine(text)):
        if word.isalnum():
            original_str_list.append(word)
            respelled_word = speller.correction(word)
            if respelled_word != word:
                new_str_list_for_df.append(respelled_word)
            else:
                new_str_list_for_df.append('')
        new_str_list.append(word)
    return treebank.detokenize(new_str_list), DataFrame({
        'Original': original_str_list,
        'Corrected': new_str_list_for_df
    })


def spellchecking_text_blob(text: str, inputFilename) -> (str, DataFrame):
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Textblob spelling checker start',
                                       'Started running TEXTBLOB spelling checker on ' + inputFilename + ' at', True,
                                       'You can follow Textblob spelling checker in command line.')
    new_str_list = []
    new_str_list_for_df = []
    original_str_list = []
    treebank = nltk.tokenize.treebank.TreebankWordDetokenizer()
    # for word in nltk.word_tokenize(text):
    for word in word_tokenize_stanza(stanzaPipeLine(text)):
        if word.isalnum():
            original_str_list.append(word)
            respelled_word = Word(word).spellcheck()[0][0]
            if respelled_word != word:
                new_str_list_for_df.append(respelled_word)
            else:
                new_str_list_for_df.append('')
        new_str_list.append(word)
    return treebank.detokenize(new_str_list), DataFrame({
        'Original': original_str_list,
        'Corrected': new_str_list_for_df
    })


# not used
# def spellchecking_pytesseract(inputDir,outputDir):
#     misspelled = spell.unknown([word])
#     if misspelled == set():
#         return False,''
#     else:
#         for misspell in misspelled:
#             # Get the one `most likely` answer
#             return True, spell.correction(misspell)

# not used
# def spell_word_pytesseract(word, spell):
#     misspelled = spell.unknown([word])
#     if misspelled == set():
#         return False,''
#     else:
#         for misspell in misspelled:
#             # Get the one `most likely` answer
#             return True, spell.correction(misspell)
#
#     if spelling_checker_var:
#         if 'autocorrect' in checker_package:
#             spell = Speller(lang='en')
#         else:
#             spell = SpellChecker()
#         header_rows = [[token, sentence_number + 1, document_number + 1, sentence, document[1],IO_csv_util.dressFilenameForCSVHyperlink(document[2]) ,''] for document_number, document in
#                      enumerate(documents)
#                      for sentence_number, sentence in enumerate(document[0])
#                      for token in NLP.word_tokenize(sentence)]
#
#         list_to_check = header_rows
#         word_list = [elmt[0] for elmt in list_to_check]
#         word_freq_dict = {i: word_list.count(i) for i in set(word_list)}
#         for word in list_to_check:
#             word.insert(1, word_freq_dict.get(word[0]))
#             if 'pyspellchecker' in checker_package:
#                 value_tuple = spell_word_pytesseract(word[0],spell)
#             else:
#                 return
#             if value_tuple[0]:
#                 word.append(value_tuple[1])  # returned similar word from check_edit_list
#                 word.append(word_freq_dict.get(value_tuple[1],0))  # returned similar word frequency from check_edit_list
#                 word.append('Typo?')
#             else:
#                 word.append('')
#                 word.append('')
#                 word.append('')
#             print(word)

def spellcheck(inputFilename,inputDir, checker_value_var, check_withinDir):
    folderID = 0
    fileID = 0

    autocorrect_df = pd.DataFrame({'Original': [],
                                    'Corrected': [],
                                    "Document ID":[],
                                    "Document": []})

    pyspellchecker_df = autocorrect_df.copy()
    textblob_df = autocorrect_df.copy()

    corrected_files_dir = os.path.join(inputDir, 'spell_checked')
    make_directory(corrected_files_dir)

    if check_withinDir:
        files=IO_files_util.getFileList(inputFilename, inputDir, '.txt')
    else:
        files=IO_files_util.getFileList_SubDir(inputFilename, inputDir, '.txt')
    if len(files) == 0:
        return
    folderID += 1

    # if not check_withinDir:
    #     for folder, subs, files in os.walk(inputDir):
    #         print("\nProcessing folder " + str(folderID) + "/ " + os.path.basename(
    #              os.path.normpath(folder)))

    for filename in files:
        if check_withinDir:
            print("Processing file:", filename)
        # else:
        #     print("  Processing file:", filename)
        fileID = fileID + 1
        # inputFilenames_path = os.path.join(folder, filename)
        # with open(inputFilenames_path, 'r', encoding='utf-8', errors='ignore') as opened_file:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as opened_file:
            print("  Processing file:", filename)
            originalText = opened_file.read()
            path_to_file = os.path.join(inputDir, filename)
            if checker_value_var == '*' or 'autocorrect' in checker_value_var:
                text, csv = spellchecking_autocorrect(originalText,filename)
                csv["Document"] = [IO_csv_util.dressFilenameForCSVHyperlink(filename)] * csv.shape[0]
                csv["Document ID"] = [fileID] * csv.shape[0]
                autocorrect_df = pandas.concat([autocorrect_df, csv], ignore_index=True)
                autocorrect_df = autocorrect_df.drop_duplicates()
                print('AUTOCORRECT\n',text)

            if checker_value_var == '*' or 'pyspellchecker' in checker_value_var:
                text, csv = spellchecking_pyspellchecker(originalText,filename)
                csv["Document"] = [IO_csv_util.dressFilenameForCSVHyperlink(filename)] * csv.shape[0]
                csv["Document ID"] = [fileID] * csv.shape[0]
                pyspellchecker_df = pandas.concat([pyspellchecker_df, csv], ignore_index=True)
                pyspellchecker_df = pyspellchecker_df.drop_duplicates()
                print('PYSPELLCHECKER\n',text)

            if checker_value_var == '*' or 'textblob' in checker_value_var:
                text, csv = spellchecking_text_blob(originalText,filename)
                csv["Document"] = [IO_csv_util.dressFilenameForCSVHyperlink(filename)] * csv.shape[0]
                csv["Document ID"] = [fileID] * csv.shape[0]
                textblob_df = pandas.concat([textblob_df, csv], ignore_index=True)
                textblob_df = textblob_df.drop_duplicates()
                print('TEXTBLOB\n',text)

            head, tail = os.path.split(filename)
            # head is path, tail is filename

            corrected_files_path = os.path.join(corrected_files_dir, tail)
            with open(corrected_files_path, 'w+', encoding='utf-8') as file_to_write:
                file_to_write.write(text)

    IO_user_interface_util.subdirectory_file_output_save(inputDir, corrected_files_path, 'INPUT', 'spell checker')

    mb.showwarning(title='Spell checking',
                   message='Spell checker algorithms are not very accurate, perhaps pyspellchecker perfoming better than autocorrect and textblob performing the worse.\n\nThe spell checkers generate in output\n  1. corrected txt file(s) in a subdirectory \'spell_checked\' of the input file and/or input directory;\n  2. csv files (one for each of the 3 available algorithms if run together) with the headers \'Original\' and \'Corrected\' that list all the words that would have been edited for misspellings in the output files.\n\nPLEASE, CAREFULLY INSPECT THE OUTPUT CSV FILE(S), DELETE ANY WRONGLY CORRECTED WORDS FROM EACH CELL UNDER THE \'Corrected\' COLUMN, THEN, RUN THE \'Find & Replace string (Spelling checker cleaner)\' SCRIPT TO EDIT THE ORIGINAL INPUT FILE(S).')
    return autocorrect_df, pyspellchecker_df, textblob_df


# function implements three different approaches to language detection: langdetect, spacy, langid
# https://towardsdatascience.com/benchmarking-language-detection-for-nlp-8250ea8b67c
# TODO print all languages and their probabilities in a csv file, with Language, Probability, Document ID, Document (with hyperlink)
def language_detection(window, inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage):

    folderID = 0
    fileID = 0
    filesToOpen=[]

    outputFilenameCSV=IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'lang_detect')
    filesToOpen.append(outputFilenameCSV)

    files=IO_files_util.getFileList(inputFilename, inputDir, '.txt')
    if len(files) == 0:
        return

    if IO_csv_util.openCSVOutputFile(outputFilenameCSV):
        return

    fieldnames = ['LANGDETECT',
                  'Language',
                  'Probability',
                  'SPACY',
                  'Language',
                  'Probability',
                  'LANGID',
                  'Language',
                  'Probability',
                  'Document ID',
                  'Document']

    config_filename = 'file_spell_checker_config.csv'
    reminders_util.checkReminder(config_filename,
                                 ['Language detection'],
                                 'Language detection algorithms are very slow. The NLP Suite runs three different types of algorithms: LANGDETECT, SPACY, and LANGID.\n\nPlease, arm yourself with patience, depennding upon the number and size of documents processed.',
                                 True)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                       'Started running language detection algorithms at', True,
                                       'You can follow the algorithms in command line.')

    with open(outputFilenameCSV, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        docErrors_empty=0
        docErrors_unknown=0
        filenameSV=''
        for filename in files:
            fileID = fileID + 1
            head, tail = os.path.split(filename)
            print("Processing file " + str(fileID) + "/" + str(len(files)) + ' ' + tail)
            text = open(filename, 'r', encoding='utf-8', errors='ignore').read()
            if len(text)==0:
                print("  The file is empty. It will be discarded from processing.")
                docErrors_empty=docErrors_empty+1
                continue
            # text = opened_file.read()
            # head, tail = os.path.split(filename)
            # head is path, tail is filename
            try:
                value = detect_langs(text)
            except:
                filenameSV=filename # do not count the same document twice in this and the other algorithms that follow
                docErrors_unknown=docErrors_unknown+1
                print("  Unknown file read error.")
                continue
            value=str(value[0]).split(':')
            language=value[0]
            probability=value[1]
            print('   LANGDETECT', language, probability)
            # print('   LANGDETECT',value[0],value[1])  # [cs:0.7142840957132709, pl:0.14285810606233737, sk:0.14285779665739756]
            currentLine = ['LANGDETECT', language, probability]

            nlp = spacy.load('en_core_web_sm')
            nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)
            try:
                doc = nlp(text)
            except:
                if filename!=filenameSV: # do not count the same document twice in this and the other algorithm that follows
                    docErrors_unknown = docErrors_unknown + 1
                    filenameSV=filename
                print("  Unknown file read error.")
                continue
            value = doc._.language
            language=value['language']
            probability=value['score']
            print('   SPACY', language, probability)  # {'language': 'en', 'score': 0.9999978351575265}
            currentLine.append(['SPACY', language, probability])

            lang_identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
            try:
                value=lang_identifier.classify(text)
            except:
                if filename!=filenameSV:
                    docErrors_unknown = docErrors_unknown + 1
                    filenameSV=filename
                print("  Unknown file read error.")
                continue
            language=value[0]
            probability=value[1]
            print('   LANGID', language, probability)  # ('en', 0.999999999999998)
            print()
            currentLine.append(['LANGID',  language, probability])
            currentLine.append([fileID, IO_csv_util.dressFilenameForCSVHyperlink(filename)])

            writer = csv.writer(csvfile)
            writer.writerows([currentLine])
            filenameSV=filename
    csvfile.close()
    msg=''
    if docErrors_empty==0 and docErrors_unknown==0:
        msg=str(fileID) + ' documents successfully processed for language detection.'
    else:
        if docErrors_empty>0:
            msg=str(fileID) + ' documents processed for language detection.\n  ' + str(docErrors_empty) + ' document(s) found empty.'
        if docErrors_unknown>0:
            if msg!='':
                msg=msg + '\n  ' + str(docErrors_unknown) + ' document(s) read with unknown errors.'
            else:
                msg = str(fileID) + ' documents processed for language detection.\n  ' + \
                      str(docErrors_unknown) + ' document(s) read with unknown errors.'
        mb.showwarning(title='File read errors',
                message=msg+ '\n\nFaulty files are listed in command line/terminal. Please, search for \'File read error\' and inspect each file carefully.')
    filesToOpen.append(outputFilenameCSV)
    if createCharts:
        columns_to_be_plotted=[[1, 1],[4,4],[7,7]]
        chart_title='Frequency of Languages Detected by 3 Algorithms'
        hover_label=['LANGDETECT', 'SPACY', 'LANGID']
        inputFilename = outputFilenameCSV
        chart_outputFilename = charts_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                  outputFileLabel='_bar_chart',
                                                  chart_type_list=["bar"],
                                                  chart_title=chart_title,
                                                  column_xAxis_label_var='Language',
                                                  hover_info_column_list=hover_label,
                                                  count_var=1)
        if chartPackage=='Excel' and chart_outputFilename!='':
            filesToOpen.append(chart_outputFilename)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
