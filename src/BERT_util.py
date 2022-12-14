# import statements
import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "BERT_util",
                                          ['os', 'transformers', 'csv', 'argparse', 'tkinter', 'time', 'stanza',
                                           'summarizer','sacremoses','contextualSpellCheck','sentencepiece','sentence_transformers', 'tensorflow']) == False:
    sys.exit(0)


from regex import R
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import BertTokenizerFast, EncoderDecoderModel
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import pandas as pd
import re
import math
from collections import Counter
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv
import time
import itertools
import stanza
import argparse
import tkinter.messagebox as mb
from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza
import torch
import spacy
import contextualSpellCheck
# Visualization
import plotly.express as px
##from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from summarizer import Summarizer


import IO_csv_util
import IO_files_util
import charts_util
import statistics_txt_util
import word2vec_tsne_plot_util
import IO_user_interface_util
import word2vec_distances_util

# Provides NER tags per sentence for every doc and stores in a csv file
def NER_tags_BERT(window, inputFilename, inputDir, outputDir, mode, createCharts, chartPackage):
    tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-large-finetuned-conll03-english")
    model = AutoModelForTokenClassification.from_pretrained("xlm-roberta-large-finetuned-conll03-english")

    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')

    Ndocs = str(len(inputDocs))

    result = []


    documentID = 0
    for doc in inputDocs:
        head, tail = os.path.split(doc)
        documentID = documentID + 1
        print("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)

        header = ["Word", "NER", "Sentence ID", "Sentence", "Document ID", "Document"]
        with open(doc, "r", encoding="utf-8", errors="ignore") as f:
            fullText = f.read()
            fullText = fullText.replace('\n', ' ')

        sentences = sent_tokenize_stanza(stanzaPipeLine(fullText))
        sentenceID = 0

        for s in sentences:
            sentenceID = sentenceID + 1
            #this model does not use BIEOS
            #aggregation_strategy="simple" ensures that multi word entities are looked at as one entity and instead of being tagged as B-LOC and I-LOC spearately, they are just tagged as LOC together
            nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
            ner_result = nlp(s)

            for el in ner_result:
                result.append([el['word'], el['entity_group'], sentenceID, s, documentID,IO_csv_util.dressFilenameForCSVHyperlink(doc)])

    result.insert(0, header)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                              'NER_BERT')
    IO_error = IO_csv_util.list_to_csv(window, result, outputFilename)

    if not IO_error:
        # chart_outputFilename = parsers_annotators_visualization_util.parsers_annotators_visualization(
        #     config_filename, inputFilename, inputDir, outputDir,
        #     outputFilename, annotator_params, kwargs, createCharts,
        #     chartPackage)
        # if chart_outputFilename != None:
        #     if len(chart_outputFilename) > 0:
        #         filesToOpen.extend(chart_outputFilename)

        return outputFilename


# provides summary of text per doc and stores in a csv file
def doc_summary_BERT(window, inputFilename, inputDir, outputDir, mode, createCharts, chartPackage):


    result_summary_list = []

    header = ["Document Name", "Summary", "Document ID", "Document"]

    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')

    Ndocs = str(len(inputDocs))

    documentID = 0
    for doc in inputDocs:
        head, tail = os.path.split(doc)
        documentID = documentID + 1
        print("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)

        with open(doc, "r", encoding="utf-8", errors="ignore") as f:
            fullText = f.read()
            fullText = fullText.replace('\n', ' ')

        bert_model = Summarizer()
        bert_summary = ''.join(bert_model(fullText, min_length=60))

        result_summary_list.append(
            [inputFilename, bert_summary, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])

    result_summary_list.insert(0, header)

    tempOutputFiles = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                              'Doc_Summary_BERT')
    IO_error = IO_csv_util.list_to_csv(window, result_summary_list, tempOutputFiles)
    if not IO_error:
        return tempOutputFiles
    return tempOutputFiles

