import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"word2vec_main.py",['os','tkinter', 'gensim', 'stanza', 'plotly'])==False:
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

    print(f'\nStarted preparing charts via t-SNE for {len(filtered_words)} distinct words at {time.asctime(time.localtime(time.time()))}')

    if vis_menu_var == 'Plot word vectors':

        if dim_menu_var == '2D':
            tsne = TSNE(n_components=2)
            xys = tsne.fit_transform(word_vector_list)
            tsne_df = pd.DataFrame({
                'Word': list(filtered_words.keys()),
                'x': xys[:, 0],
                'y': xys[:, 1]
            })
            fig = px.scatter(tsne_df, x="x", y="y", text="Word", hover_name="Word")

        else: # 3D
            tsne = TSNE(n_components=3)
            xyzs = tsne.fit_transform(word_vector_list)
            tsne_df = pd.DataFrame({
                'Word': list(filtered_words.keys()),
                'x': xyzs[:, 0],
                'y': xyzs[:, 1],
                'z': xyzs[:, 2]
            })
            fig = px.scatter_3d(tsne_df, x="x", y="y", z="z", text="Word", hover_name="Word")

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.html',
                                                             'Word2Vec_vector_ALL_words')

    fig.write_html(outputFilename)
    filesToOpen.append(outputFilename)

    return filesToOpen


# Used by BERT_util.py
def plot_interactive_graph(tsne_df):
    return px.scatter(tsne_df, x="x", y="y", hover_name="Word")

def plot_interactive_graph_words(tsne_df):
    return px.scatter(tsne_df, x="x", y="y", text="Word", hover_name="Word")

def plot_interactive_3D_graph(tsne_df):
    return px.scatter_3d(tsne_df, x="x", y="y", z="z", hover_name="Word")

def plot_interactive_3D_graph_words(tsne_df):
    return px.scatter_3d(tsne_df, x="x", y="y", z="z", text="Word", hover_name="Word")
