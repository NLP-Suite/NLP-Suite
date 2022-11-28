import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"word2vec_main.py",['os','tkinter', 'gensim', 'spacy', 'stanza', 'plotly'])==False:
    sys.exit(0)


from sys import platform
import os
import tkinter as tk
import pandas as pd
import tkinter.messagebox as mb
import math
import time

import GUI_IO_util
import IO_files_util
import IO_user_interface_util
import IO_csv_util

#Gensim
import gensim
from gensim.models import Word2Vec

# Stanza for tokenization and lemmatization
from Stanza_functions_util import stanzaPipeLine, sent_tokenize_stanza
import stanza

#Visualization
import plotly.express as px
##from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# for calculating the distance
import itertools
import numpy as np
from numpy.linalg import norm

#stopwords and punctuations
import string
fin = open('../lib/wordLists/stopwords.txt', 'r')
stop_words = set(fin.read().splitlines())
punctuations = set(string.punctuation)


def run_Gensim_word2vec(inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage,
                        remove_stopwords_var, lemmatize_var,
                        keywords_var,
                        compute_distances_var, top_words_var,
                        sg_menu_var, vector_size_var, window_var, min_count_var,
                        vis_menu_var, dim_menu_var,
                        word_vector=None):
    # initialize necessary variables
    word = []
    document = []
    tail_list = {}
    all_input_docs = {}
    dId = 0
    numFiles = 1
    filesToOpen = []
    sentences_out = []

    startTime = IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                                   'Started running Gensim Word2Vec at', True)
    # compute only distances if inputFile is csv
    if inputFilename.endswith('csv'):
        # read csv
        w2v_df = pd.read_csv(inputFilename, encoding='utf-8')
        # check if csv file has Vector column
        if 'Vector' in w2v_df.columns:
            w2v_df['Vector'] = w2v_df['Vector'].astype(object)

            # keyword cos similarity
            if keywords_var:
                keyword_df = pd.DataFrame()
                keywords_list = [x.strip() for x in keywords_var.split(',')]
                i = 0
                for a, b in itertools.combinations(keywords_list, 2):
                    try:
                        # only compute similarity score of words that exists in the csv file
                        if a in w2v_df['Word'].values and b in w2v_df['Word'].values:
                            # convert items in Vector into Python list
                            A = w2v_df['Vector'][w2v_df['Word']==a].values[0]
                            B = w2v_df['Vector'][w2v_df['Word']==b].values[0]
                            A = ' '.join(A.strip('][').split(' ')).split()
                            B = ' '.join(B.strip('][').split(' ')).split()
                            A = list(map(float, A))
                            B = list(map(float, B))

                            # calculate cos similarity
                            sim_score = np.dot(A,B)/(norm(A)*norm(B))

                            # write to dataframe
                            keyword_df.at[i, 'Word_1'] = a
                            keyword_df.at[i, 'Word_2'] = b
                            keyword_df.at[i, 'Cosine similarity'] = sim_score
                    except KeyError:
                        i+=1
                        continue
                    i+=1

                # write output file
                keyword_sim_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', f'Word2Vec_'+str(len(keywords_list))+'_Keywords_Cos_Similarity')
                keyword_df.to_csv(keyword_sim_outputFilename, encoding='utf-8', index=False)
                filesToOpen.append(keyword_sim_outputFilename)

            IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                                        'Finished running Gensim Word2Vec at', True, '', True, startTime)
            return filesToOpen

        else:
            mb.showerror(title='csv file error',
            message='The selected csv file does NOT contain Vector column.\n\nPlease, select a different csv file and try again.')

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
        numFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
        if numFiles == 0:
            mb.showerror(title='Number of files error',
                        message='The selected input directory does NOT contain any file of txt type.\n\nPlease, select a different directory and try again.')
        for doc in list(os.listdir(inputDir)):
            head, tail = os.path.split(doc)
            if doc.endswith('.txt'):
                with open(os.path.join(inputDir, doc), 'r', encoding='utf-8', errors='ignore') as file:
                    dId += 1
                    text = file.read()
                    print('Importing file ' + str(dId) + '/' + str(numFiles) + ' ' + tail)
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
        print('Processing file ' + str(doc_idx+1) + '/' + str(numFiles) + ' ' + tail_list[doc_idx+1])
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
    # filter words that is not string and not recognized by vector model
    for v in words:
        if isinstance(v, str):
            word_vector_list.append(word_vectors[v])
            filtered_words[v] = words[v]

    ## visualization
    print('Preparing charts via t-SNE...')

    if vis_menu_var == 'Plot all word vectors':

        if dim_menu_var == '2D':

            tsne = TSNE(n_components=2)
            xys = tsne.fit_transform(word_vector_list)

            xs = xys[:, 0]
            ys = xys[:, 1]
            word = filtered_words.keys()

            tsne_df = pd.DataFrame({'Word': word, 'x': xs, 'y': ys})
            fig = plot_interactive_graph(tsne_df)
            fig_words = plot_interactive_graph_words(tsne_df)

        else:

            tsne = TSNE(n_components=3)
            xyzs = tsne.fit_transform(word_vector_list)
            xs = xyzs[:, 0]
            ys = xyzs[:, 1]
            zs = xyzs[:, 2]
            word = filtered_words.keys()

            tsne_df = pd.DataFrame({'Word': word, 'x': xs, 'y': ys, 'z': zs})
            fig = plot_interactive_3D_graph(tsne_df)
            fig_words = plot_interactive_3D_graph_words(tsne_df)

    else:

        keywords_list = [x.strip() for x in keywords_var.split(',')]
        result_word = []

        for keyword in keywords_list:
            try:
                sim_words = model.wv.most_similar(keyword, topn=30)
            except:
                IO_user_interface_util.timed_alert(GUI_util.window, 1000, 'Keyword',
                                                   '"' + keyword + '" keyword not in the corpus. Keyword skipped...')
                continue
            sim_words = append_list(sim_words, keyword)
            result_word.append(sim_words)
        if len(result_word)==0:
            mb.showwarning(title="No words found",message="None of the keywords entered were found in the corpus.\n\nRoutine aborted.")
            return

        # assort similar words into lists
        similar_word = []
        similarity = []
        labels = []
        for item_list in result_word:
            for item in item_list:
                similar_word.append(item[0])
                similarity.append(item[1])
                labels.append(item[2])

        sim_word_vector_list = [word_vectors[sw] for sw in similar_word]

        if dim_menu_var == '2D':

            tsne = TSNE(n_components=2, perplexity=30)
            xys = tsne.fit_transform(sim_word_vector_list)
            xs = xys[:, 0]
            ys = xys[:, 1]

            print(similar_word)

            tsne_df = pd.DataFrame({'Word': similar_word, 'x': xs, 'y': ys, 'similarity': similarity, 'label': labels})
            fig = plot_similar_graph(tsne_df)
            fig_words = 'none'

        else:

            tsne = TSNE(n_components=3, perplexity=30)
            xyzs = tsne.fit_transform(sim_word_vector_list)
            xs = xyzs[:, 0]
            ys = xyzs[:, 1]
            zs = xyzs[:, 2]

            print(similar_word)

            tsne_df = pd.DataFrame({'Word': similar_word, 'x': xs, 'y': ys, 'z': zs, 'similarity': similarity, 'label': labels})
            fig = plot_similar_3D_graph(tsne_df)
            fig_words = 'none'


    ## saving output
    print('Saving csv vector file and html graph output for top ' + str(top_words_var) + ' of ' + str(len(words)) + ' distinct words...')
    ### write output html graph

    if not fig_words == 'none':
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '_words.html', 'Word2Vec_vector_ALL_words')
        fig_words.write_html(outputFilename)
        filesToOpen.append(outputFilename)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.html', 'Word2Vec_vector_ALL_words')

    fig.write_html(outputFilename)
    filesToOpen.append(outputFilename)

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
    outputFilename = outputFilename.replace(".html", ".csv")
    result_df.to_csv(outputFilename, encoding='utf-8', index=False)

    filesToOpen.append(outputFilename)

    # compute word distances
    if compute_distances_var:
        print('\nStarted computing word distances between top ' + str(top_words_var) + ' words of ' + str(len(words)) + ' distinct words at ' + str(time.time))
        # find user-selected top most-frequent words
        # word vectors
        tmp_result = result_df['Word'].value_counts().index.tolist()[:top_words_var]
        tmp_result_df = result_df.loc[result_df['Word'].isin(tmp_result)]
        tmp_result_df.drop_duplicates(subset=['Word'], keep='first', inplace=True)
        tmp_result_df = tmp_result_df.reset_index(drop=True)

        # TSNE x,y (z) coordinates
        tmp_tsne = tsne_df['Word'].value_counts().index.tolist()[:top_words_var]
        tmp_tsne_df = tsne_df.loc[tsne_df['Word'].isin(tmp_tsne)]
        tmp_tsne_df.drop_duplicates(subset=['Word'], keep='first', inplace=True)
        tmp_tsne_df = tmp_tsne_df.reset_index(drop=True)

        # calculate cos similarity
        cos_sim_df = pd.DataFrame()
        cos_idx = 0
        print('\nStarted computing cosine similarity between top ' + str(top_words_var) + ' words of ' + str(len(words)) + ' distinct words at ' + str(time.time))
        for i, row in tmp_result_df.iterrows():
            j = len(tmp_result_df)-1
            while i < j:
                try:
                    sim_score = word_vectors.similarity(str(row['Word']), str(tmp_result_df.at[j, 'Word']))
                    cos_sim_df.at[cos_idx, 'Word_1'] = row['Word']
                    cos_sim_df.at[cos_idx, 'Word_2'] = tmp_result_df.at[j, 'Word']
                    cos_sim_df.at[cos_idx, 'Cosine similarity'] = sim_score
                except KeyError:
                    cos_idx+=1
                    j-=1
                    continue
                cos_idx+=1
                j-=1

        # calculate 2-dimensional Euclidean distance
        # TSNE x,y (z) coordinates
        tsne_dist_df = pd.DataFrame()
        dist_idx = 0
        print('\nStarted computing t-SNE 2-dimensional Euclidean distance between top ' + str(top_words_var) + ' words of ' + str(len(words)) + ' distinct words at ' + str(time.time))
        for i, row in tmp_tsne_df.iterrows():
            j = len(tmp_tsne_df)-1
            while i < j:
                tsne_dist_df.at[dist_idx, 'Word_1'] = row['Word']
                tsne_dist_df.at[dist_idx, 'Word_2'] = tmp_tsne_df.at[j, 'Word']
                if 'z' not in tmp_tsne_df.columns:
                    tsne_dist_df.at[dist_idx, '2-dimensional Euclidean distance'] = euclidean_dist( [row['x'],row['y']], [tmp_tsne_df.at[j, 'x'],tmp_tsne_df.at[j, 'y']] )
                else:
                    tsne_dist_df.at[dist_idx, '2-dimensional Euclidean distance'] = euclidean_dist( [row['x'],row['y'],row['z']], [tmp_tsne_df.at[j, 'x'],tmp_tsne_df.at[j, 'y'],tmp_tsne_df.at[j, 'z']] )
                dist_idx+=1
                j-=1

        # vectors of top 10 freq words n-dimensional Euclidean distance
        dist_df = pd.DataFrame()
        dist_idx = 0
        print('\nStarted computing n-dimensional Euclidean distance between top ' + str(top_words_var) + ' words of ' + str(len(words)) + ' distinct words at ' + str(time.time))
        for i, row in tmp_result_df.iterrows():
            j = len(tmp_result_df)-1
            while i < j:
                dist_df.at[dist_idx, 'Word_1'] = row['Word']
                dist_df.at[dist_idx, 'Word_2'] = tmp_result_df.at[j, 'Word']
                dist_df.at[dist_idx, 'n-dimensional Euclidean distance'] = euclidean_dist(row['Vector'], tmp_result_df.at[j, 'Vector'])
                dist_idx+=1
                j-=1

        # create outputFilenames and save them
        cos_sim_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'Word2Vec_top_' + str(top_words_var)+'_Cos_Similarity')
        tsne_dist_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'Word2Vec_top_' + str(top_words_var)+'_TSNE_dist')
        dist_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'Word2Vec_top_' + str(top_words_var)+'_Euclidean_dist')

        dist_df.to_csv(dist_outputFilename, encoding='utf-8', index=False)
        tsne_dist_df.to_csv(tsne_dist_outputFilename, encoding='utf-8', index=False)
        cos_sim_df.to_csv(cos_sim_outputFilename, encoding='utf-8', index=False)

        filesToOpen.append(dist_outputFilename)
        filesToOpen.append(tsne_dist_outputFilename)
        filesToOpen.append(cos_sim_outputFilename)

    # keyword cos similarity
    if keywords_var:
        keyword_df = pd.DataFrame()
        keywords_list = [x.strip() for x in keywords_var.split(',')]
        print('\nStarted computing cosine similarity between words for ' + str(len(keywords_list)) + ' selected keywords at ' + str(time.time))
        i = 0
        for a, b in itertools.combinations(keywords_list, 2):
            try:
                sim_score = word_vectors.similarity(a, b)
                keyword_df.at[i, 'Word_1'] = a
                keyword_df.at[i, 'Word_2'] = b
                keyword_df.at[i, 'Cosine similarity'] = sim_score
            except KeyError:
                i+=1
                continue
            i+=1
        keyword_sim_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                             f'Word2Vec_' + str(
                                                                                 len(keywords_list)) + '_Keywords_Cos_Similarity')
        keyword_df.to_csv(keyword_sim_outputFilename, encoding='utf-8', index=False)
        filesToOpen.append(keyword_sim_outputFilename)

    # # write csv file
    # outputFilename = outputFilename.replace(".html", ".csv")
    # result_df.to_csv(outputFilename, encoding='utf-8', index=False)
    #
    # filesToOpen.append(outputFilename)

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