# Creates a list of vectors/word embeddings for input files and subsequently plots them on a 2d graph
def word_embeddings_BERT(window, inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage, vis_menu_var, dim_menu_var, compute_distances_var, top_words_var, keywords_var, lemmatize_var, remove_stopwords_var):
    model = SentenceTransformer('sentence-transformers/all-distilroberta-v1')
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    filesToOpen = []
    Ndocs = str(len(inputDocs))
    header = ["Word", "Vector", "Sentence ID", "Sentence", "Document ID", "Document"]
    csv_result = []
    result = []
    documentID = 0
    all_words = []
    words_to_embed = []
    word_embeddings = {}
    tsne_df=None

    bad_chars = [';', ':', '', "*", "\"", "\'", "“", "”", "—", "’s", "n’t"]
    startTime = IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                                   'Started running BERT word embeddings at', True)


    if inputFilename.endswith('csv'):
        word_vectors=None
        result_df=None
        outputFiles = word2vec_distances_util.compute_word2vec_distances(inputFilename, inputDir, outputDir, createCharts, chartPackage,
                                   word_vectors,
                                   result_df,
                                   keywords_var,
                                   compute_distances_var, top_words_var)
        filesToOpen.extend(outputFiles)
        return filesToOpen



    # TODO Naman notice how Word2Vec_Gensim_util has the option of using a .csv file of already computed vectors
    #   so that you can simply use this file to visualize different cosine similarities or
    #   compute distances if you had not previously done so
    # compute only distances if inputFile is csv
    # if inputFilename.endswith('csv'):
    #DONE

    # TODO Naman notice how Word2Vec_main has the option of lemmatzing
    #   this needs to be implemented similarly to Word2Vec_Gensim_util
    #DONE
    if lemmatize_var:
        stanzaPipeLine = stanza.Pipeline(lang='en', processors= 'tokenize, lemma')
        print('Tokenizing and Lemmatizing...')
    else:
        stanzaPipeLine = stanza.Pipeline(lang='en', processors= 'tokenize')
        print('Tokenizing...')

    for doc in inputDocs:
        head, tail = os.path.split(doc)
        documentID = documentID + 1
        print("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)

        with open(doc, "r", encoding="utf-8", errors="ignore") as f:
            fullText = f.read()
            fullText = fullText.replace('\n', ' ')


        #Splitting into sentences here so we can print out the sentence that the word is used in, in order to see the context

        sentences = split_into_sentences(fullText)
        for s in sentences:

             #add all the words from the docs into a list
            all_words.extend(word_tokenize_stanza(stanzaPipeLine(s)))

    #remove stop words from all_words list if that option has been selected in the GUI
    if remove_stopwords_var:
        words_to_embed = statistics_txt_util.excludeStopWords_list(all_words)
    else:
        words_to_embed = all_words

    print(f'\nStarted running BERT Word2Vec model on {len(words_to_embed)} words at {time.asctime( time.localtime(time.time()))}')
    #Creates the word embeddings per word and stores each embedding as an element in a list called embeddings
    word_vectors = model.encode(words_to_embed)

    # print('\nFinished running BERT computing the vector space for ' + str(len(words)) + ' distinct words in the input file(s) at ' + time.asctime( time.localtime(time.time())))

    #Creates key-value pairs of words and their corresponding vectors to be added to csv file output
    # showing words and their corresponding multidimensional vectors
    for w, e in zip(words_to_embed, word_vectors):
        word_embeddings[w] = e

    print(f'\nFinished running BERT Word2Vec model exporting {len(word_embeddings)} non-distinct words at {time.asctime( time.localtime(time.time()))}')

    # Plotting the word embeddings
     ## visualization
    if not 'Do not plot' in vis_menu_var:
        print(f'\nStarted preparing charts via t-SNE for {len(word_embeddings)} non-distinct words at {time.asctime( time.localtime(time.time()))}')
        if dim_menu_var == '2D':
            tsne = TSNE(n_components=2)
            xys = tsne.fit_transform(word_vectors)
            xs = xys[:, 0]
            ys = xys[:, 1]
            tsne_df = pd.DataFrame({'Word': words_to_embed, 'x': xs, 'y': ys})

            fig = word2vec_tsne_plot_util.plot_interactive_graph(tsne_df)
            fig_words = word2vec_tsne_plot_util.plot_interactive_graph_words(tsne_df)


        else:
            tsne = TSNE(n_components=3)
            xyzs = tsne.fit_transform(word_vectors)
            xs = xyzs[:, 0]
            ys = xyzs[:, 1]
            zs = xyzs[:, 2]
            tsne_df = pd.DataFrame({'Word': words_to_embed, 'x': xs, 'y': ys, 'z': zs})

            fig = word2vec_tsne_plot_util.plot_interactive_3D_graph(tsne_df)
            fig_words = word2vec_tsne_plot_util.plot_interactive_3D_graph_words(tsne_df)

        print(f'\nSaving csv vector file and html graph output for top {top_words_var} of {len(word_embeddings)} non-distinct words at {time.asctime( time.localtime(time.time()))}')

        ### write output html graph
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.html',
                                                                     'Word2Vec_vector_ALL_words')
        if not fig_words == 'none':
            outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '_words.html', 'Word2Vec_vector_ALL_words')
            fig_words.write_html(outputFilename)
            filesToOpen.append(outputFilename)
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.html', 'Word2Vec_vector_ALL_words')
        dist_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'Word2Vec_top_' + str(top_words_var)+'_Euclidean_dist')
        fig.write_html(outputFilename)
        filesToOpen.append(outputFilename)

    print(f'\nStarted preparing the csv vector file at {time.asctime( time.localtime(time.time()))}')

    documentID = 0
    for doc in inputDocs:
        head, tail = os.path.split(doc)
        documentID = documentID + 1

        with open(doc, "r", encoding="utf-8", errors="ignore") as f:
            fullText = f.read()
            fullText = fullText.replace('\n', ' ')

        sentenceID = 0

        #Will add every relevant sentence s to our csv output file, so we have to loop through them here
        for s in sentences:
            sentenceID = sentenceID + 1

            #need to tokenize each sentence again here so that the words we add and check for a sentence are actually words from
            # that sentence only, and not one that comes later
            words = word_tokenize_stanza(stanzaPipeLine(s))

            if remove_stopwords_var:
                words = statistics_txt_util.excludeStopWords_list(words)

            if dim_menu_var == '2D':
                #Adding rows to our output for the csv file with words, their vectors, and the sentences they are found in
                for w in words:
                    csv_result.append([w, word_embeddings[w], sentenceID, s, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])
            else:
                for w in words:
                    csv_result.append([w, word_embeddings[w], sentenceID, s, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])

    print(f'\nSaving csv vector file for top {top_words_var} of {len(words)} non-distinct words at {time.asctime( time.localtime(time.time()))}')

    result_df = pd.DataFrame(csv_result, columns=header)

    # write csv file
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                             'Word2Vec_vector_ALL_words')
    result_df.to_csv(outputFilename, encoding='utf-8', index=False)

    filesToOpen.append(outputFilename)

      # compute distances
    if compute_distances_var:



        word2vec_distances_util.compute_word2vec_distances(inputFilename, inputDir, outputDir, createCharts, chartPackage,
                                   word_vectors,
                                   result_df,
                                   keywords_var,
                                   compute_distances_var, top_words_var, BERT=True)

        # print(f'\nStarted computing word distances between top {top_words_var} words at {time.asctime( time.localtime(time.time()))}')
        # # find user-selected top most-frequent words
        # # word vectors
        # tmp_result = result_df['Word'].value_counts().index.tolist()[:top_words_var]
        # tmp_result_df = result_df.loc[result_df['Word'].isin(tmp_result)]
        # tmp_result_df.drop_duplicates(subset=['Word'], keep='first', inplace=True)
        # tmp_result_df = tmp_result_df.reset_index(drop=True)
        #
        # if not 'Do not' in vis_menu_var:
        #     # TSNE x,y (z) coordinates
        #     tmp_tsne = tsne_df['Word'].value_counts().index.tolist()[:top_words_var]
        #     tmp_tsne_df = tsne_df.loc[tsne_df['Word'].isin(tmp_tsne)]
        #     tmp_tsne_df.drop_duplicates(subset=['Word'], keep='first', inplace=True)
        #     tmp_tsne_df = tmp_tsne_df.reset_index(drop=True)
        #
        #     # calculate 2-dimensional euclidean distance
        #     # TSNE x,y (z) coordinates
        #     tsne_dist_df = pd.DataFrame()
        #     dist_idx = 0
        #     print(f'\nStarted computing t-SNE 2-dimensional Euclidean distance between top {top_words_var} words at {time.asctime( time.localtime(time.time()))}')
        #     for i, row in tmp_tsne_df.iterrows():
        #         j = len(tmp_tsne_df)-1
        #         while i < j:
        #             tsne_dist_df.at[dist_idx, 'Word_1'] = row['Word']
        #             tsne_dist_df.at[dist_idx, 'Word_2'] = tmp_tsne_df.at[j, 'Word']
        #             if 'z' not in tmp_tsne_df.columns:
        #                 tsne_dist_df.at[dist_idx, '2-dimensional Euclidean distance'] = word2vec_util.euclidean_dist( [row['x'],row['y']], [tmp_tsne_df.at[j, 'x'],tmp_tsne_df.at[j, 'y']] )
        #             else:
        #                 tsne_dist_df.at[dist_idx, '2-dimensional Euclidean distance'] = word2vec_util.euclidean_dist( [row['x'],row['y'],row['z']], [tmp_tsne_df.at[j, 'x'],tmp_tsne_df.at[j, 'y'],tmp_tsne_df.at[j, 'z']] )
        #             dist_idx+=1
        #             j-=1
        #     tsne_dist_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'Word2Vec_top_' + str(top_words_var)+'_TSNE_dist')
        #     tsne_dist_df.to_csv(tsne_dist_outputFilename, encoding='utf-8', index=False)
        #     tsne_dist_df.to_csv(tsne_dist_outputFilename, encoding='utf-8', index=False)
        #     filesToOpen.append(tsne_dist_outputFilename)
        #
        # # calculate cos similarity
        # cos_sim_df = pd.DataFrame()
        # cos_idx = 0
        # print(
        #     f'\nStarted computing cosine similarity between top {top_words_var} words at {time.asctime(time.localtime(time.time()))}')
        # for i, row in tmp_result_df.iterrows():
        #     j = len(tmp_result_df) - 1
        #     while i < j:
        #         try:
        #             tfidf_vectorizer = TfidfVectorizer(analyzer="char")
        #             sparse_matrix = tfidf_vectorizer.fit_transform(
        #                 [str(row['Word'])] + [str(tmp_result_df.at[j, 'Word'])])
        #             sim_score = cosine_similarity(sparse_matrix[0], sparse_matrix[1])
        #             cos_sim_df.at[cos_idx, 'Word_1'] = row['Word']
        #             cos_sim_df.at[cos_idx, 'Word_2'] = tmp_result_df.at[j, 'Word']
        #             cos_sim_df.at[cos_idx, 'Cosine similarity'] = sim_score
        #         except KeyError:
        #             cos_idx += 1
        #             j -= 1
        #             continue
        #         cos_idx += 1
        #         j -= 1
        #
        # # vectors of top 10 freq words n-dimensional distance
        # dist_df = pd.DataFrame()
        # dist_idx = 0
        # print(f'\nStarted computing n-dimensional Euclidean distance between top {top_words_var} words at {time.asctime( time.localtime(time.time()))}')
        # for i, row in tmp_result_df.iterrows():
        #     j = len(tmp_result_df)-1
        #     while i < j:
        #         dist_df.at[dist_idx, 'Word_1'] = row['Word']
        #         dist_df.at[dist_idx, 'Word_2'] = tmp_result_df.at[j, 'Word']
        #         dist_df.at[dist_idx, 'n-dimensional Euclidean distance'] = word2vec_util.euclidean_dist(row['Embeddings'], tmp_result_df.at[j, 'Embeddings'])
        #         dist_idx+=1
        #         j-=1
        #
        # # create outputFilenames and save them
        # cos_sim_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'Word2Vec_top_' + str(top_words_var)+'_Cos_Similarity')
        # dist_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'Word2Vec_top_' + str(top_words_var)+'_Euclidean_dist')
        #
        # dist_df.to_csv(dist_outputFilename, encoding='utf-8', index=False)
        # cos_sim_df.to_csv(cos_sim_outputFilename, encoding='utf-8', index=False)
        #
        # dist_df.to_csv(dist_outputFilename, encoding='utf-8', index=False)
        # cos_sim_df.to_csv(cos_sim_outputFilename, encoding='utf-8', index=False)
        #
        # filesToOpen.append(dist_outputFilename)
        # filesToOpen.append(cos_sim_outputFilename)
        #
        # chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, dist_outputFilename,
        #                                                    outputDir,
        #                                                    columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['n-dimensional Euclidean distance'],
        #                                                    chartTitle='Frequency Distribution of n-dimensional Euclidean distances',
        #                                                    # count_var = 1 for columns of alphabetic values
        #                                                    count_var=0, hover_label=[],
        #                                                    outputFileNameType='nDim_dist', #'POS_bar',
        #                                                    column_xAxis_label='Euclidean distance',
        #                                                    groupByList=[],
        #                                                    plotList=[],
        #                                                    chart_title_label='')
        #
        # if chart_outputFilename!=None:
        #     if len(chart_outputFilename) > 0:
        #         filesToOpen.extend(chart_outputFilename)
        #
        # chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, cos_sim_outputFilename,
        #                                                    outputDir,
        #                                                    columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Cosine similarity'],
        #                                                    chartTitle='Frequency Distribution of cosine similarities',
        #                                                    # count_var = 1 for columns of alphabetic values
        #                                                    count_var=0, hover_label=[],
        #                                                    outputFileNameType='coos_simil', #'POS_bar',
        #                                                    column_xAxis_label='Cosine similarity',
        #                                                    groupByList=[],
        #                                                    plotList=[],
        #                                                    chart_title_label='')
        #
        # if chart_outputFilename!=None:
        #     if len(chart_outputFilename) > 0:
        #         filesToOpen.extend(chart_outputFilename)


        #keyword_sim_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'Word2Vec_' + str(
                                                                                # len(keywords_list)) + '_Keywords_Cos_Similarity')
        #keyword_df.to_csv(keyword_sim_outputFilename, encoding='utf-8', index=False)
       #filesToOpen.append(keyword_sim_outputFilename)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                                       'Finished running BERT word embeddings at', True, '', True, startTime)


    return filesToOpen


