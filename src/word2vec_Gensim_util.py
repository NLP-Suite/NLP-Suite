import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"word2vec_main.py",['os','tkinter', 'pandas', 'gensim', 'stanza', 'itertools', 'numpy', 'string'])==False:
    sys.exit(0)

import os
import pandas as pd
import tkinter.messagebox as mb
import math
#Gensim
import gensim
from gensim.models import Word2Vec
# Stanza for tokenization and lemmatization
# from Stanza_functions_util import stanzaPipeLine, sent_tokenize_stanza
import stanza
# for calculating the distance
import itertools
import numpy as np
from numpy.linalg import norm
#stopwords and punctuations
import string

import IO_files_util
import IO_user_interface_util
import IO_csv_util
import word2vec_distances_util

fin = open('../lib/wordLists/stopwords.txt', 'r')
stop_words = set(fin.read().splitlines())
punctuations = set(string.punctuation)

def run_Gensim_word2vec(inputFilename, inputDir, outputDir, configFileName, openOutputFiles, chartPackage, dataTransformation,
                        remove_stopwords_var, lemmatize_var,
                        keywords_var,
                        compute_distances_var, top_words_var,
                        sg_menu_var, vector_size_var, window_var, min_count_var,
                        vis_menu_var, dim_menu_var):

    # initialize necessary variables
    word = []
    document = []
    tail_list = {}
    all_input_docs = {}
    dId = 0
    nFile = 1
    filesToOpen = []
    sentences_out = []

    startTime = IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                                   'Started running Gensim Word2Vec at', True)

    import IO_internet_util
    if not IO_internet_util.check_internet_availability_warning("Word2Vec_Gensim_util.py"):
        return

    # compute only distances if inputFile is csv
    if inputFilename.endswith('csv'):
        word_vectors=None
        result_df=None
        outputFiles = word2vec_distances_util.compute_word2vec_distances(inputFilename, inputDir, outputDir, chartPackage, dataTransformation,
                                   word_vectors,
                                   result_df,
                                   keywords_var,
                                   compute_distances_var, top_words_var)
        filesToOpen.extend(outputFiles)
        return filesToOpen

    # process inputFile/inputDir
    if len(inputFilename)>0:
        doc = inputFilename
        head, tail = os.path.split(doc)
        if doc.endswith('.txt'):
            with open(doc, 'r', encoding='utf-8', errors='ignore') as file:
                dId += 1
                text = file.read()
                print('Importing single file ' + tail)
                document.append(IO_csv_util.dressFilenameForCSVHyperlink(os.path.join(inputDir, doc)))
                all_input_docs[dId] = text
                tail_list[dId] = tail
    else:
        # numFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
        # if numFiles == 0:
        #     mb.showerror(title='Number of files error',
        #                 message='The selected input directory does NOT contain any file of txt type.\n\nPlease, select a different directory and try again.')
        inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False,
                                                  configFileName=configFileName)
        nFile = len(inputDocs)
        if nFile == 0:
            return filesToOpen

        for doc in inputDocs: # list(os.listdir(inputDir)):
            head, tail = os.path.split(doc)
            if doc.endswith('.txt'):
                with open(os.path.join(inputDir, doc), 'r', encoding='utf-8', errors='ignore') as file:
                    dId += 1
                    text = file.read()
                    print('Importing file ' + str(dId) + '/' + str(nFile) + ' ' + tail)
                    document.append(os.path.join(inputDir, doc))
                    all_input_docs[dId] = text
                    tail_list[dId] = tail

    # initialize different annotators for Stanza
    if lemmatize_var:
        stanzaPipeLine = stanza.Pipeline(lang='en', processors= 'tokenize, lemma')
        print('Tokenizing and Lemmatizing...')
    else:
        stanzaPipeLine = stanza.Pipeline(lang='en', processors= 'tokenize')
        print('Tokenizing...')

    # process input file(s)
    out_df = pd.DataFrame()
    for doc_idx, txt in enumerate(all_input_docs.items()):
        print('Processing file ' + str(doc_idx+1) + '/' + str(nFile) + ' ' + tail_list[doc_idx+1])
        temp_out_df = pd.DataFrame()
        stanza_doc = stanzaPipeLine(txt[1])

        # convert stanza doc variable to python dict
        dicts = stanza_doc.to_dict()
        for i in range(len(dicts)):
            temp_df = pd.DataFrame.from_dict(dicts[i])
            temp_out_df = pd.concat([temp_out_df, temp_df], ignore_index=True)

        # drop and rename columns + reset indices
        temp_out_df = temp_out_df.drop(['start_char', 'end_char'], axis=1, errors='ignore')
        temp_out_df = temp_out_df.reset_index(drop=True)
        temp_out_df = temp_out_df.rename(columns = {'id':'ID', 'text':'Word', 'lemma':'Lemma', 'head':'Head'})
        sentences = [sent.text for sent in stanza_doc.sentences]

        # remove rows that include stop words from the dataframe
        if remove_stopwords_var:
            for idx, row in temp_out_df.iterrows():
                if row['Word'].lower() in stop_words or row['Word'] in punctuations or len(row['Word'])==1:
                    temp_out_df.drop(idx, inplace=True)

        # get sentenece, sentenceID for result_df
        # get sentences_out for gensim
        sidx = 1
        temp_sentences_out = []
        for i, row in temp_out_df.iterrows():
            if i != 0 and row['ID'] == 1:
                sidx+=1
                sentences_out.append(temp_sentences_out)
                temp_sentences_out = []
            temp_out_df.at[i, 'Sentence ID'] = sidx
            temp_out_df.at[i, 'Sentence'] = sentences[sidx-1]
            if lemmatize_var:
                temp_sentences_out.append(temp_out_df.at[i, 'Lemma'])
            else:
                temp_sentences_out.append(temp_out_df.at[i, 'Word'])
        temp_out_df['Document ID'] = doc_idx+1
        temp_out_df['Document'] = IO_csv_util.dressFilenameForCSVHyperlink(document[doc_idx])

        # concat to output df
        out_df = pd.concat([out_df,temp_out_df], ignore_index=True)

    if sg_menu_var == 'CBOW':
        sg_var = 0
    else:
        sg_var = 1

    print('Learning architecture: ', sg_menu_var)

    ## train model
    print('Training Word2Vec model...')
    model = gensim.models.Word2Vec(
        sentences=sentences_out,
        sg = sg_var,
        vector_size=vector_size_var,
        window=window_var,
        min_count=min_count_var
    )

    word_vectors = model.wv
    words = word_vectors.key_to_index
    word_vector_list = []
    filtered_words = {}
    tsne_df=None

    # filter words that is not string and not recognized by vector model
    for v in words:
        if isinstance(v, str):
            word_vector_list.append(word_vectors[v])
            filtered_words[v] = words[v]

    if not 'Do not plot' in vis_menu_var:
        create_plots=True
    else:
        create_plots=False

    if create_plots:
        ## visualization
        import word2vec_tsne_plot_util
        outputFiles = word2vec_tsne_plot_util.run_word2vec_plot(inputFilename, inputDir, outputDir,
                              np.asarray(word_vector_list),
                              filtered_words,
                              vis_menu_var, dim_menu_var)
        filesToOpen.extend(outputFiles)

    ### csv file
    word_vector_df = pd.DataFrame()
    for v in words:
        if isinstance(v, str):
            # word_vector_df = word_vector_df.append(pd.Series([v, word_vectors[v]]), ignore_index=True)
            word_vector_df = pd.concat([word_vector_df, pd.Series([v, word_vectors[v]]).to_frame().T], ignore_index=True)

    # merge out_df with word_vector coordinates values
    if lemmatize_var:
        word_vector_df.columns = ['Lemma', 'Vector']
        # word_vector_df = word_vector_df.astype(str)
        result_df = pd.merge(word_vector_df, out_df, on='Lemma', how='inner')
        result_df = result_df[["Word", "Lemma", "Vector", "Sentence ID", "Sentence", "Document ID", "Document"]]
    else:
        word_vector_df.columns = ['Word', 'Vector']
        # word_vector_df = word_vector_df.astype(str)
        result_df = pd.merge(word_vector_df, out_df, on='Word', how='inner')
        result_df = result_df[["Word", "Vector", "Sentence ID", "Sentence", "Document ID", "Document"]]

    # write csv file
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                             'Word2Vec_vector_ALL_words')
    result_df.to_csv(outputFilename, encoding='utf-8', index=False)

    filesToOpen.append(outputFilename)

    # compute word distances
    if compute_distances_var:
        outputFiles = word2vec_distances_util.compute_word2vec_distances(inputFilename, inputDir, outputDir, chartPackage, dataTransformation,
                                   word_vectors,
                                   result_df,
                                   keywords_var,
                                   compute_distances_var, top_words_var)

        filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                                       'Finished running Gensim Word2Vec at', True, '', True, startTime)

    return filesToOpen

