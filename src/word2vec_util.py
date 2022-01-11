import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"word2vec_main.py",['os','tkinter', 'gensim', 'spacy', 'plotly'])==False:
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
                        remove_stopwords_var, lemmatize_var, sg_menu_var, vector_size_var, window_var, min_count_var,
                        word_vector=None):

    filesToOpen = []

    numFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
    if numFiles == 0:
        mb.showerror(title='Number of files error',
                     message='The selected input directory does NOT contain any file of txt type.\n\nPlease, select a different directory and try again.')
        return

    ## list for csv file
    word = []
    lemmatized_word = []
    unlemmatized_word =[]
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
                print('importing ' + str(dId) + '/' + str(numFiles) + ' file')
                documentID.append(dId)
                document.append(os.path.join(inputDir, doc))
                all_input_docs[dId] = text

    document_df = pd.DataFrame({'documentID': documentID, 'document': document})
    document_df = document_df.astype('str')

    documentID = []
    print('tokenizing...')
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
    sentence_df = sentence_df.astype(str)

    if remove_stopwords_var == True:
        print('removing stopwords..')
        ## sentence_df = remove_stopwords_df(sentence_df)
        word_list = list(remove_stopwords(word_list))
    else:
        word_list = list(word_list)

    ## lemmatize
    if lemmatize_var == True:
        print('lemmatizing...')

    sentences_out = []
    for word_in_sent in word_list:
        doc = nlp(" ".join(word_in_sent))
        if lemmatize_var == True:
            sentences_out.append([token.lemma_ for token in doc])
            unlemmatized_word.extend([token for token in doc])
            lemmatized_word.extend([token.lemma_ for token in doc])
        else:
            sentences_out.append([token for token in doc])

    word_df = pd.DataFrame({'word': unlemmatized_word})
    if (len(lemmatized_word)>0):
        word_df['lemmatized_word'] = lemmatized_word

    word_df = word_df.astype(str)
    word_df = word_df.drop_duplicates()
    sent_word_df = pd.merge(sentence_df, word_df, on='word', how='inner')
    sent_word_df = sent_word_df.astype(str)


    if sg_menu_var == 'CBOW':
        sg_var = 0
    else:
        sg_var = 1

    print('learning architecture: ', sg_menu_var)

    ## train model
    print('training word2vec model...')
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
    print('visualizing...')

    #pca = PCA(n_components=2)
    #xys = pca.fit_transform(word_vector_list)
    tsne = TSNE(n_components=2)
    xys = tsne.fit_transform(word_vector_list)

    xs = xys[:, 0]
    ys = xys[:, 1]
    word = words.keys()

    tsne_df = pd.DataFrame({'word': word, 'x': xs, 'y': ys})
    fig = plot_interactive_graph(tsne_df)

    ## saving output
    print('saving output...')

    ### graph
    fileName = os.path.join(outputDir, "NLP_Gensim_Word2Vec_graph.html")
    fig.write_html(fileName)
    filesToOpen.append(fileName)

    ### csv file
    word_vector_df = pd.DataFrame()
    for v in words:
        word_vector_df = word_vector_df.append(pd.Series([v, word_vectors[v]]), ignore_index=True)

    if(lemmatize_var == True):
        word_vector_df.columns = ['lemmatized_word', 'vector']
        word_vector_df = word_vector_df.astype(str)
        sent_word_vector = pd.merge(word_vector_df, sent_word_df, on='lemmatized_word', how='inner')
    else:
        word_vector_df.columns = ['word', 'vector']
        word_vector_df = word_vector_df.astype(str)
        sent_word_vector = pd.merge(word_vector_df, sent_word_df, on='word', how='inner')

    sent_word_vector = sent_word_vector.astype(str)
    result_df = pd.merge(document_df, sent_word_vector, on='documentID', how='inner')
    result_df = result_df.sort_values(by=["documentID","sentenceID"])

    if (lemmatize_var == True):
        result_df = result_df[["word", "lemmatized_word", "vector", "sentenceID", "sentence", "documentID", "document"]]
    else:
        result_df = result_df[["word", "vector", "sentenceID", "sentence", "documentID", "document"]]

    fileName = os.path.join(outputDir, "NLP_Gensim_Word2Vec_list.csv")
    result_df.to_csv(fileName, index=False)
    filesToOpen.append(fileName)

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
        if row['word'] in stop_words:
            sentence_df.drop(idx, inplace=True)
    return sentence_df

def plot_interactive_graph(tsne_df):
    fig = px.scatter(tsne_df, x = "x", y = "y",
                     hover_name = "word")
    return fig