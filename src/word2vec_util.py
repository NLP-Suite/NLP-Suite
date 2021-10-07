import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"word2vec_main.py",['os','tkinter', 'gensim', 'spacy'])==False:
    sys.exit(0)


import os
import tkinter as tk
import pandas as pd
import tkinter.messagebox as mb

import GUI_IO_util
import IO_files_util

#Gensim
import gensim
from gensim.models import Word2Vec
from nltk.tokenize import sent_tokenize

#Visualization
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

#stopwords
from nltk.corpus import stopwords
stop_words = stopwords.words('english')

#spacy for lemmatization
import spacy

try:
    spacy.load('en_core_web_sm')
except:
    mb.showerror(title='Library error', message='The Gensim tool could not find the English language spacy library. This needs to be installed. At command promp type:\npython -m spacy download en_core_web_sm\n\nYOU MAY HAVE TO RUN THE COMMAND AS ADMINISTRATOR.\n\nHOW DO YOU DO THAT?'
        '\n\nIn Mac, at terminal, type sudo python -m spacy download en_core_web_sm'
        '\n\nIn Windows, click on left-hand start icon in task bar'
        '\n  Scroll down to Anaconda' 
        '\n  Click on the dropdown arrow to display available options'
        '\n  Right click on Anaconda Prompt'
        '\n  Click on More'
        '\n  Click on Run as Administrator'
        '\n  At the command prompt, Enter "conda activate NLP" (if NLP is your environment)'
        '\n  Then enter: "python -m spacy download en_core_web_sm" and Return'
        '\n\nThis imports the package.')
    sys.exit(0)

nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

def run_Gensim_word2vec(inputFilename, inputDir, outputDir, openOutputFiles, createExcelCharts,
                             remove_stopwords_var, lemmatize_var, vector_size_var, window_var, min_count_var):

    filesToOpen = []

    numFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
    if numFiles == 0:
        mb.showerror(title='Number of files error',
                     message='The selected input directory does NOT contain any file of txt type.\n\nPlease, select a different directory and try again.')
        return

    all_input_docs = []
    for doc in os.listdir(inputDir):
        if doc.endswith('.txt'):
            with open(os.path.join(inputDir, doc), 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
                all_input_docs.append(text)

    sentences = make_sentences(all_input_docs)

    if remove_stopwords_var == True:
        all_sentences = list(remove_stopwords(sentences))
    else:
        all_sentences = list(sentences)

    ## lemmatize
    allowed_postags = ['NOUN', 'ADJ', 'VERB', 'ADV']
    sentences_out = []
    for sent in all_sentences:
        doc = nlp(" ".join(sent))
        if lemmatize_var == True:
            sentences_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
        else:
            sentences_out.append([token for token in doc if token.pos_ in allowed_postags])

    ## train model
    model = gensim.models.Word2Vec(
        sentences=sentences_out,
        vector_size=vector_size_var,
        window=window_var,
        min_count=min_count_var
    )

    word_vectors = model.wv
    words = word_vectors.key_to_index
    word_vector_list = [word_vectors[v] for v in words]

    ## visualization

    pca = PCA(n_components=2)
    xys = pca.fit_transform(word_vector_list)
    xs = xys[:, 0]
    ys = xys[:, 1]

    plot_2d_graph(words, xs, ys)

    fileName = os.path.join(outputDir, "NLP_Gensim_Word2Vec_graph.png")
    plt.savefig(fileName)
    filesToOpen.append(fileName)

    word_vector_csv = pd.DataFrame()
    for v in words:
        word_vector_csv = word_vector_csv.append(pd.Series([v, word_vectors[v]]), ignore_index=True)
    word_vector_csv.columns = ['word', 'vector']

    fileName = os.path.join(outputDir, "NLP_Gensim_Word2Vec_list.csv")
    word_vector_csv.to_csv(fileName, index=False)
    filesToOpen.append(fileName)

    return filesToOpen

###########################################


## functions

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

def plot_2d_graph(words, xs, ys):
    plt.figure(figsize=(8, 6))
    plt.scatter(xs, ys, marker='o')
    for i, v in enumerate(words):
        plt.annotate(v, xy=(xs[i], ys[i]))
    #plt.show()