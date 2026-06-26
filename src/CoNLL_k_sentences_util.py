#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 23:05:52 2022

@author: claude
edited by Naman Sahni 9/23.2022
rewritten 2026 (Roberto Franzosi / Claude): correct bookend-repetition finder + robust counts
"""
import pandas as pd

import IO_files_util
import charts_util
import CoNLL_util  # is_noun_POS / is_verb_POS / is_adjective_POS - handle both Penn and Universal POS tags


def k_sent(inputFilename, outputDir, chartPackage, dataTransformation, Begin_K_sent_var, End_K_sent_var):
    """First/last K-sentences analyzer for a CoNLL table. Produces two outputs per run:

    1. COUNTS: for the first K and the last K sentences of each document, the counts and proportions of
       Words / Nouns / Verbs / Adjectives / Proper-Nouns.
    2. BOOKEND REPETITION FINDER: content words (POSTAG NN*/VB*/JJ*) whose LEMMA appears in BOTH the first K
       and the last K sentences of a document - i.e. words that open AND close the text (a rhetorical/narrative
       framing device). Each repeated word is reported with its Form, Lemma, Sentence ID/text, and its CORPUS
       DOCUMENT FREQUENCY (how many documents contain the lemma); the table is sorted rarest-first, so the most
       distinctive bookend words - the meaningful ones - rise to the top. Matching is on the lemma (so 'attack'
       and 'attacks' count as the same word) while the original Form is preserved for display.

    Works directly from the CoNLL columns (Sentence ID / Document ID / Form / Lemma / POS / DepRel) - no
    re-parsing - and resets all state per document. Returns (outputDir, filesToOpen)."""
    filesToOpen = []
    try:
        Begin_K_sent_var = int(Begin_K_sent_var)
        End_K_sent_var = int(End_K_sent_var)
    except (ValueError, TypeError):
        return outputDir, filesToOpen

    label = 'CoNLL_' + str(Begin_K_sent_var) + '-' + str(End_K_sent_var) + '-sent'
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, '', outputDir, label=label, silent=True)
    if outputDir == '':
        return outputDir, filesToOpen

    conll = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')

    def _content_lemmas(rows):
        """[(lemma_lowercased, Form, Sentence ID), ...] for alphabetic content words (nouns/verbs/adjectives,
        in either Penn or Universal POS tag sets)."""
        items = []
        for form, lemma, pos, sid in zip(rows['Form'].astype(str), rows['Lemma'].astype(str),
                                         rows['POS'].astype(str), rows['Sentence ID']):
            if (CoNLL_util.is_noun_POS(pos) or CoNLL_util.is_verb_POS(pos) or CoNLL_util.is_adjective_POS(pos)) and form.isalpha():
                lem = lemma.lower()
                if lem:
                    items.append((lem, form, sid))
        return items

    # corpus distinctiveness: how many documents contain each content lemma (document frequency)
    lemma_docFreq = {}
    for doc_id in conll['Document ID'].unique():
        for lem in set(l for l, _, _ in _content_lemmas(conll.loc[conll['Document ID'] == doc_id])):
            lemma_docFreq[lem] = lemma_docFreq.get(lem, 0) + 1

    head_counts = ["First/Last Sentences", "K value", "Words Count", "Nouns Count", "Nouns Proportion",
                   "Verbs Count", "Verbs Proportion", "Adjectives Count", "Adjectives Proportion",
                   "Proper-Nouns Count", "Proper-Nouns Proportion", "Document ID", "Document"]
    head_rep = ["First/Last Sentences", "K value", "Word (Form)", "Lemma", "Word ID", "Sentence ID",
                "Sentence", "Corpus document frequency", "Document ID", "Document"]
    result_counts = []
    result_rep = []

    for doc_id in conll['Document ID'].unique():
        doc_rows = conll.loc[conll['Document ID'] == doc_id]
        if len(doc_rows) == 0:
            continue
        DOC = doc_rows['Document'].iloc[0]
        sent_ids = sorted(doc_rows['Sentence ID'].unique())
        if not sent_ids:
            continue
        first_ids = sent_ids[:Begin_K_sent_var]
        last_ids = [s for s in sent_ids[-End_K_sent_var:] if s not in first_ids] if End_K_sent_var > 0 else []
        first_rows = doc_rows.loc[doc_rows['Sentence ID'].isin(first_ids)]
        last_rows = doc_rows.loc[doc_rows['Sentence ID'].isin(last_ids)]

        # counts / proportions for the first and last K sentences
        def _counts_row(section, K, rows):
            pos = rows['POS'].astype(str)
            wc = int((~rows['DepRel'].astype(str).eq('punct')).sum())
            nn = int(pos.apply(CoNLL_util.is_noun_POS).sum())
            nnp = int(pos.apply(CoNLL_util.is_proper_noun_POS).sum())
            vb = int(pos.apply(CoNLL_util.is_verb_POS).sum())
            jj = int(pos.apply(CoNLL_util.is_adjective_POS).sum())
            den = wc if wc else 1
            return [section, K, wc, nn, nn / den, vb, vb / den, jj, jj / den, nnp, nnp / den, doc_id, DOC]
        result_counts.append(_counts_row('First', Begin_K_sent_var, first_rows))
        result_counts.append(_counts_row('Last', End_K_sent_var, last_rows))

        # bookend repetition: content lemmas appearing in BOTH the first and the last K sentences
        first_content = _content_lemmas(first_rows)
        last_content = _content_lemmas(last_rows)
        repeated = set(l for l, _, _ in first_content) & set(l for l, _, _ in last_content)
        if repeated:
            sent_text = doc_rows.groupby('Sentence ID')['Form'].apply(
                lambda f: ' '.join(f.astype(str))).to_dict()
            for section, K, content in (('First', Begin_K_sent_var, first_content),
                                        ('Last', End_K_sent_var, last_content)):
                wid = 0
                for lem, form, sid in content:
                    wid += 1
                    if lem in repeated:
                        result_rep.append([section, K, form, lem, wid, sid, sent_text.get(sid, ''),
                                           lemma_docFreq.get(lem, 0), doc_id, DOC])

    # write the counts table + chart
    if result_counts:
        outFile = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', label,
                                                          '', '', '', '', False, True)
        pd.DataFrame(result_counts, columns=head_counts).to_csv(outFile, encoding='utf-8', index=False)
        filesToOpen.append(outFile)
        ch = charts_util.visualize_chart(chartPackage, dataTransformation, outFile, outputDir, [],
                                         ['Nouns Proportion', 'Verbs Proportion', 'Adjectives Proportion',
                                          'Proper-Nouns Proportion'],
                                         chart_title="Word-class proportions in the first and last K (" +
                                                     str(Begin_K_sent_var) + '-' + str(End_K_sent_var) + ") sentences",
                                         outputFileNameType='k_sent', column_xAxis_label='Tags', count_var=0,
                                         hover_label=[], groupByList=[], plotList=[], chart_title_label='')
        if ch is not None:
            filesToOpen.extend([ch] if isinstance(ch, str) else ch)

    # write the bookend-repetition table + chart (rarest-in-corpus first = most distinctive)
    if result_rep:
        result_rep.sort(key=lambda r: r[7])
        outFile = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv',
                                                          label + '_rep_words', '', '', '', '', False, True)
        pd.DataFrame(result_rep, columns=head_rep).to_csv(outFile, encoding='utf-8', index=False)
        filesToOpen.append(outFile)
        ch = charts_util.visualize_chart(chartPackage, dataTransformation, outFile, outputDir, [], ['Lemma'],
                                         chart_title="Words repeated in BOTH the first and last K (" +
                                                     str(Begin_K_sent_var) + '-' + str(End_K_sent_var) +
                                                     ") sentences (bookend repetition)",
                                         outputFileNameType=str(Begin_K_sent_var) + '-' + str(End_K_sent_var) +
                                                            '-sent_rep_words',
                                         column_xAxis_label='Words', count_var=1,
                                         hover_label=[], groupByList=[], plotList=[], chart_title_label='')
        if ch is not None:
            filesToOpen.extend([ch] if isinstance(ch, str) else ch)

    return outputDir, filesToOpen
