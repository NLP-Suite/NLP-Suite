# Written by Roberto Franzosi & Claude
# Pure-Python replacement for the Java Lucene.jar "Find the plagiarist" /
# "Similarities between documents" tool. Computes pairwise document similarity
# with TF-IDF + cosine similarity (scikit-learn) and writes the same output
# files the Java program produced, so the existing charting and grouping code
# keeps working unchanged:
#   - document_duplicates.txt
#   - Lucene_classes_freq.csv                      [Classes of Percentage Duplication, Frequency, List of Documents in Category]
#   - Lucene_classes_time_freq.csv (if dates)      [Year, 0-10%, ... 90-100%]
#   - Lucene_document_instance_classes_freq.csv    [File Name, 0-10%, ... 90-100%]
#
# NOTE ON SCORES: the old tool scored with Lucene MoreLikeThis (an asymmetric,
# query-vs-document relevance score); this uses symmetric TF-IDF cosine
# similarity, which is the more principled measure of "how similar are two
# documents". Absolute percentages therefore differ from the Java version, so
# the 80% duplicate threshold may need re-tuning on a real corpus.

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "plagiarist_util",
        ['os', 'tkinter', 'numpy', 'sklearn']) == False:
    sys.exit(0)

import os
import re
import csv

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---- Similarity classes (must match the Java output columns) ---------------

CLASS_LABELS = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%',
                '60-70%', '70-80%', '80-90%', '90-100%']


