import logging
import string
from pathlib import Path

import IO_csv_util

_WORD_LISTS_DIR = Path(__file__).parent.parent.parent / "lib" / "wordLists"

punctuation = string.punctuation
from model_cache import get_stanza_pipeline

#     if frequency==1: # hapax


def process_hapax(ngramsList, frequency, excludePunctuation):
    if excludePunctuation:
        freq_col = 1
    else:
        freq_col = 2
    if frequency == 1:  # hapax
        # for hapax legomena keep rows with frequency=1 only; exclude items with frequency>1, i.e. i[1] > 1
        ngramsList_new = list(filter(lambda a: a[freq_col] == 1, ngramsList))
        ngramsList = ngramsList_new
    return ngramsList


import re


def removeart(original_sentence):
    fin = open(_WORD_LISTS_DIR / "articles.txt")
    articles = list(set(fin.read().splitlines()))
    # from Stanford CoreNLP calculation
    # Create a regex pattern for the determiners, case-insensitive
    # The \b ensures the match is for whole words only, avoiding partial matches within words
    dets_pattern = r"\b(?:" + "|".join(map(re.escape, articles)) + r")\b\s*"
    # Remove determiners along with the following spaces
    # We are using the \s* in the regex pattern to match zero or more whitespace characters following the determiner
    filtered_sentence = re.sub(dets_pattern, "", original_sentence, flags=re.IGNORECASE)
    # Stripping leading/trailing whitespace
    final_sentence = filtered_sentence.strip()
    return final_sentence


# ENGLISH DETERMINERS:
# Definite article: the.
# Indefinite articles: a, an.
# Demonstratives: this, that, these, those.
# Pronouns and possessive determiners: my, your, his, her, its, our, their.
# Quantifiers: all, few, little, much, many, lot, most, some, any, enough, several.
# Distributives: all, both, half, either, neither, each, every
# Difference words: other, another
# Pre - determiners: such, what, rather, quite
# Numbers: one, ten, thirty.


# determiners typically include numbers such as one, two, three,... but we cannot list them all and should use a function
def removedt(original_sentence):
    fin = open(_WORD_LISTS_DIR / "determiners.txt")
    determiners = list(set(fin.read().splitlines()))

    # from Stanford CoreNLP calculation
    # Create a regex pattern for the determiners, case-insensitive
    # The \b ensures the match is for whole words only, avoiding partial matches within words
    dets_pattern = r"(\b(?:" + "|".join(map(re.escape, determiners)) + r")\b)\s*"
    # Remove determiners along with the following spaces
    # We are using the \s* in the regex pattern to match zero or more whitespace characters following the determiner
    filtered_sentence = re.sub(dets_pattern, " ", original_sentence, flags=re.IGNORECASE)
    # Stripping leading/trailing whitespace
    final_sentence = filtered_sentence.strip()
    return final_sentence


def removestop(original_sentence):
    fin = open(_WORD_LISTS_DIR / "stopwords.txt")
    stops = list(set(fin.read().splitlines()))
    dets_pattern = r"\b(?:" + "|".join(map(re.escape, stops)) + r")\b\s*"
    filtered_sentence = re.sub(dets_pattern, "", original_sentence, flags=re.IGNORECASE)
    final_sentence = filtered_sentence.strip()
    return final_sentence


def readandsplit(
    filename, excludePunctuation, excludeArticles, excludeDeterminers, excludeStopWords, nFiles, lemmatize, index
):
    head, tail = os.path.split(filename)
    logger.info("   Processing file " + str(index + 1) + "/" + str(nFiles) + " " + tail)
    with open(filename, encoding="utf_8", errors="ignore") as f:
        out = f.read()
    if excludePunctuation:
        out = out.translate(str.maketrans("", "", punctuation))
    if excludeArticles:
        out = removeart(out)
    if excludeDeterminers:
        out = removedt(out)
    if excludeStopWords:
        out = removestop(out)

    # Stanza typically runs VERY fast as long as we don't repeatedly invoke a call
    # on its pipeline; the model cache reuses one instance across files and jobs.
    if not lemmatize:
        nlp = get_stanza_pipeline(lang="en", processors="tokenize")
        doc = nlp("".join(out))
        return [token.text for sentence in doc.sentences for token in sentence.tokens]
    else:
        nlp = get_stanza_pipeline(lang="en", processors="tokenize,lemma")
        doc = nlp("".join(out))
        return [token.lemma for sentence in doc.sentences for token in sentence.words]


import os
from collections import Counter


def find_ngrams(words, n):
    return [tuple(words[i : i + n]) for i in range(len(words) - n + 1)]


import pandas as pd

logger = logging.getLogger(__name__)


def find_frequencies(sentences_ngrams, major_ngrams, files):
    major_freq = Counter(major_ngrams)
    all_records = []
    for idx, sentence_ngrams in enumerate(sentences_ngrams):
        sent_freq = Counter(sentence_ngrams)
        for ngram, count in sent_freq.items():
            if ngram in major_freq:
                record = {
                    "ngram": " ".join(ngram),
                    "Frequency in Document": count,
                    "Frequency in Corpus": major_freq[ngram],
                    "Document ID": idx + 1,
                    "Document": IO_csv_util.dressFilenameForCSVHyperlink(files[idx]),
                }
                all_records.append(record)

    # Now, 'all_records' is a list of dictionaries, where each dictionary is a record
    # that can be directly used to create a DataFrame.
    df = pd.DataFrame(all_records)
    return df


def operateongram(documents, files, ngramsNumber):
    ngrams = []
    for document in documents:
        ngrams.extend(find_ngrams(document, ngramsNumber))
    documents_ngram = [find_ngrams(document, ngramsNumber) for document in documents]
    ngram_freq = find_frequencies(documents_ngram, ngrams, files)
    logger.info("%s gram of your corpus is complete.", ngramsNumber)
    return ngram_freq


def hapax(data, hapax_words):
    if not hapax_words:
        return data[data["Frequency in Corpus"] == 1]
    else:
        data = data[data["ngram"].str.contains(r"[a-zA-Z]", regex=True, na=False)]
        return data[data["Frequency in Corpus"] == 1]


def operate(documents, files, max_ngramsNumber, hapax_words):
    ngram_freq_results = []
    hapax_result = None
    for n in range(1, max_ngramsNumber + 1):
        ngram_freq = operateongram(documents, files, n)
        ngram_freq_results.append(ngram_freq)
        if n == 1:
            hapax_result = hapax(ngram_freq, hapax_words)
    return ngram_freq_results, hapax_result