# Performs sentiment analysis using roBERTa model
def sentiment_analysis_BERT(inputFilename, outputDir, outputFilename, mode, Document_ID, Document):
    model_path = "cardiffnlp/twitter-xlm-roberta-base-sentiment" # multilingual model
    # model_path = "cardiffnlp/twitter-roberta-base-sentiment-latest" # English language model
    # sentiment_task = pipeline("sentiment-analysis",
    #  model=model_path, tokenizer=model_path, max_length=512, truncation=True)
    sentiment_task = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path, truncation=True)

    with open(inputFilename, 'r', encoding='utf-8', errors='ignore') as myfile:
        fulltext = myfile.read()
    # end method if file is empty
    if len(fulltext) < 1:
        mb.showerror(title='File empty', message='The file ' + inputFilename +
                                                 ' is empty.\n\nPlease, use another file and try again.')
        print('Empty file ', inputFilename)
        return

    sentences = sent_tokenize_stanza(stanzaPipeLine(fulltext))

    i = 1

    for s in sentences:
        sentiment = sentiment_task(s)

        writer.writerow({
            Sentiment_measure: sentiment[0].get('score'),
            Sentiment_label: sentiment[0].get('label'),
            'Sentence ID': i,
            'Sentence': s,
            'Document ID': Document_ID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document)
        })

        i += 1

    return outputFilename