def _band_index(pct):
    """Map a similarity percentage (1..100) to a class index 0..9.

    Bands are (0,10], (10,20], ... (90,100]. Returns None for pct <= 0 so that
    completely unrelated document pairs are not counted.
    """
    if pct <= 0:
        return None
    return max(0, min(9, (int(round(pct)) - 1) // 10))


def _read_documents(input_dir):
    """Return (texts, names) for the .txt files in *input_dir* (sorted, non-empty)."""
    texts, names = [], []
    for fn in sorted(f for f in os.listdir(input_dir) if f.lower().endswith('.txt')):
        with open(os.path.join(input_dir, fn), encoding='utf-8', errors='ignore') as f:
            t = f.read()
        if t.strip():
            texts.append(t)
            names.append(fn)
    return texts, names


def _read_stopwords(stopwords_path):
    if not stopwords_path or not os.path.isfile(stopwords_path):
        return None
    with open(stopwords_path, encoding='utf-8', errors='ignore') as f:
        words = [w.strip() for w in f.read().split() if w.strip()]
    return words or None


def _extract_year(filename, date_pos, date_format, delimiter):
    """Best-effort 4-digit year from a filename that embeds a date.

    Tries the token at *date_pos* (1-based) after splitting on *delimiter*,
    then falls back to scanning every token for a plausible year.
    """
    base = os.path.splitext(os.path.basename(filename))[0]
    parts = base.split(delimiter) if delimiter else [base]
    candidates = []
    try:
        idx = int(date_pos) - 1
        if 0 <= idx < len(parts):
            candidates.append(parts[idx])
    except (ValueError, TypeError):
        pass
    candidates.extend(parts)
    for token in candidates:
        m = re.search(r'(1[0-9]{3}|20[0-9]{2})', token)
        if m:
            return m.group(1)
    return ''


def compute_and_write(input_dir, output_dir, stopwords_path, threshold,
                      embeds_date=False, date_format='', date_pos=1, delimiter='_'):
    """Compute pairwise similarity and write the Lucene-compatible output files.

    *threshold* is a fraction in [0,1]; pairs at or above it are "duplicates".
    Returns a dict of output file paths (keys: duplicates_txt, classes_freq,
    document_instance, classes_time_freq[optional]), or None if there is nothing
    to compare.
    """
    texts, names = _read_documents(input_dir)
    if len(texts) < 2:
        return None

    stopwords = _read_stopwords(stopwords_path)
    vectorizer = TfidfVectorizer(stop_words=stopwords, sublinear_tf=True)
    tfidf = vectorizer.fit_transform(texts)
    sim = cosine_similarity(tfidf)  # N x N, symmetric, diagonal ~1
    n = len(names)
    thr_pct = float(threshold) * 100.0

    # Per-document band counts (how many other docs fall in each band).
    doc_bands = [[0] * 10 for _ in range(n)]
    # Documents that have at least one partner in a given band.
    docs_in_band = [set() for _ in range(10)]
    # Duplicate partners per document: list of (name, pct) with pct >= threshold.
    duplicates = [[] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            pct = sim[i, j] * 100.0
            b = _band_index(pct)
            if b is None:
                continue
            doc_bands[i][b] += 1
            docs_in_band[b].add(names[i])
            if pct >= thr_pct:
                duplicates[i].append((names[j], pct))

    os.makedirs(output_dir, exist_ok=True)
    out = {}

    # ---- Lucene_document_instance_classes_freq.csv -------------------------
    p3 = os.path.join(output_dir, 'Lucene_document_instance_classes_freq.csv')
    with open(p3, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['File Name'] + CLASS_LABELS)
        for i in range(n):
            w.writerow([names[i]] + doc_bands[i])
    out['document_instance'] = p3

    # ---- Lucene_classes_freq.csv -------------------------------------------
    p1 = os.path.join(output_dir, 'Lucene_classes_freq.csv')
    with open(p1, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['Classes of Percentage Duplication', 'Frequency',
                    'List of Documents in Category'])
        for b in range(10):
            docs = sorted(docs_in_band[b])
            w.writerow([CLASS_LABELS[b], len(docs), '; '.join(docs)])
    out['classes_freq'] = p1

    # ---- Lucene_classes_time_freq.csv (only if filenames embed dates) ------
    if embeds_date:
        year_bands = {}
        for i in range(n):
            year = _extract_year(names[i], date_pos, date_format, delimiter)
            if not year:
                continue
            acc = year_bands.setdefault(year, [0] * 10)
            for b in range(10):
                acc[b] += doc_bands[i][b]
        if year_bands:
            p2 = os.path.join(output_dir, 'Lucene_classes_time_freq.csv')
            with open(p2, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                w.writerow(['Year'] + CLASS_LABELS)
                for year in sorted(year_bands):
                    w.writerow([year] + year_bands[year])
            out['classes_time_freq'] = p2

    # ---- document_duplicates.txt -------------------------------------------
    pdup = os.path.join(output_dir, 'document_duplicates.txt')
    docs_with_copies = [i for i in range(n) if duplicates[i]]
    most_copied = max(range(n), key=lambda i: len(duplicates[i])) if n else None
    with open(pdup, 'w', encoding='utf-8') as f:
        f.write('Document similarity report (TF-IDF cosine similarity)\n')
        f.write('Duplicate threshold: {:.0f}% similarity\n\n'.format(thr_pct))
        f.write('{} of {} documents have copies at or above the threshold.\n'
                .format(len(docs_with_copies), n))
        if most_copied is not None and duplicates[most_copied]:
            f.write('The document with the most copies is: {} ({} copies).\n'
                    .format(names[most_copied], len(duplicates[most_copied])))
        f.write('\n')
        for i in range(n):
            if not duplicates[i]:
                continue
            f.write('{} has {} copy(s):\n'.format(names[i], len(duplicates[i])))
            for name_j, pct in sorted(duplicates[i], key=lambda x: -x[1]):
                f.write('   - {}  (score: {:.1f}% match)\n'.format(name_j, pct))
            f.write('\n')
    out['duplicates_txt'] = pdup

    return out


def run(inputDir, outputDir, stopwords_path, similarity_threshold,
        embeds_date=False, date_format='', date_pos=1, delimiter='_'):
    """GUI-facing entry point. Returns a dict of output paths, or None."""
    import tkinter.messagebox as mb
    import IO_user_interface_util

    if not inputDir or not os.path.isdir(inputDir):
        mb.showwarning(title='No input', message='Please select an input directory of .txt files.')
        return None

    startTime = IO_user_interface_util.timed_alert(
        GUI_util.window, 2000, 'Analysis start', 'Started running PLAGIARIST at', True)
    result = compute_and_write(inputDir, outputDir, stopwords_path, similarity_threshold,
                               embeds_date, date_format, date_pos, delimiter)
    IO_user_interface_util.timed_alert(
        GUI_util.window, 2000, 'Analysis end', 'Finished running PLAGIARIST at',
        True, '', True, startTime)

    if result is None:
        mb.showwarning(title='Not enough documents',
                       message='The plagiarist tool needs at least two .txt documents to compare.\n\n'
                               'Please select a directory containing several .txt files and try again.')
    return result
