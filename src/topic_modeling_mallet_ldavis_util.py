"""MALLET's topic model in the pyLDAvis view - the page the Gensim topic modeling tool writes.

MALLET's train-topics writes, with --output-state, every token of the corpus with the topic it was assigned to (a
gzipped file: "#doc source pos typeindex type topic", then "#alpha : ...", "#beta : ...", then one line a token).
That is everything pyLDAvis needs: the topic-term and document-topic distributions (the counts smoothed by MALLET's own
beta and alpha), the document lengths, the vocabulary and the term frequencies. Gensim 4 dropped its MALLET wrapper
(LdaMallet), so this reads MALLET's own output instead of converting a model.

    html = mallet_to_ldavis(state_file, html_file)        # '' when pyLDAvis cannot draw it
"""
import collections
import gzip
import os
import re


def read_state(path):
    """(alpha [one a topic], beta, [(document, word, topic)]) from MALLET's --output-state file.

    THE DOCUMENT IS THE ONE ITS SOURCE NAMES when the source ends in a number ("...\\doc00042.txt" is 42) - MALLET's own
    document count follows the order the folder was listed in - and MALLET's count otherwise."""
    alpha, beta, rows = [], 0.01, []
    opener = gzip.open if path.lower().endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8', errors='replace') as fh:
        for line in fh:
            if line.startswith('#alpha'):
                alpha = [float(x) for x in line.split(':', 1)[1].split()]
            elif line.startswith('#beta'):
                beta = float(line.split(':', 1)[1])
            elif not line.startswith('#'):
                # "doc source pos typeindex type topic" - THE SOURCE IS A FILE PATH AND CAN HOLD SPACES ("Thread_Anne
                # ... .txt"): the document is read from the left, the word and its topic from the right
                parts = line.split()
                if len(parts) >= 6:
                    rows.append((int(parts[0]), parts[-2], int(parts[-1])))
    return alpha, beta, rows


def ldavis_inputs(alpha, beta, rows, n_docs=None, k=None):
    """(topic_term, doc_topic, doc_lengths, vocab, term_frequency) - the five arguments of pyLDAvis.prepare."""
    n_docs = n_docs if n_docs is not None else (max(d for d, _w, _t in rows) + 1 if rows else 0)
    k = k if k is not None else (len(alpha) or (max(t for _d, _w, t in rows) + 1 if rows else 0))
    vocab = sorted({w for _d, w, _t in rows})
    index = {w: i for i, w in enumerate(vocab)}
    tt = [[0.0] * len(vocab) for _ in range(k)]
    dt = [[0.0] * k for _ in range(n_docs)]
    tf = collections.Counter()
    for d, w, t in rows:
        tt[t][index[w]] += 1
        dt[d][t] += 1
        tf[w] += 1
    alpha = alpha or [0.1] * k
    topic_term = [[(c + beta) / (sum(r) + beta * len(vocab)) for c in r] for r in tt]
    doc_topic = [[(c + alpha[t]) / (sum(r) + sum(alpha)) for t, c in enumerate(r)] for r in dt]
    lengths = [int(sum(r)) for r in dt]
    return topic_term, doc_topic, lengths, vocab, [tf[w] for w in vocab]


def mallet_to_ldavis(state_file, html_file):
    """Write the pyLDAvis page of a MALLET run; the page's path, or '' when it cannot be drawn (no pyLDAvis, or no
    token in the state file)."""
    try:
        import pyLDAvis
    except ImportError:
        return ''
    alpha, beta, rows = read_state(state_file)
    if not rows:
        return ''
    tt, dt, lengths, vocab, tf = ldavis_inputs(alpha, beta, rows)
    keep = [i for i, n in enumerate(lengths) if n > 0]          # a document every word of which was a stopword
    vis = pyLDAvis.prepare(tt, [dt[i] for i in keep], [lengths[i] for i in keep], vocab, tf, mds='mmds',
                           sort_topics=False)
    os.makedirs(os.path.dirname(os.path.abspath(html_file)), exist_ok=True)
    pyLDAvis.save_html(vis, html_file)
    return html_file


def document_number(source):
    """The number at the end of a document's file name ("C:/x/doc00042.txt" -> 42), or None."""
    m = re.search(r'(\d+)\.\w+$', str(source))
    return int(m.group(1)) if m else None
