##not needed

import IO_csv_util
import string
punctuation = string.punctuation
import stanza

global called
global nlp

called = 0

#     if frequency==1: # hapax
#         hapax_label="_hapax_"
#         hapax_header=" (hapax)"
#         ngramsNumber=1 # if hapax, there is no point computing higher-level n-grams
#     else:
#         hapax_label=""
#         hapax_header=""

def process_hapax(ngramsList, frequency, excludePunctuation):
    if excludePunctuation:
        freq_col = 1
    else:
        freq_col = 2
    if frequency == 1:  # hapax
        # for hapax legomena keep rows with frequency=1 only; exclude items with frequency>1, i.e. i[1] > 1
        ngramsList_new=list(filter(lambda a: a[freq_col] == 1, ngramsList))
        ngramsList=ngramsList_new
    return ngramsList

import re


def removedt(original_sentence):
    determiners = [
        'a', 'all', 'an', 'another', 'any', 'both', 'each', 'either',
        'every', 'half', 'neither', 'no', 'some', 'that', 'the',
        'these', 'this', 'those'
    ]
    # from Stanford CoreNLP calculation
    # Create a regex pattern for the determiners, case-insensitive
    # The \b ensures the match is for whole words only, avoiding partial matches within words
    dets_pattern = r'\b(?:' + '|'.join(map(re.escape, determiners)) + r')\b\s*'
    # Remove determiners along with the following spaces
    # We are using the \s* in the regex pattern to match zero or more whitespace characters following the determiner
    filtered_sentence = re.sub(dets_pattern, "", original_sentence, flags=re.IGNORECASE)
    # Stripping leading/trailing whitespace
    final_sentence = filtered_sentence.strip()
    return final_sentence

def removestop(original_sentence):
    fin = open('../lib/wordLists/stopwords.txt', 'r')
    stops = list(set(fin.read().splitlines()))
    dets_pattern = r'\b(?:' + '|'.join(map(re.escape, stops)) + r')\b\s*'
    filtered_sentence = re.sub(dets_pattern, "", original_sentence, flags=re.IGNORECASE)
    final_sentence = filtered_sentence.strip()
    return final_sentence
def readandsplit(filename, excludePunctuation, excludeDeterminants, excludeStopWords, nFiles,lemmatize,index):

    global called
    global nlp
    head, tail = os.path.split(filename)
    Sentence_ID = 0
    doc_ngramsList = []
    print("   Processing file " + str(index+1) + "/" + str(nFiles) + ' ' + tail)
    with open(filename,'r', encoding='utf_8', errors='ignore') as f:
        out = f.read()
    if excludePunctuation:
        out = out.translate(str.maketrans('', '', punctuation))
    if excludeDeterminants:
        out = removedt(out)
    if excludeStopWords:
        out = removestop(out)

    # if excludeDeterminants:
    #     words = excludeStopWords_list(words)
    #     filtered_words = [word for word in words if word.isalpha()]  # strip out words with punctuation
    # if excludeStopWords:
    #     words = excludeStopWords_list(words)
    #     filtered_words = [word for word in words if word.isalpha()]  # strip out words with punctuation
    if not lemmatize:
        if not called:
            nlp = stanza.Pipeline(lang='en', processors='tokenize')
            called = 1
        doc = nlp(''.join(out))
        if index + 1 == nFiles:
            called = 0
        return [token.text for sentence in doc.sentences for token in sentence.tokens]
    else:
        if not called:
            nlp = stanza.Pipeline(lang='en', processors='tokenize,lemma')
            called = 1
        doc = nlp(''.join(out))
        if index + 1 == nFiles:
            called = 0
        return [token.lemma for sentence in doc.sentences for token in sentence.words]



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

def operateongram(documents,files,ngramsNumber):
    ngrams = []
    for document in documents:
        ngrams.extend(find_ngrams(document,ngramsNumber))
    documents_ngram = [find_ngrams(document, ngramsNumber) for document in documents]
    ngram_freq = find_frequencies(documents_ngram, ngrams, files)
    print(ngramsNumber, "gram of your corpus is complete.")
    return ngram_freq

def hapax(data,hapax_words):
    if not hapax_words:
        return data[data['Frequency in Corpus']==1]
    else:
        data = data[data['ngram'].str.contains(r'[a-zA-Z]', regex=True, na=False)]
        return data[data['Frequency in Corpus']==1]

def operate(documents, files, max_ngramsNumber,hapax_words):
    ngram_freq_results = []
    hapax_result = None
    for n in range(1, max_ngramsNumber + 1):
        ngram_freq = operateongram(documents, files, n)
        ngram_freq_results.append(ngram_freq)
        if n==1:
            hapax_result = hapax(ngram_freq,hapax_words)
    return ngram_freq_results, hapax_result

