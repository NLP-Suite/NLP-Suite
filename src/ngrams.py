import functools
import time

def timer(func):
    """A decorator that prints how long a function took to execute."""
    @functools.wraps(func)  # Preserves function meta data
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer



import stanza
nlp = stanza.Pipeline(lang='en', processors='tokenize')

@timer
def readandsplit(filename):
    with open(filename,'r') as f:
        out = f.read()
    doc = nlp(''.join(out))
    return [token.text for sentence in doc.sentences for token in sentence.tokens]
# Stanza typically runs VERY fast as long as we don't repeatedly invoke a call on its pipeline.
# It seems to be allocating some cache that speeds it up.
import os
files = [i for i in os.listdir(os.getcwd()) if '.txt' in i] # malleable line, to be replaced
files.sort()
documents = [readandsplit(i) for i in files]
from collections import Counter
@timer
def find_ngrams(words, n):
    return [tuple(words[i:i+n]) for i in range(len(words)-n+1)]
import pandas as pd

@timer
def find_frequencies(sentences_ngrams, major_ngrams):
    major_freq = Counter(major_ngrams)
    all_records = []

    for idx, sentence_ngrams in enumerate(sentences_ngrams):
        sent_freq = Counter(sentence_ngrams)

        for ngram, count in sent_freq.items():
            if ngram in major_freq:
                record = {
                    'Document ID': idx,
                    'Document': files[idx],
                    'ngram': ' '.join(ngram),
                    'Frequency in Document': count,
                    'Frequency in Corpus': major_freq[ngram]
                }
                all_records.append(record)

    # Now, 'all_records' is a list of dictionaries, where each dictionary is a record
    # that can be directly used to create a DataFrame.
    df = pd.DataFrame(all_records)
    return df
onegram = []
bigrams = []
trigrams = []
for document in documents:
    onegram.extend(find_ngrams(document,1))
    bigrams.extend(find_ngrams(document, 2))
    trigrams.extend(find_ngrams(document, 3))
documents_onegram = [find_ngrams(document,1) for document in documents]
documents_bigrams = [find_ngrams(document, 2) for document in documents]
documents_trigrams = [find_ngrams(document, 3) for document in documents]
onegram_freq = find_frequencies(documents_onegram, onegram)
bigram_freq = find_frequencies(documents_bigrams, bigrams)
trigram_freq = find_frequencies(documents_trigrams, trigrams)
trigram_freq.to_csv("trigrams.csv")
bigram_freq.to_csv("bigrams.csv")
onegram_freq.to_csv("onegram.csv")