# helper main method for sentiment analysis
def main(inputFilename, inputDir, outputDir, mode, createCharts=False, chartPackage='Excel'):
    """
    Runs analyzefile on the appropriate files, provided that the input paths are valid.
    :param inputFilename:
    :param inputDir:
    :param outputDir:
    :return:

    """

    filesToOpen = []

    if len(outputDir) < 0 or not os.path.exists(outputDir):
        print('No output directory specified, or path does not exist.')
        sys.exit(1)
    elif len(inputFilename) == 0 and len(inputDir) == 0:
        print(
            'No input specified. Please, provide either a single file -- file or a directory of files to be analyzed --dir.')
        sys.exit(1)

    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, '.csv', 'roBERTa', '', '', '', '', False, True)

    # check each word in sentence for sentiment and write to output_file
    with open(outputFilename, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
        global Sentiment_measure, Sentiment_label
        Sentiment_measure = 'Sentiment score'
        Sentiment_label = 'Sentiment label'
        fieldnames = [Sentiment_measure, Sentiment_label,
                      'Sentence ID', 'Sentence', 'Document ID', 'Document']
        global writer
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        if len(inputFilename) > 0:  # handle single file
            if os.path.exists(inputFilename):
                filesToOpen.append(sentiment_analysis_BERT(
                    inputFilename, outputDir, outputFilename, mode, 1, inputFilename))
                output_file = sentiment_analysis_BERT(
                    inputFilename, outputDir, outputFilename, mode, 1, inputFilename)
            else:
                print('Input file "' + inputFilename + '" is invalid.')
                sys.exit(1)
        elif len(inputDir) > 0:  # handle directory
            documentID = 0
            if os.path.isdir(inputDir):
                directory = os.fsencode(inputDir)
                for file in os.listdir(directory):
                    filename = os.path.join(inputDir, os.fsdecode(file))
                    if filename.endswith(".txt"):
                        start_time = time.asctime( time.localtime(time.time()))()
                        # print("Started SentiWordNet sentiment analysis of " + filename + "...")
                        documentID += 1
                        filesToOpen.append(sentiment_analysis_BERT(
                            filename, outputDir, outputFilename, mode, documentID, filename))
                        # print("Finished SentiWordNet sentiment analysis of " + filename + " in " + str((time.asctime( time.localtime(time.time()))() - start_time)) + " seconds")
                        # print("Finished SentiWordNet sentiment analysis of " + filename + " in " + str((time.asctime( time.localtime(time.time()))() - start_time)) + " seconds")
            else:
                print('Input directory "' + inputDir + '" is invalid.')
                # sys.exit(1)
    csvfile.close()

    if createCharts == True:

        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Sentiment score'],
                                                           chartTitle='Frequency of roBERTa Sentiment Scores',
                                                           count_var=0, hover_label=[],
                                                           outputFileNameType='roBERTa_scores',  # 'line_bar',
                                                           column_xAxis_label='Sentiment score',
                                                           column_yAxis_label='Scores',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Sentiment Score'],
                                                           chart_title_label='Measures of roBERTa Sentiment Scores')

        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename, outputDir,
                                                           columns_to_be_plotted_xAxis=[],
                                                           columns_to_be_plotted_yAxis=['Sentiment label'],
                                                           chartTitle='Frequency of roBERTa Sentiment Labels',
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='roBERTa_labels',  # 'line_bar',
                                                           column_xAxis_label='Sentiment label',
                                                           column_yAxis_label='Frequency',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Sentiment label'],
                                                           chart_title_label='Measures of roBERTa Sentiment Labels')

        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

    return filesToOpen


