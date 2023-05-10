# import statements
import matplotlib.pyplot as plt
from WSI_classes import Clusterer, Matcher
import re
from sklearn.cluster import KMeans
import numpy as np
import random
import pickle
from collections import Counter
from tqdm import tqdm
import os
tcache_path = f'{os.getcwd()}/cache'
if not os.path.exists(tcache_path):
    os.makedirs(tcache_path)
os.environ['TRANSFORMERS_CACHE'] = tcache_path
import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "BERT_util2",
                                          ['os', 'transformers', 'csv', 'argparse', 'tkinter', 'time', 'stanza',
                                           'summarizer','sacremoses','contextualSpellCheck','sentencepiece','sentence_transformers', 'tensorflow']) == False:
    sys.exit(0)


from regex import R
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import BertModel, BertTokenizer, BertTokenizerFast, EncoderDecoderModel
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import pandas as pd
import re
import math
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv
import time
import itertools
import stanza
import argparse
import tkinter.messagebox as mb
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
import IO_internet_util


SEED = 0
batch_size = 32
dropout_rate = 0.25
bert_dim = 768

alphabets = "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
digits = "([0-9])"


def get_vocab(text, u_vocab='', top_n=5, min_count=5, add_stopwords=['said']):

    if u_vocab == '':
        pattern = re.compile('[^A-Za-z0-9 ]+')
        text = ' '.join(re.sub(pattern, '', text).split())
        en = spacy.load('en_core_web_sm')
        stopwords = list(en.Defaults.stop_words) + add_stopwords
        u_vocab = Counter([w for w in text.split() if w.lower() not in stopwords])
        u_vocab = [w for w, i in u_vocab.most_common(top_n) if i >= min_count]
    else:
        u_vocab = [w.strip() for w in u_vocab.split(',')]

    return u_vocab


def split_into_sentences(text, docID):

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
    sentences = [(i, s.strip(), docID) for i, s in enumerate(sentences)]

    return sentences


def get_sent(doc, o_path):

    with open(doc, 'r', encoding='utf-8', errors='ignore') as f:
        fullText = f.read().lower()
    fullText.replace('\n', ' ')
    docID = doc.split('/')[-1]
    sentences = split_into_sentences(fullText, docID)
    with open(f'{o_path}/sentences.pickle', 'wb') as f_name:
        pickle.dump(sentences, f_name)

    return sentences, fullText


def get_data(inputFilename, inputDir, Word2Vec_Dir, u_vocab=[], fileType='.txt', configFileName=''):

    docs = {}
    vocabs = {}
    o_paths = {}
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType=fileType,silent=False,configFileName=configFileName)
    for doc in inputDocs:
        # o_path = f'{Word2Vec_Dir}/{doc.split("/")[-1].split(".")[0]}'
        head, tail = os.path.split(doc)
        o_path = Word2Vec_Dir+os.sep+tail[:-4]
        if not os.path.exists(o_path):
            os.makedirs(o_path)
        sentences, fullText = get_sent(doc, o_path)
        vocab = get_vocab(fullText, u_vocab=u_vocab)
        docs[doc] = sentences
        vocabs[doc] = vocab
        o_paths[doc] = o_path

    return docs, vocabs, o_paths


def get_centroids(docs, vocabs, paths, k_range, sample=None):

    #load model
    print('\nStarted word sense induction...\n')
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
    model_name = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True)
    model = Clusterer(tokenizer, model_name)
    for doc in docs:
        sentences = docs[doc]
        vocab = vocabs[doc]
        c_path = f'{paths[doc]}/centroids'
        if not os.path.exists(c_path):
            os.makedirs(c_path)
        #get centroids
        for w in tqdm(vocab, total=len(vocab), desc=f'Generating sense centroids for {doc.split("/")[-1]}...'):
            if sample is None:
                seq = [tpl for tpl in sentences if w in tpl[1]]
            else:
                seq = random.sample([tpl for tpl in sentences if tpl[1]], sample)
            batched_data, batched_words, batched_masks, batched_users = model.get_batches(seq, batch_size)
            embeddings, do_wordpiece = model.get_embeddings(batched_data, batched_words, batched_masks, batched_users, w)
            data = model.group_wordpiece(embeddings, w, do_wordpiece)
            centroids = model.cluster_embeddings(data, k_range, w, doc, lamb=10000)
            np.save(f'{c_path}/{w}.npy', centroids)


def match_embeddings(docs, vocabs, paths, added_centroids=None):

    #load model
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
    model_name = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True)
    model = Matcher(tokenizer, model_name)
    for doc in tqdm(docs, total=len(docs), desc='Matching...'):
        sentences = docs[doc]
        vocab = vocabs[doc]
        o_path = f'{paths[doc]}'
        #load centroids
        centroids_d = model.load_centroids(vocab, paths[doc])
        if added_centroids is None:
            outfile = open(f'{o_path}/senses', 'w')
        else:
            outfile = open(f'{o_path}/added_senses_{added_centroids[0]}_{added_centroids[1]}', 'w')
        seq = []
        for w in vocab:
            seq += [tpl for tpl in sentences if w in tpl[1]]
        batched_data, batched_words, batched_masks, batched_users = model.get_batches(seq, batch_size)
        model.get_embeddings_and_match(batched_data, batched_words, batched_masks, batched_users, centroids_d, o_path)
    print('\nWord sense induction finished. Producing output files...\n')


def get_cluster_sentences(docs, paths):

    s_paths = []
    for doc in docs:
        i_path = paths[doc]
        with open(f'{i_path}/senses', 'r') as f:
            tokens = f.read().split('\n')[:-1]
        with open(f'{i_path}/sentences.pickle', 'rb') as f:
            sentences = pickle.load(f)
#        o_path = f'{i_path}/clusters'
#        if not os.path.exists(o_path):
#            os.makedirs(o_path)
        senses = list(set([tok.split('\t')[-1] for tok in tokens]))
        vocab = list(set([tok.split('\t')[1] for tok in tokens]))
        tokens = [tok.split('\t') for tok in tokens]
        d = {}
        for w in vocab:
            d[w] = {}
            w_path = f'{i_path}/{w}'
            if not os.path.exists(w_path):
                os.makedirs(w_path)
            doc = open(f'{w_path}/{w}_clusters.txt', 'w')
            s_paths.append(f'{w_path}/{w}_clusters.txt')
            for s in senses:
                doc.write(f'\n\n{s}\n')
                occs = [tok for tok in tokens if tok[-1] == s and tok[1] == w]
                sents = list(set([sentences[int(tok[0])][1] for tok in occs]))
                d[w][s] = sents
                doc.write('\n'.join(sents))
        with open(f'{i_path}/d.pickle', 'wb') as f:
            pickle.dump(d, f)

    return s_paths


def main():

    with open('/home/gog/work/NLP-Suite/lib/sampleData/Bunin - Gentle breath.txt', 'r') as f:
        text = f.read().lower()
    vocab =  get_vocab(text, vocab=['olia'])
    print(vocab)


if __name__ == '__main__':
    main()

