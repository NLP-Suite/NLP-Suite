import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"word2vec_main.py",['os','tkinter', 'gensim', 'stanza', 'plotly'])==False:
    sys.exit(0)


import pandas as pd
import tkinter.messagebox as mb
import math
import time

import IO_files_util
import IO_user_interface_util
import charts_util

import itertools
import numpy as np
from numpy.linalg import norm


def _cosine_sim_vectors(vec_a, vec_b):
    """Cosine similarity between two numeric vectors."""
    a = np.array(vec_a, dtype=float)
    b = np.array(vec_b, dtype=float)
    denom = norm(a) * norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def _compute_similarity(word_a, word_b, word_vectors, result_df, BERT):
    """Compute cosine similarity between two words.

    For Gensim: uses word_vectors.similarity() (embedding-based).
    For BERT: looks up embedding vectors from result_df and computes cosine similarity directly.
    """
    if not BERT:
        return word_vectors.similarity(str(word_a), str(word_b))
    else:
        rows_a = result_df.loc[result_df['Word'] == word_a, 'Vector']
        rows_b = result_df.loc[result_df['Word'] == word_b, 'Vector']
        if rows_a.empty or rows_b.empty:
            raise KeyError(f"Word not found: {word_a} or {word_b}")
        vec_a = rows_a.iloc[0]
        vec_b = rows_b.iloc[0]
        return _cosine_sim_vectors(vec_a, vec_b)


def _visualize_and_collect(chartPackage, dataTransformation, outputFilename, outputDir,
                           x_col, y_col, chart_title, outputFileNameType, x_label, filesToOpen):
    """Run visualization and append output files."""
    outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFilename,
                                              outputDir,
                                              columns_to_be_plotted_xAxis=[x_col],
                                              columns_to_be_plotted_yAxis=[y_col],
                                              chart_title=chart_title,
                                              count_var=0, hover_label=[],
                                              outputFileNameType=outputFileNameType,
                                              column_xAxis_label=x_label,
                                              groupByList=[],
                                              plotList=[],
                                              chart_title_label='')
    if outputFiles is not None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)


