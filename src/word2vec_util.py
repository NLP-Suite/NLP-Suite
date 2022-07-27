import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"word2vec_main.py",['os','tkinter', 'gensim', 'spacy', 'plotly'])==False:
    sys.exit(0)


from sys import platform
import os
import tkinter as tk
import pandas as pd
import tkinter.messagebox as mb

import GUI_IO_util
import IO_files_util
import IO_user_interface_util
import IO_csv_util

#Gensim
import gensim
from gensim.models import Word2Vec
from nltk.tokenize import sent_tokenize

#Visualization
import plotly.express as px
##from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


#stopwords
from nltk.corpus import stopwords
stop_words = stopwords.words('english')

#spacy for lemmatization
import spacy

try:
    spacy.load('en_core_web_sm')
except:
    if platform == 'darwin':
        msg = '\n\nAt terminal, type sudo python -m spacy download en_core_web_sm'
    if platform == 'win32':
        msg = '\n\nClick on left-hand start icon in task bar' + \
                '\n  Scroll down to Anaconda' + \
                '\n  Click on the dropdown arrow to display available options' + \
                '\n  Right click on Anaconda Prompt' + \
                '\n  Click on More' + \
                '\n  Click on Run as Administrator' + \
                '\n  At the command prompt, Enter "conda activate NLP" (if NLP is your environment)' + \
                '\n  Then enter: "python -m spacy download en_core_web_sm" and Return'
    msg = msg + '\n\nThis imports the package.'
    mb.showerror(title='Library error', message='The Gensim tool could not find the English language spacy library. This needs to be installed. At command promp type:\npython -m spacy download en_core_web_sm\n\nYOU MAY HAVE TO RUN THE COMMAND AS ADMINISTRATOR.\n\nHOW DO YOU DO THAT?' + msg)
    sys.exit(0)

nlp = spacy.load('en_core_web_sm')

