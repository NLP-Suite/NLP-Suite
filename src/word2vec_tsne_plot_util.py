import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"word2vec_main.py",['os','tkinter', 'gensim', 'spacy', 'stanza', 'plotly'])==False:
    sys.exit(0)


import pandas as pd
import time

import IO_files_util
import IO_user_interface_util


#Visualization
import plotly.express as px
from sklearn.manifold import TSNE

def run_word2vec_plot(inputFilename, inputDir, outputDir,
                        word_vector_list,
                        filtered_words,
                        vis_menu_var,
                        dim_menu_var):

    filesToOpen = []

    ## visualization
    # print(f'\nStarted preparing charts via t-SNE for {len(words)} distinct words at {time.asctime(time.localtime(time.time()))}')
    print(f'\nStarted preparing charts via t-SNE for # distinct words at {time.asctime(time.localtime(time.time()))}')

    if vis_menu_var == 'Plot word vectors':

        if dim_menu_var == '2D':

            tsne = TSNE(n_components=2)
            xys = tsne.fit_transform(word_vector_list)

            xs = xys[:, 0]
            ys = xys[:, 1]
            word = filtered_words.keys()

            tsne_df = pd.DataFrame({'Word': word, 'x': xs, 'y': ys})
            fig = plot_interactive_graph(tsne_df)
            fig_words = plot_interactive_graph_words(tsne_df)

        else: # 3D

            tsne = TSNE(n_components=3)
            xyzs = tsne.fit_transform(word_vector_list)
            xs = xyzs[:, 0]
            ys = xyzs[:, 1]
            zs = xyzs[:, 2]
            word = filtered_words.keys()

            tsne_df = pd.DataFrame({'Word': word, 'x': xs, 'y': ys, 'z': zs})
            fig = plot_interactive_3D_graph(tsne_df)
            fig_words = plot_interactive_3D_graph_words(tsne_df)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.html',
                                                             'Word2Vec_vector_ALL_words')

    fig.write_html(outputFilename)
    filesToOpen.append(outputFilename)

    return filesToOpen

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

def append_list(sim_words, words):
    list_of_words = []

    for i in range(len(sim_words)):
        sim_words_list = list(sim_words[i])
        sim_words_list.append(words)
        sim_words_tuple = tuple(sim_words_list)
        list_of_words.append(sim_words_tuple)

    return list_of_words
