'''
Written by Mino Cha February 2022

Examples of Usage:

1. Instantiation
    from Stanza_functions_util import stanzaPipeLine, tokenize_stanza_text, tokenize_stanza_text, lemmatize_stanza_word

2. tokenize_stanza_text
    sentences = tokenize_stanza_text(stanzaPipeLine(text))

3. tokenize_stanza_text
    words = tokenize_stanza_text(stanzaPipeLine(text))

4. lemmatize_stanza_word
    lemma = lemmatize_stanza_word(stanzaPipeLine(word))
'''

import sys
import GUI_util
import IO_libraries_util

if not IO_libraries_util.install_all_Python_packages(GUI_util.window,"Stanza_functions_util",['tkinter','stanza']):
    sys.exit(0)

import stanza
try:
    stanza.download('en')
except:
    import IO_internet_util
    IO_internet_util.check_internet_availability_warning("Stanza_functions_util.py (stanza.download(en))")

import IO_internet_util

# should make the Stanza pipeline parametrized by lang selected by user
# @@@
# check internet connection
if IO_internet_util.check_internet_availability_warning("Stanza_functions_util.py"):
    stanzaPipeLine = stanza.Pipeline(lang='en', processors= 'tokenize, lemma')

# in INPUT the function takes a document or sentence or even word as string
#   e.g., "Robert went to Italy on vacation"
# in OUTPUT the function returns a list [] of word tokens
#   e.g., ['Robert', 'went', 'to', 'Italy', 'on', 'vacation']

# similar to lemmatized_stanza_doc except that in this one the list items are lemmatized words
# same as nltk.tokenize.sent_tokenize()
def tokenize_stanza_text(text_to_process):
    tokenized_text_to_process=[]
    for sentence in text_to_process.sentences:
        tokenized_text_to_process = [word.text for word in sentence.words]
        # you get the same result by using tokens instead or words
        # tokenized_text_to_process = [token.text for token in sentence.tokens]
    return tokenized_text_to_process

def sentence_split_stanza_text(text_to_process, return_text=True):
    if return_text is False:
        return [sentence for sentence in text_to_process.sentences]
    else:
        return [sentence.text for sentence in text_to_process.sentences]
    return sentences

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
    except:
        if return_empty_string:
            return ''
        else:
            return text_to_process.sentences[0].words[0].text

# in INPUT the function takes a document text or sentence or even word as strings
#   e.g., 'Robert went to Italy for vacation'
#   BUT MANIPULATED BY THE stanzaPipeLine function
# in OUTPUT the function returns a list [] of the lemmatized document, sentence or word
#   e.g., ['Robert', 'go', 'to', 'Italy', 'on', 'vacation']
# similar to tokenized_stanza_doc except that in this one the list items are tokenized (NOT lemmatized) words
# for text_to_process.sentences to work, the calling function must first have
#   from Stanza_functions_util import stanzaPipeLine, lemmatize_stanza_doc
# must be called as lemmatize_stanza_doc(stanzaPipeLine(text))
def lemmatize_stanza_doc(text_to_process, return_string=False, exact_word_match = True):
    if return_string:
        lemmatized_text_to_process=''
    else:
        lemmatized_text_to_process=[]
    punctuation_set = ',;.?!'
    # for text_to_process.sentences to work, the calling function must first have
    #   from Stanza_functions_util import stanzaPipeLine, lemmatize_stanza_doc
    # must be called as lemmatize_stanza_doc(stanzaPipeLine(text))

    for sentence in text_to_process.sentences:
        for word in sentence.words:
            if return_string:
                if word.lemma in punctuation_set:
                    lemmatized_text_to_process = lemmatized_text_to_process.rstrip()
                    lemmatized_text_to_process = lemmatized_text_to_process + word.lemma
                else:
                    lemmatized_text_to_process = lemmatized_text_to_process + ' ' + word.lemma
            else:
                lemmatized_text_to_process.append(word.lemma)
                # if not exact_word_match:
                #     lemmatized_text_to_process.append(word.lemma)
                # else:
                #     # remove all punctuation and returns a list for exact_word_match
                #     if word.lemma in punctuation_set:
                #         continue
    return lemmatized_text_to_process
    # the function above in a text_to_process such as "Mao Zedong went to Taiwan for vacation." return Mao Zedong as lower case mao zedong
    # in theis other way of lemmatizing
    # en_nlp = stanza.Pipeline('en')
    # end_doc = en_nlp(text_to_process)
    # for i, sent in enumerate(end_doc.sentences):
    #     for word in sent.words:
    #         print(word.lemma)
