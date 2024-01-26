'''
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
'''

import stanza
try:
    stanza.download('en')
except:
    import IO_internet_util
    IO_internet_util.check_internet_availability_warning("Stanza_functions_util.py (stanza.download(en))")

import IO_internet_util

# check internet connection
if IO_internet_util.check_internet_availability_warning("Stanza_functions_util.py"):
    stanzaPipeLine = stanza.Pipeline(lang='en', processors= 'tokenize, lemma')

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
    except:
        # if doc=[]
        return ''