if __name__ == '__main__':
    # get arguments from command line
    parser = argparse.ArgumentParser(
        description='Sentiment analysis with BERT')
    parser.add_argument('--file', type=str, dest='inputFilename', default='',
                        help='a string to hold the INPUT path and filename if only ONE txt file is processed; enter --file "" or eliminate --file flag to process ALL txt files in input directory; use "" if path and filenames contain spaces')
    parser.add_argument('--dir', type=str, dest='inputDir', default='',
                        help='a string to hold the INPUT path of the directory of ALL txt files to be processed; use "" if path contains spaces')
    parser.add_argument('--out', type=str, dest='outputDir', default='',
                        help='a string to hold the path of the OUTPUT directory; use "" if path contains spaces')
    parser.add_argument('--outfile', type=str, dest='outputFilename', default='',
                        help='output file')

    parser.add_argument('--mode', type=str, dest='mode', default='mean',
                        help='mode with which to calculate sentiment in the sentence: mean or median')
    args = parser.parse_args()

    # run main
    sys.exit(main(args.inputFilename, args.inputDir,
                  args.outputDir, args.outputFilename, args.mode))

# very fast method to split a text file into a list whose elements are each sentence in that file. Found on: https://stackoverflow.com/a/31505798
# -*- coding: utf-8 -*-
import re

alphabets = "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
digits = "([0-9])"


def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n", " ")
    text = re.sub(prefixes, "\\1<prd>", text)
    text = re.sub(websites, "<prd>\\1", text)
    text = re.sub(digits + "[.]" + digits, "\\1<prd>\\2", text)
    if "..." in text: text = text.replace("...", "<prd><prd><prd>")
    if "Ph.D" in text: text = text.replace("Ph.D.", "Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] ", " \\1<prd> ", text)
    text = re.sub(acronyms + " " + starters, "\\1<stop> \\2", text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>", text)
    text = re.sub(" " + suffixes + "[.] " + starters, " \\1<stop> \\2", text)
    text = re.sub(" " + suffixes + "[.]", " \\1<prd>", text)
    text = re.sub(" " + alphabets + "[.]", " \\1<prd>", text)
    if "”" in text: text = text.replace(".”", "”.")
    if "\"" in text: text = text.replace(".\"", "\".")
    if "!" in text: text = text.replace("!\"", "\"!")
    if "?" in text: text = text.replace("?\"", "\"?")
    text = text.replace(".", ".<stop>")
    text = text.replace("?", "?<stop>")
    text = text.replace("!", "!<stop>")
    text = text.replace("<prd>", ".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