###########################################
# functions

# calculate Euclidean distance of vectors (different from x,y coordinates)
def euclidean_dist(x, y):
    return math.sqrt(sum((p1 - p2)**2 for p1, p2 in zip(x,y)))

def make_words(sent):
    words = list(sent_to_words(sent))
    return words

def sent_to_words(sent):
    return (gensim.utils.simple_preprocess(sent, deacc=True))

def make_sentences(all_input_docs):
    from Stanza_functions_util import stanzaPipeLine, sent_tokenize_stanza
    all_txt = []
    for doc in all_input_docs:
        # sentences = sent_tokenize(doc)
        sentences = sent_tokenize_stanza(stanzaPipeLine(doc))
        sentences = [list(sent_to_words(sent)) for sent in sentences]
        all_txt += sentences
    return all_txt

def remove_stopwords(sentences):
    for sentence in sentences:
        yield [s for s in sentence if s not in stop_words]

def remove_stopwords_df(sentence_df):
    for idx, row in sentence_df.iterrows():
        if row['Word'] in stop_words:
            sentence_df.drop(idx, inplace=True)
    return sentence_df

# def plot_interactive_graph(tsne_df):
#     fig = px.scatter(tsne_df, x = "x", y = "y",
#                      hover_name = "Word")
#     return fig
#
# def plot_interactive_graph_words(tsne_df):
#     fig = px.scatter(tsne_df, x = "x", y = "y",
#                      text = "Word",
#                      hover_name = "Word")
#     return fig
#
# def plot_interactive_3D_graph(tsne_df):
#     fig = px.scatter_3d(tsne_df, x = "x", y = "y", z="z",
#                      hover_name = "Word")
#     return fig

# def plot_interactive_3D_graph_words(tsne_df):
#     fig = px.scatter_3d(tsne_df, x = "x", y = "y", z="z",
#                      text = "Word",
#                      hover_name = "Word")
#     return fig
#
def append_list(sim_words, words):
    list_of_words = []

    for i in range(len(sim_words)):
        sim_words_list = list(sim_words[i])
        sim_words_list.append(words)
        sim_words_tuple = tuple(sim_words_list)
        list_of_words.append(sim_words_tuple)

    return list_of_words

# def plot_similar_graph(tsne_df):
#     fig = px.scatter(tsne_df, x = "x", y = "y",
#                      text = "Word",
#                      color = "label",
#                      size = "similarity",
#                      hover_name = "Word")
#     return fig
#
# def plot_similar_3D_graph(tsne_df):
#     fig = px.scatter_3d(tsne_df, x = "x", y = "y", z = "z",
#                      color = "label",
#                      size = "similarity",
#                      hover_name = "Word")
#     return fig
#
