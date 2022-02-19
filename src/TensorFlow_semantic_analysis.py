import os
import nltk.data
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import tensorflow as tf
import tensorflow_hub as hub

from stanza_functions import stanzaPipeLine, sent_tokenize_stanza

# Based on this colab notebook on Semantic Similarity analysis with TensorFlow Hub's Universal Sentence Encoder
# https://colab.research.google.com/github/tensorflow/hub/blob/master/examples/colab/semantic_similarity_with_tf_hub_universal_encoder.ipynb#scrollTo=BnvjATdy64eR 



NYTarticles = dict() # Populate this dictionary with NYT[key] = sentence-level embedding
NYTtxt_files = os.listdir('corpus') 
NYTtxt_files.sort()

# TODO: Change corr_size
corr_size = 40
embedder = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4") # Embedder to convert strings to numbers
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') # Tokenizer to get list of sentences from read string
correlation_matrices = list()

for file in NYTtxt_files: 
    with open(os.path.join('corpus', file)) as f:
        data = f.read()

    # TODO: Level at which encoding happens (word / sentence / paragraph)
    # sentences = tokenizer.tokenize(data) # Convert input string to list of sentences with tokenizer
    sentences = sent_tokenize_stanza(stanzaPipeLine(data))
    
    # TODO: hardcoded, grab first n sentences 
    embed_sentences = sentences[3:23] + sentences[-20:]
    embedding = embedder(embed_sentences) # Embed the sentences
    corr = np.inner(embedding, embedding) # Take the inner product to get correlations
    if corr.shape[0] == corr_size:
        correlation_matrices.append(corr)
    NYTarticles[file[:-4]] = (sentences, embedding, corr) # Save the information

# Parameter to vary the contrast between densities
# The lower the value, the lower the contrast and the higher the value the contrast

# TODO: create slider which varies from 0.5 to 2 for alpha
alpha = 2

# TODO: 21 and 20 depend on the number of sentences selected (corr_size)
tick_labels = np.concatenate([np.arange(1,21, 1), np.arange(-20, 0, 1)])

plt.figure(figsize=(12,10))
aggregate_correlations = alpha**(np.array(correlation_matrices).sum(axis=0) - len(correlation_matrices)*np.eye(corr_size)) # Subtract out diagonals - we already know they are 100% similar
sns.heatmap(aggregate_correlations / len(NYTarticles), 
    xticklabels=tick_labels,
    yticklabels=tick_labels)
plt.xlabel('sentence index')
plt.ylabel('sentence index')
plt.axis('equal')
plt.tight_layout()

plt.title('Aggregate Semantic Similarity', fontsize=16)
plt.savefig('aggregate_corrs.png')
