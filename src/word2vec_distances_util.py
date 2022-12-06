import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"word2vec_main.py",['os','tkinter', 'gensim', 'spacy', 'stanza', 'plotly'])==False:
    sys.exit(0)


import pandas as pd
import tkinter.messagebox as mb
import math
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import IO_files_util
import IO_user_interface_util
import charts_util

# for calculating the distance
import itertools
import numpy as np
from numpy.linalg import norm

def compute_word2vec_distances(inputFilename, inputDir, outputDir, createCharts, chartPackage,
                        word_vectors,
                        result_df,
                        keywords_var,
                        compute_distances_var, top_words_var, BERT=False):

    filesToOpen = []

    # two_dim_Euclidean distances are always computed when plots are computed 2D 3D in word2vec_tsne_plot_util

    n_dim_Euclidean = compute_distances_var # always computed when distances are computed
    compute_cosine_similarity = True  # always computed

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
            else:
                mb.showerror(title='Warning',
                             message='You have selected a vector csv file in input. This I/O option allows you to compute cosine similarity distances between selected keywords. But the "Keywords" widget is empty.\n\nPlease, enter comma-separated words in the "Keywords" widget at the bottom of this GUI and try again.')
            return filesToOpen

        else:
            mb.showerror(title='csv file error',
                       message='The selected csv file does NOT contain Vector column.\n\nPlease, select a different csv file and try again.')

    # compute word distances
    if n_dim_Euclidean:
        print(
            f'\nStarted computing word distances between top {top_words_var} words at {time.asctime(time.localtime(time.time()))}')
        # find user-selected top most-frequent words
        tmp_result = result_df['Word'].value_counts().index.tolist()[:top_words_var]
        tmp_result_df = result_df.loc[result_df['Word'].isin(tmp_result)]
        tmp_result_df.drop_duplicates(subset=['Word'], keep='first', inplace=True)
        tmp_result_df = tmp_result_df.reset_index(drop=True)
        # vectors of top n freq words n-dimensional Euclidean distance
        dist_df = pd.DataFrame()
        dist_idx = 0
        print(f'\nStarted computing n-dimensional Euclidean distance between top {top_words_var} words at {time.asctime( time.localtime(time.time()))}')
        for i, row in tmp_result_df.iterrows():
            j = len(tmp_result_df)-1
            while i < j:
                dist_df.at[dist_idx, 'Word_1'] = row['Word']
                dist_df.at[dist_idx, 'Word_2'] = tmp_result_df.at[j, 'Word']
                dist_df.at[dist_idx, 'n-dimensional Euclidean distance'] = euclidean_dist(row['Vector'], tmp_result_df.at[j, 'Vector'])
                dist_idx+=1
                j-=1

        # create outputFilenames and save them
        dist_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'Word2Vec_top_' + str(top_words_var)+'_Euclidean_dist')

        dist_df.to_csv(dist_outputFilename, encoding='utf-8', index=False)

        filesToOpen.append(dist_outputFilename)
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, dist_outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['n-dimensional Euclidean distance'],
                                                           chartTitle='Frequency Distribution of n-dimensional Euclidean distances',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=0, hover_label=[],
                                                           outputFileNameType='nDim_dist', #'POS_bar',
                                                           column_xAxis_label='Euclidean distance',
                                                           groupByList=[],
                                                           plotList=[],
                                                           chart_title_label='')

        if chart_outputFilename!=None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)
    
    #BERT requires separate handling of cosine similarity since similarity(...) is a gensim word2vec function, so we have different cases for the two 
    if not BERT: 
        if compute_cosine_similarity:# now always set to True
            # calculate cos similarity
            cos_sim_df = pd.DataFrame()
            cos_idx = 0
            print(
                f'\nStarted computing cosine similarity between top {top_words_var} words at {time.asctime(time.localtime(time.time()))}')
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
        

            cos_sim_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'Word2Vec_top_' + str(top_words_var)+'_Cos_Similarity')
            cos_sim_df.to_csv(cos_sim_outputFilename, encoding='utf-8', index=False)
            filesToOpen.append(cos_sim_outputFilename)
            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, cos_sim_outputFilename,
                                                            outputDir,
                                                            columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Cosine similarity'],
                                                            chartTitle='Frequency Distribution of cosine similarities',
                                                            # count_var = 1 for columns of alphabetic values
                                                            count_var=0, hover_label=[],
                                                            outputFileNameType='coos_simil', #'POS_bar',
                                                            column_xAxis_label='Cosine similarity',
                                                            groupByList=[],
                                                            plotList=[],
                                                            chart_title_label='')

            if chart_outputFilename!=None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.extend(chart_outputFilename)

            # compute cosine similarity for selected keywords
            if keywords_var:
                keyword_df = pd.DataFrame()
                keywords_list = [x.strip() for x in keywords_var.split(',')]
                print(f'\nStarted computing cosine similarity between words for {len(keywords_list)} selected keywords at {time.asctime( time.localtime(time.time()))}')
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
        
    else:
        if compute_cosine_similarity:
            cos_sim_df = pd.DataFrame()
            cos_idx = 0
            print(f'\nStarted computing cosine similarity between top {top_words_var} words at {time.asctime(time.localtime(time.time()))}')
            for i, row in tmp_result_df.iterrows():
                j = len(tmp_result_df)-1
                while i < j:
                    try:
                        tfidf_vectorizer = TfidfVectorizer(analyzer="char")
                        sparse_matrix = tfidf_vectorizer.fit_transform([str(row['Word'])] + [str(tmp_result_df.at[j, 'Word'])])
                        sim_score = cosine_similarity(sparse_matrix[0], sparse_matrix[1])
                        cos_sim_df.at[cos_idx, 'Word_1'] = row['Word']
                        cos_sim_df.at[cos_idx, 'Word_2'] = tmp_result_df.at[j, 'Word']
                        cos_sim_df.at[cos_idx, 'Cosine similarity'] = sim_score
                    except KeyError:
                        cos_idx+=1
                        j-=1
                        continue
                    cos_idx+=1
                    j-=1

            cos_sim_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'Word2Vec_top_' + str(top_words_var)+'_Cos_Similarity')
            cos_sim_df.to_csv(cos_sim_outputFilename, encoding='utf-8', index=False)
            filesToOpen.append(cos_sim_outputFilename)
            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, cos_sim_outputFilename,
                                                            outputDir,
                                                            columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Cosine similarity'],
                                                            chartTitle='Frequency Distribution of cosine similarities',
                                                            # count_var = 1 for columns of alphabetic values
                                                            count_var=0, hover_label=[],
                                                            outputFileNameType='coos_simil', #'POS_bar',
                                                            column_xAxis_label='Cosine similarity',
                                                            groupByList=[],
                                                            plotList=[],
                                                            chart_title_label='')

            if chart_outputFilename!=None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.extend(chart_outputFilename)

            if keywords_var:
                keyword_df = pd.DataFrame()
                keywords_list = [x.strip() for x in keywords_var.split(',')]
                print(f'\nStarted computing cosine similarity between words for {len(keywords_list)} selected keywords at {time.asctime( time.localtime(time.time()))}')
                i = 0
                for a, b in itertools.combinations(keywords_list, 2):
                    try:
                        tfidf_vectorizer = TfidfVectorizer(analyzer="char")
                        sparse_matrix = tfidf_vectorizer.fit_transform([a]+[b])
                        sim_score = cosine_similarity(sparse_matrix[0],sparse_matrix[1])
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


    return filesToOpen

# calculate Euclidean distance of vectors (different from x,y coordinates)
def euclidean_dist(x, y):
    return math.sqrt(sum((p1 - p2)**2 for p1, p2 in zip(x,y)))
