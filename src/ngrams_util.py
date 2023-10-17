##not needed

import IO_csv_util
import string
punctuation = string.punctuation
import stanza
nlp = stanza.Pipeline(lang='en', processors='tokenize')
global cnter
cnter = 0
def readandsplit(filename,excludePunctuation, excludeDeterminants, excludeStopWords, nFiles):
    global cnter
    head, tail = os.path.split(filename)
    Sentence_ID = 0
    doc_ngramsList = []
    print("   Processing file " + str(cnter+1) + "/" + str(nFiles) + ' ' + tail)
    with open(filename,'r', encoding='utf_8', errors='ignore') as f:
        out = f.read()
    if excludePunctuation:
        out = out.translate(str.maketrans('', '', punctuation))
    # if excludeDeterminants:
    #     words = excludeStopWords_list(words)
    #     filtered_words = [word for word in words if word.isalpha()]  # strip out words with punctuation
    # if excludeStopWords:
    #     words = excludeStopWords_list(words)
    #     filtered_words = [word for word in words if word.isalpha()]  # strip out words with punctuation

    doc = nlp(''.join(out))
    cnter +=1
    return [token.text for sentence in doc.sentences for token in sentence.tokens]

# Stanza typically runs VERY fast as long as we don't repeatedly invoke a call on its pipeline.
# It seems to be allocating some cache that speeds it up.
import os

from collections import Counter

def find_ngrams(words, n):
    return [tuple(words[i:i+n]) for i in range(len(words)-n+1)]
import pandas as pd

def find_frequencies(sentences_ngrams, major_ngrams,files):
    major_freq = Counter(major_ngrams)
    all_records = []
    for idx, sentence_ngrams in enumerate(sentences_ngrams):
        sent_freq = Counter(sentence_ngrams)
        for ngram, count in sent_freq.items():
            if ngram in major_freq:
                record = {
                    'ngram': ' '.join(ngram),
                    'Frequency in Document': count,
                    'Frequency in Corpus': major_freq[ngram],
                    'Document ID': idx+1,
                    'Document': IO_csv_util.dressFilenameForCSVHyperlink(files[idx])
                }
                all_records.append(record)

    # Now, 'all_records' is a list of dictionaries, where each dictionary is a record
    # that can be directly used to create a DataFrame.
    df = pd.DataFrame(all_records)
    return df

def operate(documents,files, ngramsNumber):
    # need to rename 1-grams, 2-grams, 3-grams, ... 6-grams
    onegram = []
    bigrams = []
    trigrams = []
    for document in documents:
        # need to rename 1-grams, 2-grams, 3-grams, ... 6-grams
        onegram.extend(find_ngrams(document,1))
        bigrams.extend(find_ngrams(document, 2))
        trigrams.extend(find_ngrams(document, 3))
    documents_onegram = [find_ngrams(document,1) for document in documents]
    documents_bigrams = [find_ngrams(document, 2) for document in documents]
    documents_trigrams = [find_ngrams(document, 3) for document in documents]
    onegram_freq = find_frequencies(documents_onegram, onegram,files)
    bigram_freq = find_frequencies(documents_bigrams, bigrams,files)
    trigram_freq = find_frequencies(documents_trigrams, trigrams,files)
    return onegram_freq,bigram_freq,trigram_freq