def compute_word2vec_distances(inputFilename, inputDir, outputDir, chartPackage, dataTransformation,
                        word_vectors,
                        result_df,
                        keywords_var,
                        compute_distances_var, top_words_var, BERT=False):

    filesToOpen = []

    n_dim_Euclidean = compute_distances_var
    compute_cosine_similarity = True

    # compute only distances if inputFile is csv (re-run on previously saved vectors)
    if inputFilename.endswith('csv'):
        w2v_df = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
        if 'Vector' in w2v_df.columns:
            w2v_df['Vector'] = w2v_df['Vector'].astype(object)

            if keywords_var:
                keywords_list = [x.strip() for x in keywords_var.split(',')]
                rows = []
                for a, b in itertools.combinations(keywords_list, 2):
                    try:
                        if a in w2v_df['Word'].values and b in w2v_df['Word'].values:
                            A = w2v_df.loc[w2v_df['Word'] == a, 'Vector'].values[0]
                            B = w2v_df.loc[w2v_df['Word'] == b, 'Vector'].values[0]
                            A = list(map(float, ' '.join(A.strip('][').split()).split()))
                            B = list(map(float, ' '.join(B.strip('][').split()).split()))
                            sim_score = _cosine_sim_vectors(A, B)
                            rows.append({'Word_1': a, 'Word_2': b, 'Cosine similarity': sim_score})
                    except (KeyError, ValueError):
                        continue

                keyword_df = pd.DataFrame(rows)
                keyword_sim_outputFilename = IO_files_util.generate_output_file_name(
                    inputFilename, inputDir, outputDir, '.csv',
                    f'Word2Vec_{len(keywords_list)}_Keywords_Cos_Similarity')
                keyword_df.to_csv(keyword_sim_outputFilename, encoding='utf-8', index=False)
                filesToOpen.append(keyword_sim_outputFilename)
            else:
                mb.showerror(title='Warning',
                             message='You have selected a vector csv file in input. This I/O option allows you to compute cosine similarity distances between selected keywords. But the "Keywords" widget is empty.\n\nPlease, enter comma-separated words in the "Keywords" widget at the bottom of this GUI and try again.')
            return filesToOpen
        else:
            mb.showerror(title='csv file error',
                       message='The selected csv file does NOT contain Vector column.\n\nPlease, select a different csv file and try again.')

    # find top most-frequent words
    tmp_result = result_df['Word'].value_counts().index.tolist()[:top_words_var]
    tmp_result_df = result_df.loc[result_df['Word'].isin(tmp_result)]
    tmp_result_df = tmp_result_df.drop_duplicates(subset=['Word'], keep='first').reset_index(drop=True)

    # n-dimensional Euclidean distances
    if n_dim_Euclidean:
        print(f'\nStarted computing word distances between top {top_words_var} words at {time.asctime(time.localtime(time.time()))}')

        dist_rows = []
        print(f'\nStarted computing n-dimensional Euclidean distance between top {top_words_var} words at {time.asctime(time.localtime(time.time()))}')
        for i in range(len(tmp_result_df)):
            for j in range(i + 1, len(tmp_result_df)):
                w1 = tmp_result_df.iloc[i]['Word']
                w2 = tmp_result_df.iloc[j]['Word']
                v1 = tmp_result_df.iloc[i]['Vector']
                v2 = tmp_result_df.iloc[j]['Vector']
                dist_rows.append({
                    'Word_1': w1,
                    'Word_2': w2,
                    'Word_1_2': w1 + '_' + w2,
                    'n-dimensional Euclidean distance': euclidean_dist(v1, v2)
                })

        dist_df = pd.DataFrame(dist_rows)
        dist_outputFilename = IO_files_util.generate_output_file_name(
            inputFilename, inputDir, outputDir, '.csv',
            'Word2Vec_top_' + str(top_words_var) + '_Euclidean_dist')
        dist_df.to_csv(dist_outputFilename, encoding='utf-8', index=False)
        filesToOpen.append(dist_outputFilename)

        _visualize_and_collect(chartPackage, dataTransformation, dist_outputFilename, outputDir,
                               'Word_1_2', 'n-dimensional Euclidean distance',
                               'Frequency Distribution of n-dimensional Euclidean distances',
                               'nDim_dist', 'Euclidean distance', filesToOpen)

    # cosine similarity for top words
    if compute_cosine_similarity:
        cos_rows = []
        print(f'\nStarted computing cosine similarity between top {top_words_var} words at {time.asctime(time.localtime(time.time()))}')

        for i in range(len(tmp_result_df)):
            for j in range(i + 1, len(tmp_result_df)):
                w1 = tmp_result_df.iloc[i]['Word']
                w2 = tmp_result_df.iloc[j]['Word']
                try:
                    sim_score = _compute_similarity(w1, w2, word_vectors, result_df, BERT)
                    cos_rows.append({
                        'Word_1': w1,
                        'Word_2': w2,
                        'Word_1_2': w1 + '_' + w2,
                        'Cosine similarity': sim_score
                    })
                except KeyError:
                    continue

        cos_sim_df = pd.DataFrame(cos_rows)
        cos_sim_outputFilename = IO_files_util.generate_output_file_name(
            inputFilename, inputDir, outputDir, '.csv',
            'Word2Vec_top_' + str(top_words_var) + '_Cos_Similarity')
        cos_sim_df.to_csv(cos_sim_outputFilename, encoding='utf-8', index=False)
        filesToOpen.append(cos_sim_outputFilename)

        _visualize_and_collect(chartPackage, dataTransformation, cos_sim_outputFilename, outputDir,
                               'Word_1_2', 'Cosine similarity',
                               'Frequency Distribution of cosine similarities',
                               'cos_simil', 'Cosine similarity', filesToOpen)

        # cosine similarity for selected keywords
        if keywords_var:
            keywords_list = [x.strip() for x in keywords_var.split(',')]
            print(f'\nStarted computing cosine similarity between words for {len(keywords_list)} selected keywords at {time.asctime(time.localtime(time.time()))}')
            kw_rows = []
            for a, b in itertools.combinations(keywords_list, 2):
                try:
                    sim_score = _compute_similarity(a, b, word_vectors, result_df, BERT)
                    kw_rows.append({
                        'Word_1': a,
                        'Word_2': b,
                        'Word_1_2': a + '_' + b,
                        'Cosine similarity': sim_score
                    })
                except KeyError:
                    continue

            keyword_df = pd.DataFrame(kw_rows)
            keyword_sim_outputFilename = IO_files_util.generate_output_file_name(
                inputFilename, inputDir, outputDir, '.csv',
                f'Word2Vec_{len(keywords_list)}_Keywords_Cos_Similarity')
            keyword_df.to_csv(keyword_sim_outputFilename, encoding='utf-8', index=False)
            filesToOpen.append(keyword_sim_outputFilename)

            _visualize_and_collect(chartPackage, dataTransformation, keyword_sim_outputFilename, outputDir,
                                   'Word_1_2', 'Cosine similarity',
                                   'Frequency Distribution of cosine similarities',
                                   'cos_simil', 'Cosine similarity', filesToOpen)

    return filesToOpen


def euclidean_dist(x, y):
    return math.sqrt(sum((p1 - p2)**2 for p1, p2 in zip(x, y)))