def plot_interactive_graph(tsne_df):
    fig = px.scatter(tsne_df, x = "x", y = "y",
                     hover_name = "Word")
    return fig

def plot_interactive_graph_words(tsne_df):
    fig = px.scatter(tsne_df, x = "x", y = "y",
                     text = "Word",
                     hover_name = "Word")
    return fig

def plot_interactive_3D_graph(tsne_df):
    fig = px.scatter_3d(tsne_df, x = "x", y = "y", z="z",
                     hover_name = "Word")
    return fig

def plot_interactive_3D_graph_words(tsne_df):
    fig = px.scatter_3d(tsne_df, x = "x", y = "y", z="z",
                     text = "Word",
                     hover_name = "Word")
    return fig

def append_list(sim_words, words):
    list_of_words = []

    for i in range(len(sim_words)):
        sim_words_list = list(sim_words[i])
        sim_words_list.append(words)
        sim_words_tuple = tuple(sim_words_list)
        list_of_words.append(sim_words_tuple)

    return list_of_words

def plot_similar_graph(tsne_df):
    fig = px.scatter(tsne_df, x = "x", y = "y",
                     text = "Word",
                     color = "label",
                     size = "similarity",
                     hover_name = "Word")
    return fig

def plot_similar_3D_graph(tsne_df):
    fig = px.scatter_3d(tsne_df, x = "x", y = "y", z = "z",
                     color = "label",
                     size = "similarity",
                     hover_name = "Word")
    return fig

