"""What the topic modelers (Gensim and MALLET) say about corpus size. Pure: no GUI, no NLP imports."""

# How few documents is too few, and what to say about it.
#
# The old wording was "Topic modeling requires a large number of files (in the hundreds at least) to
# produce valid results", with a default-No dialog under 50 files. Two things wrong with it. The
# number is not a property of the method: a file is not a fixed quantity of text, and twenty long
# documents carry more evidence than two thousand tweets - MALLET's own tutorial corpus is under
# twenty documents. And it BLOCKED, on the strength of that number, work the user had asked for.
#
# What is genuinely true is narrower. LDA estimates topic-word distributions, which depend on the
# total amount of text, and per-document topic proportions, which are estimated per document - so
# with very few documents those proportions are noisy and the fitted topics become unstable: run it
# twice with different random seeds and the topics move. That instability is the real risk, and the
# remedy is the one the TIPS already gives - split long documents into sections, so each becomes a
# document - not a file count.
#
# So: an ERROR only where the method has nothing to work with, and ADVICE otherwise. See
# TIPS_NLP_Topic modeling and corpus size.pdf.
_FEW_DOCUMENTS = 50


def corpus_size_advice(numFiles):
    """(level, message) for a corpus of *numFiles* documents. level is 'error', 'advice' or ''.

    Separated from the dialogs so the judgement can be read and tested on its own.
    """
    if numFiles == 0:
        return 'error', ('The selected input directory contains no .txt files.\n\n'
                         'Please select a different directory and try again.')
    if numFiles == 1:
        return 'error', (
            'The selected input directory contains a single .txt file.\n\n'
            'Topic modeling works by comparing how words co-occur ACROSS documents, so it needs '
            'more than one. With a single file there is nothing to compare and the result would '
            'simply describe that file.\n\n'
            'If your text is one long document, split it into sections - chapters, articles, '
            'speeches - and use those as your documents. That is standard practice, not a '
            'workaround: it is how book-length texts are normally prepared for topic modeling. '
            'The NLP Suite\'s File Splitter will do it.')
    if numFiles < _FEW_DOCUMENTS:
        return 'advice', (
            'The selected input directory contains %d .txt files.\n\n'
            'This will run. What to watch for: topics are estimated per document as well as from '
            'the text overall, so with few documents the topics can shift from one run to the next. '
            'Check that yours hold before relying on them - run it twice and see whether the same '
            'topics come back.\n\n'
            'What matters is the amount of text and how it is divided, not the number of files. A '
            'few long documents carry more than many very short ones. If your documents are long, '
            'splitting them into sections gives the model more to compare and usually steadies the '
            'topics.\n\n'
            'See the TIPS file "Topic modeling and corpus size".' % numFiles)
    return '', ''
