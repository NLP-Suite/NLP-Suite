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

nlp = spacy.load('en_core_web_sm')

def run_Gensim_word2vec(inputFilename, inputDir, outputDir, openOutputFiles, createExcelCharts,
                             remove_stopwords_var, lemmatize_var, vector_size_var, window_var, min_count_var):

    filesToOpen = []

    numFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
    if numFiles == 0:
        mb.showerror(title='Number of files error',
                     message='The selected input directory does NOT contain any file of txt type.\n\nPlease, select a different directory and try again.')
        return

    ## list for csv file
    word = []
    lemmatized_word = []
    vector = []
    sentenceID = []
    sentence = []
    documentID = []
    document = []

    ## word list for word2vec
    word_list = []

    all_input_docs = {}
    dId = 0
    for doc in os.listdir(inputDir):
        if doc.endswith('.txt'):
            with open(os.path.join(inputDir, doc), 'r', encoding='utf-8', errors='ignore') as file:
                dId += 1
                text = file.read()
                documentID.append(dId)
                document.append(os.path.join(inputDir, doc))
                all_input_docs[dId] = text

    document_df = pd.DataFrame({'documentID': documentID, 'document': document})

    documentID = []
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

    sentence_df = pd.DataFrame({'word': word, 'sentence': sentence, 'sentenceID': sentenceID, 'documentID': documentID})


    if remove_stopwords_var == True:
        sentence_df = remove_stopwords_df(sentence_df)
        word_list = list(remove_stopwords(word_list))

    else:
        word_list = list(word_list)

    ## lemmatize
    ## allowed_postags = ['NOUN', 'ADJ', 'VERB', 'ADV']
    sentences_out = []
    for word_in_sent in word_list:
        doc = nlp(" ".join(word_in_sent))
        if lemmatize_var == True:
            sentences_out.append([token.lemma_ for token in doc])
            lemmatized_word.extend([token.lemma_ for token in doc])
        else:
            sentences_out.append([token for token in doc])

    if (len(lemmatized_word)>0):
        sentence_df['lemmatized_word'] = lemmatized_word

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

    '''
    fileName = os.path.join(outputDir, "NLP_Gensim_Word2Vec_list.csv")
    word_vector_csv.to_csv(fileName, index=False)
    filesToOpen.append(fileName)
    
    '''

    combined_df = pd.merge(document_df, sentence_df, on='documentID', how='inner')
    result_df = pd.merge(combined_df, word_vector_csv, on='word', how='inner')

    fileName = os.path.join(outputDir, "NLP_Gensim_Word2Vec_list.csv")
    result_df.to_csv(fileName, index=False)
    filesToOpen.append(fileName)

    return filesToOpen

###########################################


## functions

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
        if row['word'] in stop_words:
            sentence_df.drop(idx, inplace=True)
    return sentence_df

def plot_2d_graph(words, xs, ys):
    plt.figure(figsize=(8, 6))
    plt.scatter(xs, ys, marker='o')
    for i, v in enumerate(words):
        plt.annotate(v, xy=(xs[i], ys[i]))
    #plt.show()