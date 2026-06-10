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
import stanza
import itertools
import numpy as np
from numpy.linalg import norm
import string

import IO_files_util
import IO_user_interface_util
import IO_csv_util
import word2vec_distances_util

_stopwords_cache = None

def _load_stopwords():
    global _stopwords_cache
    if _stopwords_cache is not None:
        return _stopwords_cache
    stopwords_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  '..', 'lib', 'wordLists', 'stopwords.txt')
    try:
        with open(stopwords_path, 'r') as f:
            _stopwords_cache = set(f.read().splitlines())
    except FileNotFoundError:
        print(f"Warning: stopwords file not found at {stopwords_path}")
        _stopwords_cache = set()
    return _stopwords_cache

def run_Gensim_word2vec(inputFilename, inputDir, outputDir, configFileName, openOutputFiles, chartPackage, dataTransformation,
                        remove_stopwords_var, lemmatize_var,
                        keywords_var,
                        compute_distances_var, top_words_var,
                        sg_menu_var, vector_size_var, window_var, min_count_var,
                        vis_menu_var, dim_menu_var):

    filesToOpen = []

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

    # collect all input documents
    all_input_docs = {}
    tail_list = {}
    document = []
    dId = 0

    if len(inputFilename) > 0:
        head, tail = os.path.split(inputFilename)
        if inputFilename.endswith('.txt'):
            with open(inputFilename, 'r', encoding='utf-8', errors='ignore') as file:
                dId += 1
                text = file.read()
                print('Importing single file ' + tail)
                document.append(IO_csv_util.dressFilenameForCSVHyperlink(inputFilename))
                all_input_docs[dId] = text
                tail_list[dId] = tail
    else:
        inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False,
                                                  configFileName=configFileName)
        if len(inputDocs) == 0:
            return filesToOpen

        for doc in inputDocs:
            head, tail = os.path.split(doc)
            if doc.endswith('.txt'):
                with open(os.path.join(inputDir, doc), 'r', encoding='utf-8', errors='ignore') as file:
                    dId += 1
                    text = file.read()
                    print('Importing file ' + str(dId) + '/' + str(len(inputDocs)) + ' ' + tail)
                    document.append(os.path.join(inputDir, doc))
                    all_input_docs[dId] = text
                    tail_list[dId] = tail

    nFile = len(all_input_docs)

    # initialize Stanza pipeline
    if lemmatize_var:
        stanzaPipeLine = stanza.Pipeline(lang='en', processors='tokenize, lemma')
        print('Tokenizing and Lemmatizing...')
    else:
        stanzaPipeLine = stanza.Pipeline(lang='en', processors='tokenize')
        print('Tokenizing...')

    stop_words = _load_stopwords()
    punctuations = set(string.punctuation)

    all_rows = []
    sentences_out = []

    for doc_idx, (doc_id, txt) in enumerate(all_input_docs.items()):
        print('Processing file ' + str(doc_idx+1) + '/' + str(nFile) + ' ' + tail_list[doc_id])
        stanza_doc = stanzaPipeLine(txt)

        doc_hyperlink = IO_csv_util.dressFilenameForCSVHyperlink(document[doc_idx])

        for sent_idx, sent in enumerate(stanza_doc.sentences):
            sent_text = sent.text
            temp_sent_words = []
            for word in sent.words:
                if remove_stopwords_var:
                    if word.text.lower() in stop_words or word.text in punctuations or len(word.text) == 1:
                        continue

                token_word = word.lemma if (lemmatize_var and hasattr(word, 'lemma') and word.lemma) else word.text
                temp_sent_words.append(token_word)

                row = {
                    'ID': word.id,
                    'Word': word.text,
                    'Sentence ID': sent_idx + 1,
                    'Sentence': sent_text,
                    'Document ID': doc_idx + 1,
                    'Document': doc_hyperlink
                }
                if lemmatize_var and hasattr(word, 'lemma') and word.lemma:
                    row['Lemma'] = word.lemma

                all_rows.append(row)

            if temp_sent_words:
                sentences_out.append(temp_sent_words)

    out_df = pd.DataFrame(all_rows)

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

    for v in words:
        if isinstance(v, str):
            word_vector_list.append(word_vectors[v])
            filtered_words[v] = words[v]

    if 'Do not plot' not in vis_menu_var:
        import word2vec_tsne_plot_util
        outputFiles = word2vec_tsne_plot_util.run_word2vec_plot(inputFilename, inputDir, outputDir,
                              np.asarray(word_vector_list),
                              filtered_words,
                              vis_menu_var, dim_menu_var)
        filesToOpen.extend(outputFiles)

    ### build vector csv
    vector_rows = [{'key': v, 'Vector': word_vectors[v]} for v in words if isinstance(v, str)]
    word_vector_df = pd.DataFrame(vector_rows)

    if lemmatize_var:
        word_vector_df.columns = ['Lemma', 'Vector']
        result_df = pd.merge(word_vector_df, out_df, on='Lemma', how='inner')
        result_df = result_df[["Word", "Lemma", "Vector", "Sentence ID", "Sentence", "Document ID", "Document"]]
    else:
        word_vector_df.columns = ['Word', 'Vector']
        result_df = pd.merge(word_vector_df, out_df, on='Word', how='inner')
        result_df = result_df[["Word", "Vector", "Sentence ID", "Sentence", "Document ID", "Document"]]

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                             'Word2Vec_vector_ALL_words')
    result_df.to_csv(outputFilename, encoding='utf-8', index=False)
    filesToOpen.append(outputFilename)

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