def run_Gensim_word2vec(inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage,
                        remove_stopwords_var, lemmatize_var, sg_menu_var, vector_size_var, window_var, min_count_var,
                        vis_menu_var, dim_menu_var, keywords_var,
                        word_vector=None):
    ## list for csv file
    word = []
    lemmatized_word = []
    unlemmatized_word = []
    sentenceID = []
    sentence = []
    documentID = []
    document = []

    ## word list for word2vec
    word_list = []

    all_input_docs = {}
    dId = 0

    filesToOpen = []

    startTime = IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                                   'Started running Word2Vec at', True)

    if len(inputFilename)>0:
        doc = inputFilename
        if doc.endswith('.txt'):
            with open(doc, 'r', encoding='utf-8', errors='ignore') as file:
                dId += 1
                text = file.read()
                print('importing single file')
                documentID.append(dId)
                document.append(IO_csv_util.dressFilenameForCSVHyperlink(os.path.join(inputDir, doc)))
                all_input_docs[dId] = text

    else:
        numFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
        if numFiles == 0:
            mb.showerror(title='Number of files error',
                        message='The selected input directory does NOT contain any file of txt type.\n\nPlease, select a different directory and try again.')
            return

        for doc in os.listdir(inputDir):
            if doc.endswith('.txt'):
                with open(os.path.join(inputDir, doc), 'r', encoding='utf-8', errors='ignore') as file:
                    dId += 1
                    text = file.read()
                    print('importing ' + str(dId) + '/' + str(numFiles) + ' file')
                    documentID.append(dId)
                    document.append(os.path.join(inputDir, doc))
                    all_input_docs[dId] = text

    document_df = pd.DataFrame({'Document ID': documentID, 'Document': document})
    document_df = document_df.astype('str')

    documentID = []
    print('Tokenizing...')
    for idx, txt in enumerate(all_input_docs.items()):
        sentences = sent_tokenize(txt[1])
        sId = 0
        for sent in sentences:
            sId += 1
            words = make_words(sent)
            word_list.append(words)
            for w in words:
                documentID.append(txt[0])
                sentenceID.append(sId)
                sentence.append(sent)
                word.append(w)

    sentence_df = pd.DataFrame({'Word': word, 'Sentence ID': sentenceID, 'Sentence': sentence, 'Document ID': documentID})
    sentence_df = sentence_df.astype(str)

    if remove_stopwords_var == True:
        print('Removing stopwords..')
        ## sentence_df = remove_stopwords_df(sentence_df)
        word_list = list(remove_stopwords(word_list))
    else:
        word_list = list(word_list)

    ## lemmatize
    if lemmatize_var == True:
        print('Lemmatizing...')

    sentences_out = []
    for word_in_sent in word_list:
        doc = nlp(" ".join(word_in_sent))
        if lemmatize_var == True:
            sentences_out.append([token.lemma_ for token in doc])
            unlemmatized_word.extend([token for token in doc])
            lemmatized_word.extend([token.lemma_ for token in doc])
        else:
            sentences_out.append([token for token in doc])

    word_df = pd.DataFrame({'Word': unlemmatized_word})
    if (len(lemmatized_word)>0):
        word_df['Lemmatized word'] = lemmatized_word

    word_df = word_df.astype(str)
    word_df = word_df.drop_duplicates()
    sent_word_df = pd.merge(sentence_df, word_df, on='Word', how='inner')
    sent_word_df = sent_word_df.astype(str)


    if sg_menu_var == 'CBOW':
        sg_var = 0
    else:
        sg_var = 1

    print('learning architecture: ', sg_menu_var)

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
    word_vector_list = [word_vectors[v] for v in words]

    ## visualization
    print('Visualizing via t-SNE...')

    if vis_menu_var == 'Plot all word vectors':

        if dim_menu_var == '2D':

            tsne = TSNE(n_components=2)
            xys = tsne.fit_transform(word_vector_list)

            xs = xys[:, 0]
            ys = xys[:, 1]
            word = words.keys()

            tsne_df = pd.DataFrame({'Word': word, 'x': xs, 'y': ys})
            fig = plot_interactive_graph(tsne_df)
            fig_words = plot_interactive_graph_words(tsne_df)

        else:

            tsne = TSNE(n_components=3)
            xyzs = tsne.fit_transform(word_vector_list)
            xs = xyzs[:, 0]
            ys = xyzs[:, 1]
            zs = xyzs[:, 2]
            word = words.keys()

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
            result_word.extend(sim_words)
        if len(result_word)==0:
            mb.showwarning(title="No words found",message="None of the keywords entered were found in the corpus.\n\nRoutine aborted.")
            return
        similar_word = [word[0] for word in result_word]
        similarity = [word[1] for word in result_word]
        labels = [word[2] for word in result_word]

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
    print('Saving output...')


    ### write output html graph

    if not fig_words == 'none':
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '_words.html', 'Word2Vec')
        fig_words.write_html(outputFilename)
        filesToOpen.append(outputFilename)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.html', 'Word2Vec')
    fig.write_html(outputFilename)
    filesToOpen.append(outputFilename)

    ### csv file
    word_vector_df = pd.DataFrame()
    for v in words:
        word_vector_df = word_vector_df.append(pd.Series([v, word_vectors[v]]), ignore_index=True)

    if(lemmatize_var == True):
        word_vector_df.columns = ['Lemmatized word', 'Vector']
        word_vector_df = word_vector_df.astype(str)
        sent_word_vector = pd.merge(word_vector_df, sent_word_df, on='Lemmatized word', how='inner')
    else:
        word_vector_df.columns = ['Word', 'Vector']
        word_vector_df = word_vector_df.astype(str)
        sent_word_vector = pd.merge(word_vector_df, sent_word_df, on='Word', how='inner')

    sent_word_vector = sent_word_vector.astype(str)
    result_df = pd.merge(document_df, sent_word_vector, on='Document ID', how='inner')
    result_df = result_df.sort_values(by=["Document ID","Sentence ID"])

    if (lemmatize_var == True):
        result_df = result_df[["Word", "Lemmatized word", "Vector", "Sentence ID", "Sentence", "Document ID", "Document"]]
    else:
        result_df = result_df[["Word", "Vector", "Sentence ID", "Sentence", "Document ID", "Document"]]

    # write csv file
    outputFilename = outputFilename.replace(".html", ".csv")
    result_df.to_csv(outputFilename, index=False)
    filesToOpen.append(outputFilename)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                                       'Finished running Word2Vec at', True, '', True, startTime)

    return filesToOpen

###########################################

def make_words(sent):
    words = list(sent_to_words(sent))
    return words

def sent_to_words(sent):
    return (gensim.utils.simple_preprocess(sent, deacc=True))

def make_sentences(all_input_docs):
    all_txt = []
    for doc in all_input_docs:
        sentences = sent_tokenize(doc)
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

