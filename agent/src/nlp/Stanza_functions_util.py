"""
Written by Mino Cha February 2022

Examples of Usage:

1. Instantiation
    from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza

2. sent_tokenize_stanza
    sentences = sent_tokenize_stanza(stanzaPipeLine(text))

3. word_tokenize_stanza
    words = word_tokenize_stanza(stanzaPipeLine(text))

4. lemmatize_stanza
    lemma = lemmatize_stanza(stanzaPipeLine(word))
"""

import stanza

try:
    stanza.download("en")
except Exception:
    import IO_internet_util

    IO_internet_util.check_internet_availability_warning("Stanza_functions_util.py (stanza.download(en))")

import IO_internet_util

# check internet connection
if IO_internet_util.check_internet_availability_warning("Stanza_functions_util.py"):
    stanzaPipeLine = stanza.Pipeline(lang="en", processors="tokenize, lemma")


# returns list of word tokens
# same as nltk.tokenize.word_tokenize()
def word_tokenize_stanza(doc):
    lst = []
    for sentence in doc.sentences:
        [lst.append(token.text) for token in sentence.tokens]
    return lst


# returns list of sentence tokens
# same as nltk.tokenize.sent_tokenize()
def sent_tokenize_stanza(doc, return_text=True):
    if return_text is False:
        return [sentence for sentence in doc.sentences]
    else:
        return [sentence.text for sentence in doc.sentences]


# returns a single lemmatized word. input should be a single word.
# same as nltk.stem.wordnet.WordNetLemmatizer().lemmatize(text)
# https://stanfordnlp.github.io/stanza/lemma.html
# https://github.com/stanfordnlp/stanza/blob/main/stanza/models/lemmatizer.py
def lemmatize_stanza(doc):
    try:
        return doc.sentences[0].words[0].lemma
    except Exception:
        # if doc=[]
        return ""


# returns a single lemmatized word. input should be a single word.
# https://stanfordnlp.github.io/stanza/lemma.html
# https://github.com/stanfordnlp/stanza/blob/main/stanza/models/lemmatizer.py

# in INPUT text_to_process can be anything, an entire document, a sentence, or a word
#   typically it is a single word
#   e.g., 'Robert went to Italy for vacation'
# in OUTPUT, whatever the input, the function returns a STRING of a lemmatized single word
#   (regardless of input, always the first word of the first sentence of a document)
#   e.g., ['Robert']


# must be called as lemmatize_stanza_word(stanzaPipeLine(token))
# https://stanfordnlp.github.io/stanza/lemma.html
def lemmatize_stanza_word(text_to_process, return_empty_string=True):
    try:
        return text_to_process.sentences[0].words[0].lemma
    except Exception:
        if return_empty_string:
            return ""
        else:
            return text_to_process.sentences[0].words[0].text


# in INPUT the function takes a document text or sentence or even word as strings
#   e.g., 'Robert went to Italy for vacation'
#   BUT MANIPULATED BY THE stanzaPipeLine function
# in OUTPUT the function returns a list [] of the lemmatized document, sentence or word
#   e.g., ['Robert', 'go', 'to', 'Italy', 'on', 'vacation']
# similar to tokenized_stanza_doc except that in this one the list items are tokenized (NOT lemmatized) words
# for text_to_process.sentences to work, the calling function must first have
# must be called as lemmatize_stanza_doc(stanzaPipeLine(text))
def lemmatize_stanza_doc(text_to_process, return_string=False, exact_word_match=True):
    if return_string:
        lemmatized_text_to_process = ""
    else:
        lemmatized_text_to_process = []
    punctuation_set = ",;.?!"
    # for text_to_process.sentences to work, the calling function must first have
    # must be called as lemmatize_stanza_doc(stanzaPipeLine(text))

    for sentence in text_to_process.sentences:
        for word in sentence.words:
            if return_string:
                if word.lemma in punctuation_set:
                    lemmatized_text_to_process = lemmatized_text_to_process.rstrip()
                    lemmatized_text_to_process = lemmatized_text_to_process + word.lemma
                else:
                    lemmatized_text_to_process = lemmatized_text_to_process + " " + word.lemma
            else:
                lemmatized_text_to_process.append(word.lemma)
                # if not exact_word_match:
                #     # remove all punctuation and returns a list for exact_word_match
                #     if word.lemma in punctuation_set:
                #         continue
    return lemmatized_text_to_process
    # the function above in a text_to_process such as "Mao Zedong went to Taiwan for vacation." return Mao Zedong as lower case mao zedong
    # in theis other way of lemmatizing
    # for i, sent in enumerate(end_doc.sentences):
    #     for word in sent.words:


# in INPUT the function takes a document or sentence or even word as string
#   e.g., "Robert went to Italy on vacation"
# in OUTPUT the function returns a list [] of word tokens
#   e.g., ['Robert', 'went', 'to', 'Italy', 'on', 'vacation']


# similar to lemmatized_stanza_doc except that in this one the list items are lemmatized words
# same as nltk.tokenize.sent_tokenize()
def tokenize_stanza_text(text_to_process):
    tokenized_text_to_process = []
    for sentence in text_to_process.sentences:
        tokenized_text_to_process = [word.text for word in sentence.words]
        # you get the same result by using tokens instead or words
    return tokenized_text_to_process


def sentence_split_stanza_text(text_to_process, return_text=True):
    if return_text is False:
        return [sentence for sentence in text_to_process.sentences]
    else:
        return [sentence.text for sentence in text_to_process.sentences]
